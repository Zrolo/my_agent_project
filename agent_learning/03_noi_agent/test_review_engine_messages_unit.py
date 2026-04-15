import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

import review_engine


class ReviewEngineMessageSplitTests(unittest.TestCase):
    def _combined_review_fields(self, review: dict, fields: tuple[str, ...] = ("problem_focus", "key_bridge", "visual_hint", "guided_walkthrough", "try_now")) -> str:
        return " ".join(str(review.get(field, "")) for field in fields)

    def _p3128_tree_path_difference_review_context(self) -> dict:
        return {
            "problem_title": "P3128 [USACO15DEC] Max Flow P",
            "problem_context": "给一棵 N 个点的树和 K 对奶牛运输路径，每次从 s 到 t 的整条树上路径都会经过一些节点，要求所有路径结束后经过次数最多的节点。题目标签包含差分、最近公共祖先 LCA、树链剖分。",
            "bottleneck_text": "我只想到树剖 LCA，但不知道为什么要把每条路径的贡献变成端点和 LCA 附近的差分标记，最后再 DFS 汇总。",
            "error_layer": "core_design",
            "core_design_subtags": ["tree_path_difference"],
            "main_block": "你卡在多条树上路径的经过次数不能逐点更新。",
            "key_bridge": "把一条树上路径贡献转成端点/LCA 附近的差分标记，再通过子树汇总还原每个点经过次数。",
            "next_step": "先说清一条 s 到 t 的路径为什么可以只在 s、t、lca 及其父亲附近打标记。",
        }

    def test_load_external_bridge_snippets_should_prefer_unified_index(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_dir = root / "docs" / "common"
            docs_dir.mkdir(parents=True)
            unified = docs_dir / "bridge_external_snippets_v1.jsonl"
            cp_pdf = docs_dir / "cp_pdf_bridge_snippets_v1.jsonl"
            oi_wiki = docs_dir / "oi_wiki_bridge_snippets_v1.jsonl"
            unified.write_text(
                '{"bridge":"shared_prefix_merging","snippet_type":"bridge_explanation","source_family":"unified","excerpt":"统一索引内容"}\n',
                encoding="utf-8",
            )
            cp_pdf.write_text(
                '{"bridge":"shared_prefix_merging","snippet_type":"bridge_explanation","source_family":"cp-pdf","excerpt":"旧 cp-pdf 内容"}\n',
                encoding="utf-8",
            )
            oi_wiki.write_text(
                '{"bridge":"shared_prefix_merging","snippet_type":"bridge_explanation","source_family":"oi-wiki","excerpt":"旧 oi-wiki 内容"}\n',
                encoding="utf-8",
            )

            with patch.object(review_engine, "__file__", str(root / "review_engine.py")):
                review_engine._external_bridge_snippets_cache = None
                rows = review_engine._load_external_bridge_snippets()

            self.assertEqual(1, len(rows))
            self.assertEqual("unified", rows[0]["source_family"])
            self.assertEqual("统一索引内容", rows[0]["excerpt"])

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

    def test_infer_algorithm_category_should_prefer_focus_fallback_over_substring_false_positive(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "我没有先算规模，总觉得双层枚举也许还能过。",
            "key_bridge": "先根据数据范围判断双层枚举会不会超时。",
        }

        self.assertEqual("复杂度判断", review_engine._infer_algorithm_category(review_context, "complexity_fit"))
        self.assertEqual("方法判断", review_engine._infer_algorithm_category(review_context, "method_selection"))
        self.assertEqual("判定/二分", review_engine._infer_algorithm_category(review_context, "check_condition"))

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

    def test_build_review_system_prompt_should_require_guided_walkthrough(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("guided_walkthrough", prompt)
        self.assertIn("跟我走一遍", prompt)
        self.assertIn("2-3 步", prompt)
        self.assertIn("不能只写画图、手推、再想想", prompt)
        self.assertIn("每一步只推进一个动作", prompt)
        self.assertIn("每一步最好控制在 1-2 句", prompt)
        self.assertIn("try_now", prompt)
        self.assertIn("只能给一个很小的问题或动作", prompt)

    def test_build_review_system_prompt_should_request_optional_visual_hint(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("visual_hint", prompt)
        self.assertIn("文本化小图", prompt)
        self.assertIn("禁止直接给出最终比较结果", prompt)
        self.assertIn("优先写估算、分类、对比前的半成品提示", prompt)

    def test_build_review_system_prompt_should_require_try_now_to_probe_current_bridge(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("必须直接检查当前桥有没有真的打通", prompt)
        self.assertIn("不能退化成只做表面算数或机械抄写", prompt)

    def test_build_review_system_prompt_should_require_student_facing_short_sentences(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("面向初中生", prompt)
        self.assertIn("短句", prompt)
        self.assertIn("先讲对象，再讲关系", prompt)
        self.assertIn("先说最容易误会的一句话", prompt)
        self.assertIn("再说正确的一句话", prompt)

    def test_build_review_system_prompt_should_list_current_core_design_subtags(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("tree_diameter_candidates", prompt)
        self.assertIn("lazy_semantics", prompt)

    def test_build_review_system_prompt_should_follow_evidence_decision_feedback(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertIn("Evidence", prompt)
        self.assertIn("Decision", prompt)
        self.assertIn("Feedback", prompt)
        self.assertIn("先根据学生提供的题目、卡点、代码、提交现象", prompt)
        self.assertIn("每次只能解决一个当前桥梁", prompt)
        self.assertIn("推进半步到一步", prompt)
        self.assertIn("默认按更保守、更小步的方式支架", prompt)

    def test_build_review_system_prompt_should_keep_legacy_compatibility_out_of_main_prompt(self):
        prompt = review_engine._build_review_system_prompt("stuck_bridge")
        self.assertNotIn("兼容旧版展示", prompt)
        self.assertIn("main_block：兼容字段，内容与 problem_focus 保持一致", prompt)
        self.assertIn("next_step：兼容字段，内容与 try_now 保持一致", prompt)

    def test_build_review_system_prompt_should_add_failure_family_scaffold_goal(self):
        prompt = review_engine._build_review_system_prompt("failed_verdict")
        self.assertIn("本次任务属于 failure_diagnosis", prompt)
        self.assertIn("先定位错误或卡点，再把问题缩小到学生现在能检查的一步", prompt)

    def test_build_review_system_prompt_should_add_success_family_scaffold_goal(self):
        prompt = review_engine._build_review_system_prompt("independent_reflect")
        self.assertIn("本次任务属于 success_reflection", prompt)
        self.assertIn("先帮助学生说清为什么这样做对，再帮助他形成迁移信号", prompt)

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

    def test_build_clarify_system_prompt_should_forbid_direct_teaching(self):
        prompt = review_engine._build_clarify_system_prompt()
        self.assertIn("禁止直接讲题", prompt)
        self.assertIn("帮助学生把问题说清楚", prompt)
        self.assertIn("题目要求你求什么", prompt)
        self.assertIn("你试到哪一步", prompt)

    def test_build_remedy_system_prompt_should_require_smaller_step_not_repetition(self):
        prompt = review_engine._build_remedy_system_prompt(review_engine.REMEDY_ACTION_DYNAMIC)
        self.assertIn("不重复第一轮复盘", prompt)
        self.assertIn("只把桥缩小一步", prompt)
        self.assertIn("换一种表示方式", prompt)
        self.assertIn("只能给一个最小动作", prompt)

    def test_build_bottom_out_system_prompt_should_require_current_problem_worked_example(self):
        prompt = review_engine._build_bottom_out_system_prompt(review_engine.REMEDY_ACTION_DYNAMIC)
        self.assertIn("当前题", prompt)
        self.assertIn("worked example", prompt)
        self.assertIn("初中生", prompt)
        self.assertIn("visual_hint", prompt)
        self.assertIn("先讲对象，再讲关系，再讲这一步怎么想", prompt)

    def test_generate_remedy_explanation_should_use_clarify_prompt_for_insufficient(self):
        review_context = {
            "problem_title": "P1000 超级玛丽游戏",
            "problem_context": "题目只要求输出固定图案。",
            "error_layer": "insufficient",
            "bottleneck_text": "我不会这题",
            "main_block": "你还没把具体卡点说清楚。",
        }
        fake_json = '{"remedy_text":"先把题目目标说清楚。","micro_action":"先用一句话说这题要求你求什么。"}'

        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})) as mocked_call:
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertEqual("先把题目目标说清楚。", payload["remedy_text"])
        self.assertEqual("先用一句话说这题要求你求什么。", payload["micro_action"])
        messages = mocked_call.call_args.args[0]
        self.assertIn("帮助学生把问题说清楚", messages[0]["content"])

    def test_generate_remedy_explanation_should_use_remedy_prompt_for_non_insufficient(self):
        review_context = {
            "problem_title": "P1434 滑雪",
            "problem_context": "从任意点出发，只能走到更低的格子，求最长路径。",
            "error_layer": "modeling",
            "bottleneck_text": "我不知道状态该怎么定义。",
            "main_block": "你卡在状态含义没站稳。",
            "key_bridge": "先把每个状态表示的对象写清楚。",
            "next_step": "先写每个状态表示什么。",
        }
        fake_json = '{"remedy_text":"先把状态缩成一维来看。","micro_action":"先说 dp[i][j] 表示什么。"}'

        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})) as mocked_call:
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertEqual("先把状态缩成一维来看。", payload["remedy_text"])
        self.assertEqual("先说 dp[i][j] 表示什么。", payload["micro_action"])
        messages = mocked_call.call_args.args[0]
        self.assertIn("不重复第一轮复盘", messages[0]["content"])

    def test_generate_remedy_explanation_should_use_bottom_out_prompt_after_prior_remedy(self):
        review_context = {
            "problem_title": "P2195 HXY造公园",
            "problem_context": "把两个休息点群用新边连起来后，要求新的最大距离。",
            "error_layer": "core_design",
            "bottleneck_text": "我还是不知道新最长路会从哪几种情况里产生。",
            "problem_focus": "你卡在新最长路候选怎么产生。",
            "main_block": "你卡在新最长路候选怎么产生。",
            "key_bridge": "新最长路只会来自左边内部、右边内部、经过新边三种候选。",
            "guided_walkthrough": "1. 先看左边 2. 再看右边 3. 最后看新边",
            "try_now": "如果经过新边，左边这一端该接什么点？",
            "remedy_count": 1,
        }
        fake_json = '{"remedy_text":"先只看左边这部分。","visual_hint":"左边: A-B-C\\n右边: D-E\\n新边: C-D","micro_action":"现在只回答：左边这一端该接什么点？"}'

        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})) as mocked_call:
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertEqual("左边: A-B-C\n右边: D-E\n新边: C-D", payload["visual_hint"])
        messages = mocked_call.call_args.args[0]
        self.assertIn("worked example", messages[0]["content"])
        self.assertIn("当前题", messages[0]["content"])

    def test_generate_bridge_quiz_followup_should_shrink_trie_method_selection_to_shared_prefix_signal(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "给定很多二进制信息和很多拦截串。对每个拦截串，需要统计有多少条信息满足前缀包含关系。信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。常见做法是用 trie 统计经过每个节点的信息数量。",
            "bottleneck_text": "这里为什么不能直接枚举，而是要用到 trie 树？",
            "error_layer": "method",
            "key_bridge": "先从题面里指出哪一个结构信号真的在支持 trie，而不是先凭感觉报方法名。",
            "next_step": "先圈出题面里一个真正支持 trie 的结构信号。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果一条拦截串长度是 20，用 trie 查它时，时间更主要跟什么有关？",
            "correct_answer": "B",
        }

        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("相同开头", payload["question_text"])
        self.assertNotEqual(previous_quiz["question_text"], payload["question_text"])
        self.assertTrue(
            any("相同开头" in option["label"] or "共享前缀" in option["label"] for option in payload["options"]),
            payload["options"],
        )
        self.assertEqual("local_shared_prefix_signal", payload["meta"]["followup_mode"])

    def test_generate_bridge_quiz_main_should_be_concrete_for_trie_method_selection(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "给定很多二进制信息和很多拦截串。对每个拦截串，需要统计有多少条信息满足前缀包含关系。信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。常见做法是用 trie 统计经过每个节点的信息数量。",
            "bottleneck_text": "这里为什么不能直接枚举，而是要用到 trie 树？",
            "error_layer": "method",
            "key_bridge": "先判断逐条比对是不是在重复重看很多条消息，再看 trie 为什么只沿当前前缀往下走。",
            "next_step": "先比较“重看很多条消息”和“只沿当前前缀走”这两个查询过程。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("trie method_selection 主轮不应依赖 LLM")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                quiz_role=review_engine.QUIZ_ROLE_MAIN,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("查询", payload["question_text"])
        self.assertTrue(
            any(term in payload["question_text"] for term in ("所有消息", "前缀", "往下走")),
            payload["question_text"],
        )
        self.assertTrue(payload["options"])

    def test_generate_bridge_quiz_main_should_keep_complexity_fit_on_local_scale_bridge(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "我没有先算规模，总觉得直接枚举所有消息也能过。",
            "error_layer": "method",
            "key_bridge": "先根据数据范围判断双层枚举会不会超时。",
            "next_step": "先比较双层规模和时间限制。",
            "problem_focus": "未估算 M 和 N 同时很大时逐条比对的总量级。",
            "try_now": "假设 M=50000, N=50000, 串长=20，手算总字符比较次数并判断是否超时。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("complexity_fit 主轮不应依赖 LLM")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                quiz_role=review_engine.QUIZ_ROLE_MAIN,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertTrue(
            any(term in payload["question_text"] for term in ("规模", "枚举", "超时", "复杂度")),
            payload["question_text"],
        )
        self.assertTrue(
            any("超时" in option["label"] or "复杂度" in option["label"] or "规模" in option["label"] for option in payload["options"]),
            payload["options"],
        )

    def test_generate_bridge_quiz_followup_should_shrink_generic_method_selection_to_local_signal(self):
        review_context = {
            "problem_title": "区间覆盖题",
            "problem_context": "给很多区间，要求选出互不重叠的最多区间。常见做法是先按结束位置排序，再依次挑选能接上的区间。",
            "bottleneck_text": "我知道这是贪心，但说不清题面里到底哪一个信号支持先按结束位置更早的来选。",
            "error_layer": "method",
            "key_bridge": "先找出题面里真正支持“先看结束更早”这个方法的结构信号。",
            "next_step": "先比较“选得更早结束”和“只是看起来更顺手”有什么本质区别。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果这一步只确认“为什么该用这个方法”，下面哪句更对？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("题面", payload["question_text"])
        self.assertTrue(
            any("结构信号" in option["label"] or "结束" in option["label"] for option in payload["options"]),
            payload["options"],
        )
        self.assertNotIn("为什么该用这个方法", payload["question_text"])

    def test_generate_bridge_quiz_followup_should_shrink_complexity_fit_to_local_scale_check(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "我没有先算规模，总觉得直接枚举所有消息也能过。",
            "error_layer": "method",
            "key_bridge": "先根据数据范围判断双层枚举会不会超时。",
            "next_step": "先比较双层规模和时间限制。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果这题要先判断复杂度能不能过，下面哪种说法更合理？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertTrue(
            any(term in payload["question_text"] for term in ("双层", "枚举", "规模", "M", "N", "总量级")),
            payload["question_text"],
        )
        self.assertNotIn("为什么该用这个方法", payload["question_text"])
        self.assertTrue(
            any(term in payload["question_text"] for term in ("总量级", "乘积", "M", "N", "配对")),
            payload["question_text"],
        )
        self.assertTrue(
            any(
                "总量级" in option["label"]
                or "乘积" in option["label"]
                or "M×N" in option["label"]
                or "M 和 N" in option["label"]
                for option in payload["options"]
            ),
            payload["options"],
        )

    def test_detect_quiz_focus_should_treat_scale_language_as_complexity_fit(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "这里为什么不能直接枚举，而是要用到 trie 树？我老是感觉逐条比对也能做。",
            "error_layer": "method",
            "problem_focus": "未估算M条消息与N条拦截串逐条比对的总量级",
            "key_bridge": "看到数据量很大却未计算M与N的乘积规模，误判逐条比对可行",
            "next_step": "先圈出题面里的规模或范围信号，再判断它是不是已经支持直接枚举或当前方法，不要先套模板。",
            "try_now": "假设M=50000, N=50000, 串长=20，手算逐条比对总字符比较次数并判断是否超时",
        }

        self.assertEqual("complexity_fit", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_prefer_method_selection_when_signal_language_is_explicit(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "有很多 01 串，反复查询某个前缀能匹配多少条消息。",
            "bottleneck_text": "我总是先猜可能要 trie，但说不清题面里到底有什么结构信号支持它。",
            "error_layer": "method",
            "problem_focus": "无法从题面提取支持Trie的结构信号，直接套用模板",
            "key_bridge": "看到前缀就联想Trie，但未从题面验证是否涉及大量字符串间的前缀比对与计数",
            "guided_walkthrough": "先找题面信号，再看这些信号为什么支持 trie，最后再回到方法名。",
            "transfer_signal": "如果你一看到题就想套熟方法，先停下来问：题面里到底哪一个结构信号真的在支持它。",
        }

        self.assertEqual("method_selection", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_route_p2249_to_left_bound_update(self):
        review_context = {
            "problem_title": "P2249 查找",
            "problem_context": "在有序数组里找第一个等于 x 的位置。",
            "bottleneck_text": "我会写二分，但 a[mid] == x 时，总不知道该把右边界写成 mid 还是 mid-1。",
            "error_layer": "implementation",
            "key_bridge": "命中后要不要保留 mid 这一侧。",
        }

        self.assertEqual("left_bound_update", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_route_trie_node_count_language_to_shared_prefix_merging(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "有很多消息和拦截串，需要反复统计前缀关系。",
            "bottleneck_text": "我不知道 trie 节点该存什么信息，为什么经过次数就够了。",
            "error_layer": "core_design",
            "key_bridge": "先说清这些消息为什么能沿公共前缀合在一起，再看经过次数为什么能直接回答查询。",
        }

        self.assertEqual("shared_prefix_merging", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_route_trie_node_count_language_before_generic_state_subtag(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "有很多消息和拦截串，需要反复统计前缀关系。",
            "bottleneck_text": "我不知道 trie 节点该存什么信息，为什么经过次数就够了。",
            "error_layer": "core_design",
            "core_design_subtags": ["state_design"],
            "key_bridge": "先说清经过次数记录了多少消息经过当前前缀节点。",
        }

        self.assertEqual("shared_prefix_merging", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_route_p3128_path_count_to_tree_path_difference_not_trie(self):
        review_context = self._p3128_tree_path_difference_review_context()

        self.assertEqual("tree_path_difference", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_route_route_visit_count_language_to_tree_path_difference(self):
        review_context = {
            "problem_title": "P3258 [JLOI2014] 松鼠的新家",
            "problem_context": "一只松鼠按给定顺序在树上的房间之间移动，每一段都是从当前房间走到下一个房间，要统计每个房间最终被访问了多少次。",
            "bottleneck_text": "我知道每段路都要贡献一次，但不知道为什么可以在起点、终点、公共祖先附近打标记，最后向上汇总。",
            "error_layer": "core_design",
            "key_bridge": "把每段树上路线的访问贡献转成端点和公共祖先附近的差分标记，再 DFS 汇总每个房间的访问次数。",
        }

        self.assertEqual("tree_path_difference", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_route_edge_count_language_to_tree_path_difference(self):
        review_context = {
            "problem_title": "树上边经过次数统计",
            "problem_context": "给一棵树和很多次 u 到 v 的运输，每次会经过一串道路，最后要统计哪条边被经过最多。",
            "bottleneck_text": "我总想沿路把每条边加一，但题解说要用 LCA 和树上差分，在端点打标记后 DFS 汇总。",
            "error_layer": "core_design",
            "key_bridge": "先把每条树上路线对边的贡献变成少数几个点的标记，再用 DFS 汇总出边经过次数。",
        }

        self.assertEqual("tree_path_difference", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_keep_segment_tree_lazy_when_marker_is_range_update(self):
        review_context = {
            "problem_title": "P3372 线段树 1",
            "problem_context": "需要多次区间加和区间求和，节点维护区间 sum。",
            "bottleneck_text": "我不懂 lazy 标记到底表示什么，什么时候 pushdown 到左右儿子。",
            "error_layer": "core_design",
            "key_bridge": "lazy 记录的是这段区间已经确定但还没下传给孩子的信息。",
        }

        self.assertEqual("lazy_semantics", review_engine._detect_quiz_focus(review_context))

    def test_resolve_bridge_decision_should_record_known_bridge_without_changing_focus(self):
        review_context = self._p3128_tree_path_difference_review_context()

        decision = review_engine._resolve_bridge_decision(review_context)

        self.assertEqual("known_bridge", decision["status"])
        self.assertEqual("tree_path_difference", decision["stable_focus"])
        self.assertEqual("graph.tree_path_difference", decision["card_id"])
        self.assertEqual("high", decision["route_confidence"])
        self.assertIn("树上路径", decision["matched_signals"])
        self.assertEqual("tree_path_difference", review_engine._detect_quiz_focus(review_context))

    def test_resolve_bridge_decision_should_record_candidate_edge_variant_without_routing_to_it(self):
        review_context = {
            "problem_title": "树上边经过次数统计",
            "problem_context": "给一棵树和很多次 u 到 v 的运输，每次会经过一串道路，最后要统计哪条边被经过最多。",
            "bottleneck_text": "我总想沿路把每条边加一，但题解说要用 LCA 和树上差分，在端点打标记后 DFS 汇总。",
            "error_layer": "core_design",
            "key_bridge": "先把每条树上路线对边的贡献变成少数几个点的标记，再用 DFS 汇总出边经过次数。",
        }

        decision = review_engine._resolve_bridge_decision(review_context)

        self.assertEqual("candidate_bridge", decision["status"])
        self.assertEqual("tree_path_difference", decision["stable_focus"])
        self.assertEqual("tree_path_difference.edge_variant", decision["candidate_bridge_id"])
        self.assertEqual("tree_path_difference", decision["candidate_parent_focus"])
        self.assertIn("边", " ".join(decision["matched_signals"]))

    def test_resolve_bridge_decision_should_record_open_bridge_for_unknown_specific_method(self):
        review_context = {
            "problem_title": "KMP 模式匹配",
            "problem_context": "给定文本串和模式串，要求快速找到模式串出现位置。",
            "bottleneck_text": "我看题解说要用 next 数组，但我不理解失配之后为什么能跳到某个前后缀位置。",
            "error_layer": "method",
            "key_bridge": "先理解失配后为什么能复用已经匹配过的前后缀。",
        }

        decision = review_engine._resolve_bridge_decision(review_context)

        self.assertEqual("open_bridge", decision["status"])
        self.assertEqual("method_selection", decision["stable_focus"])
        self.assertEqual("kmp_failure_link", decision["candidate_bridge_id"])
        self.assertEqual("method_selection", decision["candidate_parent_focus"])
        self.assertIn("KMP", decision["open_bridge_label"])

    def test_generate_review_should_attach_bridge_route_meta_without_changing_review_focus(self):
        fake_json = json.dumps(
            {
                "error_tags": ["模型转化"],
                "error_layer": "core_design",
                "error_layer_confidence": "high",
                "core_design_subtags": ["tree_path_difference"],
                "diagnosis": "你卡在把每条树上边路径的贡献转成少量标记。",
                "next_action": "回到当前题先说清一条路径怎么打标记。",
                "suggested_topic": "树上路径贡献标记",
                "problem_focus": "你卡在边经过次数不能沿路逐条加。",
                "main_block": "你卡在边经过次数不能沿路逐条加。",
                "key_bridge": "先把一条树上边路径的贡献变成端点和公共祖先附近的差分标记。",
                "visual_hint": "u 到 v 的路\n-> 只在端点附近打标记\n-> DFS 汇总边贡献",
                "guided_walkthrough": "1. 先找一条 u 到 v 的路线。\n2. 再看它跨过哪些道路。\n3. 最后想哪些点标记能让 DFS 还原道路贡献。",
                "try_now": "先说 u 到 v 这条路的公共祖先是谁。",
                "next_step": "先说 u 到 v 这条路的公共祖先是谁。",
                "transfer_signal": "看到很多树上路线都要统计经过次数，先想路径差分。",
            },
            ensure_ascii=False,
        )

        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})):
            result = review_engine.generate_review(
                problem_title="树上边经过次数统计",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我总想沿路把每条边加一，但题解说要用 LCA 和树上差分。",
                error_types=["模型转化"],
                problem_context="给一棵树和很多次 u 到 v 的运输，每次会经过一串道路，最后要统计哪条边被经过最多。",
            )

        self.assertTrue(result["ok"])
        self.assertEqual(["tree_path_difference"], result["review"]["core_design_subtags"])
        self.assertEqual("candidate_bridge", result["bridge_route_meta"]["status"])
        self.assertEqual("tree_path_difference", result["bridge_route_meta"]["stable_focus"])
        self.assertEqual("tree_path_difference.edge_variant", result["bridge_route_meta"]["candidate_bridge_id"])

    def test_generate_bridge_quiz_main_should_be_concrete_for_tree_path_difference(self):
        review_context = self._p3128_tree_path_difference_review_context()

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_bridge_quiz(review_context, quiz_role=review_engine.QUIZ_ROLE_MAIN)

        combined = " ".join(
            [
                payload["question_text"],
                payload["explanation"],
                " ".join(option["label"] for option in payload["options"]),
            ]
        )
        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("tree_path_difference", payload["meta"]["focus"])
        self.assertIn("LCA", combined)
        self.assertTrue("路径" in combined and ("差分" in combined or "汇总" in combined), combined)
        self.assertNotIn("trie", combined.lower())
        self.assertNotIn("消息", combined)

    def test_generate_bridge_quiz_followup_should_shrink_tree_path_difference_to_lca_marking(self):
        review_context = self._p3128_tree_path_difference_review_context()
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "P3128 里有很多条树上路径都要给经过的点加一，为什么更该先想差分？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        combined = " ".join([payload["question_text"], payload["explanation"], " ".join(option["label"] for option in payload["options"])])
        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("tree_path_difference", payload["meta"]["focus"])
        self.assertIn("s", combined)
        self.assertIn("t", combined)
        self.assertIn("LCA", combined)
        self.assertIn("DFS", combined)
        self.assertNotIn("前缀", combined)

    def test_generate_final_micro_confirm_quiz_should_shrink_tree_path_difference_to_yes_no(self):
        review_context = self._p3128_tree_path_difference_review_context()
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "只看一条从 s 到 t 的树上路径，差分这一步最该先记住哪句话？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_final_micro_confirm_quiz(
                review_context,
                previous_quiz=previous_quiz,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertEqual("tree_path_difference", payload["meta"]["focus"])
        self.assertTrue(all(option["label"] in {"是", "不是"} for option in payload["options"]), payload["options"])
        self.assertIn("DFS", payload["explanation"])

    def test_guard_review_against_topic_drift_should_pull_trie_node_count_case_back_from_dp_wording(self):
        review = {
            "error_layer": "core_design",
            "core_design_subtags": ["state_design"],
            "main_block": "关键是先把状态里数量这一维的含义定清楚。",
            "key_bridge": "经过次数表示有多少消息以该节点为前缀，查询时路径上的结束次数统计比拦截串短的消息，终点经过次数统计比拦截串长或相等的消息",
            "next_step": "先把状态定义写出来，再想转移。",
            "transfer_signal": "如果状态里一维记录数量，就先定义它表示什么。",
        }

        guarded = review_engine._guard_review_against_topic_drift(
            review,
            "P2922 [USACO08DEC] Secret Message G",
            "有很多消息和拦截串，需要统计前缀关系。",
            "不知道节点该同时记录经过次数和结束次数，不理解查询时为何只需累加路径上的结束次数和终点的经过次数。",
            ["字典树 Trie", "前缀匹配"],
        )

        self.assertIn("经过次数", guarded["key_bridge"])
        self.assertIn("结束次数", guarded["key_bridge"])
        self.assertIn("当前前缀节点", guarded["next_step"])
        self.assertIn("前缀", guarded["transfer_signal"])

    def test_state_design_main_quiz_should_name_state_slot_when_axis_is_generic(self):
        review_context = {
            "problem_title": "P1434 滑雪",
            "problem_context": "给定一个高程矩阵，只能走到更低的格子，求最长滑行长度。",
            "bottleneck_text": "我知道是记忆化搜索，但 dp[x][y] 这一格到底表示什么，我总是说不清。",
            "error_layer": "core_design",
            "core_design_subtags": ["state_design"],
            "main_block": "你卡在 dp[x][y] 这一格到底记录什么。",
            "key_bridge": "先把 dp[x][y] 这一格的状态含义站稳。",
            "next_step": "先说清 dp[x][y] 表示什么。",
        }

        payload = review_engine._deterministic_structural_quiz(
            review_context,
            "state_design",
            "先把 dp[x][y] 这一格的状态含义站稳。",
            level="main",
        )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("dp[x][y]", payload["question_text"])
        self.assertNotIn("这一维", payload["question_text"])
        self.assertIn("含义定清楚", payload["question_text"])

    def test_greedy_basis_main_quiz_should_be_structural_not_fallback(self):
        review_context = {
            "problem_title": "P1803 凌乱的yyy / 线段覆盖",
            "problem_context": "有很多区间，要求选出最多个互不重叠的区间。",
            "bottleneck_text": "我知道要排序，但说不清为什么这里要先选结束更早的那个。",
            "error_layer": "core_design",
            "core_design_subtags": ["greedy_basis"],
            "main_block": "你卡在为什么当前这一步要先选结束更早的区间。",
            "key_bridge": "先解释这个选择为什么不会破坏后面的空间。",
            "next_step": "先说清为什么先选它不会挤掉后面的机会。",
        }

        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                quiz_role=review_engine.QUIZ_ROLE_MAIN,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("先选", payload["question_text"])
        self.assertTrue(
            any(
                "不容易破坏后面的结构" in option["label"]
                or "不会破坏后面的结构" in option["label"]
                or "留下更稳的空间" in option["label"]
                for option in payload["options"]
            ),
            payload["options"],
        )

    def test_generate_bridge_quiz_followup_should_shrink_state_design_to_state_slot_role(self):
        review_context = {
            "problem_title": "P1434 滑雪",
            "problem_context": "给定一个高程矩阵，只能走到更低的格子，求最长滑行长度。",
            "bottleneck_text": "我知道是记忆化搜索，但 dp[x][y] 这一格到底表示什么，我总是说不清。",
            "error_layer": "core_design",
            "core_design_subtags": ["state_design"],
            "key_bridge": "先把 dp[x][y] 这一格的状态含义站稳。",
            "next_step": "先说清 dp[x][y] 表示什么。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果状态里要放“位置/阶段”这一维，下面哪种解释更合理？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("dp[x][y]", payload["question_text"])
        self.assertNotIn("位置/阶段", payload["question_text"])
        self.assertTrue(
            any(term in option["label"] for option in payload["options"] for term in ("子问题结果", "最终答案", "方向")),
            payload["options"],
        )

    def test_generate_bridge_quiz_followup_should_shrink_check_condition_to_return_value_meaning(self):
        review_context = {
            "problem_title": "二分判定题",
            "problem_context": "需要二分答案，并写 check(mid) 判断当前 mid 是否可行。",
            "bottleneck_text": "我老是不知道 check(mid) 返回 true 到底在说明什么。",
            "error_layer": "core_design",
            "core_design_subtags": ["check_condition"],
            "main_block": "你卡在 check(mid) 的职责没站稳。",
            "key_bridge": "先把 check(mid) 返回 true 时说明什么说清楚。",
            "next_step": "先说清 check(mid) 判的是可行性，不是直接求答案。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果这题要写 check(mid)，下面哪种理解更合理？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("返回 true", payload["question_text"])
        self.assertNotIn("哪种理解更合理", payload["question_text"])
        self.assertTrue(
            any("当前 `mid` 可行" in option["label"] or "当前 mid 可行" in option["label"] for option in payload["options"]),
            payload["options"],
        )

    def test_generate_bridge_quiz_followup_should_shrink_enumeration_order_to_local_dependency(self):
        review_context = {
            "problem_title": "背包顺序题",
            "problem_context": "一维背包里，当前状态会用到前一个容量位置已经算好的结果。",
            "bottleneck_text": "我知道和顺序有关，但总说不清为什么这一层必须倒着枚举。",
            "error_layer": "core_design",
            "core_design_subtags": ["enumeration_order"],
            "main_block": "你卡在枚举顺序为什么必须服从依赖。",
            "key_bridge": "先说清谁依赖谁，再决定哪一维先枚举。",
            "next_step": "先看当前状态是不是要用前一个已经算好的状态。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果当前状态要用到前面已经算好的状态，下面哪种顺序理解更合理？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("前一个", payload["question_text"])
        self.assertNotIn("哪种顺序理解更合理", payload["question_text"])
        self.assertTrue(
            any("前一个状态" in option["label"] or "被依赖的状态" in option["label"] for option in payload["options"]),
            payload["options"],
        )

    def test_generate_bridge_quiz_followup_should_shrink_transition_design_to_local_source_check(self):
        review_context = {
            "problem_title": "区间转移题",
            "problem_context": "当前状态可能从左侧合并过来，也可能从上一步延续过来。",
            "bottleneck_text": "我每次写转移都只想到一种最顺手的来源，老是漏情况。",
            "error_layer": "core_design",
            "core_design_subtags": ["transition_design"],
            "main_block": "你卡在转移来源容易漏掉一支。",
            "key_bridge": "先把当前状态可能从哪些合法来源转过来想全。",
            "next_step": "先检查当前状态会不会有两类前态来源。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果在想“当前状态怎么转过来”，下面哪种理解更完整？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("当前状态", payload["question_text"])
        self.assertTrue(
            any("两类" in option["label"] or "来源" in option["label"] for option in payload["options"]),
            payload["options"],
        )
        self.assertNotIn("怎么转过来", payload["question_text"])

    def test_generate_bridge_quiz_followup_should_keep_left_bound_update_on_local_boundary_bridge(self):
        review_context = {
            "problem_title": "P2249 查找",
            "problem_context": "在有序数组里找第一个等于 x 的位置。",
            "bottleneck_text": "我会写二分，但当 a[mid] == x 时，总不知道该把右边界写成 mid 还是 mid-1。",
            "error_layer": "core_design",
            "key_bridge": "要找最左的相等位置，当 a[mid] 等于 x 时要先保留 mid 这个候选。",
            "next_step": "先说清相等时为什么不能先把 mid 丢掉。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果目标是找最左边那个等于 x 的位置，`a[mid] == x` 时下面哪种处理更稳？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("left_bound_update follow-up 不应依赖 LLM")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("a[mid] == x", payload["question_text"])
        self.assertTrue(
            any("保留 mid" in option["label"] or "最左" in option["label"] for option in payload["options"]),
            payload["options"],
        )

    def test_build_review_user_prompt_should_append_bridge_constraint_for_trie_method_selection(self):
        prompt = review_engine._build_review_user_prompt(
            problem_title="P2922 [USACO08DEC] Secret Message G",
            oj_source="luogu",
            status_text="需要提示",
            bottleneck_text="我觉得这里应该用 trie，但说不清题面里哪个信号真的支持它。",
            error_types=["方法选择"],
            problem_context="很多消息、很多拦截串，要反复判断前缀关系。",
        )

        self.assertIn("首轮 bridge 约束", prompt)
        self.assertIn("题面信号", prompt)
        self.assertTrue(any(term in prompt for term in ("相同开头", "前缀关系")), prompt)

    def test_guard_review_bridge_consistency_should_keep_shared_prefix_merging_on_trie_node_count_language(self):
        review = {
            "error_layer": "core_design",
            "problem_focus": "你现在主要是还没想清 Trie 节点到底该存什么。",
            "main_block": "你现在主要是还没想清 Trie 节点到底该存什么。",
            "key_bridge": "关键是节点上要记录一些计数。",
            "visual_hint": "101\n100\n11\n节点上记个数",
            "guided_walkthrough": "1. 先看节点。\n2. 再看计数。",
            "try_now": "先说清节点上的计数什么意思。",
            "next_step": "先说清节点上的计数什么意思。",
            "transfer_signal": "看到前缀就想到计数。",
            "core_design_subtags": [],
        }

        guarded = review_engine._guard_review_bridge_consistency(
            review.copy(),
            focus="shared_prefix_merging",
            problem_title="P2922 [USACO08DEC] Secret Message G",
            problem_context="很多消息串，反复查询拦截串的前缀关系，消息和拦截条数都很多。",
            bottleneck_text="我不知道为什么经过次数就够了，也不知道节点上到底该分清什么。",
        )

        combined = self._combined_review_fields(guarded)
        self.assertIn("经过次数", combined)
        self.assertIn("结束次数", combined)
        self.assertTrue(any(term in combined for term in ("前缀", "沿前缀路径", "公共前缀")), combined)

    def test_guard_review_bridge_consistency_should_rewrite_generic_check_condition_fields(self):
        review = {
            "error_layer": "method",
            "problem_focus": "你现在主要是还没理解这个方法。",
            "main_block": "你现在主要是还没理解这个方法。",
            "key_bridge": "关键是先理解这个条件。",
            "visual_hint": "先理解这个条件\n-> 再继续",
            "guided_walkthrough": "1. 先理解思路。\n2. 再继续推。",
            "try_now": "先想一想这个条件。",
            "next_step": "先想一想这个条件。",
            "transfer_signal": "下次先想条件。",
            "core_design_subtags": [],
        }

        guarded = review_engine._guard_review_bridge_consistency(
            review.copy(),
            focus="check_condition",
            problem_title="P2678 跳石头",
            problem_context="二分答案，check(mid) 判断删掉一些石头后最小间距是否仍能达到 mid。",
            bottleneck_text="我不知道 check(mid) 返回 true 时到底表示什么，也不知道区间该往哪边缩。",
        )

        combined = self._combined_review_fields(guarded)
        self.assertIn("check(mid)", combined)
        self.assertIn("可行", combined)
        self.assertTrue(
            any(term in combined for term in ("返回 true", "当前 mid", "check(", "二分")),
            combined,
        )

    def test_guard_review_bridge_consistency_should_keep_left_bound_update_local(self):
        review = {
            "error_layer": "implementation",
            "problem_focus": "你现在主要是二分边界没想清楚。",
            "main_block": "你现在主要是二分边界没想清楚。",
            "key_bridge": "关键是理解二分怎么缩边界。",
            "visual_hint": "二分区间\n-> 继续缩小",
            "guided_walkthrough": "1. 先看 mid。\n2. 再缩边界。",
            "try_now": "先试着缩一下边界。",
            "next_step": "先试着缩一下边界。",
            "transfer_signal": "看到二分就先想边界。",
            "core_design_subtags": ["check_condition"],
        }

        guarded = review_engine._guard_review_bridge_consistency(
            review.copy(),
            focus="left_bound_update",
            problem_title="P2249 查找",
            problem_context="在有序数组里找第一个等于 x 的位置。",
            bottleneck_text="我会二分，但 a[mid] == x 时总不知道该写 r = mid 还是 r = mid - 1。",
        )

        combined = self._combined_review_fields(guarded)
        self.assertIn("a[mid]", combined)
        self.assertTrue(
            any(term in combined for term in ("保留 mid", "最左", "左边界", "候选")),
            combined,
        )
        self.assertTrue(
            any(term in combined for term in ("a[mid] == ", "a[mid] == x", "继续往左找")),
            combined,
        )

    def test_guard_review_bridge_consistency_should_keep_method_selection_on_signal_language(self):
        review = {
            "error_layer": "method",
            "problem_focus": "你现在主要是还没想清为什么 trie 查询快。",
            "main_block": "你现在主要是还没想清为什么 trie 查询快。",
            "key_bridge": "关键是公共前缀先合在一起。",
            "visual_hint": "101\n100\n11\n前缀 10 先合在一起",
            "guided_walkthrough": "1. 先看公共前缀。\n2. 再想查询路径。",
            "try_now": "先说清为什么不用重看所有消息。",
            "next_step": "先说清为什么不用重看所有消息。",
            "transfer_signal": "看到前缀就想到 trie。",
            "core_design_subtags": [],
        }

        guarded = review_engine._guard_review_bridge_consistency(
            review.copy(),
            focus="method_selection",
            problem_title="P2922 [USACO08DEC] Secret Message G",
            problem_context="很多消息、很多拦截串，要反复判断前缀关系。",
            bottleneck_text="我总觉得这里应该用 trie，但说不清题面里到底哪个结构信号支持它。",
        )

        combined = self._combined_review_fields(guarded)
        self.assertIn("题面", combined)
        self.assertTrue(
            any(term in combined for term in ("结构信号", "题面信号", "相同开头", "前缀关系")),
            combined,
        )
        self.assertTrue(
            any(term in combined for term in ("trie", "前缀", "消息")),
            combined,
        )

    def test_guard_review_bridge_consistency_should_not_rewrite_non_trie_method_selection_to_trie_language(self):
        review = {
            "error_layer": "method",
            "problem_focus": "你现在主要是还没想清为什么这类活动要先按结束时间排序。",
            "main_block": "你现在主要是还没想清为什么这类活动要先按结束时间排序。",
            "key_bridge": "关键是先看哪些区间能接在后面。",
            "visual_hint": "区间按结束时间排好\n-> 再依次挑选",
            "guided_walkthrough": "1. 先按结束时间排序。\n2. 再挑能接上的区间。",
            "try_now": "先说清为什么要先看结束更早的区间。",
            "next_step": "先说清为什么要先看结束更早的区间。",
            "transfer_signal": "看到很多区间时先想结束时间。",
            "core_design_subtags": [],
        }

        guarded = review_engine._guard_review_bridge_consistency(
            review.copy(),
            focus="method_selection",
            problem_title="P1803 凌乱的yyy / 线段覆盖",
            problem_context="有很多区间，要求选出互不重叠的最多区间。常见做法是先按结束位置排序，再依次挑选能接上的区间。",
            bottleneck_text="我知道这是贪心，但说不清为什么这里要先选结束更早的那个。",
        )

        combined = self._combined_review_fields(guarded)
        self.assertNotIn("trie", combined.lower())
        self.assertNotIn("前缀", combined)
        self.assertNotIn("消息", combined)
        self.assertNotIn("拦截串", combined)
        self.assertNotIn("相同开头", combined)
        self.assertNotIn("前缀关系", combined)

    def test_generate_review_should_run_bridge_consistency_guard_on_first_review(self):
        llm_review = json.dumps(
            {
                "error_tags": ["方法选择"],
                "error_layer": "method",
                "error_layer_confidence": "high",
                "core_design_subtags": [],
                "diagnosis": "你现在主要是还没理解这个方法。",
                "next_action": "先回到题面。",
                "suggested_topic": "Trie",
                "problem_focus": "你现在主要是还没理解这个方法。",
                "main_block": "你现在主要是还没理解这个方法。",
                "key_bridge": "关键是先理解这个方法。",
                "visual_hint": "先理解这个方法\n-> 再继续",
                "guided_walkthrough": "1. 先理解思路。\n2. 再继续。",
                "try_now": "先想一想这个方法。",
                "next_step": "先想一想这个方法。",
                "transfer_signal": "下次先理解这个方法。",
            }
        )

        with patch.object(review_engine, "_call_llm", return_value=(True, llm_review, {})):
            result = review_engine.generate_review(
                problem_title="P2922 [USACO08DEC] Secret Message G",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我总觉得这里应该用 trie，但说不清题面里哪个信号真的支持它。",
                error_types=["方法选择"],
                problem_context="很多消息、很多拦截串，要反复判断前缀关系。",
        )

        review = result["review"]
        combined = self._combined_review_fields(review)
        self.assertTrue(
            any(term in combined for term in ("结构信号", "题面信号", "相同开头", "前缀关系")),
            combined,
        )
        self.assertTrue(any(term in combined for term in ("trie", "前缀", "消息")), combined)

    def test_generate_bridge_quiz_followup_should_shrink_greedy_basis_to_local_choice_reason(self):
        review_context = {
            "problem_title": "活动选择题",
            "problem_context": "每次要从多个活动里挑一个，目标是让后面还能留下尽可能多的空间。",
            "bottleneck_text": "我知道要贪心，但总说不清为什么这一步该先选当前这个对象。",
            "error_layer": "core_design",
            "core_design_subtags": ["greedy_basis"],
            "main_block": "你卡在局部优先的理由没站稳。",
            "key_bridge": "先说清为什么当前这个对象优先选不会破坏后面的结构。",
            "next_step": "先看这一步优先选它到底保住了什么。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果把题目换个小场景，这一步最需要保持不变的是什么？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("当前这个对象", payload["question_text"])
        self.assertTrue(
            any("后面" in option["label"] or "空间" in option["label"] or "结构" in option["label"] for option in payload["options"]),
            payload["options"],
        )
        self.assertNotIn("最需要保持不变", payload["question_text"])

    def test_detect_quiz_focus_should_map_tree_diameter_candidates_before_general_modeling(self):
        review_context = {
            "problem_title": "P2195 HXY造公园",
            "problem_context": "把两个休息点群用新边连起来后，要求新的最大距离。",
            "bottleneck_text": "这道题为什么会用到树的直径，两个不同的连通块之间不知道怎么去链接起来。",
            "error_layer": "core_design",
            "main_block": "你卡在新最长路候选怎么产生。",
            "key_bridge": "新最长路只会来自左边内部、右边内部、经过新边三种候选。",
            "next_step": "先判断经过新边时两端各该接什么点。",
        }

        self.assertEqual("tree_diameter_candidates", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_not_map_binary_search_candidate_word_to_tree_diameter(self):
        review_context = {
            "problem_title": "P2249 查找",
            "problem_context": "",
            "bottleneck_text": "我会写二分，但当 a[mid] == x 时，我总不知道应该把右边界收成 mid 还是 mid-1。",
            "error_layer": "core_design",
            "core_design_subtags": ["check_condition"],
            "main_block": "a[mid] 等于 x 时错误执行 r = mid - 1，应改为 r = mid 以保留当前候选位置继续向左查找。",
            "key_bridge": "相等时 mid 是合法候选但未必是第一个，需保留 mid 继续向左收缩。",
            "next_step": "手推 [4,5,5,5,6] 里 a[mid] == 5 时边界怎么变。",
        }

        self.assertEqual("left_bound_update", review_engine._detect_quiz_focus(review_context))

    def test_detect_quiz_focus_should_route_method_layer_check_semantics_to_check_condition(self):
        review_context = {
            "problem_title": "P2678 跳石头",
            "problem_context": "河长 L，去掉不超过 M 块石头，最大化最小跳跃距离。二分答案时要写 check(mid)。",
            "bottleneck_text": "我知道这是二分答案，但 check(mid) 返回 true 以后到底说明什么，我总是说不清。",
            "error_layer": "method",
            "main_block": "你卡在 check(mid) 的职责没站稳。",
            "key_bridge": "check(mid) 语义不清导致二分查找方向可能写反，把可行解当成不可行解排除。",
            "next_step": "先说清 check(mid) 返回 true 时说明当前 mid 可行。",
        }

        self.assertEqual("check_condition", review_engine._detect_quiz_focus(review_context))

    def test_generate_bridge_quiz_main_should_keep_check_condition_for_method_layer_binary_search_case(self):
        review_context = {
            "problem_title": "P2678 跳石头",
            "problem_context": "河长 L，去掉不超过 M 块石头，最大化最小跳跃距离。二分答案时要写 check(mid)。",
            "bottleneck_text": "我知道这是二分答案，但 check(mid) 返回 true 以后到底说明什么，我总是说不清。",
            "error_layer": "method",
            "main_block": "你卡在 check(mid) 的职责没站稳。",
            "key_bridge": "check(mid) 语义不清导致二分查找方向可能写反，把可行解当成不可行解排除。",
            "next_step": "先说清 check(mid) 返回 true 时说明当前 mid 可行。",
        }

        payload = review_engine.generate_bridge_quiz(review_context, quiz_role=review_engine.QUIZ_ROLE_MAIN)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("check_condition", payload["meta"]["focus"])
        self.assertIn("check(mid)", payload["question_text"])
        self.assertNotIn("双层规模", payload["question_text"])

    def test_generate_bridge_quiz_followup_should_shrink_tree_diameter_candidates_to_cross_edge_case(self):
        review_context = {
            "problem_title": "P2195 HXY造公园",
            "problem_context": "把两个休息点群用新边连起来后，要求新的最大距离。",
            "bottleneck_text": "这道题为什么会用到树的直径，两个不同的连通块之间不知道怎么去链接起来。",
            "error_layer": "core_design",
            "main_block": "你卡在新最长路候选怎么产生。",
            "key_bridge": "新最长路只会来自左边内部、右边内部、经过新边三种候选。",
            "next_step": "先判断经过新边时两端各该接什么点。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果加上一条新边后，新的最长路更该先从下面哪几类候选里去想？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_bridge_quiz(
                review_context,
                previous_quiz=previous_quiz,
                quiz_role=review_engine.QUIZ_ROLE_FOLLOWUP,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("经过新边", payload["question_text"])
        self.assertNotIn("哪几类候选", payload["question_text"])
        self.assertTrue(
            any("连接点" in option["label"] or "最远点" in option["label"] for option in payload["options"]),
            payload["options"],
        )

    def test_generate_remedy_explanation_should_fallback_when_llm_fails(self):
        review_context = {
            "error_layer": "modeling",
            "bottleneck_text": "我不知道状态怎么定义。",
            "main_block": "你卡在状态没站稳。",
            "next_step": "先写状态含义。",
        }

        with patch.object(review_engine, "_call_llm", return_value=(False, "", {})):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertEqual("explain", payload["remedy_type"])
        self.assertEqual(review_engine.REMEDY_ACTION_DYNAMIC, payload["remedy_action"])
        self.assertTrue(payload["remedy_text"])
        self.assertTrue(payload["micro_action"])
        self.assertIn("visual_hint", payload)

    def test_generate_final_micro_confirm_quiz_should_stay_local_for_constraint_modeling(self):
        review_context = {
            "error_layer": "core_design",
            "problem_title": "链路联调题",
            "problem_context": "每个活动都必须同时满足时间窗口和指定地点两个条件。",
            "bottleneck_text": "我试着把条件改成不等式，但不知道每条边该怎么统一方向。",
            "main_block": "你卡在约束关系没有统一。",
            "key_bridge": "先把不等式约束改写成统一方向的边。",
            "next_step": "先把每条不等式改写成边。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_final_micro_confirm_quiz(review_context)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("choice", payload["quiz_type"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertEqual("final_micro_confirm", payload["meta"]["difficulty_level"])
        self.assertEqual("final_micro_confirm", payload["meta"]["confirm_mode"])
        self.assertTrue(payload["question_text"])
        self.assertGreaterEqual(len(payload["options"]), 3)

    def test_generate_final_micro_confirm_quiz_should_be_concrete_for_trie_method_selection(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "给定很多二进制信息和很多拦截串。对每个拦截串，需要统计有多少条信息满足前缀包含关系。信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。常见做法是用 trie 统计经过每个节点的信息数量。",
            "bottleneck_text": "这里为什么不能直接枚举，而是要用到 trie 树？",
            "error_layer": "method",
            "key_bridge": "先判断逐条比对是不是在重复重看很多条消息，再看 trie 为什么只沿当前前缀往下走。",
            "next_step": "先比较“重看很多条消息”和“只沿当前前缀走”这两个查询过程。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "第二轮：查一条串时会不会重看所有消息？",
            "correct_answer": "不会，会只沿当前前缀往下走",
        }

        payload = review_engine.generate_final_micro_confirm_quiz(
            review_context,
            previous_quiz=previous_quiz,
        )

        self.assertEqual("quiz", payload["mode"])
        self.assertIn("前缀", payload["question_text"])
        self.assertTrue(
            "所有消息" in payload["question_text"] or "往下走" in payload["question_text"],
            payload["question_text"],
        )
        self.assertNotIn("为什么该用这个方法", payload["question_text"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])

    def test_generate_final_micro_confirm_quiz_should_shrink_generic_method_selection_to_signal_confirmation(self):
        review_context = {
            "problem_title": "活动选择题",
            "problem_context": "给很多活动区间，要求选最多个互不重叠的活动。常见做法是按结束时间排序。",
            "bottleneck_text": "我知道要贪心，但还是说不清题面里哪个信号支持先按结束时间更早的来选。",
            "error_layer": "method",
            "key_bridge": "先找出题面里真正支持这种方法的结构信号。",
            "next_step": "先说清题面里的哪个结构信号在支持这种做法。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果这一步更像在找题面信号，下面哪种说法更贴近？",
            "correct_answer": "A",
        }

        payload = review_engine.generate_final_micro_confirm_quiz(
            review_context,
            previous_quiz=previous_quiz,
        )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertIn("题面", payload["question_text"])
        self.assertTrue(
            any(option["label"] in {"是", "不是"} for option in payload["options"])
            or any("结构信号" in option["label"] for option in payload["options"]),
            payload["options"],
        )

    def test_generate_final_micro_confirm_quiz_should_shrink_complexity_fit_to_atomic_scale_judgement(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "我总觉得先双层枚举一下也许还能撑住。",
            "error_layer": "method",
            "key_bridge": "先根据数据范围判断双层枚举会不会超时。",
            "next_step": "先判断这种规模下双层枚举是不是已经明显过大。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果只盯住规模这一步，下面哪种说法更贴近？",
            "correct_answer": "A",
        }

        payload = review_engine.generate_final_micro_confirm_quiz(
            review_context,
            previous_quiz=previous_quiz,
        )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertTrue(
            "双层" in payload["question_text"] or "超时" in payload["question_text"] or "规模" in payload["question_text"],
            payload["question_text"],
        )
        self.assertTrue(
            all(option["label"] in {"是", "不是"} for option in payload["options"])
            or any("超时" in option["label"] for option in payload["options"]),
            payload["options"],
        )

    def test_generate_final_micro_confirm_quiz_should_shrink_state_design_to_atomic_slot_check(self):
        review_context = {
            "problem_title": "P1434 滑雪",
            "problem_context": "给定一个高程矩阵，只能走到更低的格子，求最长滑行长度。",
            "bottleneck_text": "我知道是记忆化搜索，但 dp[x][y] 这一格到底表示什么，我总是说不清。",
            "error_layer": "core_design",
            "core_design_subtags": ["state_design"],
            "main_block": "你卡在 dp[x][y] 这一格到底记录什么。",
            "key_bridge": "先把 dp[x][y] 这一格的状态含义站稳。",
            "next_step": "先说清 dp[x][y] 表示什么。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果只盯住状态里“位置/阶段”这一维，下面哪种说法才真正把它讲清了？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_final_micro_confirm_quiz(
                review_context,
                previous_quiz=previous_quiz,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertNotEqual(previous_quiz["question_text"], payload["question_text"])
        self.assertTrue(
            "dp[x][y]" in payload["question_text"] or "这一格" in payload["question_text"],
            payload["question_text"],
        )
        self.assertNotIn("位置/阶段", payload["question_text"])
        self.assertTrue(
            any(option["label"] in {"是", "不是"} for option in payload["options"]),
            payload["options"],
        )

    def test_generate_final_micro_confirm_quiz_should_shrink_check_condition_to_yes_no(self):
        review_context = {
            "problem_title": "二分判定题",
            "problem_context": "需要二分答案，并写 check(mid) 判断当前 mid 是否可行。",
            "bottleneck_text": "我老是不知道 check(mid) 返回 true 到底在说明什么。",
            "error_layer": "core_design",
            "core_design_subtags": ["check_condition"],
            "main_block": "你卡在 check(mid) 的职责没站稳。",
            "key_bridge": "先把 check(mid) 返回 true 时说明什么说清楚。",
            "next_step": "先说清 check(mid) 判的是可行性，不是直接求答案。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果只盯住 `check(mid)` 这一小步，`check(mid)` 返回 true 时更贴近下面哪种说法？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_final_micro_confirm_quiz(
                review_context,
                previous_quiz=previous_quiz,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertIn("返回 true", payload["question_text"])
        self.assertTrue(
            all(option["label"] in {"是", "不是"} for option in payload["options"]),
            payload["options"],
        )

    def test_generate_final_micro_confirm_quiz_should_shrink_enumeration_order_to_yes_no(self):
        review_context = {
            "problem_title": "背包顺序题",
            "problem_context": "一维背包里，当前状态会用到前一个容量位置已经算好的结果。",
            "bottleneck_text": "我知道和顺序有关，但总说不清为什么这一层必须倒着枚举。",
            "error_layer": "core_design",
            "core_design_subtags": ["enumeration_order"],
            "main_block": "你卡在枚举顺序为什么必须服从依赖。",
            "key_bridge": "先说清谁依赖谁，再决定哪一维先枚举。",
            "next_step": "先看当前状态是不是要用前一个已经算好的状态。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果当前这一格要用到前一个已经算好的状态，下面哪种顺序更稳？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_final_micro_confirm_quiz(
                review_context,
                previous_quiz=previous_quiz,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertNotEqual(previous_quiz["question_text"], payload["question_text"])
        self.assertIn("前一个状态", payload["question_text"])
        self.assertTrue(
            all(option["label"] in {"是", "不是"} for option in payload["options"]),
            payload["options"],
        )

    def test_generate_final_micro_confirm_quiz_should_shrink_transition_design_to_yes_no(self):
        review_context = {
            "problem_title": "区间转移题",
            "problem_context": "当前状态可能从左侧合并过来，也可能从上一步延续过来。",
            "bottleneck_text": "我每次写转移都只想到一种最顺手的来源，老是漏情况。",
            "error_layer": "core_design",
            "core_design_subtags": ["transition_design"],
            "main_block": "你卡在转移来源容易漏掉一支。",
            "key_bridge": "先把当前状态可能从哪些合法来源转过来想全。",
            "next_step": "先检查当前状态会不会有两类前态来源。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果当前状态可能有两类合法来源，下面哪种做法更稳？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_final_micro_confirm_quiz(
                review_context,
                previous_quiz=previous_quiz,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertIn("合法来源", payload["question_text"])
        self.assertTrue(
            all(option["label"] in {"是", "不是"} for option in payload["options"]),
            payload["options"],
        )

    def test_generate_final_micro_confirm_quiz_should_shrink_greedy_basis_to_yes_no(self):
        review_context = {
            "problem_title": "活动选择题",
            "problem_context": "每次要从多个活动里挑一个，目标是让后面还能留下尽可能多的空间。",
            "bottleneck_text": "我知道要贪心，但总说不清为什么这一步该先选当前这个对象。",
            "error_layer": "core_design",
            "core_design_subtags": ["greedy_basis"],
            "main_block": "你卡在局部优先的理由没站稳。",
            "key_bridge": "先说清为什么当前这个对象优先选不会破坏后面的结构。",
            "next_step": "先看这一步优先选它到底保住了什么。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果当前这个对象更优先，下面哪种理由更稳？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_final_micro_confirm_quiz(
                review_context,
                previous_quiz=previous_quiz,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertIn("优先选当前这个对象", payload["question_text"])
        self.assertTrue(
            all(option["label"] in {"是", "不是"} for option in payload["options"]),
            payload["options"],
        )

    def test_generate_final_micro_confirm_quiz_should_shrink_tree_diameter_candidates_to_yes_no(self):
        review_context = {
            "problem_title": "P2195 HXY造公园",
            "problem_context": "把两个休息点群用新边连起来后，要求新的最大距离。",
            "bottleneck_text": "这道题为什么会用到树的直径，两个不同的连通块之间不知道怎么去链接起来。",
            "error_layer": "core_design",
            "main_block": "你卡在新最长路候选怎么产生。",
            "key_bridge": "新最长路只会来自左边内部、右边内部、经过新边三种候选。",
            "next_step": "先判断经过新边时两端各该接什么点。",
        }
        previous_quiz = {
            "quiz_type": "choice",
            "question_text": "如果最长路经过新边，两端更该接到什么样的点？",
            "correct_answer": "A",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_final_micro_confirm_quiz(
                review_context,
                previous_quiz=previous_quiz,
            )

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("final_micro_confirm", payload["difficulty_level"])
        self.assertIn("经过新边", payload["question_text"])
        self.assertTrue(
            all(option["label"] in {"是", "不是"} for option in payload["options"]),
            payload["options"],
        )

    def test_generate_knowledge_bailout_card_should_return_two_part_card_for_state_design(self):
        review_context = {
            "problem_title": "P1434 滑雪",
            "problem_context": "给定一个高程矩阵，只能走到更低的格子，求最长滑行长度。",
            "bottleneck_text": "我知道是记忆化搜索，但 dp[x][y] 这一格到底表示什么，我总是说不清。",
            "error_layer": "core_design",
            "core_design_subtags": ["state_design"],
            "key_bridge": "先把 dp[x][y] 这一格的状态含义站稳。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "state_design", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("dp.state_design", card["card_id"])
        self.assertIn("刚才已经试了几种方式", card["opening"])
        self.assertIn("dp[x][y]", card["bridge_explanation"])
        self.assertIn("状态格", card["visual_hint"])
        self.assertIn("子问题结果", card["algorithm_overview"])
        self.assertTrue(card["algorithm_overview"])
        self.assertTrue(card["micro_action"])

    def test_generate_knowledge_bailout_card_should_blend_external_snippet_for_state_design(self):
        review_context = {
            "focus": "state_design",
            "problem_title": "P1434 滑雪",
            "problem_context": "给定一个高程矩阵，只能走到更低的格子，求最长滑行长度。",
            "bottleneck_text": "我总说不清 dp[x][y] 这一格到底表示什么。",
            "error_layer": "core_design",
            "key_bridge": "先把状态格里存的子问题结果说清楚。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("dp.state_design", card["card_id"])
        self.assertIn("最容易误会", card["bridge_explanation"])
        self.assertIn("状态", card["bridge_explanation"])
        self.assertIn("子问题", card["algorithm_overview"])

    def test_generate_knowledge_bailout_card_should_trust_explicit_focus_when_context_is_sparse(self):
        review_context = {
            "focus": "state_design",
            "key_bridge": "先把 dp[x][y] 这一格的状态含义站稳。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("dp.state_design", card["card_id"])
        self.assertIn("dp[x][y]", card["bridge_explanation"])

    def test_generate_knowledge_bailout_card_should_return_transition_design_card_with_source_language(self):
        review_context = {
            "problem_title": "P1216 数字三角形",
            "problem_context": "每个位置只能从上一层相邻位置转来，求最大路径和。",
            "bottleneck_text": "我知道要转移，但总会漏掉当前格子能从哪些位置过来。",
            "error_layer": "core_design",
            "core_design_subtags": ["transition_design"],
            "key_bridge": "先把当前状态可能来自哪几类前态想全。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "transition_design", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("dp.transition_design", card["card_id"])
        self.assertIn("来源", card["bridge_explanation"])
        self.assertIn("前态", card["algorithm_overview"])
        self.assertIn("前态", card["micro_action"])
        self.assertIn("当前格", card["visual_hint"])
        self.assertIn("(i-1,j)", card["visual_hint"])

    def test_generate_knowledge_bailout_card_should_return_check_condition_card_with_true_meaning(self):
        review_context = {
            "problem_title": "P2678 跳石头",
            "problem_context": "要判断最小跳跃距离是否可行，并据此二分答案。",
            "bottleneck_text": "我总分不清 check(mid) 返回 true 到底是在说什么。",
            "error_layer": "core_design",
            "core_design_subtags": ["check_condition"],
            "key_bridge": "先把 check(mid) 的 true 到底表示什么站稳。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "check_condition", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("binary_search.check_condition", card["card_id"])
        self.assertIn("mid", card["bridge_explanation"])
        self.assertIn("可行", card["algorithm_overview"])
        self.assertIn("true", card["micro_action"])
        self.assertIn("check(5)=true", card["algorithm_overview"])
        self.assertIn("check(5)=true", card["visual_hint"])

    def test_generate_knowledge_bailout_card_should_blend_external_snippet_for_check_condition(self):
        review_context = {
            "focus": "check_condition",
            "problem_title": "P2678 跳石头",
            "problem_context": "要判断最小跳跃距离是否可行，并据此二分答案。",
            "bottleneck_text": "我老是分不清 check(mid) 到底在验证什么。",
            "error_layer": "core_design",
            "key_bridge": "先把 check(mid) 的 true 只说明当前 mid 可行这件事站稳。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("binary_search.check_condition", card["card_id"])
        self.assertIn("某个值可不可行", card["bridge_explanation"])

    def test_generate_knowledge_bailout_card_should_return_greedy_card_with_choice_language(self):
        review_context = {
            "problem_title": "P1803 凌乱的yyy",
            "problem_context": "给定很多区间，要求选出最多个互不重叠的区间。",
            "bottleneck_text": "我知道好像要贪心，但不知道为什么先选这个区间不会吃亏。",
            "error_layer": "core_design",
            "core_design_subtags": ["greedy_basis"],
            "key_bridge": "先说明当前这个对象为什么不会把后面堵死。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "greedy_basis", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("greedy.greedy_basis", card["card_id"])
        self.assertIn("不会吃亏", card["bridge_explanation"])
        self.assertIn("局部最优", card["algorithm_overview"])
        self.assertIn("堵死", card["micro_action"])
        self.assertIn("[1,3]", card["visual_hint"])
        self.assertIn("[3,5]", card["visual_hint"])

    def test_generate_knowledge_bailout_card_should_return_scale_estimation_card(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "我没有先算规模，总觉得双层枚举也许还能过。",
            "error_layer": "method",
            "key_bridge": "先根据数据范围判断双层枚举会不会超时。",
            "next_step": "先比较双层规模和时间限制。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "complexity_fit", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("modeling.scale_estimation", card["card_id"])
        self.assertIn("刚才已经试了几种方式", card["opening"])
        self.assertTrue("两层" in card["bridge_explanation"] or "双层枚举" in card["bridge_explanation"])
        self.assertIn("最容易误会", card["bridge_explanation"])
        self.assertIn("真正要站稳", card["bridge_explanation"])
        self.assertIn("双层枚举", card["algorithm_overview"])
        self.assertTrue(card["algorithm_overview"])
        self.assertTrue(card["micro_action"])

    def test_generate_knowledge_bailout_card_should_return_tree_diameter_card(self):
        review_context = {
            "problem_title": "P2195 HXY造公园",
            "problem_context": "把两个休息点群用新边连起来后，要求新的最大距离。",
            "bottleneck_text": "这道题为什么会用到树的直径，两个不同的连通块之间不知道怎么去链接起来。",
            "error_layer": "core_design",
            "main_block": "你卡在新最长路候选怎么产生。",
            "key_bridge": "新最长路只会来自左边内部、右边内部、经过新边三种候选。",
            "next_step": "先判断经过新边时两端各该接什么点。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "tree_diameter_candidates", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("graph.tree_diameter.tree_diameter_candidates", card["card_id"])
        self.assertTrue("新边" in card["bridge_explanation"] or "最长路" in card["bridge_explanation"])
        self.assertIn("三类候选", card["algorithm_overview"])
        self.assertTrue(card["algorithm_overview"])
        self.assertTrue(card["micro_action"])
        self.assertIn("左边最远点", card["visual_hint"])
        self.assertIn("右边最远点", card["visual_hint"])

    def test_generate_knowledge_bailout_card_should_return_tree_path_difference_card(self):
        review_context = self._p3128_tree_path_difference_review_context()
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "tree_path_difference", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("graph.tree_path_difference", card["card_id"])
        self.assertIn("LCA", card["bridge_explanation"])
        self.assertIn("差分标记", card["bridge_explanation"])
        self.assertIn("DFS", card["algorithm_overview"])
        self.assertIn("s += 1", card["visual_hint"])
        self.assertIn("parent(lca)", card["visual_hint"])
        self.assertTrue(card["micro_action"])

    def test_generate_knowledge_bailout_card_should_return_method_selection_card_with_signal_language(self):
        review_context = {
            "problem_title": "P3372 线段树 1",
            "problem_context": "需要多次区间加和区间求和。",
            "bottleneck_text": "我总想直接套以前见过的方法，但不知道这题为什么真的是这个方法。",
            "error_layer": "method",
            "key_bridge": "先找题面里真正支持这个方法的结构信号。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "method_selection", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("modeling.method_selection", card["card_id"])
        self.assertIn("题面", card["bridge_explanation"])
        self.assertIn("结构信号", card["bridge_explanation"])
        self.assertIn("最容易误会", card["bridge_explanation"])
        self.assertIn("真正要站稳", card["bridge_explanation"])
        self.assertIn("先读题面信号", card["algorithm_overview"])
        self.assertIn("信号", card["micro_action"])

    def test_generate_knowledge_bailout_card_should_keep_trie_method_selection_on_method_card(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "给很多消息和拦截串，需要统计前缀关系。",
            "bottleneck_text": "我总是先猜要用 trie，但说不清题面里到底哪个信号支持它。",
            "error_layer": "method",
            "key_bridge": "先找题面里真正支持 trie 的结构信号。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "method_selection", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("modeling.method_selection", card["card_id"])
        self.assertIn("相同开头", card["algorithm_overview"])
        self.assertIn("合在一起", card["algorithm_overview"])
        self.assertIn("101", card["algorithm_overview"])
        self.assertIn("101", card["visual_hint"])
        self.assertIn("支持 trie", card["visual_hint"])

    def test_generate_knowledge_bailout_card_should_route_explicit_shared_prefix_focus_to_trie_card(self):
        review_context = {
            "focus": "shared_prefix_merging",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "bottleneck_text": "我不懂为什么查询时不用重看所有消息，只沿当前前缀往下走。",
            "error_layer": "method",
            "key_bridge": "公共前缀先合在一起，所以查询时只沿当前前缀路径走。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("string.trie.shared_prefix_merging", card["card_id"])

    def test_generate_knowledge_bailout_card_should_return_trie_card_with_prefix_merging_language(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "为什么这里不能直接枚举，而是要用 trie？",
            "error_layer": "method",
            "key_bridge": "先看公共前缀能不能先合并，再看查询是不是还在重看所有消息。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "method_selection", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("string.trie.shared_prefix_merging", card["card_id"])
        self.assertEqual("string.trie.shared_prefix_merging", card["knowledge_card_id"])
        self.assertIn("公共前缀", card["bridge_explanation"])
        self.assertIn("重看所有消息", card["bridge_explanation"])
        self.assertIn("相同开头", card["algorithm_overview"])
        self.assertIn("重看所有消息", card["micro_action"])

    def test_generate_knowledge_bailout_card_should_blend_external_snippet_for_shared_prefix_merging(self):
        review_context = {
            "focus": "shared_prefix_merging",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "很多消息和拦截串，问题反复围绕前缀关系展开。",
            "bottleneck_text": "我不懂为什么查询时不用把所有消息重新逐个比一遍。",
            "error_layer": "method",
            "key_bridge": "相同前缀是不是值得先合起来看。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("string.trie.shared_prefix_merging", card["card_id"])
        self.assertIn("相同前缀", card["bridge_explanation"])
        self.assertIn("重新逐个看一遍", card["algorithm_overview"])
        self.assertIn("101", card["algorithm_overview"])
        self.assertIn("最容易误会", card["bridge_explanation"])
        self.assertIn("101", card["visual_hint"])
        self.assertIn("前缀 10", card["visual_hint"])

    def test_generate_knowledge_bailout_card_should_explain_trie_node_count_semantics(self):
        review_context = {
            "focus": "shared_prefix_merging",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "需要统计前缀关系，学生卡在 trie 节点到底该存什么。",
            "bottleneck_text": "我不知道经过次数为什么就能回答查询。",
            "error_layer": "core_design",
            "key_bridge": "先说清经过次数记录了多少消息经过当前前缀节点。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("string.trie.shared_prefix_merging", card["card_id"])
        self.assertIn("经过次数", card["bridge_explanation"])
        self.assertIn("经过次数", card["algorithm_overview"])
        self.assertIn("前缀 10 这个节点", card["visual_hint"])
        self.assertIn("结束次数另算", card["visual_hint"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_trie_shared_prefix(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "对每个拦截串，需要统计有多少条信息满足前缀包含关系。信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "这里为什么不能直接枚举，而是要用到 trie 树？",
            "error_layer": "method",
            "key_bridge": "先判断逐条比对是不是在重复重看很多条消息，再看 trie 为什么只沿当前前缀往下走。",
        }
        card = {
            "card_id": "string.trie.shared_prefix_merging",
            "target_bridge": "trie 查询时不用重看所有消息，而是沿当前前缀往下走。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertIn("前缀", payload["question_text"])
        self.assertIn("重看所有消息", payload["bridge_feedback"])
        self.assertTrue(payload["meta"]["knowledge_bailout"])
        self.assertEqual("string.trie.shared_prefix_merging", payload["meta"]["knowledge_card_id"])

    def test_generate_knowledge_confirm_quiz_should_focus_on_trie_node_count_semantics_when_context_mentions_it(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "需要统计前缀关系。",
            "bottleneck_text": "我不知道为什么经过次数就够了。",
            "key_bridge": "先说清经过次数记录了多少消息经过当前前缀节点。",
        }
        card = {
            "card_id": "string.trie.shared_prefix_merging",
            "target_bridge": "先说清经过次数为什么能回答前缀查询。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertIn("经过次数", payload["question_text"])
        self.assertTrue(any("经过当前前缀节点" in option["label"] for option in payload["options"]), payload["options"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_scale_estimation(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "我没有先算规模，总觉得双层枚举也许还能过。",
            "error_layer": "method",
            "key_bridge": "先根据数据范围判断双层枚举会不会超时。",
        }
        card = {
            "card_id": "modeling.scale_estimation",
            "target_bridge": "先根据数据范围判断双层枚举会不会超时。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertTrue(
            "规模" in payload["question_text"] or "超时" in payload["question_text"] or "双层枚举" in payload["question_text"],
            payload["question_text"],
        )
        self.assertIn("双层枚举", payload["bridge_feedback"])
        self.assertTrue(payload["meta"]["knowledge_bailout"])
        self.assertEqual("modeling.scale_estimation", payload["meta"]["knowledge_card_id"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_method_selection(self):
        review_context = {
            "problem_title": "P3372 线段树 1",
            "problem_context": "需要多次区间加和区间求和。",
            "bottleneck_text": "我总想直接套以前见过的方法，但不知道这题为什么真的是这个方法。",
            "error_layer": "method",
            "key_bridge": "先找题面里真正支持这个方法的结构信号。",
        }
        card = {
            "card_id": "modeling.method_selection",
            "target_bridge": "先找题面里真正支持这个方法的结构信号。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertIn("题面", payload["question_text"])
        self.assertIn("信号", payload["bridge_feedback"])
        self.assertTrue(payload["meta"]["knowledge_bailout"])
        self.assertEqual("modeling.method_selection", payload["meta"]["knowledge_card_id"])

    def test_generate_knowledge_confirm_quiz_should_bridge_trie_method_selection_toward_shared_prefix(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "很多消息串，反复查询拦截串的前缀关系，消息和拦截条数都很多。",
            "bottleneck_text": "我知道这题该用 trie，但我说不清为什么很多消息有相同开头这件事重要。",
            "error_layer": "method",
            "key_bridge": "先找题面里真正支持 trie 的结构信号，再过渡到相同开头值不值得先合在一起看。",
        }
        card = {
            "card_id": "modeling.method_selection",
            "target_bridge": "先找题面里真正支持 trie 的信号，再补一句为什么很多消息相同开头值得先合在一起看。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertIn("相同开头", payload["question_text"])
        self.assertIn("支持 trie", payload["bridge_feedback"])
        self.assertTrue(
            any("相同开头" in option["label"] or "合在一起看" in option["label"] for option in payload["options"]),
            payload["options"],
        )
        self.assertEqual("modeling.method_selection", payload["meta"]["knowledge_card_id"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_state_design(self):
        review_context = {
            "problem_title": "P1434 滑雪",
            "problem_context": "给定一个高程矩阵，只能走到更低的格子，求最长滑行长度。",
            "bottleneck_text": "我知道是记忆化搜索，但 dp[x][y] 这一格到底表示什么，我总是说不清。",
            "error_layer": "core_design",
            "key_bridge": "先把 dp[x][y] 这一格的状态含义站稳。",
        }
        card = {
            "card_id": "dp.state_design",
            "target_bridge": "先把 dp[x][y] 这一格存的子问题结果站稳。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertIn("dp[x][y]", payload["question_text"])
        self.assertIn("子问题结果", payload["bridge_feedback"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_transition_design(self):
        review_context = {
            "problem_title": "P1216 数字三角形",
            "problem_context": "每个位置只能从上一层相邻位置转来，求最大路径和。",
            "bottleneck_text": "我知道要转移，但总会漏掉当前格子能从哪些位置过来。",
            "error_layer": "core_design",
            "key_bridge": "先把当前状态可能来自哪几类前态想全。",
        }
        card = {
            "card_id": "dp.transition_design",
            "target_bridge": "先把当前状态可能来自哪几类前态想全。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertTrue("来源" in payload["question_text"] or "前态" in payload["question_text"], payload["question_text"])
        self.assertIn("来源", payload["bridge_feedback"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_check_condition(self):
        review_context = {
            "problem_title": "P2678 跳石头",
            "problem_context": "要判断最小跳跃距离是否可行，并据此二分答案。",
            "bottleneck_text": "我总分不清 check(mid) 返回 true 到底是在说什么。",
            "error_layer": "core_design",
            "key_bridge": "先把 check(mid) 的 true 到底表示什么站稳。",
        }
        card = {
            "card_id": "binary_search.check_condition",
            "target_bridge": "先把 check(mid) 返回 true 表示当前这个 mid 可行站稳。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertIn("check(mid)", payload["question_text"])
        self.assertIn("mid 可行", payload["bridge_feedback"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_greedy_basis(self):
        review_context = {
            "problem_title": "P1803 凌乱的yyy",
            "problem_context": "给定很多区间，要求选出最多个互不重叠的区间。",
            "bottleneck_text": "我知道好像要贪心，但不知道为什么先选这个区间不会吃亏。",
            "error_layer": "core_design",
            "key_bridge": "先说明当前这个对象为什么不会把后面堵死。",
        }
        card = {
            "card_id": "greedy.greedy_basis",
            "target_bridge": "先说明当前对象为什么不吃亏。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertTrue("先选" in payload["question_text"] or "对象" in payload["question_text"], payload["question_text"])
        self.assertIn("不吃亏", payload["bridge_feedback"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_tree_diameter_candidates(self):
        review_context = {
            "problem_title": "P2195 HXY造公园",
            "problem_context": "把两个休息点群用新边连起来后，要求新的最大距离。",
            "bottleneck_text": "这道题为什么会用到树的直径，两个不同的连通块之间不知道怎么去链接起来。",
            "error_layer": "core_design",
            "key_bridge": "新最长路只会来自左边内部、右边内部、经过新边三种候选。",
        }
        card = {
            "card_id": "graph.tree_diameter.tree_diameter_candidates",
            "target_bridge": "新最长路只会来自左边内部、右边内部、经过新边三种候选。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertTrue(
            "经过新边" in payload["question_text"] or "最长路" in payload["question_text"] or "候选" in payload["question_text"],
            payload["question_text"],
        )
        self.assertTrue(payload["meta"]["knowledge_bailout"])
        self.assertEqual("graph.tree_diameter.tree_diameter_candidates", payload["meta"]["knowledge_card_id"])

    def test_generate_knowledge_confirm_quiz_should_be_concrete_for_tree_path_difference(self):
        review_context = self._p3128_tree_path_difference_review_context()
        card = {
            "card_id": "graph.tree_path_difference",
            "focus": "tree_path_difference",
            "target_bridge": "路径贡献先变成端点/LCA 附近的差分标记，最后 DFS 汇总。",
        }

        payload = review_engine.generate_knowledge_confirm_quiz(review_context, card)

        combined = " ".join([payload["question_text"], payload["bridge_feedback"], " ".join(option["label"] for option in payload["options"])])
        self.assertEqual("quiz", payload["mode"])
        self.assertEqual("knowledge_confirm", payload["difficulty_level"])
        self.assertEqual("tree_path_difference", payload["meta"]["focus"])
        self.assertIn("P3128", combined)
        self.assertIn("LCA", combined)
        self.assertIn("DFS", combined)
        self.assertTrue(payload["meta"]["knowledge_bailout"])
        self.assertEqual("graph.tree_path_difference", payload["meta"]["knowledge_card_id"])

    def test_generate_knowledge_bailout_card_should_support_lazy_semantics(self):
        review_context = {
            "focus": "lazy_semantics",
            "problem_title": "P3372 线段树 1",
            "bottleneck_text": "我不明白 lazy 标记到底表示什么。",
            "error_layer": "core_design",
            "key_bridge": "lazy 记录的是还没下传的信息，不是还没执行完的代码。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("knowledge_card", card["mode"])
        self.assertEqual("segment_tree.lazy_semantics", card["card_id"])
        self.assertIn("这段区间已经确定要加上这笔更新", card["bridge_explanation"])
        self.assertIn("区间信息", card["algorithm_overview"])
        self.assertIn("[1,4]", card["algorithm_overview"])
        self.assertIn("3×2", card["algorithm_overview"])
        self.assertIn("[1,4]", card["visual_hint"])
        self.assertIn("lazy=3", card["visual_hint"])
        self.assertIn("3×2", card["visual_hint"])

    def test_generate_knowledge_bailout_card_should_blend_external_snippet_for_left_bound_update(self):
        review_context = {
            "focus": "left_bound_update",
            "problem_title": "P2249 查找",
            "problem_context": "在有序数组里查某个值第一次出现的位置。",
            "bottleneck_text": "我不知道 a[mid] == x 时为什么还要保留 mid。",
            "error_layer": "core_design",
            "key_bridge": "如果目标是最左位置，中点满足时也要先留作候选。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("binary_search.left_bound", card["card_id"])
        self.assertIn("最容易误会", card["bridge_explanation"])
        self.assertIn("最左", card["bridge_explanation"])
        self.assertIn("候选", card["bridge_explanation"])
        self.assertIn("[1,2,2,2,3]", card["visual_hint"])
        self.assertIn("r = mid", card["visual_hint"])

    def test_normalize_review_should_realign_lazy_semantics_from_bridge_text(self):
        parsed = {
            "error_tags": ["线段树"],
            "error_layer": "core_design",
            "error_layer_confidence": "medium",
            "core_design_subtags": ["state_design"],
            "diagnosis": "把 lazy 当成代码流程。",
            "next_action": "先画根节点。",
            "suggested_topic": "lazy",
            "problem_focus": "lazy 标记在节点上到底记录什么具体数值。",
            "main_block": "lazy 标记在节点上到底记录什么具体数值。",
            "key_bridge": "lazy 记录的是还没下传的信息，不是状态格定义。",
            "visual_hint": "根节点 lazy=5",
            "guided_walkthrough": "1. 看根节点。2. 看 sum。3. 看子节点。",
            "try_now": "说清根节点的 lazy 表示什么。",
            "next_step": "说清根节点的 lazy 表示什么。",
            "transfer_signal": "看到区间加和区间求和，要先怀疑 lazy 标记。",
        }

        review = review_engine._normalize_review(parsed)

        self.assertEqual(["lazy_semantics"], review["core_design_subtags"])

    def test_backfill_student_guidance_should_fill_method_selection_with_signal_specific_language(self):
        review = {
            "error_layer": "method",
            "focus": "method_selection",
            "problem_focus": "",
            "main_block": "",
            "key_bridge": "",
            "guided_walkthrough": "",
            "try_now": "",
            "next_step": "",
            "transfer_signal": "",
            "visual_hint": "",
        }

        filled = review_engine._backfill_student_guidance(review)

        self.assertIn("结构信号", filled["key_bridge"])
        self.assertIn("题面", filled["try_now"])

    def test_generate_remedy_explanation_should_stay_local_for_complexity_fit(self):
        review_context = {
            "focus": "complexity_fit",
            "error_layer": "method",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "我没有先算规模，总觉得双层枚举也许还能过。",
            "main_block": "你卡在还没先估总量级。",
            "key_bridge": "先根据数据范围判断双层枚举会不会超时。",
            "next_step": "先把会一起变大的量圈出来，再估总量级。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("总量级", payload["remedy_text"])
        self.assertIn("双层枚举", payload["remedy_text"])
        self.assertIn("规模", payload["micro_action"])

    def test_generate_remedy_explanation_should_stay_local_for_method_selection(self):
        review_context = {
            "focus": "method_selection",
            "error_layer": "method",
            "problem_title": "P3372 线段树 1",
            "problem_context": "需要多次区间加和区间求和。",
            "bottleneck_text": "我总想直接套以前见过的方法，但不知道这题为什么真的是这个方法。",
            "main_block": "你卡在还没先抓题面里的结构信号。",
            "key_bridge": "先找题面里真正支持这个方法的结构信号。",
            "next_step": "先指出题面里一个真正支持当前方法的信号。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("结构信号", payload["remedy_text"])
        self.assertIn("题面", payload["remedy_text"])
        self.assertIn("信号", payload["micro_action"])

    def test_generate_remedy_explanation_should_bridge_trie_method_selection_toward_shared_prefix(self):
        review_context = {
            "focus": "method_selection",
            "error_layer": "method",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "给很多消息和拦截串，需要统计前缀关系。",
            "bottleneck_text": "我总是先猜要用 trie，但说不清题面里到底哪个信号支持它。",
            "main_block": "你卡在还没先抓题面里的结构信号。",
            "key_bridge": "先找题面里真正支持 trie 的结构信号。",
            "next_step": "先指出题面里一个真正支持当前方法的信号。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("相同开头", payload["remedy_text"])
        self.assertIn("合在一起", payload["remedy_text"])
        self.assertIn("相同开头", payload["visual_hint"])
        self.assertIn("相同开头", payload["micro_action"])

    def test_generate_remedy_explanation_should_stay_local_for_shared_prefix_merging(self):
        review_context = {
            "focus": "shared_prefix_merging",
            "error_layer": "method",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "给很多消息和拦截串，需要统计前缀关系。",
            "bottleneck_text": "我不懂为什么查询时不用重看所有消息，只沿当前前缀往下走。",
            "main_block": "你卡在 trie 查询机制这一步。",
            "key_bridge": "公共前缀先合在一起，所以查询时只沿当前前缀路径走。",
            "next_step": "先说清公共前缀为什么能先合在一起。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("公共前缀", payload["remedy_text"])
        self.assertIn("重看所有消息", payload["remedy_text"])
        self.assertIn("101", payload["remedy_text"])
        self.assertIn("前缀", payload["micro_action"])
        self.assertIn("101", payload["visual_hint"])
        self.assertIn("前缀 10", payload["visual_hint"])

    def test_generate_remedy_explanation_should_stay_local_for_tree_path_difference(self):
        review_context = self._p3128_tree_path_difference_review_context()

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("树剖", payload["remedy_text"])
        self.assertIn("LCA", payload["remedy_text"])
        self.assertIn("差分标记", payload["remedy_text"])
        self.assertIn("DFS", payload["remedy_text"])
        self.assertIn("s += 1", payload["visual_hint"])
        self.assertIn("lca -= 1", payload["visual_hint"])
        self.assertIn("端点/LCA", payload["micro_action"])

    def test_generate_remedy_explanation_should_explain_trie_node_count_semantics_when_context_mentions_it(self):
        review_context = {
            "focus": "shared_prefix_merging",
            "error_layer": "core_design",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "需要统计前缀关系。",
            "bottleneck_text": "我不知道节点上的经过次数为什么就够了。",
            "main_block": "你卡在 trie 节点该存什么信息这一步。",
            "key_bridge": "经过次数表示有多少消息经过当前前缀节点。",
            "next_step": "先说清经过次数为什么能直接回答前缀查询。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("经过次数", payload["remedy_text"])
        self.assertIn("当前前缀节点", payload["remedy_text"])
        self.assertIn("经过次数", payload["micro_action"])
        self.assertIn("前缀 10 这个节点", payload["visual_hint"])
        self.assertIn("结束次数另算", payload["visual_hint"])

    def test_generate_remedy_explanation_should_stay_local_for_lazy_semantics(self):
        review_context = {
            "focus": "lazy_semantics",
            "error_layer": "core_design",
            "problem_title": "P3372 线段树 1",
            "problem_context": "支持区间加和区间求和。",
            "bottleneck_text": "我不明白 lazy 标记到底表示什么。",
            "main_block": "你卡在 lazy 的语义没站稳。",
            "key_bridge": "lazy 记录的是还没下传的信息，不是还没执行完的代码。",
            "next_step": "先说清 lazy 标记到底记录什么。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("还没下传", payload["remedy_text"])
        self.assertIn("代码", payload["remedy_text"])
        self.assertIn("[1,4]", payload["remedy_text"])
        self.assertIn("lazy", payload["micro_action"])
        self.assertIn("[1,4]", payload["visual_hint"])
        self.assertIn("lazy=3", payload["visual_hint"])
        self.assertIn("3×2", payload["visual_hint"])

    def test_generate_remedy_explanation_should_blend_external_snippet_for_state_design(self):
        review_context = {
            "focus": "state_design",
            "error_layer": "core_design",
            "problem_title": "P1434 滑雪",
            "problem_context": "记忆化搜索里 dp[x][y] 这一格到底表示什么。",
            "bottleneck_text": "我总说不清 dp[x][y] 这一格在记录什么。",
            "main_block": "你卡在状态语义没有站稳。",
            "key_bridge": "状态不是代码变量名，而是这个子问题结果的定义。",
            "next_step": "先说清 dp[x][y] 这一格到底回答哪个小问题。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("子问题", payload["remedy_text"])
        self.assertIn("状态", payload["remedy_text"])
        self.assertIn("dp[x][y]", payload["micro_action"])

    def test_generate_remedy_explanation_should_blend_external_snippet_for_check_condition(self):
        review_context = {
            "focus": "check_condition",
            "error_layer": "method",
            "problem_title": "P2678 跳石头",
            "problem_context": "二分答案里要写 check(mid)。",
            "bottleneck_text": "我不知道 check(mid) 返回 true 到底说明什么。",
            "main_block": "你卡在判定函数的职责没站稳。",
            "key_bridge": "check(mid) 只说明当前这个 mid 可行不可行。",
            "next_step": "先说清 check(mid) 返回 true 说明什么。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("可不可行", payload["remedy_text"])
        self.assertIn("单独判断", payload["remedy_text"])
        self.assertIn("check(5)=true", payload["remedy_text"])
        self.assertIn("最容易误会", payload["remedy_text"])
        self.assertIn("check(mid)", payload["micro_action"])

    def test_generate_remedy_explanation_should_blend_external_snippet_for_left_bound_update(self):
        review_context = {
            "focus": "left_bound_update",
            "error_layer": "method",
            "problem_title": "P2249 查找",
            "problem_context": "有序数组里找最左边等于 x 的位置。",
            "bottleneck_text": "a[mid] == x 时我总想直接把 mid 丢掉。",
            "main_block": "你卡在边界更新这一步。",
            "key_bridge": "找最左位置时要保留 mid 作为候选。",
            "next_step": "先说清为什么 a[mid] == x 还不能马上丢掉 mid。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("最左边", payload["remedy_text"])
        self.assertIn("候选", payload["remedy_text"])
        self.assertIn("mid", payload["micro_action"])
        self.assertIn("[1,2,2,2,3]", payload["visual_hint"])
        self.assertIn("r = mid", payload["visual_hint"])

    def test_generate_remedy_explanation_should_blend_external_snippet_for_transition_design(self):
        review_context = {
            "focus": "transition_design",
            "error_layer": "core_design",
            "problem_title": "P1216 数字三角形",
            "problem_context": "当前状态要从上一层哪些位置转过来。",
            "bottleneck_text": "我总写不清当前格应该从哪几个来源转过来。",
            "main_block": "你卡在转移来源没想全。",
            "key_bridge": "转移式不是凭感觉写出来的，而是由更小状态的来源关系推出来的。",
            "next_step": "先说清当前状态可能从哪些更小状态转来。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("更小状态", payload["remedy_text"])
        self.assertIn("来源", payload["remedy_text"])
        self.assertIn("转来", payload["micro_action"])
        self.assertIn("当前格", payload["visual_hint"])
        self.assertIn("(i-1,j)", payload["visual_hint"])

    def test_generate_remedy_explanation_should_blend_external_snippet_for_complexity_fit(self):
        review_context = {
            "focus": "complexity_fit",
            "error_layer": "method",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "信息条数和拦截条数都可能达到 50000，单条串长度不超过 20。",
            "bottleneck_text": "我没有先算规模，总觉得双层枚举也许还能过。",
            "main_block": "你卡在还没先估总量级。",
            "key_bridge": "先根据数据范围判断双层枚举会不会超时。",
            "next_step": "先把会一起变大的量圈出来，再估总量级。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("输入规模", payload["remedy_text"])
        self.assertIn("总操作量", payload["remedy_text"])

    def test_generate_remedy_explanation_should_stay_local_for_constraint_modeling(self):
        review_context = {
            "focus": "constraint_modeling",
            "error_layer": "core_design",
            "problem_title": "P3275 [SCOI2011] 糖果",
            "problem_context": "把多条不等式限制统一建模后求可行解。",
            "bottleneck_text": "我不知道这些条件应该怎么统一翻成同一种关系。",
            "main_block": "你卡在限制关系还没统一。",
            "key_bridge": "先把每条限制都翻成同一种关系，再看谁限制谁。",
            "next_step": "先说清一句限制该翻成哪类关系。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("统一翻", payload["remedy_text"])
        self.assertIn("关系", payload["remedy_text"])
        self.assertIn("A <= B + c", payload["visual_hint"])
        self.assertIn("谁限制谁", payload["visual_hint"])

    def test_generate_remedy_explanation_should_blend_external_snippet_for_method_selection(self):
        review_context = {
            "focus": "method_selection",
            "error_layer": "method",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "给很多消息和拦截串，需要统计前缀关系。",
            "bottleneck_text": "我总是先猜要用 trie，但说不清题面里到底哪个信号支持它。",
            "main_block": "你卡在还没先抓题面里的结构信号。",
            "key_bridge": "先找题面里真正支持 trie 的结构信号。",
            "next_step": "先指出题面里一个真正支持当前方法的信号。",
        }

        with patch.object(review_engine, "_call_llm", side_effect=AssertionError("should not call llm")):
            payload = review_engine.generate_remedy_explanation(review_context, review_engine.REMEDY_ACTION_DYNAMIC)

        self.assertIn("相同开头", payload["remedy_text"])
        self.assertIn("更可靠", payload["remedy_text"])
        self.assertIn("101", payload["visual_hint"])
        self.assertIn("支持 trie", payload["visual_hint"])
        self.assertIn("101", payload["remedy_text"])

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
