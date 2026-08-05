# Log

Goal: Canonical runtime and lean assurance

Status: Implementation and validation complete; orchestrator accepted for publication.

## Supervisor Setup

- 2026-08-04: Barry authorised implementation of the first bounded cleanup
  tranche after a read-only `kill-your-darlings` sweep. The current canonical
  product boundary is Goal 019 direct-S3 hydrology, Goal 020 readiness audit,
  and metadata-only Goals 021-023.
- 2026-08-04: This goal is intentionally limited to validator/test hygiene
  and a small shared pure-helper surface. Hydrology algorithms, production
  outputs, historical scripts, external data, eBird actions, and publication
  are outside scope.

## Execution Checkpoints

- 2026-08-04: Starting state is `main` at `6f5f143015a7fce013ed716d7d98089b6ac05ac1`.
  The only pre-existing worktree change is this expected untracked Goal 024
  packet; no raw biodiversity data, credentials, private exports, or new
  generated artefacts were found. Protected output SHA-256 baselines are:
  Goal 019 manifest `3b2f8c85a5f59168aebf914be4ec4eef68c09cdd48c1035d46d7cf21d6ab0cfc`,
  Goal 019 series `793593532c2adb8e673f0ce70d72e97d5f0dba58a43dbfeba7a6b490480f26e8`,
  Goal 020 manifest `ea3d95a619f80987309f4c4fde594a9a3b2113a43820464e715c121f4744c63a`,
  and Goal 020 readiness `3e26fd391f89a08877b2cde98fdd63d071c261a3415096fd7dd92cc1d2196e26`.
- 2026-08-04: Exact shared duplication inventory: `read_json`, `read_csv`,
  and `file_hash` are repeated across validators 021-023; `stable_row_hash`
  is repeated in 022-023 and has a compatible 021 variant. Markdown-link and
  unfinished-marker expressions are also repeated, while policy validators
  remain goal-local. The pre-change validators all rewrite their tracked
  manifests, including a fresh `created_at_utc`, on ordinary execution.
- 2026-08-04: Added `scripts/validation_common.py` with four shared
  read-only/deterministic primitives (`read_json`, `read_csv`, `file_hash`,
  and `stable_row_hash`) plus the shared Markdown-link and unfinished-marker
  expressions. The three validators now import these primitives; their former
  12 duplicated helper definitions and six duplicated regex definitions are
  reduced to one shared implementation each. Domain-policy checks remain
  local to each validator.
- 2026-08-04: Ordinary validator execution is now read-only and reports
  `manifest unchanged`. Manifest writing is retained only behind the explicit
  `--write-manifest` flag and is documented separately in the Goal 021-024
  runbooks. Focused tests removed three exact schema assertions already covered
  by validators, added one default-read-only assertion per goal, and retained
  carry-forward, policy, submission-boundary, and guardrail tests (23 focused
  tests total).
- 2026-08-04: Validation passed: `py_compile` for all seven changed Python
  files; focused Goals 021-023 suite (23 tests); full discovery (98 tests);
  direct default invocation of all three validators with unchanged manifest
  hashes; explicit `--write-manifest` generation and JSON parsing in a
  temporary Git archive copy; affected settings/manifests JSON parsing; and
  `git diff --check`.
- 2026-08-04: Protected Goal 019/020 hashes remain exactly equal to the
  starting baselines. Changed files are the three validators, the shared
  helper, the three focused test modules, the three prior-goal runbooks, and
  this Goal 024 packet. Work remains uncommitted and unpublished for
  orchestrator review.

## Review Notes

- 2026-08-05: Orchestrator review accepted the scoped Goal 024 change for
  publication. Publication intent is limited to the reviewed paths recorded
  above; hydrology outputs, historical scripts, data, and eBird boundaries
  remain explicitly untouched.

- No commit or push is authorised by this packet. The action-agent worktree
  must remain available for orchestrator review.
- Residual risk: explicit manifest generation intentionally rewrites tracked
  Goal 021-023 manifests when requested; policy-specific validation remains
  distributed by design, and historical validators outside Goals 021-023 were
  not changed. No external data, credentials, eBird action, remote compute, or
  hydrology production path was used.
