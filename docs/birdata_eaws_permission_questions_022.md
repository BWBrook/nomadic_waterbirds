# Birdata and EAWS Permission Questions 022

## Purpose

This brief records questions to resolve before Birdata or EAWS can move beyond
secondary/validation candidate status. No contact, request, login, download, or
private data processing occurs in Goal 022.

## Birdata

Current status: `needs_clarification`.

Questions for BirdLife Australia before any extract request:

1. Can BirdLife Australia provide a bounded extract for the current wetland
   support envelope and `2018-01-01` through `2024-12-31` pilot window?
2. Which survey programs and protocol fields are available, especially 2 ha
   20 minute surveys, fixed-area searches, repeat shared sites, and breeding
   evidence fields?
3. Are eBird-imported BirdLife Australia Monitoring Project surveys included
   in the extract, and if so, what fields support duplicate detection against a
   separate eBird request?
4. What are the terms for raw data storage, derived table sharing, publication,
   and archiving?
5. How are sensitive/threatened records handled, and can exact locations be
   supplied for approved research or only generalised locations?
6. Are observer identifiers, site names, shared-site polygons, or survey point
   names available in a privacy-safe form?
7. Can the extract include survey completeness, protocol duration, area,
   distance, observer count, and repeat-survey metadata?
8. Are conservation-status fields excluded, and should the project source those
   from separate official conservation-status sources if needed?

Allowed role after clarification:

- calibration/sensitivity lane for standardised surveys;
- breeding-evidence candidate where fields support it;
- not a direct replacement for the eBird complete-checklist pilot.

## EAWS

Current status: `needs_clarification`.

Questions for UNSW / public database review before any extract or formal
agreement:

1. Which EAWS table fields are publicly downloadable, and which require a
   formal agreement?
2. Are waterbird counts, breeding/rookery evidence, flooded extent, wetland
   identifiers, survey dates, and survey-route metadata available in a reusable
   form?
3. What licence or acknowledgement terms apply to raw tables, derived
   summaries, figures, and manuscript use?
4. Can wetland names/codes be crosswalked to Goal 020 `support_id` values
   without exposing restricted or proprietary geometry?
5. Are annual survey windows comparable with monthly hydrology joins, or should
   EAWS remain at annual/survey-period validation grain?
6. Are species groups, breeding indicators, and non-breeding counts comparable
   across the full `2018-2024` pilot window?
7. Are there restrictions on publishing site-level abundance or breeding
   information for sensitive wetlands or species?

Allowed role after clarification:

- independent validation of abundance direction, breeding context, or
  drought-refuge hypotheses;
- not an occurrence/non-detection lane and not a replacement for eBird effort
  covariates.
