# Log

Goal: Bird observation linkage design and access protocol

Status: Completed.

## Supervisor Setup

- 2026-06-01: Goal 021 packet created after Goal 020 classified the full
  Goal 019 hydrology table as ready for constrained bird-linkage design:
  `820` `core_eligible`, `81` `core_eligible_with_caveat`, and `23`
  `sensitivity_only` support-month rows.
- 2026-06-01: Goal 021 is intentionally design-only. It should not download,
  request, process, or model biodiversity data.

## Execution Checkpoints

- 2026-06-01: Action start. Read required Goal 021 packet files, started required source-read context checks per goal packet, and confirmed repository is clean at `main`.
- 2026-06-01: Confirmed Goal 020 artefact gate context (`docs/hydrology_to_bird_linkage_gate_020.md`) and required 924-row hydrology readiness contract.
- 2026-06-01: Design memo, join contract, schema table, species/guild screen, access protocol draft and validation manifest scaffolding are now being authored.
- 2026-06-01: Continuation from dirty Goal 021 state after model capacity interruption. Corrected Goal 020 path references in settings, fixed observation-unit schema alignment, and tightened provisional candidate wording without downloading or processing biodiversity data.
- 2026-06-01: Generated final Goal 021 validation manifest and confirmed Goal 020 carry-forward counts: `924` readiness rows, `820` `core_eligible`, `81` `core_eligible_with_caveat`, `23` `sensitivity_only`, and four `legacy_stac_comparator_not_obtained` caveat rows.
- 2026-06-01: Ran validation gates: Goal 021 validator, focused Goal 021 tests, full unittest discovery, JSON parsing for settings/manifest, CSV schema checks, Markdown local-link check, changed-file guardrails, `git diff --check`, and GitHub private-repo visibility check. Existing ignored raw artefacts were detected under `artifacts/`, but no Goal 021 changed file used a blocked extension or exceeded the size limit.
- 2026-06-01: Final design decision: `ready_for_bird_data_access_feasibility`; first constrained lane is eBird complete-checklist occurrence/non-detection plus effort-aware relative-count design. Birdata and EAWS remain secondary/validation candidates, ALA remains presence/context only, and species/guild choices remain provisional pending lab-leader review.

## Notes

- Carry forward all Goal 020 hydrology restrictions.
- Keep candidate species/guild choices provisional until reviewed by the
  supervisor/lab leader.
- No biodiversity data were downloaded, requested, ingested, processed, or
  modelled during Goal 021.
