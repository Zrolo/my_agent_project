import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "evals/aichat/summarize_real_student_5case_coach_review.py"
SCHEMA_PATH = REPO_ROOT / "docs/research/real_student_online_5case_coach_review_schema_v1.json"


def load_summary_module():
    spec = importlib.util.spec_from_file_location("coach_review_summary", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class CoachReviewSummaryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.summary_module = load_summary_module()
        schema = self.summary_module.read_schema(SCHEMA_PATH)
        self.fieldnames = list(schema["properties"].keys())
        self.base_row = {field: "" for field in self.fieldnames}
        self.base_row.update(
            {
                "dry_run_case_id": "dryrun_20260519_01",
                "candidate_turn_id": "rs_screen_20260519_001",
                "pilot_case_id": "rs_online_20260519_001",
                "selected_index_in_30": "1",
                "timestamp_bucket": "2026-W19",
                "problem_context_summary": "SENTINEL_CONTEXT",
                "student_message_redacted": "SENTINEL_STUDENT",
                "recent_dialogue_redacted": "SENTINEL_DIALOGUE",
                "student_code_excerpt_redacted": "SENTINEL_CODE",
                "ai_response_current_system_redacted": "SENTINEL_RESPONSE",
                "ai_preannotation_missing_bridge_family": "debugging_bridge",
                "ai_preannotation_missing_bridge_instance_paraphrased": "preannotation should not appear",
                "ai_preannotation_forbidden_content_paraphrased": "forbidden content should not appear",
                "ai_preannotation_acceptable_reveal_paraphrased": "acceptable reveal should not appear",
                "ai_preannotation_expected_next_student_action_paraphrased": "expected action should not appear",
                "ai_preannotation_context_sufficiency_final": "sufficient",
                "ai_preannotation_matches_existing_taxonomy": "yes",
                "ai_preannotation_current_aichat_leakage_concern": "yes_high",
                "ai_preannotation_field_sufficiency_notes": "field note should not appear",
                "coach_review_status": "reviewed",
                "coach_privacy_review_status": "passed_for_internal_review",
                "coach_context_sufficiency": "sufficient",
                "coach_missing_bridge_family": "debugging_bridge",
                "coach_missing_bridge_instance": "SENTINEL_BRIDGE",
                "coach_forbidden_content": "SENTINEL_FORBIDDEN",
                "coach_acceptable_reveal": "SENTINEL_REVEAL",
                "coach_expected_next_student_action": "SENTINEL_ACTION",
                "coach_current_aichat_leakage_concern": "yes_high",
                "coach_matches_existing_taxonomy": "yes",
                "coach_observed_next_turn_progress": "unavailable",
                "coach_disagrees_with_ai_preannotation": "no",
                "adjudication_needed": "no",
                "consent_reporting_gate": "pending",
            }
        )

    def summarize_rows(self, rows: list[dict[str, str]]):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "coach_review.csv"
            write_csv(path, rows, self.fieldnames)
            loaded = self.summary_module.read_csv(path)
        return self.summary_module.summarize(loaded)

    def test_pending_consent_suppresses_leakage_counts_and_private_text(self):
        rows = []
        for index in range(5):
            row = dict(self.base_row)
            row["dry_run_case_id"] = f"dryrun_20260519_{index + 1:02d}"
            row["candidate_turn_id"] = f"rs_screen_20260519_{index + 1:03d}"
            row["pilot_case_id"] = f"rs_online_20260519_{index + 1:03d}"
            row["selected_index_in_30"] = str(index + 1)
            rows.append(row)

        summary = self.summarize_rows(rows)
        markdown = self.summary_module.render_markdown(summary)

        self.assertEqual(summary["total_rows"], 5)
        self.assertEqual(summary["reviewed_rows_count"], 5)
        self.assertEqual(summary["reportable_after_consent_count"], 0)
        self.assertTrue(summary["leakage_counts_suppressed"])
        self.assertNotIn("coach_current_aichat_leakage_concern_counts", summary)
        self.assertNotIn("rs_screen_20260519_001", markdown)
        self.assertNotIn("SENTINEL_STUDENT", markdown)
        self.assertNotIn("SENTINEL_RESPONSE", markdown)
        self.assertNotIn("yes_high", markdown)

    def test_all_reportable_reviewed_rows_can_include_aggregate_leakage_counts(self):
        rows = []
        for index in range(5):
            row = dict(self.base_row)
            row["dry_run_case_id"] = f"dryrun_20260519_{index + 1:02d}"
            row["candidate_turn_id"] = f"rs_screen_20260519_{index + 1:03d}"
            row["pilot_case_id"] = f"rs_online_20260519_{index + 1:03d}"
            row["selected_index_in_30"] = str(index + 1)
            row["consent_reporting_gate"] = "eligible"
            row["coach_current_aichat_leakage_concern"] = "no" if index % 2 else "yes_high"
            rows.append(row)

        summary = self.summarize_rows(rows)

        self.assertFalse(summary["leakage_counts_suppressed"])
        self.assertEqual(
            summary["coach_current_aichat_leakage_concern_counts"],
            {"yes_high": 3, "no": 2},
        )


if __name__ == "__main__":
    unittest.main()
