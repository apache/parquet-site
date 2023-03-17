---
title: "Logical Types"
linkTitle: "Logical Types"
weight: 5
---

Logical types are used to extend the types that parquet can be used to store,
by specifying how the primitive types should be interpreted. This keeps the set
of primitive types to a minimum and reuses parquet's efficient encodings. For
example, strings are stored as byte arrays (binary) with a UTF8 annotation.
These annotations define how to further decode and interpret the data.
Annotations are stored as `LogicalType` fields in the file metadata and are
documented in [LogicalTypes.md](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md).
