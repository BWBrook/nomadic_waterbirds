import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "subunit_hydrology_006.py"


def load_module():
    spec = importlib.util.spec_from_file_location("subunit_hydrology_006", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal006SubunitRegistryTests(unittest.TestCase):
    def test_ramsar_component_rows_preserve_parent_and_selection_status(self):
        module = load_module()
        candidate = {
            "candidate_id": "NWB004",
            "candidate_name": "Kerang Wetlands",
            "parent_support_id": "nwb004_ramsar_ref265",
            "selected_ramsar_objectids": [369],
        }
        features = [
            {
                "id": 369,
                "properties": {
                    "OBJECTID": 369,
                    "REFCODE": 265,
                    "RAMSAR_NAME": "Kerang Wetlands",
                    "WETLAND_NAME": "Lake Charm",
                    "AREA_HA": 703.92763352,
                    "SOURCE": "Victorian Ramsar source",
                },
            },
            {
                "id": 370,
                "properties": {
                    "OBJECTID": 370,
                    "REFCODE": 265,
                    "RAMSAR_NAME": "Kerang Wetlands",
                    "WETLAND_NAME": "Lake Cullen",
                    "AREA_HA": 671.61588795,
                    "SOURCE": "Victorian Ramsar source",
                },
            },
        ]

        rows = module.ramsar_component_registry_rows(candidate, features)

        self.assertEqual([row["parent_support_id"] for row in rows], ["nwb004_ramsar_ref265"] * 2)
        self.assertEqual(rows[0]["subunit_id"], "nwb004_ramsar_component_369")
        self.assertEqual(rows[0]["subunit_name"], "Lake Charm")
        self.assertEqual(rows[0]["inclusion_status"], "included_for_subunit_hydrology")
        self.assertEqual(rows[1]["subunit_id"], "nwb004_ramsar_component_370")
        self.assertEqual(rows[1]["inclusion_status"], "retained_for_later")
        self.assertEqual(rows[1]["subunit_type"], "ramsar_component")


if __name__ == "__main__":
    unittest.main()
