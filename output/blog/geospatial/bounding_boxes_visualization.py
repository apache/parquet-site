# Visualization code for Figure 1 in the "Native Geospatial Types in Apache Parquet" blog post.
# Generates a bounding box visualization for 130 million buildings stored in a Parquet file
# from the contiguous U.S. (Microsoft Buildings dataset, file from geoarrow.org/data).
#
# Original source: https://gist.github.com/paleolimbot/06303283b42161b57ffc37a8fed60890
# Author: Dewey Dunnington (paleolimbot)

import geoarrow.pyarrow as ga  # For GeoArrow extension type registration
import geopandas
import pyarrow as pa
from pyarrow import parquet
import shapely
import fsspec
import matplotlib.pyplot as plt

# Load Natural Earth countries for the backdrop
url = "https://raw.githubusercontent.com/geoarrow/geoarrow-data/v0.2.0/natural-earth/files/natural-earth_countries.fgb"
df = geopandas.read_file(url)

# Read bounding boxes from row group geo statistics
url = "https://github.com/geoarrow/geoarrow-data/releases/download/v0.2.0/microsoft-buildings_point.parquet"

with fsspec.open(url) as fsspec_f:
    f = parquet.ParquetFile(fsspec_f)

    boxes = []
    for i in range(f.num_row_groups):
        stats = f.metadata.row_group(i).column(0).geo_statistics
        box = shapely.box(stats.xmin, stats.ymin, stats.xmax, stats.ymax)
        boxes.append(box)

# Project to Web Mercator for visualization
boxes_geo = geopandas.GeoSeries(boxes, crs=4326).to_crs(3857)
backdrop = df.to_crs(3857)
backdrop = backdrop.intersection(
    shapely.buffer(shapely.box(*boxes_geo.total_bounds), 1000000)
)

# Plot
plt.rcParams["figure.dpi"] = 300

ax = backdrop.plot(edgecolor="black", facecolor="none", antialiased=True, linewidth=0.5)
boxes_geo.plot(ax=ax, edgecolor="purple", facecolor="none", antialiased=True, linewidth=0.5)
bounds = boxes_geo.total_bounds
x_range = bounds[2] - bounds[0]
y_range = bounds[3] - bounds[1]
ax.set_xlim(bounds[0] - 0.05 * x_range, bounds[2] + 0.05 * x_range)
ax.set_ylim(bounds[1] - 0.05 * y_range, bounds[3] + 0.05 * y_range)
ax.set_axis_off()
plt.show()
