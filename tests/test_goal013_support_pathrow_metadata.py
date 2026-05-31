import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO / "scripts" / "support_pathrow_metadata_013.py"


def load_module():
    spec = importlib.util.spec_from_file_location("support_pathrow_metadata_013", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal013SupportPathrowMetadataTests(unittest.TestCase):
    def test_path_row_key_zero_pads_numeric_values(self):
        module = load_module()

        self.assertEqual(module.path_row_key(93, 80), "093/080")
        self.assertEqual(module.path_row_key("94", "081"), "094/081")

    def test_s3_prefix_for_path_row_month_uses_dea_layout(self):
        module = load_module()

        self.assertEqual(
            module.s3_prefix_for_path_row_month("ga_ls_wo_3", "1-6-0", "93", "80", "2022-11"),
            "derivative/ga_ls_wo_3/1-6-0/093/080/2022/11/",
        )

    def test_item_set_hashes_are_stable_under_order_changes(self):
        module = load_module()
        items_a = [
            {"item_id": "scene-b", "asset_key": "b_water.tif", "path_row": "094/081"},
            {"item_id": "scene-a", "asset_key": "a_water.tif", "path_row": "093/080"},
        ]
        items_b = list(reversed(items_a))

        self.assertEqual(module.item_set_hashes(items_a), module.item_set_hashes(items_b))
        hashes = module.item_set_hashes(items_a)
        self.assertEqual(hashes["item_count"], 2)
        self.assertRegex(hashes["asset_key_hash"], r"^[0-9a-f]{64}$")

    def test_coverage_status_labels_geometry_and_bbox_methods(self):
        module = load_module()

        self.assertEqual(module.coverage_status("geometry_intersection", ["093/080"]), "complete")
        self.assertEqual(module.coverage_status("bbox_intersection", ["093/080"]), "conservative")
        self.assertEqual(module.coverage_status("geometry_intersection", []), "blocked")

    def test_comparator_status_keeps_s3_from_claiming_equivalence(self):
        module = load_module()

        self.assertEqual(
            module.final_equivalence_status(
                stac_status="available_equivalent_for_derived_pathrows",
                official_comparator_status="not_attempted",
                s3_goal012_status="identical_known_path",
                support_coverage_status="complete",
            ),
            "equivalent",
        )
        self.assertEqual(
            module.final_equivalence_status(
                stac_status="available",
                official_comparator_status="not_attempted",
                s3_goal012_status="identical_known_path",
                support_coverage_status="complete",
            ),
            "technical_viability_not_equivalence",
        )
        self.assertEqual(
            module.final_equivalence_status(
                stac_status="unavailable_service_unstable",
                official_comparator_status="missing_local_dependency",
                s3_goal012_status="identical_known_path",
                support_coverage_status="complete",
            ),
            "comparator_unavailable",
        )
        self.assertEqual(
            module.final_equivalence_status(
                stac_status="available",
                official_comparator_status="not_attempted",
                s3_goal012_status="identical_known_path",
                support_coverage_status="conservative",
            ),
            "support_coverage_incomplete",
        )

    def test_raw_source_extensions_are_blocked_from_committed_outputs(self):
        module = load_module()

        blocked = {".shp", ".dbf", ".shx", ".geojson", ".zip", ".tif", ".parquet", ".duckdb"}
        self.assertTrue(blocked.issubset(module.BLOCKED_RAW_EXTENSIONS))
        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/raw/WRS2_descending.shp")))
        self.assertFalse(module.is_blocked_raw_extension(Path("docs/support_pathrow_crosswalk_013.csv")))


if __name__ == "__main__":
    unittest.main()
