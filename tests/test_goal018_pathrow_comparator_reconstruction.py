import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "pathrow_comparator_reconstruction_018.py"


def load_module():
    spec = importlib.util.spec_from_file_location("pathrow_comparator_reconstruction_018", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal018PathrowComparatorReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_select_material_targets_keeps_exact_goal017_rows(self):
        rows = [
            {
                "candidate_id": "NWB004",
                "support_id": "nwb004_ramsar_component_369",
                "month": "2018-01",
                "reference_source": "goal009_full_window_context",
                "root_cause_class": "insufficient_reference_evidence",
                "scale_up_recommendation": "build comparator",
            },
            {
                "candidate_id": "NWB004",
                "support_id": "nwb004_ramsar_component_354",
                "month": "2022-11",
                "reference_source": "goal007_legacy_event_window",
                "root_cause_class": "tolerance_or_rounding_only",
                "scale_up_recommendation": "control",
            },
        ]

        selected = self.module.select_target_rows(rows, include_controls=False)

        self.assertEqual(1, len(selected))
        self.assertEqual("material", selected[0]["target_role"])
        self.assertEqual("insufficient_reference_evidence", selected[0]["goal017_root_cause_class"])
        self.assertIn("build comparator", selected[0]["selection_reason"])

    def test_optional_controls_are_labelled_without_changing_material_count(self):
        rows = [
            {
                "candidate_id": "NWB004",
                "support_id": "nwb004_ramsar_component_369",
                "month": "2018-01",
                "reference_source": "goal009_full_window_context",
                "root_cause_class": "insufficient_reference_evidence",
                "scale_up_recommendation": "material",
            },
            {
                "candidate_id": "NWB005",
                "support_id": "nwb005_ramsar_ref791",
                "month": "2022-11",
                "reference_source": "goal007_legacy_event_window",
                "root_cause_class": "tolerance_or_rounding_only",
                "scale_up_recommendation": "control",
            },
        ]

        selected = self.module.select_target_rows(rows, include_controls=True)

        self.assertEqual(2, len(selected))
        self.assertEqual(1, sum(row["target_role"] == "material" for row in selected))
        self.assertEqual(1, sum(row["target_role"] == "control" for row in selected))

    def test_path_rows_by_support_groups_sorted_complete_pathrows(self):
        rows = [
            {"support_id": "a", "path_row": "094/085", "coverage_status": "complete"},
            {"support_id": "a", "path_row": "093/085", "coverage_status": "complete"},
            {"support_id": "b", "path_row": "095/080", "coverage_status": "complete"},
        ]

        grouped = self.module.path_rows_by_support(rows)

        self.assertEqual(["093/085", "094/085"], grouped["a"])
        self.assertEqual(["095/080"], grouped["b"])

    def test_compare_item_sets_detects_match_and_mismatch(self):
        direct = {
            "item_count": 2,
            "asset_key_hash": "asset-hash",
            "item_id_hash": "item-hash",
        }
        comparator = {
            "item_count": 2,
            "asset_key_hash": "asset-hash",
            "item_id_hash": "item-hash",
        }

        matched = self.module.compare_item_sets(direct, comparator)
        mismatched = self.module.compare_item_sets(direct, {**comparator, "item_count": 1})

        self.assertEqual("item_sets_match", matched["comparison_status"])
        self.assertEqual("item_set_mismatch", mismatched["comparison_status"])
        self.assertFalse(matched["current_direct_s3_defect"])

    def test_route_status_and_readiness_vocabulary_cover_goal_contract(self):
        self.assertTrue(self.module.REQUIRED_ROUTE_STATUSES.issubset(self.module.ROUTE_STATUS_VOCABULARY))
        self.assertTrue(self.module.REQUIRED_READINESS_CLASSES.issubset(self.module.READINESS_CLASS_VOCABULARY))

        ready = self.module.classify_readiness(
            route_status="stac_pathrow_matches_direct_s3",
            comparison_status="item_sets_match",
            direct_matches_goal016=True,
        )
        provenance_only = self.module.classify_readiness(
            route_status="stac_unavailable_direct_s3_provenance_only",
            comparison_status="item_sets_match",
            direct_matches_goal016=True,
        )
        mismatch = self.module.classify_readiness(
            route_status="stac_available_item_mismatch",
            comparison_status="item_set_mismatch",
            direct_matches_goal016=True,
        )

        self.assertEqual("ready_for_full_window_direct_s3", ready["readiness_class"])
        self.assertEqual("ready_with_legacy_baseline_retired", provenance_only["readiness_class"])
        self.assertEqual("not_ready_item_mismatch", mismatch["readiness_class"])

    def test_output_schemas_and_raw_extension_policy_cover_deliverables(self):
        self.assertIn("target_role", self.module.targets_fieldnames())
        self.assertIn("route_status", self.module.item_sets_fieldnames())
        self.assertIn("comparison_status", self.module.comparison_fieldnames())
        self.assertIn("readiness_class", self.module.readiness_fieldnames())

        self.assertTrue(self.module.is_blocked_raw_extension(Path("raw/stac_items.json")))
        self.assertTrue(self.module.is_blocked_raw_extension(Path("intermediate/probe.npy")))
        self.assertFalse(self.module.is_blocked_raw_extension(Path("docs/pathrow_comparator_reconstruction_018_report.md")))


if __name__ == "__main__":
    unittest.main()
