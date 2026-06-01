# Goal: Bird Data Access Feasibility And Request Package

## Objective

Prepare a bounded, evidence-backed bird-data access feasibility package for
the first observation-linkage lane defined in Goal 021, without submitting any
requests, logging into services, downloading biodiversity records, or
processing private/gated data.

The main output should be a request-ready eBird complete-checklist pilot
package, plus clear permission/role decisions for Birdata, EAWS, and ALA.

## Why This Matters

Goal 021 concluded that the project is
`ready_for_bird_data_access_feasibility` and recommended eBird complete
checklists as the first constrained lane. The next risk is getting the access
envelope wrong: if the pilot request omits sampling-event metadata, uses an
over-broad spatial scope, conflates ALA presence records with non-detections,
or forgets sensitive-location restrictions, the downstream hydrology-response
analysis will be compromised before modelling starts.

This goal should convert the design into a disciplined access and feasibility
package that Barry can review and use for real data requests.

## Operating Mode

Data-access feasibility, source verification, request drafting, and governance
design. No data acquisition. No ecological modelling. No final species list.

## Scope

In scope:

- read repo instructions, this goal packet, Goal 020/021 outputs, the data
  stream register, source evidence register, analysis/validation/manuscript
  plans, and relevant literature support already in the repo;
- check current official/public documentation for eBird, Birdata, ALA, and
  EAWS access routes, terms, fields, data products, sensitive-record handling,
  and citation/reuse requirements;
- define a bounded eBird pilot request envelope for the current hydrology
  supports and date window;
- identify the required eBird products/fields needed for complete-checklist,
  effort-aware occurrence/non-detection and relative-count design;
- prepare a draft eBird request/purpose statement Barry could review and
  submit outside this goal;
- prepare Birdata and EAWS permission-question briefs for later contact;
- formalise ALA as context-only and document what it may and may not support;
- produce a machine-readable access feasibility matrix and field mapping;
- update docs/registers/decision log and this goal log;
- commit and push the validated package to private GitHub `main`.

Out of scope:

- submitting data requests or filling web forms;
- using private credentials, API tokens, local exports, browser login sessions,
  or email;
- downloading, requesting, scraping, staging, transforming, or validating
  biodiversity records;
- choosing a final species list or final guild membership;
- fitting occupancy, count, reaction-norm, POM, GAM, GLMM, or other models;
- changing hydrology tables, support definitions, quality thresholds, or Goal
  020/021 classifications;
- committing raw data, private request responses, credentials, geospatial
  exports, caches, parquet/SQLite/DuckDB stores, model outputs, or bulky
  artefacts;
- launching remote/HPC jobs.

## Required Read-First Sources

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `docs/goals/021-bird-observation-linkage-design/Goal.md`
- `docs/goals/021-bird-observation-linkage-design/Log.md`
- `docs/bird_observation_linkage_design_021.md`
- `docs/bird_hydrology_join_contract_021.csv`
- `docs/bird_observation_unit_schema_021.csv`
- `docs/candidate_species_guild_screen_021.csv`
- `docs/biodiversity_data_access_protocol_021.md`
- `docs/bird_linkage_design_021_manifest.json`
- `docs/hydrology_to_bird_linkage_gate_020.md`
- `docs/direct_s3_full_window_hydrology_020_readiness.csv`
- `docs/direct_s3_full_window_hydrology_020_support_summary.csv`
- `docs/data_stream_register.md`
- `docs/source_evidence_register.md`
- `docs/analysis_plan.md`
- `docs/validation_plan.md`
- `docs/manuscript_plan.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `813476d` (`Design bird observation
  linkage lane`).
- Inspect available docs with `rg --files docs`.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Design Requirements

Carry forward all Goal 020/021 restrictions:

- core bird-linkage design may use only `core_eligible` and
  `core_eligible_with_caveat` hydrology rows;
- the 23 `sensitivity_only` rows must remain outside core fitting and visible
  for coverage/sensitivity accounting;
- the four Goal 018 caveat rows remain caveated, not dropped;
- ALA must never be used for absence/non-detection inference;
- Birdata and EAWS remain secondary/validation lanes until permissions and
  field structures are confirmed;
- no final species/guild lock-in without Barry/lab-leader review.

The eBird pilot package must explicitly specify:

- product/request components required, including complete-checklist and
  sampling-event/effort metadata needs;
- date window, spatial envelope, and hydrology support relationship;
- candidate species/guild handling, including which rows remain lab-review
  gated;
- minimum fields required for checklist identity, date, duration, distance,
  party size, protocol, effort, count, complete-list status, coordinates or
  spatial precision, sensitive-record status, taxonomy, and location metadata;
- exclusion flags or risk flags for incomplete checklists, incidental records,
  low-effort metadata, private/suppressed coordinates, and ambiguous support
  assignment;
- expected analyst-facing derived tables, but not the derived tables
  themselves.

The permission matrix must separate:

- `request_ready`: ready for Barry review/submission;
- `needs_clarification`: questions must be resolved before request;
- `context_only`: permitted for context/provenance, not response inference;
- `defer`: not suitable for the first pilot lane.

## Required Deliverables

Create:

- `docs/bird_data_access_feasibility_022.md`: supervisor-facing memo with the
  access recommendation, source checks, feasibility status by stream, and
  recommended next step.
- `docs/ebird_pilot_request_package_022.md`: request-ready eBird pilot
  package, including purpose statement, scope, products/fields needed,
  inclusion/exclusion rules, sensitive-record handling, and submission notes.
- `docs/bird_data_access_matrix_022.csv`: machine-readable stream-level
  feasibility matrix for eBird, Birdata, EAWS, and ALA.
- `docs/ebird_required_fields_022.csv`: field-level eBird request/ingestion
  needs, with role, required status, downstream use, and validation rule.
- `docs/birdata_eaws_permission_questions_022.md`: concise permission brief
  for Birdata and EAWS.
- `docs/ala_context_rules_022.md`: explicit ALA context-only rules and
  forbidden uses.
- `docs/bird_data_access_022_manifest.json`: source files, official pages
  checked, row counts, decision status, and validation summary.
- `scripts/validate_bird_data_access_022.py`: lightweight validator for the
  CSV/Markdown/manifest package.
- `settings/bird_data_access_022.json`: expected file paths, row-count minima,
  controlled vocabularies, and validation settings.
- `tests/test_goal022_bird_data_access.py`: focused tests for required files,
  CSV schemas, controlled vocabularies, no-data-acquisition guardrails,
  manifest consistency, and Goal 020/021 carry-forward.

Update:

- `docs/data_stream_register.md`;
- `docs/source_evidence_register.md` if any new or updated public sources are
  checked;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/022-bird-data-access-feasibility/Log.md`.

## Validation Gates

Required validation:

- `git diff --check`;
- run `python3 scripts/validate_bird_data_access_022.py`;
- focused Goal 022 tests;
- full `python3 -m unittest discover -s tests -p 'test*.py'`;
- JSON parse for settings and manifest;
- CSV schema checks for the access matrix and eBird required fields table;
- guardrail check that no raw biodiversity data, geospatial exports, caches,
  model outputs, credentials, or bulky files were created or committed;
- unfinished-marker scan;
- local Markdown link check;
- GitHub visibility check;
- final clean/synced `git status --short --branch`.

## Stop Rules

Stop and report a blocker if:

- Goal 021 artefacts are missing or inconsistent;
- official/current access terms indicate eBird complete checklist or sampling
  event metadata cannot support the intended pilot role;
- the request envelope cannot be defined without actual data access;
- any data request would require Barry's credentials or a live form submission;
- validation gates fail;
- biodiversity records are accidentally downloaded, staged, or generated.

If the work remains request-prep only and validation passes, commit and push
the package and recommend Goal 023.

## Final Response Requirements

Report:

- headline access recommendation and whether the eBird pilot package is
  request-ready;
- exact data streams and roles: eBird, Birdata, EAWS, ALA;
- key eBird products/fields and scope assumptions;
- permission questions requiring Barry/lab-leader action;
- hydrology and species/guild restrictions carried forward;
- changed files;
- validation commands and outcomes;
- commit hash and push status;
- residual risks;
- recommended Goal 023.
