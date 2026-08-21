---
title: "ALP: Adaptive Lossless Floating-point Encoding in Apache Parquet"
date: 2026-08-14
description: "Fast, random access, GPU and SIMD-friendly compression and decompression; similar in size to zstd but much faster to decode."
author: "[Kosta Tarasov](https://github.com/sdf-jkl), [Andrew Lamb](https://github.com/alamb), [Prateek Gaur](https://github.com/prtkgaur)"
categories: ["features"]
---

Apache Parquet has added the [Adaptive Lossless floating-Point (ALP) Encoding] -- a new lightweight floating-point encoding with similar compression to [`zstd`], much faster decompression speed, random access support, and SIMD and GPU friendly decoding.

----
[`zstd`]: https://github.com/facebook/zstd
<!-- Note ALP is not yet published to the Parquet website, so guess what the link will be-->
[Adaptive Lossless floating-Point (ALP) Encoding]: https://parquet.apache.org/docs/file-format/data-pages/encodings/#ALP

ALP works best for decimal values that are stored as floating-point types (32-bit `FLOAT` and 64-bit `DOUBLE`), such as
- Monetary values (exchange rates, public funds, stocks, prices, etc.) - e.g. `1.2345` or `22.03`
- Geographic coordinates (longitude/latitude) - `42.3584`, `-71.0598`
- Scientific measures (temperature, pressure, speed, degrees, etc.) - e.g. `-273.15`, `9.81`, `3.14159`

ALP is not suitable for data that uses a wide range of exponents or a large
number of significant digits, such as vector embeddings which typically span the
full floating-point range. Such use cases can continue to use existing Parquet
features such as `PLAIN` or [`BYTE_STREAM_SPLIT`] encoding followed by `ZSTD` or
`SNAPPY` general purpose compression.

Decimal values can be stored with Parquet's `DECIMAL` logical type, but it
requires the precision and scale to be known and declared up front and can not
store values outside of that
range. For this reason, it is common for systems where the exact shape
of their data is not known beforehand, to store decimal values as `FLOAT` or `DOUBLE`. For example,
JavaScript's only* [number type is `DOUBLE`], common data science tools such as
pandas [infer `FLOAT` for decimal-looking values], and NumPy has [no decimal dtype at all].

[number type is `DOUBLE`]: https://tc39.es/ecma262/#sec-ecmascript-language-types-number-type
[infer `FLOAT` for decimal-looking values]: https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
[no decimal dtype at all]: https://numpy.org/doc/stable/reference/arrays.dtypes.html
[`BigInt`]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt

<small>\* JavaScript also has [`BigInt`], but it can only represent integers.</small>

## Why ALP?

Encoding floating-point data is a complicated engineering problem due to the nature of floating-point values. They do not exactly represent most real values. This leads to rounding errors that prevent using existing lightweight encodings like Delta and Frame of Reference (FOR).

Prior to ALP the only `FLOAT`/`DOUBLE` encoding in Parquet (other than `PLAIN`) was [`BYTE_STREAM_SPLIT`](https://parquet.apache.org/docs/file-format/data-pages/encodings/#BYTESTREAMSPLIT). `BYTE_STREAM_SPLIT` does not reduce the size of data but *can* make the compression ratio and speed better when a heavyweight compressor is used afterwards.

Heavyweight compression buys that ratio at three costs:
   - Decode speed -- decompression runs well below what a scan can consume.
   - Random access -- reading one value means decoding the whole page.
   - Data dependence -- variable-length compression means that decoding a value requires decoding previous values, making it hard to parallelize with modern hardware such as [SIMD instructions] and [GPU]s.

[SIMD instructions]: https://en.wikipedia.org/wiki/SIMD
[GPU]: https://en.wikipedia.org/wiki/Graphics_processing_unit
[`BYTE_STREAM_SPLIT`]: https://parquet.apache.org/docs/file-format/data-pages/encodings/#BYTESTREAMSPLIT

ALP is designed to solve all three of these problems for common data patterns, while achieving a similar compression ratio.

### ALP Performance

As shown in the charts below, users can expect ALP to be `10x` faster to decode
than `zstd`, and thousands of times faster to retrieve individual values, with
similar compression ratios and comparable compression speed.

The code and instructions to reproduce these results and try ALP with your own
Parquet datasets can be found in the [alp_benchmark](https://github.com/alamb/alp_benchmark) repository, with the Rust Parquet implementation included.

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
    <img src="/blog/alp/avg_random_access.png" alt="Average random access benchmark" class="img-fluid">
  </div>
  <div>
    <b>Figure 1</b>: Average compression ratio, compression speed, decompression speed, and random access performance of <code>PLAIN+ZSTD</code> (per-page <code>zstd</code> compression) and <code>ALP</code> across <code>30</code> datasets on three machines. Higher is better.
     Random access speed is measured by decoding <code>100</code> deterministic, uniformly distributed rows from <code>city_temperature_f</code>.
  </div>
  <p/>
</div>

The numbers reported are for the pre-release Rust implementation of ALP. We expect
the performance of ALP encoders to improve as the implementations are optimized and
tuned. The current implementations are already faster than `zstd` in many cases,
even though most `zstd` implementations have already been heavily optimized.

## Technical overview

ALP was developed by the [Database Architectures Group at CWI](https://www.cwi.nl/en/research/database-architectures/) 
and published in a [SIGMOD 2024 Paper](https://dl.acm.org/doi/10.1145/3626717). 
As mentioned above, the encoding leverages the fact that `FLOAT`/`DOUBLE` columns often do not
need the full precision of those types. This section explains the intuition behind ALP and how it works. The
following sections then explain the encoding and decoding pipeline in more detail.

ALP encodes each floating point value using three integer values: an encoded
value, an "exponent" (`e`), and a "factor" (`f`). The exponent and factor are
shared by many values, and how they are chosen is explained below.  The original
value is recovered by computing

<pre>
value = encoded × 10<sup>f</sup> × 10<sup>-e</sup>
</pre>

As anyone who has worked with floating point knows, this calculation may not
yield exactly the original value due to rounding errors. In order for ALP to be
lossless it must return exactly the original bits that were encoded, so the
original full precision floating point value is stored as an "exception" value for any
values that do not round trip losslessly (this includes special values such as
`NaN`, `±Infinity`, and `-0.0`).

ALP stores data in "vectors" of between `8` and `32K` values (e.g., `1024`). Each
vector stores a single exponent and factor, and the encoded values are stored by
subtracting the lowest value (frame of reference) and then bit-packed to a
fixed width. Exceptions are stored directly after the encoded array. The
layout of each ALP vector is shown below.


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


Since each value is stored as a bit-packed integer of a fixed width, the
location of an arbitrary row requires computing the offset of the encoded bits.
To decode the value, the frame of reference, exponent, and factor are applied to
the encoded value to recover the original floating point value. Finally, the
exception indices are checked for the target row, and if present the exception
value is returned instead.

{{% alert title="Example" color="info" %}} 

<!-- 
Rust playground with demo 
https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=5c731c344f4161e06057f5059e4598b7
--> 

Consider encoding the value `8.0605`, which can not be exactly
represented in [IEEE 754](https://ieeexplore.ieee.org/document/8766229). It is stored as
the 32-bit floating point number `8.06050014495849609375`. It can also be
encoded as `80605` with exponent `e = 8` and factor `f = 4`. Applying
the recovery formula yields

<pre>
80605 × 10<sup>4</sup> × 10<sup>-8</sup> = 8.06050014495849609375
</pre>

Which matches the original floating point value exactly. However, if the
original value had been `8.0605123` (stored as the 32-bit value
`8.060512542724609375`) the encoded value would still be `80605`, and the
decoded value would still be `8.06050014495849609375` which is not the same as
the original value and thus would be stored as an exception. 

{{% /alert %}}

Picking a good exponent and factor is key to good ALP performance. Each Parquet
writer is free to choose the exponent and factor for each vector using any
algorithm. The Parquet specification provides an example sampling based
algorithm that minimizes the encoded size. Typically, the exponent is chosen to
capture most decimal digits in the vector while minimizing exceptions, and the
factor is chosen to remove as many trailing zeros as possible.

{{% alert title="Example" color="info" %}}

Assuming some value in the vector requires `e=8`, it is valid to encode
`0.0123`, `0.0245` and `0.0201` with multiple factor choices, such as:

* `e=8, f=0`: `1230000`, `2450000`, `2010000`
* `e=8, f=4`: `123`, `245`, `201`

For these values, the second choice is better as it yields smaller encoded
values and thus requires fewer bits to store them.
{{% /alert %}}

Finally, to minimize the number of bits needed to store the encoded values, ALP
subtracts the minimum value as a frame of reference from each encoded value
before bit-packing.

{{% alert title="Example" color="info" %}}

The values above require only `7` bits per value to store after subtracting the frame of reference:
* Input values: `123`, `245`, and `201` (`8` bits per value)
* Minimum value (frame of reference): `123`
* Final bitpacked values are `0`, `122`, and `78` (`7` bits per value)

{{% /alert %}}


### ALP Encoding and Decoding

The encoding pipeline is straightforward, as shown in the following example of
encoding a vector of values:

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

To encode this vector, first the parameters <code>e = 4</code> and <code>f =
3</code> are chosen. Then the values are transformed to integers using the
formula <code>encoded = round(value × 10<sup>4</sup> × 10<sup>-3</sup>)</code>. The integers are
checked by evaluating the reverse <code>decoded = encoded × 10<sup>3</sup> × 10<sup>-4</sup></code>, and values
that do not yield the original value, such as `1234.5678` (which decodes to
`1234.6`), are stored in the
exception array. The minimum value across the vector, `3335`, becomes the frame
of reference and is subtracted from each integer, and the resulting deltas are bit-packed using `15` bits.
The ALP representation requires `1920` bytes plus space for the exceptions, whereas the floating point representation requires `8192` bytes.
See [the ALP Encoding specification] for
more details on how the parameters are chosen and the details of the rounding
and exception handling.

<!-- TODO verify this link after it has been published to the Parquet website -->
[the ALP Encoding specification]: https://parquet.apache.org/docs/file-format/data-pages/encodings/#ALP

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

First, the bit-packed deltas are unpacked and the original values are computed
by <code>original = (3335 + delta) × 10<sup>3</sup> ×
10<sup>-4</sup></code>. Then any exceptions are "patched", by overwriting the
output array at the exception positions with the exception values.

## Ecosystem adoption

The encoding was [officially accepted into Parquet] in July 2026, and we expect
several major open source Parquet implementations to add ALP support in the next
few months. Work is already in progress in the following:

- C++ (Arrow): [apache/arrow#48345](https://github.com/apache/arrow/pull/48345)
- Java (parquet-java): [apache/parquet-java#3397](https://github.com/apache/parquet-java/pull/3397)
- Rust (arrow-rs): [apache/arrow-rs#9372](https://github.com/apache/arrow-rs/pull/9372)
- Java (Hardwood): [hardwood-hq/hardwood#581](https://github.com/hardwood-hq/hardwood/issues/581)

<!-- Can include a link to the https://parquet.apache.org/docs/file-format/implementationstatus/ once https://github.com/apache/parquet-site/pull/199 is merged. It's waiting on the 2.14 Parquet release -->

[officially accepted into Parquet]: https://lists.apache.org/thread/ld025dzycrhm6dgh8p6157to7d9x8pon


## Conclusion

ALP brings fast, parallelizable decoding and practical random access to
floating-point data, in a standard form that any Parquet implementation can
read. Its addition is one more example of Apache Parquet evolving to meet the
needs of modern data systems.

As with all additions to Parquet, this was a community endeavor with contributions
from many individuals and vendors working together to agree on
a common standard. Together, we created a well-documented specification and
reference implementations in several languages, and we expect ALP to
be widely adopted in the Parquet ecosystem over the coming years.

## Resources

- **Apache Parquet Format Specification:** [apache/parquet-format](https://github.com/apache/parquet-format)
- **ALP Encoding Specification:** [AlpEncoding.md](https://github.com/apache/parquet-format/blob/master/AlpEncoding.md)
- **Community Discussions:** [dev@parquet.apache.org](mailto:dev@parquet.apache.org) / [Archive](https://lists.apache.org/list.html?dev@parquet.apache.org)
