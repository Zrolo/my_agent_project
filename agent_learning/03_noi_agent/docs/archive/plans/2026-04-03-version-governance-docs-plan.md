# Version Governance Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `docs/common/` 落地版本治理文档体系，让项目从 `V1.01` 开始进入统一版本规划、更新记录与版本规则管理。

**Architecture:** 这轮只创建和同步 3 份项目级文档：`version_policy.md`、`version_plan.md`、`changelog.md`。不改业务代码，不改 harness 规则，只把已经通过 spec 的版本治理方案落成可维护文档，并补入首版内容。

**Tech Stack:** Markdown, git, `sed`, `rg`

---

## File Structure

- Create: `docs/common/version_policy.md`
  - 写版本治理规则，只负责规则定义
- Create: `docs/common/version_plan.md`
  - 写当前所处版本与未来路线图，只负责规划
- Create: `docs/common/changelog.md`
  - 写已发生更新记录，只负责历史更新
- Reference: `docs/superpowers/specs/2026-04-03-version-governance-design.md`
  - 作为本轮唯一设计依据，不直接修改
- Reference: `docs/README.md`
  - 确认版本治理文档落在 `docs/common/` 的合理性，不直接修改

---

### Task 1: 创建 `version_policy.md`

**Files:**
- Create: `docs/common/version_policy.md`
- Reference: `docs/superpowers/specs/2026-04-03-version-governance-design.md`

- [ ] **Step 1: 先读取 spec 中的规则段**

Run: `sed -n '1,220p' docs/superpowers/specs/2026-04-03-version-governance-design.md`

Expected:
- 能看到版本编号规则
- 能看到大版本 / 小版本升级条件
- 能看到版本状态定义

- [ ] **Step 2: 用 apply_patch 创建 `version_policy.md`**

```md
# 版本治理规则

## 1. 版本治理目的

- 统一项目版本命名
- 让版本号优先表达产品阶段，而不是零散代码批次
- 让后续更新有固定记录方式

## 2. 编号规则

- 大版本：`V1`、`V2`、`V3`
- 小版本：`V1.01`、`V1.02`、`V1.03`

## 3. 大版本升级条件

只有当学生使用体验或教学闭环进入新阶段时，才升大版本。

## 4. 小版本升级条件

同一阶段内的成体系增强、质量收紧、体验改良、工程维护，升小版本。

## 5. 版本状态

- `planned`
- `in_progress`
- `released`
- `archived`

## 6. 记录规则

- `version_policy.md` 只写规则
- `version_plan.md` 只写规划
- `changelog.md` 只写已发生变化
- 不单独建立 `update.md`
```

- [ ] **Step 3: 检查文档是否只包含规则**

Run: `sed -n '1,220p' docs/common/version_policy.md`

Expected:
- 不出现具体某一轮更新流水账
- 不出现 task plan 风格内容

- [ ] **Step 4: 提交本任务**

```bash
git add docs/common/version_policy.md
git commit -m "docs: add version policy"
```

---

### Task 2: 创建 `version_plan.md`

**Files:**
- Create: `docs/common/version_plan.md`
- Reference: `docs/superpowers/specs/2026-04-03-version-governance-design.md`

- [ ] **Step 1: 先读取 spec 中的起始版本与路线建议**

Run: `sed -n '80,220p' docs/superpowers/specs/2026-04-03-version-governance-design.md`

Expected:
- 能看到当前项目起始版本
- 能看到 `V1.01` 到 `V2` 的路线建议

- [ ] **Step 2: 用 apply_patch 创建 `version_plan.md`**

```md
# 版本路线图

## 当前所处版本

- 当前主版本：`V1`
- 当前起始小版本：`V1.01`
- 当前状态：`in_progress`

## V1 总目标

跑通第一阶段 NOI 教练闭环，让学生端工作台、AI 复盘、quiz 与质量收紧机制形成稳定基础。

## V1.xx 路线

### `V1.01`

- 版本治理建立
- harness 体系已落地
- 学生端工作台主结构成立
- review / quiz 质量门已建立

### `V1.02`

- AI 复盘质量收紧
- `key_bridge / next_step` 更稳定
- 高风险 focus 的 review 漂移显著减少

### `V1.03`

- quiz / fallback / confirm 进一步收紧
- 坏题率下降
- 结构事实题与 fallback 边界更稳定

### `V1.04`

- 题库推荐、problem analysis、教师端运营能力增强

## V2 展望

- 学生端形成更稳定的个性化训练闭环
- 版本治理、评测、迭代方式进入更成熟阶段

## 当前明确非目标

- 自动版本号生成
- 发布脚本与 CI/CD
- 历史旧文档大规模重命名
```

- [ ] **Step 3: 检查文档是否只写规划**

Run: `sed -n '1,240p' docs/common/version_plan.md`

Expected:
- 没有写成 changelog
- 没有写成 task 级执行清单

- [ ] **Step 4: 提交本任务**

```bash
git add docs/common/version_plan.md
git commit -m "docs: add version plan"
```

---

### Task 3: 创建 `changelog.md`

**Files:**
- Create: `docs/common/changelog.md`
- Reference: `docs/superpowers/specs/2026-04-03-version-governance-design.md`
- Reference: `docs/harness/current_system_state.md`
- Reference: `docs/harness/active_work_item.md`

- [ ] **Step 1: 先读取 spec 与当前 harness，确认首条 changelog 写什么**

Run: `sed -n '1,220p' docs/superpowers/specs/2026-04-03-version-governance-design.md`

Run: `sed -n '1,220p' docs/harness/current_system_state.md`

Expected:
- 能确认首条 changelog 应从 `V1.01` 开始
- 能确认首条记录只写已经成立的变化

- [ ] **Step 2: 用 apply_patch 创建 `changelog.md`**

```md
# 更新记录

## `V1.01` · 2026-04-03

### 产品变化

- 项目正式进入统一版本治理
- 学生端工作台、AI 复盘、quiz 基础闭环已成立
- review / quiz 质量门文档已建立

### 工程摘要

- 建立 harness 体系与当前工作项同步方式
- 建立 review / quiz 质量门与高风险 focus 评测文档
- 开始第一轮 review bridge stability 收紧

### 影响模块

- `docs/harness/`
- `docs/subjects/noi/`
- `review_engine.py`
- `test_review_regression.py`

### 是否需要回归测试

- 是
```

- [ ] **Step 3: 检查 changelog 是否只写已发生内容**

Run: `sed -n '1,220p' docs/common/changelog.md`

Expected:
- 不出现未来计划
- 不出现规则定义

- [ ] **Step 4: 提交本任务**

```bash
git add docs/common/changelog.md
git commit -m "docs: add changelog"
```

---

### Task 4: 最终一致性检查

**Files:**
- Test: `docs/common/version_policy.md`
- Test: `docs/common/version_plan.md`
- Test: `docs/common/changelog.md`
- Reference: `docs/superpowers/specs/2026-04-03-version-governance-design.md`

- [ ] **Step 1: 并排检查三份文档职责是否串味**

Run: `sed -n '1,220p' docs/common/version_policy.md`

Run: `sed -n '1,240p' docs/common/version_plan.md`

Run: `sed -n '1,220p' docs/common/changelog.md`

Expected:
- `version_policy.md` 只写规则
- `version_plan.md` 只写未来路线
- `changelog.md` 只写已发生更新

- [ ] **Step 2: 检查命名与版本编号是否一致**

Run: `rg -n "V1|V1\\.01|V1\\.02|V1\\.03|V2|planned|in_progress|released|archived" docs/common/version_policy.md docs/common/version_plan.md docs/common/changelog.md`

Expected:
- 版本号写法一致
- 状态名写法一致

- [ ] **Step 3: 检查没有误建 `update.md`**

Run: `find docs/common -maxdepth 1 -type f | sort`

Expected:
- 只新增 `version_policy.md`
- 只新增 `version_plan.md`
- 只新增 `changelog.md`

- [ ] **Step 4: 提交本任务**

```bash
git add docs/common/version_policy.md docs/common/version_plan.md docs/common/changelog.md
git commit -m "docs: finalize version governance docs"
```

