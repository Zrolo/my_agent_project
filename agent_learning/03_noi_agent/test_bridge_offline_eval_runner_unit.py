import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
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

        def fake_leakage(**kwargs):
            calls.append(("leakage", kwargs["candidate_response"]))
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
        self.assertEqual("状态设 dp[j] 表示时间 j 内的最大价值。\n\n[LEVEL:L2]", result["candidate_response_text"])
        self.assertEqual("先别把状态写死。你想一想：时间变化后，至少要保留哪一个量？\n\n[LEVEL:L2]", result["final_response_text"])
        self.assertEqual("repair", result["final_response_source"])
        self.assertTrue(result["repair_applied"])
        self.assertFalse(result["blocked"])
        self.assertEqual(4, result["llm_call_count"])
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

    def test_tutor_stage_retries_transient_exception(self):
        rows = [{"id": "case_tutor_retry", "student_message": "我知道像背包，但状态怎么设？"}]
        attempts = []

        def fake_bridge_judge(**kwargs):
            return {
                "problem_solving_state": "modeling_representation_gap",
                "missing_bridge": {
                    "family": "representation_state_bridge",
                    "subtype": "state.dp_state_semantics",
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
                    "subtype": "predicate.check_truth_direction",
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

    def test_bridge_contract_tutor_injects_bridge_result_before_student_turn(self):
        rows = [{"id": "case_contract", "problem_ref": "P1001", "student_message": "我不会。"}]
        captured_messages = []

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

        def fake_chat(messages, student_id, problem_id, chat_model_provider=None):
            captured_messages.extend(messages)
            return "回复", "回复", "L2"

        def fake_leakage(**kwargs):
            return {"leakage_level": 0, "safe_action": "pass"}

        with patch.object(run_bridge_offline_eval, "noi_agent_chat", side_effect=fake_chat):
            result_rows = run_bridge_offline_eval.run_bridge_offline_eval_rows(
                rows,
                bridge_judge_fn=fake_bridge_judge,
                leakage_judge_fn=fake_leakage,
                tutor_mode="bridge_contract",
                chat_model_provider="deepseek",
            )

        joined = "\n".join(message["content"] for message in captured_messages)
        self.assertIn("Bridge Contract", joined)
        self.assertIn("predicate_bridge", joined)
        self.assertIn("不要直接给完整 check 条件", joined)
        self.assertIn("桥梁导向微型例子", joined)
        self.assertIn("先说明这个例子要观察的桥梁问题", joined)
        self.assertIn("抽象成一句可迁移规则", joined)
        self.assertEqual("bridge_contract", result_rows[0]["tutor_mode"])
        self.assertEqual("bridge_contract", result_rows[0]["tutor_response"]["tutor_mode"])

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
                    "subtype": "state.dp_state_semantics",
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
        self.assertIn("如果 dp 数组的格子代表", system_prompt)
        self.assertIn("让学生自己说出状态格子应该记什么", system_prompt)
        self.assertIn("self_check 必须标为 medium 或 high", system_prompt)

    def test_single_llm_structured_prompt_is_bridge_first_topic_second(self):
        system_prompt = run_bridge_offline_eval._single_llm_structured_system_prompt()

        self.assertIn("bridge-first, topic-second, focus-top-k", system_prompt)
        self.assertIn("先用 primary_bridge_family 决定教学动作", system_prompt)
        self.assertIn("algorithm_topic 只作为轻量上下文", system_prompt)
        self.assertIn("不要试图覆盖所有具体算法", system_prompt)
        self.assertIn("具体算法例子只是 regression boundary", system_prompt)
        self.assertIn("不要在微型例子里预填关键操作的一半", system_prompt)
        self.assertIn("先让学生列出观察对象、影响因素或可行性判断", system_prompt)

    def test_bridge_contract_message_is_bridge_first_not_algorithm_specific(self):
        message = run_bridge_offline_eval._bridge_contract_message(
            {
                "missing_bridge": {
                    "family": "aggregation_contribution_bridge",
                    "subtype": "aggregation.tree_path_difference_marking",
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
        self.assertEqual(["kimi"], captured["leakage"])
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
