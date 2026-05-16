import csv
import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from evals.aichat import analyze_dev_ablation_review


class DevAblationReviewAnalysisTests(unittest.TestCase):
    def test_condition_id_from_key_distinguishes_same_tutor_by_pipeline(self):
        cases = [
            (
                {
                    "tutor_mode": "current_system",
                    "pipeline_mode": "tutor_only_no_diagnosis",
                },
                "current_system_deployment",
            ),
            (
                {
                    "tutor_mode": "bridge_contract",
                    "pipeline_mode": "deterministic_safe_scaffold",
                },
                "bridge_contract_safe_scaffold",
            ),
            (
                {
                    "tutor_mode": "bridge_contract",
                    "pipeline_mode": "tutor_plus_guard",
                },
                "bridge_contract_guard",
            ),
            (
                {
                    "tutor_mode": "dbox_inspired_decomposition_tutor",
                    "pipeline_mode": "tutor_only_no_diagnosis",
                },
                "dbox_inspired_clean",
            ),
            (
                {
                    "tutor_mode": "edf_inspired_adaptive_scaffolding_tutor",
                    "pipeline_mode": "tutor_only_no_diagnosis",
                },
                "edf_inspired_clean",
            ),
            (
                {
                    "tutor_mode": "edf_inspired_adaptive_scaffolding_tutor",
                    "pipeline_mode": "tutor_plus_guard",
                },
                "edf_inspired_guard",
            ),
            (
                {
                    "tutor_mode": "single_llm_structured",
                    "pipeline_mode": "tutor_plus_guard",
                },
                "single_llm_structured_guard",
            ),
            (
                {
                    "tutor_mode": "bridge_contract_compact",
                    "pipeline_mode": "tutor_plus_guard",
                },
                "bridge_contract_compact_guard",
            ),
            (
                {
                    "tutor_mode": "bridge_contract_minimal",
                    "pipeline_mode": "tutor_plus_guard",
                },
                "bridge_contract_minimal_guard",
            ),
            (
                {
                    "tutor_mode": "bridge_guided_dbox_style_tutor",
                    "pipeline_mode": "tutor_plus_guard",
                },
                "bridge_guided_dbox_style_guard",
            ),
            (
                {
                    "tutor_mode": "enhanced_prompt_only",
                    "pipeline_mode": "tutor_plus_guard",
                },
                "enhanced_prompt_only_guard",
            ),
            (
                {
                    "tutor_mode": "enhanced_prompt_only",
                    "pipeline_mode": "tutor_plus_guard_plus_repair",
                },
                "enhanced_prompt_only_guard_repair",
            ),
        ]

        for key_row, expected in cases:
            self.assertEqual(expected, analyze_dev_ablation_review.condition_id_from_key(key_row))

    def test_systems_for_set_supports_edf_core(self):
        self.assertEqual(
            [
                "enhanced_prompt_only_clean",
                "dbox_inspired_guard",
                "edf_inspired_clean",
                "edf_inspired_guard",
                "bridge_contract_guard",
                "bridge_contract_guard_repair",
            ],
            analyze_dev_ablation_review.systems_for_set("edf_core"),
        )

    def test_systems_for_set_supports_prompt_compression(self):
        self.assertEqual(
            [
                "dbox_inspired_guard",
                "bridge_contract_guard",
                "bridge_contract_compact_guard",
                "bridge_contract_minimal_guard",
            ],
            analyze_dev_ablation_review.systems_for_set("prompt_compression"),
        )

    def test_systems_for_set_supports_dbox_bridge_hybrid(self):
        self.assertEqual(
            [
                "enhanced_prompt_only_clean",
                "dbox_inspired_clean",
                "dbox_inspired_guard",
                "bridge_contract_compact_guard",
                "bridge_guided_dbox_style_guard",
            ],
            analyze_dev_ablation_review.systems_for_set("dbox_bridge_hybrid"),
        )

    def test_systems_for_set_supports_dbox_bridge_hybrid_full_fairness(self):
        self.assertEqual(
            [
                "enhanced_prompt_only_clean",
                "enhanced_prompt_only_guard",
                "enhanced_prompt_only_guard_repair",
                "dbox_inspired_clean",
                "dbox_inspired_guard",
                "dbox_inspired_guard_repair",
                "bridge_contract_compact_clean",
                "bridge_contract_compact_guard",
                "bridge_contract_compact_guard_repair",
                "bridge_guided_dbox_style_guard",
            ],
            analyze_dev_ablation_review.systems_for_set("dbox_bridge_hybrid_full_fairness"),
        )

    def test_merge_review_and_key_rows_reads_chinese_workbook_and_builds_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            review_xlsx = tmp / "review.xlsx"
            key_csv = tmp / "key.csv"

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "盲评表"
            sheet.append(["中文表头"] * len(analyze_dev_ablation_review.REVIEW_FIELD_NAMES))
            sheet.append(analyze_dev_ablation_review.REVIEW_FIELD_NAMES)
            base_review = {
                "case_id": "case_1",
                "problem_ref": "P1",
                "problem_source_platform": "luogu",
                "problem_source_id": "P1000",
                "problem_source_url": "https://www.luogu.com.cn/problem/P1000",
                "problem_statement": "原题题面",
                "problem_statement_public_summary": "公开摘要",
                "problem_statement_rights_note": "公开材料仅保留链接和改写摘要。",
                "problem_statement_access_level": "public_summary_only",
                "student_message": "学生问题",
                "student_message_length_bucket": "short",
                "problem_context": "题目上下文",
                "success_criteria": "学生能继续推进。",
                "forbidden_content": "不能补完关键桥。",
                "critical_bridge_boundary": "不能直接说出当前关键关系。",
                "acceptable_reveal": "可以给局部观察方向。",
                "expected_student_next_action": "学生回答一个局部判断。",
                "coach_micro_example_applicability": "applicable",
                "coach_reviewer_confidence": "high",
                "coach_needs_discussion": "no",
                "review_status": "labeled",
            }

            row_a = {
                **base_review,
                "anonymized_response_id": "resp_a",
                "response_text": "回复 A",
                "coach_bridge_identification_score": 2,
                "coach_groundedness_score": 2,
                "coach_scaffold_appropriateness_score": 2,
                "coach_next_step_clarity_score": 2,
                "coach_single_focus_coherence_score": 2,
                "coach_bridge_oriented_micro_example_score": 1,
                "coach_bridge_leakage_control_score": 2,
                "coach_overall_quality_score": 5,
                "coach_would_show_to_student": "yes",
                "coach_leakage_label": "no_leakage",
                "coach_bridge_reveal_justification": "no_reveal",
                "coach_scaffold_sufficiency_score": 2,
                "coach_student_response_burden": "low",
                "coach_preference_rank": 1,
            }
            row_b = {
                **base_review,
                "anonymized_response_id": "resp_b",
                "response_text": "回复 B",
                "coach_bridge_identification_score": 1,
                "coach_groundedness_score": 2,
                "coach_scaffold_appropriateness_score": 1,
                "coach_next_step_clarity_score": 2,
                "coach_single_focus_coherence_score": 2,
                "coach_bridge_oriented_micro_example_score": 0,
                "coach_bridge_leakage_control_score": 1,
                "coach_overall_quality_score": 3,
                "coach_would_show_to_student": "borderline",
                "coach_leakage_label": "minor_bridge_leakage",
                "coach_bridge_reveal_justification": "borderline",
                "coach_scaffold_sufficiency_score": 0,
                "coach_student_response_burden": "high",
                "coach_preference_rank": 2,
                "coach_reviewer_confidence": "medium",
                "coach_needs_discussion": "yes",
                "coach_notes": "偏强",
            }
            for row in (row_a, row_b):
                sheet.append(
                    [row.get(field, "") for field in analyze_dev_ablation_review.REVIEW_FIELD_NAMES]
                )
            workbook.save(review_xlsx)

            with key_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "anonymized_response_id",
                        "case_id",
                        "tutor_mode",
                        "guard_mode",
                        "pipeline_mode",
                        "tutor_model_provider",
                        "chat_thinking_mode",
                        "final_response_source",
                        "repair_applied",
                        "blocked",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "anonymized_response_id": "resp_a",
                        "case_id": "case_1",
                        "tutor_mode": "bridge_contract",
                        "guard_mode": "predicted",
                        "pipeline_mode": "deterministic_safe_scaffold",
                        "final_response_source": "safe_fallback",
                        "repair_applied": "false",
                        "blocked": "false",
                    }
                )
                writer.writerow(
                    {
                        "anonymized_response_id": "resp_b",
                        "case_id": "case_1",
                        "tutor_mode": "bridge_contract",
                        "guard_mode": "predicted",
                        "pipeline_mode": "tutor_only",
                        "final_response_source": "candidate",
                        "repair_applied": "false",
                        "blocked": "false",
                    }
                )

            rows = analyze_dev_ablation_review.merge_review_and_key_rows(
                analyze_dev_ablation_review.load_review_workbook_rows(review_xlsx),
                analyze_dev_ablation_review.load_key_rows(key_csv),
            )
            payload = analyze_dev_ablation_review.build_payload(rows, systems=[
                "bridge_contract_safe_scaffold",
                "bridge_contract_clean",
            ])

        self.assertEqual(2, payload["row_count"])
        self.assertEqual(1, payload["case_count"])
        self.assertIn("bridge_reveal_justification_counts", payload)
        self.assertEqual({"high": 1, "low": 1}, payload["student_response_burden_counts"])
        self.assertEqual(
            2.0,
            payload["system_summary"]["bridge_contract_safe_scaffold"]["scaffold_sufficiency_mean"],
        )
        self.assertEqual(
            1,
            payload["system_summary"]["bridge_contract_safe_scaffold"]["student_ready_pass_count"],
        )
        comparison = payload["paired_comparisons"]["bridge_contract_safe_scaffold__vs__bridge_contract_clean"]
        self.assertEqual(1, comparison["wins"])
        self.assertEqual(0, comparison["losses"])
        self.assertEqual(2.0, comparison["mean_diff"])

    def test_merge_review_rows_preserves_bridge_reveal_justification_and_summarizes_it(self):
        review_rows = [
            {
                "case_id": "case_1",
                "anonymized_response_id": "resp_a",
                "coach_bridge_identification_score": 2,
                "coach_groundedness_score": 2,
                "coach_scaffold_appropriateness_score": 1,
                "coach_scaffold_sufficiency_score": 1,
                "coach_bridge_leakage_control_score": 1,
                "coach_next_step_clarity_score": 2,
                "coach_single_focus_coherence_score": 2,
                "coach_bridge_oriented_micro_example_score": 1,
                "coach_micro_example_applicability": "applicable",
                "coach_leakage_label": "minor_bridge_leakage",
                "coach_bridge_reveal_justification": "pedagogically_justified",
                "coach_preference_rank": 1,
                "coach_overall_quality_score": 4,
                "coach_would_show_to_student": "yes",
                "coach_student_response_burden": "low",
                "coach_reviewer_confidence": "medium",
                "coach_needs_discussion": "no",
                "coach_notes": "学生已经说出一部分关键桥，强提示有教学理由。",
                "review_status": "labeled",
            },
            {
                "case_id": "case_2",
                "anonymized_response_id": "resp_b",
                "coach_bridge_identification_score": 2,
                "coach_groundedness_score": 2,
                "coach_scaffold_appropriateness_score": 0,
                "coach_scaffold_sufficiency_score": 0,
                "coach_bridge_leakage_control_score": 0,
                "coach_next_step_clarity_score": 2,
                "coach_single_focus_coherence_score": 2,
                "coach_bridge_oriented_micro_example_score": 0,
                "coach_micro_example_applicability": "applicable",
                "coach_leakage_label": "major_bridge_leakage",
                "coach_bridge_reveal_justification": "unjustified",
                "coach_preference_rank": 2,
                "coach_overall_quality_score": 2,
                "coach_would_show_to_student": "no",
                "coach_student_response_burden": "high",
                "coach_reviewer_confidence": "high",
                "coach_needs_discussion": "yes",
                "coach_notes": "直接补完当前 missing bridge。",
                "review_status": "labeled",
            },
        ]
        key_rows = [
            {
                "anonymized_response_id": "resp_a",
                "case_id": "case_1",
                "tutor_mode": "bridge_contract",
                "guard_mode": "predicted",
                "pipeline_mode": "tutor_plus_guard",
                "final_response_source": "candidate",
                "repair_applied": "false",
                "blocked": "false",
            },
            {
                "anonymized_response_id": "resp_b",
                "case_id": "case_2",
                "tutor_mode": "bridge_contract",
                "guard_mode": "predicted",
                "pipeline_mode": "tutor_plus_guard",
                "final_response_source": "candidate",
                "repair_applied": "false",
                "blocked": "false",
            },
        ]

        rows = analyze_dev_ablation_review.merge_review_and_key_rows(review_rows, key_rows)
        payload = analyze_dev_ablation_review.build_payload(rows, systems=["bridge_contract_guard"])

        self.assertEqual("pedagogically_justified", rows[0]["bridge_reveal_justification"])
        self.assertEqual(1.0, rows[0]["scores"]["scaffold_sufficiency"])
        self.assertEqual("low", rows[0]["student_response_burden"])
        self.assertEqual(
            {"pedagogically_justified": 1, "unjustified": 1},
            payload["bridge_reveal_justification_counts"],
        )
        self.assertEqual(
            1,
            payload["system_summary"]["bridge_contract_guard"]["unjustified_reveal_count"],
        )
        self.assertEqual(
            1,
            payload["system_summary"]["bridge_contract_guard"]["pedagogically_justified_reveal_count"],
        )
        self.assertIn("rubric_eval_score_v1_mean", payload["system_summary"]["bridge_contract_guard"])

    def test_rubric_eval_score_penalizes_leakage_and_high_burden(self):
        good_row = {
            "overall_quality_score": 5,
            "would_show_to_student": "yes",
            "leakage_label": "no_leakage",
            "student_response_burden": "low",
            "scores": {
                "bridge_identification": 2,
                "groundedness": 2,
                "scaffold_appropriateness": 2,
                "scaffold_sufficiency": 2,
                "bridge_leakage_control": 2,
                "next_step_clarity": 2,
                "single_focus_coherence": 2,
            },
        }
        leaking_row = {
            **good_row,
            "leakage_label": "major_bridge_leakage",
            "would_show_to_student": "no",
            "student_response_burden": "high",
        }
        insufficient_row = {
            **good_row,
            "scores": {
                **good_row["scores"],
                "scaffold_sufficiency": 0,
            },
        }

        self.assertGreater(
            analyze_dev_ablation_review.rubric_eval_score_v1(good_row),
            analyze_dev_ablation_review.rubric_eval_score_v1(leaking_row),
        )
        self.assertGreater(
            analyze_dev_ablation_review.rubric_eval_score_v1(good_row),
            analyze_dev_ablation_review.rubric_eval_score_v1(insufficient_row),
        )

    def test_micro_example_not_applicable_does_not_lower_micro7(self):
        row = {
            "scores": {
                "bridge_identification": 2,
                "groundedness": 2,
                "scaffold_appropriateness": 2,
                "scaffold_sufficiency": 2,
                "bridge_leakage_control": 2,
                "next_step_clarity": 2,
                "single_focus_coherence": 2,
                "bridge_oriented_micro_example": None,
            },
            "micro_example_applicability": "not_applicable",
        }

        self.assertEqual(2.0, analyze_dev_ablation_review._row_with_micro_score(row))

    def test_render_report_titles_use_actual_scope_counts(self):
        payload = {
            "case_count": 50,
            "row_count": 400,
            "systems": [
                "current_system_deployment",
                "enhanced_prompt_only_clean",
                "dbox_inspired_guard",
            ],
            "system_summary": {
                "current_system_deployment": {
                    "student_ready_pass_count": 20,
                    "overall_quality_mean": 3.0,
                    "major_or_answer_leakage_count": 5,
                    "n": 50,
                    "core6_mean": 1.5,
                    "scaffold_sufficiency_mean": 1.5,
                    "with_micro7_mean": 1.4,
                    "rank1_count": 0,
                    "student_ready_safe_pass_count": 20,
                    "would_show_yes_count": 20,
                    "would_show_borderline_count": 20,
                    "would_show_no_count": 10,
                    "no_leakage_count": 45,
                    "minor_bridge_leakage_count": 0,
                    "borderline_reveal_count": 0,
                    "pedagogically_justified_reveal_count": 0,
                    "unjustified_reveal_count": 5,
                    "student_response_burden_low_count": 50,
                    "student_response_burden_medium_count": 0,
                    "student_response_burden_high_count": 0,
                },
                "enhanced_prompt_only_clean": {
                    "student_ready_pass_count": 30,
                    "overall_quality_mean": 3.5,
                    "major_or_answer_leakage_count": 2,
                    "n": 50,
                    "core6_mean": 1.8,
                    "scaffold_sufficiency_mean": 1.8,
                    "with_micro7_mean": 1.7,
                    "rank1_count": 0,
                    "student_ready_safe_pass_count": 30,
                    "would_show_yes_count": 30,
                    "would_show_borderline_count": 20,
                    "would_show_no_count": 0,
                    "no_leakage_count": 48,
                    "minor_bridge_leakage_count": 0,
                    "borderline_reveal_count": 0,
                    "pedagogically_justified_reveal_count": 0,
                    "unjustified_reveal_count": 2,
                    "student_response_burden_low_count": 50,
                    "student_response_burden_medium_count": 0,
                    "student_response_burden_high_count": 0,
                },
                "dbox_inspired_guard": {
                    "student_ready_pass_count": 35,
                    "overall_quality_mean": 3.7,
                    "major_or_answer_leakage_count": 1,
                    "n": 50,
                    "core6_mean": 1.9,
                    "scaffold_sufficiency_mean": 1.9,
                    "with_micro7_mean": 1.8,
                    "rank1_count": 0,
                    "student_ready_safe_pass_count": 35,
                    "would_show_yes_count": 35,
                    "would_show_borderline_count": 15,
                    "would_show_no_count": 0,
                    "no_leakage_count": 49,
                    "minor_bridge_leakage_count": 0,
                    "borderline_reveal_count": 0,
                    "pedagogically_justified_reveal_count": 0,
                    "unjustified_reveal_count": 1,
                    "student_response_burden_low_count": 50,
                    "student_response_burden_medium_count": 0,
                    "student_response_burden_high_count": 0,
                },
            },
            "paired_comparisons": {},
            "paired_comparisons_core6": {},
            "paired_comparisons_micro7": {},
            "overall_leakage_counts": {"no_leakage": 97, "answer_leakage": 3},
            "bridge_reveal_justification_counts": {"no_reveal": 97, "unjustified": 3},
            "student_response_burden_counts": {"low": 100},
            "overall_show_counts": {"yes": 65, "borderline": 35},
        }

        rows = [{"review_status": "ai_prelim_reviewed｜AI 预评，待教练复核"}]
        zh = analyze_dev_ablation_review.render_report_zh(
            payload,
            rows,
            review_xlsx=Path("review.xlsx"),
            key_csv=Path("key.csv"),
        )
        en = analyze_dev_ablation_review.render_report_en(
            payload,
            rows,
            review_xlsx=Path("review.xlsx"),
            key_csv=Path("key.csv"),
        )

        self.assertIn("# Dev Ablation 50-case AI Preliminary Review Analysis", en)
        self.assertIn("50 development cases, 3 anonymous system conditions, and 400 AI-prelim-reviewed responses", en)
        self.assertIn("# Dev Ablation 50-case AI 初评分析", zh)
        self.assertIn("50 个 dev cases、3 个匿名系统条件、400 条 AI 预评回复", zh)


if __name__ == "__main__":
    unittest.main()
