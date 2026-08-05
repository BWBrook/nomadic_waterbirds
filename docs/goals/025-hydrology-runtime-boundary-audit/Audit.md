# Goal 025 Hydrology Runtime Boundary And Retirement Audit

## Decision Summary

Goal 019 is the canonical hydrology runtime/output boundary. It produces the
11-support x 84-month (924-row) direct-S3 table and is the only production
table consumed by Goal 020. The runtime is not a single module: it imports the
Goal 016 extractor, Goal 014 helpers, Goal 007/005 metric helpers, and Goal 013
support-to-path/row provenance. Historical Goals 004-018 remain useful
provenance, but no safe deletion or broad extraction is justified in this
audit because local references exist and external human callers are unknown.

**Recommended next decision: defer runtime retirement/extraction.** Freeze Goal
019/020 as the canonical boundary. Do not open an extraction seam until the
Goal 007/019 missingness and temporal-derivation contract is explicitly chosen
and parity can be proved; do not add a generic hydrology framework now.

## Starting State And Protected Hashes

- Repository: `/Users/bwbrook/papers/nomadic_waterbirds`, `main`, HEAD
  `e121636`, initially `main...origin/main` with only the pre-existing Goal
  025 packet untracked.
- Read-only inspection only; no production command, service, S3/STAC/GDAL
  access, remote compute, raw biodiversity data, or source/runtime edit was
  performed.
- Protected SHA-256 values captured before writing this report:

| Output | SHA-256 |
|---|---|
| `docs/direct_s3_full_window_hydrology_019_manifest.json` | `3b2f8c85a5f59168aebf914be4ec4eef68c09cdd48c1035d46d7cf21d6ab0cfc` |
| `docs/direct_s3_full_window_hydrology_019_series.csv` | `793593532c2adb8e673f0ce70d72e97d5f0dba58a43dbfeba7a6b490480f26e8` |
| `docs/direct_s3_full_window_hydrology_020_manifest.json` | `ea3d95a619f80987309f4c4fde594a9a3b2113a43820464e715c121f4744c63a` |
| `docs/direct_s3_full_window_hydrology_020_readiness.csv` | `3e26fd391f89a08877b2cde98fdd63d071c261a3415096fd7dd92cc1d2196e26` |

## Canonical Active Graph

The active local graph is:

```text
settings/direct_s3_full_window_hydrology_019.json
  -> scripts/direct_s3_full_window_hydrology_019.py
      -> scripts/direct_s3_all_support_probe_016.py
          -> scripts/direct_s3_extraction_rehearsal_014.py
              -> scripts/event_window_hydrology_007.py
                  -> scripts/official_support_hydrology_005.py
              -> scripts/support_pathrow_metadata_013.py
          -> scripts/event_window_hydrology_007.py
          -> scripts/support_pathrow_metadata_013.py
      -> Goal 019 compact outputs
          -> scripts/audit_direct_s3_full_window_hydrology_020.py
```

Exact evidence:

- Goal 019 command, 11 supports, 84 months, 924 rows, and support-intersecting
  WRS path/row policy are configured at
  `settings/direct_s3_full_window_hydrology_019.json:3-25`.
- Goal 019 imports Goal 016 extraction/support selection at
  `scripts/direct_s3_full_window_hydrology_019.py:25-28`, Goal 014 IO/GDAL
  helpers at `:29-40`, and Goal 007 metric fields/retry helpers at `:41-46`.
- Goal 019 executes Goal 016 extraction, completes the expected grid, derives
  temporal metrics, and adds regional metrics at
  `scripts/direct_s3_full_window_hydrology_019.py:676-750`.
- Goal 016 imports Goal 014, Goal 007, and Goal 013 at
  `scripts/direct_s3_all_support_probe_016.py:29-66`; it rebuilds supports from
  the Goal 007 summary and requires Goal 013 path/row coverage at
  `scripts/direct_s3_all_support_probe_016.py:473-493`.
- Goal 016 performs direct-S3 listing/COG reads and writes one row per selected
  support-month at `scripts/direct_s3_all_support_probe_016.py:506-701` and
  `:976-1009`.
- Goal 014 delegates base summarisation to Goal 007/005 and direct-S3 extraction
  to `scripts/direct_s3_extraction_rehearsal_014.py:29-45` and `:347-349,
  554-640`.
- Goal 013 creates item sets from support-intersecting path/rows at
  `scripts/support_pathrow_metadata_013.py:500-560`; its configuration records
  the Goal 007 support source at `settings/support_pathrow_metadata_013.json:15-19`.
- Goal 007 imports the Goal 005 geometry/retry/base-metric helpers at
  `scripts/event_window_hydrology_007.py:24-48`; Goal 005's Water Observations
  bit decoding, quality flags, and base metrics are implemented at
  `scripts/official_support_hydrology_005.py:414-503`.
- Goal 020 is a consumer/auditor, not an acquisition dependency: it reads Goal
  019 manifest/series/item-set/summary and Goal 018 readiness at
  `scripts/audit_direct_s3_full_window_hydrology_020.py:638-669`, with paths
  fixed in `settings/audit_direct_s3_full_window_hydrology_020.json:23-37`.

Observed local commands are in the corresponding `settings/*.json` files and
historical manifests/logs. These references prove repository-local coupling or
historical invocation only; they do **not** prove that no external human
workflow imports or executes a script.

## Canonical Inputs, Outputs, Consumers

**Inputs and policies**

- DEA Water Observations Landsat `ga_ls_wo_3`, version `1-6-0`, 30 m, EPSG:3577;
  Goal 019 settings `:12-20`.
- Current 11-support set is rebuilt from the Goal 007 event-window support
  summary and geometry, then checked against Goal 013's support-intersecting
  WRS-2 path/row crosswalk (`scripts/direct_s3_all_support_probe_016.py:477-493`).
- Direct public S3 COGs are selected only from support-intersecting WRS path/rows,
  never bbox-only STAC extras (`settings/direct_s3_full_window_hydrology_019.json:21-25`).
- Base classification uses Water Observations `water_bit=128`, invalid bits
  1/2/4/8/16/32/64, meaningful zero/dry values, and quality thresholds in
  `scripts/official_support_hydrology_005.py:445-500` and
  `docs/hydrology_metric_spec.md:57-110,192-208`.

**Outputs and consumers**

- Canonical series: `docs/direct_s3_full_window_hydrology_019_series.csv`, one
  row per support-month; compact item-set provenance in
  `docs/direct_s3_full_window_hydrology_019_item_sets.csv`; support/month
  summaries and manifest are the sibling Goal 019 outputs. Goal 019 reports
  924 computed rows, 751 `quality_high`, 150 `quality_minimum`, and 23
  `quality_fail` rows (`docs/direct_s3_full_window_hydrology_019_report.md`).
- Goal 020 consumes those four outputs and keeps the 23 quality-fail rows as
  `sensitivity_only`; its report records 820 `core_eligible`, 81
  `core_eligible_with_caveat`, and 23 `sensitivity_only` rows.
- The next consumer is constrained bird-linkage design only. No Goal 019/020
  artefact upgrades hydrology readiness into an ecological or bird-data claim.

**Protected invariants**

- Preserve 924 rows (11 supports x 84 months), one support-month key each, and
  direct-S3 support-intersecting WRS path/row selection.
- Preserve meaningful zeros, missing/blocked values, Water Observations bit
  counts, quality vocabulary, lag/novelty/persistence/drying fields, regional
  fields, item hashes, and stable provenance.
- Preserve Goal 020's 23 sensitivity-only rows and the four Goal 018 comparator
  caveats (`core_eligible_with_caveat`); do not alter the four hashes above.
- No hydrology readiness result is an ecological claim, and no bird records,
  effort assumptions, or eBird permissions are changed.

## Goal 007 Versus Goal 019 Temporal Semantics

Both paths use the same Goal 005 base reducer and 0.05 wet-month threshold, but
the temporal contracts are not equivalent.

| Contract | Goal 007 (`event_window_hydrology_007.py`) | Goal 019 (`direct_s3_full_window_hydrology_019.py`) | Consequence |
|---|---|---|---|
| Window | Configured fallback is `2020-01` to `2024-12` (`settings/event_window_hydrology_007.json:5-12`). | Production is `2018-01` to `2024-12` (`settings/direct_s3_full_window_hydrology_019.json:5-11`). | Edge history and row counts differ; matching field names do not imply parity. |
| Base quality/blocked rows | Goal 005 returns `quality_fail` and blank wet flag when thresholds fail (`scripts/official_support_hydrology_005.py:475-500`); Goal 007 also emits blocked base rows with blank values (`scripts/event_window_hydrology_007.py:788-806,839-927`). | Goal 019 maps Goal 016 route failures to fixed `row_status` values and skips derivation on blocked rows (`scripts/direct_s3_full_window_hydrology_019.py:63-70,467-470`). | 019 keeps route failure distinct from computed quality failure. |
| One/three-month lag | Goal 007 reads lag-1/lag-3 values whenever a row exists (`scripts/event_window_hydrology_007.py:700-705`), without a quality-pass guard; trailing-3 averages only quality-passing prior rows (`scripts/event_window_hydrology_007.py:706-713`). | Goal 019 requires quality-passing lag rows (`scripts/direct_s3_full_window_hydrology_019.py:478-490`). | A Goal 007 lag can carry a quality-fail value that Goal 019 leaves missing. |
| Missingness/blocked prior | Goal 007 initializes `dry_prior=0` and stops at missing/bad prior (`scripts/event_window_hydrology_007.py:715-722`); derived booleans are still written for every row (`scripts/event_window_hydrology_007.py:724-765`). | Goal 019 sets `dry_prior=None` when the immediate prior is missing or non-passing (`scripts/direct_s3_full_window_hydrology_019.py:492-508`), skips blocked/quality-fail rows (`scripts/direct_s3_full_window_hydrology_019.py:467-473`), and records `derived_metric_status` (`scripts/direct_s3_full_window_hydrology_019.py:530-549`). | Goal 007 can turn unknown history into zero/False; 019 preserves unknown/partial history. |
| Novelty/persistence | Both use current wet plus at least two immediately preceding dry, quality-passing months (`scripts/event_window_hydrology_007.py:724-741`; `scripts/direct_s3_full_window_hydrology_019.py:510-524,540-544`). | 019 returns novelty as `None` when dry history is unavailable. | `False` in 007 and blank/`None` in 019 are not interchangeable. |
| Drying | Both compute lag-1 and trailing-3 deltas (`scripts/event_window_hydrology_007.py:742-745`; `scripts/direct_s3_full_window_hydrology_019.py:526-529`). | 019 additionally emits `rapid_drying_flag = drying_velocity_1m >= 0.10` (`scripts/direct_s3_full_window_hydrology_019.py:545-548`); 007 does not. | The rapid-drying field is 019-only and must not be backfilled from 007. |
| Regional availability | Goal 007 has no regional derivation in `add_time_history_metrics` or its output field list (`scripts/event_window_hydrology_007.py:688-765,960-995`). | Goal 019 sums quality-passing peer supports, excludes the focal support, and records status (`scripts/direct_s3_full_window_hydrology_019.py:555-590`). | Regional metrics are a new 019 contract, not a legacy-equivalent field. |

The 019 production CSV confirms the boundary: 78 `derived_partial_history`
rows, 823 `derived_with_available_history`, 23 `not_derived_quality_fail`, and
23 `not_computed_row_blocked_or_quality_fail` regional rows. The metric
specification also says regional supports must be documented before use
(`docs/hydrology_metric_spec.md:168-190`); the current implementation uses all
current supports as coarse peers, so this remains a documented caveat rather
than a reason to rewrite production outputs in Goal 025.

## Script Dispositions (Goals 004-020)

Disposition counts over the 19 hydrology scripts: **retain 7, simplify 1,
defer 11, retire 0**. “Defer” means historical evidence remains available but
is not an active production dependency; “simplify” identifies a future seam,
not an edit in this goal. No script is classified safe to retire while external
human invocation is unknown.

| Goal / script(s) and settings | Observed role/evidence | Disposition / confidence |
|---|---|---|
| 004 `hydrology_smoke_test_004.py` / `hydrology_smoke_test_004.json` | Tiny STAC/COG smoke path; `scripts/hydrology_smoke_test_004.py:1-7,202-215`. No active import. | Defer as historical smoke evidence; medium. |
| 005 `official_support_hydrology_005.py` / `official_support_hydrology_005.json` | Shared geometry, retry, Water Observations reducer, and quality implementation; imported by Goal 007 (`scripts/event_window_hydrology_007.py:28-48`). | Retain as active low-level dependency; high. |
| 006 `subunit_hydrology_006.py` / `subunit_hydrology_006.json` | Goal 005-derived parent/child prototype; import is historical (`scripts/subunit_hydrology_006.py:28-50`). | Defer; medium. |
| 007 `event_window_hydrology_007.py` / `event_window_hydrology_007.json` | Support loader, STAC-era extraction, base fields and temporal helper imported by 014/016/019 (`scripts/event_window_hydrology_007.py:28-48`; `scripts/direct_s3_full_window_hydrology_019.py:41-46`). | Simplify only at a future pure temporal-contract seam; high. |
| 008 `narran_subunit_evidence_008.py` / `narran_subunit_evidence_008.json` | Narran crosswalk/evidence script importing Goal 007 (`scripts/narran_subunit_evidence_008.py:16-30`). | Defer; medium. |
| 009 `remote_full_window_hydrology_009.py`, `stac_resilience_probe_009.py` / `remote_full_window_hydrology_009.json` | Historical remote STAC route wrapper/probe (`scripts/remote_full_window_hydrology_009.py:16-24`; `scripts/stac_resilience_probe_009.py:25-34,66-158`). | Defer; medium. |
| 010 `hydrology_recovery_010.py`, `stac_recovery_preflight_010.py` / `hydrology_recovery_010.json` | Recovery wrapper and service-stability preflight over Goal 009 blocked rows (`scripts/hydrology_recovery_010.py:16-24`; `scripts/stac_recovery_preflight_010.py:30-51`). | Defer; medium. |
| 011 `hydrology_acquisition_route_probe_011.py` / (uses Goal 009 settings) | Metadata-only route estimator; explicitly compares direct S3 with STAC (`scripts/hydrology_acquisition_route_probe_011.py:52-87,226-280`). | Defer as route evidence; medium. |
| 012 `hydrology_metadata_cache_s3_012.py` / `hydrology_metadata_cache_s3_012.json` | Bounded STAC preflight and S3 item-set prototype; no 019 import (`scripts/hydrology_metadata_cache_s3_012.py:192-204,693-749`). | Defer; medium. |
| 013 `support_pathrow_metadata_013.py` / `support_pathrow_metadata_013.json` | WRS geometry-intersection crosswalk and direct-S3 item sets imported by 016/014/018 (`scripts/support_pathrow_metadata_013.py:500-560`; `scripts/direct_s3_all_support_probe_016.py:62-66`). | Retain as provenance dependency; high. |
| 014 `direct_s3_extraction_rehearsal_014.py` / `direct_s3_extraction_rehearsal_014.json` | Direct-S3 grid, GDAL, IO, and base reducer wrapper imported by 016/019 (`scripts/direct_s3_extraction_rehearsal_014.py:29-45,347-349`; `scripts/direct_s3_full_window_hydrology_019.py:29-40`). | Retain; high. |
| 015 `comparator_baseline_repair_015.py` / `comparator_baseline_repair_015.json` | Repaired legacy comparator evidence; referenced by Goal 016 comparison settings, not production extraction (`settings/direct_s3_all_support_probe_016.json:41-57`). | Defer as protected audit evidence; high. |
| 016 `direct_s3_all_support_probe_016.py` / `direct_s3_all_support_probe_016.json` | Active extractor and support selector imported/executed by 019 (`scripts/direct_s3_full_window_hydrology_019.py:25-28,690-719`). | Retain as canonical extraction core; high. |
| 017 `legacy_wetness_difference_triage_017.py` / `legacy_wetness_difference_triage_017.json` | Four/six legacy wetness-difference triage evidence; script is a standalone report writer (`scripts/legacy_wetness_difference_triage_017.py:1-5,22-33`) and has no 019 runtime import. | Defer as caveat evidence; high. |
| 018 `pathrow_comparator_reconstruction_018.py` / `pathrow_comparator_reconstruction_018.json` | Reconstructs comparator item provenance; Goal 019 settings consume its readiness CSV (`settings/direct_s3_full_window_hydrology_019.json:37-41`). | Retain as protected provenance producer; high. |
| 019 `direct_s3_full_window_hydrology_019.py` / `direct_s3_full_window_hydrology_019.json` | Restartable canonical 924-row direct-S3 production (`scripts/direct_s3_full_window_hydrology_019.py:676-805`). | Retain as sole production boundary; high. |
| 020 `audit_direct_s3_full_window_hydrology_020.py` / `audit_direct_s3_full_window_hydrology_020.json` | Audits Goal 019 outputs and classifies readiness (`scripts/audit_direct_s3_full_window_hydrology_020.py:638-705`). | Retain as independent audit consumer; high. |

## Evidence Limits And Residual Risks

- Repository search found local imports, settings commands, manifests, reports,
  logs, and tests, but no mechanism that can enumerate human shell commands,
  copied scripts, notebooks, or external clones. External callers therefore
  remain **unknown**, not absent.
- Historical Goal 007/009 route outputs are still referenced as comparison or
  support evidence. Deleting their scripts would risk provenance loss even if
  Goal 019 no longer calls their acquisition route.
- Goal 019's all-peer regional metric is a coarse implementation of the metric
  spec's candidate basin/buffer concept; changing it would be a scientific
  contract change, out of scope here.
- Goal 019's first 78 rows have partial temporal history by design; Goal 020's
  caveat to review `derived_partial_history` rows must remain visible.
- No raw data, network route, production execution, or external service was
  inspected in this audit, so route availability is inherited evidence only.

## Validation Performed

- Read-only source, settings, reports, manifests, CSV schemas, and Goal
  019/020 logs named by the packet.
- In-memory CSV shape/status inspection: Goal 019 series `924 x 73`, 11
  supports, 84 months; status/quality/derived counts match committed reports.
- After writing deliverables: `git diff --check`,
  `git status --short --branch`, `git diff --name-only`; four protected hashes
  rechecked unchanged.
- No test, validator, production, network, remote, STAC/S3, GDAL, or raw-data
  command was run.

Publication remains pending orchestrator review; no commit or push was made.
