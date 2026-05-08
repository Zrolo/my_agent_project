import io
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

            def fake_rows(rows, **kwargs):
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
                    ]
                )

            self.assertEqual(0, exit_code)
            self.assertIn('"case_count": 1', stdout.getvalue())
            written = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([{"case_id": "case_1", "error": ""}], written)


if __name__ == "__main__":
    unittest.main()
