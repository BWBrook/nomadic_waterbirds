#!/usr/bin/env python3
"""Goal 012 bounded STAC-cache and S3 metadata acquisition prototype."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import platform
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO / "settings" / "hydrology_metadata_cache_s3_012.json"
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
ITEM_SET_FIELDS = [
    "candidate_id",
    "candidate_name",
    "support_id",
    "month",
    "route",
    "path_or_bbox_key",
    "item_count",
    "item_id_hash",
    "asset_key_hash",
    "route_status",
    "cache_path_status",
    "item_id_sample",
    "asset_key_sample",
    "caveat",
]
ROUTE_COMPARISON_FIELDS = [
    "route",
    "scientific_equivalence_status",
    "stac_dependence",
    "s3_or_object_store_dependence",
    "failure_mode",
    "implementation_cost",
    "recommendation",
    "evidence",
]


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cached_json(path: Path, reuse_cache: bool) -> dict[str, Any] | None:
    if not reuse_cache or not path.exists():
        return None
    return load_json(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def stable_hash(values: list[Any]) -> str:
    payload = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def bbox_hash(bbox: list[float]) -> str:
    rounded = [round(float(value), 8) for value in bbox]
    return stable_hash(rounded)[:16]


def candidate_month_cache_key(collection: str, candidate_id: str, month: str, bbox: list[float]) -> str:
    return f"{collection}|{candidate_id}|{month}|{bbox_hash(bbox)}"


def s3_prefix_for_path_row_month(collection: str, version: str, path: str, row: str, month: str) -> str:
    year, month_number = month.split("-")
    return f"derivative/{collection}/{version}/{path}/{row}/{year}/{month_number}/"


def s3_list_url(base_url: str, prefix: str, max_keys: int, continuation_token: str | None = None) -> str:
    query: dict[str, Any] = {"list-type": "2", "prefix": prefix, "max-keys": max(1, int(max_keys))}
    if continuation_token:
        query["continuation-token"] = continuation_token
    return f"{base_url}/?{urllib.parse.urlencode(query)}"


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


def url_request(method: str, url: str, timeout: int, payload: bytes | None = None) -> dict[str, Any]:
    request = urllib.request.Request(url, data=payload, method=method)
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(2_000_000)
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
        body = exc.read(512_000)
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


def classify_stac_preflight(results: list[dict[str, Any]]) -> dict[str, Any]:
    failure_months = [str(result.get("month", "")) for result in results if result.get("status_code") != 200]
    if results and not failure_months:
        return {
            "route_status": "available",
            "failure_months": [],
            "reason": "All configured probe months returned HTTP 200 under the strict preflight.",
        }
    return {
        "route_status": "unavailable_service_unstable",
        "failure_months": failure_months,
        "reason": "At least one configured probe month failed the strict STAC preflight; cache fill was not launched.",
    }


def item_id_from_s3_water_key(key: str) -> str:
    name = Path(key).name
    return re.sub(r"_water\.tif$", "", name)


def s3_water_items(keys: list[str]) -> list[dict[str, str]]:
    items = []
    for key in sorted(keys):
        if key.endswith("_water.tif"):
            items.append({"item_id": item_id_from_s3_water_key(key), "asset_key": key})
    return items


def stac_items(features: list[dict[str, Any]], bucket: str) -> list[dict[str, str]]:
    items = []
    for feature in features:
        href = feature.get("assets", {}).get("water", {}).get("href", "")
        asset_key = href
        if href.startswith(f"s3://{bucket}/"):
            asset_key = href.removeprefix(f"s3://{bucket}/")
        elif href.startswith("https://"):
            parsed = urllib.parse.urlparse(href)
            asset_key = parsed.path.lstrip("/")
        if not asset_key:
            continue
        items.append({"item_id": str(feature.get("id", "")), "asset_key": asset_key})
    return sorted(items, key=lambda item: (item["asset_key"], item["item_id"]))


def item_set_summary(
    candidate_id: str,
    month: str,
    route: str,
    path_or_bbox_key: str,
    items: list[dict[str, str]],
    cache_path_status: str,
    route_status: str,
    candidate_name: str = "",
    support_id: str = "",
    caveat: str = "",
) -> dict[str, Any]:
    item_ids = sorted(item.get("item_id", "") for item in items)
    asset_keys = sorted(item.get("asset_key", "") for item in items)
    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "support_id": support_id,
        "month": month,
        "route": route,
        "path_or_bbox_key": path_or_bbox_key,
        "item_count": len(items),
        "item_id_hash": stable_hash(item_ids) if item_ids else "",
        "asset_key_hash": stable_hash(asset_keys) if asset_keys else "",
        "route_status": route_status,
        "cache_path_status": cache_path_status,
        "item_id_sample": ";".join(item_ids[:3]),
        "asset_key_sample": ";".join(asset_keys[:3]),
        "caveat": caveat,
    }


def blocked_raw_extensions(paths: list[str]) -> list[str]:
    return [path for path in paths if Path(path).suffix.lower() in BLOCKED_RAW_EXTENSIONS]


def ensure_staging(config: dict[str, Any]) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for key, raw in config["staging_paths"].items():
        path = REPO / raw
        path.mkdir(parents=True, exist_ok=True)
        paths[key] = path
    return paths


def run_stac_preflight(
    config: dict[str, Any], raw_dir: Path, reuse_cache: bool = False
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cache_path = raw_dir / "stac_preflight_012.json"
    cached = load_cached_json(cache_path, reuse_cache)
    if cached is not None:
        results = cached.get("results", [])
        return results, classify_stac_preflight(results)
    candidate = config["candidate"]
    preflight = config["stac_preflight"]
    results: list[dict[str, Any]] = []
    for month_spec in config["months"]:
        month = month_spec["month"]
        payload = stac_payload(config["dea_collection"], candidate["candidate_bbox_wgs84"], month, preflight["limit"])
        result = url_request(
            "POST",
            config["dea_stac_search_url"],
            int(preflight["timeout_seconds"]),
            payload=json.dumps(payload).encode("utf-8"),
        )
        record = {
            "month": month,
            "period": month_spec.get("period", ""),
            "payload": payload,
            **compact_response(result),
        }
        if result["ok"] and result["body"]:
            try:
                response = json.loads(result["body"].decode("utf-8"))
                record["feature_count"] = len(response.get("features", []))
            except Exception as exc:
                record["parse_error"] = f"{type(exc).__name__}: {exc}"
        results.append(record)
    write_json(cache_path, {"results": results})
    return results, classify_stac_preflight(results)


def fill_stac_cache_if_available(
    config: dict[str, Any], raw_dir: Path, preflight_status: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, str]]]]:
    if preflight_status["route_status"] != "available":
        return [], {}
    candidate = config["candidate"]
    cache_records: list[dict[str, Any]] = []
    items_by_month: dict[str, list[dict[str, str]]] = {}
    for month_spec in config["months"]:
        month = month_spec["month"]
        cache_key = candidate_month_cache_key(
            config["dea_collection"], candidate["candidate_id"], month, candidate["candidate_bbox_wgs84"]
        )
        payload = stac_payload(config["dea_collection"], candidate["candidate_bbox_wgs84"], month, 100)
        result = url_request(
            "POST",
            config["dea_stac_search_url"],
            int(config["stac_preflight"]["timeout_seconds"]),
            payload=json.dumps(payload).encode("utf-8"),
        )
        cache_path = raw_dir / f"stac_cache_{candidate['candidate_id']}_{month}.json"
        record = {
            "month": month,
            "cache_key": cache_key,
            "cache_path": repo_relative(cache_path),
            "payload": payload,
            **compact_response(result),
        }
        if result["ok"] and result["body"]:
            try:
                response = json.loads(result["body"].decode("utf-8"))
                write_json(cache_path, response)
                features = response.get("features", [])
                items_by_month[month] = stac_items(features, config["s3"]["bucket"])
                record["feature_count"] = len(features)
                record["cache_path_status"] = "ignored_raw_cache_written"
            except Exception as exc:
                record["parse_error"] = f"{type(exc).__name__}: {exc}"
                record["cache_path_status"] = "not_written_parse_error"
        else:
            record["cache_path_status"] = "not_written_request_failed"
        cache_records.append(record)
    return cache_records, items_by_month


def parse_s3_listing(body: bytes) -> dict[str, Any]:
    root = ET.fromstring(body)
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    keys = [node.text for node in root.findall(".//s3:Key", ns) if node.text]
    if not keys:
        keys = [node.text for node in root.findall(".//Key") if node.text]
    truncated_text = root.findtext("s3:IsTruncated", default="", namespaces=ns) or root.findtext(
        "IsTruncated", default="false"
    )
    next_token = root.findtext("s3:NextContinuationToken", default="", namespaces=ns) or root.findtext(
        "NextContinuationToken", default=""
    )
    return {"keys": keys, "is_truncated": truncated_text.lower() == "true", "next_token": next_token}


def list_s3_prefix(config: dict[str, Any], prefix: str, raw_path: Path, reuse_cache: bool = False) -> dict[str, Any]:
    cached = load_cached_json(raw_path, reuse_cache)
    if cached is not None:
        return cached
    s3 = config["s3"]
    all_keys: list[str] = []
    pages: list[dict[str, Any]] = []
    continuation_token: str | None = None
    for page_number in range(1, int(s3["max_pages_per_prefix"]) + 1):
        url = s3_list_url(s3["base_url"], prefix, int(s3["list_max_keys"]), continuation_token)
        result = url_request("GET", url, int(config["stac_preflight"]["timeout_seconds"]))
        page = {"page_number": page_number, "url": url, **compact_response(result)}
        if result["ok"] and result["body"]:
            try:
                parsed = parse_s3_listing(result["body"])
                page.update(parsed)
                all_keys.extend(parsed["keys"])
                continuation_token = parsed["next_token"] or None
                pages.append(page)
                if not parsed["is_truncated"] or not continuation_token:
                    break
                continue
            except Exception as exc:
                page["parse_error"] = f"{type(exc).__name__}: {exc}"
        pages.append(page)
        break
    payload = {"prefix": prefix, "keys": all_keys, "pages": pages}
    write_json(raw_path, payload)
    return payload


def head_s3_key(config: dict[str, Any], key: str) -> dict[str, Any]:
    url = f"{config['s3']['base_url']}/{key}"
    result = url_request("HEAD", url, int(config["stac_preflight"]["timeout_seconds"]))
    return {"key": key, "url": url, **compact_response(result)}


def run_s3_route(
    config: dict[str, Any], raw_dir: Path, intermediate_dir: Path, reuse_cache: bool = False
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, str]]]]:
    records: list[dict[str, Any]] = []
    items_by_month: dict[str, list[dict[str, str]]] = {}
    for month_spec in config["months"]:
        month = month_spec["month"]
        month_items: list[dict[str, str]] = []
        month_records: list[dict[str, Any]] = []
        for path_row in config["s3"]["path_rows"]:
            prefix = s3_prefix_for_path_row_month(
                config["dea_collection"],
                config["dea_product_version"],
                path_row["path"],
                path_row["row"],
                month,
            )
            raw_path = raw_dir / f"s3_listing_{config['candidate']['candidate_id']}_{month}_{path_row['path']}{path_row['row']}.json"
            listing = list_s3_prefix(config, prefix, raw_path, reuse_cache=reuse_cache)
            water_items = s3_water_items(listing["keys"])
            head_limit = int(config["s3"]["head_limit_per_month"])
            head_path = intermediate_dir / f"s3_head_{config['candidate']['candidate_id']}_{month}_{path_row['path']}{path_row['row']}.json"
            cached_head = load_cached_json(head_path, reuse_cache)
            if cached_head is not None:
                head_records = cached_head.get("head_records", [])
            else:
                head_records = [head_s3_key(config, item["asset_key"]) for item in water_items[:head_limit]]
                write_json(head_path, {"month": month, "prefix": prefix, "head_records": head_records})
            month_items.extend(water_items)
            month_records.append(
                {
                    "month": month,
                    "path_row": f"{path_row['path']}/{path_row['row']}",
                    "prefix": prefix,
                    "listing_path": repo_relative(raw_path),
                    "head_path": repo_relative(head_path),
                    "key_count": len(listing["keys"]),
                    "water_item_count": len(water_items),
                    "head_count": len(head_records),
                    "listing_status_code": listing["pages"][0].get("status_code") if listing["pages"] else None,
                    "all_head_ok": bool(head_records) and all(record.get("status_code") == 200 for record in head_records),
                    "listing_page_count": len(listing["pages"]),
                }
            )
        items_by_month[month] = sorted(month_items, key=lambda item: (item["asset_key"], item["item_id"]))
        records.extend(month_records)
    return records, items_by_month


def compare_item_sets(
    config: dict[str, Any],
    stac_items_by_month: dict[str, list[dict[str, str]]],
    s3_items_by_month: dict[str, list[dict[str, str]]],
    stac_status: dict[str, Any],
) -> list[dict[str, Any]]:
    comparisons = []
    for month_spec in config["months"]:
        month = month_spec["month"]
        s3_items_for_month = s3_items_by_month.get(month, [])
        stac_items_for_month = stac_items_by_month.get(month, [])
        s3_asset_hash = stable_hash(sorted(item["asset_key"] for item in s3_items_for_month)) if s3_items_for_month else ""
        stac_asset_hash = stable_hash(sorted(item["asset_key"] for item in stac_items_for_month)) if stac_items_for_month else ""
        if stac_status["route_status"] != "available":
            status = "comparison_blocked_stac_unavailable"
            caveat = "S3 route viability only; scientific equivalence cannot be proven without STAC or another official metadata comparator."
        elif s3_asset_hash and stac_asset_hash and s3_asset_hash == stac_asset_hash:
            status = "asset_key_match"
            caveat = "S3 and STAC water asset keys match for this bounded candidate/month."
        else:
            status = "asset_key_mismatch_or_incomplete"
            caveat = "Both routes produced metadata, but item sets did not exactly match or were incomplete."
        comparisons.append(
            {
                "month": month,
                "status": status,
                "s3_item_count": len(s3_items_for_month),
                "stac_item_count": len(stac_items_for_month),
                "s3_asset_key_hash": s3_asset_hash,
                "stac_asset_key_hash": stac_asset_hash,
                "caveat": caveat,
            }
        )
    return comparisons


def build_item_set_rows(
    config: dict[str, Any],
    stac_status: dict[str, Any],
    stac_items_by_month: dict[str, list[dict[str, str]]],
    s3_items_by_month: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    candidate = config["candidate"]
    rows = []
    for month_spec in config["months"]:
        month = month_spec["month"]
        bbox_key = candidate_month_cache_key(
            config["dea_collection"], candidate["candidate_id"], month, candidate["candidate_bbox_wgs84"]
        )
        rows.append(
            item_set_summary(
                candidate["candidate_id"],
                month,
                "candidate_month_stac_cache",
                bbox_key,
                stac_items_by_month.get(month, []),
                "ignored_raw_cache_written" if stac_items_by_month.get(month) else "not_written",
                stac_status["route_status"],
                candidate_name=candidate["candidate_name"],
                support_id=candidate["support_id"],
                caveat=stac_status["reason"],
            )
        )
        s3_path_key = ";".join(f"{item['path']}/{item['row']}" for item in config["s3"]["path_rows"])
        rows.append(
            item_set_summary(
                candidate["candidate_id"],
                month,
                "direct_s3_path_row",
                s3_path_key,
                s3_items_by_month.get(month, []),
                "ignored_raw_listing_and_head_metadata",
                "available" if s3_items_by_month.get(month) else "no_water_items_found",
                candidate_name=candidate["candidate_name"],
                support_id=candidate["support_id"],
                caveat="Path-row/month object listing only; not yet a complete support-intersection inventory.",
            )
        )
    return rows


def build_route_comparison_rows(
    stac_status: dict[str, Any],
    s3_records: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
) -> list[dict[str, str]]:
    s3_available_months = sum(1 for record in s3_records if record.get("water_item_count", 0) > 0)
    all_s3_heads_ok = bool(s3_records) and all(record.get("all_head_ok") for record in s3_records if record.get("water_item_count", 0))
    comparison_statuses = sorted({comparison["status"] for comparison in comparisons})
    return [
        {
            "route": "candidate_month_stac_cache",
            "scientific_equivalence_status": "not_evaluable_now"
            if stac_status["route_status"] != "available"
            else "bounded_metadata_available_needs_s3_comparison",
            "stac_dependence": "strict_preflight_and_cache_fill",
            "s3_or_object_store_dependence": "COG assets after metadata discovery",
            "failure_mode": stac_status["reason"],
            "implementation_cost": "moderate",
            "recommendation": "Do not launch full extraction until endpoint preflight passes; keep cache code path ready.",
            "evidence": f"preflight_status={stac_status['route_status']}; failure_months={';'.join(stac_status['failure_months'])}",
        },
        {
            "route": "direct_s3_path_row_index",
            "scientific_equivalence_status": "technical_viability_not_equivalence",
            "stac_dependence": "none_for_known_path_row_month_listing",
            "s3_or_object_store_dependence": "public S3 prefix listing and COG HEAD metadata",
            "failure_mode": "path-row coverage may be incomplete for full candidate support",
            "implementation_cost": "moderate",
            "recommendation": "Promote to Goal 013 prototype only if path-row coverage can be derived for every support bbox.",
            "evidence": f"s3_month_records_with_water_items={s3_available_months}; all_head_ok={all_s3_heads_ok}",
        },
        {
            "route": "item_set_comparison",
            "scientific_equivalence_status": "blocked" if "comparison_blocked_stac_unavailable" in comparison_statuses else "bounded_comparison_available",
            "stac_dependence": "requires STAC or datacube comparator",
            "s3_or_object_store_dependence": "uses direct S3 item keys",
            "failure_mode": "STAC unavailable blocks equivalence proof" if "comparison_blocked_stac_unavailable" in comparison_statuses else "item-set mismatch risk",
            "implementation_cost": "low_after_routes_exist",
            "recommendation": "Repeat comparison when STAC or ODC metadata is available.",
            "evidence": "comparison_statuses=" + ";".join(comparison_statuses),
        },
        {
            "route": "odc_nci_or_dea_sandbox",
            "scientific_equivalence_status": "deferred_official_comparator",
            "stac_dependence": "none in repo loop; backend indexed metadata",
            "s3_or_object_store_dependence": "environment-dependent",
            "failure_mode": "requires account/environment setup",
            "implementation_cost": "high",
            "recommendation": "Use if STAC remains unavailable and S3 path-row coverage cannot be proven locally.",
            "evidence": "Goal 011 official-source review; no Goal 012 ODC run requested or needed.",
        },
    ]


def render_report(config: dict[str, Any], manifest: dict[str, Any], route_rows: list[dict[str, str]]) -> str:
    candidate = config["candidate"]
    months = ", ".join(month["month"] for month in config["months"])
    stac_status = manifest["stac_preflight"]["status"]["route_status"]
    s3_counts = ", ".join(
        f"{row['month']}={row['item_count']}"
        for row in manifest["item_sets"]
        if row["route"] == "direct_s3_path_row"
    )
    comparison_statuses = ", ".join(f"{item['month']}={item['status']}" for item in manifest["item_set_comparisons"])
    recommendation = next(row["recommendation"] for row in route_rows if row["route"] == "direct_s3_path_row_index")
    return f"""# Goal 012 Hydrology Metadata Cache And S3 Prototype

Accessed date for current official source checks: `{config['accessed_date']}`.

## Scope

This is a metadata-acquisition prototype only. It does not compute wet area,
wet proportion, lags, novelty, drying velocity, persistence, or ecological
response metrics.

## Official Source Checks

- [DEA Water Observations (Landsat)](https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/?tab=overview)
  remains the primary product target.
- [DEA AWS/S3 access](https://knowledge.dea.ga.gov.au/guides/setup/AWS/data_and_metadata/)
  documents the public bucket, public inventory, and no-sign S3 access route.
- [DEA STAC guidance](https://knowledge.dea.ga.gov.au/notebooks/How_to_guides/Downloading_data_with_STAC/)
  documents STAC metadata search and cloud-data streaming.
- [DEA FAQ download guidance](https://knowledge.dea.ga.gov.au/guides/about/faq/)
  supports direct S3 download when exact paths are known.

## Candidate And Months

Candidate: `{candidate['candidate_id']}` {candidate['candidate_name']}, support
`{candidate['support_id']}`.

Months: `{months}`.

Rationale: {candidate['selection_rationale']}

The candidate-month STAC cache key uses
`collection|candidate_id|month|candidate_bbox_hash`, with the bbox sourced from
Goal 009 blocked-row context. Direct S3 discovery used the known Narran
`093/080` path-row from prior smoke and Goal 011 evidence.

## Prototype Results

- STAC preflight status: `{stac_status}`.
- Direct S3 route item counts by month: {s3_counts}.
- Item-set comparison status by month: {comparison_statuses}.

STAC cache fill was launched only if every configured month passed the strict
preflight. When the preflight failed, the script wrote no STAC item cache and
continued with S3 metadata only.

Direct S3 discovery listed bounded path-row/month prefixes and used `HEAD`
metadata for discovered Water Observations COG keys. Raw listings and HEAD
metadata were written only under ignored `artifacts/` paths.

## Decision

The direct S3 route is technically viable for the known Narran `093/080`
path-row/month prefixes, but it is not yet scientifically equivalent for the
whole Narran support because path-row coverage has not been proven from the
support bbox and STAC/ODC comparison was blocked or incomplete.

The cached STAC route remains the nearest scientifically equivalent design,
but should not carry a full extraction until the strict preflight passes.

## Recommended Goal 013

Recommended Goal 013: build a bounded support-to-path-row discovery and
metadata-equivalence prototype for NWB002. It should derive all Landsat
path/row candidates intersecting the support bbox, run S3 listings for the
three probe months, and compare those keys against STAC or an official ODC/NCI
metadata query when available. If STAC is still unavailable, use ODC/NCI or DEA
Sandbox as the official comparator before promoting direct S3 extraction.

Current route recommendation from the comparison table: {recommendation}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Goal 012 prototype configuration JSON.")
    parser.add_argument(
        "--reuse-ignored-cache",
        action="store_true",
        help="Reuse existing ignored raw/intermediate metadata caches instead of re-querying live services.",
    )
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    config = load_json(config_path)
    paths = ensure_staging(config)
    started = time.time()

    stac_results, stac_status = run_stac_preflight(config, paths["raw"], reuse_cache=args.reuse_ignored_cache)
    stac_cache_records, stac_items_by_month = fill_stac_cache_if_available(config, paths["raw"], stac_status)
    s3_records, s3_items_by_month = run_s3_route(
        config, paths["raw"], paths["intermediate"], reuse_cache=args.reuse_ignored_cache
    )
    comparisons = compare_item_sets(config, stac_items_by_month, s3_items_by_month, stac_status)
    item_rows = build_item_set_rows(config, stac_status, stac_items_by_month, s3_items_by_month)
    route_rows = build_route_comparison_rows(stac_status, s3_records, comparisons)

    output_paths = {name: REPO / path for name, path in config["outputs"].items()}
    manifest = {
        "goal": config["goal"],
        "manifest_type": "hydrology_metadata_cache_s3_012",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "accessed_date": config["accessed_date"],
        "command": config["run_command"],
        "config_path": repo_relative(config_path),
        "reuse_ignored_cache": args.reuse_ignored_cache,
        "host_facts": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": sys.version,
        },
        "candidate": config["candidate"],
        "months": config["months"],
        "source_urls": config["source_urls"],
        "staging_paths": {key: repo_relative(value) for key, value in paths.items()},
        "staging_policy": config["commit_policy"],
        "stac_preflight": {
            "threshold": config["stac_preflight"],
            "results": stac_results,
            "status": stac_status,
        },
        "stac_cache_records": stac_cache_records,
        "s3_route_records": s3_records,
        "item_sets": item_rows,
        "item_set_comparisons": comparisons,
        "route_comparison": route_rows,
        "outputs": {key: repo_relative(value) for key, value in output_paths.items()},
        "elapsed_seconds": round(time.time() - started, 3),
    }
    write_csv(output_paths["item_sets_csv"], item_rows, ITEM_SET_FIELDS)
    write_csv(output_paths["route_comparison_csv"], route_rows, ROUTE_COMPARISON_FIELDS)
    write_json(output_paths["manifest_json"], manifest)
    output_paths["report_md"].write_text(render_report(config, manifest, route_rows), encoding="utf-8")
    write_json(paths["output"] / "hydrology_metadata_cache_s3_012_run.json", manifest)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
