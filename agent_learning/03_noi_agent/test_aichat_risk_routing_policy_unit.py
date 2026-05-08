import unittest

from noi_agent import compute_pre_generation_route_risk


class AIChatRiskRoutingPolicyTests(unittest.TestCase):
    def test_direct_request_should_use_deterministic_safe_route(self):
        route = compute_pre_generation_route_risk(
            rule_risk_tags=["direct_request"],
            has_problem_context=True,
            has_code=False,
            has_debug_target=False,
            has_substantive_attempt=False,
            student_already_stated_bridge=False,
            latest_user_message="直接给我完整代码。",
        )

        self.assertEqual("high", route["input_route_risk"])
        self.assertEqual("deterministic_safe", route["recommended_route"])
        self.assertIn("direct_request", route["reasons"])

    def test_bridge_attempt_should_call_bridge_judge(self):
        route = compute_pre_generation_route_risk(
            rule_risk_tags=["bridge_attempt"],
            has_problem_context=True,
            has_code=False,
            has_debug_target=False,
            has_substantive_attempt=False,
            student_already_stated_bridge=False,
            latest_user_message="我知道要 DP，但状态怎么定义？",
        )

        self.assertEqual("medium", route["input_route_risk"])
        self.assertEqual("bridge_judge", route["recommended_route"])
        self.assertIn("bridge_attempt", route["reasons"])

    def test_type_confirm_without_evidence_should_call_bridge_judge(self):
        route = compute_pre_generation_route_risk(
            rule_risk_tags=["type_confirm"],
            has_problem_context=True,
            has_code=False,
            has_debug_target=False,
            has_substantive_attempt=False,
            student_already_stated_bridge=False,
            latest_user_message="这题是不是二分？",
        )

        self.assertEqual("high", route["input_route_risk"])
        self.assertEqual("bridge_judge", route["recommended_route"])
        self.assertIn("type_confirm_without_evidence", route["reasons"])

    def test_type_confirm_with_evidence_should_use_cautious_main_route(self):
        route = compute_pre_generation_route_risk(
            rule_risk_tags=["type_confirm"],
            has_problem_context=True,
            has_code=False,
            has_debug_target=False,
            has_substantive_attempt=True,
            student_already_stated_bridge=True,
            latest_user_message="我观察到答案越大越难满足，所以想二分，这样理解对吗？",
        )

        self.assertEqual("medium", route["input_route_risk"])
        self.assertEqual("low", route["diagnosis_uncertainty"])
        self.assertEqual("main_with_caution", route["recommended_route"])
        self.assertIn("student_evidence_present", route["reasons"])

    def test_missing_context_should_raise_uncertainty_not_leakage_route(self):
        route = compute_pre_generation_route_risk(
            rule_risk_tags=["missing_context"],
            has_problem_context=False,
            has_code=False,
            has_debug_target=False,
            has_substantive_attempt=False,
            student_already_stated_bridge=False,
            latest_user_message="这题怎么做？",
        )

        self.assertEqual("medium", route["input_route_risk"])
        self.assertEqual("high", route["diagnosis_uncertainty"])
        self.assertEqual("request_context", route["recommended_route"])
        self.assertIn("missing_context", route["reasons"])

    def test_debug_no_code_should_request_debug_evidence(self):
        route = compute_pre_generation_route_risk(
            rule_risk_tags=["debug_no_code"],
            has_problem_context=True,
            has_code=False,
            has_debug_target=False,
            has_substantive_attempt=False,
            student_already_stated_bridge=False,
            latest_user_message="我 WA 了，但不知道哪里错。",
        )

        self.assertEqual("medium", route["input_route_risk"])
        self.assertEqual("high", route["diagnosis_uncertainty"])
        self.assertEqual("request_debug_evidence", route["recommended_route"])
        self.assertIn("debug_no_code", route["reasons"])

    def test_low_risk_concrete_question_should_use_main_only(self):
        route = compute_pre_generation_route_risk(
            rule_risk_tags=[],
            has_problem_context=True,
            has_code=False,
            has_debug_target=False,
            has_substantive_attempt=True,
            student_already_stated_bridge=False,
            latest_user_message="这个样例里为什么先选 2 而不是 5？",
        )

        self.assertEqual("low", route["input_route_risk"])
        self.assertEqual("low", route["diagnosis_uncertainty"])
        self.assertEqual("main_only", route["recommended_route"])
        self.assertIn("low_risk", route["reasons"])


if __name__ == "__main__":
    unittest.main()
