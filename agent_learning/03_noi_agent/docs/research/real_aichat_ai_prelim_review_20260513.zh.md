# 真实 AIChat student-only 候选 AI 预标注 20260513

本文记录对真实线上 AIChat `student-only` v3 候选表的 AI 预标注结果。该结果仅用于 dev 筛查和教练复核准备，不是 coach gold label，也不是 adjudicated reference。

## 输入与输出

输入工作簿：

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_candidate_review_33_20260512_v3.zh.xlsx
```

AI 预标注输出：

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_candidate_review_33_20260513_ai_prelim_filled.zh.xlsx
```

严格筛选后可导出的 student-only JSONL：

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_ai_prelim_exportable_20260513.jsonl
```

严格筛选报告：

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_ai_prelim_strict_screen_20260513.json
```

这些文件包含真实学生提问和审计上下文，不提交到公开仓库。

## 审查原则

AI 预标注遵循以下规则：

- 只作为 preliminary review / dev screening；
- 旧线上 AI 回复只用于审计污染和旧系统观察，不作为 gold；
- 所有新 tutor condition 的生成输入只包含真实学生当前提问和必要题目元信息；
- 删除旧 AI 后不可理解的样本不得进入主评测；
- 近重复、污染、缺上下文、隐私不确定、需要重点复判的样本不得进入主评测；
- `missing_bridge` 必须描述学生缺少的可迁移推理关系；
- `forbidden_content` 必须描述不能直接说穿的关键桥；
- `success_criteria` 必须描述好回复应引导学生完成的下一步动作。

## 结果概览

候选总数：33。

| 状态 | 数量 |
|---|---:|
| 保留主评测 | 8 |
| 转 dev/regression | 12 |
| 排除 | 13 |

严格导出结果：

| 项目 | 数量 |
|---|---:|
| accepted_rows | 8 |
| exportable_rows | 8 |
| rejected_rows | 0 |

8 条可导出样本的类别分布：

| 类别 | 数量 |
|---|---:|
| binary_search_check | 2 |
| graph_tree_modeling | 6 |

主评测候选 case id：

```text
real_aichat_1
real_aichat_27
real_aichat_987
real_aichat_1293
real_aichat_247
real_aichat_249
real_aichat_827
real_aichat_257
```

需要人工重点复判的 case id：

```text
real_aichat_163
real_aichat_219
real_aichat_981
real_aichat_259
real_aichat_1203
real_aichat_3
real_aichat_65
```

## 严格门禁

当前导出器要求主评测样本满足：

- `审查状态=保留主评测`；
- `隐私风险=none`；
- `删除旧AI后是否可理解=yes`；
- `是否自包含=yes`；
- `是否需要补充题面/代码上下文=no`；
- `是否近重复样本=no`；
- `是否代表真实卡点=yes`；
- `是否适合主评测=yes`；
- `需重点复判=no`；
- `旧AI上下文污染初筛` 只能是 `none` 或 `low`；
- `missing_bridge`、`forbidden_content`、`success_criteria` 均非空。

格式抽检显示，8 条导出样本均满足：

- `generation_input.recent_dialogue=""`；
- `generation_input.context_ai_reply=""`；
- `generation_input.student_code_excerpt=""`；
- 旧 AI 上下文只保留在 `audit_context`；
- `observed_current_system_response` 只作为旧系统观察，不作为 gold。

## 解释边界

这 8 条真实日志样本只能作为 `real-log pilot subset` 或 dev 真实提问子集，不能作为完整 held-out 主结果。原因：

- 类别分布明显偏斜，只覆盖二分和图/树；
- debug、implementation、DP、数据结构、贪心等真实日志样本多数因不可自包含、近重复或旧 AI 污染被转 dev 或排除；
- 当前标签来自 AI 预标注，必须经人类教练复核后才能作为 reference label；
- 即使通过严格门禁，仍需上线前人工脱敏抽查。

论文中建议写法：

> We additionally screened real online AIChat student questions as a small student-only pilot subset. Historical AI replies were removed from generation inputs and retained only for audit. Because the preliminary labels were AI-assisted and the resulting subset was category-skewed, these cases are used for development and realism checks rather than headline held-out claims.

中文：

> 我们额外筛选真实线上 AIChat 学生提问，形成一个 student-only pilot 子集。历史 AI 回复从生成输入中移除，只用于审计。由于当前标签为 AI 辅助预标注，且可导出样本类别偏斜，这些样本只用于开发阶段真实感检查，不作为 headline held-out 结论。

## 下一步

1. 人类教练复核 8 条主评测候选；
2. 对 7 条重点复判样本决定是否补上下文后转 dev；
3. 不把这 8 条扩写为论文主结果，只作为真实提问 pilot；
4. 若要形成真实日志 held-out，需要继续从线上日志补充 DP、数据结构、实现/debug、贪心等类别，并重复相同的 student-only 严格门禁。
