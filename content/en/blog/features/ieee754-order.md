---
title: "Taming Floating-Point Statistics in Apache Parquet: IEEE 754 Total Order and NaN Counts"
date: 2026-05-29
description: "How the Apache Parquet Community resolved potentially ambiguous floating-point statistics using IEEE 754 total order and explicit NaN counts"
author: "[Jan Finis](https://github.com/JFinis), [Gang Wu](https://github.com/wgtmac)"
categories: ["features"]
---

Column statistics are the secret to Apache Parquet's blazing fast performance. By storing compact summaries—like `min`, `max`, and null counts—for row groups, column chunks, and pages, readers can easily skip irrelevant data that doesn't match a query.

However, floating-point values throw a wrench into this simple model. The IEEE 754 standard defines special values like `NaN` (Not a Number), signed zeros (`-0.0` and `+0.0`), and infinities. Their comparison rules don't play well with the simple "total order" (a strict smaller-to-larger ranking) expected by most data-pruning algorithms. To fix this, the Parquet community recently clarified the standard by combining IEEE 754 total order semantics with an explicit `nan_count` field in the statistics.

The result is a much clearer contract between data writers and readers. Floating-point bounds can now be interpreted consistently, and readers can confidently determine if `NaN` values are present, without having to guess based solely on `min` and `max` bounds.

## Why Floating-Point Statistics Need Special Handling

For integers, strings, and many other straightforward types, Parquet statistics are simple: the writer records the absolute smallest and largest values, and the reader uses those bounds to decide if a query might find a match.

Floating-point columns are trickier for two major reasons. First, `-0.0` and `+0.0` are considered equal in normal math operations, yet they possess distinct underlying bit patterns. A data format needs strict rules on how to order these values; otherwise, different libraries might generate conflicting statistics for the exact same underlying data. Parquet's approach to dealing with this ambiguity has been to mandate that a `min` of `0.0` always be written as `-0.0`, and a `max` of `0.0` always be written as `+0.0`, regardless of any sign bits that may be present in the actual data. Readers are advised that `-0.0` may be present even if the `min` is `+0.0`, and `+0.0` may be present even if the max is `-0.0`.

Second, `NaN` is completely unordered under standard IEEE 754 comparisons. Expressions like `x < NaN`, `x > NaN`, and `x == NaN` always evaluate to false. If a writer blindly includes `NaN` in ordinary `min` or `max` calculations, the resulting bounds might be useless for skipping data. To date Parquet has followed the latter approach, forbidding the inclusion of `NaN` in the statistics. [PR #196](https://github.com/apache/parquet-format/pull/196) provides a detailed overview of the problems inherent in this approach. For instance, consider a page with a max statistic of `0.0` that also contains a `NaN`. A query engine that considers `NaN` to be greater than all values attempts a query with a predicate like `x > 1.0`. If the engine examines the statistics, it will see that the `max` is `0.0`, so it might improperly skip that page, even though it contains at least one row that satisfies the predicate. Without knowledge of the presence or absence of `NaN`, the engine cannot safely perform this type of page pruning for floating point columns.

These aren't just theoretical edge cases. Query engines rely heavily on these statistics to safely skip large chunks of data. Ambiguous floating-point bounds degrade query performance and can lead to severe inconsistencies. [PARQUET-2249](https://issues.apache.org/jira/browse/PARQUET-2249) exposed another critical flaw in how `NaN` values interacted with Parquet's `ColumnIndex` metadata.

The core problem in PARQUET-2249 arose when a data page contained *only* `NaN` values. Such a page isn't considered "null"—the data is physically there, and `NaN` is distinct from a missing `null` value. However, older guidelines stated that `NaN` values shouldn't be included when computing `min` and `max`. This put the `ColumnIndex` in an impossible situation: it strictly required valid `min` and `max` bounds for any non-null page, yet there were no non-`NaN` values available to use!

## How the Community Reached Consensus

The final solution didn't emerge overnight. The discussion began with [PR #196](https://github.com/apache/parquet-format/pull/196) in March 2023, which proposed adding a `nan_count` to floating-point statistics. This neatly solved one problem: making it explicitly clear whether a chunk of data contains `NaN`s. It also provided a safe migration path, as the new field could be added without breaking older readers.

However, adding `nan_count` alone didn't completely solve the `ColumnIndex` dilemma. For page and column chunk statistics, a reader can combine `num_values`, `null_count`, and `nan_count` to deduce if all non-null values are `NaN`. But `ColumnIndex` doesn't store `num_values`, making that math impossible. The community brainstormed various workarounds, like writing `NaN` directly into the bounds or adding special markers (like `nan_pages`). Each idea solved part of the puzzle but introduced new complexities or metadata bloat.

[PR #221](https://github.com/apache/parquet-format/pull/221) explored an alternative route: introducing a brand new `IEEE_754_TOTAL_ORDER` for floating-point columns. This gave physical `FLOAT`, `DOUBLE`, and logical `FLOAT16` values a strict, deterministic position, sorting out the signed zeros and different `NaN` bit patterns. However, this approach had a critical flaw on its own: because `NaN` values are placed at the absolute extremes of the total order, the presence of even a single `NaN` would pollute the `min` or `max` bounds, rendering normal numeric predicate pushdown completely ineffective. Furthermore, while it elegantly removed ordering ambiguity, it required an opt-in from readers and writers, and didn't fully answer how much readers should know about the presence of `NaN`s in older files.

Ultimately, the community reached a consensus: why not combine the best of both worlds? [PR #514](https://github.com/apache/parquet-format/pull/514), opened in August 2025 and merged in May 2026, successfully merged `IEEE_754_TOTAL_ORDER` with `NaN` counts. The new order strictly defines how bounds are compared, while `nan_count` clearly flags the presence of `NaN`s. Because no legacy writer uses the new order, the spec now safely *requires* `nan_count` whenever `IEEE_754_TOTAL_ORDER` is used, while gracefully handling older files.

## The Solution

The resulting specification elegantly marries two concepts: an optional `nan_count` field for both `Statistics` and `ColumnIndex`, and the `IEEE_754_TOTAL_ORDER` column order.

`nan_count` records the exact number of `NaN` values within a given scope. Because the field is optional (or completely missing from older files), readers must treat a *missing* `nan_count` differently than a `0`. If missing, readers must cautiously assume `NaN` values *might* be present. If a column is written using `IEEE_754_TOTAL_ORDER`, the writer is forced to provide the `nan_count`.

This new total order applies exclusively to physical `FLOAT`, `DOUBLE`, or logical `FLOAT16` columns. It defines a strict, deterministic ordering for bit patterns with these key properties:

1. `-0.0` is ordered strictly before `+0.0`.
2. Negative `NaN` values are ordered below all other values.
3. Positive `NaN` values are ordered above all other values.
4. Different `NaN` bit patterns have their own deterministic internal order.

For columns utilizing `IEEE_754_TOTAL_ORDER`, `min_value` and `max_value` must represent the smallest and largest **non-NaN** values. However, if *all* non-null values are `NaN` (solving the PARQUET-2249 issue), then `min_value` and `max_value` fall back to the smallest and largest `NaN` values as defined by the total order. Readers then check `nan_count` to know what they're dealing with.

Together, these rules empower readers to interpret floating-point statistics confidently, free from the quirks of different implementation languages.

## Implementation Guidance

Data writers producing floating-point statistics must now be explicit. If writing `FLOAT`, `DOUBLE`, or `FLOAT16` using `IEEE_754_TOTAL_ORDER`, writers must compute bounds using this exact total order and include the `nan_count`.

Interestingly, implementing this ordering doesn't require a heavy, complex comparison engine. A simplified logic sketch (written in Rust, but easily adaptable to C++, Java, Python, or Go) looks like this:

```rust
pub fn totalOrder(x: f64, y: f64) -> bool {
    let mut x_int = x.to_bits() as i64;
    let mut y_int = y.to_bits() as i64;
    x_int ^= (((x_int >> 63) as u64) >> 1) as i64;
    y_int ^= (((y_int >> 63) as u64) >> 1) as i64;
    return x_int <= y_int;
}
```

The same clever trick applies to 32-bit floats (`f32`): preserve the IEEE bit pattern, flip negative values so their integer representations sort correctly, and compare the resulting integers. The key takeaway for developers is that `min_value` and `max_value` must be computed with the identical total-order semantics advertised in the file's `ColumnOrder`.

Readers, conversely, should treat a missing `nan_count` with caution. Absence doesn't mean zero; it means "unknown," so `NaN` values may lurk inside. When `nan_count` is present, readers can pair it with `min` and `max` bounds to make hyper-efficient, safe pruning decisions.

Implementations that haven't adopted the new rules yet should continue handling older files conservatively, particularly when queries involve `NaN` or signed zeros, but also in the case of inequalities not involving `NaN`.

## Conclusion

By embracing IEEE 754 total order and `nan_count`, Apache Parquet now boasts a much clearer, robust foundation for floating-point statistics. This update preserves the blazing speed of predicate pushdown while finally taming the edge cases: `NaN` values are accurately counted, signed zeros have their rightful place, and all floating-point bit patterns can be ordered deterministically.

It’s a small but mighty refinement to the Parquet format. It boosts interoperability across different programming languages and query engines, giving readers the precise information they need to prune data with confidence.

## Resources

- [PARQUET-2249: Fix statistics/column index handling for NaN values](https://issues.apache.org/jira/browse/PARQUET-2249)
- [PR #196: Add NaN count to statistics](https://github.com/apache/parquet-format/pull/196)
- [PR #221: Add IEEE 754 total order](https://github.com/apache/parquet-format/pull/221)
- [PR #514: Combine IEEE 754 total order with NaN counts](https://github.com/apache/parquet-format/pull/514)
- [`parquet.thrift` column order definitions](https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift)
