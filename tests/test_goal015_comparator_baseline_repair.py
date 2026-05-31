import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO / "scripts" / "comparator_baseline_repair_015.py"


def load_module():
    if not SCRIPT_PATH.exists():
        raise AssertionError(f"missing script under test: {SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("comparator_baseline_repair_015", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal015ComparatorBaselineRepairTests(unittest.TestCase):
    def test_stac_filter_keeps_support_path_rows_and_reports_bbox_extras(self):
        module = load_module()
        items = [
            {"item_id": "a", "asset_key": "derivative/ga_ls_wo_3/1-6-0/092/081/2022/11/04/a_water.tif", "path_row": "092/081"},
            {"item_id": "b", "asset_key": "derivative/ga_ls_wo_3/1-6-0/093/080/2022/11/03/b_water.tif", "path_row": "093/080"},
            {"item_id": "c", "asset_key": "derivative/ga_ls_wo_3/1-6-0/094/080/2022/11/03/c_water.tif", "path_row": "094/080"},
        ]

        result = module.filter_items_to_path_rows(items, {"092/081", "093/080"})

        self.assertEqual([item["item_id"] for item in result["filtered_items"]], ["a", "b"])
        self.assertEqual([item["item_id"] for item in result["bbox_extra_items"]], ["c"])
        self.assertEqual(result["filtered_item_count"], 2)
        self.assertEqual(result["bbox_extra_item_count"], 1)

    def test_denominator_effect_accounts_for_bbox_only_no_data_scenes(self):
        module = load_module()
        repaired = {
            "readable_scene_count": "11",
            "n_pixel_u": "93937",
            "invalid_obs_count": "335733",
            "no_data_count": "0",
            "clear_obs_fraction": "0.675089",
            "current_wet_area_m2": "18173724.0",
            "current_proportion_wet": "0.214966",
            "wet_pixel_observation_count": "124917",
            "dry_pixel_observation_count": "572657",
        }
        legacy = {
            "readable_scene_count": "15",
            "invalid_obs_count": "711481",
            "no_data_count": "375748",
            "clear_obs_fraction": "0.495065",
            "current_wet_area_m2": "18173724.0",
            "current_proportion_wet": "0.214966",
            "wet_pixel_observation_count": "124917",
            "dry_pixel_observation_count": "572657",
        }

        effect = module.legacy_denominator_effect("2022-11", legacy, repaired, {"area_m2_abs": 0.5, "fraction_abs": 0.000001})

        self.assertEqual(effect["legacy_extra_scene_count"], 4)
        self.assertEqual(effect["expected_extra_invalid_or_no_data"], 375748)
        self.assertEqual(effect["observed_extra_invalid_or_no_data"], 375748)
        self.assertEqual(effect["effect_status"], "bbox_only_denominator_effect_confirmed")
        self.assertEqual(effect["wetness_effect"], "denominator_only")
        self.assertIn("readable_scene_count", effect["fields_affected"])
        self.assertIn("clear_obs_fraction", effect["fields_affected"])

    def test_comparison_rows_respect_predeclared_tolerances(self):
        module = load_module()
        tolerances = {"count_abs": 0.0, "fraction_abs": 0.000001, "area_m2_abs": 0.5}
        direct = {
            "readable_scene_count": "11",
            "clear_obs_count": "697574",
            "invalid_obs_count": "335733",
            "clear_obs_fraction": "0.675089",
            "current_wet_area_m2": "18173724.0",
            "valid_support_area_m2": "84542400",
            "current_proportion_wet": "0.214966",
            "wet_pixel_observation_count": "124917",
            "dry_pixel_observation_count": "572657",
            "quality_flag": "quality_high",
            "wet_month_flag": "True",
        }
        repaired = dict(direct)
        legacy = dict(direct, readable_scene_count="15", invalid_obs_count="711481", clear_obs_fraction="0.495065")

        matched = module.compare_metric_rows("2022-11", direct, repaired, tolerances, module.DEFAULT_COMPARISON_FIELDS)
        mismatched = module.compare_metric_rows("2022-11", repaired, legacy, tolerances, module.DEFAULT_COMPARISON_FIELDS)

        self.assertEqual(matched["comparison_status"], "within_tolerance")
        self.assertEqual(matched["differing_fields"], [])
        self.assertEqual(mismatched["comparison_status"], "mismatch_beyond_tolerance")
        self.assertEqual(mismatched["differing_fields"], ["readable_scene_count", "invalid_obs_count", "clear_obs_fraction"])

    def test_output_schemas_contain_goal015_required_columns(self):
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
                "comparison_type",
                "comparison_status",
                "differing_fields",
                "recommendation",
            }.issubset(set(module.comparison_fieldnames()))
        )
        self.assertTrue(
            {
                "month",
                "legacy_extra_scene_count",
                "observed_extra_invalid_or_no_data",
                "effect_status",
            }.issubset(set(module.denominator_effect_fieldnames()))
        )

    def test_raw_source_extensions_are_blocked_from_committed_outputs(self):
        module = load_module()

        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/comparator_baseline_repair_015/raw/stac.json")))
        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/comparator_baseline_repair_015/intermediate/cache.npy")))
        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/comparator_baseline_repair_015/raw/scene.tif")))
        self.assertFalse(module.is_blocked_raw_extension(Path("docs/pathrow_filtered_comparator_015_summary.csv")))


if __name__ == "__main__":
    unittest.main()
