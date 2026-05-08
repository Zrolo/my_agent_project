import contextlib
import io
import json
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
        self.assertIn("CASE_DONE index=1 total=1 case_id=case_1", progress.getvalue())

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
        self.assertEqual(1, result_rows[0]["focus_registry_size"])

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
        self.assertEqual("bridge_contract", result_rows[0]["tutor_mode"])
        self.assertEqual("bridge_contract", result_rows[0]["tutor_response"]["tutor_mode"])

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
                        "--judge-provider",
                        "kimi",
                        "--max-retries",
                        "2",
                    ]
                )

            self.assertEqual(0, exit_code)
            self.assertEqual("deepseek", captured_kwargs["chat_model_provider"])
            self.assertEqual("bridge_contract", captured_kwargs["tutor_mode"])
            self.assertEqual("oracle", captured_kwargs["guard_mode"])
            self.assertEqual("kimi", captured_kwargs["judge_provider"])
            self.assertEqual(2, captured_kwargs["max_retries"])
            self.assertIn('"case_count": 1', stdout.getvalue())
            written = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([{"case_id": "case_1", "error": ""}], written)


if __name__ == "__main__":
    unittest.main()
