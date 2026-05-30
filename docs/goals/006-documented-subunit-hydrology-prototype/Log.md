# Goal 006 Log - Documented Subunit Hydrology Prototype

## Supervisor Preparation

- 2026-05-30: Supervisor reviewed Goal 005 outputs and confirmed the action
  repo was clean and synced at `0834bc6` (`Polish Goal 005 validation log`).
- 2026-05-30: Supervisor verified the Goal 005 geometry and hydrology summaries
  parse cleanly, cover all five candidates, contain 15 real-support hydrology
  rows, and use Ramsar support IDs rather than Goal 004 probe supports.
- 2026-05-30: Supervisor spot-checked the DCCEEW Ramsar service for the five
  REFCODEs; the service returned 22 component records across the five parent
  supports, including 14 Kerang components.
- 2026-05-30: Supervisor framed Goal 006 as a parent-child subunit transition:
  Ramsar supports remain official parent anchors, but subunit-level
  heterogeneity must be documented before biodiversity linkage.
- 2026-05-30: Goal package written for publication into the action repo under
  `docs/goals/006-documented-subunit-hydrology-prototype/`.

## Executor Checkpoints

`nomad` should update this log during execution.

- 2026-05-30: Executor started Goal 006 from
  `/Users/bwbrook/papers/nomadic_waterbirds`; confirmed clean `main` tracking
  `origin/main`, latest commit `e352dc9` (`Add Goal 006 subunit hydrology
  brief`), and repo state at or beyond Goal 005 checkpoint `0834bc6`.
- 2026-05-30: Read `AGENTS.md`, `/Users/bwbrook/.codex/AGENTS.md`, Goal 006
  `Goal.md`, `Plan.md`, `Runbook.md`, and the Goal 005 geometry/hydrology
  outputs. Chose local Mac mini execution because the intended workflow is a
  bounded Ramsar component registry plus a small DEA Waterbodies overlap screen
  and selected subunit Water Observations metrics, below Goal 006 data,
  runtime, and memory thresholds.
- 2026-05-30: Confirmed no-commit raw staging policy and verified ignored
  staging paths with `git check-ignore`: `data/scratch/goal006/`,
  `artifacts/subunit_supports/raw/`,
  `artifacts/subunit_supports/intermediate/`,
  `artifacts/subunit_supports/output/`,
  `artifacts/subunit_hydrology/raw/`,
  `artifacts/subunit_hydrology/intermediate/`, and
  `artifacts/subunit_hydrology/output/`.
- 2026-05-30: Selected source paths: DCCEEW Ramsar service components for
  parent-child Ramsar subunits, DEA Waterbodies v3 public S3 shapefile ZIP for
  bounded open-water overlap screening, and DEA Water Observations STAC/COGs
  for monthly subunit metrics. The Waterbodies ZIP is about 46.5 MB, below
  local staging thresholds.
- 2026-05-30: Staged DEA Waterbodies v3 shapefile ZIP only under ignored
  `artifacts/subunit_supports/raw/ga_ls_wb_3_v3.zip` (46502008 bytes,
  SHA-256 `7f491f8487770ad237e7000ff5f3cb3b607e18abe1a0690d5ea4a6c2f3241450`).
  The zipped shapefile opens locally with 324890 features in `EPSG:3577`.
- 2026-05-30: Added a focused parent-child registry unit test and confirmed it
  fails before the Goal 006 script exists (`FileNotFoundError` for
  `scripts/subunit_hydrology_006.py`).
- 2026-05-30: Added `settings/subunit_hydrology_006.json`,
  `scripts/subunit_hydrology_006.py`, and
  `tests/test_goal006_subunit_registry.py`; the focused test now passes and
  verifies parent support preservation plus included/retained Ramsar component
  status.
- 2026-05-30: Ran the Goal 006 script locally. It refreshed the ignored Ramsar
  subset, reused the ignored DEA Waterbodies ZIP, built first parent-child
  registry rows, completed the DEA Waterbodies overlap screen, and wrote
  `docs/subunit_support_registry.csv`,
  `docs/subunit_support_registry_manifest.json`,
  `docs/subunit_hydrology_prototype_summary.csv`, and
  `docs/subunit_hydrology_prototype_manifest.json`.
- 2026-05-30: The registry covers all five parent candidates with 36 rows:
  22 Ramsar component rows and 14 DEA Waterbodies overlap rows. Six subunits
  are marked `included_for_subunit_hydrology`; the other 30 rows are retained
  for later review.
- 2026-05-30: First and complete subunit hydrology rows were computed. The run
  produced 18 selected subunit/month rows across `2019-01`, `2022-11`, and
  `2024-03`; all reached `computed_subunit_metrics`.
- 2026-05-30: Drafted
  `docs/subunit_support_registry_report.md` and
  `docs/subunit_hydrology_prototype_report.md`, and updated
  `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, and `docs/README.md` with Goal 006 evidence and
  navigation.
- 2026-05-30: Validation completed successfully with `rg --files`,
  `python3 scripts/subunit_hydrology_006.py`,
  `python3 -m unittest discover -s tests -p 'test*.py'`, JSON parsing for the
  config and both manifests, CSV shape checks for all five registry candidates
  and all hydrology parent/subunit IDs, `git diff --check`, ignored-path checks,
  tracked/candidate file-size and raw-extension checks, unresolved-stub scan,
  local Markdown link check, and a clean temporary-tree reproduction run that
  rebuilt 36 registry rows and 18 hydrology rows.
- 2026-05-30: Committed and pushed the validated Goal 006 package to `main` as
  `35003de` (`Prototype documented subunit hydrology`).
