# Goal: Bird Observation Linkage Design And Access Protocol

## Objective

Design the first constrained bird-observation linkage lane that can use the
Goal 019/020 hydrology covariate layer without yet downloading, requesting, or
processing biodiversity data.

This goal should produce a concrete, reviewable design for how bird
observations will later be joined to hydrology support-month rows, which data
streams can support which response layers, and what permission/access steps
must happen before ingestion.

## Why This Matters

Goal 020 concluded that the hydrology table is
`ready_for_constrained_bird_linkage_design`, with `820` `core_eligible`, `81`
`core_eligible_with_caveat`, and `23` `sensitivity_only` support-month rows.

The next project risk is not computation. It is scientific design: if eBird,
Birdata, ALA, or EAWS records are pulled into the repo before the observation
unit, effort/detectability assumptions, permissions, sensitive-record handling,
and hydrology join rules are explicit, the project can quietly become a static
occurrence exercise rather than a hydrological reaction-norm paper.

## Operating Mode

Observation-design, data-governance, and hydrology-linkage specification. No
biodiversity data acquisition. No model fitting. No ecological claims.

## Scope

In scope:

- read repo instructions, this goal packet, Goal 020 audit outputs, the data
  stream register, analysis/validation/manuscript plans, source evidence
  register, and literature triage materials already in the repo;
- check current public/official documentation for eBird, Birdata, ALA, and
  EAWS only as needed to verify access routes, fields, terms, or request
  requirements;
- define candidate observation units for a first constrained linkage design;
- specify how observation records would join to hydrology support-month rows;
- define response layers separately: occurrence/non-detection, relative count
  or abundance proxy, breeding evidence, and validation-only evidence;
- produce a candidate species/guild screen that is explicitly provisional and
  suitable for supervisor/lab-leader review, not a final species list;
- draft permission/request questions and data-handling constraints for eBird,
  Birdata, ALA, and EAWS;
- update project docs/registers/decision log and this goal log;
- commit and push the validated design package to private GitHub `main`.

Out of scope:

- downloading, requesting, or processing eBird, Birdata, ALA, EAWS, GBIF, or
  other biodiversity data;
- using private credentials, API tokens, existing local data exports, or web UI
  sessions;
- choosing a final species list or final guild membership;
- fitting models, generating maps from bird records, or estimating reaction
  norms;
- changing hydrology values, support definitions, quality thresholds, or Goal
  020 readiness classifications;
- launching remote/HPC jobs;
- committing raw data, private request files, credentials, geospatial exports,
  caches, parquet/SQLite/DuckDB stores, model outputs, or bulky artefacts.

## Required Read-First Sources

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `docs/goals/020-production-hydrology-audit/Goal.md`
- `docs/goals/020-production-hydrology-audit/Log.md`
- `docs/direct_s3_full_window_hydrology_020_audit_report.md`
- `docs/direct_s3_full_window_hydrology_020_manifest.json`
- `docs/direct_s3_full_window_hydrology_020_readiness.csv`
- `docs/direct_s3_full_window_hydrology_020_support_summary.csv`
- `docs/direct_s3_full_window_hydrology_020_month_summary.csv`
- `docs/hydrology_to_bird_linkage_gate_020.md`
- `docs/data_stream_register.md`
- `docs/analysis_plan.md`
- `docs/validation_plan.md`
- `docs/manuscript_plan.md`
- `docs/source_evidence_register.md`
- `docs/literature/deep_research_hydrological_reaction_norms_triage_2026-05-31.md`
- `docs/literature/source_verification_queue_2026-05-31.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `c4715f3` (`Complete Goal 020 hydrology
  audit and linkage gate`).
- Inspect available docs with `rg --files docs`.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Design Requirements

The design must explicitly carry forward the Goal 020 hydrology restrictions:

- use `core_eligible` and `core_eligible_with_caveat` rows for first core
  linkage designs;
- exclude the `23` `sensitivity_only` quality-fail rows from core fitting;
- retain sensitivity-only rows for coverage/sensitivity summaries;
- preserve the four Goal 018 legacy-comparator caveat rows as documented
  caveats, not blockers;
- do not use hydrology rows to make bird-response claims until observation
  data, effort, and validation gates are defined.

The design must separate:

- eBird complete-checklist lane: likely primary occurrence/non-detection and
  relative-count lane;
- Birdata lane: candidate standardised survey/calibration or sensitivity lane;
- ALA lane: taxonomy/range/context/presence-only lane, not absence inference;
- EAWS lane: independent validation or targeted abundance/breeding context,
  depending on access/reuse and wetland alignment.

The provisional species/guild screen must:

- be clearly labelled non-final;
- favour taxa/groups with plausible hydrological reaction-norm responses and
  likely observation support in the prototype wetlands;
- distinguish foraging/occurrence responses from colonial breeding responses;
- include data-stream fit, detectability/effort concerns, sensitive-record
  concerns, expected hydrological hypothesis, and recommended first-lane role;
- identify which choices require Barry/lab-leader approval before becoming a
  final analysis set.

## Required Deliverables

Create:

- `docs/bird_observation_linkage_design_021.md`: supervisor-facing design memo
  explaining the first observation-linkage lane, candidate observation units,
  response layers, hydrology restrictions, and recommended next step.
- `docs/bird_hydrology_join_contract_021.csv`: machine-readable join contract
  with fields for observation grain, hydrology key, spatial support rule,
  temporal rule, eligible hydrology classes, forbidden uses, and validation
  checks.
- `docs/bird_observation_unit_schema_021.csv`: proposed analyst-facing schema
  for future observation-unit tables, including field names, types, source
  streams, required/optional status, and privacy/sensitivity notes.
- `docs/candidate_species_guild_screen_021.csv`: provisional candidate
  species/guild screen for review, not a final species list.
- `docs/biodiversity_data_access_protocol_021.md`: request/access protocol and
  permission questions for eBird, Birdata, ALA, and EAWS.
- `docs/bird_linkage_design_021_manifest.json`: source files, public sources
  checked, row counts, hashes or schema fingerprints, decision status, and
  validation summary.
- `scripts/validate_bird_linkage_design_021.py`: lightweight validator for the
  schema/CSV/manifest outputs.
- `settings/bird_linkage_design_021.json`: expected file paths, row-count
  minima, controlled vocabularies, and validation settings.
- `tests/test_goal021_bird_linkage_design.py`: focused tests for required
  files, CSV schemas, controlled vocabularies, hydrology-readiness carryover,
  no-data-acquisition guardrails, and manifest consistency.

Update:

- `docs/data_stream_register.md`;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/021-bird-observation-linkage-design/Log.md`.

Update `docs/source_evidence_register.md` only if new public sources are
checked. Use stable source IDs and accessed dates.

## Validation Gates

Required validation:

- `git diff --check`;
- run `python3 scripts/validate_bird_linkage_design_021.py`;
- focused Goal 021 tests;
- full `python3 -m unittest discover -s tests -p 'test*.py'`;
- JSON parse for settings and manifest;
- CSV schema checks for the join contract, observation-unit schema, and
  species/guild screen;
- guardrail check that no raw biodiversity data, geospatial exports, caches,
  model outputs, or bulky files were created or committed;
- unfinished-marker scan;
- local Markdown link check;
- GitHub visibility check;
- final clean/synced `git status --short --branch`.

## Stop Rules

Stop and report a blocker if:

- Goal 020 artefacts are missing or inconsistent;
- current public source terms imply that the proposed data stream cannot be
  used for the intended role;
- the design cannot identify a defensible first observation unit without
  actual data access;
- validation gates fail;
- any biodiversity data are accidentally downloaded or generated.

If the work remains design-only and validation passes, commit and push the
design package and recommend Goal 022.

## Final Response Requirements

Report:

- headline design decision and recommended first observation-linkage lane;
- provisional candidate species/guild recommendation and what still needs
  lab-leader approval;
- data-access/request implications for eBird, Birdata, ALA, and EAWS;
- hydrology restrictions carried forward from Goal 020;
- changed files;
- validation commands and outcomes;
- commit hash and push status;
- residual risks;
- recommended Goal 022.
