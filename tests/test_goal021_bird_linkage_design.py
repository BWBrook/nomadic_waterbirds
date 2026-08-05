"""Focused tests for Goal 021 bird-observation linkage design deliverables."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "settings" / "bird_linkage_design_021.json"
VALIDATOR = REPO / "scripts" / "validate_bird_linkage_design_021.py"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Goal021ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        manifest_path = REPO / cls.config["files"]["manifest_json"]
        manifest_before = manifest_path.read_bytes()
        result = subprocess.run(
            ["python3", str(VALIDATOR)],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        cls.validation_stdout = result.stdout
        cls.validation_stderr = result.stderr
        cls.validation_returncode = result.returncode
        cls.manifest_unchanged = manifest_path.read_bytes() == manifest_before
        if result.returncode == 0:
            cls.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        else:
            cls.manifest = {}

    def test_validator_runs_successfully(self) -> None:
        self.assertEqual(
            self.validation_returncode,
            0,
            msg=f"validator failed with stderr:\n{self.validation_stderr}",
        )

    def test_validator_default_is_read_only(self) -> None:
        self.assertTrue(self.manifest_unchanged)
        self.assertIn("read-only; manifest unchanged", self.validation_stdout)

    def test_goal020_restrictions_carried_forward(self) -> None:
        g020_ref = self.config["goal020_reference"]
        readiness = read_csv(REPO / g020_ref["readiness_rows_path"])
        self.assertEqual(len(readiness), g020_ref["expected_row_count"])
        counts = Counter(row["bird_linkage_readiness"] for row in readiness)
        self.assertEqual(counts["core_eligible"], g020_ref["expected_core_eligible"])
        self.assertEqual(counts["core_eligible_with_caveat"], g020_ref["expected_core_eligible_with_caveat"])
        self.assertEqual(counts["sensitivity_only"], g020_ref["expected_sensitivity_only"])

        quality = read_csv(REPO / g020_ref["quality_fail_rows_path"])
        reason_counts = Counter(row["quality_fail_reason"] for row in quality)
        self.assertEqual(len(quality), g020_ref["expected_quality_fail_count"])
        for reason, expected in g020_ref["expected_quality_fail_reasons"].items():
            self.assertEqual(reason_counts[reason], expected)

        legacy = [
            row for row in readiness if "legacy_stac_comparator_not_obtained" in (row.get("caveat_code") or "")
        ]
        self.assertEqual(len(legacy), g020_ref["expected_goal018_legacy_caveat_count"])

    def test_candidate_status_vocabulary_and_lab_leader_gate(self) -> None:
        rows = read_csv(REPO / self.config["files"]["candidate_screen"])
        status_vocab = set(self.config["csv_schemas"]["candidate_screen"]["status_vocab"])
        statuses = {row["status"] for row in rows}
        self.assertTrue(statuses.issubset(status_vocab))
        self.assertGreaterEqual(sum(row["status"] == "needs_lab_leader_decision" for row in rows), 1)
        yes_no = {"yes", "no", "true", "false", "y", "n", "1", "0"}
        self.assertTrue(all(row["requires_lab_leader_approval"].strip().lower() in yes_no for row in rows))

    def test_manifest_schema_and_fingerprints(self) -> None:
        manifest = self.manifest
        self.assertEqual(manifest.get("goal"), self.config["goal"])
        self.assertIn("goal020_reference", manifest)
        goal020_ref = manifest["goal020_reference"]
        self.assertIn("readiness_row_count", goal020_ref)
        self.assertGreater(goal020_ref["readiness_row_count"], 0)
        artifacts = manifest.get("artifacts", {})
        for key in ["design_memo", "join_contract", "unit_schema", "candidate_screen", "access_protocol"]:
            self.assertIn(key, artifacts)
        join = artifacts["join_contract"]
        self.assertGreater(join["row_count"], 0)

    def test_no_large_or_blocked_artifacts_are_created(self) -> None:
        goal_status = subprocess.run(
            ["git", "status", "--short", "--porcelain"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        ).stdout.splitlines()
        blocked_ext = set(self.config["provisional_output_guardrails"]["forbidden_extensions"])
        max_mb = self.config["provisional_output_guardrails"]["max_untracked_file_size_mb"]
        for line in goal_status:
            path = REPO / line[3:]
            if path.suffix.lower() in blocked_ext:
                self.fail(f"Blocked extension changed under this goal: {path}")
            if path.exists() and path.stat().st_size > max_mb * 1024 * 1024:
                self.fail(f"Changed file exceeds max output size {max_mb} MB: {path}")

    def test_provisional_terms_not_used(self) -> None:
        unfinished = re.compile(
            r"\b(" + "|".join(["to" + "do", "tb" + "d", "place" + "holder", "fix" + "me", "x" * 3]) + r")\b",
            re.IGNORECASE,
        )
        paths = [
            REPO / self.config["files"]["design_memo"],
            REPO / self.config["files"]["access_protocol"],
            REPO / self.config["files"]["join_contract"],
            REPO / self.config["files"]["unit_schema"],
            REPO / self.config["files"]["candidate_screen"],
        ]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(
                unfinished.search(text),
                msg=f"Unfinished-marker token in {path.name}",
            )


if __name__ == "__main__":
    unittest.main()
