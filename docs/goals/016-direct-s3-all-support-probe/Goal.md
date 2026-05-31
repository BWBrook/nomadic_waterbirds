# Goal: Direct S3 All-Support Probe

## Objective

Run a bounded direct-S3 Water Observations extraction rehearsal across all
current event-window supports for the same three probe months used in Goals
014 and 015.

This is the first spatial scale step after the repaired comparator baseline.
It should test whether the Goal 015 support-intersecting WRS path/row
scene-selection policy works across the full current support set, without
launching a full event-window or historical extraction.

## Why This Matters

Goal 015 resolved the `NWB002` comparator mismatch: direct-S3 extraction and a
path-row-filtered STAC comparator match exactly for the three probe months,
while the old bbox-only STAC denominator rows are now understood as legacy
scene-selection artefacts.

The next risk is support diversity. The project has 11 current event-window
supports spanning parent Ramsar complexes, Ramsar components, and DEA
Waterbodies overlap subunits. Before any full `2018-01` through `2024-12`
direct-S3 extraction, the route needs to prove that it can derive, list, read,
mask, decode, aggregate, and report base metrics across that support set.

## Operating Mode

Bounded spatial scale rehearsal; direct-S3 extraction; remote-first compute
where practical; no full-window production; no ecological interpretation.

## Scope

In scope:

- read repo instructions, this goal packet, Goal 013 through Goal 015 evidence,
  current hydrology scripts, metric specs, and `nectar` compute/data-placement
  guidance;
- use the 11 supports currently represented in
  `docs/event_window_hydrology_summary.csv`, with support-to-path/row coverage
  from `docs/support_pathrow_crosswalk_013.csv`;
- process only these months: `2018-01`, `2022-11`, and `2024-12`;
- use direct public S3 object discovery and COG reads for DEA Water
  Observations assets;
- apply the Goal 015 production scene-selection rule: support-level monthly
  metrics use only support-intersecting WRS path/rows, not all STAC bbox hits;
- write one output row per expected support/month, with status and failure
  classes if a row cannot be computed;
- compute monthly base metrics only: scene counts, item hashes, invalid-bit
  counts, wet/dry observation counts, wet area, valid support area, wet
  proportion, quality flag, and wet-month flag;
- compare the new rows to available prior rows only as validation/provenance:
  Goal 015 repaired comparator for `NWB002`, Goal 014 direct-S3 rows for
  `NWB002`, and Goal 007 or Goal 009 legacy event-window rows where available;
- update docs navigation, source evidence, data stream register, decision log,
  and this goal log;
- commit and push the validated package to `main`.

Out of scope:

- full `2018-01` through `2024-12` extraction;
- adding lag, novelty, drying, hydroperiod, regional-water, or other derived
  time-history metrics;
- replacing or editing Goal 007, Goal 009, Goal 014, or Goal 015 output
  tables;
- biodiversity data access, bird-response analysis, modelling, manuscript
  claims, refuge interpretation, breeding interpretation, or ecological
  synthesis;
- changing the current wetland support set unless a hard inconsistency blocks
  this rehearsal;
- broad STAC recovery or endpoint retry work beyond small comparator checks;
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
- `docs/direct_s3_extraction_rehearsal_014_manifest.json`
- `docs/direct_s3_extraction_rehearsal_014_summary.csv`
- `docs/comparator_baseline_repair_015_report.md`
- `docs/comparator_baseline_repair_015_manifest.json`
- `docs/pathrow_filtered_comparator_015_summary.csv`
- `docs/comparator_baseline_repair_015_comparison.csv`
- `docs/legacy_denominator_effect_015.csv`
- `docs/hydrology_metric_spec.md`
- `docs/event_window_hydrology_summary.csv`
- `docs/event_window_hydrology_series.csv`
- `docs/event_window_hydrology_series_2018_2024.csv`
- `scripts/direct_s3_extraction_rehearsal_014.py`
- `scripts/comparator_baseline_repair_015.py`
- `settings/direct_s3_extraction_rehearsal_014.json`
- `settings/comparator_baseline_repair_015.json`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `2fee95d` (`Finalize Goal 015 log`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths before writing S3 listings, rasters, masks,
  arrays, remote logs, or intermediate products.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create:

- `docs/direct_s3_all_support_probe_016_report.md`: supervisor-facing report
  with scope, compute route, results, row/status counts, comparison summary,
  support-specific caveats, and recommendation for Goal 017.
- `docs/direct_s3_all_support_probe_016_manifest.json`: machine-readable
  command, config, support set, path/row sets, source product, route probes,
  host facts, remote paths if used, runtime, staging, row counts, status
  counts, and cleanup/provenance.
- `docs/direct_s3_all_support_probe_016_summary.csv`: expected 33-row table
  for 11 supports by 3 months. Every row must have a status, and computed rows
  must carry the monthly base metrics.
- `docs/direct_s3_all_support_probe_016_support_summary.csv`: compact
  support-level status and quality summary.
- `docs/direct_s3_all_support_probe_016_comparison.csv`: comparison to Goal
  015/014 rows for `NWB002` and to legacy Goal 007/009 rows where available,
  with denominator differences separated from wetness-field differences.
- `docs/compute_routing_memo_016.md`: compute-routing decision, target-host
  probe, remote working path, smoke test, fallback rules, and final host used.
- `scripts/direct_s3_all_support_probe_016.py`: bounded extraction-rehearsal
  script or small module.
- `settings/direct_s3_all_support_probe_016.json`: support set, months,
  product, scene-selection policy, route settings, staging paths, tolerances,
  output paths, and resource limits.
- `tests/test_goal016_direct_s3_all_support_probe.py`: focused tests for
  support/month grid construction, path/row grouping, status classification,
  metric schema, comparison classification, and raw-data exclusion.

Update:

- `docs/source_evidence_register.md` if new source checks or changed route
  facts are introduced;
- `docs/data_stream_register.md`;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/016-direct-s3-all-support-probe/Log.md`.

## Expected Support/Month Grid

Use the 11 supports in `docs/event_window_hydrology_summary.csv`.

Expected months:

- `2018-01`
- `2022-11`
- `2024-12`

Expected output grid:

- 33 rows total;
- one row per `support_id`/month;
- no silent row drops;
- if a support/month cannot be computed, emit a row with a clear status and
  failure class.

Required status vocabulary should include, at minimum:

- `computed_direct_s3_metrics`
- `blocked_no_items_found`
- `blocked_s3_listing_failure`
- `blocked_cog_read_failure`
- `blocked_mask_or_geometry_failure`
- `blocked_remote_or_route_unavailable`
- `blocked_unclassified_failure`

Add narrower statuses if they make review easier, but do not hide failures in
free text.

## Metric Requirements

Computed rows must follow `docs/hydrology_metric_spec.md`, including the
support-intersecting path/row scene-selection policy.

At minimum, every computed row should include:

- support identifiers and support caveat fields;
- month and month rationale;
- path/row set used;
- direct-S3 item count;
- stable asset-key and item-set hashes;
- readable and skipped scene counts;
- `n_scene_m`, `n_pixel_u`, `clear_obs_count`, `invalid_obs_count`,
  `clear_obs_fraction`;
- `wet_pixel_observation_count`, `dry_pixel_observation_count`;
- invalid-bit counts;
- `current_wet_area_m2`, `valid_support_area_m2`,
  `current_proportion_wet`;
- `quality_flag`, `wet_month_flag`;
- status and caveat/failure fields.

Do not compute lag or time-history metrics in this goal.

## Comparison Requirements

Treat comparison as validation evidence, not as production table replacement.

Required comparison layers:

- `NWB002` against Goal 015 repaired comparator for all three months;
- `NWB002` against Goal 014 direct-S3 rows for all three months;
- all supports against Goal 007 legacy event-window rows for `2022-11` and
  `2024-12` where matching rows exist;
- all supports against Goal 009 full-window rows for `2018-01` where matching
  computed rows exist, with blocked Goal 009 rows recorded as context only.

Comparison should label:

- `within_tolerance`;
- `wetness_within_tolerance_denominator_diff`;
- `wetness_diff`;
- `missing_or_blocked_reference`;
- `computed_row_blocked`;
- `not_compared`.

Fields compared at minimum:

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

If denominator differences appear outside `NWB002`, quantify whether they are
consistent with the Goal 015 bbox-only scene-selection effect. Do not treat
legacy denominator mismatches as direct-S3 failures unless wetness fields also
diverge or the item/path-row evidence is inconsistent.

## Compute And Parallelisation

Use the Mac mini for orientation, tests, config checks, and at most a tiny
local smoke read.

The preferred host for the 33-row extraction rehearsal is `deep-server-ts`,
provided the live probe succeeds. Stage the remote clone and generated payloads
under:

```text
/data/codex/repos/nomadic_waterbirds_goal016
```

Before launching the 33-row run:

- read the `nectar` docs listed above;
- probe `deep-server-ts` for CPU/RAM/disk, Python, GDAL, Git, and network/S3
  access;
- run the focused tests or an equivalent smoke subset on the target;
- run a one-support/one-month remote smoke test, preferably `NWB002` and
  `2022-11`, and compare it to Goal 015/014 before scale;
- record the probe and smoke results in `docs/compute_routing_memo_016.md` and
  the manifest.

If `deep-server-ts` is unavailable, do not shrink the scientific support grid
just to fit the local control plane. Either:

- run the full 33-row rehearsal locally only if a smoke test shows it is
  comfortably bounded and will not tie up the Mac mini for a long run, or
- produce a blocker package that records the failed remote route and the
  local-smoke evidence.

Parallelise by support/month or support/path-row where practical. The goal does
not require heavy parallel infrastructure, but the script should make the
natural shard key explicit so Goal 017 can scale cleanly.

Ignored local staging should use paths such as:

- `artifacts/direct_s3_all_support_probe_016/raw/`
- `artifacts/direct_s3_all_support_probe_016/intermediate/`
- `artifacts/direct_s3_all_support_probe_016/output/`

Remote staging should keep raw files under ignored `artifacts/` paths inside
the remote clone. Copy only compact summaries, reports, manifests, and logs
back into the repo.

## Scientific Guardrails

- This goal tests route and support-set behaviour. It is not ecological
  interpretation.
- Do not infer wetland condition, bird occurrence, refuge status, breeding
  opportunity, abundance, or hydrological reaction norms.
- Do not call the output a full event-window or historical hydrology table.
- Do not overwrite legacy event-window files.
- Do not promote direct S3 to production until this all-support probe is
  reviewed.

## Validation Gates

The goal is complete only when:

- `git status --short --branch` is recorded at start and finish;
- `rg --files` confirms expected files are present;
- `git diff --check` passes;
- focused Goal 016 tests pass;
- the full local test suite passes unless the goal records a narrow reason for
  targeted validation only;
- JSON manifests/settings parse with `python3 -m json.tool`;
- CSV deliverables parse and have required columns and expected row counts, or
  the report explains a predeclared blocker that prevented the 33-row run;
- every expected support/month has either a computed row or a classified
  blocked row;
- `NWB002` rows compare within tolerance to Goal 015/014 for all computed
  months;
- legacy comparisons separate wetness-field differences from denominator
  differences;
- ignored staging paths are confirmed ignored and raw files are absent from
  Git;
- no committed file exceeds 5 MB without an explicit justification;
- no raw geospatial/raster/object-store/source-data extensions are committed;
- local Markdown links resolve;
- unfinished markers are absent from changed goal outputs;
- GitHub repo visibility remains private;
- commit and push to `origin/main` succeed.

## Recommended Finish Report

Report:

- final commit SHA and push status;
- host used for the 33-row run and remote path if applicable;
- row/status counts and whether all 33 expected rows are represented;
- `NWB002` comparison status against Goal 015/014;
- whether denominator-only legacy effects appear beyond `NWB002`;
- validation commands and outcomes;
- residual risks;
- recommended Goal 017.
