# Plan

1. Confirm the clean post-Goal-024 baseline and capture protected hashes.
2. Read the current hydrology contract and Goal 019/020 evidence.
3. Build a static import/command graph and script inventory with line counts,
   entry points, settings, tests, and repository-local callers.
4. Compare Goal 007 and Goal 019 temporal derivation semantics using source
   reading and small in-memory examples only.
5. Classify every Goal 004-020 hydrology script as retain, simplify, retire,
   or defer, recording evidence and confidence.
6. Write the concise `Audit.md`; do not edit existing runtime or evidence.
7. Run link/diff/worktree checks and update `Log.md`.
8. Stop for orchestrator review; do not commit or push.

## Design Rules

- Evidence before deletion or extraction.
- Distinguish observed repository references from inference about use.
- Prefer one canonical runtime seam and one independent audit consumer.
- Do not add a new ledger or machine-readable inventory unless it materially
  reduces ambiguity in the report.
