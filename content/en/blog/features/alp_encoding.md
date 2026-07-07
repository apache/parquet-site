---
title: "ALP lightweight floating-point encoding in Apache Parquet"
date: 2026-06-23
description: "The consensus building machine strikes again"
author: "[Konstantin Tarasov](https://github.com/sdf-jkl)"
categories: ["features"]
---

## What is ALP?

ALP is a new lightweight floating-point encoding that shows better compression ratio than heavy-weight encodings like zstd **and** faster [de]compression speed than other lightweight floating-point encodings.

It was developed by the folks at [CWI](https://www.cwi.nl/en/research/database-architectures/) and uses smart tricks to represent floating-point data as integers.

ALP shines at data like:
- Monetary values (exchange rates, public funds, stocks, prices, etc.)
- Geographic coordinates (longtitute/latitude)
- Scientific measures (temperature, pressure, speed, degrees, energy, etc.)
- Timestamps stored as floating-point

## Why ALP?

<!-- Explains the usecase of ALP (decimal data that was stored in FLOAT/DOUBLE columns), single row decode -->

Two reasons to care:
1) Less storage/faster read/write
2) Better partition pruning support

### Better physical data representation

Better, faster, stronger? But how much?

<!-- Compression ratio table here I think the paper one looks better, but it's not really exactly the same -->

[De]compression speed improvement depends on the Parquet reader/writer implementation, but users can expect performance simialar to one provided in the paper.

<!-- Compression/decompression table here -->

### The most efficient way to read is to not read at all

One of the gripes users have with parquet is opimization for random access[1]. The minimum amount of data you need to decode and decompress in Parquet is usually the entire page.

ALP encoding avoids that by splitting the page into vectors (usually 1024-len, for better SIMD and being able to store in L1). Each vector stores the necessary metadata to decode any row inside. More in the [Technical overview](#technical-overview).

This way, instead of:

- Load the whole page to retrieve the value

Becomes:

- Load just the page metadata -> Get the vector offset -> only decode that vector

This basically introduces lower grain than a Parquet page and can significantly speed up single row decode/random access.

## Technical overview

<!-- Gives a technical overview of the encoding (with diagrams) -->

ALP takes inspiration from [PDE (Pseudodecimal encoding)](https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf) and havily improves on it.

The way that PDE works is by finding the smallest precision integer to represent the floating-point value.

For example:
```
8.0605 that can't be physically represented in [IEEE 754](https://ieeexplore.ieee.org/document/8766229) as is, is instead approximated as 8.06049999999999933209.

PDE takes a value and brute-force searches over the exponent, where - significand = round(value × 10^e)

For this value it should get to 80605 with exponent 4.
```

The catch is PDE keeps an exponent per each value.

The key ideas behind ALP are:
- the majority of floating-point values share similar decimal precision within 1024-len vectors
- there is a huge room and benefit in vectorizing the encoding

The first idea leads to an improvement over PDE. Instead of storing an exponent per value, we store it per vector.

This leads to smaller metadata storage footprint.

The second idea uses SIMD intrinsics to make the code as parallelizable as possible to achieve greater [de]compression speeds.

### ALP Encoding pipeline in Paruqet

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


<!-- A note on scope: no ALPrd -->

ALP paper also introduces an ALPrd enocding. It's used when ALP can't compress enought values in a row group. Apache Parquet already implements similar mechanism via BYTE_STREAM_SPLIT + ZSTD, therefore this encoding was not included.

## Ecosystem adoption

<!-- References the ALP paper (and probably mentions its adoption by other formats like Vortex) -->

The paper was published in 2024 and now has a sibling G-ALP https://ir.cwi.nl/pub/35205/35205.pdf for optimized for GPUs.

Since then ALP has been adopted by the new file formats like Vortex [https://github.com/vortex-data/vortex], F3 [https://github.com/future-file-format/f3] and Fastlanes (created by the same folks as ALP) [https://github.com/cwida/fastlanes]. 

These formats aspire to dethrone Parquet, some(Vortex) say - "Parquet is for the floor" 

<can insert a picture of their sticker>. 

This comment may sound mean, but what it really means is that Parquet stands as a baseline and a benchmark for the new contenders. 

The new file formats are created and improving rapidly because they don't have to worry about backwards compatibility for a giant userbase. Parquet, however, does not stand in place - it's a moving target. It takes more time, but it learns from the new formats and their ideas and implements them.

## Real-World Examples

<!-- Gives some more examples -->

## Conclusion

<!-- Recap of ALP's significance for Parquet -->

ALP encoding will bridge the gap between Parquet and parallelizible + random access for floating-point data. One step closer to meeting the needs of the rapidly scaling environment.

## Resources

- [ALP paper (CWI)](https://ir.cwi.nl/pub/33334/33334.pdf)
- [Column Storage for the AI era](https://sympathetic.ink/2025/12/11/Column-Storage-for-the-AI-era.html)
- [Column Storage for the AI era - file formats encoding parity slide](https://docs.google.com/presentation/d/19F-XvNJ8sgIpIeIduA3PhbsWp4pC-P632J2eJV1cLG8/edit?slide=id.g3b660485fe2_0_9#slide=id.g3b660485fe2_0_9)
- [ALP Parquet encoding PR](https://github.com/apache/parquet-format/pull/557)
- [BtrBlocks paper](https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf)