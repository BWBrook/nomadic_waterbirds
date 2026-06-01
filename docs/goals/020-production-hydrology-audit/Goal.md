# Goal: Production Hydrology Audit And Bird-Linkage Gate

## Objective

Audit the Goal 019 full-window direct-S3 hydrology production table and decide
whether it is ready to become the hydrology covariate layer for the first
bird-observation linkage design goal.

This goal should classify the `23` computed `quality_fail` rows, check the
support/month/derived-metric consistency of the `924`-row production grid, and
produce a clear hydrology-to-bird-data readiness recommendation.

## Why This Matters

Goal 019 was a major evidence transition: the project now has a complete
`2018-01` through `2024-12` direct-S3 hydrology table for the current `11`
supports, with no blocked support-month rows and stable resume/rerun hashes.

Before linking this layer to eBird, Birdata, ALA, or EAWS records, the project
needs a hydrology audit that separates:

- acceptable low-quality but status-classified months;
- rows that should be excluded from core bird-response modelling;
- rows that need sensitivity treatment;
- any genuine production-route or metric-contract problem that must be fixed
  first.

## Operating Mode

Hydrology-production QA, metric-caveat audit, and design-gate decision. No new
remote production run, no biodiversity data acquisition, no ecological
interpretation.

## Scope

In scope:

- read repo instructions, this goal packet, Goal 019 artefacts, current
  hydrology metric spec, data stream register, decision log, and relevant Goal
  015-018 route/provenance evidence;
- inspect `docs/direct_s3_full_window_hydrology_019_series.csv`,
  `docs/direct_s3_full_window_hydrology_019_item_sets.csv`,
  `docs/direct_s3_full_window_hydrology_019_summary.csv`,
  `docs/direct_s3_full_window_hydrology_019_manifest.json`, and
  `docs/direct_s3_full_window_hydrology_019_preflight.json`;
- classify every `quality_fail` row by likely audit category using existing
  production fields only;
- summarize quality, missingness, wetness, derived-metric status, regional
  metric status, item counts, and support/month coverage;
- check consistency between the series, item-set, summary, manifest, and Goal
  019 log;
- identify which support-month rows should be eligible for core analyses,
  sensitivity-only analyses, or exclusion before bird linkage;
- document retained caveats from Goal 018 and Goal 019, including the lack of
  independent STAC comparator evidence for four retired legacy rows;
- update docs navigation, data stream register, decision log, and this goal
  log;
- commit and push the validated audit package to `main`.

Out of scope:

- rerunning Goal 019 production extraction;
- changing hydrology metric values, support definitions, path-row policy,
  quality thresholds, or scene-selection policy unless a narrow documentation
  correction is clearly required;
- downloading, requesting, or processing eBird, Birdata, ALA, EAWS, or other
  biodiversity data;
- fitting bird-response models;
- making ecological claims about waterbird response, refuges, breeding, or
  wetland role;
- launching remote/HPC jobs;
- committing raw rasters, S3 listings, WRS geometry, masks, arrays, GeoJSON,
  GeoPackages, shapefiles, NetCDF, Parquet, RDS, SQLite/DuckDB stores,
  archives, remote caches, or bulky derived products.

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `docs/goals/019-full-window-direct-s3-hydrology-production/Goal.md`
- `docs/goals/019-full-window-direct-s3-hydrology-production/Log.md`
- `docs/direct_s3_full_window_hydrology_019_report.md`
- `docs/direct_s3_full_window_hydrology_019_manifest.json`
- `docs/direct_s3_full_window_hydrology_019_preflight.json`
- `docs/direct_s3_full_window_hydrology_019_series.csv`
- `docs/direct_s3_full_window_hydrology_019_item_sets.csv`
- `docs/direct_s3_full_window_hydrology_019_summary.csv`
- `docs/hydrology_metric_spec.md`
- `docs/pathrow_comparator_reconstruction_018_report.md`
- `docs/pathrow_comparator_reconstruction_018_readiness.csv`
- `docs/legacy_wetness_difference_triage_017_report.md`
- `docs/comparator_baseline_repair_015_report.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `b5270dc` (`Run full-window direct S3
  hydrology production`).
- Inspect files with `rg --files`.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Audit Categories

Assign every Goal 019 row a bird-linkage readiness class:

- `core_eligible`: row passes `quality_minimum` or better and has valid base,
  derived, regional, and item-provenance fields for its expected temporal
  context.
- `core_eligible_with_caveat`: row passes `quality_minimum` or better, but a
  documented caveat should be carried into modelling or sensitivity notes.
- `sensitivity_only`: row is computed but has `quality_fail`, edge-month
  derived-metric limits, or another nonfatal caveat that should exclude it
  from core fits but preserve it for sensitivity/coverage reporting.
- `exclude_before_bird_linkage`: row is computed but should not be used in
  bird-linkage work unless a later recovery or metric correction resolves the
  issue.
- `blocked_requires_recovery`: row or artefact evidence reveals a production
  defect that should block bird linkage.

For each `quality_fail` row, assign a `quality_fail_reason` using a fixed
vocabulary such as:

- `low_clear_fraction`;
- `low_clear_pixel_support`;
- `low_scene_count`;
- `low_support_area_after_mask`;
- `derived_metric_boundary`;
- `regional_metric_boundary`;
- `provenance_or_hash_issue`;
- `unexpected_nonfinite_metric`;
- `other_documented_caveat`.

Refine the vocabulary if the data demand it, but keep it explicit and stable.

## Required Deliverables

Create:

- `docs/direct_s3_full_window_hydrology_020_audit_report.md`: supervisor-facing
  audit report with headline status, quality-fail classification, support and
  month risk patterns, readiness recommendation, and caveats for the next
  bird-linkage goal.
- `docs/direct_s3_full_window_hydrology_020_manifest.json`: machine-readable
  provenance including source files, row counts, hashes checked, audit
  categories, validation outcomes, and the final readiness decision.
- `docs/direct_s3_full_window_hydrology_020_quality_fail_rows.csv`: one row
  per Goal 019 `quality_fail` row with support, month, relevant quality fields,
  hydrology values, item/provenance fields, audit category, reason, and
  recommended use.
- `docs/direct_s3_full_window_hydrology_020_readiness.csv`: one row per
  support-month, keyed to Goal 019 series rows, with bird-linkage readiness
  class, caveat code, and recommended analysis role.
- `docs/direct_s3_full_window_hydrology_020_support_summary.csv`: support-level
  readiness and quality summary.
- `docs/direct_s3_full_window_hydrology_020_month_summary.csv`: month-level
  readiness and quality summary.
- `docs/hydrology_to_bird_linkage_gate_020.md`: decision memo stating whether
  the hydrology layer is ready for a first constrained bird-observation
  linkage design goal, and what restrictions should apply.
- `scripts/audit_direct_s3_full_window_hydrology_020.py`: audit script.
- `settings/audit_direct_s3_full_window_hydrology_020.json`: input/output
  paths, thresholds, category vocabulary, and expected row counts.
- `tests/test_goal020_hydrology_audit.py`: focused tests for grid checks,
  `quality_fail` classification, readiness classes, schema, hash consistency,
  and raw-data exclusion.

Update:

- `docs/data_stream_register.md`;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/020-production-hydrology-audit/Log.md`.

Update `docs/hydrology_metric_spec.md` only if the audit finds an ambiguity
that must be clarified before bird linkage.

## Validation Gates

Required validation:

- `git diff --check`;
- focused Goal 020 tests;
- full `python3 -m unittest discover -s tests -p 'test*.py'`;
- JSON parsing for settings and manifest;
- CSV schema checks for audit/readiness/support/month outputs;
- expected-grid check: `924` readiness rows, `11` supports, `84` months;
- `quality_fail` check: exactly `23` quality-fail audit rows unless Goal 019
  source data prove otherwise;
- consistency check against Goal 019 manifest hashes and row counts;
- no raw or bulky committed files;
- local Markdown link check;
- unfinished-marker scan;
- GitHub visibility check;
- final clean/synced `git status --short --branch`.

## Stop Rules

Stop and report a blocker if:

- Goal 019 source artefacts are missing, inconsistent, or not at the expected
  row counts;
- the audit finds blank item hashes, missing support-month rows, duplicate
  support-month rows, or nonfinite base metrics in computed rows;
- `quality_fail` rows reveal a route or metric defect rather than ordinary
  low-clear-observation quality;
- validation gates fail.

If the audit finds only expected quality limitations, commit the audit package
and recommend the first constrained bird-observation linkage design goal as
Goal 021.

## Final Response Requirements

Report:

- whether the Goal 019 production table passed audit;
- number of rows in each readiness class;
- classification of the 23 `quality_fail` rows;
- support/month risk concentrations;
- whether hydrology is ready for constrained bird-linkage design;
- changed files;
- validation commands and outcomes;
- commit hash and push status;
- residual risks;
- recommended Goal 021.
