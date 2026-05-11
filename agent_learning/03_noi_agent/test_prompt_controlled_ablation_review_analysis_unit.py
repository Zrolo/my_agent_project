import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat.analyze_prompt_controlled_ablation_review import (
    build_effect_summary,
    build_system_summary,
    merge_review_and_key_rows,
    student_ready_pass,
    write_analysis_outputs,
)


def _review_row(case_id, response_id, overall, rank, leakage="no_leakage", show="yes", score=2):
    return {
        "case_id": case_id,
        "anonymized_response_id": response_id,
        "coach_bridge_identification_score": score,
        "coach_groundedness_score": score,
        "coach_scaffold_appropriateness_score": score,
        "coach_bridge_leakage_control_score": score,
        "coach_next_step_clarity_score": score,
        "coach_single_focus_coherence_score": score,
        "coach_bridge_oriented_micro_example_score": score,
        "coach_micro_example_applicability": "applicable",
        "coach_leakage_label": leakage,
        "coach_preference_rank": rank,
        "coach_overall_quality_score": overall,
        "coach_would_show_to_student": show,
        "coach_reviewer_confidence": "high",
        "coach_needs_discussion": "no",
        "coach_notes": "note",
        "review_status": "labeled",
    }


def _key_row(response_id, system):
    return {
        "anonymized_response_id": response_id,
        "case_id": "case",
        "tutor_mode": system,
        "guard_mode": "none",
        "pipeline_mode": "prompt_controlled_ablation",
        "final_response_source": "candidate",
        "repair_applied": "false",
        "blocked": "false",
    }


class PromptControlledAblationReviewAnalysisTests(unittest.TestCase):
    def test_merge_review_and_key_rows_normalizes_choices_and_scores(self):
        rows = merge_review_and_key_rows(
            [
                _review_row(
                    "case_a",
                    "resp_a",
                    "5｜优秀：非常愿意给学生看",
                    "1｜同题中最好",
                    leakage="minor_bridge_leakage｜轻微桥梁泄露",
                    show="yes｜愿意：可以直接给学生看",
                )
            ],
            [_key_row("resp_a", "enhanced_prompt_only")],
        )

        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual("enhanced_prompt_only", row["system"])
        self.assertEqual(5.0, row["overall_quality_score"])
        self.assertEqual("minor_bridge_leakage", row["leakage_label"])
        self.assertEqual("yes", row["would_show_to_student"])
        self.assertEqual(1.0, row["preference_rank"])

    def test_student_ready_pass_requires_quality_show_safety_and_nonzero_scores(self):
        safe = merge_review_and_key_rows(
            [_review_row("case_a", "resp_a", 4, 1)],
            [_key_row("resp_a", "enhanced_prompt_only")],
        )[0]
        leaky = merge_review_and_key_rows(
            [_review_row("case_a", "resp_b", 4, 1, leakage="major_bridge_leakage")],
            [_key_row("resp_b", "enhanced_prompt_only")],
        )[0]
        weak = merge_review_and_key_rows(
            [_review_row("case_a", "resp_c", 4, 1, score=0)],
            [_key_row("resp_c", "enhanced_prompt_only")],
        )[0]

        self.assertTrue(student_ready_pass(safe))
        self.assertFalse(student_ready_pass(leaky))
        self.assertFalse(student_ready_pass(weak))

    def test_effect_summary_reports_prompt_and_contract_deltas(self):
        rows = merge_review_and_key_rows(
            [
                _review_row("c1", "single_1", 3, 3),
                _review_row("c1", "prompt_1", 5, 1),
                _review_row("c1", "pred_1", 4, 2),
                _review_row("c1", "shuf_1", 2, 4, leakage="major_bridge_leakage"),
            ],
            [
                _key_row("single_1", "single_llm_structured"),
                _key_row("prompt_1", "enhanced_prompt_only"),
                _key_row("pred_1", "bridge_contract_predicted"),
                _key_row("shuf_1", "bridge_contract_shuffled"),
            ],
        )

        summary = build_effect_summary(rows)

        self.assertEqual(2.0, summary["prompt_effect"]["overall_quality_delta"])
        self.assertEqual(-1.0, summary["predicted_contract_vs_prompt"]["overall_quality_delta"])
        self.assertEqual(2.0, summary["predicted_contract_vs_shuffled"]["overall_quality_delta"])

    def test_write_analysis_outputs_creates_json_and_bilingual_reports(self):
        rows = merge_review_and_key_rows(
            [
                _review_row("c1", "single_1", 3, 2),
                _review_row("c1", "prompt_1", 5, 1),
            ],
            [
                _key_row("single_1", "single_llm_structured"),
                _key_row("prompt_1", "enhanced_prompt_only"),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_json = tmp / "summary.json"
            output_md_zh = tmp / "report.zh.md"
            output_md = tmp / "report.md"
            output_labels = tmp / "labels.jsonl"

            write_analysis_outputs(
                rows,
                output_json=output_json,
                output_md_zh=output_md_zh,
                output_md=output_md,
                output_labels_jsonl=output_labels,
            )

            self.assertTrue(output_json.exists())
            self.assertTrue(output_md_zh.exists())
            self.assertTrue(output_md.exists())
            self.assertTrue(output_labels.exists())
            self.assertIn("prompt_effect", output_json.read_text(encoding="utf-8"))
            self.assertIn("Prompt-Controlled Ablation", output_md.read_text(encoding="utf-8"))
            self.assertIn("Prompt-Controlled Ablation", output_md_zh.read_text(encoding="utf-8"))
            loaded = [json.loads(line) for line in output_labels.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(2, len(loaded))

    def test_build_system_summary_counts_rank_and_leakage(self):
        rows = merge_review_and_key_rows(
            [
                _review_row("c1", "resp_a", 5, 1),
                _review_row("c2", "resp_b", 2, 2, leakage="major_bridge_leakage", show="no"),
            ],
            [_key_row("resp_a", "system_a"), _key_row("resp_b", "system_a")],
        )

        summary = build_system_summary(rows, systems=["system_a"])

        self.assertEqual(2, summary["system_a"]["n"])
        self.assertEqual(1, summary["system_a"]["rank1_count"])
        self.assertEqual(1, summary["system_a"]["major_bridge_leakage_count"])
        self.assertEqual(1, summary["system_a"]["student_ready_pass_count"])


if __name__ == "__main__":
    unittest.main()
