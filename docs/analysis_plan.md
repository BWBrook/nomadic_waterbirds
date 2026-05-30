# Analysis Plan

## Purpose

This plan translates the project brief into a staged, observation-aware
analysis for estimating hydrological reaction norms of Australia's nomadic
waterbirds. The analysis should explain how species and guilds respond when
wetlands become wet, stay wet, dry, re-wet after drought, or sit within a
landscape where water is regionally scarce or abundant.

The paper should remain an ecological synthesis of dynamic wetland use, not a
static species distribution model.

## Initial Geography And Taxa

The first operational geography is eastern and inland Australia, centred on:

- the Murray-Darling Basin
- Lake Eyre/Kati Thanda-connected systems where feasible
- major eastern wetland complexes
- coastal systems that may operate as drought refugia

National expansion is a later decision that requires documented data quality,
coverage, and validation support.

The first taxonomic frame should cover roughly 30-60 waterbird species grouped
into interpretable guilds:

- ducks and grebes
- cormorants and darters
- herons and egrets
- ibis and spoonbills
- pelicans
- rails and coots
- shorebirds only if tidal/coastal detection issues can be handled explicitly

Colonial breeders should be analysed as a distinct response class because
breeding response depends on hydroperiod persistence, nesting conditions, and
recruitment opportunity rather than water presence alone.

## Research Questions

1. Which hydrological states and histories best explain waterbird occurrence,
   relative abundance, and breeding evidence?
2. How do lag structures differ among species and functional guilds?
3. Does wetting novelty after dry periods explain use better than absolute wet
   area for nomadic or opportunistic species?
4. How does regional water availability change the local value of a wetland?
5. Which wetlands behave as drought refugia, flood-pulse foraging sites,
   breeding-support wetlands, stepping-stones, variable-use wetlands, or
   low-response/uncertain wetlands?
6. Which species-level response traits are predictable from guild, breeding
   strategy, dispersal ecology, and conservation status?

## Working Hypotheses

- Opportunistic foragers respond rapidly to newly inundated wetlands, while
  colonial breeders require longer wet persistence before breeding or abundance
  peaks.
- Wetting novelty after dry periods can be more informative than absolute wet
  area because flood pulses mobilise food resources.
- A wetland's role is context-dependent: holding water during regional drought
  can make it a refuge, while the same wetland can be less distinctive when
  water is widespread.
- Drought refugia and breeding engines are overlapping but non-identical
  ecological roles.
- Guild, breeding strategy, dispersal ecology, and conservation status should
  explain part of the variation in species-specific hydrological response.

## Core Units

Analysis units should be selected only after a wetland-unit review, but the
foundation expectation is:

- spatial unit: named wetland polygons, wetland complexes, or grid cells with a
  transparent crosswalk to wetland names
- temporal unit: monthly or seasonal time steps, with the final grain chosen to
  match hydrology, biodiversity sampling, and breeding evidence
- biological unit: species-level responses with partial pooling to guild and
  breeding-strategy levels
- landscape context: regional water availability within biologically meaningful
  buffers, with candidate scales such as 50, 100, and 250 km

## Hydrological Predictors

Candidate hydrological covariates include:

- current wet area or proportion wet
- one-month, seasonal, and multi-season lagged wetness
- recent change in wet area
- wetting novelty after dry intervals
- cumulative wet months
- hydroperiod persistence
- drying velocity
- regional wetland availability around the focal site
- contrast between local wetness and regional scarcity

Predictor construction should preserve interpretable units and record
aggregation choices in provenance logs.

## Observation Model Requirements

Citizen-science data must be treated as observation-biased sampling, not aerial
survey abundance. Models using complete checklists should include, as available:

- duration
- distance travelled
- number of observers
- protocol
- time of day
- day of year
- checklist completeness
- repeated visits or spatial sampling intensity
- proximity to roads, towns, popular wetlands, or access points

Counts should be expected to be overdispersed and may require hurdle,
zero-inflated, negative-binomial, or related observation structures.
Occurrence can be modelled as a separate endpoint or a linked endpoint.

## Estimands

Primary estimands:

- species-level hydrological reaction curves for current wetness, lagged
  wetness, novelty, persistence, drying, and regional scarcity
- guild-level partial-pooled reaction curves
- lag-profile summaries describing response timing and persistence
- wetland ecological-role probabilities with uncertainty
- hindcast contrasts for major dry, flood-pulse, and post-drought periods

Secondary estimands:

- difference between refuge probability and breeding-support probability
- species or guild sensitivity to regional water scarcity
- predictive performance under spatial, temporal, and hydrological-event
  blocking
- bias sensitivity under synthetic observer-behaviour scenarios

## Candidate Model Families

Candidate families are allowed only if they preserve interpretable reaction
functions:

- hierarchical GAMMs
- Bayesian additive models
- INLA models
- Stan or TMB hierarchical models
- two-stage machine-learning-plus-inference workflows, where machine learning
  is used for nuisance prediction or screening and final ecological claims come
  from interpretable response summaries

The selected modelling engine should be justified by the data volume,
observation structure, interpretability, uncertainty reporting, and validation
performance.

## Ecological Interpretation Boundaries

- Treat effects as observational associations and predictive response
  structure, not experimental causal effects.
- Do not infer absence from opportunistic presence records.
- Do not interpret citizen-science counts as absolute abundance without an
  observation model and appropriate validation.
- Do not map wetland roles without uncertainty.
- Do not generalise beyond the validated geography, species set, temporal
  coverage, or data streams.

## Staged Analysis Phases

1. Foundation: operating rules, plans, registers, and reproducibility contract.
2. Data-access assessment: permissions, licenses, data dictionaries, and
   inclusion/exclusion decisions for each stream.
3. Wetland-unit design: candidate spatial units, hydrological extraction
   feasibility, naming/crosswalk rules, and prototype geography.
4. Hydrology prototype: monthly or seasonal wetness covariates for a small
   vetted wetland set.
5. Biodiversity prototype: complete-checklist extraction and observation
   covariates for a small species/guild subset.
6. Integrated prototype: first occurrence and relative-abundance reaction
   curves with blocked validation.
7. Breeding/validation integration: EAWS or other independent evidence used
   either as validation or as a separate observation process.
8. Full analysis: expanded species, wetlands, validation blocks, bias stress
   tests, and uncertainty-bearing wetland-role classification.
9. Manuscript and archive: figures, tables, reproducible workflow, manuscript
   build, and repository/archive release checks.
