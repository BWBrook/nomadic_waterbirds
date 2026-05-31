# Plan

## Purpose

Repair the validation baseline before scaling direct-S3 hydrology. Goal 015
should decide whether the Goal 014 denominator mismatch is an artefact of the
legacy STAC bbox scene-selection rule, and formalise the production rule for
support-relevant Water Observations scenes.

## Expected File Responsibilities

- `settings/comparator_baseline_repair_015.json`: support, months, path/rows,
  source product, scene-selection policy, tolerances, staging paths, and output
  paths.
- `scripts/comparator_baseline_repair_015.py`: bounded repair script for
  path-row-filtered STAC comparator generation, denominator-effect accounting,
  comparisons, and compact output writing.
- `tests/test_goal015_comparator_baseline_repair.py`: focused tests for pure
  helpers and output contracts.
- `docs/comparator_baseline_repair_015_report.md`: narrative result,
  policy decision, limitations, and next-step recommendation.
- `docs/comparator_baseline_repair_015_manifest.json`: machine-readable
  command, route, comparator, comparison, host, and staging provenance.
- `docs/pathrow_filtered_comparator_015_summary.csv`: repaired comparator
  baseline rows.
- `docs/comparator_baseline_repair_015_comparison.csv`: repaired versus
  direct-S3 and legacy comparisons.
- `docs/legacy_denominator_effect_015.csv`: legacy bbox-only denominator
  effect table.
- `docs/hydrology_metric_spec.md`: update only if policy clarification is
  needed.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`: project context updates.
- `docs/goals/015-comparator-baseline-repair/Log.md`: live log.

## Task Sequence

1. Confirm clean repo state and required checkpoint.
2. Read required instructions, `nectar` docs, and Goal 013/014 evidence.
3. Confirm ignored staging paths before any live metadata or raster artefacts.
4. Write focused tests for scene filtering, denominator-effect accounting,
   comparison tolerances, schema, and raw-extension exclusion.
5. Implement the bounded repair script/config, reusing Goal 014 helpers where
   practical.
6. Build or block the path-row-filtered STAC comparator baseline for the three
   months.
7. Compare repaired comparator rows to Goal 014 direct-S3 rows.
8. Quantify legacy Goal 007 denominator effects for `2022-11` and `2024-12`.
9. Update the metric spec if the scene-selection policy needs clarification.
10. Write compact CSV/JSON/Markdown outputs and update registers/logs.
11. Validate code, outputs, docs, links, Git/data hygiene, and comparison
    status.
12. Commit and push if validation passes.

## Self-Review Questions

- Did this goal repair the comparator rather than scale extraction?
- Is the scene-selection policy explicit enough for future full-window runs?
- Do repaired comparator rows match Goal 014 direct-S3 rows within tolerance?
- Is the old denominator mismatch fully explained, or is there still a real
  blocker?
- Is Goal 016 a justified scale step rather than a leap?
