# Review Bridge Stability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 收紧 `review -> key_bridge / next_step` 的上游稳定性，让 4 个高风险 focus 先在 review 层不再明显漂到泛建议，再进入 quiz 层优化。

**Architecture:** 这轮只动 review 生成与 review guard，不动 quiz prompt 主模板和前端。先把回归样例补进 `test_review_regression.py`，再最小修改 `review_engine.py` 的 review prompt、默认回退文案和通用 guard，最后用现有回归脚本验证 4 个高风险 focus 的 `key_bridge / next_step` 是否更贴样例预期。

**Tech Stack:** Python, Markdown, `review_engine.py`, `test_review_regression.py`, `rg`, `python3`

---

## File Structure

- Modify: `review_engine.py`
  - 收紧 review prompt 对 `key_bridge / next_step` 的要求；必要时补或收紧通用 guard。
- Modify: `test_review_regression.py`
  - 增加或调整 4 个高风险 focus 的回归样例，让测试更直接盯住 `key_bridge / next_step`。
- Reference: `docs/harness/review_quiz_quality_gate.md`
  - 作为放行口径，不直接修改。
- Reference: `docs/subjects/noi/focus_quality_eval_v1.md`
  - 作为 4 个高风险 focus 的具体样例来源，不直接修改。
- Modify: `docs/harness/current_system_state.md`
  - 本轮完成后同步“review 层收紧”的已落地状态。
- Modify: `docs/harness/active_work_item.md`
  - 本轮完成后同步完成状态与下一步。

---

### Task 1: 把 4 个高风险 focus 的 review 预期补进回归测试

**Files:**
- Modify: `test_review_regression.py`
- Reference: `docs/subjects/noi/focus_quality_eval_v1.md`
- Reference: `docs/harness/review_quiz_quality_gate.md`

- [ ] **Step 1: 找到现有高风险 focus 的回归样例位置**

Run: `rg -n 'general_modeling|constraint_modeling|greedy_basis|method_selection|key_bridge_terms|next_step_terms' test_review_regression.py`

Expected:
- 能定位现有样例定义
- 能看到 `key_bridge_terms` / `next_step_terms` 的使用方式

- [ ] **Step 2: 先写失败预期，补齐 4 个 focus 的关键词约束**

```python
ReviewCase(
    name="general_modeling should stay on object-edge mapping",
    review_input={
        "problem_context": "课程之间有先修关系，问怎样表示课程依赖。",
        "bottleneck_text": "我知道像图，但分不清课程和依赖关系分别放在哪里。",
        "completion_status": "没思路",
    },
    key_bridge_terms=("点", "边", "课程", "依赖"),
    next_step_terms=("对象", "关系", "写", "对应"),
)
```

- [ ] **Step 3: 运行单测，确认当前版本至少有一条不满足新约束**

Run: `python3 test_review_regression.py`

Expected:
- 至少出现一条关于 `key_bridge` 或 `next_step` 的 warning / fail
- 能看出当前漂移点在哪个 focus

- [ ] **Step 4: 补齐另外 3 个 focus 的回归样例**

```python
ReviewCase(
    name="constraint_modeling should stay on simultaneous constraints",
    review_input={
        "problem_context": "每个活动都必须同时满足时间窗口和指定地点这两个条件，才算合法安排。",
        "bottleneck_text": "我总把它们看成一个主条件加一个顺手检查。",
        "completion_status": "没思路",
    },
    key_bridge_terms=("同时", "限制", "合法", "条件"),
    next_step_terms=("整理", "标出", "同时", "条件"),
)
```

```python
ReviewCase(
    name="greedy_basis should stay on safety basis",
    review_input={
        "problem_context": "有 n 个区间，目标是最大化选出的区间数量，且任意两个被选区间不能重叠。",
        "bottleneck_text": "我知道常见做法是先选结束时间最早的区间，但不知道它为什么能留下最多后续空间。",
        "completion_status": "会做一点",
    },
    key_bridge_terms=("结束", "兼容", "后续", "空间"),
    next_step_terms=("画", "区间", "比较", "兼容"),
)
```

```python
ReviewCase(
    name="method_selection should stay on single method boundary",
    review_input={
        "problem_context": "n <= 20，需要枚举所有子集并从中找最优方案。",
        "bottleneck_text": "我一看到最优值就想套 DP，但没判断这个规模其实允许直接枚举。",
        "completion_status": "没思路",
    },
    key_bridge_terms=("n<=20", "枚举", "子集", "规模"),
    next_step_terms=("判断", "规模", "枚举", "全部"),
)
```

- [ ] **Step 5: 再跑一次回归，记录失败点**

Run: `python3 test_review_regression.py`

Expected:
- 输出能明确指出 4 个高风险 focus 里哪些 bridge / next_step 仍然漂

- [ ] **Step 6: 提交本任务**

```bash
git add test_review_regression.py
git commit -m "test: tighten review bridge regression cases"
```

---

### Task 2: 收紧 review prompt 对 key_bridge / next_step 的直接约束

**Files:**
- Modify: `review_engine.py`
- Test: `test_review_regression.py`
- Reference: `docs/harness/review_quiz_quality_gate.md`

- [ ] **Step 1: 找到 review prompt 生成区和当前 `key_bridge / next_step` 约束**

Run: `sed -n '2350,2455p' review_engine.py`

Expected:
- 能看到 review prompt 主体
- 能看到 `key_bridge` / `next_step` 的当前要求

- [ ] **Step 2: 在 review prompt 里补 4 条直接约束**

```python
15. `key_bridge` 必须落到当前题目的单一结构桥梁，禁止写成“先理解题意”“先分析对象关系”这种泛建议。
16. `next_step` 必须是围绕同一桥梁的 1-2 个微动作，禁止写成长线学习计划。
17. 对 `general_modeling / constraint_modeling / greedy_basis / method_selection`，优先写结构对应关系，不要先报算法名。
18. 如果当前输入不足以稳定落到单一结构桥梁，宁可转入保守表达，也不要硬写泛化 bridge。
```

- [ ] **Step 3: 跑回归，确认 warning 数量下降**

Run: `python3 test_review_regression.py`

Expected:
- 至少有部分高风险 focus 的 `key_bridge` / `next_step` warning 消失

- [ ] **Step 4: 如果还漂，最小补一条 prompt 文案收紧**

```python
19. `key_bridge` 必须写“什么对象 / 关系 / 条件 / 安全性依据 / 方法边界”中的一个具体结构，不允许同时混写两座桥。
```

- [ ] **Step 5: 再跑回归，保留输出作为后续 guard 设计依据**

Run: `python3 test_review_regression.py`

Expected:
- 仍失败的 focus 明显收窄到少数具体桥梁

- [ ] **Step 6: 提交本任务**

```bash
git add review_engine.py
git commit -m "refactor: tighten review bridge prompt rules"
```

---

### Task 3: 最小收紧 review guard，拦住仍然明显漂的 bridge

**Files:**
- Modify: `review_engine.py`
- Test: `test_review_regression.py`
- Reference: `docs/subjects/noi/focus_quality_eval_v1.md`

- [ ] **Step 1: 找到现有 review guard 落点**

Run: `rg -n '_guard_review_against_topic_drift|_guard_review_against_overclaim|_guard_review_for_insufficient|key_bridge|next_step' review_engine.py`

Expected:
- 能定位通用 guard 和默认兜底文案

- [ ] **Step 2: 只为 4 个高风险 focus 加最小 guard，不做大重构**

```python
if focus == "general_modeling" and "算法" in review.get("key_bridge", ""):
    review["key_bridge"] = "关键是先确定题目里的对象是什么、关系是什么，再决定图里点和边分别表示什么。"
    review["next_step"] = "先写两行：点表示什么，边表示什么，不要先写算法名。"
```

```python
if focus == "method_selection" and "dp" in review.get("key_bridge", "").lower():
    review["key_bridge"] = "关键不是先报方法名，而是先看题面给出的规模和结构，判断这一步到底允许枚举还是需要状态转移。"
    review["next_step"] = "先只判断一件事：数据范围是否已经允许直接枚举，再决定要不要继续想 DP。"
```

- [ ] **Step 3: 运行回归，确认 4 个高风险 focus 不再明显漂到泛建议**

Run: `python3 test_review_regression.py`

Expected:
- 不再出现大面积 `key_bridge` / `next_step` 漂到泛化建议的 warning

- [ ] **Step 4: 运行基础语法检查**

Run: `python3 -m py_compile review_engine.py`

Expected: 无输出

- [ ] **Step 5: 提交本任务**

```bash
git add review_engine.py
git commit -m "fix: guard unstable review bridges for high-risk focus"
```

---

### Task 4: 同步 harness 状态文件

**Files:**
- Modify: `docs/harness/current_system_state.md`
- Modify: `docs/harness/active_work_item.md`

- [ ] **Step 1: 更新 current_system_state**

```markdown
## 六、quiz / 理解检查当前真实状态

当前 review 生成链路已针对 4 个高风险 focus 收紧 `key_bridge / next_step`：

- `general_modeling`
- `constraint_modeling`
- `greedy_basis`
- `method_selection`

当前这轮收紧主要依赖：

- review prompt 约束增强
- review 通用 guard 收紧
```

- [ ] **Step 2: 更新 active_work_item**

```markdown
## 下一步建议

1. 在 review 稳住后，再进入 quiz 放行 / fallback 收紧
2. 优先补局部复测入口，再决定是否需要全量复测
```

- [ ] **Step 3: 提交本任务**

```bash
git add docs/harness/current_system_state.md docs/harness/active_work_item.md
git commit -m "docs: sync harness after review bridge tightening"
```

---

### Task 5: 全量验证与收口

**Files:**
- Test: `review_engine.py`
- Test: `test_review_regression.py`
- Test: `docs/harness/current_system_state.md`
- Test: `docs/harness/active_work_item.md`

- [ ] **Step 1: 跑 review 回归**

Run: `python3 test_review_regression.py`

Expected:
- 4 个高风险 focus 不再明显报 bridge / next_step 漂移 warning

- [ ] **Step 2: 跑基础语法检查**

Run: `python3 -m py_compile review_engine.py`

Expected: 无输出

- [ ] **Step 3: 检查 harness 同步文件没有写未来式**

Run: `rg -n '继续优化|仍在持续|待以后|productized|未来' docs/harness/current_system_state.md docs/harness/active_work_item.md`

Expected: 无输出

- [ ] **Step 4: 提交最终收尾**

```bash
git add review_engine.py test_review_regression.py docs/harness/current_system_state.md docs/harness/active_work_item.md
git commit -m "feat: tighten review bridge stability for high-risk focus"
```

---

## Self-Review Checklist

- [ ] 计划只覆盖本轮真实目标：`review -> key_bridge / next_step`
- [ ] 没有提前混入 quiz 覆盖率优化
- [ ] 每个任务都有明确文件、命令、预期结果
- [ ] 回归样例与 4 个高风险 focus 对齐
- [ ] harness 同步步骤只写本轮已落地状态
