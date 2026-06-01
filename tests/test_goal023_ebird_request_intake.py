"""Focused tests for Goal 023 eBird request-support deliverables."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "settings" / "ebird_request_intake_023.json"
VALIDATOR = REPO / "scripts" / "validate_ebird_request_intake_023.py"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Goal023EbirdRequestIntakeTests(unittest.TestCase):
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

    def test_goal020_goal021_goal022_carry_forward(self) -> None:
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
        goal021_manifest = json.loads((REPO / g021["manifest_path"]).read_text(encoding="utf-8"))
        self.assertEqual(goal021_manifest["design_goal_status"], g021["expected_status"])

        g022 = self.config["goal022_reference"]
        goal022_manifest = json.loads((REPO / g022["manifest_path"]).read_text(encoding="utf-8"))
        self.assertEqual(goal022_manifest["decision_status"], g022["expected_status"])

    def test_submission_boundary_language(self) -> None:
        text = (REPO / self.config["files"]["submission_checklist"]).read_text(encoding="utf-8")
        self.assertIn("nomad did not submit the eBird request", text)
        self.assertIn("must not use Barry's account", text)
        self.assertIn("The final submit/send action requires Barry's direct confirmation", text)
        self.assertIn("I, Barry W. Brook, confirm that the next submit/send action", text)

    def test_request_envelope_is_fixed(self) -> None:
        envelope = self.config["request_envelope"]
        self.assertEqual(envelope["start_date"], "2018-01-01")
        self.assertEqual(envelope["end_date"], "2024-12-31")
        self.assertEqual(envelope["support_count"], 11)
        self.assertEqual(set(envelope["core_hydrology_classes"]), {"core_eligible", "core_eligible_with_caveat"})
        self.assertEqual(envelope["sensitivity_hydrology_class"], "sensitivity_only")
        self.assertIn("provisional", envelope["species_guild_status"])

    def test_qa_contract_schema_and_controlled_vocabularies(self) -> None:
        rows = read_csv(REPO / self.config["files"]["qa_contract"])
        schema = self.config["csv_schemas"]["qa_contract"]
        self.assertGreaterEqual(len(rows), schema["min_rows"])
        self.assertTrue(set(schema["required_columns"]).issubset(rows[0]))
        self.assertTrue({row["stage"] for row in rows}.issubset(set(schema["stage_vocab"])))
        self.assertTrue({row["category"] for row in rows}.issubset(set(schema["category_vocab"])))
        self.assertTrue({row["severity"] for row in rows}.issubset(set(schema["severity_vocab"])))
        self.assertGreaterEqual(sum(row["severity"] == "blocker" for row in rows), 10)
        for required in ["sampling_event", "checklist_completeness", "sensitive_records", "duplicates"]:
            self.assertIn(required, {row["category"] for row in rows})

    def test_intake_staging_guardrails(self) -> None:
        text = (REPO / self.config["files"]["intake_plan"]).read_text(encoding="utf-8")
        self.assertIn("data/ebird_raw/request_<request_id>/", text)
        self.assertIn("data/ebird_quarantine/request_<request_id>/", text)
        self.assertIn("Stop before parsing records", text)
        self.assertIn("Goal 023 does not create derived bird tables", text)
        self.assertIn("Raw eBird files", text)
        self.assertIn("must stay", text)

    def test_manifest_consistency(self) -> None:
        manifest = self.manifest
        self.assertEqual(manifest["goal"], self.config["goal"])
        self.assertEqual(manifest["decision_status"], self.config["decision_status"])
        self.assertEqual(manifest["request_submission_status"], "not_submitted_by_goal023")
        self.assertTrue(manifest["action_time_confirmation_required"])
        self.assertEqual(manifest["artifacts"]["qa_contract"]["row_count"], 17)
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

    def test_no_unfinished_markers_or_request_done_claims(self) -> None:
        marker = re.compile(
            r"\b(" + "|".join(["to" + "do", "tb" + "d", "place" + "holder", "fix" + "me", "x" * 3]) + r")\b",
            re.IGNORECASE,
        )
        forbidden = [re.compile(pattern, re.IGNORECASE) for pattern in self.config["guardrails"]["forbidden_claim_patterns"]]
        paths = [
            REPO / self.config["files"]["submission_checklist"],
            REPO / self.config["files"]["request_text"],
            REPO / self.config["files"]["intake_plan"],
            REPO / self.config["files"]["qa_contract"],
        ]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(marker.search(text), msg=f"unfinished marker in {path}")
            for pattern in forbidden:
                self.assertIsNone(pattern.search(text), msg=f"forbidden request-status claim in {path}")


if __name__ == "__main__":
    unittest.main()
