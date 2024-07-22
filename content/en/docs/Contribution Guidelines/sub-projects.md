---
title: "Sub-Projects"
linkTitle: "Sub-Projects"
weight: 1
description: >

---

The [parquet-format](https://github.com/apache/parquet-format) project contains format specifications and Thrift definitions of metadata required to properly read Parquet files.

The [parquet-java](https://github.com/apache/parquet-java) project contains multiple sub-modules, which implement the core components of reading and writing a nested, column-oriented data stream, map this core onto the parquet format, and provide Hadoop Input/Output Formats, Pig loaders, and other Java-based utilities for interacting with Parquet.

The [parquet-cpp](https://arrow.apache.org/docs/cpp/parquet.html) project is a C++ library to read-write Parquet files. It is part of the [Apache Arrow](https://arrow.apache.org/) C++ implementation, with bindings to Python, R, Ruby and C/GLib.

The [parquet-rs](https://github.com/apache/arrow-rs/tree/master/parquet) project is a Rust library to read-write Parquet files.

The [parquet-compatibility](https://github.com/Parquet/parquet-compatibility) project (deprecated) contains compatibility tests that can be used to verify that implementations in different languages can read and write each other’s files. As of January 2022 compatibility tests only exist up to version 1.2.0.
