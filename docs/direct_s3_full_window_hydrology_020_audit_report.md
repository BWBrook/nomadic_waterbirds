# Goal 020 Hydrology-to-Bird Linkage Readiness Audit

Accessed date: `2026-06-01`.

## Outcome
Decision: `ready_for_constrained_bird_linkage_design`.
Core table: `924` rows (`11` supports, `84` months).
Quality-fail rows retained and classified: `23`.

## Readiness classes
| Class | Rows |
| --- | ---: |
| core_eligible | 820 |
| core_eligible_with_caveat | 81 |
| sensitivity_only | 23 |

## Quality-fail reason mix
| Reason | Rows |
| --- | ---: |
| low_clear_fraction | 21 |
| low_support_area_after_mask | 2 |

## Quality-fail support concentration
| Support | Rows |
| --- | ---: |
| nwb004_ramsar_component_369 | 6 |
| nwb004_ramsar_ref265 | 5 |
| nwb003_ramsar_ref993 | 3 |
| nwb004_ramsar_component_354 | 3 |
| nwb005_dea_waterbody_r4ysdndx8_v3 | 3 |
| nwb001_ramsar_component_359 | 1 |
| nwb001_ramsar_ref337 | 1 |
| nwb003_ramsar_component_121 | 1 |

## Quality-fail month concentration
| Month | Rows |
| --- | ---: |
| 2020-04 | 5 |
| 2019-09 | 3 |
| 2020-09 | 3 |
| 2022-05 | 2 |
| 2023-06 | 2 |
| 2022-09 | 2 |
| 2021-06 | 1 |
| 2023-11 | 1 |
| 2020-05 | 1 |
| 2024-01 | 1 |
| 2020-12 | 1 |
| 2021-11 | 1 |

## Caveats carried forward
- Keep the four Goal 018 legacy comparator caveat rows as `core_eligible_with_caveat` and do not drop them from primary tables.
- Exclude all `quality_fail` rows from core-linkage model fitting; keep them for sensitivity and coverage reporting only.
- Review `derived_partial_history` rows during sensitivity checks.

## Decision memo
- `Goal 020` supports proceeding to `Goal 021` as a constrained bird-linkage design gate.
- Restriction: apply `core_eligible` plus `core_eligible_with_caveat` tables only, and explicitly route `sensitivity_only` rows out of core fitting.
- Restriction: preserve the Goal 018 four-row comparator caveat in downstream design documentation.
- Restriction: do not use `quality_fail` rows in final primary covariate-response statements.

## Support summary preview
| Support | Core eligible | Core with caveat | Sensitivity only | Quality fail |
| --- | ---: | ---: | ---: | ---: |
| nwb001_ramsar_component_359 | 78 | 5 | 1 | 1 |
| nwb001_ramsar_ref337 | 78 | 5 | 1 | 1 |
| nwb002_ramsar_ref1291 | 81 | 3 | 0 | 0 |
| nwb003_ramsar_component_121 | 78 | 5 | 1 | 1 |
| nwb003_ramsar_ref993 | 72 | 9 | 3 | 3 |
| nwb004_ramsar_component_354 | 72 | 9 | 3 | 3 |
| nwb004_ramsar_component_369 | 63 | 15 | 6 | 6 |
| nwb004_ramsar_ref265 | 64 | 15 | 5 | 5 |
| nwb005_dea_waterbody_r4ysdndx8_v3 | 72 | 9 | 3 | 3 |
| nwb005_dea_waterbody_r4yss38r6_v3 | 81 | 3 | 0 | 0 |
| nwb005_ramsar_ref791 | 81 | 3 | 0 | 0 |


## Month summary preview
| Month | Core eligible | Core with caveat | Sensitivity only | Quality fail |
| --- | ---: | ---: | ---: | ---: |
| 2018-01 | 0 | 11 | 0 | 0 |
| 2018-02 | 0 | 11 | 0 | 0 |
| 2018-03 | 0 | 11 | 0 | 0 |
| 2018-04 | 11 | 0 | 0 | 0 |
| 2018-05 | 11 | 0 | 0 | 0 |
| 2018-06 | 11 | 0 | 0 | 0 |
| 2018-07 | 11 | 0 | 0 | 0 |
| 2018-08 | 11 | 0 | 0 | 0 |
| 2018-09 | 11 | 0 | 0 | 0 |
| 2018-10 | 11 | 0 | 0 | 0 |
| 2018-11 | 11 | 0 | 0 | 0 |
| 2018-12 | 11 | 0 | 0 | 0 |
| 2019-01 | 11 | 0 | 0 | 0 |
| 2019-02 | 11 | 0 | 0 | 0 |
| 2019-03 | 11 | 0 | 0 | 0 |
| 2019-04 | 11 | 0 | 0 | 0 |
| 2019-05 | 11 | 0 | 0 | 0 |
| 2019-06 | 11 | 0 | 0 | 0 |
| 2019-07 | 11 | 0 | 0 | 0 |
| 2019-08 | 11 | 0 | 0 | 0 |
| 2019-09 | 8 | 0 | 3 | 3 |
| 2019-10 | 8 | 3 | 0 | 0 |
| 2019-11 | 11 | 0 | 0 | 0 |
| 2019-12 | 8 | 3 | 0 | 0 |
| 2020-01 | 11 | 0 | 0 | 0 |
| 2020-02 | 11 | 0 | 0 | 0 |
| 2020-03 | 11 | 0 | 0 | 0 |
| 2020-04 | 6 | 0 | 5 | 5 |
| 2020-05 | 6 | 4 | 1 | 1 |
| 2020-06 | 10 | 1 | 0 | 0 |
| 2020-07 | 6 | 5 | 0 | 0 |
| 2020-08 | 10 | 1 | 0 | 0 |
| 2020-09 | 8 | 0 | 3 | 3 |
| 2020-10 | 8 | 3 | 0 | 0 |
| 2020-11 | 11 | 0 | 0 | 0 |
| 2020-12 | 7 | 3 | 1 | 1 |
| 2021-01 | 10 | 1 | 0 | 0 |
| 2021-02 | 11 | 0 | 0 | 0 |
| 2021-03 | 10 | 1 | 0 | 0 |
| 2021-04 | 11 | 0 | 0 | 0 |
| 2021-05 | 11 | 0 | 0 | 0 |
| 2021-06 | 10 | 0 | 1 | 1 |
| 2021-07 | 10 | 1 | 0 | 0 |
| 2021-08 | 11 | 0 | 0 | 0 |
| 2021-09 | 10 | 1 | 0 | 0 |
| 2021-10 | 11 | 0 | 0 | 0 |
| 2021-11 | 10 | 0 | 1 | 1 |
| 2021-12 | 10 | 1 | 0 | 0 |
| 2022-01 | 11 | 0 | 0 | 0 |
| 2022-02 | 10 | 1 | 0 | 0 |
| 2022-03 | 11 | 0 | 0 | 0 |
| 2022-04 | 11 | 0 | 0 | 0 |
| 2022-05 | 9 | 0 | 2 | 2 |
| 2022-06 | 9 | 2 | 0 | 0 |
| 2022-07 | 11 | 0 | 0 | 0 |
| 2022-08 | 9 | 2 | 0 | 0 |
| 2022-09 | 9 | 0 | 2 | 2 |
| 2022-10 | 9 | 2 | 0 | 0 |
| 2022-11 | 10 | 1 | 0 | 0 |
| 2022-12 | 9 | 2 | 0 | 0 |
| 2023-01 | 11 | 0 | 0 | 0 |
| 2023-02 | 11 | 0 | 0 | 0 |
| 2023-03 | 11 | 0 | 0 | 0 |
| 2023-04 | 11 | 0 | 0 | 0 |
| 2023-05 | 11 | 0 | 0 | 0 |
| 2023-06 | 9 | 0 | 2 | 2 |
| 2023-07 | 9 | 2 | 0 | 0 |
| 2023-08 | 11 | 0 | 0 | 0 |
| 2023-09 | 9 | 2 | 0 | 0 |
| 2023-10 | 11 | 0 | 0 | 0 |
| 2023-11 | 10 | 0 | 1 | 1 |
| 2023-12 | 10 | 1 | 0 | 0 |
| 2024-01 | 10 | 0 | 1 | 1 |
| 2024-02 | 9 | 2 | 0 | 0 |
| 2024-03 | 11 | 0 | 0 | 0 |
| 2024-04 | 10 | 1 | 0 | 0 |
| 2024-05 | 11 | 0 | 0 | 0 |
| 2024-06 | 11 | 0 | 0 | 0 |
| 2024-07 | 11 | 0 | 0 | 0 |
| 2024-08 | 11 | 0 | 0 | 0 |
| 2024-09 | 11 | 0 | 0 | 0 |
| 2024-10 | 11 | 0 | 0 | 0 |
| 2024-11 | 11 | 0 | 0 | 0 |
| 2024-12 | 9 | 2 | 0 | 0 |
