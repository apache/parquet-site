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

title: "Security"
linkTitle: "Security"
weight: 2
---

This page describes the security policy of the Apache Parquet project.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately to the Apache Software
Foundation (ASF) security team at
[security@apache.org](mailto:security@apache.org), who will triage the report
and coordinate with the relevant project. Do **not** file a public GitHub issue
or pull request for a suspected vulnerability, as that would disclose it before
a fix is available.

The ASF vulnerability handling process is described at
<https://www.apache.org/security/>.

## Security Model

Parquet files are frequently exchanged between systems and organizations.
Implementations should treat the contents of a file, both data and metadata, as
untrusted input and validate it before use. Reading a malformed or malicious
file should result in an error or incorrect data, not in memory corruption, code
execution, or disclosure of information from outside the file.

Apache Parquet is a file format that is read and written by many independent
implementations. Therefore, most security issues related to Parquet are specific
to a particular implementation rather than the format, and you should consult
the security policy for that implementation. For example:

| Implementation | Security information |
|----------------|----------------------|
| [parquet-java] | [SECURITY.md](https://github.com/apache/parquet-java/blob/master/SECURITY.md) |
| Parquet C++ (part of [Apache Arrow]) | [Apache Arrow security](https://arrow.apache.org/security/) |
| [arrow-rs] (the Rust `parquet` crate) | [SECURITY.md](https://github.com/apache/arrow-rs/blob/main/SECURITY.md) |

[parquet-format]: https://github.com/apache/parquet-format
[parquet-java]: https://github.com/apache/parquet-java
[Apache Arrow]: https://arrow.apache.org/
[arrow-rs]: https://github.com/apache/arrow-rs

