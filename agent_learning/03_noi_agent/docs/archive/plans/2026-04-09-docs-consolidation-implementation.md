# Docs Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the current docs set into a smaller active surface, merge overlapping guidance, and archive historical specs/plans without losing project history.

**Architecture:** Keep a small active documentation surface in `docs/common/` and `docs/harness/`, move historical design/process material under `docs/archive/`, and refresh `docs/README.md` so new readers know the exact order to read. Do not rewrite the entire knowledge base; preserve history and only merge obviously overlapping topics.

**Tech Stack:** Markdown docs, repository file moves, repo-local navigation updates

---

### Task 1: Create archive structure and move historical design/process docs

**Files:**
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/`
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/specs/`
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/plans/`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/specs/*.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/plans/*.md`

- [ ] **Step 1: Create archive directories**

Run:

```bash
mkdir -p /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common
mkdir -p /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/specs
mkdir -p /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/plans
```

Expected:

```text
No output; directories now exist.
```

- [ ] **Step 2: Move historical superpowers specs into archive**

Run:

```bash
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/specs/*.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/specs/
```

Expected:

```text
No output; docs/superpowers/specs becomes empty or contains only non-md support files.
```

- [ ] **Step 3: Move historical superpowers plans into archive**

Run:

```bash
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/superpowers/plans/*.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/plans/
```

Expected:

```text
No output; docs/superpowers/plans becomes empty or contains only non-md support files.
```


### Task 2: Archive overlapping common docs and create the merged version governance doc

**Files:**
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/version_governance.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/version_plan.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/version_policy.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/teaching_principles.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/ai_edu_design_principles_2026_04.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_backend_checklist.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_backend_tasks.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_frontend_checklist.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_frontend_tasks.md`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_teaching_tasks.md`

- [ ] **Step 1: Write merged version governance doc**

Create `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/version_governance.md` with:

```md
# 版本治理

这份文档统一当前系统的版本规则、阶段路线和更新方式。

## 1. 当前主版本

- 主版本：`V1`
- 当前状态：`in_progress`

## 2. 版本目标

`V1` 的目标是把 NOI 复盘系统收成稳定的学生学习闭环：

- 结构化复盘
- 三轮理解检查
- 补救与知识兜底
- teacher review 与基础评测

## 3. 编号规则

- 大版本：`V1`、`V2`、`V3`
- 小版本：`V1.01`、`V1.02`、`V1.03`

## 4. 升级规则

### 大版本

只有当学生体验或教学闭环进入新阶段时，才升大版本。

### 小版本

在同一阶段内，凡是成体系的质量收紧、体验增强、评测增强、工程整理，都升小版本。

## 5. 版本状态

- `planned`
- `in_progress`
- `released`
- `archived`

## 6. 当前路线

### `V1.01`

- 版本治理建立
- harness 体系建立
- 学生端工作台成立

### `V1.02`

- AI 复盘质量收紧
- `guided_walkthrough / try_now` 更稳定

### `V1.03`

- 理解检查梯子更清楚
- follow-up / confirm / remedy 边界更稳定

### `V1.04`

- 题库推荐、teacher 运营能力、problem analysis 继续增强

## 7. 更新规则

- `changelog.md` 记录已发生变化
- `decision_log.md` 记录关键取舍
- 本文档只保留当前版本治理规则与路线，不写详细实施历史
```

- [ ] **Step 2: Move overlapping common docs into archive/common**

Run:

```bash
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/teaching_principles.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/ai_edu_design_principles_2026_04.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/version_plan.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/version_policy.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_backend_checklist.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_backend_tasks.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_frontend_checklist.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_frontend_tasks.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
mv /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_teaching_tasks.md \
   /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/common/
```

Expected:

```text
No output; files now live under docs/archive/common/.
```


### Task 3: Refresh docs entry points and archive index

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/README.md`
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/README.md`

- [ ] **Step 1: Rewrite top-level docs README as a navigation-first entry**

Replace `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/README.md` with:

```md
# Docs 导航

这套 `docs/` 分成三层：

- 当前主文档：现在还有效、接手必须先读
- 学科专用文档：NOI 专用桥、案例、数据
- 历史归档：设计与实施历史，不作为当前主入口

## 新接手先看

1. `harness/current_system_state.md`
2. `common/review_scaffolding_framework_2026_04.md`
3. `common/quiz_design_patterns.md`
4. `common/oi_topic_taxonomy_2026_04.md`
5. `common/decision_log.md`

## 当前主文档

### `common/`

- `review_scaffolding_framework_2026_04.md`
- `quiz_design_patterns.md`
- `oi_topic_taxonomy_2026_04.md`
- `decision_log.md`
- `changelog.md`
- `version_governance.md`
- `review_observability_spec.md`

### `harness/`

- `current_system_state.md`
- 其他运行契约与工程接手文档

## NOI 专用文档

在 `subjects/noi/`：

- `bridge_map.md`
- `focus_taxonomy.md`
- `good_bad_examples.md`
- 相关 JSON 数据文件

## 历史归档

在 `archive/`：

- `archive/specs/`
- `archive/plans/`
- `archive/common/`

如果要回看设计演进、论文材料或历史实施细节，再进入这里。
```

- [ ] **Step 2: Add archive README**

Create `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/README.md` with:

```md
# Archive

这里存放历史设计、实施计划和已被后续主文档吸收的旧资料。

## 目录

- `common/`：已被主文档吸收或替代的旧通用文档
- `specs/`：历史设计文档
- `plans/`：历史 implementation plan

## 使用原则

- 这里不是当前主入口
- 新接手优先回到 `../README.md`
- 只有在需要回看演进过程、历史决策或论文材料时再进入这里
```


### Task 4: Verify final docs layout

**Files:**
- Verify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/`

- [ ] **Step 1: Check final active docs list**

Run:

```bash
find /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common -maxdepth 1 -type f | sort
find /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive -maxdepth 2 -type f | sort
```

Expected:

```text
common/ only contains the reduced active set plus still-relevant supporting docs.
archive/ contains specs, plans, and absorbed common docs.
```

- [ ] **Step 2: Read the rewritten entry docs to verify navigation clarity**

Run:

```bash
sed -n '1,220p' /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/README.md
sed -n '1,220p' /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/archive/README.md
```

Expected:

```text
README clearly tells a new reader what to read first and where history lives.
```
