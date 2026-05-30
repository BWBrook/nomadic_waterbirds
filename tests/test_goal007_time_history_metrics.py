import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "event_window_hydrology_007.py"


def load_module():
    spec = importlib.util.spec_from_file_location("event_window_hydrology_007", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal007TimeHistoryMetricTests(unittest.TestCase):
    def test_time_history_metrics_preserve_lags_novelty_and_dry_run_context(self):
        module = load_module()
        rows = [
            {
                "support_id": "support_a",
                "month": "2020-01",
                "status": "computed_event_window_metrics",
                "quality_flag": "quality_fail",
                "current_proportion_wet": 0.90,
                "current_wet_area_m2": 9000.0,
                "wet_month_flag": "",
            },
            {
                "support_id": "support_a",
                "month": "2020-02",
                "status": "computed_event_window_metrics",
                "quality_flag": "quality_high",
                "current_proportion_wet": 0.01,
                "current_wet_area_m2": 100.0,
                "wet_month_flag": False,
            },
            {
                "support_id": "support_a",
                "month": "2020-03",
                "status": "computed_event_window_metrics",
                "quality_flag": "quality_minimum",
                "current_proportion_wet": 0.02,
                "current_wet_area_m2": 200.0,
                "wet_month_flag": False,
            },
            {
                "support_id": "support_a",
                "month": "2020-04",
                "status": "computed_event_window_metrics",
                "quality_flag": "quality_high",
                "current_proportion_wet": 0.20,
                "current_wet_area_m2": 2000.0,
                "wet_month_flag": True,
            },
        ]

        enriched = module.add_time_history_metrics(rows)
        april = enriched[-1]

        self.assertAlmostEqual(april["wet_prop_lag_1m"], 0.02)
        self.assertAlmostEqual(april["wet_area_lag_1m"], 200.0)
        self.assertAlmostEqual(april["wet_prop_lag_3m"], 0.90)
        self.assertAlmostEqual(april["wet_prop_trailing_3m"], 0.015)
        self.assertAlmostEqual(april["wetting_delta_1m"], 0.18)
        self.assertAlmostEqual(april["wetting_delta_3m"], 0.185)
        self.assertEqual(april["consecutive_dry_months_prior"], 2)
        self.assertEqual(april["dry_spell_length_prior"], 2)
        self.assertTrue(april["novel_after_dry_flag"])
        self.assertEqual(april["consecutive_wet_months"], 1)
        self.assertEqual(april["cumulative_wet_months_12m"], 1)
        self.assertAlmostEqual(april["drying_velocity_1m"], -0.18)
        self.assertAlmostEqual(april["drying_velocity_3m"], -0.185)

    def test_unresolved_named_support_count_tracks_no_geometry_rows(self):
        module = load_module()
        rows = [
            {
                "support_id": "parent",
                "support_type": "official_ramsar_named_complex_geometry",
                "evidence_status": "official_parent_ramsar_support",
                "included_in_event_window": "yes",
            },
            {
                "support_id": "clear_lake",
                "support_type": "named_open_water_unresolved",
                "evidence_status": "name_and_within_parent_verified_no_geometry",
                "included_in_event_window": "no",
            },
            {
                "support_id": "lake_wyara",
                "support_type": "diwa_named_lake",
                "evidence_status": "official_named_geometry_linked_to_dea_waterbody",
                "included_in_event_window": "no",
            },
        ]

        self.assertEqual(module.count_unresolved_named_supports(rows), 1)


if __name__ == "__main__":
    unittest.main()
