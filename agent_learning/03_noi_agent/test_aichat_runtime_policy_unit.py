import unittest
from types import SimpleNamespace
from unittest.mock import patch

from noi_agent import (
    analyze_student_turn,
    build_pedagogical_judge_prompt,
    build_policy_override_reply,
    _extract_json_from_response,
    _validate_judge_schema,
    enforce_output_guards,
    chat_temperature_for_model,
    chat,
    build_system_prompt,
    enforce_level_gate,
    evaluate_understanding_evidence,
    evaluate_learning_phase,
)


class AIChatRuntimePolicyTests(unittest.TestCase):
    banned_generic_templates = [
        "这几个问题先别一起拆",
        "概念含义、代码怎么写，还是查询怎么合并",
        "我们先不用急着选算法",
        "手算一个很小的样例",
    ]

    def _messages(self, content, prior=None):
        return (prior or []) + [{"role": "user", "content": content}]

    def assertNoGenericTemplate(self, text):
        for phrase in self.banned_generic_templates:
            self.assertNotIn(phrase, text or "")

    def test_kimi_k26_should_use_official_required_temperature(self):
        self.assertEqual(1, chat_temperature_for_model("kimi-k2.6"))
        self.assertEqual(1, chat_temperature_for_model("kimi-k2.5"))
        self.assertEqual(0.3, chat_temperature_for_model("deepseek-chat"))

    def test_extract_json_from_response_should_strip_markdown_fence(self):
        parsed = _extract_json_from_response(
            '```json\n{"primary_intent": "learning", "student_intents": ["learning"]}\n```'
        )

        self.assertEqual("learning", parsed["primary_intent"])
        self.assertEqual(["learning"], parsed["student_intents"])

    def test_validate_judge_schema_should_require_primary_intent_first(self):
        valid = {
            "student_intents": ["learning", "code_debugging"],
            "primary_intent": "learning",
            "phase": "application_gap",
            "action_category": "scaffolding",
            "action_subtype": "build_application_bridge",
            "allowed_help_level": "L2",
            "confidence": 0.8,
            "injection_detected": False,
            "injection_source": "none",
            "reason": "知道算法不会落题",
        }

        self.assertEqual(valid, _validate_judge_schema(valid))

        invalid = dict(valid)
        invalid["primary_intent"] = "code_debugging"
        with self.assertRaisesRegex(ValueError, "primary_intent"):
            _validate_judge_schema(invalid)

    def test_validate_judge_schema_should_reject_invalid_enum(self):
        payload = {
            "student_intents": ["learning"],
            "primary_intent": "learning",
            "phase": "application_gap",
            "action_category": "scaffolding",
            "action_subtype": "ask_debug_evidence",
            "allowed_help_level": "L2",
            "confidence": 0.8,
            "injection_detected": False,
            "injection_source": "none",
            "reason": "枚举不匹配",
        }

        with self.assertRaisesRegex(ValueError, "action_subtype"):
            _validate_judge_schema(payload)

    def test_ac_reflection_should_force_checkin_handoff(self):
        messages = self._messages("我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)
        guarded_reply, guard = enforce_output_guards(
            reply.replace("\n\n[LEVEL:L2]", ""),
            control["level_control"],
            control["risk_control"],
            messages=messages,
        )

        self.assertEqual("offer_checkin_reflection", control["tutor_control"]["tutor_action"])
        self.assertIn("打卡复盘", reply)
        self.assertIsNone(guard)
        self.assertIn("打卡复盘", guarded_reply)
        self.assertIn("[LEVEL:L2]", reply)

    def test_ac_signal_alone_should_not_force_checkin_handoff(self):
        messages = self._messages("我 P3128 AC 了。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertNotEqual("offer_checkin_reflection", control["tutor_control"]["tutor_action"])
        self.assertNotIn("checkin_handoff", control["risk_control"]["risk_tags"])

    def test_uncertainty_signal_alone_should_not_force_checkin_handoff(self):
        messages = self._messages("我感觉这题是蒙的，想复盘一下。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertNotEqual("offer_checkin_reflection", control["tutor_control"]["tutor_action"])
        self.assertNotIn("checkin_handoff", control["risk_control"]["risk_tags"])

    def test_ac_unclear_should_build_fixed_handoff_payload(self):
        from noi_agent import build_policy_handoff_payload

        messages = self._messages("我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        payload = build_policy_handoff_payload(control, messages)

        self.assertEqual(
            {
                "handoff_type": "checkin_reflection",
                "source": "aichat",
                "risk_type": "ac_unclear_in_aichat",
                "problem_ref": "P3128",
                "last_user_message": "我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。",
                "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。",
            },
            payload,
        )

    def test_stage_four_stuck_should_force_checkin_exit(self):
        prior = [
            {"role": "user", "content": "我不知道 check(mid) true 后怎么缩。"},
            {"role": "assistant", "content": "先只看 mid 的含义：它是在猜哪个量？"},
            {"role": "user", "content": "猜最小距离。"},
            {"role": "assistant", "content": "那 check(mid) 要判断的是能不能让所有跳跃距离至少是多少？"},
            {"role": "user", "content": "我还是混。"},
        ]
        messages = self._messages("我还是说不清 check(mid) 到底检查什么。", prior)
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertEqual(4, control["tutor_control"]["scaffold_stage"])
        self.assertEqual("offer_micro_example_or_checkin", control["tutor_control"]["tutor_action"])
        self.assertIn("打卡复盘", reply)

    def test_repeated_stuck_signals_should_force_stage_four_even_with_short_history(self):
        from noi_agent import build_policy_handoff_payload

        prior = [
            {"role": "user", "content": "我还是不会判断 check(mid)。"},
            {"role": "assistant", "content": "先看 mid 表示什么。"},
            {"role": "user", "content": "我还是说不清。"},
        ]
        messages = self._messages("我想不明白这里。", prior)
        control = analyze_student_turn(messages[-1]["content"], messages)

        payload = build_policy_handoff_payload(control, messages)

        self.assertEqual(4, control["tutor_control"]["scaffold_stage"])
        self.assertEqual("offer_micro_example_or_checkin", control["tutor_control"]["tutor_action"])
        self.assertEqual("repeated_stuck_exit", payload["risk_type"])
        self.assertEqual("用小例子拆开当前卡住的桥，记录卡点和已尝试路径。", payload["suggested_focus"])

    def test_repeated_stuck_reply_should_not_use_ab_bridge_question(self):
        prior = [
            {"role": "user", "content": "我还是不会判断 check(mid)。"},
            {"role": "assistant", "content": "先看 mid 表示什么。"},
            {"role": "user", "content": "我还是说不清。"},
        ]
        messages = self._messages("我想不明白这里。", prior)
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertIn("打卡复盘", reply)
        self.assertNotIn("check(mid)", reply)
        self.assertNotIn("它是在统计", reply)
        self.assertNotIn("还是在找", reply)

    def test_progress_answer_should_not_be_forced_to_checkin_at_stage_four(self):
        prior = [
            {"role": "user", "content": "为什么不对"},
            {"role": "assistant", "content": "先手算 4 个点、分成 2 个部落的样例。"},
            {"role": "user", "content": "我感觉我的代码思路没有问题，但是输出不对，为什么"},
            {"role": "assistant", "content": "一开始每个点代表什么？"},
            {"role": "user", "content": "单独的部落"},
            {"role": "assistant", "content": "你每次从边数组里取边合并，是按什么顺序？合并一次后部落数怎么变？"},
        ]
        messages = self._messages("从距离小到大，每合并一次，部落总数 - 1", prior)

        control = analyze_student_turn(messages[-1]["content"], messages)
        reply = build_policy_override_reply(control, messages)

        self.assertEqual(4, control["tutor_control"]["scaffold_stage"])
        self.assertNotEqual("offer_micro_example_or_checkin", control["tutor_control"]["tutor_action"])
        self.assertIsNone(reply)

    def test_two_question_turns_plus_progress_should_force_micro_scaffold(self):
        prior = [
            {"role": "user", "content": "为什么我的思路完全没有问题，但是输出不对"},
            {"role": "assistant", "content": "你先描述一下样例 1 会先做什么？"},
            {"role": "user", "content": "找到距离最近的两个部落划分为一个部落"},
            {"role": "assistant", "content": "这里两个部落是已经分好的部落，还是某两个居住点？"},
            {"role": "user", "content": "是已经分好的两个部落"},
            {"role": "assistant", "content": "栈里压入的是同一个部落内部的边，还是两个不同部落之间的候选边？"},
        ]
        messages = self._messages("是已经连在同一个部落内部的边", prior)

        control = analyze_student_turn(messages[-1]["content"], messages)
        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="P4047")

        self.assertEqual("give_micro_scaffold", control["tutor_control"]["tutor_action"])
        self.assertIn("连续追问保护", prompt)
        self.assertIn("先给半步支架", prompt)
        self.assertIn("不能继续只反问", prompt)
        self.assertIn("先收拢一句", prompt)
        self.assertIn("一个小验证", prompt)

    def test_tree_core_dialogue_should_summarize_after_long_reasoning_chain(self):
        prior = [
            {"role": "user", "content": "这道题我知道用树的直径，但怎么用？"},
            {"role": "assistant", "content": "你打算用直径的端点来帮我们选核心城市，还是觉得直径的中间部分更有用？"},
            {"role": "user", "content": "我觉得是中间部分吧，因为如果是两端的话，那另外一端到当前这端岂不是更远了？中间的话到两边的非核心城市距离应该还好"},
            {"role": "assistant", "content": "如果 k=1，也就是只选一个核心城市，你会选在直径的哪个位置？"},
            {"role": "user", "content": "最中间的位置"},
            {"role": "assistant", "content": "现在 k 变成 2，在这条链上你会选哪两个位置？"},
            {"role": "user", "content": "还是最中间的两个点吧"},
            {"role": "assistant", "content": "如果这棵树在直径中间的某个城市上挂了一条很长的分支，会不会更远？"},
            {"role": "user", "content": "会"},
            {"role": "assistant", "content": "如果拥堵度上限设为 1，样例里哪些城市必须被覆盖到？"},
            {"role": "user", "content": "6 号城市、3 号城市、4 号城市"},
            {"role": "assistant", "content": "如果覆盖距离超过 D，你会怎么确定下一个核心城市？"},
            {"role": "user", "content": "我们选直径上与当前最远的非核心城市距离恰好为 D 的那个节点作为核心城市？"},
            {"role": "assistant", "content": "选出来的点能不能自己连成一片？"},
            {"role": "user", "content": "好像不能，那我在当前的核心城市中，找到与当前直径中与核心城市相连，并且离最远的叶子节点最近的节点作为新的核心城市"},
            {"role": "assistant", "content": "起点选在哪里？"},
            {"role": "user", "content": "从最中间的点开始选"},
            {"role": "assistant", "content": "最需要持续关注树上每个城市的什么信息？"},
            {"role": "user", "content": "应该是他到最近的已选核心城市的距离"},
        ]
        messages = self._messages(
            "我找的最远节点是 6、3、4，往回走一步会选在 2、1、5。能找到，并且满足条件是连通的",
            prior,
        )

        phase = evaluate_learning_phase(messages, has_problem_context=True, has_student_code=False)
        control = analyze_student_turn(messages[-1]["content"], messages)
        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="tree-core")

        self.assertEqual("strategy_forming", phase["phase"])
        self.assertEqual("summarize_and_scaffold", phase["recommended_action"])
        self.assertEqual(0, phase["question_budget"])
        self.assertFalse(phase["can_show_verification"])
        self.assertEqual("give_micro_scaffold", control["tutor_control"]["tutor_action"])
        self.assertIn("学生已经提出完整假设", prompt)
        self.assertIn("必须先收拢成 2-3 条草案", prompt)
        self.assertIn("不要继续用新样例追问", prompt)

    def test_tree_core_early_intuition_should_not_show_verification(self):
        messages = self._messages("我觉得是中间部分吧，因为如果是两端的话，那另外一端到当前这端岂不是更远了？中间的话到两边的非核心城市距离应该还好")

        phase = evaluate_learning_phase(messages, has_problem_context=True, has_student_code=False)
        evidence = evaluate_understanding_evidence(messages)

        self.assertEqual("strategy_forming", phase["phase"])
        self.assertFalse(phase["can_show_verification"])
        self.assertEqual("not_ready", evidence["understanding_state"])

    def test_tree_core_scaffolded_long_dialogue_should_still_summarize(self):
        prior = [
            {"role": "user", "content": "这道题我知道用树的直径，但怎么用？"},
            {"role": "assistant", "content": "你提到了树的直径。你觉得直径的端点更有用，还是中间部分更有用？"},
            {"role": "user", "content": "我觉得是中间部分吧，因为如果是两端的话，那另外一端到当前这端岂不是更远了？"},
            {"role": "assistant", "content": "你的直觉很对。那 k=1 时会选在直径哪里？"},
            {"role": "user", "content": "最中间的位置"},
            {"role": "assistant", "content": "嗯。k=2 时在链上会选哪两个位置？"},
            {"role": "user", "content": "还是最中间的两个点吧"},
            {"role": "assistant", "content": "对，但如果中间挂了长分支，会不会更远？"},
            {"role": "user", "content": "会"},
            {"role": "assistant", "content": "如果拥堵度上限是 D，哪些点必须被覆盖到？"},
            {"role": "user", "content": "6 号城市、3 号城市、4 号城市"},
            {"role": "assistant", "content": "你举出的 3、4、6 正好是远叶子。超过 D 时你会怎么选核心城市？"},
            {"role": "user", "content": "我们选直径上与当前最远的非核心城市距离恰好为 D 的那个节点作为核心城市？"},
            {"role": "assistant", "content": "方向有道理，不过还要满足核心城市连通。"},
            {"role": "user", "content": "往回走两步，如果走 3 步，为了保持连通性，就需要多放一个核心城市。那我觉得这道题应该是用二分答案，我们可以二分距离，check 条件就是当前的距离下，我们的核心城市的多少。距离越小，核心城市越多，距离越大，核心城市越小。"},
            {"role": "assistant", "content": "你抓住了几个很准的点：二分答案找最小拥堵度，check 里关心最远叶子和往回走 D 步。我们用样例试 D=1。"},
        ]
        messages = self._messages(
            "我找的最远节点是 6、3、4，往回走一步会选在 2、1、5。能找到，并且满足条件是连通的",
            prior,
        )

        phase = evaluate_learning_phase(messages, has_problem_context=True, has_student_code=False)

        self.assertEqual("summarize_and_scaffold", phase["recommended_action"])
        self.assertEqual(0, phase["question_budget"])
        self.assertFalse(phase["can_show_verification"])

    def test_pedagogical_judge_prompt_uses_transferable_rubric_not_algorithm_wordlist(self):
        prompt = build_pedagogical_judge_prompt(
            self._messages("我先把限制反过来试一个答案，再看这个答案够不够。"),
            has_problem_context=True,
            has_student_code=False,
        )

        self.assertIn("对象", prompt)
        self.assertIn("操作", prompt)
        self.assertIn("关系", prompt)
        self.assertIn("只输出 JSON", prompt)
        self.assertIn("不要按算法名或关键词是否出现来判断", prompt)
        self.assertNotIn("必须出现二分", prompt)
        self.assertNotIn("必须出现树的直径", prompt)

    def test_application_gap_should_use_bridge_scaffold_not_more_questions(self):
        prior = [{"role": "user", "content": "[当前上下文状态与回答策略]\n上下文状态：有题目 + 无代码"}]
        messages = self._messages("这道题我知道用树的直径，但怎么用？", prior)

        phase = evaluate_learning_phase(messages, has_problem_context=True, has_student_code=False)
        control = analyze_student_turn(messages[-1]["content"], messages)
        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="tree-core")

        self.assertEqual("strategy_forming", phase["phase"])
        self.assertEqual("build_application_bridge", phase["recommended_action"])
        self.assertEqual(0, phase["question_budget"])
        self.assertEqual("give_micro_scaffold", control["tutor_control"]["tutor_action"])
        self.assertIn("例子起步", prompt)
        self.assertIn("严谨收束", prompt)
        self.assertIn("3-5 个对象的小样例", prompt)
        self.assertIn("严谨一点说", prompt)
        self.assertIn("回到原题", prompt)
        self.assertIn("不要继续纯反问", prompt)

    def test_system_prompt_should_be_slim_and_not_expose_legacy_policy_blocks(self):
        prior = [{"role": "user", "content": "[当前上下文状态与回答策略]\n上下文状态：有题目 + 无代码"}]
        messages = self._messages("这道题我知道用树的直径，但怎么用？", prior)

        control = analyze_student_turn(messages[-1]["content"], messages)
        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="tree-core")

        self.assertLess(len(prompt), 2400)
        self.assertIn("做题陪跑教练", prompt)
        self.assertIn("例子起步", prompt)
        self.assertIn("严谨收束", prompt)
        self.assertIn("红线", prompt)
        self.assertNotIn("SOCRATIC_POLICY", prompt)
        self.assertNotIn("双轨控制指令", prompt)
        self.assertNotIn("L2 槽位状态", prompt)
        self.assertNotIn("本题提示状态", prompt)
        self.assertNotIn("提示次数", prompt)
        self.assertNotIn("配额", prompt)
        self.assertNotIn("不消耗配额", prompt)
        self.assertNotIn("消耗配额", prompt)

    def test_pedagogical_judge_prompt_should_stay_short_and_machine_readable(self):
        prompt = build_pedagogical_judge_prompt(
            self._messages("我知道要用二分，但不知道 check 里到底判断什么。"),
            has_problem_context=True,
            has_student_code=False,
        )

        self.assertLess(len(prompt), 1500)
        self.assertIn("只输出 JSON", prompt)
        self.assertIn("student_state", prompt)
        self.assertIn("next_action", prompt)
        self.assertIn("不要按算法名", prompt)
        self.assertNotIn("可选 student_state", prompt)
        self.assertNotIn("可选 next_action", prompt)

    def test_pedagogical_judge_prompt_can_choose_application_bridge(self):
        prompt = build_pedagogical_judge_prompt(
            self._messages("我听过强连通分量，但不知道这题为什么要缩点。"),
            has_problem_context=True,
            has_student_code=False,
        )

        self.assertIn("application_gap", prompt)
        self.assertIn("build_application_bridge", prompt)
        self.assertIn("听过", prompt)
        self.assertIn("不知道怎么落到当前题", prompt)

    def test_pedagogical_judge_prompt_should_stop_after_core_strategy_or_condition(self):
        prompt = build_pedagogical_judge_prompt(
            [
                {"role": "user", "content": "这题应该是用 dijkstra 吧，但是怎么用呢？"},
                {"role": "assistant", "content": "比较一下逐步 Floyd 和每次 Dijkstra 的复杂度。"},
                {"role": "user", "content": "哦！那我知道了，应该是 floyd 更好"},
            ],
            has_problem_context=True,
            has_student_code=False,
        )

        self.assertIn("学生已经说出正确算法", prompt)
        self.assertIn("核心判断", prompt)
        self.assertIn("summarize_and_scaffold", prompt)
        self.assertIn("不要继续追问", prompt)

    def test_llm_pedagogical_judgement_summarizes_without_algorithm_keywords(self):
        messages = self._messages(
            "我先把限制反过来试一个答案，再看这个答案够不够；如果够，就说明答案还能更小，不够就放大。"
        )
        judgement = {
            "student_state": "forming_strategy",
            "next_action": "summarize_and_scaffold",
            "question_budget": 0,
            "can_show_verification": False,
            "code_help_level": "pseudocode_skeleton",
            "evidence": "学生能说明反过来试答案以及够/不够时的调整方向。",
        }

        phase = evaluate_learning_phase(
            messages,
            has_problem_context=True,
            has_student_code=False,
            pedagogical_judgement=judgement,
        )

        self.assertEqual("strategy_forming", phase["phase"])
        self.assertEqual("summarize_and_scaffold", phase["recommended_action"])
        self.assertEqual(0, phase["question_budget"])
        self.assertEqual("llm_rubric", phase["source"])

    def test_chat_uses_llm_pedagogical_judge_to_control_prompt(self):
        messages = self._messages("我先把限制反过来试一个答案，再看这个答案够不够。")
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="我先把你的思路收一下：你已经在做答案可行性判断了。下一步把“够”和“不够”的调整方向写清楚。\n\n[LEVEL:L2]"))]
        )

        with patch(
            "noi_agent.judge_learning_phase_with_llm",
            return_value={
                "student_state": "forming_strategy",
                "next_action": "summarize_and_scaffold",
                "question_budget": 0,
                "can_show_verification": False,
                "code_help_level": "pseudocode_skeleton",
                "evidence": "学生已经提出可执行策略。",
            },
        ) as judge, patch("noi_agent._chat_completion_create", return_value=fake_response) as completion:
            chat(messages, "s1", "generic-problem", "mimo")

        judge.assert_called_once()
        sent_prompt = completion.call_args.kwargs["system_prompt"]
        self.assertIn("recommended_action=summarize_and_scaffold", sent_prompt)
        self.assertIn("question_budget=0", sent_prompt)

    def test_type_confirm_should_override_llm_application_bridge_prompt(self):
        messages = self._messages("这题是不是树剖 LCA 加差分？")
        judgement = {
            "student_state": "application_gap",
            "next_action": "build_application_bridge",
            "question_budget": 0,
            "can_show_verification": False,
        }

        control = analyze_student_turn(messages[-1]["content"], messages, pedagogical_judgement=judgement)
        prompt = build_system_prompt(control, remaining=0, student_id="s1", problem_id="P3128")

        self.assertEqual("ask_evidence_question", control["tutor_control"]["tutor_action"])
        self.assertIn("type_confirm 特殊约束", prompt)
        self.assertNotIn("recommended_action=build_application_bridge", prompt)
        self.assertNotIn("使用应用桥支架", prompt)
        self.assertIn("recommended_action=ask_grounding_question", prompt)

    def test_type_confirm_output_should_not_be_keyword_rewritten(self):
        reply, guard = enforce_output_guards(
            "你刚才已经说出了关键关系：一条路径会影响路径上的点。对，这已经接近树上差分的核心，但我们先只把“哪些点被影响”说清楚。\n\n[LEVEL:L2]",
            {"bridge_redline": False},
            {"risk_tags": ["type_confirm"]},
            messages=self._messages(
                "[学生原始问题]\n这题是不是树剖 LCA 加差分？\n\n[当前题目上下文]\n题面：给一棵树和多条路径，问所有路径经过次数最多的点。"
            ),
        )

        self.assertIsNone(guard)
        self.assertIn("树上差分", reply)
        self.assertIn("关键关系", reply)

    def test_type_confirm_reply_should_not_be_backend_rewritten(self):
        reply, guard = enforce_output_guards(
            "你注意到了 LCA 和差分。题面里哪句话让你想到路径上的点会被重复经过？\n\n[LEVEL:L2]",
            {"bridge_redline": False},
            {
                "risk_tags": ["type_confirm"],
                "learning_phase": {
                    "recommended_action": "build_application_bridge",
                    "question_budget": 0,
                },
            },
            messages=self._messages(
                "[学生原始问题]\n这题是不是树剖 LCA 加差分？\n\n[当前题目上下文]\n题面：给一棵树和多条路径，问所有路径经过次数最多的点。"
            ),
        )

        self.assertIsNone(guard)
        self.assertIn("题面里哪句话", reply)
        self.assertNotIn("应用桥", reply)

    def test_chat_main_path_should_not_read_hint_quota(self):
        messages = self._messages("我先把限制反过来试一个答案，再看这个答案够不够。")
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="你已经在做可行性判断了。下一步只要说清楚什么情况缩小答案，什么情况放大答案。\n\n[LEVEL:L2]"))]
        )

        with (
            patch("noi_agent.get_remaining_quota", side_effect=AssertionError("AIChat 主链不应读取旧配额")),
            patch(
                "noi_agent.judge_learning_phase_with_llm",
                return_value={
                    "student_state": "forming_strategy",
                    "next_action": "summarize_and_scaffold",
                    "question_budget": 0,
                    "can_show_verification": False,
                    "code_help_level": "none",
                },
            ),
            patch("noi_agent._chat_completion_create", return_value=fake_response),
        ):
            reply_for_display, reply_for_history, final_level = chat(messages, "s1", "generic-problem", "mimo")

        self.assertEqual("L2", final_level)
        self.assertEqual(reply_for_display, reply_for_history)

    def test_extract_student_original_input_strips_strategy_context(self):
        from noi_agent import _extract_student_original_input

        text = "\n".join([
            "[学生原始问题]",
            "我找的最远节点是 6、3、4。",
            "",
            "[当前上下文状态与回答策略]",
            "上下文状态：有题目 + 无代码",
            "",
            "[当前题目上下文：只用于理解学生卡点]",
            "题面...",
        ])

        self.assertEqual("我找的最远节点是 6、3、4。", _extract_student_original_input(text))

    def test_summarize_scaffold_question_is_left_to_llm_not_rewritten(self):
        messages = self._messages(
            "我找的最远节点是 6、3、4，往回走一步会选在 2、1、5。能找到，并且满足条件是连通的"
        )
        level_control = {"bridge_redline": False}
        risk_control = {
            "risk_tags": [],
            "highest_risk": None,
            "learning_phase": {
                "recommended_action": "summarize_and_scaffold",
                "question_budget": 0,
                "evidence": "学生已形成二分和往回走 D 步的策略草案。",
            },
        }

        reply, guard = enforce_output_guards(
            "你的二分和贪心方向对。但每次找最远叶子往回走 D 步选点，能保证所有核心城市自动连通吗？试画一棵链上带长分支的树，D=2,k=2，看你的方法会选在哪里。",
            level_control,
            risk_control,
            messages=messages,
        )

        self.assertIsNone(guard)
        self.assertIn("试画", reply)
        self.assertIn("？", reply)

    def test_summarize_scaffold_reply_should_not_be_backend_rewritten(self):
        reply, guard = enforce_output_guards(
            "你现在已经形成了一个策略草案：先二分 D，再找超过 D 的远叶子，沿路径往核心区域补点。需要补上的关键缺口是：补点后怎样统计为了保持核心城市连通而额外占用的路径节点。下一步先把 check(D) 写成“找超界点、补路径、统计核心块大小”三段。",
            {"bridge_redline": False},
            {
                "risk_tags": [],
                "highest_risk": None,
                "learning_phase": {
                    "recommended_action": "summarize_and_scaffold",
                    "question_budget": 0,
                },
            },
        )

        self.assertIsNone(guard)
        self.assertIn("策略草案", reply)

    def test_application_bridge_reply_is_left_to_llm_not_rewritten(self):
        messages = self._messages("这道题我知道用树的直径，但怎么用？")

        reply, guard = enforce_output_guards(
            "你觉得直径的端点更有用，还是直径的中间部分更有用？",
            {"bridge_redline": False},
            {
                "risk_tags": [],
                "highest_risk": None,
                "learning_phase": {
                    "recommended_action": "build_application_bridge",
                    "question_budget": 0,
                    "evidence": "学生知道树的直径，但不知道怎样落到当前题。",
                },
            },
            messages=messages,
        )

        self.assertIsNone(guard)
        self.assertIn("你觉得直径的端点更有用", reply)

    def test_output_guard_is_noop_even_for_complete_solution_words(self):
        messages = self._messages("这道题我知道用树的直径，但怎么用？")

        reply, guard = enforce_output_guards(
            "完整做法是先找树的直径，然后直接二分答案并写 check。",
            {"bridge_redline": False},
            {
                "risk_tags": [],
                "highest_risk": None,
                "learning_phase": {
                    "recommended_action": "build_application_bridge",
                    "question_budget": 0,
                    "evidence": "学生知道树的直径，但不知道怎样落到当前题。",
                },
            },
            messages=messages,
        )

        self.assertIsNone(guard)
        self.assertEqual("完整做法是先找树的直径，然后直接二分答案并写 check。", reply)

    def test_example_check_reply_should_not_be_rewritten_to_generic_bridge(self):
        prior = [
            {"role": "user", "content": "请问这道题我可以怎么做？我没有太多思路"},
            {"role": "assistant", "content": "假设 n=4，排列是 [3,1,4,2]。从北向南和从南向北哪些位置可见？"},
            {"role": "user", "content": "从北到南只有3、4楼能看到，从南到北只有4楼能看到"},
            {"role": "assistant", "content": "为了避免混淆，我们用位置编号。请再标一次。"},
            {"role": "user", "content": "1.北到南位置1 3 2.南到北位置3"},
            {"role": "assistant", "content": "从南向北可见位置是 4、3。现在对照 a,b,c 判断这个排列是否满足。"},
        ]
        messages = self._messages("不满足，b数组中的南向北位置2、4不满足。c数组中位置2应该为1，而不是0", prior)

        reply, guard = enforce_output_guards(
            "你已经发现 b 数组要求和实际南向北可见位置对不上。这里先别换题：再确认一下，c_i=1 表示“这个位置两侧都看不见”，那位置 2 在这个排列里是否两侧都不可见？",
            {"bridge_redline": False},
            {
                "risk_tags": [],
                "highest_risk": None,
                "learning_phase": {
                    "recommended_action": "build_application_bridge",
                    "question_budget": 0,
                    "evidence": "学生正在核对小例子里的 a,b,c 可见性。",
                },
            },
            messages=messages,
        )

        self.assertIsNone(guard)
        self.assertIn("b 数组", reply)
        self.assertIn("c_i=1", reply)
        self.assertNotIn("这个知识点", reply)
        self.assertNotIn("哪个对象最容易把目标值撑大", reply)

    def test_system_prompt_should_lower_step_when_student_says_they_do_not_understand(self):
        messages = self._messages(
            "我还是不懂",
            [
                {"role": "user", "content": "这题为什么要二分？"},
                {"role": "assistant", "content": "你先看直接枚举要试多少个答案？"},
            ],
        )

        control = analyze_student_turn(messages[-1]["content"], messages)
        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="P1")

        self.assertIn("学生表达不懂", prompt)
        self.assertIn("不要继续问抽象问题", prompt)
        self.assertIn("缩小到一个可观察对象", prompt)
        self.assertIn("一个具体动作", prompt)
        self.assertIn("一个二选一判断", prompt)
        self.assertIn("一个极小例子", prompt)
        self.assertIn("不要写固定回复模板", prompt)

    def test_system_prompt_should_anchor_reply_to_latest_student_answer(self):
        messages = self._messages(
            "从距离小到大，每合并一次，部落总数 - 1",
            [
                {"role": "user", "content": "为什么输出不对？"},
                {"role": "assistant", "content": "每合并一次后部落数怎么变？"},
            ],
        )

        control = analyze_student_turn(messages[-1]["content"], messages)
        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="P4047")

        self.assertIn("学生上一轮给出了具体回答", prompt)
        self.assertIn("必须先回应他上一句里的具体内容", prompt)
        self.assertIn("哪一部分对", prompt)
        self.assertIn("哪一部分还缺", prompt)
        self.assertIn("不能无视学生回答直接换一个新问题", prompt)

    def test_understanding_evidence_marks_verifiable_but_not_mastered(self):
        messages = self._messages("从距离小到大排序边，每合并一次，部落总数减一；剩下 k 个连通块后，下一条连接不同连通块的边才是部落之间的距离。")

        result = evaluate_understanding_evidence(messages)

        self.assertEqual("evidence_seen", result["understanding_state"])
        self.assertFalse(result["mastery_verified"])
        self.assertIn("object", result["evidence_types"])
        self.assertIn("operation", result["evidence_types"])
        self.assertIn("relation", result["evidence_types"])

    def test_understanding_evidence_does_not_treat_shallow_claim_as_ready(self):
        messages = self._messages("懂了，会了，应该就是这样。")

        result = evaluate_understanding_evidence(messages)

        self.assertEqual("not_ready", result["understanding_state"])
        self.assertFalse(result["mastery_verified"])
        self.assertEqual([], result["evidence_types"])

    def test_problem_plus_code_should_use_code_diagnostic_scaffold(self):
        messages = self._messages(
            "\n".join(
                [
                    "[学生原始问题]",
                    "为什么我的思路没问题但是输出不对？",
                    "",
                    "[当前上下文状态与回答策略]",
                    "上下文状态：有题目 + 有代码",
                    "回答策略：必须结合题面目标、学生问题和学生代码；先对齐题目目标与代码实现，再定位一个最小可疑位置。",
                    "",
                    "[当前题目上下文：只用于理解学生卡点，不要直接照抄题解]",
                    "题目标题: P4047 部落划分",
                    "题面/题意/约束: 求 k 个部落划分后，最近两个部落之间距离的最大值。",
                    "学生当前代码: ```cpp\nsort(a.begin(), a.end(), cmp);\nfor(int i = 0; i < a.size(); i ++) aaaaa(i);\nprintf(\"%.2lf\", k.top());\n```",
                ]
            )
        )

        control = analyze_student_turn(messages[-1]["content"], messages)
        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="P4047")

        self.assertEqual("diagnose_code_with_problem", control["tutor_control"]["tutor_action"])
        self.assertIn("代码诊断模式", prompt)
        self.assertIn("代码实际行为", prompt)
        self.assertIn("题目目标", prompt)
        self.assertIn("最小可疑位置", prompt)
        self.assertIn("不要先问学生完整思路", prompt)

    def test_code_without_problem_context_should_request_problem_before_debugging_code(self):
        messages = self._messages(
            "\n".join(
                [
                    "[学生原始问题]",
                    "为什么不对？",
                    "",
                    "[当前上下文状态与回答策略]",
                    "上下文状态：无题目 + 有代码",
                    "回答策略：先说明现在只看到了代码，但不知道题目目标；请学生先补题目链接或题号。",
                    "",
                    "[当前题目上下文：只用于理解学生卡点，不要直接照抄题解]",
                    "学生当前代码: ```cpp\nint main(){ int n; cin >> n; cout << n; }\n```",
                ]
            )
        )

        control = analyze_student_turn(messages[-1]["content"], messages)
        reply = build_policy_override_reply(control, messages)

        self.assertEqual("request_problem_context", control["tutor_control"]["tutor_action"])
        self.assertIn("题目链接", reply)
        self.assertIn("题号", reply)
        self.assertNotIn("哪一行", reply)
        self.assertNotIn("样例", reply)

    def test_missing_context_should_ask_for_problem_ref_before_algorithm_slots(self):
        messages = self._messages("这题怎么想？")
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertIn("题号", reply)
        self.assertIn("题面", reply)
        self.assertNotIn("一组数字", reply)
        self.assertNotIn("一张图", reply)

    def test_multi_question_should_force_focus_choice(self):
        messages = self._messages("lazy 到底是什么？pushdown 怎么写？区间查询又怎么合并？")
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)
        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="P1")

        self.assertEqual("ask_one_focus_point", control["tutor_control"]["tutor_action"])
        self.assertIsNone(reply)
        self.assertIn("优先处理最影响继续推进的一点", prompt)
        self.assertNotIn("概念含义、代码怎么写，还是查询怎么合并", prompt)
        self.assertNotIn("这几个问题先别一起拆", prompt)

    def test_system_prompt_should_not_repeat_generic_small_sample_fallback(self):
        messages = self._messages("这题怎么做")
        control = analyze_student_turn(messages[-1]["content"], messages)

        prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="P1")
        reply = build_policy_override_reply(control, messages)

        self.assertNotIn("我们先不用急着选算法", prompt)
        self.assertNotIn("手算一个很小的样例", prompt)
        if reply:
            self.assertNotIn("我们先不用急着选算法", reply)
            self.assertNotIn("手算一个很小的样例", reply)

    def test_common_student_scenarios_should_not_surface_removed_generic_templates(self):
        scenarios = [
            self._messages("这题怎么做"),
            self._messages("lazy 到底是什么？pushdown 怎么写？区间查询又怎么合并？"),
            self._messages("这题是不是二分？为什么不能直接枚举？"),
            self._messages("我输出不对，但是不知道哪里错了"),
            self._messages("```cpp\nint main(){return 0;}\n```"),
            self._messages(
                "是已经连在同一个部落内部的边",
                [
                    {"role": "user", "content": "为什么我的思路完全没有问题，但是输出不对"},
                    {"role": "assistant", "content": "你用手算会怎么得到 1.00？"},
                    {"role": "user", "content": "找到距离最近的两个部落划分为一个部落"},
                    {"role": "assistant", "content": "这里两个部落是已经分好的部落，还是某两个居住点？"},
                    {"role": "user", "content": "是已经分好的两个部落"},
                    {"role": "assistant", "content": "栈里压入的是同一个部落内部的边，还是两个不同部落之间的候选边？"},
                ],
            ),
        ]

        for messages in scenarios:
            with self.subTest(latest=messages[-1]["content"][:40]):
                control = analyze_student_turn(messages[-1]["content"], messages)
                prompt = build_system_prompt(control, remaining=999, student_id="s1", problem_id="P1")
                reply = build_policy_override_reply(control, messages)

                self.assertNoGenericTemplate(prompt)
                self.assertNoGenericTemplate(reply)

    def test_level_gate_fallback_should_not_use_removed_small_sample_template(self):
        _level, reply = enforce_level_gate("L3", "L1", "直接给完整做法。\n\n[LEVEL:L3]")

        self.assertNoGenericTemplate(reply)
        self.assertIn("题号", reply)
        self.assertIn("[LEVEL:L1]", reply)

    def test_single_why_question_should_not_be_treated_as_multi_question(self):
        content = "\n".join(
            [
                "[学生原始问题]",
                "我贴的是 CF 题，为什么判断偶数还要排除 2？",
                "",
                "[当前题目上下文：只用于理解学生卡点，不要直接照抄题解]",
                "题面/题意/约束: 给定整数 w，判断能否拆成两个正偶数之和。",
            ]
        )
        messages = self._messages(content)
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertNotEqual("ask_one_focus_point", control["tutor_control"]["tutor_action"])
        self.assertIsNone(reply)

    def test_type_confirm_output_should_not_be_rewritten_by_complexity_keyword(self):
        messages = self._messages(
            "\n".join(
                [
                    "[学生原始问题]",
                    "n 和 m 都 50000，但长度只有 20，我双层枚举是不是也还行？",
                    "",
                    "[当前题目上下文：只用于理解学生卡点，不要直接照抄题解]",
                    "题面/题意/约束: 有大量消息串和拦截串，需要反复判断前缀关系，n 和 m 都 50000，长度只有 20。",
                ]
            )
        )

        reply, guard = enforce_output_guards(
            "双层一定不行。",
            {"bridge_redline": False},
            {"risk_tags": ["type_confirm"]},
            messages=messages,
        )

        self.assertIsNone(guard)
        self.assertEqual("双层一定不行。", reply)

    def test_code_without_target_should_ask_for_suspected_line_or_case(self):
        messages = self._messages("```cpp\nwhile(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }\n```")
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertEqual("ask_code_evidence", control["tutor_control"]["tutor_action"])
        self.assertIn("哪一行", reply)
        self.assertIn("样例", reply)

    def test_code_without_target_should_not_create_handoff_payload(self):
        from noi_agent import build_policy_handoff_payload

        messages = self._messages("```cpp\nwhile(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }\n```")
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertEqual("ask_code_evidence", control["tutor_control"]["tutor_action"])
        self.assertIsNone(build_policy_handoff_payload(control, messages))

    def test_code_without_target_should_remain_evidence_guard_at_stage_four(self):
        from noi_agent import build_policy_handoff_payload

        prior = [
            {"role": "user", "content": "这个二分我不懂。"},
            {"role": "assistant", "content": "先说你怀疑哪一步。"},
            {"role": "user", "content": "还是不懂。"},
        ]
        messages = self._messages(
            "```cpp\nwhile(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }\n```",
            prior,
        )
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertEqual(4, control["tutor_control"]["scaffold_stage"])
        self.assertEqual("ask_code_evidence", control["tutor_control"]["tutor_action"])
        self.assertIsNone(build_policy_handoff_payload(control, messages))

    def test_pasted_code_with_prior_failing_sample_should_not_be_code_no_target(self):
        prior = [
            {
                "role": "user",
                "content": "样例 x=3 时输出了第二个 3，但我预期是第一个 3。",
            }
        ]
        messages = self._messages(
            "```cpp\nwhile(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }\n```",
            prior,
        )
        control = analyze_student_turn(messages[-1]["content"], messages)

        self.assertNotIn("code_no_target", control["risk_control"]["risk_tags"])
        self.assertNotEqual("ask_code_evidence", control["tutor_control"]["tutor_action"])

    def test_wa_without_code_should_request_evidence_without_echoing_answer(self):
        messages = self._messages("我第 3 个样例输出是 15 但答案是 20，不知道哪里错了。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertEqual("ask_debug_evidence", control["tutor_control"]["tutor_action"])
        self.assertIn("代码", reply)
        self.assertIn("推导", reply)
        self.assertNotIn("答案是 20", reply)

    def test_bridge_attempt_output_should_not_be_keyword_rewritten(self):
        reply, guard = enforce_output_guards(
            "比较两种定义：dp[x][y] = 从(x,y)出发的最长路径。",
            {"bridge_redline": True},
            {"risk_tags": ["bridge_attempt"]},
            messages=self._messages("我不知道 dp[x][y] 这个状态到底该表示什么。"),
        )

        self.assertIsNone(guard)
        self.assertIn("dp[x][y] =", reply)


if __name__ == "__main__":
    unittest.main()
