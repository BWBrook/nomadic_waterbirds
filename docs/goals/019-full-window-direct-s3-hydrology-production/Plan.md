# Plan

## Purpose

Move from bounded direct-S3 hydrology evidence to the first production
full-window hydrology table for the current 11-support analysis set.

The key management risk is silent incompleteness. The workflow should prefer a
complete status-classified grid over a prettier table with missing or
unexplained rows.

## Expected File Responsibilities

- `settings/direct_s3_full_window_hydrology_019.json`: support set, month
  window, route settings, remote/local staging paths, sharding, status
  vocabulary, and output paths.
- `scripts/direct_s3_full_window_hydrology_019.py`: direct-S3 preflight and
  production workflow, with restart/resume support and compact final outputs.
- `tests/test_goal019_direct_s3_full_window_hydrology.py`: focused tests for
  grid construction, path-row policy, status classification, schema,
  restartability, derived metric boundaries, and raw-data exclusion.
- `docs/direct_s3_full_window_hydrology_019_preflight.json`: preflight inputs,
  commands, hashes, and pass/fail decision.
- `docs/direct_s3_full_window_hydrology_019_series.csv`: production
  support-month hydrology table when production launches.
- `docs/direct_s3_full_window_hydrology_019_item_sets.csv`: compact
  item/path-row provenance per support-month.
- `docs/direct_s3_full_window_hydrology_019_summary.csv`: coverage, status,
  quality, and support-level summaries.
- `docs/direct_s3_full_window_hydrology_019_manifest.json`: reproducibility,
  source, remote, staging, hash, status, and validation provenance.
- `docs/direct_s3_full_window_hydrology_019_report.md`: supervisor-facing
  result and Goal 020 recommendation.
- `docs/data_stream_register.md`, `docs/decision_log.md`, `docs/README.md`:
  project context updates.
- `docs/goals/019-full-window-direct-s3-hydrology-production/Log.md`: live
  execution log.

## Task Sequence

1. Confirm clean starting state and that Goal 018 is in history.
2. Read required repo/global/`nectar` docs and Goal 013-018 evidence.
3. Probe `deep-server-ts` and prepare `/data/codex/repos/nomadic_waterbirds_goal019`.
4. Confirm ignored staging paths locally and remotely.
5. Write focused tests and settings before the full run.
6. Implement or adapt the direct-S3 workflow with shard-level restartability.
7. Run remote preflight over representative support-months.
8. Prove preflight resume/rerun hash stability.
9. If preflight passes, run the full 924-row production grid remotely.
10. Rerun with resume enabled and record stable final hashes.
11. Pull back only compact committed outputs and logs/provenance needed for
    review; leave raw/intermediate files ignored.
12. Write report, manifest, preflight file, series table, item-set table, and
    summary table.
13. Update docs index, data stream register, decision log, and Goal 019 log.
14. Run validation gates.
15. Commit and push if validation passes.

## Production Grid

- Supports: current 11 supports from Goal 016.
- Months: `2018-01` through `2024-12`.
- Expected rows: 924.
- Route: direct S3 only.
- Scene-selection policy: support-intersecting WRS path/rows from Goal 013 and
  Goal 015.

## Stop Rules

- Do not launch production if remote preflight fails.
- Do not use STAC as a production dependency.
- Do not silently omit support-months.
- Do not commit raw rasters, listings, geometry, arrays, databases, archives,
  or bulky remote artefacts.
- Do not change scientific supports or metric definitions without narrow
  evidence, tests, and documentation.
- If production has blocked rows, keep the full status-classified grid and
  recommend a recovery goal rather than hiding the blockers.

## Self-Review Questions

- Did the workflow run on the selected remote host rather than forcing another
  local fallback?
- Is every expected support-month represented exactly once?
- Are computed and blocked rows clearly distinguished?
- Are direct-S3 item sets compactly provenanced by path/row, count, and hash?
- Does resume/rerun evidence prove restartability?
- Are derived hydrology metrics clearly separated from base monthly metrics?
- Are downstream ecological claims avoided?
- Is the Goal 020 recommendation based on the production evidence rather than
  the desire to move to birds quickly?
