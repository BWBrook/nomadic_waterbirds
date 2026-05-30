# Prototype Scope For Goal 003

## Recommended Smallest Defensible Prototype

Goal 003 should build a no-bulk-download wetland-unit and hydrology-access
prototype for a small Murray-Darling Basin/eastern-inland wetland-complex
envelope.

The prototype should not attempt a national analysis, final species list, final
wetland-unit system, or biodiversity ingestion. Its purpose is to prove that
official spatial units, DEA hydrology, and biodiversity validation surfaces can
be aligned in a small area before the project scales.

## Candidate Geography

Recommended envelope:

- Murray-Darling Basin/eastern-inland wetland complexes
- initial preference for a few named floodplain or lake complexes with
  documented official wetland status, DEA water coverage, and likely EAWS
  relevance
- final inclusion deferred until Goal 003 confirms intersections among official
  named wetland sources, DEA products, and public biodiversity/validation
  coverage

The envelope is deliberately smaller than the project vision but still tests
the central ecological problem: wetland use under flood-pulse, drying,
persistence, and regional-water-availability contrasts.

## Candidate Wetland Units

Goal 003 should create a candidate unit table with one row per named wetland
complex and columns for:

- official source name and identifier
- source type: DIWA, Ramsar, CAPAD/protected area, EAWS name/code if publicly
  visible, or other official source
- geometry source and licence
- overlapping DEA Waterbodies geohashes
- whether custom DEA Water Observations raster masks are likely required
- Geofabric basin/catchment context
- expected biodiversity alignment: eBird, Birdata, EAWS, ALA context
- known uncertainty or boundary caveat

This table should be committed before any real biodiversity data request or
bulk hydrology extraction.

## Temporal Grain

Use monthly summaries for the first hydrology design, with seasonal summaries
as a secondary roll-up. Monthly grain is the smallest sensible unit for lag,
novelty, persistence, drying, and event timing while remaining realistic for
initial computation and validation.

Goal 003 should not yet fit models. It should define how monthly metrics would
be calculated from DEA Water Observations and whether Waterbodies time series
are adequate for any candidate subunits.

## First Hydrology Metrics

Prototype metrics:

- current wet area or proportion wet
- one-month and three-month lagged wetness
- wetting novelty after a dry spell
- cumulative wet months
- drying velocity
- regional water availability within candidate buffers or basin/context units

DEA Water Observations should be treated as the authoritative source for these
metrics. DEA Waterbodies time series can be used for fast screening where
mapped open-water subunits are adequate.

## Biodiversity Stream Status

For Goal 003:

- eBird should remain access-request gated; use only public metadata checks or
  request-preparation notes unless Barry approves a request
- Birdata should remain request-gated
- EAWS should be inspected only through public pages, reports, or public
  database surfaces without credentialed access
- ALA should be used only for public taxonomy/range-context feasibility checks,
  not absence or trend inference

## Scaling Gates

Do not scale beyond the prototype until these gates pass:

1. Unit crosswalk: named wetland complexes can be linked to official geometry,
   DEA hydrology support, and biodiversity/validation names or locations.
2. Hydrology support: monthly DEA Water Observations summaries can be defined
   with clear handling of invalid pixels and missing observations.
3. Open-water limitation: DEA Waterbodies overlap is adequate for some units or
   clearly flagged as insufficient for vegetated/floodplain wetlands.
4. Biodiversity feasibility: eBird/Birdata/EAWS access and terms are clear
   enough to design extraction without breaching provider conditions.
5. Validation design: candidate units can support spatial, temporal, and
   hydrological-event blocking.

## Recommended Goal 003

Recommended Goal 003: create the prototype wetland-unit crosswalk and hydrology
metric specification for the MDB/eastern-inland pilot, using only public
metadata and small official geometry/product-access checks that do not require
private credentials or bulk biodiversity downloads.
