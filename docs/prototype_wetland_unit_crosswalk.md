# Prototype Wetland Unit Crosswalk

## Purpose

This document interprets
[prototype_wetland_unit_crosswalk.csv](prototype_wetland_unit_crosswalk.csv).
The CSV is a design contract for the first small wetland-unit and hydrology
smoke test. It is not a final wetland-unit decision and it does not contain
raw geometry, hydrology, or biodiversity data.

## Candidate Selection

The crosswalk includes 7 candidate wetland complexes. Five are recommended for
the next extraction smoke test and 2 are retained as deferred edge comparators.

Recommended smoke-test candidates:

- Macquarie Marshes: northern MDB floodplain, major breeding/refuge value, and
  a strong test of vegetated wetland caveats [S25].
- Narran Lake Nature Reserve: terminal Narran/Condamine wetland with open-lake
  and lignum-floodplain breeding dynamics [S26].
- Gwydir Wetlands: terminal vegetated wetlands where the Ramsar parcel is much
  smaller than the broader ecological wetland system [S27].
- Kerang Wetlands: multi-lake southern MDB complex with open-water,
  drought-refuge, breeding, salinity, and regulation contrasts [S28].
- Currawinya Lakes: arid Paroo system with contrasting Lake Numalla and Lake
  Wyara hydrology, drought-refuge value, and breeding events [S29].

Deferred edge comparators:

- The Coorong, Lakes Alexandrina and Albert: valuable downstream/coastal edge
  case, but too large, estuarine, and regulated for the first smoke test [S30].
- Coongie Lakes: strong Lake Eyre Basin boom-bust comparator, but outside the
  core MDB smoke-test centre and too large for the first pass [S31].

## Selection Rationale

The selected smoke-test set spans the hydrological behaviours needed for a
reaction-norm prototype:

- floodplain breeding and refugia
- terminal wetlands
- vegetated wetland detection limits
- multi-lake open-water systems
- arid boom-bust wetting and drying
- northern and southern MDB contrasts

The list deliberately favours official Ramsar/DCCEEW pages for first-pass
traceability. That keeps the prototype reviewable while the project still
avoids committing raw geometry or making a final unit choice.

## Unit Support Interpretation

Each candidate should be treated as a named interpretation unit with 3 linked
supports:

1. named wetland complex from official public sources
2. DEA Waterbodies subunits where open water is mapped
3. DEA Water Observations raster summaries as the authoritative hydrology
   metric source

Geofabric should be used for basin identity, regional water availability, and
spatial blocking context, not as the local wetland-response unit.

## Deferred Or Rejected Starting Points

Booligal Wetlands, Great Cumbung Swamp, and related lower Lachlan wetlands are
ecologically valuable and officially visible in CEWH material [S32]. They are
deferred because the first pass found a less direct geometry/source pathway
than the Ramsar candidates. They should be reconsidered once the Ramsar-based
crosswalk pattern is working.

Lake Cowal is deferred because this pass did not establish a sufficiently
direct official geometry and biodiversity-alignment pathway for the first smoke
test. It remains plausible for a later Lachlan/Central NSW expansion.

## Caveats

- DEA Waterbodies is a screening/subunit aid, not a substitute for vegetated or
  diffuse floodplain habitat.
- Ramsar boundaries may be narrower than ecologically relevant wetland
  complexes, especially for Gwydir and Macquarie.
- Large regulated or coastal systems, especially the Coorong/Lower Lakes, need
  subunit stratification before monthly hydrology summaries are meaningful.
- Public biodiversity alignment is not biodiversity data. eBird, Birdata, and
  EAWS access/reuse questions remain unresolved until later goals.
