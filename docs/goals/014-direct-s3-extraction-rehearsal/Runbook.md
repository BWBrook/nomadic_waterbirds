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
rg -n "current_wet_area|current_proportion_wet|clear_obs|invalid_obs|wet_pixel|quality_flag|readable_scene|water.tif|bit" scripts tests docs
rg -n "nwb002|092/081|093/080|093/081|support_pathrow|direct_s3" docs scripts settings tests
```

## Suggested Staging Checks

Before writing raster-read artefacts:

```bash
mkdir -p artifacts/direct_s3_extraction_rehearsal_014/raw
mkdir -p artifacts/direct_s3_extraction_rehearsal_014/intermediate
mkdir -p artifacts/direct_s3_extraction_rehearsal_014/output
git check-ignore artifacts/direct_s3_extraction_rehearsal_014/raw/probe.tif
git check-ignore artifacts/direct_s3_extraction_rehearsal_014/intermediate/probe.npy
git check-ignore artifacts/direct_s3_extraction_rehearsal_014/output/probe.json
```

The exact filenames may differ. Raw rasters, arrays, S3 listings, STAC item
JSON, and temporary extraction outputs must remain ignored.

## Comparison Guidance

Use `docs/event_window_hydrology_series.csv` for `2022-11` and `2024-12`.

Minimum fields to compare:

- `readable_scene_count`
- `clear_obs_count`
- `invalid_obs_count`
- `clear_obs_fraction`
- `current_wet_area_m2`
- `valid_support_area_m2`
- `current_proportion_wet`
- `wet_pixel_observation_count`
- `dry_pixel_observation_count`
- `quality_flag`
- `wet_month_flag`

For `2018-01`, use `docs/event_window_hydrology_series_2018_2024.csv` only to
record that the status was previously endpoint-blocked.

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/direct_s3_extraction_rehearsal_014.json >/dev/null
python3 -m json.tool docs/direct_s3_extraction_rehearsal_014_manifest.json >/dev/null
```

CSV:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/direct_s3_extraction_rehearsal_014_summary.csv": {
        "candidate_id",
        "support_id",
        "month",
        "status",
        "readable_scene_count",
        "clear_obs_count",
        "invalid_obs_count",
        "current_wet_area_m2",
        "current_proportion_wet",
        "quality_flag",
    },
    "docs/direct_s3_extraction_comparison_014.csv": {
        "month",
        "comparison_target",
        "comparison_status",
        "max_abs_numeric_difference",
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
if len(list(csv.DictReader(open("docs/direct_s3_extraction_rehearsal_014_summary.csv", newline="", encoding="utf-8")))) != 3:
    raise SystemExit("summary must have exactly 3 rows")
PY
```

Tests and hygiene:

```bash
git diff --check
python3 -m unittest tests.test_goal014_direct_s3_extraction
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
git commit -m "Rehearse direct S3 hydrology extraction"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include item-set validation, raster-read route, summary
metrics, comparison status for `2022-11` and `2024-12`, `2018-01` status,
validation outcomes, commit/push status, residual risks, and the recommended
Goal 015.
