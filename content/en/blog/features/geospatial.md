---
title: "Native Geospatial Types in Apache Parquet"
date: 2026-02-04
description: "Native Geospatial Types in Apache Parquet"
author: "[Jia Yu](https://www.linkedin.com/in/dr-jia-yu/)"
categories: ["features"]
---

Geospatial data has become a core input for modern analytics across logistics, climate science, urban planning, mobility, and location intelligence. Yet for a long time, spatial data lived outside the mainstream analytics ecosystem. In primarily non-spatial data engineering workflows, spatial data was common but required workarounds to handlebe handled efficiently at scale. Formats such as Shapefile, GeoJSON, or proprietary spatial databases worked well for visualization and GIS workflows, but they did not integrate cleanly with large scale analytical engines.

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

**Figure 1**: Visualization of bounding boxes for 130 million buildings stored in a Parquet file from the contiguous U.S. (Microsoft Buildings, file from geoarrow.org/data, visualization code here)



(TODO: migrate the rest of the content from https://docs.google.com/document/d/1JPK0F6Vn4sjXGO4AzrkywOjlj_ybDV_6v0zuaFIIjlk)

