# Validation Plan

## Purpose

Validation must test whether estimated hydrological reaction norms generalise
across places, times, hydrological regimes, and sampling biases. The central
validation claim should never rest on random cross-validation alone.

## Claims That Need Validation

| Claim | Required validation evidence |
| --- | --- |
| Species and guilds have interpretable hydrological reaction norms. | Held-out prediction and uncertainty checks for current, lagged, novelty, persistence, drying, and regional-scarcity terms. |
| Wetland ecological-role classes are meaningful. | Role probabilities with uncertainty plus sensitivity to geography, time period, hydrological metric, and data stream. |
| Citizen-science signals recover real wetland-use dynamics. | Independent validation against aerial-survey or standardised survey evidence where access and alignment allow. |
| Drought refugia differ from breeding-support wetlands. | Separate validation of dry-period persistence use and breeding/nesting evidence. |
| Results are not artefacts of observer behaviour. | Synthetic-bias stress tests and observation-model diagnostics. |

## Spatial Blocking

Spatial validation should hold out wetland complexes, basins, or spatial blocks
large enough to test transfer beyond local sampling hotspots.

Candidate block definitions:

- basin or sub-basin groups
- named wetland complexes
- spatial grid blocks with buffers to reduce leakage
- coastal versus inland blocks where ecological interpretation requires it

The chosen blocks should be documented before fitting final models.

## Temporal Blocking

Temporal validation should hold out contiguous periods rather than random dates.

Candidate temporal tests:

- train on earlier years and test on later years
- rotating multi-year folds
- wet-season or breeding-season holdouts
- pre-defined drought, post-drought, and flood-pulse periods once the hydrology
  timeline is constructed

Temporal validation should report whether lagged hydrological terms improve
prediction and interpretation in held-out periods.

## Hydrological-Event Blocking

Hydrological-event blocking should ask whether the model can predict responses
to event types that matter ecologically:

- severe drought years
- newly wet post-drought basins
- region-wide flood pulses
- drying or contraction phases
- high regional scarcity with local persistence
- widespread water availability where birds may disperse across alternatives

Events must be defined from the hydrology data, not chosen after inspecting
bird-response success.

## Independent Data Validation

The Eastern Australian Waterbird Survey or other standardised survey streams
should be used as independent validation where permissions, timing, spatial
alignment, and response definitions allow.

Validation questions:

- Do citizen-science-derived reaction norms recover independent wetland-use
  patterns?
- Do predicted role classes correspond to independent abundance, diversity, or
  breeding evidence?
- Are refuge and breeding-support predictions separable in independent data?

If independent integration is not feasible, the reason should be recorded in
the data-stream register and decision log.

## Synthetic Bias Stress Test

The bias stress test should simulate observer behaviour concentrated near:

- roads and towns
- popular or iconic wetlands
- coastal population centres
- accessible reserve infrastructure
- charismatic or easily detected species

The stress test should compare known simulated hydrological responses against
responses recovered after imposing biased sampling. A model that invents strong
hydrological responses under biased sampling should not support central claims
without redesign.

## Diagnostics And Reporting

Report:

- predictive performance by species, guild, block, and event type
- calibration of occurrence and count endpoints
- uncertainty intervals for reaction curves and wetland roles
- sensitivity to alternative wetland units and temporal aggregation
- sensitivity to effort covariates and sampling-intensity controls
- failure modes, not only successful folds

Random folds may be used as secondary diagnostics, but they cannot be presented
as the main evidence of generalisation.
