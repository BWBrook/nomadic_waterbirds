# Goal 019 Full-Window Direct-S3 Hydrology Production

Accessed date: `2026-06-01`.

## Scope

This hydrology-only production package used direct public S3 COG reads with the support-intersecting WRS path-row scene-selection policy. It does not use STAC as a production dependency and does not make biodiversity or ecological-response claims.

## Remote Route

Run host label: `deep-server-ts`.
Remote working path: `/data/codex/repos/nomadic_waterbirds_goal019`.
Remote compute used: `True`.

## Preflight

Preflight passed: `True`.
Preflight file: `docs/direct_s3_full_window_hydrology_019_preflight.json`.

## Production Grid

Expected rows: `924`.
Observed rows: `924`.
Expected grid complete: `True`.
Computed rows: `924`.
Blocked rows: `0`.

| Row status | Rows |
| --- | ---: |
| computed_direct_s3_metrics | 924 |

| Quality flag | Rows |
| --- | ---: |
| quality_fail | 23 |
| quality_high | 751 |
| quality_minimum | 150 |

## Restartability

Resume/rerun stable: `True`.
Initial series hash: `ac3b77b18ba80ee7b9ba4213331b63151eb4fd98c8dbfbb776fe34fb637d5da9`.
Resume series hash: `ac3b77b18ba80ee7b9ba4213331b63151eb4fd98c8dbfbb776fe34fb637d5da9`.

## Compact Outputs

- Series: `docs/direct_s3_full_window_hydrology_019_series.csv`.
- Item sets: `docs/direct_s3_full_window_hydrology_019_item_sets.csv`.
- Summary: `docs/direct_s3_full_window_hydrology_019_summary.csv`.
- Manifest: `docs/direct_s3_full_window_hydrology_019_manifest.json`.

## Recommendation For Goal 020

Use Goal 020 to audit the production hydrology table, document any metric caveats, and prepare the next hydrology-to-bird-data design gate.
