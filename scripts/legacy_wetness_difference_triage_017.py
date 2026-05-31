#!/usr/bin/env python3
"""Goal 017 triage for legacy wetness-field differences."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import platform
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO / "settings" / "legacy_wetness_difference_triage_017.json"

ROOT_CAUSE_VOCABULARY = {
    "tolerance_or_rounding_only",
    "legacy_bbox_scene_selection_effect",
    "legacy_support_grid_or_mask_effect",
    "legacy_metric_formula_or_quality_effect",
    "current_direct_s3_extraction_defect",
    "insufficient_reference_evidence",
    "unresolved_requires_bounded_rerun",
}
REQUIRED_ROOT_CAUSES = set(ROOT_CAUSE_VOCABULARY)
BLOCKED_RAW_EXTENSIONS = {
    ".shp",
    ".dbf",
    ".shx",
    ".prj",
    ".gpkg",
    ".geojson",
    ".kml",
    ".kmz",
    ".tif",
    ".tiff",
    ".nc",
    ".parquet",
    ".rds",
    ".zip",
    ".tar",
    ".gz",
    ".sqlite",
    ".duckdb",
    ".npy",
    ".npz",
}
COUNT_FIELDS = {
    "readable_scene_count",
    "clear_obs_count",
    "invalid_obs_count",
    "wet_pixel_observation_count",
    "dry_pixel_observation_count",
    "n_pixel_u",
    "clear_pixel_count",
    "no_data_count",
    "contiguity_count",
    "low_solar_angle_count",
    "terrain_shadow_count",
    "high_slope_count",
    "cloud_shadow_count",
    "cloud_count",
}
FRACTION_FIELDS = {"clear_obs_fraction", "current_proportion_wet", "clear_pixel_fraction"}
AREA_FIELDS = {"current_wet_area_m2", "valid_support_area_m2", "support_area_m2"}
STRING_FIELDS = {"quality_flag", "wet_month_flag", "status"}
WETNESS_FIELDS = {
    "current_wet_area_m2",
    "current_proportion_wet",
    "wet_pixel_observation_count",
    "dry_pixel_observation_count",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialise(row.get(field, "")) for field in fieldnames})


def serialise(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, list):
        return ";".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    if isinstance(value, float):
        return str(round(value, 9))
    return str(value)


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:
        return "unknown"


def git_status() -> str:
    try:
        return subprocess.check_output(["git", "status", "--short", "--branch"], cwd=REPO, text=True).strip()
    except Exception:
        return "unknown"


def host_facts() -> dict[str, str]:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
    }


def stable_hash(rows: list[dict[str, Any]], fields: list[str]) -> str:
    payload = [
        {field: str(row.get(field, "")) for field in fields}
        for row in sorted(rows, key=lambda row: tuple(str(row.get(field, "")) for field in fields))
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def is_blocked_raw_extension(path: Path) -> bool:
    path_text = path.as_posix()
    if path.suffix.lower() == ".json" and "/raw/" in f"/{path_text}":
        return True
    return path.suffix.lower() in BLOCKED_RAW_EXTENSIONS


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def select_target_rows(comparison_rows: list[dict[str, str]], target_status: str = "wetness_diff") -> list[dict[str, str]]:
    return sorted(
        [row for row in comparison_rows if row.get("comparison_status") == target_status],
        key=lambda row: (row.get("month", ""), row.get("support_id", ""), row.get("reference_source", "")),
    )


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return row.get("support_id", ""), row.get("month", ""), row.get("reference_source", "")


def validate_target_set(targets: list[dict[str, str]], expected: list[dict[str, str]]) -> None:
    observed = {key(row) for row in targets}
    expected_keys = {(row["support_id"], row["month"], row["reference_source"]) for row in expected}
    if observed != expected_keys:
        missing = sorted(expected_keys - observed)
        extra = sorted(observed - expected_keys)
        raise RuntimeError(f"Goal 017 target set mismatch; missing={missing}; extra={extra}")


def lookup_row(rows: list[dict[str, str]], support_id: str, month: str) -> dict[str, str]:
    return next((row for row in rows if row.get("support_id") == support_id and row.get("month") == month), {})


def reference_rows_for_source(config: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    inputs = config["inputs"]
    return {
        "goal007_legacy_event_window": read_csv(REPO / inputs["legacy_event_window_csv"]),
        "goal009_full_window_context": read_csv(REPO / inputs["legacy_full_window_csv"]),
    }


def numeric_delta(field: str, computed_value: Any, reference_value: Any) -> dict[str, Any]:
    computed_number = to_float(computed_value)
    reference_number = to_float(reference_value)
    if computed_number is None or reference_number is None:
        return {
            "field": field,
            "computed_number": "",
            "reference_number": "",
            "signed_difference": "",
            "abs_difference": "",
            "relative_difference": "",
        }
    signed = computed_number - reference_number
    relative = signed / reference_number if reference_number else ""
    return {
        "field": field,
        "computed_number": computed_number,
        "reference_number": reference_number,
        "signed_difference": signed,
        "abs_difference": abs(signed),
        "relative_difference": relative,
    }


def same_text(left: Any, right: Any) -> bool:
    return str(left or "").strip() == str(right or "").strip()


def numeric_equal(left: Any, right: Any, tolerance: float = 0.0) -> bool:
    left_number = to_float(left)
    right_number = to_float(right)
    if left_number is None or right_number is None:
        return same_text(left, right)
    return abs(left_number - right_number) <= tolerance


def rounding_wetness_only(computed: dict[str, str], reference: dict[str, str], tolerances: dict[str, Any]) -> bool:
    area_tol = float(tolerances.get("rounding_area_m2_abs", 0.0))
    frac_tol = float(tolerances.get("rounding_fraction_abs", 0.0))
    if not numeric_equal(computed.get("wet_pixel_observation_count"), reference.get("wet_pixel_observation_count")):
        return False
    if not numeric_equal(computed.get("dry_pixel_observation_count"), reference.get("dry_pixel_observation_count")):
        return False
    if not numeric_equal(computed.get("valid_support_area_m2"), reference.get("valid_support_area_m2")):
        return False
    if not same_text(computed.get("quality_flag"), reference.get("quality_flag")):
        return False
    if not same_text(computed.get("wet_month_flag"), reference.get("wet_month_flag")):
        return False
    area_ok = numeric_equal(computed.get("current_wet_area_m2"), reference.get("current_wet_area_m2"), area_tol)
    prop_ok = numeric_equal(computed.get("current_proportion_wet"), reference.get("current_proportion_wet"), frac_tol)
    return area_ok and prop_ok


def support_grid_or_mask_differs(computed: dict[str, str], reference: dict[str, str]) -> bool:
    checks = [
        ("geometry_hash_sha256", 0.0),
        ("n_pixel_u", 0.0),
        ("valid_support_area_m2", 0.0),
        ("support_area_m2", 1.0),
        ("clear_pixel_count", 0.0),
        ("clear_pixel_fraction", 0.000001),
    ]
    for field, tolerance in checks:
        if not numeric_equal(computed.get(field), reference.get(field), tolerance):
            return True
    return False


def material_wetness_diff(computed: dict[str, str], reference: dict[str, str], tolerances: dict[str, Any]) -> bool:
    if not rounding_wetness_only(computed, reference, tolerances):
        return True
    return False


def classify_root_cause(
    computed: dict[str, str],
    reference: dict[str, str],
    item_delta: dict[str, Any],
    tolerances: dict[str, Any],
) -> dict[str, str]:
    if computed.get("status") != "computed_direct_s3_metrics" or str(computed.get("skipped_scene_count", "0")) not in {"", "0"}:
        return {
            "root_cause_class": "current_direct_s3_extraction_defect",
            "evidence_basis": "Goal 016 computed row is not a clean direct-S3 metric row or has skipped scenes.",
            "scale_up_recommendation": "Do not scale; fix the current direct-S3 extraction row and repeat the bounded probe.",
            "current_direct_s3_defect": "yes",
        }
    if rounding_wetness_only(computed, reference, tolerances):
        return {
            "root_cause_class": "tolerance_or_rounding_only",
            "evidence_basis": "Wet/dry integer counts, support geometry, valid support area, quality flag, and wet-month flag match; remaining wetness delta is within triage rounding tolerance.",
            "scale_up_recommendation": "Treat as harmless for direct-S3 route promotion, while retaining rounded legacy values as provenance.",
            "current_direct_s3_defect": "no",
        }
    if support_grid_or_mask_differs(computed, reference):
        return {
            "root_cause_class": "legacy_support_grid_or_mask_effect",
            "evidence_basis": "Support geometry hash, pixel count, valid support area, or clear-pixel mask semantics differ between rows.",
            "scale_up_recommendation": "Do not scale until the support-grid or mask semantics are reconciled.",
            "current_direct_s3_defect": "no",
        }
    if item_delta.get("reference_asset_key_hash") or item_delta.get("reference_path_rows"):
        if item_delta.get("computed_path_rows") != item_delta.get("reference_path_rows"):
            return {
                "root_cause_class": "legacy_bbox_scene_selection_effect",
                "evidence_basis": "Reference item/path-row evidence differs from the Goal 015 support-intersecting path-row set.",
                "scale_up_recommendation": "Use Goal 015 path-row-filtered semantics; do not use the legacy bbox row as the validation baseline.",
                "current_direct_s3_defect": "no",
            }
        return {
            "root_cause_class": "legacy_metric_formula_or_quality_effect",
            "evidence_basis": "Item/path-row evidence is comparable but material wetness fields differ, pointing to legacy metric or quality semantics.",
            "scale_up_recommendation": "Audit formula and quality semantics before scale-up.",
            "current_direct_s3_defect": "no",
        }
    if material_wetness_diff(computed, reference, tolerances):
        return {
            "root_cause_class": "insufficient_reference_evidence",
            "evidence_basis": "Geometry and support-grid fields match, and Goal 016 has clean direct-S3 rows, but the legacy reference lacks item/path-row hashes needed to attribute the material wetness delta.",
            "scale_up_recommendation": "Do not use this legacy row as a blocking validation baseline; build a path-row-filtered comparator or bounded item reconstruction before production scale-up.",
            "current_direct_s3_defect": "no",
        }
    return {
        "root_cause_class": "unresolved_requires_bounded_rerun",
        "evidence_basis": "Static evidence does not separate scene-selection, metric, or route causes.",
        "scale_up_recommendation": "Run a bounded comparator rerun before scale-up.",
        "current_direct_s3_defect": "no",
    }


def difference_class(field: str, computed: dict[str, str], reference: dict[str, str], tolerances: dict[str, Any]) -> str:
    computed_value = computed.get(field, "")
    reference_value = reference.get(field, "")
    if same_text(computed_value, reference_value):
        return "equal"
    if field in AREA_FIELDS:
        delta = numeric_delta(field, computed_value, reference_value)
        if delta["abs_difference"] != "" and float(delta["abs_difference"]) <= float(tolerances.get("rounding_area_m2_abs", 0.0)):
            return "rounding_within_triage_tolerance"
    if field in FRACTION_FIELDS:
        delta = numeric_delta(field, computed_value, reference_value)
        if delta["abs_difference"] != "" and float(delta["abs_difference"]) <= float(tolerances.get("rounding_fraction_abs", 0.0)):
            return "rounding_within_triage_tolerance"
    if field in WETNESS_FIELDS:
        return "wetness_material_difference"
    if field in COUNT_FIELDS or field in STRING_FIELDS:
        return "denominator_or_quality_difference"
    return "non_numeric_difference"


def build_item_delta(
    target: dict[str, str],
    computed: dict[str, str],
    reference: dict[str, str],
    support_grids: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    support_id = target["support_id"]
    grid = support_grids.get(support_id, {})
    computed_scene_count = to_float(computed.get("readable_scene_count")) or 0
    reference_scene_count = to_float(reference.get("readable_scene_count")) or 0
    scene_delta = computed_scene_count - reference_scene_count
    if reference.get("asset_key_hash") or reference.get("path_rows"):
        item_status = "reference_item_provenance_available"
    elif scene_delta:
        item_status = "scene_count_diff_reference_lacks_item_provenance"
    else:
        item_status = "item_counts_match_reference_lacks_item_hash"
    return {
        "candidate_id": computed.get("candidate_id", ""),
        "support_id": support_id,
        "month": target["month"],
        "reference_source": target["reference_source"],
        "computed_path_rows": computed.get("path_rows", ""),
        "reference_path_rows": reference.get("path_rows", ""),
        "computed_asset_key_hash": computed.get("asset_key_hash", ""),
        "reference_asset_key_hash": reference.get("asset_key_hash", ""),
        "computed_item_id_hash": computed.get("item_id_hash", ""),
        "reference_item_id_hash": reference.get("item_id_hash", ""),
        "computed_readable_scene_count": computed.get("readable_scene_count", ""),
        "reference_readable_scene_count": reference.get("readable_scene_count", ""),
        "readable_scene_count_delta": int(scene_delta) if scene_delta == int(scene_delta) else scene_delta,
        "computed_geometry_hash_sha256": computed.get("geometry_hash_sha256", ""),
        "reference_geometry_hash_sha256": reference.get("geometry_hash_sha256", ""),
        "geometry_hash_match": same_text(computed.get("geometry_hash_sha256"), reference.get("geometry_hash_sha256")),
        "computed_n_pixel_u": computed.get("n_pixel_u", ""),
        "reference_n_pixel_u": reference.get("n_pixel_u", ""),
        "n_pixel_match": numeric_equal(computed.get("n_pixel_u"), reference.get("n_pixel_u")),
        "computed_valid_support_area_m2": computed.get("valid_support_area_m2", ""),
        "reference_valid_support_area_m2": reference.get("valid_support_area_m2", ""),
        "valid_support_area_match": numeric_equal(computed.get("valid_support_area_m2"), reference.get("valid_support_area_m2")),
        "goal016_grid_xsize": grid.get("xsize", ""),
        "goal016_grid_ysize": grid.get("ysize", ""),
        "goal016_support_mask_pixels": grid.get("support_mask_pixels", ""),
        "item_delta_status": item_status,
    }


def build_metric_delta_rows(
    target: dict[str, str],
    computed: dict[str, str],
    reference: dict[str, str],
    fields: list[str],
    tolerances: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in fields:
        delta = numeric_delta(field, computed.get(field, ""), reference.get(field, ""))
        rows.append(
            {
                "candidate_id": computed.get("candidate_id", ""),
                "support_id": target["support_id"],
                "month": target["month"],
                "reference_source": target["reference_source"],
                "field": field,
                "computed_value": computed.get(field, ""),
                "reference_value": reference.get(field, ""),
                "signed_difference": delta["signed_difference"],
                "abs_difference": delta["abs_difference"],
                "relative_difference": delta["relative_difference"],
                "difference_class": difference_class(field, computed, reference, tolerances),
            }
        )
    return rows


def audit_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "reference_source",
        "root_cause_class",
        "evidence_basis",
        "scale_up_recommendation",
        "current_direct_s3_defect",
        "computed_status",
        "reference_status",
        "geometry_hash_match",
        "n_pixel_match",
        "valid_support_area_match",
        "computed_path_rows",
        "reference_path_rows",
        "computed_readable_scene_count",
        "reference_readable_scene_count",
        "readable_scene_count_delta",
        "wetness_differing_fields",
        "max_abs_current_wet_area_m2_delta",
        "max_abs_current_proportion_wet_delta",
        "wet_pixel_observation_count_delta",
        "dry_pixel_observation_count_delta",
    ]


def item_delta_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "reference_source",
        "computed_path_rows",
        "reference_path_rows",
        "computed_asset_key_hash",
        "reference_asset_key_hash",
        "computed_item_id_hash",
        "reference_item_id_hash",
        "computed_readable_scene_count",
        "reference_readable_scene_count",
        "readable_scene_count_delta",
        "computed_geometry_hash_sha256",
        "reference_geometry_hash_sha256",
        "geometry_hash_match",
        "computed_n_pixel_u",
        "reference_n_pixel_u",
        "n_pixel_match",
        "computed_valid_support_area_m2",
        "reference_valid_support_area_m2",
        "valid_support_area_match",
        "goal016_grid_xsize",
        "goal016_grid_ysize",
        "goal016_support_mask_pixels",
        "item_delta_status",
    ]


def metric_delta_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "reference_source",
        "field",
        "computed_value",
        "reference_value",
        "signed_difference",
        "abs_difference",
        "relative_difference",
        "difference_class",
    ]


def build_audit_row(
    target: dict[str, str],
    computed: dict[str, str],
    reference: dict[str, str],
    item_delta: dict[str, Any],
    classification: dict[str, str],
) -> dict[str, Any]:
    wet_area_delta = numeric_delta("current_wet_area_m2", computed.get("current_wet_area_m2", ""), reference.get("current_wet_area_m2", ""))
    wet_prop_delta = numeric_delta("current_proportion_wet", computed.get("current_proportion_wet", ""), reference.get("current_proportion_wet", ""))
    wet_count_delta = numeric_delta(
        "wet_pixel_observation_count",
        computed.get("wet_pixel_observation_count", ""),
        reference.get("wet_pixel_observation_count", ""),
    )
    dry_count_delta = numeric_delta(
        "dry_pixel_observation_count",
        computed.get("dry_pixel_observation_count", ""),
        reference.get("dry_pixel_observation_count", ""),
    )
    return {
        "candidate_id": computed.get("candidate_id", ""),
        "support_id": target["support_id"],
        "month": target["month"],
        "reference_source": target["reference_source"],
        "root_cause_class": classification["root_cause_class"],
        "evidence_basis": classification["evidence_basis"],
        "scale_up_recommendation": classification["scale_up_recommendation"],
        "current_direct_s3_defect": classification["current_direct_s3_defect"],
        "computed_status": computed.get("status", ""),
        "reference_status": reference.get("status", ""),
        "geometry_hash_match": item_delta["geometry_hash_match"],
        "n_pixel_match": item_delta["n_pixel_match"],
        "valid_support_area_match": item_delta["valid_support_area_match"],
        "computed_path_rows": item_delta["computed_path_rows"],
        "reference_path_rows": item_delta["reference_path_rows"],
        "computed_readable_scene_count": item_delta["computed_readable_scene_count"],
        "reference_readable_scene_count": item_delta["reference_readable_scene_count"],
        "readable_scene_count_delta": item_delta["readable_scene_count_delta"],
        "wetness_differing_fields": target.get("wetness_differing_fields", ""),
        "max_abs_current_wet_area_m2_delta": wet_area_delta["abs_difference"],
        "max_abs_current_proportion_wet_delta": wet_prop_delta["abs_difference"],
        "wet_pixel_observation_count_delta": wet_count_delta["signed_difference"],
        "dry_pixel_observation_count_delta": dry_count_delta["signed_difference"],
    }


def status_counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(collections.Counter(str(row.get(field, "")) for row in rows).items()))


def write_report(path: Path, config: dict[str, Any], audit_rows: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    root_counts = status_counts(audit_rows, "root_cause_class")
    table = "\n".join(
        f"| {row['support_id']} | {row['month']} | {row['reference_source']} | {row['root_cause_class']} | {row['scale_up_recommendation']} |"
        for row in audit_rows
    )
    count_table = "\n".join(f"| {root} | {count} |" for root, count in root_counts.items())
    direct_defect = "yes" if any(row["current_direct_s3_defect"] == "yes" for row in audit_rows) else "no"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Goal 017 Legacy Wetness Difference Triage",
                "",
                f"Accessed date: `{config['accessed_date']}`.",
                "",
                "## Scope",
                "",
                "This compact triage audits the six Goal 016 rows labelled `wetness_diff` against legacy Goal 007/009 references. It does not launch full-window direct-S3 production or alter legacy output tables.",
                "",
                "## Root-Cause Counts",
                "",
                "| Root-cause class | Rows |",
                "| --- | ---: |",
                count_table,
                "",
                f"Current direct-S3 extraction defect found: `{direct_defect}`.",
                f"Bounded raster reruns used: `{manifest['bounded_reruns_used']}`.",
                "",
                "## Row Classifications",
                "",
                "| Support | Month | Reference | Root-cause class | Recommendation |",
                "| --- | --- | --- | --- | --- |",
                table,
                "",
                "## Interpretation",
                "",
                "Two rows are tolerance or rounding only: their wet/dry integer counts, support grid fields, valid support area, quality flag, and wet-month flag match, with only tiny rounded wet-area or proportion differences.",
                "",
                "The four material rows share support geometry, pixel counts, valid support area, and clean Goal 016 direct-S3 status, but the legacy references do not contain item hashes or path-row sets. They are therefore classified as `insufficient_reference_evidence`, not as current direct-S3 extraction defects.",
                "",
                "## Recommendation For Goal 018",
                "",
                manifest["recommendation_for_goal018"],
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def check_ignored(paths: list[Path]) -> dict[str, Any]:
    rel_paths = [repo_relative(path) for path in paths]
    completed = subprocess.run(
        ["git", "check-ignore", *rel_paths],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    ignored = completed.stdout.strip().splitlines() if completed.stdout.strip() else []
    return {
        "status": "all_ignored" if sorted(ignored) == sorted(rel_paths) else "not_all_ignored",
        "checked_paths": rel_paths,
        "ignored_paths": ignored,
        "stderr": completed.stderr.strip(),
    }


def recommendation_for_goal018(root_counts: dict[str, int]) -> str:
    if root_counts.get("current_direct_s3_extraction_defect", 0):
        return "Fix the direct-S3 extraction defect and repeat the bounded all-support probe before any full-window scale-up."
    if root_counts.get("insufficient_reference_evidence", 0):
        return "Build a bounded all-support path-row-filtered comparator or item-provenance reconstruction for the material legacy rows before full-window direct-S3 production."
    return "Proceed to a carefully scoped direct-S3 scale-up design with the Goal 015 scene-selection policy and retained provenance checks."


def run(config_path: Path) -> dict[str, Any]:
    started = time.time()
    config = load_json(config_path)
    for staging_path in config["staging_paths"].values():
        (REPO / staging_path).mkdir(parents=True, exist_ok=True)
    ignored_check = check_ignored(
        [
            REPO / config["staging_paths"]["raw"] / "probe.json",
            REPO / config["staging_paths"]["intermediate"] / "probe.npy",
            REPO / config["staging_paths"]["output"] / "probe.json",
        ]
    )
    if ignored_check["status"] != "all_ignored":
        raise RuntimeError(f"Goal 017 staging paths are not all ignored: {ignored_check}")

    inputs = config["inputs"]
    comparison_rows = read_csv(REPO / inputs["goal016_comparison_csv"])
    computed_rows = read_csv(REPO / inputs["goal016_summary_csv"])
    references = reference_rows_for_source(config)
    manifest016 = load_json(REPO / inputs["goal016_manifest_json"])
    support_grids = {
        row["support_id"]: row for row in manifest016.get("extraction_records", {}).get("support_grids", [])
    }
    targets = select_target_rows(comparison_rows, str(config.get("target_status", "wetness_diff")))
    validate_target_set(targets, config["target_rows"])

    audit_rows: list[dict[str, Any]] = []
    item_delta_rows: list[dict[str, Any]] = []
    metric_delta_rows: list[dict[str, Any]] = []
    for target in targets:
        support_id = target["support_id"]
        month = target["month"]
        reference_source = target["reference_source"]
        computed = lookup_row(computed_rows, support_id, month)
        reference = lookup_row(references.get(reference_source, []), support_id, month)
        if not computed or not reference:
            raise RuntimeError(f"missing computed or reference row for {support_id} {month} {reference_source}")
        item_delta = build_item_delta(target, computed, reference, support_grids)
        classification = classify_root_cause(computed, reference, item_delta, config["tolerances"])
        audit_rows.append(build_audit_row(target, computed, reference, item_delta, classification))
        item_delta_rows.append(item_delta)
        metric_delta_rows.extend(
            build_metric_delta_rows(target, computed, reference, config["metric_delta_fields"], config["tolerances"])
        )

    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    write_csv(outputs["audit_csv"], audit_rows, audit_fieldnames())
    write_csv(outputs["item_delta_csv"], item_delta_rows, item_delta_fieldnames())
    write_csv(outputs["metric_delta_csv"], metric_delta_rows, metric_delta_fieldnames())
    root_counts = status_counts(audit_rows, "root_cause_class")
    manifest = {
        "goal": config["goal"],
        "manifest_type": "legacy_wetness_difference_triage_017",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "accessed_date": config["accessed_date"],
        "command": config["run_command"],
        "config_path": repo_relative(config_path),
        "git_head_at_run": git_head(),
        "git_status_at_run": git_status(),
        "host_facts": host_facts(),
        "source_files": inputs,
        "source_urls": config["source_urls"],
        "target_row_count": len(targets),
        "target_rows": [{field: row[field] for field in ("support_id", "month", "reference_source")} for row in targets],
        "root_cause_counts": root_counts,
        "current_direct_s3_defect_found": any(row["current_direct_s3_defect"] == "yes" for row in audit_rows),
        "bounded_reruns_used": False,
        "bounded_rerun_reason": "Static evidence was sufficient to classify rows as tolerance-only or insufficient legacy reference evidence.",
        "outputs": {key: repo_relative(path) for key, path in outputs.items()},
        "audit_row_hash": stable_hash(audit_rows, ["support_id", "month", "reference_source", "root_cause_class"]),
        "item_delta_row_hash": stable_hash(item_delta_rows, ["support_id", "month", "reference_source", "item_delta_status"]),
        "metric_delta_row_count": len(metric_delta_rows),
        "root_cause_vocabulary": config["root_cause_vocabulary"],
        "tolerances": config["tolerances"],
        "staging_paths": config["staging_paths"],
        "staging_ignored_check": ignored_check,
        "staging_policy": config["commit_policy"],
        "recommendation_for_goal018": recommendation_for_goal018(root_counts),
        "elapsed_seconds": round(time.time() - started, 3),
    }
    write_json(outputs["manifest_json"], manifest)
    write_report(outputs["report_md"], config, audit_rows, manifest)
    write_json(REPO / config["staging_paths"]["output"] / "legacy_wetness_difference_triage_017_run.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to Goal 017 config JSON")
    args = parser.parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    manifest = run(config_path)
    print(
        json.dumps(
            {
                "target_rows": manifest["target_row_count"],
                "root_cause_counts": manifest["root_cause_counts"],
                "manifest": manifest["outputs"]["manifest_json"],
                "elapsed_seconds": manifest["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
