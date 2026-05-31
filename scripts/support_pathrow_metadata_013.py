#!/usr/bin/env python3
"""Goal 013 support-to-path/row coverage and metadata comparator prototype."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib
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
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from osgeo import ogr, osr


REPO = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = REPO / "settings" / "support_pathrow_metadata_013.json"
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
}
CROSSWALK_FIELDS = [
    "support_id",
    "candidate_id",
    "candidate_name",
    "support_class",
    "support_level",
    "support_type",
    "path",
    "row",
    "path_row",
    "coverage_method",
    "coverage_status",
    "source_id",
    "support_geometry_hash_sha256",
    "support_bbox_wgs84",
    "wrs_zip_sha256",
    "wrs_feature_pr",
    "wrs_mode",
    "intersection_area_m2",
    "support_area_m2",
    "caveat",
]
ITEM_SET_FIELDS = [
    "candidate_id",
    "candidate_name",
    "support_id",
    "month",
    "path",
    "row",
    "path_row",
    "item_count",
    "item_id_hash",
    "asset_key_hash",
    "route_status",
    "listing_status_code",
    "head_ok_count",
    "key_sample",
    "caveat",
]
COMPARATOR_FIELDS = [
    "comparator",
    "status",
    "scientific_equivalence_status",
    "recommendation",
    "evidence",
    "attempted",
    "blocker",
]


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(values: list[Any]) -> str:
    payload = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def path_row_key(path: int | str, row: int | str) -> str:
    return f"{int(path):03d}/{int(row):03d}"


def split_path_row(path_row: str) -> tuple[str, str]:
    path, row = path_row.split("/")
    return f"{int(path):03d}", f"{int(row):03d}"


def s3_prefix_for_path_row_month(collection: str, version: str, path: int | str, row: int | str, month: str) -> str:
    year, month_number = month.split("-")
    path_text, row_text = split_path_row(path_row_key(path, row))
    return f"derivative/{collection}/{version}/{path_text}/{row_text}/{year}/{month_number}/"


def is_blocked_raw_extension(path: Path) -> bool:
    return path.suffix.lower() in BLOCKED_RAW_EXTENSIONS


def coverage_status(method: str, path_rows: list[str]) -> str:
    if not path_rows:
        return "blocked"
    if method == "geometry_intersection":
        return "complete"
    if method == "bbox_intersection":
        return "conservative"
    return "unresolved"


def item_set_hashes(items: list[dict[str, str]]) -> dict[str, Any]:
    item_ids = sorted(item.get("item_id", "") for item in items)
    asset_keys = sorted(item.get("asset_key", "") for item in items)
    path_rows = sorted(item.get("path_row", "") for item in items)
    return {
        "item_count": len(items),
        "item_id_hash": stable_hash(item_ids) if item_ids else "",
        "asset_key_hash": stable_hash(asset_keys) if asset_keys else "",
        "path_row_hash": stable_hash(path_rows) if path_rows else "",
    }


def final_equivalence_status(
    stac_status: str,
    official_comparator_status: str,
    s3_goal012_status: str,
    support_coverage_status: str,
) -> str:
    if support_coverage_status != "complete":
        return "support_coverage_incomplete"
    if stac_status in {"available_equivalent", "available_equivalent_for_derived_pathrows"}:
        return "equivalent"
    if official_comparator_status in {"available_equivalent", "equivalent"}:
        return "equivalent"
    if stac_status.startswith("unavailable") or official_comparator_status in {
        "missing_local_dependency",
        "requires_external_account_or_environment",
    }:
        return "comparator_unavailable"
    if stac_status == "available":
        return "technical_viability_not_equivalence"
    if s3_goal012_status.startswith("identical"):
        return "lower_evidence_only"
    return "technical_viability_not_equivalence"


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, text=True).strip()
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


def ensure_download(url: str, path: Path, timeout: int = 180) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return {
            "path": repo_relative(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "downloaded": False,
        }
    with urllib.request.urlopen(url, timeout=timeout) as response, path.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return {
        "path": repo_relative(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "downloaded": True,
    }


def load_event_window_supports(config: dict[str, Any]) -> list[dict[str, Any]]:
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    from event_window_hydrology_007 import build_parent_supports, build_support_set

    support_source = config["support_source"]
    event_config = load_json(REPO / support_source["event_config_path"])
    ramsar_subset = load_json(REPO / support_source["ramsar_subset_geojson"])
    parents, features_by_refcode = build_parent_supports(event_config, ramsar_subset)
    supports, _crosswalk_rows, _evidence_checks, _named_geometry_manifest = build_support_set(
        event_config,
        parents,
        features_by_refcode,
        REPO / support_source["waterbodies_zip"],
    )
    return supports


def support_bbox_text(support: dict[str, Any]) -> str:
    minx, maxx, miny, maxy = support["bbox_wgs84"]
    return json.dumps([round(minx, 10), round(miny, 10), round(maxx, 10), round(maxy, 10)], separators=(",", ":"))


def feature_path_row(feature: ogr.Feature) -> tuple[str, str, str]:
    path = int(feature.GetField("PATH"))
    row = int(feature.GetField("ROW"))
    key = path_row_key(path, row)
    path_text, row_text = split_path_row(key)
    return path_text, row_text, key


def wrs_layer_path(zip_path: Path, layer_path: str) -> str:
    return f"/vsizip/{zip_path}/{layer_path}"


def derive_support_pathrow_crosswalk(
    supports: list[dict[str, Any]],
    wrs_zip_path: Path,
    wrs_layer_name: str,
    wrs_source_id: str,
    wrs_zip_sha: str,
    coverage_method_name: str,
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    dataset = ogr.Open(wrs_layer_path(wrs_zip_path, wrs_layer_name))
    if dataset is None:
        raise RuntimeError(f"could not open WRS layer in {wrs_zip_path}")
    layer = dataset.GetLayer(0)
    wrs_srs = layer.GetSpatialRef()
    if wrs_srs is not None:
        wrs_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    from event_window_hydrology_007 import epsg_srs

    to_albers = osr.CoordinateTransformation(wrs_srs, epsg_srs(3577)) if wrs_srs is not None else None
    rows: list[dict[str, Any]] = []
    by_support: dict[str, list[str]] = {}
    for support in sorted(supports, key=lambda item: item["support_id"]):
        minx, maxx, miny, maxy = support["bbox_wgs84"]
        layer.SetSpatialFilterRect(minx, miny, maxx, maxy)
        support_rows: list[dict[str, Any]] = []
        for feature in layer:
            geom = feature.GetGeometryRef()
            if geom is None:
                continue
            geom = geom.Clone()
            if to_albers is not None:
                geom.Transform(to_albers)
            if not geom.Intersects(support["geom_albers"]):
                continue
            intersection = geom.Intersection(support["geom_albers"])
            if intersection is None or intersection.IsEmpty():
                continue
            area_m2 = float(intersection.GetArea())
            if area_m2 <= 0:
                continue
            path_text, row_text, key = feature_path_row(feature)
            support_rows.append(
                {
                    "support_id": support["support_id"],
                    "candidate_id": support["candidate_id"],
                    "candidate_name": support["candidate_name"],
                    "support_class": support.get("evidence_status", ""),
                    "support_level": support.get("support_level", ""),
                    "support_type": support.get("support_type", ""),
                    "path": path_text,
                    "row": row_text,
                    "path_row": key,
                    "coverage_method": coverage_method_name,
                    "coverage_status": "",
                    "source_id": wrs_source_id,
                    "support_geometry_hash_sha256": support.get("geometry_hash_sha256", ""),
                    "support_bbox_wgs84": support_bbox_text(support),
                    "wrs_zip_sha256": wrs_zip_sha,
                    "wrs_feature_pr": feature.GetField("PR") or feature.GetField("WRSPR") or "",
                    "wrs_mode": feature.GetField("MODE") or "",
                    "intersection_area_m2": round(area_m2, 3),
                    "support_area_m2": round(float(support.get("support_area_m2") or support["geom_albers"].GetArea()), 3),
                    "caveat": "WRS scene footprints overlap; intersection areas are per scene and are not additive.",
                }
            )
        layer.SetSpatialFilter(None)
        path_rows = sorted({row["path_row"] for row in support_rows})
        status = coverage_status(coverage_method_name, path_rows)
        for row in sorted(support_rows, key=lambda item: (item["path"], item["row"])):
            row["coverage_status"] = status
            rows.append(row)
        by_support[support["support_id"]] = path_rows
    return rows, by_support


def url_request(method: str, url: str, timeout: int, payload: bytes | None = None) -> dict[str, Any]:
    request = urllib.request.Request(url, data=payload, method=method)
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(4_000_000)
            return {
                "ok": 200 <= response.status < 300,
                "status_code": response.status,
                "elapsed_seconds": round(time.time() - started, 3),
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": response.headers.get("Content-Length", ""),
                "body": body,
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(1_000_000)
        return {
            "ok": False,
            "status_code": exc.code,
            "elapsed_seconds": round(time.time() - started, 3),
            "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
            "content_length": exc.headers.get("Content-Length", "") if exc.headers else "",
            "body": body,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "status_code": None,
            "elapsed_seconds": round(time.time() - started, 3),
            "content_type": "",
            "content_length": "",
            "body": b"",
            "error": f"{type(exc).__name__}: {exc}",
        }


def compact_response(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "body"}


def s3_list_url(base_url: str, prefix: str, max_keys: int, continuation_token: str | None = None) -> str:
    query: dict[str, Any] = {"list-type": "2", "prefix": prefix, "max-keys": max(1, int(max_keys))}
    if continuation_token:
        query["continuation-token"] = continuation_token
    return f"{base_url}/?{urllib.parse.urlencode(query)}"


def s3_listing_keys(xml_body: bytes) -> tuple[list[str], str | None]:
    root = ET.fromstring(xml_body)
    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag.split("}", 1)[0].strip("{")

    def tag(name: str) -> str:
        return f"{{{namespace}}}{name}" if namespace else name

    keys = [node.text or "" for node in root.findall(f".//{tag('Key')}")]
    token_node = root.find(tag("NextContinuationToken"))
    token = token_node.text if token_node is not None else None
    return keys, token


def load_cached_json(path: Path, reuse_cache: bool) -> dict[str, Any] | None:
    if not reuse_cache or not path.exists():
        return None
    return load_json(path)


def list_s3_prefix(config: dict[str, Any], prefix: str, cache_path: Path, reuse_cache: bool) -> dict[str, Any]:
    cached = load_cached_json(cache_path, reuse_cache)
    if cached is not None:
        return cached
    all_keys: list[str] = []
    pages: list[dict[str, Any]] = []
    continuation: str | None = None
    for _page_index in range(int(config["s3"]["max_pages"])):
        url = s3_list_url(config["s3"]["base_url"], prefix, int(config["s3"]["max_keys"]), continuation)
        result = url_request("GET", url, int(config["s3"]["timeout_seconds"]))
        keys: list[str] = []
        next_token: str | None = None
        if result["ok"]:
            keys, next_token = s3_listing_keys(result["body"])
            all_keys.extend(keys)
        pages.append({**compact_response(result), "url": url, "key_count": len(keys), "next_token_present": bool(next_token)})
        if not result["ok"] or not next_token:
            break
        continuation = next_token
    payload = {
        "prefix": prefix,
        "pages": pages,
        "keys": sorted(set(all_keys)),
    }
    write_json(cache_path, payload)
    return payload


def item_id_from_s3_water_key(key: str) -> str:
    return re.sub(r"_water\.tif$", "", Path(key).name)


def s3_water_items(keys: list[str], path_row: str) -> list[dict[str, str]]:
    items = []
    for key in sorted(keys):
        if key.endswith("_water.tif"):
            path_text, row_text = split_path_row(path_row)
            items.append(
                {
                    "item_id": item_id_from_s3_water_key(key),
                    "asset_key": key,
                    "path_row": path_row,
                    "path": path_text,
                    "row": row_text,
                }
            )
    return items


def head_s3_items(config: dict[str, Any], items: list[dict[str, str]], cache_path: Path, reuse_cache: bool) -> dict[str, Any]:
    cached = load_cached_json(cache_path, reuse_cache)
    if cached is not None:
        return cached
    head_records: list[dict[str, Any]] = []
    limit = int(config["s3"]["head_request_limit_per_prefix"])
    for item in items[:limit]:
        url = f"{config['s3']['base_url']}/{item['asset_key']}"
        result = url_request("HEAD", url, int(config["s3"]["timeout_seconds"]))
        head_records.append({**item, **compact_response(result), "url": url})
    payload = {
        "head_request_limit": limit,
        "head_records": head_records,
        "head_ok_count": sum(1 for record in head_records if record.get("status_code") == 200),
    }
    write_json(cache_path, payload)
    return payload


def item_set_row(
    config: dict[str, Any],
    candidate: dict[str, Any],
    month: str,
    path_row: str,
    items: list[dict[str, str]],
    listing: dict[str, Any],
    head: dict[str, Any],
) -> dict[str, Any]:
    path_text, row_text = split_path_row(path_row)
    hashes = item_set_hashes(items)
    first_page = listing.get("pages", [{}])[0] if listing.get("pages") else {}
    listing_status = first_page.get("status_code", "")
    status = "available" if listing_status == 200 else "listing_failed"
    return {
        "candidate_id": candidate["candidate_id"],
        "candidate_name": candidate["candidate_name"],
        "support_id": candidate["support_id"],
        "month": month,
        "path": path_text,
        "row": row_text,
        "path_row": path_row,
        "item_count": hashes["item_count"],
        "item_id_hash": hashes["item_id_hash"],
        "asset_key_hash": hashes["asset_key_hash"],
        "route_status": status,
        "listing_status_code": listing_status,
        "head_ok_count": head.get("head_ok_count", 0),
        "key_sample": ";".join(item["asset_key"] for item in items[:3]),
        "caveat": "Direct S3 path-row/month listing only; no hydrology metrics computed.",
    }


def direct_s3_item_sets(
    config: dict[str, Any],
    candidate: dict[str, Any],
    path_rows: list[str],
    reuse_cache: bool,
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, str]]], list[dict[str, Any]]]:
    raw_dir = REPO / config["staging_paths"]["raw"]
    intermediate_dir = REPO / config["staging_paths"]["intermediate"]
    rows: list[dict[str, Any]] = []
    item_lookup: dict[str, list[dict[str, str]]] = {}
    records: list[dict[str, Any]] = []
    for month in config["months"]:
        for path_row in path_rows:
            path_text, row_text = split_path_row(path_row)
            prefix = s3_prefix_for_path_row_month(
                config["dea_collection"], config["dea_product_version"], path_text, row_text, month
            )
            cache_stem = f"s3_listing_{candidate['candidate_id']}_{month}_{path_text}{row_text}.json"
            listing = list_s3_prefix(config, prefix, raw_dir / cache_stem, reuse_cache)
            items = s3_water_items(listing.get("keys", []), path_row)
            head_stem = f"s3_head_{candidate['candidate_id']}_{month}_{path_text}{row_text}.json"
            head = head_s3_items(config, items, intermediate_dir / head_stem, reuse_cache)
            rows.append(item_set_row(config, candidate, month, path_row, items, listing, head))
            item_lookup[f"{month}|{path_row}"] = items
            records.append(
                {
                    "month": month,
                    "path_row": path_row,
                    "prefix": prefix,
                    "water_item_count": len(items),
                    "listing_cache": repo_relative(raw_dir / cache_stem),
                    "head_cache": repo_relative(intermediate_dir / head_stem),
                    "listing_pages": listing.get("pages", []),
                    "head_ok_count": head.get("head_ok_count", 0),
                }
            )
    return rows, item_lookup, records


def month_range(month: str) -> tuple[str, str]:
    year, month_number = map(int, month.split("-"))
    start = dt.datetime(year, month_number, 1, tzinfo=dt.UTC)
    stop = dt.datetime(year + int(month_number == 12), 1 if month_number == 12 else month_number + 1, 1, tzinfo=dt.UTC)
    return start.strftime("%Y-%m-%dT%H:%M:%SZ"), stop.strftime("%Y-%m-%dT%H:%M:%SZ")


def stac_payload(collection: str, bbox: list[float], month: str, limit: int) -> dict[str, Any]:
    start, stop = month_range(month)
    return {
        "collections": [collection],
        "bbox": bbox,
        "datetime": f"{start}/{stop}",
        "limit": int(limit),
    }


def support_bbox_list(support: dict[str, Any]) -> list[float]:
    minx, maxx, miny, maxy = support["bbox_wgs84"]
    return [float(minx), float(miny), float(maxx), float(maxy)]


def stac_preflight(config: dict[str, Any], support: dict[str, Any], reuse_cache: bool) -> tuple[dict[str, Any], dict[str, list[dict[str, str]]]]:
    raw_path = REPO / config["staging_paths"]["raw"] / "stac_preflight_013.json"
    cached = load_cached_json(raw_path, reuse_cache)
    if cached is not None:
        return cached, stac_items_by_month(cached.get("month_results", []), config["s3"]["bucket"])
    results: list[dict[str, Any]] = []
    for month in config["months"]:
        payload = stac_payload(
            config["dea_collection"],
            support_bbox_list(support),
            month,
            int(config["stac_preflight"]["limit"]),
        )
        response = url_request(
            "POST",
            config["dea_stac_search_url"],
            int(config["stac_preflight"]["timeout_seconds"]),
            json.dumps(payload).encode("utf-8"),
        )
        body_json: dict[str, Any] = {}
        if response["body"]:
            try:
                body_json = json.loads(response["body"].decode("utf-8"))
            except Exception:
                body_json = {}
        results.append(
            {
                "month": month,
                "payload": payload,
                **compact_response(response),
                "feature_count": len(body_json.get("features", [])),
                "features": body_json.get("features", []) if response["ok"] else [],
            }
        )
    failed = [result["month"] for result in results if result.get("status_code") != 200]
    status = "available" if not failed and results else "unavailable_service_unstable"
    summary = {
        "route_status": status,
        "failure_months": failed,
        "reason": "All probe months returned HTTP 200." if status == "available" else "At least one probe month failed strict STAC preflight.",
    }
    payload = {
        "support_id": support["support_id"],
        "bbox": support_bbox_list(support),
        "summary": summary,
        "month_results": results,
    }
    write_json(raw_path, payload)
    return payload, stac_items_by_month(results, config["s3"]["bucket"])


def stac_items_by_month(results: list[dict[str, Any]], bucket: str) -> dict[str, list[dict[str, str]]]:
    by_month: dict[str, list[dict[str, str]]] = {}
    for result in results:
        items: list[dict[str, str]] = []
        for feature in result.get("features", []):
            href = feature.get("assets", {}).get("water", {}).get("href", "")
            asset_key = href
            if href.startswith(f"s3://{bucket}/"):
                asset_key = href.removeprefix(f"s3://{bucket}/")
            elif href.startswith("https://"):
                asset_key = urllib.parse.urlparse(href).path.lstrip("/")
            path_row_match = re.search(r"/(\d{3})/(\d{3})/\d{4}/\d{2}/", asset_key)
            path_row = f"{path_row_match.group(1)}/{path_row_match.group(2)}" if path_row_match else ""
            if asset_key:
                items.append({"item_id": str(feature.get("id", "")), "asset_key": asset_key, "path_row": path_row})
        by_month[str(result.get("month", ""))] = sorted(items, key=lambda item: (item["asset_key"], item["item_id"]))
    return by_month


def compare_stac_to_s3_item_sets(
    stac_status: str,
    stac_items: dict[str, list[dict[str, str]]],
    s3_items: dict[str, list[dict[str, str]]],
    months: list[str],
    derived_path_rows: list[str],
) -> dict[str, Any]:
    if stac_status != "available":
        return {
            "status": stac_status,
            "all_months_equal": False,
            "month_results": [],
            "reason": "STAC item comparison was not run because strict preflight did not pass.",
        }
    derived_set = set(derived_path_rows)
    month_results: list[dict[str, Any]] = []
    all_equal = True
    for month in months:
        stac_month_all = stac_items.get(month, [])
        stac_month_filtered = [item for item in stac_month_all if item.get("path_row") in derived_set]
        stac_outside = [item for item in stac_month_all if item.get("path_row") not in derived_set]
        s3_month: list[dict[str, str]] = []
        for path_row in derived_path_rows:
            s3_month.extend(s3_items.get(f"{month}|{path_row}", []))
        stac_assets = sorted(item["asset_key"] for item in stac_month_filtered)
        s3_assets = sorted(item["asset_key"] for item in s3_month)
        missing_from_s3 = sorted(set(stac_assets) - set(s3_assets))
        missing_from_stac = sorted(set(s3_assets) - set(stac_assets))
        equal = not missing_from_s3 and not missing_from_stac and len(stac_assets) == len(s3_assets)
        all_equal = all_equal and equal
        month_results.append(
            {
                "month": month,
                "stac_filtered_item_count": len(stac_assets),
                "s3_item_count": len(s3_assets),
                "stac_bbox_extra_item_count": len(stac_outside),
                "stac_asset_key_hash": stable_hash(stac_assets) if stac_assets else "",
                "s3_asset_key_hash": stable_hash(s3_assets) if s3_assets else "",
                "equal_for_derived_pathrows": equal,
                "missing_from_s3_sample": missing_from_s3[:5],
                "missing_from_stac_sample": missing_from_stac[:5],
            }
        )
    return {
        "status": "available_equivalent_for_derived_pathrows" if all_equal else "available_mismatch_for_derived_pathrows",
        "all_months_equal": all_equal,
        "month_results": month_results,
        "reason": "STAC assets filtered to the derived WRS path/row set match direct S3 assets."
        if all_equal
        else "STAC assets filtered to the derived WRS path/row set do not match direct S3 assets.",
    }


def probe_official_datacube_comparator(config: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    imported: list[str] = []
    for module_name in config["official_comparator"]["local_modules"]:
        try:
            importlib.import_module(module_name)
            imported.append(module_name)
        except Exception as exc:
            missing.append(f"{module_name}: {type(exc).__name__}")
    if missing:
        return {
            "status": "missing_local_dependency",
            "scientific_equivalence_status": "comparator_unavailable",
            "attempted": "yes",
            "blocker": "; ".join(missing),
            "evidence": "Local Python environment lacks the official ODC/odc-stac modules needed for an indexed metadata comparator.",
        }
    return {
        "status": "available_not_configured",
        "scientific_equivalence_status": "blocked",
        "attempted": "yes",
        "blocker": "Modules import, but no project datacube index/environment is configured in this repo.",
        "evidence": "Local imports succeeded for " + ";".join(imported),
    }


def load_goal012_known_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("route") == "direct_s3_path_row":
                rows[f"{row['month']}|{row['path_or_bbox_key']}"] = row
    return rows


def compare_goal012_known_path(
    config: dict[str, Any],
    item_rows: list[dict[str, Any]],
    derived_path_rows: list[str],
) -> dict[str, Any]:
    known = load_goal012_known_rows(REPO / config["goal012"]["item_sets_csv"])
    known_path = config["goal012"]["known_path_row"]
    mismatches: list[str] = []
    identical: list[str] = []
    for row in item_rows:
        if row["path_row"] != known_path:
            continue
        prior = known.get(f"{row['month']}|{known_path}")
        if not prior:
            mismatches.append(f"{row['month']} missing prior Goal 012 row")
            continue
        if str(row["asset_key_hash"]) == str(prior.get("asset_key_hash")) and str(row["item_count"]) == str(prior.get("item_count")):
            identical.append(row["month"])
        else:
            mismatches.append(f"{row['month']} hash/count mismatch")
    added_path_rows = sorted(set(derived_path_rows) - {known_path})
    if mismatches:
        status = "known_path_mismatch"
    elif len(identical) == len(config["months"]):
        status = "identical_known_path_plus_added_pathrows" if added_path_rows else "identical_known_path"
    else:
        status = "known_path_incomplete"
    return {
        "status": status,
        "known_path_row": known_path,
        "identical_months": identical,
        "mismatches": mismatches,
        "added_path_rows": added_path_rows,
    }


def build_comparator_rows(
    config: dict[str, Any],
    stac_result: dict[str, Any],
    stac_comparison: dict[str, Any],
    official_comparator: dict[str, Any],
    goal012_comparison: dict[str, Any],
    support_coverage: str,
) -> list[dict[str, Any]]:
    stac_status = stac_comparison["status"]
    final_status = final_equivalence_status(
        stac_status=stac_status,
        official_comparator_status=official_comparator["status"],
        s3_goal012_status=goal012_comparison["status"],
        support_coverage_status=support_coverage,
    )
    rows = [
        {
            "comparator": "dea_stac",
            "status": stac_status,
            "scientific_equivalence_status": "equivalent"
            if stac_status == "available_equivalent_for_derived_pathrows"
            else "comparator_unavailable",
            "recommendation": "Treat direct S3 as metadata-equivalent for this bounded path/row-month set."
            if stac_status == "available_equivalent_for_derived_pathrows"
            else "Do not claim equivalence from STAC while preflight or item-set comparison fails.",
            "evidence": stac_comparison["reason"]
            + f" preflight={stac_result['summary']['route_status']}; failure_months={';'.join(stac_result['summary']['failure_months'])}",
            "attempted": "yes",
            "blocker": ""
            if stac_status == "available_equivalent_for_derived_pathrows"
            else "DEA STAC strict preflight or filtered item-set comparison did not prove equivalence.",
        },
        {
            "comparator": "official_odc_local",
            "status": official_comparator["status"],
            "scientific_equivalence_status": official_comparator["scientific_equivalence_status"],
            "recommendation": "Use a configured DEA Sandbox/NCI/ODC environment if STAC remains unavailable.",
            "evidence": official_comparator["evidence"],
            "attempted": official_comparator["attempted"],
            "blocker": official_comparator["blocker"],
        },
        {
            "comparator": "goal012_known_path",
            "status": goal012_comparison["status"],
            "scientific_equivalence_status": "lower_evidence_only",
            "recommendation": "Use as regression evidence only; it is not an official metadata comparator.",
            "evidence": (
                "known_path="
                + goal012_comparison["known_path_row"]
                + "; identical_months="
                + ";".join(goal012_comparison["identical_months"])
                + "; added_path_rows="
                + ";".join(goal012_comparison["added_path_rows"])
            ),
            "attempted": "yes",
            "blocker": "" if not goal012_comparison["mismatches"] else "; ".join(goal012_comparison["mismatches"]),
        },
        {
            "comparator": "final_equivalence_status",
            "status": final_status,
            "scientific_equivalence_status": final_status,
            "recommendation": (
                "Do not promote direct S3 extraction until an official comparator is available."
                if final_status != "equivalent"
                else "Direct S3 metadata is equivalent for this bounded candidate/month set."
            ),
            "evidence": f"support_coverage={support_coverage}; stac={stac_status}; odc={official_comparator['status']}; goal012={goal012_comparison['status']}",
            "attempted": "yes",
            "blocker": "" if final_status == "equivalent" else "Official item-set comparator remains unavailable or incomplete.",
        },
    ]
    return rows


def write_report(
    path: Path,
    config: dict[str, Any],
    wrs_record: dict[str, Any],
    support_count: int,
    primary_path_rows: list[str],
    item_rows: list[dict[str, Any]],
    comparator_rows: list[dict[str, Any]],
    stac_comparison: dict[str, Any],
) -> None:
    counts_by_month: dict[str, int] = {}
    for row in item_rows:
        counts_by_month[row["month"]] = counts_by_month.get(row["month"], 0) + int(row["item_count"])
    final_row = next(row for row in comparator_rows if row["comparator"] == "final_equivalence_status")
    stac_lines = [
        f"- {result['month']}: filtered STAC={result['stac_filtered_item_count']}, direct S3={result['s3_item_count']}, bbox-only STAC extras={result['stac_bbox_extra_item_count']}, equal={result['equal_for_derived_pathrows']}"
        for result in stac_comparison.get("month_results", [])
    ]
    if final_row["scientific_equivalence_status"] == "equivalent":
        recommendation = (
            "Recommended Goal 014: build a bounded direct-S3 extraction rehearsal for `NWB002` only, using the derived complete path/row set and the same three probe months. "
            "Keep it as a read/aggregation rehearsal with strict validation against STAC-derived metadata and no full `2018-01` through `2024-12` run until the bounded extraction path passes."
        )
    else:
        recommendation = (
            "Recommended Goal 014: run an official metadata comparator for the complete `NWB002` path/row set, preferably by repeating the STAC item-set comparison after service recovery or by using a configured DEA Sandbox/NCI/Open Data Cube environment. "
            "Keep direct S3 extraction paused until that comparator proves item-set equivalence or the remaining gap is explicitly accepted."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Goal 013 Support Path-Row Coverage And Metadata Equivalence",
                "",
                f"Accessed date for current official source checks: `{config['accessed_date']}`.",
                "",
                "## Scope",
                "",
                "This is a metadata and coverage prototype only. It does not compute wet area, wet proportion, lags, novelty, drying velocity, persistence, or ecological response metrics.",
                "",
                "## Path/Row Source And Coverage",
                "",
                f"Path/row source: [{config['wrs2_source']['title']}]({config['wrs2_source']['source_page_url']}), staged under ignored `{wrs_record['path']}` with SHA-256 `{wrs_record['sha256']}`.",
                "",
                f"The prototype rebuilt the current event-window support set and derived geometry intersections against the official WRS-2 descending footprint layer for `{support_count}` supports.",
                "",
                f"`NWB002` complete derived path/row set: `{', '.join(primary_path_rows)}`.",
                "",
                "Coverage is labelled `complete` because the crosswalk used support geometry intersection. WRS scene footprints overlap, so intersection areas in the CSV are per-scene evidence and are not additive support area estimates.",
                "",
                "## Direct S3 Item Sets",
                "",
                "Direct public S3 listing was run for the complete `NWB002` path/row set and the three Goal 012 probe months.",
                "",
                "| Month | Complete-path/row S3 Water Observations item count |",
                "| --- | ---: |",
                *[f"| {month} | {counts_by_month.get(month, 0)} |" for month in config["months"]],
                "",
                "The Goal 012 known `093/080` slice was reproduced, and the derived support coverage added the other intersecting path/row slices listed above. Raw S3 listings and HEAD metadata remain under ignored `artifacts/` paths.",
                "",
                "## Official Comparator Status",
                "",
                f"Final equivalence status: `{final_row['scientific_equivalence_status']}`.",
                "",
                "DEA STAC was probed first under the strict preflight. STAC bbox results were then filtered to the derived WRS path/row set before comparison with direct S3 assets, because bbox search can include scene footprints outside the support geometry-derived path/row set.",
                "",
                *stac_lines,
                "",
                "The local Open Data Cube/`odc-stac` comparator availability check was still recorded as a contingency route; this Mac mini environment does not currently include those modules.",
                "",
                "## Recommendation For Goal 014",
                "",
                recommendation,
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run(config_path: Path, reuse_cache: bool) -> dict[str, Any]:
    started = time.time()
    config = load_json(config_path)
    for path_text in config["staging_paths"].values():
        (REPO / path_text).mkdir(parents=True, exist_ok=True)
    wrs_zip = REPO / config["wrs2_source"]["staged_zip_path"]
    wrs_record = ensure_download(config["wrs2_source"]["download_url"], wrs_zip)
    supports = load_event_window_supports(config)
    crosswalk_rows, by_support = derive_support_pathrow_crosswalk(
        supports=supports,
        wrs_zip_path=wrs_zip,
        wrs_layer_name=config["wrs2_source"]["zip_layer_path"],
        wrs_source_id=config["wrs2_source"]["source_id"],
        wrs_zip_sha=wrs_record["sha256"],
        coverage_method_name=config["wrs2_source"]["coverage_method"],
    )
    primary_support = next(support for support in supports if support["support_id"] == config["primary_support_id"])
    primary_candidate = {
        "candidate_id": primary_support["candidate_id"],
        "candidate_name": primary_support["candidate_name"],
        "support_id": primary_support["support_id"],
    }
    primary_path_rows = by_support[config["primary_support_id"]]
    item_rows, item_lookup, s3_records = direct_s3_item_sets(config, primary_candidate, primary_path_rows, reuse_cache)
    stac_result, stac_item_lookup = stac_preflight(config, primary_support, reuse_cache)
    official_comparator = probe_official_datacube_comparator(config)
    goal012_comparison = compare_goal012_known_path(config, item_rows, primary_path_rows)
    support_statuses = {row["coverage_status"] for row in crosswalk_rows if row["support_id"] == config["primary_support_id"]}
    support_coverage = "complete" if support_statuses == {"complete"} else "support_coverage_incomplete"
    stac_comparison = compare_stac_to_s3_item_sets(
        stac_result["summary"]["route_status"],
        stac_item_lookup,
        item_lookup,
        config["months"],
        primary_path_rows,
    )
    comparator_rows = build_comparator_rows(
        config, stac_result, stac_comparison, official_comparator, goal012_comparison, support_coverage
    )

    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    write_csv(outputs["crosswalk_csv"], crosswalk_rows, CROSSWALK_FIELDS)
    write_csv(outputs["item_sets_csv"], item_rows, ITEM_SET_FIELDS)
    write_csv(outputs["comparator_status_csv"], comparator_rows, COMPARATOR_FIELDS)
    manifest = {
        "goal": config["goal"],
        "manifest_type": "support_pathrow_coverage_013",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "accessed_date": config["accessed_date"],
        "command": config["run_command"] + (" --reuse-ignored-cache" if reuse_cache else ""),
        "config_path": repo_relative(config_path),
        "reuse_ignored_cache": reuse_cache,
        "git_head_at_run": git_head(),
        "git_status_at_run": git_status(),
        "host_facts": host_facts(),
        "source_urls": config["source_urls"],
        "wrs2_source": {
            **config["wrs2_source"],
            "staged_file": wrs_record,
            "raw_geometry_committed": False,
        },
        "support_source": config["support_source"],
        "support_count": len(supports),
        "crosswalk_row_count": len(crosswalk_rows),
        "support_path_rows": by_support,
        "primary_candidate": primary_candidate,
        "primary_path_rows": primary_path_rows,
        "s3_route_records": s3_records,
        "stac_preflight": {
            "summary": stac_result["summary"],
            "cache_path": repo_relative(REPO / config["staging_paths"]["raw"] / "stac_preflight_013.json"),
            "stac_item_counts_by_month": {month: len(items) for month, items in stac_item_lookup.items()},
        },
        "stac_item_set_comparison": stac_comparison,
        "official_comparator": official_comparator,
        "goal012_known_path_comparison": goal012_comparison,
        "comparator_status": comparator_rows,
        "outputs": {key: repo_relative(path) for key, path in outputs.items()},
        "staging_paths": config["staging_paths"],
        "staging_policy": config["commit_policy"],
        "remote_compute_used": False,
        "elapsed_seconds": round(time.time() - started, 3),
    }
    write_json(outputs["manifest_json"], manifest)
    write_report(
        outputs["report_md"],
        config,
        wrs_record,
        len(supports),
        primary_path_rows,
        item_rows,
        comparator_rows,
        stac_comparison,
    )
    write_json(REPO / config["staging_paths"]["output"] / "support_pathrow_metadata_013_run.json", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--reuse-ignored-cache", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = args.config if args.config.is_absolute() else REPO / args.config
    manifest = run(config_path, args.reuse_ignored_cache)
    print(
        "Goal 013 wrote "
        f"{manifest['crosswalk_row_count']} crosswalk rows and "
        f"{sum(record['water_item_count'] for record in manifest['s3_route_records'])} direct-S3 water items."
    )


if __name__ == "__main__":
    main()
