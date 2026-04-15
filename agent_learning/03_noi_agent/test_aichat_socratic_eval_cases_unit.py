import json
import re
import unittest
from pathlib import Path


EVAL_CASES_PATH = Path("docs/common/aichat_socratic_eval_cases_2026_04.json")


class AIChatSocraticEvalCasesTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(EVAL_CASES_PATH.read_text())
        self.cases = self.data["cases"]

    def test_cases_should_have_unique_ids_and_required_control_fields(self):
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))

        required_control_fields = {"zpd_level", "tutor_action", "scaffold_stage"}
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(required_control_fields <= set(case["expected_control"]))
                self.assertIn(case["expected_control"]["scaffold_stage"], {1, 2, 3, 4})

    def test_hard_fail_patterns_should_not_include_overbroad_answer_phrase(self):
        patterns = self.data["rubric"]["hard_fail_patterns"]

        self.assertNotIn("答案是", patterns)
        for safe_question in [
            "check(mid) 返回 true 时你觉得答案是往左缩还是往右缩？",
            "这条路径影响的点集，答案是一条线还是两段？",
            "不要跳过思考直接套模板，先说你的最小尝试。",
        ]:
            with self.subTest(safe_question=safe_question):
                self.assertFalse(any(re.search(pattern, safe_question) for pattern in patterns))

    def test_reviewed_cases_should_keep_corrected_semantics(self):
        cases = {case["id"]: case for case in self.cases}

        self.assertEqual("P3128", cases["chat_socratic_016_emotion_pressure"]["problem_ref"])
        self.assertEqual("Z2", cases["chat_socratic_011_shared_prefix_merging"]["expected_control"]["zpd_level"])
        self.assertEqual("Z2", cases["chat_socratic_013_code_no_target"]["expected_control"]["zpd_level"])
        self.assertEqual("L3", cases["chat_socratic_019_repeated_stuck_to_checkin"]["expected_control"]["max_level"])
        self.assertEqual("Z2", cases["chat_socratic_019_repeated_stuck_to_checkin"]["expected_control"]["zpd_level"])

    def test_contract_cases_align_with_handoff_spec(self):
        cases = {case["id"]: case for case in self.cases}

        case_013 = cases["chat_socratic_013_code_no_target"]
        self.assertEqual("ask_code_evidence", case_013["expected_control"]["tutor_action"])
        self.assertIn("不追踪代码执行", "".join(case_013["expected_reply_behavior"]))
        self.assertIn("追踪代码执行", "".join(case_013["forbidden_reply_behavior"]))

        case_019 = cases["chat_socratic_019_repeated_stuck_to_checkin"]
        self.assertIn("避免 A/B 夹答案", "".join(case_019["expected_reply_behavior"]))
        self.assertIn("check(mid)", "".join(case_019["forbidden_reply_behavior"]))

        case_023 = cases["chat_socratic_023_already_ac_redirect"]
        self.assertIn("不在 AIChat 里继续理解验证", "".join(case_023["expected_reply_behavior"]))
        self.assertIn("代码里用来累加路径次数的数组", "".join(case_023["forbidden_reply_behavior"]))

    def test_baseline_should_cover_common_student_conversation_gaps(self):
        topics = {case["topic"] for case in self.cases}

        for expected_topic in [
            "knapsack_dp / state_design",
            "debug / evidence_request",
            "checkin_handoff",
            "complexity_fit / tle_debug",
            "greedy / correctness_proof",
            "tree_dp / state_design",
            "mid_conversation_pivot",
            "union_find / application",
        ]:
            with self.subTest(topic=expected_topic):
                self.assertIn(expected_topic, topics)


if __name__ == "__main__":
    unittest.main()
