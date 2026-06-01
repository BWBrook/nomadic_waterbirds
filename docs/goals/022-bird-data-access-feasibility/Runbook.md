# Runbook

Use this runbook as the practical checklist for Goal 022.

## 1. Start

```bash
cd /Users/bwbrook/papers/nomadic_waterbirds
git status --short --branch
git log --oneline -5
rg --files docs | sort
```

Confirm the repo is clean and includes Goal 021 commit `813476d` or later.

Update `docs/goals/022-bird-data-access-feasibility/Log.md` before editing.

## 2. Read Context

Read the files listed in `Goal.md`, especially:

```bash
sed -n '1,220p' docs/bird_observation_linkage_design_021.md
sed -n '1,220p' docs/biodiversity_data_access_protocol_021.md
sed -n '1,120p' docs/bird_hydrology_join_contract_021.csv
sed -n '1,120p' docs/candidate_species_guild_screen_021.csv
python3 -m json.tool docs/bird_linkage_design_021_manifest.json >/tmp/goal022_goal021_manifest_check.json
sed -n '1,220p' docs/hydrology_to_bird_linkage_gate_020.md
sed -n '1,220p' docs/data_stream_register.md
```

Inspect Goal 020 row-class counts:

```bash
python3 - <<'PY'
import csv
from collections import Counter
with open("docs/direct_s3_full_window_hydrology_020_readiness.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
print("rows", len(rows))
print(Counter(row["readiness_class"] for row in rows))
print("caveat rows", sum("legacy_stac_comparator_not_obtained" in row.get("caveat_code", "") for row in rows))
PY
```

## 3. Source Checks

Use current official/public pages for:

- eBird data products, terms, citation, sensitive species, and complete
  checklist/sampling event requirements;
- Birdata request and reuse documentation;
- ALA API/download/terms and sensitive-record handling;
- EAWS public data/report/access information.

Do not log in, submit forms, use credentials, or download records.

Record checked sources in `docs/source_evidence_register.md` if they are new
or more specific than existing entries. Include accessed date.

## 4. Create Artefacts

Create the required Markdown, CSV, JSON, script, settings, and test files.

CSV expectations:

- `bird_data_access_matrix_022.csv` should have one row per stream/role
  decision.
- `ebird_required_fields_022.csv` should have one row per field or field group
  required for the pilot request and future ingestion.
- Controlled feasibility statuses should be:
  `request_ready`, `needs_clarification`, `context_only`, or `defer`.

## 5. Validate

Run:

```bash
python3 scripts/validate_bird_data_access_022.py
python3 -m unittest tests.test_goal022_bird_data_access
python3 -m unittest discover -s tests -p 'test*.py'
python3 -m json.tool settings/bird_data_access_022.json >/dev/null
python3 -m json.tool docs/bird_data_access_022_manifest.json >/dev/null
git diff --check
```

Run guardrail checks:

```bash
find . -type f -size +5M -not -path './.git/*' -print
find . -type f \( -name '*.shp' -o -name '*.gpkg' -o -name '*.geojson' -o -name '*.parquet' -o -name '*.sqlite' -o -name '*.duckdb' -o -name '*.rds' -o -name '*.zip' -o -name '*.tif' -o -name '*.nc' \) -not -path './.git/*' -print
git status --short --porcelain | awk '{print $2}' | while read p; do case "$p" in *.shp|*.gpkg|*.geojson|*.parquet|*.sqlite|*.duckdb|*.rds|*.zip|*.tif|*.nc) echo "$p";; esac; done
rg -n --pcre2 '(?i)(todo|tbd|fixme|placeholder|lorem)' docs scripts tests settings -g '!docs/goals/**/Runbook.md'
```

Run a local Markdown link check using the repo's existing approach or a small
script. Ensure links added by this goal resolve locally.

Check GitHub visibility:

```bash
gh repo view --json isPrivate,defaultBranchRef,nameWithOwner
```

## 6. Publish

If validation passes and the changed-file scope is only this goal's intended
files:

```bash
git status --short --branch
git add \
  docs/README.md \
  docs/data_stream_register.md \
  docs/source_evidence_register.md \
  docs/decision_log.md \
  docs/bird_data_access_feasibility_022.md \
  docs/ebird_pilot_request_package_022.md \
  docs/bird_data_access_matrix_022.csv \
  docs/ebird_required_fields_022.csv \
  docs/birdata_eaws_permission_questions_022.md \
  docs/ala_context_rules_022.md \
  docs/bird_data_access_022_manifest.json \
  docs/goals/022-bird-data-access-feasibility/Log.md \
  scripts/validate_bird_data_access_022.py \
  settings/bird_data_access_022.json \
  tests/test_goal022_bird_data_access.py
git commit -m "Prepare bird data access package"
git push origin main
git status --short --branch
```

Omit `docs/source_evidence_register.md` from staging if it was not changed.

## 7. Final Response

Report the access decision, eBird request status, validation evidence, changed
files, commit hash, push status, residual risks, and recommended Goal 023.
