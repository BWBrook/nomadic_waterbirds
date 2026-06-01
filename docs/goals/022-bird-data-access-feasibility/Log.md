# Log

Goal: Bird data access feasibility and request package

Status: Completed.

## Supervisor Setup

- 2026-06-01: Goal 022 packet created after Goal 021 classified the first
  bird-observation lane as `ready_for_bird_data_access_feasibility`.
- 2026-06-01: Goal 022 is request-prep only. It should not submit access
  requests, log into services, download biodiversity records, or process
  private/gated data.

## Execution Checkpoints

- 2026-06-01: Action start. Read Goal 022 packet files in order, confirmed clean `main` branch beyond Goal 021 commit `813476d`, and began required context/source checks. No data requests, logins, credentials, biodiversity downloads, or private/gated data processing initiated.
- 2026-06-01: Read required Goal 020/021 artefacts, analysis/validation/manuscript plans, data stream register, and source evidence register. Confirmed Goal 020 carry-forward counts: `924` readiness rows, `820` `core_eligible`, `81` `core_eligible_with_caveat`, `23` `sensitivity_only`, and four `legacy_stac_comparator_not_obtained` caveat rows.
- 2026-06-01: Checked current official/public access documentation for eBird, Birdata, ALA, and EAWS without logging in or downloading data. Added S56-S66 source-register entries and drafted the Goal 022 access package, field matrix, permission briefs, ALA context rules, settings, validator, and tests.
- 2026-06-01: Generated `docs/bird_data_access_022_manifest.json` and validated the package. Validation gates passed: Goal 022 validator, focused Goal 022 tests, full unittest discovery (`89` tests), JSON parsing for settings/manifest, CSV schema checks, `git diff --check`, unfinished-marker scan, local Markdown link check, changed-file extension/size guardrails, and private GitHub visibility check.
- 2026-06-01: Final access decision: `ready_for_ebird_request_review`. eBird EBD complete-checklist pilot is request-ready for Barry review, not submitted. Birdata and EAWS remain `needs_clarification`; ALA remains `context_only`. Existing ignored raw artefacts were detected under `artifacts/`, but no Goal 022 changed file added blocked data, credentials, geospatial exports, caches, model outputs, or bulky files.

## Notes

- First constrained lane remains eBird complete checklists with sampling-event
  and effort metadata.
- Birdata and EAWS remain permission-question and validation candidates.
- ALA remains context-only and must not support absence inference.
- Species/guild choices remain provisional until Barry/lab-leader review.
- Recommended Goal 023: supervisor-reviewed eBird request submission and
  intake-staging design gate before any data request or raw-data handling.
