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
        "id": "cp_bridge_dbox_unit",
        "problem_ref": "segment_tree_lazy",
        "student_message": "线段树区间加我会写一点，但 lazy 到底表示还没做什么，我说不清。",
        "problem_context": "区间加和区间求和，需要线段树懒标记。",
        "gold_forbidden_completion": "不能直接给出 lazy 的完整语义。",
    }


def _bridge_result(**overrides):
    result = {
        "turn_type": "diagnosable_learning_turn",
        "missing_bridge": {
            "family": "representation_state_bridge",
            "subtype": "state.lazy_tag_semantics",
            "known_focus": "segment_tree.lazy_semantics",
            "description": "学生不知道 lazy 标记表示子节点尚未下推的增量。",
        },
        "allowed_help_level": "L2",
        "help_forms": ["guiding_question", "micro_example"],
        "forbidden_content": ["不能直接给出 lazy 的完整语义。"],
        "leakage_risk": "high",
        "confidence": 0.86,
    }
    result.update(overrides)
    return result


class DBoxInspiredDecompositionTutorTests(unittest.TestCase):
    def test_dbox_prompt_has_first_level_step_tree_constraints(self):
        prompt = runner._dbox_inspired_decomposition_system_prompt()

        self.assertIn("DBox-inspired", prompt)
        self.assertIn("step-tree-style", prompt)
        self.assertIn("only one current substep", prompt)
        self.assertIn("first-level", prompt)
        self.assertIn("general_hint", prompt)
        self.assertIn("detailed_hint", prompt)
        self.assertIn("correctStep", prompt)
        self.assertIn("correct_code", prompt)
        self.assertIn("no reveal substep", prompt)
        self.assertIn("no reveal code", prompt)
        self.assertIn("no direct critical bridge completion", prompt)

    def test_validate_dbox_payload_keeps_structured_decomposition_fields(self):
        payload = runner._validate_dbox_inspired_decomposition_payload(
            {
                "baseline_group": "literature_inspired_decomposition",
                "decomposition_view": [
                    {"step_id": "s1", "step_name": "确认题目动作", "status": "known_or_not_relevant"},
                    {"step_id": "s2", "step_name": "说清 lazy 当前代表的未下推信息", "status": "current_stuck_step"},
                    {"step_id": "s3", "step_name": "再考虑 pushdown 何时发生", "status": "defer"},
                ],
                "current_substep": "先判断一个区间节点被整体加值后，子节点是否已经同步更新。",
                "hint_level": "general_question",
                "student_visible_response": "先把问题缩小到一个节点：如果 [1,2] 整体加 5，它的两个叶子现在是否已经改了？你先选并说理由。",
            }
        )

        self.assertEqual("literature_inspired_decomposition", payload["baseline_group"])
        self.assertEqual("general_question", payload["hint_level"])
        self.assertEqual("current_stuck_step", payload["decomposition_view"][1]["status"])
        self.assertIn("一个节点", payload["student_visible_response"])

    def test_runner_supports_dbox_inspired_tutor_mode_and_emits_trace_fields(self):
        calls = []

        def fake_bridge_judge(**kwargs):
            return _bridge_result()

        def fake_chat_completion_create(*, system_prompt, messages, provider_id=None):
            calls.append(
                {
                    "system_prompt": system_prompt,
                    "messages": messages,
                    "provider_id": provider_id,
                }
            )
            return _FakeChatResponse(
                json.dumps(
                    {
                        "baseline_group": "literature_inspired_decomposition",
                        "decomposition_view": [
                            {
                                "step_id": "s1",
                                "step_name": "确定区间加会先落在哪个节点",
                                "status": "known_or_not_relevant",
                            },
                            {
                                "step_id": "s2",
                                "step_name": "判断当前节点打 lazy 后子节点是否已更新",
                                "status": "current_stuck_step",
                            },
                            {
                                "step_id": "s3",
                                "step_name": "之后再讨论 pushdown 触发时机",
                                "status": "defer",
                            },
                        ],
                        "current_substep": "判断父节点整体加值后，子节点是否已经同步修改。",
                        "hint_level": "general_question",
                        "student_visible_response": "先把大问题拆小：只看 [1,2] 这个节点被整体加 5 后，它的两个叶子此时是否已经被改？先选一个并说理由。",
                    },
                    ensure_ascii=False,
                )
            )

        original_chat = runner._chat_completion_create
        runner._chat_completion_create = fake_chat_completion_create
        try:
            rows = runner.run_bridge_offline_eval_rows(
                [_seed_row()],
                bridge_judge_fn=fake_bridge_judge,
                chat_model_provider="deepseek",
                tutor_mode="dbox_inspired_decomposition_tutor",
                pipeline_mode="tutor_only",
                judge_provider="deepseek",
                max_retries=0,
                focus_registry=[],
                focus_registry_path=None,
            )
        finally:
            runner._chat_completion_create = original_chat

        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual("dbox_inspired_decomposition_tutor", row["tutor_mode"])
        self.assertEqual("literature_inspired_decomposition", row["baseline_group"])
        self.assertEqual("literature_inspired_decomposition", row["tutor_response"]["baseline_group"])
        self.assertEqual("general_question", row["hint_level"])
        self.assertEqual("判断父节点整体加值后，子节点是否已经同步修改。", row["current_substep"])
        self.assertEqual("current_stuck_step", row["decomposition_view"][1]["status"])
        self.assertIn("只看 [1,2]", row["final_response_text"])
        self.assertEqual(2, row["llm_call_count"])
        self.assertEqual("deepseek", calls[0]["provider_id"])
        self.assertIn("no reveal code", calls[0]["system_prompt"])

    def test_dbox_standalone_can_run_without_bridge_diagnosis(self):
        def bridge_judge_should_not_run(**kwargs):
            raise AssertionError("standalone DBox-inspired baseline should not require Bridge Judge")

        def fake_chat_completion_create(*, system_prompt, messages, provider_id=None):
            return _FakeChatResponse(
                json.dumps(
                    {
                        "baseline_group": "literature_inspired_decomposition",
                        "decomposition_view": [
                            {"step_id": "s1", "step_name": "确认当前目标", "status": "known_or_not_relevant"},
                            {"step_id": "s2", "step_name": "拆出一个当前小问题", "status": "current_stuck_step"},
                            {"step_id": "s3", "step_name": "再回到完整实现", "status": "defer"},
                        ],
                        "current_substep": "先回答当前小问题。",
                        "hint_level": "general_question",
                        "student_visible_response": "先别看完整做法，把它拆成一个小问题：你觉得当前节点需要先判断什么？",
                    },
                    ensure_ascii=False,
                )
            )

        original_chat = runner._chat_completion_create
        runner._chat_completion_create = fake_chat_completion_create
        try:
            rows = runner.run_bridge_offline_eval_rows(
                [_seed_row()],
                bridge_judge_fn=bridge_judge_should_not_run,
                chat_model_provider="deepseek",
                tutor_mode="dbox_inspired_decomposition_tutor",
                pipeline_mode="tutor_only_no_diagnosis",
                judge_provider="deepseek",
                max_retries=0,
                focus_registry=[],
                focus_registry_path=None,
            )
        finally:
            runner._chat_completion_create = original_chat

        self.assertEqual(1, rows[0]["llm_call_count"])
        self.assertEqual({}, rows[0].get("bridge_judge_result", {}))
        self.assertEqual("candidate", rows[0]["final_response_source"])


if __name__ == "__main__":
    unittest.main()
