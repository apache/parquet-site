---
title: "Compression"
linkTitle: "Compression"
weight: 1
---

## Overview

Parquet allows the data block inside dictionary pages and data pages to
be compressed for better space efficiency. The Parquet format supports
several compression covering different areas in the compression ratio /
processing cost spectrum.

The detailed specifications of compression codecs are maintained externally
by their respective authors or maintainers, which we reference hereafter.

For all compression codecs except the deprecated `LZ4` codec, the raw data
of a (data or dictionary) page is fed *as-is* to the underlying compression
library, without any additional framing or padding.  The information required
for precise allocation of compressed and decompressed buffers is written
in the `PageHeader` struct.

## Codecs

### UNCOMPRESSED

No-op codec.  Data is left uncompressed.

### SNAPPY

A codec based on the
[Snappy compression format](https://github.com/google/snappy/blob/master/format_description.txt).
If any ambiguity arises when implementing this format, the implementation
provided by Google Snappy [library](https://github.com/google/snappy/)
is authoritative.

### GZIP

A codec based on the GZIP format (not the closely-related "zlib" or "deflate"
formats) defined by [RFC 1952](https://tools.ietf.org/html/rfc1952).
If any ambiguity arises when implementing this format, the implementation
provided by the [zlib compression library](https://zlib.net/) is authoritative.

Readers should support reading pages containing multiple GZIP members, however,
as this has historically not been supported by all implementations, it is recommended
that writers refrain from creating such pages by default for better interoperability.

### LZO

A codec based on or interoperable with the
[LZO compression library](https://www.oberhumer.com/opensource/lzo/).

### BROTLI

A codec based on the Brotli format defined by
[RFC 7932](https://tools.ietf.org/html/rfc7932).
If any ambiguity arises when implementing this format, the implementation
provided by the  [Brotli compression library](https://github.com/google/brotli)
is authoritative.

### LZ4

A **deprecated** codec loosely based on the LZ4 compression algorithm,
but with an additional undocumented framing scheme.  The framing is part
of the original Hadoop compression library and was historically copied
first in parquet-mr, then emulated with mixed results by parquet-cpp.

It is strongly suggested that implementors of Parquet writers deprecate
this compression codec in their user-facing APIs, and advise users to
switch to the newer, interoperable `LZ4_RAW` codec.

### ZSTD

A codec based on the Zstandard format defined by
[RFC 8478](https://tools.ietf.org/html/rfc8478).  If any ambiguity arises
when implementing this format, the implementation provided by the
[Zstandard compression library](https://facebook.github.io/zstd/)
is authoritative.

### LZ4_RAW

A codec based on the [LZ4 block format](https://github.com/lz4/lz4/blob/dev/doc/lz4_Block_format.md).
If any ambiguity arises when implementing this format, the implementation
provided by the [LZ4 compression library](https://www.lz4.org/) is authoritative.
