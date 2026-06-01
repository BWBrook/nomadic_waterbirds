# Goal: Full-Window Direct-S3 Hydrology Production

## Objective

Run a remote, restartable full-window direct-S3 hydrology production workflow
for the current support set, using the support-intersecting WRS path-row
scene-selection policy.

The target production grid is the 11 current supports from Goal 016 across
`2018-01` through `2024-12` inclusive: 84 months and 924 expected
support-month rows. The goal should produce a committed, compact hydrology
evidence package if preflight gates pass, or a committed blocker/preflight
package if they do not.

## Why This Matters

Goals 011 through 018 replaced the unstable per-support/month STAC route with
a direct-S3 acquisition route, repaired the scene-selection policy, tested
bounded extraction, probed all supports, triaged legacy wetness differences,
and retired weak legacy baselines as blocking evidence.

The project is now ready to attempt the first production hydrology table that
can support later bird-response analysis. This is still a hydrology-only goal:
it should establish a reproducible environmental covariate layer, not interpret
waterbird ecology.

## Operating Mode

Remote scientific production run with restartability, provenance, and
production-readiness review. No biodiversity linkage and no ecological
interpretation.

## Scope

In scope:

- read repo instructions, this goal packet, Goal 013 through Goal 018
  artefacts, current hydrology metric spec, and `nectar` remote-compute/data
  placement guidance;
- use `deep-server-ts` as the preferred production host unless live route
  checks show it is unavailable;
- stage the remote working clone under
  `/data/codex/repos/nomadic_waterbirds_goal019`;
- implement or adapt a direct-S3 full-window production workflow that uses
  Goal 013 support-to-WRS path/row coverage and the Goal 015
  support-intersecting scene-selection policy;
- make the workflow restartable by support/month or another explicit shard
  unit, with resumable ignored intermediate outputs and stable final row
  hashes;
- run a bounded remote preflight before launching production;
- launch the full `2018-01` through `2024-12` production run only if the
  preflight gates pass;
- emit exactly one status-classified row for every expected support-month when
  a production run is launched;
- compute base monthly Water Observations metrics for every computed row;
- compute derived time-history metrics from the hydrology metric spec when
  sufficient preceding/following base rows exist, leaving clear `NA` or status
  values where derivation is not valid;
- record item-set/path-row provenance for each support-month as compact counts
  and hashes, not raw listings;
- update docs navigation, data stream register, decision log, and this goal
  log;
- commit and push the validated package to `main`.

Out of scope:

- STAC-dependent production route recovery;
- changing the support set, WRS path-row policy, hydrology metric definitions,
  or quality thresholds without narrow evidence and tests;
- new wetland boundaries, biodiversity data access, eBird/Birdata/ALA/EAWS
  processing, bird-response modelling, refuge interpretation, breeding
  interpretation, manuscript claims, or ecological synthesis;
- silently overwriting Goal 007, Goal 009, Goal 016, Goal 017, or Goal 018
  outputs;
- committing raw rasters, S3 listings, WRS geometry, masks, arrays, GeoJSON,
  GeoPackages, shapefiles, NetCDF, Parquet, RDS, SQLite/DuckDB stores,
  archives, remote caches, or bulky derived products.

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `/Users/bwbrook/work/nectar/docs/workflows/control-plane-doctrine.md`
- `/Users/bwbrook/work/nectar/docs/workflows/compute-resource-selection.md`
- `/Users/bwbrook/work/nectar/docs/workflows/project-integration.md`
- `/Users/bwbrook/work/nectar/docs/workflows/data-placement.md`
- `/Users/bwbrook/work/nectar/docs/workflows/smoke-tests.md`
- `/Users/bwbrook/work/nectar/docs/exchange/current_status.md`
- `docs/hydrology_metric_spec.md`
- `docs/support_pathrow_coverage_013_report.md`
- `docs/support_pathrow_coverage_013_manifest.json`
- `docs/support_pathrow_crosswalk_013.csv`
- `docs/comparator_baseline_repair_015_report.md`
- `docs/comparator_baseline_repair_015_manifest.json`
- `docs/direct_s3_all_support_probe_016_report.md`
- `docs/direct_s3_all_support_probe_016_manifest.json`
- `docs/direct_s3_all_support_probe_016_summary.csv`
- `docs/direct_s3_all_support_probe_016_comparison.csv`
- `docs/compute_routing_memo_016.md`
- `docs/legacy_wetness_difference_triage_017_report.md`
- `docs/legacy_wetness_difference_triage_017_manifest.json`
- `docs/pathrow_comparator_reconstruction_018_report.md`
- `docs/pathrow_comparator_reconstruction_018_manifest.json`
- `docs/pathrow_comparator_reconstruction_018_readiness.csv`
- `docs/pathrow_comparator_reconstruction_018_item_sets.csv`
- `scripts/direct_s3_all_support_probe_016.py`
- `scripts/pathrow_comparator_reconstruction_018.py`
- `settings/direct_s3_all_support_probe_016.json`
- `settings/pathrow_comparator_reconstruction_018.json`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `d005f38` (`Reconstruct path-row comparator
  evidence`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths locally and remotely before writing S3 caches,
  rasters, masks, arrays, per-shard outputs, or remote logs.
- Probe `deep-server-ts` live state and record CPU, RAM, `/data` capacity,
  Python, GDAL, and repo clone path in the log.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Preflight Gates

Run a bounded remote preflight before production. It should cover:

- at least one single-pathrow support-month;
- at least one multi-pathrow support-month;
- at least one Kerang support-month from the Goal 017/018 discrepancy cluster;
- at least one early-window month, one flood/wet-window month, and one recent
  month.

The preflight passes only if:

- direct-S3 listing and COG reads work from the remote host;
- the workflow writes one row per expected preflight support-month;
- item counts and hashes are stable across an immediate resume/rerun;
- base wetness fields are finite or explicitly status-classified;
- raw/intermediate outputs stay in ignored staging;
- focused tests and schema checks pass.

If preflight fails, do not launch production. Write a blocker report, manifest,
and log update explaining the failure and the next recovery route.

## Production Requirements

If preflight passes, run the full production grid:

- support set: the 11 current supports used in Goal 016;
- window: `2018-01` through `2024-12` inclusive;
- expected grid: 924 support-month rows;
- acquisition: direct S3 only, using support-intersecting WRS path/rows;
- row status: one of `computed_direct_s3_metrics`,
  `blocked_direct_s3_listing_failure`, `blocked_direct_s3_read_failure`,
  `blocked_geometry_or_mask_failure`, `blocked_metric_computation_failure`, or
  another documented fixed-vocabulary status if needed;
- quality flags: use the existing hydrology metric spec vocabulary unless a
  narrowly tested correction is required;
- restartability: rerun the workflow with resume enabled after the first run
  and record stable output hashes.

It is acceptable for a production run to contain status-classified blocked
rows if failures are real and documented. It is not acceptable to silently omit
support-month rows or to fabricate computed metrics for failed rows.

## Required Deliverables

Create:

- `docs/direct_s3_full_window_hydrology_019_report.md`: supervisor-facing
  report covering preflight, production status counts, quality counts, support
  and month coverage, blocked rows if any, restartability evidence, and the
  next decision.
- `docs/direct_s3_full_window_hydrology_019_manifest.json`: command,
  source files, support set, month window, remote host/path, git SHAs, staging
  paths, status vocabularies, output row hashes, item-set hashes, validation
  outcomes, and cleanup/provenance notes.
- `docs/direct_s3_full_window_hydrology_019_series.csv`: one row per expected
  support-month if production launches, with base and derived hydrology
  metrics, row status, quality flag, item count, and compact provenance fields.
- `docs/direct_s3_full_window_hydrology_019_item_sets.csv`: one row per
  support-month listing path/rows, item count, asset-key hash, item-id hash,
  and route status.
- `docs/direct_s3_full_window_hydrology_019_summary.csv`: support-level and
  overall status/quality/coverage summary.
- `docs/direct_s3_full_window_hydrology_019_preflight.json`: preflight grid,
  commands, route status, resume/rerun hashes, and pass/fail decision.
- `scripts/direct_s3_full_window_hydrology_019.py`: production workflow or
  wrapper around reusable hydrology code.
- `settings/direct_s3_full_window_hydrology_019.json`: support set, month
  window, direct-S3 route settings, remote/local staging paths, sharding,
  status vocabulary, and output paths.
- `tests/test_goal019_direct_s3_full_window_hydrology.py`: focused tests for
  support/month grid construction, path-row policy use, row status
  classification, restart/resume hashing, schema, derived metric boundary
  behaviour, and raw-data exclusion.

Update:

- `docs/data_stream_register.md`;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/019-full-window-direct-s3-hydrology-production/Log.md`.

Update `docs/hydrology_metric_spec.md` only if implementation reveals a
metric-contract ambiguity that must be clarified before later analysis.

## Validation Gates

Required validation:

- `git diff --check`;
- focused Goal 019 tests;
- full `python3 -m unittest discover -s tests -p 'test*.py'`;
- JSON parsing for settings, manifest, and preflight files;
- CSV schema checks for series, item-set, and summary outputs;
- expected-grid check: if production launches, exactly 924 support-month rows
  and all 11 supports x 84 months represented;
- row-status check: every expected row is computed or explicitly blocked;
- restartability check: resume/rerun produces stable committed output hashes;
- item-provenance check: no blank item hash for computed rows;
- raw/large-file hygiene checks;
- ignored-staging checks locally and on the remote host;
- local Markdown link check;
- unfinished-marker scan;
- GitHub visibility check;
- final clean/synced `git status --short --branch`.

## Stop Rules

Stop before production if preflight fails.

Stop and report a blocker if:

- `deep-server-ts` is unavailable and no suitable alternative is confirmed;
- direct-S3 listing or COG reads fail in the preflight;
- row hashes are not stable under resume/rerun;
- support/month rows go missing without status classification;
- a current extraction defect is found that cannot be fixed narrowly with a
  regression test inside this goal;
- validation gates fail.

If a narrow implementation defect is found before production, fix it with a
focused test and rerun preflight. If a scientific metric or support-policy
ambiguity is found, pause rather than changing the science silently.

## Final Response Requirements

Report:

- preflight outcome;
- whether production launched;
- row count and expected-grid status;
- computed/blocked status counts;
- quality counts;
- restartability evidence;
- remote host/path;
- changed files;
- validation commands and outcomes;
- commit hash and push status;
- residual risks;
- recommended Goal 020.
