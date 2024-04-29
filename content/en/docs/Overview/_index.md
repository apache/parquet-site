---
title: "Overview"
linkTitle: "Overview"
weight: 1
description: >
  All about Parquet.
---

Apache Parquet is a columnar storage format available to any project in the Hadoop ecosystem, regardless of the choice of data processing framework, data model or programming language.

This documentation contains information about both the [parquet-mr](https://github.com/apache/parquet-mr) and [parquet-format](https://github.com/apache/parquet-format) projects. 


### Parquet Format

The "Parquet Format" project hosts the official specification of the Parquet file format, defining how data is structured and stored. This specification, along with Thrift metadata definitions and other crucial components, is essential for developers to effectively read and write Parquet files. The parquet-format project specifically contains the format specifications needed to understand and properly utilize Parquet files.

As a repository focused on specification, the parquet-format repository does not contain source code. 


### Parquet-MR 

The parquet-mr GitHub repository is part of the Apache Parquet project and specifically focuses on providing Java tools for handling the Parquet file format within the Hadoop ecosystem. Essentially, this repository includes all the necessary Java libraries and modules that allow developers to read and write Parquet files.

Parquet-MR can be seen as a "reference" implementation of parquet-format. There are a number of other Parquet Format implementations, which are listed below. 

Included in parquet-mr:
* Java/Scala Implementation: It contains the core Java/Scala implementation of the Parquet format, making it possible to use Parquet files in Java applications, particularly those based on Hadoop.

* Utilities and APIs: It provides various utilities and APIs for working with Parquet files, including tools for data import/export, schema management, and data conversion.


###  Other Clients / Libraries / Tools

The Parquet ecosystem is rich and varied, encompassing a wide array of tools, libraries, and clients, each offering different levels of feature support. It's important to note that not all implementations support the same features of the Parquet format. When integrating multiple Parquet implementations within your workflow, it is crucial to conduct thorough testing to ensure compatibility and performance across different platforms and tools.

Here is a non-exhaustive list of Parquet implementations:

* [parquet-mr](https://github.com/apache/parquet-mr)
* [parquet-cpp](https://github.com/apache/parquet-cpp)
* [parquet rust](https://github.com/apache/arrow-rs/blob/master/parquet/README.md)
* [cudf](https://github.com/rapidsai/cudf)
* [impala](https://github.com/apache/impala)
* [duckdb](https://github.com/duckdb/duckdb)