import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat.build_bridgebench_v2_gold_seed import (
    build_legacy_seed_row,
    merge_seed_rows_with_v2_gold,
)


class BuildBridgebenchV2GoldSeedTests(unittest.TestCase):
    def test_build_legacy_seed_row_maps_v2_gold_to_runner_fields(self):
        seed_row = {
            "id": "cp_bridge_001",
            "student_message": "我知道要 LCA，但不知道每条路径到底在哪里加减标记。",
            "gold_bridge_family": "aggregation_bridge",
        }
        gold_row = {
            "case_id": "cp_bridge_001",
            "student_problem_solving_state": "method_application_gap",
            "primary_bridge_family": "aggregation_contribution_bridge",
            "registered_focus_id": "tree_path_difference",
            "help_seeking_type": ["strategy_hint_request", "implementation_help"],
            "missing_bridge_instance": "缺路径贡献标记桥。",
            "max_scaffold_level": "L2",
            "bridge_specific_forbidden_content": ["no_exact_contribution_formula"],
            "general_forbidden_content": ["no_full_solution", "no_full_code"],
            "focus_match_status": "matched_existing",
        }

        merged = build_legacy_seed_row(seed_row, gold_row)

        self.assertEqual(merged["gold_student_state"], "method_application_gap")
        self.assertEqual(merged["gold_bridge_family"], "aggregation_contribution_bridge")
        self.assertEqual(merged["gold_known_focus"], "tree_path_difference")
        self.assertEqual(merged["gold_help_seeking_type"], "strategy_hint_request")
        self.assertEqual(merged["gold_missing_link"], "缺路径贡献标记桥。")
        self.assertEqual(merged["gold_allowed_help_level"], "L2")
        self.assertIn("no_exact_contribution_formula", merged["gold_forbidden_completion"])
        self.assertFalse(merged["needs_new_focus"])
        self.assertEqual(merged["coach_v2_gold"]["case_id"], "cp_bridge_001")

    def test_merge_seed_rows_with_v2_gold_marks_new_focus_candidates(self):
        seed_rows = [
            {"id": "cp_bridge_017", "student_message": "题目说合并两个集合。"},
            {"id": "cp_bridge_999", "student_message": "没有标注的样本。"},
        ]
        gold_rows = [
            {
                "case_id": "cp_bridge_017",
                "student_problem_solving_state": "implementation_translation_gap",
                "primary_bridge_family": "data_structure_operation_bridge",
                "registered_focus_id": "unknown",
                "help_seeking_type": ["implementation_help"],
                "missing_bridge_instance": "缺并查集操作映射。",
                "max_scaffold_level": "L2",
                "new_focus_candidate": "union_find_operation_mapping",
                "focus_match_status": "needs_new_focus",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "merged.jsonl"
            merged_count = merge_seed_rows_with_v2_gold(seed_rows, gold_rows, output_path)
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(merged_count, 1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "cp_bridge_017")
        self.assertFalse(rows[0]["needs_new_focus"])
        self.assertEqual(rows[0]["gold_known_focus"], "union_find_operation_mapping")
        self.assertEqual(rows[0]["new_focus_candidate"], "union_find_operation_mapping")


if __name__ == "__main__":
    unittest.main()
