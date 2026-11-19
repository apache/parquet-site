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
Data pages are the unit of compression and encoding, so a reader must decompress
and decode a whole page to read any value in it. The right size depends on the
workload; there is no single best value.

Smaller pages allow more fine grained reading (e.g. point lookups or selective
filters combined with the [page index](../pageindex/)), since less unneeded data
is decompressed and decoded.

Larger pages:
* compress better, since each page is compressed independently. How much this
  helps depends on the codec: codecs with small windows (e.g. Snappy, Gzip) gain
  little beyond a few tens of KB, while ZSTD can benefit from larger pages.
* have less overhead from page headers and their parsing.
* produce smaller page indexes, since there is one entry per page.

Page size does not determine IO size: for sequential scans, readers typically
read whole column chunks (or large ranges of them) rather than one page at a
time.

Most implementations (e.g. parquet-java, Arrow C++, Arrow Rust) default to a 1MB
page size target, often combined with a cap on the number of rows per page.
Sizes in the range of 64KB to 1MB work well for most workloads.
