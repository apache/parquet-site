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
Data pages are compressed independently. Smaller pages can reduce unnecessary
decompression and decoding for selective reads (e.g. single row lookups), when the
reader can skip pages. Larger pages reduce the number of page headers and page
index entries, saving space and parsing overhead. They can also improve
compression, depending on the data, encoding, compression codec, and codec
settings.

A page is not necessarily the unit of IO: readers can combine adjacent pages into
larger reads, particularly for sequential scans. On storage with high request
latency, such as cloud object storage, consider the reader's buffering and read
coalescing behavior when choosing a page size. Page size can also affect
parallelism in readers that decompress or decode pages in parallel.

There is no single page size that is best for all workloads. Start with the
writer's default and benchmark representative data and queries using the intended
readers and storage system. Consider data types and value sizes, compression
ratio, metadata overhead, and the tradeoff between scan throughput and selective
read performance.
