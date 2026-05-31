# Goal: Legacy Wetness Difference Triage

## Objective

Review and classify the six Goal 016 legacy wetness-field differences before
any full-window direct-S3 scale-up.

Goal 016 successfully computed all 33 expected support/month rows and matched
the repaired `NWB002` Goal 015/014 baseline. The remaining blocker is not
route execution. It is whether the six wetness-field differences against
legacy Goal 007/009 rows are harmless tolerance or legacy-semantics artefacts,
or whether they expose a current direct-S3 extraction problem.

## Why This Matters

The project is close to promoting direct S3 as the hydrology acquisition route
for production-scale Water Observations metrics. That promotion should not
happen while any core wetness-field differences remain unexplained.

Some Goal 016 differences look tiny or plausibly tied to legacy scene
selection, but the correct standard is not guesswork. The next step is a
compact discrepancy-triage package that identifies the cause, evidence, and
scale-up implication of every wetness-field difference.

## Operating Mode

Discrepancy triage; validation-baseline governance; bounded reruns only if
needed; no production extraction; no ecological interpretation.

## Scope

In scope:

- read repo instructions, this goal packet, Goal 014 through Goal 016
  artefacts, current hydrology scripts, metric specs, and `nectar`
  compute/data-placement guidance;
- correct `docs/goals/016-direct-s3-all-support-probe/Log.md` if it still says
  `Status: In progress` despite completed validation and push evidence;
- audit exactly the six Goal 016 rows with
  `comparison_status == wetness_diff` in
  `docs/direct_s3_all_support_probe_016_comparison.csv`;
- quantify the absolute and relative differences for all compared fields;
- compare asset/item hashes, path/row sets, readable-scene counts, support
  geometry hashes, support grid properties, pixel counts, valid support area,
  invalid-bit counts, wet/dry observation counts, and quality flags;
- distinguish these possible root-cause classes:
  - `tolerance_or_rounding_only`;
  - `legacy_bbox_scene_selection_effect`;
  - `legacy_support_grid_or_mask_effect`;
  - `legacy_metric_formula_or_quality_effect`;
  - `current_direct_s3_extraction_defect`;
  - `insufficient_reference_evidence`;
  - `unresolved_requires_bounded_rerun`;
- run small bounded reruns or helper comparisons only when needed to classify
  a discrepancy;
- use `deep-server-ts` for bounded reruns if raster reads are needed and the
  target smoke/probe is healthy;
- update docs navigation, data stream register, decision log, and this goal
  log;
- commit and push the validated package to `main`.

Out of scope:

- full `2018-01` through `2024-12` extraction;
- all-support full-window direct-S3 production;
- changing the support set;
- adding lag, novelty, drying, hydroperiod, regional-water, or other
  time-history metrics;
- biodiversity data access, bird-response analysis, modelling, manuscript
  claims, refuge interpretation, breeding interpretation, or ecological
  synthesis;
- silently overwriting Goal 007, Goal 009, Goal 014, Goal 015, or Goal 016
  output tables;
- broad STAC endpoint recovery work;
- committing raw rasters, WRS geometry, S3 listings, full STAC item dumps,
  inventories, GeoPackages, shapefiles, NetCDF, Parquet, RDS, SQLite/DuckDB
  stores, arrays, archives, or bulky derived products.

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `/Users/bwbrook/work/nectar/docs/workflows/control-plane-doctrine.md`
- `/Users/bwbrook/work/nectar/docs/workflows/compute-resource-selection.md`
- `/Users/bwbrook/work/nectar/docs/workflows/project-integration.md`
- `/Users/bwbrook/work/nectar/docs/workflows/data-placement.md`
- `/Users/bwbrook/work/nectar/docs/workflows/smoke-tests.md`
- `/Users/bwbrook/work/nectar/docs/exchange/current_status.md`
- `docs/direct_s3_all_support_probe_016_report.md`
- `docs/direct_s3_all_support_probe_016_manifest.json`
- `docs/direct_s3_all_support_probe_016_summary.csv`
- `docs/direct_s3_all_support_probe_016_support_summary.csv`
- `docs/direct_s3_all_support_probe_016_comparison.csv`
- `docs/compute_routing_memo_016.md`
- `docs/comparator_baseline_repair_015_report.md`
- `docs/comparator_baseline_repair_015_manifest.json`
- `docs/pathrow_filtered_comparator_015_summary.csv`
- `docs/comparator_baseline_repair_015_comparison.csv`
- `docs/legacy_denominator_effect_015.csv`
- `docs/direct_s3_extraction_rehearsal_014_summary.csv`
- `docs/event_window_hydrology_series.csv`
- `docs/event_window_hydrology_series_2018_2024.csv`
- `docs/support_pathrow_crosswalk_013.csv`
- `docs/hydrology_metric_spec.md`
- `scripts/direct_s3_all_support_probe_016.py`
- `settings/direct_s3_all_support_probe_016.json`
- `tests/test_goal016_direct_s3_all_support_probe.py`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `9463980` (`Finalize Goal 016 log`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths before writing S3 listings, rasters, masks,
  arrays, remote logs, or intermediate products.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create:

- `docs/legacy_wetness_difference_triage_017_report.md`: supervisor-facing
  report with row-by-row diagnosis, root-cause classes, evidence, and
  scale-up recommendation.
- `docs/legacy_wetness_difference_triage_017_manifest.json`:
  machine-readable command, source files, target rows, host facts, remote paths
  if used, bounded rerun evidence, status counts, root-cause counts, and
  staging/cleanup provenance.
- `docs/legacy_wetness_difference_triage_017_audit.csv`: one row per six
  wetness-difference cases, with compared values, absolute/relative
  differences, root-cause class, evidence basis, and recommendation.
- `docs/legacy_wetness_difference_triage_017_item_delta.csv`: item/path-row
  and scene-count differences for the six cases, including asset hashes where
  available.
- `docs/legacy_wetness_difference_triage_017_metric_delta.csv`: compact
  field-level metric deltas for the six cases.
- `scripts/legacy_wetness_difference_triage_017.py`: bounded triage script or
  small module.
- `settings/legacy_wetness_difference_triage_017.json`: target rows,
  tolerances, root-cause vocabulary, input/output paths, staging paths, and
  rerun settings.
- `tests/test_goal017_legacy_wetness_difference_triage.py`: focused tests for
  target-row selection, delta calculations, tolerance classification,
  root-cause vocabulary, schema, and raw-data exclusion.

Update:

- `docs/goals/016-direct-s3-all-support-probe/Log.md` status if still stale;
- `docs/data_stream_register.md`;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/017-legacy-wetness-difference-triage/Log.md`.

Update `docs/hydrology_metric_spec.md` only if the triage reveals that the
metric contract itself needs clarification.

## Target Rows

The triage target is the six rows in
`docs/direct_s3_all_support_probe_016_comparison.csv` with
`comparison_status == wetness_diff`:

1. `nwb004_ramsar_component_354`, `2022-11`, reference
   `goal007_legacy_event_window`;
2. `nwb004_ramsar_component_369`, `2018-01`, reference
   `goal009_full_window_context`;
3. `nwb004_ramsar_component_369`, `2024-12`, reference
   `goal007_legacy_event_window`;
4. `nwb004_ramsar_ref265`, `2022-11`, reference
   `goal007_legacy_event_window`;
5. `nwb004_ramsar_ref265`, `2024-12`, reference
   `goal007_legacy_event_window`;
6. `nwb005_ramsar_ref791`, `2022-11`, reference
   `goal007_legacy_event_window`.

Do not broaden the target set unless the six-row audit reveals that a wider
class of rows is affected and the report justifies the expansion.

## Triage Questions

For each target row, answer:

- Is the difference actually a tolerance/rounding artefact?
- Do the computed and reference rows use the same support geometry hash and
  support grid semantics?
- Do they use the same support-intersecting path/row set?
- Do the asset-key or item hashes differ?
- Does the difference disappear if the direct-S3 route uses the legacy
  scene-selection or denominator semantics?
- Does the difference remain when both routes are compared under the Goal 015
  scene-selection policy?
- Are wet/dry observation count differences consistent with extra or missing
  scenes, changed masks, changed valid support area, or changed bit decoding?
- Does the difference change any likely downstream classification, such as
  `wet_month_flag` or quality filtering?
- Is the direct-S3 row safe to treat as the production metric for this
  support/month?

## Classification Rules

Use a root-cause class from the configured vocabulary for every target row.

Recommended interpretation:

- `tolerance_or_rounding_only`: differences are smaller than a justified
  tolerance, do not change integer counts or proportions materially, and have
  no downstream classification effect.
- `legacy_bbox_scene_selection_effect`: item/path-row evidence shows legacy
  rows included bbox-only scenes outside the support-intersecting path/row set,
  and the resulting wetness change is attributable to that legacy inclusion.
- `legacy_support_grid_or_mask_effect`: geometry hash, pixel count, valid
  support area, rasterisation grid, or mask treatment differs enough to explain
  the metric delta.
- `legacy_metric_formula_or_quality_effect`: scene/item sets and support masks
  are effectively the same, but formula, invalid-bit, quality, or aggregation
  semantics differ.
- `current_direct_s3_extraction_defect`: evidence points to a bug in Goal 016
  extraction or comparison. If this is found, fix narrowly, add regression
  tests, regenerate affected Goal 016/017 outputs as needed, and stop before
  scale-up.
- `insufficient_reference_evidence`: legacy row does not carry enough item,
  grid, or provenance evidence to classify confidently.
- `unresolved_requires_bounded_rerun`: classification requires a small rerun
  that could not be completed within this goal.

## Compute And Data Placement

This goal is primarily a compact audit and should start locally on the Mac
mini.

Use `deep-server-ts` only if bounded raster reruns are needed. If remote work
is used:

- read the `nectar` docs listed above;
- use `/data/codex/repos/nomadic_waterbirds_goal017`;
- run a target-machine smoke test before raster reads;
- copy back only compact CSV/JSON/Markdown outputs;
- record remote paths, host facts, runtime, and cleanup status in the
  manifest.

Ignored local staging should use paths such as:

- `artifacts/legacy_wetness_difference_triage_017/raw/`
- `artifacts/legacy_wetness_difference_triage_017/intermediate/`
- `artifacts/legacy_wetness_difference_triage_017/output/`

Confirm these paths are ignored before writing route or rerun artefacts.

## Scientific Guardrails

- This goal reviews validation differences. It does not interpret hydrology
  ecologically.
- Do not infer bird response, refuge status, breeding opportunity, abundance,
  or reaction norms.
- Do not call any newly computed row full-window recovery.
- Do not overwrite legacy outputs silently.
- Do not recommend full-window direct-S3 scale-up unless every wetness-field
  difference is either resolved, classified as harmless for production, or
  explicitly excluded by a defensible rule.

## Validation Gates

The goal is complete only when:

- `git status --short --branch` is recorded at start and finish;
- `rg --files` confirms expected files are present;
- `git diff --check` passes;
- focused Goal 017 tests pass;
- the full local test suite passes unless the goal records a narrow reason for
  targeted validation only;
- JSON manifests/settings parse with `python3 -m json.tool`;
- CSV deliverables parse and have required columns and expected row counts;
- the audit table has exactly six target rows unless a justified expansion is
  recorded;
- every target row has a non-empty root-cause class and recommendation;
- any current direct-S3 defect has a regression test and corrected outputs, or
  the project is left with a clear blocker recommendation;
- ignored staging paths are confirmed ignored and raw files are absent from
  Git;
- no committed file exceeds 5 MB without explicit justification;
- no raw geospatial/raster/object-store/source-data extensions are committed;
- local Markdown links resolve;
- unfinished markers are absent from changed goal outputs;
- GitHub repo visibility remains private;
- commit and push to `origin/main` succeed.

## Recommended Finish Report

Report:

- final commit SHA and push status;
- whether the stale Goal 016 log status was corrected;
- six-row root-cause counts and row-level classifications;
- whether any current direct-S3 defect was found;
- whether any bounded reruns were needed and where they ran;
- validation commands and outcomes;
- residual risks;
- recommended Goal 018.
