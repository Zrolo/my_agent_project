import unittest

import review_engine


class ReviewEngineFocusTests(unittest.TestCase):
    def test_constraint_modeling_should_beat_general_modeling_for_parallel_constraints(self):
        review_context = {
            "error_layer": "modeling",
            "problem_title": "活动时间与地点约束",
            "problem_context": "每个活动都必须同时满足时间窗口和指定地点两个条件，才算合法安排。题目问的是这些限制之间是什么关系。",
            "bottleneck_text": "我看到时间和地点两个限制，但总把它们当成主条件加附带检查，不确定是不是要同时满足。",
            "main_block": "",
            "key_bridge": "",
            "next_step": "",
            "transfer_signal": "",
        }

        self.assertEqual(review_engine._detect_quiz_focus(review_context), "constraint_modeling")

    def test_tree_diameter_formula_case_should_not_be_overwritten_by_greedy_template(self):
        review = {
            "error_layer": "core_design",
            "core_design_subtags": ["greedy_basis", "check_condition"],
            "main_block": "你不是不会树的直径，而是没有先说明为什么答案能直接从直径长度和 k 推出来。",
            "key_bridge": "关键是先说明核心城市必须在直径上形成连续一段，以及非核心城市到这段的最远距离为什么能由直径长度推出。",
            "next_step": "先在直径上画出连续的 k 个核心城市，再手推最远非核心城市离这段的距离怎么变化。",
            "transfer_signal": "如果题目让你在树上选连续的一段点并最小化最远距离，就先检查答案是不是由直径和覆盖段共同决定。",
        }

        guarded = review_engine._guard_review_bridge_stability(
            review.copy(),
            problem_title="P5536 【XR-3】核心城市",
            problem_context="题目在树上选 k 个连通核心城市，并最小化其余城市到核心城市集合的最远距离。",
            bottleneck_text="我知道这题和树的直径有关，也写出了先求直径长度 d 再套公式的做法，但我不明白为什么答案能直接写成 (d-k+2)/2。",
            error_types=["模型转化", "知道算法但不知道怎么用"],
        )

        self.assertNotIn("为什么当前对象优先选不会吃亏", guarded["key_bridge"])
        self.assertIn("直径", guarded["main_block"])


if __name__ == "__main__":
    unittest.main()
