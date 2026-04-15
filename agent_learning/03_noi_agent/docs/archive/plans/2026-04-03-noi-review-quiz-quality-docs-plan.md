# NOI Review + Quiz 质量文档 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地第一版 `review + quiz` 质量闭环文档，先写 harness 级质量门，再写 NOI 专项评测样例文档，并把 Claude 审核通过的两条优化一起吸收进去。

**Architecture:** 采用两层文档分工。`docs/harness/review_quiz_quality_gate.md` 只承载跨 focus 通用的硬门槛与复测门；`docs/subjects/noi/focus_quality_eval_v1.md` 只承载 4 个高风险 focus 的评测样例、坏例和 rubric。执行时先写质量门，再写样例文档，最后做一致性检查，避免两层文档互相污染。

**Tech Stack:** Markdown, `apply_patch`, `sed`, `rg`, `git`

---

## File Structure

- Create: `docs/harness/review_quiz_quality_gate.md`
  - 负责承载 `review` 放行条件、`quiz` 放行条件、`fallback` 必触条件、`fallback` 克制规则、复测门触发条件。
- Create: `docs/subjects/noi/focus_quality_eval_v1.md`
  - 负责承载 4 个 focus 的评测样例模板、样例字段、样例优先级、rubric、记录实际输出的方式。
- Modify: `docs/harness/active_work_item.md`
  - 负责把当前工作项从“spec 设计”推进到“文档落地 / 待实现”状态。
- Modify: `docs/harness/current_system_state.md`
  - 只在本轮实际新增质量文档后补一行当前已落地的文档状态，不写未来计划。

---

### Task 1: 写 Harness 级质量门文档

**Files:**
- Create: `docs/harness/review_quiz_quality_gate.md`
- Reference: `docs/harness/ai_output_contracts.md`
- Reference: `docs/superpowers/specs/2026-04-03-noi-review-quiz-quality-loop-design.md`

- [ ] **Step 1: 起草文档骨架**

```markdown
# Review + Quiz 质量门

## 本文件的写入标准

只写跨 focus 通用的最小质量门：

- review 放行条件
- quiz 放行条件
- fallback 必触条件
- fallback 克制规则
- 复测门触发条件

不要写：

- 具体题目样例
- 某个 focus 的特例
- 某次 prompt 调参经验
```

- [ ] **Step 2: 写 review / quiz / fallback 规则正文**

```markdown
## 一、Review 放行条件

1. `key_bridge` 必须对应学生这次真实卡点
2. `next_step` 必须是当前桥梁下的可执行小步
3. 不得滑成学习建议、方法口号或泛化迁移建议
4. 不得用同类题套路替代本题结构判断
5. `main_block / key_bridge / next_step / transfer_signal` 必须指向同一个结构问题

## 二、Quiz 放行条件

1. 正确答案必须是结构事实
2. 必须贴原题语境测当前桥梁
3. `main / followup / confirm` 必须围绕同一桥梁
4. 每个错误选项必须对应具体结构误区
5. `bridge_feedback` 必须指出学生答对的结构事实
6. `distractor_feedback` 必须指出学生答错的具体结构

## 三、Fallback 必触条件

1. 当前桥梁无法稳定落成结构事实题
2. 正确答案本质属于 `learning_advice`
3. 题目已滑成口号题、策略题、泛方法题
4. `confirm` 的新情境已改变核心结构事实，而不只是表面场景变化
```

- [ ] **Step 3: 吸收 Claude 的两条优化**

```markdown
## 四、Fallback 克制规则

`fallback_explain` 只说明“当前桥梁不适合出结构事实题”，
不展开长讲解，不替代 `remedy`。

## 五、复测门触发条件

### 必须全量复测

- `review prompt` 改动
- `quiz prompt` 改动
- 全局规则改动
- 后端通用 guard 改动

### 只需局部复测

- 单个 focus snippet 改动，只复测对应 focus 的 3 组样例
```

- [ ] **Step 4: 检查文档边界**

Run: `sed -n '1,260p' docs/harness/review_quiz_quality_gate.md`

Expected:
- 能看到“写入标准”
- 没有具体题目样例
- 没有 `TBD` / `TODO`

- [ ] **Step 5: 提交本任务**

```bash
git add docs/harness/review_quiz_quality_gate.md
git commit -m "docs: add review quiz quality gate"
```

---

### Task 2: 写 NOI 专项评测样例文档

**Files:**
- Create: `docs/subjects/noi/focus_quality_eval_v1.md`
- Reference: `docs/subjects/noi/focus_taxonomy.md`
- Reference: `docs/superpowers/specs/2026-04-03-noi-review-quiz-quality-loop-design.md`
- Reference: `docs/harness/review_quiz_quality_gate.md`

- [ ] **Step 1: 起草专项文档骨架**

```markdown
# 高风险 Focus 质量评测 v1

## 本文件的写入标准

只写 4 个高风险 focus 的专项评测内容：

- 样例模板
- 样例优先级
- rubric
- 典型坏例

不要写：

- 跨 focus 通用质量门
- prompt 调参过程
- 与当前 focus 无关的教学讨论
```

- [ ] **Step 2: 写 4 个 focus 的覆盖范围与样例优先级**

```markdown
## 一、覆盖范围

- `general_modeling`
- `constraint_modeling`
- `greedy_basis`
- `method_selection`

## 二、每个 focus 的固定样例组

1. `易滑坡坏例`
2. `应 fallback`
3. `应放行`

说明：
- 第一版先从 `易滑坡坏例` 开始写
- 因为它最容易被现有 prompt 漏掉
```

- [ ] **Step 3: 写样例字段模板，补上“实际输出记录”**

```markdown
## 三、样例记录模板

- 原题简述
- 学生卡点
- 期望 `review` 方向
- 期望 `quiz` 行为
- 是否应 fallback
- 判坏理由
- 实际 `review` 输出（跑完后填）
- 实际 `quiz` 输出（跑完后填）
```

- [ ] **Step 4: 写 rubric 和通过标准，避免“明显坏题”这种模糊词**

```markdown
## 四、统一评分 Rubric

1. 桥梁是否对
2. 是否是结构事实
3. 是否贴原题语境
4. 反馈是否具体指出结构差错
5. fallback 是否克制

## 五、通过标准

### `应放行` 样例

- review 必须满足质量门里的 5 条放行条件
- quiz 必须满足质量门里的 6 条放行条件

### `应 fallback` 样例

- 必须命中至少 1 条 fallback 必触条件
- 不得错误放行为结构 quiz

### `易滑坡坏例`

- 只要出现口号题、泛方法题、桥梁错位、confirm 换核心结构事实，直接判坏
```

- [ ] **Step 5: 检查专项文档与 harness 不串味**

Run: `sed -n '1,320p' docs/subjects/noi/focus_quality_eval_v1.md`

Expected:
- 能看到 4 个 focus
- 能看到“实际输出”字段
- 能看到 `应放行 / 应 fallback / 易滑坡坏例`
- 文档没有重写跨 focus 质量门全文

- [ ] **Step 6: 提交本任务**

```bash
git add docs/subjects/noi/focus_quality_eval_v1.md
git commit -m "docs: add NOI focus quality eval v1"
```

---

### Task 3: 同步 Harness 状态文件

**Files:**
- Modify: `docs/harness/active_work_item.md`
- Modify: `docs/harness/current_system_state.md`
- Reference: `docs/harness/project_invariants.md`

- [ ] **Step 1: 更新 active_work_item**

```markdown
## 当前目标

将第一版 `review + quiz` 质量闭环文档正式落地：

1. 新增 harness 级质量门文档
2. 新增 NOI 专项评测样例文档
3. 为后续 prompt / guard 调整提供固定复测入口

## 下一步建议

1. 基于这两份文档进入 prompt / guard 实施计划
2. 优先处理 `review -> key_bridge / next_step` 稳定性
```

- [ ] **Step 2: 更新 current_system_state**

```markdown
## 十一、质量闭环文档当前状态

当前已新增两份质量闭环文档：

- `docs/harness/review_quiz_quality_gate.md`
- `docs/subjects/noi/focus_quality_eval_v1.md`

它们当前提供：

- review / quiz / fallback 的最小质量门
- 4 个高风险 focus 的第一版评测模板
- 全量复测 / 局部复测的文档化入口
```

- [ ] **Step 3: 校验没有误改长期规则**

Run: `sed -n '1,260p' docs/harness/project_invariants.md`

Expected:
- 不需要修改
- 没有把当前实现状态误写进长期规则

- [ ] **Step 4: 提交本任务**

```bash
git add docs/harness/active_work_item.md docs/harness/current_system_state.md
git commit -m "docs: sync harness state for quality loop docs"
```

---

### Task 4: 全量自检

**Files:**
- Test: `docs/harness/review_quiz_quality_gate.md`
- Test: `docs/subjects/noi/focus_quality_eval_v1.md`
- Test: `docs/harness/active_work_item.md`
- Test: `docs/harness/current_system_state.md`

- [ ] **Step 1: 搜占位词**

Run: `rg -n 'TBD|TODO|待补|占位' docs/harness/review_quiz_quality_gate.md docs/subjects/noi/focus_quality_eval_v1.md docs/harness/active_work_item.md docs/harness/current_system_state.md`

Expected: 无输出

- [ ] **Step 2: 检查分层边界**

Run: `rg -n '样例|原题简述|实际 `review` 输出|实际 `quiz` 输出' docs/harness/review_quiz_quality_gate.md docs/subjects/noi/focus_quality_eval_v1.md`

Expected:
- harness 文档不出现具体样例模板
- subjects 文档出现样例模板和“实际输出”字段

- [ ] **Step 3: 检查关键名词一致性**

Run: `rg -n 'key_bridge|fallback_explain|review|quiz|confirm' docs/harness/review_quiz_quality_gate.md docs/subjects/noi/focus_quality_eval_v1.md docs/superpowers/specs/2026-04-03-noi-review-quiz-quality-loop-design.md`

Expected:
- 关键名词拼写一致
- `confirm` 的判断标准都指向“核心结构事实是否变化”

- [ ] **Step 4: 生成交付摘要**

```markdown
- 已新增 harness 级质量门文档
- 已新增 NOI 专项评测文档
- 已同步当前工作项和当前系统状态
- 后续可以进入 prompt / guard 的实现计划
```

- [ ] **Step 5: 提交最终收尾**

```bash
git add docs/harness/review_quiz_quality_gate.md docs/subjects/noi/focus_quality_eval_v1.md docs/harness/active_work_item.md docs/harness/current_system_state.md
git commit -m "docs: finalize NOI review quiz quality loop docs"
```

---

## Self-Review Checklist

- [ ] 计划覆盖了 spec 中的两份目标文档
- [ ] 已把 Claude 审核通过的两条优化写进任务
- [ ] 没有出现 `TBD` / `TODO` / “以后再补”
- [ ] 每个任务都有明确文件、命令、预期结果
- [ ] 没有把实现层 prompt 调整混进本轮文档任务
