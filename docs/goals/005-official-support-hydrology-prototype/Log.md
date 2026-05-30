# Goal 005 Log - Official-Support Hydrology Prototype

## Supervisor Preparation

- 2026-05-30: Supervisor reviewed Goal 004 outputs and confirmed the action
  repo was clean and synced at `589af6a` (`Record Goal 004 publication
  checkpoint`).
- 2026-05-30: Supervisor verified the Goal 004 manifest and summary agree on
  15 computed tiny-probe rows, all five candidates, all three target months,
  empty raw staging, and local Mac execution.
- 2026-05-30: Supervisor framed Goal 005 as an evidence-level transition from
  3x3 product-access probes to documented official support geometry and
  monthly real-support hydrology metrics.
- 2026-05-30: Goal package written for publication into the action repo under
  `docs/goals/005-official-support-hydrology-prototype/`.

## Executor Checkpoints

`nomad` should update this log during execution.

- 2026-05-30: Executor started Goal 005 from
  `/Users/bwbrook/papers/nomadic_waterbirds`; confirmed clean `main` tracking
  `origin/main`, latest commit `d157862` (`Add Goal 005 official support
  hydrology brief`), and repo state at or beyond Goal 004 checkpoint
  `589af6a`.
- 2026-05-30: Read `AGENTS.md`, `/Users/bwbrook/.codex/AGENTS.md`, Goal 005
  `Goal.md`, `Plan.md`, `Runbook.md`, and the Goal 004/crosswalk/hydrology
  source docs. Chose local Mac mini execution because the intended workflow is
  a bounded five-candidate Ramsar geometry query plus monthly Water
  Observations reads, below the Goal 005 data, runtime, and memory thresholds.
- 2026-05-30: Confirmed no-commit raw staging policy and verified ignored
  staging paths with `git check-ignore`: `data/scratch/goal005/`,
  `artifacts/hydrology_supports/raw/`,
  `artifacts/hydrology_supports/intermediate/`,
  `artifacts/hydrology_supports/output/`,
  `artifacts/hydrology_real_support/raw/`,
  `artifacts/hydrology_real_support/intermediate/`, and
  `artifacts/hydrology_real_support/output/`.
- 2026-05-30: Selected the DCCEEW Geospatial Ramsar Wetlands ArcGIS service as
  the official named-complex support path for the five candidates. Live service
  checks found matching Ramsar records for Macquarie Marshes, Narran Lake
  Nature Reserve, Gwydir Wetlands, Kerang Wetlands, and Currawinya Lakes.
- 2026-05-30: Added a focused unit test for monthly Water Observations
  support-mask aggregation and confirmed it fails before the Goal 005 script
  exists (`FileNotFoundError` for `scripts/official_support_hydrology_005.py`).
- 2026-05-30: Added `scripts/official_support_hydrology_005.py` and
  `settings/official_support_hydrology_005.json`; the focused monthly
  aggregation unit test now passes, and script/config syntax checks pass.
- 2026-05-30: First official support staging succeeded: the DCCEEW Ramsar
  service subset for the five candidates was written only to ignored
  `artifacts/hydrology_supports/raw/ramsar_goal005_subset.geojson` (488K).
- 2026-05-30: First real-support hydrology row computed for official Ramsar
  support geometry. Final local prototype run completed in 72.884 seconds with
  15 `computed_real_support_metrics` rows for all five candidates and all
  three Goal 004 months.
- 2026-05-30: All five candidates now have geometry/status rows in
  `docs/official_support_geometry_summary.csv`; all hydrology rows use
  Ramsar support IDs rather than Goal 004 `*_probe_3x3` supports.
- 2026-05-30: Drafted Goal 005 reports and provenance outputs:
  `docs/official_support_geometry_report.md`,
  `docs/official_support_geometry_manifest.json`,
  `docs/official_support_geometry_summary.csv`,
  `docs/real_support_hydrology_prototype_report.md`,
  `docs/real_support_hydrology_prototype_manifest.json`, and
  `docs/real_support_hydrology_prototype_summary.csv`; updated
  `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, and `docs/README.md`.
- 2026-05-30: Validation complete. Fresh `python3
  scripts/official_support_hydrology_005.py` rerun produced 15
  `computed_real_support_metrics` rows and restaged only the ignored 497145
  byte Ramsar subset. `git diff --check`, script/config/manifest JSON parsing,
  `python3 -m py_compile`, `python3 -m unittest`, CSV shape checks, raw
  extension checks, file-size checks, stub-language scan, and local Markdown
  link checks all passed.
- 2026-05-30: Temporary-tree reproducibility check copied only unignored files
  to `/tmp`, reran `python3 scripts/official_support_hydrology_005.py`, and
  rebuilt the same 15-row computed hydrology package plus a 497145 byte ignored
  Ramsar raw subset.
- 2026-05-30: Committed and pushed the validated Goal 005 package to
  `origin/main` as `196ce72` (`Prototype official-support hydrology
  extraction`).
