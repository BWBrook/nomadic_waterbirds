# Goal: Hydrology-Only Extraction Smoke Test

## Objective

Run a small hydrology-only extraction smoke test for the five included
prototype wetland candidates, committing only small provenance, manifest,
summary, and review artefacts.

## Why This Matters

Goal 003 produced a structured wetland-unit crosswalk and hydrology metric
specification. Goal 004 should prove the first executable data path: official
geometry or workable masks can be staged, DEA hydrology can be accessed at tiny
scale, and the metric contract can produce auditable monthly summaries without
touching biodiversity data or committing raw source products.

The outcome is not ecological interpretation. It is evidence that the hydrology
pipeline is technically feasible and well bounded.

## Operating Mode

Full paper workflow plus hydrology extraction smoke test.

## Scope

In scope:

- run a tiny local hydrology-only extraction/access smoke test for the five
  `include_in_next_extraction_smoke=yes` candidates from
  `docs/prototype_wetland_unit_crosswalk.csv`
- stage any raw official geometry, raster, or product-access files only under
  ignored local paths
- use DEA Water Observations as the target authoritative hydrology source and
  DEA Waterbodies only as a screening/subunit aid
- compute or minimally validate a small subset of monthly metrics from
  `docs/hydrology_metric_spec.md`
- record provenance, data sizes, access methods, commands, and limitations
- commit only small summaries, manifests, documentation, and source code/config
  needed to reproduce the smoke test

Out of scope:

- eBird, Birdata, ALA, or EAWS biodiversity downloads
- submitting access requests or using private credentials
- full historical hydrology extraction
- ecological modelling or bird-response analysis
- final wetland-unit or mask decisions
- committing raw geometry, rasters, GeoPackages, shapefiles, NetCDF, Parquet,
  RDS, archive files, or large derived products
- remote/HPC execution unless a compute-routing memo justifies a follow-up goal

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/prototype_wetland_unit_crosswalk.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/prototype_wetland_unit_crosswalk.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/hydrology_metric_spec.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/product_access_probe_003.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/decision_memo_003.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/reproducibility_plan.md`
- `/Users/bwbrook/.codex/AGENTS.md`, especially the HPC / remote compute
  context, before deciding whether the local Mac is sufficient

If remote compute looks necessary, read the `nectar` control-plane docs named
in `/Users/bwbrook/.codex/AGENTS.md` and write a compute-routing memo. Prefer
stopping at the memo in this goal rather than spending the run on remote setup.

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `2da4ad9` (`Record Goal 003 publication
  checkpoint`).
- Inspect the tree with `rg --files`.
- Confirm `data/` and `artifacts/` remain ignored except their policy README
  files.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Work

Create or update these deliverables:

- `docs/hydrology_smoke_test_report.md`: human-readable smoke-test report,
  including what was attempted, what succeeded, what failed, candidate-level
  caveats, and whether the project is ready for a fuller hydrology prototype.
- `docs/hydrology_smoke_test_manifest.json`: machine-readable provenance with
  commands, software/tool versions where available, source URLs, access dates,
  staged raw-data paths, staged file sizes, cleanup status, output paths, and
  metric-spec version.
- `docs/hydrology_smoke_test_summary.csv`: small summary table. Include one row
  per candidate/support/month attempted, with candidate ID/name, support ID/type,
  month, source product, access method, status, clear/invalid observation
  evidence if computed, wetness metric values if computed, and failure/caveat
  fields.
- `docs/compute_routing_memo_004.md`: required if the local smoke test cannot
  proceed cleanly or if remote/HPC would be a better next step; optional
  otherwise as a short section in the report.
- executable script/config files if needed, preferably under `scripts/` and
  `settings/`, with narrow dependencies and comments.
- updated `docs/data_stream_register.md`, `docs/decision_log.md`, and
  `docs/README.md`.
- updated `docs/goals/004-hydrology-extraction-smoke-test/Log.md`.

Use ignored local scratch paths such as:

```text
data/scratch/goal004/
artifacts/hydrology_smoke/raw/
artifacts/hydrology_smoke/intermediate/
```

Do not force these exact paths if another ignored layout is cleaner, but record
the chosen paths in the manifest.

## Minimum Smoke-Test Expectations

Attempt all five included candidates:

- `NWB001` Macquarie Marshes
- `NWB002` Narran Lake Nature Reserve
- `NWB003` Gwydir Wetlands
- `NWB004` Kerang Wetlands
- `NWB005` Currawinya Lakes

For each candidate, try to establish:

- official geometry or mask source can be staged or clearly identified
- DEA Waterbodies overlap/support can be checked or explicitly marked
  unavailable/untested
- at least one Water Observations access path can be tested for a tiny AOI,
  support, or product subset

For the metric smoke, target 2-3 contrasting months total, not a full time
series. It is acceptable if the smoke computes a subset of metrics for a subset
of supports, provided the report clearly distinguishes:

- successfully computed metrics
- access-only checks
- candidates blocked by geometry or product-access constraints
- metric-spec fields deferred to the full prototype

## Compute And Resource Rules

Default to the Mac mini for this tiny smoke test.

Stop and write `docs/compute_routing_memo_004.md` instead of pushing through if
any of these occur:

- expected temporary downloads exceed 2 GB total or any single raw file exceeds
  500 MB
- expected local runtime exceeds about 45 minutes
- expected local memory pressure exceeds about 12 GB
- macOS geospatial dependency setup becomes the main task
- Linux/Open Data Cube tooling appears clearly more appropriate
- remote/HPC resources would be needed for anything beyond a tiny smoke

Do not launch remote/HPC work in this goal unless it is only a narrow live probe
needed to write the routing memo. A future goal can execute remote work after
the routing decision is explicit.

## Scientific Guardrails

- Treat this as hydrology pipeline validation, not ecological inference.
- Do not make claims about bird response, abundance, refuge value, or breeding
  outcomes.
- Do not treat DEA Waterbodies overlap as proof of full wetland support.
- Preserve Water Observations invalid/mixed-vegetation caveats.
- Report failures and missingness as useful evidence.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- run the smoke-test script or document the exact blocker that prevented it
- parse `docs/hydrology_smoke_test_manifest.json` as JSON
- parse `docs/hydrology_smoke_test_summary.csv` as CSV and confirm it has at
  least one row per five included candidates
- confirm no committed files larger than 5 MB
- confirm no raw source-data extensions are committed, including `.shp`,
  `.dbf`, `.shx`, `.prj`, `.gpkg`, `.geojson`, `.tif`, `.tiff`, `.nc`,
  `.parquet`, `.rds`, `.zip`, `.tar`, `.gz`, `.sqlite`, and `.duckdb`
- inspect new Markdown/CSV/JSON files for unresolved stub language
- verify local Markdown links in new or edited docs resolve
- if executable code/config is added, run the narrow syntax/config checks
  appropriate to the chosen language/tooling

If validation passes, commit and push the smoke-test package to `main`.

## Checkpoint Rules

Update `docs/goals/004-hydrology-extraction-smoke-test/Log.md` when:

- starting state and compute choice are confirmed
- raw-data staging path and no-commit policy are confirmed
- geometry/product access path is chosen
- first candidate access or extraction succeeds/fails
- all five candidates have summary rows
- report/manifest/summary are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- choose R, Python, GDAL, DEA-native tooling, or shell tools for the tiny smoke,
  provided dependencies stay narrow and documented
- add minimal scripts/config needed to reproduce the smoke
- stage public raw data in ignored paths
- choose 2-3 contrasting months for the smoke test, with rationale
- downgrade from metric extraction to access-only checks for a candidate if
  geometry/product constraints require it, but document why
- recommend the next goal based on evidence
- commit and push validated scripts, docs, manifests, and small summaries

Pause and ask Barry before:

- downloading biodiversity data
- submitting access requests
- using private credentials
- committing raw source data or large derived products
- running full historical extraction
- launching remote/HPC work beyond a narrow routing probe
- making ecological interpretation claims

## Stop Conditions

Stop when one of these is true:

- the hydrology smoke test has produced a validated report, manifest, and
  summary for all five included candidates and the package is committed/pushed
- local execution is blocked by data volume, dependency, memory, runtime, or
  platform constraints and a compute-routing memo is committed/pushed
- the work would require biodiversity access, final wetland decisions, or full
  extraction outside this goal

## Final Response Requirements

Report:

- what changed
- candidates attempted and smoke-test status
- metrics computed versus access-only checks
- raw-data staging paths and cleanup status
- compute/resource decision
- exact validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual risks
- recommended Goal 005
