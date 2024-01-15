---
title: "Checksumming"
linkTitle: "Checksumming"
weight: 7
---
Pages of all kinds can be individually checksummed. This allows disabling of checksums
at the HDFS file level, to better support single row lookups. Checksums are calculated
using the standard CRC32 algorithm - as used in e.g. GZip - on the serialized binary
representation of a page (not including the page header itself).
