import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "narran_subunit_evidence_008.py"


def load_module():
    spec = importlib.util.spec_from_file_location("narran_subunit_evidence_008", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal008NarranCrosswalkTests(unittest.TestCase):
    def test_named_narran_candidates_remain_unresolved_without_geometry_or_dea_uid(self):
        module = load_module()

        rows = module.build_unresolved_named_candidate_rows("nwb002_ramsar_ref1291")
        by_name = {row["display_name"]: row for row in rows}

        for expected in [
            "Clear Lake",
            "Back Lake",
            "Long Arm",
            "Narran lignum/channelised floodplain",
        ]:
            self.assertIn(expected, by_name)
            self.assertEqual(by_name[expected]["included_in_event_window"], "no")
            self.assertIn("unresolved", by_name[expected]["geometry_status"])
            self.assertEqual(by_name[expected]["related_dea_waterbody_uid"], "")


if __name__ == "__main__":
    unittest.main()
