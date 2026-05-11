# DBox Official Materials Review v1

本文记录对官方材料包 `pn2271.zip` 的离线检查结果。目的不是复现 DBox，而是让 Research v1 的 DBox-inspired baseline 有更可靠的材料依据。

## 材料包内容

官方包包含：

- `Prompts.pdf`
- `ReadMe.txt`
- 后端源码：`Source Code/Back End/server.py`
- 前端源码：`Source Code/Front End/UserStudy.html`、`UserStudy_logical.js`、`DBox_try.html` 等

`ReadMe.txt` 说明该系统由 Flask 后端和前端页面通过 HTTP 通信；运行时需要启动 `server.py`，再打开前端 HTML。

## 官方材料确认的 DBox 机制

`Prompts.pdf` 和 `server.py` 显示，DBox 后端主要围绕四类交互：

| 功能 | 输入 | 输出/作用 |
|---|---|---|
| From Editor to Step Tree | problem + learner code | 从学生代码生成 step tree，并标记节点状态 |
| Check Step Tree | problem + learner step tree | 检查学生构建的 step tree，补充 missing node 并生成 hints |
| Copy to Comments | problem + learner code + learner steps | 将 step tree 节点映射到代码行 |
| Check Match | problem + learner code + learner steps | 判断 step 是否已实现、错误实现或待实现 |

这说明 DBox 的核心是交互式 step tree 与代码/步骤对齐，不是单轮 tutor response prompt。

## 节点与提示字段

官方 prompt 中的节点状态包括：

- `correct`
- `incorrect`
- `missing`
- `can / cannot be further divided`

官方 prompt 还会生成多类字段：

- `general_hint`
- `detailed_hint`
- `correctStep`
- `code`
- `correct_code`
- `psuedo_code` / pseudocode

其中 `general_hint` 更接近我们单轮 baseline 可以安全使用的 first-level hint；`detailed_hint`、`correctStep`、`correct_code` 和 pseudocode 在我们的 benchmark 中容易变成 critical bridge leakage，因此必须禁用或只作为不可学生可见的研究背景。

## 对我们实现的影响

我们保留：

- step-tree-style decomposition；
- 当前子步骤定位；
- correct / incorrect / missing / divisible 的思想；
- question-form `general_hint`；
- 对 missing / incorrect 当前节点的鼓励式引导。

我们不保留：

- 完整交互式 step tree UI；
- 多轮 co-decomposition；
- repeated failed attempts；
- reveal substep；
- reveal code；
- detailed hint；
- correctStep；
- correct_code；
- pseudocode；
- code-line mapping；
- 真实学生 learning gain / engagement / critical thinking 实验。

## Runner 实现映射

Research v1 的 offline runner 使用：

```text
tutor_mode=dbox_inspired_decomposition_tutor
```

输出结构：

```json
{
  "baseline_group": "literature_inspired_decomposition",
  "decomposition_view": [
    {"step_id": "s1", "step_name": "...", "status": "known_or_not_relevant"},
    {"step_id": "s2", "step_name": "...", "status": "current_stuck_step"},
    {"step_id": "s3", "step_name": "...", "status": "defer"}
  ],
  "current_substep": "...",
  "hint_level": "general_question",
  "student_visible_response": "..."
}
```

这里的 `status` 是对 DBox 原状态的单轮评测压缩：

| DBox 原机制 | Research v1 压缩映射 |
|---|---|
| correct / 已有有效部分 | `known_or_not_relevant` |
| incorrect / missing / can be divided 的当前卡点 | `current_stuck_step` |
| 后续未处理步骤 | `defer` |

## 论文写法

可以写：

```text
We consulted the official DBox supplementary materials and implemented a single-turn DBox-inspired decomposition baseline.
```

不应写：

```text
We reproduce DBox.
```

更稳的中文表述：

```text
我们参考 DBox 官方材料中的 step tree、节点状态和 general hint 设计了单轮 DBox-inspired baseline；但没有复现其交互式 UI、多轮 co-decomposition、progressive reveal、代码-步骤对齐或真实学生实验。
```

## Source Anchors

- Local official package: `/Users/kongyouli/Downloads/pn2271.zip`
- Extracted read-only review copy: `/tmp/dbox_pn2271/SupplementaryMaterials`
- DBox paper anchor: [ar5iv](https://ar5iv.org/html/2502.19133v1)
- DBox ACM anchor: [ACM DL](https://dl.acm.org/doi/abs/10.1145/3706598.3713748)
