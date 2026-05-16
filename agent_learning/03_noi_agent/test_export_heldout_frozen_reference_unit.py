import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from evals.aichat import export_heldout_frozen_reference as exporter
from evals.aichat import validate_heldout_50_dataset
from evals.aichat.coach_labeling_schema_v2 import option_label


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _draft_row(case_id: str = "heldout_cp_001") -> dict:
    return {
        "case_id": case_id,
        "category": "dp_state",
        "problem_ref": "heldout_dp_state_01",
        "student_message": "状态到底应该存什么？",
        "problem_context": "给若干物品的代价和收益，在总代价限制内最大化收益。",
        "recent_dialogue": "N/A",
        "student_code_excerpt": "N/A",
        "student_known_state": "学生知道像 DP，但没有说清状态语义。",
        "missing_bridge": "缺把下标含义和值含义分开。",
        "allowed_help_level": "L2",
        "forbidden_content": ["no_exact_state_definition", "no_full_solution"],
        "success_criteria": ["回复不直接给完整状态定义。"],
        "review_notes_for_coach": "检查是否过早补完状态语义。",
        "reference_label_status": "draft_needs_coach_review",
    }


def _make_workbook(path: Path, rows: list[dict]) -> None:
    headers = [
        "case_id",
        "problem_ref",
        "student_message",
        "problem_context",
        "recent_dialogue",
        "student_code_excerpt",
        "turn_type",
        "diagnosis_uncertainty",
        "student_problem_solving_state",
        "student_attempt_level",
        "student_already_knows",
        "student_already_stated_bridge",
        "policy_risk_type",
        "primary_bridge_family",
        "primary_bridge_subtype_id",
        "missing_bridge_instance",
        "evidence_type",
        "evidence_quote",
        "registered_focus_id",
        "focus_match_status",
        "help_seeking_type",
        "max_scaffold_level",
        "help_forms",
        "general_forbidden_content",
        "bridge_specific_forbidden_content",
        "leakage_risk",
        "coach_confidence",
        "review_status",
    ]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "标注表"
    sheet.append([""] * len(headers))
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header, "") for header in headers])
    workbook.save(path)


def _labeled_workbook_row(case_id: str = "heldout_cp_001") -> dict:
    return {
        "case_id": case_id,
        "problem_ref": "heldout_dp_state_01",
        "student_message": "状态到底应该存什么？",
        "problem_context": "给若干物品的代价和收益，在总代价限制内最大化收益。",
        "recent_dialogue": "N/A",
        "student_code_excerpt": "N/A",
        "turn_type": option_label("critical_bridge_request"),
        "diagnosis_uncertainty": option_label("low"),
        "student_problem_solving_state": option_label("method_application_gap"),
        "student_attempt_level": option_label("partial_attempt"),
        "student_already_knows": "知道像 DP。",
        "student_already_stated_bridge": option_label("not_stated"),
        "policy_risk_type": option_label("critical_bridge_completion_risk"),
        "primary_bridge_family": option_label("representation_state_bridge"),
        "primary_bridge_subtype_id": option_label("state.table_or_memo_cell_semantics"),
        "missing_bridge_instance": "缺把下标含义和值含义分开。",
        "evidence_type": option_label("asks_state_definition"),
        "evidence_quote": "“状态到底应该存什么”",
        "registered_focus_id": "state_design",
        "focus_match_status": option_label("matched_existing"),
        "help_seeking_type": option_label("concept_explanation"),
        "max_scaffold_level": option_label("L2"),
        "help_forms": f"{option_label('micro_example')};{option_label('guiding_question')}",
        "general_forbidden_content": option_label("no_full_solution"),
        "bridge_specific_forbidden_content": option_label("no_exact_state_definition"),
        "leakage_risk": option_label("high"),
        "coach_confidence": "5",
        "review_status": option_label("labeled"),
    }


class ExportHeldoutFrozenReferenceTests(unittest.TestCase):
    def test_export_merges_coach_labels_and_passes_formal_preflight(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            draft_path = tmp / "draft.jsonl"
            workbook_path = tmp / "coach_a.xlsx"
            output_path = tmp / "frozen.jsonl"
            _write_jsonl(draft_path, [_draft_row()])
            _make_workbook(workbook_path, [_labeled_workbook_row()])

            summary = exporter.export_frozen_reference(
                draft_jsonl=draft_path,
                coach_a_workbook=workbook_path,
                output_jsonl=output_path,
                reference_status="coach_reference",
            )
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
            preflight = validate_heldout_50_dataset.validate_dataset(
                output_path,
                expected_count=1,
                require_frozen_status=True,
            )

        self.assertEqual(1, summary["row_count"])
        self.assertEqual("coach_reference", rows[0]["reference_label_status"])
        self.assertEqual("representation_state_bridge", rows[0]["gold_bridge_family"])
        self.assertEqual("state_design", rows[0]["gold_known_focus"])
        self.assertEqual("L2", rows[0]["gold_allowed_help_level"])
        self.assertEqual("coach_reference", rows[0]["coach_v2_gold"]["label_reference_type"])
        self.assertTrue(preflight["ok"])

    def test_export_rejects_unlabeled_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            draft_path = tmp / "draft.jsonl"
            workbook_path = tmp / "coach_a.xlsx"
            output_path = tmp / "frozen.jsonl"
            _write_jsonl(draft_path, [_draft_row()])
            unlabeled = _labeled_workbook_row()
            unlabeled["review_status"] = option_label("unlabeled")
            _make_workbook(workbook_path, [unlabeled])

            with self.assertRaisesRegex(ValueError, "missing_labeled_reference"):
                exporter.export_frozen_reference(
                    draft_jsonl=draft_path,
                    coach_a_workbook=workbook_path,
                    output_jsonl=output_path,
                    reference_status="coach_reference",
                )

    def test_adjudicated_status_sets_adjudication_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            draft_path = tmp / "draft.jsonl"
            workbook_path = tmp / "coach_a.xlsx"
            output_path = tmp / "frozen.jsonl"
            _write_jsonl(draft_path, [_draft_row()])
            _make_workbook(workbook_path, [_labeled_workbook_row()])

            exporter.export_frozen_reference(
                draft_jsonl=draft_path,
                coach_a_workbook=workbook_path,
                output_jsonl=output_path,
                reference_status="adjudicated_reference",
            )
            row = json.loads(output_path.read_text(encoding="utf-8").splitlines()[0])

        self.assertEqual("adjudicated_reference", row["reference_label_status"])
        self.assertEqual("adjudicated_reference", row["coach_v2_gold"]["label_reference_type"])
        self.assertEqual("adjudicated", row["coach_v2_gold"]["label_adjudication_status"])
        self.assertTrue(row["coach_v2_gold"]["is_adjudicated_gold"])


if __name__ == "__main__":
    unittest.main()
