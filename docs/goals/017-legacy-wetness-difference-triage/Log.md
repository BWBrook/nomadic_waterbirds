# Log

Goal: Legacy wetness difference triage

Status: Complete.

## Supervisor Setup

- 2026-05-31: Goal 017 packet created after Goal 016 computed all 33
  all-support direct-S3 probe rows and matched the repaired `NWB002`
  baseline, but left six legacy wetness-field differences that need
  classification before full-window scale-up.

## Execution Checkpoints

- Starting state: 2026-05-31 23:41 AEST; `git status --short --branch`
  reported `## main...origin/main`; `9463980` is an ancestor of `HEAD`, and
  current `HEAD` was `198c7c0` (`Add Goal 017 wetness difference triage
  brief`).
- Required reading complete: 2026-05-31 23:41 AEST; read repo/global
  instructions, Goal 017 `Goal.md` then `Plan.md` then `Runbook.md`, Goal 017
  `Log.md`, required `nectar` compute/data-placement/smoke/current-status
  notes, and inspected required Goal 014-016 artefact structure and target
  rows before editing.
- Goal 016 log status checked/corrected if needed: 2026-05-31 23:41 AEST;
  `docs/goals/016-direct-s3-all-support-probe/Log.md` still said
  `Status: In progress` despite validation and push evidence, so it was
  corrected to `Status: Complete`.
- Ignored staging confirmed: 2026-05-31 23:41 AEST; `git check-ignore`
  confirmed `artifacts/legacy_wetness_difference_triage_017/raw/probe.json`,
  `artifacts/legacy_wetness_difference_triage_017/intermediate/probe.npy`,
  and `artifacts/legacy_wetness_difference_triage_017/output/probe.json` are
  ignored; local staging directories were created under `artifacts/`.
- Six-row target set confirmed: 2026-05-31 23:41 AEST; extracted exactly six
  `wetness_diff` rows from
  `docs/direct_s3_all_support_probe_016_comparison.csv`, matching the Goal 017
  target list.
- Static discrepancy audit complete: 2026-05-31 23:51 AEST; compared the six
  target rows against Goal 016 summary rows and legacy Goal 007/009 reference
  rows, including wetness, support-grid, scene-count, item-hash, and path-row
  fields.
- Bounded reruns complete or not needed: 2026-05-31 23:51 AEST; no bounded
  raster rerun was needed because static evidence separated rounding-only rows
  from material rows whose legacy references lack item/path-row provenance.
- Root-cause classifications complete: 2026-05-31 23:51 AEST; classified four
  rows as `insufficient_reference_evidence` and two rows as
  `tolerance_or_rounding_only`; no row was classified as a current direct-S3
  extraction defect.
- Reports/manifests/CSV outputs written: 2026-05-31 23:51 AEST; wrote
  `docs/legacy_wetness_difference_triage_017_report.md`,
  `docs/legacy_wetness_difference_triage_017_manifest.json`,
  `docs/legacy_wetness_difference_triage_017_audit.csv`,
  `docs/legacy_wetness_difference_triage_017_item_delta.csv`, and
  `docs/legacy_wetness_difference_triage_017_metric_delta.csv`, plus ignored
  run metadata under `artifacts/legacy_wetness_difference_triage_017/output/`.
- Registers/docs/logs updated: 2026-05-31 23:51 AEST; updated
  `docs/README.md`, `docs/data_stream_register.md`, `docs/decision_log.md`,
  this log, and the stale Goal 016 log status.
- Validation complete: 2026-05-31 23:53 AEST; `git diff --check`,
  `python3 -m unittest tests.test_goal017_legacy_wetness_difference_triage`,
  `python3 -m unittest discover -s tests -p 'test*.py'`, JSON parsing,
  audit CSV shape checks, Markdown local-link checks, tracked raw/artifact/size
  hygiene checks, ignored staging checks, unfinished-marker scans, and
  `gh repo view BWBrook/nomadic_waterbirds --json visibility --jq .visibility`
  all passed. GitHub visibility was `PRIVATE`.
- Commit/push complete: 2026-05-31 23:54 AEST; committed the validated Goal
  017 package and pushed `main` to `origin` after validation.

## Notes

- Do not broaden into production extraction.
- Every target row needs a root-cause class and a scale-up recommendation.
- Keep raw rerun artefacts in ignored staging only.
