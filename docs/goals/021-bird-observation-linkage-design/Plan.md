# Plan

## Purpose

Move the project from hydrology-readiness into bird-observation design without
prematurely ingesting data or fitting models.

The output should be a concrete contract for the next data-access or feasibility
goal: what the first observation lane is, how it joins to hydrology, which
records can support which response layers, and which permissions/questions must
be resolved before data enter the repo.

## Expected File Responsibilities

- `settings/bird_linkage_design_021.json`: expected file paths, controlled
  vocabularies, row-count minima, and guardrail settings.
- `scripts/validate_bird_linkage_design_021.py`: validate the design artefacts
  and no-data-acquisition guardrails.
- `tests/test_goal021_bird_linkage_design.py`: focused regression tests.
- `docs/bird_observation_linkage_design_021.md`: narrative design memo.
- `docs/bird_hydrology_join_contract_021.csv`: machine-readable hydrology join
  contract.
- `docs/bird_observation_unit_schema_021.csv`: future observation-unit table
  schema.
- `docs/candidate_species_guild_screen_021.csv`: provisional review screen for
  species/guild candidates.
- `docs/biodiversity_data_access_protocol_021.md`: request/access protocol and
  permission questions.
- `docs/bird_linkage_design_021_manifest.json`: provenance and validation
  manifest.
- `docs/data_stream_register.md`, `docs/decision_log.md`, `docs/README.md`:
  project state updates.
- `docs/goals/021-bird-observation-linkage-design/Log.md`: live execution log.

## Task Sequence

1. Confirm clean starting state and Goal 020 commit in history.
2. Read required repo docs and Goal 020 artefacts.
3. Check current public/official data-source documentation only where needed.
4. Draft the observation-linkage design memo.
5. Draft the hydrology join contract and observation-unit schema.
6. Draft the provisional species/guild screen.
7. Draft the biodiversity data-access protocol.
8. Implement the lightweight validator and tests.
9. Generate the manifest.
10. Update docs index, data stream register, decision log, and Goal 021 log.
11. Run validation gates.
12. Commit and push if validation passes.

## Expected Decision Shape

Likely acceptable outcome:

- `ready_for_bird_data_access_feasibility`: the project has a defined first
  observation-linkage lane and can proceed to a bounded data-access/request or
  public-feasibility goal.

Other possible outcomes:

- `needs_lab_leader_species_decision`: design is structurally ready but the
  first candidate species/guild set needs Barry's decision before data access.
- `not_ready_observation_design_gap`: the design cannot yet define an
  observation unit or data-source role without more source review.

## Stop Rules

- Do not download, request, or process biodiversity data.
- Do not use credentials or private browser sessions.
- Do not fit models.
- Do not choose a final species list.
- Do not change hydrology artefacts.
- Stop if the design cannot honestly carry Goal 020 restrictions.

## Self-Review Questions

- Does the design preserve the hydrological reaction-norm thesis?
- Are occurrence, relative count, breeding, and validation evidence separated?
- Is ALA kept out of absence-style inference?
- Are eBird complete-checklist assumptions explicit?
- Are Birdata and EAWS permission/reuse questions explicit?
- Does every proposed observation unit have a hydrology join rule?
- Are Goal 020 quality restrictions carried forward?
- Is the candidate species/guild table provisional rather than final?
