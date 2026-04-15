import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import run_socratic_eval


class AIChatSocraticEvalRunnerTests(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _write_jsonl(self, path: Path, rows: list[dict]) -> None:
        path.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
            encoding="utf-8",
        )

    def test_evaluate_responses_should_flag_hard_fail_patterns_and_forbidden_snippets(self):
        cases_data = {
            "rubric": {
                "hard_fail_patterns": [
                    "完整代码如下",
                    "#include\\s*<",
                    "答案是\\d",
                ]
            },
            "cases": [
                {
                    "id": "case_ok",
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z2", "tutor_action": "ask_evidence_question"},
                    "forbidden_reply_behavior": ["直接给 check 函数"],
                },
                {
                    "id": "case_bad",
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z0", "tutor_action": "ask_baseline_attempt"},
                    "forbidden_reply_behavior": ["dp[i][j] 表示前 i 件物品，容量为 j 时的最大价值"],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            responses_path = tmp / "responses.jsonl"
            self._write_json(cases_path, cases_data)
            self._write_jsonl(
                responses_path,
                [
                    {
                        "case_id": "case_ok",
                        "response_text": "那你觉得答案是往左缩还是往右缩？先只看 true 的含义。",
                    },
                    {
                        "case_id": "case_bad",
                        "response_text": "完整代码如下：#include <bits/stdc++.h>",
                    },
                ],
            )

            summary = run_socratic_eval.evaluate_response_file(cases_path, responses_path)

        self.assertEqual(2, summary["case_count"])
        self.assertEqual(1, summary["passed_case_count"])
        self.assertEqual(1, summary["failed_case_count"])
        self.assertEqual(0.5, summary["pass_rate"])
        self.assertEqual("case_bad", summary["results"][1]["case_id"])
        self.assertIn("hard_fail_pattern:完整代码如下", summary["results"][1]["failures"])
        self.assertIn("hard_fail_pattern:#include\\s*<", summary["results"][1]["failures"])
        self.assertTrue(summary["results"][0]["passed"])

    def test_evaluate_responses_should_report_missing_response_per_case(self):
        cases_data = {
            "rubric": {"hard_fail_patterns": []},
            "cases": [
                {
                    "id": "case_missing",
                    "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
                    "forbidden_reply_behavior": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_path = tmp / "cases.json"
            responses_path = tmp / "responses.jsonl"
            self._write_json(cases_path, cases_data)
            self._write_jsonl(responses_path, [])

            summary = run_socratic_eval.evaluate_response_file(cases_path, responses_path)

        self.assertEqual(1, summary["failed_case_count"])
        self.assertEqual(["missing_response"], summary["results"][0]["failures"])

    def test_evaluate_responses_should_flag_semantic_dp_state_leak_variants(self):
        case = {
            "id": "case_dp_state",
            "expected_control": {"scaffold_stage": 1, "zpd_level": "Z1", "tutor_action": "ask_slot_question"},
            "forbidden_reply_behavior": ["dp[x][y] 表示从 x,y 出发的最长路"],
        }

        result = run_socratic_eval.evaluate_response(
            case,
            "比较这两种定义：B: dp[x][y] = 从(x,y)出发的最长路径。",
            {"hard_fail_patterns": []},
        )

        self.assertFalse(result["passed"])
        self.assertIn("forbidden_semantic:dp_state_definition", result["failures"])

    def test_evaluate_responses_should_require_checkin_handoff_words(self):
        for tutor_action in ["offer_checkin_reflection", "offer_micro_example_or_checkin"]:
            with self.subTest(tutor_action=tutor_action):
                case = {
                    "id": f"case_{tutor_action}",
                    "expected_control": {
                        "scaffold_stage": 4 if tutor_action == "offer_micro_example_or_checkin" else 1,
                        "zpd_level": "Z2",
                        "tutor_action": tutor_action,
                    },
                    "forbidden_reply_behavior": [],
                }

                result = run_socratic_eval.evaluate_response(
                    case,
                    "我们继续看 check(mid)：它到底在检查什么？",
                    {"hard_fail_patterns": []},
                )

                self.assertFalse(result["passed"])
                self.assertIn(f"missing_tutor_action:{tutor_action}", result["failures"])

    def test_evaluate_responses_should_flag_check_mid_ab_bridge_leak(self):
        case = {
            "id": "case_check_mid_ab_leak",
            "expected_control": {
                "scaffold_stage": 4,
                "zpd_level": "Z2",
                "tutor_action": "offer_micro_example_or_checkin",
            },
            "forbidden_reply_behavior": [],
        }

        result = run_socratic_eval.evaluate_response(
            case,
            "它是在统计为了能让每步都至少跳 mid 米一共需要移走几块石头，还是在找所有跳跃里最短的那一步有多远？",
            {"hard_fail_patterns": []},
        )

        self.assertFalse(result["passed"])
        self.assertIn("forbidden_semantic:ab_bridge_leak", result["failures"])

    def test_evaluate_responses_should_flag_code_trace_before_debug_evidence(self):
        case = {
            "id": "case_code_no_target",
            "expected_control": {
                "scaffold_stage": 1,
                "zpd_level": "Z2",
                "tutor_action": "ask_code_evidence",
            },
            "forbidden_reply_behavior": [],
        }

        result = run_socratic_eval.evaluate_response(
            case,
            "这段代码跑完后，l 也就是 r 指向的位置一定是第一个等于 x 的元素吗？如果数组里根本没有 x，这个循环会停在哪里？",
            {"hard_fail_patterns": []},
        )

        self.assertFalse(result["passed"])
        self.assertIn("forbidden_semantic:code_trace_before_evidence", result["failures"])


if __name__ == "__main__":
    unittest.main()
