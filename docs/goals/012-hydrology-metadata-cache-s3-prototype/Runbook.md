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
rg -n "stac_search|dea_stac|process_event_window|support_id|candidate_id|path_row|retry|blocked" scripts settings tests docs
rg -n "hydrology_metadata|hydrology_access_route|event_window_hydrology" .gitignore docs scripts settings tests
```

## Suggested Staging Checks

Before writing live route artefacts:

```bash
mkdir -p artifacts/hydrology_metadata_cache_012/raw
mkdir -p artifacts/hydrology_metadata_cache_012/intermediate
mkdir -p artifacts/hydrology_metadata_cache_012/output
git check-ignore artifacts/hydrology_metadata_cache_012/raw/probe.json
git check-ignore artifacts/hydrology_metadata_cache_012/intermediate/probe.json
git check-ignore artifacts/hydrology_metadata_cache_012/output/probe.json
```

The exact filenames may differ, but any raw item JSON, S3 listing, inventory,
cache, raster, or array output must be ignored.

## STAC Preflight Guidance

Define the pass threshold in code/config before running it. A reasonable
starting threshold is:

- all three probe months return a successful small metadata response within
  bounded retry;
- no HTTP 503 or equivalent service-unavailable response;
- no unclassified exception.

If the threshold is not met, mark the STAC cache route unavailable for this
goal and do not launch repeated retries.

## Direct S3/Inventory Guidance

Use official DEA public object conventions or public inventory metadata. Prefer
bounded prefix listing and `HEAD` requests. Do not download rasters unless a
tiny metadata/header check is essential, and never commit downloaded rasters.

Record enough detail to reproduce the route:

- bucket or base URL;
- prefix pattern or inventory source;
- product collection/version;
- path/row or candidate bounding information;
- month;
- item/key count;
- stable hash of item IDs and Water Observations asset keys.

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/hydrology_metadata_cache_s3_012.json >/dev/null
python3 -m json.tool docs/hydrology_metadata_cache_s3_012_manifest.json >/dev/null
```

CSV:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/hydrology_metadata_item_sets_012.csv": {
        "candidate_id",
        "month",
        "route",
        "item_count",
        "item_id_hash",
        "asset_key_hash",
        "route_status",
    },
    "docs/hydrology_metadata_route_comparison_012.csv": {
        "route",
        "scientific_equivalence_status",
        "stac_dependence",
        "s3_or_object_store_dependence",
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
PY
```

Tests and hygiene:

```bash
git diff --check
python3 -m unittest tests.test_goal012_hydrology_metadata_cache
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

Use or adapt the repo's local Markdown link-check pattern and record the
method in `Log.md`.

## Finish

```bash
git add docs scripts settings tests
git commit -m "Prototype hydrology metadata acquisition routes"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include candidate/months, STAC preflight status, S3/index
route status, item-set comparison status, validation outcomes, commit/push
status, residual risks, and the recommended Goal 013.
