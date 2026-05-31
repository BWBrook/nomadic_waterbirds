# Plan

## Purpose

Expand from the repaired `NWB002` comparator baseline to a bounded all-support
direct-S3 extraction rehearsal. This goal should test support diversity,
path/row grouping, remote execution, row-level failure classification, and
comparison behaviour before any full event-window extraction is authorised.

## Expected File Responsibilities

- `settings/direct_s3_all_support_probe_016.json`: support source files,
  months, product, scene-selection policy, route settings, staging paths,
  tolerances, output paths, and resource limits.
- `scripts/direct_s3_all_support_probe_016.py`: bounded extraction script for
  support/month grid construction, direct-S3 item discovery, COG reads,
  support masking, bit decoding, base metric aggregation, status
  classification, comparison output, and report/manifest writing.
- `tests/test_goal016_direct_s3_all_support_probe.py`: focused tests for grid
  construction, path/row grouping, status vocabulary, metric schema, comparison
  classification, and raw-data exclusion.
- `docs/direct_s3_all_support_probe_016_report.md`: narrative result and Goal
  017 recommendation.
- `docs/direct_s3_all_support_probe_016_manifest.json`: command, source,
  route, compute, output, runtime, staging, row-count, and cleanup provenance.
- `docs/direct_s3_all_support_probe_016_summary.csv`: 33-row support/month
  base-metric table with status fields.
- `docs/direct_s3_all_support_probe_016_support_summary.csv`: support-level
  compact status/quality summary.
- `docs/direct_s3_all_support_probe_016_comparison.csv`: comparison to
  Goal 015/014 and legacy event-window rows.
- `docs/compute_routing_memo_016.md`: compute route and remote smoke evidence.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`: project context updates.
- `docs/goals/016-direct-s3-all-support-probe/Log.md`: live execution log.

## Task Sequence

1. Confirm clean repo state and that `2fee95d` is in history.
2. Read the required local, global, and `nectar` instructions.
3. Inspect Goal 013 through Goal 015 artefacts and current hydrology scripts.
4. Confirm ignored local and remote staging paths before writing route
   artefacts.
5. Write focused tests for support/month grid construction, path/row grouping,
   status classification, output schema, comparison classification, and raw
   exclusion.
6. Implement or adapt the bounded direct-S3 extraction script/config.
7. Probe `deep-server-ts`, create or refresh the remote clone under
   `/data/codex/repos/nomadic_waterbirds_goal016`, and run a target smoke test.
8. Run the 33-row support/month extraction rehearsal on the chosen host.
9. Copy compact outputs back to the local repo if remote execution was used.
10. Compare computed rows to Goal 015/014 for `NWB002` and to legacy rows
    where available.
11. Write the report, manifest, compute-routing memo, support summary, and
    comparison table.
12. Update registers, docs index, decision log, and this goal log.
13. Run validation gates, including focused tests, full tests, JSON/CSV checks,
    link checks, raw-data hygiene checks, and final Git status.
14. Commit and push if validation passes.

## Stop Rules

- Stop before the 33-row run if `deep-server-ts` is unavailable and the local
  smoke suggests the full support grid would be a long or disruptive Mac mini
  job.
- Stop before production-scale work even if the 33-row probe succeeds.
- Stop and write a blocker package if support geometry, path/row grouping, S3
  listing, COG reading, or masking fails in a way that cannot be classified
  cleanly.
- Do not silently remove difficult supports, months, or path/rows.

## Self-Review Questions

- Are all 11 supports and all 3 months represented in the output or blocker
  accounting?
- Did the run use the Goal 015 support-intersecting path/row scene-selection
  policy?
- Did `NWB002` reproduce the Goal 015/014 rows?
- Are legacy comparison differences labelled as wetness-field differences,
  denominator-only differences, or missing/blocker states?
- Is the recommended Goal 017 justified by evidence from all supports, not
  only by `NWB002`?
