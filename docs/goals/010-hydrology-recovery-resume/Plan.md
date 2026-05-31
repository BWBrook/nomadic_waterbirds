# Plan

## Purpose

Recover from Goal 009's endpoint-blocked full-window run without blindly
rerunning the same failure mode. The goal should first test whether service
stability has improved enough to justify a remote recovery run.

## Expected File Responsibilities

- `docs/stac_recovery_010_report.md`: preflight, launch decision, recovery or
  blocker interpretation.
- `docs/stac_recovery_010_manifest.json`: machine-readable probes, sample
  rows, retry settings, remote path, command, runtime, output inventory, and
  status counts.
- `docs/event_window_hydrology_series_2018_2024_recovery010.csv`: versioned
  recovered full-window table if recovery is launched.
- `docs/event_window_hydrology_summary_2018_2024_recovery010.csv`: compact
  support-level recovery summary if recovery is launched.
- `docs/remote_full_window_hydrology_010_retry_summary.csv`: compact
  support-level retry/recovery summary if useful.
- `scripts/`, `settings/`, and `tests/`: minimal preflight/resume support if
  needed.
- `docs/data_stream_register.md`, `docs/decision_log.md`, `docs/README.md`,
  and `docs/source_evidence_register.md`: project state updates as needed.
- `docs/goals/010-hydrology-recovery-resume/Log.md`: live execution log.

## Task Sequence

1. Confirm clean repo state and required checkpoint.
2. Read repo/global instructions, `nectar` docs, and Goal 009 evidence.
3. Confirm ignored staging paths locally and remotely.
4. Summarise Goal 009 blocked rows by support, month, and failure class.
5. Build or configure a representative blocked-row preflight sample.
6. Run endpoint probes and blocked-row preflight locally/remotely as needed.
7. Decide whether preflight meets launch criteria.
8. If not stable, write blocker report/manifest, update docs, validate, commit,
   and push.
9. If stable, stage source to `deep-server-ts`, run remote tests, and launch
   blocked-row resume or full rerun.
10. Bring back only small review artefacts.
11. Merge/preserve Goal 009 computed rows if using resume strategy.
12. Update reports, manifests, registers, decision log, docs navigation, and
    goal log.
13. Validate code/tests, JSON, CSV, docs, Git hygiene, links, and raw-data
    exclusion.
14. Commit and push if validation passes.

## Self-Review Questions

- Did the preflight prevent another expensive run under unstable service
  conditions?
- Is the decision to launch or stop supported by machine-readable evidence?
- Are Goal 009 and Goal 010 outputs versioned separately?
- Can the supervisor tell which rows were preserved, recovered, still blocked,
  or newly failed?
- Does the result move the project closer to usable hydrology evidence?
- Did the goal avoid biodiversity, literature integration, and ecological
  interpretation?
