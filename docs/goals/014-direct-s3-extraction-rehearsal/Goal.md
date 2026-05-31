# Goal: Direct S3 Extraction Rehearsal

## Objective

Build a bounded direct-S3 DEA Water Observations extraction rehearsal for
`NWB002` Narran Lake Nature Reserve using the complete derived Landsat
path/row set from Goal 013.

This goal should compute monthly base hydrology metrics for only three probe
months and compare the overlapping months against the existing STAC-derived
event-window metrics. It should not launch a full `2018-01` through `2024-12`
run.

## Why This Matters

Goal 013 proved support-to-path/row coverage and bounded metadata equivalence
for `NWB002`: the support intersects `092/081`, `093/080`, and `093/081`, and
filtered STAC Water Observations assets matched direct S3 assets for
`2018-01`, `2022-11`, and `2024-12`.

Metadata equivalence does not yet prove extraction equivalence. Before direct
S3 can replace the unstable per-support/month STAC search workflow, the
project must show that direct S3 COG reads, support masking, Water Observations
bit decoding, monthly aggregation, quality flags, and output schemas reproduce
the existing metric contract at bounded scale.

## Operating Mode

Bounded extraction rehearsal; direct-S3 read path; base hydrology metrics only;
strict comparison against existing evidence; no ecological interpretation.

## Scope

In scope:

- read repo instructions, Goal 013 artefacts, existing hydrology scripts, and
  relevant `nectar` compute/data-placement guidance;
- verify and, if needed, correct any minor Goal 013 provenance inconsistency
  encountered during orientation, especially WRS raw-zip file size references
  across log/manifest/report;
- use `NWB002` Narran Lake Nature Reserve (`nwb002_ramsar_ref1291`) and the
  complete Goal 013 path/row set: `092/081`, `093/080`, `093/081`;
- use the same three probe months: `2018-01`, `2022-11`, and `2024-12`;
- reuse or regenerate the Goal 013 direct-S3 item set under ignored cache,
  validating item counts and hashes before extraction;
- read the direct-S3 Water Observations COGs without committing rasters;
- apply the same support geometry, Water Observations bit decoding, monthly
  aggregation, and base quality rules used by the current event-window
  hydrology workflow;
- produce a three-row direct-S3 base-metric table for `NWB002`;
- compare `2022-11` and `2024-12` against the existing
  `docs/event_window_hydrology_series.csv` STAC-derived event-window metrics;
- record `2018-01` as a newly rehearsed direct-S3 metric for a month that was
  endpoint-blocked in `docs/event_window_hydrology_series_2018_2024.csv`, not
  as full-window recovery;
- update docs navigation, source evidence, data stream register, decision log,
  and this goal log;
- commit and push the validated package to `main`.

Out of scope:

- full `2018-01` through `2024-12` hydrology extraction;
- all-support extraction;
- derived time-history metrics such as lags, novelty, drying velocity,
  cumulative wet months, or hydroperiod persistence, except to document that
  they are not computed in this three-month rehearsal;
- biodiversity data access, modelling, species/guild decisions, or manuscript
  claims;
- changing supports, subunits, WRS coverage, or metadata-equivalence status
  except for a provenance correction noted above;
- committing raw rasters, WRS geometry, S3 listings, full STAC item dumps,
  full inventories, GeoPackages, shapefiles, NetCDF, Parquet, RDS,
  SQLite/DuckDB stores, archives, or bulky derived products.

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `/Users/bwbrook/work/nectar/docs/workflows/control-plane-doctrine.md`
- `/Users/bwbrook/work/nectar/docs/workflows/compute-resource-selection.md`
- `/Users/bwbrook/work/nectar/docs/workflows/project-integration.md`
- `/Users/bwbrook/work/nectar/docs/workflows/data-placement.md`
- `/Users/bwbrook/work/nectar/docs/workflows/smoke-tests.md`
- `/Users/bwbrook/work/nectar/docs/machines/deep-server.md`
- `/Users/bwbrook/work/nectar/docs/exchange/current_status.md`
- `docs/support_pathrow_coverage_013_report.md`
- `docs/support_pathrow_coverage_013_manifest.json`
- `docs/support_pathrow_crosswalk_013.csv`
- `docs/support_pathrow_item_sets_013.csv`
- `docs/metadata_comparator_status_013.csv`
- `scripts/support_pathrow_metadata_013.py`
- `settings/support_pathrow_metadata_013.json`
- `docs/hydrology_metric_spec.md`
- `docs/event_window_hydrology_series.csv`
- `docs/event_window_hydrology_series_2018_2024.csv`
- `scripts/event_window_hydrology_007.py`
- `scripts/official_support_hydrology_005.py`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `001b9d0` (`Prototype support path-row
  metadata equivalence`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths before any raster read, item cache, or
  intermediate array is written.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create:

- `docs/direct_s3_extraction_rehearsal_014_report.md`: supervisor-facing
  extraction rehearsal report and recommendation for Goal 015.
- `docs/direct_s3_extraction_rehearsal_014_manifest.json`: machine-readable
  command, source, item-set, raster-read, support, comparison, host, runtime,
  and staging provenance.
- `docs/direct_s3_extraction_rehearsal_014_summary.csv`: three-row direct-S3
  base hydrology metrics for `NWB002`.
- `docs/direct_s3_extraction_comparison_014.csv`: comparison against existing
  event-window metrics for overlapping months and Goal 009 blocked status for
  `2018-01`.
- `scripts/direct_s3_extraction_rehearsal_014.py`: bounded extraction
  rehearsal script or small module.
- `settings/direct_s3_extraction_rehearsal_014.json`: rehearsal
  configuration.
- `tests/test_goal014_direct_s3_extraction.py`: focused tests for item-set
  validation, Water Observations bit aggregation helpers, comparison
  tolerances, output schema, and raw-data exclusion.

Update:

- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`
- `docs/README.md`
- `docs/goals/014-direct-s3-extraction-rehearsal/Log.md`
- Goal 013 log/report only if a provenance inconsistency is confirmed and
  corrected.

## Extraction Requirements

Use only:

- support: `nwb002_ramsar_ref1291`;
- path/rows: `092/081`, `093/080`, `093/081`;
- months: `2018-01`, `2022-11`, `2024-12`;
- product: `ga_ls_wo_3`, version `1-6-0`.

Before extraction:

- confirm the Goal 013 path/row crosswalk says `complete` for `NWB002`;
- confirm Goal 013 final equivalence status is `equivalent`;
- confirm direct-S3 item counts are `2018-01=9`, `2022-11=11`,
  `2024-12=11`, or record any current source drift/blocker;
- confirm all raw/cache paths are ignored.

Metrics:

- compute base monthly metrics aligned with the existing event-window metric
  contract, including clear/invalid counts, clear fraction, current wet area,
  valid support area, current proportion wet, wet/dry pixel observation counts,
  no-data/contiguity/cloud/shadow/terrain-related bit counts where available,
  readable/skipped scene counts, quality flag, and wet-month flag;
- do not compute lagged or cumulative time-history fields in this goal except
  as blank/not-applicable fields if needed for schema compatibility.

Comparison:

- compare `2022-11` and `2024-12` to `docs/event_window_hydrology_series.csv`
  for `nwb002_ramsar_ref1291`;
- compare at least current wet area, current proportion wet, clear observation
  count, invalid observation count, clear observation fraction, readable scene
  count, and quality flag;
- set strict numeric tolerances in code/config before seeing the results;
- if direct-S3 and existing event-window metrics differ beyond tolerance, stop
  with a mismatch report rather than recommending scale-up;
- for `2018-01`, compare only against
  `docs/event_window_hydrology_series_2018_2024.csv` status to show that this
  rehearsal addresses a previously endpoint-blocked month.

## Compute And Data Placement

This is a bounded real-raster read and may be larger than prior metadata-only
goals. Start locally on the Mac mini only after a tiny read probe succeeds.

Use `deep-server-ts` if:

- local COG reads are too slow or unreliable;
- GDAL/raster tooling behaves differently enough to require Linux rehearsal;
- the local run appears likely to exceed about 20 minutes;
- repeated COG read failures suggest a network locality issue.

If remote work is used:

- read the `nectar` docs listed above;
- run a target-machine smoke test first;
- stage remote clones and generated payloads under `/data/codex`;
- copy only compact summaries/manifests/logs back into the repo;
- record remote paths, host facts, runtime, and cleanup state in the manifest.

Ignored local staging should use paths such as:

- `artifacts/direct_s3_extraction_rehearsal_014/raw/`
- `artifacts/direct_s3_extraction_rehearsal_014/intermediate/`
- `artifacts/direct_s3_extraction_rehearsal_014/output/`

Confirm these paths are ignored before writing route artefacts.

## Scientific Guardrails

- This goal produces extraction-method evidence, not ecological interpretation.
- Do not interpret wetness, refuge status, breeding, abundance, occurrence, or
  bird response.
- Do not call the 2018 month "recovered full-window hydrology"; it is a
  bounded rehearsal row.
- Do not promote direct S3 extraction beyond `NWB002` unless both extraction
  comparison and validation pass.
- The central scientific question remains dynamic hydrological reaction norms.

## Validation Gates

The goal is complete only when:

- `git status --short --branch` is recorded at start and finish;
- `rg --files` confirms expected files are present;
- `git diff --check` passes;
- focused Goal 014 tests pass;
- the full local test suite passes unless the goal records a narrow reason for
  targeted validation only;
- JSON manifests/settings parse with `python3 -m json.tool`;
- CSV deliverables parse and have required columns and exactly three summary
  rows;
- the direct-S3 item set hashes match Goal 013 or any drift is explicitly
  explained;
- comparison rows for `2022-11` and `2024-12` pass the predeclared tolerance
  or the goal stops with a mismatch recommendation;
- source URLs in claim-bearing docs have corresponding source-register entries
  or are recorded in the Goal 014 manifest;
- ignored staging paths are confirmed ignored;
- no committed files exceed 5 MB;
- no committed raw source-data extensions are present;
- local Markdown links in new/edited docs resolve;
- unfinished-marker scan finds no unresolved stub language.

If validation passes, commit and push the Goal 014 package to `main`.

## Checkpoint Rules

Update `Log.md` when:

- starting state is confirmed;
- required docs and Goal 013 evidence have been read;
- any Goal 013 provenance correction is made or deemed unnecessary;
- ignored staging paths are confirmed;
- item-set validation is complete;
- tiny raster-read probe is complete;
- direct-S3 extraction is complete or blocked;
- comparison to existing event-window metrics is complete;
- route recommendation is drafted;
- validation is complete;
- commit/push is complete or a blocker is recorded.

## Decision Authority

You may decide:

- whether local Mac mini execution is sufficient or `deep-server-ts` is needed;
- the exact predeclared numeric tolerances, as long as they are recorded before
  comparison;
- whether the result supports Goal 015 scaling to all supports for three
  months, all months for `NWB002`, or a blocker/debugging goal.

Pause for Barry only if the work would require credentials, paid services,
large downloads beyond this bounded rehearsal, a non-DEA product substitution,
or a scientific narrowing of the planned paper.
