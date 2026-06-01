# Goal 020 Hydrology-to-Bird-Linkage Gate

Decision: `ready_for_constrained_bird_linkage_design`.

## Scope
Use this hydrology table only for a constrained linkage design. Core analyses should start with `core_eligible` and `core_eligible_with_caveat` support-month rows.

## Restrictions
- exclude_quality_fail_rows_from_core
- retain_quality_fail_rows_in_sensitivity
- carry_goal018_comparator_caveat
- review_derived_metric_boundary_rows_in_context
- Keep all `quality_fail` rows (`23`) for sensitivity-only or reporting contexts.

## Next goal
Recommended next goal: `Goal 021`.