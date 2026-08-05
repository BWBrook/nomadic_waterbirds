# Runbook

## Start

Run from the action repository root:

```bash
cd /Users/bwbrook/papers/nomadic_waterbirds
git status --short --branch
git rev-parse --short HEAD
shasum -a 256 docs/direct_s3_full_window_hydrology_019_manifest.json
shasum -a 256 docs/direct_s3_full_window_hydrology_019_series.csv
shasum -a 256 docs/direct_s3_full_window_hydrology_020_manifest.json
shasum -a 256 docs/direct_s3_full_window_hydrology_020_readiness.csv
```

Read `AGENTS.md`, this goal packet, the required contract documents, and the
Goal 019/020 reports and logs before making the inventory.

## Static Runtime Inventory

Use read-only commands to inspect the hydrology family:

```bash
rg -n '^(from|import) |sys\.path|subprocess|python3 scripts/|def (run|main)\b' scripts docs settings
find scripts settings -maxdepth 1 -type f -print | sort
wc -l scripts/*.py settings/*.json
```

Trace imports, direct script invocations, settings references, and documented
commands. Record file and line numbers in `Audit.md`. A repository reference is
evidence of a local dependency or historical mention, not proof of an external
caller.

## Temporal Comparison

Read the complete implementations of Goal 007 temporal derivation and Goal
019 derived metrics, including their quality, blocked-row, missingness, lag,
novelty, persistence, drying, and regional branches. Use only small in-memory
examples or source-level reasoning. Do not call STAC, S3, GDAL, production
entry points, remote machines, or any data extraction path.

State semantic differences explicitly. Matching names or similar formulas are
not evidence of equivalence. Preserve the current Goal 019 and Goal 020 output
hashes throughout.

## Audit Deliverable

Write only:

```text
docs/goals/025-hydrology-runtime-boundary-audit/Audit.md
docs/goals/025-hydrology-runtime-boundary-audit/Log.md
```

`Audit.md` should stay concise (target 250 lines or fewer) and include:

- canonical active graph and line-evidenced local callers;
- a disposition table covering every Goal 004-020 hydrology script, or an
  explicit grouped row that names every member;
- temporal-logic comparison and its scientific/provenance implications;
- canonical inputs, outputs, consumers, and protected invariants;
- evidence limits, especially unknown external human workflows;
- one smallest defensible next implementation seam, or a clear defer decision.

Do not edit existing scripts, settings, tests, reports, manifests, readiness
outputs, or other goal packets.

## Validation And Stop

Before reporting completion:

```bash
git diff --check
git status --short --branch
git diff --name-only
```

Confirm the diff contains only the new Goal 025 audit packet files, the four
protected hashes are unchanged, and all Markdown links used in the report
resolve within the repository. Do not commit or push. Stop after the audit
supports one next decision; return the evidence and any blocker to the
orchestrator for review.
