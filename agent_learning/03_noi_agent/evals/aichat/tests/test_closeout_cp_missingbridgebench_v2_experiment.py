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


class V2CloseoutHelperTest(unittest.TestCase):
    def setUp(self) -> None:
        self.closeout = load_module(
            "evals/aichat/closeout_cp_missingbridgebench_v2_experiment.py",
            "v2_closeout",
        )

    def make_review_row(self, case_idx: int, design_id: str, response_idx: int) -> dict:
        return {
            "case_id": f"case-{case_idx:03d}",
            "anonymized_response_id": f"resp-{response_idx:04d}",
            "condition_id": design_id,
            "response_text": "redacted candidate response",
            "overall_quality_score": "4",
            "would_show_to_student": "yes",
            "leakage_label": "no_leakage",
            "bridge_reveal_justification": "no_reveal",
            "student_response_burden": "low",
            "review_status": "labeled",
            "reviewer_confidence": "high",
            "scores": {
                "bridge_identification": 2,
                "bridge_leakage_control": 2,
                "bridge_oriented_micro_example": 1,
                "groundedness": 2,
                "next_step_clarity": 2,
                "scaffold_appropriateness": 2,
                "scaffold_sufficiency": 2,
                "single_focus_coherence": 2,
            },
        }

    def make_full_review_rows(self) -> list[dict]:
        rows = []
        response_idx = 0
        for case_idx in range(1, 101):
            for design_id in self.closeout.DESIGN_ORDER:
                response_idx += 1
                rows.append(self.make_review_row(case_idx, design_id, response_idx))
        return rows

    def test_slug_maps_known_designs_to_reader_labels(self):
        self.assertEqual(
            self.closeout.reader_label("dbox_inspired_guard"),
            "DBox-inspired + Guard",
        )
        self.assertEqual(
            self.closeout.reader_label("bridge_contract_compact_guard_repair"),
            "Bridge Contract + Guard/Repair",
        )

    def test_main_summary_extracts_core_metrics(self):
        payload = {
            "row_count": 700,
            "case_count": 100,
            "system_summary": {
                "dbox_inspired_guard": {
                    "n": 100,
                    "overall_quality_mean": 4.23,
                    "student_ready_pass_count": 72,
                    "student_ready_safe_pass_count": 54,
                    "major_or_answer_leakage_count": 1,
                    "answer_leakage_count": 0,
                    "student_response_burden_low_count": 69,
                    "student_response_burden_medium_count": 30,
                    "student_response_burden_high_count": 1,
                    "scaffold_sufficiency_mean": 1.89,
                }
            },
        }
        summary = self.closeout.extract_main_results(payload)
        row = summary["designs"][0]
        self.assertEqual(row["design_id"], "dbox_inspired_guard")
        self.assertEqual(row["design_label"], "DBox-inspired + Guard")
        self.assertEqual(row["overall_quality_mean"], 4.23)
        self.assertEqual(row["student_ready_count"], 72)
        self.assertEqual(row["safe_ready_count"], 54)
        self.assertEqual(row["major_plus_answer_leakage_count"], 1)
        self.assertEqual(row["burden_low_medium_high"], "69/30/1")

    def test_extract_required_pairwise_comparisons(self):
        payload = {
            "paired_comparisons": {
                "bridge_contract_compact_guard__vs__dbox_inspired_guard": {
                    "paired_cases": 100,
                    "mean_diff": -0.41,
                    "wins": 18,
                    "ties": 45,
                    "losses": 37,
                    "bootstrap_ci95": [-0.63, -0.19],
                }
            }
        }
        comparisons = self.closeout.extract_required_pairwise(payload)
        self.assertEqual(len(comparisons), 1)
        item = comparisons[0]
        self.assertEqual(item["comparison"], "Bridge Contract + Guard - DBox-inspired + Guard")
        self.assertEqual(item["delta_overall"], -0.41)
        self.assertEqual(item["w_t_l"], "18/45/37")

    def test_manifest_hashes_existing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifact.txt"
            path.write_text("stable evidence\n", encoding="utf-8")
            manifest = self.closeout.build_freeze_manifest(
                input_paths=[path],
                output_paths=[],
                closeout_summary={"case_count": 100, "row_count": 700},
                evidence_role="v2 benchmark closeout",
                freeze_date="2026-05-22",
            )
        self.assertEqual(manifest["freeze_date"], "2026-05-22")
        self.assertEqual(manifest["closeout_summary"]["case_count"], 100)
        self.assertEqual(len(manifest["inputs"]), 1)
        self.assertEqual(manifest["inputs"][0]["sha256"], "1e134b371815db58aca1e1b09f1a744a94ee7e12db46baccb1773d1e794484e0")
        self.assertEqual(manifest["inputs"][0]["label"], "artifact.txt")
        self.assertTrue(manifest["inputs"][0]["private_path_redacted"])

    def test_manifest_redacts_private_and_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            private_path = Path(tmpdir) / ".local_private" / "review_labels.jsonl"
            private_path.parent.mkdir()
            private_path.write_text("private evidence\n", encoding="utf-8")
            user_path = Path(tmpdir) / "Users" / "kongyouli" / "Downloads" / "workbook.xlsx"
            user_path.parent.mkdir(parents=True)
            user_path.write_text("workbook bytes\n", encoding="utf-8")
            manifest = self.closeout.build_freeze_manifest(
                input_paths=[private_path, user_path],
                output_paths=[],
                closeout_summary={"case_count": 100, "row_count": 700},
                evidence_role="v2 benchmark closeout",
                freeze_date="2026-05-22",
            )

        manifest_json = json.dumps(manifest, ensure_ascii=False)
        self.assertNotIn(".local_private", manifest_json)
        self.assertNotIn("/Users", manifest_json)
        self.assertEqual(manifest["inputs"][0]["label"], "review_labels.jsonl")
        self.assertEqual(manifest["inputs"][1]["label"], "workbook.xlsx")
        self.assertTrue(manifest["inputs"][0]["private_path_redacted"])
        self.assertTrue(manifest["inputs"][1]["private_path_redacted"])

    def test_second_review_summary_is_sanitized(self):
        reliability = self.closeout.build_review_reliability(
            {
                "source": "computed_from_review_labels",
                "observed": {"row_count": 700, "case_count": 100, "unique_response_id_count": 700},
                "missing_required_fields": {},
                "missing_score_fields": {},
                "duplicate_response_id_count": 0,
                "cases_missing_designs_total": 0,
                "cases_with_duplicate_designs": 0,
                "passed": True,
            },
            {
                "status": "complete",
                "reviewed_rows": 40,
                "agreement_rate": 0.82,
                "private_path": "/Users/kongyouli/Downloads/private.xlsx",
                "notes": "raw adjudicator notes should stay private",
                "row_examples": [{"case_id": "case-001"}],
            },
        )
        second_review = reliability["second_review_summary"]
        second_review_json = json.dumps(second_review, ensure_ascii=False)
        self.assertEqual(second_review["status"], "complete")
        self.assertEqual(second_review["reviewed_rows"], 40)
        self.assertEqual(second_review["agreement_rate"], 0.82)
        self.assertNotIn("private_path", second_review)
        self.assertNotIn("notes", second_review)
        self.assertNotIn("row_examples", second_review)
        self.assertNotIn("/Users", second_review_json)
        self.assertNotIn("raw adjudicator notes", second_review_json)

    def test_failure_mode_summary_uses_aggregates_without_case_ids(self):
        summary = self.closeout.summarize_failure_modes(
            [
                {
                    "case_id": "case-001",
                    "condition_id": "dbox_inspired_guard",
                    "leakage_label": "major_bridge_leakage",
                    "would_show_to_student": "no",
                    "overall_quality_score": "2",
                },
                {
                    "case_id": "case-002",
                    "condition_id": "dbox_inspired_guard",
                    "leakage_label": "answer_leakage",
                    "would_show_to_student": "yes",
                    "overall_quality_score": "4",
                },
            ]
        )
        summary_json = json.dumps(summary, ensure_ascii=False)
        aggregate = summary["major_or_answer_aggregate_by_design"]["DBox-inspired + Guard"]
        self.assertEqual(aggregate["total"], 2)
        self.assertEqual(aggregate["by_leakage"]["major_bridge_leakage"], 1)
        self.assertEqual(aggregate["by_leakage"]["answer_leakage"], 1)
        self.assertEqual(aggregate["by_show"]["no"], 1)
        self.assertEqual(aggregate["by_show"]["yes"], 1)
        self.assertEqual(aggregate["by_overall_bucket"]["low_1_2"], 1)
        self.assertEqual(aggregate["by_overall_bucket"]["high_4_5"], 1)
        self.assertNotIn("major_or_answer_rows_no_private_text", summary)
        self.assertNotIn("case-001", summary_json)
        self.assertNotIn("case_id", summary_json)

    def test_report_does_not_include_private_paths_by_default(self):
        closeout_summary = {
            "case_count": 100,
            "row_count": 700,
            "main_results": {
                "designs": [
                    {
                        "design_label": "DBox-inspired + Guard",
                        "n": 100,
                        "overall_quality_mean": 4.23,
                        "student_ready_count": 72,
                        "safe_ready_count": 54,
                        "major_plus_answer_leakage_count": 1,
                        "answer_leakage_count": 0,
                        "burden_low_medium_high": "69/30/1",
                    }
                ]
            },
            "required_pairwise": [],
            "privacy_boundary": "Aggregate-only public reporting.",
        }
        report = self.closeout.render_closeout_report_zh(closeout_summary)
        self.assertIn("DBox-inspired + Guard", report)
        self.assertNotIn(".local_private", report)
        self.assertNotIn("full_student_code", report)

    def test_integrity_audit_passes_complete_100_by_7_labels(self):
        payload = {
            "case_count": 100,
            "row_count": 700,
            "row_count_by_system": {design_id: 100 for design_id in self.closeout.DESIGN_ORDER},
        }
        audit = self.closeout.build_integrity_audit(payload, self.make_full_review_rows())
        self.assertTrue(audit["passed"])
        self.assertEqual(audit["observed"]["row_count"], 700)
        self.assertEqual(audit["observed"]["case_count"], 100)
        self.assertEqual(audit["observed"]["unique_response_id_count"], 700)
        self.assertTrue(audit["checks"]["each_case_has_all_designs"])

    def test_integrity_audit_fails_without_label_rows(self):
        audit = self.closeout.build_integrity_audit({"case_count": 100, "row_count": 700}, [])
        self.assertFalse(audit["passed"])
        self.assertFalse(audit["checks"]["labels_rows_present"])
        self.assertEqual(audit["observed"]["row_count"], 0)

    def test_integrity_audit_fails_missing_required_review_field(self):
        rows = self.make_full_review_rows()
        rows[0]["overall_quality_score"] = ""
        audit = self.closeout.build_integrity_audit({"case_count": 100, "row_count": 700}, rows)
        self.assertFalse(audit["passed"])
        self.assertEqual(audit["missing_required_fields"]["overall_quality_score"], 1)

    def test_integrity_audit_treats_micro_example_score_as_optional(self):
        rows = self.make_full_review_rows()
        rows[0]["scores"]["bridge_oriented_micro_example"] = ""
        audit = self.closeout.build_integrity_audit({"case_count": 100, "row_count": 700}, rows)
        self.assertTrue(audit["passed"])
        self.assertEqual(audit["missing_optional_score_fields"]["bridge_oriented_micro_example"], 1)

    def test_integrity_audit_fails_duplicate_response_id(self):
        rows = self.make_full_review_rows()
        rows[1]["anonymized_response_id"] = rows[0]["anonymized_response_id"]
        audit = self.closeout.build_integrity_audit({"case_count": 100, "row_count": 700}, rows)
        self.assertFalse(audit["passed"])
        self.assertEqual(audit["duplicate_response_id_count"], 1)

    def test_integrity_audit_fails_missing_design_for_case(self):
        rows = self.make_full_review_rows()
        rows = [row for row in rows if not (row["case_id"] == "case-001" and row["condition_id"] == "dbox_inspired_guard")]
        audit = self.closeout.build_integrity_audit({"case_count": 100, "row_count": 699}, rows)
        self.assertFalse(audit["passed"])
        self.assertEqual(audit["cases_missing_designs_total"], 1)
        self.assertEqual(audit["cases_with_wrong_row_count"], 1)


if __name__ == "__main__":
    unittest.main()
