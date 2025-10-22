---
title: "Implementation status"
linkTitle: "Implementation status"
weight: 8
---

This page summarizes the features supported by different Parquet
implementations.

*Note*: This is a work in progress and we would welcome help expanding its scope.

### Legend
The value in each box means:
* ✅: supported
* ❌: not supported
* (R/W): partial reader/writer only support
* (blank) no data

Implementations:
* [arrow](https://github.com/apache/arrow/tree/main/cpp/src/parquet) (C++)
* [parquet-java](https://github.com/apache/parquet-java) (Java)
* [arrow-go](https://github.com/apache/arrow-go/tree/main/parquet) (Go)
* [arrow-rs](https://github.com/apache/arrow-rs/blob/main/parquet/README.md) (Rust)
* [cudf](https://github.com/rapidsai/cudf) (cuDF C++)
* [hyparquet](https://github.com/hyparam/hyparquet) (JavaScript)
* [duckdb](https://github.com/duckdb/duckdb) (C++)

### Physical types

| Data type                                 | arrow | parquet-java  | arrow-go | arrow-rs | cudf  | hyparquet | duckdb |
| ----------------------------------------- | ----- | ------------- | -------- | -------- | ----- | --------- | ------ |
| BOOLEAN                                   |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  ✅   |
| INT32                                     |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  ✅   |
| INT64                                     |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  ✅   |
| INT96 (1)                                 |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |  (R)  |
| FLOAT                                     |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  ✅   |
| DOUBLE                                    |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  ✅   |
| BYTE_ARRAY                                |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  ✅   |
| FIXED_LEN_BYTE_ARRAY                      |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  ✅   |

* \(1) This type is deprecated, but as of 2024 it's common in currently produced parquet files


### Logical types

| Data type                                 | arrow | parquet-java  | arrow-go | arrow-rs | cudf  | hyparquet | duckdb |
| ----------------------------------------- | ----- | ------------- | -------- | -------- | ----- | --------- | ------ |
| STRING                                    |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| ENUM                                      |  ❌   |  ✅           |  ✅      |  ✅ (1)  |  ❌   |  ✅       |   ✅   |
| UUID                                      |  ❌   |  ✅           |  ✅      |  ✅ (1)  |  ❌   |  ✅       |   ✅   |
| 8, 16, 32, 64 bit signed and unsigned INT |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| DECIMAL (INT32)                           |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| DECIMAL (INT64)                           |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| DECIMAL (BYTE_ARRAY)                      |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   (R)  |
| DECIMAL (FIXED_LEN_BYTE_ARRAY)            |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| DATE                                      |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| TIME (INT32)                              |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| TIME (INT64)                              |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| TIMESTAMP (INT64)                         |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| INTERVAL                                  |  ✅   |  ✅ (1)       |  ✅      |  ✅      |  ❌   |  ✅       |   ✅   |
| JSON                                      |  ✅   |  ✅ (1)       |  ✅      |  ✅ (1)  |  ❌   |  ✅       |   ✅   |
| BSON                                      |  ❌   |  ✅ (1)       |  ✅      |  ✅ (1)  |  ❌   |  ❌       |   ❌   |
| LIST                                      |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |   ✅   |
| MAP                                       |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |   ✅   |
| UNKNOWN (always null)                     |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| FLOAT16                                   |  ✅   |  ✅ (1)       |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |

* \(1) Only supported to use its annotated physical type

### Encodings

| Encoding                                  | arrow | parquet-java  | arrow-go | arrow-rs | cudf  | hyparquet | duckdb |
| ----------------------------------------- | ----- | ------------- | -------- | -------- | ----- | --------- | ------ |
| PLAIN                                     |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| PLAIN_DICTIONARY                          |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  (R)   |
| RLE_DICTIONARY                            |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| RLE                                       |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| BIT_PACKED (deprecated)                   |  ✅   |  ✅           |  ✅      |  ❌ (1)  |  (R)  |  (R)      |   ❌   |
| DELTA_BINARY_PACKED                       |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |   ✅   |
| DELTA_LENGTH_BYTE_ARRAY                   |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |   ✅   |
| DELTA_BYTE_ARRAY                          |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |   ✅   |
| BYTE_STREAM_SPLIT                         |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |   ✅   |

* \(1) Partial read support, but only in the case of level data with a bitwidth of 0

### Compressions

| Compression                               | arrow | parquet-java  | arrow-go | arrow-rs | cudf  | hyparquet | duckdb |
| ----------------------------------------- | ----- | ------------- | -------- | -------- | ----- | --------- | ------ |
| UNCOMPRESSED                              |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| BROTLI                                    |  ✅   |  ✅           |  ✅      |  ✅      |  (R)  |  (R)      |   ✅   |
| GZIP                                      |  ✅   |  ✅           |  ✅      |  ✅      |  (R)  |  (R)      |   ✅   |
| LZ4 (deprecated)                          |  ✅   |  ❌           |  ❌      |  ✅      |  ❌   |  (R)      |   ❌   |
| LZ4_RAW                                   |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |   ✅   |
| LZO                                       |  ❌   |  ❌           |  ❌      |  ❌      |  ❌   |  ❌       |   ❌   |
| SNAPPY                                    |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| ZSTD                                      |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |   ✅   |

### Other format level features

| Feature                                   | arrow | parquet-java  | arrow-go | arrow-rs | cudf  | hyparquet | duckdb |
| ----------------------------------------- | ----- | ------------- | -------- | -------- | ----- | --------- | ------ |
| xxHash-based bloom filters                |  (R)  |  ✅           |  ✅      |  ✅      |  (R)  |           |  ✅    |
| Bloom filter length (1)                   |  (R)  |  ✅           |  ✅      |  ✅      |  (R)  |           |  ✅    |
| Statistics min_value, max_value           |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |  ✅    |
| Page index                                |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  (R)      |  (R)   |
| Page CRC32 checksum                       |  ✅   |  ✅           |  ❌      |  ✅      |  ❌   |  ❌       |  (R)   |
| Modular encryption                        |  ✅   |  ✅           |  ✅      |  ✅      |  ❌   |  ❌       | ✅ (*) |
| Size statistics (2)                       |  ✅   |  ✅           |  (R)     |  ✅      |  ✅   |           |  (R)   |

* \(1) In parquet.thrift: ColumnMetaData->bloom_filter_length

* \(2) In parquet.thrift: ColumnMetaData->size_statistics

* (*) Partial support

### High level data APIs for Parquet feature usage

| Feature                                   | arrow | parquet-java  | arrow-go | arrow-rs | cudf  | hyparquet | duckdb |
| ----------------------------------------- | ----- | ------------- | -------- | -------- | ----- | --------- | ------ |
| External column data (1)                  |  ✅   |  ✅           |  ❌      |  ❌      |  (W)  |  ✅       |   ❌   |
| Row group "Sorting column" metadata (2)   |  ✅   |  ❌           |  ✅      |  ✅      |  (W)  |  ❌       |   (R)  |
| Row group pruning using statistics        |  ❌   |  ✅           |  ✅ (*)  |  ✅      |  ✅   |  ❌       |   ✅   |
| Row group pruning using bloom filter      |  ❌   |  ✅           |  ✅ (*)  |  ✅      |  ✅   |  ❌       |   ✅   |
| Reading select columns only               |  ✅   |  ✅           |  ✅      |  ✅      |  ✅   |  ✅       |   ✅   |
| Page pruning using statistics             |  ❌   |  ✅           |  ✅ (*)  |  ✅      |  ❌   |  ❌       |   ❌   |

* \(1) In parquet.thrift: ColumnChunk->file_path

* \(2) In parquet.thrift: RowGroup->sorting_columns

* (*) Partial Support
