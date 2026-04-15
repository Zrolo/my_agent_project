# Docs Consolidation Design

## Goal

把当前 `docs/` 从“不断追加的过程记录”收成“新 AI 和团队成员都能快速接手的文档体系”，同时保留历史演进材料，不做激进删除。

## Why Now

当前 `docs/` 已经出现了三个明显问题：

1. 主入口不够清楚，第一次接手时不知道先读哪几份。
2. `common/` 中存在同主题重复，例如教学原则、设计原则、支架框架、observability、版本治理。
3. `superpowers/specs/` 和 `superpowers/plans/` 已经积累了较多历史设计与实施文档，但没有清晰标出哪些仍有效、哪些只作历史参考。

这会直接影响：

- 新对话或新 AI 的接手效率
- 当前系统状态的理解一致性
- 后续继续扩功能时是否会丢线

## Design Principles

### 1. 先保留主文档，再归档历史文档

这次整理不做激进删除，优先建立清晰的“当前有效入口”，再把历史设计迁移到 archive。

### 2. 只保留少量主入口

当前仍应作为系统主入口的文档数量要尽量少。主入口只回答：

- 系统现在是什么
- 当前设计语言是什么
- quiz 如何设计
- 知识桥如何分类
- 后续有哪些关键决策

### 3. 历史文档不再与当前主文档混放

历史 spec、implementation plan、已被吸收的旧 `common/` 文档不删除，但统一转入 `docs/archive/`，避免和当前有效文档竞争入口。

### 4. 先瘦身，不重写全部内容

这次整理不重写所有文档，而是：

- 调整目录
- 合并重复主题
- 新增清晰导航
- 给历史文档明确定位

## Target Information Architecture

整理后的文档体系收成 5 层：

### A. 顶层入口

- `docs/README.md`

职责：

- 说明整个 `docs/` 的目的
- 给出“新接手先看什么”的顺序
- 链接到当前主文档
- 链接到 archive

### B. 当前系统主文档

放在 `docs/common/` 与 `docs/harness/`。

建议保留为当前主文档的只有：

- `docs/harness/current_system_state.md`
- `docs/common/review_scaffolding_framework_2026_04.md`
- `docs/common/quiz_design_patterns.md`
- `docs/common/oi_topic_taxonomy_2026_04.md`
- `docs/common/decision_log.md`
- `docs/common/changelog.md`

其中：

- `current_system_state.md` 回答“代码里现在真实成立了什么”
- `review_scaffolding_framework_2026_04.md` 回答“系统设计语言和教学框架是什么”
- `quiz_design_patterns.md` 回答“理解检查设计有哪些正反模式”
- `oi_topic_taxonomy_2026_04.md` 回答“知识桥如何分类”
- `decision_log.md` 回答“为什么做出这些关键决策”
- `changelog.md` 回答“最近发生了什么变化”

### C. 学科专用文档

保留在 `docs/subjects/noi/`：

- `bridge_map.md`
- `focus_taxonomy.md`
- `good_bad_examples.md`
- 相关 JSON 数据文件

职责：

- 只承载 NOI 场景特有桥梁、案例、实验素材
- 不再承担跨学科总入口职责

### D. Harness / 运行契约文档

保留在 `docs/harness/`：

- `active_work_item.md`
- `ai_output_contracts.md`
- `api_insert.md`
- `project_invariants.md`
- `review_quiz_quality_gate.md`
- `student_workspace_contract.md`

职责：

- 服务代码实现和多轮接手
- 不和产品原则文档混放

### E. Archive

新增：

- `docs/archive/common/`
- `docs/archive/specs/`
- `docs/archive/plans/`

职责：

- 保留历史过程材料
- 不作为当前入口
- 供论文/复盘/回看设计演进时使用

## Consolidation Decisions

### 1. 教学 / 设计原则组

当前存在重复：

- `docs/common/teaching_principles.md`
- `docs/common/ai_edu_design_principles_2026_04.md`
- `docs/common/review_scaffolding_framework_2026_04.md`

处理方式：

- 保留 `review_scaffolding_framework_2026_04.md` 作为主文档
- 其中继续承担：
  - `ZPD + Adaptive Scaffolding + EDF`
  - 复盘设计原则
  - 当前系统的教学逻辑
- `teaching_principles.md` 与 `ai_edu_design_principles_2026_04.md` 转入 archive

原因：

- 现在真正最贴系统实现的是 scaffold framework
- 另外两份更像早期原则沉淀或外围阅读结论

### 2. Observability 组

当前存在：

- `review_observability_spec.md`
- `review_observability_backend_checklist.md`
- `review_observability_backend_tasks.md`
- `review_observability_frontend_checklist.md`
- `review_observability_frontend_tasks.md`
- `review_observability_teaching_tasks.md`

处理方式：

- 保留 `review_observability_spec.md` 作为总文档
- 其余 5 份转入 archive

原因：

- 这 5 份更像执行期 checklist / task note
- 不适合作为长期主入口

### 3. 版本治理组

当前存在：

- `version_plan.md`
- `version_policy.md`
- `changelog.md`

处理方式：

- 保留 `changelog.md`
- 合并 `version_plan.md + version_policy.md` 为新文档：
  - `docs/common/version_governance.md`
- 原 `version_plan.md` 和 `version_policy.md` 转入 archive

原因：

- 这两份现在主题强相关，拆开反而增加阅读成本

### 4. superpowers 设计与计划文档

当前：

- `docs/superpowers/specs/` 中有 13 份
- `docs/superpowers/plans/` 中有 14 份

处理方式：

- 整体迁入 `docs/archive/specs/` 和 `docs/archive/plans/`
- 保留文件名不变
- 不重写内容

原因：

- 这些文档大多是历史设计与实施轨迹
- 继续放在顶层活跃路径中，会和当前主文档竞争入口

## New Navigation Design

新的 `docs/README.md` 需要明确给出：

### 新 AI / 新成员接手顺序

1. `docs/harness/current_system_state.md`
2. `docs/common/review_scaffolding_framework_2026_04.md`
3. `docs/common/quiz_design_patterns.md`
4. `docs/common/oi_topic_taxonomy_2026_04.md`
5. `docs/common/decision_log.md`

### 如果要了解历史演进

再进入：

- `docs/archive/specs/`
- `docs/archive/plans/`

### 如果要看 NOI 专用桥和案例

再进入：

- `docs/subjects/noi/`

## Migration Plan

### Phase 1: 建立 archive 目录

- 创建：
  - `docs/archive/common/`
  - `docs/archive/specs/`
  - `docs/archive/plans/`

### Phase 2: 移动历史文档

- 将旧 `superpowers/specs/*.md` 移入 `docs/archive/specs/`
- 将旧 `superpowers/plans/*.md` 移入 `docs/archive/plans/`
- 将已被吸收的 `common/` 文档移入 `docs/archive/common/`

### Phase 3: 新建合并文档

- 新建：
  - `docs/common/version_governance.md`

并把：

- `version_plan.md`
- `version_policy.md`

中的有效内容合并进去。

### Phase 4: 更新导航

- 重写 `docs/README.md`
- 让顶层 README 明确：
  - 当前主入口
  - 学科入口
  - archive 入口

## Non-Goals

这次整理不做：

- 重写所有旧文档内容
- 删除历史 spec / plan
- 变更 `subjects/noi/` 数据文件结构
- 把 `harness/` 内容并回 `common/`
- 为每个文档补统一模板

## Success Criteria

整理完成后，应满足：

1. 新 AI 第一次接手时，只需要看 5 份主文档就能知道系统当前状态。
2. `common/` 中不再存在明显重复的教学/设计/版本治理主题。
3. 历史 spec / plan 不删除，但统一迁入 archive。
4. `docs/README.md` 明确告诉读者：
   - 先看什么
   - 再看什么
   - 历史材料在哪
