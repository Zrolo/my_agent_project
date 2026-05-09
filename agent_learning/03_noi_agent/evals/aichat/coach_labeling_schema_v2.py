import re
from collections.abc import Iterable


INPUT_COLUMNS = [
    "case_id",
    "problem_ref",
    "student_message",
    "problem_context",
    "recent_dialogue",
    "student_code_excerpt",
]

LABEL_COLUMNS = [
    "turn_type",
    "diagnosis_uncertainty",
    "student_problem_solving_state",
    "student_attempt_level",
    "student_already_knows",
    "student_already_stated_bridge",
    "policy_risk_type",
    "primary_bridge_family",
    "primary_bridge_subtype_id",
    "primary_bridge_subtype_note",
    "secondary_bridge_family",
    "secondary_bridge_subtype_id",
    "missing_bridge_instance",
    "evidence_type",
    "evidence_quote",
    "registered_focus_id",
    "secondary_registered_focus_id",
    "focus_match_status",
    "new_focus_candidate",
    "help_seeking_type",
    "max_scaffold_level",
    "help_forms",
    "general_forbidden_content",
    "bridge_specific_forbidden_content",
    "leakage_risk",
    "coach_confidence",
    "coach_note_tags",
    "coach_free_notes",
    "review_status",
]

V2_COLUMNS = [*INPUT_COLUMNS, *LABEL_COLUMNS]

CHINESE_HEADERS = {
    "case_id": "样本编号",
    "problem_ref": "题目编号",
    "student_message": "学生当前问题（先看）",
    "problem_context": "题目/上下文",
    "recent_dialogue": "近期对话",
    "student_code_excerpt": "学生代码片段",
    "turn_type": "这一轮类型",
    "diagnosis_uncertainty": "诊断不确定性",
    "student_problem_solving_state": "学生当前解题状态",
    "student_attempt_level": "学生已有尝试程度",
    "student_already_knows": "学生已经知道什么（可写中文）",
    "student_already_stated_bridge": "学生是否已说出关键桥",
    "policy_risk_type": "策略风险类型",
    "primary_bridge_family": "主要缺失桥梁大类",
    "primary_bridge_subtype_id": "主要桥梁细分 ID",
    "primary_bridge_subtype_note": "主要桥梁细分补充",
    "secondary_bridge_family": "次要桥梁大类（可空）",
    "secondary_bridge_subtype_id": "次要桥梁细分 ID（可空）",
    "missing_bridge_instance": "当前缺的那一步",
    "evidence_type": "证据类型",
    "evidence_quote": "证据原话/上下文引用",
    "registered_focus_id": "系统已有焦点 ID",
    "secondary_registered_focus_id": "次要焦点 ID（可空）",
    "focus_match_status": "焦点匹配状态",
    "new_focus_candidate": "新焦点候选名",
    "help_seeking_type": "求助类型（可多选）",
    "max_scaffold_level": "本轮最多帮助强度",
    "help_forms": "建议帮助形式（可多选）",
    "general_forbidden_content": "通用不能直接补完",
    "bridge_specific_forbidden_content": "当前桥梁不能直接补完",
    "leakage_risk": "泄露风险",
    "coach_confidence": "置信度 1-5",
    "coach_note_tags": "备注标签",
    "coach_free_notes": "自由备注",
    "review_status": "标注状态",
}

FIELD_HELP = {
    "turn_type": "先判断这一轮属于什么交互场景。完整答案、完整代码、关键桥请求、算法确认和局部补全要分开。",
    "student_problem_solving_state": "判断学生当前卡在解题流程的哪个状态，而不是学生整体水平。",
    "primary_bridge_family": "判断学生当前最主要缺的是哪类推理桥；信息不足或不适用时选 unknown_or_not_applicable。",
    "primary_bridge_subtype_id": "选择一个可统计的细分 ID；如果不贴切，选 unknown 并在补充列写中文说明。",
    "registered_focus_id": "系统已有教学焦点/知识卡 ID，不等于学生已经掌握的知识。",
    "student_already_knows": "写学生已经显式说出的已有知识，例如 LCA、会暴力、知道要 DP。",
    "student_already_stated_bridge": "判断关键桥是否已经由学生自己说出，这会影响后续是否算泄露。",
    "policy_risk_type": "只描述策略/泄露风险，不描述学生认知状态。比如算法确认、关键桥补全、完整代码请求。",
    "help_seeking_type": "可用英文分号 ; 多选。比如 type_confirmation;strategy_hint_request。",
    "max_scaffold_level": "这是本轮最多允许帮助强度，不是学生想要多少就给多少。直接要答案通常是 L0/L1。",
    "bridge_specific_forbidden_content": "写当前最不能被 AI 直接说穿的关键桥，例如完整状态定义、完整 check 条件、完整端点/LCA 公式。",
    "evidence_quote": "标注为 labeled 时请引用学生原话或上下文证据，便于复核分歧。",
}

TURN_TYPES = {
    "diagnosable_learning_turn": "可诊断学习轮：学生给出具体卡点或尝试，可判断下一步",
    "insufficient_context": "信息不足轮：只说不会/错了/没思路，先要题面、尝试或证据",
    "complete_solution_request": "完整题解请求：要求从思路到步骤的完整做法",
    "complete_code_request": "完整代码请求：要求可提交代码或大段代写",
    "critical_bridge_request": "关键桥请求：直接索要状态、转移、check、公式、标记规则",
    "algorithm_confirmation_request": "算法/题型确认请求：问是不是 DP、二分、贪心等",
    "local_completion_request": "局部补全请求：要求补一行、一个 if、一个边界或模板空位",
    "code_debugging_without_evidence": "调试缺证据轮：说代码错了但没给代码、现象或样例",
    "code_debugging_with_evidence": "有证据调试轮：提供代码、错误现象或 WA/TLE/RE 证据",
    "step_validation_request": "步骤验证轮：学生已有推理，想确认局部判断是否成立",
    "reflection_or_transfer_turn": "复盘迁移轮：做完或接近做完，想总结何时使用",
    "emotional_or_time_pressure": "情绪/时间压力轮：焦虑、赶时间或催促主导",
}

DIAGNOSIS_UNCERTAINTY = {
    "low": "低：证据清楚，可以直接判断主要卡点",
    "medium": "中：能初判，但可能存在次要桥或多种解释",
    "high": "高：证据不足，应先澄清题面、尝试、代码或错误现象",
}

STUDENT_STATES = {
    "insufficient_evidence": "证据不足：当前无法可靠判断认知卡点",
    "goal_comprehension_gap": "题意目标理解卡住：不清楚要求、限制、输入输出或样例含义",
    "modeling_representation_gap": "建模/表示卡住：题意懂一些，但不会抽象成对象、状态、变量、事件",
    "method_selection_gap": "方法选择卡住：不知道该往 DP、图、贪心、二分、搜索等哪个方向想",
    "method_application_gap": "方法应用/变式卡住：知道方向、算法或知识点，但不会落到当前题的关键步骤",
    "misconception_or_wrong_strategy": "错误思路卡住：已有思路，但核心假设或策略错了且未意识到",
    "correctness_reasoning_gap": "正确性解释卡住：会做或会写一部分，但说不清为什么对",
    "complexity_optimization_gap": "复杂度优化卡住：暴力会或有初解，但不知道瓶颈和优化方式",
    "implementation_translation_gap": "思路到代码卡住：关系基本明确，但变量、循环、函数或局部代码难落地",
    "debugging_evidence_gap": "调试证据不足：知道错了，但缺最小样例、实际输出或可疑位置",
    "debugging_localization_gap": "调试定位卡住：有错误证据，但不知道 bug 在哪类逻辑或边界",
    "reflection_transfer_gap": "迁移总结卡住：当前题会了，但不会总结触发条件和下次识别方式",
}

POLICY_RISK_TYPES = {
    "none": "无明显策略风险",
    "algorithm_confirmation_risk": "算法确认风险：直接确认会泄露题型或核心方向",
    "critical_bridge_completion_risk": "关键桥补全风险：直接回答会补完状态、转移、check 或公式",
    "complete_answer_risk": "完整题解风险：可能给出完整流程或标准做法",
    "complete_code_risk": "完整代码风险：可能代写可提交代码",
    "local_code_completion_risk": "局部补全风险：可能替学生补完关键 if、边界或一行代码",
    "prompt_injection_risk": "提示词注入风险：要求改变规则、泄露提示或绕过限制",
}

STUDENT_ATTEMPT_LEVELS = {
    "none": "无尝试：没有暴露题意理解、思路或代码",
    "vague": "模糊尝试：只有方向猜测或笼统感觉",
    "partial_attempt": "部分尝试：说出了一些对象、算法、状态、代码片段或手算",
    "wrong_attempt": "错误尝试：有明确方案，但关键假设或逻辑明显错误",
    "near_correct_attempt": "接近正确：主要方向对，只差局部桥、边界或验证",
    "has_code_no_evidence": "有代码无证据：贴了代码，但没有失败样例、现象或怀疑点",
    "has_code_with_evidence": "有代码有证据：有代码且给出 WA/TLE/RE、样例或实际输出",
    "completed_but_no_transfer": "已完成但未迁移：做出来或 AC 了，但不会总结",
}

STUDENT_ALREADY_STATED_BRIDGE = {
    "not_stated": "未说出：学生还没提出当前关键桥",
    "partial_hypothesis": "部分猜到：学生提出了不完整或待验证的关键桥假设",
    "correctly_stated": "已正确说出：学生已经完整表达当前关键桥",
    "incorrectly_stated": "说出错误桥：学生给出了错误的关键关系",
    "already_exposed_by_tutor": "已被前文暴露：前面 AI 或老师已经说过关键桥",
}

BRIDGE_FAMILIES = {
    "goal_constraint_bridge": "目标/限制理解桥：题目要求、限制、输入输出或样例含义没有转成明确目标",
    "modeling_bridge": "题面建模桥：不知道什么当点、边、状态、事件或约束",
    "method_selection_bridge": "方法选择桥：不知道题目特征指向哪类算法或数据结构",
    "representation_state_bridge": "表示/状态语义桥：不知道 dp、mask、lazy、dist、数组格子或节点字段表示什么",
    "transition_recurrence_bridge": "转移/递推桥：不知道当前状态或答案从哪些前置情况来",
    "predicate_condition_bridge": "判定/条件桥：不知道 check、if、relax、while 的语义和方向",
    "ordering_dependency_bridge": "顺序/依赖桥：不知道为什么要按某个枚举、遍历、拓扑、倒序或区间长度顺序",
    "aggregation_contribution_bridge": "汇总/贡献桥：不知道多次影响如何压缩、累计、合并或还原",
    "data_structure_operation_bridge": "数据结构操作映射桥：不知道题目动作如何映射到 push、pop、unite、query、relax 等操作",
    "correctness_invariant_bridge": "正确性/不变量桥：不知道为什么贪心、最短路、单调结构等选择是安全的",
    "complexity_optimization_bridge": "复杂度/优化桥：不知道数据范围、瓶颈和优化结构之间的关系",
    "implementation_boundary_bridge": "实现/边界桥：下标、初始化、base case、类型、取模、输入输出等实现细节",
    "debugging_evidence_bridge": "调试证据桥：不知道如何构造反例、定位 WA/TLE/RE 或收集最小证据",
    "reflection_transfer_bridge": "迁移总结桥：不知道如何总结题型信号和下次复用",
    "unknown_or_not_applicable": "不确定/不适用：信息不足、纯策略风险或非学习型请求",
}

BRIDGE_SUBTYPES = {
    "unknown": "不确定或信息不足",
    "goal.constraint_decomposition": "目标限制拆解：把题目要求、限制和样例目标拆成可操作判断",
    "modeling.objects_relations": "对象关系建模：判断题面对象之间的关系该如何表示",
    "modeling.events_constraints": "事件约束建模：把操作、限制、合法性转成事件或约束",
    "modeling.constraint_to_edge": "约束转边：把不等式、先后关系或可达条件转成图边/方向/权值",
    "modeling.graph_vertices_edges": "点边建模：判断什么当点、什么当边、什么当边权",
    "modeling.interval_to_events": "区间转事件：把区间端点或矩形边转成扫描线事件",
    "method.selection_signal": "方法选择信号：从数据范围、目标、操作中判断算法方向",
    "method.binary_search_answer_signal": "二分答案信号：识别候选答案和可行性判断之间的单调关系",
    "method.dp_state_candidate_signal": "DP 状态候选信号：判断哪些历史信息需要被状态保留",
    "method.greedy_candidate_signal": "贪心候选信号：识别可排序、可交换或局部选择的线索",
    "state.dp_state_semantics": "DP 状态语义：定义 dp 数组格子、维度和含义",
    "state.mask_semantics": "mask 语义：定义二进制位表示的选择、集合或状态",
    "state.lazy_tag_semantics": "lazy 标记语义：说明懒标记保存了什么尚未下传的信息",
    "state.search_augmented_state": "搜索扩展状态：BFS/DFS 除位置外还要携带钥匙、资源、mask 等信息",
    "state.kmp_prefix_function_semantics": "KMP 前缀函数语义：next/prefix 数组表示最长相等真前后缀",
    "transition.take_or_skip_cases": "取或不取转移：把当前决策拆成选/不选等前置情况",
    "transition.child_to_parent_merge": "子树合并转移：父节点状态如何由多个子节点贡献合并",
    "transition.combinatorial_recurrence": "组合计数递推：当前计数如何由上一层或拆分情况得到",
    "predicate.check_truth_direction": "check 真假方向：候选答案对应的 true/false 语义",
    "predicate.binary_search_bound_update": "二分边界更新：根据 check 结果移动左边界或右边界",
    "predicate.relax_condition": "relax 条件：什么时候能用一条边更新 dist 或状态",
    "predicate.dijkstra_stale_entry_guard": "Dijkstra 旧项判断：优先队列弹出过期距离时如何跳过",
    "predicate.local_if_boundary_condition": "局部 if/边界条件：某个局部条件该判断什么才合法",
    "ordering.reverse_capacity_loop": "背包倒序循环：避免同一物品在一轮里被重复使用",
    "ordering.rolling_array_overwrite_order": "滚动数组覆盖顺序：压维后如何避免覆盖仍需使用的旧状态",
    "ordering.interval_dp_order": "区间 DP 顺序：先算小区间或短长度以满足依赖",
    "ordering.topological_dependency": "拓扑依赖顺序：先处理前驱，再处理后继或当前状态",
    "aggregation.tree_path_difference_marking": "树上路径差分标记：路径贡献如何压到端点和 LCA 附近再汇总",
    "aggregation.prefix_sum_1d": "一维前缀和：区间贡献如何由两个前缀值相减得到",
    "aggregation.prefix_sum_2d": "二维前缀和：矩形贡献如何用四角容斥还原",
    "aggregation.difference_array_range_update": "差分区间更新：区间加如何只改 l 和 r+1 再还原",
    "ds.heap_push_pop_mapping": "堆操作映射：题目中的取最小/最大如何对应 push 和 pop",
    "ds.union_find_operation_mapping": "并查集操作映射：连通、合并、查询如何对应 unite/find",
    "ds.monotonic_stack_mapping": "单调栈操作映射：比较关系如何决定入栈、弹栈和记录答案",
    "implementation.loop_boundary": "循环下标边界：循环起止、开闭区间、0/1 下标是否对齐",
    "implementation.integer_overflow": "整数溢出：范围估算、哨兵值和 long long 使用",
    "implementation.modular_multiplication_overflow": "取模乘法溢出：中间乘法先溢出再取模的问题",
    "implementation.dfs_parent_guard": "DFS 防回父边：树/无向图递归如何避免走回父节点",
    "implementation.initialization_base_case": "初始化/base case：DP 初值、递归出口和空状态设置",
    "implementation.io_format_parsing": "输入输出解析：读入格式、多组数据、编号和输出要求",
    "correctness.greedy_exchange_argument": "贪心交换论证：说明局部选择为什么不亏",
    "correctness.shortest_path_invariant": "最短路不变量：说明 Dijkstra/BFS 等为何保证当前结果正确",
    "correctness.monotonic_structure_dominance": "单调结构支配：说明被弹掉/淘汰的元素为什么不会再优",
    "complexity.bruteforce_bottleneck": "暴力瓶颈定位：找出哪层枚举或查询导致复杂度过高",
    "complexity.replace_inner_loop_with_structure": "结构替代内层循环：用数据结构或预处理维护原本反复计算的量",
    "debug.minimal_failing_case": "最小失败样例：先构造能复现错误的小样例和期望输出",
    "debug.wa_counterexample_construction": "WA 反例构造：针对当前错误思路构造能打破它的反例",
    "debug.tle_bottleneck_localization": "TLE 瓶颈定位：用数据范围和代码结构定位慢在哪里",
    "reflection.problem_signature": "题型信号总结：总结下次如何识别同类题",
    "policy.direct_answer_request": "完整答案/代码请求策略：不诊断具体桥，先安全收束",
    "policy.critical_bridge_request": "关键桥请求策略：不直接补状态、转移、check 或公式",
    "policy.local_completion_request": "局部补全请求策略：不直接补关键 if、边界或一行代码",
}

EVIDENCE_TYPES = {
    "asks_goal_or_constraint": "学生直接问题意目标、限制、输入输出或样例含义",
    "asks_modeling": "学生表达不知道如何把题面抽象成结构",
    "asks_method": "学生表达不知道该往哪个算法方向想",
    "asks_type_confirmation": "学生直接问是不是某算法或题型",
    "asks_state_semantics": "学生直接问状态、变量、数组格子、标记的含义",
    "asks_transition": "学生直接问转移、递推来源或分类讨论",
    "asks_predicate_condition": "学生直接问 check、if、relax、while 的条件",
    "asks_ordering": "学生直接问循环、遍历、拓扑、倒序或处理顺序",
    "asks_aggregation": "学生直接问前缀、差分、贡献或子树如何汇总",
    "asks_data_structure_mapping": "学生直接问题目动作如何对应数据结构操作",
    "wrong_strategy_presented": "学生给出明确但错误的思路或解释",
    "code_or_debug_issue": "学生提供代码、错误现象、样例或运行结果",
    "vague_confusion_only": "学生只有笼统不会，没有具体卡点",
    "direct_answer_request": "学生要求完整答案、完整代码或直接给关键结论",
    "needs_discussion": "当前证据不足、边界不清或多个标签都合理",
}

FOCUS_MATCH_STATUS = {
    "matched_existing": "匹配已有焦点：已有 focus 能准确覆盖当前卡点",
    "uncertain_existing": "疑似已有焦点：可能能匹配，但粒度或边界不完全确定",
    "needs_new_focus": "需要新增焦点：现有 focus 覆盖不了当前卡点",
    "unknown_not_enough_evidence": "证据不足未知：当前信息不够判断 focus",
    "not_applicable": "不适用：策略风险或非学习型请求，不映射知识焦点",
}

HELP_SEEKING_TYPES = {
    "vague_confusion": "笼统困惑：只说不会、没思路、看不懂",
    "concept_explanation": "概念解释：要求解释术语、变量、状态或结构含义",
    "strategy_hint_request": "方向提示：想要下一步提示，但仍愿意自己推",
    "type_confirmation": "算法确认：想确认是不是某算法或题型",
    "step_validation": "步骤验证：已有局部推理，想确认是否正确",
    "proof_why_request": "正确性追问：问为什么这样做是对的",
    "complexity_check": "复杂度检查：问当前做法能不能过或为什么 TLE",
    "implementation_help": "实现帮助：思路到代码表达卡住",
    "debugging_request": "调试求助：代码错了，希望定位问题",
    "local_code_completion_request": "局部补全：想让 AI 补一行、一个 if 或一个边界",
    "complete_answer_request": "完整接管：要完整题解、完整代码或标准做法",
    "emotional_time_pressure": "情绪/时间压力：焦虑、赶时间、催促求快",
    "reflection_transfer_request": "复盘迁移：做完后想总结如何识别同类题",
    "unclear": "求助意图不清：当前信息不足，无法判断",
}

SCAFFOLD_LEVELS = {
    "L0": "澄清/要证据：只要题面、尝试、代码、错误现象，不给实质解题提示",
    "L1": "轻提示：给观察角度、约束追问或让学生先表达想法，不补关键桥",
    "L2": "中提示：给微型样例、局部反例、半步关系或一个引导问题",
    "L3": "强提示：学生已有足够尝试时，给局部结构、检查清单、局部伪代码或局部代码诊断",
}

HELP_FORMS = {
    "guiding_question": "引导问题：只问一个能推进思考的问题",
    "micro_example": "微型例子：用很小样例让学生看见关系",
    "counterexample": "反例：用小反例暴露错误思路",
    "constraint_probe": "约束追问：追问数据范围、限制或合法性",
    "debug_evidence_request": "调试证据请求：要求失败样例、实际输出或怀疑位置",
    "local_code_hint": "局部代码提示：只提示一个局部位置或变量关系",
    "code_diagnosis": "代码诊断：定位一个最小可疑点，不代写完整代码",
    "checklist": "检查清单：列少量局部检查项",
    "partial_trace": "局部手算/跟踪：跟踪一个小样例或几步状态变化",
    "visual_table": "表格辅助：用表格呈现状态、样例或关系",
    "ascii_diagram": "文本图示：用 ASCII 图画树、图、区间或流程",
    "pseudocode_skeleton": "局部伪代码骨架：只给关键局部结构，不给完整可提交流程",
    "summary": "小结：收束学生已说清的内容",
    "summary_and_next_step": "小结并给下一步：总结后给一个可执行小目标",
    "understanding_check": "理解检查：用短问题验证是否真的理解",
    "reflection_prompt": "迁移总结问题：引导总结下次识别信号",
}

GENERAL_FORBIDDEN_CONTENT = {
    "no_full_solution": "不能给完整题解：不一次性给完整思路、步骤和证明",
    "no_full_code": "不能给完整代码：不提供可直接提交的大段代码",
    "no_direct_algorithm_confirmation": "不能直接确认算法名/题型：不直接说“就是 DP/二分/贪心”等",
    "no_guess_without_context": "不能缺上下文乱猜：信息不足时先要题面、尝试或证据",
}

BRIDGE_SPECIFIC_FORBIDDEN_CONTENT = {
    "no_exact_state_definition": "不能直接给完整状态定义：让学生自己说出状态含义",
    "no_exact_recurrence": "不能直接给完整转移方程：避免补完当前递推桥",
    "no_exact_check_condition": "不能直接给完整 check 条件和边界更新：避免说穿判定方向",
    "no_exact_modeling_plan": "不能直接给完整建模方案：避免一次性给点、边、状态、约束",
    "no_exact_greedy_rule": "不能直接给完整贪心准则和证明：避免直接暴露选择规则",
    "no_exact_contribution_formula": "不能直接给完整贡献公式：避免说穿前缀、差分、树上标记等公式",
    "no_exact_iteration_template": "不能直接给完整循环/遍历模板：避免补完整顺序和边界",
    "no_exact_data_structure_template": "不能直接给完整数据结构模板：避免完整套出并查集、堆、线段树等实现",
    "no_complete_local_condition": "不能直接补完整局部条件：避免替学生补完关键 if 或边界",
}

LEAKAGE_RISKS = {
    "low": "低：正常支架不太容易泄露关键桥",
    "medium": "中：如果表达过强，可能泄露局部关键桥",
    "high": "高：学生正在索取题型、关键桥、完整步骤或代码",
    "unknown": "未知：证据不足，无法判断泄露风险",
}

NOTES_OPTIONS = {
    "no_note": "无特殊备注",
    "needs_discussion": "需要讨论：标注边界不清",
    "multi_bridge_case": "多桥混合：一个主要桥不够表达",
    "insufficient_evidence": "证据不足：需要更多上下文才能定标",
    "needs_new_focus": "可能需要新增 focus：现有知识卡粒度不贴切",
    "acceptable_non_unique": "标签不唯一：多个标签都可接受",
}

REVIEW_STATUSES = {
    "unlabeled": "未标：还没有完成这一行",
    "labeled": "已标完：可进入校验或复核",
    "needs_discussion": "需讨论：教练不确定或存在分歧",
    "review_seed_gold": "内部复核：只用于检查 seed gold，不用于盲标",
}

CONFIDENCE_OPTIONS = {
    "1": "很不确定：基本靠猜",
    "2": "较不确定：证据较弱",
    "3": "一般确定：可用但可能有争议",
    "4": "比较确定：证据较充分",
    "5": "非常确定：证据直接且边界清楚",
}

OPTIONS_BY_FIELD = {
    "turn_type": TURN_TYPES,
    "diagnosis_uncertainty": DIAGNOSIS_UNCERTAINTY,
    "student_problem_solving_state": STUDENT_STATES,
    "student_attempt_level": STUDENT_ATTEMPT_LEVELS,
    "student_already_stated_bridge": STUDENT_ALREADY_STATED_BRIDGE,
    "policy_risk_type": POLICY_RISK_TYPES,
    "primary_bridge_family": BRIDGE_FAMILIES,
    "secondary_bridge_family": BRIDGE_FAMILIES,
    "primary_bridge_subtype_id": BRIDGE_SUBTYPES,
    "secondary_bridge_subtype_id": BRIDGE_SUBTYPES,
    "evidence_type": EVIDENCE_TYPES,
    "focus_match_status": FOCUS_MATCH_STATUS,
    "help_seeking_type": HELP_SEEKING_TYPES,
    "max_scaffold_level": SCAFFOLD_LEVELS,
    "help_forms": HELP_FORMS,
    "general_forbidden_content": GENERAL_FORBIDDEN_CONTENT,
    "bridge_specific_forbidden_content": BRIDGE_SPECIFIC_FORBIDDEN_CONTENT,
    "leakage_risk": LEAKAGE_RISKS,
    "coach_confidence": CONFIDENCE_OPTIONS,
    "coach_note_tags": NOTES_OPTIONS,
    "review_status": REVIEW_STATUSES,
}

MULTI_VALUE_FIELDS = {
    "help_seeking_type",
    "help_forms",
    "general_forbidden_content",
    "bridge_specific_forbidden_content",
    "coach_note_tags",
}

FREE_TEXT_FIELDS = {
    "student_already_knows",
    "primary_bridge_subtype_note",
    "missing_bridge_instance",
    "evidence_quote",
    "new_focus_candidate",
    "coach_free_notes",
}

FOCUS_FIELDS = {"registered_focus_id", "secondary_registered_focus_id"}

COLUMN_WIDTHS = {
    "A": 15,
    "B": 14,
    "C": 40,
    "D": 44,
    "E": 28,
    "F": 28,
    "G": 28,
    "H": 20,
    "I": 30,
    "J": 24,
    "K": 28,
    "L": 28,
    "M": 28,
    "N": 26,
    "O": 28,
    "P": 26,
    "Q": 28,
    "R": 28,
    "S": 26,
    "T": 30,
    "U": 30,
    "V": 26,
    "W": 26,
    "X": 34,
    "Y": 28,
    "Z": 28,
    "AA": 28,
    "AB": 28,
    "AC": 36,
    "AD": 36,
    "AE": 16,
    "AF": 28,
    "AG": 28,
    "AH": 32,
    "AI": 18,
}

_OPTION_ID_PATTERN = re.compile(r"[（(]([^（）()]+)[）)]\s*$")


def option_label(option_id: str, description: str | None = None) -> str:
    if description is None:
        description = _lookup_description(option_id) or option_id
    return f"{description}（{option_id}）"


def option_labels(options: dict[str, str]) -> list[str]:
    return [option_label(option_id, description) for option_id, description in options.items()]


def extract_option_id(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    match = _OPTION_ID_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return text


def split_option_ids(value: object) -> list[str]:
    text = "" if value is None else str(value).strip()
    if not text:
        return []
    normalized = text.replace("\n", ";")
    return [extract_option_id(item) for item in normalized.split(";") if extract_option_id(item)]


def ids_from_values(values: Iterable[object]) -> list[str]:
    return [extract_option_id(value) for value in values if extract_option_id(value)]


def _lookup_description(option_id: str) -> str | None:
    for options in OPTIONS_BY_FIELD.values():
        if option_id in options:
            return options[option_id]
    return None
