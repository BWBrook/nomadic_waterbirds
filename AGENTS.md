# AGENTS.md - Nomadic Waterbirds

Repo-local operating instructions for agents working on the hydrological
reaction-norm paper for Australia's nomadic waterbirds.

## Project Thesis

The central ecological object is a hydrological reaction norm: how species and
guilds respond to current wetness, lagged wetness, hydroperiod persistence,
drying, wetting novelty after dry periods, and regional water availability.

Do not reframe this project as a static species distribution model. Wetlands
are dynamic ecological contexts, not fixed habitat points.

## Current Scope

- Start with eastern and inland Australia, especially the Murray-Darling Basin,
  Lake Eyre/Kati Thanda-connected systems where feasible, major eastern
  wetlands, and coastal drought-refuge systems.
- National expansion is allowed only after explicit quality-control and
  validation gates justify it.
- Treat colonial breeders separately from simpler foraging/occurrence
  responses because breeding depends on persistence and nesting conditions.
- Keep the first foundation phase to planning, governance, and reproducibility.

## Work Boundaries

Allowed without further approval:

- write or refine repo-local plans, registers, runbooks, and lightweight
  scaffold files
- add conservative ignore rules for generated data, caches, logs, model
  outputs, and manuscript build products
- run local validation commands that inspect files, Markdown, links, Git state,
  and repository hygiene
- commit and push validated foundation or documentation work when the worktree
  is clean and the relevant goal authorizes publication

Pause for Barry before:

- downloading, requesting, or processing external datasets
- choosing final species lists, guild membership, wetland-unit layers, model
  families, journal targets, or analysis geography beyond the scoped plan
- launching remote/HPC work
- adding heavyweight dependencies or environment managers
- making current factual claims from web or literature searches without doing
  those searches and citing sources

## Data Policy

- Treat eBird complete checklists as the likely primary citizen-science stream
  because checklist completeness supports stronger non-detection inference.
- Treat ALA records as presence, taxonomy, range, and historical-context
  material only unless metadata justify a narrower analytical role. Never use
  opportunistic ALA records as absences.
- Treat Birdata and Eastern Australian Waterbird Survey data as
  permission-sensitive streams until access, licensing, and intended analytical
  use are recorded.
- Do not commit raw external data, credentials, data-use agreements, API keys,
  private exports, or bulky derived products.
- Keep derived data reproducible from documented inputs where licensing allows;
  otherwise record provenance and expected rebuild instructions.

## Analysis Policy

- Model occurrence, relative abundance, and breeding evidence as distinct
  response layers when data support them.
- Make effort, detectability, checklist completeness, observer behaviour,
  temporal coverage, and sampling intensity visible in the design.
- Prefer interpretable hierarchical models, GAMMs, Bayesian additive models,
  INLA, Stan/TMB, or two-stage prediction-plus-inference designs over black-box
  leaderboard optimization.
- Report uncertainty for reaction curves, wetland ecological-role classes, and
  hindcasts.
- Do not overclaim causality; this is an observational synthesis of association,
  temporal response, and predictive structure.

## Validation Policy

- Random cross-validation is not acceptable as the main performance claim.
- Use spatial blocking, temporal blocking, hydrological-event blocking, and
  independent validation where possible.
- Include a synthetic sampling-bias stress test before relying on
  citizen-science hydrological response estimates.
- Treat validation evidence as incomplete unless it covers the claim being made.

## Compute Policy

- Default to this Mac mini for planning, document work, local checks, and small
  reproducibility tests.
- Do not use remote compute during foundation goals.
- For later heavy extraction, modelling, or geospatial work, choose compute
  deliberately and record the rationale in project notes before dispatching.
- When a goal explicitly authorises remote compute, prefer `deep-server` for
  CPU-heavy single-host Linux extraction, long remote-sensing loops, large
  geospatial staging, or runs likely to take more than about 30 minutes on the
  Mac mini.
- Use the Mac mini as the control plane for heavy work: prepare reproducible
  scripts and small local checks here, then stage source and ignored artefacts
  to the selected remote host when scale, runtime, or platform fit justify it.
- Do not downsize scientifically important event windows only to avoid using
  available remote compute. If a local run forces a scientifically weaker
  fallback, write a compute-routing memo and either run or recommend a
  `deep-server` rehearsal as authorised by the goal.
- GPU work should prefer Alien WSL when it fits dual RTX 2080 GPUs; use Nectar
  GPU only when more VRAM, throughput, isolation, or availability is needed.
  Use `kunanyi` only for production-grade multi-node or large job-array work.

## Manuscript And Reproducibility

- The manuscript build should connect to `/Users/bwbrook/work/makedoc` once
  substantive manuscript sources exist.
- Keep manuscript text, figures, tables, data dictionaries, model
  specifications, validation reports, and provenance logs clearly separated.
- Generated outputs belong under ignored or explicitly documented artifact
  paths, not as accidental source files.
- New workflows should be runnable from the repo with clear inputs, outputs,
  and provenance notes.

## Repo Documents

Foundation documents live under `docs/`:

- [project_brief.md](docs/project_brief.md)
- [analysis_plan.md](docs/analysis_plan.md)
- [data_stream_register.md](docs/data_stream_register.md)
- [reproducibility_plan.md](docs/reproducibility_plan.md)
- [validation_plan.md](docs/validation_plan.md)
- [manuscript_plan.md](docs/manuscript_plan.md)
- [decision_log.md](docs/decision_log.md)

## Action-Agent Reporting

For each goal:

- read the goal packet before editing
- update the goal `Log.md` at required checkpoints
- report changed files, validation commands and outcomes, commit hash, push
  status, residual risks, and recommended next goal when the goal asks for it
- keep final reports concise and evidence-backed
