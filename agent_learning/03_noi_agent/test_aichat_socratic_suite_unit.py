import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from evals.aichat import run_socratic_suite


class AIChatSocraticSuiteTests(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _write_jsonl(self, path: Path, rows: list[dict]) -> None:
        path.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
            encoding="utf-8",
        )

    def test_build_markdown_report_should_summarize_hard_and_judge_results(self):
        hard_summary = {
            "case_count": 2,
            "passed_case_count": 1,
            "failed_case_count": 1,
            "pass_rate": 0.5,
            "results": [
                {"case_id": "case_ok", "passed": True, "failures": []},
                {"case_id": "case_bad", "passed": False, "failures": ["hard_fail_pattern:完整做法是"]},
            ],
        }
        judge_summary = {
            "case_count": 2,
            "coverage": "smoke",
            "total_case_count": 28,
            "passed_case_count": 1,
            "failed_case_count": 1,
            "pass_rate": 0.5,
            "average_score": 2.0,
            "results": [
                {"case_id": "case_ok", "passed": True, "score": 3, "reasons": ["ok"]},
                {"case_id": "case_bad", "passed": False, "score": 1, "reasons": ["泄露"]},
            ],
        }

        report = run_socratic_suite.build_markdown_report(
            hard_summary,
            judge_summary=judge_summary,
            responses_path=Path("responses.jsonl"),
        )

        self.assertIn("# AIChat Socratic Eval Report", report)
        self.assertIn("responses.jsonl", report)
        self.assertIn("Hard gate pass rate: 50.0%", report)
        self.assertIn("Judge coverage: smoke (2/28 cases)", report)
        self.assertIn("Judge pass rate: 50.0%", report)
        self.assertIn("Average judge score: 2.0 / 3", report)
        self.assertIn("case_bad", report)
        self.assertIn("hard_fail_pattern:完整做法是", report)

    def test_run_suite_should_evaluate_existing_responses_and_write_outputs(self):
        cases_data = {
            "rubric": {"hard_fail_patterns": ["完整做法是"]},
            "cases": [
                {
                    "id": "case_1",
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z2", "tutor_action": "ask_evidence_question"},
                    "forbidden_reply_behavior": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            responses_path = tmp / "responses.jsonl"
            output_dir = tmp / "report"
            self._write_json(cases_path, cases_data)
            self._write_jsonl(responses_path, [{"case_id": "case_1", "response_text": "先看一个证据？"}])

            summary = run_socratic_suite.run_suite(
                cases_path=cases_path,
                responses_path=responses_path,
                output_dir=output_dir,
                with_judge=False,
            )

            self.assertEqual(1, summary["hard_summary"]["passed_case_count"])
            self.assertIsNone(summary["judge_summary"])
            self.assertTrue((output_dir / "hard_summary.json").exists())
            self.assertTrue((output_dir / "suite_summary.json").exists())
            self.assertIn("Hard gate pass rate: 100.0%", (output_dir / "report.md").read_text(encoding="utf-8"))

    def test_run_suite_should_generate_responses_and_run_injected_judge(self):
        cases_data = {
            "rubric": {"hard_fail_patterns": [], "automation_mapping": {"llm_judge": ["只问一个核心问题"]}},
            "cases": [
                {
                    "id": "case_1",
                    "problem_ref": "P3128",
                    "student_message": "卡住了",
                    "problem_context": "树上路径。",
                    "prior_messages": [],
                    "expected_reply_behavior": [],
                    "forbidden_reply_behavior": [],
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                }
            ],
        }

        def fake_chat(messages, student_id, problem_id):
            return "先看一条路径会影响哪些点？", "先看一条路径会影响哪些点？", "L2"

        def fake_judge(prompt):
            return '{"pass": true, "score": 3, "reasons": ["ok"], "failed_criteria": []}'

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            output_dir = tmp / "report"
            self._write_json(cases_path, cases_data)
            progress = StringIO()

            summary = run_socratic_suite.run_suite(
                cases_path=cases_path,
                responses_path=None,
                output_dir=output_dir,
                with_judge=True,
                chat_fn=fake_chat,
                judge_fn=fake_judge,
                progress_stream=progress,
            )

            self.assertEqual(1, summary["hard_summary"]["passed_case_count"])
            self.assertEqual(1, summary["judge_summary"]["passed_case_count"])
            self.assertIn("JUDGE_START index=1 total=1 case_id=case_1", progress.getvalue())
            self.assertIn("JUDGE_DONE index=1 total=1 case_id=case_1 score=3 passed=True ok=True", progress.getvalue())
            self.assertTrue((output_dir / "responses.jsonl").exists())
            self.assertTrue((output_dir / "judge_summary.json").exists())
            self.assertIn("Judge pass rate: 100.0%", (output_dir / "report.md").read_text(encoding="utf-8"))

    def test_run_suite_should_apply_judge_timeout_during_judge_run(self):
        cases_data = {
            "rubric": {"hard_fail_patterns": [], "automation_mapping": {"llm_judge": ["只问一个核心问题"]}},
            "cases": [
                {
                    "id": "case_1",
                    "problem_ref": "P3128",
                    "student_message": "卡住了",
                    "problem_context": "树上路径。",
                    "prior_messages": [],
                    "expected_reply_behavior": [],
                    "forbidden_reply_behavior": [],
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                }
            ],
        }
        captured_timeouts = []

        def fake_chat(messages, student_id, problem_id):
            return "先看一条路径会影响哪些点？", "先看一条路径会影响哪些点？", "L2"

        def fake_judge(prompt):
            captured_timeouts.append(os.environ.get("REVIEW_EVAL_KIMI_TIMEOUT_SECONDS"))
            return '{"pass": true, "score": 3, "reasons": ["ok"], "failed_criteria": []}'

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            output_dir = tmp / "report"
            self._write_json(cases_path, cases_data)

            run_socratic_suite.run_suite(
                cases_path=cases_path,
                output_dir=output_dir,
                with_judge=True,
                chat_fn=fake_chat,
                judge_fn=fake_judge,
                judge_timeout_seconds=11,
            )

        self.assertEqual(["11"], captured_timeouts)

    def test_run_suite_limit_should_apply_to_generation_and_evaluation(self):
        cases_data = {
            "rubric": {"hard_fail_patterns": []},
            "cases": [
                {
                    "id": "case_1",
                    "problem_ref": "P3128",
                    "student_message": "第一条",
                    "problem_context": "",
                    "prior_messages": [],
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                    "forbidden_reply_behavior": [],
                },
                {
                    "id": "case_2",
                    "problem_ref": "P1048",
                    "student_message": "第二条",
                    "problem_context": "",
                    "prior_messages": [],
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                    "forbidden_reply_behavior": [],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            output_dir = tmp / "report"
            self._write_json(cases_path, cases_data)

            summary = run_socratic_suite.run_suite(
                cases_path=cases_path,
                responses_path=None,
                output_dir=output_dir,
                limit=1,
                chat_fn=lambda messages, student_id, problem_id: ("回复？", "回复？", "L2"),
            )

        self.assertEqual(1, summary["hard_summary"]["case_count"])
        self.assertEqual(1, summary["hard_summary"]["passed_case_count"])

    def test_run_suite_should_reject_limited_judge_unless_explicit_smoke(self):
        cases_data = {
            "rubric": {"hard_fail_patterns": [], "automation_mapping": {"llm_judge": ["只问一个核心问题"]}},
            "cases": [
                {
                    "id": "case_1",
                    "problem_ref": "P3128",
                    "student_message": "第一条",
                    "problem_context": "",
                    "prior_messages": [],
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                    "forbidden_reply_behavior": [],
                },
                {
                    "id": "case_2",
                    "problem_ref": "P1048",
                    "student_message": "第二条",
                    "problem_context": "",
                    "prior_messages": [],
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                    "forbidden_reply_behavior": [],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            self._write_json(cases_path, cases_data)

            with self.assertRaisesRegex(ValueError, "limited judge smoke"):
                run_socratic_suite.run_suite(
                    cases_path=cases_path,
                    output_dir=tmp / "report",
                    with_judge=True,
                    limit=1,
                    chat_fn=lambda messages, student_id, problem_id: ("回复？", "回复？", "L2"),
                    judge_fn=lambda prompt: '{"pass": true, "score": 3, "reasons": ["ok"], "failed_criteria": []}',
                )

    def test_main_should_return_clear_error_for_limited_judge(self):
        cases_data = {
            "rubric": {"hard_fail_patterns": [], "automation_mapping": {"llm_judge": ["只问一个核心问题"]}},
            "cases": [
                {
                    "id": "case_1",
                    "problem_ref": "P3128",
                    "student_message": "第一条",
                    "problem_context": "",
                    "prior_messages": [],
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                    "forbidden_reply_behavior": [],
                },
                {
                    "id": "case_2",
                    "problem_ref": "P1048",
                    "student_message": "第二条",
                    "problem_context": "",
                    "prior_messages": [],
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                    "forbidden_reply_behavior": [],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            output_dir = tmp / "report"
            self._write_json(cases_path, cases_data)
            stderr = StringIO()

            with redirect_stderr(stderr):
                exit_code = run_socratic_suite.main(
                    [
                        "--cases",
                        str(cases_path),
                        "--output-dir",
                        str(output_dir),
                        "--with-judge",
                        "--limit",
                        "1",
                    ]
                )

        self.assertEqual(2, exit_code)
        self.assertIn("limited judge smoke", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
