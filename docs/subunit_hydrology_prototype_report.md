# Subunit Hydrology Prototype Report

## Purpose

Goal 006 computed bounded monthly DEA Water Observations metrics over selected
child supports from the new parent-child registry. The prototype keeps the Goal
005 Ramsar parent supports as context, but tests whether documented subunits
can be processed with the same monthly metric contract.

This is hydrology-support prototype evidence only. It is not bird-response,
breeding, abundance, refuge, or ecological-role analysis.

## Compute Decision

The prototype ran locally on the Mac mini. No compute-routing memo was needed:
the raw Ramsar subset was 497145 bytes, the DEA Waterbodies ZIP was 46502008
bytes, the run completed in 52.510 seconds, and the largest selected subunit
reference grid was 788256 cells, below the configured 2000000-cell local stop
threshold.

## Workflow

Executable files:

- [../scripts/subunit_hydrology_006.py](../scripts/subunit_hydrology_006.py)
- [../settings/subunit_hydrology_006.json](../settings/subunit_hydrology_006.json)

Committed outputs:

- [subunit_support_registry.csv](subunit_support_registry.csv)
- [subunit_support_registry_manifest.json](subunit_support_registry_manifest.json)
- [subunit_hydrology_prototype_summary.csv](subunit_hydrology_prototype_summary.csv)
- [subunit_hydrology_prototype_manifest.json](subunit_hydrology_prototype_manifest.json)

Processing steps:

1. Query the DCCEEW Geospatial Ramsar Wetlands service for the five parent
   REFCODEs and stage the returned GeoJSON only under ignored `artifacts/`.
2. Use Ramsar component records as official candidate child supports.
3. Open the DEA Waterbodies v3 shapefile ZIP from ignored staging and intersect
   Waterbodies polygons with each parent Ramsar support in `EPSG:3577`.
4. Select six bounded subunits for hydrology metrics.
5. For each selected subunit and target month, query DEA STAC for
   `ga_ls_wo_3`, warp every readable Water Observations scene to a 30 m support
   grid, and calculate the Goal 003 base monthly metrics.

## Selected Subunits

| Candidate | Selected subunit | Source type | Support area or overlap area |
| --- | --- | --- | ---: |
| NWB001 Macquarie Marshes | `nwb001_ramsar_component_359` Macquarie Marshes Nature Reserve | Ramsar component | 187555533 m2 |
| NWB003 Gwydir Wetlands | `nwb003_ramsar_component_121` Old Dromana | Ramsar component | 6079398 m2 |
| NWB004 Kerang Wetlands | `nwb004_ramsar_component_354` Reedy Lake | Ramsar component | 7737916 m2 |
| NWB004 Kerang Wetlands | `nwb004_ramsar_component_369` Lake Charm | Ramsar component | 7039276 m2 |
| NWB005 Currawinya Lakes | `nwb005_dea_waterbody_r4yss38r6_v3` | DEA Waterbodies overlap | 40621261 m2 |
| NWB005 Currawinya Lakes | `nwb005_dea_waterbody_r4ysdndx8_v3` | DEA Waterbodies overlap | 38136237 m2 |

## Results

The run produced 18 hydrology rows: six selected subunits by the three Goal
004/005 months (`2019-01`, `2022-11`, `2024-03`). All rows reached
`computed_subunit_metrics`.

| Subunit | 2019-01 wet proportion | 2022-11 wet proportion | 2024-03 wet proportion | Quality notes |
| --- | ---: | ---: | ---: | --- |
| Macquarie Marshes Nature Reserve | 0.000240 | 0.055790 | 0.002221 | All months `quality_minimum`. |
| Old Dromana | 0.000197 | 0.003777 | 0.005628 | 2022-11 is `quality_fail`; other months `quality_minimum`. |
| Reedy Lake | 0.715381 | 0.748615 | 0.494191 | 2019-01 and 2024-03 `quality_high`; 2022-11 `quality_minimum`. |
| Lake Charm | 0.818906 | 0.849393 | 0.808567 | 2022-11 is `quality_fail`; other months `quality_minimum`. |
| DEA Waterbody `r4yss38r6_v3` | 0.000033 | 0.466710 | 0.287109 | All months `quality_high`. |
| DEA Waterbody `r4ysdndx8_v3` | 0.000053 | 0.837247 | 0.519386 | 2019-01 and 2022-11 `quality_high`; 2024-03 `quality_minimum`. |

Quality summary: 7 rows are `quality_high`, 9 are `quality_minimum`, and 2 are
`quality_fail`. The failed rows are retained in the table with blank wet-month
flags because they do not meet the minimum clear-observation rule.

## Parent Context

The Goal 005 parent support rows remain the reporting context. The subunit
rows show why parent-only summaries can obscure within-complex differences, but
they do not replace the parent supports.

| Candidate | Goal 005 parent 2022-11 wet proportion | Selected subunit 2022-11 wet proportion |
| --- | ---: | --- |
| NWB001 Macquarie Marshes | 0.056122 | Macquarie Marshes Nature Reserve: 0.055790 |
| NWB003 Gwydir Wetlands | 0.019048 | Old Dromana: 0.003777 (`quality_fail`) |
| NWB004 Kerang Wetlands | 0.738985 (`quality_fail`) | Reedy Lake: 0.748615; Lake Charm: 0.849393 (`quality_fail`) |
| NWB005 Currawinya Lakes | 0.051861 | DEA Waterbody `r4yss38r6_v3`: 0.466710; DEA Waterbody `r4ysdndx8_v3`: 0.837247 |

## Deferred Metrics And Caveats

Lag, novelty, drying velocity, hydroperiod persistence, and regional water
availability remain deferred because they require longer monthly series and a
settled regional support set.

DEA Waterbodies rows are open-water screening supports, not final ecological
wetland units. Ramsar components are official and reproducible, but some
components are narrower than the broader wetland system. Water Observations can
under-detect inundation in vegetated or mixed water/vegetation pixels, so the
Macquarie, Narran, and Gwydir caveats remain active.

## Conclusion

Goal 006 proves that a bounded subunit registry and selected subunit Water
Observations metrics can run locally without committing raw geometry or rasters.
The next hydrology step should improve named-lake/component evidence and scale
the monthly series only after the subunit support design is reviewed.
