# Compute Routing Memo 008

## Purpose

Goal 008 required a live compute-routing decision before attempting hydrology
scale-up. The decision target was the full `2018-01` through `2024-12`
event-window extraction for the current reviewed support set.

## Decision

Use `deep-server-ts` as the preferred near-term CPU-heavy single-host target
for hydrology scale-up, with the Mac mini as the control plane.

Do not launch `kunanyi`, Nectar GPU, Alien WSL, or any GPU workflow for this
goal. Do not run the full event window while DEA STAC is returning service-wide
`503 Service Temporarily Unavailable` responses.

## Live Probe

Default alias:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=20 deep-server ...
```

Result: timed out to `131.217.90.193:22`.

Documented Tailscale alias:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=20 deep-server-ts \
  'hostname; whoami; uname -a; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true; git --version || true'
```

Result:

| Check | Result |
| --- | --- |
| Host | `deep-server` |
| User | `bwbrook` |
| OS | Ubuntu/Linux `6.8.0-117-generic` x86_64 |
| CPU | 64 logical CPUs |
| Memory | 125 GiB total, 123 GiB available at probe |
| `/data` | 13T total, 4.5T available |
| Python | 3.12.3 |
| GDAL CLI | 3.8.4 |
| Python `osgeo` | available, 3.8.4 |
| Python `numpy` | available, 1.26.4 |
| Git | 2.43.0 |
| GitHub SSH from remote | `Permission denied (publickey)` |

Because GitHub SSH is not configured on `deep-server`, the remote working copy
was staged from the Mac mini using `.git` plus the unignored source file list:

```bash
rsync -a .git/ deep-server-ts:/data/codex/repos/nomadic_waterbirds_goal008/.git/
git ls-files --cached --others --exclude-standard |
  rsync -a --files-from=- ./ deep-server-ts:/data/codex/repos/nomadic_waterbirds_goal008/
```

This follows the control-plane rule to use Git for durable source state where
available and rsync/bundle transfer when remote GitHub auth is absent.

## Remote Rehearsal Outcome

Remote path:

```text
/data/codex/repos/nomadic_waterbirds_goal008
```

Remote tests:

```bash
python3 -m unittest discover -s tests -p "test*.py"
```

Result: 7 tests passed.

Remote Narran evidence script:

```bash
python3 scripts/narran_subunit_evidence_008.py
```

Result: 44 crosswalk rows and 39 DEA parent-overlap screens.

Remote hydrology smoke:

- First attempt exposed a portability bug: older GDAL/OGR on `deep-server`
  uses `Memory` rather than `MEM` for the in-memory vector driver.
- The shared helper now falls back from `MEM` to `Memory`, with a focused test.
- Second attempt built the Narran parent reference grid successfully.
- Monthly Water Observations processing then stopped at DEA STAC with
  `HTTP Error 503: Service Temporarily Unavailable`.

The same STAC `503` response was reproduced from the Mac mini for `2020-03`
and `2024-12`, so the blocker is upstream service availability, not the
remote host.

## Full-Window Decision

The full `2018-01` through `2024-12` event-window run was not launched in Goal
008. Running it while the upstream STAC endpoint returns `503` would create a
large set of blocked rows and obscure the compute-routing evidence.

The remote host itself is viable. The remaining blockers before a full run are:

- DEA STAC service availability.
- A repeatable remote full-window entrypoint that writes outputs under ignored
  remote artifact paths before selected small summaries are brought back.
- Either remote GitHub SSH configuration or the documented Mac-mini rsync/bundle
  source-staging pattern.

## Recommendation

Goal 009 should be a remote hydrology scale-up goal, not a biodiversity-access
goal yet. It should:

- rerun the remote STAC smoke after DEA service recovery,
- add retry/backoff around STAC and COG reads,
- run the full `2018-01` through `2024-12` support set on `deep-server-ts`,
- commit only reviewable CSV/JSON summaries, manifests, and reports.
