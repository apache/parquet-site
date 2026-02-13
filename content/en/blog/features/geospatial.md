---
title: "Native Geospatial Types in Apache Parquet"
date: 2026-02-13
description: "Native Geospatial Types in Apache Parquet"
author: "[Jia Yu](https://github.com/jiayuasu), [Dewey Dunnington](https://github.com/paleolimbot), [Kristin Cowalcijk](https://github.com/Kontinuation), [Feng Zhang](https://github.com/zhangfengcdt)"
categories: ["features"]
---

Geospatial data has become a core input for modern analytics across logistics, climate science, urban planning, mobility, and location intelligence. Yet for a long time, spatial data lived outside the mainstream analytics ecosystem. In primarily non-spatial data engineering workflows, spatial data was common but required workarounds to handle efficiently at scale. Formats such as Shapefile, GeoJSON, or proprietary spatial databases worked well for visualization and GIS workflows, but they did not integrate cleanly with large scale analytical engines.

The introduction of native geospatial types in Apache Parquet marks a major shift. Geometry and geography are no longer opaque blobs stored alongside tabular data. They are now first class citizens in the columnar storage layer that underpins modern data lakes and lakehouses.

This post explains why native geospatial support in Parquet matters and gives a technical overview of how these types are represented and stored.

## Why Geospatial Types Matter in Analytical Storage

Spatial data storage presents unique challenges: a single geometry may represent a point, a road segment, or a complex polygon with thousands of vertices. Queries are also different: instead of simple equality or range filters, users ask spatial questions such as containment, intersection, distance, and proximity in two (XY) or even three (XYZ) dimensions.

Historically, geospatial columns in Parquet were stored as generic binary or string values, with spatial meaning encoded in external metadata. This approach had several limitations.

1. Query engines could not detect a column was GEOMETRY or GEOGRAPHY without an explicit function call by the user (even if the engine supported GEOMETRY or GEOGRAPHY types natively)
2. Query engines could not apply statistics-based pruning: full Parquet files were required to be read even for spatial queries that returned a small number of rows.

Native geospatial types address these issues directly. By making geometry and geography part of the Parquet logical type system, spatial columns become visible to query planners, execution engines, and storage optimizers.

A key benefit is the ability to attach spatial statistics such as bounding boxes to column chunks and row groups. With bounding boxes available in Parquet statistics, engines can skip entire row groups that fall completely outside a query window. This dramatically reduces IO for spatial filters and joins, especially on large datasets.

In practice, this means that spatial analytics can finally benefit from the same performance techniques that made Parquet dominant for non-spatial workloads.

![Building Bounding Boxes Visualization](/blog/geospatial/bounding_boxes.png)

**Figure 1:** Visualization of bounding boxes for 130 million buildings stored in a Parquet file from the contiguous U.S. (Microsoft Buildings, file from geoarrow.org/data, visualization [code](/blog/geospatial/bounding_boxes_visualization.py) here)

Consider a [SedonaDB](https://sedona.apache.org/sedonadb/) Spatial SQL query that filters buildings by intersection with a small region around Austin, Texas:

```sql
SELECT * FROM buildings
WHERE ST_Intersects(
    geometry,
    ST_SetSRID(
        ST_GeomFromText('POLYGON((-97.8 30.2, -97.8 30.3, -97.7 30.3, -97.7 30.2, -97.8 30.2))'),
        4326
    )
)
```

With bounding box statistics attached to each row group, the query engine compares the query window against each row group's bounding box before reading any geometry data. In the visualization below, the query window (red box) overlaps with only 3 row groups out of 2,585 (highlighted in orange). The engine skips all other row groups entirely.

![Spatial Pruning Visualization](/blog/geospatial/spatial_pruning.png)

**Figure 2:** Spatial pruning in action: the query window over Austin (red) intersects only 3 row group bounding boxes (orange). The remaining 2,582 row groups (gray) are skipped without reading their data. (visualization [code](/blog/geospatial/spatial_pruning_visualization.py) here)

## From GeoParquet Metadata to Native Types

Before Parquet adopted GEOMETRY and GEOGRAPHY types in 2025, the [GeoParquet](https://geoparquet.org/) community had already standardized how geometries should be stored in Parquet as early as 2022, using well known binary encoding plus a set of metadata keys. This was an important step because it enabled interoperability across tools.

However, geometry columns were still fundamentally binary columns with sidecar metadata. Engines had to explicitly opt in to understanding that metadata and its placement in the file key/value metadata made it difficult to integrate with primarily non-spatial engines that were not designed to be extended in this way. Moreover, data lake table formats such as Apache Iceberg require concrete, first class Parquet data types to enable engine interoperability, which sidecar metadata cannot adequately support.

The newer direction, sometimes referred to as [GeoParquet 2.0](https://cloudnativegeo.org/blog/2025/02/geoparquet-2.0-going-native/), moves geospatial concepts directly into the Parquet type system. Geometry and geography are defined as logical types, similar in spirit to decimal or timestamp types. This eliminates ambiguity such that non-spatial engines are better able to integrate Geometry and Geography concepts, improving type fidelity and performance for spatial and non-spatial users alike.

## Overview of Geospatial Types in Parquet

Parquet introduces two primary [logical types for spatial data](https://parquet.apache.org/docs/file-format/types/geospatial/).

### GEOMETRY

The GEOMETRY type represents planar spatial objects. This includes points, linestrings, polygons, and multi geometries. The logical type indicates that the column contains spatial objects, while the physical storage uses a standard binary encoding.

Typical examples include:

1. Engineering or CAD data in local coordinates
2. Projected map data such as Web Mercator or UTM
3. Spatial joins and overlays where longitude and latitude data distributed over a small area or where vertices are closely spaced, such as intersections, unions, clipping, and containment analysis

![Westminster Bridge Engineering Precision](/blog/geospatial/westminster_bridge.png)

**Figure 3:** Building the London Westminster Bridge: the Geometry type under a local coordinate reference system would provide better precision and performance than the Geography type.

### GEOGRAPHY

The GEOGRAPHY type is similar to GEOMETRY but represents objects on a spherical or ellipsoidal Earth model. Geography values are encoded using longitude and latitude coordinates expressed in degrees.

Common use cases include:

1. Global scale datasets that span large geographic extents (e.g., country boundaries)
2. Distance calculations where curvature of the earth matters (e.g., the distance between New York and Beijing)
3. Use cases such as aviation, maritime tracking, or global mobility

![London NYC Distance Comparison](/blog/geospatial/london_nyc_distance.png)

**Figure 4:** The shortest distance between London and NYC should cross Canada when using the Geography type, whereas the Geometry type incorrectly misses Canada.

Both types integrate into Parquet schemas just like other logical types. From the perspective of a schema definition, a geometry column is no longer an opaque binary field but a typed spatial column.

## How Geospatial Types Are Stored

Although geospatial types are logical constructs, their physical storage follows [Parquet's existing columnar design](https://parquet.apache.org/docs/file-format/types/geospatial/). The following points highlight key aspects of the geospatial type design.

1. **Physical encoding**
   Geometry and geography values are stored as binary payloads, using [Well Known Binary (WKB)](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry#Well-known_binary) encoding. This ensures compatibility across engines and languages.
2. **Spatial statistics**
   In addition to standard Parquet statistics such as null counts, spatial columns can carry bounding box information. Each row group can record the minimum and maximum extents of the geometries it contains. Query engines can use this information to prune data early when evaluating spatial predicates.
3. **Engine interoperability**
   Because the spatial meaning is encoded as a Parquet logical type, engines do not need out of band conventions to interpret the column. A reader that understands Parquet geospatial types can immediately treat the column as a spatial object.
4. **Coordinate Reference System (CRS) information**
   CRS information is stored in the file metadata (i.e., type definition) using authoritative identifiers or structured definitions such as EPSG codes or PROJJSON strings.

Native geospatial types align naturally with modern lakehouse architectures built on Parquet. Table formats such as [Apache Iceberg](https://iceberg.apache.org/) no longer need to reinvent geospatial logic since core spatial semantics live in Parquet. Instead, they can focus on well defined type mappings between Parquet and Iceberg and on [propagating spatial statistics into the tables](https://wherobots.com/blog/iceberg-geo-technical-insights-and-implementation-strategies/).

## Implementation status and ecosystem adoption

Native Parquet geo types are not theoretical. Geometry and geography have already been implemented across multiple core libraries, indicating broad and growing adoption.

Today, support exists in multiple languages and runtimes, including Parquet Java, Arrow C++, Rust, Hyparquet Javascript, DuckDB, and more! This ensures that geospatial Parquet files can be produced and consumed consistently across ecosystems, from JVM engines to native and embedded query engines.

An up to date view of implementation coverage can be found in the [official Parquet documentation](https://parquet.apache.org/docs/file-format/implementationstatus/).

## Conclusion

Native geospatial support in Apache Parquet represents a foundational improvement for spatial analytics and a welcome quality of life improvement for general-purpose workloads with a spatial component. By elevating geometry and geography to first class logical types, Parquet enables efficient storage, meaningful statistics, and true engine interoperability.

Bounding boxes, columnar layout, and standard encodings together allow spatial data to participate fully in modern analytics systems. As a result, geospatial workloads no longer need specialized storage formats or isolated systems. They can live natively inside the open, scalable data lake ecosystem.

To get started with Geometry/Geography in Parquet, see the [example files provided by the geoarrow-data repository](https://geoarrow.org/data) or write your own using your favourite Parquet implementation!

```python
import geoarrow.pyarrow as ga # For GeoArrow extension type registration
import geopandas
import pyarrow as pa
from pyarrow import parquet

# From GeoPandas, create a GeoDataFrame from your favourite data source
url = "https://raw.githubusercontent.com/geoarrow/geoarrow-data/v0.2.0/natural-earth/files/natural-earth_countries.fgb"
df = geopandas.read_file(url)

# Write to Parquet using pyarrow.parquet()
tab = pa.table(df.to_arrow())
parquet.write_table(tab, "countries.parquet")

# Verify that the Geometry logical type was written to the file
parquet.ParquetFile("countries.parquet").schema
#> <pyarrow._parquet.ParquetSchema object at 0x10776dac0>
#> required group field_id=-1 schema {
#>   optional binary field_id=-1 name (String);
#>   optional binary field_id=-1 continent (String);
#>   optional binary field_id=-1 geometry (Geometry(crs=));
#> }

# Geometry is read to a pyarrow.Table as GeoArrow arrays that can be
# converted back to GeoPandas
tab = parquet.read_table("countries.parquet")
df = geopandas.GeoDataFrame.from_arrow(tab)
df.head(2)
#> name continent  \
#> 0                         Fiji   Oceania  
#> 1  United Republic of Tanzania    Africa  
#>
#>                                             geometry 
#> 0  MULTIPOLYGON (((180 -16.06713, 180 -16.55522, ... 
#> 1  MULTIPOLYGON (((33.90371 -0.95, 34.07262 -1.05...
```


