# Goal: eBird Request Support And Intake-Staging Design Gate

## Objective

Prepare the final no-data-acquisition support package for submitting the
bounded eBird Basic Dataset request, and design the no-raw-data-in-Git intake,
staging, and QA contract for any future eBird delivery.

This goal must make the request easy for Barry or a browser-capable helper to
submit with explicit action-time confirmation, while keeping `nomad` away from
live form submission, credentials, browser sessions, and raw biodiversity data.

## Why This Matters

Goal 022 classified the eBird complete-checklist pilot as
`ready_for_ebird_request_review`, but no request has been submitted and no bird
records have been acquired. The next project risk is operational rather than
analytical: the request should preserve the hydrology support window, complete
checklist and sampling-event requirements, sensitive-record handling, and
provisional species/guild uncertainty without accidentally starting data
acquisition.

This goal should turn the Goal 022 package into a clear human-submission
checklist and future intake QA design. It is a gate before any raw eBird file,
request response, or private data-handling workflow enters the project.

## Operating Mode

Request-submission support, governance, provenance design, and intake-staging
planning. No live submission. No browser automation. No data acquisition. No
ecological modelling.

## Scope

In scope:

- read repo instructions, this goal packet, Goal 020/021/022 outputs, the data
  stream register, source evidence register, analysis plan, validation plan,
  reproducibility plan, and manuscript plan;
- confirm the Goal 022 request envelope is still the basis for the first
  eBird lane;
- use current official/public eBird documentation only as needed to check any
  request-submission, terms, field, or citation details that are not already
  pinned in Goal 022;
- prepare paste-ready request text blocks and a human-submission checklist for
  Barry or a browser-capable helper;
- make the action-time confirmation boundary explicit: the final eBird
  submit/send action requires Barry's direct confirmation;
- design a future eBird intake staging layout under ignored paths and a
  manifest/provenance scheme for request IDs, delivery timestamps, file names,
  checksums, citation/version text, and terms;
- define the QA contract for the first eBird delivery before any records are
  transformed into analysis tables;
- add a lightweight validator, settings file, manifest, and tests for the Goal
  023 documentation package;
- update docs/registers/decision log and this goal log;
- commit and push the validated package to private GitHub `main`.

Out of scope:

- submitting, clicking, sending, or finalising an eBird request;
- logging into eBird, using Barry's account, using browser sessions, filling
  live web forms, inspecting cookies, or handling credentials;
- downloading, receiving, opening, parsing, staging, transforming, or
  validating raw eBird or other biodiversity records;
- recording private request responses, raw confirmation emails, account
  details, credentials, API tokens, or non-public data-use terms in Git;
- asking for Birdata, EAWS, ALA, or any non-eBird data access;
- broadening the date window, spatial envelope, support set, or species/guild
  scope beyond Goal 022 without explicit Barry/lab-leader approval;
- choosing final species lists or final guild membership;
- deriving observation units, fitting models, making bird-response claims, or
  changing hydrology data/readiness classes;
- committing raw data, private request responses, credentials, geospatial
  exports, caches, parquet/SQLite/DuckDB stores, model outputs, or bulky
  artefacts;
- launching remote/HPC jobs.

## Required Read-First Sources

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `docs/goals/022-bird-data-access-feasibility/Goal.md`
- `docs/goals/022-bird-data-access-feasibility/Log.md`
- `docs/bird_data_access_feasibility_022.md`
- `docs/ebird_pilot_request_package_022.md`
- `docs/bird_data_access_matrix_022.csv`
- `docs/ebird_required_fields_022.csv`
- `docs/bird_data_access_022_manifest.json`
- `docs/birdata_eaws_permission_questions_022.md`
- `docs/ala_context_rules_022.md`
- `docs/goals/021-bird-observation-linkage-design/Goal.md`
- `docs/goals/021-bird-observation-linkage-design/Log.md`
- `docs/bird_observation_linkage_design_021.md`
- `docs/bird_hydrology_join_contract_021.csv`
- `docs/bird_observation_unit_schema_021.csv`
- `docs/candidate_species_guild_screen_021.csv`
- `docs/biodiversity_data_access_protocol_021.md`
- `docs/hydrology_to_bird_linkage_gate_020.md`
- `docs/direct_s3_full_window_hydrology_020_readiness.csv`
- `docs/direct_s3_full_window_hydrology_020_support_summary.csv`
- `docs/data_stream_register.md`
- `docs/source_evidence_register.md`
- `docs/analysis_plan.md`
- `docs/validation_plan.md`
- `docs/reproducibility_plan.md`
- `docs/manuscript_plan.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `9bee436` (`Prepare bird data access
  package`).
- Inspect available docs with `rg --files docs`.
- Confirm `data/*`, `artifacts/*`, secrets, credentials, and generated
  products are ignored by `.gitignore`.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Design Requirements

Carry forward all Goal 020/021/022 restrictions:

- eBird Basic Dataset complete checklists with sampling-event/effort metadata
  remain the first constrained bird-data lane;
- eBird Observational Dataset, GBIF, and ALA-style occurrence-only routes must
  not be substituted for absence/non-detection inference;
- the request window remains `2018-01-01` through `2024-12-31`;
- the request envelope remains the current 11 Goal 020 hydrology supports and
  their wetland complexes: Macquarie Marshes, Narran Lake Nature Reserve,
  Gwydir Wetlands, Kerang Wetlands, and Currawinya Lakes;
- core bird-linkage design may use only `core_eligible` and
  `core_eligible_with_caveat` hydrology rows;
- the 23 `sensitivity_only` rows must remain outside core fitting and visible
  for coverage/sensitivity accounting;
- the four Goal 018 caveat rows remain caveated, not dropped;
- species/guild choices remain provisional and lab-review gated;
- Birdata and EAWS remain secondary/validation lanes until permissions and
  field structures are confirmed;
- ALA remains context-only and must never support absence/non-detection
  inference.

The submission-support package must include:

- paste-ready project title, short purpose, detailed description, sensitive
  species justification, data handling/terms statement, intended outputs, and
  field/product needs;
- a checklist separating pre-submit review, live-form fill steps, action-time
  confirmation, and post-submit provenance capture;
- exact language for the action-time confirmation, stating that the next click
  would submit an eBird Basic Dataset request to Cornell/eBird under Barry's
  logged-in account;
- a clear instruction that `nomad` did not and must not submit the request.

The intake-staging design must specify:

- ignored staging roots for future raw eBird delivery, for example under
  `data/ebird_raw/` or another `data/*` path already excluded by `.gitignore`;
- a committed metadata-only provenance note pattern that can record request
  ID, delivery date, eBird data version, citation text, terms version, file
  names, checksums, row counts, and analyst initials without committing raw
  rows;
- a quarantine step before any delivered file is parsed into derived tables;
- required QA checks for file inventory, checksums, CSV/TSV headers, expected
  eBird products, complete-checklist fields, sampling-event fields, sensitive
  record indicators, spatial precision, date-window conformance, support
  assignment readiness, duplicate/shared checklist handling, and license/cite
  metadata;
- explicit stop rules for missing sampling-event metadata, unclear terms,
  sensitive-record restrictions, or any delivery that cannot support the Goal
  022 observation design.

## Required Deliverables

Create:

- `docs/ebird_request_submission_checklist_023.md`: human-facing submission
  checklist and action-time confirmation script.
- `docs/ebird_request_text_023.md`: paste-ready request text blocks derived
  from Goal 022.
- `docs/ebird_intake_staging_plan_023.md`: future no-raw-data-in-Git intake,
  quarantine, provenance, and QA design.
- `docs/ebird_intake_qa_contract_023.csv`: machine-readable QA checks for
  the future eBird delivery.
- `docs/ebird_request_023_manifest.json`: source files, official pages
  checked if any, request envelope, deliverable checksums/counts, decision
  status, and validation summary.
- `settings/ebird_request_intake_023.json`: expected files, controlled
  vocabularies, minimum counts, and guardrail settings.
- `scripts/validate_ebird_request_intake_023.py`: lightweight validator for
  the Markdown/CSV/JSON package.
- `tests/test_goal023_ebird_request_intake.py`: focused tests for required
  files, CSV schema, controlled vocabularies, submission-boundary language,
  intake-staging guardrails, manifest consistency, and carry-forward
  restrictions.

Update:

- `docs/data_stream_register.md`;
- `docs/source_evidence_register.md` if new or updated public sources are
  checked;
- `docs/decision_log.md`;
- `docs/README.md`;
- `docs/goals/023-ebird-request-support-intake-staging/Log.md`.

## Validation Gates

Required validation:

- `git diff --check`;
- run `python3 scripts/validate_ebird_request_intake_023.py`;
- focused Goal 023 tests;
- full `python3 -m unittest discover -s tests -p 'test*.py'`;
- JSON parse for settings and manifest;
- CSV schema check for `docs/ebird_intake_qa_contract_023.csv`;
- guardrail check that no raw biodiversity data, geospatial exports, caches,
  model outputs, credentials, browser screenshots, private request responses,
  or bulky files were created or committed;
- guardrail check that the committed text does not claim the eBird request was
  submitted;
- unfinished-marker scan;
- local Markdown link check;
- GitHub visibility check;
- final clean/synced `git status --short --branch`.

## Stop Rules

Stop and report a blocker if:

- Goal 022 artefacts are missing or inconsistent;
- current official/public eBird documentation contradicts the Goal 022 request
  route or terms materially;
- the submission checklist cannot be made request-ready without logging in,
  using a browser session, or seeing private account-specific fields;
- the future intake plan would require committing raw eBird data or private
  terms to Git;
- validation gates fail;
- any biodiversity records, request responses, credentials, or browser
  artefacts are accidentally downloaded, staged, generated, or exposed.

If the work remains request-support/intake-design only and validation passes,
commit and push the package. The recommended next step should be a supervised
browser submission support task that stops before final submit and asks Barry
for explicit action-time confirmation.

## Final Response Requirements

Report:

- whether the Goal 023 package is ready for human/browser submission support;
- the exact eBird request scope carried forward;
- the human confirmation boundary and whether any live submission happened;
- the future raw-data staging and QA design;
- changed files;
- validation commands and outcomes;
- commit hash and push status;
- residual risks;
- recommended next step.
