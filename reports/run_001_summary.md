# Run 001 Summary

## Overview

This run evaluated Codex on three CompBioBench-style spatial transcriptomics benchmark questions derived from the DLPFC 10x Visium sample 151673 and augmented spatial-domain tasks.

## Questions

| Question | Task | Result |
|---|---|---|
| srt-accuracy-q1 | Clustering accuracy evaluation using NMI, homogeneity, and completeness | Pass |
| srt-marker-q1 | Domain marker genes and Moran's I spatial autocorrelation | Pass with numeric tolerance |
| srt-noncontinuous-q1 | Rare noncontinuous-domain recovery versus global NMI | Pass |

## Key observations

Q1 was a clean exact match. Codex correctly identified `bass_like` as the best prediction column and matched all metrics.

Q2 identified all top marker genes correctly. Moran's I values differed slightly from the answer key because the prompt did not fully specify the kNN implementation, tie-breaking, or exact Moran's I implementation. This suggests spatial-statistics benchmark questions should either use tolerance-based grading or specify exact implementation details.

Q3 was the strongest biological reasoning task. Codex correctly recognized that `spatial_smooth_method` had higher global NMI but completely missed the rare noncontinuous domain, while `expression_weighted_method` had lower global NMI but recovered most of the rare domain.

## Interpretation

This mini-benchmark shows that Codex can complete several bounded spatial transcriptomics analysis tasks. It also reveals an important benchmark-design issue: exact-string grading is appropriate for some metric tasks, but spatial-statistics tasks may require either strict implementation prompts or tolerance-aware grading.
