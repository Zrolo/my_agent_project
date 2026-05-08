import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import summarize_bridge_offline_eval


def _result_row(
    *,
    case_id: str,
    gold_family: str,
    pred_family: str,
    gold_focus: str = "state_design",
    pred_focus: str = "state_design",
    leakage_level: int = 0,
    safe_action: str = "pass",
    repaired: bool = False,
    confidence: float = 0.8,
):
    row = {
        "case_id": case_id,
        "gold": {
            "student_state": "strategy_application_gap",
            "bridge_family": gold_family,
            "known_focus": gold_focus,
            "help_seeking_type": "instrumental_help",
            "allowed_help_level": "L2",
        },
        "bridge_judge_result": {
            "problem_solving_state": "strategy_application_gap",
            "missing_bridge": {
                "family": pred_family,
                "known_focus": pred_focus,
            },
            "help_seeking_type": "instrumental_help",
            "allowed_help_level": "L2",
            "confidence": confidence,
        },
        "tutor_response": {
            "baseline_group": "current_system",
            "response_text": "回复",
            "level": "L2",
        },
        "leakage_judge_result": {
            "leakage_level": leakage_level,
            "leakage_types": ["critical_bridge"] if leakage_level >= 3 else [],
            "is_critical_bridge_leakage": leakage_level >= 3,
            "is_answer_or_code_leakage": False,
            "safe_action": safe_action,
        },
    }
    if repaired:
        row["repair_result"] = {
            "repaired_response": "修复后回复",
            "still_needs_leakage_check": True,
        }
    return row


class BridgeOfflineEvalSummaryTests(unittest.TestCase):
    def test_summarize_bridge_offline_results_counts_accuracy_and_leakage_rates(self):
        rows = [
            _result_row(
                case_id="case_1",
                gold_family="representation_bridge",
                pred_family="representation_bridge",
                leakage_level=3,
                safe_action="rewrite",
                repaired=True,
                confidence=0.9,
            ),
            _result_row(
                case_id="case_2",
                gold_family="predicate_bridge",
                pred_family="transition_bridge",
                gold_focus="check_condition",
                pred_focus="transition_design",
                confidence=0.7,
            ),
            {
                "case_id": "case_3",
                "gold": {"bridge_family": "aggregation_bridge"},
                "error": "bridge_judge_failed",
            },
        ]

        summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(rows)

        self.assertEqual(3, summary["case_count"])
        self.assertEqual(2, summary["completed_count"])
        self.assertEqual(1, summary["error_count"])
        self.assertEqual(0.5, summary["bridge_family_accuracy"])
        self.assertEqual(0.5, summary["known_focus_accuracy"])
        self.assertEqual(1.0, summary["student_state_accuracy"])
        self.assertEqual(0.5, summary["leakage_rate"])
        self.assertEqual(0.5, summary["critical_bridge_leakage_rate"])
        self.assertEqual(0.5, summary["rewrite_rate"])
        self.assertEqual(0.5, summary["repair_rate"])
        self.assertEqual(0.8, summary["avg_bridge_judge_confidence"])

    def test_render_markdown_report_includes_core_metrics(self):
        summary = {
            "case_count": 3,
            "completed_count": 2,
            "error_count": 1,
            "bridge_family_accuracy": 0.5,
            "known_focus_accuracy": 0.5,
            "student_state_accuracy": 1.0,
            "help_seeking_type_accuracy": 1.0,
            "allowed_help_level_accuracy": 1.0,
            "leakage_rate": 0.5,
            "critical_bridge_leakage_rate": 0.5,
            "answer_or_code_leakage_rate": 0.0,
            "rewrite_rate": 0.5,
            "block_rate": 0.0,
            "repair_rate": 0.5,
            "avg_bridge_judge_confidence": 0.8,
            "safe_action_counts": {"pass": 1, "rewrite": 1},
            "leakage_level_counts": {"0": 1, "3": 1},
            "error_cases": ["case_3"],
        }

        report = summarize_bridge_offline_eval.render_markdown_report(summary)

        self.assertIn("# Bridge Offline Eval Summary", report)
        self.assertIn("| Bridge Family Accuracy | 0.500 |", report)
        self.assertIn("| Critical Bridge Leakage Rate | 0.500 |", report)
        self.assertIn("case_3", report)

    def test_load_and_write_summary_files(self):
        rows = [
            _result_row(
                case_id="case_1",
                gold_family="representation_bridge",
                pred_family="representation_bridge",
            )
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "results.jsonl"
            json_path = Path(tmpdir) / "summary.json"
            md_path = Path(tmpdir) / "summary.md"
            input_path.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                encoding="utf-8",
            )

            loaded = summarize_bridge_offline_eval.load_result_rows(input_path)
            summary = summarize_bridge_offline_eval.summarize_bridge_offline_results(loaded)
            summarize_bridge_offline_eval.write_summary_files(json_path, md_path, summary)

            self.assertEqual(rows, loaded)
            self.assertEqual(1.0, json.loads(json_path.read_text(encoding="utf-8"))["bridge_family_accuracy"])
            self.assertIn("Bridge Offline Eval Summary", md_path.read_text(encoding="utf-8"))

    def test_main_writes_summary_and_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "results.jsonl"
            json_path = Path(tmpdir) / "summary.json"
            md_path = Path(tmpdir) / "summary.md"
            input_path.write_text(
                json.dumps(
                    _result_row(
                        case_id="case_1",
                        gold_family="representation_bridge",
                        pred_family="representation_bridge",
                    ),
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = summarize_bridge_offline_eval.main(
                    [
                        "--input-jsonl",
                        str(input_path),
                        "--output-json",
                        str(json_path),
                        "--output-md",
                        str(md_path),
                    ]
                )

            self.assertEqual(0, exit_code)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertIn('"case_count": 1', stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
