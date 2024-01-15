---
title: "Nulls"
linkTitle: "Nulls"
weight: 7
---
Nullity is encoded in the definition levels (which is run-length encoded).  NULL values
are not encoded in the data.  For example, in a non-nested schema, a column with 1000 NULLs
would be encoded with run-length encoding (0, 1000 times) for the definition levels and
nothing else.
