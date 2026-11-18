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

This page describes the security policy of the Apache Parquet project: how to
report a suspected vulnerability, and what the project does and does not
consider a security issue.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately to the Apache Software
Foundation (ASF) security team at
[security@apache.org](mailto:security@apache.org), who will triage the report
and coordinate with the relevant project. Do **not** file a public GitHub issue
or pull request for a suspected vulnerability, as that would disclose it before
a fix is available.

The ASF vulnerability handling process is described at
<https://www.apache.org/security/>.

## Parquet is a File Format, Not an Implementation

Apache Parquet is a file format. The format is defined by the specification in
the [parquet-format] repository, and it is read and written by many independent
implementations, several of which are maintained by projects other than Apache
Parquet.

Most security issues, such as crashes, out-of-bounds memory access, or
excessive resource consumption when reading a file, are issues in a particular
implementation rather than in the format. Each implementation has its own
threat model, security policy, and release process. Please consult the security
information for the implementation you use, for example:

| Implementation | Security information |
|----------------|----------------------|
| [parquet-java] | [SECURITY.md](https://github.com/apache/parquet-java/blob/master/SECURITY.md) |
| Parquet C++ (part of [Apache Arrow]) | [Apache Arrow security](https://arrow.apache.org/security/) |
| [arrow-rs] (the Rust `parquet` crate) | [SECURITY.md](https://github.com/apache/arrow-rs/blob/main/SECURITY.md) |

For any other implementation, see that project's documentation.

[parquet-format]: https://github.com/apache/parquet-format
[parquet-java]: https://github.com/apache/parquet-java
[Apache Arrow]: https://arrow.apache.org/
[arrow-rs]: https://github.com/apache/arrow-rs

## General Security Posture

The following applies to the format itself, and describes what users and
implementers of Parquet should assume.

### Parquet files may come from untrusted sources

Parquet files are frequently exchanged between systems and organizations.
Implementations should treat the contents of a file, both data and metadata, as
untrusted input and validate it before use. Reading a malformed or malicious
file should result in an error or in incorrect data, and not in memory
corruption, code execution, or disclosure of information from outside the file.
The extent to which each implementation guarantees this, and the resource
limits (memory, time, input size) that applications are expected to impose
themselves, are described in that implementation's security information.

### Incorrect results from a crafted file are not a security issue

Whoever writes a Parquet file controls its entire contents. A file whose
contents are internally inconsistent can cause a reader to return incorrect
results, or cause different readers (or the same reader with different
settings) to return different results for the same file. The Parquet project
does not consider this a security issue: a party able to craft such a file
could equally have written different data values in the first place.

In particular, the metadata that readers use to skip data, such as
[statistics], the [page index], and [bloom filters], is an optimization and
**not a security control**. A reader that uses this metadata for filter
pushdown trusts it to describe the data accurately. If it does not, for example
because the minimum and maximum values recorded for a column chunk do not match
the values actually stored, rows may be silently omitted from query results.
Likewise, other fields in the metadata, such as row counts and null counts, may
be used to answer queries without reading the data.

Systems must therefore not rely on the contents of a Parquet file to enforce
security decisions (such as access control or row-level filtering) unless they
trust the writer of that file.

[statistics]: https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift
[page index]: https://github.com/apache/parquet-format/blob/master/PageIndex.md
[bloom filters]: https://github.com/apache/parquet-format/blob/master/BloomFilter.md

### Integrity and authenticity

By default, a Parquet file carries no proof of who wrote it or that it has not
been modified. The optional page checksums (CRC) detect accidental corruption
only and offer no protection against deliberate modification.

Applications that need to detect tampering should either use
[Parquet Modular Encryption], which can protect both the confidentiality and
the integrity of data and metadata against parties that do not hold the keys,
or use a mechanism external to the file, such as digital signatures or access
controls on the underlying storage. Note that none of these mechanisms protects
against a writer that is authorized but malicious or faulty.

[Parquet Modular Encryption]: https://github.com/apache/parquet-format/blob/master/Encryption.md

### What is a security issue in the format

Examples of issues that the Parquet project would treat as security issues in
the format specification include:

* A flaw in the design of Parquet Modular Encryption that weakens the
  confidentiality or integrity guarantees it describes.
* A requirement in the specification that cannot be implemented without
  exposing readers or writers to a vulnerability.

If you are unsure whether an issue is in the format or in an implementation, or
whether it is a security issue at all, please err on the side of reporting it
privately as described above.
