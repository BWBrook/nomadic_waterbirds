#!/usr/bin/env python3
"""Goal 008 Narran named-subunit evidence crosswalk."""

from __future__ import annotations

import csv
import datetime as dt
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[0]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from event_window_hydrology_007 import (  # noqa: E402
    build_parent_supports,
    fetch_ramsar_subset,
    load_json,
    sha256_file,
    waterbodies_layer,
    waterbody_overlap_lookup,
    waterbody_support_id,
    write_json,
)

CONFIG_PATH = REPO / "settings" / "narran_subunit_evidence_008.json"


def quiet_git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def source_join(*ids: str) -> str:
    return ";".join(ids)


def base_row(parent_support_id: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": row.get("candidate_id", "NWB002"),
        "candidate_name": row.get("candidate_name", "Narran Lake Nature Reserve"),
        "parent_support_id": parent_support_id,
        "support_id": row["support_id"],
        "display_name": row["display_name"],
        "support_level": row.get("support_level", "subunit"),
        "support_type": row["support_type"],
        "source": row.get("source", ""),
        "source_identifier": row.get("source_identifier", ""),
        "source_url": row.get("source_url", ""),
        "evidence_status": row["evidence_status"],
        "name_evidence": row.get("name_evidence", ""),
        "location_evidence": row.get("location_evidence", ""),
        "geometry_status": row["geometry_status"],
        "geometry_evidence": row.get("geometry_evidence", ""),
        "dea_uid_relationship": row.get("dea_uid_relationship", "not verified"),
        "related_dea_waterbody_uid": row.get("related_dea_waterbody_uid", ""),
        "support_area_m2": row.get("support_area_m2", ""),
        "overlap_area_m2": row.get("overlap_area_m2", ""),
        "overlap_fraction_of_parent": row.get("overlap_fraction_of_parent", ""),
        "overlap_fraction_of_dea_waterbody": row.get("overlap_fraction_of_dea_waterbody", ""),
        "included_in_event_window": row.get("included_in_event_window", "no"),
        "inclusion_decision": row["inclusion_decision"],
        "recommended_next_step": row.get("recommended_next_step", ""),
        "caveat": row["caveat"],
    }


def build_unresolved_named_candidate_rows(parent_support_id: str) -> list[dict[str, Any]]:
    common_sources = source_join(
        "dcceew_narran_page",
        "ramsar_ris_2022",
        "ramsar_ecd_2011",
        "nsw_draft_plan_2025",
    )
    common = {
        "candidate_id": "NWB002",
        "candidate_name": "Narran Lake Nature Reserve",
        "source": "Official Ramsar, DCCEEW, and NSW public source review",
        "source_identifier": common_sources,
        "source_url": (
            "https://www.dcceew.gov.au/water/wetlands/australian-ramsar-wetlands/"
            "narran-lake-nature-reserve"
        ),
        "support_level": "subunit",
        "included_in_event_window": "no",
        "inclusion_decision": "retained_unresolved_no_event_window_hydrology",
        "recommended_next_step": (
            "Use only after a public vector geometry, defensible digitised source, "
            "or reviewed DEA UID relationship is verified."
        ),
    }
    rows = [
        {
            **common,
            "support_id": "nwb002_named_clear_lake_unresolved",
            "display_name": "Clear Lake",
            "support_type": "named_open_water_unresolved",
            "evidence_status": "name_location_hydrology_verified_no_standalone_geometry",
            "name_evidence": "Official sources identify Clear Lake within the Narran Ramsar/Nature Reserve context.",
            "location_evidence": "Official sources place Clear Lake in the northern Narran wetland complex.",
            "geometry_status": "unresolved_no_public_vector_subunit",
            "geometry_evidence": "Official public sources reviewed here did not expose standalone Clear Lake polygon geometry.",
            "caveat": (
                "Do not equate Clear Lake with any DEA Waterbody UID until overlap, "
                "centroid, or containment evidence is reviewed against defensible geometry."
            ),
        },
        {
            **common,
            "support_id": "nwb002_named_back_lake_unresolved",
            "display_name": "Back Lake",
            "support_type": "named_open_water_lignum_unresolved",
            "evidence_status": "name_location_hydrology_verified_no_standalone_geometry",
            "name_evidence": "Official sources identify Back Lake within the Narran Ramsar/Nature Reserve context.",
            "location_evidence": "Official sources place Back Lake in the northern Narran wetland complex.",
            "geometry_status": "unresolved_no_public_vector_subunit",
            "geometry_evidence": "Official public sources reviewed here did not expose standalone Back Lake polygon geometry.",
            "caveat": (
                "Back Lake is described with lignum and open-water context, but no "
                "defensible standalone polygon or named DEA UID link was verified."
            ),
        },
        {
            **common,
            "support_id": "nwb002_named_long_arm_unresolved",
            "display_name": "Long Arm",
            "support_type": "named_lignum_wetland_unresolved",
            "evidence_status": "name_location_hydrology_verified_no_standalone_geometry",
            "name_evidence": "Official Ramsar/ECD and NSW sources identify Long Arm as part of the reserve wetland complex.",
            "location_evidence": "Official sources describe Long Arm in sequence with Clear Lake and Back Lake.",
            "geometry_status": "unresolved_no_public_vector_subunit",
            "geometry_evidence": "Official public sources reviewed here did not expose standalone Long Arm polygon geometry.",
            "caveat": (
                "Long Arm is hydrologically important in official descriptions, but "
                "should remain unresolved for support geometry until a vector or UID link is verified."
            ),
        },
        {
            **common,
            "source_identifier": source_join(*common_sources.split(";"), "nsw_vegetation_map_metadata_2026"),
            "support_id": "nwb002_lignum_channelised_floodplain_unresolved",
            "display_name": "Narran lignum/channelised floodplain",
            "support_type": "vegetation_floodplain_unresolved",
            "evidence_status": "vegetation_context_verified_no_support_geometry",
            "name_evidence": "Official sources identify extensive lignum and channelised floodplain wetlands in the Ramsar site.",
            "location_evidence": "Official sources describe lignum around Clear Lake, Back Lake, Long Arm, and floodplain channels.",
            "geometry_status": "unresolved_no_named_support_polygon",
            "geometry_evidence": (
                "A current NSW landscape-scale vegetation map exists, but this goal did "
                "not verify a support-ready named lignum/floodplain polygon."
            ),
            "caveat": (
                "Vegetation context is strong enough for source evidence, but not for "
                "event-window hydrology support inclusion without reviewed vector class extraction."
            ),
        },
    ]
    return [base_row(parent_support_id, row) for row in rows]


def crosswalk_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "candidate_name",
        "parent_support_id",
        "support_id",
        "display_name",
        "support_level",
        "support_type",
        "source",
        "source_identifier",
        "source_url",
        "evidence_status",
        "name_evidence",
        "location_evidence",
        "geometry_status",
        "geometry_evidence",
        "dea_uid_relationship",
        "related_dea_waterbody_uid",
        "support_area_m2",
        "overlap_area_m2",
        "overlap_fraction_of_parent",
        "overlap_fraction_of_dea_waterbody",
        "included_in_event_window",
        "inclusion_decision",
        "recommended_next_step",
        "caveat",
    ]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def url_to_file(url: str, path: Path) -> dict[str, Any]:
    if path.exists() and path.stat().st_size > 0:
        return {
            "path": str(path.relative_to(REPO)),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "committed": False,
            "status": "reused_existing_staged_file",
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=180) as response, path.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    return {
        "path": str(path.relative_to(REPO)),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "committed": False,
        "status": "downloaded",
    }


def stage_source_files(config: dict[str, Any]) -> list[dict[str, Any]]:
    staged: list[dict[str, Any]] = []
    for source in config["source_files"]:
        path = REPO / source["staged_path"]
        try:
            record = url_to_file(source["url"], path)
        except Exception as exc:
            record = {
                "path": str(path.relative_to(REPO)),
                "bytes": "",
                "sha256": "",
                "committed": False,
                "status": f"not_staged: {exc}",
            }
        staged.append({**source, **record})
    return staged


def stage_waterbodies_zip(config: dict[str, Any]) -> dict[str, Any]:
    target = REPO / config["staged_files"]["dea_waterbodies_zip"]
    seed = REPO / config["existing_waterbodies_zip_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        if seed.exists():
            shutil.copyfile(seed, target)
        else:
            url_to_file(config["dea_waterbodies_zip_url"], target)
    return {
        "path": str(target.relative_to(REPO)),
        "bytes": target.stat().st_size,
        "sha256": sha256_file(target),
        "committed": False,
        "status": "reused_or_copied_for_overlap_check",
    }


def build_parent_row(config: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    return base_row(
        config["parent_support_id"],
        {
            "candidate_id": config["candidate_id"],
            "candidate_name": config["candidate_name"],
            "support_id": config["parent_support_id"],
            "display_name": config["candidate_name"],
            "support_level": "parent",
            "support_type": "official_ramsar_parent_support",
            "source": "DCCEEW Geospatial Ramsar Wetlands service and Ramsar RSIS",
            "source_identifier": "REFCODE=1291",
            "source_url": "https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Ramsar_Wetlands/MapServer/0",
            "evidence_status": "official_parent_ramsar_support",
            "name_evidence": "Official Ramsar site name.",
            "location_evidence": "Official Ramsar boundary places the support in NSW Narran Lake Nature Reserve.",
            "geometry_status": "official_parent_geometry_verified",
            "geometry_evidence": "Official Ramsar parent polygon union.",
            "dea_uid_relationship": "not applicable at parent level",
            "support_area_m2": round(parent["area_m2"], 3),
            "included_in_event_window": "yes",
            "inclusion_decision": "retain_as_current_event_window_parent_support",
            "recommended_next_step": "Keep as the hydrology support until named subunit geometry is verified.",
            "caveat": (
                "Parent support is defensible, but it does not resolve Clear Lake, "
                "Back Lake, Long Arm, or lignum/floodplain subunit boundaries."
            ),
        },
    )


def build_dea_overlap_rows(
    config: dict[str, Any], parent: dict[str, Any], waterbodies_zip: Path
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    overlaps = waterbody_overlap_lookup(waterbodies_zip, parent["geom_albers"])
    for item in overlaps:
        uid = item["uid"]
        rows.append(
            base_row(
                config["parent_support_id"],
                {
                    "candidate_id": config["candidate_id"],
                    "candidate_name": config["candidate_name"],
                    "support_id": waterbody_support_id(config["candidate_id"], uid),
                    "display_name": f"DEA Waterbody {uid} within Narran parent",
                    "support_level": "screen",
                    "support_type": "dea_waterbody_parent_overlap_unresolved_name",
                    "source": "DEA Waterbodies v3 shapefile",
                    "source_identifier": uid,
                    "source_url": config["dea_waterbodies_zip_url"],
                    "evidence_status": "dea_parent_overlap_no_named_subunit_link",
                    "name_evidence": "DEA Waterbody UID only; no official named lake relationship verified.",
                    "location_evidence": "DEA Waterbody polygon overlaps the official Narran Ramsar parent support.",
                    "geometry_status": "dea_waterbody_polygon_overlaps_parent",
                    "geometry_evidence": "Intersection with parent Ramsar support computed in EPSG:3577.",
                    "dea_uid_relationship": "parent overlap verified; named Clear Lake/Back Lake/Long Arm link not verified",
                    "related_dea_waterbody_uid": uid,
                    "support_area_m2": round(item["area_m2"], 3),
                    "overlap_area_m2": round(item["overlap_area_m2"], 3),
                    "overlap_fraction_of_parent": round(item["overlap_fraction_of_support"], 8),
                    "overlap_fraction_of_dea_waterbody": round(item["overlap_fraction_of_waterbody"], 8),
                    "included_in_event_window": "no",
                    "inclusion_decision": "retained_as_dea_overlap_screen_not_named_support",
                    "recommended_next_step": (
                        "Review against official map/vector evidence before using as a named Narran subunit."
                    ),
                    "caveat": (
                        "This is useful open-water screening evidence only; it does not prove "
                        "a Clear Lake, Back Lake, Long Arm, or lignum support identity."
                    ),
                },
            )
        )
    return rows


def narran_ramsar_subset(config: dict[str, Any], goal007_config: dict[str, Any]) -> tuple[dict[str, Any], str]:
    payload, url = fetch_ramsar_subset(goal007_config)
    refcode = int(config["parent_ramsar_refcode"])
    features = [
        feature
        for feature in payload.get("features", [])
        if int(feature.get("properties", {}).get("REFCODE", -1)) == refcode
    ]
    return {**payload, "features": features}, url


def run() -> int:
    config = load_json(CONFIG_PATH)
    goal007_config = load_json(REPO / config["goal007_config_path"])
    for relpath in config["scratch_paths"].values():
        (REPO / relpath).mkdir(parents=True, exist_ok=True)

    staged_sources = stage_source_files(config)
    waterbody_record = stage_waterbodies_zip(config)
    waterbodies_zip = REPO / waterbody_record["path"]

    ramsar_subset, ramsar_query_url = narran_ramsar_subset(config, goal007_config)
    ramsar_path = REPO / config["staged_files"]["ramsar_subset_geojson"]
    ramsar_path.parent.mkdir(parents=True, exist_ok=True)
    ramsar_path.write_text(json.dumps(ramsar_subset, indent=2), encoding="utf-8")
    ramsar_record = {
        "path": str(ramsar_path.relative_to(REPO)),
        "bytes": ramsar_path.stat().st_size,
        "sha256": sha256_file(ramsar_path),
        "committed": False,
        "status": "downloaded_from_ramsar_service_query",
    }

    parents, _ = build_parent_supports(goal007_config, ramsar_subset)
    parent = parents[config["candidate_id"]]
    dea_rows = build_dea_overlap_rows(config, parent, waterbodies_zip)
    rows = [
        build_parent_row(config, parent),
        *build_unresolved_named_candidate_rows(config["parent_support_id"]),
        *dea_rows,
    ]
    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    write_csv(outputs["crosswalk_csv"], rows, crosswalk_fieldnames())

    _, layer = waterbodies_layer(waterbodies_zip)
    manifest = {
        "goal": config["goal"],
        "manifest_type": "narran_named_subunit_evidence",
        "accessed_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "command": "python3 scripts/narran_subunit_evidence_008.py",
        "config_path": str(CONFIG_PATH.relative_to(REPO)),
        "git_commit_at_run": quiet_git_commit(),
        "source_urls": {source["id"]: source["url"] for source in config["source_files"]},
        "ramsar_service_query": ramsar_query_url,
        "staged_raw_files": [ramsar_record, waterbody_record, *staged_sources],
        "source_checks": [
            {
                "topic": "Clear Lake",
                "status": "name and approximate location verified; standalone vector geometry not verified",
                "support_id": "nwb002_named_clear_lake_unresolved",
            },
            {
                "topic": "Back Lake",
                "status": "name and approximate location verified; standalone vector geometry not verified",
                "support_id": "nwb002_named_back_lake_unresolved",
            },
            {
                "topic": "Long Arm",
                "status": "name and hydrological sequence verified; standalone vector geometry not verified",
                "support_id": "nwb002_named_long_arm_unresolved",
            },
            {
                "topic": "Lignum/channelised floodplain",
                "status": "vegetation context verified; support-ready named polygon not verified",
                "support_id": "nwb002_lignum_channelised_floodplain_unresolved",
            },
            {
                "topic": "DEA Waterbodies parent overlaps",
                "status": "parent-overlap screens computed; no named subunit UID relationship verified",
                "count": len(dea_rows),
            },
        ],
        "crosswalk_rows": len(rows),
        "parent_support_count": 1,
        "named_unresolved_support_count": 4,
        "dea_parent_overlap_count": len(dea_rows),
        "dea_waterbodies_layer_feature_count": layer.GetFeatureCount(),
        "outputs": {
            "crosswalk_csv": str(outputs["crosswalk_csv"].relative_to(REPO)),
            "manifest_json": str(outputs["manifest_json"].relative_to(REPO)),
        },
        "cleanup_status": (
            "Raw source HTML/PDF, Ramsar GeoJSON, and DEA Waterbodies ZIP are staged only "
            "under ignored Goal 008 artifact paths and are not committed."
        ),
    }
    write_json(outputs["manifest_json"], manifest)
    print(json.dumps({"crosswalk_rows": len(rows), "dea_parent_overlap_count": len(dea_rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
