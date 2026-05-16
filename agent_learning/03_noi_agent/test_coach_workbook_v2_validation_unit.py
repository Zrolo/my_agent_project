import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from evals.aichat import validate_coach_workbook_v2 as validator_v2
from evals.aichat.coach_labeling_schema_v2 import option_label


class CoachWorkbookV2ValidationTests(unittest.TestCase):
    def test_validate_rows_accepts_chinese_labels_and_multivalue_fields(self):
        rows = [
            {
                "case_id": "case_1",
                "turn_type": option_label("diagnosable_learning_turn"),
                "diagnosis_uncertainty": option_label("low"),
                "student_problem_solving_state": option_label("modeling_representation_gap"),
                "student_attempt_level": option_label("partial_attempt"),
                "student_already_stated_bridge": option_label("partial_hypothesis"),
                "policy_risk_type": option_label("none"),
                "primary_bridge_family": option_label("representation_state_bridge"),
                "secondary_bridge_family": "",
                "primary_bridge_subtype_id": option_label("state.table_or_memo_cell_semantics"),
                "secondary_bridge_subtype_id": "",
                "registered_focus_id": "state_design",
                "secondary_registered_focus_id": "unknown",
                "focus_match_status": option_label("matched_existing"),
                "help_seeking_type": f"{option_label('strategy_hint_request')};{option_label('step_validation')}",
                "max_scaffold_level": option_label("L2"),
                "help_forms": f"{option_label('guiding_question')};{option_label('micro_example')}",
                "leakage_risk": option_label("medium"),
                "coach_confidence": "4",
                "review_status": option_label("labeled"),
                "evidence_quote": "学生说：不知道 dp 数组每一格到底应该表示什么。",
                "recent_dialogue": "N/A",
                "student_code_excerpt": "N/A",
            }
        ]

        errors = validator_v2.validate_rows(rows, focus_ids={"state_design"})

        self.assertEqual([], errors)

    def test_validate_rows_reports_invalid_placeholder_and_focus(self):
        rows = [
            {
                "case_id": "case_bad",
                "turn_type": option_label("diagnosable_learning_turn"),
                "diagnosis_uncertainty": option_label("low"),
                "student_problem_solving_state": option_label("modeling_representation_gap"),
                "student_attempt_level": option_label("partial_attempt"),
                "student_already_stated_bridge": option_label("not_stated"),
                "policy_risk_type": option_label("none"),
                "primary_bridge_family": option_label("representation_state_bridge"),
                "primary_bridge_subtype_id": option_label("state.table_or_memo_cell_semantics"),
                "registered_focus_id": "made_up_focus",
                "focus_match_status": option_label("matched_existing"),
                "help_seeking_type": option_label("strategy_hint_request"),
                "max_scaffold_level": option_label("L2"),
                "help_forms": option_label("micro_example"),
                "leakage_risk": option_label("medium"),
                "coach_confidence": "4",
                "review_status": option_label("labeled"),
                "evidence_quote": "",
                "recent_dialogue": "1",
                "student_code_excerpt": "N/A",
            }
        ]

        errors = validator_v2.validate_rows(rows, focus_ids={"state_design"})
        fields = {error["field"] for error in errors}

        self.assertIn("registered_focus_id", fields)
        self.assertIn("evidence_quote", fields)
        self.assertIn("recent_dialogue", fields)

    def test_complete_code_request_can_use_unknown_bridge_family(self):
        rows = [
            {
                "case_id": "case_direct",
                "turn_type": option_label("complete_code_request"),
                "diagnosis_uncertainty": option_label("high"),
                "student_problem_solving_state": option_label("insufficient_evidence"),
                "student_attempt_level": option_label("none"),
                "student_already_stated_bridge": option_label("not_stated"),
                "policy_risk_type": option_label("complete_code_risk"),
                "primary_bridge_family": option_label("unknown_or_not_applicable"),
                "primary_bridge_subtype_id": option_label("policy.direct_answer_request"),
                "registered_focus_id": "direct_answer_request_policy",
                "focus_match_status": option_label("matched_existing"),
                "help_seeking_type": option_label("complete_answer_request"),
                "max_scaffold_level": option_label("L0"),
                "help_forms": option_label("debug_evidence_request"),
                "leakage_risk": option_label("high"),
                "coach_confidence": "5",
                "review_status": option_label("labeled"),
                "evidence_quote": "学生说：直接给我完整代码。",
                "recent_dialogue": "N/A",
                "student_code_excerpt": "N/A",
            }
        ]

        errors = validator_v2.validate_rows(rows, focus_ids={"direct_answer_request_policy"})

        self.assertEqual([], errors)

    def test_validate_rows_reports_subtype_family_mismatch(self):
        rows = [
            {
                "case_id": "case_mismatch",
                "turn_type": option_label("diagnosable_learning_turn"),
                "diagnosis_uncertainty": option_label("low"),
                "student_problem_solving_state": option_label("method_application_gap"),
                "student_attempt_level": option_label("partial_attempt"),
                "student_already_stated_bridge": option_label("not_stated"),
                "policy_risk_type": option_label("none"),
                "primary_bridge_family": option_label("aggregation_contribution_bridge"),
                "primary_bridge_subtype_id": option_label("predicate.feasibility_truth_direction"),
                "registered_focus_id": "check_condition",
                "focus_match_status": option_label("matched_existing"),
                "help_seeking_type": option_label("strategy_hint_request"),
                "max_scaffold_level": option_label("L2"),
                "help_forms": option_label("micro_example"),
                "leakage_risk": option_label("medium"),
                "coach_confidence": "4",
                "review_status": option_label("labeled"),
                "evidence_quote": "学生说：check(mid) 到底返回 true 还是 false。",
                "recent_dialogue": "N/A",
                "student_code_excerpt": "N/A",
            }
        ]

        errors = validator_v2.validate_rows(rows, focus_ids={"check_condition"})

        self.assertIn("primary_bridge_subtype_id", {error["field"] for error in errors})

    def test_validate_rows_rejects_l4_as_max_scaffold_level(self):
        rows = [
            {
                "case_id": "case_l4",
                "turn_type": option_label("diagnosable_learning_turn"),
                "diagnosis_uncertainty": option_label("low"),
                "student_problem_solving_state": option_label("method_application_gap"),
                "student_attempt_level": option_label("partial_attempt"),
                "student_already_stated_bridge": option_label("not_stated"),
                "policy_risk_type": option_label("none"),
                "primary_bridge_family": option_label("predicate_condition_bridge"),
                "primary_bridge_subtype_id": option_label("predicate.feasibility_truth_direction"),
                "registered_focus_id": "check_condition",
                "focus_match_status": option_label("matched_existing"),
                "help_seeking_type": option_label("strategy_hint_request"),
                "max_scaffold_level": "直接补完关键桥、完整题解或完整代码；只用于泄露评价（L4_forbidden）",
                "help_forms": option_label("micro_example"),
                "leakage_risk": option_label("medium"),
                "coach_confidence": "4",
                "review_status": option_label("labeled"),
                "evidence_quote": "学生说：check(mid) 到底返回 true 还是 false。",
                "recent_dialogue": "N/A",
                "student_code_excerpt": "N/A",
            }
        ]

        errors = validator_v2.validate_rows(rows, focus_ids={"check_condition"})

        self.assertIn("max_scaffold_level", {error["field"] for error in errors})

    def test_policy_risk_mismatch_is_reported_as_warning(self):
        rows = [
            {
                "case_id": "case_warning",
                "turn_type": option_label("complete_code_request"),
                "policy_risk_type": option_label("none"),
            }
        ]

        warnings = validator_v2.validate_warnings(rows)

        self.assertEqual("policy_risk_type", warnings[0]["field"])

    def test_load_xlsx_rows_reads_data_after_machine_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "mini.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "标注表"
            sheet.append(["样本编号", "标注状态"])
            sheet.append(["case_id", "review_status"])
            sheet.append(["case_1", option_label("labeled")])
            workbook.save(path)

            rows = validator_v2.load_xlsx_rows(path)

        self.assertEqual([{"case_id": "case_1", "review_status": option_label("labeled")}], rows)


if __name__ == "__main__":
    unittest.main()
