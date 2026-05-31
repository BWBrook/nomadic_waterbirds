# Goal: Support Path-Row Coverage And Metadata Equivalence

## Objective

Build a bounded support-to-Landsat-path/row coverage and official metadata
comparison prototype for the hydrology acquisition route.

Goal 012 proved that direct public S3 discovery works for the known Narran
`093/080` path-row/month prefixes while DEA STAC remained unavailable. It did
not prove that `093/080` covers the whole Narran support, nor that direct S3
item discovery is equivalent to STAC, Open Data Cube, or another official
metadata route.

This goal should close as much of that gap as possible without computing
hydrology metrics or launching a full extraction.

## Why This Matters

Direct S3 can only replace repeated live STAC search if the project can prove:

1. every support bbox or support geometry maps to the correct Landsat path/row
   set;
2. every path/row/month Water Observations item is discovered reproducibly;
3. discovered item sets match an official metadata comparator, or the remaining
   equivalence blocker is recorded precisely.

Without this proof, a direct S3 extraction could silently omit scenes and bias
monthly wetness metrics.

## Operating Mode

Metadata and spatial-coverage prototype; official-source verification; compact
item-set evidence; no hydrology metrics; no ecological interpretation.

## Scope

In scope:

- read repo instructions, Goal 011 and Goal 012 artefacts, current hydrology
  scripts, and relevant `nectar` compute/data-placement guidance;
- obtain or reuse an official/current Landsat WRS-2 path/row footprint source
  for coverage derivation, staging raw geometry in ignored paths only;
- derive a support-to-path/row crosswalk for the current event-window support
  set, with `NWB002` Narran as the primary proof case;
- for `NWB002`, run direct S3 path-row/month listing over the complete derived
  path/row set for the same three months used in Goal 012:
  `2018-01`, `2022-11`, and `2024-12`;
- compare the derived complete-path-row S3 item set to:
  - Goal 012's known `093/080` item set;
  - DEA STAC, if a strict preflight passes;
  - otherwise an official Open Data Cube, NCI, DEA Sandbox, or equivalent
    official metadata comparator if practically available;
- if all official comparators remain unavailable, produce a precise comparator
  blocker and do not promote direct S3 to extraction-ready;
- add compact Markdown, CSV, JSON, script, settings, and tests that make the
  support coverage and item-set status reviewable;
- keep raw WRS geometry, STAC item JSON, S3 listings, inventories, rasters,
  arrays, and temporary route caches ignored;
- update docs navigation, source evidence, data stream register, decision log,
  and this goal log;
- commit and push the validated package to `main`.

Out of scope:

- computing wet area, wet proportion, invalid/clear counts, lags, novelty,
  drying velocity, persistence, or any hydrology metric;
- recovering Goal 009 blocked rows;
- full `2018-01` through `2024-12` extraction;
- biodiversity data access, modelling, species/guild decisions, or manuscript
  claims;
- changing wetland supports or subunit decisions except to add path/row
  coverage evidence;
- using non-official path/row coverage or metadata sources as claim-grade
  evidence without lab-leader approval;
- committing raw rasters, WRS geometry, full STAC item dumps, full S3
  inventories, GeoPackages, shapefiles, NetCDF, Parquet, RDS, SQLite/DuckDB
  stores, archives, or bulky derived products.

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
- `docs/hydrology_acquisition_route_011_report.md`
- `docs/hydrology_acquisition_route_011_manifest.json`
- `docs/hydrology_metadata_cache_s3_012_report.md`
- `docs/hydrology_metadata_cache_s3_012_manifest.json`
- `docs/hydrology_metadata_item_sets_012.csv`
- `docs/hydrology_metadata_route_comparison_012.csv`
- `docs/event_window_hydrology_series_2018_2024.csv`
- `scripts/hydrology_metadata_cache_s3_012.py`
- `scripts/event_window_hydrology_007.py`
- `settings/hydrology_metadata_cache_s3_012.json`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `b95a146` (`Prototype hydrology metadata
  acquisition routes`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths before any live probe or geometry download
  writes files.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create:

- `docs/support_pathrow_coverage_013_report.md`: supervisor-facing coverage
  and equivalence report with a clear recommendation for Goal 014.
- `docs/support_pathrow_coverage_013_manifest.json`: machine-readable source,
  command, route, comparator, host, staging, and item-set provenance.
- `docs/support_pathrow_crosswalk_013.csv`: compact support-to-path/row table.
  Include support ID, candidate ID, support class, path, row, coverage method,
  coverage status, source ID, geometry/hash fields where useful, and caveat.
- `docs/support_pathrow_item_sets_013.csv`: compact direct-S3 item-set table
  for `NWB002` complete path/row coverage across the three probe months.
- `docs/metadata_comparator_status_013.csv`: comparator status table covering
  STAC, ODC/NCI/Sandbox or another official comparator, Goal 012 known-path
  comparison, and final equivalence status.
- `scripts/support_pathrow_metadata_013.py`: bounded coverage and item-set
  prototype script or equivalent small module.
- `settings/support_pathrow_metadata_013.json`: prototype configuration.
- `tests/test_goal013_support_pathrow_metadata.py`: focused tests for
  path/row parsing, crosswalk shape, item-set hashing, comparator status
  classification, and raw-data exclusion.

Update:

- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`
- `docs/README.md`
- `docs/goals/013-support-pathrow-metadata-equivalence/Log.md`

## Coverage Requirements

Support set:

- Build a crosswalk for all 11 current event-window supports if practical.
- Treat `NWB002` Narran as the primary proof case. If all-support coverage is
  blocked by source or geometry issues, complete `NWB002` and at least one
  non-Narran control support, then record the blocker.

Path/row source:

- Use official/current Landsat WRS-2 path/row footprint evidence where
  available, or another clearly official path/row source.
- Record source URL, access date, file/version if applicable, and staging path.
- Keep raw geometry ignored; commit only compact source facts, hashes, and
  crosswalk summaries.

Coverage method:

- Prefer support geometry intersection when official support geometry is
  available in the existing workflow or can be rebuilt reproducibly.
- If bbox intersection is used instead, label it conservative bbox coverage,
  not geometry coverage.
- Record whether each support has complete, conservative, blocked, or
  unresolved path/row coverage.

## Item-Set And Comparator Requirements

For `NWB002`:

- Use the complete derived path/row set, not only the Goal 012 `093/080`
  known path-row.
- List direct public S3 Water Observations COG keys for `2018-01`, `2022-11`,
  and `2024-12`.
- Commit only compact item counts, stable item hashes, route status, and sample
  key snippets; keep raw S3 listings and HEAD metadata ignored.
- Compare the complete derived S3 item set against the Goal 012 `093/080`
  item set and report any added, missing, or identical path/row/month slices.

Official comparator:

- Run a strict STAC preflight first. If it passes, compare S3 item sets against
  STAC item sets for the same candidate/months.
- If STAC remains unavailable, attempt one bounded official comparator route
  that is practical in this repo context: Open Data Cube/NCI/DEA Sandbox or an
  equivalent official indexed metadata source.
- If every official comparator is unavailable or requires credentials/account
  setup, record a precise blocker and stop before extraction.

Equivalence statuses must be explicit:

- `equivalent`
- `technical_viability_not_equivalence`
- `support_coverage_incomplete`
- `comparator_unavailable`
- `lower_evidence_only`
- `blocked`

## Compute And Data Placement

This is still metadata-light and should usually run locally on the Mac mini.
Use `deep-server-ts` only if Linux tooling, GDAL behaviour, or persistent
`/data/codex` staging materially improves the official comparator test.

If remote work is used:

- read the `nectar` docs listed above;
- run a target-machine smoke test before live route discovery;
- stage remote clones and generated payloads under `/data/codex`;
- copy only compact summaries/manifests back into the repo;
- record remote paths and cleanup state in the manifest.

Ignored local staging should use paths such as:

- `artifacts/support_pathrow_metadata_013/raw/`
- `artifacts/support_pathrow_metadata_013/intermediate/`
- `artifacts/support_pathrow_metadata_013/output/`

Confirm these paths are ignored before writing route artefacts.

## Scientific Guardrails

- This goal does not produce hydrology evidence for ecological analysis.
- Do not interpret wetness, refuge status, breeding, abundance, occurrence, or
  bird response.
- Do not promote direct S3 extraction unless support-to-path/row coverage and
  official item-set equivalence have both been proven or the remaining gap is
  explicitly accepted by Barry.
- Do not substitute easier lower-evidence products for the monthly Water
  Observations metric contract.
- The central scientific question remains dynamic hydrological reaction norms.

## Validation Gates

The goal is complete only when:

- `git status --short --branch` is recorded at start and finish;
- `rg --files` confirms expected files are present;
- `git diff --check` passes;
- focused Goal 013 tests pass;
- the full local test suite passes unless the goal records a narrow reason for
  targeted validation only;
- JSON manifests/settings parse with `python3 -m json.tool`;
- CSV deliverables parse and have required columns;
- path/row crosswalk rows have valid path and row values;
- item-set hashes are stable under repeated local execution from the same
  ignored cache;
- source URLs in claim-bearing docs have corresponding source-register entries
  or are recorded in the Goal 013 manifest;
- ignored staging paths are confirmed ignored;
- no committed files exceed 5 MB;
- no committed raw source-data extensions are present;
- local Markdown links in new/edited docs resolve;
- unfinished-marker scan finds no unresolved stub language.

If validation passes, commit and push the Goal 013 package to `main`.

## Checkpoint Rules

Update `Log.md` when:

- starting state is confirmed;
- required docs and Goal 012 evidence have been read;
- path/row source is selected and staged or blocked;
- ignored staging paths are confirmed;
- support-to-path/row crosswalk is drafted;
- direct S3 complete-path-row listing for `NWB002` is complete;
- official comparator probe is complete or blocked;
- equivalence status is decided;
- route recommendation is drafted;
- validation is complete;
- commit/push is complete or a blocker is recorded.

## Decision Authority

You may decide:

- whether all 11 supports can be covered in this goal or whether `NWB002` plus
  a control support is the defensible bound;
- the official path/row source and coverage method;
- the most practical official comparator route;
- whether Goal 014 should be direct-S3 extraction, cached STAC extraction,
  ODC/NCI/Sandbox setup, or a wait/permission step.

Pause for Barry only if the work would require credentials, paid services,
large downloads, non-official path/row sources as claim-grade evidence, or a
scientific narrowing of the planned paper.
