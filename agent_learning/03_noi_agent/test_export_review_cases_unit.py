import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.review import export_cases


class ExportReviewCasesTests(unittest.TestCase):
    def test_write_promptfoo_tests_should_export_guided_review_contract(self) -> None:
        cases = [
            {
                "id": "stuck_bridge_312",
                "mode": "stuck_bridge",
                "input": {
                    "problem_title": "P2195 HXY造公园",
                    "completion_status": "unfinished",
                },
                "notes": "draft",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "promptfoo_tests.jsonl"
            with patch.object(export_cases, "PROMPTFOO_TESTS_PATH", target):
                export_cases.write_promptfoo_tests(cases)

            rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(1, len(rows))
        record = rows[0]
        js_assert = next(a for a in record["assert"] if a["type"] == "javascript")
        rubric_assert = next(a for a in record["assert"] if a["type"] == "llm-rubric")

        self.assertIn("problem_focus", js_assert["value"])
        self.assertIn("guided_walkthrough", js_assert["value"])
        self.assertIn("try_now", js_assert["value"])
        self.assertNotIn("main_block &&", js_assert["value"])
        self.assertNotIn("next_step &&", js_assert["value"])

        self.assertIn("guided_walkthrough", rubric_assert["value"])
        self.assertIn("try_now", rubric_assert["value"])
        self.assertIn("problem_focus", rubric_assert["value"])
        self.assertIn("visual_hint 不能直接给出最终比较结果", rubric_assert["value"])
        self.assertIn("guided_walkthrough 每一步只推进一个动作", rubric_assert["value"])
        self.assertIn("try_now 必须直接检查当前桥有没有真的打通", rubric_assert["value"])

    def test_write_promptfoo_tests_should_skip_low_quality_cases(self) -> None:
        cases = [
            {
                "id": "stuck_bridge_312",
                "mode": "stuck_bridge",
                "input": {"problem_title": "A"},
                "notes": "good",
            },
            {
                "id": "stuck_bridge_999",
                "mode": "stuck_bridge_low_quality",
                "input": {"problem_title": "B"},
                "notes": "bad",
            },
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "promptfoo_tests.jsonl"
            with patch.object(export_cases, "PROMPTFOO_TESTS_PATH", target):
                export_cases.write_promptfoo_tests(cases)

            rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(1, len(rows))
        self.assertEqual("stuck_bridge_312", rows[0]["description"])


if __name__ == "__main__":
    unittest.main()
