# Plan

## Purpose

Move from three-month subunit proof to a bounded monthly time-history series
while strengthening weak named-subunit evidence.

## Expected File Responsibilities

- `docs/named_subunit_evidence_report.md`: supervisor-facing interpretation of
  support names, source evidence, and unresolved named-subunit questions.
- `docs/named_subunit_evidence_manifest.json`: source/staging/file-size/hash
  provenance for named-subunit source checks.
- `docs/named_subunit_crosswalk.csv`: support-set decision table for the
  event-window series.
- `docs/event_window_hydrology_series_report.md`: interpretation of the
  2018-2024 or fallback event-window hydrology series.
- `docs/event_window_hydrology_series_manifest.json`: command, version,
  source, staging, runtime, and output provenance.
- `docs/event_window_hydrology_series.csv`: monthly base and derived hydrology
  metrics.
- `docs/event_window_hydrology_summary.csv`: compact review table.
- `docs/compute_routing_memo_007.md`: required only if local execution is
  blocked or should be rerouted.
- `scripts/` and `settings/`: minimal reproducible workflow.
- `tests/`: focused test for derived time-history metrics.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, and `docs/README.md`: updated navigation/status.
- `docs/goals/007-named-subunit-evidence-event-series/Log.md`: live execution
  log.

## Task Sequence

1. Confirm clean repo state and read Goal 006 artefacts.
2. Confirm ignored raw staging paths.
3. Review named-subunit evidence, especially Narran and Currawinya.
4. Build `docs/named_subunit_crosswalk.csv` for the event-window support set.
5. Implement or adapt a bounded monthly hydrology workflow for the selected
   support set.
6. Compute base monthly metrics and derived time-history metrics.
7. Write event-window series, compact summary, manifests, and reports.
8. Update project registers, decision log, docs navigation, and goal log.
9. Validate JSON, CSV, Git hygiene, staging paths, size limits, raw-data
   exclusion, links, tests, and code/config syntax.
10. Commit and push if validation passes.

## Self-Review Questions

- Did the goal improve named-support evidence rather than merely run more
  pixels?
- Are Narran and Currawinya handled honestly if named subunit evidence remains
  unresolved?
- Does the event window support lag, novelty, drying, and hydroperiod metrics?
- Are quality-fail and missing months retained?
- Is the support set bounded and scientifically defensible?
- Does the report avoid bird-response or ecological-role claims?
- Is the next recommended goal ready to move toward hydrology scale-up,
  biodiversity-access preparation, or literature/claim integration?
