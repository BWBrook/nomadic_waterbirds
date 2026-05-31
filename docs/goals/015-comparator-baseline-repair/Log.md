# Log

Goal: Comparator baseline repair

Status: Completed and pushed to main.

## Supervisor Setup

- 2026-05-31: Goal 015 packet created from Goal 014 direct-S3 extraction
  rehearsal. This goal should repair the comparator baseline and clarify the
  support-relevant scene-selection policy before any direct-S3 scale-up.

## Execution Checkpoints

- Starting state: 2026-05-31 confirmed clean `main` at `02bdc7c`
  (`origin/main`), with `fa9d69f` present in history and no dirty working-tree
  entries.
- Required reading complete: 2026-05-31 read `Goal.md`, `Plan.md`,
  `Runbook.md`, repo/global agent instructions, required `nectar` compute and
  data-placement guidance, Goal 013/014 reports/manifests/CSV outputs, the
  hydrology metric specification, event-window hydrology tables, relevant
  scripts, source evidence, and data stream register.
- Ignored staging confirmed: 2026-05-31 created
  `artifacts/comparator_baseline_repair_015/{raw,intermediate,output}/` and
  confirmed probe JSON/NPY artefacts under those paths are ignored by Git.
- STAC/path-row-filtered comparator route available or blocked: 2026-05-31
  initial live STAC calls with `limit=100` timed out, so the bounded Goal 015
  settings were tightened to `limit=20`; the rerun returned HTTP 200 for all
  three probe months with bbox item counts `2018-01=12`, `2022-11=15`, and
  `2024-12=14`. Filtering to support path/rows retained `9`, `11`, and `11`
  items respectively, with bbox-only extras all from `092/080`.
- Repaired comparator baseline generated or blocked: 2026-05-31 generated
  `docs/pathrow_filtered_comparator_015_summary.csv` with three
  `repaired_pathrow_filtered_stac_comparator` rows. STAC-filtered asset-key
  hashes matched Goal 014 direct-S3 hashes for every month.
- Comparison to Goal 014 direct-S3 rows complete: 2026-05-31
  `docs/comparator_baseline_repair_015_comparison.csv` records
  `within_tolerance` for repaired comparator versus Goal 014 direct-S3 rows
  across all three months under the predeclared tolerances.
- Legacy denominator effect quantified: 2026-05-31
  `docs/legacy_denominator_effect_015.csv` confirms the Goal 007 legacy
  denominator differences: `2022-11` has 4 bbox-only scenes and 375748 extra
  invalid/no-data observations; `2024-12` has 3 bbox-only scenes and 281811
  extra invalid/no-data observations. Both equal extra scenes multiplied by
  93937 support-mask pixels and change denominator fields only.
- Scene-selection policy drafted: 2026-05-31 report and
  `docs/hydrology_metric_spec.md` update state that support-level Water
  Observations monthly metrics should include only support-intersecting WRS
  path/rows, not all STAC bbox hits.
- Validation complete: 2026-05-31 validation passed. Commands/checks:
  `rg --files` expected-file check, `git diff --check`,
  `python3 -m unittest tests.test_goal015_comparator_baseline_repair`,
  `python3 -m unittest discover -s tests -p 'test*.py'` (42 tests),
  `python3 -m json.tool` for settings and manifest, CSV schema/row-count
  checks (3 summary rows, 6 comparison rows, 2 denominator-effect rows),
  Goal 015 output-consistency audit, source URL coverage check, ignored-staging
  check, committed-size check, committed raw-extension check, local Markdown
  link check (109 links), unfinished-marker scan, and final dirty-state review.
- Commit/push complete: Goal 015 package committed as `184e0bb` (`Repair
  hydrology comparator baseline`); this final log-status commit and the
  package commit were pushed to `origin/main` on 2026-05-31.
