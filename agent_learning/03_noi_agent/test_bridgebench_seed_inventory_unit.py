import json
import unittest
from pathlib import Path


SEED_PATH = Path("docs/research/bridgebench_cp_seed_v1.jsonl")

REQUIRED_FIELDS = {
    "id",
    "problem_ref",
    "topic",
    "student_message",
    "problem_context",
    "gold_student_state",
    "gold_bridge_family",
    "gold_known_focus",
    "gold_help_seeking_type",
    "gold_missing_link",
    "gold_allowed_help_level",
    "gold_forbidden_completion",
    "needs_new_focus",
}

EXPECTED_STATES = {
    "text_comprehension_blocked",
    "problem_representation_unclear",
    "strategy_generation_blocked",
    "strategy_misconception",
    "strategy_application_gap",
    "implementation_execution_gap",
    "debugging_verification_gap",
    "reflection_transfer_gap",
}

EXPECTED_HELP_LEVELS = {"L1", "L2", "L3"}


def _load_seed_rows() -> list[dict]:
    return [json.loads(line) for line in SEED_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


class BridgeBenchSeedInventoryTests(unittest.TestCase):
    def test_seed_inventory_has_50_unique_complete_rows(self):
        rows = _load_seed_rows()

        self.assertGreaterEqual(len(rows), 50)
        self.assertEqual(len(rows), len({row["id"] for row in rows}))
        for row in rows:
            missing = REQUIRED_FIELDS - set(row)
            self.assertEqual(set(), missing, row.get("id"))
            for field in REQUIRED_FIELDS - {"needs_new_focus"}:
                self.assertTrue(str(row.get(field, "")).strip(), f"{row['id']} missing {field}")
            self.assertIsInstance(row["needs_new_focus"], bool)

    def test_seed_inventory_covers_core_student_states_and_help_levels(self):
        rows = _load_seed_rows()

        states = {row["gold_student_state"] for row in rows}
        levels = {row["gold_allowed_help_level"] for row in rows}

        self.assertTrue(EXPECTED_STATES <= states)
        self.assertTrue(EXPECTED_HELP_LEVELS <= levels)

    def test_seed_inventory_has_broad_bridge_family_coverage(self):
        rows = _load_seed_rows()

        families = {row["gold_bridge_family"] for row in rows}

        self.assertGreaterEqual(len(families), 10)


if __name__ == "__main__":
    unittest.main()
