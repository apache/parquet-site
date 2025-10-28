---
title: "Overview"
linkTitle: "Overview"
weight: 1
description: >
  All about Parquet.
---

Apache Parquet is an open source, column-oriented data file format designed for efficient data storage and retrieval.
It provides high performance compression and encoding schemes to handle complex data in bulk and is supported in many programming language and analytics tools.


### parquet-format (Specification)

The [parquet-format] repository hosts the official specification of the Parquet file format, defining how data is structured and stored. This specification, along with the [parquet.thrift] Thrift metadata definitions, is necessary for developing software to effectively read and write Parquet files. 

Note that the parquet-format repository does not contain source code for libraries to read or write Parquet files, but rather the formal definitions and documentation of the file format itself.

[parquet-format]: https://github.com/apache/parquet-format
[parquet.thrift]: https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift

### parquet-java 

The [parquet-java] (formerly named `parquet-mr`) repository is part of the Apache Parquet project and contains:
* Java libraries to read and write Parquet files in Java applications.
* Utilities and APIs for working with Parquet files, including tools for data import/export, schema management, and data conversion.

Note that there are a number of other implementations of the Parquet format, some of which are listed below. 

[parquet-java]: https://github.com/apache/parquet-java

###  Other Clients / Libraries / Tools

The Parquet ecosystem is rich and varied, encompassing a wide array of tools, libraries, and clients, each offering different levels of feature support. It's important to note that not all implementations support the same features of the Parquet format. When integrating multiple Parquet implementations within your workflow, it is crucial to conduct thorough testing to ensure compatibility and performance across different platforms and tools.

You can find more information about the feature support of various Parquet implementations on the [implementation status] page.

[implementation status]: /docs/file-format/implementationstatus

Here is a non-exhaustive list of open source Parquet implementations:

* [Parquet-java](https://github.com/apache/parquet-java)
* [Parquet C++, a subproject of Arrow C++](https://github.com/apache/arrow/tree/main/cpp/src/parquet) ([documentation](https://arrow.apache.org/docs/cpp/parquet.html))
* [Parquet Go, a subproject of Arrow Go](https://github.com/apache/arrow-go/tree/main/parquet) ([documentation](https://github.com/apache/arrow-go/tree/main/parquet))
* [Parquet Rust, a subproject of Arrow Rust](https://github.com/apache/arrow-rs/blob/main/parquet/README.md)
* [cuDF](https://github.com/rapidsai/cudf)
* [Apache Impala](https://github.com/apache/impala)
* [DuckDB](https://github.com/duckdb/duckdb)
* [fastparquet, a Python implementation of the Apache Parquet format](https://github.com/dask/fastparquet)
