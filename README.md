# Spatial Agent Benchmark

Prototype CompBioBench-style benchmark tasks based on the spatial transcriptomics clustering benchmark paper.

## Goal

Create small, objectively gradable computational biology tasks that test whether Codex can perform spatial transcriptomics analysis steps inspired by Yuan et al. Nature Methods 2024.

## Initial task categories

1. Clustering accuracy evaluation on DLPFC-like spatial domains
2. Detection of noncontinuous-domain failure modes
3. Marker gene detection and spatial autocorrelation

## Project structure

- questions/: benchmark CSV files for compbiobench-runner
- data/: input files for each benchmark question
- answer_keys/: expected outputs for each question
- grading/: scripts to compare Codex outputs to answer keys
- reports/: writeups and final report
- notes/: setup notes, run logs, observations
- runs/: copied benchmark outputs from compbiobench-runner
