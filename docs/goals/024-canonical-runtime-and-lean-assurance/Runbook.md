# Runbook

## 1. Start And Baseline

```bash
cd /Users/bwbrook/papers/nomadic_waterbirds
git status --short --branch
git rev-parse --short HEAD
sha256sum \
  docs/direct_s3_full_window_hydrology_019_manifest.json \
  docs/direct_s3_full_window_hydrology_019_series.csv \
  docs/direct_s3_full_window_hydrology_020_manifest.json \
  docs/direct_s3_full_window_hydrology_020_readiness.csv
```

Read the required sources in `Goal.md`. Re-read this `Log.md` immediately
before each log edit.

## 2. Inspect The Assurance Surface

```bash
rg -n '^def |write_text|write_bytes|mkdir|subprocess|manifest' \
  scripts/validate_bird_linkage_design_021.py \
  scripts/validate_bird_data_access_022.py \
  scripts/validate_ebird_request_intake_023.py
rg -n '^    def test_|subprocess\.run|manifest|status|hash|schema|guardrail' \
  tests/test_goal021_bird_linkage_design.py \
  tests/test_goal022_bird_data_access.py \
  tests/test_goal023_ebird_request_intake.py
```

Record which helpers are exact duplicates and which checks are semantically
distinct. Do not centralise checks merely because their names match.

## 3. Implement The Narrow Cleanup

- Add `scripts/validation_common.py` only for pure, exact shared primitives.
- Refactor validators 021-023 to use it without changing policy vocabularies,
  expected counts, or source-boundary checks.
- Make default validator execution read-only. If a manifest is generated,
  expose that as an explicit documented mode and test it separately.
- Remove or merge only duplicate test assertions; preserve one clear test for
  each consequential policy boundary.
- Update only the affected runbook/README instructions.

Do not edit Goal 019/020 production scripts or outputs.

## 4. Validate

```bash
python3 -m py_compile scripts/validation_common.py \
  scripts/validate_bird_linkage_design_021.py \
  scripts/validate_bird_data_access_022.py \
  scripts/validate_ebird_request_intake_023.py
python3 -m unittest tests.test_goal021_bird_linkage_design
python3 -m unittest tests.test_goal022_bird_data_access
python3 -m unittest tests.test_goal023_ebird_request_intake
python3 -m unittest discover -s tests -p 'test*.py'
python3 scripts/validate_bird_linkage_design_021.py
python3 scripts/validate_bird_data_access_022.py
python3 scripts/validate_ebird_request_intake_023.py
git diff --check
```

The three validator commands above are read-only by default and must not
rewrite their tracked manifests. Manifest regeneration, when explicitly
reviewed, uses the corresponding `--write-manifest` flag in a temporary copy
or other deliberate publication workflow; it is not part of routine tests.

After default validation and tests, verify that no tracked file outside the
intended Goal 024 changes was modified. Recompute the four baseline hashes and
compare them with the starting values.

If explicit manifest generation is retained, run it only in a temporary copy
or with an explicit flag and document the expected output.

## 5. Closeout

Update `Log.md` with the before/after inventory, validation results, output
hash comparison, residual risks, and the exact uncommitted status. Do not
commit or push; the orchestrator will review the diff first.
