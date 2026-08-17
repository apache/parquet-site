---
title: "ALP: Adaptive Lightweight Floating-point Encoding in Apache Parquet"
date: 2026-08-14
description: "Fast, random access, GPU and SIMD-friendly compression and decompression; similar in size to ZSTD"
author: "[Kosta Tarasov](https://github.com/sdf-jkl), [Andrew Lamb](https://github.com/alamb), [Prateek Gaur](https://github.com/prtkgaur)"
categories: ["features"]
---

Apache Parquet has added ALP (Adaptive Lossless floating-Point) -- a new lightweight floating-point encoding with similar compression to heavyweight compressors like zstd and **much** faster decompression speed, supports random access, and is SIMD and GPU friendly. 

----

ALP was developed by the [Database Architectures Group at CWI](https://www.cwi.nl/en/research/database-architectures/) and uses smart tricks to represent floating-point data as integers.

ALP shines on values that represent DECIMAL but are modeled as FLOAT/DOUBLE:
- Monetary values (exchange rates, public funds, stocks, prices, etc.)
- Geographic coordinates (longitude/latitude)
- Scientific measures (temperature, pressure, speed, degrees, etc.)
- Timestamps stored as floating-point

## Why ALP?

Encoding floating point data is a complicated engineering problem. Prior to ALP the only FLOAT/DOUBLE encoding in Parquet (other than Plain) was [Byte Stream Split](https://parquet.apache.org/docs/file-format/data-pages/encodings/#BYTESTREAMSPLIT). Byte Stream Split does not reduce the size of data but *can* make the compression ratio and speed better when a heavyweight compressor is used afterwards.

Using heavyweight compression, however, introduces two problems:
- Slow decompression speed
- Requires decoding the entire page to retrieve a single value (the "random access" problem)

ALP is designed to solve both of these problems for common data patterns, while achieving a similar compression ratio.

### Benchmark

To demonstrate ALP's performance we used the same datasets used in the paper.

- The first 13 are time series data, mostly scientific measurements
- 17 datasets are more representative of
doubles stored in classical database workloads, mostly monetary data

<details><summary>Full list of datasets </summary>

| Name | Semantics | Source | N° of Values |
|---|---|---|---:|
| **Time series** | | | |
| Air-Pressure | Barometric Pressure (kPa) | NEON | 137,721,453 |
| Basel-temp | Temperature (C°) | meteoblue | 123,480 |
| Basel-wind | Wind Speed (Km/h) | meteoblue | 123,480 |
| Bird-migration | Coordinates (lat, lon) | InfluxDB | 17,964 |
| Bitcoin-price | Exchange Rate (BTC-USD) | InfluxDB | 2,686 |
| City-Temp | Temperature (F°) | Udayton | 2,905,887 |
| Dew-Point-Temp | Temperature (C°) | NEON | 5,413,914 |
| IR-bio-temp | Temperature (C°) | NEON | 380,817,839 |
| PM10-dust | Dust content in air (mg/m3) | NEON | 221,568 |
| Stocks-DE | Monetary (Stocks) | INFORE | 43,565,658 |
| Stocks-UK | Monetary (Stocks) | INFORE | 59,305,326 |
| Stocks-USA | Monetary (Stocks) | INFORE | 282,076,179 |
| Wind-dir | Angle Degree (0°-360°) | NEON | 198,898,762 |
| **Non Time series** | | | |
| Arade/4 | Energy | PBI Bench. | 9,888,775 |
| Blockchain-tr | Monetary (BTC) | Blockchain | 231,031 |
| CMS/1 | Monetary Avg. (USD) | PBI Bench. | 18,575,752 |
| CMS/25 | Monetary Std. Dev. (USD) | PBI Bench. | 18,575,752 |
| CMS/9 | Discrete Count | PBI Bench. | 18,575,752 |
| Food-prices | Monetary (USD) | WFP | 2,050,638 |
| Gov/10 | Monetary (USD) | PBI Bench. | 141,123,827 |
| Gov/26 | Monetary (USD) | PBI Bench. | 141,123,827 |
| Gov/30 | Monetary (USD) | PBI Bench. | 141,123,827 |
| Gov/31 | Monetary (USD) | PBI Bench. | 141,123,827 |
| Gov/40 | Monetary (USD) | PBI Bench. | 141,123,827 |
| Medicare/1 | Monetary Avg. (USD) | PBI Bench. | 9,287,876 |
| Medicare/9 | Discrete Count | PBI Bench. | 9,287,876 |
| NYC/29 | Coordinates (lon) | PBI Bench. | 17,446,346 |
| POI-lat | Coordinates (lat, in radians) | Kaggle | 424,205 |
| POI-lon | Coordinates (lon, in radians) | Kaggle | 424,205 |
| SD-bench | Storage Capacity (GB) | Kaggle | 8,927 |

</details>

<br>

We compare compression ratio and [de]compression speed between:
- Plain
- Plain + ZSTD
- Byte Stream Split + ZSTD
- ALP

### Benchmark results

| Encoding scheme | Compression (GB/s) | Decompression (GB/s) | Compressed size (bits/value) |
|---|---:|---:|---:|
| **PLAIN** | **65.547** | **76.644** | **64.01** |
| **PLAIN + ZSTD** | **1.401** | **3.236** | **22.75** |
| **BYTE_STREAM_SPLIT + ZSTD** | **1.786** | **5.132** | **32.76** |
| **ALP** | **1.273** | **33.805** | **24.27** |

<details><summary>Full benchmark results </summary>

| Dataset | Parquet choice | Compression (GB/s) | Decompression (GB/s) | Compressed size (bits/value) |
|---|---|---:|---:|---:|
| arade4 | PLAIN | 63.775 | 68.205 | 64.01 |
| arade4 | PLAIN + ZSTD | 0.574 | 1.499 | 37.39 |
| arade4 | BYTE_STREAM_SPLIT + ZSTD | 1.875 | 4.980 | 54.58 |
| arade4 | ALP | 1.698 | 31.860 | 24.99 |
| basel_temp_f | PLAIN | 33.559 | 57.828 | 64.01 |
| basel_temp_f | PLAIN + ZSTD | 0.458 | 1.656 | 23.07 |
| basel_temp_f | BYTE_STREAM_SPLIT + ZSTD | 1.181 | 2.080 | 54.59 |
| basel_temp_f | ALP | 0.534 | 28.058 | 29.23 |
| basel_wind_f | PLAIN | 52.641 | 76.402 | 64.01 |
| basel_wind_f | PLAIN + ZSTD | 0.591 | 1.733 | 18.53 |
| basel_wind_f | BYTE_STREAM_SPLIT + ZSTD | 1.405 | 2.191 | 54.12 |
| basel_wind_f | ALP | 0.576 | 29.778 | 29.87 |
| bird_migration_f | PLAIN | 65.238 | 93.070 | 64.01 |
| bird_migration_f | PLAIN + ZSTD | 0.420 | 1.778 | 23.49 |
| bird_migration_f | BYTE_STREAM_SPLIT + ZSTD | 1.210 | 10.407 | 45.82 |
| bird_migration_f | ALP | 0.164 | 27.212 | 20.24 |
| bitcoin_f | PLAIN | 91.371 | 222.346 | 64.07 |
| bitcoin_f | PLAIN + ZSTD | 0.585 | 1.660 | 50.01 |
| bitcoin_f | BYTE_STREAM_SPLIT + ZSTD | 1.345 | 19.512 | 48.79 |
| bitcoin_f | ALP | 0.047 | 30.608 | 27.18 |
| bitcoin_transactions_f | PLAIN | 61.862 | 76.608 | 64.01 |
| bitcoin_transactions_f | PLAIN + ZSTD | 1.081 | 1.985 | 47.96 |
| bitcoin_transactions_f | BYTE_STREAM_SPLIT + ZSTD | 1.412 | 2.580 | 56.65 |
| bitcoin_transactions_f | ALP | 0.572 | 21.192 | 41.27 |
| city_temperature_f | PLAIN | 74.404 | 75.291 | 64.01 |
| city_temperature_f | PLAIN + ZSTD | 0.561 | 1.368 | 17.67 |
| city_temperature_f | BYTE_STREAM_SPLIT + ZSTD | 0.962 | 3.569 | 16.64 |
| city_temperature_f | ALP | 1.972 | 37.725 | 10.80 |
| cms1 | PLAIN | 64.257 | 62.655 | 64.01 |
| cms1 | PLAIN + ZSTD | 0.627 | 1.600 | 26.84 |
| cms1 | BYTE_STREAM_SPLIT + ZSTD | 0.670 | 1.651 | 38.64 |
| cms1 | ALP | 1.061 | 18.514 | 35.19 |
| cms25 | PLAIN | 70.317 | 71.847 | 64.01 |
| cms25 | PLAIN + ZSTD | 0.798 | 1.829 | 58.11 |
| cms25 | BYTE_STREAM_SPLIT + ZSTD | 1.287 | 4.345 | 56.72 |
| cms25 | ALP | 1.516 | 21.901 | 41.17 |
| cms9 | PLAIN | 65.334 | 67.735 | 64.01 |
| cms9 | PLAIN + ZSTD | 0.668 | 1.436 | 11.71 |
| cms9 | BYTE_STREAM_SPLIT + ZSTD | 2.151 | 5.502 | 10.07 |
| cms9 | ALP | 1.932 | 34.393 | 12.16 |
| food_prices | PLAIN | 71.786 | 75.631 | 64.01 |
| food_prices | PLAIN + ZSTD | 0.574 | 1.356 | 18.13 |
| food_prices | BYTE_STREAM_SPLIT + ZSTD | 0.744 | 1.865 | 25.47 |
| food_prices | ALP | 0.887 | 20.747 | 23.20 |
| gov10 | PLAIN | 67.983 | 70.573 | 64.01 |
| gov10 | PLAIN + ZSTD | 0.486 | 1.259 | 29.12 |
| gov10 | BYTE_STREAM_SPLIT + ZSTD | 0.648 | 1.740 | 37.31 |
| gov10 | ALP | 1.119 | 24.621 | 29.88 |
| gov26 | PLAIN | 66.105 | 67.432 | 64.01 |
| gov26 | PLAIN + ZSTD | 10.325 | 23.010 | 0.20 |
| gov26 | BYTE_STREAM_SPLIT + ZSTD | 8.112 | 18.208 | 0.24 |
| gov26 | ALP | 1.876 | 84.789 | 1.40 |
| gov30 | PLAIN | 61.089 | 64.308 | 64.01 |
| gov30 | PLAIN + ZSTD | 2.038 | 5.186 | 4.52 |
| gov30 | BYTE_STREAM_SPLIT + ZSTD | 1.695 | 4.155 | 6.14 |
| gov30 | ALP | 1.020 | 33.276 | 17.88 |
| gov31 | PLAIN | 70.238 | 71.923 | 64.01 |
| gov31 | PLAIN + ZSTD | 3.821 | 8.994 | 1.65 |
| gov31 | BYTE_STREAM_SPLIT + ZSTD | 3.780 | 9.643 | 2.47 |
| gov31 | ALP | 1.659 | 50.153 | 6.77 |
| gov40 | PLAIN | 74.751 | 75.933 | 64.01 |
| gov40 | PLAIN + ZSTD | 9.232 | 17.740 | 0.43 |
| gov40 | BYTE_STREAM_SPLIT + ZSTD | 6.477 | 13.890 | 0.62 |
| gov40 | ALP | 1.879 | 77.866 | 2.59 |
| medicare1 | PLAIN | 73.791 | 65.523 | 64.01 |
| medicare1 | PLAIN + ZSTD | 0.552 | 1.508 | 31.68 |
| medicare1 | BYTE_STREAM_SPLIT + ZSTD | 0.800 | 2.166 | 45.27 |
| medicare1 | ALP | 0.958 | 19.660 | 40.46 |
| medicare9 | PLAIN | 73.908 | 75.228 | 64.01 |
| medicare9 | PLAIN + ZSTD | 0.706 | 1.471 | 11.86 |
| medicare9 | BYTE_STREAM_SPLIT + ZSTD | 2.126 | 5.717 | 10.19 |
| medicare9 | ALP | 1.938 | 36.311 | 12.82 |
| neon_air_pressure | PLAIN | 70.685 | 73.563 | 64.01 |
| neon_air_pressure | PLAIN + ZSTD | 0.789 | 2.051 | 11.85 |
| neon_air_pressure | BYTE_STREAM_SPLIT + ZSTD | 0.782 | 2.268 | 28.51 |
| neon_air_pressure | ALP | 1.876 | 36.770 | 16.48 |
| neon_bio_temp_c | PLAIN | 63.818 | 69.314 | 64.01 |
| neon_bio_temp_c | PLAIN + ZSTD | 0.522 | 1.513 | 16.84 |
| neon_bio_temp_c | BYTE_STREAM_SPLIT + ZSTD | 1.240 | 2.885 | 35.40 |
| neon_bio_temp_c | ALP | 1.941 | 35.578 | 10.81 |
| neon_dew_point_temp | PLAIN | 72.097 | 73.614 | 64.01 |
| neon_dew_point_temp | PLAIN + ZSTD | 0.465 | 1.638 | 23.73 |
| neon_dew_point_temp | BYTE_STREAM_SPLIT + ZSTD | 1.503 | 2.370 | 48.00 |
| neon_dew_point_temp | ALP | 1.931 | 32.863 | 13.63 |
| neon_pm10_dust | PLAIN | 51.533 | 70.722 | 64.01 |
| neon_pm10_dust | PLAIN + ZSTD | 0.848 | 1.689 | 7.79 |
| neon_pm10_dust | BYTE_STREAM_SPLIT + ZSTD | 0.634 | 1.682 | 22.21 |
| neon_pm10_dust | ALP | 0.927 | 38.427 | 8.41 |
| neon_wind_dir | PLAIN | 54.631 | 60.583 | 64.01 |
| neon_wind_dir | PLAIN + ZSTD | 0.432 | 1.312 | 24.41 |
| neon_wind_dir | BYTE_STREAM_SPLIT + ZSTD | 1.387 | 3.518 | 42.31 |
| neon_wind_dir | ALP | 1.883 | 47.114 | 15.94 |
| nyc29 | PLAIN | 71.342 | 71.984 | 64.01 |
| nyc29 | PLAIN + ZSTD | 0.611 | 1.539 | 24.67 |
| nyc29 | BYTE_STREAM_SPLIT + ZSTD | 0.939 | 3.768 | 36.91 |
| nyc29 | ALP | 1.679 | 24.137 | 40.43 |
| poi_lat | PLAIN | 58.440 | 50.294 | 64.01 |
| poi_lat | PLAIN + ZSTD | 0.635 | 1.793 | 57.78 |
| poi_lat | BYTE_STREAM_SPLIT + ZSTD | 2.711 | 5.929 | 55.30 |
| poi_lat | ALP | 1.052 | 11.874 | 88.19 |
| poi_lon | PLAIN | 61.546 | 73.497 | 64.01 |
| poi_lon | PLAIN + ZSTD | 0.850 | 1.945 | 60.44 |
| poi_lon | BYTE_STREAM_SPLIT + ZSTD | 2.467 | 5.826 | 57.24 |
| poi_lon | ALP | 1.180 | 14.614 | 79.12 |
| ssd_hdd_benchmarks_f | PLAIN | 66.698 | 112.905 | 64.02 |
| ssd_hdd_benchmarks_f | PLAIN + ZSTD | 0.813 | 1.802 | 12.98 |
| ssd_hdd_benchmarks_f | BYTE_STREAM_SPLIT + ZSTD | 1.265 | 2.850 | 17.42 |
| ssd_hdd_benchmarks_f | ALP | 0.114 | 35.975 | 16.04 |
| stocks_de | PLAIN | 68.397 | 71.924 | 64.01 |
| stocks_de | PLAIN + ZSTD | 0.664 | 1.689 | 10.07 |
| stocks_de | BYTE_STREAM_SPLIT + ZSTD | 0.881 | 2.278 | 33.46 |
| stocks_de | ALP | 1.224 | 35.921 | 11.20 |
| stocks_uk | PLAIN | 60.600 | 64.531 | 64.01 |
| stocks_uk | PLAIN + ZSTD | 0.608 | 1.413 | 11.29 |
| stocks_uk | BYTE_STREAM_SPLIT + ZSTD | 1.180 | 4.006 | 14.89 |
| stocks_uk | ALP | 0.948 | 32.869 | 12.75 |
| stocks_usa_c | PLAIN | 64.214 | 67.851 | 64.01 |
| stocks_usa_c | PLAIN + ZSTD | 0.692 | 1.634 | 8.24 |
| stocks_usa_c | BYTE_STREAM_SPLIT + ZSTD | 0.712 | 2.390 | 26.89 |
| stocks_usa_c | ALP | 2.028 | 39.329 | 7.95 |
| **ALL AVG.** | **PLAIN** | **65.547** | **76.644** | **64.01** |
| **ALL AVG.** | **PLAIN + ZSTD** | **1.401** | **3.236** | **22.75** |
| **ALL AVG.** | **BYTE_STREAM_SPLIT + ZSTD** | **1.786** | **5.132** | **32.76** |
| **ALL AVG.** | **ALP** | **1.273** | **33.805** | **24.27** |

</details>

### Random access benchmark

We also measured random access time for the encodings above. 

Time to decode 100 deterministic, uniformly distributed rows from `city_temperature_f` (lower is better). Each lookup starts from the encoded page.

| Parquet choice | 100 random rows (µs) |
|---|---:|
| PLAIN | 2.819 |
| PLAIN + ZSTD | 74317.077 |
| BYTE_STREAM_SPLIT + ZSTD | 27025.798 |
| ALP | 10.007 |

## Technical overview

### Decimal encoding

The core idea that ALP utilizes is that a lot of data that is represented as FLOAT/DOUBLE is not *real* FLOAT/DOUBLE and was originally DECIMAL that can be represented with an integer and an exponent. Let's follow the logic with a simple example.

ALP finds the smallest integer and keeps an exponent and factor to return it to its decimal value.

> 8.0605 can't be physically represented in [IEEE 754](https://ieeexplore.ieee.org/document/8766229) as is, and is instead approximated as 8.06049999999999933209.
>
> To find the smallest representation you take the value and brute-force search over exponents, computing `significand = round(value × 10^e)`.
>
> For this value it arrives at significand 80605 with exponent 4.

To improve compression ALP stores a single exponent per vector vs storing one per value. To increase coverage of the algorithm using a larger exponent is preferable. This introduces another issue of integers containing too many trailing 0-digits and reducing compression.

ALP solves this by introducing a factor and using it to get rid of as many trailing zeros as possible.

> We have a vector with multiple values. The exponent is trying to capture as many values as possible. The value with the highest precision needs exponent 14.
> 
> That makes 8.06049999999999933209 represented as 806050000000000.
> 
> ALP then searches for a factor to get rid of as many trailing zeros as possible for all values within the vector losslessly. It happens to be 10.
>
> The encoded value can be calculated via `significand = round(value × 10^e × 10^-f)`.
> 
> This makes our value 80605 with e = 14 and f = 10 for this vector.

To make sure that the encoded value still represents the FLOAT/DOUBLE value losslessly we round trip each value during this step.

> Decoding applies the inverse formula `value = significand × 10^f × 10^-e`.
>
> `80605 × 10^10 × 10^-14 = 8.06049999999999933209`
>
> The result matches the stored double exactly: the value round-trips losslessly.

Some values don't survive the round-trip. Instead, they are written to the exception array at the end of the vector. The exceptions positions are stored prior to the exception array.

While very performant, not all floating point data can be exploited by ALP, for example vector embeddings typically span the full floating point range and do not encode well with ALP. Such use cases can continue to use existing Parquet features such as PLAIN or [BYTE_STREAM_SPLIT](https://parquet.apache.org/docs/file-format/data-pages/encodings/#BYTESTREAMSPLIT) encoding followed by ZSTD or SNAPPY general purpose compression.

### Random access

ALP encoding avoids that by encoding values into one or more vectors (between 8 and 32K, defaults to 1024, chosen by the writer), sized for SIMD and for fitting in L1 cache. Each vector stores the necessary metadata to decode any row inside.

**Before**, reading a single value:

> Load the whole page → decompress and decode all of it → retrieve the value

**After**, with ALP:

> Load just the page metadata and get the vector offset → read the vector's metadata → decode the value

This introduces a finer read granularity than the Parquet page and significantly speeds up single-row decode and random access.

### ALP Encoding pipeline in Parquet

The way that ALP encodes data is:

<!-- needs some prose -->

<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM --> 
![ALP encoding pipeline steps](/blog/alp/alp_encoding_pipeline.png)

<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM --> 
![ALP encoding pipeline example](/blog/alp/alp_encoding_example.png)

### ALP Decoding pipeline in Parquet

<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM --> 
![ALP decoding pipeline steps](/blog/alp/alp_decoding_pipeline.png)

<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM --> 
![ALP decoding pipeline example](/blog/alp/alp_decoding_example.png)


To decode we go through mostly the same steps, but in reverse:

1) Unpack bit_width-bit integers 
2) Add frame_of_reference to each unpacked integer.
3) Decode: multiply each integer by 10^factor then by 10^(-exponent).
4) Patch exceptions: for each (position, value) in the exception arrays, overwrite the decoded output at that position with the stored value.


## Ecosystem adoption

<!-- More on how it was implemented in the Parquet ecosystem -->

ALP has been adopted as the default floating-point encoding by [DuckDB](https://duckdb.org/2024/02/13/announcing-duckdb-0100#adaptive-lossless-floating-point-compression-alp) and [CedarDB](https://cedardb.com/blog/release_notes/early_2026/#better-compression-less-storage-floats-and-text), and implemented as a codec by [ClickHouse](https://github.com/ClickHouse/ClickHouse/pull/91362).

It has also been adopted by the new file formats like [Vortex](https://github.com/vortex-data/vortex), [F3](https://github.com/future-file-format/f3) and [FastLanes](https://github.com/cwida/fastlanes) (created by the same folks as ALP).

## Conclusion

<!-- needs more work -->

ALP brings fast, parallelizable decoding and practical random access to floating-point data in Parquet. It's one more step toward closing the gap with the newest file formats.

## Resources

- [ALP paper (CWI)](https://ir.cwi.nl/pub/33334/33334.pdf)
- [ALP Parquet encoding PR](https://github.com/apache/parquet-format/pull/557)