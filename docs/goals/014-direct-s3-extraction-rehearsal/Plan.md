# Plan

## Purpose

Move from metadata equivalence to extraction-method evidence. Goal 014 should
prove whether direct S3 COG reads and support aggregation reproduce existing
STAC-derived event-window metrics for `NWB002` at bounded scale.

## Expected File Responsibilities

- `settings/direct_s3_extraction_rehearsal_014.json`: support, months,
  path/rows, source product, tolerance rules, staging paths, and output paths.
- `scripts/direct_s3_extraction_rehearsal_014.py`: small extraction rehearsal
  script for item-set validation, COG reads, support masking, base metric
  aggregation, comparison, and compact output writing.
- `tests/test_goal014_direct_s3_extraction.py`: focused tests for helper
  functions and output contracts.
- `docs/direct_s3_extraction_rehearsal_014_report.md`: narrative result,
  limitations, comparison status, and next-step recommendation.
- `docs/direct_s3_extraction_rehearsal_014_manifest.json`: machine-readable
  command, route, item, read, comparison, host, and staging provenance.
- `docs/direct_s3_extraction_rehearsal_014_summary.csv`: three direct-S3
  monthly metric rows.
- `docs/direct_s3_extraction_comparison_014.csv`: comparison against existing
  STAC-derived event-window metrics and Goal 009 blocked status.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`: project context updates.
- `docs/goals/014-direct-s3-extraction-rehearsal/Log.md`: live log.

## Task Sequence

1. Confirm clean repo state and required checkpoint.
2. Read required instructions, `nectar` docs, and Goal 013 evidence.
3. Check Goal 013 manifest/log/report consistency; correct only confirmed
   provenance inconsistencies.
4. Confirm ignored staging paths before raster reads or intermediate arrays are
   written.
5. Write focused tests for item-set validation, aggregation helpers, tolerance
   comparison, and raw-extension exclusion.
6. Implement the bounded rehearsal script/config, reusing existing hydrology
   code where practical.
7. Validate Goal 013 item counts and hashes for the three months.
8. Run a tiny direct COG read probe.
9. Run direct-S3 extraction for `NWB002` and three months only.
10. Compare `2022-11` and `2024-12` to existing event-window metrics.
11. Write compact CSV/JSON/Markdown outputs and update registers/logs.
12. Validate code, outputs, docs, links, Git/data hygiene, and comparison
    status.
13. Commit and push if validation passes.

## Self-Review Questions

- Did this goal prove extraction behaviour rather than only metadata access?
- Are all raw rasters and intermediates ignored?
- Do overlapping months match existing event-window metrics within predeclared
  tolerances?
- Is `2018-01` clearly labelled as a rehearsal row, not full-window recovery?
- Is the recommended Goal 015 an evidence-based scale step rather than a leap?
