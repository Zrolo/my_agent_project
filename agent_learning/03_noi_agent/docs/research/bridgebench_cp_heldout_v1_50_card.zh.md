# BridgeBench CP Held-out v1 50 Draft Dataset Card

日期：2026-05-12

文件：`docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl`

Coach A 教练审查表：`docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx`

Coach B 复标表：`docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx`

本数据集是 Research v1 的 **50-case held-out 草稿**，用于进入正式主实验前的教练审查、修改和双标。它不是 adjudicated gold，也不是最终论文 headline 结果。

## 状态

| 项 | 状态 |
|---|---|
| 样本数 | 50 |
| 数据状态 | `draft_needs_coach_review` |
| 是否可直接作为 gold | 否 |
| 是否来自 20-case dev/regression | 否，case_id 已使用 `heldout_cp_###` |
| 是否需要 Coach A 审查 | 是 |
| 是否需要 Coach B 复标 | 是，至少 20 条 |
| 已导出 Coach A 审查 workbook | 是，`coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx` |
| 已导出 Coach B 复标 workbook | 是，`coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx` |

## 为什么这张表没有 AI 回复

本数据集卡对应的是 **case/reference annotation**，不是 response blind review。教练这一阶段审查的是：

- 学生当前问题是否真实；
- 题目/上下文是否足够；
- 近期对话是否会改变学生已知信息；
- 当前 missing bridge、forbidden content 和 success criteria 是否合理。

因此，50-case reference 标注表 **不需要 AI 回复**。AI 回复会在后续步骤中由冻结后的系统条件统一生成，然后导出另一份 response blind review workbook；那份表才会包含“上下文 AI 回复”和“AI 回复（要评分）”。

## Recent Dialogue 分布

| recent_dialogue 类型 | Count | 说明 |
|---|---:|---|
| `none` | 10 | `recent_dialogue = N/A`，模拟真正单轮输入 |
| `short` | 25 | 1-2 轮短上下文，模拟学生已经给出一点状态或卡点 |
| `long` | 15 | 2-4 轮中/长上下文，模拟学生已被追问、已有部分已知信息 |

这个分布是刻意设计的：Research v1 不能只评估单轮问答，还必须评估 AIChat 在近期对话中判断“学生已经说了什么 / 还没说什么”的能力。`recent_dialogue` 会影响 critical bridge leakage：同一句 AI 回复，在学生已经说出关键桥时可能是合理确认；在学生还没说出关键桥时可能是泄露。

## 学生代码片段分布

| student_code_excerpt 类型 | Count | 说明 |
|---|---:|---|
| `none` | 38 | `student_code_excerpt = N/A`，学生没有贴代码，只描述卡点 |
| `present` | 12 | 学生贴了局部代码、错误片段或待补条件 |

这 12 条代码样本用于覆盖真实 AIChat 中常见的调试、边界、局部条件补全和代码理解场景。它们不要求 AI 直接改完整代码；教练仍然要判断当前回复是否只围绕证据、是否避免直接补完关键桥。

## 字段

每条样本包含：

- `case_id`
- `category`
- `problem_ref`
- `student_message`
- `problem_context`
- `recent_dialogue`
- `student_code_excerpt`
- `student_known_state`
- `missing_bridge`
- `allowed_help_level`
- `forbidden_content`
- `success_criteria`
- `review_notes_for_coach`
- `reference_label_status`

## 类别分布

| Category | Count |
|---|---:|
| `dp_state` | 5 |
| `dp_transition` | 5 |
| `binary_search_predicate` | 5 |
| `binary_search_boundary` | 4 |
| `graph_tree_modeling` | 5 |
| `greedy_correctness` | 5 |
| `data_structure_semantics` | 5 |
| `implementation_boundary` | 5 |
| `debugging_evidence` | 4 |
| `policy_request` | 7 |

## 使用规则

1. 这 50 条不能再用于 prompt tuning 后直接报告同一批 held-out headline。
2. 教练可以先修改草稿文本和 `success_criteria`，修改完成后再冻结为 held-out。
3. 若修改后发现某条样本不适合判断质量或泄露，应替换，不要强行保留。
4. 进入主实验前，每条样本都应能回答两个问题：
   - 什么样的回复算好？
   - 什么样的回复算过早补完当前 missing bridge？

## 下一步

1. Coach A 审查全部 50 条。
2. Coach B 独立复标至少 20 条；当前 overlap 子集中包含 8 条代码样本，用于估计带代码场景下的标注一致性。
3. 计算 agreement 并裁决分歧。
4. 冻结为正式 `bridgebench_cp_heldout_v1_50.jsonl`。
5. 使用冻结 prompt / judge / rubric 跑主实验。
