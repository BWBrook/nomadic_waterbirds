# Plan

## Purpose

Prove the first executable hydrology path at tiny scale while preserving the
repo's raw-data boundaries.

## Expected File Responsibilities

- `docs/hydrology_smoke_test_report.md`: supervisor-facing interpretation of
  the smoke test.
- `docs/hydrology_smoke_test_manifest.json`: machine-readable provenance and
  resource record.
- `docs/hydrology_smoke_test_summary.csv`: small candidate/support/month
  summary table.
- `docs/compute_routing_memo_004.md`: required only if local execution is not
  appropriate or is blocked.
- `scripts/` and `settings/`: optional minimal executable smoke workflow and
  configuration.
- `docs/data_stream_register.md`: updated hydrology feasibility status.
- `docs/decision_log.md`: decisions and deferrals.
- `docs/README.md`: navigation updates.
- `docs/goals/004-hydrology-extraction-smoke-test/Log.md`: live execution log.

## Task Sequence

1. Confirm repo state, read Goal 003 artefacts, and choose local versus routing
   memo path.
2. Confirm ignored scratch/staging paths.
3. Select the minimal official geometry/product access method.
4. Implement the smallest repeatable access/extraction workflow.
5. Attempt all five smoke-test candidates and record one or more summary rows
   per candidate.
6. Compute the feasible subset of monthly metric-spec fields for 2-3
   contrasting months, or record access-only blockers.
7. Write the report, manifest, and summary table.
8. Update registers, decision log, docs navigation, and goal log.
9. Validate JSON, CSV, Git hygiene, size limits, raw-data exclusion, links, and
   any code/config syntax.
10. Commit and push if validation passes.

## Self-Review Questions

- Did the smoke test prove something executable, not just add more prose?
- Are raw inputs staged only in ignored paths?
- Can a supervisor see exactly what was fetched, how large it was, and whether
  it was cleaned up?
- Does every included candidate have a status row?
- Are failures captured as design evidence rather than hidden?
- Is the next goal a logical scale-up, reroute, or redesign decision?
