# Goal: Remote Full-Window Hydrology Scale-Up

## Objective

Make the DEA Water Observations event-window workflow resilient to transient
service failures, then run the full `2018-01` through `2024-12` event-window
hydrology series for the current reviewed support set on `deep-server-ts`.

## Why This Matters

Goal 008 proved two important things:

- `deep-server-ts` is viable for CPU-heavy single-host hydrology work: 64
  CPUs, 125 GiB RAM, 4.5 TiB free under `/data`, Python 3.12.3, GDAL 3.8.4,
  NumPy, and passing project tests.
- The full-window hydrology run was blocked by upstream DEA STAC `HTTP 503`
  responses observed from both `deep-server-ts` and the Mac mini, not by the
  remote host.

Goal 009 should therefore retry the full event window from the correct compute
host, but only after adding enough retry/backoff/resume discipline that a
transient upstream outage does not turn a scientific run into a pile of opaque
blocked rows.

## Operating Mode

Remote compute scale-up; hydrology-only; resilience/retry hardening; no
biodiversity data; no ecological interpretation.

## Scope

In scope:

- read the `nectar` control-plane docs carefully before touching remote state
- confirm current repo state and Goal 008 evidence
- add retry/backoff and clear transient-failure classification for DEA STAC
  requests and remote COG reads where appropriate
- add focused tests for retry/backoff or transient-failure classification
  without relying on live network availability
- probe DEA STAC from both Mac mini and `deep-server-ts` before launching the
  full run
- use `deep-server-ts` as the default remote host and `/data/codex` for remote
  working state
- stage source to remote using the Goal 008 rsync pattern if GitHub SSH remains
  unavailable from `deep-server`
- run the full `2018-01` through `2024-12` event-window hydrology series for
  the current Goal 007/008 reviewed 11-support set if STAC is available
- make the full-window run restartable or at least document a support/month
  shard plan and any resume limitations
- return small CSV/JSON summaries, manifests, reports, and logs to the local
  repo
- update registers, decision log, docs navigation, and this goal log
- commit and push the validated package to `main`

Out of scope:

- biodiversity data requests or downloads
- eBird, Birdata, ALA, or EAWS extraction
- changing wetland/support definitions
- adding Narran named subunit hydrology
- ecological interpretation of wetness, refuge status, breeding, abundance, or
  nomadic response
- full historical extraction back to 1986
- GPU work, Nectar GPU, Alien WSL, or `kunanyi`
- committing raw geometry, rasters, KMZ/KML, GeoPackages, shapefiles, NetCDF,
  Parquet, RDS, SQLite/DuckDB stores, archives, or bulky derived products

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `/Users/bwbrook/work/nectar/docs/workflows/control-plane-doctrine.md`
- `/Users/bwbrook/work/nectar/docs/workflows/compute-resource-selection.md`
- `/Users/bwbrook/work/nectar/docs/workflows/project-integration.md`
- `/Users/bwbrook/work/nectar/docs/workflows/data-placement.md`
- `/Users/bwbrook/work/nectar/docs/workflows/smoke-tests.md`
- `/Users/bwbrook/work/nectar/docs/workflows/tailscale-connectivity.md`
- `/Users/bwbrook/work/nectar/docs/machines/deep-server.md`
- `/Users/bwbrook/work/nectar/docs/exchange/current_status.md`
- `docs/compute_routing_memo_008.md`
- `docs/remote_hydrology_rehearsal_008_report.md`
- `docs/remote_hydrology_rehearsal_008_manifest.json`
- `docs/event_window_hydrology_series_report.md`
- `docs/event_window_hydrology_series_manifest.json`
- `docs/event_window_hydrology_summary.csv`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `26ed2d3` (`Correct Goal 008 validation
  evidence`).
- Inspect the tree with `rg --files`.
- Confirm local and remote staging paths are ignored before placing raw files
  or generated heavy outputs there.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create or update:

- `docs/stac_resilience_009_report.md`: report describing retry/backoff,
  transient-failure classification, STAC availability probes, and whether the
  full run was launched.
- `docs/stac_resilience_009_manifest.json`: machine-readable probe commands,
  retry settings, probe results, timestamps, and endpoint status.
- `docs/remote_full_window_hydrology_009_report.md`: remote run report, or a
  blocker report if STAC remains unavailable after the retry policy is tested.
- `docs/remote_full_window_hydrology_009_manifest.json`: machine-readable
  remote host facts, source-staging method, commands, paths, runtime, retry
  counts, output inventory, cleanup/continuation status, and commit context.
- if the full run succeeds:
  - `docs/event_window_hydrology_series_2018_2024.csv`
  - `docs/event_window_hydrology_summary_2018_2024.csv`
  - optional compact failure/retry table if useful
- if the full run is not launched because STAC remains unavailable:
  - a clear blocker state in the report and manifest, with exact probe
    evidence, no simulated success rows
- minimal script/config/test changes required for retry/backoff and remote
  full-window execution
- updates to `docs/source_evidence_register.md`,
  `docs/data_stream_register.md`, `docs/decision_log.md`, `docs/README.md`,
  and this goal's `Log.md`

Use ignored local/remote paths such as:

```text
data/scratch/goal009/
artifacts/remote_full_window_hydrology/raw/
artifacts/remote_full_window_hydrology/intermediate/
artifacts/remote_full_window_hydrology/output/
/data/codex/repos/nomadic_waterbirds_goal009/
/data/codex/scratch/nomadic_waterbirds_goal009/
/data/codex/artifacts/nomadic_waterbirds_goal009/
```

Do not force these exact paths if the `nectar` docs or Goal 008 remote state
make another `/data/codex` layout cleaner. Record the chosen paths.

## Support Set And Event Window

Use the existing reviewed support set from Goal 007:

- five parent Ramsar supports
- four official Ramsar component subunits
- two Currawinya DEA Waterbodies open-water supports linked to DIWA named
  geometry evidence

Do not add Narran named subunit rows to the hydrology run. Goal 008 confirmed
they remain unresolved.

Run:

```text
2018-01 through 2024-12 inclusive
```

Expected successful row count:

```text
11 supports x 84 months = 924 rows
```

Rows may be retained as failed or blocked only for well-classified per-row
read failures after retry. If the whole STAC endpoint is unavailable, stop with
a blocker memo rather than writing a full table of endpoint-outage rows.

## STAC And COG Resilience Rules

Implement or configure:

- finite retry count
- exponential backoff or bounded increasing delay
- jitter if straightforward
- clear distinction between transient endpoint failures, no-item results,
  per-asset read failures, and deterministic geometry/config failures
- logged attempt counts and final status
- no infinite loops
- no hidden sleeps longer than the goal can account for

For live endpoint availability, probe at least:

- one early dry/window month
- one 2022 wet/flood month
- one recent post-wet month

Probe from both Mac mini and `deep-server-ts` if practical. If both still show
service-wide `503`, do not launch the full run.

## Remote Compute Rules

This goal explicitly authorises remote work on `deep-server-ts`.

Use the Mac mini as control plane. Use `deep-server-ts` as the remote execution
host unless the `nectar` docs identify a better current path.

Preferred source staging:

- use GitHub on remote if already configured
- otherwise use the Goal 008 `.git` plus `git ls-files --cached --others
  --exclude-standard` rsync pattern from the Mac mini

Do not spend the goal configuring permanent GitHub SSH on `deep-server` unless
it is trivial and non-invasive. The documented rsync/bundle path is acceptable.

Remote outputs should stay under `/data/codex` while the run is active. Bring
back only small reviewable CSV/JSON/Markdown/log artefacts to the project repo.

## Scientific Guardrails

- This goal produces hydrology-support evidence only.
- Do not make ecological claims from the full-window run.
- Preserve quality-fail, per-row read-failure, and missingness evidence.
- Treat the 2018-2024 output as an event-window prototype, not full historical
  inference.
- Do not let retry/backoff hide persistent endpoint failure.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- raw/staging paths confirmed ignored before use
- focused retry/backoff tests pass
- all existing local tests pass
- remote tests pass on `deep-server-ts` if the remote path is reachable
- JSON manifests parse with `python3 -m json.tool`
- CSV outputs parse and, if full run succeeds, confirm:
  - 11 supports
  - 84 months from `2018-01` to `2024-12`
  - 924 expected rows
  - required Goal 007 time-history fields present
  - status and quality counts are summarised
- if full run is blocked, manifest records exact endpoint/host/probe evidence
  and no fake full-window rows are written
- no committed files exceed 5 MB
- no committed raw source-data extensions are present
- local Markdown links in new/edited docs resolve
- unfinished-marker scan finds no unresolved stub language

If validation passes, commit and push the Goal 009 package to `main`.

## Checkpoint Rules

Update `Log.md` when:

- starting state is confirmed
- `nectar` docs and Goal 008 remote evidence have been read
- local and remote staging paths are confirmed
- retry/backoff implementation and tests are complete
- STAC availability probes are complete
- remote source staging is complete
- remote full-window run starts, finishes, or is blocked
- reports/manifests/summaries are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- add retry/backoff and transient-failure classification to the hydrology code
- add minimal settings/tests for the full-window remote run
- use `deep-server-ts` and `/data/codex` remote paths
- use rsync/bundle source staging from the Mac mini if remote GitHub SSH is not
  configured
- run the full 2018-2024 remote hydrology event window if STAC probes recover
- commit and push validated scripts, docs, manifests, tests, and small outputs

Pause and ask Barry before:

- requesting/downloading biodiversity data
- changing support definitions
- adding paid/cloud resources or launching Nectar/Alien/kunanyi
- configuring broad machine-level credentials
- committing raw source data or bulky outputs
- making ecological interpretation claims

## Stop Conditions

Stop when one of these is true:

- full 2018-2024 remote event-window hydrology is validated, committed, and
  pushed
- STAC remains unavailable after bounded retry probes and a blocker package is
  validated, committed, and pushed
- `deep-server-ts` becomes unreachable or unsuitable and the blocker package
  records exact evidence
- the work would require biodiversity data, support-definition changes, full
  historical extraction, production scheduler use, or remote-system
  administration outside this goal

## Final Response Requirements

Report:

- what changed
- retry/backoff behaviour implemented
- local and remote STAC probe outcomes
- `deep-server-ts` source-staging and run path
- whether the full `2018-01` to `2024-12` run completed
- row/support/month/status/quality counts if completed
- blocker evidence if not completed
- raw/remote staging paths and cleanup or continuation status
- validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual risks
- recommended Goal 010
