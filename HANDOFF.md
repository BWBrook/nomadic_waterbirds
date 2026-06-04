# nomadic_waterbirds Handoff

Date: 2026-06-04

This note is for the next Codex thread taking over the
`/Users/bwbrook/papers/nomadic_waterbirds` action repo after the current
orchestration-location migration and thread archive.

## Current State

- The repo is clean and synced at `main` as of commit `5e63794`:
  `Fix Goal 023 completion status`.
- Goal 023 is completed as a metadata-only eBird request-support and future
  intake-staging package.
- No eBird request has been submitted by Codex, no live web form has been
  filled, no credentials have been used, and no raw biodiversity data has been
  downloaded, opened, staged, parsed, transformed, or validated.
- The Goal 023 log status correction has been made:
  `docs/goals/023-ebird-request-support-intake-staging/Log.md` now records
  `Status: Completed.`

## Key Project Context

- The project is a goal-packet driven scientific repo. For new work, start from
  the relevant `docs/goals/<goal-id>/Goal.md`, then `Plan.md`, `Runbook.md`,
  and keep `Log.md` updated during execution.
- The hydrology-to-bird linkage lane is deliberately constrained. Goals 020,
  021, 022, and 023 form the current chain:
  - Goal 020 audited hydrology-production readiness and restrictions.
  - Goal 021 defined the first constrained bird-observation linkage design.
  - Goal 022 prepared biodiversity data access feasibility and request scope.
  - Goal 023 prepared eBird request-submission support and future intake QA
    without submitting the request or handling bird records.
- Goal 020 hydrology restrictions and support readiness classes must continue
  to be carried forward exactly unless a future approved goal explicitly
  changes them.
- Candidate species/guild choices remain provisional and reviewable. Do not
  treat them as a final species list.

## Goal 023 Artifacts

The completed Goal 023 package includes:

- `docs/ebird_request_submission_checklist_023.md`
- `docs/ebird_request_text_023.md`
- `docs/ebird_intake_staging_plan_023.md`
- `docs/ebird_intake_qa_contract_023.csv`
- `docs/ebird_request_023_manifest.json`
- `settings/ebird_request_intake_023.json`
- `scripts/validate_ebird_request_intake_023.py`
- `tests/test_goal023_ebird_request_intake.py`

Shared project context was also recorded in:

- `docs/README.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

## Thread And Orchestration Relationships

- Barry is the human project owner and must directly confirm any final eBird
  submit/send action at action time.
- This repo is the action repo for the science work. The broader supervisor /
  orchestration side has been moving through `goal_composer`; do not assume
  old thread locations remain authoritative during the wholesale migration.
- Previous supervision context accepted the hierarchy in which Barry directs
  the supervisor/orchestrator layer, and the action repo executes bounded goal
  packets. The next thread should treat repo-local goal packets as the source
  of truth for action-repo work.

## Risks And Guardrails

- The largest immediate risk is accidentally crossing the human-submission
  boundary for eBird. Do not submit, send, log in, use Barry's account, inspect
  credentials, or fill a live form unless Barry gives direct action-time
  confirmation for that specific action.
- Keep all future raw eBird delivery under ignored paths such as `data/*`.
  Commit only metadata, manifests, QA contracts, scripts, and documentation
  that are safe for Git.
- Do not use ALA for absence or non-detection inference. Keep it context-only
  unless a later approved goal changes the access design.
- Keep Birdata and EAWS as permission-question or validation candidates, not
  primary complete-checklist lanes.
- eBird remains the primary complete-checklist pilot lane, scoped to the EBD
  complete-checklist product with sampling-event/effort metadata for
  `2018-01-01` through `2024-12-31`, the current 11 Goal 020 hydrology
  supports, and provisional Goal 021 species/guild scope.

## Recommended Next Actions

- If Barry is ready, the next human-facing step is to review the Goal 023
  request package and decide whether to submit/send the eBird request. That
  final action requires Barry's direct confirmation at action time.
- After any eBird delivery exists, the next repo goal should be a
  metadata-only intake provenance and quarantine QA goal before opening,
  parsing, or transforming records.
- If the orchestration migration changes where goal packets are created,
  linked, or reviewed, record the new relationship in the repo before starting
  substantive science work.

## Caveats

- This handoff was written during a post-completion repo handoff request, not
  as a new project goal. It should not be interpreted as validation evidence or
  a new approval to proceed.
- No tests, validators, browsing, eBird actions, credential checks, raw-data
  inspection, or new goal work were run for this handoff note.
