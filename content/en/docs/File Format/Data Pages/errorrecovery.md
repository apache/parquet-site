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

title: "Error Recovery"
linkTitle: "Error Recovery"
weight: 7
---
If the file metadata is corrupt, the file is lost.  If the column metadata is corrupt,
that column chunk is lost (but column chunks for this column in other row groups are
okay).  If a page header is corrupt, the remaining pages in that chunk are lost.  If
the data within a page is corrupt, that page is lost.  The file will be more
resilient to corruption with smaller row groups.

Potential extension: With smaller row groups, the biggest issue is placing the file
metadata at the end.  If an error happens while writing the file metadata, all the
data written will be unreadable.  This can be fixed by writing the file metadata
every Nth row group.
Each file metadata would be cumulative and include all the row groups written so
far.  Combining this with the strategy used for rc or avro files using sync markers,
a reader could recover partially written files.
