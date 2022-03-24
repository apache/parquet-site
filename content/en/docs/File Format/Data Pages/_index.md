---
title: "Data Pages"
linkTitle: "Data Pages"
weight: 7
---
For data pages, the 3 pieces of information are encoded back to back, after the page header. We have the

* definition levels data,
* repetition levels data,
* encoded values. The size of specified in the header is for all 3 pieces combined.

The data for the data page is always required. The definition and repetition levels are optional, based on the schema definition. If the column is not nested (i.e. the path to the column has length 1), we do not encode the repetition levels (it would always have the value 1). For data that is required, the definition levels are skipped (if encoded, it will always have the value of the max definition level).

For example, in the case where the column is non-nested and required, the data in the page is only the encoded values.

The supported encodings are described in Encodings.md
