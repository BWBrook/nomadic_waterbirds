# Goal 007 Log - Named Subunit Evidence And Event-Window Hydrology Series

## Supervisor Preparation

- 2026-05-30: Supervisor reviewed Goal 006 outputs and confirmed the action
  repo was clean and synced at `2c1ee61` (`Record Goal 006 publication
  checkpoint`).
- 2026-05-30: Supervisor verified the Goal 006 registry and hydrology summaries
  parse cleanly: 36 registry rows, all five parent supports represented, 22
  Ramsar component rows, 14 DEA Waterbodies overlap rows, six selected subunits,
  and 18 computed subunit-month rows.
- 2026-05-30: Supervisor ran `python3 -m unittest discover -s tests -p
  'test*.py'`; both focused tests passed.
- 2026-05-30: Supervisor framed Goal 007 as the next hydrology-only step:
  strengthen weak named-subunit evidence and run a bounded monthly event-window
  series to exercise lag, novelty, drying, and hydroperiod metrics.
- 2026-05-30: Goal package written for publication into the action repo under
  `docs/goals/007-named-subunit-evidence-event-series/`.

## Executor Checkpoints

`nomad` should update this log during execution.

- 2026-05-30: Executor started Goal 007 from
  `/Users/bwbrook/papers/nomadic_waterbirds`; confirmed clean `main` tracking
  `origin/main`, latest commit `0e669d6` (`Add Goal 007 event-window
  hydrology brief`), and repo state at or beyond Goal 006 checkpoint
  `2c1ee61`.
- 2026-05-30: Read `AGENTS.md`, `/Users/bwbrook/.codex/AGENTS.md`, Goal 007
  `Goal.md`, `Plan.md`, `Runbook.md`, and the Goal 006 registry/hydrology
  reports, manifests, and CSV outputs. Chose local Mac mini execution unless
  a timed probe shows the default event window breaches Goal 007 thresholds.
- 2026-05-30: Confirmed no-commit raw staging policy and verified ignored
  staging paths with `git check-ignore`: `data/scratch/goal007/`,
  `artifacts/event_window_hydrology/raw/`,
  `artifacts/event_window_hydrology/intermediate/`,
  `artifacts/event_window_hydrology/output/`, and
  `artifacts/named_subunit_evidence/raw/`.
- 2026-05-30: Added a focused time-history metric unit test for lag,
  trailing wetness, novelty after dry months, consecutive wet/dry counts, and
  drying velocity; confirmed the test fails before
  `scripts/event_window_hydrology_007.py` exists.
- 2026-05-30: Implemented initial Goal 007 script/config and confirmed the
  focused time-history test plus all existing tests pass. A default
  `2018-01` through `2024-12` run was started, but the first support took
  roughly ten minutes before the run reached support 2, making the 13-support
  local run likely to challenge the two-hour Goal 007 threshold. Stopped the
  probe and switched to a documented `2020-01` through `2024-12` fallback
  window that still supports lag, novelty, drying, cumulative, and consecutive
  wet/dry metrics.
- 2026-05-30: Named-subunit source checks completed. Narran Clear Lake and
  Back Lake were retained as named-but-unresolved rows because no separate
  vector geometry or DEA UID relationship was verified. Currawinya
  WetlandInfo DIWA KMZs were staged under ignored
  `artifacts/named_subunit_evidence/raw/` and linked Lake Numalla Aggregation
  to DEA UID `r4yss38r6_v3` and Lake Wyara to DEA UID `r4ysdndx8_v3` by
  overlap evidence.
- 2026-05-30: Drafted `docs/named_subunit_crosswalk.csv` with 15 rows:
  11 supports included in the fallback event-window hydrology series and 4
  retained evidence-only/unresolved rows.
- 2026-05-30: Ran `python3 scripts/event_window_hydrology_007.py` for the
  `2020-01` through `2024-12` fallback window. First and complete
  event-window rows were computed; output contains 660 support-month rows
  across 11 supports and 60 months, with 659 `computed_event_window_metrics`
  rows and one retained `blocked_event_window_processing_error` row caused by
  a read timeout for `nwb004_ramsar_ref265` in `2023-01`.
- 2026-05-30: Derived time-history metrics were added to every
  event-window row, including 1-month and 3-month lags, trailing 3-month
  wetness, wetting deltas, novelty after dry periods, cumulative 12-month wet
  counts, consecutive wet/dry counts, and drying velocities.
- 2026-05-30: Drafted
  `docs/named_subunit_evidence_report.md`,
  `docs/event_window_hydrology_series_report.md`,
  `docs/named_subunit_evidence_manifest.json`,
  `docs/event_window_hydrology_series_manifest.json`,
  `docs/event_window_hydrology_series.csv`, and
  `docs/event_window_hydrology_summary.csv`. Updated
  `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, and `docs/README.md` with Goal 007 evidence and
  navigation.
- 2026-05-30: Validation checks passed for `git diff --check`, script/config
  syntax, both manifest JSON files, all CSV shape/month/support gates,
  unignored file-size and raw-extension hygiene, unfinished-marker scan,
  local Markdown link checks, and `python3 -m unittest discover -s tests -p
  'test*.py'`.
- 2026-05-30: Temporary-tree reproducibility check copied only unignored files
  to `/tmp`, reran `python3 scripts/event_window_hydrology_007.py`, and
  rebuilt the Goal 007 support set with 11 supports, 60 months, 660 rows, two
  unresolved named supports, and 47008464 bytes of ignored staged source
  files. The temp run returned 660 computed rows, indicating the committed
  Kerang `2023-01` timeout row is a live read variability artefact rather than
  a structural workflow failure.
- 2026-05-30: Validation completed successfully with `rg --files`,
  `python3 -m unittest discover -s tests -p 'test*.py'`, syntax/config checks,
  JSON parsing for the Goal 007 config and both manifests, CSV shape checks for
  15 crosswalk rows, 11 included supports, 60 event-window months, 660 series
  rows, required derived metric fields, and matching summary rows,
  `git diff --check`, ignored-path checks, tracked/candidate file-size and
  raw-extension checks, unresolved-stub scan, local Markdown link check, and a
  clean temporary-tree reproduction run. The reproduction rebuilt 15 crosswalk
  rows and 660 event-window rows from fresh ignored staging; all 660 rows
  computed in that run, confirming the working-tree timeout row is a transient
  read issue rather than a deterministic geometry/config blocker.
- 2026-05-30: Committed and pushed the validated Goal 007 package to `main` as
  `111640f` (`Build event-window hydrology series`).
