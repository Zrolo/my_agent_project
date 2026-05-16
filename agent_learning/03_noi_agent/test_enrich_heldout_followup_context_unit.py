import unittest

from evals.aichat.enrich_heldout_followup_context import enrich_rows_for_followup_scaffold
from evals.aichat.audit_case_context_readiness import audit_case_row


class EnrichHeldoutFollowupContextTests(unittest.TestCase):
    def test_enriches_short_no_dialogue_case_into_followup_context(self):
        rows = [
            {
                "case_id": "heldout_v2_luogu_007",
                "problem_source_id": "P4141",
                "problem_title": "消失之物",
                "bridge_bucket": "transition_recurrence_source",
                "student_message": "分支该怎么列？",
                "recent_dialogue": "N/A",
                "problem_context": "背包计数题，需要统计缺失每个物品后的方案数。",
            }
        ]

        enriched = enrich_rows_for_followup_scaffold(rows, version="v4")

        row = enriched[0]
        self.assertEqual("heldout_v4_luogu_001", row["case_id"])
        self.assertEqual("heldout_v2_luogu_007", row["source_case_id"])
        self.assertEqual("synthetic_followup_context_added", row["context_enrichment_status"])
        self.assertIn("学生：", row["recent_dialogue"])
        self.assertIn("AI：", row["recent_dialogue"])
        self.assertNotIn("分支该怎么列？", row["recent_dialogue"])
        self.assertEqual("followup", row["turn_position"])
        self.assertEqual("followup_after_context_probe", row["context_type"])
        self.assertEqual("continue_prior_scaffold", row["expected_tutor_move"])
        self.assertEqual("分支该怎么列？", row["student_reply_to_prior_scaffold"])
        self.assertEqual(row["prior_ai_scaffold"], row["context_ai_reply"])

        audit = audit_case_row(row)
        self.assertNotEqual("insufficient", audit["context_sufficiency"])
        self.assertEqual("recent_dialogue_ends_with_assistant", audit["recent_dialogue_status"])

    def test_synthetic_probes_vary_across_short_student_question_shapes(self):
        rows = [
            {
                "case_id": "state_a",
                "bridge_bucket": "state_representation_semantics",
                "student_message": "dp 这一格是啥意思？",
                "recent_dialogue": "N/A",
                "problem_context": "DP 题。",
            },
            {
                "case_id": "state_b",
                "bridge_bucket": "state_representation_semantics",
                "student_message": "状态维度怎么定？",
                "recent_dialogue": "N/A",
                "problem_context": "DP 题。",
            },
            {
                "case_id": "transition_a",
                "bridge_bucket": "transition_recurrence_source",
                "student_message": "这里从哪转来？",
                "recent_dialogue": "N/A",
                "problem_context": "树形 DP 题。",
            },
        ]

        enriched = enrich_rows_for_followup_scaffold(rows, version="v4")
        probes = [row["prior_ai_scaffold"] for row in enriched]

        self.assertEqual(len(probes), len(set(probes)))
        for row in enriched:
            self.assertNotIn(row["student_message"], row["recent_dialogue"])

    def test_preserves_existing_followup_context_and_renumbers_id(self):
        rows = [
            {
                "case_id": "heldout_v2_luogu_011",
                "problem_source_id": "P13680",
                "bridge_bucket": "transition_recurrence_source",
                "student_message": "为什么能这样转？",
                "recent_dialogue": "学生：样例能跟。\nAI：你先说最卡的一步。",
                "context_ai_reply": "你先说最卡的一步。",
            }
        ]

        enriched = enrich_rows_for_followup_scaffold(rows, version="v4")

        row = enriched[0]
        self.assertEqual("heldout_v4_luogu_001", row["case_id"])
        self.assertEqual("heldout_v2_luogu_011", row["source_case_id"])
        self.assertEqual("context_preserved", row["context_enrichment_status"])
        self.assertEqual("学生：样例能跟。\nAI：你先说最卡的一步。", row["recent_dialogue"])


if __name__ == "__main__":
    unittest.main()
