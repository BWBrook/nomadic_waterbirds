# Plan

## Purpose

Move from official parent supports to documented child supports while keeping
the workflow hydrology-only, bounded, and reviewable.

## Expected File Responsibilities

- `docs/subunit_support_registry_report.md`: supervisor-facing interpretation
  of parent-child support options, selected subunits, caveats, and blockers.
- `docs/subunit_support_registry_manifest.json`: source, staging, file-size,
  hash, and cleanup provenance for subunit source checks.
- `docs/subunit_support_registry.csv`: machine-readable parent/subunit status
  table covering all five parent candidates.
- `docs/subunit_hydrology_prototype_report.md`: interpretation of bounded
  subunit hydrology metrics relative to Goal 005 parent context.
- `docs/subunit_hydrology_prototype_manifest.json`: command, version, source,
  staging, runtime, and output provenance for subunit hydrology processing.
- `docs/subunit_hydrology_prototype_summary.csv`: parent/subunit/month metric
  table.
- `docs/compute_routing_memo_006.md`: required only if local execution is
  blocked or should be rerouted.
- `scripts/` and `settings/`: minimal reproducible subunit workflow.
- `tests/`: focused test for registry or metric logic.
- `docs/source_evidence_register.md`: updated only for new/current source
  facts actually verified during this goal.
- `docs/data_stream_register.md`: updated hydrology and wetland-support status.
- `docs/decision_log.md`: decisions and deferrals.
- `docs/README.md`: navigation updates.
- `docs/goals/006-documented-subunit-hydrology-prototype/Log.md`: live
  execution log.

## Task Sequence

1. Confirm clean repo state and read Goal 005 artefacts.
2. Confirm raw staging paths are ignored before use.
3. Reuse or refresh the small Ramsar subset as needed for Ramsar component
   subunits.
4. Investigate DEA Waterbodies v3 access at bounded scale and stop with a
   blocker/routing memo if it wants to become a bulky national extraction.
5. Build `docs/subunit_support_registry.csv` with parent IDs, subunit IDs,
   source identifiers, inclusion decisions, and caveats.
6. Implement the smallest reproducible subunit hydrology extraction over a
   selected, scientifically informative subset.
7. Aggregate all readable Water Observations scenes within each target month.
8. Write subunit registry and hydrology manifests, reports, and summary tables.
9. Update project registers, decision log, docs navigation, and goal log.
10. Validate JSON, CSV, Git hygiene, staging paths, size limits, raw-data
    exclusion, links, tests, and code/config syntax.
11. Commit and push if validation passes.

## Self-Review Questions

- Does every subunit row have a parent support ID and a defensible source?
- Are Ramsar components, DEA Waterbodies overlaps, and other official subunits
  clearly distinguished?
- Did the workflow remain bounded rather than becoming full Waterbodies or
  historical extraction?
- Can a supervisor see which subunits are ready, deferred, blocked, or rejected?
- Are raw geometry and rasters staged only in ignored paths?
- Does the report avoid bird-response or ecological-role claims?
- Is the next recommended goal a logical hydrology scale-up, source redesign,
  biodiversity-access preparation, or validation-design step?
