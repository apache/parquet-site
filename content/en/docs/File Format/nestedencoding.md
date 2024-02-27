---
title: "Nested Encoding"
linkTitle: "Nested Encoding"
weight: 6
---
To encode nested columns, Parquet uses the Dremel encoding with definition and
repetition levels.  Definition levels specify how many optional fields in the
path for the column are defined.  Repetition levels specify at what repeated field
in the path has the value repeated.  The max definition and repetition levels can
be computed from the schema (i.e. how much nesting there is).  This defines the
maximum number of bits required to store the levels (levels are defined for all
values in the column).

Two encodings for the levels are supported BIT_PACKED and RLE. Only RLE is now used as it supersedes BIT_PACKED.
