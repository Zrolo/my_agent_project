import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import generate_dialogue_state_v3_50
from evals.aichat import validate_dialogue_state_v3_dataset
from test_dialogue_state_v3_generation_unit import _v2_case


class DialogueStateV3ValidationTests(unittest.TestCase):
    def _write_cases(self, rows: list[dict], path: Path) -> None:
        path.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
            encoding="utf-8",
        )

    def test_validate_dialogue_state_v3_accepts_generated_dataset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = Path(tmpdir) / "v3.jsonl"
            cases = generate_dialogue_state_v3_50.build_dialogue_state_cases([_v2_case(i) for i in range(1, 51)])
            self._write_cases(cases, dataset)

            report = validate_dialogue_state_v3_dataset.validate_dataset(dataset)

        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(50, report["row_count"])
        self.assertEqual({"initial": 10, "followup": 40}, report["turn_position_counts"])
        self.assertEqual(7, report["followability_counts"]["F1"])
        self.assertEqual(18, report["followability_counts"]["F2"])
        self.assertEqual(10, report["followability_counts"]["F3"])
        self.assertEqual(5, report["followability_counts"]["F4"])
        self.assertEqual(0, report["low_confidence_count"])

    def test_validate_dialogue_state_v3_rejects_missing_followability_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = Path(tmpdir) / "v3_bad.jsonl"
            cases = generate_dialogue_state_v3_50.build_dialogue_state_cases([_v2_case(i) for i in range(1, 51)])
            cases[10]["followability_evidence_quote"] = ""
            self._write_cases(cases, dataset)

            report = validate_dialogue_state_v3_dataset.validate_dataset(dataset)

        self.assertFalse(report["ok"])
        self.assertTrue(
            any(error["code"] == "missing_followability_evidence" for error in report["errors"]),
            report["errors"],
        )

    def test_validate_dialogue_state_v3_rejects_initial_with_followability_label(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = Path(tmpdir) / "v3_bad.jsonl"
            cases = generate_dialogue_state_v3_50.build_dialogue_state_cases([_v2_case(i) for i in range(1, 51)])
            cases[0]["student_scaffold_followability"] = "F1"
            self._write_cases(cases, dataset)

            report = validate_dialogue_state_v3_dataset.validate_dataset(dataset)

        self.assertFalse(report["ok"])
        self.assertTrue(any(error["code"] == "initial_followability_must_be_na" for error in report["errors"]))

    def test_cli_writes_json_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = Path(tmpdir) / "v3.jsonl"
            output = Path(tmpdir) / "report.json"
            cases = generate_dialogue_state_v3_50.build_dialogue_state_cases([_v2_case(i) for i in range(1, 51)])
            self._write_cases(cases, dataset)

            exit_code = validate_dialogue_state_v3_dataset.main(
                ["--dataset", str(dataset), "--output-json", str(output)]
            )
            report = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(0, exit_code)
        self.assertTrue(report["ok"])


if __name__ == "__main__":
    unittest.main()
