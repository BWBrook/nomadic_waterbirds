# Runbook

## Working Directory

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Local Orientation

```bash
git status --short --branch
git log --oneline --decorate -10
rg --files
```

Confirm ignored staging:

```bash
git check-ignore -v \
  data/scratch/goal010/example.tmp \
  artifacts/remote_full_window_hydrology/raw/example.tmp \
  artifacts/remote_full_window_hydrology/output/example.tmp || true
```

## Goal 009 Shape Check

```bash
python3 - <<'PY'
import csv
from collections import Counter

with open("docs/event_window_hydrology_series_2018_2024.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("rows", len(rows))
print("supports", len({r["support_id"] for r in rows}))
print("months", len({r["month"] for r in rows}))
print("status", Counter(r["status"] for r in rows))
print("quality", Counter(r["quality_flag"] for r in rows))
print("failure_class", Counter(r.get("failure_class", "") for r in rows).most_common(10))
PY
```

## Remote Orientation

```bash
ssh -o BatchMode=yes -o ConnectTimeout=20 deep-server-ts \
  'hostname; whoami; uname -a; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true; git --version || true'
```

## Source Staging

Use GitHub on remote if it works cleanly. Otherwise use the Goal 008/009 rsync
pattern:

```bash
ssh deep-server-ts 'mkdir -p /data/codex/repos/nomadic_waterbirds_goal010'
rsync -a .git/ deep-server-ts:/data/codex/repos/nomadic_waterbirds_goal010/.git/
git ls-files --cached --others --exclude-standard |
  rsync -a --files-from=- ./ deep-server-ts:/data/codex/repos/nomadic_waterbirds_goal010/
ssh deep-server-ts 'cd /data/codex/repos/nomadic_waterbirds_goal010 && git status --short --branch'
```

Do not rsync ignored raw artefacts as source.

## Preflight Pattern

Use or adapt the existing Goal 009 STAC probe. The preflight must test:

- endpoint availability
- representative Goal 009 blocked support/month rows
- attempt counts and failure classes
- enough supports/months to justify launching or stopping

Stop before full recovery if service-wide or widespread transient endpoint
failure persists.

## Validation Snippets

JSON:

```bash
python3 -m json.tool docs/stac_recovery_010_manifest.json >/dev/null
```

CSV, if recovery output exists:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

path = Path("docs/event_window_hydrology_series_2018_2024_recovery010.csv")
if not path.exists():
    print("no recovery CSV; blocker-only package")
    raise SystemExit(0)

rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
months = {row["month"] for row in rows}
supports = {row["support_id"] for row in rows}
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
missing = required - set(rows[0]) if rows else required
if missing:
    raise SystemExit(f"missing fields: {sorted(missing)}")
if len(months) != 84 or min(months) != "2018-01" or max(months) != "2024-12":
    raise SystemExit("unexpected month coverage")
if len(supports) != 11:
    raise SystemExit("unexpected support coverage")
if len(rows) != 924:
    raise SystemExit(f"unexpected row count: {len(rows)}")
print("recovery CSV check ok")
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
UNFINISHED_PATTERNS="TO""DO|TB""D|FIX""ME|lor""em|place""holder"
rg -n "$UNFINISHED_PATTERNS" docs scripts settings tests AGENTS.md README.md || true
git status --short --branch
```

Use a small local Markdown link check for new/edited docs and record the
method in `Log.md`.

## Finish

```bash
git add docs scripts settings tests
git commit -m "Run Goal 010 hydrology recovery preflight"
git push origin main
git status --short --branch
```

Adjust commit message if recovery runs successfully, for example:

```text
Recover full-window hydrology after STAC stabilization
```

## Reporting Rules

Final response should include preflight sample size and success rate, launch
decision, remote path, output row/status/quality counts, blocker evidence if
not launched, validation outcomes, commit/push status, residual risks, and
recommended Goal 011.
