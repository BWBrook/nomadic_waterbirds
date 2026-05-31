#!/usr/bin/env python3
"""Probe DEA STAC availability with Goal 009 retry classification."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import socket
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from osgeo import gdal


SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[0]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from official_support_hydrology_005 import (  # noqa: E402
    RetryExhaustedError,
    classify_remote_failure,
    load_json,
    normalise_retry_policy,
    reset_retry_audit_log,
    retry_audit_events,
    stac_search,
    write_json,
)


DEFAULT_MONTHS = ["2018-01", "2022-11", "2024-12"]
DEFAULT_PROBE_BBOX = (147.47, 147.49, -29.79, -29.77)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(REPO / "settings" / "remote_full_window_hydrology_009.json"),
        help="Goal 009 event-window config path.",
    )
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--host-label", default=socket.gethostname(), help="Short label for this probe host.")
    parser.add_argument("--months", nargs="*", default=DEFAULT_MONTHS, help="YYYY-MM probe months.")
    return parser.parse_args()


def endpoint_status(results: list[dict[str, Any]]) -> str:
    if results and all(result["status"] == "available" for result in results):
        return "available"
    status_codes = {result.get("status_code") for result in results}
    failure_classes = {result.get("failure_class") for result in results}
    if status_codes == {503} and failure_classes == {"transient_endpoint_failure"}:
        return "service_unavailable_503"
    if "transient_endpoint_failure" in failure_classes:
        return "transient_endpoint_failure"
    return "not_available"


def run() -> int:
    args = parse_args()
    start = time.time()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    config = load_json(config_path)
    reset_retry_audit_log()
    results: list[dict[str, Any]] = []
    for month in args.months:
        before_events = len(retry_audit_events())
        month_started = dt.datetime.now(dt.UTC).isoformat()
        try:
            payload = stac_search(config, DEFAULT_PROBE_BBOX, month)
            status = {
                "month": month,
                "started_at_utc": month_started,
                "finished_at_utc": dt.datetime.now(dt.UTC).isoformat(),
                "status": "available",
                "feature_count": len(payload.get("features", [])),
                "failure_class": "",
                "status_code": None,
                "caveat": "Endpoint probe only; tiny Narran AOI is not a wetland support mask.",
            }
        except RetryExhaustedError as exc:
            event = exc.event
            status = {
                "month": month,
                "started_at_utc": month_started,
                "finished_at_utc": dt.datetime.now(dt.UTC).isoformat(),
                "status": "blocked_after_retry",
                "feature_count": "",
                "failure_class": event["failure_class"],
                "status_code": event["status_code"],
                "attempt_count": event["attempt_count"],
                "caveat": str(exc),
            }
        except Exception as exc:
            classification = classify_remote_failure(exc, "dea_stac_search")
            status = {
                "month": month,
                "started_at_utc": month_started,
                "finished_at_utc": dt.datetime.now(dt.UTC).isoformat(),
                "status": "blocked_unclassified" if classification["transient"] else "blocked_deterministic",
                "feature_count": "",
                "failure_class": classification["failure_class"],
                "status_code": classification["status_code"],
                "attempt_count": 1,
                "caveat": classification["message"],
            }
        new_events = retry_audit_events()[before_events:]
        if new_events:
            status["retry_events"] = new_events
        else:
            status["attempt_count"] = status.get("attempt_count", 1)
        results.append(status)

    manifest = {
        "goal": config["goal"],
        "manifest_type": "stac_resilience_probe",
        "host_label": args.host_label,
        "host_facts": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": sys.version,
            "gdal_version": gdal.VersionInfo("--version"),
            "numpy_version": np.__version__,
        },
        "started_at_utc": dt.datetime.fromtimestamp(start, tz=dt.UTC).isoformat(),
        "finished_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "elapsed_seconds": round(time.time() - start, 3),
        "command": "python3 scripts/stac_resilience_probe_009.py",
        "config_path": str(config_path.relative_to(REPO)) if config_path.is_relative_to(REPO) else str(config_path),
        "dea_stac_search_url": config["dea_stac_search_url"],
        "dea_collection": config["dea_collection"],
        "probe_bbox_wgs84": list(DEFAULT_PROBE_BBOX),
        "probe_bbox_caveat": "Tiny Narran product-access AOI from Goal 004; used only for endpoint availability.",
        "probe_months": args.months,
        "retry_policy": normalise_retry_policy(config),
        "endpoint_status": endpoint_status(results),
        "results": results,
        "retry_audit_events": retry_audit_events(),
    }
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = REPO / output
        write_json(output, manifest)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
