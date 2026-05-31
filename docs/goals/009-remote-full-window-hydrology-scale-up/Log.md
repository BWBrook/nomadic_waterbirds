# Goal 009 Log - Remote Full-Window Hydrology Scale-Up

## Supervisor Preparation

- 2026-05-31: Supervisor reviewed Goal 008 outputs and confirmed the action
  repo was clean and synced at `26ed2d3` (`Correct Goal 008 validation
  evidence`).
- 2026-05-31: Supervisor verified the Goal 008 Narran crosswalk shape:
  44 rows, including one parent support, four unresolved named/context
  candidates, and 39 DEA parent-overlap screens. Narran remains parent-only
  for event-window hydrology.
- 2026-05-31: Supervisor reviewed the Goal 008 compute memo and remote
  rehearsal. `deep-server-ts` is viable for hydrology scale-up, while direct
  `deep-server` timed out and remote GitHub SSH was unavailable.
- 2026-05-31: Supervisor noted the true blocker was upstream DEA STAC
  `HTTP 503` responses reproduced from both remote and local probes.
- 2026-05-31: Lab-leader note emphasised that remote/HPC goals should direct
  action agents to read `/Users/bwbrook/work/nectar` carefully. Goal 009
  therefore requires the relevant `nectar` workflow and machine docs before
  remote work.
- 2026-05-31: Goal package written for publication into the action repo under
  `docs/goals/009-remote-full-window-hydrology-scale-up/`.

## Executor Checkpoints

`nomad` should update this log during execution.

- 2026-05-31: Executor confirmed a normal `main` checkout with
  `main...origin/main`, no submodule/worktree indirection, and HEAD at
  `821cd64` (`Add Goal 009 remote hydrology scale-up brief`), which is beyond
  the required Goal 008 checkpoint.
- 2026-05-31: Read Goal 009 `Goal.md`, `Plan.md`, and `Runbook.md`; rechecked
  the required AGENTS and `nectar` control-plane docs from the packet. The
  selected compute path remains Mac mini control plane plus `deep-server-ts`
  under `/data/codex`.
- 2026-05-31: Verified local ignored staging coverage for
  `data/scratch/goal009/` and
  `artifacts/remote_full_window_hydrology/{raw,intermediate,output}/`.
- 2026-05-31: Added focused offline retry/classification tests in
  `tests/test_goal009_stac_resilience.py`. Red check failed first because the
  retry/classification API was absent; green check then passed with
  `python3 -m unittest tests.test_goal009_stac_resilience` (5 tests).
- 2026-05-31: Added bounded retry/backoff and transient-failure classification
  for DEA STAC searches and remote COG reads, with retry audit events exposed
  in manifests. The full local suite passed:
  `python3 -m unittest discover -s tests -p 'test*.py'` (12 tests).
- 2026-05-31: Created Goal 009 full-window config and wrapper entrypoint so a
  successful run writes `docs/event_window_hydrology_series_2018_2024.csv`,
  `docs/event_window_hydrology_summary_2018_2024.csv`, and
  `docs/remote_full_window_hydrology_009_manifest.json` without overwriting the
  Goal 007 fallback outputs.
- 2026-05-31: Ran the Mac mini STAC availability probe with
  `python3 scripts/stac_resilience_probe_009.py --host-label mac-mini
  --output artifacts/remote_full_window_hydrology/output/stac_probe_macmini_009.json`.
  DEA STAC was available for `2018-01`, `2022-11`, and `2024-12`; `2022-11`
  needed one retry after a transient read timeout and then returned 15
  features.
- 2026-05-31: Confirmed `deep-server-ts` remote facts: host `deep-server`,
  64 logical CPUs, 125 GiB RAM, 4.5 TiB free on `/data`, Python 3.12.3,
  GDAL 3.8.4, and Git 2.43.0.
- 2026-05-31: Staged source to
  `/data/codex/repos/nomadic_waterbirds_goal009` using the Goal 008 rsync
  pattern (`.git` plus `git ls-files --cached --others --exclude-standard`).
  Remote `python3 -m py_compile ...` passed for changed scripts, and remote
  `python3 -m unittest discover -s tests -p "test*.py"` passed (12 tests).
- 2026-05-31: Ran the `deep-server-ts` STAC availability probe with
  `python3 scripts/stac_resilience_probe_009.py --host-label deep-server-ts
  --output artifacts/remote_full_window_hydrology/output/stac_probe_deep_server_ts_009.json`.
  DEA STAC was available for `2018-01`, `2022-11`, and `2024-12` on first
  attempt.
- 2026-05-31: Launched full remote event-window hydrology with
  `python3 scripts/remote_full_window_hydrology_009.py`. The run completed in
  8089.7 seconds and wrote 924 support-month rows, covering 11 supports and
  84 months from `2018-01` to `2024-12`.
- 2026-05-31: Retrieved only small review outputs to the local repo:
  `docs/event_window_hydrology_series_2018_2024.csv`,
  `docs/event_window_hydrology_summary_2018_2024.csv`, and
  `docs/remote_full_window_hydrology_009_manifest.json`. Remote raw and
  intermediate files remain under ignored `/data/codex` project artifact
  paths.
- 2026-05-31: Audited full-run status counts: 145 rows computed and 779 rows
  retained as classified `transient_endpoint_failure` blocked rows after
  bounded retry. Added `docs/remote_full_window_hydrology_009_retry_summary.csv`
  to keep the per-support blocked/computed status reviewable.
- 2026-05-31: Validation passed before commit: `git diff --check`;
  `python3 -m py_compile` on changed scripts; focused Goal 009 tests
  (5 tests); full local suite (12 tests); JSON parse for Goal 009 manifests
  and config; full-window CSV shape check (11 supports, 84 months, 924 rows,
  required time-history fields); local Markdown link check; ignored-path check;
  staged/tracked size checks below 5 MB; staged/tracked raw-extension checks;
  and stub scan with no hits.
