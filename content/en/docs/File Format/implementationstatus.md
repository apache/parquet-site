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
* `C++`: [parquet-cpp](https://github.com/apache/arrow/tree/main/cpp/src/parquet)
* `Java`: [parquet-java](https://github.com/apache/parquet-java)
* `Go`: [parquet-go](https://github.com/apache/arrow-go/tree/main/parquet)
* `Rust`: [parquet-rs](https://github.com/apache/arrow-rs/blob/main/parquet/README.md)
* `cuDF`: [cudf](https://github.com/rapidsai/cudf)
* `JavaScript`: [hyparquet](https://github.com/hyparam/hyparquet)


### Physical types

| Data type                                 | C++   | Java  | Go    | Rust  | cuDF  | hyparquet |
| ----------------------------------------- | ----- | ----- | ----- | ----- | ----- | --------- |
| BOOLEAN                                   |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| INT32                                     |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| INT64                                     |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| INT96 (1)                                 |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| FLOAT                                     |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| DOUBLE                                    |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| BYTE_ARRAY                                |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| FIXED_LEN_BYTE_ARRAY                      |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |

* \(1) This type is deprecated, but as of 2024 it's common in currently produced parquet files


### Logical types

| Data type                                 | C++   | Java  | Go    | Rust  | cuDF  | hyparquet |
| ----------------------------------------- | ----- | ----- | ----- | ----- | ----- | --------- |
| STRING                                    |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| ENUM                                      |  ❌   |  ✅   |       |  ✅(*)|  ❌   | (R)       |
| UUID                                      |  ❌   |  ✅   |       |  ✅(*)|  ❌   | (R)       |
| 8, 16, 32, 64 bit signed and unsigned INT |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| DECIMAL (INT32)                           |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| DECIMAL (INT64)                           |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| DECIMAL (BYTE_ARRAY)                      |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| DECIMAL (FIXED_LEN_BYTE_ARRAY)            |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| DATE                                      |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| TIME (INT32)                              |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| TIME (INT64)                              |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| TIMESTAMP (INT64)                         |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| INTERVAL                                  |  ✅   |  ✅(*)|       |  ✅   |  ❌   | (R)       |
| JSON                                      |  ✅   |  ✅(*)|       |  ✅(*)|  ❌   | (R)       |
| BSON                                      |  ❌   |  ✅(*)|       |  ✅(*)|  ❌   | (R)       |
| LIST                                      |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| MAP                                       |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| UNKNOWN (always null)                     |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| FLOAT16                                   |  ✅   |  ✅(*)|       |  ✅   |  ✅   | (R)       |

(*): Only supported to use its annotated physical type

### Encodings

| Encoding                                  | C++   | Java  | Go    | Rust  | cuDF  | hyparquet |
| ----------------------------------------- | ----- | ----- | ----- | ----- | ----- | --------- |
| PLAIN                                     |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| PLAIN_DICTIONARY                          |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| RLE_DICTIONARY                            |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| RLE                                       |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| BIT_PACKED (deprecated)                   |  ✅   |  ✅   |       |  ❌(*)|  (R)  | (R)       |
| DELTA_BINARY_PACKED                       |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| DELTA_LENGTH_BYTE_ARRAY                   |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| DELTA_BYTE_ARRAY                          |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| BYTE_STREAM_SPLIT                         |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |

(*): Partial read support, but only in the case of level data with a bitwidth of 0

### Compressions

| Compression                               | C++   | Java  | Go    | Rust  | cuDF  | hyparquet |
| ----------------------------------------- | ----- | ----- | ----- | ----- | ----- | --------- |
| UNCOMPRESSED                              |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| BROTLI                                    |  ✅   |  ✅   |       |  ✅   |  (R)  | (R)       |
| GZIP                                      |  ✅   |  ✅   |       |  ✅   |  (R)  | (R)       |
| LZ4 (deprecated)                          |  ✅   |  ❌   |       |  ✅   |  ❌   | (R)       |
| LZ4_RAW                                   |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| LZO                                       |  ❌   |  ❌   |       |  ❌   |  ❌   | ❌        |
| SNAPPY                                    |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| ZSTD                                      |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |

### Other format level features

|                                           | C++   | Java  | Go    | Rust  | cuDF  | hyparquet |
| ----------------------------------------- | ----- | ----- | ----- | ----- | ----- | --------- |
| xxHash-based bloom filters                |  (R)  |  ✅   |       |  ✅   |  (R)  |           |
| Bloom filter length (1)                   |  (R)  |  ✅   |       |  ✅   |  (R)  |           |
| Statistics min_value, max_value           |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| Page index                                |  ✅   |  ✅   |       |  ✅   |  ✅   | (R)       |
| Page CRC32 checksum                       |  ✅   |  ✅   |       |  ✅   |  ❌   | ❌        |
| Modular encryption                        |  ✅   |  ✅   |       |  ❌   |  ❌   | ❌        |
| Size statistics (2)                       |  ✅   |  ✅   |       |  ✅   |  ✅   |           |


* \(1) In parquet.thrift: ColumnMetaData->bloom_filter_length

* \(2) In parquet.thrift: ColumnMetaData->size_statistics

### High level data APIs for Parquet feature usage

| Format                                       | C++   | Java  | Go    | Rust  | cuDF  | hyparquet |
| -------------------------------------------- | ----- | ----- | ----- | ----- | ----- | --------- |
| External column data (1)                     |  ✅   |  ✅   |       |  ❌   |  (W)  | ❌        |
| Row group "Sorting column" metadata (2)      |  ✅   |  ❌   |       |  ✅   |  (W)  | ❌        |
| Row group pruning using statistics           |  ❌   |  ✅   |       |  ✅   |  ✅   | ❌        |
| Row group pruning using bloom filter         |  ❌   |  ✅   |       |  ✅   |  ✅   | ❌        |
| Reading select columns only                  |  ✅   |  ✅   |       |  ✅   |  ✅   | ✅        |
| Page pruning using statistics                |  ❌   |  ✅   |       |  ✅   |  ❌   | ❌        |


* \(1) In parquet.thrift: ColumnChunk->file_path

* \(2) In parquet.thrift: RowGroup->sorting_columns
