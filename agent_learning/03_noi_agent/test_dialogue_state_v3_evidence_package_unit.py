import unittest
from pathlib import Path


class DialogueStateV3EvidencePackageTest(unittest.TestCase):
    def test_reproduce_bundle_core_numbers(self):
        from evals.aichat import reproduce_dialogue_state_v3_tables as reproduce

        root = Path(__file__).resolve().parent
        bundle = reproduce.reproduce(root)

        main = bundle["main_paper_ready_tables"]["main_scaffold_eval"][
            "priority60_adjudicated_plus_coachA"
        ]
        bridge_repair = main["bridge_contract_compact_guard_repair"]
        self.assertEqual(bridge_repair["n"], 31)
        self.assertAlmostEqual(bridge_repair["overall"], 4.064516129032258)
        self.assertEqual(bridge_repair["major_answer"], 0)
        self.assertEqual(bridge_repair["no_leakage"], 25)
        self.assertEqual(bridge_repair["burden"], {"low": 3, "medium": 28, "high": 0})

        pair = bundle["pairwise"]["priority60_adjudicated_plus_coachA"][
            "bridge_contract_compact_guard_repair__vs__dbox_inspired_guard"
        ]
        self.assertEqual(pair["win_tie_loss"], {"win": 14, "tie": 10, "loss": 7})
        self.assertAlmostEqual(pair["mean_delta_overall"], 0.2903225806451613)
        self.assertEqual(pair["major_answer_delta"], -2)

        repair = bundle["repair_same_candidate_summary"]
        self.assertEqual(repair["labeled_pairs"], 30)
        self.assertEqual(
            repair["before_leakage_distribution"]["major_bridge_leakage"], 7
        )
        self.assertEqual(
            repair["after_leakage_distribution"].get("major_bridge_leakage", 0), 0
        )
        self.assertEqual(
            repair["leakage_delta"], {"improved": 16, "same": 14, "worse": 0}
        )

        dbox = bundle["dbox_fairness_addon"]
        self.assertAlmostEqual(
            dbox["summaries"]["dbox_repair_addon_review20"]["overall"], 3.55
        )
        self.assertEqual(
            dbox["paired"]["dbox_repair_addon_minus_main_dbox_guard_A"]["win_tie_loss"],
            {"win": 6, "tie": 9, "loss": 5},
        )

        llm = bundle["llm_grader_calibration"]["priority60_adjudicated_deepseek"][
            "case_specific_bridge_rubric_judge"
        ]
        self.assertAlmostEqual(llm["leakage_label_accuracy"], 0.6166666666666667)
        self.assertEqual(llm["major_leakage_false_negative_rate"], 1.0)

    def test_report_verification_has_no_diff(self):
        from evals.aichat import reproduce_dialogue_state_v3_tables as reproduce
        from evals.aichat import verify_dialogue_state_v3_reports as verify

        root = Path(__file__).resolve().parent
        bundle = reproduce.reproduce(root)
        diffs = verify.collect_diffs(root, bundle)
        self.assertEqual(diffs, [])


if __name__ == "__main__":
    unittest.main()
