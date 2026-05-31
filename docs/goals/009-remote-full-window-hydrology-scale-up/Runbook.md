# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Operating Rules

- Follow `AGENTS.md`.
- Read `/Users/bwbrook/.codex/AGENTS.md` and the `nectar` control-plane docs
  named in `Goal.md`.
- Use the Mac mini as control plane and `deep-server-ts` as the remote compute
  host.
- Stage raw public files, caches, remote intermediates, and remote outputs only
  under ignored paths.
- Commit only code/config, tests, docs, manifests, reports, small CSVs, and
  small logs.
- Do not download biodiversity data, submit access requests, change supports,
  use private credentials, commit raw source data, make ecological claims, or
  launch production HPC.

## Local Orientation

```bash
git status --short --branch
git log --oneline --decorate -10
rg --files
git check-ignore -v data/scratch/goal009/example.tmp artifacts/remote_full_window_hydrology/raw/example.tmp artifacts/remote_full_window_hydrology/output/example.tmp || true
```

## Remote Orientation

Start with the known viable alias:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=20 deep-server-ts \
  'hostname; whoami; uname -a; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true; git --version || true'
```

Record the result in `docs/stac_resilience_009_manifest.json` or
`docs/remote_full_window_hydrology_009_manifest.json`.

## Suggested Source Staging

Use GitHub if already configured on remote. If it is still unavailable, use the
Goal 008 rsync pattern from the Mac mini:

```bash
ssh deep-server-ts 'mkdir -p /data/codex/repos/nomadic_waterbirds_goal009'
rsync -a .git/ deep-server-ts:/data/codex/repos/nomadic_waterbirds_goal009/.git/
git ls-files --cached --others --exclude-standard |
  rsync -a --files-from=- ./ deep-server-ts:/data/codex/repos/nomadic_waterbirds_goal009/
ssh deep-server-ts 'cd /data/codex/repos/nomadic_waterbirds_goal009 && git status --short --branch'
```

Do not rsync ignored raw artifacts as source.

## Suggested STAC Probe Pattern

Use whatever project entrypoint you implement, but it should test at least
three months and record status:

```text
2018-01
2022-11
2024-12
```

If these return service-wide `503` after bounded retry, stop with a blocker
package.

## Suggested Remote Test/Run Commands

Adjust to actual script/config names:

```bash
ssh deep-server-ts 'cd /data/codex/repos/nomadic_waterbirds_goal009 && python3 -m unittest discover -s tests -p "test*.py"'
ssh deep-server-ts 'cd /data/codex/repos/nomadic_waterbirds_goal009 && python3 scripts/<goal009-stac-probe>.py'
ssh deep-server-ts 'cd /data/codex/repos/nomadic_waterbirds_goal009 && python3 scripts/<goal009-full-window-run>.py'
```

Remote run outputs should go under `/data/codex/artifacts` or ignored project
artifact paths first. Bring back only small review outputs.

## Validation Snippets

JSON checks:

```bash
python3 -m json.tool docs/stac_resilience_009_manifest.json >/dev/null
python3 -m json.tool docs/remote_full_window_hydrology_009_manifest.json >/dev/null
```

CSV full-window check if the run succeeds:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

series = list(csv.DictReader(Path("docs/event_window_hydrology_series_2018_2024.csv").open(newline="", encoding="utf-8")))
summary = list(csv.DictReader(Path("docs/event_window_hydrology_summary_2018_2024.csv").open(newline="", encoding="utf-8")))
months = {row["month"] for row in series}
supports = {row["support_id"] for row in series}
required = {
    "support_id",
    "month",
    "status",
    "quality_flag",
    "wet_prop_lag_1m",
    "wet_prop_lag_3m",
    "wet_prop_trailing_3m",
    "novel_after_dry_flag",
    "drying_velocity_1m",
}
missing = required - set(series[0]) if series else required
if missing:
    raise SystemExit(f"missing fields: {sorted(missing)}")
if len(months) != 84 or min(months) != "2018-01" or max(months) != "2024-12":
    raise SystemExit(f"unexpected months: {len(months)} {min(months) if months else None} {max(months) if months else None}")
if len(supports) != 11:
    raise SystemExit(f"unexpected support count: {len(supports)}")
if len(series) != 924:
    raise SystemExit(f"unexpected row count: {len(series)}")
if len(summary) != 11:
    raise SystemExit(f"unexpected summary rows: {len(summary)}")
print("full-window CSV check ok")
PY
```

Git/data hygiene:

```bash
git diff --check
python3 -m unittest discover -s tests -p 'test*.py'
python3 - <<'PY'
from pathlib import Path
import subprocess

paths = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
large = [p for p in paths if Path(p).is_file() and Path(p).stat().st_size > 5_000_000]
if large:
    raise SystemExit("committed files larger than 5 MB: " + ", ".join(large))
print("committed-size check ok")
PY
python3 - <<'PY'
from pathlib import Path
import subprocess

blocked = {
    ".shp", ".dbf", ".shx", ".prj", ".gpkg", ".geojson", ".kml", ".kmz",
    ".tif", ".tiff", ".nc", ".parquet", ".rds", ".zip", ".tar", ".gz",
    ".sqlite", ".duckdb",
}
paths = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
hits = [p for p in paths if Path(p).suffix.lower() in blocked]
if hits:
    raise SystemExit("committed raw/source-data extensions: " + ", ".join(hits))
print("committed raw-extension check ok")
PY
rg -n 'TO''DO|TB''D|FIX''ME|lor''em|place''holder' docs scripts settings tests AGENTS.md README.md || true
git status --short --branch
```

Use a small link-checking approach of your choice for local Markdown links in
new or edited docs. Record the command or method in the goal log.

## Finish

```bash
git add docs scripts settings tests
git commit -m "Run remote full-window hydrology scale-up"
git push origin main
git status --short --branch
```

Adjust `git add` paths to actual changed files. If the full run is blocked by
STAC availability, use a commit message that says so.

## Reporting Rules

Final response should include retry/backoff changes, endpoint probe results,
remote run path, whether the full-window run completed, row/status/quality
counts if available, blocker evidence if not, staging paths and cleanup status,
validation outcomes, commit/push status, residual risks, and recommended
Goal 010.
