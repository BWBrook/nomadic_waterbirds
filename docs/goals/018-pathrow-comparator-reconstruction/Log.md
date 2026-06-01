# Log

Goal: Path-row comparator reconstruction

Status: Complete.

## Supervisor Setup

- 2026-06-01: Goal 018 packet created after Goal 017 classified four material
  legacy wetness differences as `insufficient_reference_evidence`. This goal
  should rebuild bounded item/path-row evidence for those material rows before
  full-window direct-S3 production is authorised.

## Execution Checkpoints

- Starting state: 2026-06-01 11:38 AEST; `git status --short --branch`
  reported `## main...origin/main`; current `HEAD` was `0cbecaa` (`Add Goal
  018 path-row comparator reconstruction brief`) and `8515169` (`Triage
  legacy wetness differences`) is in history.
- Required reading complete: 2026-06-01 11:38 AEST; read Goal 018 `Goal.md`,
  then `Plan.md`, then `Runbook.md`, followed by repo/global instructions,
  required `nectar` control-plane notes, Goal 013-017 reports/manifests/tables,
  hydrology metric spec, Goal 016/017 scripts and settings, data stream
  register, and decision log before editing.
- Ignored staging confirmed: 2026-06-01 11:38 AEST; `git check-ignore`
  confirmed `artifacts/pathrow_comparator_reconstruction_018/raw/probe.json`,
  `artifacts/pathrow_comparator_reconstruction_018/intermediate/probe.npy`,
  and `artifacts/pathrow_comparator_reconstruction_018/output/probe.json` are
  ignored; local staging directories were created under `artifacts/`.
- Four material target rows confirmed: 2026-06-01 11:38 AEST; extracted
  exactly four `insufficient_reference_evidence` rows from
  `docs/legacy_wetness_difference_triage_017_audit.csv`: `component_369`
  `2018-01`, `ref265` `2022-11`, `component_369` `2024-12`, and `ref265`
  `2024-12`.
- Direct-S3 item provenance reconstructed: 2026-06-01 11:50 AEST; ran
  `python3 scripts/pathrow_comparator_reconstruction_018.py` and then
  regenerated with `--reuse-ignored-cache`; reconstructed direct-S3 path-row
  item sets matched committed Goal 016 item counts, asset-key hashes, and
  item-id hashes for all four material target rows.
- STAC path-row comparator attempted or blocked: 2026-06-01 11:50 AEST; DEA
  STAC was queried for each material support/month bbox and returned `HTTP
  503` for all four attempts, so route status was
  `stac_unavailable_direct_s3_provenance_only`; raw STAC responses were kept
  under ignored Goal 018 staging.
- Item-set comparisons complete: 2026-06-01 11:50 AEST; comparison rows
  include four `item_sets_match` direct-S3 reconstruction vs Goal 016 committed
  hash checks and four `comparator_unavailable` STAC comparator checks.
- Readiness classifications complete: 2026-06-01 11:50 AEST; all four
  material rows were classified `ready_with_legacy_baseline_retired`; no
  current direct-S3 defect was found.
- Bounded raster reruns complete or not needed: 2026-06-01 11:50 AEST; no
  raster reads or bounded raster reruns were needed because no item-set
  mismatch was found.
- Reports/manifests/CSV outputs written: 2026-06-01 11:50 AEST; wrote
  `docs/pathrow_comparator_reconstruction_018_report.md`,
  `docs/pathrow_comparator_reconstruction_018_manifest.json`,
  `docs/pathrow_comparator_reconstruction_018_targets.csv`,
  `docs/pathrow_comparator_reconstruction_018_item_sets.csv`,
  `docs/pathrow_comparator_reconstruction_018_comparison.csv`, and
  `docs/pathrow_comparator_reconstruction_018_readiness.csv`, plus ignored run
  metadata under `artifacts/pathrow_comparator_reconstruction_018/output/`.
- Registers/docs/logs updated: 2026-06-01 11:51 AEST; updated
  `docs/README.md`, `docs/data_stream_register.md`, `docs/decision_log.md`,
  and this log. `docs/hydrology_metric_spec.md` did not require changes
  because Goal 018 confirmed the existing support-intersecting WRS path-row
  scene-selection policy rather than changing it.
- Validation complete: 2026-06-01 11:53 AEST; `git diff --check`,
  `python3 -m unittest tests.test_goal018_pathrow_comparator_reconstruction`,
  `python3 -m unittest discover -s tests -p 'test*.py'`, JSON parsing for
  settings and manifest, CSV shape and material-row checks, Markdown
  local-link checks, ignored staging checks, committed size/raw-extension and
  Goal 018 artifact checks, expected-file checks with `rg --files`,
  unfinished-marker scans, and
  `gh repo view BWBrook/nomadic_waterbirds --json visibility --jq .visibility`
  all passed. GitHub visibility was `PRIVATE`.
- Commit/push complete: 2026-06-01 11:54 AEST; committed the validated Goal
  018 package and pushed `main` to `origin` after validation.

## Notes

- Do not launch full-window production in this goal.
- Every material target needs route status, readiness class, and a
  scale-up recommendation.
- Keep raw STAC/S3/raster artefacts in ignored staging only.
