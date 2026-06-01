import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "direct_s3_full_window_hydrology_019.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError(f"missing script under test: {SCRIPT}")
    spec = importlib.util.spec_from_file_location("direct_s3_full_window_hydrology_019", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal019DirectS3FullWindowHydrologyTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_month_sequence_and_grid_cover_full_window(self):
        months = self.module.month_sequence("2018-01", "2024-12")
        supports = [
            {"support_id": "s2", "candidate_id": "NWB002"},
            {"support_id": "s1", "candidate_id": "NWB001"},
        ]

        grid = self.module.expected_support_month_grid(supports, months[:2])

        self.assertEqual(84, len(months))
        self.assertEqual("2018-01", months[0])
        self.assertEqual("2024-12", months[-1])
        self.assertEqual(
            [(row["support_id"], row["month"]) for row in grid],
            [("s1", "2018-01"), ("s1", "2018-02"), ("s2", "2018-01"), ("s2", "2018-02")],
        )

    def test_preflight_targets_cover_scene_selection_and_window_requirements(self):
        targets = [
            {"support_id": "nwb003_ramsar_component_121", "month": "2018-01"},
            {"support_id": "nwb004_ramsar_ref265", "month": "2022-11"},
            {"support_id": "nwb004_ramsar_component_369", "month": "2024-12"},
        ]
        pathrow_map = {
            "nwb003_ramsar_component_121": ["091/080"],
            "nwb004_ramsar_ref265": ["093/085", "094/085"],
            "nwb004_ramsar_component_369": ["094/085"],
        }

        coverage = self.module.preflight_coverage(targets, pathrow_map)

        self.assertTrue(coverage["has_single_pathrow"])
        self.assertTrue(coverage["has_multi_pathrow"])
        self.assertTrue(coverage["has_kerang_discrepancy_cluster"])
        self.assertTrue(coverage["has_early_window_month"])
        self.assertTrue(coverage["has_flood_window_month"])
        self.assertTrue(coverage["has_recent_month"])
        self.assertTrue(coverage["passes"])

    def test_row_status_vocabulary_maps_goal_contract(self):
        self.assertTrue(self.module.REQUIRED_ROW_STATUSES.issubset(self.module.ROW_STATUS_VOCABULARY))
        self.assertEqual(
            "blocked_direct_s3_listing_failure",
            self.module.row_status_for_failure("s3_listing", RuntimeError("boom")),
        )
        self.assertEqual(
            "blocked_direct_s3_read_failure",
            self.module.row_status_for_failure("cog_read", RuntimeError("boom")),
        )
        self.assertEqual(
            "blocked_geometry_or_mask_failure",
            self.module.row_status_for_failure("mask", RuntimeError("boom")),
        )
        self.assertEqual(
            "blocked_metric_computation_failure",
            self.module.row_status_for_failure("metric", RuntimeError("boom")),
        )

    def test_series_item_and_summary_schemas_include_required_columns(self):
        self.assertTrue(
            {
                "candidate_id",
                "support_id",
                "month",
                "row_status",
                "quality_flag",
                "item_count",
                "asset_key_hash",
                "item_id_hash",
                "current_wet_area_m2",
                "current_proportion_wet",
                "wet_area_lag_1m",
                "wet_prop_trailing_3m",
                "novel_after_dry_flag",
                "drying_velocity_1m",
                "derived_metric_status",
            }.issubset(set(self.module.series_fieldnames()))
        )
        self.assertTrue(
            {
                "support_id",
                "month",
                "path_rows",
                "item_count",
                "asset_key_hash",
                "item_id_hash",
                "route_status",
            }.issubset(set(self.module.item_set_fieldnames()))
        )
        self.assertTrue(
            {"summary_level", "row_count", "computed_count", "blocked_count"}.issubset(
                set(self.module.summary_fieldnames())
            )
        )

    def test_derived_metric_boundaries_use_quality_passing_prior_months(self):
        rows = [
            {
                "support_id": "s1",
                "month": "2018-01",
                "row_status": "computed_direct_s3_metrics",
                "quality_flag": "quality_high",
                "current_wet_area_m2": "0",
                "current_proportion_wet": "0",
                "wet_month_flag": "False",
            },
            {
                "support_id": "s1",
                "month": "2018-02",
                "row_status": "computed_direct_s3_metrics",
                "quality_flag": "quality_high",
                "current_wet_area_m2": "90",
                "current_proportion_wet": "0.01",
                "wet_month_flag": "False",
            },
            {
                "support_id": "s1",
                "month": "2018-03",
                "row_status": "blocked_direct_s3_read_failure",
                "quality_flag": "quality_fail",
                "current_wet_area_m2": "",
                "current_proportion_wet": "",
                "wet_month_flag": "",
            },
            {
                "support_id": "s1",
                "month": "2018-04",
                "row_status": "computed_direct_s3_metrics",
                "quality_flag": "quality_high",
                "current_wet_area_m2": "900",
                "current_proportion_wet": "0.10",
                "wet_month_flag": "True",
            },
        ]

        enriched = self.module.add_derived_metrics(rows)
        april = [row for row in enriched if row["month"] == "2018-04"][0]

        self.assertEqual("", april["wet_prop_lag_1m"])
        self.assertEqual("0", april["wet_prop_lag_3m"])
        self.assertEqual("0.005", april["wet_prop_trailing_3m"])
        self.assertEqual("", april["novel_after_dry_flag"])
        self.assertEqual("", april["dry_spell_length_prior"])
        self.assertEqual("1", april["cumulative_wet_months_12m"])
        self.assertEqual("derived_partial_history", april["derived_metric_status"])

    def test_stable_grid_hash_is_order_independent(self):
        rows = [
            {"support_id": "s2", "month": "2018-01", "row_status": "computed", "asset_key_hash": "b"},
            {"support_id": "s1", "month": "2018-01", "row_status": "computed", "asset_key_hash": "a"},
        ]
        shuffled = list(reversed(rows))

        self.assertEqual(
            self.module.stable_grid_hash(rows, ["support_id", "month", "row_status", "asset_key_hash"]),
            self.module.stable_grid_hash(shuffled, ["support_id", "month", "row_status", "asset_key_hash"]),
        )

    def test_raw_source_extensions_are_excluded_from_committed_outputs(self):
        self.assertTrue(self.module.is_blocked_raw_extension(Path("raw/listing.json")))
        self.assertTrue(self.module.is_blocked_raw_extension(Path("intermediate/mask.npy")))
        self.assertTrue(self.module.is_blocked_raw_extension(Path("raw/scene.tif")))
        self.assertFalse(self.module.is_blocked_raw_extension(Path("docs/direct_s3_full_window_hydrology_019_series.csv")))


if __name__ == "__main__":
    unittest.main()
