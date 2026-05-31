import importlib.util
import io
import urllib.error
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "official_support_hydrology_005.py"


def load_module():
    spec = importlib.util.spec_from_file_location("official_support_hydrology_005", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://example.test/stac/search", code, "status", hdrs={}, fp=io.BytesIO(b""))


def no_wait(_seconds: float) -> None:
    return None


def retry_config(max_attempts: int = 3) -> dict:
    return {
        "retry_policy": {
            "max_attempts": max_attempts,
            "initial_delay_seconds": 0,
            "backoff_multiplier": 1,
            "max_delay_seconds": 0,
            "jitter_fraction": 0,
        }
    }


class Goal009StacResilienceTests(unittest.TestCase):
    def test_classifies_http_503_as_transient_stac_endpoint_failure(self):
        module = load_module()

        classification = module.classify_remote_failure(http_error(503), "dea_stac_search")

        self.assertTrue(classification["transient"])
        self.assertEqual(classification["failure_class"], "transient_endpoint_failure")
        self.assertEqual(classification["status_code"], 503)

    def test_classifies_http_503_gdal_message_as_transient_asset_read_failure(self):
        module = load_module()
        error = RuntimeError("GDAL warp failed: HTTP response code: 503")

        classification = module.classify_remote_failure(error, "remote_cog_read")

        self.assertTrue(classification["transient"])
        self.assertEqual(classification["failure_class"], "transient_asset_read_failure")
        self.assertEqual(classification["status_code"], 503)

    def test_retry_remote_operation_retries_transient_failures_and_records_attempts(self):
        module = load_module()
        module.reset_retry_audit_log()
        attempts = []

        def operation():
            attempts.append(len(attempts) + 1)
            if len(attempts) < 3:
                raise http_error(503)
            return {"features": []}

        result = module.retry_remote_operation(
            "dea_stac_search",
            {"month": "2022-11"},
            retry_config(),
            operation,
            sleep_func=no_wait,
            random_func=lambda: 0,
        )

        self.assertEqual(result, {"features": []})
        self.assertEqual(attempts, [1, 2, 3])
        events = module.retry_audit_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["attempt_count"], 3)
        self.assertEqual(events[0]["final_status"], "success_after_retry")
        self.assertEqual(events[0]["failure_class"], "transient_endpoint_failure")

    def test_retry_remote_operation_does_not_retry_deterministic_http_404(self):
        module = load_module()
        module.reset_retry_audit_log()
        attempts = []

        def operation():
            attempts.append(len(attempts) + 1)
            raise http_error(404)

        with self.assertRaises(urllib.error.HTTPError):
            module.retry_remote_operation(
                "dea_stac_search",
                {"month": "2022-11"},
                retry_config(),
                operation,
                sleep_func=no_wait,
                random_func=lambda: 0,
            )

        self.assertEqual(attempts, [1])
        events = module.retry_audit_events()
        self.assertEqual(events[0]["attempt_count"], 1)
        self.assertEqual(events[0]["final_status"], "deterministic_failure")
        self.assertEqual(events[0]["failure_class"], "deterministic_endpoint_failure")

    def test_stac_search_uses_configured_retry_policy(self):
        module = load_module()
        module.reset_retry_audit_log()
        original_post_json = module.post_json
        calls = []

        def fake_post_json(_url, _payload, _timeout=90):
            calls.append(len(calls) + 1)
            if len(calls) == 1:
                raise http_error(503)
            return {"features": [], "type": "FeatureCollection"}

        module.post_json = fake_post_json
        try:
            config = {
                "dea_collection": "ga_ls_wo_3",
                "dea_stac_search_url": "https://example.test/stac/search",
                "stac_limit": 10,
                **retry_config(),
            }
            result = module.stac_search(config, (147.47, 147.49, -29.79, -29.77), "2022-11")
        finally:
            module.post_json = original_post_json

        self.assertEqual(calls, [1, 2])
        self.assertEqual(result["features"], [])
        self.assertEqual(result["_query_payload"]["datetime"], "2022-11-01T00:00:00Z/2022-12-01T00:00:00Z")
        self.assertEqual(module.retry_audit_events()[0]["attempt_count"], 2)


if __name__ == "__main__":
    unittest.main()
