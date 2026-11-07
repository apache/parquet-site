---
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

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
* [ClickHouse](https://github.com/ClickHouse/ClickHouse/tree/master/src/Processors/Formats/Impl/Parquet) (C++)
* [cudf](https://github.com/rapidsai/cudf) (cuDF C++)
* [hyparquet](https://github.com/hyparam/hyparquet) (JavaScript)
* [duckdb](https://github.com/duckdb/duckdb) (C++)
* [polars](https://github.com/pola-rs/polars) (Rust)
* [DataHaskell](https://github.com/DataHaskell/dataframe) (Haskell)

<!-- Data driven table, see /layouts/shortcodes -->
{{< implementation-status >}}
