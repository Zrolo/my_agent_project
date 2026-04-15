import unittest

from noi_agent import analyze_student_turn, build_policy_override_reply, enforce_output_guards


class AIChatRuntimePolicyTests(unittest.TestCase):
    def _messages(self, content, prior=None):
        return (prior or []) + [{"role": "user", "content": content}]

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
        self.assertNotIn("它是在统计", reply)
        self.assertNotIn("还是在找", reply)

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

        self.assertEqual("ask_one_focus_point", control["tutor_control"]["tutor_action"])
        self.assertIn("先聚焦", reply)
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
        self.assertIn("w=2", reply)
        self.assertIn("正偶数", reply)

    def test_type_confirm_guard_should_use_complexity_context_not_generic_why(self):
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

        self.assertEqual("type_confirm_guard", guard)
        self.assertIn("50000", reply)
        self.assertIn("20", reply)
        self.assertNotIn("为什么会这么猜", reply)

    def test_code_without_target_should_ask_for_suspected_line_or_case(self):
        messages = self._messages("```cpp\nwhile(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }\n```")
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertEqual("ask_code_evidence", control["tutor_control"]["tutor_action"])
        self.assertIn("哪一行", reply)
        self.assertIn("样例", reply)

    def test_wa_without_code_should_request_evidence_without_echoing_answer(self):
        messages = self._messages("我第 3 个样例输出是 15 但答案是 20，不知道哪里错了。")
        control = analyze_student_turn(messages[-1]["content"], messages)

        reply = build_policy_override_reply(control, messages)

        self.assertEqual("ask_debug_evidence", control["tutor_control"]["tutor_action"])
        self.assertIn("代码", reply)
        self.assertIn("推导", reply)
        self.assertNotIn("答案是 20", reply)

    def test_guard_should_replace_dp_state_definition_variants(self):
        reply, guard = enforce_output_guards(
            "比较两种定义：dp[x][y] = 从(x,y)出发的最长路径。",
            {"bridge_redline": True},
            {"risk_tags": ["bridge_attempt"]},
            messages=self._messages("我不知道 dp[x][y] 这个状态到底该表示什么。"),
        )

        self.assertEqual("bridge_guard", guard)
        self.assertNotIn("dp[x][y] =", reply)


if __name__ == "__main__":
    unittest.main()
