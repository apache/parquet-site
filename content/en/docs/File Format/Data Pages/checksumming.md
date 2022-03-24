---
title: "Checksumming"
linkTitle: "Checksumming"
weight: 7
---
Column chunks are composed of pages written back to back. The pages share a common header and readers can skip over page they are not interested in. The data for the page follows the header and can be compressed and/or encoded. The compression and encoding is specified in the page metadata.
