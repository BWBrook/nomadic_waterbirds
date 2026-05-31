import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hydrology_acquisition_route_probe_011.py"


def load_module():
    spec = importlib.util.spec_from_file_location("hydrology_acquisition_route_probe_011", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal011HydrologyAcquisitionRouteTests(unittest.TestCase):
    def test_estimate_query_patterns_counts_support_candidate_and_month_cache_units(self):
        module = load_module()
        rows = [
            {"support_id": "s1", "candidate_id": "c1", "month": "2022-11"},
            {"support_id": "s2", "candidate_id": "c1", "month": "2022-11"},
            {"support_id": "s3", "candidate_id": "c2", "month": "2022-11"},
            {"support_id": "s1", "candidate_id": "c1", "month": "2022-12"},
        ]

        estimates = module.estimate_query_patterns(rows, max_attempts=3)
        by_unit = {row["workflow_unit"]: row for row in estimates}

        self.assertEqual(by_unit["support_month_status_quo"]["estimated_live_stac_searches"], 4)
        self.assertEqual(by_unit["support_month_status_quo"]["estimated_max_http_attempts"], 12)
        self.assertEqual(by_unit["candidate_month_cache"]["estimated_live_stac_searches"], 3)
        self.assertEqual(by_unit["month_support_set_cache"]["estimated_live_stac_searches"], 2)
        self.assertEqual(by_unit["candidate_month_cache"]["search_reduction_percent"], 25.0)
        self.assertEqual(by_unit["month_support_set_cache"]["cache_key"], "collection|month|support_set_bbox_hash")

    def test_s3_url_from_href_converts_dea_s3_href_to_public_https(self):
        module = load_module()
        href = (
            "s3://dea-public-data/derivative/ga_ls_wo_3/1-6-0/093/080/"
            "2022/11/03/ga_ls_wo_3_093080_2022-11-03_final_water.tif"
        )

        self.assertEqual(
            module.s3_href_to_https(href),
            (
                "https://dea-public-data.s3.ap-southeast-2.amazonaws.com/"
                "derivative/ga_ls_wo_3/1-6-0/093/080/2022/11/03/"
                "ga_ls_wo_3_093080_2022-11-03_final_water.tif"
            ),
        )

    def test_s3_list_url_uses_bounded_max_keys(self):
        module = load_module()

        self.assertEqual(
            module.s3_list_url("derivative/ga_ls_wo_3/1-6-0/093/080/2022/11/", max_keys=3),
            (
                "https://dea-public-data.s3.ap-southeast-2.amazonaws.com/"
                "?list-type=2&prefix=derivative%2Fga_ls_wo_3%2F1-6-0%2F093%2F080%2F2022%2F11%2F&max-keys=3"
            ),
        )


if __name__ == "__main__":
    unittest.main()
