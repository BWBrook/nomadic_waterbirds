# Goal 004 Log - Hydrology-Only Extraction Smoke Test

## Supervisor Preparation

- 2026-05-30: Supervisor reviewed Goal 003 outputs, verified action repo state,
  parsed the crosswalk CSV, and spot-checked high-leverage official sources.
- 2026-05-30: Supervisor incorporated Barry's reminder about available
  remote/HPC resources into the next goal as an explicit compute-routing gate.
- 2026-05-30: Goal package written for publication into the action repo under
  `docs/goals/004-hydrology-extraction-smoke-test/`.

## Executor Checkpoints

`nomad` should update this log during execution.

- 2026-05-30: Executor started Goal 004 from
  `/Users/bwbrook/papers/nomadic_waterbirds`; confirmed clean `main` tracking
  `origin/main`, latest commit `376ff11` (`Add Goal 004 hydrology smoke
  brief`), and current tree containing Goal 001-003 outputs plus the Goal 004
  packet. Read `AGENTS.md`, `/Users/bwbrook/.codex/AGENTS.md`, Goal 004
  `Goal.md`, `Plan.md`, `Runbook.md`, and the Goal 003 crosswalk/spec docs.
- 2026-05-30: Chose a local Mac mini smoke test rather than remote/HPC: the
  intended workflow is a tiny STAC search and 3x3-pixel GDAL read per
  candidate/month, well below the 2 GB, 500 MB/file, 45 minute, and 12 GB
  memory routing thresholds.
- 2026-05-30: Confirmed raw staging paths are ignored by `.gitignore`:
  `data/scratch/goal004/`, `artifacts/hydrology_smoke/raw/`,
  `artifacts/hydrology_smoke/intermediate/`, and
  `artifacts/hydrology_smoke/output/`.
- 2026-05-30: Added minimal executable workflow:
  `scripts/hydrology_smoke_test_004.py` and
  `settings/hydrology_smoke_test_004.json`; syntax/config checks passed with
  `python3 -m py_compile` and `python3 -m json.tool`.
- 2026-05-30: First smoke run succeeded for all five candidates and all three
  target months with 15 summary rows. Initial item selection exposed invalid
  scenes for some tiny probes, so the script was tightened to choose the
  clearest readable scene from the small STAC item set.
- 2026-05-30: Final smoke run succeeded locally with 15
  `computed_tiny_probe_metrics` rows and 15 `quality_high` rows. No raw source
  files were downloaded; ignored staging directories remained empty.
- 2026-05-30: Drafted `docs/hydrology_smoke_test_report.md`,
  `docs/hydrology_smoke_test_manifest.json`, and
  `docs/hydrology_smoke_test_summary.csv`; updated `docs/data_stream_register.md`,
  `docs/decision_log.md`, and `docs/README.md`.
- 2026-05-30: Validation checkpoint completed before commit: `git diff
  --check` passed; `python3 -m py_compile` passed for
  `scripts/hydrology_smoke_test_004.py`; `python3 -m json.tool` passed for
  settings and manifest JSON; summary CSV parsed with 15 rows across all five
  required candidates; size check found no tracked/to-be-tracked files over 5
  MB; raw-extension check found no tracked/to-be-tracked source data files;
  targeted unfinished-language scan found no matches in new or edited Goal 004
  files; local Markdown link check resolved 41 local links; ignored scratch
  directories were empty.
- 2026-05-30: Hydrology smoke-test package committed as `a248515` (`Run
  hydrology extraction smoke test`) and pushed to `origin/main`.
