# Plan

## Purpose

Turn Goal 002's feasibility recommendation into a structured prototype
crosswalk and hydrology metric contract for the first MDB/eastern-inland pilot.

## Expected File Responsibilities

- `docs/prototype_wetland_unit_crosswalk.csv`: machine-readable candidate-unit
  crosswalk.
- `docs/prototype_wetland_unit_crosswalk.md`: rationale and interpretation for
  the crosswalk.
- `docs/hydrology_metric_spec.md`: monthly DEA Water Observations metric and
  quality-rule contract.
- `docs/product_access_probe_003.md`: record of public metadata/access checks.
- `docs/decision_memo_003.md`: supervisor-facing recommendation for Goal 004.
- `docs/data_stream_register.md`: status and next-action updates.
- `docs/decision_log.md`: decisions or deferrals.
- `docs/goals/003-prototype-wetland-crosswalk-hydrology-spec/Log.md`: live
  execution log.

## Task Sequence

1. Confirm repo state and read Goal 002 artefacts.
2. Build a candidate wetland list from official/public sources.
3. Perform small metadata/product-access checks needed to classify each
   candidate.
4. Write the crosswalk CSV with required columns and 5-8 candidate rows.
5. Write the crosswalk interpretation memo, including deferred candidates and
   caveats.
6. Write the hydrology metric spec with monthly formulas and invalid-observation
   rules.
7. Write the product-access probe record and decision memo.
8. Update registers, decision log, docs navigation, and goal log.
9. Validate CSV structure, links, Git hygiene, size limits, and absence of raw
   committed data.
10. Commit and push if validation passes.

## Self-Review Questions

- Can a later extraction goal execute the hydrology spec without guessing the
  intended metrics?
- Does every candidate row expose geometry, hydrology, biodiversity alignment,
  and caveats?
- Are Waterbodies limitations visible per candidate?
- Did the goal avoid data acquisition while still proving access feasibility?
- Is the recommendation for Goal 004 concrete enough to run?
