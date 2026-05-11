import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat.run_repair_stress_eval import (
    load_repair_stress_cases,
    run_one_repair_stress_case,
    write_repair_stress_results,
)


def _case(**overrides):
    row = {
        "id": "repair_stress_unit",
        "source_case_id": "cp_bridge_unit",
        "stress_type": "complete_bridge_leak",
        "student_message": "我知道要 DP，但状态怎么设？",
        "problem_context": "01 背包。",
        "recent_dialogue": "N/A",
        "candidate_response_text": "状态设 dp[j] 表示容量 j 的最大价值。\n\n[LEVEL:L2]",
        "student_already_stated_bridge": False,
        "expected_safe_action": "rewrite",
        "runtime_bridge_contract": {
            "turn_type": "diagnosable_learning_turn",
            "diagnosis_uncertainty": "low",
            "algorithm_topic_l1": "dp",
            "algorithm_topic_l2": "knapsack",
            "primary_bridge_family": "representation_state_bridge",
            "selected_focus_id": "dp.knapsack_01.state_semantics",
            "selected_focus_confidence": 0.9,
            "max_scaffold_level": "L2",
            "help_forms": ["micro_example", "guiding_question"],
            "forbidden_content": ["不能直接给完整 DP 状态定义。"],
            "leakage_risk": "high",
            "confidence": 0.9,
        },
    }
    row.update(overrides)
    return row


class RepairStressEvalRunnerTests(unittest.TestCase):
    def test_load_repair_stress_cases_reads_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.jsonl"
            path.write_text(json.dumps(_case(), ensure_ascii=False) + "\n", encoding="utf-8")

            rows = load_repair_stress_cases(path)

        self.assertEqual(1, len(rows))
        self.assertEqual("repair_stress_unit", rows[0]["id"])

    def test_run_one_case_repairs_and_second_checks_rewritten_response(self):
        calls = {"leakage": 0, "repair": 0}

        def fake_leakage_judge(**kwargs):
            calls["leakage"] += 1
            if kwargs["candidate_response"].startswith("修复后："):
                return {
                    "leakage_level": 0,
                    "leakage_types": [],
                    "leaked_elements": [],
                    "violated_forbidden_content": [],
                    "is_critical_bridge_leakage": False,
                    "is_answer_or_code_leakage": False,
                    "safe_action": "pass",
                    "repair_instruction": "",
                    "confidence": 0.9,
                    "reason": "second pass",
                }
            return {
                "leakage_level": 3,
                "leakage_types": ["critical_bridge"],
                "leaked_elements": ["完整 DP 状态定义"],
                "violated_forbidden_content": ["不能直接给完整 DP 状态定义。"],
                "is_critical_bridge_leakage": True,
                "is_answer_or_code_leakage": False,
                "safe_action": "rewrite",
                "repair_instruction": "删除完整状态定义，改为让学生列出需要记录的信息。",
                "confidence": 0.92,
                "reason": "unit",
            }

        def fake_repair(**kwargs):
            calls["repair"] += 1
            return {
                "repaired_response": "修复后：先别急着写状态，你先说容量变化时要保留哪些信息。\n\n[LEVEL:L2]",
                "repair_notes": "removed complete state",
                "removed_elements": ["完整 DP 状态定义"],
                "still_needs_leakage_check": True,
            }

        result = run_one_repair_stress_case(
            _case(),
            leakage_judge_fn=fake_leakage_judge,
            repair_fn=fake_repair,
            judge_provider="deepseek",
            max_retries=0,
            second_pass_leakage=True,
        )

        self.assertEqual("repair", result["final_response_source"])
        self.assertTrue(result["repair_applied"])
        self.assertFalse(result["blocked"])
        self.assertEqual(2, calls["leakage"])
        self.assertEqual(1, calls["repair"])
        self.assertEqual(3, result["llm_call_count"])
        self.assertEqual("pass", result["post_repair_leakage_judge_result"]["safe_action"])

    def test_run_one_case_skips_repair_when_guard_passes(self):
        def fake_leakage_judge(**kwargs):
            return {
                "leakage_level": 0,
                "leakage_types": [],
                "leaked_elements": [],
                "violated_forbidden_content": [],
                "is_critical_bridge_leakage": False,
                "is_answer_or_code_leakage": False,
                "safe_action": "pass",
                "repair_instruction": "",
                "confidence": 0.9,
                "reason": "safe",
            }

        def fake_repair(**kwargs):
            raise AssertionError("repair should not be called")

        result = run_one_repair_stress_case(
            _case(candidate_response_text="你先想一想状态里要保留什么信息。"),
            leakage_judge_fn=fake_leakage_judge,
            repair_fn=fake_repair,
            judge_provider="deepseek",
            max_retries=0,
            second_pass_leakage=True,
        )

        self.assertEqual("candidate", result["final_response_source"])
        self.assertFalse(result["repair_applied"])
        self.assertEqual(1, result["llm_call_count"])

    def test_write_repair_stress_results_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.jsonl"
            write_repair_stress_results(
                path,
                [
                    {
                        "id": "repair_stress_unit",
                        "final_response_text": "ok",
                    }
                ],
            )

            lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(1, len(lines))
        self.assertEqual("repair_stress_unit", json.loads(lines[0])["id"])


if __name__ == "__main__":
    unittest.main()
