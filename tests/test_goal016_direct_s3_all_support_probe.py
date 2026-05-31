import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO / "scripts" / "direct_s3_all_support_probe_016.py"


def load_module():
    if not SCRIPT_PATH.exists():
        raise AssertionError(f"missing script under test: {SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("direct_s3_all_support_probe_016", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal016DirectS3AllSupportProbeTests(unittest.TestCase):
    def test_support_month_grid_preserves_all_supports_and_months(self):
        module = load_module()
        supports = [
            {"support_id": "s2", "candidate_id": "NWB002"},
            {"support_id": "s1", "candidate_id": "NWB001"},
        ]

        grid = module.expected_support_month_grid(supports, ["2022-11", "2018-01"])

        self.assertEqual(
            [(row["support_id"], row["month"]) for row in grid],
            [("s1", "2018-01"), ("s1", "2022-11"), ("s2", "2018-01"), ("s2", "2022-11")],
        )

    def test_path_rows_are_grouped_and_sorted_by_support(self):
        module = load_module()
        rows = [
            {"support_id": "s1", "path_row": "093/081"},
            {"support_id": "s1", "path_row": "092/081"},
            {"support_id": "s2", "path_row": "095/080"},
            {"support_id": "s1", "path_row": "092/081"},
        ]

        grouped = module.path_rows_by_support(rows)

        self.assertEqual(grouped["s1"], ["092/081", "093/081"])
        self.assertEqual(grouped["s2"], ["095/080"])

    def test_required_status_vocabulary_is_explicit(self):
        module = load_module()

        self.assertTrue(module.REQUIRED_STATUSES.issubset(module.STATUS_VOCABULARY))
        self.assertEqual(module.status_for_failure("s3_listing", RuntimeError("boom")), "blocked_s3_listing_failure")
        self.assertEqual(module.status_for_failure("cog_read", RuntimeError("boom")), "blocked_cog_read_failure")
        self.assertEqual(module.status_for_failure("mask", RuntimeError("boom")), "blocked_mask_or_geometry_failure")
        self.assertEqual(module.status_for_failure("remote", RuntimeError("boom")), "blocked_remote_or_route_unavailable")
        self.assertEqual(module.status_for_failure("unknown", RuntimeError("boom")), "blocked_unclassified_failure")

    def test_comparison_classification_separates_denominator_from_wetness(self):
        module = load_module()
        tolerances = {"count_abs": 0.0, "fraction_abs": 0.000001, "area_m2_abs": 0.5, "numeric_abs": 0.0}
        computed = {
            "status": "computed_direct_s3_metrics",
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
        denominator_reference = dict(
            computed,
            status="computed_event_window_metrics",
            readable_scene_count="15",
            invalid_obs_count="711481",
            clear_obs_fraction="0.495065",
        )
        wetness_reference = dict(denominator_reference, current_proportion_wet="0.314966")

        denominator = module.classify_comparison(computed, denominator_reference, tolerances)
        wetness = module.classify_comparison(computed, wetness_reference, tolerances)
        missing = module.classify_comparison(computed, {}, tolerances)
        blocked = module.classify_comparison({"status": "blocked_cog_read_failure"}, denominator_reference, tolerances)

        self.assertEqual(denominator["comparison_status"], "wetness_within_tolerance_denominator_diff")
        self.assertEqual(wetness["comparison_status"], "wetness_diff")
        self.assertEqual(missing["comparison_status"], "missing_or_blocked_reference")
        self.assertEqual(blocked["comparison_status"], "computed_row_blocked")

    def test_output_schemas_contain_goal016_required_columns(self):
        module = load_module()

        self.assertTrue(
            {
                "candidate_id",
                "support_id",
                "month",
                "status",
                "path_rows",
                "direct_s3_items_found",
                "readable_scene_count",
                "clear_obs_count",
                "invalid_obs_count",
                "current_wet_area_m2",
                "valid_support_area_m2",
                "current_proportion_wet",
                "quality_flag",
                "wet_month_flag",
            }.issubset(set(module.summary_fieldnames()))
        )
        self.assertTrue(
            {
                "support_id",
                "expected_month_count",
                "computed_month_count",
                "blocked_month_count",
                "quality_high_count",
                "quality_minimum_count",
                "quality_fail_count",
            }.issubset(set(module.support_summary_fieldnames()))
        )
        self.assertTrue(
            {
                "support_id",
                "month",
                "reference_source",
                "comparison_status",
                "differing_fields",
                "recommendation",
            }.issubset(set(module.comparison_fieldnames()))
        )

    def test_raw_source_extensions_are_blocked_from_committed_outputs(self):
        module = load_module()

        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/direct_s3_all_support_probe_016/raw/stac.json")))
        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/direct_s3_all_support_probe_016/raw/scene.tif")))
        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/direct_s3_all_support_probe_016/intermediate/cache.npy")))
        self.assertFalse(module.is_blocked_raw_extension(Path("docs/direct_s3_all_support_probe_016_summary.csv")))


if __name__ == "__main__":
    unittest.main()
