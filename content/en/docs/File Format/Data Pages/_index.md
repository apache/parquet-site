---
title: "Data Pages"
linkTitle: "Data Pages"
weight: 7
---
For data pages, the 3 pieces of information are encoded back to back, after the page
header. No padding is allowed in the data page.
In order we have:
 1. repetition levels data
 1. definition levels data
 1. encoded values

The value of `uncompressed_page_size` specified in the header is for all the 3 pieces combined.

The encoded values for the data page is always required.  The definition and repetition levels
are optional, based on the schema definition.  If the column is not nested (i.e.
the path to the column has length 1), we do not encode the repetition levels (it would
always have the value 1).  For data that is required, the definition levels are
skipped (if encoded, it will always have the value of the max definition level).

For example, in the case where the column is non-nested and required, the data in the
page is only the encoded values.

The supported encodings are described in [Encodings.md](https://github.com/apache/parquet-format/blob/master/Encodings.md)

The supported compression codecs are described in
[Compression.md](https://github.com/apache/parquet-format/blob/master/Compression.md)
