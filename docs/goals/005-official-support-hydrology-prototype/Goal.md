# Goal: Official-Support Hydrology Prototype

## Objective

Build the first hydrology-only prototype that uses documented official wetland
supports or subunits rather than tiny probe pixels, and compute bounded monthly
DEA Water Observations metrics over those real supports.

## Why This Matters

Goal 004 proved that the project can reach DEA STAC, open Water Observations
COGs through GDAL `/vsis3/`, decode the bit field, and write auditable
manifests without committing raw data. It deliberately did not prove any
wetland-level hydrology because the supports were analyst-chosen 3x3-pixel
probes.

Goal 005 should move the evidence level from access smoke test to real-support
prototype. The central question is whether official wetland geometry or
official open-water subunits can be staged reproducibly and used to calculate
monthly hydrology metrics for the five included candidates without crossing
into biodiversity data, ecological interpretation, or full historical scale-up.

## Operating Mode

Full paper workflow, hydrology-only prototype, raw-data-staged workflow.

## Scope

In scope:

- attempt the five Goal 004 candidates:
  - `NWB001` Macquarie Marshes
  - `NWB002` Narran Lake Nature Reserve
  - `NWB003` Gwydir Wetlands
  - `NWB004` Kerang Wetlands
  - `NWB005` Currawinya Lakes
- verify and stage current official geometry or subunit sources under ignored
  local paths
- use official Ramsar/DCCEEW geometry where feasible for named-complex
  supports
- use DEA Waterbodies only as documented open-water subunits or screening
  supports, not as a substitute for the whole wetland complex
- compute bounded monthly Water Observations metrics for real supports for the
  same three months used in Goal 004 unless a better documented month set is
  justified
- aggregate all readable Water Observations scenes within each target month for
  each support; do not choose only the clearest single scene as the metric
- write small committed support registries, summaries, manifests, and reports
- update project docs and the Goal 005 log
- commit and push the validated package to `main`

Out of scope:

- eBird, Birdata, ALA, EAWS, or any biodiversity download
- submitting access requests or using private credentials
- full historical hydrology extraction
- ecological modelling, bird-response analysis, breeding/refuge claims, or
  manuscript result prose
- final wetland-unit decisions
- committing raw geometry, rasters, GeoPackages, shapefiles, GeoJSON, NetCDF,
  Parquet, RDS, archive files, DuckDB/SQLite stores, or large derived files
- remote/HPC execution unless this goal stops with a compute-routing memo

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/hydrology_smoke_test_report.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/hydrology_smoke_test_manifest.json`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/hydrology_smoke_test_summary.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/prototype_wetland_unit_crosswalk.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/prototype_wetland_unit_crosswalk.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/hydrology_metric_spec.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/source_evidence_register.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/data_stream_register.md`
- `/Users/bwbrook/.codex/AGENTS.md`, especially the HPC / remote compute
  context

If remote compute looks necessary, read the `nectar` control-plane docs named
in `/Users/bwbrook/.codex/AGENTS.md` and write
`docs/compute_routing_memo_005.md`. Prefer stopping at a routing memo in this
goal rather than spending the run on remote setup.

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `589af6a` (`Record Goal 004 publication
  checkpoint`).
- Inspect the tree with `rg --files`.
- Confirm raw-data staging paths are ignored before placing any raw files
  there.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Work

Create or update these deliverables:

- `docs/official_support_geometry_report.md`: human-readable report describing
  which official support sources were checked, which were staged, which support
  definitions were used, and which candidates remain blocked or caveated.
- `docs/official_support_geometry_manifest.json`: machine-readable provenance
  for geometry/subunit staging, including source URLs, accessed dates, staged
  raw paths, file sizes, hashes where practical, cleanup status, selected
  candidate/support IDs, and geometry caveats.
- `docs/official_support_geometry_summary.csv`: one row per candidate/support
  considered, with candidate ID/name, support ID, support type, source,
  source ID/URL, staged path class, geometry area if computed, geometry hash or
  source hash if practical, inclusion status, and caveat.
- `docs/real_support_hydrology_prototype_report.md`: interpretation of the
  real-support hydrology prototype, explicitly distinguishing computed
  wetland-support metrics from unresolved geometry or product caveats.
- `docs/real_support_hydrology_prototype_manifest.json`: machine-readable
  provenance for Water Observations processing, commands, versions, month set,
  source products, staged raw/intermediate paths, output paths, runtime, and
  resource notes.
- `docs/real_support_hydrology_prototype_summary.csv`: one row per
  candidate/support/month attempted with the Goal 003 base monthly metrics
  where computed, plus status and caveat fields.
- `docs/compute_routing_memo_005.md`: required if local execution is blocked
  or if real-support extraction should be moved to `deep-server`, Nectar, or
  another target; optional otherwise as a short section in the prototype
  report.
- minimal executable script/config files under `scripts/` and `settings/`.
- updated `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`, and this goal's `Log.md`.

Use ignored local scratch paths such as:

```text
data/scratch/goal005/
artifacts/hydrology_supports/raw/
artifacts/hydrology_supports/intermediate/
artifacts/hydrology_supports/output/
artifacts/hydrology_real_support/raw/
artifacts/hydrology_real_support/intermediate/
artifacts/hydrology_real_support/output/
```

Do not force these exact paths if a cleaner ignored layout is better, but record
the chosen paths in the manifests and verify they are ignored before use.

## Minimum Prototype Expectations

For all five candidates:

- attempt to identify and stage a current official named-complex geometry or a
  documented official subunit source
- record candidate-level support status even if the support is blocked
- distinguish named-complex supports from DEA Waterbodies open-water subunits
- record why any candidate cannot yet receive real-support metrics

For hydrology metrics:

- target the Goal 004 months by default:
  - `2019-01`
  - `2022-11`
  - `2024-03`
- compute at least the monthly base metrics from
  `docs/hydrology_metric_spec.md` for every feasible real support:
  - `n_scene_m`
  - `n_pixel_u`
  - `clear_obs_count`
  - `invalid_obs_count`
  - `clear_obs_fraction`
  - `current_wet_area_m2`
  - `valid_support_area_m2`
  - `current_proportion_wet`
  - wet/dry pixel evidence
  - invalid-bit counts
  - quality flag
  - wet-month flag
- defer lag, novelty, drying, hydroperiod, and regional-water metrics unless
  they fall out cleanly from the bounded prototype; record deferrals clearly

If all five candidates are feasible within local resource rules, process all
five. If not, process a scientifically informative subset and preserve a
complete geometry/status table for all five. A useful fallback subset would
include one open-water-heavy unit, one vegetated/floodplain unit, and one
multi-lake or arid unit.

## Geometry And Evidence Rules

- Do not hand-draw wetland boundaries from the Goal 004 probe points.
- Do not treat a DEA Waterbodies polygon as the whole wetland unless official
  source evidence supports that interpretation.
- Do not commit raw coordinates or geometry files, even if the source is public
  and licensed. Commit metadata, hashes, summaries, support IDs, and caveats.
- It is acceptable to stage public raw geometry locally in ignored paths for
  processing.
- It is acceptable to compute derived areas and support-level summary rows for
  committed CSV/JSON outputs.
- Every support row must identify whether the support is:
  - official named-complex geometry
  - official Ramsar parcel/component
  - DEA Waterbodies open-water subunit
  - other official subunit
  - blocked/deferred

## Compute And Resource Rules

Default to the Mac mini for this bounded prototype.

Stop and write `docs/compute_routing_memo_005.md` instead of pushing through if
any of these occur:

- expected temporary downloads exceed 5 GB total or any single raw file exceeds
  1.5 GB
- expected local runtime exceeds about 90 minutes
- expected local memory pressure exceeds about 14 GB
- macOS geospatial dependency setup becomes the main task
- Linux/Open Data Cube tooling is clearly more appropriate
- the prototype wants to become full historical extraction rather than a
  bounded evidence step

Do not launch remote/HPC work in this goal unless it is only a narrow live probe
needed to write the routing memo. A future goal can execute remote work after
the routing decision is explicit.

## Scientific Guardrails

- Treat this as hydrology-support prototype evidence, not ecological inference.
- Do not make claims about waterbird abundance, breeding, refuge value, or
  nomadic response.
- Preserve the special risk that Water Observations may under-detect vegetated
  or mixed inundation.
- Preserve Ramsar and named-complex boundary caveats, especially for Macquarie
  Marshes and Gwydir Wetlands.
- Treat all-zero wetness, missing scenes, invalid-heavy months, and geometry
  mismatch as important evidence, not failure to hide.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- confirm chosen raw/staging paths are ignored before raw files are placed
  there
- run the support/hydrology prototype script or document the exact blocker
- parse both manifest JSON files with `python3 -m json.tool`
- parse both summary CSV files and confirm all five required candidates are
  represented in the geometry/status summary
- confirm hydrology rows, where computed, use real-support IDs rather than
  `*_probe_3x3`
- confirm no committed files are larger than 5 MB
- confirm no raw source-data extensions are committed, including `.shp`,
  `.dbf`, `.shx`, `.prj`, `.gpkg`, `.geojson`, `.tif`, `.tiff`, `.nc`,
  `.parquet`, `.rds`, `.zip`, `.tar`, `.gz`, `.sqlite`, and `.duckdb`
- inspect new Markdown/CSV/JSON files for unresolved stub language
- verify local Markdown links in new or edited docs resolve
- if executable code/config is added, run narrow syntax/config checks
- run a reproducibility check from a clean or temporary working tree if the raw
  staging volume is small enough; otherwise document why cached ignored staging
  was used

If validation passes, commit and push the Goal 005 package to `main`.

## Checkpoint Rules

Update `docs/goals/005-official-support-hydrology-prototype/Log.md` when:

- starting state and compute choice are confirmed
- raw-data staging paths and no-commit policy are confirmed
- official geometry/subunit source path is selected
- first official support is staged or blocked
- first real-support hydrology row is computed or blocked
- all five candidates have geometry/status rows
- report/manifest/summary files are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- choose Python, R, GDAL/OGR, `sf`, or other existing repo-appropriate tools
  for the bounded prototype
- add minimal dependencies only if the need is concrete and documented
- stage public raw geometry and raster windows in ignored local paths
- choose one or more real supports per candidate
- process fewer than all five candidates for hydrology metrics if resource or
  geometry constraints require it, provided the geometry/status table covers
  all five and the report explains the fallback
- recommend the next goal based on evidence
- commit and push validated scripts, docs, manifests, and small summaries

Pause and ask Barry before:

- downloading biodiversity data
- submitting access requests
- using private credentials
- committing raw source data or large derived products
- running full historical extraction
- launching remote/HPC work beyond a narrow routing probe
- narrowing the biological or geographic scope of the paper
- making ecological interpretation claims

## Stop Conditions

Stop when one of these is true:

- the official-support geometry/status registry and real-support hydrology
  prototype are validated, committed, and pushed
- local execution is blocked by data volume, dependency, memory, runtime,
  geometry access, or platform constraints and a compute-routing or blocker
  memo is committed/pushed
- the work would require biodiversity access, final wetland-unit decisions, or
  full historical extraction outside this goal

## Final Response Requirements

Report:

- what changed
- official supports attempted and their status
- hydrology rows computed versus blocked/deferred
- how Goal 005 differs from the Goal 004 tiny-probe smoke test
- raw-data staging paths, file sizes, and cleanup status
- compute/resource decision
- exact validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual risks
- recommended Goal 006
