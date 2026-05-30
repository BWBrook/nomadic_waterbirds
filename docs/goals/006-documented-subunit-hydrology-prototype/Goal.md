# Goal: Documented Subunit Hydrology Prototype

## Objective

Build a hydrology-only parent/subunit prototype that decomposes the Goal 005
official Ramsar parent supports into documented subunits where feasible, then
computes bounded monthly Water Observations metrics for a reviewable subset of
those subunits.

## Why This Matters

Goal 005 proved that official Ramsar supports can be staged reproducibly and
used for monthly DEA Water Observations metrics. That is now a solid parent
support layer, but it is not yet the ecological unit system the paper needs.
Macquarie, Narran, Gwydir, Kerang, and Currawinya all retain important
subunit-level heterogeneity: vegetated floodplain versus open water, Ramsar
component parcels, named lakes, regulated/saline/freshwater contrasts, and
DEA Waterbodies open-water polygons.

Goal 006 should create the first auditable parent-child support registry and a
small subunit hydrology prototype before any biodiversity linkage or ecological
interpretation.

## Operating Mode

Full paper workflow, hydrology-only subunit prototype, raw-data-staged
workflow.

## Scope

In scope:

- start from the five Goal 005 parent supports:
  - `NWB001` Macquarie Marshes
  - `NWB002` Narran Lake Nature Reserve
  - `NWB003` Gwydir Wetlands
  - `NWB004` Kerang Wetlands
  - `NWB005` Currawinya Lakes
- construct a documented subunit registry linking each parent support to
  candidate child supports
- include Ramsar component polygons as candidate subunits where the service
  already exposes named components
- attempt a bounded DEA Waterbodies v3 overlap screen for open-water subunits
  within or near the parent supports
- include official named lake/component sources if they can be verified
  cheaply and staged safely
- compute the Goal 003 monthly base hydrology metrics for selected subunits
  for the same three prototype months unless a better documented month set is
  justified
- preserve Goal 005 parent support IDs and link every subunit row to a parent
  support
- write small committed registries, summaries, manifests, reports, tests, and
  script/config files
- update project docs and the Goal 006 log
- commit and push the validated package to `main`

Out of scope:

- biodiversity data, access requests, private credentials, eBird, Birdata, ALA,
  or EAWS downloads
- full historical hydrology extraction
- final wetland-unit decisions
- ecological modelling, bird-response analysis, refuge/breeding/abundance
  claims, or manuscript result prose
- treating DEA Waterbodies as the whole wetland complex
- committing raw geometry, rasters, GeoPackages, shapefiles, GeoJSON, NetCDF,
  Parquet, RDS, archive files, DuckDB/SQLite stores, or large derived files
- remote/HPC execution unless this goal stops with a compute-routing memo

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/official_support_geometry_report.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/official_support_geometry_manifest.json`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/official_support_geometry_summary.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/real_support_hydrology_prototype_report.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/real_support_hydrology_prototype_manifest.json`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/real_support_hydrology_prototype_summary.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/prototype_wetland_unit_crosswalk.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/hydrology_metric_spec.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/source_evidence_register.md`
- `/Users/bwbrook/.codex/AGENTS.md`, especially the HPC / remote compute
  context

If remote compute looks necessary, read the `nectar` control-plane docs named
in `/Users/bwbrook/.codex/AGENTS.md` and write
`docs/compute_routing_memo_006.md`. Prefer stopping at a routing memo in this
goal rather than spending the run on remote setup.

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `0834bc6` (`Polish Goal 005 validation
  log`).
- Inspect the tree with `rg --files`.
- Confirm raw-data staging paths are ignored before placing any raw files
  there.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Work

Create or update these deliverables:

- `docs/subunit_support_registry_report.md`: human-readable report describing
  subunit source options, parent-child support decisions, included/deferred
  subunits, and caveats.
- `docs/subunit_support_registry_manifest.json`: machine-readable provenance
  for subunit source checks and staged files, including source URLs, accessed
  dates, staged raw paths, file sizes, hashes, and cleanup status.
- `docs/subunit_support_registry.csv`: one row per candidate subunit considered,
  including parent support ID, subunit ID, subunit name, subunit type, source,
  source identifier, overlap/area evidence where computed, inclusion status,
  and caveat.
- `docs/subunit_hydrology_prototype_report.md`: human-readable report comparing
  selected subunit hydrology metrics with the Goal 005 parent-support context.
- `docs/subunit_hydrology_prototype_manifest.json`: machine-readable hydrology
  processing provenance with commands, versions, source products, month set,
  parent/subunit IDs, staged paths, output paths, runtime, and resource notes.
- `docs/subunit_hydrology_prototype_summary.csv`: one row per
  parent/subunit/month attempted with monthly base metrics where computed,
  plus status and caveat fields.
- `docs/compute_routing_memo_006.md`: required if local execution is blocked
  or if subunit processing should be moved to `deep-server`, Nectar, or another
  target; optional otherwise as a section in the prototype report.
- minimal executable script/config files under `scripts/` and `settings/`.
- at least one focused test covering parent-child registry construction or
  subunit metric aggregation.
- updated `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`, and this goal's `Log.md`.

Use ignored local scratch paths such as:

```text
data/scratch/goal006/
artifacts/subunit_supports/raw/
artifacts/subunit_supports/intermediate/
artifacts/subunit_supports/output/
artifacts/subunit_hydrology/raw/
artifacts/subunit_hydrology/intermediate/
artifacts/subunit_hydrology/output/
```

Do not force these exact paths if a cleaner ignored layout is better, but record
the chosen paths in the manifests and verify they are ignored before use.

## Minimum Prototype Expectations

For the subunit registry:

- cover all five parent candidates with at least one registry row each, even if
  candidate subunits are deferred
- represent Ramsar component rows explicitly where the Goal 005 service exposes
  components, especially:
  - Macquarie Marshes: 2 Ramsar components
  - Gwydir Wetlands: 4 Ramsar components
  - Kerang Wetlands: 14 Ramsar components
- attempt a bounded DEA Waterbodies overlap screen for each parent support
  unless source access or data volume blocks it
- distinguish subunit types:
  - `ramsar_component`
  - `dea_waterbody_overlap`
  - `official_named_lake_or_component`
  - `blocked_or_deferred`
- preserve parent-child IDs and source caveats in every row

For subunit hydrology:

- target the Goal 004/005 months by default:
  - `2019-01`
  - `2022-11`
  - `2024-03`
- compute monthly base metrics from `docs/hydrology_metric_spec.md` for a
  bounded set of selected subunits
- include at minimum, if feasible:
  - at least two Kerang component or lake/open-water subunits
  - at least one Currawinya lake/open-water subunit or a clear blocker explaining
    why Lake Numalla/Lake Wyara could not yet be split
  - at least one vegetated/floodplain-sensitive unit from Macquarie, Narran, or
    Gwydir
- preserve parent-support metrics as context but do not recompute full parent
  historical series
- defer lag, novelty, drying, hydroperiod, and regional-water metrics unless
  they fall out cleanly from the bounded prototype

If all selected subunits are feasible within local resource rules, process them
all. If not, process a scientifically informative subset and preserve complete
registry/status rows for the attempted candidates.

## Evidence Rules

- Do not hand-draw subunits from probe points.
- Do not treat DEA Waterbodies as final ecological wetland units.
- Do not commit raw coordinates or geometry files.
- It is acceptable to stage public raw geometry locally in ignored paths for
  processing.
- It is acceptable to commit derived subunit metadata, areas, overlaps, hashes,
  and small hydrology summaries.
- Every subunit row must state whether it is included for hydrology metrics,
  retained for later, rejected, or blocked.
- Every report should state what this subunit layer can and cannot support.

## Compute And Resource Rules

Default to the Mac mini for this bounded prototype.

Stop and write `docs/compute_routing_memo_006.md` instead of pushing through if
any of these occur:

- expected temporary downloads exceed 5 GB total or any single raw file exceeds
  1.5 GB
- expected local runtime exceeds about 90 minutes
- expected local memory pressure exceeds about 14 GB
- macOS geospatial dependency setup becomes the main task
- Linux/Open Data Cube tooling is clearly more appropriate
- the prototype wants to become national Waterbodies extraction or full
  historical hydrology rather than a bounded evidence step

Do not launch remote/HPC work in this goal unless it is only a narrow live probe
needed to write the routing memo. A future goal can execute remote work after
the routing decision is explicit.

## Scientific Guardrails

- Treat this as subunit hydrology-support evidence, not ecological inference.
- Do not make claims about bird abundance, breeding, refuge value, or nomadic
  response.
- Preserve vegetated/mixed-water under-detection caveats for Water
  Observations.
- Preserve the difference between Ramsar components, DEA Waterbodies polygons,
  and ecological wetland-response units.
- Treat missing overlaps, invalid-heavy rows, all-zero wetness, and source
  mismatch as useful evidence.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- confirm chosen raw/staging paths are ignored before raw files are placed
  there
- run the subunit registry/hydrology prototype script or document the exact
  blocker
- run the focused test
- parse both manifest JSON files with `python3 -m json.tool`
- parse both summary/registry CSV files and confirm all five parent candidates
  are represented in `docs/subunit_support_registry.csv`
- confirm hydrology rows, where computed, include both `parent_support_id` and
  `subunit_id`
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

If validation passes, commit and push the Goal 006 package to `main`.

## Checkpoint Rules

Update `docs/goals/006-documented-subunit-hydrology-prototype/Log.md` when:

- starting state and compute choice are confirmed
- raw-data staging paths and no-commit policy are confirmed
- subunit source paths are selected
- first parent-child registry rows are created
- DEA Waterbodies overlap screen succeeds or is blocked
- first subunit hydrology row is computed or blocked
- all five parent candidates have registry/status rows
- report/manifest/summary files are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- choose Python, R, GDAL/OGR, `sf`, or other existing repo-appropriate tools
  for the bounded prototype
- add minimal dependencies only if the need is concrete and documented
- stage public raw geometry and raster windows in ignored local paths
- choose a bounded and scientifically informative subset of subunits for
  hydrology metrics
- defer a candidate or subunit if source access, geometry, or resource
  constraints require it, provided the registry records why
- recommend the next goal based on evidence
- commit and push validated scripts, docs, manifests, tests, and small
  summaries

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

- the subunit registry and bounded subunit hydrology prototype are validated,
  committed, and pushed
- local execution is blocked by data volume, dependency, memory, runtime,
  source access, or platform constraints and a compute-routing or blocker memo
  is committed/pushed
- the work would require biodiversity access, final wetland-unit decisions, or
  full historical extraction outside this goal

## Final Response Requirements

Report:

- what changed
- parent supports and subunit sources attempted
- subunit registry coverage and inclusion/defer/block statuses
- subunit hydrology rows computed versus blocked/deferred
- raw-data staging paths, file sizes, and cleanup status
- compute/resource decision
- exact validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual risks
- recommended Goal 007
