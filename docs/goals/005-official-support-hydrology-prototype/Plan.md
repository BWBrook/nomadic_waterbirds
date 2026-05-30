# Plan

## Purpose

Move from product-access smoke evidence to a bounded real-support hydrology
prototype while keeping raw data staged outside Git.

## Expected File Responsibilities

- `docs/official_support_geometry_report.md`: supervisor-facing interpretation
  of support selection, staging, caveats, and blockers.
- `docs/official_support_geometry_manifest.json`: source, staging, file-size,
  hash, and cleanup provenance for official geometry/subunit inputs.
- `docs/official_support_geometry_summary.csv`: candidate/support status
  table covering all five required candidates.
- `docs/real_support_hydrology_prototype_report.md`: supervisor-facing
  interpretation of the computed real-support hydrology prototype.
- `docs/real_support_hydrology_prototype_manifest.json`: command, version,
  source, staging, runtime, and output provenance for hydrology processing.
- `docs/real_support_hydrology_prototype_summary.csv`: support/month metric
  table.
- `docs/compute_routing_memo_005.md`: required only if local execution is
  blocked or should be rerouted.
- `scripts/` and `settings/`: minimal reproducible support/hydrology workflow.
- `docs/source_evidence_register.md`: updated only for new/current source
  facts actually verified during this goal.
- `docs/data_stream_register.md`: updated hydrology and wetland-support status.
- `docs/decision_log.md`: decisions and deferrals.
- `docs/README.md`: navigation updates.
- `docs/goals/005-official-support-hydrology-prototype/Log.md`: live execution
  log.

## Task Sequence

1. Confirm clean repo state and read Goal 004 artefacts.
2. Confirm raw staging paths are ignored before use.
3. Re-check official geometry/subunit source access for the five candidates.
4. Stage raw geometry or subunit inputs only in ignored paths.
5. Build a support registry with one or more candidate supports, plus blocked
   status where needed.
6. Implement the smallest reproducible real-support monthly Water Observations
   extraction workflow.
7. Aggregate all readable scenes within each target month; avoid the Goal 004
   "clearest single scene" shortcut for support metrics.
8. Write geometry and hydrology manifests, reports, and summary tables.
9. Update project registers, decision log, docs navigation, and goal log.
10. Validate JSON, CSV, Git hygiene, staging paths, size limits, raw-data
    exclusion, links, and code/config syntax.
11. Commit and push if validation passes.

## Self-Review Questions

- Did the work genuinely advance from 3x3 probes to documented official
  supports or subunits?
- Are all five candidates represented in the support/status table, even if
  hydrology metrics are blocked for some?
- Can a supervisor tell exactly what raw files were staged, where they live,
  and why they are not committed?
- Are Water Observations metrics aggregated across all relevant scenes in the
  month rather than selected from one convenient scene?
- Does the report distinguish official named-complex geometry, Ramsar parcels,
  and DEA Waterbodies subunits?
- Are zero wetness, invalid pixels, geometry mismatch, or missing scenes
  preserved as evidence?
- Is the next recommended goal a logical scale-up, reroute, geometry redesign,
  or first biodiversity-access step?
