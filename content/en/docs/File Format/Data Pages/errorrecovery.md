---
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
