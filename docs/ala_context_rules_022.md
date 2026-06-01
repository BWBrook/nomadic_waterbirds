# ALA Context-Only Rules 022

## Decision

ALA remains `context_only` for Goal 022. It can support taxonomy, range,
historical occurrence context, provider provenance review, and sensitive-record
handling design. It must not support absence, non-detection, or core
hydrological reaction-norm inference.

## Allowed Uses

- Taxonomy and name-resolution context.
- Historical and geographic presence context.
- Rare, edge-of-range, or sensitive-record review as presence-only evidence.
- Provider/licence provenance design for later downloads.
- Cross-checking whether project candidate taxa have public context records.

## Forbidden Uses

- No absence or non-detection inference.
- No occupancy or detection/non-detection modelling from ALA-only records.
- No core reaction curves from ALA-only occurrence snapshots.
- No support-month coverage claims from opportunistic presence records.
- No use of sensitive or private records without approved authentication,
  provider terms, and explicit governance review.

## Required Fields For Any Later Context Download

Any later ALA context-only download must retain:

- data provider and dataset name;
- licence and attribution;
- occurrence identifier;
- event date or date precision;
- coordinate uncertainty or precision;
- sensitivity/generalisation flags;
- basis of record;
- taxon identifiers and accepted names;
- download DOI or citation metadata if generated.

## Project Rule

If a later analysis needs absence-style evidence, it must come from a stream
with explicit survey completeness and effort metadata, such as approved eBird
complete-checklist records or another standardised survey stream with documented
non-detection logic. ALA is not that stream.
