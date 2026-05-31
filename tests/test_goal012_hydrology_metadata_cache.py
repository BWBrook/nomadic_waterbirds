import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hydrology_metadata_cache_s3_012.py"


def load_module():
    if not SCRIPT_PATH.exists():
        raise AssertionError(f"missing script under test: {SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("hydrology_metadata_cache_s3_012", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal012HydrologyMetadataCacheTests(unittest.TestCase):
    def test_candidate_month_cache_key_is_deterministic_and_uses_bbox_hash(self):
        module = load_module()
        bbox = [147.36564063799995, -29.777802256186163, 147.49428485099997, -29.67042131618795]

        key = module.candidate_month_cache_key("ga_ls_wo_3", "NWB002", "2022-11", bbox)

        self.assertEqual(key, module.candidate_month_cache_key("ga_ls_wo_3", "NWB002", "2022-11", list(bbox)))
        self.assertRegex(key, r"^ga_ls_wo_3\\|NWB002\\|2022-11\\|[0-9a-f]{16}$")

    def test_s3_prefix_from_path_row_month_is_goal012_bounded_pattern(self):
        module = load_module()

        prefix = module.s3_prefix_for_path_row_month("ga_ls_wo_3", "1-6-0", "093", "080", "2024-12")

        self.assertEqual(prefix, "derivative/ga_ls_wo_3/1-6-0/093/080/2024/12/")

    def test_item_set_summary_hashes_are_stable_under_item_order(self):
        module = load_module()
        items = [
            {"item_id": "b", "asset_key": "path/b_water.tif"},
            {"item_id": "a", "asset_key": "path/a_water.tif"},
        ]

        first = module.item_set_summary("NWB002", "2022-11", "direct_s3_path_row", "093/080", items, "ignored", "available")
        second = module.item_set_summary(
            "NWB002", "2022-11", "direct_s3_path_row", "093/080", list(reversed(items)), "ignored", "available"
        )

        self.assertEqual(first["item_count"], 2)
        self.assertEqual(first["item_id_hash"], second["item_id_hash"])
        self.assertEqual(first["asset_key_hash"], second["asset_key_hash"])
        self.assertEqual(first["route_status"], "available")

    def test_classify_stac_preflight_requires_every_month_available(self):
        module = load_module()

        available = module.classify_stac_preflight(
            [{"month": "2018-01", "status_code": 200}, {"month": "2022-11", "status_code": 200}]
        )
        unavailable = module.classify_stac_preflight(
            [{"month": "2018-01", "status_code": 200}, {"month": "2022-11", "status_code": 503}]
        )

        self.assertEqual(available["route_status"], "available")
        self.assertEqual(unavailable["route_status"], "unavailable_service_unstable")
        self.assertIn("2022-11", unavailable["failure_months"])

    def test_blocked_raw_extensions_identify_uncommittable_cache_outputs(self):
        module = load_module()

        hits = module.blocked_raw_extensions(
            [
                "docs/hydrology_metadata_item_sets_012.csv",
                "artifacts/hydrology_metadata_cache_012/raw/items.json",
                "artifacts/hydrology_metadata_cache_012/raw/scene.tif",
                "scratch/cache.duckdb",
            ]
        )

        self.assertEqual(hits, ["artifacts/hydrology_metadata_cache_012/raw/scene.tif", "scratch/cache.duckdb"])

    def test_load_cached_json_returns_payload_only_when_reuse_enabled(self):
        module = load_module()
        tmp = Path(__file__).with_suffix(".tmp.json")
        tmp.write_text('{"ok": true}', encoding="utf-8")
        try:
            self.assertIsNone(module.load_cached_json(tmp, reuse_cache=False))
            self.assertEqual(module.load_cached_json(tmp, reuse_cache=True), {"ok": True})
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
