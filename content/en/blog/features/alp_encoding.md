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

Decimal values have a small number of significant digits and a small range of
values and typically require many fewer bits to store than full-precision
floating-point values.

However, `DECIMAL` values require the precision and scale to be known and declared
up front as part of the logical type and can not store values outside of that
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

In general, ALP achieves similar compression to `zstd`, with much faster
decompression speed and random access support, with slightly slower compression
as shown in the charts below. Users can expect ALP to be 10x faster
to decode and to retrieve random values than `zstd`, with similar compression
ratios.

The code and instructions to reproduce these results and try ALP with your own
Parquet datasets can be found in the [alp_benchmark](https://github.com/alamb/alp_benchmark) repository, with the Rust Parquet implementation included.

<div class="row g-3">
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
    <b>Figure 1</b>: Average compression ratio, compression speed, decompression speed, and random access performance of <code>PLAIN</code> (no encoding), <code>PLAIN+ZSTD</code> (per-page <code>zstd</code> compression), and <code>ALP</code> across 30 datasets. Higher is better.
     Random access speed is the time to decode 100 deterministic, uniformly distributed rows from <code>city_temperature_f</code>.
  </div>
  <p/>
</div>

These numbers were gathered using the Rust implementation of ALP. We expect
the performance of ALP encoders to improve as the implementations are optimized and
tuned. The current implementations are already faster than `zstd` in many cases,
even though most `zstd` implementations have already been heavily optimized.

## Technical overview

ALP was developed by the [Database Architectures Group at CWI](https://www.cwi.nl/en/research/database-architectures/) 
and published in a [SIGMOD 2024 Paper](https://dl.acm.org/doi/10.1145/3626717). 
As mentioned above, the encoding leverages the fact that `FLOAT`/`DOUBLE` columns often do not
need the full precision of those types. This section explains the intuition behind ALP and how it works. The
following sections then explain the encoding and decoding pipeline in more detail.

ALP encodes each floating point value using three integer values: a encoded value, 
and "exponent" (e), and a "factor" (f). The choice of exponent and factor is explained below.
The original value is recovered by computing

<pre>
value = encoded × 10<sup>f</sup> × 10<sup>-e</sup>
</pre>

As anyone who has worked with floating point knows, this calculation may not
yield exactly the original value due to rounding errors. In order for ALP to be
lossless it must return exactly the original bits that were encoded, so the
original full precision floating point value is stored an "exception" value for any
values that do not round trip losslessly.

ALP stores data in "vectors" of between 8 and 32K values  (e.g., 1024). Each
vector stores a single exponent and factor, and the encoded values are stored by
subtracting the lowest value (frame of reference) and then bit-packed into a
fixed size location. Exceptions are stored directly after the encoded array. The
layout of each ALP vector is shown below.


<!-- TODO: make a nicer graphic for this --> 

```text
<----------- Vector Header -----------><----------------------- Data Section ----------------------->
+-------------------+-----------------+-------------------+---------------------+-------------------+
|      AlpInfo      |     ForInfo     |   PackedValues    | ExceptionPositions  | ExceptionValues   |
|     (4 bytes)     | (5B or 9B)      |    (variable)     |     (variable)      |    (variable)     |
+-------------------+-----------------+-------------------+---------------------+-------------------+
```


Decoding a row with ALP is significantly less work than decompressing an entire
page with `zstd` or `snappy`. Since each value is stored as a bit-packed value
of a fixed width, decoding an arbitrary row requires computing the offset of the
encoded bits, and applying the frame of reference, exponent, and factor to
decode it. The exception indices must also be checked to see if the stored
exception value must be returned instead.

{{% alert title="Example" color="info" %}} 

Consider encoding the value `8.0605`, which can not be exactly
represented in [IEEE 754](https://ieeexplore.ieee.org/document/8766229). It is encoded as
the 32-bit floating point number `8.06049999999999933209`. It can also be
can be encoded as `80605` with exponent `e = 14` and factor `f = 10`. Applying
the recovery formula yields

<pre>
80605 × 10<sup>10</sup> × 10<sup>-14</sup> = 8.06049999999999933209
</pre>

Which matches the original floating point value exactly. However, if the
original value had been `8.0605000000000000001` the encoded value would still be
`80605`, but the decoded value would be `8.06049999999999933209` which is not the
same as the original value and thus would be stored as an exception.
{{% /alert %}}

Picking a good exponent and factor is key to good ALP performance. Each Parquet
writer is free to choose the exponent and factor for each vector using any
algorithm. The Parquet specification provides an example sampling based
algorithm which minimize exceptions. Typically, the exponent is chosen to cover
the range of values in the vector, and the factor is chosen to remove as many
trailing zeros as possible.

{{% alert title="Example" color="info" %}}

It is valid to encode the values `1.23`, `2.45` and `2.01` with
multiple exponent and factor choices, such as:

* `e=1, f=2`: 123, 245, 201
* `e=2, f=3`: 1230, 2450, 2010

For these values, the first choice is better as it yields smaller encoded
values and thus fewer bits to store them.
{{% /alert %}}

Finally, to minimize the number of bits needed to store the encoded values, ALP
subtracts the minimum value as a frame of reference from each encoded value
before bit-packing.

{{% alert title="Example" color="info" %}}

The values above require only 7 bits per value to store after subtracting the frame of reference:
* Input values: `123`, `245`, and `201` (8 bits per value)
* Minimum value (frame of reference):`123`
* Final bitpacked values are `0`, `122`, and `78` (7 bits per value)

{{% /alert %}}



<!-- 
*********
** Start commented region
*********
alamb: this is the original example walk through section from sdf-jkl that walks
through encoding in more detail. I think it is redundant now but want to leave it in for
comparison

{{% alert title="Example" color="info" %}}
8.0605 can't be physically represented in [IEEE 754](https://ieeexplore.ieee.org/document/8766229) as is, and is instead approximated as 8.06049999999999933209.

To find the smallest representation you take the value and brute-force search over exponents, computing <code>significand = round(value × 10<sup>e</sup>)</code>.

For this value it arrives at significand 80605 with exponent 4.
{{% /alert %}}

To improve compression ALP stores a single exponent per vector vs storing one per value. To increase coverage of the algorithm using a larger exponent is preferable. This introduces another issue of integers containing too many trailing 0-digits and reducing compression.

ALP solves this by introducing a factor and using it to get rid of as many trailing zeros as possible.

{{% alert title="Example" color="info" %}}
We have a vector with multiple values. The exponent is trying to capture as many values as possible. The value with the highest precision needs exponent 14.

That makes 8.06049999999999933209 represented as 806050000000000.

ALP then searches for a factor to get rid of as many trailing zeros as possible for all values within the vector losslessly. It happens to be 10.

The encoded value can be calculated via <code>significand = round(value × 10<sup>e</sup> × 10<sup>-f</sup>)</code>.

This makes our value 80605 with e = 14 and f = 10 for this vector.
{{% /alert %}}

To make sure that the encoded value still represents the `FLOAT`/`DOUBLE` value losslessly we round trip each value during this step.

{{% alert title="Example" color="info" %}}
Decoding applies the inverse formula <code>value = significand × 10<sup>f</sup> × 10<sup>-e</sup></code>.

<code>80605 × 10<sup>10</sup> × 10<sup>-14</sup> = 8.06049999999999933209</code>

The result matches the stored double exactly: the value round-trips losslessly.
{{% /alert %}}

Some values don't survive the round-trip. Instead, they are written to the exception array at the end of the vector. The exception positions are stored prior to the exception array.

While very performant, not all floating-point data can be exploited by ALP, for example vector embeddings typically span the full floating-point range and do not encode well with ALP. Such use cases can continue to use existing Parquet features such as `PLAIN` or [`BYTE_STREAM_SPLIT`](https://parquet.apache.org/docs/file-format/data-pages/encodings/#BYTESTREAMSPLIT) encoding followed by `ZSTD` or `SNAPPY` general purpose compression.
***** End Commented Region *******
-->

### ALP Encoding and Decoding

The actual encoding and decoding pipelines are straightforward, and shown in the diagrams below.

<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM -->
<div class="row g-3">
  <div class="col-12 col-md-6">
    <img src="/blog/alp/alp_encoding_pipeline.png" alt="ALP encoding pipeline steps" class="img-fluid">
  </div>
  <div class="col-12 col-md-6">
    <img src="/blog/alp/alp_decoding_pipeline.png" alt="ALP decoding pipeline steps" class="img-fluid">
  </div>
  <div>
    <b>Figure 2</b>: ALP encoding pipeline (left) and decoding pipeline (right). 
  </div>
  <p/>
</div>

Vectors of values are encoded by first computing the exponent and factor,
transforming the input values to integers and checking for exceptions,
subtracting the frame of reference then bit-packing the integers. Decoding
proceeds in reverse, unpacking the integers, adding the frame of reference and
applying the exponent and factor, and patching any exceptions.

To make the encoding pipeline more concrete, consider the following example of encoding a vector of values:

<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM -->
<div class="row g-3">
  <div class="col-12">
    <img src="/blog/alp/alp_encoding_example.png" alt="ALP encoding pipeline example" class="img-fluid">
  </div>
  <div>
    <b>Figure 3</b>: Encoding a vector of 1024 32-bit floating-point values using ALP. 
  </div>
  <p/>
</div>

To encode this vector, first the parameters <code>e = 4</code> and <code>f =
3</code> are chosen . Then the values are transformed to integers using the
formula <code>encoded = round(value × 10<sup>4</sup> × 10<sup>-3</sup>)</code>. The integers are
checked by evaluating the reverse <code>decoded = encoded × 10<sup>3</sup> × 10<sup>-4</sup></code>, and values
that do not yield the original value, such as `1234.5567`, are stored in the
exception array. The minimum value across the vector, `3335`, is then subtracted from each integer
to compute the frame of reference, and the integers are bit-packed using 15-bits.
The ALP representation requires `1920` bytes and space for the exceptions, whereas the floating point representation requires `4096` bytes.
See [the ALP Encoding specification] for
more details on how the parameters are chosen and the details of the rounding
and exception handling.

<!-- TODO verify this link after it has been published to the Parquet website -->
[the ALP Encoding specification]: https://parquet.apache.org/docs/file-format/Alp


<!-- Diagrams source: https://docs.google.com/presentation/d/1NeYAGKV2wZZMSme5rVgUGGMkfOTEnxw8oCDxid5UouM -->
<div class="row g-3">
  <div class="col-12">
    <img src="/blog/alp/alp_decoding_example.png" alt="ALP decoding pipeline example" class="img-fluid">
  </div>
  <div>
    <b>Figure 4</b>: Decoding the same vector of 1024 values back to floating-point values using ALP.
  </div>
  <p/>
</div>

To decode we go through mostly the same steps, but in reverse:

1) Unpack bit_width-bit integers
2) Add frame_of_reference to each unpacked integer.
3) Decode: multiply each integer by <code>10<sup>factor</sup></code> then by <code>10<sup>-exponent</sup></code>.
4) Patch exceptions: for each (position, value) in the exception arrays, overwrite the decoded output at that position with the stored value.

## Ecosystem adoption

Since the proposal, ALP support has been underway across multiple Parquet implementations:

- C++ (Arrow): [apache/arrow#48345](https://github.com/apache/arrow/pull/48345) (complete, in final review)
- Rust (arrow-rs): [apache/arrow-rs#9372](https://github.com/apache/arrow-rs/pull/9372) (complete, awaiting the [shared test dataset](https://github.com/apache/parquet-testing/pull/100) to merge)
- Java (parquet-java): [apache/parquet-java#3397](https://github.com/apache/parquet-java/pull/3397) (in progress)
- Hardwood, a newer Java implementation, is tracking support in [hardwood-hq/hardwood#581](https://github.com/hardwood-hq/hardwood/issues/581)

<!-- Can include a link to the https://parquet.apache.org/docs/file-format/implementationstatus/ once https://github.com/apache/parquet-site/pull/199 is merged. It's waiting on the 2.14 Parquet release -->

ALP has already been implemented in new formats such as Vortex, several academic formats such as F3, FastLanes (which originated at the same CWI lab as ALP), and in tightly integrated open source systems such as DuckDB file format (also same CWI lab) as well as ClickHouse and CedarDB.

## Conclusion

<!-- needs more work -->

ALP brings fast, parallelizable decoding and practical random access to floating-point data in Parquet. It's one more step toward closing the gap with the newest file formats.

## Resources

- [ALP paper (CWI)](https://ir.cwi.nl/pub/33334/33334.pdf)
- [ALP MSc thesis (Kuffo, CWI)](https://homepages.cwi.nl/~boncz/msc/2023-KuffoRivero.pdf)
- [ALP Parquet encoding PR](https://github.com/apache/parquet-format/pull/557)
- [Benchmark code](https://github.com/alamb/alp_benchmark)

## Appendix

<details><summary>Full benchmark results </summary>

| Dataset | Parquet choice | Compression (GB/s) | Decompression (GB/s) | Compressed size (bits/value) |
|---|---|---:|---:|---:|
| arade4 | PLAIN | 63.775 | 68.205 | 64.01 |
| arade4 | PLAIN + ZSTD | 0.574 | 1.499 | 37.39 |
| arade4 | BYTE_STREAM_SPLIT + ZSTD | 1.875 | 4.980 | 54.58 |
| arade4 | ALP | 1.698 | 31.860 | 24.99 |
| basel_temp_f | PLAIN | 33.559 | 57.828 | 64.01 |
| basel_temp_f | PLAIN + ZSTD | 0.458 | 1.656 | 23.07 |
| basel_temp_f | BYTE_STREAM_SPLIT + ZSTD | 1.181 | 2.080 | 54.59 |
| basel_temp_f | ALP | 0.534 | 28.058 | 29.23 |
| basel_wind_f | PLAIN | 52.641 | 76.402 | 64.01 |
| basel_wind_f | PLAIN + ZSTD | 0.591 | 1.733 | 18.53 |
| basel_wind_f | BYTE_STREAM_SPLIT + ZSTD | 1.405 | 2.191 | 54.12 |
| basel_wind_f | ALP | 0.576 | 29.778 | 29.87 |
| bird_migration_f | PLAIN | 65.238 | 93.070 | 64.01 |
| bird_migration_f | PLAIN + ZSTD | 0.420 | 1.778 | 23.49 |
| bird_migration_f | BYTE_STREAM_SPLIT + ZSTD | 1.210 | 10.407 | 45.82 |
| bird_migration_f | ALP | 0.164 | 27.212 | 20.24 |
| bitcoin_f | PLAIN | 91.371 | 222.346 | 64.07 |
| bitcoin_f | PLAIN + ZSTD | 0.585 | 1.660 | 50.01 |
| bitcoin_f | BYTE_STREAM_SPLIT + ZSTD | 1.345 | 19.512 | 48.79 |
| bitcoin_f | ALP | 0.047 | 30.608 | 27.18 |
| bitcoin_transactions_f | PLAIN | 61.862 | 76.608 | 64.01 |
| bitcoin_transactions_f | PLAIN + ZSTD | 1.081 | 1.985 | 47.96 |
| bitcoin_transactions_f | BYTE_STREAM_SPLIT + ZSTD | 1.412 | 2.580 | 56.65 |
| bitcoin_transactions_f | ALP | 0.572 | 21.192 | 41.27 |
| city_temperature_f | PLAIN | 74.404 | 75.291 | 64.01 |
| city_temperature_f | PLAIN + ZSTD | 0.561 | 1.368 | 17.67 |
| city_temperature_f | BYTE_STREAM_SPLIT + ZSTD | 0.962 | 3.569 | 16.64 |
| city_temperature_f | ALP | 1.972 | 37.725 | 10.80 |
| cms1 | PLAIN | 64.257 | 62.655 | 64.01 |
| cms1 | PLAIN + ZSTD | 0.627 | 1.600 | 26.84 |
| cms1 | BYTE_STREAM_SPLIT + ZSTD | 0.670 | 1.651 | 38.64 |
| cms1 | ALP | 1.061 | 18.514 | 35.19 |
| cms25 | PLAIN | 70.317 | 71.847 | 64.01 |
| cms25 | PLAIN + ZSTD | 0.798 | 1.829 | 58.11 |
| cms25 | BYTE_STREAM_SPLIT + ZSTD | 1.287 | 4.345 | 56.72 |
| cms25 | ALP | 1.516 | 21.901 | 41.17 |
| cms9 | PLAIN | 65.334 | 67.735 | 64.01 |
| cms9 | PLAIN + ZSTD | 0.668 | 1.436 | 11.71 |
| cms9 | BYTE_STREAM_SPLIT + ZSTD | 2.151 | 5.502 | 10.07 |
| cms9 | ALP | 1.932 | 34.393 | 12.16 |
| food_prices | PLAIN | 71.786 | 75.631 | 64.01 |
| food_prices | PLAIN + ZSTD | 0.574 | 1.356 | 18.13 |
| food_prices | BYTE_STREAM_SPLIT + ZSTD | 0.744 | 1.865 | 25.47 |
| food_prices | ALP | 0.887 | 20.747 | 23.20 |
| gov10 | PLAIN | 67.983 | 70.573 | 64.01 |
| gov10 | PLAIN + ZSTD | 0.486 | 1.259 | 29.12 |
| gov10 | BYTE_STREAM_SPLIT + ZSTD | 0.648 | 1.740 | 37.31 |
| gov10 | ALP | 1.119 | 24.621 | 29.88 |
| gov26 | PLAIN | 66.105 | 67.432 | 64.01 |
| gov26 | PLAIN + ZSTD | 10.325 | 23.010 | 0.20 |
| gov26 | BYTE_STREAM_SPLIT + ZSTD | 8.112 | 18.208 | 0.24 |
| gov26 | ALP | 1.876 | 84.789 | 1.40 |
| gov30 | PLAIN | 61.089 | 64.308 | 64.01 |
| gov30 | PLAIN + ZSTD | 2.038 | 5.186 | 4.52 |
| gov30 | BYTE_STREAM_SPLIT + ZSTD | 1.695 | 4.155 | 6.14 |
| gov30 | ALP | 1.020 | 33.276 | 17.88 |
| gov31 | PLAIN | 70.238 | 71.923 | 64.01 |
| gov31 | PLAIN + ZSTD | 3.821 | 8.994 | 1.65 |
| gov31 | BYTE_STREAM_SPLIT + ZSTD | 3.780 | 9.643 | 2.47 |
| gov31 | ALP | 1.659 | 50.153 | 6.77 |
| gov40 | PLAIN | 74.751 | 75.933 | 64.01 |
| gov40 | PLAIN + ZSTD | 9.232 | 17.740 | 0.43 |
| gov40 | BYTE_STREAM_SPLIT + ZSTD | 6.477 | 13.890 | 0.62 |
| gov40 | ALP | 1.879 | 77.866 | 2.59 |
| medicare1 | PLAIN | 73.791 | 65.523 | 64.01 |
| medicare1 | PLAIN + ZSTD | 0.552 | 1.508 | 31.68 |
| medicare1 | BYTE_STREAM_SPLIT + ZSTD | 0.800 | 2.166 | 45.27 |
| medicare1 | ALP | 0.958 | 19.660 | 40.46 |
| medicare9 | PLAIN | 73.908 | 75.228 | 64.01 |
| medicare9 | PLAIN + ZSTD | 0.706 | 1.471 | 11.86 |
| medicare9 | BYTE_STREAM_SPLIT + ZSTD | 2.126 | 5.717 | 10.19 |
| medicare9 | ALP | 1.938 | 36.311 | 12.82 |
| neon_air_pressure | PLAIN | 70.685 | 73.563 | 64.01 |
| neon_air_pressure | PLAIN + ZSTD | 0.789 | 2.051 | 11.85 |
| neon_air_pressure | BYTE_STREAM_SPLIT + ZSTD | 0.782 | 2.268 | 28.51 |
| neon_air_pressure | ALP | 1.876 | 36.770 | 16.48 |
| neon_bio_temp_c | PLAIN | 63.818 | 69.314 | 64.01 |
| neon_bio_temp_c | PLAIN + ZSTD | 0.522 | 1.513 | 16.84 |
| neon_bio_temp_c | BYTE_STREAM_SPLIT + ZSTD | 1.240 | 2.885 | 35.40 |
| neon_bio_temp_c | ALP | 1.941 | 35.578 | 10.81 |
| neon_dew_point_temp | PLAIN | 72.097 | 73.614 | 64.01 |
| neon_dew_point_temp | PLAIN + ZSTD | 0.465 | 1.638 | 23.73 |
| neon_dew_point_temp | BYTE_STREAM_SPLIT + ZSTD | 1.503 | 2.370 | 48.00 |
| neon_dew_point_temp | ALP | 1.931 | 32.863 | 13.63 |
| neon_pm10_dust | PLAIN | 51.533 | 70.722 | 64.01 |
| neon_pm10_dust | PLAIN + ZSTD | 0.848 | 1.689 | 7.79 |
| neon_pm10_dust | BYTE_STREAM_SPLIT + ZSTD | 0.634 | 1.682 | 22.21 |
| neon_pm10_dust | ALP | 0.927 | 38.427 | 8.41 |
| neon_wind_dir | PLAIN | 54.631 | 60.583 | 64.01 |
| neon_wind_dir | PLAIN + ZSTD | 0.432 | 1.312 | 24.41 |
| neon_wind_dir | BYTE_STREAM_SPLIT + ZSTD | 1.387 | 3.518 | 42.31 |
| neon_wind_dir | ALP | 1.883 | 47.114 | 15.94 |
| nyc29 | PLAIN | 71.342 | 71.984 | 64.01 |
| nyc29 | PLAIN + ZSTD | 0.611 | 1.539 | 24.67 |
| nyc29 | BYTE_STREAM_SPLIT + ZSTD | 0.939 | 3.768 | 36.91 |
| nyc29 | ALP | 1.679 | 24.137 | 40.43 |
| poi_lat | PLAIN | 58.440 | 50.294 | 64.01 |
| poi_lat | PLAIN + ZSTD | 0.635 | 1.793 | 57.78 |
| poi_lat | BYTE_STREAM_SPLIT + ZSTD | 2.711 | 5.929 | 55.30 |
| poi_lat | ALP | 1.052 | 11.874 | 88.19 |
| poi_lon | PLAIN | 61.546 | 73.497 | 64.01 |
| poi_lon | PLAIN + ZSTD | 0.850 | 1.945 | 60.44 |
| poi_lon | BYTE_STREAM_SPLIT + ZSTD | 2.467 | 5.826 | 57.24 |
| poi_lon | ALP | 1.180 | 14.614 | 79.12 |
| ssd_hdd_benchmarks_f | PLAIN | 66.698 | 112.905 | 64.02 |
| ssd_hdd_benchmarks_f | PLAIN + ZSTD | 0.813 | 1.802 | 12.98 |
| ssd_hdd_benchmarks_f | BYTE_STREAM_SPLIT + ZSTD | 1.265 | 2.850 | 17.42 |
| ssd_hdd_benchmarks_f | ALP | 0.114 | 35.975 | 16.04 |
| stocks_de | PLAIN | 68.397 | 71.924 | 64.01 |
| stocks_de | PLAIN + ZSTD | 0.664 | 1.689 | 10.07 |
| stocks_de | BYTE_STREAM_SPLIT + ZSTD | 0.881 | 2.278 | 33.46 |
| stocks_de | ALP | 1.224 | 35.921 | 11.20 |
| stocks_uk | PLAIN | 60.600 | 64.531 | 64.01 |
| stocks_uk | PLAIN + ZSTD | 0.608 | 1.413 | 11.29 |
| stocks_uk | BYTE_STREAM_SPLIT + ZSTD | 1.180 | 4.006 | 14.89 |
| stocks_uk | ALP | 0.948 | 32.869 | 12.75 |
| stocks_usa_c | PLAIN | 64.214 | 67.851 | 64.01 |
| stocks_usa_c | PLAIN + ZSTD | 0.692 | 1.634 | 8.24 |
| stocks_usa_c | BYTE_STREAM_SPLIT + ZSTD | 0.712 | 2.390 | 26.89 |
| stocks_usa_c | ALP | 2.028 | 39.329 | 7.95 |
| **ALL AVG.** | **PLAIN** | **65.547** | **76.644** | **64.01** |
| **ALL AVG.** | **PLAIN + ZSTD** | **1.401** | **3.236** | **22.75** |
| **ALL AVG.** | **BYTE_STREAM_SPLIT + ZSTD** | **1.786** | **5.132** | **32.76** |
| **ALL AVG.** | **ALP** | **1.273** | **33.805** | **24.27** |

</details>
