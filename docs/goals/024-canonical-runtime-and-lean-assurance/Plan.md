# Plan

1. Read the Goal 024 packet and repository contract; capture clean starting
   state and authoritative Goal 019/020 output hashes.
2. Map the exact duplicated primitives and side effects in the Goal 021/022/023
   validators and tests. Do not generalise policy-specific checks.
3. Add the smallest shared pure helper module that removes exact duplication.
4. Refactor the three validators to use it and make ordinary validation
   read-only. Keep any manifest-writing path explicit and documented.
5. Remove or merge only tests that are demonstrably redundant; retain unique
   carry-forward, terms, effort, sensitivity, and submission-boundary checks.
6. Update the minimum runbook/README references needed to describe the new
   validation contract.
7. Run the validation ladder, check output hashes and worktree side effects,
   and record evidence in `Log.md`.
8. Stop for orchestrator review. Do not commit or push.

## Design Rules

- Prefer simple functions and standard-library code.
- Do not add compatibility wrappers or preserve obsolete invocation modes.
- Keep domain-policy logic in the validator where it is easiest to audit.
- Treat current Goal 019/020 artefacts as read-only release evidence.
- Keep this a single focused pass; do not start hydrology-core extraction or
  historical cleanup in the same goal.
