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
Each data page is compressed on its own. To read any value in a page, a reader
must decompress and decode the whole page. Small pages help selective reads, such
as single row lookups, when the reader skips the pages that it does not need.
Large pages have fewer page headers and fewer page index entries, so they use less
space and less parsing time. Large pages can also compress better. The gain
depends on the data, the encoding, the compression codec, and the codec settings.

A page is not always the unit of IO. Readers can combine adjacent pages into one
larger read, mostly in sequential scans. Cloud object storage has a high latency
for each request. If your files are on such storage, check how your reader
buffers and combines reads before you choose a page size. Some readers decompress
and decode pages in parallel. For these readers, the page size also changes the
amount of parallel work.

No single page size is best for all workloads. Start with the default of your
writer. Then benchmark representative data and queries with the readers and the
storage system that you plan to use. Compare the compression ratio, the metadata
size, the scan throughput, and the speed of selective reads. Include the data
types and value sizes that your workload uses.
