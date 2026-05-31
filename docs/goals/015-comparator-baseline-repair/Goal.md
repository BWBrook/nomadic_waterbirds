# Goal: Comparator Baseline Repair

## Objective

Repair the hydrology comparator baseline exposed by Goal 014 before any
direct-S3 extraction scale-up.

Goal 014 showed that direct-S3 extraction for `NWB002` reproduced the core
wetness fields for overlapping months, but failed strict comparison against
legacy event-window rows for denominator fields. The mismatch pattern was
consistent with legacy STAC bbox-only no-data scenes that fall outside the
Goal 013 support-derived WRS path/row set.

This goal should build a path-row-filtered comparator baseline, quantify the
legacy denominator effect, and formalise the production scene-selection policy
for the next extraction step.

## Why This Matters

Direct S3 should not be scaled while the trusted comparator is known to include
scene-selection artefacts. A production pipeline needs a clear rule for which
Water Observations scenes are support-relevant.

The key question is not whether direct S3 can read files. Goal 014 proved that.
The key question is whether the project should count bbox-only no-data scenes
as readable scenes and invalid observations for a wetland support. If the
answer is no, then the old comparator needs a repaired baseline before it can
be used to validate scale-up.

## Operating Mode

Comparator repair; metric-policy clarification; bounded `NWB002` baseline; no
full extraction; no ecological interpretation.

## Scope

In scope:

- read repo instructions, Goal 013/014 artefacts, existing hydrology scripts,
  hydrology metric spec, and relevant `nectar` compute/data-placement
  guidance;
- use `NWB002` Narran Lake Nature Reserve (`nwb002_ramsar_ref1291`), the Goal
  013 path/rows `092/081`, `093/080`, `093/081`, and the three Goal 014
  months `2018-01`, `2022-11`, `2024-12`;
- build a path-row-filtered STAC comparator baseline when STAC is available,
  using only assets whose WRS path/rows intersect the support;
- compare the repaired comparator baseline to the Goal 014 direct-S3 summary;
- quantify the legacy Goal 007 denominator effect for `2022-11` and `2024-12`,
  including bbox-only extra scene count, extra no-data or invalid observation
  count, and fields affected;
- decide and document the production scene-selection policy for support-level
  Water Observations metrics;
- update `docs/hydrology_metric_spec.md` if the scene-selection policy needs
  clarification;
- update docs navigation, source evidence, data stream register, decision log,
  and this goal log;
- commit and push the validated package to `main`.

Out of scope:

- full `2018-01` through `2024-12` extraction;
- all-support extraction;
- adding derived time-history metrics such as lags, novelty, drying velocity,
  cumulative wet months, or hydroperiod persistence;
- biodiversity data access, modelling, species/guild decisions, or manuscript
  claims;
- changing wetland supports, WRS coverage, or metadata-equivalence status
  unless a clear inconsistency is discovered;
- silently editing or replacing the historical Goal 007 or Goal 009 output
  tables;
- committing raw rasters, WRS geometry, S3 listings, full STAC item dumps,
  full inventories, GeoPackages, shapefiles, NetCDF, Parquet, RDS,
  SQLite/DuckDB stores, archives, arrays, or bulky derived products.

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `/Users/bwbrook/work/nectar/docs/workflows/control-plane-doctrine.md`
- `/Users/bwbrook/work/nectar/docs/workflows/compute-resource-selection.md`
- `/Users/bwbrook/work/nectar/docs/workflows/project-integration.md`
- `/Users/bwbrook/work/nectar/docs/workflows/data-placement.md`
- `/Users/bwbrook/work/nectar/docs/workflows/smoke-tests.md`
- `docs/support_pathrow_coverage_013_report.md`
- `docs/support_pathrow_coverage_013_manifest.json`
- `docs/support_pathrow_crosswalk_013.csv`
- `docs/direct_s3_extraction_rehearsal_014_report.md`
- `docs/direct_s3_extraction_rehearsal_014_manifest.json`
- `docs/direct_s3_extraction_rehearsal_014_summary.csv`
- `docs/direct_s3_extraction_comparison_014.csv`
- `scripts/direct_s3_extraction_rehearsal_014.py`
- `settings/direct_s3_extraction_rehearsal_014.json`
- `docs/hydrology_metric_spec.md`
- `docs/event_window_hydrology_series.csv`
- `docs/event_window_hydrology_series_2018_2024.csv`
- `scripts/event_window_hydrology_007.py`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `fa9d69f` (`Mark Goal 014 log complete`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths before any STAC item cache, raster read, or
  intermediate array is written.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create:

- `docs/comparator_baseline_repair_015_report.md`: supervisor-facing baseline
  repair report and recommendation for Goal 016.
- `docs/comparator_baseline_repair_015_manifest.json`: machine-readable
  command, source, scene-selection, comparator, comparison, host, runtime, and
  staging provenance.
- `docs/pathrow_filtered_comparator_015_summary.csv`: three-row repaired
  comparator baseline for `NWB002`.
- `docs/comparator_baseline_repair_015_comparison.csv`: comparison between
  repaired comparator rows, Goal 014 direct-S3 rows, and legacy Goal 007/009
  rows.
- `docs/legacy_denominator_effect_015.csv`: compact table quantifying
  bbox-only no-data/denominator effects for overlapping months.
- `scripts/comparator_baseline_repair_015.py`: bounded baseline-repair script
  or small module.
- `settings/comparator_baseline_repair_015.json`: baseline-repair
  configuration.
- `tests/test_goal015_comparator_baseline_repair.py`: focused tests for
  scene-selection filtering, denominator-effect accounting, comparison
  tolerances, output schema, and raw-data exclusion.

Update:

- `docs/hydrology_metric_spec.md` if scene-selection policy needs
  clarification;
- `docs/source_evidence_register.md`;
- `docs/data_stream_register.md`;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/015-comparator-baseline-repair/Log.md`.

## Comparator Requirements

Path-row-filtered comparator:

- Use the Goal 013 complete WRS path/row set for `NWB002`.
- If STAC is available, retrieve candidate/month STAC metadata and filter to
  the derived path/rows before reading or summarising assets.
- If STAC is unavailable, reuse Goal 013/014 direct-S3 item sets only to build
  a labelled `comparator_blocked_stac_unavailable` package; do not invent
  independent comparator evidence.
- Keep raw STAC JSON, S3 listings, rasters, and arrays ignored.

Comparison:

- Compare repaired comparator rows to Goal 014 direct-S3 rows for all three
  months.
- Compare legacy Goal 007 rows for `2022-11` and `2024-12` to the repaired
  comparator.
- Use predeclared tolerances and record them in settings/manifest before
  comparison.
- Fields to compare at minimum:
  - `readable_scene_count`
  - `clear_obs_count`
  - `invalid_obs_count`
  - `clear_obs_fraction`
  - `current_wet_area_m2`
  - `valid_support_area_m2`
  - `current_proportion_wet`
  - `wet_pixel_observation_count`
  - `dry_pixel_observation_count`
  - `quality_flag`
  - `wet_month_flag`

Legacy denominator effect:

- For `2022-11` and `2024-12`, quantify which fields differ between legacy and
  repaired rows.
- Identify whether the observed invalid/no-data difference equals the extra
  bbox-only scene count multiplied by support-mask pixels.
- Label whether the effect changes wetness fields or only denominator/quality
  bookkeeping fields.

Production policy:

- State whether support-level monthly metrics should use support-intersecting
  WRS path/rows rather than all STAC bbox hits.
- If the policy changes or clarifies the metric contract, update
  `docs/hydrology_metric_spec.md`.
- Do not overwrite legacy output tables. New repaired baseline files should
  live alongside them with clear provenance.

## Compute And Data Placement

This goal is bounded and should usually run locally on the Mac mini. Use
`deep-server-ts` only if local STAC/raster reads are unstable, too slow, or
Linux/GDAL behaviour is required to diagnose the baseline.

If remote work is used:

- read the `nectar` docs listed above;
- run a target-machine smoke test first;
- stage remote clones and generated payloads under `/data/codex`;
- copy only compact summaries/manifests/logs back into the repo;
- record remote paths, host facts, runtime, and cleanup state in the manifest.

Ignored local staging should use paths such as:

- `artifacts/comparator_baseline_repair_015/raw/`
- `artifacts/comparator_baseline_repair_015/intermediate/`
- `artifacts/comparator_baseline_repair_015/output/`

Confirm these paths are ignored before writing route artefacts.

## Scientific Guardrails

- This goal repairs a validation baseline. It does not produce ecological
  interpretation.
- Do not interpret wetness, refuge status, breeding, abundance, occurrence, or
  bird response.
- Do not call this full-window recovery.
- Do not scale direct-S3 extraction until the repaired comparator either
  matches or records a blocker/mismatch that is understood.
- The central scientific question remains dynamic hydrological reaction norms.

## Validation Gates

The goal is complete only when:

- `git status --short --branch` is recorded at start and finish;
- `rg --files` confirms expected files are present;
- `git diff --check` passes;
- focused Goal 015 tests pass;
- the full local test suite passes unless the goal records a narrow reason for
  targeted validation only;
- JSON manifests/settings parse with `python3 -m json.tool`;
- CSV deliverables parse and have required columns and expected row counts;
- repaired comparator rows match Goal 014 direct-S3 rows within predeclared
  tolerance, or the goal stops with a clear mismatch/blocker recommendation;
- legacy denominator-effect rows support the stated explanation or explicitly
  reject it;
- source URLs in claim-bearing docs have corresponding source-register entries
  or are recorded in the Goal 015 manifest;
- ignored staging paths are confirmed ignored;
- no committed files exceed 5 MB;
- no committed raw source-data extensions are present;
- local Markdown links in new/edited docs resolve;
- unfinished-marker scan finds no unresolved stub language.

If validation passes, commit and push the Goal 015 package to `main`.

## Checkpoint Rules

Update `Log.md` when:

- starting state is confirmed;
- required docs and Goal 014 evidence have been read;
- ignored staging paths are confirmed;
- STAC/path-row-filtered comparator route is available or blocked;
- repaired comparator baseline is generated or blocked;
- comparison to Goal 014 direct-S3 rows is complete;
- legacy denominator effect is quantified;
- scene-selection policy is drafted;
- validation is complete;
- commit/push is complete or a blocker is recorded.

## Decision Authority

You may decide:

- whether STAC is available enough to build the repaired comparator;
- whether local Mac mini execution is sufficient or `deep-server-ts` is needed;
- whether the next goal should scale to all supports for the three probe
  months, scale `NWB002` over the full window, or debug a remaining mismatch.

Pause for Barry only if the repair would change the scientific support
definition, require credentials or paid services, substitute a non-DEA product,
or narrow the planned paper.
