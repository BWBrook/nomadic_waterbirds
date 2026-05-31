# Goal: Narran Subunit Evidence And Remote Hydrology Rehearsal

## Objective

Resolve the remaining Narran named-subunit geometry gap as far as public source
evidence allows, then make the hydrology compute route more ambitious by
rehearsing event-window extraction on `deep-server`.

## Why This Matters

Goal 007 produced the first monthly parent/subunit event-window hydrology
series and confirmed that the current metric design is useful. It also exposed
two blockers before ecological interpretation:

- Narran still has named features, including Clear Lake and Back Lake, but no
  verified standalone vector geometry or DEA Waterbody UID relationship.
- The Mac mini had to use a `2020-01` through `2024-12` fallback window because
  the default `2018-01` through `2024-12` local run looked too slow.

Goal 008 should treat both as project-management lessons. Do not move to
biodiversity linkage or ecological role interpretation until the Narran unit
problem and compute-routing pathway are better controlled.

## Operating Mode

Full paper workflow; source-evidence strengthening; hydrology-only compute
routing and remote rehearsal; no biodiversity data.

## Scope

In scope:

- search current official or primary public sources for Narran named subunit
  geometry or defensible open-water/lignum/floodplain support evidence
- update the Narran support-evidence status honestly, including keeping it
  unresolved if no defensible geometry is found
- create a Narran-specific crosswalk that separates names, geometry evidence,
  DEA Waterbody relationships, and inclusion decisions
- write a mandatory compute-routing memo for Goal 008 and near-term hydrology
  scale-up
- probe `deep-server` as the preferred CPU-heavy single-host Linux target
- if `deep-server` is reachable and viable, run a small remote hydrology
  rehearsal and, if practical, the full `2018-01` through `2024-12`
  event-window series for the current reviewed support set
- commit only scripts/config, tests, docs, manifests, and small summaries
- update project registers, docs navigation, decision log, and this goal log
- commit and push the validated package to `main`

Out of scope:

- biodiversity data requests or downloads
- eBird, Birdata, ALA, or EAWS extraction
- final ecological wetland-unit decisions
- refuge, breeding, abundance, or nomadic-response interpretation
- full historical extraction back to 1986
- remote GPU work
- `kunanyi` production scheduling
- committing raw geometry, rasters, KMZ/KML, GeoPackages, shapefiles, NetCDF,
  Parquet, RDS, SQLite/DuckDB stores, archives, or bulky derived products

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `/Users/bwbrook/work/nectar/docs/workflows/control-plane-doctrine.md`
- `/Users/bwbrook/work/nectar/docs/workflows/compute-resource-selection.md`
- `/Users/bwbrook/work/nectar/docs/workflows/project-integration.md`
- `/Users/bwbrook/work/nectar/docs/workflows/data-placement.md`
- `/Users/bwbrook/work/nectar/docs/exchange/current_status.md`
- `docs/named_subunit_evidence_report.md`
- `docs/named_subunit_crosswalk.csv`
- `docs/event_window_hydrology_series_report.md`
- `docs/event_window_hydrology_series_manifest.json`
- `docs/literature/deep_research_hydrological_reaction_norms_triage_2026-05-31.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `afea5fc` (`Record Goal 007 clean-tree
  validation`).
- Inspect the tree with `rg --files`.
- Confirm any raw/staging paths are ignored before placing raw source files
  there.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create or update:

- `docs/narran_named_subunit_evidence_report.md`: source-evidence report for
  Clear Lake, Back Lake, Long Arm, lignum/floodplain supports, DEA Waterbody
  overlaps, and any other defensible Narran subunit candidates.
- `docs/narran_named_subunit_evidence_manifest.json`: source URLs, accessed
  dates, staged raw paths, file sizes, hashes, commands, and cleanup status.
- `docs/narran_named_subunit_crosswalk.csv`: machine-readable Narran support
  table with support ID, display name, evidence status, source identifier,
  geometry status, DEA UID relationship, inclusion decision, and caveat.
- `docs/compute_routing_memo_008.md`: mandatory memo choosing the next compute
  path for hydrology scale-up, with live probe evidence and a recommendation.
- `docs/remote_hydrology_rehearsal_008_report.md`: remote rehearsal report if
  `deep-server` is reachable; otherwise explain why the memo is the final
  compute artefact for this goal.
- `docs/remote_hydrology_rehearsal_008_manifest.json`: machine-readable
  commands, host facts, remote paths, runtimes, outputs, and cleanup status if
  a remote rehearsal runs.
- optional `docs/event_window_hydrology_series_2018_2024.csv`,
  `docs/event_window_hydrology_summary_2018_2024.csv`, and
  `docs/event_window_hydrology_series_2018_2024_manifest.json` only if the
  full default event window is successfully run and outputs remain small and
  reviewable.
- minimal scripts/config/tests needed to support the source-evidence and
  remote-rehearsal workflow.
- updates to `docs/source_evidence_register.md`,
  `docs/data_stream_register.md`, `docs/decision_log.md`, `docs/README.md`,
  and this goal's `Log.md`.

Use ignored local or remote staging paths such as:

```text
data/scratch/goal008/
artifacts/narran_subunit_evidence/raw/
artifacts/remote_hydrology_rehearsal/raw/
artifacts/remote_hydrology_rehearsal/intermediate/
artifacts/remote_hydrology_rehearsal/output/
/data/codex/nomadic_waterbirds_goal008/   # remote deep-server working area
```

Do not force these exact paths if a cleaner ignored layout is better, but
record the chosen paths and verify ignore status before use.

## Narran Evidence Rules

- Prefer official or primary public sources: DCCEEW/Ramsar, NSW government
  spatial data, official Ramsar information sheets, state wetland plans,
  agency reports, or other authoritative public records.
- It is acceptable to use source pages, PDFs, WMS/WFS/ArcGIS endpoints, KMZ/KML
  boundary downloads, or small public geometry downloads if staged under
  ignored paths and manifested.
- Do not infer Clear Lake, Back Lake, Long Arm, or lignum geometry solely from
  name text on a webpage.
- Do not infer a DEA Waterbody UID relationship without documented overlap,
  centroid, or containment evidence.
- If no defensible named subunit geometry exists, say so and keep Narran
  parent-only for event-window hydrology.

## Remote Compute Rules

This goal explicitly authorises a narrow `deep-server` probe and remote
hydrology rehearsal.

Default target:

```text
deep-server
```

Use `deep-server-ts` or another documented alias only if the default alias is
not reachable and the control-plane docs support the alternative.

Minimum live probe:

- host identity
- CPU count
- memory
- free space under `/data`
- Python version
- GDAL availability if already installed
- GitHub access or ability to receive source via Git/rsync

If the probe succeeds, create or refresh a remote working clone under
`/data/codex`, run a tiny workflow smoke test, and record all commands and
outputs in `docs/compute_routing_memo_008.md` and the remote rehearsal
manifest.

If dependencies are not present, install only minimal project-required
dependencies if this is quick and non-invasive. Otherwise stop with a routing
memo rather than turning this goal into remote-system administration.

Remote stretch target:

- run the default `2018-01` through `2024-12` event window for the current 11
  reviewed supports on `deep-server`
- commit the small CSV/JSON summaries only if outputs are reviewable and no raw
  data enter Git

If the full run is not practical in this goal, the remote smoke and routing
memo are sufficient.

## Scientific Guardrails

- This is still hydrology-support evidence, not ecological interpretation.
- Do not make bird abundance, breeding, refuge, drought-response, or
  conservation-priority claims.
- Preserve the distinction between official parent supports, named geometry,
  DEA Waterbodies open-water screens, unresolved names, and final ecological
  units.
- Treat unresolved Narran geometry as useful evidence, not a failure.
- Treat compute routing as part of reproducibility, not an implementation
  afterthought.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- raw/staging paths confirmed ignored before use
- JSON manifests parse with `python3 -m json.tool`
- CSV outputs parse and have required columns
- Narran crosswalk has explicit rows for at least parent support, Clear Lake,
  Back Lake, and any additional named/geometry candidates reviewed
- compute-routing memo records live probe commands, outcomes, host choice, and
  next recommendation
- remote rehearsal report/manifest exists if `deep-server` was reachable
- focused tests pass if scripts were added or changed
- no committed files exceed 5 MB
- no committed raw source-data extensions are present
- local Markdown links in new/edited docs resolve
- unfinished-marker scan finds no unresolved stub language

If validation passes, commit and push the Goal 008 package to `main`.

## Checkpoint Rules

Update `Log.md` when:

- starting state is confirmed
- source/staging policy is confirmed
- Narran source search is complete
- Narran crosswalk is drafted
- compute-routing probe is complete
- remote rehearsal starts, finishes, or is blocked
- reports/manifests are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- search official/current public sources for Narran geometry evidence
- stage small public source files in ignored paths
- create remote working directories under `/data/codex` on `deep-server`
- run narrow SSH probes and remote smoke/rehearsal commands
- add minimal scripts/config/tests required for this goal
- recommend whether the next goal should be remote full-window hydrology,
  biodiversity-access preparation, or literature-source verification
- commit and push validated scripts, docs, manifests, tests, and small
  summaries

Pause and ask Barry before:

- requesting or downloading biodiversity data
- using private credentials
- committing raw source data or bulky derived products
- changing the project's biological/geographic scope
- launching `kunanyi`, Nectar GPU, or Alien WSL work
- making ecological interpretation claims

## Stop Conditions

Stop when one of these is true:

- Narran subunit evidence and compute-routing rehearsal are validated,
  committed, and pushed
- no defensible Narran subunit geometry can be found and this is documented in
  the report, manifest, crosswalk, and decision log
- `deep-server` is not reachable or not viable and the compute-routing memo
  documents exact blocker evidence
- the work would require biodiversity access, final ecological-unit decisions,
  full historical extraction, or production-scale HPC beyond this goal

## Final Response Requirements

Report:

- what changed
- Narran evidence status and whether named subunits remain unresolved
- remote compute probe result and host recommendation
- remote rehearsal outcome or blocker
- whether the full `2018-01` through `2024-12` event window was run
- raw-data staging paths, file sizes, and cleanup status
- exact validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual risks
- recommended Goal 009
