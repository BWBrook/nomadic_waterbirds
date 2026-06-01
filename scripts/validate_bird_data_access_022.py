#!/usr/bin/env python3
"""Validate Goal 022 bird data access feasibility artefacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO / "settings" / "bird_data_access_022.json"
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
UNFINISHED_MARKER_PATTERN = re.compile(
    r"\b(" + "|".join(["to" + "do", "tb" + "d", "place" + "holder", "fix" + "me", "x" * 3]) + r")\b",
    re.IGNORECASE,
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def stable_row_hash(rows: list[dict[str, str]], sort_key: str) -> str:
    normalised = []
    for row in rows:
        normalised.append({key: (value or "") for key, value in row.items()})
    normalised.sort(key=lambda row: row.get(sort_key, ""))
    payload = json.dumps(normalised, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_settings(path: Path) -> dict[str, Any]:
    settings = read_json(path)
    required = {
        "goal",
        "manifest_type",
        "run_command",
        "decision_status",
        "files",
        "csv_schemas",
        "goal020_reference",
        "goal021_reference",
        "required_public_sources",
        "guardrails",
    }
    missing = required - set(settings)
    if missing:
        raise RuntimeError(f"settings missing required keys: {sorted(missing)}")
    return settings


def validate_required_files(config: dict[str, Any], errors: list[str]) -> dict[str, Path]:
    paths = {name: REPO / rel for name, rel in config["files"].items()}
    for name, path in paths.items():
        if name == "manifest_json":
            continue
        if not path.exists():
            errors.append(f"missing required file {name}: {path.relative_to(REPO)}")
    return paths


def validate_goal020(config: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    ref = config["goal020_reference"]
    path = REPO / ref["readiness_rows_path"]
    if not path.exists():
        errors.append(f"missing Goal 020 readiness table: {ref['readiness_rows_path']}")
        return {}
    rows = read_csv(path)
    if len(rows) != ref["expected_row_count"]:
        errors.append(f"Goal 020 row count {len(rows)} != {ref['expected_row_count']}")
    readiness_field = "readiness_class" if "readiness_class" in rows[0] else "bird_linkage_readiness"
    counts = Counter(row[readiness_field] for row in rows)
    expected = {
        "core_eligible": ref["expected_core_eligible"],
        "core_eligible_with_caveat": ref["expected_core_eligible_with_caveat"],
        "sensitivity_only": ref["expected_sensitivity_only"],
    }
    for key, value in expected.items():
        if counts.get(key, 0) != value:
            errors.append(f"Goal 020 {key} count {counts.get(key, 0)} != {value}")
    caveat_rows = sum("legacy_stac_comparator_not_obtained" in row.get("caveat_code", "") for row in rows)
    if caveat_rows != ref["expected_goal018_legacy_caveat_count"]:
        errors.append(f"Goal 018 caveat count {caveat_rows} != {ref['expected_goal018_legacy_caveat_count']}")
    return {
        "readiness_rows_path": ref["readiness_rows_path"],
        "readiness_row_count": len(rows),
        "readiness_class_counts": dict(counts),
        "legacy_comparator_caveat_rows": caveat_rows,
    }


def validate_goal021(config: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    ref = config["goal021_reference"]
    manifest_path = REPO / ref["manifest_path"]
    if not manifest_path.exists():
        errors.append(f"missing Goal 021 manifest: {ref['manifest_path']}")
        return {}
    manifest = read_json(manifest_path)
    if manifest.get("design_goal_status") != ref["expected_status"]:
        errors.append(
            f"Goal 021 status {manifest.get('design_goal_status')} != {ref['expected_status']}"
        )
    for required_path in [ref["candidate_screen_path"], ref["join_contract_path"]]:
        if not (REPO / required_path).exists():
            errors.append(f"missing Goal 021 reference artefact: {required_path}")
    return {
        "manifest_path": ref["manifest_path"],
        "design_goal_status": manifest.get("design_goal_status"),
        "candidate_screen_path": ref["candidate_screen_path"],
        "join_contract_path": ref["join_contract_path"],
    }


def validate_csv_schema(
    rows: list[dict[str, str]],
    schema: dict[str, Any],
    errors: list[str],
    context: str,
) -> None:
    if not rows:
        errors.append(f"{context}: empty CSV")
        return
    missing = set(schema["required_columns"]) - set(rows[0])
    if missing:
        errors.append(f"{context}: missing columns {sorted(missing)}")
        return
    if len(rows) < schema["min_rows"]:
        errors.append(f"{context}: row count {len(rows)} < {schema['min_rows']}")
    for row_no, row in enumerate(rows, start=1):
        for column in schema["required_columns"]:
            if not (row.get(column) or "").strip():
                errors.append(f"{context} row {row_no}: empty {column}")


def validate_access_matrix(rows: list[dict[str, str]], config: dict[str, Any], errors: list[str]) -> None:
    schema = config["csv_schemas"]["access_matrix"]
    validate_csv_schema(rows, schema, errors, "access_matrix")
    if errors:
        return
    statuses = set(schema["status_vocab"])
    streams = {row["stream"] for row in rows}
    missing_streams = set(schema["required_streams"]) - streams
    if missing_streams:
        errors.append(f"access_matrix: missing streams {sorted(missing_streams)}")
    for row in rows:
        if row["decision_status"] not in statuses:
            errors.append(f"access_matrix {row['stream']}: bad decision_status {row['decision_status']}")
    ebird = next((row for row in rows if row["stream"] == "eBird"), None)
    ala = next((row for row in rows if row["stream"] == "ALA"), None)
    if not ebird or ebird["decision_status"] != "request_ready":
        errors.append("access_matrix: eBird must be request_ready")
    if ebird and "EBD" not in ebird["key_fields_or_products"]:
        errors.append("access_matrix: eBird row must require EBD product route")
    if not ala or ala["decision_status"] != "context_only":
        errors.append("access_matrix: ALA must be context_only")
    if ala and "absence" not in ala["forbidden_use"].lower():
        errors.append("access_matrix: ALA forbidden_use must prohibit absence inference")


def validate_ebird_fields(rows: list[dict[str, str]], config: dict[str, Any], errors: list[str]) -> None:
    schema = config["csv_schemas"]["ebird_fields"]
    validate_csv_schema(rows, schema, errors, "ebird_fields")
    if errors:
        return
    allowed = set(schema["required_status_vocab"])
    for row_no, row in enumerate(rows, start=1):
        if row["required_status"] not in allowed:
            errors.append(f"ebird_fields row {row_no}: bad required_status {row['required_status']}")
    groups = {row["field_group"] for row in rows}
    required_groups = {
        "checklist_identity",
        "observation_identity",
        "taxonomy",
        "checklist_completeness",
        "protocol",
        "date_time",
        "effort",
        "location",
        "counting",
        "quality",
        "sensitivity",
        "provenance",
        "join_key",
        "response_layer",
    }
    missing = required_groups - groups
    if missing:
        errors.append(f"ebird_fields: missing field groups {sorted(missing)}")


def validate_source_register(config: dict[str, Any], source_register: Path, errors: list[str]) -> None:
    text = source_register.read_text(encoding="utf-8")
    for source_id in config["required_public_sources"]:
        if f"| {source_id} |" not in text:
            errors.append(f"source_evidence_register missing {source_id}")


def validate_markdown_links(paths: list[Path], errors: list[str], allowed_missing: set[Path] | None = None) -> None:
    allowed_missing = allowed_missing or set()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")) or not target:
                continue
            target = target.split("#", 1)[0]
            if not target or target.startswith(("<", "`")):
                continue
            resolved = (path.parent / target).resolve()
            if resolved in allowed_missing:
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(REPO)}: broken local link {target}")


def validate_text_guardrails(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if UNFINISHED_MARKER_PATTERN.search(path.read_text(encoding="utf-8")):
            errors.append(f"{path.relative_to(REPO)}: unfinished marker text found")


def validate_changed_file_guardrails(config: dict[str, Any], errors: list[str]) -> None:
    status = subprocess.run(
        ["git", "status", "--short", "--porcelain"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    blocked = set(config["guardrails"]["forbidden_extensions"])
    max_bytes = int(config["guardrails"]["max_changed_file_size_mb"]) * 1024 * 1024
    for line in status.stdout.splitlines():
        if len(line) < 4:
            continue
        path = REPO / line[3:]
        if path.suffix.lower() in blocked:
            errors.append(f"changed file uses blocked extension: {path.relative_to(REPO)}")
        if path.exists() and path.is_file() and path.stat().st_size > max_bytes:
            errors.append(f"changed file exceeds size gate: {path.relative_to(REPO)}")


def main() -> int:
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CONFIG
    errors: list[str] = []
    config = parse_settings(config_path)
    paths = validate_required_files(config, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    goal020 = validate_goal020(config, errors)
    goal021 = validate_goal021(config, errors)
    access_rows = read_csv(paths["access_matrix"])
    ebird_rows = read_csv(paths["ebird_fields"])
    validate_access_matrix(access_rows, config, errors)
    validate_ebird_fields(ebird_rows, config, errors)
    validate_source_register(config, paths["source_evidence_register"], errors)

    markdown_paths = [
        paths["feasibility_memo"],
        paths["ebird_request_package"],
        paths["birdata_eaws_questions"],
        paths["ala_context_rules"],
        paths["data_stream_register"],
        paths["decision_log"],
        paths["docs_readme"],
        paths["goal_log"],
    ]
    validate_markdown_links(markdown_paths, errors, {paths["manifest_json"].resolve()})
    validate_text_guardrails(markdown_paths + [paths["settings"], paths["validation_script"], paths["tests"]], errors)
    validate_changed_file_guardrails(config, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    manifest_path = paths["manifest_json"]
    payload = {
        "goal": config["goal"],
        "manifest_type": config["manifest_type"],
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "accessed_date": config["accessed_date"],
        "run_command": config["run_command"],
        "decision_status": config["decision_status"],
        "goal020_reference": goal020,
        "goal021_reference": goal021,
        "official_sources_checked": config["required_public_sources"],
        "artifacts": {
            "feasibility_memo": {"path": config["files"]["feasibility_memo"], "sha256": file_hash(paths["feasibility_memo"])},
            "ebird_request_package": {"path": config["files"]["ebird_request_package"], "sha256": file_hash(paths["ebird_request_package"])},
            "access_matrix": {
                "path": config["files"]["access_matrix"],
                "row_count": len(access_rows),
                "row_hash": stable_row_hash(access_rows, "stream"),
                "sha256": file_hash(paths["access_matrix"]),
            },
            "ebird_fields": {
                "path": config["files"]["ebird_fields"],
                "row_count": len(ebird_rows),
                "row_hash": stable_row_hash(ebird_rows, "field_name_or_group"),
                "sha256": file_hash(paths["ebird_fields"]),
            },
            "birdata_eaws_questions": {"path": config["files"]["birdata_eaws_questions"], "sha256": file_hash(paths["birdata_eaws_questions"])},
            "ala_context_rules": {"path": config["files"]["ala_context_rules"], "sha256": file_hash(paths["ala_context_rules"])},
        },
        "validation": {
            "status": "pass",
            "checks": [
                "required_files",
                "goal020_counts",
                "goal021_status",
                "csv_schemas",
                "source_register",
                "markdown_links",
                "unfinished_marker_scan",
                "changed_file_guardrails",
            ],
        },
    }
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Goal 022 validation passed.")
    print(f"Manifest written: {manifest_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
