# Goal: Data-Access And Wetland-Unit Feasibility Design

## Objective

Produce a current, source-backed feasibility package that tells the supervisor
which data streams and wetland-unit options are credible enough for the first
small prototype of the nomadic waterbirds paper workflow.

## Why This Matters

Goal 001 created the research foundation, but it deliberately did not verify
external data access, licensing, wetland-unit sources, or current provider
requirements. Before the project downloads data or chooses a spatial support,
we need a decision package grounded in current official sources.

The outcome should be a supervisor-ready recommendation for Goal 003, not a
dataset.

## Operating Mode

Full paper workflow plus current-source feasibility reconnaissance.

## Scope

In scope:

- verify current official access, licensing, citation, sensitivity, and
  redistribution constraints for candidate data streams
- identify and compare candidate wetland-unit sources or construction
  strategies
- recommend the smallest defensible prototype geography and wetland-unit
  strategy
- update project planning documents and decision logs
- cite current official sources with access dates
- commit and push the feasibility package if validation passes

Out of scope:

- downloading, requesting, or processing bulk external datasets
- submitting eBird, Birdata, EAWS, or other access requests
- logging into services or using private credentials
- final species-list, guild, wetland-unit, or model-family decisions
- hydrological extraction or biodiversity ingestion
- remote/HPC work
- manuscript drafting beyond feasibility notes

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/project_brief.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/analysis_plan.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/data_stream_register.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/reproducibility_plan.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/validation_plan.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/manuscript_plan.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/decision_log.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `23700b6` (`Record Goal 001 publication
  checkpoint`).
- Inspect the tree with `rg --files`.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Work

Create a feasibility package with these deliverables:

- `docs/source_evidence_register.md`: a current-source register with one row
  per checked source. Include source name, provider, URL, accessed date
  (`2026-05-30` unless actually different), what was verified, what remains
  unresolved, and whether the source is official/primary or secondary.
- `docs/data_access_feasibility.md`: a data-stream feasibility memo covering
  DEA Water Observations or the currently correct DEA water product, eBird
  complete checklists, Birdata, Atlas of Living Australia, Eastern Australian
  Waterbird Survey, climate covariates, static landscape covariates, and
  sensitive-record handling.
- `docs/wetland_unit_feasibility.md`: a comparison of candidate wetland-unit
  strategies. Consider named wetland polygons/complexes, grid-cell supports,
  basin/catchment supports, DEA-derived waterbody products if current sources
  support them, and hybrid strategies. Record pros, cons, licensing,
  hydrology-extraction feasibility, biodiversity-alignment feasibility,
  mapping/interpretability implications, and uncertainty implications.
- `docs/prototype_scope.md`: recommended smallest defensible prototype for
  Goal 003, including candidate geography, wetland units, temporal grain,
  hydrology metrics, biodiversity stream status, and the decision gates that
  must pass before scaling up.
- `docs/decision_memo_002.md`: a concise supervisor decision memo with a
  recommendation, alternatives considered, unresolved risks, and recommended
  Goal 003.
- updated `docs/data_stream_register.md` with verified status notes and next
  actions.
- updated `docs/decision_log.md` with the feasibility decisions made or
  deferred.
- updated `docs/goals/002-data-access-wetland-unit-feasibility/Log.md`.

## Source Standards

- Prefer official provider pages, official dataset documentation, official
  data catalogues, and official access/request pages.
- Use secondary sources only to interpret context, never as the sole evidence
  for access or licensing.
- Record access dates and URLs. Do not include long copied passages; paraphrase
  and use only short excerpts if needed.
- Separate verified facts from inferred implications and unresolved questions.
- If a source cannot be verified without login, request submission, or bulk
  download, record that limitation instead of working around it.

## Scientific Guardrails

- Do not choose the final wetland-unit system; recommend a prototype strategy.
- Do not treat ALA as an absence stream.
- Do not imply eBird, Birdata, or EAWS can be used until permission and terms
  are verified for the intended role.
- Keep hydrology central; climate/static covariates should support, not replace,
  hydrological reaction norms.
- Keep validation and uncertainty implications visible when comparing wetland
  units.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- confirm no data files larger than 5 MB were added
- inspect new Markdown files for unresolved stub language
- verify all local Markdown links in new or edited docs resolve
- confirm all current-source claims in the feasibility docs are backed by rows
  in `docs/source_evidence_register.md`

If validation passes, commit and push the feasibility package to `main`.

## Checkpoint Rules

Update `docs/goals/002-data-access-wetland-unit-feasibility/Log.md` when:

- starting state is confirmed
- source evidence register has first pass entries
- data-access feasibility memo is drafted
- wetland-unit feasibility memo is drafted
- prototype recommendation and decision memo are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- choose official sources to inspect
- add feasibility documents and update existing planning docs
- recommend a prototype geography and wetland-unit strategy
- recommend the next goal based on evidence
- commit and push validated feasibility documentation

Pause and ask Barry before:

- downloading datasets
- submitting access requests
- using credentials or private portals
- making a final wetland-unit or species/guild decision
- narrowing the project thesis or first operational geography beyond the brief
- adding analysis dependencies or executable extraction code
- launching remote compute

## Stop Conditions

Stop when one of these is true:

- the feasibility package is complete, validated, committed, and pushed
- current official sources cannot answer a key access question and a human
  decision is needed
- the work would require data downloads, private access, or final scientific
  choices outside this goal

## Final Response Requirements

Report:

- what changed
- official/current sources checked at a high level
- recommended prototype strategy
- exact validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual risks and unresolved permission questions
- recommended Goal 003
