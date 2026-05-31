# Goal: Hydrology Acquisition Route Redesign

## Objective

Produce a source-backed decision package for how the project should obtain the
`2018-01` through `2024-12` DEA Water Observations hydrology evidence after
Goal 009 and Goal 010 showed that repeated per-support/month STAC access is
too unstable.

The goal should determine whether the next executable hydrology goal should:

- wait and retry the existing STAC path under stricter preflight gates
- redesign the workflow around cached/batched STAC queries
- use a documented alternate DEA access route
- change the hydrology evidence level or defer full-window recovery

## Why This Matters

Goal 009 proved remote execution but produced 779 endpoint-blocked rows.
Goal 010 correctly stopped before another expensive run because both Mac mini
and `deep-server-ts` service-stability probes failed.

The project now needs a better acquisition strategy, not another blind retry.
The current implementation appears to query DEA STAC inside the
support/month loop, which can imply hundreds of live endpoint calls for one
event-window run. That may be scientifically avoidable if metadata can be
queried, cached, or staged at a coarser month/region level before support-level
warping.

## Operating Mode

Current-source feasibility; hydrology acquisition design; lightweight
prototype/probe only; no full extraction; no ecological interpretation.

## Scope

In scope:

- read repo instructions, Goal 009/010 reports and manifests, current hydrology
  code, and relevant `nectar` compute/data-placement guidance
- verify current official DEA access documentation for Water Observations,
  DEA STAC, AWS/S3 public data, NCI or other official routes, and any relevant
  product metadata
- audit the current hydrology workflow's live STAC query pattern and estimate
  call counts for the 11-support, 84-month event window
- compare feasible acquisition strategies, including at least:
  - status quo STAC retry with stricter preflight
  - month/region or month/support-set STAC query caching
  - direct public S3/COG access where item paths can be known without repeated
    STAC search
  - official DEA/NCI/datacube-style routes if accessible and appropriate
  - lower-evidence fallback products such as Water Observations Statistics or
    Waterbodies time series, explicitly noting why they are or are not
    substitutes for event-window Water Observations
- add small scripts/config/tests only if they make the acquisition decision
  more concrete
- run only lightweight live probes; no full-window recovery or large download
- update docs navigation, source evidence, data stream register, decision log,
  and this goal log
- commit and push the validated package to `main`

Out of scope:

- running the full 2018-2024 hydrology extraction
- rerunning Goal 009 or Goal 010 recovery
- biodiversity data requests, downloads, or modelling
- changing wetland/support definitions
- adding Narran named subunit hydrology
- manuscript drafting or literature-source verification
- using non-official or unclear hydrology products as substitutes
- committing raw rasters, full STAC item dumps, GeoPackages, shapefiles,
  NetCDF, Parquet, RDS, SQLite/DuckDB stores, archives, or bulky derived
  products

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
- `docs/stac_resilience_009_report.md`
- `docs/stac_resilience_009_manifest.json`
- `docs/remote_full_window_hydrology_009_report.md`
- `docs/remote_full_window_hydrology_009_manifest.json`
- `docs/stac_recovery_010_report.md`
- `docs/stac_recovery_010_manifest.json`
- `docs/event_window_hydrology_series_2018_2024.csv`
- `scripts/event_window_hydrology_007.py`
- `scripts/official_support_hydrology_005.py`
- `settings/remote_full_window_hydrology_009.json`
- `settings/hydrology_recovery_010.json`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `fdb22dc` (`Run Goal 010 hydrology
  recovery preflight`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths before any probe writes files.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create:

- `docs/hydrology_acquisition_route_011_report.md`: supervisor-facing report
  comparing acquisition routes and recommending the next hydrology strategy.
- `docs/hydrology_acquisition_route_011_manifest.json`: machine-readable
  source URLs checked, probe commands, host facts, route statuses, and
  recommendation metadata.
- `docs/hydrology_acquisition_options_011.csv`: route comparison table with
  columns for route, source status, stability evidence, implementation cost,
  data volume, licensing/provenance, scientific equivalence, and recommendation.
- `docs/hydrology_stac_query_pattern_011.csv`: audit table estimating live
  query counts and cache opportunities for the current support/month workflow.

Optional, only if useful:

- `scripts/hydrology_acquisition_route_probe_011.py`
- `settings/hydrology_acquisition_route_011.json`
- `tests/test_goal011_hydrology_acquisition_route.py`

Update:

- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`
- `docs/README.md`
- `docs/goals/011-hydrology-acquisition-route-redesign/Log.md`

## Route-Comparison Requirements

For each candidate route, report:

- official source or provider
- current documentation URL and accessed date
- whether the route can reproduce the Goal 007/009 monthly support metrics
- whether it avoids or reduces live STAC search calls
- whether it still depends on remote COG reads
- expected source-data volume and staging policy
- whether it can be run from Mac mini, `deep-server-ts`, NCI, or another
  environment
- whether credentials, accounts, request steps, or special network access are
  needed
- what small smoke test would prove it
- what would be committed versus kept ignored

## Query-Pattern Audit

Audit the current code path enough to answer:

- how many STAC searches the Goal 009 full run attempted or could attempt
- whether searches are repeated for overlapping supports/months
- whether a month-level or candidate-level STAC metadata cache could reduce
  calls
- what cache key would be scientifically safe: month, product, bbox, region,
  support group, or another unit
- whether cached STAC metadata can be stored as ignored raw/intermediate data
  with a small committed manifest
- what tests would protect against stale or mismatched cached items

Do not implement a large cache system unless it is small and clearly within
this goal. A concrete design and tiny proof are enough.

## Live Probe Limits

Live probes are allowed only to support the decision package.

Keep probes bounded:

- no more than a handful of months and regions
- no full support/month extraction
- no large downloads
- no raw raster or full STAC dump committed

If DEA STAC remains unavailable, still finish the route decision package using
official documentation, code audit, prior Goal 009/010 evidence, and any
non-STAC official probes that are safe.

## Scientific Guardrails

- This goal does not produce hydrology evidence for ecological analysis.
- Do not interpret wetness, refuge status, breeding, abundance, or bird
  response.
- Do not substitute annual/statistical/open-water products for monthly
  event-window Water Observations unless the report clearly labels the lower
  evidence level and scientific loss.
- Do not narrow the central thesis to fit a convenient data route without
  recommending supervisor/lab-leader review.

## Validation Gates

The goal is complete only when:

- `git status --short --branch` is recorded at start and finish
- `rg --files` confirms expected files are present
- `git diff --check` passes
- any new tests pass
- all existing local tests pass unless the goal justifies targeted validation
  and records why
- JSON manifests parse with `python3 -m json.tool`
- CSV deliverables parse and have required columns
- source URLs in claim-bearing docs have corresponding source-register entries
  or are recorded in the Goal 011 manifest
- no committed files exceed 5 MB
- no committed raw source-data extensions are present
- local Markdown links in new/edited docs resolve
- unfinished-marker scan finds no unresolved stub language

If validation passes, commit and push the Goal 011 package to `main`.

## Checkpoint Rules

Update `Log.md` when:

- starting state is confirmed
- required docs and Goal 009/010 evidence have been read
- source/current-access documentation review is complete
- current query pattern audit is complete
- live probes, if any, are complete
- route comparison tables are drafted
- recommendation is made
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may decide:

- which official access routes are worth a lightweight probe
- whether small helper scripts/tests are needed
- which route is recommended for Goal 012

Pause or stop with a blocker package before:

- launching full-window extraction
- downloading large raw data
- requiring new credentials or accounts
- switching to a non-official data source
- changing wetland supports or hydrology metrics
- making ecological claims

## Final Response Requirements

Report:

- commit SHA and push status
- route recommendation and rationale
- source docs and routes checked
- live probes performed, if any
- estimated STAC call reduction or alternative-route benefit
- validation commands and outcomes
- final git status
- residual risks
- recommended Goal 012
