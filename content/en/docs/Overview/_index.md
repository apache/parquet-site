---
title: "Overview"
linkTitle: "Overview"
weight: 1
description: >
  All about Parquet.
---

Apache Parquet is an open source, column-oriented data file format designed for efficient data storage and retrieval.
It provides high performance compression and encoding schemes to handle complex data in bulk and is supported in many programming language and analytics tools.

This documentation contains information about both the [parquet-java](https://github.com/apache/parquet-java) and [parquet-format](https://github.com/apache/parquet-format) repositories. 

### parquet-format

The parquet-format repository hosts the official specification of the Apache Parquet file format, defining how data is structured and stored. This specification, along with Thrift metadata definitions and other crucial components, is essential for developers to effectively read and write Parquet files. The parquet-format project specifically contains the format specifications needed to understand and properly utilize Parquet files.

As a repository focused on specification, the parquet-format repository does not contain source code. 


### parquet-java 

The parquet-java (formerly named 'parquet-mr') repository is part of the Apache Parquet project and specifically focuses on providing Java tools for handling the Parquet file format. Essentially, this repository includes all the necessary Java libraries and modules that allow developers to read and write Apache Parquet files.

The parquet-java repository contains an implementation of the Apache Parquet format. There are a number of other Parquet format implementations, which are listed below. 

Included in parquet-java:
* Java Implementation: It contains the core Java implementation of the Apache Parquet format, making it possible to use Parquet files in Java applications.

* Utilities and APIs: It provides various utilities and APIs for working with Apache Parquet files, including tools for data import/export, schema management, and data conversion.


###  Other Clients / Libraries / Tools

The Parquet ecosystem is rich and varied, encompassing a wide array of tools, libraries, and clients, each offering different levels of feature support. It's important to note that not all implementations support the same features of the Parquet format. When integrating multiple Parquet implementations within your workflow, it is crucial to conduct thorough testing to ensure compatibility and performance across different platforms and tools.

Here is a non-exhaustive list of Parquet implementations:

* [Parquet-java](https://github.com/apache/parquet-java)
* [Parquet C++, a subproject of Arrow C++](https://github.com/apache/arrow/tree/main/cpp/src/parquet) ([documentation](https://arrow.apache.org/docs/cpp/parquet.html))
* [Parquet Go, a subproject for Arrow Go](https://github.com/apache/arrow-go/tree/main/parquet) ([documentation](https://github.com/apache/arrow-go/tree/main/parquet))
* [Parquet Rust](https://github.com/apache/arrow-rs/blob/main/parquet/README.md)
* [cuDF](https://github.com/rapidsai/cudf)
* [Apache Impala](https://github.com/apache/impala)
* [DuckDB](https://github.com/duckdb/duckdb)
* [fastparquet, a Python implementation of the Apache Parquet format](https://github.com/dask/fastparquet)
