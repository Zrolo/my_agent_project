import unittest

from evals.aichat import bridge_candidate_retriever as retriever


class BridgeCandidateRetrieverTests(unittest.TestCase):
    def test_retrieve_algorithm_topic_candidates_returns_top_k_binary_search(self):
        candidates = retriever.retrieve_algorithm_topic_candidates(
            student_message="我知道要二分答案，但是 check(mid) 到底返回 true 还是 false 我总写反。",
            problem_context="最大化最小距离，判断 mid 是否可行。",
            limit=5,
        )

        self.assertLessEqual(len(candidates), 5)
        self.assertEqual("binary_search", candidates[0]["topic_l1"])
        self.assertIn("answer", candidates[0]["topic_l2"])
        self.assertGreater(candidates[0]["score"], 0)

    def test_retrieve_focus_candidates_uses_top_topics_and_focus_registry(self):
        focus_registry = [
            {
                "focus_id": "check_condition",
                "bridge_family": "predicate_bridge",
                "description": "二分、判定或循环中的 check/if 条件语义不清。",
                "aliases": ["check", "判定函数", "可行性判断"],
            },
            {
                "focus_id": "tree_path_difference",
                "bridge_family": "aggregation_bridge",
                "description": "树上路径贡献转成端点/LCA 差分标记。",
                "aliases": ["树上差分", "LCA 标记"],
            },
        ]
        topics = retriever.retrieve_algorithm_topic_candidates(
            student_message="check(mid) 到底返回 true 还是 false？",
            problem_context="二分答案。",
            limit=5,
        )

        candidates = retriever.retrieve_focus_candidates(
            student_message="check(mid) 到底返回 true 还是 false？",
            problem_context="二分答案。",
            algorithm_topic_candidates=topics,
            focus_registry=focus_registry,
            limit=5,
        )

        self.assertLessEqual(len(candidates), 5)
        self.assertEqual("check_condition", candidates[0]["focus_id"])
        self.assertIn("unknown", {candidate["focus_id"] for candidate in candidates})

    def test_retrieve_focus_candidates_prioritizes_union_find_operation_mapping(self):
        focus_registry = [
            {
                "focus_id": "union_find_operation_mapping",
                "bridge_family": "data_structure_operation_bridge",
                "description": "并查集中，题面里的合并集合、连通查询或代表元维护如何映射到 find 和 union。",
                "aliases": ["并查集操作映射", "合并集合", "union", "find", "代表元"],
            },
            {
                "focus_id": "heap_push_pop_mapping",
                "bridge_family": "data_structure_operation_bridge",
                "description": "题面动作映射到堆或优先队列的 push 和 pop。",
                "aliases": ["堆操作映射", "push", "pop"],
            },
        ]
        topics = retriever.retrieve_algorithm_topic_candidates(
            student_message="题目说合并两个集合，我知道可能是并查集，但不知道这个操作在代码里对应哪一步。",
            problem_context="动态维护若干集合的合并与查询。",
            limit=5,
        )

        candidates = retriever.retrieve_focus_candidates(
            student_message="题目说合并两个集合，我知道可能是并查集，但不知道这个操作在代码里对应哪一步。",
            problem_context="动态维护若干集合的合并与查询。",
            algorithm_topic_candidates=topics,
            focus_registry=focus_registry,
            limit=5,
        )

        self.assertEqual("union_find_operation_mapping", candidates[0]["focus_id"])

    def test_retrieve_focus_candidates_prioritizes_topological_zero_indegree_reason(self):
        focus_registry = [
            {
                "focus_id": "dag_topological_dp_order",
                "bridge_family": "ordering_dependency_bridge",
                "description": "DAG DP 中按照拓扑序处理状态。",
                "aliases": ["DAG DP", "拓扑序"],
            },
            {
                "focus_id": "topological_zero_indegree_reason",
                "bridge_family": "ordering_dependency_bridge",
                "description": "拓扑排序中，入度为 0 表示当前没有未处理前置依赖。",
                "aliases": ["拓扑排序", "入度为0", "零入度", "前置依赖"],
            },
        ]
        topics = retriever.retrieve_algorithm_topic_candidates(
            student_message="有些任务必须先做，我不知道为什么要按入度为 0 的点开始处理。",
            problem_context="有先后依赖关系，需要生成合法顺序。",
            limit=5,
        )

        candidates = retriever.retrieve_focus_candidates(
            student_message="有些任务必须先做，我不知道为什么要按入度为 0 的点开始处理。",
            problem_context="有先后依赖关系，需要生成合法顺序。",
            algorithm_topic_candidates=topics,
            focus_registry=focus_registry,
            limit=5,
        )

        self.assertEqual("topological_zero_indegree_reason", candidates[0]["focus_id"])

    def test_retrieve_focus_candidates_prioritizes_generic_dp_transition_before_specific_unrelated_dp(self):
        focus_registry = [
            {
                "focus_id": "state_design",
                "bridge_family": "representation_bridge",
                "description": "不能定义 DP 状态、数组格子、维度或状态含义。",
                "aliases": ["状态定义", "状态设计", "dp 含义"],
            },
            {
                "focus_id": "transition_design",
                "bridge_family": "transition_bridge",
                "description": "不知道当前状态从哪些前置情况转移而来，或漏掉来源。",
                "aliases": ["转移设计", "转移方程", "来源关系", "状态转移"],
            },
            {
                "focus_id": "combinatorial_recurrence",
                "bridge_family": "transition_bridge",
                "description": "组合计数中当前值如何递推而来。",
                "aliases": ["组合递推", "C(n,k)", "计数 DP"],
            },
        ]
        topics = retriever.retrieve_algorithm_topic_candidates(
            student_message="我知道 dp[j] 可能和时间有关，但我不知道当前这株药到底从哪些情况转过来。",
            problem_context="0/1 背包，每株药草只能采一次。",
            limit=5,
        )

        candidates = retriever.retrieve_focus_candidates(
            student_message="我知道 dp[j] 可能和时间有关，但我不知道当前这株药到底从哪些情况转过来。",
            problem_context="0/1 背包，每株药草只能采一次。",
            algorithm_topic_candidates=topics,
            focus_registry=focus_registry,
            limit=5,
        )

        self.assertEqual("transition_design", candidates[0]["focus_id"])

    def test_retrieve_focus_candidates_does_not_match_single_letter_binary_bounds_inside_lca(self):
        focus_registry = [
            {
                "focus_id": "tree_path_difference",
                "bridge_family": "aggregation_bridge",
                "description": "树上路径贡献转成端点/LCA 差分标记。",
                "aliases": ["树上差分", "LCA 标记"],
            },
            {
                "focus_id": "binary_search_bound_direction",
                "bridge_family": "predicate_bridge",
                "description": "二分查找中根据 check 结果更新左右边界的方向。",
                "aliases": ["二分边界方向", "l r 更新"],
            },
        ]
        topics = retriever.retrieve_algorithm_topic_candidates(
            student_message="我知道要 LCA，但不知道每条路径到底在哪里加减标记。",
            problem_context="树上多条路径统计每个点经过次数。",
            limit=5,
        )

        candidates = retriever.retrieve_focus_candidates(
            student_message="我知道要 LCA，但不知道每条路径到底在哪里加减标记。",
            problem_context="树上多条路径统计每个点经过次数。",
            algorithm_topic_candidates=topics,
            focus_registry=focus_registry,
            limit=5,
        )

        self.assertEqual("tree_path_difference", candidates[0]["focus_id"])
        self.assertNotEqual("binary_search_bound_direction", candidates[1]["focus_id"])

    def test_retrieve_focus_candidates_keeps_method_selection_for_algorithm_confirmation(self):
        focus_registry = [
            {
                "focus_id": "method_selection",
                "bridge_family": "complexity_bridge",
                "description": "学生不知道该选择哪类方法，或正在确认算法方向。",
                "aliases": ["方法选择", "题型判断", "算法方向"],
            },
            {
                "focus_id": "shared_prefix_merging",
                "bridge_family": "aggregation_bridge",
                "description": "多个字符串共享前缀时如何复用节点。",
                "aliases": ["共享前缀", "trie"],
            },
        ]
        topics = retriever.retrieve_algorithm_topic_candidates(
            student_message="这题是不是 trie？我感觉很多 01 串像 trie，但不确定。",
            problem_context="输入多条 01 消息串，并反复处理前缀包含关系。",
            limit=5,
        )

        candidates = retriever.retrieve_focus_candidates(
            student_message="这题是不是 trie？我感觉很多 01 串像 trie，但不确定。",
            problem_context="输入多条 01 消息串，并反复处理前缀包含关系。",
            algorithm_topic_candidates=topics,
            focus_registry=focus_registry,
            limit=5,
        )

        self.assertIn("method_selection", [candidate["focus_id"] for candidate in candidates[:2]])

    def test_retrieve_focus_candidates_covers_common_competitive_programming_focus_phrases(self):
        focus_registry = [
            {
                "focus_id": "greedy_basis",
                "bridge_family": "selection_bridge",
                "description": "学生不知道为什么某个贪心选择是安全的。",
                "aliases": ["贪心依据", "交换证明", "结束早"],
            },
            {
                "focus_id": "enumeration_order",
                "bridge_family": "ordering_bridge",
                "description": "学生不知道为什么枚举或更新必须按某个顺序。",
                "aliases": ["枚举顺序", "倒序枚举", "更新顺序"],
            },
            {
                "focus_id": "complexity_fit",
                "bridge_family": "complexity_bridge",
                "description": "学生不能根据数据范围判断复杂度是否可行。",
                "aliases": ["复杂度匹配", "数据范围", "会不会过"],
            },
        ]
        examples = [
            (
                "我知道要先选结束早的活动，但为什么这样不会影响后面的选择？",
                "活动选择类问题，目标是在不冲突条件下选尽量多的活动。",
                "greedy_basis",
            ),
            (
                "01 背包为什么容量要倒着枚举？正着枚举不是也能更新吗？",
                "每个物品只能选一次。",
                "enumeration_order",
            ),
            (
                "我写了两层循环，但 n 到 1e5，会不会过我判断不出来。",
                "需要根据数据范围估算复杂度是否可行。",
                "complexity_fit",
            ),
        ]
        for student_message, problem_context, expected_focus in examples:
            with self.subTest(expected_focus=expected_focus):
                topics = retriever.retrieve_algorithm_topic_candidates(
                    student_message=student_message,
                    problem_context=problem_context,
                    limit=5,
                )
                candidates = retriever.retrieve_focus_candidates(
                    student_message=student_message,
                    problem_context=problem_context,
                    algorithm_topic_candidates=topics,
                    focus_registry=focus_registry,
                    limit=5,
                )
                self.assertEqual(expected_focus, candidates[0]["focus_id"])


if __name__ == "__main__":
    unittest.main()
