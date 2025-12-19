---
title: "Implementation status"
linkTitle: "Implementation status"
weight: 8
---

This page summarizes the features supported by different Parquet
implementations.

*Note*: If you find out of date information, please help us improve the accuracy
of this page by opening an issue or submitting a pull request.

### Legend
The value in each box means:
* ✅: supported. Footnote added when support is partial. When data is available, links to release notes are provided on the implementing version.
* ❌: not supported
* (R): only read support
* (W): only write support
* (blank): no data

### Implementations
* [arrow](https://github.com/apache/arrow/tree/main/cpp/src/parquet) (C++)
* [parquet-java](https://github.com/apache/parquet-java) (Java)
* [arrow-go](https://github.com/apache/arrow-go/tree/main/parquet) (Go)
* [arrow-rs](https://github.com/apache/arrow-rs/blob/main/parquet/README.md) (Rust)
* [cudf](https://github.com/rapidsai/cudf) (cuDF C++)
* [hyparquet](https://github.com/hyparam/hyparquet) (JavaScript)
* [duckdb](https://github.com/duckdb/duckdb) (C++)

<!-- Status source in data/implementations -->
{{< implementation-status >}}
