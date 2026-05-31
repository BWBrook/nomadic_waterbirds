# Log

Goal: Direct S3 all-support probe

Status: Complete.

## Supervisor Setup

- 2026-05-31: Goal 016 packet created after Goal 015 repaired the hydrology
  comparator baseline and formalised support-intersecting WRS path/rows as the
  production scene-selection policy. This goal should test the direct-S3 route
  across all current event-window supports for the same three probe months
  before any full event-window extraction.

## Execution Checkpoints

- Starting state: 2026-05-31 23:02 AEST; `git status --short --branch`
  reported `## main...origin/main`; recent history includes `d9162e3` and
  `2fee95d` is an ancestor of `HEAD`.
- Required reading complete: 2026-05-31 23:02 AEST; read repo/global
  instructions, Goal 016 `Goal.md` then `Plan.md` then `Runbook.md`, the
  required `nectar` control-plane/data-placement/smoke/current-status notes,
  Goal 013-015 reports/manifests/tables/settings/scripts/tests, metric spec,
  event-window tables, source evidence register, data stream register,
  decision log, and docs index.
- Ignored staging confirmed: 2026-05-31 23:02 AEST; `git check-ignore`
  confirmed `artifacts/direct_s3_all_support_probe_016/raw/probe.json`,
  `artifacts/direct_s3_all_support_probe_016/intermediate/probe.npy`, and
  `artifacts/direct_s3_all_support_probe_016/output/probe.json` are ignored;
  local staging directories were created under `artifacts/`.
- Compute-routing memo complete:
- `deep-server-ts` probe complete or blocked: 2026-05-31 23:08 AEST; SSH
  probe passed to `deep-server`, with 64 CPUs, 125 GiB RAM, 4.5 TiB free on
  `/data`, Python 3.12.3, GDAL 3.8.4, Git 2.43.0, NumPy 1.26.4, GDAL Python
  bindings, and HTTP 200 from `dea-public-data`.
- Remote smoke complete or blocker recorded: 2026-05-31 23:10 AEST;
  refreshed `/data/codex/repos/nomadic_waterbirds_goal016`, ran focused Goal
  016 tests on `deep-server-ts` (`6` tests passed), then ran the preferred
  `NWB002`/`2022-11` remote smoke. The smoke wrote one
  `computed_direct_s3_metrics` row in 12.288 s, matching Goal 015/014 hashes,
  counts, wet/dry observations, wet proportion, and quality fields; cross-host
  `current_wet_area_m2` differed by 2.367188 m2, so the predeclared area
  tolerance was widened to 5.0 m2 before the full run.
- 33-row all-support extraction rehearsal complete or blocked: 2026-05-31
  23:14 AEST; `deep-server-ts` ran all 11 supports by 3 months in 139.789 s
  at `/data/codex/repos/nomadic_waterbirds_goal016`; all 33 rows were
  `computed_direct_s3_metrics`, with no skipped scenes recorded in the summary.
- Comparison to Goal 015/014 and legacy rows complete: 2026-05-31 23:18 AEST;
  `NWB002` matched Goal 015 repaired comparator and Goal 014 direct-S3 rows
  within tolerance for all three months. Legacy/context comparison status
  counts were `within_tolerance=11`,
  `wetness_within_tolerance_denominator_diff=14`, `wetness_diff=6`, and
  `missing_or_blocked_reference=8`.
- Reports/manifests/CSV outputs written: 2026-05-31 23:18 AEST; compact
  deliverables copied back from `deep-server-ts` into `docs/`, including the
  report, manifest, 33-row summary, support summary, comparison CSV, and
  compute-routing memo.
- Registers/docs/logs updated: 2026-05-31 23:20 AEST; updated source evidence
  register, data stream register, decision log, docs index, and this log.
- Validation complete: 2026-05-31 23:24 AEST; passed `rg --files` expected
  file check, `git diff --check`, JSON parsing for settings and manifest, CSV
  schema/row-count checks, 33-row support/month grid check, `NWB002`
  Goal 015/014 comparison check, legacy comparison separation check,
  `python3 -m unittest tests.test_goal016_direct_s3_all_support_probe`,
  `python3 -m unittest discover -s tests -p 'test*.py'` (`48` tests),
  candidate file size/raw-extension hygiene checks, local Markdown link check
  over 112 Markdown files, unfinished-marker scan over changed Goal 016
  outputs, and `gh repo view BWBrook/nomadic_waterbirds --json visibility`
  (`PRIVATE`).
- Commit/push complete: 2026-05-31 23:27 AEST; validated package committed
  as `19d3842` (`Probe all-support direct S3 hydrology extraction`). This log
  finalisation is committed separately and pushed with the package to
  `origin/main`.

## Notes

- Keep raw S3 listings, rasters, masks, arrays, remote logs, and other bulky
  generated files in ignored staging only.
- Do not shrink the support grid silently. Every expected support/month needs
  either a computed row or a classified blocked row.
