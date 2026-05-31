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
rg -n "path_row|path/row|093/080|wrs|support_id|candidate_id|stac|s3|bbox|geometry" docs scripts settings tests
rg -n "nwb002|narran|event_window_hydrology|hydrology_metadata" docs scripts settings tests
```

## Suggested Staging Checks

Before writing raw geometry, listings, inventories, or route artefacts:

```bash
mkdir -p artifacts/support_pathrow_metadata_013/raw
mkdir -p artifacts/support_pathrow_metadata_013/intermediate
mkdir -p artifacts/support_pathrow_metadata_013/output
git check-ignore artifacts/support_pathrow_metadata_013/raw/probe.json
git check-ignore artifacts/support_pathrow_metadata_013/intermediate/probe.json
git check-ignore artifacts/support_pathrow_metadata_013/output/probe.json
```

The exact filenames may differ. Raw WRS geometry, S3 listings, STAC item JSON,
inventories, rasters, and array outputs must remain ignored.

## Path/Row Source Guidance

Prefer official/current WRS-2 footprint data or another clearly official
path/row source. Record:

- source title and URL;
- access date;
- file/version/date if available;
- staged path and size;
- whether the source is descending/ascending and why it fits Landsat Water
  Observations;
- whether the coverage method uses support geometry or only support bbox.

## Comparator Guidance

Use this order unless evidence suggests a better one:

1. Strict DEA STAC preflight and item-set comparison, if available.
2. Practical official ODC/NCI/DEA Sandbox or equivalent indexed metadata route.
3. Precise comparator blocker if no official comparator is available without
   credentials/account setup.

Do not treat S3 object listing alone as an equivalence proof.

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/support_pathrow_metadata_013.json >/dev/null
python3 -m json.tool docs/support_pathrow_coverage_013_manifest.json >/dev/null
```

CSV:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/support_pathrow_crosswalk_013.csv": {
        "support_id",
        "candidate_id",
        "path",
        "row",
        "coverage_status",
        "coverage_method",
        "source_id",
    },
    "docs/support_pathrow_item_sets_013.csv": {
        "candidate_id",
        "support_id",
        "month",
        "path",
        "row",
        "item_count",
        "asset_key_hash",
        "route_status",
    },
    "docs/metadata_comparator_status_013.csv": {
        "comparator",
        "status",
        "scientific_equivalence_status",
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
python3 -m unittest tests.test_goal013_support_pathrow_metadata
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
git commit -m "Prototype support path-row metadata equivalence"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include support coverage status, path/row source,
`NWB002` complete-path-row item counts, comparator status, validation outcomes,
commit/push status, residual risks, and the recommended Goal 014.
