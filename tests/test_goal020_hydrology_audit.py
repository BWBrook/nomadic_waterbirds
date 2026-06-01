import csv
import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "audit_direct_s3_full_window_hydrology_020.py"
CONFIG = REPO / "settings" / "audit_direct_s3_full_window_hydrology_020.json"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError(f"missing script under test: {SCRIPT}")
    spec = importlib.util.spec_from_file_location("audit_direct_s3_full_window_hydrology_020", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Goal020HydrologyAuditTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.config = json.loads(CONFIG.read_text(encoding="utf-8"))

        goal019_manifest = json.loads(
            (REPO / self.config["inputs"]["goal019_manifest_json"]).read_text(encoding="utf-8")
        )
        outputs = self.config["outputs"]
        self.goal019_series = read_csv(REPO / self.config["inputs"]["goal019_series_csv"])
        self.goal019_item_sets = read_csv(REPO / self.config["inputs"]["goal019_item_sets_csv"])
        self.goal019_summary = read_csv(REPO / self.config["inputs"]["goal019_summary_csv"])
        self.goal020_manifest = json.loads((REPO / outputs["manifest_json"]).read_text(encoding="utf-8"))
        self.goal020_readiness = read_csv(REPO / outputs["readiness_csv"])
        self.goal020_quality_fail = read_csv(REPO / outputs["quality_fail_csv"])
        self.goal020_support_summary = read_csv(REPO / outputs["support_summary_csv"])
        self.goal020_month_summary = read_csv(REPO / outputs["month_summary_csv"])

    def test_month_window_and_grid_shape_match_expected_counts(self):
        start = self.config["month_window"]["start"]
        end = self.config["month_window"]["end"]
        months = self.module.month_sequence(start, end)

        supports = sorted({row["support_id"] for row in self.goal019_series})
        expected_keys = {(row["support_id"], row["month"]) for row in self.goal019_series}

        self.assertEqual(len(months), self.config["expected_month_count"])
        self.assertEqual(months[0], start)
        self.assertEqual(months[-1], end)
        self.assertEqual(len(supports), self.config["expected_support_count"])
        self.assertEqual(len(expected_keys), self.config["expected_row_count"])
        for support_id in supports:
            for month in months:
                self.assertIn((support_id, month), expected_keys)

    def test_manifest_json_schemas_and_status(self):
        expected = {
            "goal",
            "manifest_type",
            "created_at_utc",
            "goal019_manifest",
            "goal020_readiness_decision",
            "readiness_class_counts",
            "quality_fail_reasons",
            "quality_fail_count",
        }

        self.assertTrue(expected.issubset(self.goal020_manifest))
        self.assertEqual(self.config["goal"], self.goal020_manifest["goal"])

    def test_csv_schemas_and_row_counts(self):
        quality_fail_fields = {
            "support_id",
            "month",
            "candidate_id",
            "support_type",
            "quality_flag",
            "quality_fail_reason",
            "bird_linkage_readiness",
            "recommended_use",
            "caveat_code",
        }
        readiness_fields = {
            "support_id",
            "month",
            "quality_flag",
            "quality_fail_reason",
            "bird_linkage_readiness",
            "recommended_use",
            "caveat_code",
            "row_status",
            "item_set_status",
            "derived_metric_status",
            "regional_metric_status",
        }
        support_summary_fields = {
            "support_id",
            "row_count",
            "core_eligible_count",
            "core_eligible_with_caveat_count",
            "sensitivity_only_count",
            "exclude_count",
            "quality_fail_count",
        }
        month_summary_fields = {
            "month",
            "row_count",
            "core_eligible_count",
            "core_eligible_with_caveat_count",
            "sensitivity_only_count",
            "exclude_count",
            "quality_fail_count",
        }

        self.assertTrue(quality_fail_fields.issubset(set(self.goal020_quality_fail[0])) )
        self.assertTrue(readiness_fields.issubset(set(self.goal020_readiness[0])))
        self.assertTrue(support_summary_fields.issubset(set(self.goal020_support_summary[0])))
        self.assertTrue(month_summary_fields.issubset(set(self.goal020_month_summary[0])))

        self.assertEqual(self.config["expected_row_count"], len(self.goal020_readiness))
        self.assertEqual(self.config["expected_row_count"], len({(row["support_id"], row["month"]) for row in self.goal020_readiness}))

    def test_quality_fail_rows_visible_classified_and_expected_count(self):
        self.assertEqual(self.config["quality_fail_expected_count"], len(self.goal020_quality_fail))
        reasons = Counter(row["quality_fail_reason"] for row in self.goal020_quality_fail)

        self.assertEqual(21, reasons["low_clear_fraction"])
        self.assertEqual(2, reasons["low_support_area_after_mask"])

        for row in self.goal020_quality_fail:
            self.assertEqual("quality_fail", row["quality_flag"])
            self.assertEqual("sensitivity_only", row["bird_linkage_readiness"])
            self.assertEqual("sensitivity_only", row["recommended_use"])

    def test_readiness_class_counts_and_classification_integrity(self):
        readiness_counts = Counter(row["bird_linkage_readiness"] for row in self.goal020_readiness)

        self.assertEqual(820, readiness_counts["core_eligible"])
        self.assertEqual(81, readiness_counts["core_eligible_with_caveat"])
        self.assertEqual(23, readiness_counts["sensitivity_only"])

        for row in self.goal020_readiness:
            self.assertIn(row["bird_linkage_readiness"], self.module.READINESS_CLASS_VOCABULARY)
            self.assertTrue(row["bird_linkage_readiness"] in row["recommended_use"] or row["recommended_use"].startswith("core") or row["recommended_use"] in {"sensitivity_only", "exclude_before_bird_linkage"})

    def test_goal019_manifest_hash_consistency_check(self):
        checks = {
            "expected_support_count": self.config["expected_support_count"],
            "expected_month_count": self.config["expected_month_count"],
            "expected_row_count": self.config["expected_row_count"],
            "quality_fail_expected_count": self.config["quality_fail_expected_count"],
            "expected_support_types": self.config["expected_support_types"],
            "month_window": self.config["month_window"],
            **self.config["checks"],
        }

        goal019_manifest = json.loads((REPO / self.config["inputs"]["goal019_manifest_json"]).read_text(encoding="utf-8"))
        self.module.validate_inputs(self.goal019_series, self.goal019_item_sets, self.goal019_summary, goal019_manifest, checks)

        self.assertEqual(self.goal020_manifest["goal019_row_count"], goal019_manifest["row_count"])
        self.assertEqual(self.goal020_manifest["goal019_support_count"], goal019_manifest["support_count"])
        self.assertEqual(self.goal020_manifest["goal019_series_row_count"], self.config["expected_row_count"])

        self.assertEqual(
            goal019_manifest["series_row_hash"],
            self.module.stable_row_hash(self.goal019_series, self.module.GOAL019_SERIES_HASH_FIELDS),
        )
        self.assertEqual(
            goal019_manifest["item_set_row_hash"],
            self.module.stable_row_hash(self.goal019_item_sets, self.module.ITEM_SET_HASH_FIELDS),
        )

    def test_quality_fail_reason_and_row_status_logic(self):
        checks = self.config["checks"]
        row_low_fraction = {
            "support_id": "nwb004_ramsar_component_369",
            "month": "2020-04",
            "clear_obs_fraction": "0.10",
            "support_area_m2": "100000",
            "valid_support_area_m2": "60000",
            "n_scene_m": "2",
            "current_wet_area_m2": "100",
            "derived_metric_status": "derived_with_available_history",
            "regional_metric_status": "computed_all_current_supports_excluding_focal",
        }
        row_low_support = {
            "support_id": "nwb004_ramsar_component_369",
            "month": "2020-05",
            "clear_obs_fraction": "0.4",
            "support_area_m2": "100000",
            "valid_support_area_m2": "1000",
            "n_scene_m": "2",
            "current_wet_area_m2": "100",
            "derived_metric_status": "derived_with_available_history",
            "regional_metric_status": "computed_all_current_supports_excluding_focal",
        }

        self.assertEqual("low_clear_fraction", self.module.quality_fail_reason(row_low_fraction, checks))
        self.assertEqual("low_support_area_after_mask", self.module.quality_fail_reason(row_low_support, checks))

    def test_raw_extension_blocklist(self):
        self.assertTrue(self.module.is_blocked_raw_extension(Path("raw/listing.json")))
        self.assertTrue(self.module.is_blocked_raw_extension(Path("intermediate/mask.npy")))
        self.assertTrue(self.module.is_blocked_raw_extension(Path("artifacts/direct_s3_full_window_hydrology_019/raw/listing.json")))
        self.assertFalse(self.module.is_blocked_raw_extension(Path("docs/direct_s3_full_window_hydrology_019_series.csv")))


if __name__ == "__main__":
    unittest.main()
