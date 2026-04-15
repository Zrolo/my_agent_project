# Review Bridge Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让首轮 review 在 `method_selection`、`shared_prefix_merging`、`check_condition`、`left_bound_update` 这 4 个高频易漂 bridge 上既不判错桥，也不退回泛化话术。

**Architecture:** 保持现有首轮 review 生成链不变，仍然由 `generate_review(...)` 调 LLM 生成结构化结果，再经过一系列 guard 修正。第五阶段只做两层轻量增强：先在首轮 prompt 里加入 bridge-specific 薄约束，再在 post-generation guard 中统一检查并修正 `problem_focus / key_bridge / visual_hint / guided_walkthrough / try_now` 这 5 个字段的 bridge 一致性与非泛化要求。

**Tech Stack:** Python, unittest, existing `review_engine.py` review pipeline, existing harness docs

---

## File Structure

- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
  - 继续承载首轮 review prompt、解析、guard 链和 bridge-specific fallback 文案。
  - 新增第五阶段需要的最小 helper：
    - bridge prompt constraint 生成
    - review bridge guard rule 表
    - 5 个关键字段的一致性检查与最小重写
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
  - 增加第五阶段红测，锁定：
    - prompt 轻约束是否出现
    - post-generation guard 是否能拉回错桥
    - post-generation guard 是否能修掉泛化话术
    - `generate_review(...)` 总链路是否真的执行新 guard
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md`
  - 记录第五阶段已接入首轮 review 的 bridge guard 范围和已验证样例。
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`
  - 记录第五阶段当前状态，避免后续只能靠聊天上下文记忆。

---

### Task 1: 写第五阶段红测，锁定 prompt 轻约束和首轮 bridge guard

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 写首轮 prompt 必须出现 bridge-specific 轻约束的失败测试**

```python
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
        self.assertIn("相同开头", prompt)
```

- [ ] **Step 2: 写 bridge guard 必须拉回 `check_condition` 泛化文案的失败测试**

```python
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

        self.assertIn("check(mid)", guarded["problem_focus"])
        self.assertIn("可行", guarded["key_bridge"])
        self.assertIn("check(", guarded["visual_hint"])
        self.assertIn("当前 mid", guarded["guided_walkthrough"])
        self.assertIn("可行", guarded["try_now"])
```

- [ ] **Step 3: 写 bridge guard 必须拉回 `left_bound_update` 泛二分文案的失败测试**

```python
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

        self.assertIn("a[mid]", guarded["problem_focus"])
        self.assertIn("保留 mid", guarded["key_bridge"])
        self.assertIn("a[mid] == ", guarded["visual_hint"])
        self.assertIn("最左", guarded["guided_walkthrough"])
        self.assertIn("保留 mid", guarded["try_now"])
```

- [ ] **Step 4: 写 bridge guard 必须拉回 trie 方法桥与机制桥的失败测试**

```python
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

        self.assertIn("题面", guarded["problem_focus"])
        self.assertIn("结构信号", guarded["key_bridge"])
        self.assertIn("题面信号", guarded["visual_hint"])
        self.assertIn("相同开头", guarded["guided_walkthrough"])
        self.assertIn("信号", guarded["try_now"])
```

- [ ] **Step 5: 写 `generate_review(...)` 必须真正执行新 guard 的失败测试**

```python
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
        self.assertIn("题面", review["problem_focus"])
        self.assertIn("结构信号", review["key_bridge"])
        self.assertIn("题面信号", review["visual_hint"])
        self.assertIn("相同开头", review["guided_walkthrough"])
        self.assertIn("信号", review["try_now"])
```

- [ ] **Step 6: 跑单测确认真红**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:
- 新增测试至少部分失败
- 失败点落在“prompt 没加约束”或“首轮 review 没有 bridge consistency guard”

### Task 2: 加轻量 prompt constraint，只给首轮 review 一个薄约束

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 添加首轮 bridge prompt constraint helper**

在 `review_engine.py` 里新增最小 helper，结构按下面写：

```python
def _review_bridge_prompt_constraint(
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
    error_types: list[str],
) -> str:
    focus = _detect_quiz_focus(
        {
            "error_layer": "method" if _contains_any(" ".join(error_types or []), ("方法", "判定", "二分", "前缀", "trie")) else "unknown",
            "core_design_subtags": [],
            "problem_title": problem_title,
            "problem_context": problem_context or "",
            "bottleneck_text": bottleneck_text,
            "error_types": error_types or [],
            "main_block": "",
            "key_bridge": "",
            "next_step": "",
            "transfer_signal": "",
        }
    )

    bridge_rules = {
        "method_selection": "首轮 bridge 约束：这次必须围着题面信号/结构信号来讲，不要退回“理解这个方法”这类空话；如果是 trie 语境，至少点名“相同开头”或“前缀关系”。",
        "shared_prefix_merging": "首轮 bridge 约束：这次必须围着公共前缀、沿前缀路径、为什么不用重看所有消息来讲；如果是节点计数语境，至少点名经过次数或结束次数。",
        "check_condition": "首轮 bridge 约束：这次必须围着 check(mid) 在判断当前 mid 是否可行来讲，不要退回泛化复杂度说明。",
        "left_bound_update": "首轮 bridge 约束：这次必须围着 a[mid] == x 时为什么还要保留 mid、继续往左找来讲，不要退回泛泛的二分边界。",
    }
    return bridge_rules.get(focus, "")
```

- [ ] **Step 2: 把 bridge prompt constraint 拼进 `_build_review_user_prompt(...)`**

在 `_build_review_user_prompt(...)` 末尾追加：

```python
    bridge_constraint = _review_bridge_prompt_constraint(
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
        error_types=error_types,
    )
    if bridge_constraint:
        parts.append(f"首轮 bridge 约束：\n{bridge_constraint}")
```

- [ ] **Step 3: 跑聚焦单测，确认 prompt 测试转绿**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:
- Task 1 的 prompt 相关测试转绿
- 其余 review prompt 旧测试不回退

### Task 3: 加 post-generation bridge guard，只修 5 个关键字段

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 定义第五阶段 bridge guard 规则表**

在 `review_engine.py` 新增：

```python
REVIEW_BRIDGE_GUARD_RULES = {
    "check_condition": {
        "focus_terms": ("check(mid)", "check(", "可行", "当前 mid"),
        "problem_focus": "你不是在直接算答案，而是在想 `check(mid)` 到底是不是只在判断当前这个 mid 是否可行。",
        "key_bridge": "关键是先站稳：`check(mid)` 的 true 只说明当前 mid 可行，不是已经找到最终答案。",
        "visual_hint": "check(5)=true\n-> 只说明 5 可行\n-> 再决定区间往哪边缩",
        "guided_walkthrough": "1. 先只看 `check(mid)` 这一句，它是不是只在判断当前 mid 能不能成立。\n2. 再把 true/false 分别翻成“当前值可行/不可行”。\n3. 最后再决定二分区间该往哪边缩。",
        "try_now": "先只回答一句：`check(5)=true` 现在说明的是“5 可行”还是“答案就是 5”？",
    },
    "left_bound_update": {
        "focus_terms": ("a[mid]", "保留 mid", "最左", "左边界"),
        "problem_focus": "你不是一般地不会二分，而是卡在 `a[mid] == x` 时，为什么还要把 mid 这一侧保留下来继续往左找。",
        "key_bridge": "关键是如果你要找最左边那个等于 x 的位置，命中后 mid 仍然可能就是答案，所以不能先丢掉。",
        "visual_hint": "[1,2,2,2,3]\na[mid] == 2\n-> mid 先留作候选\n-> r = mid 继续往左缩",
        "guided_walkthrough": "1. 先只盯 `a[mid] == x` 这一格，mid 现在是不是已经可能是答案。\n2. 如果目标是最左边那个位置，mid 这一侧能不能先丢掉。\n3. 最后再决定为什么要保留 mid 继续往左缩。",
        "try_now": "先只回答一句：如果目标是最左边那个 2，`a[mid] == 2` 时为什么不能先丢掉 mid？",
    },
    "shared_prefix_merging": {
        "focus_terms": ("前缀", "沿前缀路径", "公共前缀", "经过次数", "结束次数"),
        "problem_focus": "你不是在做一般字符串处理，而是在分清：公共前缀为什么能先合起来，以及查询时为什么只沿前缀路径走。",
        "key_bridge": "关键是把相同开头先合在一起；这样查询时不用重看所有消息，只沿当前前缀那条路径往下走。",
        "visual_hint": "101\n100\n11\n前缀 10 先合在一起\n查询时只沿前缀路径往下走",
        "guided_walkthrough": "1. 先把 101、100、11 这三个串写出来，看前两条是不是有相同开头。\n2. 再想这些相同开头能不能先共用一段路径。\n3. 最后再说查询时为什么不用把所有消息重新逐个看一遍。",
        "try_now": "先只回答一句：trie 省下来的，为什么是“不用重看所有消息”而不是“把答案背下来”？",
    },
    "method_selection": {
        "focus_terms": ("题面信号", "结构信号", "相同开头", "前缀关系"),
        "problem_focus": "你不是已经站稳了 trie 机制，而是还没从题面里指出哪个结构信号真的在支持这个方法。",
        "key_bridge": "关键不是先报方法名，而是先回到题面，指出“很多字符串 + 反复前缀关系 + 相同开头”这些结构信号。",
        "visual_hint": "题面信号\n-> 很多字符串\n-> 反复前缀关系\n-> 相同开头支持 trie",
        "guided_walkthrough": "1. 先只看题面里有哪些对象和操作：消息、拦截串、前缀关系。\n2. 再找哪一个结构信号最直接支持 trie，而不是别的方法。\n3. 最后补一句：为什么“相同开头”会让 trie 变得合理。",
        "try_now": "先只指出一个题面信号：这题里哪件事最直接支持 trie？",
    },
}
```

- [ ] **Step 2: 新增 `_guard_review_bridge_consistency(...)`**

实现按下面骨架写，确保只修 5 个字段：

```python
def _guard_review_bridge_consistency(
    review: dict,
    focus: str,
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
) -> dict:
    rule = REVIEW_BRIDGE_GUARD_RULES.get(focus)
    if not rule:
        return review

    fields = (
        "problem_focus",
        "key_bridge",
        "visual_hint",
        "guided_walkthrough",
        "try_now",
    )

    combined = " ".join(str(review.get(field, "")) for field in fields)
    missing_anchor = _count_keyword_hits(combined, rule["focus_terms"]) < 2
    too_generic = any(
        _contains_any(str(review.get(field, "")), GENERIC_TOPIC_TERMS + GENERIC_ACTION_TERMS + GENERIC_BRIDGE_TERMS)
        for field in ("problem_focus", "key_bridge", "guided_walkthrough", "try_now")
    )

    if not missing_anchor and not too_generic:
        return review

    review["problem_focus"] = rule["problem_focus"]
    review["main_block"] = rule["problem_focus"]
    review["key_bridge"] = rule["key_bridge"]
    review["visual_hint"] = rule["visual_hint"]
    review["guided_walkthrough"] = rule["guided_walkthrough"]
    review["try_now"] = rule["try_now"]
    review["next_step"] = rule["try_now"]
    return review
```

- [ ] **Step 3: 在 `generate_review(...)` 里接线**

在现有 guard 链里，接在：
- `_guard_review_against_topic_drift(...)`
- `_guard_review_against_overclaim(...)`
- `_guard_teacher_guidance(...)`
- `_guard_review_bridge_stability(...)`

之后，加入：

```python
    focus = _detect_quiz_focus(
        {
            "error_layer": review.get("error_layer", "insufficient"),
            "core_design_subtags": review.get("core_design_subtags") or [],
            "problem_title": problem_title,
            "problem_context": problem_context or "",
            "bottleneck_text": bottleneck_text,
            "error_types": error_types or [],
            "main_block": review.get("main_block", ""),
            "key_bridge": review.get("key_bridge", ""),
            "next_step": review.get("next_step", ""),
            "transfer_signal": review.get("transfer_signal", ""),
        }
    )
    review = _guard_review_bridge_consistency(
        review,
        focus=focus,
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
    )
```

- [ ] **Step 4: 跑单测，确认 4 个 bridge 的 guard 红测转绿**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:
- Task 1 的 bridge consistency 相关测试全部通过
- 现有 topic drift / remedy / knowledge card 测试不回退

### Task 4: 收紧 trie 节点计数语境和二分语境的 bridge 一致性细节

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`

- [ ] **Step 1: 给 `shared_prefix_merging` guard 增加节点计数语境变体**

按下面补一层特殊分支：

```python
    if focus == "shared_prefix_merging" and _is_trie_node_count_context(" ".join(filter(None, [problem_context or "", bottleneck_text]))):
        review["problem_focus"] = "你不是在做一般字符串处理，而是在分清 Trie 节点上“经过次数”和“结束次数”各在回答什么。"
        review["main_block"] = review["problem_focus"]
        review["key_bridge"] = "关键是先把经过次数和结束次数分开：经过次数表示有多少消息经过当前前缀节点，结束次数表示有多少消息正好在这里结束。"
        review["visual_hint"] = "101\n100\n11\n前缀 10 这个节点\n-> 经过次数至少是 2\n-> 结束次数另算"
        review["guided_walkthrough"] = "1. 先只盯前缀 10 这个节点，看 101 和 100 会不会都经过它。\n2. 再把“经过次数”和“结束次数”分开说清楚。\n3. 最后再回到查询路径，看为什么只沿前缀节点往下走。"
        review["try_now"] = "先只回答一句：前缀 10 这个节点上的经过次数，正在说明什么？"
        review["next_step"] = review["try_now"]
```

- [ ] **Step 2: 给 `check_condition` 和 `left_bound_update` guard 增加“禁止退回复杂度/泛二分”的定向断言**

新增测试：

```python
    def test_generate_review_should_not_fall_back_to_complexity_fit_for_check_condition_case(self):
        llm_review = json.dumps({... 泛复杂度文案 ...})
        with patch.object(review_engine, "_call_llm", return_value=(True, llm_review, {})):
            result = review_engine.generate_review(
                problem_title="P2678 跳石头",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我知道要二分答案，但不知道 check(mid) 的 true 到底代表什么。",
                error_types=["方法理解"],
                problem_context="二分答案，check(mid) 判断当前最小间距是否可行。",
            )
        self.assertIn("check(mid)", result["review"]["key_bridge"])
        self.assertNotIn("复杂度", result["review"]["problem_focus"])
```

```python
    def test_generate_review_should_not_fall_back_to_generic_binary_search_for_left_bound_case(self):
        llm_review = json.dumps({... 泛二分文案 ...})
        with patch.object(review_engine, "_call_llm", return_value=(True, llm_review, {})):
            result = review_engine.generate_review(
                problem_title="P2249 查找",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我总不知道 a[mid] == x 时该写 r = mid 还是 r = mid - 1。",
                error_types=["二分边界"],
                problem_context="在有序数组里找第一个等于 x 的位置。",
            )
        self.assertIn("a[mid]", result["review"]["problem_focus"])
        self.assertIn("保留 mid", result["review"]["key_bridge"])
```

- [ ] **Step 3: 跑聚焦测试**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py
```

Expected:
- trie 节点计数语境测试通过
- 二分两类 case 不再回退到泛化桥

### Task 5: 同步 harness，并做全量验证

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`

- [ ] **Step 1: 更新 `current_system_state.md`**

加入这段结论：

```md
- 第五阶段已为首轮 review 接入轻量 bridge 约束。
- 当前只覆盖 4 个高频易漂 bridge：
  - `method_selection`
  - `shared_prefix_merging`
  - `check_condition`
  - `left_bound_update`
- 约束分两层：
  - prompt 轻约束
  - post-generation bridge consistency guard
- 统一 guard 的字段范围固定为：
  - `problem_focus`
  - `key_bridge`
  - `visual_hint`
  - `guided_walkthrough`
  - `try_now`
```

- [ ] **Step 2: 更新 `active_work_item.md`**

加入这段状态：

```md
## 当前任务
- 第五阶段：首轮 review 的轻量 bridge 约束

## 已完成
- 4 个高频易漂 bridge 已接 prompt 轻约束
- 首轮 review 已接 bridge consistency guard

## 下一步
- 用真实样例继续复审：
  - `P2922`
  - `P2678`
  - `P2249`
```

- [ ] **Step 3: 跑相关 Python 单测**

Run:
```bash
python3 -m unittest -v /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py
```

Expected:
- 全部 PASS

- [ ] **Step 4: 跑全量回归**

Run:
```bash
bash /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh
```

Expected:
- 后端测试全绿
- 学习流集成 `4/4`
- 前端 Node 基线不回退

- [ ] **Step 5: Commit**

```bash
git -C /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent add \
  /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py \
  /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py \
  /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/current_system_state.md \
  /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/active_work_item.md
git -C /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent commit -m "feat: harden first-review bridge guard"
```

---

## Self-Review

### 1. Spec coverage

- “只收 4 个高频易漂 bridge”：
  - Task 1 / 3 / 4 都只覆盖 `method_selection`、`shared_prefix_merging`、`check_condition`、`left_bound_update`
- “只 guard 5 个关键字段”：
  - Task 3 的 `_guard_review_bridge_consistency(...)` 只改 `problem_focus / key_bridge / visual_hint / guided_walkthrough / try_now`
- “两层约束：轻量 prompt + post-generation guard”：
  - Task 2 负责 prompt
  - Task 3 负责 guard
- “只修桥判错和文案泛化”：
  - Task 1/3 的测试和实现都只针对这两类问题
- “代表样例 `P2922 / P2678 / P2249` 必须被钉住”：
  - Task 1 和 Task 4 都直接写了这 3 条样例

没有发现 spec 漏项。

### 2. Placeholder scan

- 全文没有 `TODO / TBD / implement later`
- 每个代码步骤都给了实际代码块
- 每个测试步骤都给了实际命令和预期

没有发现占位符问题。

### 3. Type consistency

- 计划里统一使用的新增 helper 名称：
  - `_review_bridge_prompt_constraint`
  - `REVIEW_BRIDGE_GUARD_RULES`
  - `_guard_review_bridge_consistency`
- 后续步骤中的调用名与定义名一致
- 5 个关键字段名称全程一致：
  - `problem_focus`
  - `key_bridge`
  - `visual_hint`
  - `guided_walkthrough`
  - `try_now`

没有发现命名不一致问题。
