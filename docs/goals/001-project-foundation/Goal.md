# Goal: Project Foundation And Reproducible Research Contract

## Objective

Turn Barry's project brief into an executable, repo-local foundation for a
publishable and fully reproducible paper on hydrological reaction norms of
Australia's nomadic waterbirds.

## Why This Matters

This project is starting from a clean scaffold. Before any data acquisition,
hydrology extraction, species filtering, or model fitting, the repo needs a
durable operating contract that keeps the work focused on dynamic hydrological
reaction norms rather than drifting into a static SDM or loosely documented
data exercise.

The desired outcome of this goal is not analysis results. It is the research
architecture that will let later agents work ambitiously and safely.

## Operating Mode

Scientific project foundation plus reproducible workflow design.

## Scope

In scope:

- create repo-local operating instructions for future agents
- convert the project brief into a staged analysis plan
- create a data-stream and data-access register
- specify the first-pass wetland, hydrology, biodiversity, validation, and
  manuscript work packages
- define review surfaces and pause boundaries for future goals
- add lightweight reproducibility scaffolding only where it is clearly useful
- commit and push the foundation package if validation passes

Out of scope:

- downloading, requesting, or processing real biodiversity or remote-sensing
  data
- choosing a final species list or final wetland-unit layer
- fitting statistical models
- running web/literature searches and presenting claims as current evidence
- launching remote/HPC jobs
- drafting substantive manuscript text beyond structure, outline, and build
  pathway notes
- adding heavyweight dependencies before the workflow stack is justified

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/README.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/project_brief.md`
- `/Users/bwbrook/work/makedoc/README.md`, if present, only enough to
  understand how a later manuscript build should connect to `makedoc`

If a repo-local instruction file is created during this goal, follow it after
creation for the remainder of the run.

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the latest commit is the initial scaffold unless the repo has moved
  forward.
- Inspect the existing tree with `rg --files`.
- Treat any unexpected dirty state as a blocker unless it is only the goal files
  you are executing.

## Required Work

Create a foundation package that includes, at minimum:

- `AGENTS.md` with repo-local operating rules, compute policy, data policy,
  validation expectations, manuscript/reproducibility expectations, and
  action-agent reporting rules.
- `docs/analysis_plan.md` translating the brief into research questions,
  hypotheses, estimands, candidate model families, ecological interpretation
  boundaries, and staged analysis phases.
- `docs/data_stream_register.md` recording each proposed data stream, its role,
  expected access route, likely license or permission issue, current status,
  inclusion/exclusion rule, and next action. Include DEA Water Observations,
  eBird complete checklists, Birdata, ALA, Eastern Australian Waterbird Survey,
  climate/static covariates, and any required wetland-unit source.
- `docs/reproducibility_plan.md` defining the intended repo structure,
  environment strategy, generated artefact policy, provenance logging,
  manuscript build pathway through `makedoc`, and archive expectations.
- `docs/validation_plan.md` defining spatial, temporal, hydrological-event, and
  synthetic-bias validation. Explicitly reject random cross-validation as the
  main validation claim.
- `docs/manuscript_plan.md` with target contribution, likely journal framing,
  figure/table plan, and the evidence required for each central claim.
- `docs/decision_log.md` with dated entries for foundation decisions made in
  this goal.
- `docs/goals/001-project-foundation/Log.md` updated throughout the run.

Add any small supporting files that make the foundation genuinely executable,
such as `.gitignore`, `docs/README.md`, `data/README.md`, `artifacts/README.md`,
or `manuscript/README.md`. Keep these lightweight and policy-oriented.

## Scientific Guardrails

- The central object is hydrological reaction norms: response to current water,
  hydrological history, persistence, drying, novelty after dry periods, and
  surrounding regional water availability.
- Do not reframe the paper as a static species distribution model.
- Do not treat ALA records as absences.
- Do not bury effort, detectability, checklist completeness, or sampling
  intensity.
- Do not propose maps or wetland classifications without uncertainty.
- Do not overclaim causal inference from observational data.
- Keep the first operational geography focused on eastern and inland Australia
  unless the plan explains why a smaller prototype is needed first.

## Deliverables

- repo-local operating guide: `AGENTS.md`
- analysis plan: `docs/analysis_plan.md`
- data stream register: `docs/data_stream_register.md`
- reproducibility plan: `docs/reproducibility_plan.md`
- validation plan: `docs/validation_plan.md`
- manuscript plan: `docs/manuscript_plan.md`
- decision log: `docs/decision_log.md`
- optional lightweight supporting README/scaffold files
- updated goal log:
  `/Users/bwbrook/papers/nomadic_waterbirds/docs/goals/001-project-foundation/Log.md`
- final response with changed files, validation, Git commit/push status,
  residual risks, and recommended Goal 002

## Validation Gates

The goal is complete only when these have passed or a blocker is clearly
recorded:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- confirm no large data files were added
- inspect all new Markdown files for broken local links or unfinished stub
  language
- if any executable scripts/configuration files are added, run the narrow
  syntax or smoke checks appropriate to them

If validation passes, commit and push the foundation package to `main`.

## Checkpoint Rules

Update `docs/goals/001-project-foundation/Log.md` when:

- starting state is confirmed
- the operating guide is drafted
- the main planning documents are drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- choose document names and lightweight repo folders that fit the foundation
  purpose
- write first-pass plans and registers using Barry's brief
- add conservative ignore rules for generated data, artefacts, caches, and
  manuscript build outputs
- commit and push this foundation work if the repo is otherwise clean and
  validation passes

Pause and ask Barry before:

- downloading, requesting, or processing external datasets
- making final species/guild, wetland-unit, or model-family choices
- changing the central research aim
- using remote/HPC compute
- adding heavyweight language/toolchain dependencies
- making current factual claims from web or literature searches without doing
  the search and citing sources

## Stop Conditions

Stop when one of these is true:

- the foundation package is complete, validated, committed, and pushed
- an unexpected dirty state or access problem prevents clean publication of the
  goal output
- the work requires a scientific choice that should be made by Barry before
  proceeding

## Final Response Requirements

Report:

- what changed
- exact validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual scientific/project risks
- recommended Goal 002
