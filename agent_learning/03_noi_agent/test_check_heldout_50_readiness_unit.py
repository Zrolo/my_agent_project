import io
import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from evals.aichat import check_heldout_50_readiness as checker
from evals.aichat.coach_labeling_schema_v2 import option_label


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _draft_row(case_id: str, *, status: str = "draft_needs_coach_review") -> dict:
    return {
        "case_id": case_id,
        "category": "dp_state",
        "problem_ref": f"problem_{case_id}",
        "student_message": "状态到底应该存什么？",
        "problem_context": "背包类 DP。",
        "recent_dialogue": "N/A",
        "student_code_excerpt": "N/A",
        "student_known_state": "学生知道大方向。",
        "missing_bridge": "缺状态语义。",
        "allowed_help_level": "L2",
        "forbidden_content": ["no_exact_state_definition"],
        "success_criteria": ["不直接给状态定义。"],
        "review_notes_for_coach": "检查是否说穿状态语义。",
        "reference_label_status": status,
    }


def _workbook_row(case_id: str, *, review_status: str = "labeled") -> dict:
    return {
        "case_id": case_id,
        "turn_type": option_label("critical_bridge_request"),
        "diagnosis_uncertainty": option_label("low"),
        "student_problem_solving_state": option_label("method_application_gap"),
        "student_attempt_level": option_label("partial_attempt"),
        "student_already_stated_bridge": option_label("not_stated"),
        "policy_risk_type": option_label("critical_bridge_completion_risk"),
        "primary_bridge_family": option_label("representation_state_bridge"),
        "primary_bridge_subtype_id": option_label("state.table_or_memo_cell_semantics"),
        "missing_bridge_instance": "缺状态语义。",
        "evidence_type": option_label("asks_state_definition"),
        "evidence_quote": "“状态到底应该存什么”",
        "registered_focus_id": "state_design",
        "focus_match_status": option_label("matched_existing"),
        "help_seeking_type": option_label("concept_explanation"),
        "max_scaffold_level": option_label("L2"),
        "help_forms": option_label("guiding_question"),
        "general_forbidden_content": option_label("no_full_solution"),
        "bridge_specific_forbidden_content": option_label("no_exact_state_definition"),
        "leakage_risk": option_label("high"),
        "coach_confidence": "5",
        "review_status": option_label(review_status),
    }


def _make_workbook(path: Path, rows: list[dict]) -> None:
    headers = [
        "case_id",
        "turn_type",
        "diagnosis_uncertainty",
        "student_problem_solving_state",
        "student_attempt_level",
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


class Heldout50ReadinessCheckerTests(unittest.TestCase):
    def test_draft_only_reports_labeling_blockers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            draft = tmp / "draft.jsonl"
            coach_a = tmp / "coach_a.xlsx"
            coach_b = tmp / "coach_b.xlsx"
            frozen = tmp / "frozen.jsonl"
            _write_jsonl(draft, [_draft_row("case_1"), _draft_row("case_2")])
            _make_workbook(coach_a, [_workbook_row("case_1"), _workbook_row("case_2", review_status="unlabeled")])
            _make_workbook(coach_b, [_workbook_row("case_1")])

            result = checker.check_readiness(
                draft_jsonl=draft,
                coach_a_workbook=coach_a,
                coach_b_workbook=coach_b,
                frozen_jsonl=frozen,
                expected_count=2,
                expected_coach_b_overlap=2,
            )

        self.assertFalse(result["ready_for_main_experiment"])
        self.assertEqual(1, result["coach_a"]["labeled_count"])
        self.assertEqual(1, result["coach_b"]["labeled_count"])
        self.assertFalse(result["frozen_dataset"]["exists"])
        self.assertIn("coach_a_incomplete", result["blocking_reasons"])
        self.assertIn("coach_b_overlap_incomplete", result["blocking_reasons"])
        self.assertIn("frozen_jsonl_missing", result["blocking_reasons"])

    def test_frozen_reference_can_be_ready(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            draft = tmp / "draft.jsonl"
            coach_a = tmp / "coach_a.xlsx"
            coach_b = tmp / "coach_b.xlsx"
            frozen = tmp / "frozen.jsonl"
            frozen_rows = [
                _draft_row("case_1", status="coach_reference"),
                _draft_row("case_2", status="coach_reference"),
            ]
            _write_jsonl(draft, [_draft_row("case_1"), _draft_row("case_2")])
            _write_jsonl(frozen, frozen_rows)
            _make_workbook(coach_a, [_workbook_row("case_1"), _workbook_row("case_2")])
            _make_workbook(coach_b, [_workbook_row("case_1"), _workbook_row("case_2")])

            result = checker.check_readiness(
                draft_jsonl=draft,
                coach_a_workbook=coach_a,
                coach_b_workbook=coach_b,
                frozen_jsonl=frozen,
                expected_count=2,
                expected_coach_b_overlap=2,
            )

        self.assertTrue(result["ready_for_main_experiment"])
        self.assertEqual([], result["blocking_reasons"])
        self.assertTrue(result["frozen_dataset"]["formal_preflight_ok"])

    def test_main_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            draft = tmp / "draft.jsonl"
            coach_a = tmp / "coach_a.xlsx"
            coach_b = tmp / "coach_b.xlsx"
            frozen = tmp / "frozen.jsonl"
            output_json = tmp / "readiness.json"
            output_md_zh = tmp / "readiness.zh.md"
            output_md = tmp / "readiness.md"
            _write_jsonl(draft, [_draft_row("case_1")])
            _make_workbook(coach_a, [_workbook_row("case_1")])
            _make_workbook(coach_b, [_workbook_row("case_1")])

            exit_code = checker.main(
                [
                    "--draft-jsonl",
                    str(draft),
                    "--coach-a-workbook",
                    str(coach_a),
                    "--coach-b-workbook",
                    str(coach_b),
                    "--frozen-jsonl",
                    str(frozen),
                    "--expected-count",
                    "1",
                    "--expected-coach-b-overlap",
                    "1",
                    "--output-json",
                    str(output_json),
                    "--output-md-zh",
                    str(output_md_zh),
                    "--output-md",
                    str(output_md),
                ],
                stdout=io.StringIO(),
            )

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            zh = output_md_zh.read_text(encoding="utf-8")
            en = output_md.read_text(encoding="utf-8")

        self.assertEqual(0, exit_code)
        self.assertFalse(payload["ready_for_main_experiment"])
        self.assertIn("Held-out 50 Readiness", zh)
        self.assertIn("Held-out 50 Readiness", en)


if __name__ == "__main__":
    unittest.main()
