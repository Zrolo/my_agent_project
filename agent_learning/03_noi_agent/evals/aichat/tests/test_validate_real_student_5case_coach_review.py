import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "evals/aichat/validate_real_student_5case_coach_review.py"
SCHEMA_PATH = REPO_ROOT / "docs/research/real_student_online_5case_coach_review_schema_v1.json"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("coach_review_validator", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class CoachReviewValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator_module()
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.fieldnames = list(self.schema["properties"].keys())
        self.base_row = {field: "" for field in self.fieldnames}
        self.base_row.update(
            {
                "dry_run_case_id": "dryrun_20260519_01",
                "candidate_turn_id": "rs_screen_20260519_001",
                "pilot_case_id": "rs_online_20260519_001",
                "selected_index_in_30": "1",
                "timestamp_bucket": "2026-W19",
                "problem_context_summary": "redacted summary",
                "student_message_redacted": "redacted student message",
                "recent_dialogue_redacted": "redacted dialogue",
                "student_code_excerpt_redacted": "",
                "ai_response_current_system_redacted": "redacted response",
                "ai_preannotation_missing_bridge_family": "debugging_bridge",
                "ai_preannotation_missing_bridge_instance_paraphrased": "student needs to distinguish the local bridge",
                "ai_preannotation_forbidden_content_paraphrased": "do not provide the full bridge",
                "ai_preannotation_acceptable_reveal_paraphrased": "ask a diagnostic question",
                "ai_preannotation_expected_next_student_action_paraphrased": "state the next reasoning step",
                "ai_preannotation_context_sufficiency_final": "sufficient",
                "ai_preannotation_matches_existing_taxonomy": "yes",
                "ai_preannotation_current_aichat_leakage_concern": "yes_high",
                "ai_preannotation_field_sufficiency_notes": "schema appears sufficient",
                "coach_review_status": "pending",
                "coach_privacy_review_status": "pending",
                "coach_context_sufficiency": "",
                "coach_current_aichat_leakage_concern": "",
                "coach_matches_existing_taxonomy": "",
                "coach_disagrees_with_ai_preannotation": "",
                "adjudication_needed": "",
                "consent_reporting_gate": "pending",
            }
        )

    def validate_rows(self, rows: list[dict[str, str]], expected_rows: int = 5):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "coach_review.csv"
            write_csv(csv_path, rows, self.fieldnames)
            header, loaded = self.validator.read_csv(csv_path)
        return self.validator.validate(loaded, header, self.schema, expected_rows)

    def test_pending_five_case_packet_is_valid_with_reporting_warnings(self):
        rows = []
        for index in range(5):
            row = dict(self.base_row)
            row["dry_run_case_id"] = f"dryrun_20260519_{index + 1:02d}"
            row["candidate_turn_id"] = f"rs_screen_20260519_{index + 1:03d}"
            row["pilot_case_id"] = f"rs_online_20260519_{index + 1:03d}"
            row["selected_index_in_30"] = str(index + 1)
            rows.append(row)

        result = self.validate_rows(rows)

        self.assertTrue(result["ok"])
        self.assertEqual(result["total_rows"], 5)
        self.assertEqual(result["reviewed_rows_count"], 0)
        self.assertEqual(result["reportable_after_consent_count"], 0)
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["warnings"])

    def test_reviewed_row_requires_core_coach_fields(self):
        row = dict(self.base_row)
        row["coach_review_status"] = "reviewed"
        rows = [dict(row, dry_run_case_id=f"dryrun_20260519_{i + 1:02d}", candidate_turn_id=f"rs_{i}") for i in range(5)]

        result = self.validate_rows(rows)

        self.assertFalse(result["ok"])
        self.assertTrue(
            any("reviewed row requires coach_context_sufficiency" in error for error in result["errors"])
        )
        self.assertTrue(
            any("reviewed row requires coach_current_aichat_leakage_concern" in error for error in result["errors"])
        )

    def test_duplicate_candidate_turn_id_is_error(self):
        rows = []
        for index in range(5):
            row = dict(self.base_row)
            row["dry_run_case_id"] = f"dryrun_20260519_{index + 1:02d}"
            row["candidate_turn_id"] = "rs_screen_duplicate"
            rows.append(row)

        result = self.validate_rows(rows)

        self.assertFalse(result["ok"])
        self.assertTrue(any("duplicate candidate_turn_id" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
