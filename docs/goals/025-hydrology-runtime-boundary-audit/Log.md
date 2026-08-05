# Log

Goal: Hydrology runtime boundary and retirement audit

Status: Audit accepted and published.

## Supervisor Setup

- 2026-08-05: Goal 024 was accepted and published at `e121636`. Barry
  authorised continuation to the next highest-value tranche.
- 2026-08-05: This goal is an evidence-first, read-only audit. It must not
  delete, move, refactor, execute, or republish hydrology code or outputs.

## Execution Checkpoints

- 2026-08-05: Started from `/Users/bwbrook/papers/nomadic_waterbirds` on
  `main` at `e121636` (`main...origin/main`). The only pre-existing worktree
  change was the untracked Goal 025 packet directory; no source, settings,
  tests, reports, manifests, readiness outputs, or other goal packets were
  edited.
- 2026-08-05: Captured protected SHA-256 values before writing the audit:
  Goal 019 manifest
  `3b2f8c85a5f59168aebf914be4ec4eef68c09cdd48c1035d46d7cf21d6ab0cfc`, Goal
  019 series
  `793593532c2adb8e673f0ce70d72e97d5f0dba58a43dbfeba7a6b490480f26e8`, Goal
  020 manifest
  `ea3d95a619f80987309f4c4fde594a9a3b2113a43820464e715c121f4744c63a`, and
  Goal 020 readiness
  `3e26fd391f89a08877b2cde98fdd63d071c261a3415096fd7dd92cc1d2196e26`.
- 2026-08-05: Inspected `AGENTS.md`, README/project brief, analysis,
  hydrology metric, reproducibility, validation, and data-register contracts;
  Goal 019/020 packets, reports, manifests, readiness outputs and logs; all
  Goal 004-020 hydrology scripts/settings needed for the static graph; and
  local command/import references. No external caller was assumed absent.
- 2026-08-05: Static audit completed. Canonical graph is
  `019 -> 016 -> 014/013 -> 007 -> 005`, with Goal 020 as the audit consumer.
  Dispositions cover all 19 scripts: retain 7, simplify 1, defer 11, retire 0.
  Goal 007 and Goal 019 temporal derivations are not semantically equivalent:
  Goal 007 collapses missing prior history to `dry_prior=0`/False, while Goal
  019 preserves missingness as `None`, skips quality-fail rows, records partial
  history, adds rapid-drying, and computes regional metrics.
- 2026-08-05: Wrote `Audit.md` only; no runtime, settings, tests, reports,
  manifests, readiness outputs, or other packet changed. Recommended decision
  is to defer retirement/extraction until the temporal contract is explicit and
  parity can be proved.

## Review Notes

- 2026-08-05: Orchestrator review found no material defect. The audit supports
  deferring retirement/extraction and freezing the Goal 019/020 boundary.
- 2026-08-05: Barry authorised publication. The packet was committed and
  pushed as `884fad7` (`Goal 025: publish hydrology runtime boundary audit`).
  No runtime, settings, tests, or authoritative outputs changed.

## Validation

- `git diff --check`: passed after writing the deliverables.
- Before publication, `git status --short --branch` was
  `main...origin/main` with only the Goal 025 packet directory untracked; no
  unrelated paths appeared.
- Before publication, `git diff --name-only` was empty because the new packet
  files were untracked; the exact five packet files were then staged.
- Recomputed four protected hashes: unchanged from the starting values above.
- No tests, production execution, network/service access, STAC/S3/GDAL use,
  remote/HPC use, or raw-data inspection was performed during the audit.

## Publication

- Action repository is clean on `main...origin/main` at `884fad7`.
- The four protected hashes remain unchanged after publication.

## Residual Risks

- Unknown external human callers may still depend on historical scripts.
- Goal 019's coarse all-current-support regional peer set and Goal 007/019
  missingness split require an explicit contract decision before any extraction
  or retirement.
- Publication is complete. Any temporal-contract implementation seam remains
  pending a separately authorised development goal.
