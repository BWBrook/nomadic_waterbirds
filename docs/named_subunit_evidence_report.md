# Named Subunit Evidence Report

## Purpose

Goal 007 reviewed the Goal 006 parent/subunit support system before extending
hydrology metrics through a monthly event window. The aim was to strengthen
named-subunit evidence where possible, especially for Narran and Currawinya,
without forcing weak names onto open-water polygons.

This is hydrology-support evidence only. It is not a final ecological wetland
unit decision and does not support bird-response, breeding, abundance, refuge,
or ecological-role claims.

## Workflow

Executable files:

- [../scripts/event_window_hydrology_007.py](../scripts/event_window_hydrology_007.py)
- [../settings/event_window_hydrology_007.json](../settings/event_window_hydrology_007.json)

Committed outputs:

- [named_subunit_crosswalk.csv](named_subunit_crosswalk.csv)
- [named_subunit_evidence_manifest.json](named_subunit_evidence_manifest.json)
- [event_window_hydrology_series.csv](event_window_hydrology_series.csv)
- [event_window_hydrology_summary.csv](event_window_hydrology_summary.csv)
- [event_window_hydrology_series_manifest.json](event_window_hydrology_series_manifest.json)

Raw source files were staged only under ignored paths:

| Staged file | Bytes | Commit status |
| --- | ---: | --- |
| `artifacts/event_window_hydrology/raw/ramsar_goal007_subset.geojson` | 497145 | Not committed |
| `artifacts/event_window_hydrology/raw/ga_ls_wb_3_v3.zip` | 46502008 | Not committed |
| `artifacts/named_subunit_evidence/raw/lake_numalla_aggregation.kmz` | 2988 | Not committed |
| `artifacts/named_subunit_evidence/raw/lake_wyara.kmz` | 1781 | Not committed |
| `artifacts/named_subunit_evidence/raw/currawinya_ramsar.kmz` | 4542 | Not committed |

## Evidence Status

The crosswalk contains 15 support-evidence rows. Eleven supports were included
in the event-window hydrology series: five Goal 005 Ramsar parent supports,
four Goal 006 Ramsar component subunits, and two Goal 006 Currawinya DEA
Waterbodies open-water clips.

| Evidence status | Rows | Included in event series |
| --- | ---: | ---: |
| `official_parent_ramsar_support` | 5 | 5 |
| `official_named_ramsar_component` | 4 | 4 |
| `open_water_screen_linked_to_diwa_named_geometry` | 2 | 2 |
| `official_named_geometry_linked_to_dea_waterbody` | 2 | 0 |
| `name_and_within_parent_verified_no_geometry` | 2 | 0 |

## Narran

Narran Lake Nature Reserve remains included only as the official Ramsar parent
support. The evidence pass retained two named unresolved rows:

- `nwb002_named_clear_lake_unresolved`
- `nwb002_named_back_lake_unresolved`

The DCCEEW Narran page supports these names within the Ramsar site context, but
this goal did not verify separate vector geometry or a defensible DEA
Waterbody UID relationship for either named feature. The Goal 006 Narran
Waterbodies overlaps therefore remain retained open-water evidence, not named
subunit supports for event-window hydrology.

## Currawinya

Currawinya gained stronger named-lake evidence from Queensland WetlandInfo DIWA
boundary KMZs. The named geometry evidence was retained in the crosswalk, while
the event-window hydrology series kept the default Goal 006 DEA Waterbodies
support clips to avoid expanding the fallback hydrology run.

| Named evidence row | Linked DEA UID | Overlap evidence |
| --- | --- | --- |
| `nwb005_diwa_lake_numalla_aggregation` Lake Numalla Aggregation | `r4yss38r6_v3` | 34.970 million m2 overlap; 0.326 of named support and 0.774 of DEA polygon |
| `nwb005_diwa_lake_wyara` Lake Wyara | `r4ysdndx8_v3` | 47.140 million m2 overlap; 0.784 of named support and 0.959 of DEA polygon |

This evidence strengthens the interpretation of the two Currawinya open-water
screening supports, but it does not make DEA Waterbodies final ecological
units. Lake Numalla Aggregation is also broader than the single DEA polygon, so
later support decisions should choose deliberately between named DIWA geometry
and clipped DEA open-water geometry.

## Support-Set Decision

The event-window hydrology series used the bounded default support set:

- five parent Ramsar supports:
  `nwb001_ramsar_ref337`, `nwb002_ramsar_ref1291`,
  `nwb003_ramsar_ref993`, `nwb004_ramsar_ref265`,
  `nwb005_ramsar_ref791`
- four official Ramsar component subunits:
  `nwb001_ramsar_component_359`, `nwb003_ramsar_component_121`,
  `nwb004_ramsar_component_354`, `nwb004_ramsar_component_369`
- two Currawinya DEA Waterbodies clips:
  `nwb005_dea_waterbody_r4yss38r6_v3`,
  `nwb005_dea_waterbody_r4ysdndx8_v3`

The two DIWA named Currawinya geometries and two unresolved Narran named rows
were retained in the crosswalk but not included in the fallback event-window
hydrology run.

## Conclusion

Goal 007 strengthens Currawinya named-subunit evidence and preserves Narran as
an unresolved named-subunit problem. The support set is now more reviewable:
official parent supports, official Ramsar components, DEA open-water screens,
and unresolved named features are explicitly separated.
