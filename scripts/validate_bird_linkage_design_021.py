#!/usr/bin/env python3
"""Goal 021 validator for bird observation linkage design outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import subprocess

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO / "settings" / "bird_linkage_design_021.json"
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


def split_pipe_list(text: str) -> list[str]:
    return [item.strip() for item in str(text).split("|") if item.strip()]


def to_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def stable_row_hash(rows: list[dict[str, Any]], sort_key: list[str] | None = None) -> str:
    normalised: list[dict[str, Any]] = []
    for row in rows:
        norm_row: dict[str, str] = {}
        for key in row:
            value = row.get(key, "")
            if isinstance(value, bool):
                value = "true" if value else "false"
            norm_row[key] = "" if value is None else str(value)
        normalised.append(norm_row)

    if sort_key and all(all(k in row for row in normalised) for k in sort_key):
        normalised.sort(key=lambda row: tuple(row.get(k, "") for k in sort_key))
    else:
        normalised.sort(key=lambda row: json.dumps(row, sort_keys=True))

    payload = json.dumps(normalised, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def check_file_exists(path: Path, what: str, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing {what} file: {path}")


def validate_csv_schema(
    rows: list[dict[str, str]],
    schema_cfg: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    context: str,
) -> None:
    if not rows:
        errors.append(f"{context}: empty CSV")
        return

    required_columns = set(schema_cfg["required_columns"])
    missing = required_columns - set(rows[0].keys())
    if missing:
        errors.append(f"{context}: missing required columns {sorted(missing)}")
        return

    min_rows = int(schema_cfg["min_rows"])
    if len(rows) < min_rows:
        errors.append(f"{context}: expected >= {min_rows} rows, got {len(rows)}")

    for i, row in enumerate(rows, start=1):
        for field in required_columns:
            if str(row.get(field, "")).strip() == "":
                errors.append(f"{context}: row {i} has empty '{field}'")
    if context.startswith("join_contract"):
        validate_join_contract_rows(rows, schema_cfg, errors)
    if context.startswith("unit_schema"):
        validate_unit_schema_rows(rows, schema_cfg, errors, warnings)
    if context.startswith("candidate_screen"):
        validate_candidate_screen_rows(rows, schema_cfg, errors, warnings)


def validate_join_contract_rows(
    rows: list[dict[str, str]],
    schema_cfg: dict[str, Any],
    errors: list[str],
) -> None:
    seen_ids: set[str] = set()
    allowed_stream_roles = set(schema_cfg.get("stream_roles", []))
    required_key_tokens = set(schema_cfg.get("required_hydrology_key_tokens", []))

    lane_ids = [row["lane_id"] for row in rows]
    if len(lane_ids) != len(set(lane_ids)):
        errors.append("join_contract: lane_id is not unique")

    for row_no, row in enumerate(rows, start=1):
        lane_id = row["lane_id"]
        if not lane_id.startswith("l"):
            errors.append(f"join_contract row {row_no}: lane_id should use stable IDs like l01_xxx")

        allowed = set(split_pipe_list(row["hydrology_classes_eligible"]))
        forbidden = set(split_pipe_list(row["hydrology_classes_forbidden"]))
        if not allowed:
            errors.append(f"join_contract row {row_no}: hydrology_classes_eligible is empty")
        if not forbidden:
            warnings.append(f"join_contract row {row_no}: hydrology_classes_forbidden is empty")
        if allowed.intersection(forbidden):
            errors.append(f"join_contract row {row_no}: same class in eligible and forbidden")
        if row["stream_role"] not in allowed_stream_roles:
            errors.append(f"join_contract row {row_no}: unexpected stream_role '{row['stream_role']}'")

        key_tokens = set(required_key_tokens)
        if required_key_tokens and not key_tokens.issubset({*row["hydrology_key"].split("|"), *row["hydrology_key"].split(";")}):
            # allow alternative delimiters, keep strict on required tokens presence
            missing = key_tokens - set(row["hydrology_key"].replace(";", "|").replace(",", "|").split("|"))
            missing = {m for m in missing if m}
            if missing:
                errors.append(
                    f"join_contract row {row_no}: hydrology_key '{row['hydrology_key']}' missing tokens {sorted(missing)}"
                )

        if row["stream_role"] == "Atlas of Living Australia":
            if "Never use as non-detection source." not in row["forbidden_uses"]:
                warnings.append(
                    f"join_contract row {row_no}: ALA lane should include explicit non-detection restriction in forbidden_uses"
                )
        if row["forbidden_uses"] == "":
            errors.append(f"join_contract row {row_no}: forbidden_uses is empty")
        if row["validation_checks"] == "":
            errors.append(f"join_contract row {row_no}: validation_checks is empty")
        if "support_id" not in row["hydrology_key"] and "support_id|month" not in row["hydrology_key"]:
            errors.append(f"join_contract row {row_no}: hydrology_key should include support_id context")

        seen_ids.add(lane_id)


def validate_unit_schema_rows(
    rows: list[dict[str, str]],
    schema_cfg: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    field_names = {row["field_name"] for row in rows}
    if len(field_names) != len(rows):
        warnings.append("unit_schema: duplicate field_name entries detected")

    allowed_required = set(schema_cfg["allowed_required_values"])
    allowed_types = set(schema_cfg["allowed_data_types"])
    allowed_sources = set(schema_cfg["allowed_source_streams"])

    for row_no, row in enumerate(rows, start=1):
        if row["required"] not in allowed_required:
            errors.append(f"unit_schema row {row_no}: required column must be required or optional")
        if row["data_type"] not in allowed_types:
            errors.append(f"unit_schema row {row_no}: unsupported data_type '{row['data_type']}'")
        sources = set(filter(None, [part.strip() for part in row["source_streams"].split(";")]))
        if not sources:
            errors.append(f"unit_schema row {row_no}: source_streams empty")
        if not sources.issubset(allowed_sources):
            extra = ", ".join(sorted(sources - allowed_sources))
            errors.append(f"unit_schema row {row_no}: unknown source_streams '{extra}'")


def validate_candidate_screen_rows(
    rows: list[dict[str, str]],
    schema_cfg: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    status_vocab = set(schema_cfg["status_vocab"])
    status_counter = Counter()
    requires_lab = 0
    for row_no, row in enumerate(rows, start=1):
        status = row["status"]
        status_counter[status] += 1
        if status not in status_vocab:
            errors.append(f"candidate_screen row {row_no}: unknown status '{status}'")
        if status == "needs_lab_leader_decision":
            warnings.append(f"candidate row {row_no}: explicitly review with lab leader")
        req = row["requires_lab_leader_approval"]
        if to_bool(req):
            requires_lab += 1
        if req.lower() not in {"true", "false", "yes", "no"}:
            errors.append(f"candidate_screen row {row_no}: requires_lab_leader_approval should be true/false/yes/no")

    if status_counter["needs_lab_leader_decision"] < 1:
        errors.append("candidate_screen: no needs_lab_leader_decision rows")
    if requires_lab < schema_cfg["requires_lab_leader_decision_min"]:
        errors.append(
            "candidate_screen: needs_lab_leader_approval minimum not met "
            f"(got {requires_lab}, need {schema_cfg['requires_lab_leader_decision_min']})"
        )


def validate_goal020_inputs(config: dict[str, Any], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    g020_ref = config["goal020_reference"]
    manifest_path = REPO / g020_ref["manifest_path"]
    readiness_rows = REPO / g020_ref["readiness_rows_path"]
    quality_rows = REPO / g020_ref["quality_fail_rows_path"]

    check_file_exists(manifest_path, "goal020 manifest", errors)
    check_file_exists(readiness_rows, "goal020 readiness", errors)
    check_file_exists(quality_rows, "goal020 quality_fail", errors)

    if not (manifest_path.exists() and readiness_rows.exists() and quality_rows.exists()):
        return {}

    readiness = read_csv(readiness_rows)
    quality_fail = read_csv(quality_rows)
    if len(readiness) != g020_ref["expected_row_count"]:
        errors.append(
            f"goal020 readiness row_count {len(readiness)} != expected {g020_ref['expected_row_count']}"
        )

    key_count = len({(row["support_id"], row["month"]) for row in readiness})
    if key_count != g020_ref["expected_row_count"]:
        errors.append(f"goal020 readiness composite key count {key_count} != expected {g020_ref['expected_row_count']}")

    counts = Counter(row["bird_linkage_readiness"] for row in readiness)
    expected_counts = {
        "core_eligible": g020_ref["expected_core_eligible"],
        "core_eligible_with_caveat": g020_ref["expected_core_eligible_with_caveat"],
        "sensitivity_only": g020_ref["expected_sensitivity_only"],
    }
    for status, exp_count in expected_counts.items():
        if counts.get(status, 0) != exp_count:
            errors.append(f"goal020 readiness {status} count {counts.get(status, 0)} != {exp_count}")

    quality_counts = Counter(row["quality_fail_reason"] for row in quality_fail)
    for reason, exp_reason_count in g020_ref["expected_quality_fail_reasons"].items():
        if quality_counts.get(reason, 0) != exp_reason_count:
            errors.append(f"goal020 quality_fail reason '{reason}' count {quality_counts.get(reason, 0)} != {exp_reason_count}")

    if len(quality_fail) != g020_ref["expected_quality_fail_count"]:
        errors.append(
            f"goal020 quality_fail row_count {len(quality_fail)} != expected {g020_ref['expected_quality_fail_count']}"
        )

    legacy_rows = [
        row
        for row in readiness
        if "legacy_stac_comparator_not_obtained" in (row.get("caveat_code") or "")
    ]
    if len(legacy_rows) != g020_ref["expected_goal018_legacy_caveat_count"]:
        errors.append(
            f"goal020 legacy comparator caveat row_count {len(legacy_rows)} != expected {g020_ref['expected_goal018_legacy_caveat_count']}"
        )
    for row in legacy_rows:
        if row["bird_linkage_readiness"] != "core_eligible_with_caveat":
            warnings.append(
                "goal020 legacy comparator caveat row not in core_eligible_with_caveat:"
                f" {row['support_id']}, {row['month']}"
            )

    return {
        "manifest_path": g020_ref["manifest_path"],
        "readiness_rows_path": g020_ref["readiness_rows_path"],
        "quality_fail_rows_path": g020_ref["quality_fail_rows_path"],
        "readiness_row_count": len(readiness),
        "quality_fail_row_count": len(quality_fail),
        "readiness_class_counts": dict(counts),
        "quality_fail_reasons": dict(quality_counts),
        "legacy_caveat_rows": len(legacy_rows),
    }


def validate_markdown_links(file_paths: list[Path], errors: list[str]) -> None:
    for file_path in file_paths:
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            target = target.split("#", 1)[0]
            if target.startswith(("`", "<", ">")):
                continue
            if not target:
                continue
            resolved = (file_path.parent / target)
            if not resolved.exists():
                errors.append(f"{file_path}: broken link -> {target}")


def validate_text_guardrails(file_paths: list[Path], errors: list[str]) -> None:
    for file_path in file_paths:
        text = file_path.read_text(encoding="utf-8")
        if UNFINISHED_MARKER_PATTERN.search(text):
            errors.append(
                f"{file_path}: contains unfinished-marker text"
            )


def validate_file_guardrails(config: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    guard = config["provisional_output_guardrails"]
    status = subprocess.run(
        ["git", "status", "--short", "--porcelain"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    paths: list[Path] = []
    for line in status.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        paths.append(REPO / path)

    for path in paths:
        suffix = path.suffix.lower()
        if suffix in set(guard["forbidden_extensions"]):
            errors.append(f"Guardrail: blocked extension in changed path {path}")
            continue
        if suffix and "raw" in path.parts and not "artifacts" in path.parts:
            warnings.append(f"Guardrail: raw path changed outside declared ignore area {path}")
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > guard["max_untracked_file_size_mb"]:
                errors.append(f"Guardrail: file too large {size_mb:.2f} MB in changed paths: {path}")


def parse_settings(path: Path) -> dict[str, Any]:
    settings = read_json(path)
    required = {"goal", "manifest_type", "run_command", "files", "csv_schemas", "join_contract_checks", "goal020_reference"}
    missing = required - set(settings)
    if missing:
        raise RuntimeError(f"Invalid settings: missing required keys {sorted(missing)}")
    return settings


def main() -> int:
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CONFIG
    errors: list[str] = []
    warnings: list[str] = []

    try:
        config = parse_settings(config_path)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 1

    files_cfg = config["files"]
    goal020 = validate_goal020_inputs(config, errors, warnings)

    design_memo = REPO / files_cfg["design_memo"]
    join_contract = REPO / files_cfg["join_contract"]
    unit_schema = REPO / files_cfg["unit_schema"]
    candidate_screen = REPO / files_cfg["candidate_screen"]
    access_protocol = REPO / files_cfg["access_protocol"]
    manifest_path = REPO / files_cfg["manifest_json"]
    goal_log = REPO / files_cfg["goal_log"]
    stream_register = REPO / files_cfg["data_stream_register"]
    decision_log = REPO / files_cfg["decision_log"]
    for path in [design_memo, join_contract, unit_schema, candidate_screen, access_protocol, goal_log, stream_register, decision_log]:
        check_file_exists(path, "artifact", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    try:
        join_rows = read_csv(join_contract)
        unit_rows = read_csv(unit_schema)
        candidate_rows = read_csv(candidate_screen)
    except Exception as exc:
        print(f"CSV READ ERROR: {exc}", file=sys.stderr)
        return 1

    validate_csv_schema(join_rows, config["csv_schemas"]["join_contract"], errors, warnings, "join_contract")
    validate_csv_schema(unit_rows, config["csv_schemas"]["unit_schema"], errors, warnings, "unit_schema")
    validate_csv_schema(candidate_rows, config["csv_schemas"]["candidate_screen"], errors, warnings, "candidate_screen")

    validate_markdown_links(
        [design_memo, access_protocol, join_contract, unit_schema, candidate_screen],
        errors,
    )
    validate_text_guardrails(
        [design_memo, access_protocol, join_contract, unit_schema, candidate_screen],
        errors,
    )
    validate_file_guardrails(config, errors, warnings)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        if warnings:
            for warning in warnings:
                print(f"WARNING: {warning}")
        return 1

    payload = {
        "goal": config["goal"],
        "manifest_type": config["manifest_type"],
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "accessed_date": config["accessed_date"],
        "run_command": config["run_command"],
        "goal020_decision": config["goal020_decision"],
        "design_goal_status": config["design_goal_status"],
        "goal020_reference": {
            "manifest_path": goal020["manifest_path"],
            "readiness_rows_path": goal020["readiness_rows_path"],
            "quality_fail_rows_path": goal020["quality_fail_rows_path"],
            "readiness_row_count": goal020["readiness_row_count"],
            "quality_fail_row_count": goal020["quality_fail_row_count"],
            "readiness_class_counts": goal020["readiness_class_counts"],
            "quality_fail_reasons": goal020["quality_fail_reasons"],
            "legacy_comparator_caveat_rows": goal020["legacy_caveat_rows"],
        },
        "artifacts": {
            "design_memo": {
                "path": files_cfg["design_memo"],
                "row_count": sum(1 for _ in design_memo.open(encoding="utf-8")),
                "sha256": file_hash(design_memo),
            },
            "join_contract": {
                "path": files_cfg["join_contract"],
                "row_count": len(join_rows),
                "row_hash": stable_row_hash(join_rows, ["lane_id"]),
                "sha256": file_hash(join_contract),
            },
            "unit_schema": {
                "path": files_cfg["unit_schema"],
                "row_count": len(unit_rows),
                "row_hash": stable_row_hash(unit_rows, ["field_name"]),
                "sha256": file_hash(unit_schema),
            },
            "candidate_screen": {
                "path": files_cfg["candidate_screen"],
                "row_count": len(candidate_rows),
                "row_hash": stable_row_hash(candidate_rows, ["species_or_guild"]),
                "sha256": file_hash(candidate_screen),
            },
            "access_protocol": {
                "path": files_cfg["access_protocol"],
                "lines": sum(1 for _ in access_protocol.open(encoding="utf-8")),
                "sha256": file_hash(access_protocol),
            },
        },
        "validation": {
            "status": "pass",
            "errors": [],
            "warnings": warnings,
            "file_scans": [
                {
                    "path": files_cfg["join_contract"],
                    "required_columns": config["csv_schemas"]["join_contract"]["required_columns"],
                    "row_count": len(join_rows),
                },
                {
                    "path": files_cfg["unit_schema"],
                    "required_columns": config["csv_schemas"]["unit_schema"]["required_columns"],
                    "row_count": len(unit_rows),
                },
                {
                    "path": files_cfg["candidate_screen"],
                    "required_columns": config["csv_schemas"]["candidate_screen"]["required_columns"],
                    "row_count": len(candidate_rows),
                },
            ],
        },
        "source_evidence_ids": config["required_public_sources"],
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Goal 021 validation passed.")
    print(f"Manifest written: {manifest_path.relative_to(REPO)}")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
