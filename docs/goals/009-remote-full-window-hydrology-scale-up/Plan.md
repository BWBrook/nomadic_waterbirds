# Plan

## Purpose

Turn the Goal 008 remote rehearsal into a robust full-window hydrology
scale-up, while treating DEA STAC availability as a first-class dependency.

## Expected File Responsibilities

- `docs/stac_resilience_009_report.md`: retry/backoff and endpoint probe
  interpretation.
- `docs/stac_resilience_009_manifest.json`: machine-readable endpoint probes,
  retry settings, attempt counts, and status.
- `docs/remote_full_window_hydrology_009_report.md`: full-window run report or
  blocker report.
- `docs/remote_full_window_hydrology_009_manifest.json`: remote host, command,
  path, runtime, retry, output, and cleanup provenance.
- `docs/event_window_hydrology_series_2018_2024.csv`: full-window monthly
  support table if the run succeeds.
- `docs/event_window_hydrology_summary_2018_2024.csv`: compact full-window
  summary if the run succeeds.
- `scripts/`, `settings/`, and `tests/`: minimal retry/backoff and remote
  full-window support.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, and `docs/README.md`: project state updates.
- `docs/goals/009-remote-full-window-hydrology-scale-up/Log.md`: live
  execution log.

## Task Sequence

1. Confirm clean repo state and Goal 008 checkpoint.
2. Read repo/local AGENTS plus required `nectar` control-plane docs.
3. Confirm local and remote ignored staging paths.
4. Add retry/backoff/transient-failure classification and focused tests.
5. Run local tests and a local STAC availability probe.
6. Stage source to `deep-server-ts` using GitHub or Goal 008 rsync pattern.
7. Run remote tests and remote STAC availability probes.
8. If probes show service-wide outage, write blocker reports/manifests and
   stop.
9. If probes recover, run the full 2018-2024 event-window series on
   `deep-server-ts`.
10. Bring back small CSV/JSON/Markdown/log artefacts only.
11. Update registers, decision log, docs navigation, and goal log.
12. Validate docs, JSON, CSV, code/tests, Git hygiene, links, and raw-data
    exclusion.
13. Commit and push if validation passes.

## Self-Review Questions

- Did retry/backoff improve resilience without hiding persistent endpoint
  failure?
- Did the goal use `deep-server-ts` as the default compute host rather than
  falling back to local scale-down?
- Are output row counts and failure classes reviewable?
- Are remote paths and source-staging methods documented enough for a later
  agent to resume?
- Did the goal avoid changing support definitions or making ecological claims?
- Is Goal 010 now ready to move toward biodiversity access, regional water
  availability, or source-verified literature support?
