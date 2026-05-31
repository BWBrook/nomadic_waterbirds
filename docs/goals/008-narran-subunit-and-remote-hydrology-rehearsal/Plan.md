# Plan

## Purpose

Close the major support-evidence gap left by Goal 007 and make the next
hydrology scale-up path executable on the correct machine.

## Expected File Responsibilities

- `docs/narran_named_subunit_evidence_report.md`: human-readable assessment of
  Narran named features and geometry evidence.
- `docs/narran_named_subunit_evidence_manifest.json`: source and staging
  provenance for Narran evidence checks.
- `docs/narran_named_subunit_crosswalk.csv`: machine-readable support decision
  table for Narran.
- `docs/compute_routing_memo_008.md`: mandatory compute-resource decision and
  live probe evidence.
- `docs/remote_hydrology_rehearsal_008_report.md`: remote rehearsal report if
  a remote run is possible.
- `docs/remote_hydrology_rehearsal_008_manifest.json`: machine-readable remote
  commands, host facts, paths, runtimes, and outputs.
- optional `docs/event_window_hydrology_series_2018_2024*`: small committed
  full-window outputs if `deep-server` can run them cleanly.
- `scripts/`, `settings/`, and `tests/`: minimal support for this goal.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, and `docs/README.md`: project state updates.
- `docs/goals/008-narran-subunit-and-remote-hydrology-rehearsal/Log.md`: live
  execution log.

## Task Sequence

1. Confirm clean repo state and Goal 007 checkpoint.
2. Read project and compute-control documentation.
3. Confirm ignored staging paths.
4. Search official/current public sources for Narran named geometry evidence.
5. Build and validate the Narran crosswalk.
6. Write Narran evidence report and manifest.
7. Probe `deep-server` and write the compute-routing memo.
8. If viable, stage a remote working clone and run a small remote hydrology
   rehearsal.
9. If practical, run the full `2018-01` through `2024-12` event window on
   `deep-server` and commit only small summaries/manifests.
10. Update registers, decision log, docs navigation, and goal log.
11. Validate docs, JSON, CSV, code/tests, Git hygiene, links, and raw-data
    exclusion.
12. Commit and push if validation passes.

## Self-Review Questions

- Did the work resolve Narran evidence or honestly prove it remains unresolved?
- Are names, geometry, and DEA Waterbody relationships separated clearly?
- Did the compute decision use available resources rather than shrinking the
  science to fit the local machine?
- Are remote paths, commands, outputs, and cleanup status documented enough for
  a later agent to repeat or scale the run?
- Did the goal avoid ecological interpretation?
- Is Goal 009 now a cleaner choice between remote hydrology scale-up,
  biodiversity access, or source-verified literature support?
