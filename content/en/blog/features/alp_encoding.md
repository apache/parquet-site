---
title: "ALP lightweight floating-point encoding in Apache Parquet"
date: 2026-07-08
description: "The consensus building machine strikes again"
author: "[Konstantin Tarasov](https://github.com/sdf-jkl)"
categories: ["features"]
---

## What is ALP?

ALP (Adaptive Lossless floating-Point) is a new lightweight floating-point encoding that shows a better compression ratio than heavyweight compressors like zstd **and** faster [de]compression speed than other lightweight floating-point encodings.

It was developed by the folks at [CWI](https://www.cwi.nl/en/research/database-architectures/) and uses smart tricks to represent floating-point data as integers.

ALP shines at data like:
- Monetary values (exchange rates, public funds, stocks, prices, etc.)
- Geographic coordinates (longitude/latitude)
- Scientific measures (temperature, pressure, speed, degrees, energy, etc.)
- Timestamps stored as floating-point

## Why ALP?

### Better physical data representation

Better, faster, stronger? But how much?

<!-- Compression ratio table here I think the paper one looks better, but it's not really exactly the same -->

[De]compression speed improvement depends on the Parquet reader/writer implementation, but users can expect performance similar to what the paper reports.

<!-- Compression/decompression table here -->

### The most efficient way to read is to not read at all

One of the [gripes users have with Parquet](https://sympathetic.ink/2025/12/11/Column-Storage-for-the-AI-era.html) is that it is not optimized for random access. The minimum amount of data you need to decompress and decode in Parquet is usually an entire page.

ALP encoding avoids that by splitting the page into vectors (usually 1024 values each, sized for SIMD and for fitting in L1 cache). Each vector stores the necessary metadata to decode any row inside.

**Before**, reading a single value:

> Load the whole page → decompress and decode all of it → retrieve the value

**After**, with ALP:

> Load just the page metadata → get the vector offset → decode only that vector

This introduces a finer read granularity than the Parquet page and can significantly speed up single-row decodes and random access.

## Technical overview

ALP takes inspiration from [PDE (Pseudodecimal encoding)](https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf) and heavily improves on it.

PDE works by finding the smallest integer, paired with a decimal exponent, that represents the floating-point value exactly.

For example:

> 8.0605 can't be physically represented in [IEEE 754](https://ieeexplore.ieee.org/document/8766229) as is, and is instead approximated as 8.06049999999999933209.
>
> PDE takes the value and brute-force searches over exponents, computing `significand = round(value × 10^e)` for each.
>
> For this value it arrives at significand 80605 with exponent 4.

The catch is that PDE stores an exponent for every single value.

The key ideas behind ALP are:
- the majority of floating-point values share similar decimal precision within vectors
- there is a huge benefit in vectorizing the encoding

The first idea leads to an improvement over PDE. Instead of storing an exponent per value, we store it per vector. This way we get a much smaller metadata footprint.

The second idea uses SIMD intrinsics to make the code as parallelizable as possible to achieve greater [de]compression speeds.

### ALP Encoding pipeline in Parquet

The way that ALP encodes data is:

                    Input: float/double array
                              |
                              v
    +----------------------------------------------------------+
    |  1. CHOOSE PARAMETERS                                    |
    |     Select (exponent, factor) pair for this vector       |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  2. DECIMAL ENCODING                                     |
    |     encoded[i] = fast_round(value[i] * 10^e * 10^(-f))  |
    |     Detect exceptions where decode(encode(v)) != v       |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  3. FRAME OF REFERENCE (FOR)                             |
    |     min_val = min(encoded[])                             |
    |     delta[i] = encoded[i] - min_val                      |
    +----------------------------------------------------------+
                              |
                              v
    +----------------------------------------------------------+
    |  4. BIT PACKING                                          |
    |     bit_width = ceil(log2(max_delta + 1))                |
    |     Pack each delta into bit_width bits                  |
    +----------------------------------------------------------+
                              |
                              v
                   Output: Serialized vector bytes

**1. Choose parameters**

First, sample multiple vectors within a row group to find the overall best combinations of exponent and factor.

Then re-evaluate those candidate combinations on each vector to pick the pair that compresses it best.

**2. Decimal encoding**

Encode each value with the formula above, then round-trip it (decode it back) to make sure it matches the original.

If the round-trip fails, the value is added to the vector's exceptions list.

**3. Frame of reference (FOR)**

Once the values are encoded as integers, we pick the smallest one as the frame of reference. Every value is then stored as its delta from that minimum.

**4. Bit packing**

Finally, we take the bit width of the largest delta and pack every delta into that many bits.


### ALPrd

The ALP paper also introduces an ALPrd encoding, used when ALP can't compress enough of the values in a row group. Apache Parquet already provides a similar mechanism via BYTE_STREAM_SPLIT + ZSTD, so ALPrd was not included.

## Ecosystem adoption

The paper was published in 2024 and now has a sibling [G-ALP](https://ir.cwi.nl/pub/35205/35205.pdf) optimized for GPUs.

Since then ALP has been adopted as the default floating-point encoding by [DuckDB](https://duckdb.org/2024/02/13/announcing-duckdb-0100#adaptive-lossless-floating-point-compression-alp) and [CedarDB](https://cedardb.com/blog/release_notes/early_2026/#better-compression-less-storage-floats-and-text), and implemented as a codec by [ClickHouse](https://github.com/ClickHouse/ClickHouse/pull/91362).

It has also been adopted by the new file formats like [Vortex](https://github.com/vortex-data/vortex), [F3](https://github.com/future-file-format/f3) and [FastLanes](https://github.com/cwida/fastlanes) (created by the same folks as ALP).

These formats aspire to dethrone Parquet, some (Vortex) say - ["Parquet is for the floor"](<!--I'll get a picture and add a link here -->).

This comment may sound mean, but what it really means is that Parquet stands as a baseline and a benchmark for the new contenders.

The new file formats improve rapidly because they don't have to worry about backwards compatibility for a giant userbase. Parquet, however, does not stand still: it's a moving target. It takes more time, but it learns from the new formats and adopts their best ideas.

## Conclusion

ALP brings fast, parallelizable decoding and practical random access to floating-point data in Parquet. It's one more step toward closing the gap with the newest file formats.

## Resources

- [ALP paper (CWI)](https://ir.cwi.nl/pub/33334/33334.pdf)
- [Column Storage for the AI era](https://sympathetic.ink/2025/12/11/Column-Storage-for-the-AI-era.html)
- [Column Storage for the AI era slides - file formats encoding parity slide](https://docs.google.com/presentation/d/19F-XvNJ8sgIpIeIduA3PhbsWp4pC-P632J2eJV1cLG8/edit?slide=id.g3b660485fe2_0_9#slide=id.g3b660485fe2_0_9)
- [ALP Parquet encoding PR](https://github.com/apache/parquet-format/pull/557)
- [BtrBlocks paper](https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf)