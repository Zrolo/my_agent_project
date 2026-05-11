import json
import unittest

from evals.aichat import run_bridge_offline_eval as runner


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeChatResponse:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


def _seed_row():
    return {
        "id": "cp_literature_baseline_unit",
        "problem_ref": "binary_search_answer",
        "student_message": "我知道要二分答案，但 check(mid) 到底返回 true 还是 false 我总写反。",
        "problem_context": "给定限制条件，要求找满足条件的最小答案。",
        "gold_forbidden_completion": "不能直接给出 check(mid) 的真假语义和边界更新规则。",
    }


class LiteratureBaselineTutorsTests(unittest.TestCase):
    def test_codehelp_codeaid_prompt_has_no_direct_solution_constraints(self):
        prompt = runner._codehelp_codeaid_no_direct_solution_system_prompt()

        self.assertIn("CodeHelp", prompt)
        self.assertIn("CodeAid", prompt)
        self.assertIn("no-direct-solution", prompt)
        self.assertIn("no full solution", prompt)
        self.assertIn("no full code", prompt)
        self.assertIn("do not reveal the critical intermediate reasoning", prompt)
        self.assertIn("do not ask for exact operations on u/v/LCA", prompt)

    def test_bridge_inspired_prompt_has_expert_decision_fields(self):
        prompt = runner._bridge_inspired_expert_decision_system_prompt()

        self.assertIn("Bridge-inspired", prompt)
        self.assertIn("student_error_or_gap", prompt)
        self.assertIn("remediation_strategy", prompt)
        self.assertIn("teaching_intention", prompt)
        self.assertIn("student_visible_response", prompt)
        self.assertIn("not a CP-specific Bridge Contract", prompt)
        self.assertIn("no formula-like decomposition", prompt)
        self.assertIn("do not mention parent/neighbor of LCA", prompt)

    def test_socratic_no_answer_prompt_has_solution_withholding_constraints(self):
        prompt = runner._socratic_no_answer_system_prompt()

        self.assertIn("Socratic", prompt)
        self.assertIn("no-answer", prompt)
        self.assertIn("one question", prompt)
        self.assertIn("do not state the missing bridge", prompt)
        self.assertIn("no formula-like decomposition", prompt)
        self.assertIn("do not mention parent/neighbor of LCA", prompt)
        self.assertIn("do not ask for exact operations on u/v/LCA", prompt)
        self.assertIn("do not pre-fill endpoint marks", prompt)
        self.assertIn("do not mention +1/-1", prompt)

    def test_validate_codehelp_codeaid_payload(self):
        payload = runner._validate_codehelp_codeaid_payload(
            {
                "baseline_group": "literature_inspired_guardrail",
                "student_visible_response": "先不要急着写完整 check。你可以先拿一个 mid，判断它是否满足题目限制，再说你希望 true 代表哪一边。",
                "self_check": {
                    "reveals_full_solution": False,
                    "reveals_full_code": False,
                    "reveals_critical_bridge": False,
                },
            }
        )

        self.assertEqual("literature_inspired_guardrail", payload["baseline_group"])
        self.assertIn("check", payload["student_visible_response"])
        self.assertFalse(payload["self_check"]["reveals_full_code"])

    def test_validate_bridge_inspired_payload(self):
        payload = runner._validate_bridge_inspired_expert_decision_payload(
            {
                "baseline_group": "literature_inspired_expert_decision",
                "student_error_or_gap": "学生混淆了 check(mid) 的布尔语义。",
                "remediation_strategy": "让学生用一个具体 mid 判断可行性，再自己定义 true 的方向。",
                "teaching_intention": "保留边界更新规则，让学生先建立谓词语义。",
                "student_visible_response": "你先别急着定边界。拿一个很小的 mid，问自己：这个 mid 满足限制吗？如果满足，你希望 check 返回什么？",
            }
        )

        self.assertEqual("literature_inspired_expert_decision", payload["baseline_group"])
        self.assertIn("布尔语义", payload["student_error_or_gap"])
        self.assertIn("一个很小的 mid", payload["student_visible_response"])

    def test_validate_socratic_no_answer_payload(self):
        payload = runner._validate_socratic_no_answer_payload(
            {
                "baseline_group": "literature_inspired_socratic",
                "question_intent": "让学生先定义 check 的语义，而不是直接给边界规则。",
                "student_visible_response": "先只回答一个问题：给定 mid 时，你想让 check 表达“满足限制”还是“不满足限制”？",
            }
        )

        self.assertEqual("literature_inspired_socratic", payload["baseline_group"])
        self.assertIn("check", payload["student_visible_response"])

    def test_runner_supports_codehelp_codeaid_tutor_without_bridge_diagnosis(self):
        rows = self._run_with_fake_chat(
            tutor_mode="codehelp_codeaid_no_direct_solution_tutor",
            payload={
                "baseline_group": "literature_inspired_guardrail",
                "student_visible_response": "我先不直接给 check 的真假方向。你先选一个 mid，判断它是否满足限制，再说你希望 true 表示“可行”还是“不可行”。",
                "self_check": {
                    "reveals_full_solution": False,
                    "reveals_full_code": False,
                    "reveals_critical_bridge": False,
                },
            },
        )

        self.assertEqual("codehelp_codeaid_no_direct_solution_tutor", rows[0]["tutor_mode"])
        self.assertEqual("literature_inspired_guardrail", rows[0]["baseline_group"])
        self.assertEqual("literature_inspired_guardrail", rows[0]["tutor_response"]["baseline_group"])
        self.assertIn("check", rows[0]["final_response_text"])
        self.assertEqual(1, rows[0]["llm_call_count"])
        self.assertEqual({}, rows[0].get("bridge_judge_result", {}))

    def test_runner_supports_socratic_no_answer_tutor_without_bridge_diagnosis(self):
        rows = self._run_with_fake_chat(
            tutor_mode="socratic_no_answer_tutor",
            payload={
                "baseline_group": "literature_inspired_socratic",
                "question_intent": "用一个问题让学生表达谓词含义。",
                "student_visible_response": "先回答一个小问题：你希望 check(mid) 这句话描述的是哪种可行性？",
            },
        )

        self.assertEqual("socratic_no_answer_tutor", rows[0]["tutor_mode"])
        self.assertEqual("literature_inspired_socratic", rows[0]["baseline_group"])
        self.assertIn("question_intent", rows[0]["socratic_no_answer_result"])
        self.assertEqual(1, rows[0]["llm_call_count"])

    def test_runner_supports_bridge_inspired_expert_decision_tutor_without_bridge_diagnosis(self):
        rows = self._run_with_fake_chat(
            tutor_mode="bridge_inspired_expert_decision_tutor",
            payload={
                "baseline_group": "literature_inspired_expert_decision",
                "student_error_or_gap": "学生不知道如何稳定定义 check 的真假语义。",
                "remediation_strategy": "先用一个具体 mid 做可行性判断，再让学生选择 true 的含义。",
                "teaching_intention": "不直接给边界更新，只校准谓词语义。",
                "student_visible_response": "你可以先把问题拆成一句判断：给定 mid 时，这个答案是否满足限制？先写出你希望 check 表达的这句话。",
            },
        )

        self.assertEqual("bridge_inspired_expert_decision_tutor", rows[0]["tutor_mode"])
        self.assertEqual("literature_inspired_expert_decision", rows[0]["baseline_group"])
        self.assertIn("student_error_or_gap", rows[0]["expert_decision_result"])
        self.assertIn("给定 mid", rows[0]["final_response_text"])
        self.assertEqual(1, rows[0]["llm_call_count"])

    def _run_with_fake_chat(self, *, tutor_mode, payload):
        def bridge_judge_should_not_run(**kwargs):
            raise AssertionError(f"{tutor_mode} standalone should not require Bridge Judge")

        def fake_chat_completion_create(*, system_prompt, messages, provider_id=None):
            return _FakeChatResponse(json.dumps(payload, ensure_ascii=False))

        original_chat = runner._chat_completion_create
        runner._chat_completion_create = fake_chat_completion_create
        try:
            return runner.run_bridge_offline_eval_rows(
                [_seed_row()],
                bridge_judge_fn=bridge_judge_should_not_run,
                chat_model_provider="deepseek",
                tutor_mode=tutor_mode,
                pipeline_mode="tutor_only_no_diagnosis",
                judge_provider="deepseek",
                max_retries=0,
                focus_registry=[],
                focus_registry_path=None,
            )
        finally:
            runner._chat_completion_create = original_chat


if __name__ == "__main__":
    unittest.main()
