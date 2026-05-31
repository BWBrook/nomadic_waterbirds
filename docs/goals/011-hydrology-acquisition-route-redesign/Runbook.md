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

Read the files listed in `Goal.md`, especially Goal 009/010 reports and the
current hydrology scripts.

## Query-Pattern Audit Hints

Start with:

```bash
rg -n "stac_search|dea_stac|for month|for support|process_event_window|retry" scripts settings tests
```

Useful questions:

- Is STAC search called inside the support/month loop?
- Can multiple supports share the same month-level STAC search?
- Could the workflow build a month/region STAC item cache and then reuse it
  for support-level warping?
- What would be the cache key and provenance record?

## Official Source Review Hints

Use official or primary sources where possible:

- DEA Water Observations product page
- DEA STAC/API documentation
- DEA public AWS/S3 documentation or bucket examples
- NCI/datacube documentation if relevant and accessible
- DEA Water Observations Statistics and DEA Waterbodies documentation as
  lower-evidence fallback products

Record source URLs in the manifest and source evidence register. Do not rely on
secondary blog posts for route decisions unless clearly labelled as context.

## Probe Limits

Keep probes tiny. Examples:

```bash
python3 scripts/stac_resilience_probe_009.py --host-label mac-mini-goal011 --output artifacts/hydrology_access_route_011/output/stac_probe_macmini_011.json
```

If implementing a new route probe, make it small, repeatable, and safe to run
without committing raw data.

## Validation Snippets

JSON:

```bash
python3 -m json.tool docs/hydrology_acquisition_route_011_manifest.json >/dev/null
```

CSV:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/hydrology_acquisition_options_011.csv": {
        "route",
        "source_status",
        "scientific_equivalence",
        "recommendation",
    },
    "docs/hydrology_stac_query_pattern_011.csv": {
        "workflow_unit",
        "estimated_live_stac_searches",
        "cache_opportunity",
    },
}
for path, cols in required.items():
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    missing = cols - set(rows[0]) if rows else cols
    if missing:
        raise SystemExit(f"{path} missing columns {sorted(missing)}")
    if not rows:
        raise SystemExit(f"{path} has no rows")
    print(path, "rows", len(rows))
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
git commit -m "Assess hydrology acquisition routes"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include route recommendation, supporting evidence, probe
results, validation outcomes, commit/push status, residual risks, and the
recommended Goal 012.
