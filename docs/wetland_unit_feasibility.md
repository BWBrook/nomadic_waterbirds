# Wetland Unit Feasibility

## Purpose

This memo compares candidate spatial supports for the first prototype. The
goal is not to choose the final wetland-unit system. It is to recommend a
small, testable strategy that preserves hydrological dynamics, biodiversity
alignment, interpretability, and uncertainty.

Evidence IDs refer to [source_evidence_register.md](source_evidence_register.md).

## Candidate Strategies

| Strategy | Pros | Cons | Licensing/access | Hydrology extraction | Biodiversity alignment | Mapping and interpretation | Uncertainty implications |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Named wetland polygons or complexes from DIWA/Ramsar and related official sources | Ecologically legible; maps to management language; easier for supervisor/reviewer interpretation; DIWA includes nationally important wetland criteria and descriptions [S19]; Ramsar has national spatial data [S21]. | DIWA is maintained for reference and not updated since 2005 [S19]; spatial metadata warn that current boundary authority and state-source restrictions must be checked [S20]; Ramsar is too sparse. | DIWA metadata and Ramsar catalogue require source-specific licence/acknowledgement checks [S20, S21]. | Works well if polygons represent the hydrological unit; may be too coarse or stale for floodplain dynamics. | Best fit for EAWS and management-facing wetland names if crosswalk succeeds [S14]. | Strongest interpretability for figures and wetland-role classes. | Boundary age and coarse complexes require explicit boundary-sensitivity tests. |
| DEA Waterbodies v3 polygons | Current official DEA product; ready waterbody IDs; shapefile/AWS/WMS access; per-waterbody time series of wet percentage and wet pixels [S03]. | Detects open-water waterbodies, not necessarily entire ecological wetlands; may miss vegetated or diffuse floodplain inundation; area is not depth or volume [S03]. | CC BY 4.0 with DOI/citation [S03]. | Very feasible for first hydrology smoke tests and open-water subunits. | Alignment with eBird/EAWS depends on whether records can be assigned to the relevant waterbody or complex. | Good for subunit maps; weaker if used alone for ecological wetland roles. | Need omission uncertainty for wetland habitat not represented by mapped waterbodies. |
| DEA Water Observations raster grid cells | Directly represents event-scale wet/dry observation at 30 m from 1986 to present [S01]. | Less interpretable than named units; can create artificial units; requires more processing and quality masking. | CC BY 4.0 with DEA citation [S01]. | Best for monthly/seasonal lag, novelty, persistence, drying, and regional water metrics. | Point/checklist records can be linked by buffers or grid assignment, but ecological naming is weaker. | Useful for gridded prototype or within-polygon summaries; poor as sole final map unit. | Grid support lets uncertainty be propagated from observation validity and aggregation choices. |
| Basin or catchment supports from Geofabric | Hydrologically coherent context; official hydrological feature/catchment framework under CC BY 4.0 [S17, S18]. | Too coarse for wetland ecological roles and local bird responses; catchments are not wetlands. | Public access via download/web services; CC BY 4.0 [S17, S18]. | Useful for regional water availability, basin identity, and blocking. | Good for spatial blocking and context; weak for local checklist attribution. | Good context layer, not response-unit layer. | Coarse supports can hide wetland heterogeneity; use as context only. |
| DEA Wetlands Insight Tool style units | Combines water and vegetation dynamics and has wetland-oriented interpretation [S04]. | Current official product located in Queensland; linework and threshold caveats apply [S04]. | DEA product documentation and access route apply for Qld product [S04]. | Strong method reference for wetland cover dynamics where available. | Potentially useful for Queensland prototype only. | Good conceptual fit for wetland condition and dynamics. | Must not generalise Qld product availability nationally without verification. |
| Hybrid named-complex plus DEA subunits | Keeps management/ecological names while measuring hydrology with official DEA products; allows open-water subunits, raster summaries, and catchment context. | Requires crosswalks, boundary decisions, and uncertainty reporting. | Combines source-specific licences; each layer must be tracked [S01, S03, S17, S19, S20, S21]. | Best balance: Water Observations for metrics; Waterbodies for quick subunit tests; Geofabric for context. | Best balance if eBird/EAWS records can be assigned to named complexes and subunits. | Strongest route to maps reviewers can understand while preserving dynamics. | Requires explicit unit-support sensitivity, but makes that sensitivity visible. |

## Recommended Prototype Unit Strategy

Use the hybrid strategy for Goal 003.

The first prototype should define a small MDB/eastern-inland wetland-complex
envelope from official named wetland sources, then create three linked unit
supports:

1. named wetland complex: the interpretation and reporting unit
2. DEA Waterbodies v3 subunits: fast open-water time-series screening where
   mapped waterbodies overlap the named complex [S03]
3. DEA Water Observations raster summaries: the authoritative event-scale
   hydrology layer for current, lagged, novelty, persistence, and drying
   metrics [S01]

Use Geofabric only for basin identity, hydrological context, and validation
blocking, not as the response unit [S17, S18].

## Prototype Geography

The smallest defensible geography is a Murray-Darling Basin/eastern-inland
wetland-complex pilot rather than a continental pilot. Goal 003 should select
a handful of named wetland complexes inside that envelope only after confirming
that they intersect:

- official named wetland or protected-area sources [S19, S20, S21, S22]
- DEA Waterbodies and/or DEA Water Observations coverage [S01, S03]
- plausible EAWS or public report/database coverage [S14]
- enough candidate eBird complete checklist density to justify a later access
  request and extraction [S05, S07]

The prototype should be small enough to finish by hand-auditing unit crosswalks
and hydrology coverage before any bulk data workflow is built.

## Feasibility Decision

Do not use a single off-the-shelf wetland layer as the final unit system yet.
The evidence supports a prototype that compares unit supports before committing
to one. DEA Waterbodies is the fastest way to start, but named wetland
complexes and Water Observations raster summaries are needed to avoid reducing
waterbird habitat to open-water polygons alone [S01, S03, S19, S20].
