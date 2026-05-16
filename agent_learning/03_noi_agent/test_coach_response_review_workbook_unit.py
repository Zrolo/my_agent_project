import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import export_coach_response_review_workbook as response_workbook


class CoachResponseReviewWorkbookTests(unittest.TestCase):
    def test_build_review_rows_hides_baseline_identity_and_uses_final_response(self):
        result_rows = [
            {
                "case_id": "case_1",
                "problem_ref": "P1048",
                "problem_source_platform": "luogu",
                "problem_source_id": "P1048",
                "problem_source_url": "https://www.luogu.com.cn/problem/P1048",
                "problem_statement": "给定 n 个草药，每个草药有时间和价值，在总时间 M 内选择若干草药使价值最大。",
                "problem_statement_public_summary": "洛谷 P1048 采药：在总时间限制内选择若干物品最大化价值。",
                "problem_statement_rights_note": "本地教练评审使用必要题面；公开材料仅保留来源链接和改写摘要。",
                "problem_statement_access_level": "public_summary_only",
                "student_message": "状态怎么设？",
                "problem_context": "采药。",
                "recent_dialogue": "user: 我知道要 DP",
                "context_ai_reply": "那你先想想状态应该保留哪些信息。",
                "tutor_mode": "bridge_contract",
                "guard_mode": "predicted",
                "models": {"tutor_model_provider": "deepseek", "chat_thinking_mode": "disabled"},
                "candidate_response_text": "状态设 dp[j]。",
                "final_response_text": "先说说时间变化后要保留什么。",
                "final_response_source": "repair",
            }
        ]

        rows, key_rows = response_workbook.build_review_rows(result_rows, shuffle_seed=7)

        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual("case_1", row["case_id"])
        self.assertEqual("luogu", row["problem_source_platform"])
        self.assertEqual("P1048", row["problem_source_id"])
        self.assertEqual("https://www.luogu.com.cn/problem/P1048", row["problem_source_url"])
        self.assertEqual(
            "给定 n 个草药，每个草药有时间和价值，在总时间 M 内选择若干草药使价值最大。",
            row["problem_statement"],
        )
        self.assertEqual(
            "洛谷 P1048 采药：在总时间限制内选择若干物品最大化价值。",
            row["problem_statement_public_summary"],
        )
        self.assertEqual(
            "本地教练评审使用必要题面；公开材料仅保留来源链接和改写摘要。",
            row["problem_statement_rights_note"],
        )
        self.assertEqual("public_summary_only", row["problem_statement_access_level"])
        self.assertEqual("short", row["student_message_length_bucket"])
        self.assertEqual("先说说时间变化后要保留什么。", row["response_text"])
        self.assertEqual("那你先想想状态应该保留哪些信息。", row["context_ai_reply"])
        self.assertEqual("dialogue_mismatch_last_student_differs", row["context_alignment_flag"])
        self.assertNotIn("bridge_contract", row.values())
        self.assertNotIn("deepseek", row.values())
        self.assertEqual("case_1", key_rows[0]["case_id"])
        self.assertEqual(row["anonymized_response_id"], key_rows[0]["anonymized_response_id"])
        self.assertEqual("bridge_contract", key_rows[0]["tutor_mode"])
        self.assertEqual("disabled", key_rows[0]["chat_thinking_mode"])
        self.assertEqual("repair", key_rows[0]["final_response_source"])

    def test_build_review_rows_uses_id_salt_to_avoid_cross_run_collisions(self):
        result_rows = [
            {
                "case_id": "case_1",
                "student_message": "状态怎么设？",
                "final_response_text": "先说说时间变化后要保留什么。",
                "tutor_mode": "bridge_contract",
                "guard_mode": "predicted",
                "pipeline_mode": "tutor_only",
                "final_response_source": "candidate",
            }
        ]

        rows_a, key_rows_a = response_workbook.build_review_rows(
            result_rows,
            shuffle_seed=7,
            id_salt="micro_example_policy_a",
        )
        rows_b, key_rows_b = response_workbook.build_review_rows(
            result_rows,
            shuffle_seed=7,
            id_salt="micro_example_policy_b",
        )

        self.assertNotEqual(rows_a[0]["anonymized_response_id"], rows_b[0]["anonymized_response_id"])
        self.assertEqual(rows_a[0]["anonymized_response_id"], key_rows_a[0]["anonymized_response_id"])
        self.assertEqual(rows_b[0]["anonymized_response_id"], key_rows_b[0]["anonymized_response_id"])

    def test_write_review_csv_has_rubric_columns(self):
        rows, _ = response_workbook.build_review_rows(
            [{"case_id": "case_1", "student_message": "不会", "final_response_text": "先贴题面。"}],
            shuffle_seed=1,
        )
        output = io.StringIO()

        response_workbook.write_review_csv(output, rows)

        output.seek(0)
        reader = csv.DictReader(output)
        self.assertIn("coach_bridge_identification_score", reader.fieldnames)
        self.assertIn("problem_source_platform", reader.fieldnames)
        self.assertIn("problem_source_id", reader.fieldnames)
        self.assertIn("problem_source_url", reader.fieldnames)
        self.assertIn("problem_statement", reader.fieldnames)
        self.assertIn("problem_statement_public_summary", reader.fieldnames)
        self.assertIn("problem_statement_rights_note", reader.fieldnames)
        self.assertIn("problem_statement_access_level", reader.fieldnames)
        self.assertIn("student_message_length_bucket", reader.fieldnames)
        self.assertIn("context_ai_reply", reader.fieldnames)
        self.assertIn("context_alignment_flag", reader.fieldnames)
        self.assertIn("success_criteria", reader.fieldnames)
        self.assertIn("forbidden_content", reader.fieldnames)
        self.assertIn("critical_bridge_boundary", reader.fieldnames)
        self.assertIn("acceptable_reveal", reader.fieldnames)
        self.assertIn("expected_student_next_action", reader.fieldnames)
        self.assertIn("coach_bridge_oriented_micro_example_score", reader.fieldnames)
        self.assertIn("coach_scaffold_sufficiency_score", reader.fieldnames)
        self.assertIn("coach_leakage_label", reader.fieldnames)
        self.assertIn("coach_bridge_reveal_justification", reader.fieldnames)
        self.assertIn("coach_preference_rank", reader.fieldnames)
        self.assertIn("coach_micro_example_applicability", reader.fieldnames)
        self.assertIn("coach_overall_quality_score", reader.fieldnames)
        self.assertIn("coach_would_show_to_student", reader.fieldnames)
        self.assertIn("coach_student_response_burden", reader.fieldnames)
        self.assertIn("coach_reviewer_confidence", reader.fieldnames)
        self.assertIn("coach_needs_discussion", reader.fieldnames)

    def test_build_review_rows_backfills_case_specific_rubric_from_case_source(self):
        result_rows = [
            {
                "case_id": "dialogue_v3_001_state_representation_semantics",
                "problem_ref": "P1001",
                "student_message": "这个状态怎么想？",
                "context_type": "initial_question",
                "turn_position": "initial",
                "student_scaffold_followability": "NA",
                "expected_tutor_move": "micro_step",
                "final_response_text": "先说这个格子对应题面里的哪个对象。",
            }
        ]
        case_source_by_id = {
            "dialogue_v3_001_state_representation_semantics": {
                "case_id": "dialogue_v3_001_state_representation_semantics",
                "missing_bridge": "缺少把题面对象、已处理范围和状态值语义对应起来的表示关系。",
                "success_criteria": ["回复让学生先说清状态下标代表的对象或范围。"],
                "forbidden_content": ["no_exact_state_definition", "no_full_solution"],
                "context_type_zh": "初始提问",
                "turn_position": "initial",
                "student_scaffold_followability_zh": "不适用",
                "expected_tutor_move_zh": "拆成更小一步",
            }
        }

        rows, _ = response_workbook.build_review_rows(
            result_rows,
            shuffle_seed=1,
            case_source_by_id=case_source_by_id,
        )
        row = rows[0]

        self.assertIn("回复让学生先说清状态下标代表的对象或范围", row["success_criteria"])
        self.assertIn("不要直接给出完整状态/表示定义", row["forbidden_content"])
        self.assertNotIn("no_exact_state_definition", row["forbidden_content"])
        self.assertIn("缺少把题面对象", row["critical_bridge_boundary"])
        self.assertIn("可以复述题意", row["acceptable_reveal"])
        self.assertIn("学生下一步应能", row["expected_student_next_action"])
        self.assertEqual("初始提问", row["context_type"])
        self.assertEqual("初始提问", row["turn_position"])
        self.assertEqual("不适用", row["student_scaffold_followability"])
        self.assertEqual("拆成更小一步", row["expected_tutor_move"])

    def test_main_writes_blind_workbook_and_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "results.jsonl"
            output_csv = Path(tmpdir) / "review.csv"
            key_csv = Path(tmpdir) / "review.key.csv"
            input_path.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "student_message": "不会",
                        "final_response_text": "先贴题面。",
                        "tutor_mode": "current_system",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            exit_code = response_workbook.main(
                [
                    "--input-jsonl",
                    str(input_path),
                    "--output-csv",
                    str(output_csv),
                    "--key-csv",
                    str(key_csv),
                    "--shuffle-seed",
                    "3",
                    "--id-salt",
                    "unit_test_run",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(output_csv.exists())
            self.assertTrue(key_csv.exists())
            self.assertIn("anonymized_response_id", output_csv.read_text(encoding="utf-8-sig"))
            self.assertIn("current_system", key_csv.read_text(encoding="utf-8-sig"))

    def test_main_can_backfill_rubric_from_case_source_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "results.jsonl"
            case_path = Path(tmpdir) / "cases.jsonl"
            output_csv = Path(tmpdir) / "review.csv"
            key_csv = Path(tmpdir) / "review.key.csv"
            input_path.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "student_message": "不会",
                        "final_response_text": "先说一个小观察。",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            case_path.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "missing_bridge": "缺少把候选值和可行性方向对应起来。",
                        "success_criteria": ["回复让学生判断 true/false 的含义。"],
                        "forbidden_content": ["no_complete_check_condition"],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            response_workbook.main(
                [
                    "--input-jsonl",
                    str(input_path),
                    "--output-csv",
                    str(output_csv),
                    "--key-csv",
                    str(key_csv),
                    "--case-source-jsonl",
                    str(case_path),
                ]
            )

            content = output_csv.read_text(encoding="utf-8-sig")
            self.assertIn("回复让学生判断 true/false 的含义", content)
            self.assertIn("不要直接给出完整 check/判定条件", content)
            self.assertNotIn("no_complete_check_condition", content)

    def test_context_ai_reply_is_extracted_from_prior_assistant_message(self):
        rows, _ = response_workbook.build_review_rows(
            [
                {
                    "case_id": "case_1",
                    "student_message": "我还是不知道 lazy 是什么。",
                    "prior_messages": [
                        {"role": "user", "content": "区间加怎么处理？"},
                        {"role": "assistant", "content": "先看一次区间加后，父节点和子节点分别更新到了哪一层。"},
                        {"role": "user", "content": "父节点更新了。"},
                    ],
                    "final_response_text": "那你现在只观察子节点是否同步更新。",
                }
            ],
            shuffle_seed=1,
        )

        self.assertEqual(
            "先看一次区间加后，父节点和子节点分别更新到了哪一层。",
            rows[0]["context_ai_reply"],
        )
        self.assertEqual("dialogue_mismatch_last_student_differs", rows[0]["context_alignment_flag"])
        self.assertIn("assistant:", rows[0]["recent_dialogue"])

    def test_context_alignment_flag_marks_recent_dialogue_that_ends_with_ai(self):
        rows, _ = response_workbook.build_review_rows(
            [
                {
                    "case_id": "case_1",
                    "student_message": "为什么能这样转？",
                    "recent_dialogue": "学生：我看了题面。\nAI：你先说最卡的一步。",
                    "final_response_text": "先把当前关系拆成一个小问题。",
                }
            ],
            shuffle_seed=1,
        )

        self.assertEqual("aligned_prior_context_ends_with_assistant", rows[0]["context_alignment_flag"])

    def test_context_alignment_flag_marks_missing_recent_dialogue(self):
        rows, _ = response_workbook.build_review_rows(
            [
                {
                    "case_id": "case_1",
                    "student_message": "状态怎么设？",
                    "recent_dialogue": "N/A",
                    "final_response_text": "先说一格需要记录什么。",
                }
            ],
            shuffle_seed=1,
        )

        self.assertEqual("no_recent_dialogue", rows[0]["context_alignment_flag"])

    def test_student_message_length_bucket_uses_stable_thresholds(self):
        result_rows = [
            {
                "case_id": "short",
                "student_message": "状态怎么设？",
                "final_response_text": "先说说。",
            },
            {
                "case_id": "medium_short",
                "student_message": "我知道要二分答案，但是 check(mid) 到底返回 true 还是 false 我总写反。",
                "final_response_text": "先看谓词。",
            },
            {
                "case_id": "medium_long",
                "student_message": "我大概知道要用树上差分，也知道路径两端要打标记，但是到 LCA 的时候到底要加还是减，我每次都背公式，换一题就忘。尤其是多条路径叠加时，我不知道每个点统计到的值到底代表什么。",
                "final_response_text": "先比较贡献。",
            },
            {
                "case_id": "long",
                "student_message": (
                    "我写了一个线段树区间加区间求和的代码，pushdown 里面先把 lazy 下传到左右儿子，"
                    "然后清空当前节点。我能照模板写出来，但我不理解为什么查询只查到一部分区间时必须先 pushdown。"
                    "如果不下传，我感觉父节点 sum 已经是对的，为什么子节点会影响答案？"
                    "另外我还想知道，如果连续做两次区间加，lazy 标记到底是覆盖还是累加，什么时候才真的把这些变化写到叶子节点上。"
                ),
                "final_response_text": "先观察一次部分查询。",
            },
        ]

        rows, _ = response_workbook.build_review_rows(result_rows, shuffle_seed=1)
        bucket_by_case = {row["case_id"]: row["student_message_length_bucket"] for row in rows}

        self.assertEqual("short", bucket_by_case["short"])
        self.assertEqual("medium_short", bucket_by_case["medium_short"])
        self.assertEqual("medium_long", bucket_by_case["medium_long"])
        self.assertEqual("long", bucket_by_case["long"])


if __name__ == "__main__":
    unittest.main()
