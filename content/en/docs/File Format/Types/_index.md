---
title: "Types"
linkTitle: "Types"
weight: 5
---

The types supported by the file format are intended to be as minimal as possible,
with a focus on how the types effect on disk storage.  For example, 16-bit ints
are not explicitly supported in the storage format since they are covered by
32-bit ints with an efficient encoding.  This reduces the complexity of implementing
readers and writers for the format.  The types are:

  - BOOLEAN: 1 bit boolean
  - INT32: 32 bit signed ints
  - INT64: 64 bit signed ints
  - INT96: 96 bit signed ints
  - FLOAT: IEEE 32-bit floating point values
  - DOUBLE: IEEE 64-bit floating point values
  - BYTE_ARRAY: arbitrarily long byte arrays
  - FIXED_LEN_BYTE_ARRAY: fixed length byte arrays
