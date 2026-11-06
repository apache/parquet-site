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

title: "Metadata"
linkTitle: "Metadata"
weight: 5
---
There are two types of metadata: file metadata, and page header metadata.

All thrift structures are serialized using the TCompactProtocol. The full
definition of these structures is given in the Parquet
[Thrift definition](https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift).

## File metadata

In the diagram below, file metadata is described by the `FileMetaData`
structure. This file metadata provides offset and size information useful
when navigating the Parquet file.

![Parquet Metadata format](/images/FileMetaData.svg)

## Page header

Page header metadata (`PageHeader` and children in the diagram) is stored
in-line with the page data, and is used in the reading and decoding of data.

![Parquet PageHeader format](/images/PageHeader.svg)

