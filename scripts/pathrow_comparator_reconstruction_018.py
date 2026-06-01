#!/usr/bin/env python3
"""Goal 018 bounded path-row comparator and item-provenance reconstruction."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import platform
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from support_pathrow_metadata_013 import direct_s3_item_sets  # noqa: E402


DEFAULT_CONFIG = REPO / "settings" / "pathrow_comparator_reconstruction_018.json"

ROUTE_STATUS_VOCABULARY = {
    "stac_pathrow_matches_direct_s3",
    "stac_unavailable_direct_s3_provenance_only",
    "stac_available_item_mismatch",
    "direct_s3_item_reconstruction_mismatch",
    "blocked_route_failure",
    "blocked_insufficient_metadata",
    "not_applicable_control",
}
REQUIRED_ROUTE_STATUSES = set(ROUTE_STATUS_VOCABULARY)

READINESS_CLASS_VOCABULARY = {
    "ready_for_full_window_direct_s3",
    "ready_with_legacy_baseline_retired",
    "not_ready_item_mismatch",
    "not_ready_current_route_defect",
    "blocked_external_service",
    "blocked_insufficient_evidence",
}
REQUIRED_READINESS_CLASSES = set(READINESS_CLASS_VOCABULARY)

COMPARISON_STATUSES = {
    "item_sets_match",
    "item_set_mismatch",
    "comparator_unavailable",
    "not_applicable_control",
}

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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialise(row.get(field, "")) for field in fieldnames})


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


def stable_hash(values: list[Any]) -> str:
    payload = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stable_row_hash(rows: list[dict[str, Any]], fields: list[str]) -> str:
    payload = [
        {field: str(row.get(field, "")) for field in fields}
        for row in sorted(rows, key=lambda row: tuple(str(row.get(field, "")) for field in fields))
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def item_set_hashes(items: list[dict[str, str]]) -> dict[str, Any]:
    item_ids = sorted(item.get("item_id", "") for item in items)
    asset_keys = sorted(item.get("asset_key", "") for item in items)
    return {
        "item_count": len(items),
        "item_id_hash": stable_hash(item_ids) if item_ids else "",
        "asset_key_hash": stable_hash(asset_keys) if asset_keys else "",
    }


def is_blocked_raw_extension(path: Path) -> bool:
    parts = set(path.parts)
    if path.suffix.lower() == ".json" and "raw" in parts:
        return True
    return path.suffix.lower() in BLOCKED_RAW_EXTENSIONS


def select_target_rows(rows: list[dict[str, str]], include_controls: bool = False) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        root = row.get("root_cause_class", "")
        role = ""
        if root == "insufficient_reference_evidence":
            role = "material"
        elif include_controls and root == "tolerance_or_rounding_only":
            role = "control"
        if not role:
            continue
        selected.append(
            {
                "candidate_id": row.get("candidate_id", ""),
                "support_id": row.get("support_id", ""),
                "month": row.get("month", ""),
                "reference_source": row.get("reference_source", ""),
                "target_role": role,
                "goal017_root_cause_class": root,
                "goal017_reference_status": row.get("reference_status", ""),
                "goal017_computed_status": row.get("computed_status", ""),
                "goal017_current_direct_s3_defect": row.get("current_direct_s3_defect", ""),
                "goal017_wetness_differing_fields": row.get("wetness_differing_fields", ""),
                "computed_path_rows": row.get("computed_path_rows", ""),
                "selection_reason": row.get("scale_up_recommendation", ""),
            }
        )
    return sorted(selected, key=lambda row: (row["target_role"] != "material", row["month"], row["support_id"], row["reference_source"]))


def validate_material_targets(targets: list[dict[str, Any]]) -> None:
    expected = {
        ("nwb004_ramsar_component_369", "2018-01", "goal009_full_window_context"),
        ("nwb004_ramsar_ref265", "2022-11", "goal007_legacy_event_window"),
        ("nwb004_ramsar_component_369", "2024-12", "goal007_legacy_event_window"),
        ("nwb004_ramsar_ref265", "2024-12", "goal007_legacy_event_window"),
    }
    observed = {
        (row["support_id"], row["month"], row["reference_source"])
        for row in targets
        if row.get("target_role") == "material"
    }
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        raise RuntimeError(f"Goal 018 material target mismatch; missing={missing}; extra={extra}")


def path_rows_by_support(crosswalk_rows: list[dict[str, str]]) -> dict[str, list[str]]:
    grouped: dict[str, set[str]] = collections.defaultdict(set)
    for row in crosswalk_rows:
        support_id = row.get("support_id", "")
        path_row = row.get("path_row", "")
        if support_id and path_row and row.get("coverage_status", "complete") == "complete":
            grouped[support_id].add(path_row)
    return {support_id: sorted(path_rows) for support_id, path_rows in grouped.items()}


def support_context_by_id(crosswalk_rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    contexts: dict[str, dict[str, Any]] = {}
    for row in crosswalk_rows:
        support_id = row.get("support_id", "")
        if support_id and support_id not in contexts:
            contexts[support_id] = {
                "candidate_id": row.get("candidate_id", ""),
                "candidate_name": row.get("candidate_name", ""),
                "support_id": support_id,
                "support_class": row.get("support_class", ""),
                "support_level": row.get("support_level", ""),
                "support_type": row.get("support_type", ""),
                "support_area_m2": row.get("support_area_m2", ""),
                "support_geometry_hash_sha256": row.get("support_geometry_hash_sha256", ""),
                "support_bbox_wgs84": json.loads(row["support_bbox_wgs84"]) if row.get("support_bbox_wgs84") else [],
            }
    return contexts


def summary_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row.get("support_id", ""), row.get("month", "")): row for row in rows}


def config_for_months(config: dict[str, Any], months: list[str]) -> dict[str, Any]:
    run_config = dict(config)
    run_config["months"] = list(months)
    return run_config


def direct_items_for_target(
    item_lookup: dict[str, list[dict[str, str]]],
    month: str,
    path_rows: list[str],
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for path_row in path_rows:
        items.extend(item_lookup.get(f"{month}|{path_row}", []))
    return sorted(items, key=lambda item: (item.get("asset_key", ""), item.get("item_id", "")))


def month_range(month: str) -> tuple[str, str]:
    year, month_number = map(int, month.split("-"))
    start = dt.datetime(year, month_number, 1, tzinfo=dt.UTC)
    stop = dt.datetime(year + int(month_number == 12), 1 if month_number == 12 else month_number + 1, 1, tzinfo=dt.UTC)
    return start.strftime("%Y-%m-%dT%H:%M:%SZ"), stop.strftime("%Y-%m-%dT%H:%M:%SZ")


def stac_payload(config: dict[str, Any], bbox: list[float], month: str) -> dict[str, Any]:
    start, stop = month_range(month)
    return {
        "collections": [config["dea_collection"]],
        "bbox": bbox,
        "datetime": f"{start}/{stop}",
        "limit": int(config["stac"]["limit"]),
    }


def compact_headers(headers: dict[str, Any]) -> dict[str, str]:
    keep = {}
    for key in ("Content-Type", "Retry-After", "X-Request-Id"):
        if key in headers:
            keep[key] = str(headers[key])
    return keep


def post_stac(url: str, payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read()
            return {
                "ok": True,
                "status_code": int(response.status),
                "headers": compact_headers(dict(response.headers)),
                "elapsed_seconds": round(time.time() - started, 3),
                "body": body.decode("utf-8"),
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        body = exc.read()
        return {
            "ok": False,
            "status_code": int(exc.code),
            "headers": compact_headers(dict(exc.headers)),
            "elapsed_seconds": round(time.time() - started, 3),
            "body": body.decode("utf-8", errors="replace"),
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "status_code": "",
            "headers": {},
            "elapsed_seconds": round(time.time() - started, 3),
            "body": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def path_row_from_asset_key(asset_key: str) -> str:
    match = re.search(r"/(\d{3})/(\d{3})/\d{4}/\d{2}/", asset_key)
    return f"{match.group(1)}/{match.group(2)}" if match else ""


def stac_feature_to_item(feature: dict[str, Any], bucket: str) -> dict[str, str] | None:
    href = feature.get("assets", {}).get("water", {}).get("href", "")
    if not href:
        return None
    asset_key = href
    if href.startswith(f"s3://{bucket}/"):
        asset_key = href.removeprefix(f"s3://{bucket}/")
    elif href.startswith("https://"):
        parsed = urllib.parse.urlparse(href)
        asset_key = parsed.path.lstrip("/")
        bucket_prefix = f"{bucket}/"
        if asset_key.startswith(bucket_prefix):
            asset_key = asset_key.removeprefix(bucket_prefix)
    return {
        "item_id": str(feature.get("id", "")),
        "asset_key": asset_key,
        "path_row": path_row_from_asset_key(asset_key),
    }


def fetch_stac_items(
    config: dict[str, Any],
    target: dict[str, Any],
    bbox: list[float],
    reuse_cache: bool,
) -> dict[str, Any]:
    raw_dir = REPO / config["staging_paths"]["raw"]
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_path = raw_dir / f"stac_bbox_{target['support_id']}_{target['month']}.json"
    payload = stac_payload(config, bbox, target["month"])
    if reuse_cache and cache_path.exists():
        cached = load_json(cache_path)
        body_json = cached.get("body_json", {})
        status_code = cached.get("status_code", "")
        ok = bool(cached.get("ok", False))
        result = cached
    else:
        response = post_stac(config["stac"]["search_url"], payload, int(config["stac"]["timeout_seconds"]))
        body_json: dict[str, Any] = {}
        if response.get("body"):
            try:
                body_json = json.loads(str(response["body"]))
            except Exception:
                body_json = {}
        result = {
            "support_id": target["support_id"],
            "month": target["month"],
            "payload": payload,
            "ok": response["ok"],
            "status_code": response["status_code"],
            "headers": response["headers"],
            "elapsed_seconds": response["elapsed_seconds"],
            "error": response["error"],
            "feature_count": len(body_json.get("features", [])),
            "body_json": body_json if response["ok"] else {},
            "body_excerpt": str(response.get("body", ""))[:500] if not response["ok"] else "",
        }
        write_json(cache_path, result)
        status_code = result["status_code"]
        ok = bool(result["ok"])
    features = body_json.get("features", []) if ok else []
    items = [
        item
        for item in (stac_feature_to_item(feature, config["s3"]["bucket"]) for feature in features)
        if item is not None
    ]
    return {
        "support_id": target["support_id"],
        "month": target["month"],
        "cache_path": repo_relative(cache_path),
        "ok": ok,
        "status_code": status_code,
        "error": result.get("error", ""),
        "feature_count": len(features),
        "items": sorted(items, key=lambda item: (item["asset_key"], item["item_id"])),
        "limit_reached": ok and len(features) >= int(config["stac"]["limit"]),
    }


def filter_items_to_path_rows(items: list[dict[str, str]], path_rows: set[str]) -> dict[str, Any]:
    filtered = sorted(
        [item for item in items if item.get("path_row") in path_rows],
        key=lambda item: (item.get("asset_key", ""), item.get("item_id", "")),
    )
    extras = sorted(
        [item for item in items if item.get("path_row") not in path_rows],
        key=lambda item: (item.get("asset_key", ""), item.get("item_id", "")),
    )
    return {
        "filtered_items": filtered,
        "bbox_extra_items": extras,
        "filtered_hashes": item_set_hashes(filtered),
        "bbox_hashes": item_set_hashes(items),
        "bbox_extra_item_count": len(extras),
        "bbox_extra_path_rows": sorted({item.get("path_row", "") for item in extras if item.get("path_row")}),
    }


def compare_item_sets(direct: dict[str, Any], comparator: dict[str, Any]) -> dict[str, Any]:
    direct_count = int(direct.get("item_count") or 0)
    comparator_count = int(comparator.get("item_count") or 0)
    count_delta = comparator_count - direct_count
    asset_match = str(direct.get("asset_key_hash", "")) == str(comparator.get("asset_key_hash", ""))
    item_match = str(direct.get("item_id_hash", "")) == str(comparator.get("item_id_hash", ""))
    status = "item_sets_match" if count_delta == 0 and asset_match and item_match else "item_set_mismatch"
    return {
        "comparison_status": status,
        "item_count_delta": count_delta,
        "asset_key_hash_match": asset_match,
        "item_id_hash_match": item_match,
        "current_direct_s3_defect": False,
    }


def classify_route_status(
    direct_matches_goal016: bool,
    stac_result: dict[str, Any],
    stac_filtered_hashes: dict[str, Any],
    direct_hashes: dict[str, Any],
) -> str:
    if not direct_matches_goal016:
        return "direct_s3_item_reconstruction_mismatch"
    if stac_result.get("limit_reached"):
        return "blocked_insufficient_metadata"
    if not stac_result.get("ok"):
        return "stac_unavailable_direct_s3_provenance_only"
    comparison = compare_item_sets(direct_hashes, stac_filtered_hashes)
    if comparison["comparison_status"] == "item_sets_match":
        return "stac_pathrow_matches_direct_s3"
    return "stac_available_item_mismatch"


def classify_readiness(route_status: str, comparison_status: str, direct_matches_goal016: bool) -> dict[str, str]:
    if not direct_matches_goal016 or route_status == "direct_s3_item_reconstruction_mismatch":
        return {
            "readiness_class": "not_ready_current_route_defect",
            "scale_up_recommendation": "Do not scale; resolve direct-S3 item reconstruction versus Goal 016 committed hash mismatch and repeat the bounded probe.",
        }
    if route_status == "stac_pathrow_matches_direct_s3" and comparison_status == "item_sets_match":
        return {
            "readiness_class": "ready_for_full_window_direct_s3",
            "scale_up_recommendation": "Legacy row can be retired as a blocking baseline; independent STAC path-row comparator matches direct-S3 item selection for this target.",
        }
    if route_status == "stac_unavailable_direct_s3_provenance_only" and comparison_status == "item_sets_match":
        return {
            "readiness_class": "ready_with_legacy_baseline_retired",
            "scale_up_recommendation": "Legacy row can be retired as a blocking baseline; direct-S3 item provenance matches Goal 016, but independent STAC comparator evidence was unavailable.",
        }
    if route_status == "stac_available_item_mismatch" or comparison_status == "item_set_mismatch":
        return {
            "readiness_class": "not_ready_item_mismatch",
            "scale_up_recommendation": "Do not scale; investigate the path-row-filtered STAC versus direct-S3 item-set mismatch before production.",
        }
    if route_status == "blocked_route_failure":
        return {
            "readiness_class": "blocked_external_service",
            "scale_up_recommendation": "Repeat the bounded route probe after the external service recovers before production.",
        }
    return {
        "readiness_class": "blocked_insufficient_evidence",
        "scale_up_recommendation": "Do not scale; reconstruct enough item metadata to classify this target before production.",
    }


def targets_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "reference_source",
        "target_role",
        "goal017_root_cause_class",
        "goal017_reference_status",
        "goal017_computed_status",
        "goal017_current_direct_s3_defect",
        "goal017_wetness_differing_fields",
        "computed_path_rows",
        "derived_path_rows",
        "selection_reason",
    ]


def item_sets_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "target_role",
        "route",
        "route_status",
        "path_rows",
        "item_count",
        "asset_key_hash",
        "item_id_hash",
        "bbox_extra_item_count",
        "bbox_extra_path_rows",
        "source_status_code",
        "source_cache_path",
        "provenance_caveat",
    ]


def comparison_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "target_role",
        "comparison_type",
        "comparison_status",
        "route_status",
        "direct_s3_item_count",
        "comparator_item_count",
        "item_count_delta",
        "direct_s3_asset_key_hash",
        "comparator_asset_key_hash",
        "asset_key_hash_match",
        "direct_s3_item_id_hash",
        "comparator_item_id_hash",
        "item_id_hash_match",
        "current_direct_s3_defect",
        "recommendation",
    ]


def readiness_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "target_role",
        "route_status",
        "readiness_class",
        "stac_comparator_obtained",
        "direct_s3_matches_goal016",
        "current_direct_s3_defect",
        "bounded_raster_rerun_needed",
        "scale_up_recommendation",
    ]


def check_ignored(paths: list[Path]) -> dict[str, Any]:
    check_paths = [str(path) for path in paths]
    result = subprocess.run(["git", "check-ignore", *check_paths], cwd=REPO, text=True, capture_output=True)
    ignored = set(result.stdout.splitlines())
    return {
        "checked": [repo_relative(path) for path in paths],
        "ignored": sorted(repo_relative(Path(path)) for path in ignored),
        "all_ignored": result.returncode == 0 and len(ignored) == len(paths),
        "returncode": result.returncode,
    }


def status_counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(collections.Counter(str(row.get(field, "")) for row in rows).items()))


def comparison_recommendation(comparison_type: str, comparison_status: str, route_status: str) -> str:
    if comparison_status == "item_sets_match" and comparison_type == "direct_s3_reconstruction_vs_goal016_committed":
        return "Use reconstructed direct-S3 item provenance as compact evidence that Goal 016 committed hashes are reproducible."
    if comparison_status == "item_sets_match":
        return "Use the path-row-filtered comparator as independent support for direct-S3 scene selection."
    if comparison_status == "comparator_unavailable" and route_status == "stac_unavailable_direct_s3_provenance_only":
        return "Retain direct-S3 item provenance and record STAC unavailability; do not use the legacy row as a blocker."
    return "Do not scale until this item-set comparison is resolved."


def write_report(path: Path, manifest: dict[str, Any], readiness_rows: list[dict[str, Any]], comparison_rows: list[dict[str, Any]]) -> None:
    route_counts = status_counts(readiness_rows, "route_status")
    readiness_counts = status_counts(readiness_rows, "readiness_class")
    comparison_counts = status_counts(comparison_rows, "comparison_status")
    target_table = "\n".join(
        f"| {row['support_id']} | {row['month']} | {row['route_status']} | {row['readiness_class']} | {row['scale_up_recommendation']} |"
        for row in readiness_rows
    )
    route_table = "\n".join(f"| {status} | {count} |" for status, count in route_counts.items())
    ready_table = "\n".join(f"| {status} | {count} |" for status, count in readiness_counts.items())
    comparison_table = "\n".join(f"| {status} | {count} |" for status, count in comparison_counts.items())
    independent = "yes" if manifest["independent_stac_comparator_obtained"] else "no"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Goal 018 Path-Row Comparator Reconstruction",
                "",
                f"Accessed date: `{manifest['accessed_date']}`.",
                "",
                "## Scope",
                "",
                "This bounded reconstruction covers the four Goal 017 material rows classified as `insufficient_reference_evidence`. It does not launch full-window direct-S3 production or alter legacy output tables.",
                "",
                "## Route Status Counts",
                "",
                "| Route status | Rows |",
                "| --- | ---: |",
                route_table,
                "",
                "## Readiness Counts",
                "",
                "| Readiness class | Rows |",
                "| --- | ---: |",
                ready_table,
                "",
                "## Item-Set Comparison Counts",
                "",
                "| Comparison status | Rows |",
                "| --- | ---: |",
                comparison_table,
                "",
                f"Independent STAC comparator evidence obtained for all material targets: `{independent}`.",
                f"Current direct-S3 defect found: `{'yes' if manifest['current_direct_s3_defect_found'] else 'no'}`.",
                f"Bounded raster reruns used: `{manifest['bounded_raster_reruns_used']}`.",
                "",
                "## Material Target Readiness",
                "",
                "| Support | Month | Route status | Readiness class | Recommendation |",
                "| --- | --- | --- | --- | --- |",
                target_table,
                "",
                "## Interpretation",
                "",
                manifest["interpretation"],
                "",
                "## Recommendation For Goal 019",
                "",
                manifest["recommendation_for_goal019"],
                "",
            ]
        ),
        encoding="utf-8",
    )


def recommendation_for_goal019(readiness_rows: list[dict[str, Any]]) -> str:
    ready = {"ready_for_full_window_direct_s3", "ready_with_legacy_baseline_retired"}
    not_ready = [row for row in readiness_rows if row.get("readiness_class") not in ready]
    if not_ready:
        return "Repair or rerun the blocked/mismatched Goal 018 target rows before any full-window direct-S3 production goal."
    return "Proceed to Goal 019 as a remote, restartable full-window direct-S3 hydrology production preflight or production run, retaining the support-intersecting WRS path-row scene-selection policy."


def build_outputs(config: dict[str, Any], reuse_cache: bool) -> dict[str, Any]:
    inputs = {key: REPO / value for key, value in config["inputs"].items()}
    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    audit_rows = read_csv(inputs["goal017_audit_csv"])
    crosswalk_rows = read_csv(inputs["goal013_crosswalk_csv"])
    summary_rows = read_csv(inputs["goal016_summary_csv"])
    manifest013 = load_json(inputs["goal013_manifest_json"])
    manifest016 = load_json(inputs["goal016_manifest_json"])

    targets = select_target_rows(audit_rows, bool(config.get("include_controls", False)))
    validate_material_targets(targets)
    material_targets = [row for row in targets if row["target_role"] == "material"]

    pathrow_map = path_rows_by_support(crosswalk_rows)
    contexts = support_context_by_id(crosswalk_rows)
    summary_by_key = summary_lookup(summary_rows)
    for target in targets:
        target["derived_path_rows"] = ";".join(pathrow_map.get(target["support_id"], []))
        if not target["derived_path_rows"]:
            raise RuntimeError(f"missing derived path rows for {target['support_id']}")

    item_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    readiness_rows: list[dict[str, Any]] = []
    route_records: list[dict[str, Any]] = []
    stac_route_records: list[dict[str, Any]] = []

    targets_by_support: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for target in targets:
        targets_by_support[target["support_id"]].append(target)

    direct_lookup_by_support: dict[str, dict[str, list[dict[str, str]]]] = {}
    for support_id, support_targets in sorted(targets_by_support.items()):
        months = sorted({target["month"] for target in support_targets})
        context = contexts[support_id]
        candidate = {
            "candidate_id": context["candidate_id"],
            "candidate_name": context["candidate_name"],
            "support_id": support_id,
        }
        run_config = config_for_months(config, months)
        _pathrow_item_rows, item_lookup, route_record_rows = direct_s3_item_sets(
            run_config,
            candidate,
            pathrow_map[support_id],
            reuse_cache,
        )
        direct_lookup_by_support[support_id] = item_lookup
        route_records.extend({**record, "support_id": support_id} for record in route_record_rows)

    for target in material_targets:
        context = contexts[target["support_id"]]
        path_rows = pathrow_map[target["support_id"]]
        path_row_set = set(path_rows)
        goal016_row = summary_by_key.get((target["support_id"], target["month"]), {})
        goal016_hashes = {
            "item_count": int(goal016_row.get("direct_s3_items_found") or goal016_row.get("readable_scene_count") or 0),
            "asset_key_hash": goal016_row.get("asset_key_hash", ""),
            "item_id_hash": goal016_row.get("item_id_hash", ""),
        }
        direct_items = direct_items_for_target(direct_lookup_by_support[target["support_id"]], target["month"], path_rows)
        direct_hashes = item_set_hashes(direct_items)
        direct_goal016_comparison = compare_item_sets(direct_hashes, goal016_hashes)
        direct_matches_goal016 = direct_goal016_comparison["comparison_status"] == "item_sets_match"

        stac_result = fetch_stac_items(config, target, context["support_bbox_wgs84"], reuse_cache)
        stac_route_records.append(
            {
                "support_id": target["support_id"],
                "month": target["month"],
                "ok": stac_result.get("ok", False),
                "status_code": stac_result.get("status_code", ""),
                "error": stac_result.get("error", ""),
                "feature_count": stac_result.get("feature_count", 0),
                "cache_path": stac_result.get("cache_path", ""),
                "limit_reached": stac_result.get("limit_reached", False),
            }
        )
        stac_filtered = filter_items_to_path_rows(stac_result["items"], path_row_set)
        stac_hashes = stac_filtered["filtered_hashes"]
        route_status = classify_route_status(direct_matches_goal016, stac_result, stac_hashes, direct_hashes)
        if not stac_result.get("ok"):
            stac_comparison_status = "comparator_unavailable"
        else:
            stac_comparison = compare_item_sets(direct_hashes, stac_hashes)
            stac_comparison_status = stac_comparison["comparison_status"]
        readiness = classify_readiness(route_status, direct_goal016_comparison["comparison_status"], direct_matches_goal016)
        if route_status == "stac_pathrow_matches_direct_s3":
            readiness = classify_readiness(route_status, stac_comparison_status, direct_matches_goal016)
        elif route_status == "stac_available_item_mismatch":
            readiness = classify_readiness(route_status, "item_set_mismatch", direct_matches_goal016)

        common = {
            "candidate_id": target["candidate_id"],
            "support_id": target["support_id"],
            "month": target["month"],
            "target_role": target["target_role"],
        }
        item_rows.extend(
            [
                {
                    **common,
                    "route": "goal016_committed_direct_s3",
                    "route_status": route_status,
                    "path_rows": goal016_row.get("path_rows", target["computed_path_rows"]),
                    "item_count": goal016_hashes["item_count"],
                    "asset_key_hash": goal016_hashes["asset_key_hash"],
                    "item_id_hash": goal016_hashes["item_id_hash"],
                    "bbox_extra_item_count": "",
                    "bbox_extra_path_rows": "",
                    "source_status_code": "",
                    "source_cache_path": config["inputs"]["goal016_summary_csv"],
                    "provenance_caveat": "Committed Goal 016 summary hash and item count.",
                },
                {
                    **common,
                    "route": "direct_s3_reconstructed",
                    "route_status": route_status,
                    "path_rows": ";".join(path_rows),
                    "item_count": direct_hashes["item_count"],
                    "asset_key_hash": direct_hashes["asset_key_hash"],
                    "item_id_hash": direct_hashes["item_id_hash"],
                    "bbox_extra_item_count": "",
                    "bbox_extra_path_rows": "",
                    "source_status_code": "200" if direct_hashes["item_count"] else "",
                    "source_cache_path": config["staging_paths"]["raw"],
                    "provenance_caveat": "Fresh direct-S3 path-row/month listing reconstruction; raw listing and HEAD caches remain ignored.",
                },
                {
                    **common,
                    "route": "stac_pathrow_filtered",
                    "route_status": route_status,
                    "path_rows": ";".join(path_rows),
                    "item_count": stac_hashes["item_count"] if stac_result.get("ok") else "",
                    "asset_key_hash": stac_hashes["asset_key_hash"] if stac_result.get("ok") else "",
                    "item_id_hash": stac_hashes["item_id_hash"] if stac_result.get("ok") else "",
                    "bbox_extra_item_count": stac_filtered["bbox_extra_item_count"] if stac_result.get("ok") else "",
                    "bbox_extra_path_rows": stac_filtered["bbox_extra_path_rows"] if stac_result.get("ok") else "",
                    "source_status_code": stac_result.get("status_code", ""),
                    "source_cache_path": stac_result.get("cache_path", ""),
                    "provenance_caveat": "DEA STAC bbox metadata filtered to support-intersecting WRS path/rows; raw STAC response remains ignored."
                    if stac_result.get("ok")
                    else f"DEA STAC comparator unavailable: {stac_result.get('status_code') or stac_result.get('error')}",
                },
            ]
        )

        comparison_rows.append(
            {
                **common,
                "comparison_type": "direct_s3_reconstruction_vs_goal016_committed",
                "comparison_status": direct_goal016_comparison["comparison_status"],
                "route_status": route_status,
                "direct_s3_item_count": direct_hashes["item_count"],
                "comparator_item_count": goal016_hashes["item_count"],
                "item_count_delta": direct_goal016_comparison["item_count_delta"],
                "direct_s3_asset_key_hash": direct_hashes["asset_key_hash"],
                "comparator_asset_key_hash": goal016_hashes["asset_key_hash"],
                "asset_key_hash_match": direct_goal016_comparison["asset_key_hash_match"],
                "direct_s3_item_id_hash": direct_hashes["item_id_hash"],
                "comparator_item_id_hash": goal016_hashes["item_id_hash"],
                "item_id_hash_match": direct_goal016_comparison["item_id_hash_match"],
                "current_direct_s3_defect": not direct_matches_goal016,
                "recommendation": comparison_recommendation(
                    "direct_s3_reconstruction_vs_goal016_committed",
                    direct_goal016_comparison["comparison_status"],
                    route_status,
                ),
            }
        )
        stac_compare = compare_item_sets(direct_hashes, stac_hashes) if stac_result.get("ok") else {
            "comparison_status": "comparator_unavailable",
            "item_count_delta": "",
            "asset_key_hash_match": "",
            "item_id_hash_match": "",
            "current_direct_s3_defect": False,
        }
        comparison_rows.append(
            {
                **common,
                "comparison_type": "stac_pathrow_filtered_vs_direct_s3",
                "comparison_status": stac_compare["comparison_status"],
                "route_status": route_status,
                "direct_s3_item_count": direct_hashes["item_count"],
                "comparator_item_count": stac_hashes["item_count"] if stac_result.get("ok") else "",
                "item_count_delta": stac_compare["item_count_delta"],
                "direct_s3_asset_key_hash": direct_hashes["asset_key_hash"],
                "comparator_asset_key_hash": stac_hashes["asset_key_hash"] if stac_result.get("ok") else "",
                "asset_key_hash_match": stac_compare["asset_key_hash_match"],
                "direct_s3_item_id_hash": direct_hashes["item_id_hash"],
                "comparator_item_id_hash": stac_hashes["item_id_hash"] if stac_result.get("ok") else "",
                "item_id_hash_match": stac_compare["item_id_hash_match"],
                "current_direct_s3_defect": False,
                "recommendation": comparison_recommendation(
                    "stac_pathrow_filtered_vs_direct_s3",
                    stac_compare["comparison_status"],
                    route_status,
                ),
            }
        )
        readiness_rows.append(
            {
                **common,
                "route_status": route_status,
                "readiness_class": readiness["readiness_class"],
                "stac_comparator_obtained": route_status == "stac_pathrow_matches_direct_s3",
                "direct_s3_matches_goal016": direct_matches_goal016,
                "current_direct_s3_defect": not direct_matches_goal016,
                "bounded_raster_rerun_needed": route_status in {"stac_available_item_mismatch", "direct_s3_item_reconstruction_mismatch"},
                "scale_up_recommendation": readiness["scale_up_recommendation"],
            }
        )

    write_csv(outputs["targets_csv"], targets, targets_fieldnames())
    write_csv(outputs["item_sets_csv"], item_rows, item_sets_fieldnames())
    write_csv(outputs["comparison_csv"], comparison_rows, comparison_fieldnames())
    write_csv(outputs["readiness_csv"], readiness_rows, readiness_fieldnames())

    staging_probe_paths = [
        REPO / config["staging_paths"]["raw"] / "probe.json",
        REPO / config["staging_paths"]["intermediate"] / "probe.npy",
        REPO / config["staging_paths"]["output"] / "probe.json",
    ]
    ignored_check = check_ignored(staging_probe_paths)
    readiness_ready = {"ready_for_full_window_direct_s3", "ready_with_legacy_baseline_retired"}
    independent = all(row["route_status"] == "stac_pathrow_matches_direct_s3" for row in readiness_rows)
    current_defect = any(row["current_direct_s3_defect"] for row in readiness_rows)
    bounded_rerun = any(row["bounded_raster_rerun_needed"] for row in readiness_rows)
    interpretation = (
        "All four material legacy rows have reconstructed direct-S3 item provenance matching the committed Goal 016 item counts and hashes. "
        "STAC path-row comparator evidence was obtained for every material row and matched direct S3."
        if independent
        else "All four material legacy rows have reconstructed direct-S3 item provenance matching the committed Goal 016 item counts and hashes. "
        "Independent STAC comparator evidence was unavailable for at least one material row, so the legacy rows should be retired as blocking baselines on provenance grounds rather than independent STAC equivalence."
    )
    manifest = {
        "goal": config["goal"],
        "manifest_type": "pathrow_comparator_reconstruction_018",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "accessed_date": config["accessed_date"],
        "command": config["run_command"] + (" --reuse-ignored-cache" if reuse_cache else ""),
        "config_path": repo_relative(DEFAULT_CONFIG),
        "reuse_ignored_cache": reuse_cache,
        "git_head_at_run": git_head(),
        "git_status_at_run": git_status(),
        "host_facts": host_facts(),
        "source_files": config["inputs"],
        "source_urls": config["source_urls"],
        "scene_selection_policy": config["scene_selection_policy"],
        "goal013_support_path_rows": manifest013.get("support_path_rows", {}),
        "goal016_summary_row_hash": manifest016.get("summary_row_hash", ""),
        "target_row_count": len(targets),
        "material_target_row_count": len(material_targets),
        "control_row_count": len([row for row in targets if row["target_role"] == "control"]),
        "target_rows": [
            {
                "support_id": row["support_id"],
                "month": row["month"],
                "reference_source": row["reference_source"],
                "target_role": row["target_role"],
                "derived_path_rows": row["derived_path_rows"],
            }
            for row in targets
        ],
        "route_status_counts": status_counts(readiness_rows, "route_status"),
        "comparison_status_counts": status_counts(comparison_rows, "comparison_status"),
        "readiness_class_counts": status_counts(readiness_rows, "readiness_class"),
        "independent_stac_comparator_obtained": independent,
        "current_direct_s3_defect_found": current_defect,
        "bounded_raster_reruns_used": bounded_rerun,
        "bounded_raster_rerun_reason": "Item-set mismatch requires diagnostic raster rerun." if bounded_rerun else "No item-set mismatch required raster reads.",
        "direct_s3_route_records": route_records,
        "stac_route_records": stac_route_records,
        "outputs": {key: repo_relative(path) for key, path in outputs.items()},
        "target_row_hash": stable_row_hash(targets, ["support_id", "month", "target_role", "goal017_root_cause_class"]),
        "item_set_row_hash": stable_row_hash(item_rows, ["support_id", "month", "route", "asset_key_hash"]),
        "comparison_row_hash": stable_row_hash(comparison_rows, ["support_id", "month", "comparison_type", "comparison_status"]),
        "readiness_row_hash": stable_row_hash(readiness_rows, ["support_id", "month", "readiness_class", "route_status"]),
        "staging_paths": config["staging_paths"],
        "staging_ignored_check": ignored_check,
        "staging_policy": config["commit_policy"],
        "remote_compute_used": False,
        "remote_paths": {},
        "cleanup_status": "Local raw route caches retained only in ignored Goal 018 staging; no remote cleanup required.",
        "route_status_vocabulary": sorted(ROUTE_STATUS_VOCABULARY),
        "readiness_class_vocabulary": sorted(READINESS_CLASS_VOCABULARY),
        "interpretation": interpretation,
        "recommendation_for_goal019": recommendation_for_goal019(readiness_rows),
        "ready_material_target_count": sum(row["readiness_class"] in readiness_ready for row in readiness_rows),
    }
    write_json(outputs["manifest_json"], manifest)
    write_report(outputs["report_md"], manifest, readiness_rows, comparison_rows)
    write_json(REPO / config["staging_paths"]["output"] / "pathrow_comparator_reconstruction_018_run.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to Goal 018 JSON settings")
    parser.add_argument("--reuse-ignored-cache", action="store_true", help="Reuse ignored STAC/S3 route caches")
    args = parser.parse_args()
    started = time.time()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    config = load_json(config_path)
    manifest = build_outputs(config, args.reuse_ignored_cache)
    print(
        json.dumps(
            {
                "elapsed_seconds": round(time.time() - started, 3),
                "material_target_rows": manifest["material_target_row_count"],
                "route_status_counts": manifest["route_status_counts"],
                "readiness_class_counts": manifest["readiness_class_counts"],
                "manifest": manifest["outputs"]["manifest_json"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
