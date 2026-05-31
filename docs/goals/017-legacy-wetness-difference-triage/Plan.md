# Plan

## Purpose

Classify the six Goal 016 wetness-field differences against legacy reference
rows before promoting direct S3 to a full-window hydrology extraction route.
The goal should produce an auditable discrepancy package, not a new production
table.

## Expected File Responsibilities

- `settings/legacy_wetness_difference_triage_017.json`: target rows,
  tolerances, root-cause vocabulary, input/output paths, staging paths, and
  optional bounded-rerun settings.
- `scripts/legacy_wetness_difference_triage_017.py`: compact triage script for
  selecting the six target rows, joining Goal 016 and reference metrics,
  computing field deltas, checking item/path-row evidence, assigning or
  recording root-cause classifications, and writing CSV/JSON/Markdown outputs.
- `tests/test_goal017_legacy_wetness_difference_triage.py`: focused tests for
  target selection, delta calculations, tolerance handling, root-cause
  vocabulary, schema, and raw-data exclusion.
- `docs/legacy_wetness_difference_triage_017_report.md`: narrative diagnosis
  and Goal 018 recommendation.
- `docs/legacy_wetness_difference_triage_017_manifest.json`: command, source,
  target-row, route, host, rerun, output, staging, and validation provenance.
- `docs/legacy_wetness_difference_triage_017_audit.csv`: one row per target
  discrepancy with classification and recommendation.
- `docs/legacy_wetness_difference_triage_017_item_delta.csv`: path/row,
  item-hash, asset-hash, scene-count, and support-grid comparison.
- `docs/legacy_wetness_difference_triage_017_metric_delta.csv`: field-level
  metric deltas for the target rows.
- `docs/goals/016-direct-s3-all-support-probe/Log.md`: stale status fix if
  required.
- `docs/data_stream_register.md`, `docs/decision_log.md`, `docs/README.md`:
  project context updates.
- `docs/goals/017-legacy-wetness-difference-triage/Log.md`: live execution
  log.

## Task Sequence

1. Confirm clean repo state and that `9463980` is in history.
2. Read required repo/global/`nectar` instructions and Goal 014-016 evidence.
3. Correct Goal 016 `Log.md` status if it is still stale.
4. Confirm ignored staging paths.
5. Write focused tests for target-row selection, delta calculations,
   classification vocabulary, schemas, and raw-data exclusion.
6. Implement the bounded triage script/config.
7. Generate the six-row audit, item/path-row delta, and metric-delta tables.
8. Run bounded reruns only if the static evidence cannot classify a target
   row.
9. Write the report and manifest.
10. Update docs index, data stream register, decision log, and Goal 017 log.
11. Run validation gates, including focused tests, full tests, JSON/CSV checks,
    link checks, raw-data hygiene checks, and final Git status.
12. Commit and push if validation passes.

## Stop Rules

- Stop before full-window extraction.
- Stop before changing the support set.
- Stop and write a blocker if the six-row audit cannot classify a difference
  without a larger rerun.
- If a current direct-S3 extraction defect is found, fix only that defect with
  a regression test, regenerate only affected bounded outputs, and recommend a
  repeat bounded probe rather than production scale-up.

## Self-Review Questions

- Are exactly the six Goal 016 wetness-difference rows audited?
- Does every row have a root-cause class, evidence basis, and scale-up
  recommendation?
- Are tolerance-only differences separated from material wetness differences?
- Are legacy scene-selection, support-grid, metric-formula, and current-route
  defect explanations kept distinct?
- Is the Goal 018 recommendation earned by the evidence rather than by the
  desire to move on?
