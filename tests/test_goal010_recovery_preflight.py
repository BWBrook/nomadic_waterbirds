import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "stac_recovery_preflight_010.py"


def load_module():
    spec = importlib.util.spec_from_file_location("stac_recovery_preflight_010", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(support_id, month, status="blocked_event_window_processing_error"):
    return {
        "support_id": support_id,
        "month": month,
        "status": status,
        "failure_or_caveat": "transient_endpoint_failure: exhausted retry",
    }


class Goal010RecoveryPreflightTests(unittest.TestCase):
    def test_select_preflight_sample_covers_supports_and_periods_from_blocked_rows(self):
        module = load_module()
        rows = []
        for support_id in ["a", "b", "c"]:
            rows.extend(
                [
                    row(support_id, "2018-01"),
                    row(support_id, "2019-07"),
                    row(support_id, "2022-11"),
                    row(support_id, "2024-12"),
                    row(support_id, "2024-03", status="computed_event_window_metrics"),
                ]
            )

        sample = module.select_preflight_sample(rows, target_size=9)

        self.assertEqual(len(sample), 9)
        self.assertEqual({item["support_id"] for item in sample}, {"a", "b", "c"})
        self.assertEqual({item["sample_period"] for item in sample}, {"early", "wet_flood", "recent"})
        self.assertTrue(all(item["status"] != "computed_event_window_metrics" for item in sample))
        self.assertEqual([item["sample_order"] for item in sample], list(range(1, 10)))

    def test_launch_decision_requires_endpoint_availability_and_eighty_percent_success(self):
        module = load_module()
        endpoint_probes = [{"host_label": "mac-mini", "endpoint_status": "available"}]
        rows = [{"status": "computed_preflight_metrics", "support_id": f"s{i}", "sample_period": "early"} for i in range(8)]
        rows.extend(
            [
                {"status": "blocked_preflight_processing_error", "support_id": "s8", "sample_period": "recent"},
                {"status": "blocked_preflight_processing_error", "support_id": "s9", "sample_period": "wet_flood"},
            ]
        )

        decision = module.launch_decision(endpoint_probes, rows)

        self.assertEqual(decision["decision"], "launch_recovery")
        self.assertEqual(decision["sample_size"], 10)
        self.assertEqual(decision["computed_count"], 8)
        self.assertEqual(decision["computed_fraction"], 0.8)

    def test_launch_decision_stops_on_clustered_failures_even_if_global_rate_passes(self):
        module = load_module()
        endpoint_probes = [{"host_label": "deep-server-ts", "endpoint_status": "available"}]
        rows = [{"status": "computed_preflight_metrics", "support_id": f"s{i}", "sample_period": "early"} for i in range(8)]
        rows.extend(
            [
                {"status": "blocked_preflight_processing_error", "support_id": "clustered", "sample_period": "recent"},
                {"status": "blocked_preflight_processing_error", "support_id": "clustered", "sample_period": "wet_flood"},
            ]
        )

        decision = module.launch_decision(endpoint_probes, rows)

        self.assertEqual(decision["decision"], "stop_service_stability_blocker")
        self.assertIn("clustered_support_failures", decision["blockers"])

    def test_launch_decision_stops_when_endpoint_probe_is_unavailable(self):
        module = load_module()
        endpoint_probes = [{"host_label": "deep-server-ts", "endpoint_status": "service_unavailable_503"}]
        rows = [{"status": "computed_preflight_metrics", "support_id": "s1", "sample_period": "early"}]

        decision = module.launch_decision(endpoint_probes, rows)

        self.assertEqual(decision["decision"], "stop_service_stability_blocker")
        self.assertIn("endpoint_probe_unavailable", decision["blockers"])


if __name__ == "__main__":
    unittest.main()
