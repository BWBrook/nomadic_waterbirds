# Goal 012 Hydrology Metadata Cache And S3 Prototype

Accessed date for current official source checks: `2026-05-31`.

## Scope

This is a metadata-acquisition prototype only. It does not compute wet area,
wet proportion, lags, novelty, drying velocity, persistence, or ecological
response metrics.

## Official Source Checks

- [DEA Water Observations (Landsat)](https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/?tab=overview)
  remains the primary product target.
- [DEA AWS/S3 access](https://knowledge.dea.ga.gov.au/guides/setup/AWS/data_and_metadata/)
  documents the public bucket, public inventory, and no-sign S3 access route.
- [DEA STAC guidance](https://knowledge.dea.ga.gov.au/notebooks/How_to_guides/Downloading_data_with_STAC/)
  documents STAC metadata search and cloud-data streaming.
- [DEA FAQ download guidance](https://knowledge.dea.ga.gov.au/guides/about/faq/)
  supports direct S3 download when exact paths are known.

## Candidate And Months

Candidate: `NWB002` Narran Lake Nature Reserve, support
`nwb002_ramsar_ref1291`.

Months: `2018-01, 2022-11, 2024-12`.

Rationale: Default Goal 012 candidate: current support set member, all 84 Goal 009 full-window rows blocked, and prior Goal 004/011 evidence includes a known 093/080 S3 path-row for Narran product-access probes.

The candidate-month STAC cache key uses
`collection|candidate_id|month|candidate_bbox_hash`, with the bbox sourced from
Goal 009 blocked-row context. Direct S3 discovery used the known Narran
`093/080` path-row from prior smoke and Goal 011 evidence.

## Prototype Results

- STAC preflight status: `unavailable_service_unstable`.
- Direct S3 route item counts by month: 2018-01=3, 2022-11=4, 2024-12=4.
- Item-set comparison status by month: 2018-01=comparison_blocked_stac_unavailable, 2022-11=comparison_blocked_stac_unavailable, 2024-12=comparison_blocked_stac_unavailable.

STAC cache fill was launched only if every configured month passed the strict
preflight. When the preflight failed, the script wrote no STAC item cache and
continued with S3 metadata only.

Direct S3 discovery listed bounded path-row/month prefixes and used `HEAD`
metadata for discovered Water Observations COG keys. Raw listings and HEAD
metadata were written only under ignored `artifacts/` paths.

## Decision

The direct S3 route is technically viable for the known Narran `093/080`
path-row/month prefixes, but it is not yet scientifically equivalent for the
whole Narran support because path-row coverage has not been proven from the
support bbox and STAC/ODC comparison was blocked or incomplete.

The cached STAC route remains the nearest scientifically equivalent design,
but should not carry a full extraction until the strict preflight passes.

## Recommended Goal 013

Recommended Goal 013: build a bounded support-to-path-row discovery and
metadata-equivalence prototype for NWB002. It should derive all Landsat
path/row candidates intersecting the support bbox, run S3 listings for the
three probe months, and compare those keys against STAC or an official ODC/NCI
metadata query when available. If STAC is still unavailable, use ODC/NCI or DEA
Sandbox as the official comparator before promoting direct S3 extraction.

Current route recommendation from the comparison table: Promote to Goal 013 prototype only if path-row coverage can be derived for every support bbox.
