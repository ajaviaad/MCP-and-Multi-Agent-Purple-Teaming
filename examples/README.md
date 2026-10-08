# Example data

`baseline/` contains actual output from the unchanged core CLI executed during companion preparation. It includes the complete synthetic event/protocol trace, JSON and CSV summaries, and a provenance record. It contains deliberately printed test-key signatures and synthetic canaries; these are not real credentials.

`paired-outcomes.csv` is a constructed 100-case statistical example: two successes in both conditions, 28 in baseline only, none in hardened only, and 70 in neither. It reproduces `decision_stats.py --demo`. It is **not** a collection of observed model trials and is separate from the 96 deterministic executions.

Timing fields in observed runs vary between systems. Compare effect predicates and counts, not byte-for-byte timings. Read [measurement](../docs/measurement.md) before drawing an inference.
