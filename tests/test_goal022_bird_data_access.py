"""Focused tests for Goal 022 bird-data access feasibility deliverables."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "settings" / "bird_data_access_022.json"
VALIDATOR = REPO / "scripts" / "validate_bird_data_access_022.py"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Goal022BirdDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        result = subprocess.run(
            ["python3", str(VALIDATOR)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        cls.stdout = result.stdout
        cls.stderr = result.stderr
        cls.returncode = result.returncode
        if result.returncode == 0:
            cls.manifest = json.loads((REPO / cls.config["files"]["manifest_json"]).read_text(encoding="utf-8"))
        else:
            cls.manifest = {}

    def test_validator_runs(self) -> None:
        self.assertEqual(self.returncode, 0, msg=f"stdout:\n{self.stdout}\nstderr:\n{self.stderr}")

    def test_goal020_and_goal021_carry_forward(self) -> None:
        g020 = self.config["goal020_reference"]
        readiness = read_csv(REPO / g020["readiness_rows_path"])
        self.assertEqual(len(readiness), g020["expected_row_count"])
        field = "readiness_class" if "readiness_class" in readiness[0] else "bird_linkage_readiness"
        counts = Counter(row[field] for row in readiness)
        self.assertEqual(counts["core_eligible"], g020["expected_core_eligible"])
        self.assertEqual(counts["core_eligible_with_caveat"], g020["expected_core_eligible_with_caveat"])
        self.assertEqual(counts["sensitivity_only"], g020["expected_sensitivity_only"])
        caveats = sum("legacy_stac_comparator_not_obtained" in row.get("caveat_code", "") for row in readiness)
        self.assertEqual(caveats, g020["expected_goal018_legacy_caveat_count"])

        g021 = self.config["goal021_reference"]
        manifest = json.loads((REPO / g021["manifest_path"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["design_goal_status"], g021["expected_status"])

    def test_access_matrix_statuses_and_roles(self) -> None:
        rows = read_csv(REPO / self.config["files"]["access_matrix"])
        status_vocab = set(self.config["csv_schemas"]["access_matrix"]["status_vocab"])
        self.assertTrue({row["decision_status"] for row in rows}.issubset(status_vocab))
        by_stream = {row["stream"]: row for row in rows}
        self.assertEqual(by_stream["eBird"]["decision_status"], "request_ready")
        self.assertIn("EBD", by_stream["eBird"]["key_fields_or_products"])
        self.assertEqual(by_stream["ALA"]["decision_status"], "context_only")
        self.assertIn("absence", by_stream["ALA"]["forbidden_use"].lower())
        self.assertEqual(by_stream["Birdata"]["decision_status"], "needs_clarification")
        self.assertEqual(by_stream["EAWS"]["decision_status"], "needs_clarification")

    def test_ebird_fields_have_required_groups(self) -> None:
        rows = read_csv(REPO / self.config["files"]["ebird_fields"])
        self.assertGreaterEqual(len(rows), self.config["csv_schemas"]["ebird_fields"]["min_rows"])
        groups = {row["field_group"] for row in rows}
        for group in ["checklist_completeness", "effort", "location", "sensitivity", "provenance"]:
            self.assertIn(group, groups)

    def test_manifest_consistency(self) -> None:
        manifest = self.manifest
        self.assertEqual(manifest["goal"], self.config["goal"])
        self.assertEqual(manifest["decision_status"], self.config["decision_status"])
        self.assertEqual(manifest["artifacts"]["access_matrix"]["row_count"], 4)
        self.assertGreaterEqual(manifest["artifacts"]["ebird_fields"]["row_count"], 20)
        self.assertEqual(set(manifest["official_sources_checked"]), set(self.config["required_public_sources"]))

    def test_no_changed_blocked_or_large_files(self) -> None:
        status = subprocess.run(
            ["git", "status", "--short", "--porcelain"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        ).stdout.splitlines()
        blocked = set(self.config["guardrails"]["forbidden_extensions"])
        max_bytes = self.config["guardrails"]["max_changed_file_size_mb"] * 1024 * 1024
        for line in status:
            path = REPO / line[3:]
            self.assertNotIn(path.suffix.lower(), blocked, msg=f"blocked changed file {path}")
            if path.exists() and path.is_file():
                self.assertLessEqual(path.stat().st_size, max_bytes)

    def test_no_unfinished_markers_in_goal022_outputs(self) -> None:
        marker = re.compile(
            r"\b(" + "|".join(["to" + "do", "tb" + "d", "place" + "holder", "fix" + "me", "x" * 3]) + r")\b",
            re.IGNORECASE,
        )
        paths = [
            REPO / self.config["files"]["feasibility_memo"],
            REPO / self.config["files"]["ebird_request_package"],
            REPO / self.config["files"]["birdata_eaws_questions"],
            REPO / self.config["files"]["ala_context_rules"],
            REPO / self.config["files"]["access_matrix"],
            REPO / self.config["files"]["ebird_fields"],
        ]
        for path in paths:
            self.assertIsNone(marker.search(path.read_text(encoding="utf-8")), msg=f"unfinished marker in {path}")


if __name__ == "__main__":
    unittest.main()
