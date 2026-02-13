# Visualization code for the "Spatial Pruning in Action" section in the
# "Native Geospatial Types in Apache Parquet" blog post.
#
# Demonstrates how spatial statistics enable row group pruning by showing
# a query window that intersects only a few row groups out of thousands.
#
# Requirements:
#   pip install sedonadb pyarrow pyproj pyogrio \
#       --pre \
#       --index-url https://repo.fury.io/sedona-nightlies/ \
#       --extra-index-url https://pypi.org/simple/
#
# Also requires: geoarrow-pyarrow, shapely, matplotlib, fsspec, aiohttp

import sedonadb
import geoarrow.pyarrow as ga  # For GeoArrow extension type registration
from pyarrow import parquet
import shapely
from shapely import box
from shapely.ops import transform as shapely_transform
import pyproj
import fsspec
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MplPolygon

# ── SedonaDB: run the spatial query ──────────────────────────────────────────

sd = sedonadb.connect()

parquet_url = (
    "https://github.com/geoarrow/geoarrow-data/releases/download/"
    "v0.2.0/microsoft-buildings_point.parquet"
)

# Load the 130M buildings Parquet file
buildings = sd.read_parquet(parquet_url)
buildings.to_view("buildings")

# Spatial filter: Austin, Texas bounding box
query_sql = """
SELECT * FROM buildings
WHERE ST_Intersects(
    geometry,
    ST_SetSRID(
        ST_GeomFromText('POLYGON((-97.8 30.2, -97.8 30.3, -97.7 30.3, -97.7 30.2, -97.8 30.2))'),
        4326
    )
)
"""

result = sd.sql(query_sql)
print(f"Query returned {result.count()} buildings in the Austin query window")

# Show the explain plan with actual execution metrics (includes row-group pruning stats)
print("\n── Execution plan with pruning metrics ──")
result.explain(type="analyze").show()

# ── Visualization: bounding boxes + pruning ──────────────────────────────────

# Set up CRS transformer (WGS84 to Web Mercator)
transformer_4326_to_3857 = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

def to_mercator(geom):
    """Transform a shapely geometry from EPSG:4326 to EPSG:3857."""
    return shapely_transform(transformer_4326_to_3857.transform, geom)

# Load Natural Earth countries for the backdrop using SedonaDB's read_pyogrio
backdrop_url = (
    "https://raw.githubusercontent.com/geoarrow/geoarrow-data/v0.2.0/"
    "natural-earth/files/natural-earth_countries.fgb"
)
backdrop_df = sd.read_pyogrio(backdrop_url)
backdrop_geoms = ga.as_geoarrow(backdrop_df.to_arrow().column("geometry")).to_shapely()

# Read bounding boxes from row group geo statistics

with fsspec.open(parquet_url) as fsspec_f:
    f = parquet.ParquetFile(fsspec_f)

    boxes = []
    for i in range(f.num_row_groups):
        stats = f.metadata.row_group(i).column(0).geo_statistics
        b = box(stats.xmin, stats.ymin, stats.xmax, stats.ymax)
        boxes.append(b)

# Define query window around Austin, Texas
# This corresponds to: ST_GeomFromText('POLYGON((-97.8 30.2, -97.8 30.3, -97.7 30.3, -97.7 30.2, -97.8 30.2))')
query_window = box(-97.8, 30.2, -97.7, 30.3)

# Identify which row groups intersect the query window
intersects_query = np.array([b.intersects(query_window) for b in boxes])

# Project geometries to Web Mercator for visualization
boxes_mercator = [to_mercator(b) for b in boxes]
query_window_mercator = to_mercator(query_window)
backdrop_mercator = [to_mercator(g) for g in backdrop_geoms]

# Compute bounds from all boxes
all_bounds = shapely.bounds(shapely.GeometryCollection(boxes_mercator))
x_range = all_bounds[2] - all_bounds[0]
y_range = all_bounds[3] - all_bounds[1]

# Clip backdrop to viewing area
view_bbox = shapely.buffer(box(all_bounds[0], all_bounds[1], all_bounds[2], all_bounds[3]), 1000000)
backdrop_clipped = [g.intersection(view_bbox) for g in backdrop_mercator if g.intersects(view_bbox)]

# Separate intersecting and non-intersecting row groups
intersecting_boxes = [boxes_mercator[i] for i in range(len(boxes_mercator)) if intersects_query[i]]
non_intersecting_boxes = [boxes_mercator[i] for i in range(len(boxes_mercator)) if not intersects_query[i]]

# Plot
plt.rcParams["figure.dpi"] = 300
fig, ax = plt.subplots(figsize=(12, 8))

# Draw backdrop (country boundaries)
for geom in backdrop_clipped:
    if geom.is_empty:
        continue
    if geom.geom_type == 'MultiPolygon':
        for poly in geom.geoms:
            if poly.exterior:
                ax.plot(*poly.exterior.xy, color='black', linewidth=0.5)
    elif geom.geom_type == 'Polygon' and geom.exterior:
        ax.plot(*geom.exterior.xy, color='black', linewidth=0.5)

# Draw non-intersecting row groups in light gray
for geom in non_intersecting_boxes:
    if geom.geom_type == 'Polygon' and geom.exterior:
        ax.plot(*geom.exterior.xy, color='#cccccc', linewidth=0.2, alpha=0.4)

# Draw intersecting row groups with bright yellow fill and dark orange border
for geom in intersecting_boxes:
    if geom.geom_type == 'Polygon' and geom.exterior:
        patch = MplPolygon(
            list(zip(*geom.exterior.xy)),
            facecolor='#ffdd00',
            edgecolor='#cc5500',
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(patch)

# Draw query window as a thin dashed red outline (no fill, drawn last so it's on top)
query_bounds = query_window_mercator.bounds
query_rect = Rectangle(
    (query_bounds[0], query_bounds[1]),
    query_bounds[2] - query_bounds[0],
    query_bounds[3] - query_bounds[1],
    linewidth=2,
    edgecolor="red",
    facecolor="none",
    linestyle=(0, (5, 3))  # dashed pattern
)
ax.add_patch(query_rect)

# Set bounds to show full US
ax.set_xlim(all_bounds[0] - 0.05 * x_range, all_bounds[2] + 0.05 * x_range)
ax.set_ylim(all_bounds[1] - 0.05 * y_range, all_bounds[3] + 0.05 * y_range)
ax.set_axis_off()

# Add legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
legend_elements = [
    Line2D([0], [0], color='#cccccc', linewidth=1, alpha=0.5, label='Skipped row groups'),
    Patch(facecolor='#ffcc00', edgecolor='#ff3300', linewidth=2, alpha=0.7, label='Scanned row groups'),
    Line2D([0], [0], color='red', linewidth=2, linestyle='--', label='Query window (Austin, TX)'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

# Print statistics
print(f"Total row groups: {len(boxes)}")
print(f"Intersecting row groups: {intersects_query.sum()}")
print(f"Skipped row groups: {(~intersects_query).sum()}")
print(f"Data reduction: {(~intersects_query).sum() / len(boxes) * 100:.1f}% of row groups skipped")

plt.tight_layout()
plt.savefig("spatial_pruning.png", dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
