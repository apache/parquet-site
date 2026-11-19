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

title: "Configurations"
linkTitle: "Configurations"
weight: 5
---

### Row Group Size

Larger row groups allow for larger column chunks which makes it
possible to do larger sequential IO.  Larger groups also require more buffering in
the write path (or a two pass write).  We recommend large row groups (512MB - 1GB).
Since an entire row group might need to be read, we want it to completely fit on
one HDFS block.  Therefore, HDFS block sizes should also be set to be larger.  An
optimized read setup would be: 1GB row groups, 1GB HDFS block size, 1 HDFS block
per HDFS file.

### Data Page Size
Data page size is a tradeoff. Small pages are better for point lookups, because a
reader decompresses and decodes less data to read one value. Large pages need less
metadata, because a column chunk has fewer page headers and fewer page index
entries. Large pages also compress and encode better.

A page is not necessarily the unit of IO. Readers can combine the fetches of
adjacent pages into one larger read to reduce IO time.

No single page size fits all workloads. Choose the page size for the workload,
the storage system, and the engine that reads the files.
