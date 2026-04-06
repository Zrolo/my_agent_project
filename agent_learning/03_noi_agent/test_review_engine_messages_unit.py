import unittest
from types import SimpleNamespace
from unittest.mock import patch

import review_engine


class ReviewEngineMessageSplitTests(unittest.TestCase):
    def test_detect_review_mode_prefers_failed_verdict_for_wa_with_spaces(self):
        mode = review_engine._detect_review_mode("unfinished", " WA ")
        self.assertEqual(mode, "failed_verdict")

    def test_detect_review_mode_maps_editorial_before_independent(self):
        mode = review_engine._detect_review_mode("editorial", "unknown")
        self.assertEqual(mode, "editorial_transfer")

    def test_detect_review_mode_maps_unfinished_to_stuck_bridge(self):
        mode = review_engine._detect_review_mode("unfinished", "not_submitted")
        self.assertEqual(mode, "stuck_bridge")

    def test_detect_review_mode_defaults_to_independent_reflect(self):
        mode = review_engine._detect_review_mode("independent", "unknown")
        self.assertEqual(mode, "independent_reflect")

    def test_family_for_review_mode_maps_failure_modes_to_failure_diagnosis(self):
        self.assertEqual("failure_diagnosis", review_engine._family_for_review_mode("failed_verdict"))
        self.assertEqual("failure_diagnosis", review_engine._family_for_review_mode("stuck_bridge"))
        self.assertEqual("failure_diagnosis", review_engine._family_for_review_mode("editorial_transfer"))

    def test_family_for_review_mode_maps_independent_reflect_to_success_reflection(self):
        self.assertEqual("success_reflection", review_engine._family_for_review_mode("independent_reflect"))

    def test_build_review_system_prompt_should_append_failed_verdict_supplement(self):
        prompt = review_engine._build_review_system_prompt("failed_verdict")
        self.assertIn("WA/TLE/RE/CE", prompt)
        self.assertIn("具体出错位置或逻辑", prompt)

    def test_build_review_system_prompt_should_append_stuck_bridge_supplement(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("学生卡住了", prompt)
        self.assertIn("不能只写\"不会建模\"", prompt)
        self.assertIn("不要在字段内容里使用半角双引号", prompt)

    def test_build_review_system_prompt_should_append_editorial_transfer_supplement(self):
        prompt = review_engine._build_review_system_prompt("editorial_transfer")
        self.assertIn("学生看了题解", prompt)
        self.assertIn("为什么这个方法能解决这道题", prompt)
        self.assertIn("这道题里的哪个动作对应算法里的哪个操作", prompt)
        self.assertIn("合并舰队指令", prompt)
        self.assertIn("查询间距", prompt)
        self.assertIn("不写练习题或类比", prompt)

    def test_build_review_system_prompt_should_append_independent_reflect_supplement(self):
        prompt = review_engine._build_review_system_prompt("independent_reflect")
        self.assertIn("学生独立完成", prompt)
        self.assertIn("不写变形和拓展", prompt)

    def test_build_review_system_prompt_should_not_emit_family_comments_to_model(self):
        prompt = review_engine._build_review_system_prompt("failed_verdict")
        self.assertNotIn("# family:", prompt)

    def test_build_review_system_prompt_should_require_problem_specific_language(self):
        prompt = review_engine._build_review_system_prompt("independent_reflect")
        self.assertIn("不要抽象成方法名或概念名", prompt)
        self.assertIn("优先复用题目里的对象名、条件名、公式名", prompt)
        self.assertIn("不要写专项训练、经典题、做3道", prompt)

    def test_build_review_system_prompt_should_require_stuck_bridge_to_name_specific_facts(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("点名一个对象、关系、条件或状态含义", prompt)
        self.assertIn("手画一次 / 逐条列出 / 手推一轮", prompt)
        self.assertIn("不要给题面特征加引号", prompt)
        self.assertIn("逐字摘出至少一个名词或条件", prompt)
        self.assertIn("不允许改写或概括", prompt)
        self.assertIn("再用这个原文词说明为什么这一步是关键", prompt)

    def test_build_review_system_prompt_should_keep_next_action_on_current_problem(self):
        prompt = review_engine._build_review_system_prompt("failed_verdict")
        self.assertIn("优先回到当前题", prompt)
        self.assertIn("不要写专项训练、经典题、做3道", prompt)

    def test_build_review_system_prompt_should_make_failed_verdict_main_block_more_specific(self):
        prompt = review_engine._build_review_system_prompt("failed_verdict")
        self.assertIn("点名具体判断条件、连接符、代码位置或输出位置", prompt)
        self.assertIn("不要只写“没想清楚”", prompt)
        self.assertIn("不要只写“组合判断语句”", prompt)
        self.assertIn("必须同时说明是代码里哪一处写错", prompt)
        self.assertIn("点名变量名、条件表达式、判断符号或代码位置中至少一个", prompt)

    def test_build_review_system_prompt_should_make_independent_signal_observable(self):
        prompt = review_engine._build_review_system_prompt("independent_reflect")
        self.assertIn("必须直接引用题目里出现的具体名词或数量关系", prompt)
        self.assertIn("不能写算法类型描述", prompt)
        self.assertIn("不能出现题目名或题目编号", prompt)
        self.assertIn("每个决策点可以选择做多少、后面还有更优选择", prompt)
        self.assertIn("棋盘上马从指定起点按日字走法到达每个格子", prompt)
        self.assertIn("每组最多两件且总重量不超过 w", prompt)

    def test_build_review_system_prompt_should_make_independent_main_block_name_decision_flow(self):
        prompt = review_engine._build_review_system_prompt("independent_reflect")
        self.assertIn("必须写清这道题的核心决策流程", prompt)
        self.assertIn("在当前油站决定加多少油", prompt)
        self.assertIn("从堆里弹出最小元素后更新相邻节点", prompt)
        self.assertIn("不能为空，也不能只写做出来了", prompt)

    def test_build_review_system_prompt_should_make_stuck_bridge_avoid_abstract_state_words(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("next_step 同样：必须点名题目里直接出现过的某个对象或条件", prompt)
        self.assertIn("不允许用\"某变量\"\"某限制\"\"进度\"等自造概念替代", prompt)

    def test_call_llm_should_stream_and_collect_chunks_for_kimi(self):
        captured = {}

        class FakeCompletions:
            def create(self, **kwargs):
                captured.update(kwargs)
                return iter(
                    [
                        SimpleNamespace(
                            choices=[SimpleNamespace(delta=SimpleNamespace(content="o"), finish_reason=None)],
                            usage=None,
                        ),
                        SimpleNamespace(
                            choices=[SimpleNamespace(delta=SimpleNamespace(content="k"), finish_reason="stop")],
                            usage=SimpleNamespace(prompt_tokens=1, completion_tokens=2),
                        ),
                    ]
                )

        fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

        with patch.object(review_engine, "get_client", return_value=fake_client):
            ok, content, telemetry = review_engine._call_llm(
                [
                    {"role": "system", "content": "system"},
                    {"role": "user", "content": "user"},
                ]
            )

        self.assertTrue(ok)
        self.assertEqual("ok", content)
        self.assertIn("timeout", captured)
        self.assertIn("max_completion_tokens", captured)
        self.assertNotIn("max_tokens", captured)
        self.assertEqual({"type": "json_object"}, captured["response_format"])
        self.assertNotIn("temperature", captured)
        self.assertTrue(captured["stream"])
        self.assertEqual("stop", telemetry["finish_reason"])

    def test_call_llm_should_keep_temperature_for_non_kimi_models(self):
        captured = {}

        class FakeCompletions:
            def create(self, **kwargs):
                captured.update(kwargs)
                return SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="ok"), finish_reason="stop")],
                    usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
                )

        fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

        with (
            patch.object(review_engine, "get_client", return_value=fake_client),
            patch.object(review_engine, "get_model_candidates", return_value=("gpt-4.1-mini",)),
        ):
            ok, content, telemetry = review_engine._call_llm(
                [
                    {"role": "system", "content": "system"},
                    {"role": "user", "content": "user"},
                ]
            )

        self.assertTrue(ok)
        self.assertEqual("ok", content)
        self.assertEqual(0.3, captured["temperature"])
        self.assertEqual({"type": "json_object"}, captured["response_format"])

    def test_call_llm_should_fail_when_model_returns_empty_content(self):
        class FakeCompletions:
            def create(self, **kwargs):
                return SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content=""), finish_reason="stop")],
                    usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1200),
                )

        fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

        with patch.object(review_engine, "get_client", return_value=fake_client):
            ok, content, telemetry = review_engine._call_llm(
                [
                    {"role": "system", "content": "system"},
                    {"role": "user", "content": "user"},
                ]
            )

        self.assertFalse(ok)
        self.assertEqual("", content)
        self.assertEqual("stop", telemetry["finish_reason"])

    def test_call_llm_should_fail_when_finish_reason_is_length(self):
        class FakeCompletions:
            def create(self, **kwargs):
                return iter(
                    [
                        SimpleNamespace(
                            choices=[SimpleNamespace(delta=SimpleNamespace(content="{\"a\":1}"), finish_reason="length")],
                            usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1200),
                        )
                    ]
                )

        fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

        with patch.object(review_engine, "get_client", return_value=fake_client):
            ok, content, telemetry = review_engine._call_llm(
                [
                    {"role": "system", "content": "system"},
                    {"role": "user", "content": "user"},
                ]
            )

        self.assertFalse(ok)
        self.assertEqual("", content)
        self.assertEqual("length", telemetry["finish_reason"])

    def test_call_llm_should_retry_once_when_first_stream_is_empty(self):
        captured = {"calls": 0}

        class FakeCompletions:
            def create(self, **kwargs):
                captured["calls"] += 1
                if captured["calls"] == 1:
                    return iter(
                        [
                            SimpleNamespace(
                                choices=[SimpleNamespace(delta=SimpleNamespace(content=""), finish_reason="stop")],
                                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=10),
                            )
                        ]
                    )
                return iter(
                    [
                        SimpleNamespace(
                            choices=[SimpleNamespace(delta=SimpleNamespace(content="{"), finish_reason=None)],
                            usage=None,
                        ),
                        SimpleNamespace(
                            choices=[SimpleNamespace(delta=SimpleNamespace(content="\"ok\":true}"), finish_reason="stop")],
                            usage=SimpleNamespace(prompt_tokens=1, completion_tokens=12),
                        ),
                    ]
                )

        fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

        with patch.object(review_engine, "get_client", return_value=fake_client):
            ok, content, telemetry = review_engine._call_llm(
                [
                    {"role": "system", "content": "system"},
                    {"role": "user", "content": "user"},
                ]
            )

        self.assertTrue(ok)
        self.assertEqual('{"ok":true}', content)
        self.assertEqual(2, captured["calls"])

    def test_call_llm_should_emit_draft_preview_callback(self):
        previews = []

        class FakeCompletions:
            def create(self, **kwargs):
                return iter(
                    [
                        SimpleNamespace(
                            choices=[SimpleNamespace(delta=SimpleNamespace(content='{"main_block":"你卡在公式'), finish_reason=None)],
                            usage=None,
                        ),
                        SimpleNamespace(
                            choices=[SimpleNamespace(delta=SimpleNamespace(content='为什么成立","key_bridge":"先说明直径覆盖"}'), finish_reason="stop")],
                            usage=SimpleNamespace(prompt_tokens=1, completion_tokens=20),
                        ),
                    ]
                )

        fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

        with patch.object(review_engine, "get_client", return_value=fake_client):
            ok, content, telemetry = review_engine._call_llm(
                [
                    {"role": "system", "content": "system"},
                    {"role": "user", "content": "user"},
                ],
                chunk_callback=lambda raw, preview: previews.append((raw, preview)),
            )

        self.assertTrue(ok)
        self.assertEqual("stop", telemetry["finish_reason"])
        self.assertIn("main_block", previews[-1][1])
        self.assertIn("key_bridge", previews[-1][1])

    def test_generate_review_should_call_llm_with_system_and_user_messages(self):
        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})) as mocked_call:
            result = review_engine.generate_review(
                problem_title="活动安排",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我知道题目里有时间和地点两个限制，但总分不清它们是不是同一层条件。",
                error_types=["modeling"],
                problem_context="每个活动必须同时满足时间窗口和指定地点两个条件。",
            )

        self.assertFalse(result["ok"])
        messages = mocked_call.call_args.args[0]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("只输出 JSON", messages[0]["content"])
        self.assertIn("活动安排", messages[1]["content"])

    def test_generate_review_should_normalize_submission_result_before_routing(self):
        with (
            patch.object(review_engine, "_call_llm", return_value=(False, "", {})),
            patch.object(review_engine, "_detect_review_mode", return_value="failed_verdict") as mocked_detect,
        ):
            review_engine.generate_review(
                problem_title="活动安排",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我知道这里错在条件判断，但还说不清是哪一步断了。",
                error_types=["implementation"],
                submission_result=" WA ",
            )

        mocked_detect.assert_called_once_with("unfinished", "wa")

    def test_generate_review_should_trim_optional_prompt_inputs(self):
        long_context = "这是一道树上选核心城市的题。 " * 40
        long_reflection = "我总觉得自己是把直径和答案公式硬套上去，但说不清为什么。 " * 10
        long_code = "int dfs(int u){return u;}\n" * 80

        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})) as mocked_call:
            review_engine.generate_review(
                problem_title="P5536 核心城市",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我知道这题和树的直径有关，也写出了公式，但不知道为什么答案能直接这样推。",
                error_types=["模型转化", "知道算法但不知道怎么用"],
                problem_context=long_context,
                problem_tags=["O2优化", "堆", "树的直径", "贪心"],
                chat_context_summary="这是一段默认不该进入 prompt 的同题摘要。",
                reflection=long_reflection,
                student_code=long_code,
            )

        user_prompt = mocked_call.call_args.args[0][1]["content"]
        self.assertIn("相关标签：树的直径、贪心", user_prompt)
        self.assertNotIn("O2优化", user_prompt)
        self.assertNotIn("同题摘要", user_prompt)
        self.assertIn("题目摘要：", user_prompt)
        self.assertIn("代码片段：", user_prompt)
        self.assertIn("\n...\n", user_prompt)
        self.assertNotIn(long_context, user_prompt)
        self.assertNotIn(long_reflection, user_prompt)

    def test_generate_review_should_not_backfill_only_generic_tags(self):
        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})) as mocked_call:
            review_engine.generate_review(
                problem_title="模板题",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我知道这里错在公式，但说不清哪里推错了。",
                error_types=["模型转化"],
                problem_tags=["O2优化", "NOIP", "模板"],
                problem_context="给定一个式子，需要说明公式为什么成立。",
            )

        user_prompt = mocked_call.call_args.args[0][1]["content"]
        self.assertNotIn("相关标签：", user_prompt)
        self.assertNotIn("O2优化", user_prompt)
        self.assertNotIn("NOIP", user_prompt)

    def test_generate_review_should_keep_middle_formula_line_in_code_excerpt(self):
        student_code = "\n".join(
            [f"int filler_{i} = {i};" for i in range(40)]
            + ["int answer = (d - k + 2) / 2;"]
            + [f"int tail_{i} = {i};" for i in range(40)]
        )

        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})) as mocked_call:
            review_engine.generate_review(
                problem_title="P5536 核心城市",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我知道答案公式和树的直径有关，也定位到了代码里这一行，但不知道为什么这一行会是对的。",
                error_types=["模型转化"],
                student_code=student_code,
                problem_context="要解释树的直径和答案公式之间的关系。",
            )

        user_prompt = mocked_call.call_args.args[0][1]["content"]
        self.assertIn("int answer = (d - k + 2) / 2;", user_prompt)
        self.assertIn("\n...\n", user_prompt)

    def test_generate_review_should_keep_short_context_patch_when_problem_card_exists(self):
        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})) as mocked_call:
            review_engine.generate_review(
                problem_title="P5536 核心城市",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我知道这题和树的直径有关，也知道最后要套公式，但不知道公式为什么能成立、卡在证明这一步。",
                error_types=["模型转化"],
                problem_context="关键是证明核心城市在直径上形成连续覆盖段，答案取决于两侧剩余最长距离。",
                problem_card={
                    "summary": "树上选 k 个连通核心城市。",
                    "goal": "最小化非核心城市到核心集合的最远距离。",
                },
            )

        user_prompt = mocked_call.call_args.args[0][1]["content"]
        self.assertIn("题目结构化卡：", user_prompt)
        self.assertIn("题目补充：", user_prompt)
        self.assertIn("连续覆盖段", user_prompt)

    def test_meta_knowledge_guard_should_prefer_bottleneck_anchor_for_formula_case(self):
        review = {
            "main_block": "你不是不会背结论，而是还没先说明这个局部选择为什么不吃亏、为什么还能给后续留空间。",
            "key_bridge": "关键不是先记贪心结论，而是先说明为什么当前对象优先选不会吃亏，它给后续留下了什么空间。",
            "diagnosis": "你已经知道直径和公式有关，但没说明为什么公式可以直接从覆盖关系推出。",
            "next_step": "先画图。",
            "transfer_signal": "先看局部选择。",
        }

        guarded = review_engine._guard_review_against_meta_knowledge(
            review.copy(),
            problem_title="P5536 核心城市",
            problem_context="在树上选 k 个连通核心城市，最小化其他城市到核心城市集合的最远距离。",
            bottleneck_text="我知道这题和树的直径有关，也写出了先求直径长度 d 再套公式的做法，但我不明白为什么答案能直接写成 (d-k+2)/2。",
        )

        self.assertIn("树的直径", guarded["main_block"])
        self.assertNotIn("后续留空间", guarded["key_bridge"])

    def test_generate_problem_analysis_should_call_llm_with_system_and_user_messages(self):
        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})) as mocked_call:
            result = review_engine.generate_problem_analysis(
                problem_title="子集枚举",
                compact_card={"summary": "枚举所有选择", "samples": []},
                difficulty=2,
            )

        self.assertFalse(result["ok"])
        messages = mocked_call.call_args.args[0]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("结构化教学分析卡", messages[0]["content"])
        self.assertIn("子集枚举", messages[1]["content"])

    def test_generate_structural_quiz_should_call_llm_with_system_and_user_messages(self):
        review_context = {
            "problem_title": "活动安排",
            "problem_context": "每个活动必须同时满足时间窗口和指定地点两个条件。",
            "bottleneck_text": "我总把两个条件看成先后顺序。",
            "error_layer": "modeling",
            "key_bridge": "时间和地点条件是并列约束，两个都要满足。",
            "next_step": "先把两个条件分开列出来。",
            "core_design_subtags": [],
        }
        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})) as mocked_call:
            review_engine._generate_structural_quiz(
                review_context,
                "constraint_modeling",
                "两个条件都要满足",
                level="main",
            )

        messages = mocked_call.call_args.args[0]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("结构型小题", messages[0]["content"])
        self.assertIn("活动安排", messages[1]["content"])


if __name__ == "__main__":
    unittest.main()
