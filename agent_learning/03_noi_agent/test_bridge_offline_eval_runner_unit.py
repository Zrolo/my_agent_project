import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from evals.aichat import run_bridge_offline_eval


class BridgeOfflineEvalRunnerTests(unittest.TestCase):
    def test_load_seed_rows_reads_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seed.jsonl"
            path.write_text(
                "\n".join(
                    [
                        json.dumps({"id": "case_1", "student_message": "卡住了"}, ensure_ascii=False),
                        "",
                        json.dumps({"id": "case_2", "student_message": "不会 check"}, ensure_ascii=False),
                    ]
                ),
                encoding="utf-8",
            )

            rows = run_bridge_offline_eval.load_seed_rows(path)

        self.assertEqual(["case_1", "case_2"], [row["id"] for row in rows])

    def test_build_messages_from_seed_row_adds_context_without_dropping_prior_dialogue(self):
        row = {
            "id": "cp_bridge_001",
            "problem_ref": "P3128",
            "student_message": "我知道要 LCA，但不知道在哪里加减标记。",
            "problem_context": "树上多条路径统计每个点经过次数。",
            "prior_messages": [{"role": "assistant", "content": "先看单条路径。"}],
        }

        messages = run_bridge_offline_eval.build_messages_from_seed_row(row)

        self.assertEqual("assistant", messages[0]["role"])
        self.assertEqual("user", messages[-1]["role"])
        self.assertIn("[学生原始问题]", messages[-1]["content"])
        self.assertIn("题目编号/链接: P3128", messages[-1]["content"])
        self.assertIn("树上多条路径统计", messages[-1]["content"])

    def test_build_messages_from_seed_row_parses_recent_dialogue_like_online_history(self):
        row = {
            "id": "cp_bridge_context",
            "problem_ref": "P3948",
            "problem_title": "数据结构",
            "problem_source_url": "https://www.luogu.com.cn/problem/P3948",
            "student_message": "区间影响怎么转成加减标记？",
            "problem_context": "多次区间影响，最后统一统计。",
            "recent_dialogue": "学生：我看懂一次操作会影响一段。\nAI：先只看这一段里哪些位置真的变了。",
            "student_code_excerpt": "diff[l] += x;\n// r 这里不确定",
        }

        messages = run_bridge_offline_eval.build_messages_from_seed_row(row)

        self.assertEqual(
            [
                {"role": "user", "content": "我看懂一次操作会影响一段。"},
                {"role": "assistant", "content": "先只看这一段里哪些位置真的变了。"},
            ],
            messages[:-1],
        )
        self.assertEqual("user", messages[-1]["role"])
        self.assertIn("[学生原始问题]", messages[-1]["content"])
        self.assertIn("区间影响怎么转成加减标记？", messages[-1]["content"])
        self.assertIn("[当前上下文状态与回答策略]", messages[-1]["content"])
        self.assertIn("题目标题: 数据结构", messages[-1]["content"])
        self.assertIn("题目链接: https://www.luogu.com.cn/problem/P3948", messages[-1]["content"])
        self.assertIn("题面/题意/约束: 多次区间影响，最后统一统计。", messages[-1]["content"])
        self.assertIn("学生当前代码: diff[l] += x;", messages[-1]["content"])
        self.assertNotIn("recent_dialogue", messages[-1]["content"])

    def test_latest_assistant_reply_accepts_chinese_ai_role_prefix(self):
        dialogue = "学生：顺序总写反。\nAI：你先判断哪一边还可能包含答案。\n学生：我觉得是左边。"

        reply = run_bridge_offline_eval._latest_assistant_reply(dialogue)

        self.assertEqual("你先判断哪一边还可能包含答案。", reply)

    def test_result_rows_preserve_dialogue_state_metadata_for_review_workbook(self):
        rows = [
            {
                "id": "dialogue_v3_case",
                "case_id": "dialogue_v3_case",
                "problem_ref": "P1049",
                "problem_source_platform": "luogu",
                "problem_source_url": "https://www.luogu.com.cn/problem/P1049",
                "problem_statement": "题面摘要。",
                "problem_statement_public_summary": "公开摘要。",
                "student_message": "我觉得是从前面推，但还是乱。",
                "problem_context": "01 背包。",
                "recent_dialogue": "学生：顺序总写反。\nAI：你先判断哪一边还可能包含答案。",
                "turn_position": "followup",
                "context_type": "followup_after_partial_answer",
                "student_scaffold_followability": "F2",
                "expected_tutor_move": "clarify",
                "prior_ai_scaffold": "你先判断哪一边还可能包含答案。",
                "student_reply_to_prior_scaffold": "我觉得是左边，但不确定。",
            }
        ]

        def fake_chat(messages, student_id, problem_id, chat_model_provider=None):
            return "回复", "回复", "L2"

        with patch.object(run_bridge_offline_eval, "noi_agent_chat", side_effect=fake_chat):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                tutor_mode="current_system",
                pipeline_mode="tutor_only_no_diagnosis",
            )

        result = result_rows[0]
        self.assertEqual("https://www.luogu.com.cn/problem/P1049", result["problem_source_url"])
        self.assertEqual("题面摘要。", result["problem_statement"])
        self.assertEqual("parsed_recent_dialogue", result["generation_context_source"])
        self.assertEqual(3, result["generation_message_count"])
        self.assertEqual("followup", result["turn_position"])
        self.assertEqual("F2", result["student_scaffold_followability"])
        self.assertEqual("clarify", result["expected_tutor_move"])
        self.assertEqual("你先判断哪一边还可能包含答案。", result["context_ai_reply"])
        self.assertEqual("你先判断哪一边还可能包含答案。", result["prior_ai_scaffold"])

    def test_run_bridge_offline_eval_rows_runs_bridge_leakage_and_repair(self):
        rows = [
            {
                "id": "case_1",
                "problem_ref": "P1048",
                "student_message": "我知道像背包，但状态怎么设？",
                "problem_context": "采药，时间限制内最大化价值。",
                "gold_bridge_family": "representation_bridge",
                "gold_known_focus": "state_design",
                "gold_forbidden_completion": "不能直接给完整 dp[j] 定义和转移式。",
            }
        ]
        calls = []

        def fake_bridge_judge(**kwargs):
            calls.append(("bridge", kwargs["student_message"]))
            return {
                "problem_solving_state": "problem_representation_unclear",
                "missing_bridge": {
                    "family": "representation_bridge",
                    "subtype": "state_design",
                    "description": "状态含义缺失。",
                    "evidence": ["学生问状态怎么设"],
                    "known_focus": "state_design",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "question",
                "forbidden_content": ["不能直接给完整 dp[j] 定义和转移式。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            calls.append(("tutor", row["id"]))
            return {
                "baseline_group": "current_system",
                "response_text": "状态设 dp[j] 表示时间 j 内的最大价值。\n\n[LEVEL:L2]",
                "history_text": "状态设 dp[j] 表示时间 j 内的最大价值。\n\n[LEVEL:L2]",
                "level": "L2",
            }

        leakage_calls = []

        def fake_leakage(**kwargs):
            leakage_calls.append(kwargs["candidate_response"])
            calls.append(("leakage", kwargs["candidate_response"]))
            if "先别把状态写死" in kwargs["candidate_response"]:
                return {
                    "leakage_level": 0,
                    "leakage_types": [],
                    "leaked_elements": [],
                    "violated_forbidden_content": [],
                    "is_critical_bridge_leakage": False,
                    "is_answer_or_code_leakage": False,
                    "safe_action": "pass",
                    "repair_instruction": "",
                    "confidence": 0.88,
                    "reason": "unit test post repair pass",
                }
            return {
                "leakage_level": 3,
                "leakage_types": ["critical_bridge"],
                "leaked_elements": ["完整 dp[j] 状态定义"],
                "violated_forbidden_content": ["不能直接给完整 dp[j] 定义和转移式。"],
                "is_critical_bridge_leakage": True,
                "is_answer_or_code_leakage": False,
                "safe_action": "rewrite",
                "repair_instruction": "删除完整状态定义，改成询问需要保留的信息。",
                "confidence": 0.91,
                "reason": "unit test",
            }

        def fake_repair(**kwargs):
            calls.append(("repair", kwargs["student_message"]))
            return {
                "repaired_response": "先别把状态写死。你想一想：时间变化后，至少要保留哪一个量？\n\n[LEVEL:L2]",
                "repair_notes": "删除完整状态定义。",
                "removed_elements": ["完整 dp[j] 状态定义"],
                "still_needs_leakage_check": True,
            }

        progress = io.StringIO()

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            repair_fn=fake_repair,
            progress_stream=progress,
        )

        self.assertEqual([("bridge", rows[0]["student_message"]), ("tutor", "case_1")], calls[:2])
        self.assertEqual(1, len(result_rows))
        result = result_rows[0]
        self.assertEqual("case_1", result["case_id"])
        self.assertEqual("representation_bridge", result["gold"]["bridge_family"])
        self.assertEqual("representation_bridge", result["bridge_judge_result"]["missing_bridge"]["family"])
        self.assertEqual("rewrite", result["leakage_judge_result"]["safe_action"])
        self.assertIn("repaired_response", result["repair_result"])
        self.assertEqual(
            [
                "状态设 dp[j] 表示时间 j 内的最大价值。",
                "先别把状态写死。你想一想：时间变化后，至少要保留哪一个量？",
            ],
            leakage_calls,
        )
        self.assertEqual("状态设 dp[j] 表示时间 j 内的最大价值。", result["candidate_response_text"])
        self.assertEqual("先别把状态写死。你想一想：时间变化后，至少要保留哪一个量？", result["final_response_text"])
        self.assertEqual("repair", result["final_response_source"])
        self.assertTrue(result["repair_applied"])
        self.assertIn("post_repair_leakage_judge_result", result)
        self.assertFalse(result["repair_still_leaks"])
        self.assertFalse(result["blocked"])
        self.assertEqual(5, result["llm_call_count"])
        self.assertIn("CASE_DONE index=1 total=1 case_id=case_1", progress.getvalue())

    def test_diagnosis_only_pipeline_skips_tutor_leakage_and_repair(self):
        rows = [{"id": "case_diag", "student_message": "我不会。"}]
        calls = []

        def fake_bridge_judge(**kwargs):
            calls.append("bridge")
            return {
                "problem_solving_state": "strategy_generation_blocked",
                "missing_bridge": {
                    "family": "unknown_bridge",
                    "subtype": "unknown",
                    "description": "信息不足。",
                    "evidence": ["学生说不会"],
                    "known_focus": "unknown",
                    "needs_new_focus": True,
                },
                "help_seeking_type": "unclear",
                "allowed_help_level": "L1",
                "help_form": "question",
                "forbidden_content": ["不要给完整题解。"],
                "leakage_risk": "unknown",
                "confidence": 0.6,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            calls.append("tutor")
            return {"response_text": "不应调用"}

        def fake_leakage(**kwargs):
            calls.append("leakage")
            return {"leakage_level": 0, "safe_action": "pass"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            pipeline_mode="diagnosis_only",
        )

        self.assertEqual(["bridge"], calls)
        result = result_rows[0]
        self.assertNotIn("tutor_response", result)
        self.assertNotIn("leakage_judge_result", result)
        self.assertEqual("", result["candidate_response_text"])
        self.assertEqual("", result["final_response_text"])
        self.assertEqual("none", result["final_response_source"])
        self.assertEqual(1, result["llm_call_count"])

    def test_post_repair_leakage_check_marks_repair_still_leaks(self):
        rows = [{"id": "case_repair_leak", "student_message": "我知道要 DP，但状态怎么设？"}]

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "problem_representation_unclear",
                "missing_bridge": {
                    "family": "representation_bridge",
                    "subtype": "state_design",
                    "description": "状态含义缺失。",
                    "evidence": ["学生问状态怎么设"],
                    "known_focus": "state_design",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "question",
                "forbidden_content": ["不能直接给完整状态定义。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "状态设 dp[j] 表示容量 j 的最大价值。", "level": "L2"}

        def fake_leakage(**kwargs):
            if kwargs["candidate_response"].startswith("修复后仍然"):
                return {
                    "leakage_level": 3,
                    "leakage_types": ["critical_bridge"],
                    "leaked_elements": ["修复后仍然给出完整状态定义"],
                    "violated_forbidden_content": ["不能直接给完整状态定义。"],
                    "is_critical_bridge_leakage": True,
                    "is_answer_or_code_leakage": False,
                    "safe_action": "rewrite",
                    "repair_instruction": "仍需删除完整状态定义。",
                    "confidence": 0.9,
                    "reason": "unit test post repair leak",
                }
            return {
                "leakage_level": 3,
                "leakage_types": ["critical_bridge"],
                "leaked_elements": ["完整状态定义"],
                "violated_forbidden_content": ["不能直接给完整状态定义。"],
                "is_critical_bridge_leakage": True,
                "is_answer_or_code_leakage": False,
                "safe_action": "rewrite",
                "repair_instruction": "删除完整状态定义。",
                "confidence": 0.9,
                "reason": "unit test initial leak",
            }

        def fake_repair(**kwargs):
            return {
                "repaired_response": "修复后仍然说 dp[j] 表示容量 j 的最大价值。",
                "repair_notes": "unit test bad repair",
                "removed_elements": [],
                "still_needs_leakage_check": True,
            }

        result = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            repair_fn=fake_repair,
        )[0]

        self.assertTrue(result["repair_applied"])
        self.assertTrue(result["repair_still_leaks"])
        self.assertEqual("rewrite", result["post_repair_safe_action"])
        self.assertEqual(3, result["post_repair_leakage_judge_result"]["leakage_level"])
        self.assertEqual("repair", result["final_response_source"])
        self.assertIn("post_repair_leakage_judge_latency_ms", result["latency_ms"])

    def test_post_repair_fallback_on_leak_uses_deterministic_safe_scaffold(self):
        rows = [{"id": "case_repair_leak", "student_message": "我知道要 DP，但状态怎么设？"}]

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "modeling_representation_gap",
                "missing_bridge": {
                    "family": "representation_state_bridge",
                    "subtype": "state.table_or_memo_cell_semantics",
                    "description": "学生缺少状态含义。",
                    "evidence": ["学生问状态怎么设"],
                    "known_focus": "dp_state_semantics",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "concept_explanation",
                "allowed_help_level": "L2",
                "help_form": "micro_example",
                "forbidden_content": ["不能直接给完整状态定义。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "状态设 dp[j] 表示容量 j 的最大价值。", "level": "L2"}

        def fake_leakage(**kwargs):
            if kwargs["candidate_response"].startswith("修复后仍然"):
                return {
                    "leakage_level": 3,
                    "leakage_types": ["critical_bridge"],
                    "leaked_elements": ["修复后仍然给出完整状态定义"],
                    "violated_forbidden_content": ["不能直接给完整状态定义。"],
                    "is_critical_bridge_leakage": True,
                    "is_answer_or_code_leakage": False,
                    "safe_action": "rewrite",
                    "repair_instruction": "仍需删除完整状态定义。",
                    "confidence": 0.9,
                    "reason": "unit test post repair leak",
                }
            return {
                "leakage_level": 3,
                "leakage_types": ["critical_bridge"],
                "leaked_elements": ["完整状态定义"],
                "violated_forbidden_content": ["不能直接给完整状态定义。"],
                "is_critical_bridge_leakage": True,
                "is_answer_or_code_leakage": False,
                "safe_action": "rewrite",
                "repair_instruction": "删除完整状态定义。",
                "confidence": 0.9,
                "reason": "unit test initial leak",
            }

        def fake_repair(**kwargs):
            return {
                "repaired_response": "修复后仍然说 dp[j] 表示容量 j 的最大价值。",
                "repair_notes": "unit test bad repair",
                "removed_elements": [],
                "still_needs_leakage_check": True,
            }

        result = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            repair_fn=fake_repair,
            post_repair_fallback_on_leak=True,
        )[0]

        self.assertTrue(result["repair_applied"])
        self.assertTrue(result["repair_still_leaks"])
        self.assertEqual("safe_fallback_after_repair", result["final_response_source"])
        self.assertIn("safe_fallback_after_repair_result", result)
        self.assertIn("先不要把它写成完整状态", result["final_response_text"])
        self.assertNotIn("dp[j]", result["final_response_text"])
        self.assertFalse(result["blocked"])

    def test_static_leakage_risk_lint_flags_answer_slots_and_worked_examples(self):
        response = (
            "请回答 check(mid) 应该返回 true 还是 false。"
            "然后把规则填成：可行返回____，不可行返回____。"
            "再按 dp[c] = max(dp[c], dp[c-2] + 5) 模拟正序和倒序。"
        )

        lint = run_bridge_offline_eval._static_leakage_risk_lint(response)

        self.assertTrue(lint["answer_slot_risk_flag"])
        self.assertTrue(lint["filled_trace_risk_flag"])
        self.assertTrue(lint["worked_example_risk_flag"])
        self.assertIn("answer_slot", lint["risk_types"])
        self.assertIn("filled_trace", lint["risk_types"])
        self.assertIn("worked_example", lint["risk_types"])

    def test_run_bridge_offline_eval_rows_records_static_leakage_risk_lint(self):
        rows = [{"id": "case_static_lint", "student_message": "check 返回值怎么定？"}]

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "predicate_condition_gap",
                "missing_bridge": {
                    "family": "predicate_condition_bridge",
                    "subtype": "predicate.feasibility_truth_direction",
                    "description": "学生缺少判定真假语义。",
                    "evidence": ["学生问返回值怎么定"],
                    "known_focus": "check_truth_direction",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "concept_explanation",
                "allowed_help_level": "L2",
                "help_form": "micro_example",
                "forbidden_content": ["不能直接给 check true/false 语义。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {
                "response_text": "请回答 check(mid) 应该返回 true 还是 false，并填写可行返回____。",
                "level": "L2",
            }

        result = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            pipeline_mode="tutor_only",
        )[0]

        self.assertTrue(result["candidate_static_leakage_risk_lint"]["answer_slot_risk_flag"])
        self.assertTrue(result["final_static_leakage_risk_lint"]["answer_slot_risk_flag"])
        self.assertIn("answer_slot", result["candidate_static_leakage_risk_lint"]["risk_types"])

    def test_tutor_only_pipeline_skips_leakage_and_uses_candidate_as_final(self):
        rows = [{"id": "case_tutor", "student_message": "我不会。"}]
        calls = []

        def fake_bridge_judge(**kwargs):
            calls.append("bridge")
            return {
                "problem_solving_state": "strategy_generation_blocked",
                "missing_bridge": {
                    "family": "unknown_bridge",
                    "subtype": "unknown",
                    "description": "信息不足。",
                    "evidence": ["学生说不会"],
                    "known_focus": "unknown",
                    "needs_new_focus": True,
                },
                "help_seeking_type": "unclear",
                "allowed_help_level": "L1",
                "help_form": "question",
                "forbidden_content": ["不要给完整题解。"],
                "leakage_risk": "unknown",
                "confidence": 0.6,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            calls.append("tutor")
            return {"response_text": "你先贴题面。", "level": "L1"}

        def fake_leakage(**kwargs):
            calls.append("leakage")
            return {"leakage_level": 0, "safe_action": "pass"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            pipeline_mode="tutor_only",
        )

        self.assertEqual(["bridge", "tutor"], calls)
        result = result_rows[0]
        self.assertNotIn("leakage_judge_result", result)
        self.assertEqual("你先贴题面。", result["candidate_response_text"])
        self.assertEqual("你先贴题面。", result["final_response_text"])
        self.assertEqual("candidate", result["final_response_source"])

    def test_deterministic_safe_scaffold_pipeline_skips_tutor_and_uses_safe_fallback(self):
        rows = [
            {
                "id": "case_safe",
                "student_message": "我知道要 LCA，但不知道每条路径到底在哪里加减标记。",
                "problem_context": "树上多条路径统计每个点经过次数。",
            }
        ]
        calls = []

        def fake_bridge_judge(**kwargs):
            calls.append("bridge")
            return {
                "problem_solving_state": "method_application_gap",
                "missing_bridge": {
                    "family": "aggregation_contribution_bridge",
                    "subtype": "aggregation.path_contribution_marking",
                    "description": "学生缺少贡献转汇总规则。",
                    "evidence": ["学生问每条路径在哪里加减标记"],
                    "known_focus": "tree_path_difference",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "strategy_hint_request",
                "allowed_help_level": "L2",
                "help_form": "micro_example",
                "forbidden_content": ["不能直接给出完整贡献标记规则。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            calls.append("tutor")
            raise AssertionError("safe scaffold should not call tutor")

        def fake_leakage(**kwargs):
            calls.append("leakage")
            raise AssertionError("safe scaffold should not call leakage judge")

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            pipeline_mode="deterministic_safe_scaffold",
        )

        self.assertEqual(["bridge"], calls)
        result = result_rows[0]
        self.assertEqual("safe_fallback", result["final_response_source"])
        self.assertFalse(result["repair_applied"])
        self.assertFalse(result["blocked"])
        self.assertEqual(1, result["llm_call_count"])
        self.assertEqual(result["final_response_text"], result["candidate_response_text"])
        self.assertIn("真实影响", result["final_response_text"])
        self.assertIn("最终应该被统计", result["final_response_text"])
        self.assertNotIn("[LEVEL:L1]", result["final_response_text"])
        self.assertNotIn("LCA", result["final_response_text"])
        self.assertNotIn("端点", result["final_response_text"])
        self.assertNotIn("+", result["final_response_text"])
        self.assertNotIn("-", result["final_response_text"])

    def test_tutor_stage_retries_transient_exception(self):
        rows = [{"id": "case_tutor_retry", "student_message": "我知道像背包，但状态怎么设？"}]
        attempts = []

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "modeling_representation_gap",
                "missing_bridge": {
                    "family": "representation_state_bridge",
                    "subtype": "state.table_or_memo_cell_semantics",
                    "description": "学生缺少状态含义。",
                    "evidence": ["学生问状态怎么设"],
                    "known_focus": "state_design",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "concept_explanation",
                "allowed_help_level": "L2",
                "help_form": "micro_example",
                "forbidden_content": ["不要直接给完整状态定义。"],
                "leakage_risk": "high",
                "confidence": 0.8,
                "reason": "unit test",
            }

        def flaky_tutor(row, messages, bridge_result):
            attempts.append("try")
            if len(attempts) == 1:
                raise ValueError("transient json parse")
            return {"response_text": "先说说数组下标和格子值分别可能表示什么。", "level": "L2"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=flaky_tutor,
            pipeline_mode="tutor_only",
            max_retries=1,
        )

        result = result_rows[0]
        self.assertEqual(2, len(attempts))
        self.assertEqual("先说说数组下标和格子值分别可能表示什么。", result["final_response_text"])
        self.assertEqual("candidate", result["final_response_source"])
        self.assertEqual(1, result["retry_count"])
        self.assertEqual(3, result["llm_call_count"])
        self.assertNotIn("tutor", result["stage_errors"])
        self.assertNotIn("error", result)

    def test_tutor_only_no_diagnosis_pipeline_skips_bridge_judge_for_current_system_baseline(self):
        rows = [{"id": "case_current_only", "student_message": "我不会。"}]
        calls = []

        def fake_bridge_judge(**kwargs):
            calls.append("bridge")
            return {}

        def fake_tutor(row, messages, bridge_result):
            calls.append(("tutor", bridge_result))
            return {"response_text": "你先贴题面。", "level": "L1"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            tutor_mode="current_system",
            pipeline_mode="tutor_only_no_diagnosis",
        )

        self.assertEqual([("tutor", {})], calls)
        result = result_rows[0]
        self.assertNotIn("bridge_judge_result", result)
        self.assertNotIn("candidate_retrieval", result)
        self.assertEqual("你先贴题面。", result["candidate_response_text"])
        self.assertEqual("你先贴题面。", result["final_response_text"])
        self.assertEqual("candidate", result["final_response_source"])
        self.assertEqual(1, result["llm_call_count"])

    def test_tutor_only_no_diagnosis_is_invalid_for_bridge_contract(self):
        with self.assertRaisesRegex(ValueError, "requires one of"):
            run_bridge_offline_eval.run_bridge_offline_eval_rows(
                [{"id": "case_invalid", "student_message": "我不会。"}],
                tutor_mode="bridge_contract",
                pipeline_mode="tutor_only_no_diagnosis",
            )

    def test_tutor_plus_guard_pipeline_does_not_repair_rewrite_action(self):
        rows = [{"id": "case_guard_only", "student_message": "状态怎么设？"}]
        calls = []

        def fake_bridge_judge(**kwargs):
            calls.append("bridge")
            return {
                "problem_solving_state": "problem_representation_unclear",
                "missing_bridge": {
                    "family": "representation_bridge",
                    "subtype": "state_design",
                    "description": "状态含义缺失。",
                    "evidence": ["学生问状态"],
                    "known_focus": "state_design",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "question",
                "forbidden_content": ["不要直接给完整状态定义。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            calls.append("tutor")
            return {"response_text": "状态设 dp[j]。", "level": "L2"}

        def fake_leakage(**kwargs):
            calls.append("leakage")
            return {"leakage_level": 3, "safe_action": "rewrite"}

        def fake_repair(**kwargs):
            calls.append("repair")
            return {"repaired_response": "不应调用"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            repair_fn=fake_repair,
            pipeline_mode="tutor_plus_guard",
        )

        self.assertEqual(["bridge", "tutor", "leakage"], calls)
        result = result_rows[0]
        self.assertNotIn("repair_result", result)
        self.assertEqual("状态设 dp[j]。", result["final_response_text"])
        self.assertEqual("candidate", result["final_response_source"])
        self.assertFalse(result["repair_applied"])

    def test_tutor_plus_guard_block_uses_safe_fallback_instead_of_empty_response(self):
        rows = [{"id": "case_guard_block", "student_message": "check 怎么返回？"}]
        calls = []

        def fake_bridge_judge(**kwargs):
            calls.append("bridge")
            return {
                "problem_solving_state": "strategy_application_gap",
                "missing_bridge": {
                    "family": "predicate_condition_bridge",
                    "subtype": "predicate.feasibility_truth_direction",
                    "description": "判定条件真假方向缺失。",
                    "evidence": ["学生问 check 怎么返回"],
                    "known_focus": "check_condition",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "question",
                "forbidden_content": ["不要直接给完整 check 返回条件。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            calls.append("tutor")
            return {"response_text": "如果贪心结果满足要求，check 就返回 true。", "level": "L2"}

        def fake_leakage(**kwargs):
            calls.append("leakage")
            return {"leakage_level": 3, "safe_action": "block"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            pipeline_mode="tutor_plus_guard",
        )

        self.assertEqual(["bridge", "tutor", "leakage"], calls)
        result = result_rows[0]
        self.assertIn("safe_fallback_result", result)
        self.assertTrue(result["final_response_text"])
        self.assertEqual("safe_fallback_block", result["final_response_source"])
        self.assertFalse(result["blocked"])
        self.assertFalse(result["repair_applied"])
        self.assertIn("先不要写真假方向", result["final_response_text"])

    def test_default_tutor_uses_requested_chat_model_provider_and_records_models(self):
        rows = [
            {
                "id": "case_1",
                "problem_ref": "P1001",
                "student_message": "我不会。",
                "problem_context": "简单题。",
                "gold_bridge_family": "representation_bridge",
            }
        ]
        calls = []

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "problem_representation_unclear",
                "missing_bridge": {
                    "family": "representation_bridge",
                    "subtype": "state_design",
                    "description": "缺状态语义。",
                    "evidence": ["学生说不会"],
                    "known_focus": "state_design",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "question",
                "forbidden_content": ["不要给完整答案。"],
                "leakage_risk": "low",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_chat(messages, student_id, problem_id, chat_model_provider=None):
            calls.append((student_id, problem_id, chat_model_provider))
            return "回复", "回复", "L2"

        def fake_leakage(**kwargs):
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
                "reason": "unit test",
            }

        with patch.object(run_bridge_offline_eval, "noi_agent_chat", side_effect=fake_chat):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=fake_bridge_judge,
                leakage_judge_fn=fake_leakage,
                chat_model_provider="deepseek",
            )

        self.assertEqual("deepseek", calls[0][2])
        self.assertEqual("deepseek", result_rows[0]["models"]["tutor_model_provider"])
        self.assertEqual("deepseek-v4-flash", result_rows[0]["models"]["judge_model"])
        self.assertEqual("deepseek", result_rows[0]["tutor_response"]["tutor_model_provider"])

    def test_default_focus_registry_is_passed_when_seed_has_no_available_focus(self):
        rows = [
            {
                "id": "case_focus",
                "problem_ref": "P3128",
                "student_message": "我知道要 LCA，但不知道路径贡献在哪里加减。",
                "problem_context": "树上多条路径统计经过次数。",
            }
        ]
        focus_registry = [
            {
                "focus_id": "tree_path_difference",
                "bridge_family": "aggregation_bridge",
                "bridge_family_v2": "aggregation_contribution_bridge",
                "description": "树上路径贡献转成端点/LCA 差分标记并 DFS 汇总。",
                "aliases": ["树上差分", "LCA 标记"],
            }
        ]
        captured_focus = []

        def fake_bridge_judge(**kwargs):
            captured_focus.extend(kwargs["available_known_focus"])
            return {
                "problem_solving_state": "strategy_application_gap",
                "missing_bridge": {
                    "family": "aggregation_bridge",
                    "subtype": "tree_path_difference",
                    "description": "路径贡献映射缺失。",
                    "evidence": ["学生说不知道路径贡献在哪里加减"],
                    "known_focus": "tree_path_difference",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "micro_example",
                "forbidden_content": ["不要直接给端点和 LCA 的完整加减式。"],
                "leakage_risk": "medium",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "先看单条路径。", "level": "L2"}

        def fake_leakage(**kwargs):
            return {"leakage_level": 0, "safe_action": "pass"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            focus_registry=focus_registry,
        )

        self.assertEqual("tree_path_difference", captured_focus[0]["focus_id"])
        self.assertEqual("aggregation_contribution_bridge", captured_focus[0]["bridge_family"])
        self.assertEqual("aggregation_bridge", captured_focus[0]["legacy_bridge_family"])
        self.assertEqual(1, result_rows[0]["focus_registry_size"])

    def test_retrieval_augmented_compact_judge_records_candidates_and_contract(self):
        rows = [
            {
                "id": "case_compact",
                "problem_ref": "P0001",
                "student_message": "我知道要二分答案，但是 check(mid) 到底返回 true 还是 false 我总写反。",
                "problem_context": "最大化最小距离，判断 mid 是否可行。",
            }
        ]
        focus_registry = [
            {
                "focus_id": "check_condition",
                "bridge_family": "predicate_condition_bridge",
                "description": "二分、判定或循环中的 check/if 条件语义不清。",
                "aliases": ["check", "判定函数", "可行性判断"],
            },
            {
                "focus_id": "tree_path_difference",
                "bridge_family": "aggregation_contribution_bridge",
                "description": "树上路径贡献转成端点/LCA 差分标记。",
                "aliases": ["树上差分", "LCA 标记"],
            },
        ]
        captured_kwargs = {}

        def fake_bridge_judge(**kwargs):
            captured_kwargs.update(kwargs)
            return {
                "problem_solving_state": "method_application_gap",
                "missing_bridge": {
                    "family": "predicate_condition_bridge",
                    "subtype": "predicate.feasibility_truth_direction",
                    "description": "学生无法判断 check(mid) 的真假语义。",
                    "evidence": ["学生问 check(mid) 返回 true 还是 false"],
                    "known_focus": "check_condition",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "strategy_hint_request",
                "allowed_help_level": "L2",
                "help_form": "micro_example",
                "forbidden_content": [
                    "不要直接给完整 check 条件。",
                    "不要直接给完整边界更新方向。",
                    "不要给完整代码。",
                    "这条不应进入 compact contract。",
                ],
                "leakage_risk": "high",
                "confidence": 0.86,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "先用一个 mid 手算一下可行性。", "level": "L2"}

        def fake_leakage(**kwargs):
            return {"leakage_level": 0, "safe_action": "pass"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            focus_registry=focus_registry,
            judge_schema_mode="retrieval_augmented_compact_judge",
        )

        result = result_rows[0]
        self.assertEqual("retrieval_augmented_compact_judge", result["judge_schema_mode"])
        self.assertIn("top_k_algorithm_topics", captured_kwargs)
        self.assertEqual("binary_search", captured_kwargs["top_k_algorithm_topics"][0]["topic_l1"])
        self.assertEqual("check_condition", captured_kwargs["top_k_registered_focus"][0]["focus_id"])
        self.assertEqual("check_condition", result["candidate_retrieval"]["focus_candidate_ids"][0])
        contract = result["runtime_bridge_contract"]
        self.assertEqual("predicate_condition_bridge", contract["primary_bridge_family"])
        self.assertEqual("check_condition", contract["selected_focus_id"])
        self.assertLessEqual(len(contract["help_forms"]), 2)
        self.assertEqual(3, len(contract["forbidden_content"]))
        self.assertIn("prompt_budget_estimate", result)

    def test_predicted_guard_does_not_pass_gold_forbidden_completion_to_leakage_judge(self):
        rows = [
            {
                "id": "case_guard",
                "student_message": "状态怎么设？",
                "gold_forbidden_completion": "不能直接给完整 dp[j] 定义。",
            }
        ]
        captured_forbidden = []

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "problem_representation_unclear",
                "missing_bridge": {
                    "family": "representation_bridge",
                    "subtype": "state_design",
                    "description": "状态含义缺失。",
                    "evidence": ["学生问状态"],
                    "known_focus": "state_design",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "question",
                "forbidden_content": ["不要直接给完整状态定义。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "你先说状态里要保留什么。", "level": "L2"}

        def fake_leakage(**kwargs):
            captured_forbidden.extend(kwargs["forbidden_content"])
            return {"leakage_level": 0, "safe_action": "pass"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            guard_mode="predicted",
        )

        self.assertEqual(["不要直接给完整状态定义。"], captured_forbidden)
        self.assertEqual("predicted", result_rows[0]["guard_mode"])

    def test_oracle_guard_passes_gold_forbidden_completion_to_leakage_judge(self):
        rows = [
            {
                "id": "case_oracle",
                "student_message": "状态怎么设？",
                "gold_forbidden_completion": "不能直接给完整 dp[j] 定义。",
            }
        ]
        captured_forbidden = []

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "problem_representation_unclear",
                "missing_bridge": {
                    "family": "representation_bridge",
                    "subtype": "state_design",
                    "description": "状态含义缺失。",
                    "evidence": ["学生问状态"],
                    "known_focus": "state_design",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "question",
                "forbidden_content": ["不要直接给完整状态定义。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "你先说状态里要保留什么。", "level": "L2"}

        def fake_leakage(**kwargs):
            captured_forbidden.extend(kwargs["forbidden_content"])
            return {"leakage_level": 0, "safe_action": "pass"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            guard_mode="oracle",
        )

        self.assertIn("不能直接给完整 dp[j] 定义。", captured_forbidden)
        self.assertEqual("oracle", result_rows[0]["guard_mode"])

    def test_current_system_tutor_does_not_inject_bridge_contract(self):
        rows = [{"id": "case_current", "problem_ref": "P1001", "student_message": "我不会。"}]
        captured_messages = []

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "strategy_generation_blocked",
                "missing_bridge": {
                    "family": "selection_bridge",
                    "subtype": "method_selection",
                    "description": "方法选择缺失。",
                    "evidence": ["学生说不会"],
                    "known_focus": "method_selection",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L1",
                "help_form": "question",
                "forbidden_content": ["不要直接给算法名。"],
                "leakage_risk": "medium",
                "confidence": 0.8,
                "reason": "unit test",
            }

        def fake_chat(messages, student_id, problem_id, chat_model_provider=None):
            captured_messages.extend(messages)
            return "回复", "回复", "L1"

        def fake_leakage(**kwargs):
            return {"leakage_level": 0, "safe_action": "pass"}

        with patch.object(run_bridge_offline_eval, "noi_agent_chat", side_effect=fake_chat):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=fake_bridge_judge,
                leakage_judge_fn=fake_leakage,
                tutor_mode="current_system",
            )

        joined = "\n".join(message["content"] for message in captured_messages)
        self.assertNotIn("Bridge Contract", joined)
        self.assertEqual("current_system", result_rows[0]["tutor_mode"])

    def test_bridge_contract_tutor_uses_bridge_result_in_clean_system_prompt(self):
        rows = [{"id": "case_contract", "problem_ref": "P1001", "student_message": "我不会。"}]
        captured = {}

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "strategy_application_gap",
                "missing_bridge": {
                    "family": "predicate_bridge",
                    "subtype": "check_condition",
                    "description": "学生缺少 check 判断关系。",
                    "evidence": ["学生说 check 不会写"],
                    "known_focus": "check_condition",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "instrumental_help",
                "allowed_help_level": "L2",
                "help_form": "micro_example",
                "forbidden_content": ["不要直接给完整 check 条件。"],
                "leakage_risk": "high",
                "confidence": 0.88,
                "reason": "unit test",
            }

        def fake_completion(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content="回复\n\n[LEVEL:L2]"))
                ]
            )

        def fake_leakage(**kwargs):
            return {"leakage_level": 0, "safe_action": "pass"}

        with patch.object(run_bridge_offline_eval, "_chat_completion_create", side_effect=fake_completion):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=fake_bridge_judge,
                leakage_judge_fn=fake_leakage,
                tutor_mode="bridge_contract",
                chat_model_provider="deepseek",
            )

        system_prompt = captured["system_prompt"]
        joined_messages = "\n".join(message["content"] for message in captured["messages"])
        self.assertIn("Offline Bridge Contract Tutor", system_prompt)
        self.assertIn("Bridge Contract", system_prompt)
        self.assertIn("predicate_bridge", system_prompt)
        self.assertIn("不要直接给完整 check 条件", system_prompt)
        self.assertIn("桥梁导向微型例子", system_prompt)
        self.assertIn("先说明这个例子要观察的桥梁问题", system_prompt)
        self.assertIn("先让学生完成局部观察", system_prompt)
        self.assertIn("下一轮再抽象", system_prompt)
        self.assertIn("我不会", joined_messages)
        self.assertNotIn("线上 AIChat 主 system prompt", joined_messages)
        self.assertEqual("bridge_contract", result_rows[0]["tutor_mode"])
        self.assertEqual("bridge_contract", result_rows[0]["tutor_response"]["tutor_mode"])



    def test_bridge_contract_tutor_system_prompt_forbids_answer_bearing_micro_example_slots(self):
        prompt = run_bridge_offline_eval._bridge_contract_tutor_system_prompt(
            {
                "missing_bridge": {
                    "family": "aggregation_contribution_bridge",
                    "subtype": "aggregation.path_contribution_marking",
                    "known_focus": "tree_path_difference",
                    "description": "学生不知道贡献规则。",
                },
                "allowed_help_level": "L2",
                "help_forms": ["micro_example"],
                "forbidden_content": ["不要直接给完整贡献规则。"],
                "leakage_risk": "high",
            }
        )

        self.assertIn("不要给候选答案式标记", prompt)
        self.assertIn("不要预填正负号、操作位置、边界方向或最终规则", prompt)
        self.assertIn("不要要求学生直接写完整通用公式或完整规则", prompt)
        self.assertIn("只让学生完成一个局部观察", prompt)
        self.assertIn("不要把当前 missing bridge 本身改写成短答槽位", prompt)
        self.assertIn("应该返回什么", prompt)
        self.assertIn("应该在哪里", prompt)
        self.assertIn("分别写什么值", prompt)
        self.assertIn("这个格子应该记录什么", prompt)
        self.assertIn("不要把关键符号、方向或位置做成二选一", prompt)
        self.assertIn("先问观察对象和期望计数", prompt)
        self.assertIn("贡献/汇总类桥", prompt)
        self.assertIn("不要引入任何人工标记、正负号或补偿操作", prompt)
        self.assertIn("只让学生列出真实受影响对象和期望汇总结果", prompt)

    def test_bridge_contract_tutor_uses_clean_offline_prompt_not_online_chat(self):
        row = {
            "id": "case_contract_direct",
            "problem_ref": "P3128",
            "student_message": "我知道要 LCA，但不知道每条路径到底在哪里加减标记。",
            "problem_context": "树上多条路径统计每个点经过次数。",
        }
        messages = run_bridge_offline_eval.build_messages_from_seed_row(row)
        bridge_result = {
            "missing_bridge": {
                "family": "aggregation_contribution_bridge",
                "subtype": "aggregation.path_contribution_marking",
                "known_focus": "tree_path_difference",
                "description": "学生知道 LCA 但不知道路径贡献如何汇总。",
            },
            "allowed_help_level": "L2",
            "help_form": "micro_example",
            "help_forms": ["micro_example"],
            "forbidden_content": ["不要直接给完整贡献公式。"],
            "leakage_risk": "high",
        }
        captured = {}

        def fake_completion(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="只看一个局部影响：先标出这条路径实际经过哪些对象，再比较哪些对象应被统计到。\n\n[LEVEL:L2]")
                    )
                ]
            )

        with patch.object(run_bridge_offline_eval, "noi_agent_chat", side_effect=AssertionError("should not call online AIChat prompt")), patch.object(
            run_bridge_offline_eval, "_chat_completion_create", side_effect=fake_completion
        ):
            result = run_bridge_offline_eval._call_bridge_contract_tutor(
                row,
                messages,
                bridge_result,
                chat_model_provider="deepseek_flash",
            )

        self.assertEqual("bridge_contract", result["tutor_mode"])
        self.assertIn("局部影响", result["response_text"])
        self.assertEqual("deepseek_flash", captured["provider_id"])
        self.assertIn("Offline Bridge Contract Tutor", captured["system_prompt"])
        self.assertIn("Bridge Contract", captured["system_prompt"])
        self.assertIn("current_substep", captured["system_prompt"])
        self.assertNotIn("trie", captured["system_prompt"].lower())

    def test_single_llm_structured_skips_bridge_judge_and_outputs_contract_response_self_check(self):
        rows = [
            {
                "id": "case_single_llm",
                "problem_ref": "P1048",
                "student_message": "我知道像背包，但状态怎么设？",
                "problem_context": "采药，时间限制内最大化价值。",
            }
        ]

        def fake_bridge_judge(**kwargs):
            raise AssertionError("single_llm_structured should not call Bridge Judge")

        class FakeMessage:
            content = json.dumps(
                {
                    "runtime_bridge_contract": {
                        "turn_type": "diagnosable_learning_turn",
                        "diagnosis_uncertainty": "low",
                        "algorithm_topic_l1": "dp",
                        "algorithm_topic_l2": "knapsack",
                        "primary_bridge_family": "representation_state_bridge",
                        "selected_focus_id": "state_design",
                        "selected_focus_confidence": 0.86,
                        "max_scaffold_level": "L2",
                        "help_forms": ["micro_example", "guiding_question"],
                        "forbidden_content": ["不要直接给完整 dp[j] 状态定义。"],
                        "leakage_risk": "high",
                        "confidence": 0.86,
                    },
                    "student_response": "我们先不把状态写死。你先说说：数组一格至少要记录什么信息？",
                    "self_check": {
                        "predicted_leakage_risk": "low",
                        "violated_forbidden_content": [],
                        "notes": "没有直接给完整状态。",
                    },
                },
                ensure_ascii=False,
            )

        class FakeChoice:
            message = FakeMessage()

        class FakeResponse:
            choices = [FakeChoice()]

        with patch.object(
            run_bridge_offline_eval,
            "_chat_completion_create",
            return_value=FakeResponse(),
            create=True,
        ):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=fake_bridge_judge,
                tutor_mode="single_llm_structured",
                pipeline_mode="tutor_only",
                chat_model_provider="deepseek_flash",
            )

        result = result_rows[0]
        self.assertEqual("single_llm_structured", result["tutor_mode"])
        self.assertEqual("single_llm_structured", result["tutor_response"]["tutor_mode"])
        self.assertEqual("single_llm_structured", result["tutor_response"]["baseline_group"])
        self.assertEqual("representation_state_bridge", result["runtime_bridge_contract"]["primary_bridge_family"])
        self.assertEqual("state_design", result["runtime_bridge_contract"]["selected_focus_id"])
        self.assertEqual("low", result["single_llm_structured_result"]["self_check"]["predicted_leakage_risk"])
        self.assertEqual("我们先不把状态写死。你先说说：数组一格至少要记录什么信息？", result["candidate_response_text"])
        self.assertEqual("candidate", result["final_response_source"])
        self.assertEqual(1, result["llm_call_count"])

    def test_enhanced_prompt_only_runs_without_bridge_diagnosis(self):
        rows = [
            {
                "id": "case_enhanced_prompt",
                "problem_ref": "P1048",
                "student_message": "我知道像背包，但状态怎么设？",
                "problem_context": "采药，时间限制内最大化价值。",
            }
        ]
        captured_messages = []

        def bridge_judge_should_not_run(**kwargs):
            raise AssertionError("enhanced_prompt_only standalone should not call Bridge Judge")

        def fake_noi_agent_chat(messages, student_id, problem_id, chat_model_provider=None):
            captured_messages.extend(messages)
            return (
                "先不直接定义状态。你先说说：数组一格至少要记录哪类信息？",
                "history",
                "L2",
            )

        with patch.object(run_bridge_offline_eval, "noi_agent_chat", side_effect=fake_noi_agent_chat):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=bridge_judge_should_not_run,
                tutor_mode="enhanced_prompt_only",
                pipeline_mode="tutor_only_no_diagnosis",
                chat_model_provider="deepseek_flash",
            )

        result = result_rows[0]
        self.assertEqual("enhanced_prompt_only", result["tutor_mode"])
        self.assertEqual("enhanced_prompt_only", result["baseline_group"])
        self.assertEqual("enhanced_prompt_only", result["tutor_response"]["baseline_group"])
        self.assertEqual("candidate", result["final_response_source"])
        self.assertEqual(1, result["llm_call_count"])
        joined = "\n".join(message["content"] for message in captured_messages)
        self.assertIn("Enhanced Tutor Prompt", joined)
        self.assertIn("不给你具体 Bridge Contract", joined)
        self.assertIn("不要直接补完学生当前缺失的关键桥", joined)

    def test_enhanced_prompt_only_can_run_with_guard_stack(self):
        rows = [
            {
                "id": "case_enhanced_guard",
                "problem_ref": "P1048",
                "student_message": "我知道像背包，但状态怎么设？",
                "problem_context": "采药，时间限制内最大化价值。",
            }
        ]
        calls = []

        def fake_bridge_judge(**kwargs):
            calls.append(("bridge", kwargs["student_message"]))
            return {
                "problem_solving_state": "modeling_representation_gap",
                "missing_bridge": {
                    "family": "representation_state_bridge",
                    "subtype": "state.table_or_memo_cell_semantics",
                    "description": "学生缺少状态含义。",
                    "evidence": ["学生问状态怎么设"],
                    "known_focus": "state_design",
                    "needs_new_focus": False,
                },
                "help_seeking_type": "concept_explanation",
                "allowed_help_level": "L2",
                "help_form": "micro_example",
                "forbidden_content": ["不要直接给完整状态定义。"],
                "leakage_risk": "high",
                "confidence": 0.9,
                "reason": "unit test",
            }

        def fake_noi_agent_chat(messages, student_id, problem_id, chat_model_provider=None):
            calls.append(("tutor", chat_model_provider))
            return (
                "先不直接定义状态。你先说说：数组一格至少要记录哪类信息？",
                "history",
                "L2",
            )

        def fake_leakage(**kwargs):
            calls.append(("leakage", kwargs["forbidden_content"]))
            return {
                "leakage_level": 0,
                "leakage_types": [],
                "leaked_elements": [],
                "violated_forbidden_content": [],
                "is_critical_bridge_leakage": False,
                "is_answer_or_code_leakage": False,
                "safe_action": "pass",
                "confidence": 0.88,
                "reason": "unit test",
            }

        with patch.object(run_bridge_offline_eval, "noi_agent_chat", side_effect=fake_noi_agent_chat):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=fake_bridge_judge,
                leakage_judge_fn=fake_leakage,
                tutor_mode="enhanced_prompt_only",
                pipeline_mode="tutor_plus_guard",
                chat_model_provider="deepseek_flash",
            )

        result = result_rows[0]
        self.assertEqual(
            [
                ("bridge", "我知道像背包，但状态怎么设？"),
                ("tutor", "deepseek_flash"),
                ("leakage", ["不要直接给完整状态定义。"]),
            ],
            calls,
        )
        self.assertEqual("enhanced_prompt_only", result["tutor_mode"])
        self.assertEqual("enhanced_prompt_only", result["baseline_group"])
        self.assertEqual("pass", result["leakage_judge_result"]["safe_action"])
        self.assertEqual("candidate", result["final_response_source"])
        self.assertFalse(result["repair_applied"])
        self.assertEqual(3, result["llm_call_count"])

    def test_single_llm_structured_receives_strict_enum_and_top_k_focus_candidates(self):
        rows = [
            {
                "id": "case_single_llm_strict",
                "problem_ref": "P3128",
                "student_message": "我知道要 LCA，但不知道每条路径到底在哪里加减标记。",
                "problem_context": "树上多条路径统计每个点经过次数。",
            }
        ]
        captured = {}

        class FakeMessage:
            content = json.dumps(
                {
                    "runtime_bridge_contract": {
                        "turn_type": "diagnosable_learning_turn",
                        "diagnosis_uncertainty": "low",
                        "algorithm_topic_l1": "tree",
                        "algorithm_topic_l2": "tree_path_difference",
                        "primary_bridge_family": "aggregation_contribution_bridge",
                        "selected_focus_id": "tree_path_difference",
                        "selected_focus_confidence": 0.9,
                        "max_scaffold_level": "L2",
                        "help_forms": ["micro_example", "guiding_question"],
                        "forbidden_content": ["不要直接给完整树上差分标记公式。"],
                        "leakage_risk": "high",
                        "confidence": 0.9,
                    },
                    "student_response": "先用一条小路径观察：端点和最近公共祖先分别承担什么作用？",
                    "self_check": {
                        "predicted_leakage_risk": "low",
                        "violated_forbidden_content": [],
                        "notes": "未给完整公式。",
                    },
                },
                ensure_ascii=False,
            )

        class FakeChoice:
            message = FakeMessage()

        class FakeResponse:
            choices = [FakeChoice()]

        def fake_chat_completion_create(**kwargs):
            captured.update(kwargs)
            return FakeResponse()

        with patch.object(
            run_bridge_offline_eval,
            "_chat_completion_create",
            side_effect=fake_chat_completion_create,
        ):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=lambda **kwargs: (_ for _ in ()).throw(
                    AssertionError("single_llm_structured should not call Bridge Judge")
                ),
                tutor_mode="single_llm_structured",
                pipeline_mode="tutor_only",
                chat_model_provider="deepseek_flash",
                judge_schema_mode="retrieval_augmented_compact_judge",
                focus_registry=[
                    {
                        "focus_id": "tree_path_difference",
                        "bridge_family_v2": "aggregation_contribution_bridge",
                        "description": "树上路径贡献转端点/LCA 标记。",
                        "aliases": ["树上差分", "LCA 标记"],
                    }
                ],
            )

        system_prompt = captured["system_prompt"]
        joined_messages = "\n".join(message["content"] for message in captured["messages"])
        self.assertIn("primary_bridge_family 只能使用以下枚举值", system_prompt)
        self.assertIn("aggregation_contribution_bridge", system_prompt)
        self.assertIn("不要输出中文自由标签", system_prompt)
        self.assertIn("top_k_registered_focus", joined_messages)
        self.assertIn("tree_path_difference", joined_messages)
        self.assertEqual(["tree_path_difference"], result_rows[0]["candidate_retrieval"]["focus_candidate_ids"][:1])

    def test_single_llm_structured_prompt_contains_scaffold_level_calibration(self):
        system_prompt = run_bridge_offline_eval._single_llm_structured_system_prompt()

        self.assertIn("帮助强度校准", system_prompt)
        self.assertIn("L0", system_prompt)
        self.assertIn("只澄清或索取证据", system_prompt)
        self.assertIn("L2", system_prompt)
        self.assertIn("学生已经暴露明确卡点", system_prompt)
        self.assertIn("微型例子", system_prompt)
        self.assertIn("不要因为保守而把所有可诊断学习轮次都选成 L1", system_prompt)

    def test_single_llm_structured_prompt_warns_against_hypothetical_bridge_leakage(self):
        system_prompt = run_bridge_offline_eval._single_llm_structured_system_prompt()

        self.assertIn("禁止内容不能包装成假设句", system_prompt)
        self.assertIn("如果这个量/格子/标记代表", system_prompt)
        self.assertIn("让学生自己说出某个量、格子、标记或对象应该记录什么", system_prompt)
        self.assertIn("self_check 必须标为 medium 或 high", system_prompt)

    def test_single_llm_structured_prompt_is_bridge_first_topic_second(self):
        system_prompt = run_bridge_offline_eval._single_llm_structured_system_prompt()

        self.assertIn("bridge-first, topic-second, focus-top-k", system_prompt)
        self.assertIn("先用 primary_bridge_family 决定教学动作", system_prompt)
        self.assertIn("algorithm_topic 只作为轻量上下文", system_prompt)
        self.assertIn("具体算法名只作为上下文信号", system_prompt)
        self.assertIn("不要把 prompt 中的示例当作算法清单", system_prompt)
        self.assertIn("不要在微型例子里预填关键操作的一半", system_prompt)
        self.assertIn("先让学生列出观察对象、影响因素或可行性判断", system_prompt)

    def test_bridge_contract_message_is_bridge_first_not_algorithm_specific(self):
        message = run_bridge_offline_eval._bridge_contract_message(
            {
                "missing_bridge": {
                    "family": "aggregation_contribution_bridge",
                    "subtype": "aggregation.path_contribution_marking",
                    "known_focus": "tree_path_difference",
                    "description": "路径贡献如何汇总。",
                },
                "allowed_help_level": "L2",
                "help_forms": ["micro_example"],
                "forbidden_content": ["不要直接给完整端点/LCA 公式。"],
                "leakage_risk": "high",
            }
        )

        self.assertIn("bridge-first, topic-second", message["content"])
        self.assertIn("按 missing_bridge.family 控制教学动作", message["content"])
        self.assertIn("具体算法名只用于理解上下文", message["content"])

    def test_bridge_contract_message_uses_current_substep_without_step_tree_claim(self):
        message = run_bridge_offline_eval._bridge_contract_message(
            {
                "missing_bridge": {
                    "family": "ordering_dependency_bridge",
                    "subtype": "ordering.rolling_array_overwrite_order",
                    "known_focus": "dp.knapsack_01.reverse_capacity_loop",
                    "description": "学生不知道正序更新为什么会复用当前物品。",
                },
                "allowed_help_level": "L2",
                "help_forms": ["micro_example"],
                "forbidden_content": ["不要直接给完整正序/倒序更新规则。"],
                "leakage_risk": "high",
            }
        )

        self.assertIn("current_substep", message["content"])
        self.assertIn("当前最小子步骤", message["content"])
        self.assertIn("第一层提示", message["content"])
        self.assertIn("不要展示完整分解树", message["content"])
        self.assertNotIn("step tree", message["content"].lower())

    def test_bridge_contract_tutor_prompt_blocks_state_definition_leakage(self):
        prompt = run_bridge_offline_eval._bridge_contract_tutor_system_prompt(
            {
                "missing_bridge": {
                    "family": "representation_state_bridge",
                    "subtype": "state.semantic_payload",
                    "known_focus": "palindrome_interval_state",
                    "description": "学生不知道区间状态应该记录什么。",
                },
                "allowed_help_level": "L2",
                "help_forms": ["micro_example"],
                "forbidden_content": ["不要直接给完整状态定义。"],
                "leakage_risk": "high",
            }
        )

        self.assertIn("状态/表示类桥的第一层提示", prompt)
        self.assertIn("不要直接给出表示对象承载的完整语义", prompt)
        self.assertIn("目标量、最优性含义或可行性含义", prompt)
        self.assertIn("先问哪些输入因素、边界对象、历史选择或约束会影响后续决策", prompt)
        self.assertIn("让学生先列出影响后续决策的因素", prompt)
        self.assertNotIn("dp[l][r]", prompt)
        self.assertNotIn("最小代价/最优值/可行性", prompt)

    def test_bridge_contract_tutor_prompt_requires_teacher_like_response_shape(self):
        prompt = run_bridge_offline_eval._bridge_contract_tutor_system_prompt(
            {"missing_bridge": {"family": "representation_state_bridge"}}
        )

        self.assertIn("学生可见回复建议形状", prompt)
        self.assertIn("一句承接学生当前说法", prompt)
        self.assertIn("一个很小的观察任务", prompt)
        self.assertIn("一个可短答的问题", prompt)
        self.assertIn("不要像规则清单一样回复", prompt)
        self.assertIn("不要连续追问多个问题", prompt)

    def test_bridge_contract_compact_prompt_keeps_core_controls_but_is_shorter(self):
        bridge_result = {
            "missing_bridge": {"family": "representation_state_bridge"},
            "allowed_help_level": "L2",
            "help_forms": ["micro_example"],
            "forbidden_content": ["不要直接给完整表示含义。"],
            "leakage_risk": "high",
        }
        full_prompt = run_bridge_offline_eval._bridge_contract_tutor_system_prompt(bridge_result)
        compact_prompt = run_bridge_offline_eval._bridge_contract_compact_tutor_system_prompt(
            bridge_result,
            compression_level="compact",
        )

        self.assertLess(len(compact_prompt), len(full_prompt) * 0.7)
        self.assertIn("Bridge Contract", compact_prompt)
        self.assertIn("missing_bridge", compact_prompt)
        self.assertIn("allowed_help_level", compact_prompt)
        self.assertIn("forbidden_content", compact_prompt)
        self.assertIn("一句承接学生", compact_prompt)
        self.assertIn("小观察任务", compact_prompt)
        self.assertIn("可短答问题", compact_prompt)
        self.assertIn("不直接补完整关键桥", compact_prompt)
        self.assertIn("不要输出 JSON、Markdown 代码块或内部标签", compact_prompt)
        self.assertNotIn("[LEVEL:L1|L2|L3]", compact_prompt)
        self.assertNotIn("末尾保留", compact_prompt)
        self.assertNotIn("不要给候选答案式标记", compact_prompt)
        self.assertNotIn("贡献/汇总类桥的第一层提示", compact_prompt)

    def test_bridge_contract_minimal_prompt_is_shorter_than_compact(self):
        bridge_result = {
            "missing_bridge": {"family": "predicate_condition_bridge"},
            "allowed_help_level": "L2",
            "help_forms": ["question"],
            "forbidden_content": ["不要直接给完整判定条件。"],
        }
        compact_prompt = run_bridge_offline_eval._bridge_contract_compact_tutor_system_prompt(
            bridge_result,
            compression_level="compact",
        )
        minimal_prompt = run_bridge_offline_eval._bridge_contract_compact_tutor_system_prompt(
            bridge_result,
            compression_level="minimal",
        )

        self.assertLess(len(minimal_prompt), len(compact_prompt))
        self.assertIn("不直接补完整关键桥", minimal_prompt)
        self.assertIn("一个当前最小子步骤", minimal_prompt)
        self.assertIn("不要输出 JSON、Markdown 代码块或内部标签", minimal_prompt)
        self.assertNotIn("[LEVEL:L1|L2|L3]", minimal_prompt)
        self.assertNotIn("末尾保留", minimal_prompt)

    def test_bridge_contract_compact_tutor_uses_compact_prompt_and_records_mode(self):
        row = {"id": "case_compact", "student_message": "状态这里说不清。"}
        messages = run_bridge_offline_eval.build_messages_from_seed_row(row)
        bridge_result = {
            "missing_bridge": {"family": "representation_state_bridge"},
            "allowed_help_level": "L2",
            "help_forms": ["micro_example"],
            "forbidden_content": ["不要直接给完整表示含义。"],
        }
        captured = {}

        def fake_completion(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="先看影响后续选择的因素。\n\n[LEVEL:L2]"))]
            )

        with patch.object(run_bridge_offline_eval, "_chat_completion_create", side_effect=fake_completion):
            result = run_bridge_offline_eval._call_bridge_contract_tutor(
                row,
                messages,
                bridge_result,
                chat_model_provider="deepseek_flash",
                tutor_mode_name="bridge_contract_compact",
                prompt_compression_level="compact",
            )

        self.assertEqual("bridge_contract_compact", result["tutor_mode"])
        self.assertEqual("bridge_contract_tutor_compact", result["baseline_group"])
        self.assertIn("compact", captured["system_prompt"].lower())
        self.assertNotIn("贡献/汇总类桥的第一层提示", captured["system_prompt"])

    def test_tutor_modes_include_bridge_contract_compression_variants(self):
        self.assertIn("bridge_contract_compact", run_bridge_offline_eval.TUTOR_MODES)
        self.assertIn("bridge_contract_minimal", run_bridge_offline_eval.TUTOR_MODES)
        self.assertIn("bridge_guided_dbox_style_tutor", run_bridge_offline_eval.TUTOR_MODES)

    def test_bridge_guided_dbox_style_tutor_uses_bridge_contract_and_dbox_shape(self):
        row = {
            "id": "case_bridge_guided_dbox",
            "student_message": "状态这里说不清。",
            "problem_context": "区间 DP。",
        }
        messages = run_bridge_offline_eval.build_messages_from_seed_row(row)
        bridge_result = {
            "missing_bridge": {
                "family": "representation_state_bridge",
                "subtype": "state.representation_semantics",
                "description": "学生不知道表示对象应该承载哪些信息。",
                "known_focus": "state_semantics",
            },
            "allowed_help_level": "L2",
            "help_forms": ["guiding_question"],
            "forbidden_content": ["不要直接给完整状态含义。"],
            "leakage_risk": "high",
        }
        captured = {}

        def fake_completion(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=json.dumps(
                                {
                                    "baseline_group": "missing_bridge_guided_decomposition",
                                    "decomposition_view": [
                                        {
                                            "step_id": "s1",
                                            "step_name": "读出题目中的对象",
                                            "status": "known_or_not_relevant",
                                        },
                                        {
                                            "step_id": "s2",
                                            "step_name": "判断当前表示要保留哪些影响后续决策的因素",
                                            "status": "current_stuck_step",
                                        },
                                        {
                                            "step_id": "s3",
                                            "step_name": "再讨论关系或转移",
                                            "status": "defer",
                                        },
                                    ],
                                    "current_substep": "判断当前表示要保留哪些影响后续决策的因素",
                                    "hint_level": "general_question",
                                    "student_visible_response": "你先不用写状态名。只看当前小问题：哪些输入因素会影响后面选择？先列两个。",
                                },
                                ensure_ascii=False,
                            )
                        )
                    )
                ]
            )

        with patch.object(run_bridge_offline_eval, "_chat_completion_create", side_effect=fake_completion):
            result = run_bridge_offline_eval._call_bridge_guided_dbox_style_tutor(
                row,
                messages,
                bridge_result,
                chat_model_provider="deepseek_flash",
            )

        self.assertEqual("bridge_guided_dbox_style_tutor", result["tutor_mode"])
        self.assertEqual("missing_bridge_guided_decomposition", result["baseline_group"])
        self.assertEqual("general_question", result["hint_level"])
        self.assertEqual("deepseek_flash", captured["provider_id"])
        self.assertTrue(captured["response_format_json"])
        self.assertIn("Bridge-guided DBox-style", captured["system_prompt"])
        self.assertIn("Bridge Contract", captured["system_prompt"])
        self.assertIn("decomposition_view", captured["system_prompt"])
        self.assertIn("forbidden_content", captured["system_prompt"])
        self.assertIn("do not reveal substep", captured["system_prompt"])
        self.assertIn("不要直接给完整状态含义", captured["system_prompt"])


    def test_generation_control_prompts_use_abstract_bridge_shapes_not_algorithm_examples(self):
        enhanced = run_bridge_offline_eval._enhanced_prompt_message()["content"]
        structured = run_bridge_offline_eval._single_llm_structured_system_prompt()

        self.assertIn("完整表示含义、完整关系或公式、完整判定条件", enhanced)
        self.assertIn("具体算法名只作为上下文信号", structured)
        self.assertIn("不要把 prompt 中的示例当作算法清单", structured)
        self.assertIn("表示类卡点", structured)
        self.assertIn("判定类卡点", structured)
        self.assertIn("汇总/贡献类卡点", structured)

        for concrete_phrase in ["DP、check、LCA", "KMP、Dijkstra", "判定/check", "端点/LCA"]:
            self.assertNotIn(concrete_phrase, structured)
        self.assertNotIn("check 条件", enhanced)

    def test_generation_prompts_assume_students_will_reply_briefly(self):
        prompts = "\n".join(
            [
                run_bridge_offline_eval._enhanced_prompt_message()["content"],
                run_bridge_offline_eval._single_llm_structured_system_prompt(),
                run_bridge_offline_eval._bridge_contract_tutor_system_prompt(
                    {"missing_bridge": {"family": "representation_state_bridge"}}
                ),
                run_bridge_offline_eval._dbox_inspired_decomposition_system_prompt(),
            ]
        )

        self.assertIn("学生在线回复通常很短", prompts)
        self.assertIn("一两个关键词、局部判断或一句短句", prompts)
        self.assertIn("不要要求长篇解释", prompts)
        self.assertIn("不要要求完整表格", prompts)
        self.assertIn("不要要求多步推导", prompts)
        self.assertIn("最低足够学生努力", prompts)
        self.assertIn("优先短生成式回答", prompts)
        self.assertIn("慎用选择题", prompts)
        self.assertIn("选项不能承载关键桥答案", prompts)
        self.assertIn("学生卡住后再降级为选项", prompts)
        self.assertIn("不要把当前 missing bridge 本身改写成短答槽位", prompts)
        self.assertIn("应该返回什么", prompts)
        self.assertIn("应该在哪里", prompts)
        self.assertIn("分别写什么值", prompts)
        self.assertIn("这个格子应该记录什么", prompts)
        self.assertIn("认知价值", prompts)
        self.assertIn("诊断价值", prompts)
        self.assertNotIn("1-2 个词、一个选项或一句短句", prompts)

    def test_literature_baseline_prompts_do_not_encode_specific_answer_bearing_slots(self):
        prompts = "\n".join(
            [
                run_bridge_offline_eval._dbox_inspired_decomposition_system_prompt(),
                run_bridge_offline_eval._codehelp_codeaid_no_direct_solution_system_prompt(),
                run_bridge_offline_eval._socratic_no_answer_system_prompt(),
                run_bridge_offline_eval._bridge_inspired_expert_decision_system_prompt(),
            ]
        )

        self.assertIn("full predicate condition", prompts)
        self.assertIn("answer-bearing slots", prompts)
        for concrete_phrase in ["u/v/LCA", "parent/neighbor of LCA", "path = root-path", "check direction rules", "full check condition"]:
            self.assertNotIn(concrete_phrase, prompts)

    def test_bridge_contract_prompt_blocks_definition_first_and_followup_action_leaks(self):
        prompt = run_bridge_offline_eval._bridge_contract_tutor_system_prompt(
            {
                "missing_bridge": {
                    "family": "representation_state_bridge",
                    "subtype": "state.lazy_semantics",
                    "known_focus": "segment_tree.lazy",
                    "description": "学生说不清一个标记表示还没做什么。",
                },
                "allowed_help_level": "L2",
                "help_forms": ["micro_example"],
                "forbidden_content": ["不要直接给完整表示含义。"],
                "leakage_risk": "high",
            }
        )

        self.assertIn("不要用开头定义句", prompt)
        self.assertIn("把当前 missing bridge 命名或解释完", prompt)
        self.assertIn("不要在同一轮", prompt)
        self.assertIn("后续动作", prompt)
        self.assertIn("边界方向", prompt)

    def test_dbox_prompt_blocks_canonical_template_and_definition_leaks(self):
        prompt = run_bridge_offline_eval._dbox_inspired_decomposition_system_prompt()

        self.assertIn("不要把经典模板或标准定义搬给学生", prompt)
        self.assertIn("不要先给概念定义再追问", prompt)
        self.assertIn("不要把 current_substep 写成答案句", prompt)

    def test_stage_latency_and_stage_errors_are_recorded(self):
        rows = [{"id": "case_latency", "student_message": "我不会。"}]

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "strategy_generation_blocked",
                "missing_bridge": {
                    "family": "unknown_bridge",
                    "subtype": "unknown",
                    "description": "信息不足。",
                    "evidence": ["学生说不会"],
                    "known_focus": "unknown",
                    "needs_new_focus": True,
                },
                "help_seeking_type": "unclear",
                "allowed_help_level": "L1",
                "help_form": "question",
                "forbidden_content": ["不要给完整题解。"],
                "leakage_risk": "unknown",
                "confidence": 0.6,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "你先贴题面。", "level": "L1"}

        def fake_leakage(**kwargs):
            return {"_failed": True, "_error": "timeout", "safe_action": "pass"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
        )

        result = result_rows[0]
        self.assertIn("bridge_judge_latency_ms", result["latency_ms"])
        self.assertIn("tutor_latency_ms", result["latency_ms"])
        self.assertIn("leakage_judge_latency_ms", result["latency_ms"])
        self.assertEqual(0, result["retry_count"])
        self.assertEqual("timeout", result["stage_errors"]["leakage_judge"])

    def test_chat_thinking_mode_is_available_during_tutor_stage(self):
        rows = [{"id": "case_thinking", "student_message": "我不会。"}]
        captured_modes = []

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "strategy_generation_blocked",
                "missing_bridge": {
                    "family": "unknown_bridge",
                    "subtype": "unknown",
                    "description": "信息不足。",
                    "evidence": ["学生说不会"],
                    "known_focus": "unknown",
                    "needs_new_focus": True,
                },
                "help_seeking_type": "unclear",
                "allowed_help_level": "L1",
                "help_form": "question",
                "forbidden_content": ["不要给完整题解。"],
                "leakage_risk": "unknown",
                "confidence": 0.6,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            captured_modes.append(os.environ.get("NOI_CHAT_THINKING_MODE"))
            return {"response_text": "你先贴题面。", "level": "L1"}

        def fake_leakage(**kwargs):
            return {"leakage_level": 0, "safe_action": "pass"}

        with patch.dict(os.environ, {"NOI_CHAT_THINKING_MODE": ""}, clear=False):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=fake_bridge_judge,
                tutor_fn=fake_tutor,
                leakage_judge_fn=fake_leakage,
                chat_thinking_mode="disabled",
            )

        self.assertEqual(["disabled"], captured_modes)
        self.assertEqual("disabled", result_rows[0]["models"]["chat_thinking_mode"])

    def test_bridge_judge_retries_transient_failed_result(self):
        rows = [{"id": "case_retry", "student_message": "我不会。"}]
        attempts = []

        def fake_bridge_judge(**kwargs):
            attempts.append(kwargs["student_message"])
            if len(attempts) == 1:
                return {"_failed": True, "_reason": "InternalServerError: 503 busy"}
            return {
                "problem_solving_state": "strategy_generation_blocked",
                "missing_bridge": {
                    "family": "unknown_bridge",
                    "subtype": "unknown",
                    "description": "信息不足。",
                    "evidence": ["学生说不会"],
                    "known_focus": "unknown",
                    "needs_new_focus": True,
                },
                "help_seeking_type": "unclear",
                "allowed_help_level": "L1",
                "help_form": "question",
                "forbidden_content": ["不要给完整题解。"],
                "leakage_risk": "unknown",
                "confidence": 0.6,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "你先贴题面。", "level": "L1"}

        def fake_leakage(**kwargs):
            return {"leakage_level": 0, "safe_action": "pass"}

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            max_retries=1,
        )

        self.assertEqual(2, len(attempts))
        self.assertFalse(result_rows[0].get("error"))
        self.assertEqual(1, result_rows[0]["retry_count"])

    def test_default_judge_provider_is_passed_to_offline_judges(self):
        rows = [{"id": "case_provider", "student_message": "我不会。"}]
        captured = {"bridge": [], "leakage": [], "repair": []}

        def fake_bridge_judge(**kwargs):
            captured["bridge"].append(kwargs["judge_provider"])
            return {
                "problem_solving_state": "strategy_generation_blocked",
                "missing_bridge": {
                    "family": "unknown_bridge",
                    "subtype": "unknown",
                    "description": "信息不足。",
                    "evidence": ["学生说不会"],
                    "known_focus": "unknown",
                    "needs_new_focus": True,
                },
                "help_seeking_type": "unclear",
                "allowed_help_level": "L1",
                "help_form": "question",
                "forbidden_content": ["不要给完整题解。"],
                "leakage_risk": "high",
                "confidence": 0.6,
                "reason": "unit test",
            }

        def fake_tutor(row, messages, bridge_result):
            return {"response_text": "完整答案是这样。", "level": "L3"}

        def fake_leakage(**kwargs):
            captured["leakage"].append(kwargs["judge_provider"])
            return {"leakage_level": 3, "safe_action": "rewrite"}

        def fake_repair(**kwargs):
            captured["repair"].append(kwargs["judge_provider"])
            return {
                "repaired_response": "先说你的尝试。",
                "repair_notes": "unit test",
                "removed_elements": [],
                "still_needs_leakage_check": True,
            }

        result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
            rows,
            bridge_judge_fn=fake_bridge_judge,
            tutor_fn=fake_tutor,
            leakage_judge_fn=fake_leakage,
            repair_fn=fake_repair,
            judge_provider="kimi",
        )

        self.assertEqual(["kimi"], captured["bridge"])
        self.assertEqual(["kimi", "kimi"], captured["leakage"])
        self.assertEqual(["kimi"], captured["repair"])
        self.assertEqual("kimi", result_rows[0]["models"]["judge_provider"])

    def test_write_result_rows_emits_jsonl(self):
        rows = [{"case_id": "case_1", "bridge_judge_result": {"confidence": 0.9}}]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "out" / "results.jsonl"

            run_bridge_offline_eval.write_result_rows(path, rows)

            loaded = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(rows, loaded)

    def test_main_writes_summary_and_output_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            seed_path = Path(tmpdir) / "seed.jsonl"
            output_path = Path(tmpdir) / "results.jsonl"
            seed_path.write_text(
                json.dumps(
                    {
                        "id": "case_1",
                        "problem_ref": "P1001",
                        "student_message": "我不会",
                        "problem_context": "简单题。",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            captured_kwargs = {}

            def fake_rows(rows, **kwargs):
                captured_kwargs.update(kwargs)
                return [{"case_id": rows[0]["id"], "error": ""}]

            stdout = io.StringIO()
            with patch.object(
                run_bridge_offline_eval,
                "run_bridge_offline_eval_rows",
                side_effect=fake_rows,
            ), contextlib.redirect_stdout(stdout):
                exit_code = run_bridge_offline_eval.main(
                    [
                        "--input-jsonl",
                        str(seed_path),
                        "--output-jsonl",
                        str(output_path),
                        "--limit",
                        "1",
                        "--chat-model-provider",
                        "deepseek",
                        "--tutor-mode",
                        "bridge_contract",
                        "--guard-mode",
                        "oracle",
                        "--pipeline-mode",
                        "tutor_plus_guard",
                        "--judge-schema-mode",
                        "compact_contract_judge",
                        "--judge-provider",
                        "kimi",
                        "--max-retries",
                        "2",
                        "--chat-thinking-mode",
                        "disabled",
                    ]
                )

            self.assertEqual(0, exit_code)
            self.assertEqual("deepseek", captured_kwargs["chat_model_provider"])
            self.assertEqual("bridge_contract", captured_kwargs["tutor_mode"])
            self.assertEqual("oracle", captured_kwargs["guard_mode"])
            self.assertEqual("tutor_plus_guard", captured_kwargs["pipeline_mode"])
            self.assertEqual("compact_contract_judge", captured_kwargs["judge_schema_mode"])
            self.assertEqual("kimi", captured_kwargs["judge_provider"])
            self.assertEqual(2, captured_kwargs["max_retries"])
            self.assertEqual("disabled", captured_kwargs["chat_thinking_mode"])
            self.assertIn('"case_count": 1', stdout.getvalue())
            written = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([{"case_id": "case_1", "error": ""}], written)

    def test_cli_accepts_single_llm_structured_tutor_mode(self):
        args = run_bridge_offline_eval._parse_args(
            [
                "--tutor-mode",
                "single_llm_structured",
                "--pipeline-mode",
                "tutor_only",
            ]
        )

        self.assertEqual("single_llm_structured", args.tutor_mode)
        self.assertEqual("tutor_only", args.pipeline_mode)

    def test_cli_accepts_enhanced_prompt_only_tutor_mode(self):
        args = run_bridge_offline_eval._parse_args(
            [
                "--tutor-mode",
                "enhanced_prompt_only",
                "--pipeline-mode",
                "tutor_only_no_diagnosis",
            ]
        )

        self.assertEqual("enhanced_prompt_only", args.tutor_mode)
        self.assertEqual("tutor_only_no_diagnosis", args.pipeline_mode)


if __name__ == "__main__":
    unittest.main()
