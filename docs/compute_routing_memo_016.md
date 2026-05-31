# Goal 016 Compute Routing Memo

## Decision

Preferred target: `deep-server-ts`.
Final run host label: `deep-server-ts`.
Remote compute used: `True`.
Remote working path: `/data/codex/repos/nomadic_waterbirds_goal016`.

## Target Probe

Probe status: `deep_server_ts_probe_passed`.
Route evidence source: `artifacts/direct_s3_all_support_probe_016/output/route_evidence_016.json`.
Hostname: `deep-server`.
CPU count: `64`.
Memory total: `125Gi`.
`/data` available: `4.5T`.
Python: `3.12.3`.
GDAL: `3.8.4`.
Git: `2.43.0`.
S3 route: `HTTP 200`.
Python bindings: NumPy `1.26.4`, GDAL/OGR/OSR `available`.

## Target Tests

Focused test command: `python3 -m unittest tests.test_goal016_direct_s3_all_support_probe`.
Focused test status: `passed` with `6` tests.

## Smoke Test

Remote smoke status: `passed_with_area_tolerance_update`.
Preferred smoke support/month: `NWB002` / `2022-11`.
Smoke elapsed seconds: `12.288`.
Smoke status counts: `{"computed_direct_s3_metrics": 1}`.
Smoke Goal 015/014 hash/count status: `matched`.
Area difference vs Goal 015/014: `2.367188` m2; full-run area tolerance: `5.0` m2.

## Final Run

Summary row count: `33`.
Status counts: `{"computed_direct_s3_metrics": 33}`.

## Fallback Rules

If `deep-server-ts` is unavailable or fails the project-native smoke test, the support grid must not be reduced. A local full run is acceptable only when a local smoke shows the 33-row workload is comfortably bounded; otherwise the package should record a blocker.
