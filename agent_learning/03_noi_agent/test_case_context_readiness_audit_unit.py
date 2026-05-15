import unittest

from evals.aichat.audit_case_context_readiness import audit_case_row, render_report, summarize_audit_rows


class CaseContextReadinessAuditTests(unittest.TestCase):
    def test_short_vague_question_without_dialogue_requires_clarification(self):
        audit = audit_case_row(
            {
                "case_id": "case_short",
                "student_message": "分支该怎么列？",
                "recent_dialogue": "N/A",
                "problem_context": "背包计数题，需要统计缺失每个物品后的方案数。",
                "bridge_bucket": "transition_recurrence_source",
            }
        )

        self.assertEqual("insufficient", audit["context_sufficiency"])
        self.assertEqual("vague", audit["current_question_specificity"])
        self.assertEqual("clarify_context", audit["expected_tutor_move"])
        self.assertEqual("no", audit["model_should_infer_bridge"])
        self.assertIn("short_vague_question_without_dialogue", audit["audit_reasons"])

    def test_short_question_with_prior_ai_context_is_followup_scaffold(self):
        audit = audit_case_row(
            {
                "case_id": "case_followup",
                "student_message": "分支该怎么列？",
                "recent_dialogue": "学生：我已经会算全部物品的方案数了。\nAI：下一步先想某个物品消失时，原来的方案会少掉哪一类。",
                "problem_context": "背包计数题，需要统计缺失每个物品后的方案数。",
                "bridge_bucket": "transition_recurrence_source",
            }
        )

        self.assertEqual("sufficient", audit["context_sufficiency"])
        self.assertEqual("pronoun_dependent", audit["current_question_specificity"])
        self.assertEqual("continue_prior_scaffold", audit["expected_tutor_move"])
        self.assertEqual("yes", audit["model_should_infer_bridge"])
        self.assertIn("recent_dialogue_ends_with_assistant", audit["audit_reasons"])

    def test_specific_question_without_dialogue_is_partial_micro_scaffold(self):
        audit = audit_case_row(
            {
                "case_id": "case_specific",
                "student_message": "我知道要二分答案，但是 check(mid) 到底返回 true 还是 false 我总写反。",
                "recent_dialogue": "N/A",
                "problem_context": "给定一个最大值限制，判断是否能在限制内完成。",
                "bridge_bucket": "predicate_check_condition",
            }
        )

        self.assertEqual("partial", audit["context_sufficiency"])
        self.assertEqual("specific", audit["current_question_specificity"])
        self.assertEqual("micro_scaffold", audit["expected_tutor_move"])
        self.assertEqual("low_confidence_only", audit["model_should_infer_bridge"])

    def test_direct_answer_request_routes_to_safe_refusal(self):
        audit = audit_case_row(
            {
                "case_id": "case_policy",
                "student_message": "直接给我完整代码吧。",
                "recent_dialogue": "N/A",
                "problem_context": "图论最短路题。",
                "bridge_bucket": "direct_answer_code_confirmation",
            }
        )

        self.assertEqual("policy_request", audit["current_question_specificity"])
        self.assertEqual("safe_refusal", audit["expected_tutor_move"])
        self.assertEqual("no", audit["model_should_infer_bridge"])

    def test_summary_counts_audit_dimensions(self):
        rows = [
            audit_case_row({"case_id": "a", "student_message": "分支该怎么列？", "recent_dialogue": "N/A"}),
            audit_case_row(
                {
                    "case_id": "b",
                    "student_message": "为什么这样转？",
                    "recent_dialogue": "学生：我会状态了。\nAI：你先看当前转移来自哪一步。",
                }
            ),
        ]

        summary = summarize_audit_rows(rows)

        self.assertEqual(2, summary["row_count"])
        self.assertEqual(1, summary["context_sufficiency_counts"]["insufficient"])
        self.assertEqual(1, summary["context_sufficiency_counts"]["sufficient"])

    def test_render_report_uses_dataset_label_in_title_and_counterpart_links(self):
        summary = {
            "row_count": 50,
            "context_sufficiency_counts": {"sufficient": 45, "partial": 5},
            "question_specificity_counts": {"specific": 10},
            "expected_tutor_move_counts": {"micro_scaffold": 10},
            "model_should_infer_bridge_counts": {"yes": 10},
            "recommended_use_counts": {"main_scaffold_eval": 10},
        }

        zh_report = render_report(summary, language="zh", dataset_label="v4")
        en_report = render_report(summary, language="en", dataset_label="v4")

        self.assertIn("Held-out v4 50 Context Readiness Audit 20260514", zh_report)
        self.assertIn("heldout_v4_50_context_readiness_audit_20260514.md", zh_report)
        self.assertIn("Held-out v4 50 Context Readiness Audit 20260514", en_report)
        self.assertIn("heldout_v4_50_context_readiness_audit_20260514.zh.md", en_report)


if __name__ == "__main__":
    unittest.main()
