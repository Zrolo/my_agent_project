import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from evals.aichat import run_socratic_judge_eval


class AIChatSocraticJudgeEvalTests(unittest.TestCase):
    def test_build_judge_prompt_should_include_case_response_and_output_schema(self):
        case = {
            "id": "case_1",
            "problem_ref": "P3128",
            "student_message": "这题是不是树上差分？",
            "problem_context": "树上路径计数。",
            "expected_reply_behavior": ["不直接确认树上差分", "追问路径影响哪些点"],
            "forbidden_reply_behavior": ["对，这题就是树上差分"],
            "prior_messages": [{"role": "user", "content": "我不知道怎么统计。"}],
        }
        rubric = {
            "automation_mapping": {
                "llm_judge": ["是否只提出一个核心问题", "是否围绕题面证据而不是泛算法建议"]
            }
        }

        prompt = run_socratic_judge_eval.build_judge_prompt(case, "你看一条路径会影响哪些点？", rubric)

        self.assertIn("case_1", prompt)
        self.assertIn("P3128", prompt)
        self.assertIn("这题是不是树上差分？", prompt)
        self.assertIn("你看一条路径会影响哪些点？", prompt)
        self.assertIn("是否只提出一个核心问题", prompt)
        self.assertIn("不能只因为回复安全就给高分", prompt)
        self.assertIn("如果 expected_reply_behavior 要求追问具体题面证据", prompt)
        self.assertIn('"score": 0-3', prompt)

    def test_judge_prompt_contains_bridge_leak_and_code_evidence_redlines(self):
        case = {
            "id": "case_contract",
            "problem_ref": "P2678",
            "student_message": "我还是说不清 check(mid)。",
            "expected_reply_behavior": [],
            "forbidden_reply_behavior": [],
        }

        prompt = run_socratic_judge_eval.build_judge_prompt(
            case,
            "继续看 check(mid)。",
            {"automation_mapping": {"llm_judge": []}},
        )

        self.assertIn("A/B", prompt)
        self.assertIn("完整关键桥", prompt)
        self.assertIn("代码证据", prompt)

    def test_extract_judge_result_should_parse_fenced_json_and_validate_score(self):
        parsed = run_socratic_judge_eval.extract_judge_result(
            '```json\n{"pass": true, "score": 3, "reasons": ["贴题"], "failed_criteria": []}\n```'
        )

        self.assertTrue(parsed["ok"])
        self.assertTrue(parsed["pass"])
        self.assertEqual(3, parsed["score"])
        self.assertEqual(["贴题"], parsed["reasons"])

        invalid = run_socratic_judge_eval.extract_judge_result('{"pass": true, "score": 9, "reasons": []}')
        self.assertFalse(invalid["ok"])
        self.assertFalse(invalid["pass"])

    def test_evaluate_judge_should_call_injected_judge_and_aggregate_summary(self):
        cases_data = {
            "rubric": {"automation_mapping": {"llm_judge": ["只问一个核心问题"]}},
            "cases": [
                {
                    "id": "case_ok",
                    "problem_ref": "P3128",
                    "student_message": "卡住了",
                    "problem_context": "树上路径。",
                    "expected_reply_behavior": [],
                    "forbidden_reply_behavior": [],
                    "prior_messages": [],
                },
                {
                    "id": "case_bad",
                    "problem_ref": "P1048",
                    "student_message": "dp 怎么定义",
                    "problem_context": "背包。",
                    "expected_reply_behavior": [],
                    "forbidden_reply_behavior": [],
                    "prior_messages": [],
                },
            ],
        }
        responses = {
            "case_ok": "先看一条路径影响哪些点？",
            "case_bad": "完整做法是先定义 dp[i][j]...",
        }

        def fake_judge(prompt):
            if "case_ok" in prompt:
                return '{"pass": true, "score": 3, "reasons": ["ok"], "failed_criteria": []}'
            return '{"pass": false, "score": 1, "reasons": ["泄露状态"], "failed_criteria": ["半步支架"]}'

        summary = run_socratic_judge_eval.evaluate_judge(cases_data, responses, judge_fn=fake_judge)

        self.assertEqual(2, summary["case_count"])
        self.assertEqual(1, summary["passed_case_count"])
        self.assertEqual(1, summary["failed_case_count"])
        self.assertEqual(2.0, summary["average_score"])
        self.assertEqual("case_bad", summary["results"][1]["case_id"])
        self.assertFalse(summary["results"][1]["passed"])

    def test_evaluate_judge_should_write_per_case_progress(self):
        cases_data = {
            "rubric": {"automation_mapping": {"llm_judge": ["只问一个核心问题"]}},
            "cases": [
                {
                    "id": "case_ok",
                    "problem_ref": "P3128",
                    "student_message": "卡住了",
                    "problem_context": "树上路径。",
                    "expected_reply_behavior": [],
                    "forbidden_reply_behavior": [],
                    "prior_messages": [],
                },
                {
                    "id": "case_bad",
                    "problem_ref": "P1048",
                    "student_message": "dp 怎么定义",
                    "problem_context": "背包。",
                    "expected_reply_behavior": [],
                    "forbidden_reply_behavior": [],
                    "prior_messages": [],
                },
            ],
        }
        responses = {
            "case_ok": "先看一条路径会影响哪些点？",
            "case_bad": "完整做法是先定义 dp[i][j]...",
        }
        progress = StringIO()

        summary = run_socratic_judge_eval.evaluate_judge(
            cases_data,
            responses,
            judge_fn=lambda prompt: '{"pass": true, "score": 3, "reasons": ["ok"], "failed_criteria": []}',
            progress_stream=progress,
        )

        log = progress.getvalue()
        self.assertEqual(2, summary["case_count"])
        self.assertIn("JUDGE_START index=1 total=2 case_id=case_ok", log)
        self.assertIn("JUDGE_DONE index=1 total=2 case_id=case_ok score=3 passed=True ok=True", log)
        self.assertIn("JUDGE_START index=2 total=2 case_id=case_bad", log)
        self.assertIn("JUDGE_DONE index=2 total=2 case_id=case_bad score=3 passed=True ok=True", log)

    def test_evaluate_judge_should_fail_safe_but_generic_score_two_replies(self):
        cases_data = {
            "rubric": {"automation_mapping": {"llm_judge": ["必须贴题"]}},
            "cases": [
                {
                    "id": "case_generic",
                    "problem_ref": "P2922",
                    "student_message": "是不是用 trie？",
                    "problem_context": "大量 01 串和前缀关系。",
                    "expected_reply_behavior": ["追问看到了什么前缀证据"],
                    "forbidden_reply_behavior": [],
                    "prior_messages": [],
                }
            ],
        }

        summary = run_socratic_judge_eval.evaluate_judge(
            cases_data,
            {"case_generic": "先别急着确认题型。你为什么会这么猜？"},
            judge_fn=lambda prompt: '{"pass": true, "score": 2, "reasons": ["安全但泛"], "failed_criteria": ["未贴题"]}',
        )

        self.assertEqual(0, summary["passed_case_count"])
        self.assertEqual(1, summary["failed_case_count"])
        self.assertFalse(summary["results"][0]["passed"])

    def test_evaluate_judge_file_should_load_responses_jsonl(self):
        cases_data = {
            "rubric": {"automation_mapping": {"llm_judge": ["只问一个核心问题"]}},
            "cases": [
                {
                    "id": "case_1",
                    "problem_ref": "P3128",
                    "student_message": "卡住了",
                    "problem_context": "树上路径。",
                    "expected_reply_behavior": [],
                    "forbidden_reply_behavior": [],
                    "prior_messages": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            responses_path = tmp / "responses.jsonl"
            cases_path.write_text(json.dumps(cases_data, ensure_ascii=False), encoding="utf-8")
            responses_path.write_text(
                json.dumps({"case_id": "case_1", "response_text": "先看一条路径？"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            summary = run_socratic_judge_eval.evaluate_judge_file(
                cases_path,
                responses_path,
                judge_fn=lambda prompt: '{"pass": true, "score": 3, "reasons": ["ok"], "failed_criteria": []}',
            )

        self.assertEqual(1, summary["passed_case_count"])

    def test_main_should_set_judge_timeout_env_for_cli_run(self):
        summary = {
            "case_count": 1,
            "passed_case_count": 1,
            "failed_case_count": 0,
            "pass_rate": 1.0,
            "average_score": 3.0,
            "results": [],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_path = tmp / "judge.json"
            with patch.dict(os.environ, {}, clear=True):
                with patch.object(run_socratic_judge_eval, "evaluate_judge_file", return_value=summary) as mocked:
                    with redirect_stdout(StringIO()):
                        exit_code = run_socratic_judge_eval.main(
                            [
                                "--cases",
                                str(tmp / "cases.json"),
                                "--responses-jsonl",
                                str(tmp / "responses.jsonl"),
                                "--output-json",
                                str(output_path),
                                "--judge-timeout-seconds",
                                "7",
                            ]
                        )
                    self.assertEqual("7", os.environ["REVIEW_EVAL_KIMI_TIMEOUT_SECONDS"])
                    self.assertTrue(output_path.exists())

        self.assertEqual(0, exit_code)
        mocked.assert_called_once()


if __name__ == "__main__":
    unittest.main()
