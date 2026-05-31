#!/usr/bin/env python3
"""Goal 011 bounded acquisition-route probe and STAC-call estimator."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import platform
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
DEA_PUBLIC_BUCKET_HTTPS = "https://dea-public-data.s3.ap-southeast-2.amazonaws.com"
DEA_PUBLIC_BUCKET = "dea-public-data"
DEFAULT_SERIES = REPO / "docs" / "event_window_hydrology_series_2018_2024.csv"
DEFAULT_SETTINGS = REPO / "settings" / "remote_full_window_hydrology_009.json"
DEFAULT_S3_HREF = (
    "s3://dea-public-data/derivative/ga_ls_wo_3/1-6-0/093/080/2022/11/03/"
    "ga_ls_wo_3_093080_2022-11-03_final_water.tif"
)
DEFAULT_S3_PREFIX = "derivative/ga_ls_wo_3/1-6-0/093/080/2022/11/"
DEFAULT_STAC_BBOX = [147.47, -29.79, 147.49, -29.77]
DEFAULT_STAC_MONTH = "2022-11"


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_series_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def estimate_query_patterns(rows: list[dict[str, str]], max_attempts: int = 3) -> list[dict[str, Any]]:
    support_month = {(row["support_id"], row["month"]) for row in rows}
    candidate_month = {(row["candidate_id"], row["month"]) for row in rows}
    month_set = {row["month"] for row in rows}
    status_quo = len(support_month)
    patterns = [
        {
            "workflow_unit": "support_month_status_quo",
            "estimated_live_stac_searches": status_quo,
            "cache_key": "collection|month|support_bbox_hash",
            "cache_opportunity": "baseline only; avoids repeat calls only across reruns, not within one full-window run",
        },
        {
            "workflow_unit": "candidate_month_cache",
            "estimated_live_stac_searches": len(candidate_month),
            "cache_key": "collection|month|candidate_bbox_hash",
            "cache_opportunity": "query each candidate-month once, then filter cached items to child supports",
        },
        {
            "workflow_unit": "month_support_set_cache",
            "estimated_live_stac_searches": len(month_set),
            "cache_key": "collection|month|support_set_bbox_hash",
            "cache_opportunity": "query one unioned support-set/month cache, then filter cached items to every support",
        },
        {
            "workflow_unit": "direct_s3_or_inventory_index",
            "estimated_live_stac_searches": 0,
            "cache_key": "collection|path_row|month|maturity",
            "cache_opportunity": "avoid live STAC search if a path/row or inventory index can be proven complete",
        },
    ]
    for pattern in patterns:
        count = int(pattern["estimated_live_stac_searches"])
        pattern["estimated_max_http_attempts"] = count * max_attempts
        pattern["search_reduction_percent"] = round((1 - count / status_quo) * 100, 1) if status_quo else 0.0
    return patterns


def s3_href_to_https(href: str) -> str:
    parsed = urllib.parse.urlparse(href)
    if parsed.scheme != "s3" or parsed.netloc != DEA_PUBLIC_BUCKET:
        raise ValueError(f"expected s3://{DEA_PUBLIC_BUCKET}/... href, got {href}")
    return f"{DEA_PUBLIC_BUCKET_HTTPS}/{parsed.path.lstrip('/')}"


def s3_list_url(prefix: str, max_keys: int = 5) -> str:
    bounded_max_keys = max(1, min(int(max_keys), 25))
    query = urllib.parse.urlencode({"list-type": "2", "prefix": prefix, "max-keys": bounded_max_keys})
    return f"{DEA_PUBLIC_BUCKET_HTTPS}/?{query}"


def month_range(month: str) -> tuple[str, str]:
    year, month_number = map(int, month.split("-"))
    start = dt.datetime(year, month_number, 1, tzinfo=dt.UTC)
    if month_number == 12:
        stop = dt.datetime(year + 1, 1, 1, tzinfo=dt.UTC)
    else:
        stop = dt.datetime(year, month_number + 1, 1, tzinfo=dt.UTC)
    return start.strftime("%Y-%m-%dT%H:%M:%SZ"), stop.strftime("%Y-%m-%dT%H:%M:%SZ")


def url_request(method: str, url: str, timeout: int = 30, payload: bytes | None = None) -> dict[str, Any]:
    request = urllib.request.Request(url, data=payload, method=method)
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(512_000)
            return {
                "ok": 200 <= response.status < 300,
                "status_code": response.status,
                "elapsed_seconds": round(time.time() - started, 3),
                "content_length": response.headers.get("Content-Length", ""),
                "content_type": response.headers.get("Content-Type", ""),
                "body": body,
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(512_000)
        return {
            "ok": False,
            "status_code": exc.code,
            "elapsed_seconds": round(time.time() - started, 3),
            "content_length": exc.headers.get("Content-Length", "") if exc.headers else "",
            "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
            "body": body,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "status_code": None,
            "elapsed_seconds": round(time.time() - started, 3),
            "content_length": "",
            "content_type": "",
            "body": b"",
            "error": f"{type(exc).__name__}: {exc}",
        }


def compact_response(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "body"}


def probe_s3_prefix(prefix: str, max_keys: int, timeout: int) -> dict[str, Any]:
    url = s3_list_url(prefix, max_keys=max_keys)
    result = url_request("GET", url, timeout=timeout)
    summary = compact_response(result)
    summary["url"] = url
    summary["prefix"] = prefix
    summary["max_keys"] = max_keys
    if result["body"]:
        try:
            root = ET.fromstring(result["body"])
            ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
            key_count = root.findtext("s3:KeyCount", default="", namespaces=ns) or root.findtext("KeyCount", default="")
            keys = [item.text for item in root.findall(".//s3:Key", ns)] or [item.text for item in root.findall(".//Key")]
            summary["key_count"] = int(key_count) if key_count else len(keys)
            summary["sample_keys"] = keys[:max_keys]
        except Exception as exc:
            summary["parse_error"] = f"{type(exc).__name__}: {exc}"
    return summary


def probe_s3_head(href: str, timeout: int) -> dict[str, Any]:
    url = s3_href_to_https(href)
    result = url_request("HEAD", url, timeout=timeout)
    summary = compact_response(result)
    summary["url"] = url
    summary["href"] = href
    return summary


def probe_stac_search(settings: dict[str, Any], month: str, bbox: list[float], timeout: int) -> dict[str, Any]:
    start, stop = month_range(month)
    payload = {
        "collections": [settings["dea_collection"]],
        "bbox": bbox,
        "datetime": f"{start}/{stop}",
        "limit": 1,
    }
    body = json.dumps(payload).encode("utf-8")
    result = url_request("POST", settings["dea_stac_search_url"], timeout=timeout, payload=body)
    summary = compact_response(result)
    summary["url"] = settings["dea_stac_search_url"]
    summary["month"] = month
    summary["bbox"] = bbox
    summary["payload"] = payload
    if result["body"] and result["ok"]:
        try:
            response = json.loads(result["body"].decode("utf-8"))
            summary["feature_count"] = len(response.get("features", []))
        except Exception as exc:
            summary["parse_error"] = f"{type(exc).__name__}: {exc}"
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", default=str(DEFAULT_SERIES), help="Goal 009 support/month CSV.")
    parser.add_argument("--settings", default=str(DEFAULT_SETTINGS), help="Goal 009 settings JSON.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--host-label", default=socket.gethostname(), help="Short host label for provenance.")
    parser.add_argument("--s3-href", default=DEFAULT_S3_HREF, help="Known DEA Water Observations S3 href to HEAD.")
    parser.add_argument("--s3-prefix", default=DEFAULT_S3_PREFIX, help="Known DEA Water Observations S3 prefix to list.")
    parser.add_argument("--s3-max-keys", type=int, default=5, help="Bounded number of S3 keys to request.")
    parser.add_argument("--stac-month", default=DEFAULT_STAC_MONTH, help="YYYY-MM month for a one-item STAC probe.")
    parser.add_argument("--stac-bbox", nargs=4, type=float, default=DEFAULT_STAC_BBOX, help="min lon/lat/max lon/lat.")
    parser.add_argument("--timeout", type=int, default=30, help="Network timeout in seconds for each probe.")
    parser.add_argument("--skip-live", action="store_true", help="Only estimate query patterns; skip live URL probes.")
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    started = time.time()
    series_path = Path(args.series)
    if not series_path.is_absolute():
        series_path = REPO / series_path
    settings_path = Path(args.settings)
    if not settings_path.is_absolute():
        settings_path = REPO / settings_path
    settings = load_json(settings_path)
    rows = load_series_rows(series_path)
    estimates = estimate_query_patterns(rows, max_attempts=int(settings.get("retry_policy", {}).get("max_attempts", 3)))
    live_probes: dict[str, Any] = {}
    if not args.skip_live:
        live_probes = {
            "s3_prefix_list": probe_s3_prefix(args.s3_prefix, args.s3_max_keys, args.timeout),
            "s3_known_cog_head": probe_s3_head(args.s3_href, args.timeout),
            "stac_one_item_search": probe_stac_search(settings, args.stac_month, list(args.stac_bbox), args.timeout),
        }
    manifest = {
        "goal": "011-hydrology-acquisition-route-redesign",
        "manifest_type": "hydrology_acquisition_route_probe_011",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "host_label": args.host_label,
        "host_facts": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": sys.version,
        },
        "series_path": repo_relative(series_path),
        "settings_path": repo_relative(settings_path),
        "row_count": len(rows),
        "query_pattern_estimates": estimates,
        "live_probe_limits": {
            "s3_max_keys": args.s3_max_keys,
            "stac_limit": 1,
            "timeout_seconds": args.timeout,
            "raw_downloads": False,
            "full_stac_dump": False,
        },
        "live_probes": live_probes,
        "elapsed_seconds": round(time.time() - started, 3),
    }
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = REPO / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
