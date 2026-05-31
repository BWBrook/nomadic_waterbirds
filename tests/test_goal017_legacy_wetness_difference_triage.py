import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO / "scripts" / "legacy_wetness_difference_triage_017.py"


def load_module():
    if not SCRIPT_PATH.exists():
        raise AssertionError(f"missing script under test: {SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("legacy_wetness_difference_triage_017", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal017LegacyWetnessDifferenceTriageTests(unittest.TestCase):
    def test_select_target_rows_keeps_only_wetness_diff_rows(self):
        module = load_module()
        rows = [
            {"support_id": "s2", "month": "2024-12", "reference_source": "goal007", "comparison_status": "within_tolerance"},
            {"support_id": "s1", "month": "2022-11", "reference_source": "goal007", "comparison_status": "wetness_diff"},
            {"support_id": "s3", "month": "2018-01", "reference_source": "goal009", "comparison_status": "wetness_diff"},
        ]

        selected = module.select_target_rows(rows)

        self.assertEqual([(row["support_id"], row["month"]) for row in selected], [("s3", "2018-01"), ("s1", "2022-11")])

    def test_numeric_delta_reports_absolute_and_relative_difference(self):
        module = load_module()

        delta = module.numeric_delta("current_wet_area_m2", "125.5", "100.0")

        self.assertEqual(delta["abs_difference"], 25.5)
        self.assertEqual(delta["signed_difference"], 25.5)
        self.assertEqual(delta["relative_difference"], 0.255)

    def test_classification_labels_rounding_only_wetness_difference(self):
        module = load_module()
        tolerances = {"rounding_area_m2_abs": 25.0, "rounding_fraction_abs": 0.0000015}
        computed = {
            "status": "computed_direct_s3_metrics",
            "geometry_hash_sha256": "abc",
            "n_pixel_u": "10",
            "valid_support_area_m2": "9000",
            "current_wet_area_m2": "100.000002",
            "current_proportion_wet": "0.100001",
            "wet_pixel_observation_count": "5",
            "dry_pixel_observation_count": "5",
            "quality_flag": "quality_high",
            "wet_month_flag": "True",
            "skipped_scene_count": "0",
        }
        reference = dict(computed, status="computed_event_window_metrics", current_wet_area_m2="100.0", current_proportion_wet="0.100000")

        classification = module.classify_root_cause(computed, reference, {}, tolerances)

        self.assertEqual(classification["root_cause_class"], "tolerance_or_rounding_only")

    def test_classification_uses_insufficient_reference_when_legacy_lacks_item_evidence(self):
        module = load_module()
        tolerances = {"rounding_area_m2_abs": 25.0, "rounding_fraction_abs": 0.0000015}
        computed = {
            "status": "computed_direct_s3_metrics",
            "geometry_hash_sha256": "abc",
            "n_pixel_u": "10",
            "valid_support_area_m2": "9000",
            "current_wet_area_m2": "5000",
            "current_proportion_wet": "0.555556",
            "wet_pixel_observation_count": "100",
            "dry_pixel_observation_count": "80",
            "quality_flag": "quality_high",
            "wet_month_flag": "True",
            "skipped_scene_count": "0",
            "readable_scene_count": "4",
        }
        reference = dict(
            computed,
            status="computed_event_window_metrics",
            current_wet_area_m2="4500",
            current_proportion_wet="0.500000",
            wet_pixel_observation_count="95",
            readable_scene_count="8",
        )
        item_delta = {"reference_asset_key_hash": "", "reference_path_rows": "", "readable_scene_count_delta": "-4"}

        classification = module.classify_root_cause(computed, reference, item_delta, tolerances)

        self.assertEqual(classification["root_cause_class"], "insufficient_reference_evidence")
        self.assertIn("legacy reference lacks item/path-row hashes", classification["evidence_basis"])

    def test_root_cause_vocabulary_and_schemas_cover_goal_contract(self):
        module = load_module()

        self.assertTrue(module.REQUIRED_ROOT_CAUSES.issubset(module.ROOT_CAUSE_VOCABULARY))
        self.assertTrue(
            {
                "candidate_id",
                "support_id",
                "month",
                "reference_source",
                "root_cause_class",
                "evidence_basis",
                "scale_up_recommendation",
            }.issubset(set(module.audit_fieldnames()))
        )
        self.assertTrue(
            {
                "support_id",
                "month",
                "reference_source",
                "computed_path_rows",
                "reference_readable_scene_count",
                "computed_readable_scene_count",
                "item_delta_status",
            }.issubset(set(module.item_delta_fieldnames()))
        )
        self.assertTrue(
            {
                "support_id",
                "month",
                "reference_source",
                "field",
                "computed_value",
                "reference_value",
                "abs_difference",
                "difference_class",
            }.issubset(set(module.metric_delta_fieldnames()))
        )

    def test_raw_source_extensions_are_blocked_from_committed_outputs(self):
        module = load_module()

        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/legacy_wetness_difference_triage_017/raw/stac.json")))
        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/legacy_wetness_difference_triage_017/raw/scene.tif")))
        self.assertTrue(module.is_blocked_raw_extension(Path("artifacts/legacy_wetness_difference_triage_017/intermediate/cache.npy")))
        self.assertFalse(module.is_blocked_raw_extension(Path("docs/legacy_wetness_difference_triage_017_audit.csv")))


if __name__ == "__main__":
    unittest.main()
