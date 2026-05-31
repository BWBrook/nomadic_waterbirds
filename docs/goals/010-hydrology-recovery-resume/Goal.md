# Goal: Hydrology Recovery Preflight And Conditional Resume

## Objective

Determine whether DEA STAC and remote COG access are stable enough to recover
the `2018-01` through `2024-12` full-window hydrology table, then either resume
or rerun the Goal 009 blocked rows on `deep-server-ts` or stop with a clear
service-stability blocker package.

## Why This Matters

Goal 009 succeeded as remote-compute and retry/provenance evidence, but not as
a usable full-window hydrology evidence table:

- 11 supports x 84 months = 924 expected rows
- 145 rows computed
- 779 rows retained as classified `transient_endpoint_failure` blocked rows
- the output is not suitable for ecological interpretation

The next step is not biodiversity linkage. The project first needs to know
whether the full-window hydrology table can be recovered under stable service
conditions, or whether the analysis plan must wait, change access strategy, or
use a different hydrology acquisition route.

## Operating Mode

Remote compute recovery; hydrology-only; service-stability preflight;
conditional resume/rerun; no ecological interpretation.

## Scope

In scope:

- read the repo instructions, Goal 009 reports/manifests, and required
  `nectar` compute guidance
- verify the current local repo is clean and at or beyond `de7de89`
  (`Archive traceable literature mining report`)
- use Goal 009 outputs to identify blocked support/month rows
- probe DEA STAC and representative blocked rows before launching a large
  recovery run
- use `deep-server-ts` and `/data/codex` as the target execution path if
  service-stability criteria are met
- recover the full-window table by resuming blocked rows, or rerun all rows if
  that is simpler and safer, while preserving Goal 009 outputs
- write versioned Goal 010 outputs rather than overwriting Goal 009 files
- update project docs, registers, decision log, and this goal log
- commit and push the validated package to `main`

Out of scope:

- biodiversity data requests, downloads, or modelling
- eBird, Birdata, ALA, or EAWS extraction
- changing wetland/support definitions
- adding Narran named subunit hydrology
- manual literature verification or bibliography work
- full historical extraction back to 1986
- changing the central manuscript thesis
- ecological interpretation of wetness, refuge status, breeding, abundance, or
  nomadic response
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
- `docs/stac_resilience_009_report.md`
- `docs/stac_resilience_009_manifest.json`
- `docs/remote_full_window_hydrology_009_report.md`
- `docs/remote_full_window_hydrology_009_manifest.json`
- `docs/event_window_hydrology_series_2018_2024.csv`
- `docs/event_window_hydrology_summary_2018_2024.csv`
- `docs/remote_full_window_hydrology_009_retry_summary.csv`
- `settings/remote_full_window_hydrology_009.json`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `de7de89`.
- Inspect available files with `rg --files`.
- Confirm local and remote staging paths are ignored before use.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Service-Stability Preflight

Before launching a full recovery run, create a preflight over Goal 009 blocked
rows.

Minimum preflight:

- repeat the Goal 009 endpoint probes from both Mac mini and `deep-server-ts`
- select a representative blocked-row sample from
  `docs/event_window_hydrology_series_2018_2024.csv`
- cover all supports if possible, multiple years, and at least one month from
  each of early, wet/flood, and recent periods
- record per-row status, attempt counts, elapsed time, and failure class

Suggested sample size: 24 to 44 blocked support/month rows.

Proceed to full recovery only if:

- the endpoint probes do not show service-wide outage, and
- at least 80 percent of the representative blocked-row sample computes, and
- failures do not cluster in a way that would make the full recovery output
  scientifically unreviewable.

If the sample still shows widespread `transient_endpoint_failure`, stop with a
blocker package. Do not rerun all 779 blocked rows just to confirm the same
service failure at larger cost.

## Recovery Run

If preflight passes, recover the table on `deep-server-ts`.

Preferred strategy:

- preserve the 145 computed Goal 009 rows
- rerun the 779 Goal 009 blocked rows
- merge recovered rows with preserved computed rows into Goal 010 output files

Acceptable alternative:

- rerun all 924 support/month rows if that is simpler, safer, or more
  reproducible

Do not overwrite Goal 009 outputs. Use Goal 010-specific file names.

Expected output names:

- `docs/stac_recovery_010_report.md`
- `docs/stac_recovery_010_manifest.json`
- `docs/event_window_hydrology_series_2018_2024_recovery010.csv`
- `docs/event_window_hydrology_summary_2018_2024_recovery010.csv`
- `docs/remote_full_window_hydrology_010_retry_summary.csv`

If recovery is not launched, still produce:

- `docs/stac_recovery_010_report.md`
- `docs/stac_recovery_010_manifest.json`

The report and manifest must distinguish:

- service-wide outage
- transient endpoint failure
- transient asset/COG read failure
- no-data month
- deterministic geometry/config/code error
- successful computed row

## Remote Compute Rules

This goal explicitly authorises remote work on `deep-server-ts`.

Use the Mac mini as control plane. Use `/data/codex` for remote working state.
Use the established Goal 008/009 source-staging pattern unless GitHub access on
remote is already working cleanly.

Suggested remote paths:

```text
/data/codex/repos/nomadic_waterbirds_goal010/
/data/codex/scratch/nomadic_waterbirds_goal010/
/data/codex/artifacts/nomadic_waterbirds_goal010/
```

Bring back only small CSV/JSON/Markdown/log artefacts to the local repo.

## Scientific Guardrails

- This goal produces hydrology recovery evidence only.
- Goal 010 outputs are not ecological interpretation by themselves.
- Preserve failed and blocked rows with explicit status rather than filtering
  them away.
- A recovered table becomes a candidate hydrology evidence table only if
  support/month coverage is high enough to review scientifically.
- If large gaps remain, recommend the next action as service retry, alternate
  acquisition strategy, or revised hydrology scope. Do not silently narrow the
  science.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- raw/staging paths confirmed ignored before use
- focused retry/resume/preflight tests pass if code changes are made
- all existing local tests pass
- remote tests pass on `deep-server-ts` if the remote path is reachable
- JSON manifests parse with `python3 -m json.tool`
- CSV outputs parse
- if recovery output is produced, confirm:
  - 11 supports
  - 84 months from `2018-01` to `2024-12`
  - 924 expected rows
  - required Goal 007 time-history fields present
  - status and quality counts are summarised
  - preserved-versus-recovered rows are distinguishable
- if recovery is blocked, manifest records exact endpoint/host/sample evidence
  and no fake recovery table is written
- no committed files exceed 5 MB
- no committed raw source-data extensions are present
- local Markdown links in new/edited docs resolve
- unfinished-marker scan finds no unresolved stub language

## Checkpoint Rules

Update `Log.md` when:

- starting state is confirmed
- required docs and Goal 009 evidence have been read
- local and remote staging paths are confirmed
- blocked rows are summarised
- preflight probes are complete
- decision to launch or stop is made
- remote source staging is complete, if used
- recovery run starts, finishes, or is blocked
- reports/manifests/summaries are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may decide:

- exact blocked-row sampling scheme if it covers the stability question
- whether to resume blocked rows or rerun all rows after preflight passes
- implementation details for preflight/resume scripts
- whether Goal 010 output is "candidate hydrology evidence" or only "recovery
  provenance", based on coverage and quality

Pause or stop with a blocker package before:

- changing support definitions
- using a different hydrology product or provider
- requesting biodiversity data
- making ecological or manuscript-result claims
- launching a longer or broader run than the 2018-2024 reviewed support set
- spending time on permanent remote infrastructure instead of the bounded
  recovery task

## Final Response Requirements

Report:

- commit SHA and push status
- endpoint and blocked-row preflight results
- whether full recovery was launched
- remote path and host facts
- output row/status/quality counts
- whether the output is candidate hydrology evidence or only blocker/recovery
  provenance
- validation commands and outcomes
- final git status
- residual risks
- recommended Goal 011
