# Runbook

## Working Directory

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Orientation

```bash
git status --short --branch
git log --oneline --decorate -12
rg --files
```

Read `Goal.md` first, then `Plan.md`, then the required documents listed in
`Goal.md`.

## Remote Probe

```bash
ssh deep-server-ts 'hostname; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true'
ssh deep-server-ts 'mkdir -p /data/codex/repos'
```

Use:

```text
/data/codex/repos/nomadic_waterbirds_goal019
```

Record the probe result and remote path in `Log.md`.

## Expected Grid Check

```bash
python3 - <<'PY'
from datetime import date

months = []
year, month = 2018, 1
while (year, month) <= (2024, 12):
    months.append(f"{year:04d}-{month:02d}")
    month += 1
    if month == 13:
        month = 1
        year += 1
print("months", len(months), months[0], months[-1])
print("expected rows for 11 supports", len(months) * 11)
if len(months) != 84:
    raise SystemExit("expected 84 months")
PY
```

## Suggested Local Staging Checks

```bash
mkdir -p artifacts/direct_s3_full_window_hydrology_019/raw
mkdir -p artifacts/direct_s3_full_window_hydrology_019/intermediate
mkdir -p artifacts/direct_s3_full_window_hydrology_019/output
git check-ignore artifacts/direct_s3_full_window_hydrology_019/raw/probe.json
git check-ignore artifacts/direct_s3_full_window_hydrology_019/intermediate/probe.npy
git check-ignore artifacts/direct_s3_full_window_hydrology_019/output/probe.csv
```

Use equivalent ignored paths on `deep-server-ts`. Do not commit raw route
caches or remote outputs.

## Useful Searches

```bash
rg -n "direct_s3|pathrow|path_row|asset_key_hash|item_id_hash|resume|quality_" docs scripts settings tests
rg -n "current_wet_area|proportion_wet|wet_pixel|dry_pixel|lag|novelty|drying|hydroperiod|spell" docs scripts settings tests
```

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/direct_s3_full_window_hydrology_019.json >/dev/null
python3 -m json.tool docs/direct_s3_full_window_hydrology_019_preflight.json >/dev/null
python3 -m json.tool docs/direct_s3_full_window_hydrology_019_manifest.json >/dev/null
```

Production grid, if production launches:

```bash
python3 - <<'PY'
import csv
from collections import Counter

series_path = "docs/direct_s3_full_window_hydrology_019_series.csv"
with open(series_path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

print("series rows", len(rows))
if len(rows) != 924:
    raise SystemExit(f"expected 924 rows, found {len(rows)}")

supports = {row["support_id"] for row in rows}
months = {row["month"] for row in rows}
if len(supports) != 11:
    raise SystemExit(f"expected 11 supports, found {len(supports)}")
if len(months) != 84:
    raise SystemExit(f"expected 84 months, found {len(months)}")

keys = [(row["support_id"], row["month"]) for row in rows]
dupes = [key for key, count in Counter(keys).items() if count != 1]
if dupes:
    raise SystemExit(f"duplicate or missing grid keys: {dupes[:5]}")

if any(not row.get("row_status") for row in rows):
    raise SystemExit("blank row_status")

computed = [row for row in rows if row["row_status"] == "computed_direct_s3_metrics"]
if any(not row.get("asset_key_hash") or not row.get("item_id_hash") for row in computed):
    raise SystemExit("computed rows require item hashes")

print("supports", len(supports), "months", len(months))
print("status counts", Counter(row["row_status"] for row in rows))
print("quality counts", Counter(row.get("quality_flag", "") for row in rows))
PY
```

CSV shape:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/direct_s3_full_window_hydrology_019_series.csv": {
        "support_id", "month", "row_status", "quality_flag",
        "item_count", "asset_key_hash", "item_id_hash",
    },
    "docs/direct_s3_full_window_hydrology_019_item_sets.csv": {
        "support_id", "month", "path_rows", "item_count",
        "asset_key_hash", "item_id_hash", "route_status",
    },
    "docs/direct_s3_full_window_hydrology_019_summary.csv": {
        "summary_level", "row_count", "computed_count", "blocked_count",
    },
}

for path, cols in required.items():
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"{path} has no rows")
    missing = cols - set(rows[0])
    if missing:
        raise SystemExit(f"{path} missing columns {sorted(missing)}")
    print(path, "rows", len(rows))
PY
```

Tests and hygiene:

```bash
git diff --check
python3 -m unittest tests.test_goal019_direct_s3_full_window_hydrology
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
    ".sqlite", ".duckdb", ".npy", ".npz",
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

Use or adapt the repo's local Markdown link-check pattern and record the
method in `Log.md`.

## Finish

```bash
git add docs scripts settings tests
git commit -m "Run full-window direct S3 hydrology production"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include preflight pass/fail, production launch status,
row counts, status counts, quality counts, restartability evidence, remote
host/path, validation outcomes, commit/push status, residual risks, and the
recommended Goal 020.
