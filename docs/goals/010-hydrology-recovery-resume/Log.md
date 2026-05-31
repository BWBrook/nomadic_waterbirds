# Goal 010 Log - Hydrology Recovery Preflight And Conditional Resume

## Supervisor Preparation

- 2026-05-31: Supervisor reviewed Goal 009 outputs and verified the action
  repo was clean and synced at `0be991c` (`Run Goal 009 remote hydrology
  scale-up`).
- 2026-05-31: Supervisor verified Goal 009 output shape: 924 rows, 11
  supports, 84 months, with 145 computed rows and 779 classified
  `transient_endpoint_failure` blocked rows.
- 2026-05-31: Supervisor ran focused local Goal 009 retry tests
  (`python3 -m unittest tests.test_goal009_stac_resilience`) and parsed both
  Goal 009 JSON manifests successfully.
- 2026-05-31: Supervisor archived the GPT-5.5 Pro traceable literature-mining
  report in `docs/literature/` as a separate checkpoint at `de7de89`. Goal 010
  should not modify literature files.
- 2026-05-31: Goal package written for publication into the action repo under
  `docs/goals/010-hydrology-recovery-resume/`.

## Executor Checkpoints

`nomad` should update this log during execution.

- 2026-05-31: Executor confirmed a clean `main` checkout synced with
  `origin/main` at `ba0d69e` (`Add Goal 010 hydrology recovery brief`), which
  is beyond the required `de7de89` checkpoint.
- 2026-05-31: Read Goal 010 `Goal.md`, `Plan.md`, and `Runbook.md`; re-read
  repo/global AGENTS instructions, required `nectar` control-plane docs, and
  Goal 009 reports/manifests/output summaries.
- 2026-05-31: Confirmed ignored staging coverage for `data/scratch/goal010/`,
  `artifacts/hydrology_recovery_010/`, and the existing
  `artifacts/remote_full_window_hydrology/` paths.
- 2026-05-31: Rechecked Goal 009 shape: 924 rows, 11 supports, 84 months
  (`2018-01` to `2024-12`), 145 computed rows, and 779 blocked rows. Blocked
  rows span 10 supports and all years from 2018 through 2024.
- 2026-05-31: Baseline local tests passed before Goal 010 edits:
  `python3 -m unittest discover -s tests -p 'test*.py'` (12 tests).
- 2026-05-31: Added offline Goal 010 preflight tests for blocked-row sample
  selection and recovery launch/stop decisions. Red check failed because
  `scripts/stac_recovery_preflight_010.py` did not exist; green check passed
  with `python3 -m unittest tests.test_goal010_recovery_preflight` (4 tests).
- 2026-05-31: Added `scripts/stac_recovery_preflight_010.py`,
  `settings/hydrology_recovery_010.json`, and
  `scripts/hydrology_recovery_010.py` so Goal 010 can preflight blocked rows
  and, if warranted, produce versioned recovery outputs without overwriting
  Goal 009 files.
- 2026-05-31: Built a deterministic 33-row blocked-row preflight sample from
  Goal 009 output. It covers all 10 supports with blocked rows and includes
  early, wet/flood, and recent periods.
- 2026-05-31: Ran the local Mac mini Goal 010 endpoint probe with
  `python3 scripts/stac_resilience_probe_009.py --config
  settings/hydrology_recovery_010.json --host-label mac-mini-goal010
  --output artifacts/hydrology_recovery_010/output/stac_probe_macmini_010.json`.
  DEA STAC returned `HTTP 503` for `2018-01`, `2022-11`, and `2024-12` after
  three attempts each, yielding `endpoint_status=service_unavailable_503`.
- 2026-05-31: Confirmed `deep-server-ts` remote facts: host `deep-server`,
  64 logical CPUs, 125 GiB RAM, 4.5 TiB free on `/data`, Python 3.12.3,
  GDAL 3.8.4, and Git 2.43.0.
- 2026-05-31: Staged source to
  `/data/codex/repos/nomadic_waterbirds_goal010` using the Goal 008/009 rsync
  pattern. Remote `python3 -m py_compile ...` passed for changed scripts, and
  remote `python3 -m unittest discover -s tests -p "test*.py"` passed
  (16 tests).
- 2026-05-31: Ran the `deep-server-ts` Goal 010 endpoint probe with
  `python3 scripts/stac_resilience_probe_009.py --config
  settings/hydrology_recovery_010.json --host-label deep-server-ts-goal010
  --output artifacts/hydrology_recovery_010/output/stac_probe_deep_server_ts_010.json`.
  The endpoint remained unstable: `2018-01` and `2024-12` returned features
  only after three attempts following read timeouts, while `2022-11` exhausted
  all three attempts with read timeouts. Probe status was
  `transient_endpoint_failure`.
- 2026-05-31: Stopped before blocked-row computation or full recovery launch
  because endpoint probes failed the service-stability gate. The 33 selected
  blocked sample rows were recorded with status
  `not_run_endpoint_probe_unavailable` in
  `docs/stac_recovery_010_manifest.json`; no fake recovery CSV was written.
- 2026-05-31: Drafted `docs/stac_recovery_010_report.md` and
  `docs/stac_recovery_010_manifest.json`, and updated the docs index, source
  evidence register, data stream register, and decision log.
- 2026-05-31: Validation passed before commit: changed-script
  `python3 -m py_compile`; focused Goal 010 tests (4 tests); full local suite
  (16 tests); JSON parse for Goal 010 manifest/config; blocker-manifest check;
  no recovery CSV present; Goal 009 source CSV shape still 11 supports, 84
  months, and 924 rows; `git diff --check`; ignored-path check; local Markdown
  link check; unfinished-marker scan; committed-size check; and committed
  raw-extension check.
