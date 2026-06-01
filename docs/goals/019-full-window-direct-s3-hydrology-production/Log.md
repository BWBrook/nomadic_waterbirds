# Log

Goal: Full-window direct-S3 hydrology production

Status: Complete.

## Supervisor Setup

- 2026-06-01: Goal 019 packet created after Goal 018 reconstructed direct-S3
  item provenance for the four material legacy comparator rows, found no
  current direct-S3 defect, and recommended a remote restartable full-window
  direct-S3 hydrology production run.

## Execution Checkpoints

- 2026-06-01: Started execution from the ordered packet:
  `Goal.md`, then `Plan.md`, then `Runbook.md`.
- 2026-06-01: Required reading completed for repo/global instructions,
  `nectar` control-plane/data-placement/smoke-test/current-status notes,
  the hydrology metric spec, Goal 013-018 evidence artefacts, Goal 016 and
  Goal 018 scripts/settings, data-stream register, and decision log.
- 2026-06-01: Starting Git state clean on `main` at `f845a89`
  (`Add Goal 019 full-window hydrology brief`), with `d005f38`
  (`Reconstruct path-row comparator evidence`) in history.
- 2026-06-01: Expected grid check passed: `84` months from `2018-01` through
  `2024-12`, `11` supports, `924` expected support-month rows.
- 2026-06-01: Local ignored staging check passed for
  `artifacts/direct_s3_full_window_hydrology_019/raw/probe.json`,
  `artifacts/direct_s3_full_window_hydrology_019/intermediate/probe.npy`, and
  `artifacts/direct_s3_full_window_hydrology_019/output/probe.csv`.
- 2026-06-01: `deep-server-ts` live probe passed and
  `/data/codex/repos` was created/confirmed. Probe output: host
  `deep-server`, `64` CPUs, `125Gi` RAM, `/data` `13T` total / `4.5T`
  available, Python `3.12.3`, GDAL `3.8.4`.
- 2026-06-01: Wrote Goal 019 focused tests, settings, and restartable
  direct-S3 workflow wrapper around the Goal 016 extraction core. Local
  `python3 -m unittest tests.test_goal019_direct_s3_full_window_hydrology`
  passed (`7` tests); local `python3 -m unittest discover -s tests -p
  'test*.py'` passed (`67` tests).
- 2026-06-01: Staged the working tree to
  `/data/codex/repos/nomadic_waterbirds_goal019`, including the ignored
  Goal 007 support-loader inputs
  `artifacts/event_window_hydrology/raw/ramsar_goal007_subset.geojson` and
  `artifacts/event_window_hydrology/raw/ga_ls_wb_3_v3.zip`. Remote Git state
  is clean apart from intended Goal 019 changes; remote ignored-staging checks
  passed for raw/intermediate/output and per-shard JSON paths.
- 2026-06-01: Remote focused Goal 019 tests passed on `deep-server-ts`
  (`7` tests).
- 2026-06-01: Remote bounded preflight passed with
  `python3 scripts/direct_s3_full_window_hydrology_019.py --mode preflight
  --verify-resume --run-host-label deep-server-ts --remote-workdir
  /data/codex/repos/nomadic_waterbirds_goal019`. Preflight covered `3`
  target support-months, all `computed_direct_s3_metrics`; resume/rerun hash
  stability was `true`; series hash
  `899cbfd1cab0089576cf528915c22b8e9df886499364570e4d4b54499254d737`;
  item-set hash
  `f4718f71875da215a9b24f7b20303f3de42cb25811d4ab133d064c8d69bd6667`.
- 2026-06-01: Production launch authorised by passing preflight.
- 2026-06-01: Remote production completed on `deep-server-ts` at
  `/data/codex/repos/nomadic_waterbirds_goal019` with `924` observed rows
  for `924` expected support-months. All rows were
  `computed_direct_s3_metrics`; blocked rows `0`. Quality counts:
  `751` `quality_high`, `150` `quality_minimum`, `23` `quality_fail`.
  Initial production elapsed time was `4585.881` seconds; resume pass elapsed
  time was `6.611` seconds.
- 2026-06-01: Production resume/rerun hashes were stable. Series hash
  `ac3b77b18ba80ee7b9ba4213331b63151eb4fd98c8dbfbb776fe34fb637d5da9`;
  item-set hash
  `76b26db1466aa5bc43e4ad65339b703ed3941d9049f9497c92d66044e54da448`;
  summary hash
  `6ca5a653e5ab82fa9f5a084966cb95c65c128298c916c4820be5f3e9095eff52`.
- 2026-06-01: Pulled back only compact committed outputs:
  `docs/direct_s3_full_window_hydrology_019_report.md`,
  `docs/direct_s3_full_window_hydrology_019_manifest.json`,
  `docs/direct_s3_full_window_hydrology_019_series.csv`,
  `docs/direct_s3_full_window_hydrology_019_item_sets.csv`,
  `docs/direct_s3_full_window_hydrology_019_summary.csv`, and
  `docs/direct_s3_full_window_hydrology_019_preflight.json`.
- 2026-06-01: Validation passed: `git diff --check`; focused Goal 019
  tests (`7` tests); full unittest discovery (`67` tests); JSON parse checks
  for settings/preflight/manifest; production grid check (`924` rows, `11`
  supports, `84` months, no duplicate support-months, no blank row status);
  CSV schema checks (`924` series rows, `924` item-set rows, `96` summary
  rows); manifest restartability and item-provenance checks; remote ignored
  staging check on `deep-server-ts`; committed-size check; committed
  raw-extension check; local Markdown link check (`139` links); unfinished
  marker scan; and GitHub private visibility check
  (`BWBrook/nomadic_waterbirds`, `PRIVATE`).
- 2026-06-01: Recorded validation outcomes in
  `docs/direct_s3_full_window_hydrology_019_manifest.json`.
- 2026-06-01: Final manifest parse and `git diff --check` passed after
  recording validation outcomes. Package is ready for commit and push.

## Notes

- Use `deep-server-ts` as the preferred host and
  `/data/codex/repos/nomadic_waterbirds_goal019` as the remote working path.
- Do not launch production if preflight fails.
- If production launches, emit exactly one status-classified row for each of
  924 expected support-months.
- Keep raw S3 listings, rasters, masks, arrays, and remote caches in ignored
  staging only.
