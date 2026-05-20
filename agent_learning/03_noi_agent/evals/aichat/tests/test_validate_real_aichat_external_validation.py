import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def load_module(relative_path: str, module_name: str):
    script_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class RealAIChat100ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_module(
            "evals/aichat/validate_real_aichat_100_observational_validation.py",
            "real_aichat_100_validator",
        )
        self.schema = json.loads(
            (REPO_ROOT / "docs/research/real_aichat_100_observational_validation_schema_v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.fieldnames = list(self.schema["properties"].keys())
        self.base_row = {field: "" for field in self.fieldnames}
        self.base_row.update(
            {
                "real_aichat_case_id": "real_aichat_001",
                "source_candidate_turn_id": "rs_screen_20260519_001",
                "student_id_hash_private_or_redacted": "redacted_student_001",
                "problem_id_hash_private_or_redacted": "redacted_problem_001",
                "session_id_hash_private_or_redacted": "redacted_session_001",
                "cp_tutoring_relevance": "yes",
                "substantial_turn": "yes",
                "context_sufficiency_light": "sufficient",
                "rough_bridge_family": "debugging_bridge",
                "surface_anchor": "debugging trace",
                "help_seeking_type": "debugging",
                "missing_bridge_identifiable": "yes",
                "observed_current_aichat_response_available": "yes",
                "observed_current_aichat_response_role": "observed_only_not_condition",
                "possible_bridge_leakage_concern": "unclear",
                "candidate_for_replay": "yes",
                "candidate_for_trajectory_subset": "no",
                "privacy_review_status": "passed",
                "consent_reporting_gate": "eligible",
                "public_reporting_allowed": "yes",
                "selection_reason": "coverage of debugging bridge and sufficient context",
                "exclusion_reason": "",
                "annotator_id": "ann_001",
                "annotation_date": "2026-05-20",
                "notes_no_raw_text": "No raw student text.",
            }
        )

    def validate_rows(self, rows: list[dict[str, str]]):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "real_aichat_100.csv"
            write_csv(csv_path, rows, self.fieldnames)
            header, loaded = self.validator.read_csv(csv_path)
        return self.validator.validate(loaded, header, self.schema)

    def test_valid_observational_row_passes(self):
        result = self.validate_rows([self.base_row])
        self.assertTrue(result["ok"])
        self.assertEqual(result["total_rows"], 1)

    def test_observed_response_role_must_be_observed_only(self):
        row = dict(self.base_row)
        row["observed_current_aichat_response_role"] = "baseline_condition"
        result = self.validate_rows([row])
        self.assertFalse(result["ok"])
        self.assertTrue(any("observed_current_aichat_response_role" in error for error in result["errors"]))

    def test_public_reporting_requires_consent_gate(self):
        row = dict(self.base_row)
        row["consent_reporting_gate"] = "pending"
        result = self.validate_rows([row])
        self.assertFalse(result["ok"])
        self.assertTrue(any("public_reporting_allowed=yes" in error for error in result["errors"]))

    def test_replay_candidate_requires_context(self):
        row = dict(self.base_row)
        row["context_sufficiency_light"] = "insufficient"
        result = self.validate_rows([row])
        self.assertFalse(result["ok"])
        self.assertTrue(any("candidate_for_replay=yes" in error for error in result["errors"]))


class RealAIChatReplayCaseValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_module(
            "evals/aichat/validate_real_aichat_replay_30_50_cases.py",
            "real_aichat_replay_case_validator",
        )
        self.schema = json.loads(
            (REPO_ROOT / "docs/research/real_aichat_replay_30_50_case_schema_v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.fieldnames = list(self.schema["properties"].keys())
        self.base_row = {field: "" for field in self.fieldnames}
        self.base_row.update(
            {
                "replay_case_id": "replay_case_001",
                "source_real_aichat_case_id": "real_aichat_001",
                "replay_subset": "replay30",
                "problem_summary": "Redacted task summary.",
                "constraints_io_summary": "Redacted constraint and I/O summary.",
                "recent_dialogue_summary": "Redacted recent dialogue summary.",
                "current_student_state_summary": "Student has not located the debugging bridge.",
                "missing_bridge_candidate": "debugging evidence selection",
                "forbidden_bridge_content": "Do not give the exact failing step.",
                "acceptable_hint_boundary": "Ask for one minimal trace check.",
                "expected_next_student_action": "Student identifies which variable to inspect.",
                "context_sufficiency": "sufficient",
                "privacy_review_status": "passed",
                "consent_reporting_gate": "pending",
                "public_reporting_allowed": "no",
                "selection_reason": "context-sufficient replay candidate",
                "exclusion_reason": "",
                "notes_no_raw_text": "Internal only until consent gate.",
            }
        )

    def validate_rows(self, rows: list[dict[str, str]]):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "replay_cases.csv"
            write_csv(csv_path, rows, self.fieldnames)
            header, loaded = self.validator.read_csv(csv_path)
        return self.validator.validate(loaded, header, self.schema)

    def test_valid_replay_case_passes(self):
        result = self.validate_rows([self.base_row])
        self.assertTrue(result["ok"])

    def test_public_reporting_requires_consent(self):
        row = dict(self.base_row)
        row["public_reporting_allowed"] = "yes"
        result = self.validate_rows([row])
        self.assertFalse(result["ok"])
        self.assertTrue(any("public_reporting_allowed=yes" in error for error in result["errors"]))


class RealAIChatReplayReviewValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_module(
            "evals/aichat/validate_real_aichat_replay_30_50_reviews.py",
            "real_aichat_replay_review_validator",
        )
        self.schema = json.loads(
            (REPO_ROOT / "docs/research/real_aichat_replay_30_50_coach_review_schema_v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.fieldnames = list(self.schema["properties"].keys())
        self.base_row = {field: "" for field in self.fieldnames}
        self.base_row.update(
            {
                "replay_case_id": "replay_case_001",
                "anonymized_response_id": "resp_001",
                "condition_hidden_from_reviewer": "yes",
                "condition_name_private_or_redacted": "redacted_condition_a",
                "response_role": "offline_harness_response",
                "harness_name_private_or_redacted": "enhanced_prompt_only_clean",
                "bridge_leakage_severity": "none",
                "answer_or_code_leakage": "none",
                "helpfulness": "medium",
                "learner_burden": "medium",
                "scaffold_quality": "medium",
                "student_ready": "yes",
                "safe_ready": "yes",
                "context_sufficiency_for_judgment": "sufficient",
                "coach_confidence": "medium",
                "reviewer_id": "coach_001",
                "review_date": "2026-05-20",
                "notes_no_raw_text": "No raw text.",
            }
        )

    def validate_rows(self, rows: list[dict[str, str]]):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "replay_reviews.csv"
            write_csv(csv_path, rows, self.fieldnames)
            header, loaded = self.validator.read_csv(csv_path)
        return self.validator.validate(loaded, header, self.schema)

    def test_valid_replay_review_passes(self):
        result = self.validate_rows([self.base_row])
        self.assertTrue(result["ok"])

    def test_offline_harness_count_cannot_exceed_seven_per_case(self):
        rows = []
        for index in range(8):
            row = dict(self.base_row)
            row["anonymized_response_id"] = f"resp_{index:03d}"
            row["harness_name_private_or_redacted"] = f"harness_{index}"
            rows.append(row)
        result = self.validate_rows(rows)
        self.assertFalse(result["ok"])
        self.assertTrue(any("more than 7 offline harness responses" in error for error in result["errors"]))

    def test_observed_reference_is_not_counted_as_offline_harness(self):
        rows = []
        for index in range(7):
            row = dict(self.base_row)
            row["anonymized_response_id"] = f"resp_{index:03d}"
            row["harness_name_private_or_redacted"] = f"harness_{index}"
            rows.append(row)
        observed = dict(self.base_row)
        observed["anonymized_response_id"] = "observed_ref"
        observed["response_role"] = "observed_reference"
        observed["harness_name_private_or_redacted"] = "observed_current_aichat_response"
        rows.append(observed)
        result = self.validate_rows(rows)
        self.assertTrue(result["ok"])

    def test_hidden_condition_required_for_offline_response(self):
        row = dict(self.base_row)
        row["condition_hidden_from_reviewer"] = "no"
        result = self.validate_rows([row])
        self.assertFalse(result["ok"])
        self.assertTrue(any("condition_hidden_from_reviewer" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
