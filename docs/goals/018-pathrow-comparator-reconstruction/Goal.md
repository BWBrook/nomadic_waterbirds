# Goal: Path-Row Comparator Reconstruction

## Objective

Build a bounded path-row-filtered comparator or item-provenance reconstruction
for the four material Goal 017 legacy rows classified as
`insufficient_reference_evidence`.

This goal should decide whether those legacy rows can be retired as blocking
validation baselines, and whether the project is ready for a full-window
direct-S3 hydrology production goal.

## Why This Matters

Goal 016 proved that direct-S3 extraction can compute all 33 all-support probe
rows across the current support set. Goal 017 then showed that the only
remaining material differences are not evidence of a current direct-S3 defect;
instead, four legacy reference rows lack the item/path-row provenance needed to
serve as fair validation baselines.

Before full-window production, the project needs a compact bridge from
"legacy reference is insufficient" to "the new route is sufficiently
provenanced for production." That bridge should be item/path-row evidence, and
an independent path-row-filtered STAC comparator when STAC is available.

## Operating Mode

Comparator and provenance reconstruction; production-readiness decision; no
full-window extraction; no ecological interpretation.

## Scope

In scope:

- read repo instructions, this goal packet, Goal 013 through Goal 017
  artefacts, current hydrology scripts, metric specs, and `nectar`
  compute/data-placement guidance;
- select the four Goal 017 rows with
  `root_cause_class == insufficient_reference_evidence`;
- optionally include the two Goal 017 `tolerance_or_rounding_only` rows as
  controls, but keep the material decision focused on the four rows;
- reconstruct support-intersecting WRS path/row item provenance for each
  material target row using `docs/support_pathrow_crosswalk_013.csv`;
- build a path-row-filtered STAC metadata comparator for each target row when
  STAC is available;
- compare STAC-filtered item sets to Goal 016 direct-S3 item sets using stable
  item counts, asset-key hashes, item-id hashes, path/row sets, and month
  coverage;
- if STAC is unavailable or incomplete, build a labelled direct-S3
  item-provenance reconstruction and record why independent comparator evidence
  was not obtained;
- run bounded raster reruns only if an item-set mismatch or missing current
  output requires it;
- produce a clear production-readiness recommendation for full-window
  direct-S3 hydrology extraction;
- update docs navigation, data stream register, decision log, and this goal
  log;
- commit and push the validated package to `main`.

Out of scope:

- full `2018-01` through `2024-12` hydrology extraction;
- all-support production metrics beyond the bounded target rows;
- adding lag, novelty, drying, hydroperiod, regional-water, or other
  time-history metrics;
- changing the current support set;
- treating legacy rows without item/path-row evidence as authoritative
  production blockers;
- biodiversity data access, bird-response analysis, modelling, manuscript
  claims, refuge interpretation, breeding interpretation, or ecological
  synthesis;
- silently overwriting Goal 007, Goal 009, Goal 014, Goal 015, Goal 016, or
  Goal 017 output tables;
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
- `docs/support_pathrow_coverage_013_report.md`
- `docs/support_pathrow_coverage_013_manifest.json`
- `docs/support_pathrow_crosswalk_013.csv`
- `docs/direct_s3_extraction_rehearsal_014_report.md`
- `docs/comparator_baseline_repair_015_report.md`
- `docs/comparator_baseline_repair_015_manifest.json`
- `docs/pathrow_filtered_comparator_015_summary.csv`
- `docs/direct_s3_all_support_probe_016_report.md`
- `docs/direct_s3_all_support_probe_016_manifest.json`
- `docs/direct_s3_all_support_probe_016_summary.csv`
- `docs/direct_s3_all_support_probe_016_comparison.csv`
- `docs/compute_routing_memo_016.md`
- `docs/legacy_wetness_difference_triage_017_report.md`
- `docs/legacy_wetness_difference_triage_017_manifest.json`
- `docs/legacy_wetness_difference_triage_017_audit.csv`
- `docs/legacy_wetness_difference_triage_017_item_delta.csv`
- `docs/legacy_wetness_difference_triage_017_metric_delta.csv`
- `docs/hydrology_metric_spec.md`
- `scripts/direct_s3_all_support_probe_016.py`
- `scripts/legacy_wetness_difference_triage_017.py`
- `settings/direct_s3_all_support_probe_016.json`
- `settings/legacy_wetness_difference_triage_017.json`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `8515169` (`Triage legacy wetness
  differences`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths before writing STAC caches, S3 listings,
  rasters, masks, arrays, remote logs, or intermediate products.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create:

- `docs/pathrow_comparator_reconstruction_018_report.md`: supervisor-facing
  report with target rows, comparator route status, item-set evidence,
  row-level production-readiness classifications, and Goal 019 recommendation.
- `docs/pathrow_comparator_reconstruction_018_manifest.json`:
  machine-readable command, source files, target rows, route probes, host
  facts, remote paths if used, item-set hashes, status counts, staging, and
  cleanup provenance.
- `docs/pathrow_comparator_reconstruction_018_targets.csv`: target rows
  selected from Goal 017, including root-cause class and reason.
- `docs/pathrow_comparator_reconstruction_018_item_sets.csv`: one row per
  target support/month/route, with path/rows, item counts, asset-key hashes,
  item-id hashes, route status, and provenance caveats.
- `docs/pathrow_comparator_reconstruction_018_comparison.csv`: comparison of
  STAC-filtered comparator item sets, direct-S3 item sets, and Goal 016 hashes.
- `docs/pathrow_comparator_reconstruction_018_readiness.csv`: one row per
  material target with final readiness class and scale-up recommendation.
- `scripts/pathrow_comparator_reconstruction_018.py`: bounded comparator and
  provenance reconstruction script or small module.
- `settings/pathrow_comparator_reconstruction_018.json`: target selection,
  route settings, tolerances, status vocabulary, input/output paths, and
  staging paths.
- `tests/test_goal018_pathrow_comparator_reconstruction.py`: focused tests for
  target selection, path/row grouping, item-hash comparison, route status
  classification, readiness classification, schema, and raw-data exclusion.

Update:

- `docs/data_stream_register.md`;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/018-pathrow-comparator-reconstruction/Log.md`.

Update `docs/hydrology_metric_spec.md` only if the comparator reconstruction
reveals that the scene-selection or provenance contract needs clarification.

## Target Rows

The material target set is the four rows in
`docs/legacy_wetness_difference_triage_017_audit.csv` with
`root_cause_class == insufficient_reference_evidence`:

1. `nwb004_ramsar_component_369`, `2018-01`,
   `goal009_full_window_context`;
2. `nwb004_ramsar_ref265`, `2022-11`,
   `goal007_legacy_event_window`;
3. `nwb004_ramsar_component_369`, `2024-12`,
   `goal007_legacy_event_window`;
4. `nwb004_ramsar_ref265`, `2024-12`,
   `goal007_legacy_event_window`.

Optional controls:

- `nwb004_ramsar_component_354`, `2022-11`;
- `nwb005_ramsar_ref791`, `2022-11`.

If controls are included, label them as controls and do not let them obscure
the four material-row decision.

## Comparator Requirements

For each material target:

- derive the support-intersecting WRS path/row set from Goal 013 evidence;
- reconstruct the Goal 016 direct-S3 item set from committed Goal 016 outputs
  and, if necessary, direct-S3 listings in ignored staging;
- query STAC for the support/month when available, filter candidate metadata
  to the support-intersecting path/rows, and compute stable item counts and
  hashes;
- compare STAC-filtered item sets with Goal 016 direct-S3 item sets;
- record bbox-only or non-support path/row extras separately from
  support-relevant item sets;
- classify route evidence using a fixed vocabulary.

Suggested route-status vocabulary:

- `stac_pathrow_matches_direct_s3`;
- `stac_unavailable_direct_s3_provenance_only`;
- `stac_available_item_mismatch`;
- `direct_s3_item_reconstruction_mismatch`;
- `blocked_route_failure`;
- `blocked_insufficient_metadata`;
- `not_applicable_control`.

Do not read rasters unless item metadata mismatch means a bounded raster rerun
is needed to diagnose a current route problem.

## Readiness Classification

Every material target row must receive one readiness class:

- `ready_for_full_window_direct_s3`: independent comparator or sufficient
  provenance supports direct-S3 item selection, and no current-route defect is
  found.
- `ready_with_legacy_baseline_retired`: legacy row is not a fair blocker, and
  direct-S3 provenance is sufficient, but no independent STAC comparator was
  available.
- `not_ready_item_mismatch`: path-row-filtered comparator and direct-S3 item
  sets disagree.
- `not_ready_current_route_defect`: evidence points to current direct-S3
  item-selection or extraction defect.
- `blocked_external_service`: comparator/provenance route failed for external
  reasons.
- `blocked_insufficient_evidence`: the goal could not reconstruct enough
  evidence to make a readiness decision.

If all material targets are either `ready_for_full_window_direct_s3` or
`ready_with_legacy_baseline_retired`, recommend Goal 019 as a remote,
restartable full-window direct-S3 production extraction preflight or production
run. If any target is not ready or blocked, recommend the narrow repair or
rerun required before production.

## Compute And Data Placement

This goal should start locally on the Mac mini because it is primarily
metadata and provenance reconstruction.

Use `deep-server-ts` only if bounded direct-S3 listings, STAC probes, or
diagnostic raster reruns are slower or more reliable there. If remote work is
used:

- read the `nectar` docs listed above;
- use `/data/codex/repos/nomadic_waterbirds_goal018`;
- run a target-machine smoke test before route probes or raster reads;
- copy back only compact CSV/JSON/Markdown outputs;
- record remote paths, host facts, runtime, and cleanup status in the
  manifest.

Ignored local staging should use paths such as:

- `artifacts/pathrow_comparator_reconstruction_018/raw/`
- `artifacts/pathrow_comparator_reconstruction_018/intermediate/`
- `artifacts/pathrow_comparator_reconstruction_018/output/`

Confirm these paths are ignored before writing route or rerun artefacts.

## Scientific Guardrails

- This goal is a validation/provenance bridge. It does not interpret
  hydrology ecologically.
- Do not infer bird response, refuge status, breeding opportunity, abundance,
  or reaction norms.
- Do not call any reconstructed target row full-window recovery.
- Do not overwrite legacy outputs silently.
- Do not launch full-window direct-S3 extraction inside this goal.

## Validation Gates

The goal is complete only when:

- `git status --short --branch` is recorded at start and finish;
- `rg --files` confirms expected files are present;
- `git diff --check` passes;
- focused Goal 018 tests pass;
- the full local test suite passes unless the goal records a narrow reason for
  targeted validation only;
- JSON manifests/settings parse with `python3 -m json.tool`;
- CSV deliverables parse and have required columns and expected row counts;
- the target table contains exactly four material rows, plus any controls
  clearly labelled;
- every material target has a route status, readiness class, and
  recommendation;
- any item-set mismatch has a regression test, corrected output, or explicit
  blocker recommendation;
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
- material target row count and optional control count;
- STAC route status and whether independent comparator evidence was obtained;
- item-set comparison/readiness counts;
- whether any current direct-S3 defect was found;
- whether any bounded raster reruns were needed and where they ran;
- validation commands and outcomes;
- residual risks;
- recommended Goal 019.
