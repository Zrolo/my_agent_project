import unittest

from evals.aichat.run_prompt_controlled_ablation import (
    build_oracle_bridge_result,
    build_shuffled_oracle_bridge_results,
    run_prompt_controlled_ablation,
)


def _row(case_id, bridge_family, focus):
    return {
        "id": case_id,
        "problem_ref": "generic",
        "student_message": f"{case_id} student",
        "problem_context": f"{case_id} context",
        "gold_student_state": "strategy_application_gap",
        "gold_bridge_family": bridge_family,
        "gold_known_focus": focus,
        "gold_missing_link": f"{case_id} missing link",
        "gold_allowed_help_level": "L2",
        "gold_forbidden_completion": f"{case_id} forbidden",
        "needs_new_focus": False,
    }


class PromptControlledAblationRunnerTests(unittest.TestCase):
    def test_build_oracle_bridge_result_uses_gold_fields(self):
        result = build_oracle_bridge_result(_row("case_a", "ordering_bridge", "enumeration_order"))

        self.assertEqual("ordering_bridge", result["missing_bridge"]["family"])
        self.assertEqual("enumeration_order", result["missing_bridge"]["known_focus"])
        self.assertEqual("case_a missing link", result["missing_bridge"]["description"])
        self.assertEqual(["case_a forbidden"], result["forbidden_content"])
        self.assertEqual("L2", result["allowed_help_level"])

    def test_shuffled_oracle_contracts_shift_by_one_case(self):
        rows = [
            _row("case_a", "ordering_bridge", "enumeration_order"),
            _row("case_b", "predicate_bridge", "check_condition"),
        ]

        shuffled = build_shuffled_oracle_bridge_results(rows)

        self.assertEqual("case_b", shuffled["case_a"]["source_case_id"])
        self.assertEqual("check_condition", shuffled["case_a"]["bridge_result"]["missing_bridge"]["known_focus"])
        self.assertEqual("case_a", shuffled["case_b"]["source_case_id"])

    def test_run_prompt_controlled_ablation_emits_all_variants_with_sources(self):
        rows = [_row("case_a", "ordering_bridge", "enumeration_order")]
        calls = []

        def fake_single(row, messages, bridge_result, chat_model_provider=None):
            calls.append(("single", row["id"], bridge_result.get("missing_bridge", {}).get("known_focus", "")))
            return {"response_text": "single response", "runtime_bridge_contract": {}, "self_check": {}}

        def fake_enhanced(row, messages, bridge_result, chat_model_provider=None):
            calls.append(("enhanced", row["id"], ""))
            return {"response_text": "enhanced response"}

        def fake_bridge(row, messages, bridge_result, chat_model_provider=None):
            focus = bridge_result.get("missing_bridge", {}).get("known_focus", "")
            calls.append(("bridge", row["id"], focus))
            return {"response_text": f"bridge response {focus}"}

        def fake_bridge_judge(**kwargs):
            return build_oracle_bridge_result(rows[0])

        results = run_prompt_controlled_ablation(
            rows,
            variants=[
                "single_llm_structured",
                "enhanced_prompt_only",
                "bridge_contract_predicted",
                "bridge_contract_shuffled",
                "bridge_contract_oracle",
            ],
            single_llm_tutor_fn=fake_single,
            enhanced_prompt_tutor_fn=fake_enhanced,
            bridge_contract_tutor_fn=fake_bridge,
            bridge_judge_fn=fake_bridge_judge,
            chat_model_provider="deepseek",
            judge_provider="deepseek",
            max_retries=0,
        )

        self.assertEqual(5, len(results))
        self.assertEqual(
            [
                "single_llm_structured",
                "enhanced_prompt_only",
                "bridge_contract_predicted",
                "bridge_contract_shuffled",
                "bridge_contract_oracle",
            ],
            [item["ablation_variant"] for item in results],
        )
        self.assertEqual("predicted", results[2]["contract_source"])
        self.assertEqual("shuffled_oracle", results[3]["contract_source"])
        self.assertEqual("oracle_gold", results[4]["contract_source"])
        self.assertTrue(any(call[0] == "enhanced" for call in calls))


if __name__ == "__main__":
    unittest.main()
