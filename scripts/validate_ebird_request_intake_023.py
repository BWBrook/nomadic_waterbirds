#!/usr/bin/env python3
"""Validate Goal 023 eBird request-support and intake-staging artefacts."""

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
DEFAULT_CONFIG = REPO / "settings" / "ebird_request_intake_023.json"
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
    normalised = [{key: (value or "") for key, value in row.items()} for row in rows]
    normalised.sort(key=lambda row: row.get(sort_key, ""))
    payload = json.dumps(normalised, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_settings(path: Path) -> dict[str, Any]:
    settings = read_json(path)
    required = {
        "goal",
        "manifest_type",
        "run_command",
        "accessed_date",
        "decision_status",
        "goal020_reference",
        "goal021_reference",
        "goal022_reference",
        "request_envelope",
        "files",
        "csv_schemas",
        "required_public_sources",
        "required_text",
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
        errors.append(f"Goal 021 status {manifest.get('design_goal_status')} != {ref['expected_status']}")
    for required_path in [ref["candidate_screen_path"], ref["join_contract_path"]]:
        if not (REPO / required_path).exists():
            errors.append(f"missing Goal 021 reference artefact: {required_path}")
    return {
        "manifest_path": ref["manifest_path"],
        "design_goal_status": manifest.get("design_goal_status"),
        "candidate_screen_path": ref["candidate_screen_path"],
        "join_contract_path": ref["join_contract_path"],
    }


def validate_goal022(config: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    ref = config["goal022_reference"]
    manifest_path = REPO / ref["manifest_path"]
    if not manifest_path.exists():
        errors.append(f"missing Goal 022 manifest: {ref['manifest_path']}")
        return {}
    manifest = read_json(manifest_path)
    if manifest.get("decision_status") != ref["expected_status"]:
        errors.append(f"Goal 022 status {manifest.get('decision_status')} != {ref['expected_status']}")
    for required_path in [ref["request_package_path"], ref["required_fields_path"]]:
        if not (REPO / required_path).exists():
            errors.append(f"missing Goal 022 reference artefact: {required_path}")
    return {
        "manifest_path": ref["manifest_path"],
        "decision_status": manifest.get("decision_status"),
        "request_package_path": ref["request_package_path"],
        "required_fields_path": ref["required_fields_path"],
    }


def validate_text_requirements(config: dict[str, Any], paths: dict[str, Path], errors: list[str]) -> None:
    for file_key, phrases in config["required_text"].items():
        text = paths[file_key].read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{paths[file_key].relative_to(REPO)} missing required phrase: {phrase}")


def validate_qa_contract(rows: list[dict[str, str]], config: dict[str, Any], errors: list[str]) -> None:
    schema = config["csv_schemas"]["qa_contract"]
    if not rows:
        errors.append("qa_contract: empty CSV")
        return
    missing = set(schema["required_columns"]) - set(rows[0])
    if missing:
        errors.append(f"qa_contract: missing columns {sorted(missing)}")
        return
    if len(rows) < schema["min_rows"]:
        errors.append(f"qa_contract: row count {len(rows)} < {schema['min_rows']}")
    stages = set(schema["stage_vocab"])
    categories = set(schema["category_vocab"])
    severities = set(schema["severity_vocab"])
    seen_stages: set[str] = set()
    seen_categories: set[str] = set()
    blocker_count = 0
    for row_no, row in enumerate(rows, start=1):
        for column in schema["required_columns"]:
            if not (row.get(column) or "").strip():
                errors.append(f"qa_contract row {row_no}: empty {column}")
        if row["stage"] not in stages:
            errors.append(f"qa_contract row {row_no}: bad stage {row['stage']}")
        if row["category"] not in categories:
            errors.append(f"qa_contract row {row_no}: bad category {row['category']}")
        if row["severity"] not in severities:
            errors.append(f"qa_contract row {row_no}: bad severity {row['severity']}")
        seen_stages.add(row["stage"])
        seen_categories.add(row["category"])
        if row["severity"] == "blocker":
            blocker_count += 1
    missing_stages = stages - seen_stages
    if missing_stages:
        errors.append(f"qa_contract: missing stages {sorted(missing_stages)}")
    required_categories = {
        "inventory",
        "provenance",
        "terms",
        "schema",
        "sampling_event",
        "checklist_completeness",
        "sensitive_records",
        "spatial",
        "temporal",
        "support_assignment",
        "duplicates",
        "handoff",
    }
    missing_categories = required_categories - seen_categories
    if missing_categories:
        errors.append(f"qa_contract: missing categories {sorted(missing_categories)}")
    if blocker_count < 10:
        errors.append(f"qa_contract: blocker count {blocker_count} < 10")


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


def validate_text_guardrails(
    paths: list[Path],
    config: dict[str, Any],
    errors: list[str],
    request_status_paths: list[Path] | None = None,
) -> None:
    forbidden = [re.compile(pattern, re.IGNORECASE) for pattern in config["guardrails"]["forbidden_claim_patterns"]]
    request_status_paths = request_status_paths or []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if UNFINISHED_MARKER_PATTERN.search(text):
            errors.append(f"{path.relative_to(REPO)}: unfinished marker text found")
    for path in request_status_paths:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern.search(text):
                errors.append(f"{path.relative_to(REPO)}: forbidden request-status claim found: {pattern.pattern}")


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


def validate_envelope(config: dict[str, Any], errors: list[str]) -> None:
    envelope = config["request_envelope"]
    if envelope["start_date"] != "2018-01-01" or envelope["end_date"] != "2024-12-31":
        errors.append("request envelope date window changed")
    if envelope["support_count"] != 11:
        errors.append("request envelope support count changed")
    if set(envelope["core_hydrology_classes"]) != {"core_eligible", "core_eligible_with_caveat"}:
        errors.append("request envelope core hydrology classes changed")
    if envelope["sensitivity_hydrology_class"] != "sensitivity_only":
        errors.append("request envelope sensitivity class changed")
    if "provisional" not in envelope["species_guild_status"]:
        errors.append("request envelope must keep species/guild status provisional")


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
    goal022 = validate_goal022(config, errors)
    validate_envelope(config, errors)
    validate_text_requirements(config, paths, errors)
    qa_rows = read_csv(paths["qa_contract"])
    validate_qa_contract(qa_rows, config, errors)
    validate_source_register(config, paths["source_evidence_register"], errors)

    markdown_paths = [
        paths["submission_checklist"],
        paths["request_text"],
        paths["intake_plan"],
        paths["data_stream_register"],
        paths["decision_log"],
        paths["docs_readme"],
        paths["goal_log"],
    ]
    validate_markdown_links(markdown_paths, errors, {paths["manifest_json"].resolve()})
    validate_text_guardrails(
        markdown_paths + [paths["qa_contract"], paths["settings"], paths["validation_script"], paths["tests"]],
        config,
        errors,
        markdown_paths + [paths["qa_contract"]],
    )
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
        "request_submission_status": "not_submitted_by_goal023",
        "action_time_confirmation_required": True,
        "request_envelope": config["request_envelope"],
        "goal020_reference": goal020,
        "goal021_reference": goal021,
        "goal022_reference": goal022,
        "official_sources_checked": config["required_public_sources"],
        "new_public_sources_checked_for_goal023": config["new_public_sources_checked_for_goal023"],
        "artifacts": {
            "submission_checklist": {
                "path": config["files"]["submission_checklist"],
                "sha256": file_hash(paths["submission_checklist"]),
            },
            "request_text": {
                "path": config["files"]["request_text"],
                "sha256": file_hash(paths["request_text"]),
            },
            "intake_plan": {
                "path": config["files"]["intake_plan"],
                "sha256": file_hash(paths["intake_plan"]),
            },
            "qa_contract": {
                "path": config["files"]["qa_contract"],
                "row_count": len(qa_rows),
                "row_hash": stable_row_hash(qa_rows, "qa_id"),
                "sha256": file_hash(paths["qa_contract"]),
            },
        },
        "validation": {
            "status": "pass",
            "checks": [
                "required_files",
                "goal020_counts",
                "goal021_status",
                "goal022_status",
                "request_envelope",
                "submission_boundary_language",
                "qa_contract_schema",
                "source_register",
                "markdown_links",
                "unfinished_marker_scan",
                "request_status_claim_guardrail",
                "changed_file_guardrails",
            ],
        },
    }
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Goal 023 validation passed.")
    print(f"Manifest written: {manifest_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
