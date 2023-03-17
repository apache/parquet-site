---
title: "Column Chunks"
linkTitle: "Column Chunks"
weight: 7
---
Column chunks are composed of pages written back to back.  The pages share a common
header and readers can skip over pages they are not interested in.  The data for the
page follows the header and can be compressed and/or encoded.  The compression and
encoding is specified in the page metadata.

A column chunk might be partly or completely dictionary encoded. It means that
dictionary indexes are saved in the data pages instead of the actual values. The
actual values are stored in the dictionary page. See details in
[Encodings.md](https://github.com/apache/parquet-format/blob/master/Encodings.md#dictionary-encoding-plain_dictionary--2-and-rle_dictionary--8).
The dictionary page must be placed at the first position of the column chunk. At
most one dictionary page can be placed in a column chunk.

Additionally, files can contain an optional column index to allow readers to
skip pages more efficiently. See [PageIndex.md](PageIndex.md) for details and
the reasoning behind adding these to the format.
