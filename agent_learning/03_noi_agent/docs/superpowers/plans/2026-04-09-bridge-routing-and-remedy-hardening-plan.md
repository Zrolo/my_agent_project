# Bridge Routing And Remedy Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修正当前学生主链路里最影响教学体验的错桥、漏桥和泛化补课问题，让高频桥的 quiz / knowledge card / remedy 更贴当前题。

**Architecture:** 保持现有 review schema 和学习状态机不变，只在 `review_engine.py` 内补桥级 focus、桥级 backfill、桥级 knowledge card 选择和 deterministic remedy。新增的桥优先服务真实高频样例：`P2249`、`P2922`、`P3372`。

**Tech Stack:** Python, unittest, existing review engine deterministic quiz/card pipeline

---

### Task 1: 补失败测试，锁定错桥与漏桥

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 写 `P2249` 左边界桥检测失败测试**

```python
    def test_detect_quiz_focus_should_route_p2249_to_left_bound_update(self):
        review_context = {
            "problem_title": "P2249 查找",
            "problem_context": "在有序数组里找第一个等于 x 的位置。",
            "bottleneck_text": "我会写二分，但 a[mid] == x 时，总不知道该把右边界写成 mid 还是 mid-1。",
            "error_layer": "implementation",
            "key_bridge": "命中后要不要保留 mid 这一侧。",
        }

        self.assertEqual("left_bound_update", review_engine._detect_quiz_focus(review_context))
```

- [ ] **Step 2: 写 `P2922` 方法桥不应被 trie 机制桥吞掉的失败测试**

```python
    def test_generate_knowledge_bailout_card_should_keep_trie_method_selection_on_method_card(self):
        review_context = {
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "problem_context": "很多消息、很多拦截串，单条串长度不超过 20。",
            "bottleneck_text": "我总是先猜要用 trie，但说不清题面里到底哪个信号支持它。",
            "error_layer": "method",
            "key_bridge": "先找题面里真正支持 trie 的结构信号。",
        }
        previous_quiz = {
            "quiz_role": review_engine.QUIZ_ROLE_REMEDY,
            "meta": {"focus": "method_selection", "difficulty_level": "final_micro_confirm"},
        }

        card = review_engine.generate_knowledge_bailout_card(review_context, previous_quiz)

        self.assertEqual("modeling.method_selection", card["card_id"])
```

- [ ] **Step 3: 写 trie 机制桥仍应存在的失败测试**

```python
    def test_generate_knowledge_bailout_card_should_route_explicit_shared_prefix_focus_to_trie_card(self):
        review_context = {
            "focus": "shared_prefix_merging",
            "problem_title": "P2922 [USACO08DEC] Secret Message G",
            "bottleneck_text": "我不懂为什么查询时不用重看所有消息，只沿当前前缀往下走。",
            "error_layer": "method",
            "key_bridge": "公共前缀先合在一起，所以查询时只沿当前前缀路径走。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("string.trie.shared_prefix_merging", card["card_id"])
```

- [ ] **Step 4: 写 `lazy_semantics` 链路缺失的失败测试**

```python
    def test_generate_knowledge_bailout_card_should_support_lazy_semantics(self):
        review_context = {
            "focus": "lazy_semantics",
            "problem_title": "P3372 线段树 1",
            "bottleneck_text": "我不明白 lazy 标记到底表示什么。",
            "error_layer": "core_design",
            "key_bridge": "lazy 记录的是还没下传的信息，不是还没执行完的代码。",
        }

        card = review_engine.generate_knowledge_bailout_card(review_context)

        self.assertEqual("segment_tree.lazy_semantics", card["card_id"])
```

- [ ] **Step 5: 写方法桥 fallback/backfill 不应退回泛 modeling 的失败测试**

```python
    def test_backfill_student_guidance_should_fill_method_selection_with_signal_specific_language(self):
        review = {
            "error_layer": "method",
            "focus": "method_selection",
            "problem_focus": "",
            "key_bridge": "",
            "guided_walkthrough": "",
            "try_now": "",
            "transfer_signal": "",
        }

        filled = review_engine._backfill_student_guidance(review)

        self.assertIn("结构信号", filled["key_bridge"])
        self.assertIn("题面", filled["try_now"])
```

- [ ] **Step 6: 跑失败测试，确认真红**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:
- 新增测试至少有一部分失败
- 失败点正好落在左边界桥、trie 方法桥拆分、lazy 语义桥、backfill 这几处

### Task 2: 修桥检测与主链路 focus

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 扩充 focus 常量与默认桥文本**

需要补进：
- `left_bound_update`
- `shared_prefix_merging`
- `lazy_semantics`

并同步：
- `STRUCTURAL_QUIZ_FOCI`
- `HIGH_RISK_REVIEW_FOCI`（按需要）
- `_default_target_bridge(...)`
- `_infer_algorithm_category(...)` 的命名映射

- [ ] **Step 2: 修 `_detect_quiz_focus(...)`**

目标：
- `P2249` 这类 `a[mid]==x` / `mid-1` / 左边界语义优先判到 `left_bound_update`
- method 桥里，只有明确出现“公共前缀合在一起 / 不用重看所有消息 / 沿当前前缀走”这类机制语言时，才判到 `shared_prefix_merging`
- 仅出现 `trie / 前缀 / 消息` 但学生真正问“为什么该用 trie”时，仍保留 `method_selection`
- 对 `lazy / 下传 / 标记 / 区间加 / 线段树` 这类语言，允许命中 `lazy_semantics`

- [ ] **Step 3: 修 method 主轮，不再把 trie 题直接改成机制题**

目标：
- `_main_quiz_payload(...)` 里 `focus == "method_selection"` 时
- 如果题目是 trie 语境，主轮仍先问“题面里哪个结构信号支持 trie”
- `shared_prefix_merging` 才问“为什么不用重看所有消息”

- [ ] **Step 4: 修 followup/final 对应关系**

目标：
- `method_selection` 的 second/final 都继续围绕“结构信号”
- `shared_prefix_merging` 的 second/final 围绕“公共前缀合并 / 不重看所有消息”
- `left_bound_update` 和 `lazy_semantics` 都有 main/followup/final 三层 deterministic 题

- [ ] **Step 5: 跑单测**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:
- Task 1 的新增测试全部转绿
- 原有 state/transition/check/greedy/tree/trie 相关测试不回退

### Task 3: 补 knowledge card / knowledge confirm / backfill

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 给 `left_bound_update` 增知识卡与确认题**

内容方向：
- 误解：命中后直接丢掉 `mid`
- 正解：如果要找最左边界，命中后还要保留 `mid` 这一侧继续找

- [ ] **Step 2: 给 `lazy_semantics` 增知识卡与确认题**

内容方向：
- 误解：lazy 是“还没执行完的代码”
- 正解：lazy 是“还没下传到子节点的信息”

- [ ] **Step 3: 修 `_knowledge_card_id(...)`**

目标：
- `method_selection` 默认回 `modeling.method_selection`
- `shared_prefix_merging` 才回 `string.trie.shared_prefix_merging`
- `lazy_semantics` 回 `segment_tree.lazy_semantics`

- [ ] **Step 4: 修 `_backfill_student_guidance(...)`**

目标：
- 给 `method_selection`
- `complexity_fit`
- `shared_prefix_merging`
- `left_bound_update`
- `lazy_semantics`

补专门 guidance，不再掉回 `general_modeling / state_design`

- [ ] **Step 5: 跑单测**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:
- 知识卡与确认题新增测试通过
- backfill 新增测试通过

### Task 4: 给高频桥补参数化 deterministic remedy

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 为这些 focus 添加专门 fallback remedy**

范围：
- `method_selection`
- `complexity_fit`
- `shared_prefix_merging`
- `lazy_semantics`
- `left_bound_update`

要求：
- 先说“最容易误会什么”
- 再说“真正要站稳什么”
- `visual_hint` 贴当前桥
- `micro_action` 只问当前桥的一小步

- [ ] **Step 2: 加回归测试，防止 fallback 讲偏**

示例检查：
- trie 桥 fallback 不再掉成树直径 visual hint
- `method_selection` fallback 里必须出现“题面/结构信号”
- `complexity_fit` fallback 里必须出现“规模/总量级/双层”
- `lazy_semantics` fallback 里必须出现“下传/信息”

- [ ] **Step 3: 跑聚焦测试**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py
```

Expected:
- 都通过

### Task 5: 同步 harness 并做整体验证

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/project_invariants.md`（只在长期规则发生变化时）

- [ ] **Step 1: 同步当前真实状态**

要写入：
- 新增 focus：
  - `left_bound_update`
  - `shared_prefix_merging`
  - `lazy_semantics`
- `method_selection` 与 trie 机制桥已经拆开
- 高频桥 fallback 已有专门桥级文案

- [ ] **Step 2: 跑完整回归**

Run:
```bash
bash /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh
```

Expected:
- 后端回归通过
- 学习流集成通过
- 前端 Node 测试不回退
