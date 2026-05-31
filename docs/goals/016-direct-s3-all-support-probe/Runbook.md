# Runbook

## Working Directory

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Orientation

```bash
git status --short --branch
git log --oneline --decorate -10
rg --files
```

Read `Goal.md` first, then `Plan.md`, then the required documents listed in
`Goal.md`.

## Useful Searches

```bash
rg -n "direct_s3|pathrow|path_row|support_intersecting|scene-selection|scene selection|readable_scene_count" docs scripts settings tests
rg -n "event_window|current_wet_area|current_proportion_wet|quality_flag|wet_month_flag" docs scripts tests
rg -n "deep-server-ts|/data/codex|compute_routing|remote" docs scripts settings tests
```

## Expected Grid Check

```bash
python3 - <<'PY'
import csv
from collections import Counter

with open("docs/event_window_hydrology_summary.csv", newline="", encoding="utf-8") as handle:
    supports = list(csv.DictReader(handle))
print("supports", len(supports))
print("support_ids", [row["support_id"] for row in supports])
print("expected_rows", len(supports) * 3)

with open("docs/support_pathrow_crosswalk_013.csv", newline="", encoding="utf-8") as handle:
    pathrows = list(csv.DictReader(handle))
coverage = Counter(row["support_id"] for row in pathrows)
missing = [row["support_id"] for row in supports if row["support_id"] not in coverage]
if missing:
    raise SystemExit(f"missing path-row coverage: {missing}")
print("pathrow_covered_supports", len(coverage))
PY
```

## Suggested Local Staging Checks

Before writing live artefacts:

```bash
mkdir -p artifacts/direct_s3_all_support_probe_016/raw
mkdir -p artifacts/direct_s3_all_support_probe_016/intermediate
mkdir -p artifacts/direct_s3_all_support_probe_016/output
git check-ignore artifacts/direct_s3_all_support_probe_016/raw/probe.json
git check-ignore artifacts/direct_s3_all_support_probe_016/intermediate/probe.npy
git check-ignore artifacts/direct_s3_all_support_probe_016/output/probe.json
```

Raw S3 listings, STAC JSON, rasters, masks, arrays, and temporary extraction
outputs must remain ignored.

## Remote Probe Sketch

Use the exact commands that fit the current `nectar` guidance, but record the
equivalent of:

```bash
ssh deep-server-ts 'hostname; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true'
ssh deep-server-ts 'mkdir -p /data/codex/repos'
```

Clone or refresh under:

```text
/data/codex/repos/nomadic_waterbirds_goal016
```

Run a one-support/one-month target smoke before the 33-row run. The preferred
smoke is `NWB002` and `2022-11` because it has Goal 015/014 comparison
evidence.

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/direct_s3_all_support_probe_016.json >/dev/null
python3 -m json.tool docs/direct_s3_all_support_probe_016_manifest.json >/dev/null
```

CSV shape:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/direct_s3_all_support_probe_016_summary.csv": {
        "candidate_id",
        "support_id",
        "month",
        "status",
        "path_rows",
        "direct_s3_items_found",
        "readable_scene_count",
        "clear_obs_count",
        "invalid_obs_count",
        "current_wet_area_m2",
        "valid_support_area_m2",
        "current_proportion_wet",
        "quality_flag",
        "wet_month_flag",
    },
    "docs/direct_s3_all_support_probe_016_support_summary.csv": {
        "support_id",
        "expected_month_count",
        "computed_month_count",
        "blocked_month_count",
        "quality_high_count",
        "quality_minimum_count",
        "quality_fail_count",
    },
    "docs/direct_s3_all_support_probe_016_comparison.csv": {
        "support_id",
        "month",
        "reference_source",
        "comparison_status",
        "differing_fields",
        "recommendation",
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

with open("docs/direct_s3_all_support_probe_016_summary.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
if len(rows) != 33:
    raise SystemExit(f"expected 33 support/month rows, found {len(rows)}")
if any(not row["status"] for row in rows):
    raise SystemExit("blank status in summary rows")
print("summary grid ok")
PY
```

Tests and hygiene:

```bash
git diff --check
python3 -m unittest tests.test_goal016_direct_s3_all_support_probe
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
git commit -m "Probe all-support direct S3 hydrology extraction"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include host used, remote path if applicable, row/status
counts, `NWB002` comparison status, legacy comparison findings, validation
outcomes, commit/push status, residual risks, and the recommended Goal 017.
