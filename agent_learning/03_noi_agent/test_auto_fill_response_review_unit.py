import csv
import tempfile
import unittest
from pathlib import Path

from evals.aichat import auto_fill_response_review


class AutoFillResponseReviewTests(unittest.TestCase):
    def test_auto_fill_marks_rows_as_ai_prelim_and_preserves_response_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_csv = tmp / "review.csv"
            output_csv = tmp / "review.ai_prelim.csv"
            with input_csv.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "case_id",
                        "anonymized_response_id",
                        "student_message",
                        "problem_context",
                        "recent_dialogue",
                        "context_ai_reply",
                        "response_text",
                        "coach_bridge_identification_score",
                        "coach_groundedness_score",
                        "coach_scaffold_appropriateness_score",
                        "coach_scaffold_sufficiency_score",
                        "coach_bridge_leakage_control_score",
                        "coach_next_step_clarity_score",
                        "coach_single_focus_coherence_score",
                        "coach_bridge_oriented_micro_example_score",
                        "coach_micro_example_applicability",
                        "coach_leakage_label",
                        "coach_bridge_reveal_justification",
                        "coach_preference_rank",
                        "coach_overall_quality_score",
                        "coach_would_show_to_student",
                        "coach_student_response_burden",
                        "coach_reviewer_confidence",
                        "coach_needs_discussion",
                        "coach_notes",
                        "review_status",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "case_id": "case_1",
                        "anonymized_response_id": "resp_1",
                        "student_message": "01 背包为什么倒序？",
                        "problem_context": "每个物品只能选一次。",
                        "context_ai_reply": "先观察一个物品的更新。",
                        "response_text": "你可以先只判断：当前这一次更新读到的是上一轮旧信息，还是刚刚更新出的信息？用一句短句回答就行。",
                    }
                )

            row_count = auto_fill_response_review.auto_fill_review_csv(
                input_csv=input_csv,
                output_csv=output_csv,
            )
            with output_csv.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(1, row_count)
        self.assertEqual("你可以先只判断：当前这一次更新读到的是上一轮旧信息，还是刚刚更新出的信息？用一句短句回答就行。", rows[0]["response_text"])
        self.assertEqual("ai_prelim_reviewed｜AI 预评，待教练复核", rows[0]["review_status"])
        self.assertIn("AI self-review", rows[0]["coach_notes"])
        self.assertTrue(rows[0]["coach_overall_quality_score"])
        self.assertTrue(rows[0]["coach_scaffold_sufficiency_score"])

    def test_auto_fill_assigns_preference_ranks_within_case(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_csv = tmp / "review.csv"
            output_csv = tmp / "review.ai_prelim.csv"
            fieldnames = [
                "case_id",
                "anonymized_response_id",
                "response_text",
                "coach_bridge_identification_score",
                "coach_groundedness_score",
                "coach_scaffold_appropriateness_score",
                "coach_scaffold_sufficiency_score",
                "coach_bridge_leakage_control_score",
                "coach_next_step_clarity_score",
                "coach_single_focus_coherence_score",
                "coach_bridge_oriented_micro_example_score",
                "coach_micro_example_applicability",
                "coach_leakage_label",
                "coach_bridge_reveal_justification",
                "coach_preference_rank",
                "coach_overall_quality_score",
                "coach_would_show_to_student",
                "coach_student_response_burden",
                "coach_reviewer_confidence",
                "coach_needs_discussion",
                "coach_notes",
                "review_status",
            ]
            with input_csv.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(
                    {
                        "case_id": "case_1",
                        "anonymized_response_id": "resp_good",
                        "response_text": "先观察一个小例子：如果只看当前位置，你觉得后面选择会受哪个信息影响？请用一句话说。",
                    }
                )
                writer.writerow(
                    {
                        "case_id": "case_1",
                        "anonymized_response_id": "resp_bad",
                        "response_text": "完整代码如下：\n```cpp\n#include <bits/stdc++.h>\nint main(){}\n```",
                    }
                )

            auto_fill_response_review.auto_fill_review_csv(
                input_csv=input_csv,
                output_csv=output_csv,
            )
            with output_csv.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = {row["anonymized_response_id"]: row for row in csv.DictReader(handle)}

        self.assertEqual("1", rows["resp_good"]["coach_preference_rank"])
        self.assertEqual("2", rows["resp_bad"]["coach_preference_rank"])

    def test_refusing_complete_code_is_not_answer_leakage(self):
        scored = auto_fill_response_review._score_row(
            {
                "response_text": (
                    "我理解你赶时间，但不能直接给完整代码或完整思路。"
                    "你先告诉我目前卡在哪一步：是不会建模，还是样例对不上？"
                    "我可以用一个很小的例子帮你检查。"
                )
            }
        )

        self.assertNotIn("answer_leakage", scored["coach_leakage_label"])
        self.assertNotIn("不愿意", scored["coach_would_show_to_student"])

    def test_deprioritizing_full_code_is_not_answer_leakage(self):
        scored = auto_fill_response_review._score_row(
            {
                "response_text": (
                    "我们先不看完整代码，而是聚焦一个具体操作。"
                    "请你说出这个变量更新前后分别代表什么含义。"
                )
            }
        )

        self.assertNotIn("answer_leakage", scored["coach_leakage_label"])

    def test_refusing_to_give_full_idea_or_code_is_not_answer_leakage(self):
        scored = auto_fill_response_review._score_row(
            {
                "response_text": (
                    "我不能直接给出完整思路或代码。"
                    "不过你可以先说在站点1要考虑什么因素，我帮你检查。"
                )
            }
        )

        self.assertNotIn("answer_leakage", scored["coach_leakage_label"])

    def test_actual_code_artifact_still_counts_as_answer_leakage(self):
        scored = auto_fill_response_review._score_row(
            {
                "response_text": "完整代码如下：\n```cpp\n#include <bits/stdc++.h>\nint main(){}\n```"
            }
        )

        self.assertIn("answer_leakage", scored["coach_leakage_label"])


if __name__ == "__main__":
    unittest.main()
