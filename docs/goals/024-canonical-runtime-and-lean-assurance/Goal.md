# Goal: Canonical Runtime And Lean Assurance

## Objective

Reduce the maintenance burden in the current validation surface without
changing the scientific hydrology contract or deleting historical hydrology
evidence. Establish the current canonical product boundary as:

`Goal 019 direct-S3 hydrology -> Goal 020 readiness audit -> Goals 021-023 metadata-only bird/access/eBird gate`

The completed goal must leave validation useful, deterministic, and
side-effect-free by default, while removing the most obvious duplicated
assurance machinery.

## Why This Matters

The repository has accumulated goal-by-goal scripts and validators. Goals
021-023 contain repeated file, hash, schema, link, and guardrail code, and
their validators rewrite tracked manifests when tests invoke them. That makes
routine assurance noisy and makes it difficult to tell a real scientific
change from a validation timestamp or bookkeeping change.

This is a low-risk first cleanup tranche. It should improve the active review
surface while deliberately leaving the hydrology algorithms, production
outputs, and historical route evidence alone until a later retirement
decision is made.

## Operating Mode

Local code-architecture cleanup and test/validator hygiene. No external data,
web requests, remote compute, model fitting, or eBird action.

## Scope

In scope:

- read this packet, the repo-local `AGENTS.md`, the current Goal 019/020
  reports and manifests, and the Goal 021/022/023 validators, tests, settings,
  and runbooks;
- baseline the current clean worktree and hashes of the authoritative Goal
  019/020 outputs before editing;
- introduce a small, pure shared helper module for genuinely identical
  validation primitives where doing so reduces duplication rather than adding
  a new framework;
- refactor the Goal 021/022/023 validators to use those primitives while
  keeping their semantic policy checks local and legible;
- separate validation from manifest generation: the normal validator/test
  path must not rewrite tracked files. If manifest generation is retained,
  make it an explicit, documented action;
- reduce or merge tests only where they duplicate the validator or another
  test. Keep unique policy and scientific-boundary tests;
- update only the minimum documentation/runbook text needed to describe the
  new deterministic validation contract;
- update this goal `Log.md` with the before/after inventory, changed files,
  validation evidence, and residual risks.

Out of scope:

- changing Goal 019 or Goal 020 algorithms, schemas, thresholds, readiness
  classes, support IDs, path/row selection, metric definitions, hashes, or
  committed production outputs;
- refactoring the Goal 005-020 hydrology runtime chain;
- deleting, moving, or renaming historical scripts, settings, manifests,
  tests, or goal packets;
- adding CI, a dependency manager, a package build system, or new third-party
  dependencies;
- broad documentation or ledger rewriting;
- downloading, opening, parsing, or validating biodiversity records;
- submitting or sending an eBird request, using credentials, browser sessions,
  or private request data;
- remote/HPC execution;
- committing or pushing the work. Publication is a later review decision.

## Required Read-First Sources

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `README.md`
- `HANDOFF.md`
- `docs/project_brief.md`
- `docs/reproducibility_plan.md`
- `docs/validation_plan.md`
- `docs/data_stream_register.md`
- `docs/direct_s3_full_window_hydrology_019_manifest.json`
- `docs/direct_s3_full_window_hydrology_020_manifest.json`
- `docs/direct_s3_full_window_hydrology_020_readiness.csv`
- `scripts/validate_bird_linkage_design_021.py`
- `scripts/validate_bird_data_access_022.py`
- `scripts/validate_ebird_request_intake_023.py`
- `tests/test_goal021_bird_linkage_design.py`
- `tests/test_goal022_bird_data_access.py`
- `tests/test_goal023_ebird_request_intake.py`
- the corresponding Goal 021/022/023 `Goal.md`, `Runbook.md`, and `Log.md`

## Starting-State Checks

- Confirm `git status --short --branch` is clean on `main` before editing.
- Record the current HEAD and SHA-256 hashes of the authoritative Goal 019/020
  CSV/JSON outputs.
- Confirm no raw biodiversity data, credentials, private exports, or new
  generated artefacts are present in the worktree.
- Treat any unexpected dirty state as a blocker; do not clean or revert it.

## Protected Invariants

- The current hydrology contract remains 11 supports x 84 months = 924 unique
  support-month rows for 2018-01 through 2024-12.
- Support-intersecting WRS path/row scene selection, Water Observations bit
  decoding, quality flags, missingness/zero semantics, and stable item/grid
  hashes remain unchanged.
- Goal 020 continues to expose all 23 sensitivity-only rows and permits core
  linkage only for `core_eligible` and `core_eligible_with_caveat`; the four
  Goal 018 comparator caveats remain visible.
- eBird remains human-gated and unsent; ALA remains context-only; species and
  guild choices remain provisional; no raw biodiversity records enter Git.
- Validation must remain proportional: one fast deterministic contract path
  plus substantive unique policy checks, not repeated manifest bookkeeping.

## Required Deliverables

- `scripts/validation_common.py`, containing only small pure primitives that
  are demonstrably shared by Goals 021-023;
- updated Goal 021/022/023 validators using the shared primitives and a
  read-only-by-default validation path;
- focused Goal 021/022/023 tests retaining unique policy boundaries and no
  longer relying on validator-created timestamps as test side effects;
- the minimum affected runbook/README text documenting validation versus
  explicit manifest generation;
- this Goal 024 packet and a complete `Log.md`.

## Validation Gates

- `python3 -m py_compile` for every changed Python file;
- focused Goal 021, 022, and 023 test modules;
- full local unittest discovery, if it remains side-effect-free after the
  change;
- direct invocation of the three validators in their default mode, followed
  by a clean-path check proving they did not rewrite tracked files;
- explicit manifest-generation checks only if that mode is retained;
- JSON parsing for affected settings/manifests;
- `git diff --check`;
- comparison showing no changes to Goal 019/020 authoritative output hashes or
  schemas;
- final `git status --short --branch` and a changed-file inventory.

## Stop Rules

Stop and report a blocker if:

- the change requires altering scientific outputs or Goal 020 classifications;
- a shared helper would obscure a policy distinction rather than remove exact
  duplication;
- tests or validators still mutate unrelated tracked files;
- a required check needs external data, credentials, browser access, or
  remote compute;
- the clean-up expands into historical-script retirement or a broad runtime
  refactor.

## Final Response Requirements

Report the canonical active path, exact changed files, before/after helper and
test inventory, validation commands and outcomes, proof that default
validation is side-effect-free, protected-output hash comparison, residual
risks, and whether any publication was deliberately left for review.
