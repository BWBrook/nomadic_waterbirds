# Remote Full-Window Hydrology Report 009

Goal 009 ran the reviewed 11-support event-window hydrology workflow on
`deep-server-ts` for `2018-01` through `2024-12`.

## Run Context

| Item | Value |
| --- | --- |
| Control plane | Mac mini |
| Remote host | `deep-server-ts` / `deep-server` |
| Remote repo path | `/data/codex/repos/nomadic_waterbirds_goal009` |
| Source staging | Goal 008 rsync pattern: `.git` plus `git ls-files --cached --others --exclude-standard` |
| Command | `python3 scripts/remote_full_window_hydrology_009.py` |
| Elapsed time | 8089.7 seconds |
| Python / GDAL | Python 3.12.3; GDAL 3.8.4 |

Raw geometry, KMZ, ZIP, and intermediate files remained under ignored remote
artifact paths and were not brought back to Git.

## Output Shape

| Check | Result |
| --- | --- |
| Supports | 11 |
| Months | 84 (`2018-01` to `2024-12`) |
| Rows | 924 |
| Computed rows | 145 |
| Blocked rows | 779 |
| Dominant blocked class | `transient_endpoint_failure` |

Returned review files:

- `docs/event_window_hydrology_series_2018_2024.csv`
- `docs/event_window_hydrology_summary_2018_2024.csv`
- `docs/remote_full_window_hydrology_009_retry_summary.csv`
- `docs/remote_full_window_hydrology_009_manifest.json`

## Per-Support Status

| Support | Computed | Blocked | High | Minimum | Fail | Dominant failure |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `nwb001_ramsar_component_359` | 25 | 59 | 3 | 19 | 62 | `transient_endpoint_failure` |
| `nwb001_ramsar_ref337` | 12 | 72 | 3 | 8 | 73 | `transient_endpoint_failure` |
| `nwb002_ramsar_ref1291` | 0 | 84 | 0 | 0 | 84 | `transient_endpoint_failure` |
| `nwb003_ramsar_component_121` | 11 | 73 | 0 | 11 | 73 | `transient_endpoint_failure` |
| `nwb003_ramsar_ref993` | 0 | 84 | 0 | 0 | 84 | `transient_endpoint_failure` |
| `nwb004_ramsar_component_354` | 84 | 0 | 51 | 28 | 5 |  |
| `nwb004_ramsar_component_369` | 13 | 71 | 2 | 7 | 75 | `transient_endpoint_failure` |
| `nwb004_ramsar_ref265` | 0 | 84 | 0 | 0 | 84 | `transient_endpoint_failure` |
| `nwb005_dea_waterbody_r4ysdndx8_v3` | 0 | 84 | 0 | 0 | 84 | `transient_endpoint_failure` |
| `nwb005_dea_waterbody_r4yss38r6_v3` | 0 | 84 | 0 | 0 | 84 | `transient_endpoint_failure` |
| `nwb005_ramsar_ref791` | 0 | 84 | 0 | 0 | 84 | `transient_endpoint_failure` |

## Interpretation Boundary

The full run completed and produced the expected 924 support-month rows, but
it is not a complete hydrological evidence table. Most rows exhausted bounded
retry against transient DEA STAC endpoint failures and are retained as
classified `quality_fail` blocked rows. These outputs are suitable for
provenance, retry diagnostics, and run-resume planning, but not for ecological
interpretation.
