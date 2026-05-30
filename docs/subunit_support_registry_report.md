# Subunit Support Registry Report

## Purpose

Goal 006 builds the first hydrology-only parent-child support registry for the
five Goal 005 Ramsar parent supports. It records candidate Ramsar components
and DEA Waterbodies open-water overlaps, then marks which child supports were
included in the bounded subunit hydrology prototype.

This registry is support evidence only. It is not a final ecological wetland
unit system and does not support bird-response, breeding, abundance, refuge, or
ecological-role claims.

## Sources And Staging

Executable files:

- [../scripts/subunit_hydrology_006.py](../scripts/subunit_hydrology_006.py)
- [../settings/subunit_hydrology_006.json](../settings/subunit_hydrology_006.json)

Committed outputs:

- [subunit_support_registry.csv](subunit_support_registry.csv)
- [subunit_support_registry_manifest.json](subunit_support_registry_manifest.json)
- [subunit_hydrology_prototype_summary.csv](subunit_hydrology_prototype_summary.csv)
- [subunit_hydrology_prototype_manifest.json](subunit_hydrology_prototype_manifest.json)

Raw source files were staged only under ignored `artifacts/` paths:

| Staged file | Bytes | SHA-256 | Commit status |
| --- | ---: | --- | --- |
| `artifacts/subunit_supports/raw/ramsar_goal006_subset.geojson` | 497145 | `3486b9639434995ee3d24eaa8b064860508288366b4a4a9d4741ed9988b63bd7` | Not committed |
| `artifacts/subunit_supports/raw/ga_ls_wb_3_v3.zip` | 46502008 | `7f491f8487770ad237e7000ff5f3cb3b607e18abe1a0690d5ea4a6c2f3241450` | Not committed |

The DEA Waterbodies v3 zipped shapefile opened locally with 324890 features in
`EPSG:3577`. The overlap screen kept the top three intersecting Waterbodies
per parent support for review, except where fewer overlaps were found.

## Registry Coverage

The registry contains 36 candidate subunit rows: 22 Ramsar component rows and
14 DEA Waterbodies overlap rows. All five parent candidates are represented.

| Candidate | Ramsar component rows | DEA Waterbodies overlap rows | Selected for hydrology | Registry status |
| --- | ---: | ---: | --- | --- |
| NWB001 Macquarie Marshes | 2 | 3 | `nwb001_ramsar_component_359` | 1 included; 4 retained |
| NWB002 Narran Lake Nature Reserve | 1 | 3 | None | 4 retained |
| NWB003 Gwydir Wetlands | 4 | 2 | `nwb003_ramsar_component_121` | 1 included; 5 retained |
| NWB004 Kerang Wetlands | 14 | 3 | `nwb004_ramsar_component_354`; `nwb004_ramsar_component_369` | 2 included; 15 retained |
| NWB005 Currawinya Lakes | 1 | 3 | `nwb005_dea_waterbody_r4yss38r6_v3`; `nwb005_dea_waterbody_r4ysdndx8_v3` | 2 included; 2 retained |

## Selection Decisions

Macquarie Marshes used the official Ramsar component for Macquarie Marshes
Nature Reserve. Wilgara Wetland and the three largest DEA Waterbodies overlaps
were retained for later because the immediate goal was to keep one
floodplain-sensitive official component while avoiding a premature
open-water-only split.

Narran Lake Nature Reserve was represented in the registry, but no child
subunit was selected for hydrology. The Ramsar service exposes a single
component matching the parent support, and the prototype did not verify a
strong enough named lake/lignum split.

Gwydir selected the official `Old Dromana` Ramsar component as a small
hydrology subunit. The other three Ramsar components and the two Waterbodies
overlaps were retained for later comparison.

Kerang selected two official named Ramsar components, `Reedy Lake` and
`Lake Charm`, to meet the minimum two-subunit Kerang expectation. The remaining
Ramsar components and top Waterbodies overlaps were retained because the
registry does not yet settle saline, freshwater, and regulation strata.

Currawinya selected the two largest intersecting DEA Waterbodies polygons as
bounded open-water screening subunits. These rows do not prove official Lake
Numalla/Lake Wyara identity; they are retained as reproducible open-water
subunits until a stronger named-lake source is added.

## What This Supports

The registry supports reproducible parent-child provenance, hydrology-only
subunit extraction, and review of which subunits are ready, retained, or
deferred. It also shows where Ramsar components and DEA Waterbodies answer
different questions.

The registry does not settle final ecological wetland-response units, does not
replace vegetated floodplain supports with open-water polygons, and does not
justify biodiversity linkage without a later data-access and validation goal.
