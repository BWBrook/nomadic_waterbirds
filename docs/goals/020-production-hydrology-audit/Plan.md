# Plan

## Purpose

Convert Goal 019's complete direct-S3 hydrology production table into a
reviewed, documented hydrology covariate layer with explicit row-level
readiness classes for later bird-observation linkage.

The audit should not make ecological claims. Its job is to decide whether the
hydrology data product is structurally and scientifically ready for the next
design gate.

## Expected File Responsibilities

- `settings/audit_direct_s3_full_window_hydrology_020.json`: thresholds,
  source/output paths, expected row counts, and category vocabularies.
- `scripts/audit_direct_s3_full_window_hydrology_020.py`: load Goal 019
  outputs, validate cross-file consistency, classify rows, write CSV/JSON/MD
  audit outputs.
- `tests/test_goal020_hydrology_audit.py`: focused tests for quality-fail
  classification, readiness classes, grid shape, manifest consistency, schema,
  and raw-data exclusion.
- `docs/direct_s3_full_window_hydrology_020_audit_report.md`: narrative audit.
- `docs/direct_s3_full_window_hydrology_020_manifest.json`: source, command,
  row counts, hashes, classification counts, validation provenance.
- `docs/direct_s3_full_window_hydrology_020_quality_fail_rows.csv`: 23-row
  quality-fail audit table.
- `docs/direct_s3_full_window_hydrology_020_readiness.csv`: 924-row
  support-month readiness table.
- `docs/direct_s3_full_window_hydrology_020_support_summary.csv`: support
  summary.
- `docs/direct_s3_full_window_hydrology_020_month_summary.csv`: month summary.
- `docs/hydrology_to_bird_linkage_gate_020.md`: next-step decision memo.
- `docs/data_stream_register.md`, `docs/decision_log.md`, `docs/README.md`:
  project context updates.
- `docs/goals/020-production-hydrology-audit/Log.md`: live execution log.

## Task Sequence

1. Confirm clean starting state and Goal 019 commit in history.
2. Read required instructions and Goal 019 artefacts.
3. Write settings and focused tests before or alongside implementation.
4. Implement audit script.
5. Validate Goal 019 series/item-set/summary/manifest consistency.
6. Generate the 924-row readiness table.
7. Generate the 23-row quality-fail audit table.
8. Generate support/month summaries.
9. Write the audit report and hydrology-to-bird-linkage gate memo.
10. Update docs index, data stream register, decision log, and Goal 020 log.
11. Run validation gates.
12. Commit and push if validation passes.

## Expected Decision Shape

Likely acceptable outcomes:

- `ready_for_constrained_bird_linkage_design`: Goal 019 passes audit, with
  quality-fail rows excluded from core analysis and retained for sensitivity or
  coverage context.
- `ready_after_minor_documentation_caveat`: only wording/contract caveats
  need clarifying.
- `not_ready_requires_hydrology_recovery`: audit finds production defects or
  metric inconsistencies that should block bird linkage.

The decision should be evidence-based, not optimistic.

## Stop Rules

- Do not process bird data.
- Do not launch remote compute.
- Do not change Goal 019 hydrology values.
- Do not hide or drop low-quality rows from the audit outputs.
- Stop if cross-file consistency checks fail.

## Self-Review Questions

- Does every support-month have exactly one readiness row?
- Are all 23 quality-fail rows visible and classified?
- Are `quality_fail` rows excluded from core bird-linkage recommendations?
- Are support/month quality concentrations described without ecological
  overinterpretation?
- Are retained STAC/direct-S3 provenance caveats carried forward?
- Does Goal 021 follow from the audit evidence?
