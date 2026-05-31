# STAC Resilience Report 009

Goal 009 added bounded retry/backoff and explicit transient-failure
classification around DEA STAC requests and remote COG reads before launching
the remote full-window hydrology run.

## Implementation

- Retry policy: 3 attempts, 2 second initial delay, 2x backoff, 15 second
  maximum delay, 0.1 jitter fraction.
- Transient HTTP status codes: `408`, `429`, `500`, `502`, `503`, `504`.
- STAC endpoint failures are classified as `transient_endpoint_failure`.
- Remote COG/GDAL read failures are classified as
  `transient_asset_read_failure` when the exception text or exception type
  indicates transient HTTP, timeout, or connection behaviour.
- Deterministic HTTP/status failures are not retried.
- Retry events record operation, context, attempt count, final status, failure
  class, status code, exception type, and final error text.

Focused offline tests:

```bash
python3 -m unittest tests.test_goal009_stac_resilience
```

Full local suite:

```bash
python3 -m unittest discover -s tests -p 'test*.py'
```

## Endpoint Probes

Probe AOI: the small Narran product-access AOI from Goal 004, used only for
endpoint availability. It is not a wetland support mask.

| Host | Months | Endpoint status | Notes |
| --- | --- | --- | --- |
| Mac mini | `2018-01`, `2022-11`, `2024-12` | available | All months returned features; `2022-11` succeeded after one retry following a read timeout. |
| `deep-server-ts` | `2018-01`, `2022-11`, `2024-12` | available | All months returned features on first attempt. |

Because both hosts reported `endpoint_status: available`, the full remote
event-window run was launched on `deep-server-ts`.

Machine-readable evidence is in
`docs/stac_resilience_009_manifest.json`.
