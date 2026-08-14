---
title: "ALP lightweight floating-point encoding in Apache Parquet"
date: 2026-08-14
description: "Fast, random access, GPU and SIMD-friendly compression and decompression; similar in size to ZSTD"
author: "[Kosta Tarasov](https://github.com/sdf-jkl), [Andrew Lamb](https://github.com/alamb)"
categories: ["features"]
---

Apache Parquet adopts ALP (Adaptive Lossless floating-Point) - new lightweight floating-point encoding that shows simiar compression ratio to heavyweight compressors like zstd and **much** faster [de]compression speed + "random access" support.

"Random access" is a key feature of ALP -- it allows retrieving a single value without decoding the entire page. This property is becoming increasingly important for workloads such as point lookups with text and vector indexes.

----

ALP was developed by the [Database Architectures Group at CWI](https://www.cwi.nl/en/research/database-architectures/) and uses smart tricks to represent floating-point data as integers.

ALP shines at data that was originally decimal and stored as FLOAT/DOUBLE:
- Monetary values (exchange rates, public funds, stocks, prices, etc.)
- Geographic coordinates (longitude/latitude)
- Scientific measures (temperature, pressure, speed, degrees, etc.)
- Timestamps stored as floating-point

## Why ALP?

Encoding floating point data is a complicated engineering problem. Prior to ALP the only FLOAT/DOUBLE encoding in Parquet (other than Plain) was [Byte Stream Split](https://parquet.apache.org/docs/file-format/data-pages/encodings/#BYTESTREAMSPLIT). Byte Stream Split does not reduce the size of data but **can** make the compression ratio and speed better when a heavyweight compressor is used afterwards.

Using heavyweight compressions however introduces two problems:
- Slow decompression speed
- Requires to decode entire page to retrieve a single value (the "random access" problem)

ALP succeeds at solving both of this problems without losing compression ratio.

### Benchmark

To demonstrate ALP's performance we used the same datasets used in the paper.

- The first 13 are time series data 
- 17 datasets are more representative of
doubles stored in classical database workloads

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
| **ALP** | **2.046** | **33.805** | **24.27** |

<details><summary>Full benchmark results </summary>

| Dataset | Parquet choice | Compression (GB/s) | Decompression (GB/s) | Compressed size (bits/value) |
|---|---|---:|---:|---:|
| arade4 | PLAIN | 63.775 | 68.205 | 64.01 |
| arade4 | PLAIN + ZSTD | 0.574 | 1.499 | 37.39 |
| arade4 | BYTE_STREAM_SPLIT + ZSTD | 1.875 | 4.980 | 54.58 |
| arade4 | ALP | 2.275 | 31.860 | 24.99 |
| basel_temp_f | PLAIN | 33.559 | 57.828 | 64.01 |
| basel_temp_f | PLAIN + ZSTD | 0.458 | 1.656 | 23.07 |
| basel_temp_f | BYTE_STREAM_SPLIT + ZSTD | 1.181 | 2.080 | 54.59 |
| basel_temp_f | ALP | 1.346 | 28.058 | 29.23 |
| basel_wind_f | PLAIN | 52.641 | 76.402 | 64.01 |
| basel_wind_f | PLAIN + ZSTD | 0.591 | 1.733 | 18.53 |
| basel_wind_f | BYTE_STREAM_SPLIT + ZSTD | 1.405 | 2.191 | 54.12 |
| basel_wind_f | ALP | 2.365 | 29.778 | 29.87 |
| bird_migration_f | PLAIN | 65.238 | 93.070 | 64.01 |
| bird_migration_f | PLAIN + ZSTD | 0.420 | 1.778 | 23.49 |
| bird_migration_f | BYTE_STREAM_SPLIT + ZSTD | 1.210 | 10.407 | 45.82 |
| bird_migration_f | ALP | 2.542 | 27.212 | 20.24 |
| bitcoin_f | PLAIN | 91.371 | 222.346 | 64.07 |
| bitcoin_f | PLAIN + ZSTD | 0.585 | 1.660 | 50.01 |
| bitcoin_f | BYTE_STREAM_SPLIT + ZSTD | 1.345 | 19.512 | 48.79 |
| bitcoin_f | ALP | 1.732 | 30.608 | 27.18 |
| bitcoin_transactions_f | PLAIN | 61.862 | 76.608 | 64.01 |
| bitcoin_transactions_f | PLAIN + ZSTD | 1.081 | 1.985 | 47.96 |
| bitcoin_transactions_f | BYTE_STREAM_SPLIT + ZSTD | 1.412 | 2.580 | 56.65 |
| bitcoin_transactions_f | ALP | 2.137 | 21.192 | 41.27 |
| city_temperature_f | PLAIN | 74.404 | 75.291 | 64.01 |
| city_temperature_f | PLAIN + ZSTD | 0.561 | 1.368 | 17.67 |
| city_temperature_f | BYTE_STREAM_SPLIT + ZSTD | 0.962 | 3.569 | 16.64 |
| city_temperature_f | ALP | 2.607 | 37.725 | 10.80 |
| cms1 | PLAIN | 64.257 | 62.655 | 64.01 |
| cms1 | PLAIN + ZSTD | 0.627 | 1.600 | 26.84 |
| cms1 | BYTE_STREAM_SPLIT + ZSTD | 0.670 | 1.651 | 38.64 |
| cms1 | ALP | 1.300 | 18.514 | 35.19 |
| cms25 | PLAIN | 70.317 | 71.847 | 64.01 |
| cms25 | PLAIN + ZSTD | 0.798 | 1.829 | 58.11 |
| cms25 | BYTE_STREAM_SPLIT + ZSTD | 1.287 | 4.345 | 56.72 |
| cms25 | ALP | 2.057 | 21.901 | 41.17 |
| cms9 | PLAIN | 65.334 | 67.735 | 64.01 |
| cms9 | PLAIN + ZSTD | 0.668 | 1.436 | 11.71 |
| cms9 | BYTE_STREAM_SPLIT + ZSTD | 2.151 | 5.502 | 10.07 |
| cms9 | ALP | 2.564 | 34.393 | 12.16 |
| food_prices | PLAIN | 71.786 | 75.631 | 64.01 |
| food_prices | PLAIN + ZSTD | 0.574 | 1.356 | 18.13 |
| food_prices | BYTE_STREAM_SPLIT + ZSTD | 0.744 | 1.865 | 25.47 |
| food_prices | ALP | 1.130 | 20.747 | 23.20 |
| gov10 | PLAIN | 67.983 | 70.573 | 64.01 |
| gov10 | PLAIN + ZSTD | 0.486 | 1.259 | 29.12 |
| gov10 | BYTE_STREAM_SPLIT + ZSTD | 0.648 | 1.740 | 37.31 |
| gov10 | ALP | 1.686 | 24.621 | 29.88 |
| gov26 | PLAIN | 66.105 | 67.432 | 64.01 |
| gov26 | PLAIN + ZSTD | 10.325 | 23.010 | 0.20 |
| gov26 | BYTE_STREAM_SPLIT + ZSTD | 8.112 | 18.208 | 0.24 |
| gov26 | ALP | 1.990 | 84.789 | 1.40 |
| gov30 | PLAIN | 61.089 | 64.308 | 64.01 |
| gov30 | PLAIN + ZSTD | 2.038 | 5.186 | 4.52 |
| gov30 | BYTE_STREAM_SPLIT + ZSTD | 1.695 | 4.155 | 6.14 |
| gov30 | ALP | 1.157 | 33.276 | 17.88 |
| gov31 | PLAIN | 70.238 | 71.923 | 64.01 |
| gov31 | PLAIN + ZSTD | 3.821 | 8.994 | 1.65 |
| gov31 | BYTE_STREAM_SPLIT + ZSTD | 3.780 | 9.643 | 2.47 |
| gov31 | ALP | 2.658 | 50.153 | 6.77 |
| gov40 | PLAIN | 74.751 | 75.933 | 64.01 |
| gov40 | PLAIN + ZSTD | 9.232 | 17.740 | 0.43 |
| gov40 | BYTE_STREAM_SPLIT + ZSTD | 6.477 | 13.890 | 0.62 |
| gov40 | ALP | 2.864 | 77.866 | 2.59 |
| medicare1 | PLAIN | 73.791 | 65.523 | 64.01 |
| medicare1 | PLAIN + ZSTD | 0.552 | 1.508 | 31.68 |
| medicare1 | BYTE_STREAM_SPLIT + ZSTD | 0.800 | 2.166 | 45.27 |
| medicare1 | ALP | 1.265 | 19.660 | 40.46 |
| medicare9 | PLAIN | 73.908 | 75.228 | 64.01 |
| medicare9 | PLAIN + ZSTD | 0.706 | 1.471 | 11.86 |
| medicare9 | BYTE_STREAM_SPLIT + ZSTD | 2.126 | 5.717 | 10.19 |
| medicare9 | ALP | 2.593 | 36.311 | 12.82 |
| neon_air_pressure | PLAIN | 70.685 | 73.563 | 64.01 |
| neon_air_pressure | PLAIN + ZSTD | 0.789 | 2.051 | 11.85 |
| neon_air_pressure | BYTE_STREAM_SPLIT + ZSTD | 0.782 | 2.268 | 28.51 |
| neon_air_pressure | ALP | 2.495 | 36.770 | 16.48 |
| neon_bio_temp_c | PLAIN | 63.818 | 69.314 | 64.01 |
| neon_bio_temp_c | PLAIN + ZSTD | 0.522 | 1.513 | 16.84 |
| neon_bio_temp_c | BYTE_STREAM_SPLIT + ZSTD | 1.240 | 2.885 | 35.40 |
| neon_bio_temp_c | ALP | 2.551 | 35.578 | 10.81 |
| neon_dew_point_temp | PLAIN | 72.097 | 73.614 | 64.01 |
| neon_dew_point_temp | PLAIN + ZSTD | 0.465 | 1.638 | 23.73 |
| neon_dew_point_temp | BYTE_STREAM_SPLIT + ZSTD | 1.503 | 2.370 | 48.00 |
| neon_dew_point_temp | ALP | 2.517 | 32.863 | 13.63 |
| neon_pm10_dust | PLAIN | 51.533 | 70.722 | 64.01 |
| neon_pm10_dust | PLAIN + ZSTD | 0.848 | 1.689 | 7.79 |
| neon_pm10_dust | BYTE_STREAM_SPLIT + ZSTD | 0.634 | 1.682 | 22.21 |
| neon_pm10_dust | ALP | 1.784 | 38.427 | 8.41 |
| neon_wind_dir | PLAIN | 54.631 | 60.583 | 64.01 |
| neon_wind_dir | PLAIN + ZSTD | 0.432 | 1.312 | 24.41 |
| neon_wind_dir | BYTE_STREAM_SPLIT + ZSTD | 1.387 | 3.518 | 42.31 |
| neon_wind_dir | ALP | 2.356 | 47.114 | 15.94 |
| nyc29 | PLAIN | 71.342 | 71.984 | 64.01 |
| nyc29 | PLAIN + ZSTD | 0.611 | 1.539 | 24.67 |
| nyc29 | BYTE_STREAM_SPLIT + ZSTD | 0.939 | 3.768 | 36.91 |
| nyc29 | ALP | 2.333 | 24.137 | 40.43 |
| poi_lat | PLAIN | 58.440 | 50.294 | 64.01 |
| poi_lat | PLAIN + ZSTD | 0.635 | 1.793 | 57.78 |
| poi_lat | BYTE_STREAM_SPLIT + ZSTD | 2.711 | 5.929 | 55.30 |
| poi_lat | ALP | 1.691 | 11.874 | 88.19 |
| poi_lon | PLAIN | 61.546 | 73.497 | 64.01 |
| poi_lon | PLAIN + ZSTD | 0.850 | 1.945 | 60.44 |
| poi_lon | BYTE_STREAM_SPLIT + ZSTD | 2.467 | 5.826 | 57.24 |
| poi_lon | ALP | 1.838 | 14.614 | 79.12 |
| ssd_hdd_benchmarks_f | PLAIN | 66.698 | 112.905 | 64.02 |
| ssd_hdd_benchmarks_f | PLAIN + ZSTD | 0.813 | 1.802 | 12.98 |
| ssd_hdd_benchmarks_f | BYTE_STREAM_SPLIT + ZSTD | 1.265 | 2.850 | 17.42 |
| ssd_hdd_benchmarks_f | ALP | 2.587 | 35.975 | 16.04 |
| stocks_de | PLAIN | 68.397 | 71.924 | 64.01 |
| stocks_de | PLAIN + ZSTD | 0.664 | 1.689 | 10.07 |
| stocks_de | BYTE_STREAM_SPLIT + ZSTD | 0.881 | 2.278 | 33.46 |
| stocks_de | ALP | 1.460 | 35.921 | 11.20 |
| stocks_uk | PLAIN | 60.600 | 64.531 | 64.01 |
| stocks_uk | PLAIN + ZSTD | 0.608 | 1.413 | 11.29 |
| stocks_uk | BYTE_STREAM_SPLIT + ZSTD | 1.180 | 4.006 | 14.89 |
| stocks_uk | ALP | 0.886 | 32.869 | 12.75 |
| stocks_usa_c | PLAIN | 64.214 | 67.851 | 64.01 |
| stocks_usa_c | PLAIN + ZSTD | 0.692 | 1.634 | 8.24 |
| stocks_usa_c | BYTE_STREAM_SPLIT + ZSTD | 0.712 | 2.390 | 26.89 |
| stocks_usa_c | ALP | 2.627 | 39.329 | 7.95 |
| **ALL AVG.** | **PLAIN** | **65.547** | **76.644** | **64.01** |
| **ALL AVG.** | **PLAIN + ZSTD** | **1.401** | **3.236** | **22.75** |
| **ALL AVG.** | **BYTE_STREAM_SPLIT + ZSTD** | **1.786** | **5.132** | **32.76** |
| **ALL AVG.** | **ALP** | **2.046** | **33.805** | **24.27** |

</details>


### Random access

We also measured random access time for the encodings above. 

Time to decode 100 deterministic, uniformly distributed rows from `city_temperature_f` (lower is better). Each lookup starts from the encoded page.

| Parquet choice | 100 random rows (µs) |
|---|---:|
| PLAIN | 2.817 |
| PLAIN + ZSTD | 75898.583 |
| ALP | 10.100 |

## Technical overview

<!-- How alp works -->

For example:

> 8.0605 can't be physically represented in [IEEE 754](https://ieeexplore.ieee.org/document/8766229) as is, and is instead approximated as 8.06049999999999933209.
>
> PDE takes the value and brute-force searches over exponents, computing `significand = round(value × 10^e)` for each.
>
> For this value it arrives at significand 80605 with exponent 4.

The catch is that PDE stores an exponent for every single value.

The key ideas behind ALP are:
- the majority of floating-point values share similar decimal precision within vectors
- there is a huge benefit in vectorizing the encoding

The first idea leads to an improvement over PDE. Instead of storing an exponent per value, we store it per vector. This way we get a much smaller metadata footprint.

The second idea is to make the code SIMD-friendly to achieve greater [de]compression speeds.

While very performant not all floating point data can be exploited by ALP, for example vector embeddings typically span the full floating point range and do not encode well with ALP. Such usecases can continue to use existing Parquet features such as PLAIN or [BYTE_STREAM_SPLIT](https://parquet.apache.org/docs/file-format/data-pages/encodings/#BYTESTREAMSPLIT) encoding followed by ZSTD or SNAPPY general purpose decompression.

### Random access

"ALP encoding avoids that by encoding values into one or more vectors (between 8 and 32K, defaults to 1024, chosen by the writer), sized for SIMD and for fitting in L1 cache. Each vector stores the necessary metadata to decode any row inside."

**Before**, reading a single value:

> Load the whole page → decompress and decode all of it → retrieve the value

**After**, with ALP:

> Load just the page metadata → get the vector offset → decode only that vector

This introduces a finer read granularity than the Parquet page and can significantly speed up single-row decodes and random access.

### ALP Encoding pipeline in Parquet

The way that ALP encodes data is:

<!-- Andrew's chart :rocket: -->


                    Input: float/double array
                              |
                              v
    +----------------------------------------------------------+
    |  1. CHOOSE PARAMETERS                                    |
    |     Select (exponent, factor) pair for this vector       |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  2. DECIMAL ENCODING                                     |
    |     encoded[i] = fast_round(value[i] * 10^e * 10^(-f))  |
    |     Detect exceptions where decode(encode(v)) != v       |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  3. FRAME OF REFERENCE (FOR)                             |
    |     min_val = min(encoded[])                             |
    |     delta[i] = encoded[i] - min_val                      |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  4. BIT PACKING                                          |
    |     bit_width = ceil(log2(max_delta + 1))                |
    |     Pack each delta into bit_width bits                  |
    +----------------------------------------------------------+
                              |
                              v
                   Output: Serialized vector bytes

**1. Choose parameters**

First, sample multiple vectors within a row group to find the overall best combinations of exponent and factor.

Then re-evaluate those candidate combinations on each vector to pick the pair that compresses it best.

**2. Decimal encoding**

Encode each value with the formula above, then round-trip it (decode it back) to make sure it matches the original.

If the round-trip fails, the value is added to the vector's exceptions list.

**3. Frame of reference (FOR)**

Once the values are encoded as integers, we pick the smallest one as the frame of reference. Every value is then stored as its delta from that minimum.

**4. Bit packing**

Finally, we take the bit width of the largest delta and pack every delta into that many bits.

### ALP Decoding pipeline in Parquet

<!-- Andrew's chart :rocket: -->

                    Input: Serialized vector bytes
                              |
                              v
    +----------------------------------------------------------+
    |  1. BIT UNPACKING                                        |
    |     Unpack num_elements values at bit_width bits each    |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  2. REVERSE FOR                                          |
    |     encoded[i] = delta[i] + frame_of_reference           |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  3. DECIMAL DECODING                                     |
    |     value[i] = encoded[i] * 10^factor * 10^(-exponent)   |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  4. PATCH EXCEPTIONS                                     |
    |     value[pos[j]] = exception_values[j]                  |
    +----------------------------------------------------------+
                              |
                              v
                  Output: Original float/double array

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

ALP brings fast, parallelizable decoding and practical random access to floating-point data in Parquet. It's one more step toward closing the gap with the newest file formats.

## Resources

- [ALP paper (CWI)](https://ir.cwi.nl/pub/33334/33334.pdf)
- [ALP Parquet encoding PR](https://github.com/apache/parquet-format/pull/557)