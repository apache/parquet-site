---
title: "ALP: Adaptive Lossless Floating-Point Encoding in Apache Parquet"
date: 2026-09-22
description: "A technical overview of ALP's design, performance, and adoption across the Apache Parquet ecosystem."
author: "[Kosta Tarasov](https://github.com/sdf-jkl), [Andrew Lamb](https://github.com/alamb), [Prateek Gaur](https://github.com/prtkgaur)"
categories: ["features"]
---

Apache Parquet has added the [Adaptive Lossless floating-Point (ALP) Encoding] -- a new lightweight floating-point encoding with compression ratios similar to [`zstd`], much faster decompression, random-access support, and GPU- and SIMD-friendly decoding.

----
[`zstd`]: https://github.com/facebook/zstd
[Adaptive Lossless floating-Point (ALP) Encoding]: https://parquet.apache.org/docs/file-format/data-pages/alpencoding/

ALP works best for decimal values stored as floating-point types (32-bit `FLOAT` and 64-bit `DOUBLE`), such as

- Monetary values (exchange rates, public funds, stocks, prices, etc.) -- e.g., `1.2345` or `22.03`
- Geographic coordinates (longitude/latitude) -- e.g., `42.3584`, `-71.0598`
- Scientific measurements (temperature, pressure, speed, degrees, etc.) -- e.g., `-273.15`, `9.81`, `3.14159`

ALP is not suitable for data that uses a wide range of exponents or a large
number of significant digits, such as vector embeddings, which typically span
the full floating-point range. Such data can continue to use existing Parquet
features such as `PLAIN` or [`BYTE_STREAM_SPLIT`] encoding followed by
general-purpose compression like `ZSTD`.

Decimal values can be stored with Parquet's `DECIMAL` logical type, but that
type requires the precision and scale to be known and declared up front and
cannot store values outside that range. For this reason, systems commonly
store decimal values as `FLOAT` or `DOUBLE` when the exact shape of their data
is not known beforehand. For example,
JavaScript's only* [number type is `DOUBLE`], common data science tools such as
pandas [infer `float64` for decimal-looking values], and NumPy has [no decimal dtype at all].

[number type is `DOUBLE`]: https://tc39.es/ecma262/#sec-ecmascript-language-types-number-type
[infer `float64` for decimal-looking values]: https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
[no decimal dtype at all]: https://numpy.org/doc/stable/reference/arrays.dtypes.html
[`BigInt`]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt

<small>\* JavaScript also has [`BigInt`], but it can only represent integers.</small>

## Why ALP?

Encoding floating-point data is a complicated engineering problem due to the
nature of floating-point values. They do not exactly represent most real
numbers. This leads to rounding errors that prevent the use of existing lightweight
encodings like Delta and Frame of Reference.

Prior to ALP, [`BYTE_STREAM_SPLIT`] was the only non-dictionary alternative to
`PLAIN` for `FLOAT`/`DOUBLE` values in Parquet. It does not reduce the size of the
data but *can* improve the compression ratio and speed when a heavyweight
compressor is used afterwards.

Heavyweight compression effectively decreases the data size, but at the cost of:
   - Decode speed -- decompression speed is often the bottleneck in data access.
   - Random access -- reading one value requires decoding an entire data page containing potentially thousands of other values.
   - Data dependence -- variable-length compression means that decoding a value requires decoding previous values, making it hard to parallelize with modern hardware such as [SIMD instructions] and [GPU]s.

[SIMD instructions]: https://en.wikipedia.org/wiki/SIMD
[GPU]: https://en.wikipedia.org/wiki/Graphics_processing_unit
[`BYTE_STREAM_SPLIT`]: https://parquet.apache.org/docs/file-format/data-pages/encodings/#BYTESTREAMSPLIT

ALP is designed to solve all three of these problems for common data patterns, while achieving a similar compression ratio to heavyweight compression.

Parquet applies an encoding first, then an optional compression codec as a
separate step. The charts below compare the `PLAIN` and `BYTE_STREAM_SPLIT`
encodings followed by `ZSTD` compression with the `ALP` encoding and no
additional compression. Users can expect ALP to decode `10x` faster and
retrieve individual values thousands of times faster, with a slightly lower
compression ratio and slightly faster compression.[^benchmark]

[^benchmark]: The code and instructions to reproduce these results and try ALP
    on your own Parquet datasets are in the
    [alp_benchmark](https://github.com/alamb/alp_benchmark) repository, which
    uses the Rust Parquet implementation.

<div class="row g-3 td-max-width-on-larger-screens">
  <div class="col-12 col-md-6">
    <img src="/blog/alp/avg_compression_ratio.png" alt="Average compression ratio benchmark" class="img-fluid">
  </div>
  <div class="col-12 col-md-6">
    <img src="/blog/alp/avg_compression_speed.png" alt="Average compression speed benchmark" class="img-fluid">
  </div>
  <div class="col-12 col-md-6">
    <img src="/blog/alp/avg_decompression_speed.png" alt="Average decompression speed benchmark" class="img-fluid">
  </div>
  <div class="col-12 col-md-6">
    <img src="/blog/alp/avg_random_access.png" alt="Average random-access benchmark" class="img-fluid">
  </div>
  <div>
    <b>Figure 1</b>: Average compression ratio, compression speed, decompression speed, and random-access speed of <code>PLAIN+ZSTD</code> and <code>BYTE_STREAM_SPLIT+ZSTD</code> (each encoding followed by per-page <code>ZSTD</code> compression), and <code>ALP</code> (no compression codec), across <code>30</code> datasets on <code>3</code> machines. Higher is better.
     Random-access speed is measured by decoding <code>100</code> deterministic, uniformly distributed rows from <code>city_temperature_f</code>.
  </div>
  <p/>
</div>

Note that these numbers are for the pre-release Rust implementation of ALP, and
we expect performance to improve as implementations are optimized and tuned.
Even so, ALP is already faster than `zstd` in many cases, despite years of
optimization work on `zstd` implementations. We also measured similar
[improvements for the C++ implementation].

[improvements for the C++ implementation]: https://docs.google.com/spreadsheets/d/1NmCg0WZKeZUc6vNXXD8M3GIyNqF_H3goj6mVbT8at7A/

## Technical Overview

ALP takes advantage of a common pattern: many values stored as `FLOAT` or
`DOUBLE` originated as decimal numbers with relatively few digits, such as
prices or measurements. This section explains the intuition behind ALP and
then covers the encoding and decoding pipelines in more detail.

ALP encodes floating-point values in batches called "vectors", ranging in size from `8` to `32K` values (e.g., `1024`). Each value in a vector is encoded as an
integer, and the vector stores two integer parameters shared by all its
values: an "exponent" (`e`) and a "factor" (`f`). Each vector can use a
different exponent and factor. How they are chosen is explained below. The
original value is recovered by computing

<pre>
value = encoded × 10<sup>f</sup> × 10<sup>-e</sup>
</pre>

This calculation uses floating-point arithmetic, which rounds to the nearest
representable value and thus may not reproduce the original value exactly. When
that happens, ALP stores the original full-precision value separately as an
"exception", keeping the encoding lossless. Special values such as `NaN`,
`±Infinity`, and `-0.0` are also stored as exceptions.

Within each vector, the encoded values are stored by subtracting the lowest
value (the frame of reference) and then bit-packing to a fixed width. Exceptions
are stored directly after the encoded array. The layout of each ALP vector is
shown below.


<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM -->
<div class="row g-3 td-max-width-on-larger-screens">
  <div class="col-12">
    <img src="/blog/alp/alp_vector_layout.png" alt="ALP serialized vector layout" class="img-fluid">
  </div>
  <div>
    <b>Figure 2</b>: Layout of a serialized ALP vector: a fixed-size Vector Header followed by a variable-size Data Section.
  </div>
  <p/>
</div>


Since each value is stored as a bit-packed integer of a fixed width, locating
an arbitrary row requires only computing the offset of its encoded bits.
Applying the frame of reference, exponent, and factor to that integer recovers
the original floating-point value. Finally, the exception indices are checked
for the target row, and if an exception is present, its value is returned
instead.

{{% alert title="Example" color="info" %}}

<!--
Rust playground with demo
https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=5c731c344f4161e06057f5059e4598b7
-->

Consider encoding the value `8.0605`, which cannot be exactly
represented in [IEEE 754](https://ieeexplore.ieee.org/document/8766229). It is stored as
the 32-bit floating-point number `8.06050014495849609375`. It can also be
encoded as `80605` with exponent `e = 8` and factor `f = 4`. Applying
the recovery formula with 32-bit floating-point arithmetic, which rounds after
each multiplication, yields

<pre>
80605 × 10<sup>4</sup> × 10<sup>-8</sup> → 8.06050014495849609375 (<code>FLOAT</code>)
</pre>

This is the nearest representable `FLOAT` to `8.0605` and matches the original
stored floating-point value exactly. However, if the original value had been
`8.0605123` (stored as the 32-bit value `8.060512542724609375`), the encoded
value would still be `80605` and the decoded value still
`8.06050014495849609375`, which differs from the original. That value would
therefore be stored as an exception.

{{% /alert %}}

Picking the exponent and factor well is key to ALP's performance. Each Parquet
writer is free to choose them for each vector using any algorithm. The Parquet specification provides an example sampling-based
algorithm that aims to minimize the encoded size. Typically, the exponent is chosen to
capture most decimal digits in the vector while minimizing exceptions, and the
factor is chosen to remove as many trailing zeros as possible.

{{% alert title="Example" color="info" %}}

Assuming some value in the vector requires `e = 8`, it is valid to encode
`0.0123`, `0.0245`, and `0.0201` with multiple factor choices:

- `e = 8, f = 0`: `1230000`, `2450000`, `2010000`
- `e = 8, f = 4`: `123`, `245`, `201`

The second choice is better: it yields smaller encoded values, which require
fewer bits to store.
{{% /alert %}}

Finally, ALP subtracts the minimum encoded value (the frame of reference) from
every encoded value before bit-packing, further reducing the bits required.

{{% alert title="Example" color="info" %}}

The values above require only `7` bits each after subtracting the frame of reference:

- Input values: `123`, `245`, and `201` (`8` bits per value)
- Minimum value (frame of reference): `123`
- Final bit-packed values: `0`, `122`, and `78` (`7` bits per value)

{{% /alert %}}

The encoding pipeline is straightforward, as shown in the following example of
encoding a vector:

<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM -->
<div class="row g-3 td-max-width-on-larger-screens">
  <div class="col-12">
    <img src="/blog/alp/alp_encoding_example.png" alt="ALP encoding pipeline example" class="img-fluid">
  </div>
  <div>
    <b>Figure 3</b>: Encoding a vector of <code>1024</code> 64-bit floating-point values using ALP.
  </div>
  <p/>
</div>

To encode this vector, the parameters <code>e = 4</code> and <code>f =
3</code> are chosen first. Then the values are transformed to integers using the
formula <code>encoded = round(value × 10<sup>4</sup> × 10<sup>-3</sup>)</code>. Each integer is
checked by reversing the transformation with <code>decoded = encoded × 10<sup>3</sup> × 10<sup>-4</sup></code>.
Values that do not round-trip, such as `8.0605123` (which decodes to `8.1`), are
stored in the exception array. The minimum value across the vector, `3335`,
becomes the frame of reference and is subtracted from each integer, and the
resulting deltas are bit-packed using `15` bits.
In this example, ALP uses `1920` bytes for the bit-packed deltas, plus a
`13`-byte vector header and space for exceptions. `PLAIN` uses `8192` bytes for
the same `1024` values. This comparison excludes page-level metadata for both
encodings. See [the ALP Encoding specification] for more details on how the
parameters are chosen and how rounding and exception handling work.

[the ALP Encoding specification]: https://parquet.apache.org/docs/file-format/data-pages/alpencoding/

Decoding a vector requires similar steps, but in reverse, as shown below.


<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM -->
<div class="row g-3 td-max-width-on-larger-screens">
  <div class="col-12">
    <img src="/blog/alp/alp_decoding_example.png" alt="ALP decoding pipeline example" class="img-fluid">
  </div>
  <div>
    <b>Figure 4</b>: Decoding a vector of <code>1024</code> values back to floating-point values using ALP.
  </div>
  <p/>
</div>

First, the bit-packed deltas are unpacked, and the original values are computed
by <code>original = (3335 + delta) × 10<sup>3</sup> ×
10<sup>-4</sup></code>. Then any exceptions are "patched" by overwriting the
output array at the exception positions with the exception values.

## Acknowledgements

ALP was first published in a [SIGMOD 2024 paper] by Azim
Afroozeh, Leonardo Kuffó, and Peter Boncz from the [Database Architectures Group
at CWI]. The [Vortex] and [Lance] formats adopted ALP early, demonstrating its
benefits in industrial applications. In late 2025, the community began the standardization process. Along with the
authors of this blog post, many community members contributed, including Divjot Arora,
Arnav Balyan, Devan Benz, Ryan Blue, Alkis Evlogimenos, Vinoo Ganesh, Adrian
Garcia Badaracco, Curt Hagenlocher, Amogh Jahagirdar, Micah Kornfield, Robert
Kruszewski, Julien Le Dem, Kevin Liu, Steve Loughran, Ismaël Mejía, mwish,
Antoine Pitrou, Adam Reeve, Ed Seidl, Russell Spitzer, Matt Topol, Jeffrey Vo,
Daniel Weeks, Gang Wu, and Zehua Zou.

<!-- The list of people came from
Mailing list threads
https://lists.apache.org/thread/tjtln1mmjqfoql1ls2dw9xpdk91r1909
https://lists.apache.org/thread/nkfowy04f73cfo7g43p2v0wl79spqkpz
https://lists.apache.org/thread/hgmd58wrv9yoopcrf61m1bg211l65tbt
https://lists.apache.org/thread/ld025dzycrhm6dgh8p6157to7d9x8pon
https://lists.apache.org/thread/4h75ww5h0z1hx2yk2b6z2tpt0wfh3nzq
https://lists.apache.org/thread/gfodxyzx27pzbpkvns6zvfrm55y41sdt
https://lists.apache.org/thread/1q84qhkj9ofjsgrj798ftl3vgww067z6
Rust PR: https://github.com/apache/arrow-rs/pull/9372
Java PR: https://github.com/apache/parquet-java/pull/3397
C++ PR: https://github.com/apache/arrow/pull/48345/changes
Spec PR: https://github.com/apache/parquet-format/pull/557
Google Doc Spec (including all comments): https://docs.google.com/document/d/1PlyUSfqCqPVwNt8XA-CfRqsbc0NKRG0Kk1FigEm3JOg/edit?tab=t.0#heading=h.5xf60mx6q7xk
-->


[SIGMOD 2024 paper]: https://dl.acm.org/doi/10.1145/3626717
[Database Architectures Group at CWI]: https://www.cwi.nl/en/research/database-architectures/
[Vortex]: https://vortex.dev/
[Lance]: https://lance.org/

## Ecosystem Adoption

The encoding was released as part of [parquet-format 2.14.0] in September 2026.
ALP is already supported in at least one major open-source implementation (the
[`parquet` 60.0.0][arrow-rs-60] Rust crate), and we expect other Parquet
implementations to add support in the coming months. Please check the
[Implementation Status] page for the current state of support.
You can also try it today on your own datasets using the [tool in the ALP benchmark repository](https://github.com/alamb/alp_benchmark#run-on-your-own-parquet-files).


[parquet-format 2.14.0]: /blog/2026/09/11/2.14.0/
[arrow-rs-60]: https://crates.io/crates/parquet/60.0.0
[Implementation Status]: https://parquet.apache.org/docs/file-format/implementationstatus/


## Conclusion

ALP brings fast, parallelizable decoding and practical random access to
floating-point data in a standard form that any Parquet implementation can
read once it adds support for the encoding. Its addition is one more example of Apache Parquet evolving to meet the needs of modern data systems.

As with all additions to Parquet, this was a community endeavor, with many
individuals and vendors working together to agree on a common standard and
produce a well-documented specification and multiple reference implementations. We
expect ALP to be widely adopted in the Parquet ecosystem over the coming
years.

## Resources

- [**ALP Encoding Specification**](https://parquet.apache.org/docs/file-format/data-pages/alpencoding/)
- [**Apache Parquet Format Specification**](https://github.com/apache/parquet-format)
- [**Implementation Status Page**](https://parquet.apache.org/docs/file-format/implementationstatus/)
