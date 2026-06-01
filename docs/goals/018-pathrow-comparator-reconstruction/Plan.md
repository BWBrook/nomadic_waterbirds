# Plan

## Purpose

Replace the four insufficient legacy validation rows from Goal 017 with a
bounded path-row-filtered comparator or item-provenance reconstruction. The
goal should decide whether direct-S3 hydrology is ready for a full-window
production extraction goal.

## Expected File Responsibilities

- `settings/pathrow_comparator_reconstruction_018.json`: target selection,
  route settings, status/readiness vocabularies, input/output paths, staging
  paths, and optional remote settings.
- `scripts/pathrow_comparator_reconstruction_018.py`: bounded script for
  selecting material target rows, deriving support path/rows, reconstructing
  direct-S3 item provenance, querying/filtering STAC when available, comparing
  item sets, assigning readiness classes, and writing CSV/JSON/Markdown
  outputs.
- `tests/test_goal018_pathrow_comparator_reconstruction.py`: focused tests for
  target selection, path/row grouping, item-hash comparison, status
  classification, readiness classification, schemas, and raw-data exclusion.
- `docs/pathrow_comparator_reconstruction_018_report.md`: narrative result
  and Goal 019 recommendation.
- `docs/pathrow_comparator_reconstruction_018_manifest.json`: command, source,
  target, route, host, output, staging, and validation provenance.
- `docs/pathrow_comparator_reconstruction_018_targets.csv`: selected target
  and optional control rows.
- `docs/pathrow_comparator_reconstruction_018_item_sets.csv`: route-level item
  counts and hashes.
- `docs/pathrow_comparator_reconstruction_018_comparison.csv`: item-set
  comparison table.
- `docs/pathrow_comparator_reconstruction_018_readiness.csv`: row-level
  readiness and scale-up recommendation table.
- `docs/data_stream_register.md`, `docs/decision_log.md`, `docs/README.md`:
  project context updates.
- `docs/goals/018-pathrow-comparator-reconstruction/Log.md`: live execution
  log.

## Task Sequence

1. Confirm clean repo state and that `8515169` is in history.
2. Read required repo/global/`nectar` instructions and Goal 013-017 evidence.
3. Confirm ignored staging paths.
4. Write focused tests for material-target selection, path/row grouping,
   item-hash comparison, route status, readiness classes, schemas, and raw
   exclusion.
5. Implement the bounded comparator/provenance script and settings.
6. Build the four-row material target table, with optional controls labelled.
7. Reconstruct direct-S3 item provenance for each material target.
8. Query and filter STAC metadata when available, keeping raw STAC caches in
   ignored staging only.
9. Compare path-row-filtered STAC item sets to direct-S3 item sets and Goal
   016 hashes.
10. Run bounded diagnostic raster reruns only if item mismatch requires it.
11. Write report, manifest, item-set table, comparison table, and readiness
    table.
12. Update docs index, data stream register, decision log, and Goal 018 log.
13. Run validation gates, including focused tests, full tests, JSON/CSV checks,
    link checks, raw-data hygiene checks, and final Git status.
14. Commit and push if validation passes.

## Stop Rules

- Stop before full-window extraction.
- Stop before changing the support set.
- Stop if STAC and direct-S3 item evidence disagree, unless the cause is found
  and fixed within the bounded target set.
- Stop with a blocker if external route failures prevent enough evidence for
  the four material rows.
- If a current direct-S3 item-selection or extraction defect is found, fix only
  that defect with a regression test and recommend a repeat bounded probe
  before production.

## Self-Review Questions

- Did the target table include exactly the four material Goal 017 rows?
- Are optional controls clearly labelled and kept out of the main readiness
  decision?
- Does every material target have path/row evidence, item counts, hashes,
  route status, readiness class, and recommendation?
- Does the Goal 019 recommendation follow from comparator/provenance evidence,
  not from impatience to scale?
