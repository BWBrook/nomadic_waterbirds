# Data Access Feasibility

## Purpose

This memo evaluates whether the candidate data streams are credible enough for
the first small prototype of the hydrological reaction-norm workflow. It is
based on the current-source evidence in
[source_evidence_register.md](source_evidence_register.md). No external data
were downloaded, requested, or processed for Goal 002.

## Summary Recommendation

Start Goal 003 with a public-source, hydrology-first prototype:

- use DEA Water Observations (Landsat) as the authoritative event-scale water
  source [S01]
- use DEA Water Observations Statistics only for screening and broad context
  [S02]
- use DEA Waterbodies v3 as a convenient open-water subunit layer where it
  overlaps candidate wetlands [S03]
- define named wetland-complex candidates from official wetland sources, then
  test whether DEA Waterbodies and/or custom raster masks adequately represent
  their hydrological behaviour [S19, S20, S21]
- treat eBird, Birdata, and EAWS as feasible but permission- or
  terms-gated biodiversity streams until access/request conditions are
  explicitly satisfied [S05, S06, S09, S14]

## Data Stream Feasibility

### DEA Water Observations

Feasibility: high for the prototype hydrology layer.

DEA Water Observations (Landsat) is the current official DEA product for
per-scene surface-water observations (`ga_ls_wo_3`). It is 30 m, covers
Australia from 16 August 1986 to present, has ongoing daily updates, and is CC
BY 4.0 with a supplied DOI and citation [S01]. This is the best source for
monthly, seasonal, lagged, novelty, persistence, and drying metrics because it
preserves the underlying observation timing.

Key constraints:

- invalid pixels, cloud, cloud shadow, and scene-quality issues must be handled
  explicitly [S01]
- a later prototype must choose quality thresholds and document how invalid
  observations affect each wetland unit [S01]
- direct use of `ga_ls_wo_3` will likely require DEA Sandbox, NCI, AWS, or
  Open Data Cube access design; this goal did not run those tools [S01]

DEA Water Observations Statistics are useful for reconnaissance, broad
screening, and context because they provide annual, seasonal, and multi-year
frequency summaries [S02]. They should not replace the event-scale Water
Observations layer for reaction-norm modelling because the paper needs current
and lagged hydrological states, wetting novelty, and drying dynamics.

### DEA Waterbodies

Feasibility: high as a subunit and screening layer; medium as the sole wetland
unit layer.

DEA Waterbodies v3 provides mapped waterbody polygons, geohash identifiers,
shapefile/AWS/WMS access, and per-waterbody `pc_wet` and `px_wet` time series
[S03]. It is attractive for Goal 003 because it can quickly test whether
open-water basins have enough temporal variation and spatial overlap with
waterbird records.

Limitations are central for this project. DEA Waterbodies measures wet surface
area, not depth, volume, water source, or ecological wetland function [S03].
It may under-represent vegetated, diffuse, ephemeral, or floodplain wetlands
that are important to waterbirds. Therefore it should not be adopted as the
final spatial support without comparing it to named wetland complexes and
custom masks.

### DEA Wetlands Insight Tool

Feasibility: medium as a method reference; low as the first spatial support
unless the prototype is in Queensland.

The DEA Wetlands Insight Tool (Qld) summarises water, green vegetation, dry
vegetation, and bare soil for key Queensland wetlands since 1987 [S04]. Its
combined water/vegetation framing is scientifically useful for floodplain and
vegetated wetland interpretation. However, it is Queensland-specific and has
linework and threshold caveats [S04]. Use it as method evidence and, if the
prototype includes Queensland wetlands, as a candidate comparator.

### eBird Complete Checklists

Feasibility: high scientific value; access-gated.

The eBird Basic Dataset is the core raw eBird observation and metadata product,
updated monthly and available to logged-in users after a data request [S05].
The data-use help states that public eBird data require a request, are
purpose-specific, and cannot be passed on to another user [S06].

Complete checklists remain the preferred citizen-science stream because eBird
defines them as lists where birding was the primary purpose and every species
identified to the observer's best ability was reported [S07]. That supports
stronger non-detection inference than opportunistic presence-only data, but it
does not remove detectability bias. Effort, duration, distance, protocol,
observer count, timing, and spatial sampling intensity must remain explicit.

Sensitive-species handling is not optional. eBird restricts public output for
sensitive species, including site-level suppression or coarser display [S08].
Goal 003 should not assume raw sensitive coordinates are available or
publishable.

### Birdata

Feasibility: medium; valuable if permission and overlap are resolved.

Birdata extracts require a request form sent to BirdLife Australia; provided
files may not be shared publicly unless the request terms explicitly allow it
[S09]. Birdata's strength is standardised monitoring, especially the 2 ha
20 minute method. BirdLife's eBird collaboration page confirms that the
2 ha 20 minute survey is a key standardised survey type and that BirdLife
periodically imports eBird project checklists using that protocol into Birdata
[S10].

Use Birdata as a prototype stream only after clarifying:

- whether an extract can be used for this project
- whether eBird-imported surveys are included
- how duplicate eBird/Birdata records will be identified
- what raw and derived outputs may be shared [S09, S10]

Until then, Birdata should be planned as a validation or calibration stream,
not a dependency for the first hydrology-unit prototype.

### Atlas of Living Australia

Feasibility: high for taxonomy, range context, and supplementary presence;
low for absence or trend inference.

ALA provides occurrence, taxonomy, geospatial, temporal, and bulk download
access through public APIs, with authentication required for some sensitive or
private access [S11]. ALA terms require users to comply with provider terms,
attribute providers, respect licences, and check restrictions for sensitive
data [S12]. ALA support also warns users to consider licensing and citation
obligations when publishing or sharing outputs [S13].

Use ALA only for:

- taxonomy and name concordance support
- historical range and rare-species presence context
- supplementary presence checks
- identifying candidate data providers or legacy records

Do not treat ALA records as absences. Do not treat an ALA download as a single
licence object; provider-specific licences and sensitivity flags must be
captured in provenance [S12, S13].

### Eastern Australian Waterbird Survey

Feasibility: high validation value; access/export details unresolved.

UNSW's EAWS page confirms a long-running annual aerial survey from 1983 to
present, with waterbird counts, breeding/non-breeding evidence, flooded-area
estimates, and major eastern Australian wetland coverage [S14]. The same page
links reports and an Australian Waterbird Surveys database for public
retrieval [S14].

For this project, EAWS is most credible as:

- independent validation of citizen-science-derived reaction norms
- breeding or nesting evidence where available
- a wetland-name and survey-history crosswalk for eastern Australia and MDB
  prototypes

Goal 003 should inspect the public database fields and export constraints
without assuming that bulk or raw-data reuse is unrestricted [S14].

### Climate Covariates

Feasibility: high as supporting context.

The Bureau's AGCD is the official monthly gridded rainfall analysis and is
suitable for rainfall anomaly or drought-context variables [S15]. Climate Data
Online provides station observations and other data from the Australian Data
Archive for Meteorology [S16]. Climate covariates should support, not replace,
hydrological reaction-norm predictors.

Goal 003 should keep climate to one or two simple context variables unless a
later model-design goal justifies more.

### Static Landscape Covariates

Feasibility: high as static context; not central response units.

Useful official static covariates include:

- Geofabric catchments and hydrological reporting regions for basin/context
  support [S17, S18]
- CAPAD 2024 for protected-area context [S22]
- NVIS 7.0 for broad vegetation context [S23]
- ABARES land-use services for surrounding land-use context [S24]

These layers should be introduced only after each covariate has a defined
ecological or observation-bias role. They should not become a substitute for
hydrological state, hydrological history, or regional water availability.

## Sensitive-Record Handling

Sensitive biodiversity data must be handled stream by stream:

- eBird may suppress or coarsen sensitive-species details [S08]
- ALA may require authentication for sensitive/private access and provider
  terms may impose additional restrictions [S11, S12]
- Birdata extracts may not be publicly redistributed unless approved [S09]
- EAWS public database and report data need export and reuse checks before use
  [S14]

No raw biodiversity records should be committed to Git. Derived outputs should
be published only if they cannot reveal sensitive locations or breach provider
terms.
