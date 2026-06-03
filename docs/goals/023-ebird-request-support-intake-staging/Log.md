# Log

Goal: eBird request support and intake-staging design gate

Status: Completed.

## Supervisor Setup

- 2026-06-01: Goal 023 packet created after Barry approved making the next
  `nomad` goal, while reserving explicit human confirmation for the eBird
  submission itself.
- 2026-06-01: This goal is request-submission support and future intake-design
  only. It must not submit an eBird request, log into eBird, use credentials,
  fill a live browser form, download biodiversity records, or handle raw
  private/gated data.

## Execution Checkpoints

- 2026-06-01: Execution started from the clean `main` worktree. Confirmed the
  repo is at Goal 023 setup commit `cefe9e9`, beyond Goal 022 commit
  `9bee436`. Scope remains submission-support and future intake-staging design
  only; no eBird request submission, browser session, credentials, or
  biodiversity data handling will be performed.
- 2026-06-01: Read required Goal 020/021/022 context, project plans, data stream
  register, source evidence register, decision log, and README. Confirmed the
  Goal 020 carry-forward counts from the current readiness table: `924`
  support-month rows, `820` `core_eligible`, `81`
  `core_eligible_with_caveat`, `23` `sensitivity_only`, and four
  `legacy_stac_comparator_not_obtained` caveat rows.
- 2026-06-01: Drafted the Goal 023 package: human eBird submission checklist,
  paste-ready request text, future ignored-path intake/quarantine/provenance
  plan, machine-readable QA contract, settings, validator, and focused tests.
  No new official web pages were checked because Goal 022 source entries
  S56-S59 were checked on the same date and already pin the needed eBird
  product, terms, complete-checklist, and sensitive-record details.
- 2026-06-01: Validation passed for the Goal 023 package. Commands run:
  `python3 scripts/validate_ebird_request_intake_023.py`,
  `python3 -m unittest tests.test_goal023_ebird_request_intake`,
  `python3 -m unittest discover -s tests -p 'test*.py'` (`98` tests),
  JSON parsing for settings/manifest, CSV schema check for the 17-row QA
  contract, `git diff --check`, local Markdown link check, changed-file blocked
  extension check, and GitHub private-repo visibility check. Full unittest
  discovery refreshed older Goal 021/022 manifest timestamps; those generated
  side effects were restored so only Goal 023 files remain changed.
- 2026-06-01: Guardrail notes: broad size/extension scans still report
  pre-existing ignored raw artefacts under `artifacts/`; the credential/status
  regex also reports pre-existing `token` variable names in older hydrology
  scripts. No Goal 023 changed file added raw biodiversity data, private
  request responses, credentials, screenshots, geospatial exports, caches,
  model outputs, or bulky files. The eBird request remains unsent by `nomad`.

## Notes

- Goal 022 status is `ready_for_ebird_request_review`; no request has been
  sent and no data were acquired.
- The next live eBird submission step remains a human-confirmed action outside
  `nomad`'s Goal 023 scope.
- Recommended next step: Barry or an authorised browser-capable human reviews
  the Goal 023 request package and, only with Barry's direct action-time
  confirmation, sends the eBird Basic Dataset request; the next `nomad` goal
  after any delivery should be metadata-only intake provenance and quarantine
  QA before opening or parsing records.
