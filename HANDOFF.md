# Nomadic Waterbirds: Successor Handoff

Updated: 2026-09-05

This is the restart note for a fresh agent working directly in
`/Users/bwbrook/papers/nomadic_waterbirds`. Start here rather than rebuilding
context from old orchestration threads. Historical goal records are scientific
provenance, not a workflow that must be reenacted.

Baseline before this edit: clean `main...origin/main` at `96de836`. Expect only
`HANDOFF.md` to be modified until Barry chooses to commit it.

## Start Here

1. Read `AGENTS.md` and this file.
2. Check `git status --short --branch` and the latest commits before editing.
3. Read `docs/project_brief.md`, `docs/analysis_plan.md`, and recent entries in
   `docs/decision_log.md`.
4. Ask Barry whether the eBird request is unsent, submitted, or delivered. The
   last confirmed state is below; do not infer that a planned action occurred.
5. Read only the stage-specific files under "Where To Resume".

## Scientific Destination

Estimate interpretable hydrological reaction norms for Australian nomadic and
wetland-dependent waterbirds: how occurrence, relative counts, and where
possible breeding evidence respond to current wetness, lagged wetness,
hydroperiod persistence, drying, wetting novelty after dry periods, and
regional water availability.

The intended synthesis should classify wetland roles with uncertainty, such as
drought refuge, flood-pulse foraging site, breeding-support wetland, or
stepping-stone. Do not turn this into a static species distribution model. The
scientific object is response to pulsed water through time, with explicit
observation processes and appropriately blocked validation.

## Current Scientific State

### Hydrology is ready for the pilot

- Goal 019 is the canonical DEA Water Observations production layer.
- It covers 11 supports across Macquarie Marshes, Narran Lake Nature Reserve,
  Gwydir Wetlands, Kerang Wetlands, and Currawinya Lakes.
- The window is `2018-01` through `2024-12`: 924 support-month rows.
- Goal 020 classified 820 rows as `core_eligible`, 81 as
  `core_eligible_with_caveat`, and 23 as `sensitivity_only`.
- Four Goal 018 legacy-comparator caveats remain visible.
- Meaningful dry zeros are evidence. Missing, blocked, or insufficient-quality
  observations are not ecological zeros.

### The bird-data design is ready, but no bird data exist here yet

- Goal 021 defined a `support_id x month` linkage and kept
  occurrence/non-detection, relative count, and breeding evidence separate.
- Goal 022 selected eBird Basic Dataset complete checklists plus sampling-event
  and effort metadata as the primary pilot lane.
- Birdata and Eastern Australian Waterbird Survey remain permission-dependent
  secondary or validation streams.
- ALA is taxonomy, range, historical occurrence, and context only. Never use
  opportunistic ALA records as absences.
- Species and guild choices remain provisional. Colonial breeding responses
  must remain distinct from simpler occurrence or foraging responses.
- No fitted bird model, reaction curve, wetland-role result, or ecological
  inference exists yet.

### Request and intake preparation is complete

Goal 023 produced a paste-ready eBird request, human submission checklist,
ignored-path intake plan, and QA contract. It did not acquire or process bird
records.

Barry last confirmed on 2026-08-05 that he had not submitted the request and
intended to do so himself. There is no later confirmation in this repository.
Verify the live state with him.

The prepared request is deliberately bounded:

- eBird Basic Dataset observations plus sampling-event/checklist effort data;
- complete-checklist, observation-aware use;
- `2018-01-01` through `2024-12-31`;
- the current 11 Goal 020 supports across the five named complexes;
- provisional Goal 021 taxa/guilds, not a final species list;
- raw delivery private and outside Git;
- final submit/send by Barry or an explicitly authorised human.

If assisting with submission, recheck current official eBird product and terms
information because the source review dates from 2026-06-01. Do not use
credentials, fill a live form, or submit anything without Barry's explicit
action-time authorization.

## Where To Resume

### If the request is unsent

Read:

- `docs/ebird_request_submission_checklist_023.md`
- `docs/ebird_request_text_023.md`
- `docs/ebird_pilot_request_package_022.md`

The next action is Barry's review and human submission. Do not invent work to
fill the wait. A dry task is worthwhile only if it resolves a real scientific
decision.

### If submitted but no delivery has arrived

Record only safe metadata supplied by Barry: submission date, request or
confirmation reference, requested products and fields, purpose version, and
terms or sensitive-record constraints. Do not store private responses,
credentials, screenshots, or raw data in Git.

A compact discussion of pilot taxa/guild hypotheses or the bias stress test is
useful only if it advances a decision rather than speculative infrastructure.

### If a delivery has arrived

Read:

- `docs/ebird_intake_staging_plan_023.md`
- `docs/ebird_intake_qa_contract_023.csv`
- `docs/ebird_required_fields_022.csv`
- `docs/bird_hydrology_join_contract_021.csv`

Begin with metadata-only intake and quarantine: inventory without opening
record contents, place files under an approved ignored path, record checksums
and product identity, establish terms/citation and sensitive-record rules, and
confirm that observations and sampling-event metadata are both present. Only
after these gates pass should a separately authorized stage inspect headers,
assess coverage, or parse rows.

Ingestion is not analysis readiness. The next decisions depend on checklist
coverage, effort-field completeness, support assignment, shared-checklist and
duplicate handling, sensitive-location precision, and numeric counts versus
present-only `X` records.

## Protected Scientific Boundaries

- Keep the Goal 019/020 hydrology outputs and readiness classes fixed unless a
  new scientific goal explicitly changes and validates the contract.
- Keep `sensitivity_only` rows visible but outside core fitting.
- Model effort, detectability, checklist completeness, sampling intensity, and
  repeated/shared checklists when required by the estimand.
- Keep occurrence, relative count, and breeding evidence distinct.
- Never infer absence from incomplete or opportunistic records.
- Use spatial, temporal, and hydrological-event blocking for central claims;
  random folds may be secondary diagnostics only.
- Include a synthetic sampling-bias stress test before relying on
  citizen-science reaction norms.
- Report uncertainty and do not present observational associations as causal.
- Discuss final species/guild scope, model family, expanded geography, or
  wetland units with Barry after relevant data diagnostics exist.

## Code State And Restraint

Goal 024 made the Goal 021-023 validators read-only by default; manifest
regeneration requires `--write-manifest`. The full suite last recorded 98
passing tests on 2026-08-05.

Goal 025 audited the active hydrology chain:

`019 -> 016 -> 014/013 -> 007 -> 005`, with Goal 020 as audit consumer.

Goal 007 and Goal 019 have different temporal missingness semantics. Goal 019
quality-filters lag history and preserves unavailable history. The accepted
decision was to freeze Goal 019/020 and defer broad hydrology refactoring or
retirement until a concrete scientific consumer earns it. Do not begin another
general cleanup pass before new science.

Read `docs/goals/025-hydrology-runtime-boundary-audit/Audit.md` only if
hydrology is being changed or questioned.

## Working Contract And Skills

The governing principle is:

> Rigour at the scientific decision boundary; proportional engineering
> everywhere else.

Barry wants an assertive senior collaborator. Make routine, reversible,
testable choices autonomously. Consult him when his ecological judgment or
authority could materially change the question, estimand, species/guild scope,
observation model, interpretation, privacy or licensing risk, compute
commitment, public action, or project direction.

Use `/Users/bwbrook/.codex/skills/twilight-laboratory/SKILL.md` as the primary
workflow for the multi-stage scientific programme: set a meaningful reporting
horizon, protect decision boundaries, use workers selectively, and return at a
scientific gold stamp rather than after every internal step.

Use `/Users/bwbrook/.codex/skills/kill-your-darlings/SKILL.md` when accumulated
code, tests, outputs, or workflow machinery impede the current question. It is
a pruning discipline, not a reason to repeat repository-wide audits. The two
accepted cleanup passes are enough for now.

Ordinary work now begins directly in this repository. `chief_of_staff`,
`goal_composer`, the old named agent `nomad`, mandatory thread gates, and
mandatory four-file goal packets are retired workflow machinery. Use native
subagents only for substantial bounded work where parallelism or an independent
check is genuinely useful, and inspect their evidence directly.

Complete the high-value core, verify evidence that could change the decision,
perform one focused repair pass, and stop when the remainder is polish. Commit,
push, publish, use remote compute, access gated data, or take external actions
only when the current request authorizes them.

## Immediate Successor Decision

The project is `awaiting external input`, not `in execution`. Establish whether
the eBird request is unsent, submitted, or delivered, then recommend one
coherent scientific tranche. Do not reopen hydrology or engineering cleanup
unless the live science exposes a material need.
