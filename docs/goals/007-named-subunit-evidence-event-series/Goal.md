# Goal: Named Subunit Evidence And Event-Window Hydrology Series

## Objective

Strengthen the named-subunit evidence for the Goal 006 parent-child support
system, then run a bounded hydrology-only monthly event-window series for the
reviewed parent/subunit support set.

## Why This Matters

Goal 006 proved that a parent-child registry and selected subunit hydrology
metrics can be built reproducibly without committing raw data. The registry is
now good enough to show where subunit evidence is strong and where it remains
thin. In particular:

- Ramsar components give named official supports for Macquarie, Gwydir, and
  Kerang.
- DEA Waterbodies give useful open-water screening subunits for Currawinya, but
  do not yet prove Lake Numalla/Lake Wyara identity.
- Narran remains represented by the parent Ramsar support and Waterbodies
  overlap rows, but lacks a defensible named lake/lignum subunit split.
- The current hydrology rows cover only three months, so lag, novelty, drying,
  and hydroperiod metrics remain deferred.

Goal 007 should bridge those gaps while staying hydrology-only. It should
produce a stronger support evidence package and an event-window monthly series
that is long enough to exercise the time-history metrics needed for later
reaction-norm modelling.

## Operating Mode

Full paper workflow, hydrology-only event-window prototype, source-evidence
strengthening, raw-data-staged workflow.

## Scope

In scope:

- review and strengthen named-subunit evidence for the current parent/subunit
  system, with special attention to Narran and Currawinya
- preserve the Goal 005 parent supports and Goal 006 subunit registry as the
  starting point
- create a versioned support-set decision table for the longer hydrology series
- run a bounded monthly hydrology series over an event window, not the full
  historical archive
- compute monthly base metrics plus first-pass derived time-history metrics:
  lag, trailing wetness, wetting novelty, consecutive wet/dry months, and
  drying velocity
- compare parent and selected subunit time series in small reviewable tables
- update project docs and the Goal 007 log
- commit and push the validated package to `main`

Out of scope:

- biodiversity data, access requests, private credentials, eBird, Birdata, ALA,
  or EAWS downloads
- full historical hydrology extraction back to 1986
- final wetland-unit decisions
- regional water availability metrics beyond a documented deferral or a very
  small feasibility note
- ecological modelling, bird-response analysis, refuge/breeding/abundance
  claims, or manuscript result prose
- committing raw geometry, rasters, GeoPackages, shapefiles, GeoJSON, NetCDF,
  Parquet, RDS, archive files, DuckDB/SQLite stores, or large derived files
- remote/HPC execution unless this goal stops with a compute-routing memo

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/subunit_support_registry_report.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/subunit_support_registry_manifest.json`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/subunit_support_registry.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/subunit_hydrology_prototype_report.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/subunit_hydrology_prototype_manifest.json`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/subunit_hydrology_prototype_summary.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/real_support_hydrology_prototype_summary.csv`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/hydrology_metric_spec.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/source_evidence_register.md`
- `/Users/bwbrook/.codex/AGENTS.md`, especially the HPC / remote compute
  context

If remote compute looks necessary, read the `nectar` control-plane docs named
in `/Users/bwbrook/.codex/AGENTS.md` and write
`docs/compute_routing_memo_007.md`. Prefer stopping at a routing memo in this
goal rather than spending the run on remote setup.

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `2c1ee61` (`Record Goal 006 publication
  checkpoint`).
- Inspect the tree with `rg --files`.
- Confirm raw-data staging paths are ignored before placing any raw files
  there.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Work

Create or update these deliverables:

- `docs/named_subunit_evidence_report.md`: human-readable report assessing
  which parent/subunit supports now have adequate name/source evidence and
  which remain open-water screens or unresolved.
- `docs/named_subunit_evidence_manifest.json`: machine-readable provenance for
  source checks, source URLs, accessed dates, staged files, file sizes, hashes,
  and cleanup status.
- `docs/named_subunit_crosswalk.csv`: one row per support considered for the
  event-window series, with parent support ID, subunit ID if any, display name,
  evidence status, support type, source identifiers, inclusion decision, and
  caveat.
- `docs/event_window_hydrology_series_report.md`: human-readable report
  summarising the event-window series, derived time-history metrics, quality
  gaps, and what the result does and does not support.
- `docs/event_window_hydrology_series_manifest.json`: machine-readable
  provenance for hydrology processing, commands, versions, source products,
  event-window dates, support set, staged paths, output paths, runtime, and
  resource notes.
- `docs/event_window_hydrology_series.csv`: monthly support-level table with
  base metrics and derived time-history fields.
- `docs/event_window_hydrology_summary.csv`: compact review table summarising
  support-level wetness, quality, wet-month counts, maximum wetness, timing,
  and missing/quality-fail counts.
- `docs/compute_routing_memo_007.md`: required if local execution is blocked
  or if the event-window series should be moved to `deep-server`, Nectar, or
  another target; optional otherwise as a section in the report.
- minimal executable script/config files under `scripts/` and `settings/`.
- at least one focused test covering derived time-history metrics.
- updated `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`, and this goal's `Log.md`.

Use ignored local scratch paths such as:

```text
data/scratch/goal007/
artifacts/event_window_hydrology/raw/
artifacts/event_window_hydrology/intermediate/
artifacts/event_window_hydrology/output/
artifacts/named_subunit_evidence/raw/
```

Do not force these exact paths if a cleaner ignored layout is better, but record
the chosen paths in the manifests and verify they are ignored before use.

## Support Set

Use a bounded support set, not every retained subunit.

Default included supports:

- five Goal 005 parent Ramsar supports:
  - `nwb001_ramsar_ref337`
  - `nwb002_ramsar_ref1291`
  - `nwb003_ramsar_ref993`
  - `nwb004_ramsar_ref265`
  - `nwb005_ramsar_ref791`
- six Goal 006 selected subunits:
  - `nwb001_ramsar_component_359`
  - `nwb003_ramsar_component_121`
  - `nwb004_ramsar_component_354`
  - `nwb004_ramsar_component_369`
  - `nwb005_dea_waterbody_r4yss38r6_v3`
  - `nwb005_dea_waterbody_r4ysdndx8_v3`

Optional additions:

- add a Narran named subunit only if source evidence is strong enough
- add Currawinya Lake Numalla/Lake Wyara named rows only if source evidence is
  strong enough to link the current Waterbodies subunits or another official
  geometry to those names

Do not add a support merely because it would make the table look complete.
Record unresolved support evidence as a useful result.

## Event Window

Default event window:

```text
2018-01 through 2024-12 inclusive
```

Rationale:

- includes severe dry baseline conditions
- includes the 2022 wet/flood period
- includes recent post-wet-period conditions
- is long enough for 1-month, 3-month, trailing, 12-month cumulative, and
  consecutive wet/dry metrics
- remains bounded enough for local prototype execution

If this is too heavy, fall back to a shorter documented event window that still
supports lag and novelty metrics, or stop with `docs/compute_routing_memo_007.md`.

## Metric Expectations

For each support/month, compute or preserve:

- all Goal 003 monthly base fields already used in Goals 005 and 006
- `wet_area_lag_1m`
- `wet_prop_lag_1m`
- `wet_area_lag_3m`
- `wet_prop_lag_3m`
- `wet_prop_trailing_3m`
- `wetting_delta_1m`
- `wetting_delta_3m`
- `novel_after_dry_flag`
- `dry_spell_length_prior`
- `cumulative_wet_months_12m`
- `consecutive_wet_months`
- `consecutive_dry_months_prior`
- `drying_velocity_1m`
- `drying_velocity_3m`

Preserve missing and quality-fail months. Do not interpolate in this goal.

## Source Evidence Rules

- Use official or primary sources where possible.
- For named-lake evidence, record whether the source proves:
  - name only
  - approximate location
  - polygon/geometry
  - relationship to a DEA Waterbody UID
  - relationship to a Ramsar component
- Do not infer a Lake Numalla/Lake Wyara or Narran subunit identity solely from
  a Waterbodies UID without evidence.
- If evidence remains unresolved, leave the current subunit as an open-water
  screening support and say so.

## Compute And Resource Rules

Default to the Mac mini for this bounded event-window prototype.

Stop and write `docs/compute_routing_memo_007.md` instead of pushing through if
any of these occur:

- expected temporary downloads exceed 8 GB total or any single raw file exceeds
  2 GB
- expected local runtime exceeds about 2 hours
- expected local memory pressure exceeds about 14 GB
- macOS geospatial dependency setup becomes the main task
- Linux/Open Data Cube tooling is clearly more appropriate
- the prototype wants to become full historical extraction rather than the
  bounded 2018-2024 event window

Do not launch remote/HPC work in this goal unless it is only a narrow live probe
needed to write the routing memo. A future goal can execute remote work after
the routing decision is explicit.

## Scientific Guardrails

- Treat this as hydrology-support and time-history evidence, not ecological
  inference.
- Do not make claims about bird abundance, breeding, refuge value, or nomadic
  response.
- Preserve vegetated/mixed-water under-detection caveats.
- Preserve the distinction between official parent supports, Ramsar
  components, DEA Waterbodies open-water screens, and final ecological units.
- Treat quality-fail, missing, all-zero, and sparse-support periods as
  important evidence.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- confirm chosen raw/staging paths are ignored before raw files are placed
  there
- run the named-subunit/event-window script or document the exact blocker
- run the focused time-history metric test
- parse both manifest JSON files with `python3 -m json.tool`
- parse all CSV outputs and confirm:
  - every included support appears in `docs/named_subunit_crosswalk.csv`
  - every hydrology row has a support ID, month, status, and quality flag
  - derived time-history fields are present
  - event-window months match the configured range or documented fallback
- confirm no committed files are larger than 5 MB
- confirm no raw source-data extensions are committed, including `.shp`,
  `.dbf`, `.shx`, `.prj`, `.gpkg`, `.geojson`, `.tif`, `.tiff`, `.nc`,
  `.parquet`, `.rds`, `.zip`, `.tar`, `.gz`, `.sqlite`, and `.duckdb`
- inspect new Markdown/CSV/JSON files for unresolved stub language
- verify local Markdown links in new or edited docs resolve
- run a reproducibility check from a clean or temporary working tree if the raw
  staging volume is small enough; otherwise document why cached ignored staging
  was used

If validation passes, commit and push the Goal 007 package to `main`.

## Checkpoint Rules

Update `docs/goals/007-named-subunit-evidence-event-series/Log.md` when:

- starting state and compute choice are confirmed
- raw-data staging paths and no-commit policy are confirmed
- named-subunit source checks are complete
- support-set decision table is drafted
- first event-window hydrology rows are computed or blocked
- derived time-history metrics are computed or blocked
- report/manifest/summary files are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- choose Python, R, GDAL/OGR, `sf`, or other existing repo-appropriate tools
  for the bounded event-window prototype
- add minimal dependencies only if the need is concrete and documented
- stage public raw geometry and raster windows in ignored local paths
- choose a shorter event window if the default is too heavy, provided the
  fallback still supports lag/novelty testing and is documented
- retain open support-evidence questions rather than forcing weak named
  crosswalks
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

- named-subunit evidence and event-window hydrology series are validated,
  committed, and pushed
- local execution is blocked by data volume, dependency, memory, runtime,
  source access, or platform constraints and a compute-routing or blocker memo
  is committed/pushed
- the work would require biodiversity access, final wetland-unit decisions, or
  full historical extraction outside this goal

## Final Response Requirements

Report:

- what changed
- named-subunit evidence status, especially Narran and Currawinya
- support set used for the event-window series
- event window and metric coverage
- derived time-history metrics computed versus deferred
- raw-data staging paths, file sizes, and cleanup status
- compute/resource decision
- exact validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual risks
- recommended Goal 008
