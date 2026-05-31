import importlib.util
import unittest
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO / "scripts" / "direct_s3_extraction_rehearsal_014.py"


def load_module():
    if not SCRIPT_PATH.exists():
        raise AssertionError(f"missing script under test: {SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("direct_s3_extraction_rehearsal_014", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal014DirectS3ExtractionTests(unittest.TestCase):
    def test_item_set_validation_sums_complete_path_rows_by_month(self):
        module = load_module()
        rows = [
            {"support_id": "nwb002_ramsar_ref1291", "month": "2018-01", "path_row": "092/081", "item_count": "3"},
            {"support_id": "nwb002_ramsar_ref1291", "month": "2018-01", "path_row": "093/080", "item_count": "3"},
            {"support_id": "nwb002_ramsar_ref1291", "month": "2018-01", "path_row": "093/081", "item_count": "3"},
            {"support_id": "nwb002_ramsar_ref1291", "month": "2022-11", "path_row": "092/081", "item_count": "3"},
            {"support_id": "nwb002_ramsar_ref1291", "month": "2022-11", "path_row": "093/080", "item_count": "4"},
            {"support_id": "nwb002_ramsar_ref1291", "month": "2022-11", "path_row": "093/081", "item_count": "4"},
        ]

        summary = module.validate_item_set_rows(
            rows,
            support_id="nwb002_ramsar_ref1291",
            months=["2018-01", "2022-11"],
            path_rows=["092/081", "093/080", "093/081"],
            expected_month_counts={"2018-01": 9, "2022-11": 11},
        )

        self.assertEqual(summary["status"], "matched_goal013_item_sets")
        self.assertEqual(summary["month_counts"], {"2018-01": 9, "2022-11": 11})
        self.assertEqual(summary["missing_path_rows"], [])

    def test_water_observation_aggregation_uses_existing_bit_contract(self):
        module = load_module()
        support_mask = np.array([[True, True], [True, False]])
        scene_values = [
            np.array([[0, 128], [64, 0]], dtype=np.uint8),
            np.array([[128, 128], [1, 0]], dtype=np.uint8),
        ]

        metrics = module.summarise_direct_support_month(scene_values, support_mask)

        self.assertEqual(metrics["n_scene_m"], 2)
        self.assertEqual(metrics["n_pixel_u"], 3)
        self.assertEqual(metrics["clear_obs_count"], 4)
        self.assertEqual(metrics["invalid_obs_count"], 2)
        self.assertEqual(metrics["wet_pixel_observation_count"], 3)
        self.assertEqual(metrics["dry_pixel_observation_count"], 1)
        self.assertEqual(metrics["no_data_count"], 1)
        self.assertEqual(metrics["cloud_count"], 1)
        self.assertAlmostEqual(metrics["current_proportion_wet"], 0.75)
        self.assertEqual(metrics["quality_flag"], "quality_minimum")

    def test_metric_comparison_reports_strict_numeric_mismatch(self):
        module = load_module()
        tolerances = {"count_abs": 0.0, "fraction_abs": 0.000001, "area_m2_abs": 0.5}
        direct = {
            "readable_scene_count": "11",
            "clear_obs_count": "697574",
            "invalid_obs_count": "335733",
            "clear_obs_fraction": "0.675105",
            "current_wet_area_m2": "18173724.0",
            "current_proportion_wet": "0.214966",
            "quality_flag": "quality_high",
        }
        target = {
            "readable_scene_count": "15",
            "clear_obs_count": "697574",
            "invalid_obs_count": "711481",
            "clear_obs_fraction": "0.495065",
            "current_wet_area_m2": "18173724.0",
            "current_proportion_wet": "0.214966",
            "quality_flag": "quality_high",
        }

        result = module.compare_metric_rows("2022-11", direct, target, tolerances)

        self.assertEqual(result["comparison_status"], "mismatch_beyond_tolerance")
        self.assertIn("readable_scene_count", result["differing_fields"])
        self.assertIn("invalid_obs_count", result["differing_fields"])
        self.assertGreater(result["max_abs_numeric_difference"], 0)

    def test_bbox_extra_no_data_hint_identifies_legacy_denominator_difference(self):
        module = load_module()
        direct = {
            "n_pixel_u": "93937",
            "readable_scene_count": "11",
            "current_wet_area_m2": "18173724.0",
            "current_proportion_wet": "0.214966",
            "no_data_count": "0",
        }
        target = {
            "readable_scene_count": "15",
            "current_wet_area_m2": "18173724.0",
            "current_proportion_wet": "0.214966",
            "no_data_count": "375748",
        }

        hint = module.legacy_bbox_extra_no_data_hint(direct, target)

        self.assertTrue(hint["matches_hint"])
        self.assertEqual(hint["extra_scene_count"], 4)

    def test_output_schema_contains_required_goal_fields(self):
        module = load_module()

        self.assertTrue(
            {
                "candidate_id",
                "support_id",
                "month",
                "status",
                "readable_scene_count",
                "clear_obs_count",
                "invalid_obs_count",
                "current_wet_area_m2",
                "current_proportion_wet",
                "quality_flag",
            }.issubset(set(module.summary_fieldnames()))
        )
        self.assertTrue(
            {
                "month",
                "comparison_target",
                "comparison_status",
                "max_abs_numeric_difference",
                "recommendation",
            }.issubset(set(module.comparison_fieldnames()))
        )

    def test_raw_source_extensions_are_blocked_from_committed_outputs(self):
        module = load_module()

        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/direct_s3_extraction/raw/scene.tif")))
        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/direct_s3_extraction/intermediate/cache.npy")))
        self.assertFalse(module.is_blocked_raw_extension(Path("docs/direct_s3_extraction_rehearsal_014_summary.csv")))


if __name__ == "__main__":
    unittest.main()
