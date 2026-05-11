import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat.analyze_fair_mini_study_paired import (
    build_system_summary,
    compute_paired_comparisons,
    load_label_rows,
    student_ready_pass,
    write_analysis_outputs,
)


def _row(case_id, system, overall, leakage="no_leakage", show="yes", score=2.0, rank="1"):
    return {
        "case_id": case_id,
        "system": system,
        "scores": {
            "bridge_identification": score,
            "groundedness": score,
            "scaffold_appropriateness": score,
            "bridge_leakage_control": score,
            "next_step_clarity": score,
            "single_focus_coherence": score,
            "bridge_oriented_micro_example": score,
        },
        "leakage_label": leakage,
        "overall_quality_score": overall,
        "would_show_to_student": show,
        "preference_rank": rank,
    }


class FairMiniStudyPairedAnalysisTests(unittest.TestCase):
    def test_student_ready_pass_requires_quality_show_safety_and_no_zero_core_score(self):
        self.assertTrue(student_ready_pass(_row("c1", "a", 4.0)))
        self.assertFalse(student_ready_pass(_row("c1", "a", 4.0, leakage="major_bridge_leakage")))
        self.assertFalse(student_ready_pass(_row("c1", "a", 4.0, show="borderline")))
        self.assertFalse(student_ready_pass(_row("c1", "a", 3.0)))
        self.assertFalse(student_ready_pass(_row("c1", "a", 4.0, score=0.0)))

    def test_compute_paired_comparisons_counts_case_level_wins(self):
        rows = [
            _row("c1", "system_a", 5.0),
            _row("c1", "system_b", 3.0),
            _row("c2", "system_a", 3.0),
            _row("c2", "system_b", 4.0),
        ]

        comparisons = compute_paired_comparisons(rows, systems=["system_a", "system_b"], bootstrap_rounds=50)

        key = "system_a__vs__system_b"
        self.assertEqual(1, comparisons[key]["wins"])
        self.assertEqual(1, comparisons[key]["losses"])
        self.assertEqual(0, comparisons[key]["ties"])
        self.assertEqual(0.5, comparisons[key]["mean_diff"])
        self.assertIn("bootstrap_ci95", comparisons[key])

    def test_build_system_summary_counts_student_ready_and_rank_one(self):
        rows = [
            _row("c1", "system_a", 5.0, rank="1"),
            _row("c2", "system_a", 2.0, leakage="major_bridge_leakage", show="no", rank="2"),
        ]

        summary = build_system_summary(rows, systems=["system_a"])

        self.assertEqual(2, summary["system_a"]["n"])
        self.assertEqual(1, summary["system_a"]["student_ready_pass_count"])
        self.assertEqual(1, summary["system_a"]["rank1_count"])

    def test_load_and_write_outputs(self):
        rows = [_row("c1", "system_a", 5.0), _row("c1", "system_b", 4.0)]
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "labels.jsonl"
            input_path.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                encoding="utf-8",
            )
            loaded = load_label_rows(input_path)
            output_json = Path(tmp) / "summary.json"
            output_md_zh = Path(tmp) / "report.zh.md"
            output_md = Path(tmp) / "report.md"

            write_analysis_outputs(
                loaded,
                output_json=output_json,
                output_md_zh=output_md_zh,
                output_md=output_md,
                systems=["system_a", "system_b"],
                bootstrap_rounds=50,
            )

            self.assertTrue(output_json.exists())
            self.assertTrue(output_md_zh.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
