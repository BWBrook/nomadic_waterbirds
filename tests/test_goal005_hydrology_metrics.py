import importlib.util
import unittest
from pathlib import Path

import numpy as np


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "official_support_hydrology_005.py"


def load_module():
    spec = importlib.util.spec_from_file_location("official_support_hydrology_005", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal005HydrologyMetricTests(unittest.TestCase):
    def test_monthly_metrics_aggregate_scene_observations_by_pixel(self):
        module = load_module()
        support_mask = np.array([[True, True], [True, False]])
        scene_values = [
            np.array([[0, 128], [64, 0]], dtype=np.uint8),
            np.array([[128, 128], [0, 0]], dtype=np.uint8),
        ]

        metrics = module.summarise_support_month(scene_values, support_mask)

        self.assertEqual(metrics["n_scene_m"], 2)
        self.assertEqual(metrics["n_pixel_u"], 3)
        self.assertEqual(metrics["clear_obs_count"], 5)
        self.assertEqual(metrics["invalid_obs_count"], 1)
        self.assertAlmostEqual(metrics["clear_obs_fraction"], 5 / 6)
        self.assertEqual(metrics["current_wet_area_m2"], 1350.0)
        self.assertEqual(metrics["valid_support_area_m2"], 2700)
        self.assertAlmostEqual(metrics["current_proportion_wet"], 0.5)
        self.assertEqual(metrics["wet_pixel_observation_count"], 3)
        self.assertEqual(metrics["dry_pixel_observation_count"], 2)
        self.assertEqual(metrics["cloud_count"], 1)
        self.assertEqual(metrics["quality_flag"], "quality_high")
        self.assertTrue(metrics["wet_month_flag"])


if __name__ == "__main__":
    unittest.main()
