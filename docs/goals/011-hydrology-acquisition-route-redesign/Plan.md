# Plan

## Purpose

Move from repeated STAC retry attempts to a deliberate hydrology acquisition
strategy. Goal 011 should produce a decision package, not another full-window
hydrology table.

## Expected File Responsibilities

- `docs/hydrology_acquisition_route_011_report.md`: narrative comparison and
  recommendation.
- `docs/hydrology_acquisition_route_011_manifest.json`: source/probe/host
  provenance and route statuses.
- `docs/hydrology_acquisition_options_011.csv`: acquisition-route comparison.
- `docs/hydrology_stac_query_pattern_011.csv`: current query-pattern and
  cache-opportunity audit.
- Optional `scripts/`, `settings/`, `tests/`: tiny probes or validation helpers
  if they make the decision more reproducible.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`: project state updates.
- `docs/goals/011-hydrology-acquisition-route-redesign/Log.md`: live log.

## Task Sequence

1. Confirm clean repo state and required checkpoint.
2. Read repo/global instructions, `nectar` docs, and Goal 009/010 evidence.
3. Audit current hydrology code for STAC query pattern and repeated calls.
4. Verify current official DEA access documentation and source routes.
5. Identify candidate acquisition strategies.
6. Run tiny live probes only where they materially improve the decision.
7. Build route-comparison and query-pattern CSVs.
8. Draft report and manifest with a recommended Goal 012.
9. Update registers, decision log, docs navigation, and goal log.
10. Validate docs, JSON, CSV, code/tests, Git hygiene, links, and raw-data
    exclusion.
11. Commit and push if validation passes.

## Self-Review Questions

- Does the recommendation reduce the chance of another 779-row endpoint
  failure?
- Is the recommended route scientifically equivalent to monthly DEA Water
  Observations support metrics, or is it a lower-evidence fallback?
- Does the route reduce live STAC dependence through caching, batching, direct
  access, or a more appropriate compute/data environment?
- Are source claims backed by current official documentation?
- Is Goal 012 executable without guessing?
