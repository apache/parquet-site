---
title: "Parquet format versions"
linkTitle: "Features and Versions"
weight: 9
---

This page describes how features are added to the [Parquet format
specification](https://github.com/apache/parquet-format) and how they affect
reader and writer compatibility. See the
[Implementation status](../implementationstatus/) page for which implementations
(arrow, parquet-java, arrow-rs, etc.) support each feature.

*Note*: If you find out-of-date information, please open an issue or pull request.

## Feature compatibility

The Parquet format spec [classifies changes] by their effect on reader and
writer compatibility. Changes differ in their *forward* compatibility — whether
an older reader can read files that use a newer feature.

**Forward compatible** features remain **readable by older readers**, with a
possibly degraded experience: some metadata may be missing or performance may
suffer, but the reader does not fail. Examples:

* **Bloom filters**: a reader that ignores them skips the pruning metadata but
  still reads the data correctly.
* **Logical type annotations** such as `VARIANT`: an older reader reads the
  underlying physical column (e.g. `BYTE_ARRAY`) as raw bytes without applying
  the logical type.

**Forward incompatible** features make the data **unreadable** to older software.
Examples:

* **New encodings** (e.g. the `DELTA_*` encodings, `BYTE_STREAM_SPLIT`,
  `RLE_DICTIONARY`): a reader that does not implement them cannot decode the
  column values.
* **Data Page V2 headers**: a reader that only understands `DataPageHeader`
  cannot parse `DataPageHeaderV2` pages.

[classifies changes]: https://github.com/apache/parquet-format/blob/master/CONTRIBUTING.md#compatibility-and-feature-enablement

## `FileMetadata` version field

Each Parquet file has a `version` field in the [`thrift FileMetadata`]. This
field has historically been used inconsistently: writers populate `1` or `2`
without a consistent relationship to the features actually used. See the
[note in parquet.thrift] and [this discussion][closing-out-2.0] for details.

## `parquet-format` release versions

The Thrift definition is released independently of implementations such as
parquet-java or arrow-rs, following the Apache release process. This
release version is not recorded in the FileMetaData. Note that
release numbering **DOES NOT FOLLOW** [semantic versioning]:
minor releases (e.g. `2.10.0` to `2.11.0`) sometimes contain forward
incompatible features.

## Adding new features

New features are added by discussion and voting on the [parquet dev mailing list]
(full process in the [contributing guide]). Once approved, a feature is added to the spec and ships in
the next parquet-format release.

[parquet dev mailing list]: https://lists.apache.org/list.html?dev@parquet.apache.org
[semantic versioning]: https://semver.org/
[`thrift FileMetadata`]: https://github.com/apache/parquet-format/blob/c42c2cb4ecfccb38153375e24b702a82fd763cc0/src/main/thrift/parquet.thrift#L1365-L1373
[contributing guide]: https://github.com/apache/parquet-format/blob/master/CONTRIBUTING.md#additionschanges-to-the-format
[note in parquet.thrift]: https://github.com/apache/parquet-format/blob/74001e41f5c5a1856b29be115f9c992cab16a4bf/src/main/thrift/parquet.thrift#L1368-L1373
[closing-out-2.0]: https://lists.apache.org/thread/0bdyyb7qobrxx94x8v7t5z7g2ksnpyr2

## Forward incompatible features by version

Forward incompatible features and the format version each became available in:

| Feature | Released in | Source | Notes |
| ------------------------------------------ | ----------------------------- | --- | ------------------------- |
| [BOOLEAN] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [INT32] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [INT64] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [INT96 (deprecated)] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [FLOAT] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [DOUBLE] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [BYTE_ARRAY] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [FIXED_LEN_BYTE_ARRAY] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [Data Page V1] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [Data Page V2] | [2.0.0] | [1.0.0..2.0.0] |  |
| [PLAIN] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [PLAIN_DICTIONARY] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [RLE] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [BIT_PACKED (deprecated)] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [RLE_DICTIONARY] | [2.0.0] | [1.0.0..2.0.0] |  |
| [DELTA_BINARY_PACKED] | [2.0.0] | [1.0.0..2.0.0] |  |
| [DELTA_LENGTH_BYTE_ARRAY] | [2.0.0] | [1.0.0..2.0.0] |  |
| [DELTA_BYTE_ARRAY] | [2.0.0] | [1.0.0..2.0.0] |  |
| [BYTE_STREAM_SPLIT] | [2.8.0] | [2.7.0..2.8.0] | [Approved 2019-12-03] |
| [BYTE_STREAM_SPLIT<br/>(Additional Types)] | [2.11.0] | [2.10.0..2.11.0] | [Approved 2024-03-18] |
| [UNCOMPRESSED] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [SNAPPY] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [GZIP] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [LZO] | [1.0.0] | [1.0.0][tree-1.0.0] |  |
| [BROTLI] | [2.4.0] | [2.3.1..2.4.0] |  |
| [LZ4 (deprecated)] | [2.4.0] | [2.3.1..2.4.0] |  |
| [LZ4_RAW] | [2.9.0] | [2.8.0..2.9.0] |  |
| [ZSTD] | [2.4.0] | [2.3.1..2.4.0] |  |
| [Modular encryption] | [2.7.0] | [2.6.0..2.7.0] | [Approved 2019-01-16] |


> **Note:** Files with an [encrypted footer] use different magic bytes (`PARE`
> instead of `PAR1`), making it clear to readers they must support modular
> encryption to read the file; [plaintext footer] files use `PAR1` so legacy
> readers can still read their unencrypted columns.

## Forward compatible additions

Older readers can read files that use these features but may not understand the
new information.

| Feature | Released in | Source | Notes                                                     |
| ------------------------------------------- | ----------------------------- | --- |-----------------------------------------------------------|
| [xxHash-based bloom filters] | [2.7.0] | [2.6.0..2.7.0] | [Approved 2019-09-09]                                     |
| [Bloom filter length] | [2.10.0] | [2.9.0..2.10.0] |                                                           |
| [Page index] | [2.4.0] | [2.3.1..2.4.0] |                                                           |
| [Page CRC32 checksum] | [1.0.0] | [1.0.0][tree-1.0.0] |                                                           |
| [Size statistics] | [2.10.0] | [2.9.0..2.10.0] | [Approved 2023-11-14]                                     |
| [Geospatial statistics] | [2.11.0] | [2.10.0..2.11.0] | [Approved 2025-02-09]                                     |
| [Binary protocol extensions] | [2.11.0] | [2.10.0..2.11.0] | [Approved 2024-09-06]                                     |
| [IEEE 754 total order and NaN counts] | [2.13.0] | [2.12.0..2.13.0] | [Approved 2026-05-26]                                     |
| [LogicalType union] | [2.4.0] | [2.3.1..2.4.0] | Supersedes `ConvertedType` enum<br/>deprecated in [2.9.0] |
| [STRING (BYTE_ARRAY)] | [1.0.0] | [1.0.0][tree-1.0.0] |                                                           |
| [ENUM (BYTE_ARRAY)] | [2.0.0] | [1.0.0..2.0.0] |                                                           |
| [UUID (FIXED_LEN_BYTE_ARRAY(16))] | [2.6.0] | [2.5.0..2.6.0] |                                                           |
| [Signed and unsigned integer logical types (INT32, INT64)] | [2.2.0] | [2.1.0..2.2.0] |                                                           |
| [DECIMAL (INT32)] | [2.1.0] | [2.0.0..2.1.0] |                                                           |
| [DECIMAL (INT64)] | [2.1.0] | [2.0.0..2.1.0] |                                                           |
| [DECIMAL (BYTE_ARRAY)] | [2.1.0] | [2.0.0..2.1.0] |                                                           |
| [DECIMAL (FIXED_LEN_BYTE_ARRAY)] | [2.1.0] | [2.0.0..2.1.0] |                                                           |
| [FLOAT16 (FIXED_LEN_BYTE_ARRAY(2))] | [2.10.0] | [2.9.0..2.10.0] | [Approved 2023-10-13]                                     |
| [DATE (INT32)] | [2.2.0] | [2.1.0..2.2.0] |                                                           |
| [TIME (INT32)] | [2.2.0] | [2.1.0..2.2.0] |                                                           |
| [TIME (INT64)] | [2.4.0] | [2.3.1..2.4.0] |                                                           |
| [TIMESTAMP (INT64)] | [2.2.0] | [2.1.0..2.2.0] |                                                           |
| [Nanosecond TIME/TIMESTAMP] | [2.6.0] | [2.5.0..2.6.0] |                                                           |
| [INTERVAL (FIXED_LEN_BYTE_ARRAY(12))] | [2.2.0] | [2.1.0..2.2.0] |                                                           |
| [JSON (BYTE_ARRAY)] | [2.2.0] | [2.1.0..2.2.0] |                                                           |
| [BSON (BYTE_ARRAY)] | [2.2.0] | [2.1.0..2.2.0] |                                                           |
| [VARIANT] | [2.12.0] | [2.11.0..2.12.0] | [Approved 2025-08-24]                                     |
| [Variant shredding] | [2.12.0] | [2.11.0..2.12.0] | [Approved 2025-08-24]                                     |
| [GEOMETRY (BYTE_ARRAY)] | [2.11.0] | [2.10.0..2.11.0] | [Approved 2025-02-09]                                     |
| [GEOGRAPHY (BYTE_ARRAY)] | [2.11.0] | [2.10.0..2.11.0] | [Approved 2025-02-09]                                     |
| [LIST] | [1.0.0] | [1.0.0][tree-1.0.0] |                                                           |
| [MAP] | [1.0.0] | [1.0.0][tree-1.0.0] |                                                           |
| [UNKNOWN (always null)] | [2.4.0] | [2.3.1..2.4.0] |                                                           |

[PLAIN]: https://github.com/apache/parquet-format/blob/master/Encodings.md#plain-plain--0
[PLAIN_DICTIONARY]: https://github.com/apache/parquet-format/blob/master/Encodings.md#dictionary-encoding-plain_dictionary--2-and-rle_dictionary--8
[RLE]: https://github.com/apache/parquet-format/blob/master/Encodings.md#run-length-encoding--bit-packing-hybrid-rle--3
[RLE_DICTIONARY]: https://github.com/apache/parquet-format/blob/master/Encodings.md#dictionary-encoding-plain_dictionary--2-and-rle_dictionary--8
[DELTA_BINARY_PACKED]: https://github.com/apache/parquet-format/blob/master/Encodings.md#delta-encoding-delta_binary_packed--5
[DELTA_LENGTH_BYTE_ARRAY]: https://github.com/apache/parquet-format/blob/master/Encodings.md#delta-length-byte-array-delta_length_byte_array--6
[DELTA_BYTE_ARRAY]: https://github.com/apache/parquet-format/blob/master/Encodings.md#delta-strings-delta_byte_array--7
[BYTE_STREAM_SPLIT]: https://github.com/apache/parquet-format/blob/master/Encodings.md#byte-stream-split-byte_stream_split--9
[Modular encryption]: https://github.com/apache/parquet-format/blob/master/Encryption.md
[encrypted footer]: https://github.com/apache/parquet-format/blob/master/Encryption.md#54-encrypted-footer-mode
[plaintext footer]: https://github.com/apache/parquet-format/blob/master/Encryption.md#55-plaintext-footer-mode
[xxHash-based bloom filters]: https://github.com/apache/parquet-format/blob/master/BloomFilter.md
[Page index]: https://github.com/apache/parquet-format/blob/master/PageIndex.md
[FLOAT16 (FIXED_LEN_BYTE_ARRAY(2))]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#float16
[VARIANT]: https://github.com/apache/parquet-format/blob/master/VariantEncoding.md
[GEOMETRY (BYTE_ARRAY)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#geometry
[GEOGRAPHY (BYTE_ARRAY)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#geography

[1.0.0]: https://github.com/apache/parquet-format/releases/tag/parquet-format-1.0.0
[2.0.0]: https://github.com/apache/parquet-format/releases/tag/parquet-format-2.0.0
[2.8.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.8.0
[2.11.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.11.0
[2.4.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.4.0
[2.9.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.9.0
[2.7.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.7.0
[2.10.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.10.0
[2.12.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.12.0
[2.13.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.13.0

[Approved 2019-12-03]: https://lists.apache.org/thread/xs5qt2odm299pxgqb22mty2csc1so5yr
[Approved 2024-03-18]: https://lists.apache.org/thread/nlsj0ftxy7y4ov1678rgy5zc7dmogg6q
[Approved 2019-01-16]: https://lists.apache.org/thread/l8zcwnbrnhjh3w2k1lyb0v6ct5lnzr0h
[Approved 2019-09-09]: https://lists.apache.org/thread/ktdx1xp0d2gjfgkcvd29zxvt3cgg88bo
[Approved 2023-11-14]: https://lists.apache.org/thread/wgobz41mfldbhqpg9q4mdwypghg2cxg2
[Approved 2023-10-13]: https://lists.apache.org/thread/gyvqcx9ssxkjlrwogqwy7n4z6ofdm871
[Approved 2025-08-24]: https://lists.apache.org/thread/obn1yzhgm5zlznwrdpg7f66mswwooxw7
[Approved 2025-02-09]: https://lists.apache.org/thread/s6s714c98cn9gg22mnk5nsn7xymym8xo

[1.0.0..2.0.0]: https://github.com/apache/parquet-format/compare/parquet-format-1.0.0...parquet-format-2.0.0
[2.7.0..2.8.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.7.0...apache-parquet-format-2.8.0
[2.10.0..2.11.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.10.0...apache-parquet-format-2.11.0
[2.3.1..2.4.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.3.1...apache-parquet-format-2.4.0
[2.8.0..2.9.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.8.0...apache-parquet-format-2.9.0
[2.6.0..2.7.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.6.0...apache-parquet-format-2.7.0
[2.9.0..2.10.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.9.0...apache-parquet-format-2.10.0
[2.11.0..2.12.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.11.0...apache-parquet-format-2.12.0
[2.12.0..2.13.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.12.0...apache-parquet-format-2.13.0

[2.1.0]: https://github.com/apache/parquet-format/releases/tag/parquet-format-2.1.0
[2.2.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.2.0
[2.6.0]: https://github.com/apache/parquet-format/releases/tag/apache-parquet-format-2.6.0
[2.0.0..2.1.0]: https://github.com/apache/parquet-format/compare/parquet-format-2.0.0...parquet-format-2.1.0
[2.1.0..2.2.0]: https://github.com/apache/parquet-format/compare/parquet-format-2.1.0...apache-parquet-format-2.2.0
[2.5.0..2.6.0]: https://github.com/apache/parquet-format/compare/apache-parquet-format-2.5.0...apache-parquet-format-2.6.0

[tree-1.0.0]: https://github.com/apache/parquet-format/tree/parquet-format-1.0.0

[Variant shredding]: https://github.com/apache/parquet-format/blob/master/VariantShredding.md
[Geospatial statistics]: https://github.com/apache/parquet-format/blob/master/Geospatial.md#statistics
[Binary protocol extensions]: https://github.com/apache/parquet-format/blob/master/BinaryProtocolExtensions.md
[Approved 2024-09-06]: https://lists.apache.org/thread/x3472kldrq5kjnld9ztj1jozz25f40hg
[Approved 2026-05-26]: https://lists.apache.org/thread/h0k0hqo0sojqphnbnrkp8b0gmwdzq9on

[Bloom filter length]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L933
[Page CRC32 checksum]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L829
[Size statistics]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L202
[LogicalType union]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L471
[Nanosecond TIME/TIMESTAMP]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L352
[STRING (BYTE_ARRAY)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#string
[ENUM (BYTE_ARRAY)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#enum
[UUID (FIXED_LEN_BYTE_ARRAY(16))]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#uuid
[DECIMAL (INT32)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#decimal
[DECIMAL (INT64)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#decimal
[DECIMAL (BYTE_ARRAY)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#decimal
[DECIMAL (FIXED_LEN_BYTE_ARRAY)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#decimal
[DATE (INT32)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#date
[TIME (INT32)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#time
[TIME (INT64)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#time
[TIMESTAMP (INT64)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#timestamp
[INTERVAL (FIXED_LEN_BYTE_ARRAY(12))]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#interval
[JSON (BYTE_ARRAY)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#json
[BSON (BYTE_ARRAY)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#bson
[LIST]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#lists
[MAP]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#maps
[UNKNOWN (always null)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#unknown-always-null
[Signed and unsigned integer logical types (INT32, INT64)]: https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#signed-integers
[IEEE 754 total order and NaN counts]: https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift#L1061

[BOOLEAN]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L33
[INT32]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L34
[INT64]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L35
[INT96 (deprecated)]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L36
[FLOAT]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L37
[DOUBLE]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L38
[BYTE_ARRAY]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L39
[FIXED_LEN_BYTE_ARRAY]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L40
[Data Page V1]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L671
[Data Page V2]: https://github.com/apache/parquet-format/blob/96656a543a2165d57cc1c9abefaad7f9aeb563a5/src/main/thrift/parquet.thrift#L724
[BIT_PACKED (deprecated)]: https://github.com/apache/parquet-format/blob/master/Encodings.md#bit-packed-deprecated-bit_packed--4
[BYTE_STREAM_SPLIT<br/>(Additional Types)]: https://github.com/apache/parquet-format/blob/master/Encodings.md#byte-stream-split-byte_stream_split--9
[UNCOMPRESSED]: https://github.com/apache/parquet-format/blob/master/Compression.md#uncompressed
[SNAPPY]: https://github.com/apache/parquet-format/blob/master/Compression.md#snappy
[GZIP]: https://github.com/apache/parquet-format/blob/master/Compression.md#gzip
[LZO]: https://github.com/apache/parquet-format/blob/master/Compression.md#lzo
[BROTLI]: https://github.com/apache/parquet-format/blob/master/Compression.md#brotli
[LZ4 (deprecated)]: https://github.com/apache/parquet-format/blob/master/Compression.md#lz4
[LZ4_RAW]: https://github.com/apache/parquet-format/blob/master/Compression.md#lz4_raw
[ZSTD]: https://github.com/apache/parquet-format/blob/master/Compression.md#zstd
