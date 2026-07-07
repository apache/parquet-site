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
[encrypted footer]: https://github.com/apache/parquet-format/blob/master/Encryption.md#54-encrypted-footer-mode
[plaintext footer]: https://github.com/apache/parquet-format/blob/master/Encryption.md#55-plaintext-footer-mode

## Forward incompatible features by version

Forward incompatible features and the format version each became available in:

<!-- Data driven table, see /layouts/shortcodes -->
{{< format-versions table="forward_incompatible" >}}

> **Note:** Files with an [encrypted footer] use different magic bytes (`PARE`
> instead of `PAR1`), making it clear to readers they must support modular
> encryption to read the file; [plaintext footer] files use `PAR1` so legacy
> readers can still read their unencrypted columns.

## Forward compatible additions

Older readers can read files that use these features but may not understand the
new information.

<!-- Data driven table, see /layouts/shortcodes -->
{{< format-versions table="forward_compatible" >}}
