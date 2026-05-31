# Log

Goal: Direct S3 extraction rehearsal

Status: Ready for action agent.

## Supervisor Setup

- 2026-05-31: Goal 014 packet created from Goal 013 support path-row metadata
  equivalence. This goal should rehearse actual direct-S3 Water Observations
  extraction for `NWB002` before any full-window or all-support scale-up.

## Execution Checkpoints

- Starting state: 2026-05-31 21:28:48 AEST; `git status --short --branch`
  returned `## main...origin/main`; `001b9d0` is an ancestor of `HEAD`
  (`f3a9807`).
- Required reading complete: read Goal 014 `Goal.md`, `Plan.md`, `Runbook.md`,
  `Log.md`, repo/global `AGENTS.md`, required `nectar` control-plane docs,
  Goal 013 report/manifest/crosswalk/item-set/comparator/settings/script,
  hydrology metric spec, existing event-window metric tables, current
  hydrology scripts, source evidence register, and data stream register.
- Goal 013 provenance correction made or deemed unnecessary: corrected the WRS
  raw ZIP byte count from `5268121` to `5268095` in the Goal 013 log and source
  evidence register after confirming the current ignored file and Goal 013
  manifest agree on `5268095` bytes and SHA-256
  `9e6467f7709999683a41a71f9b0e388b6b84a5f59732ca797c5266c72eb9ce76`.
- Ignored staging confirmed: 2026-05-31; `git check-ignore` confirmed
  `artifacts/direct_s3_extraction_rehearsal_014/raw/probe.tif`,
  `artifacts/direct_s3_extraction_rehearsal_014/intermediate/probe.npy`, and
  `artifacts/direct_s3_extraction_rehearsal_014/output/probe.json` are ignored.
- Item-set validation complete: `python3 scripts/direct_s3_extraction_rehearsal_014.py`
  regenerated direct-S3 listings under ignored Goal 014 staging and matched
  Goal 013 counts/hashes for `NWB002`: `2018-01=9`, `2022-11=11`,
  `2024-12=11`; no missing path/rows or hash mismatches.
- Tiny raster-read probe complete: direct `/vsis3/` COG probe succeeded for
  `092/081` `2018-01` asset
  `ga_ls_wo_3_092081_2018-01-09_final_water.tif` with a 1 x 1 GDAL warp in
  1.422 seconds.
- Direct-S3 extraction complete: local Mac mini run completed in 20.0 seconds
  without remote compute; three summary rows written. Readable direct-S3 scene
  counts were `2018-01=9`, `2022-11=11`, `2024-12=11`; skipped scenes were 0
  for all three months.
- Comparison to existing event-window metrics complete: `2018-01` recorded as
  a new bounded rehearsal row for a Goal 009 endpoint-blocked month. Strict
  comparison against Goal 007 STAC-derived rows found `2022-11` and `2024-12`
  mismatched beyond tolerance for `readable_scene_count`, `invalid_obs_count`,
  and `clear_obs_fraction`; wet area, wet proportion, wet/dry observation
  counts, valid support area, and quality flag matched. The mismatch pattern is
  consistent with legacy STAC bbox-only no-data scenes outside the Goal 013
  support-derived path/row set.
- Route recommendation drafted: do not scale direct S3 yet; recommended Goal
  015 is a comparator-baseline repair goal that builds a path-row-filtered STAC
  or no-data-adjusted baseline before any full-window direct-S3 extraction.
- Validation complete: 2026-05-31 validation passed before staging:
  - expected Goal 014 files found with `rg --files`;
  - `git diff --check`;
  - `python3 -m unittest tests.test_goal014_direct_s3_extraction` (6 tests);
  - `python3 -m unittest discover -s tests -p 'test*.py'` (37 tests);
  - settings and manifest parsed with `python3 -m json.tool`;
  - CSV deliverables parsed with required columns and exactly three summary
    rows plus three comparison rows;
  - item-set validation and hash audit matched Goal 013 counts/hashes;
  - comparison audit confirmed mismatch rows carry `do_not_scale`
    recommendations and legacy bbox-only no-data scene hints;
  - source URL coverage, ignored staging, committed-size, committed
    raw-extension, local Markdown-link, and unfinished-marker checks passed.
- Commit/push complete:
