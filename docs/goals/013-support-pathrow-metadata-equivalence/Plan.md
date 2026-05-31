# Plan

## Purpose

Move from "known S3 path-row works" to "support-level scene discovery is
reviewable". Goal 013 should prove path/row coverage for the event-window
supports, test complete direct-S3 item discovery for Narran, and decide whether
an official comparator can establish equivalence.

## Expected File Responsibilities

- `settings/support_pathrow_metadata_013.json`: support set, primary candidate,
  probe months, WRS/path-row source, route limits, ignored staging paths,
  comparator thresholds, and output paths.
- `scripts/support_pathrow_metadata_013.py`: small prototype for path/row
  coverage derivation, direct S3 item discovery, comparator probes, item-set
  hashes, and compact output writing.
- `tests/test_goal013_support_pathrow_metadata.py`: focused tests for pure
  functions and committed output contracts.
- `docs/support_pathrow_coverage_013_report.md`: narrative coverage,
  comparator, and next-step recommendation.
- `docs/support_pathrow_coverage_013_manifest.json`: machine-readable source,
  command, route, comparator, host, staging, and item-set provenance.
- `docs/support_pathrow_crosswalk_013.csv`: support-to-path/row crosswalk.
- `docs/support_pathrow_item_sets_013.csv`: direct-S3 item-set summary for
  `NWB002` complete path/row coverage.
- `docs/metadata_comparator_status_013.csv`: comparator and equivalence status
  table.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`: project context updates.
- `docs/goals/013-support-pathrow-metadata-equivalence/Log.md`: live log.

## Task Sequence

1. Confirm clean repo state and required checkpoint.
2. Read required instructions, `nectar` docs, and Goal 011/012 evidence.
3. Review existing support geometry and bbox provenance.
4. Identify and verify an official/current WRS-2 path/row footprint source.
5. Confirm ignored staging paths before raw geometry or route artefacts are
   written.
6. Write focused tests for path/row parsing, crosswalk status classification,
   item hashing, comparator status, and raw-extension exclusion.
7. Implement the bounded prototype script/config.
8. Derive support-to-path/row coverage, preferably for all 11 supports.
9. Run direct-S3 complete-path-row listing for `NWB002` and the three probe
   months.
10. Compare against Goal 012's known-path item set.
11. Run strict STAC preflight; if it fails, attempt one practical official
    comparator route or record why none is available.
12. Write compact CSV/JSON/Markdown outputs and update registers/logs.
13. Validate code, outputs, docs, links, Git/data hygiene, and repeated-hash
    stability.
14. Commit and push if validation passes.

## Self-Review Questions

- Did this goal prove complete path/row coverage for the support, or label the
  coverage as conservative/blocked?
- Did it avoid hydrology extraction and ecological interpretation?
- Is direct S3 still only technically viable, or now evidence-equivalent?
- Is the official comparator status explicit enough for a supervisor to decide
  the next step?
- Can Goal 014 be issued without guessing which route is safe?
