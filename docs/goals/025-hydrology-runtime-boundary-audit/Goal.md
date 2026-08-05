# Goal: Hydrology Runtime Boundary And Retirement Audit

## Objective

Produce a concise, evidence-backed audit of the hydrology runtime so the next
implementation decision is explicit: which code is canonical, which code is
historical evidence, which code can be retired, and where a small future
hydrology core would begin.

The audit must distinguish repository-local callers from unknown external
human workflows. It must not delete, move, or refactor code in this goal.

## Why This Matters

The current production path is a deep chronological chain:

`019 -> 016 -> 014/013 -> 007 -> 005`

Several modules are large mixed-responsibility scripts, and temporal
derivation logic exists in both Goal 007 and Goal 019. We need evidence before
extracting a core or retiring historical route code; otherwise cleanup could
silently change hydrology semantics or destroy useful audit provenance.

## Operating Mode

Read-only repository architecture and scientific-contract audit. Static local
inspection and small in-memory reasoning only. No external network, datasets,
raw biodiversity records, remote compute, production extraction, model fitting,
or eBird action.

## Scope

In scope:

- read this packet, `AGENTS.md`, the project brief, hydrology metric,
  reproducibility and validation plans, the Goal 019/020 packets and reports,
  and relevant Goal 004-018 logs;
- map the repository-local import and command graph for hydrology scripts and
  settings, with file/line evidence;
- inventory the Goal 004-020 hydrology scripts, wrappers, tests, settings, and
  committed reports sufficiently to classify their current role;
- compare Goal 007 temporal derivation with Goal 019 derived metrics, including
  blocked-row, missingness, lag, novelty, drying, and regional-metric behavior;
- classify every hydrology script in the 004-020 family as `retain`,
  `simplify`, `retire`, or `defer`, with evidence and confidence;
- state the canonical active inputs, outputs, consumers, and protected
  scientific/provenance invariants;
- propose the smallest defensible next implementation seam, if one is
  justified;
- create one concise audit report inside this Goal 025 directory and update
  this goal `Log.md`.

Out of scope:

- editing, deleting, moving, renaming, or refactoring existing hydrology
  scripts, tests, settings, reports, or outputs;
- running any production or remote-sensing extraction, STAC/S3 request, or
  remote/HPC job;
- opening raw external data or any biodiversity records;
- changing hydrology metrics, quality/readiness thresholds, support IDs,
  path/row policy, output schemas, or Goal 019/020 hashes;
- adding dependencies, CI, packages, compatibility wrappers, or migrations;
- broad documentation/ledger cleanup;
- commit or push in this execution pass. Publication follows review.

## Required Read-First Sources

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `README.md`
- `docs/project_brief.md`
- `docs/analysis_plan.md`
- `docs/hydrology_metric_spec.md`
- `docs/reproducibility_plan.md`
- `docs/validation_plan.md`
- `docs/data_stream_register.md`
- `docs/direct_s3_full_window_hydrology_019_report.md`
- `docs/direct_s3_full_window_hydrology_019_manifest.json`
- `docs/direct_s3_full_window_hydrology_020_audit_report.md`
- `docs/direct_s3_full_window_hydrology_020_manifest.json`
- `docs/direct_s3_full_window_hydrology_020_readiness.csv`
- `docs/goals/019-full-window-direct-s3-hydrology-production/Goal.md`
- `docs/goals/019-full-window-direct-s3-hydrology-production/Log.md`
- `docs/goals/020-production-hydrology-audit/Goal.md`
- `docs/goals/020-production-hydrology-audit/Log.md`
- all `scripts/*.py` and `settings/*.json` in the Goal 004-020 hydrology
  family that are needed to establish the graph and dispositions

## Starting-State Checks

- Confirm `main` is clean and synced after Goal 024 publication.
- Record HEAD and the four protected Goal 019/020 output hashes.
- Confirm no unexpected worktree changes, raw data, credentials, or private
  exports are present.
- Treat external callers as unknown unless directly evidenced; documentation
  references alone are historical evidence, not proof of active invocation.

## Protected Invariants

- Goal 019 direct-S3 production remains the canonical hydrology output for 11
  supports x 84 months = 924 support-month rows.
- Goal 020 readiness and quality classes, the 23 sensitivity-only rows, and
  the four Goal 018 comparator caveats remain unchanged and visible.
- Meaningful zeros, unsampled/missing values, Water Observations bit decoding,
  support-intersecting WRS path/rows, lag/novelty/persistence/drying metrics,
  and stable provenance hashes remain explicit.
- No ecological claim is upgraded from hydrology readiness alone; no bird
  records, effort assumptions, or eBird permissions are altered.

## Required Deliverables

- `docs/goals/025-hydrology-runtime-boundary-audit/Audit.md`: a concise audit
  report (target <= 250 lines) containing the active graph, script disposition
  table, temporal-logic comparison, protected invariants, evidence limits,
  and a recommended next implementation seam;
- this goal `Log.md` with starting state, evidence inspected, validation, and
  residual risks.

## Validation Gates

- static evidence includes exact file/line references for the active import
  chain and every disposition category;
- temporal comparison identifies any semantic difference rather than claiming
  equivalence from matching function names;
- all Goal 004-020 hydrology scripts are accounted for or explicitly grouped;
- the report contains no unsupported claim of zero external callers;
- `git diff --check` and local Markdown-link checks pass;
- no existing code, settings, tests, reports, or authoritative outputs are
  changed;
- final `git status --short --branch` and changed-file inventory are recorded.

## Stop Rules

Stop and report if the audit requires running external services, inspecting raw
data, changing scientific semantics, or deleting historical evidence. Stop
once the report supports a single next decision; do not turn this into a
second exploratory refactor.

## Final Response Requirements

Report the canonical graph, exact script disposition counts, temporal-logic
finding, evidence limits around external callers, proposed next seam, changed
files, validation results, protected hashes, and whether publication remains
pending review.
