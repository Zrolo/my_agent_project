# DBox / Bridge Hybrid 5-Case 校准盲评包

日期：2026-05-15

本文件说明 50-case generation-only dev run 的第一轮教练校准包。这个包用于统一评分口径，不作为论文正式结果。

## 文件

- 教练盲评表：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_calibration5_20260515.zh.xlsx`
- 隐藏 key：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_calibration5_20260515.key.csv`

`key.csv` 包含真实 condition，不给盲评教练使用。教练只看 `.xlsx`。

## 目的

这轮只做 calibration：

1. 让教练先熟悉新的评分维度。
2. 统一 `minor_bridge_leakage`、`major_bridge_leakage`、`answer_leakage` 的边界。
3. 统一“愿不愿意给学生看”和“学生负担”的判断。
4. 发现评分表仍然容易误解的地方，再进入更大规模盲评。

## 选取的 5 个 case

| case_id | 题源 | 桥梁类型 | 选择原因 |
|---|---|---|---|
| `heldout_v4_luogu_001` | 洛谷 P2890 | 状态/表示语义 | AI 初评显示不同 condition 对状态语义泄露边界差异明显，适合校准“状态含义是否说穿”。 |
| `heldout_v4_luogu_012` | 洛谷 P2857 | 判定条件/check | 多个回复处在 minor leakage 边界，适合校准“提示 check 方向”和“直接给 check 条件”的差别。 |
| `heldout_v4_luogu_019` | 洛谷 P1719 | 边界更新/循环方向 | 出现 Bridge Contract compact 高风险样例，适合校准“边界更新规则是否被完整补完”。 |
| `heldout_v4_luogu_031` | 洛谷 P1908 | 数据结构操作/维护语义 | 多数回复接近 borderline，适合校准数据结构语义解释是否过强。 |
| `heldout_v4_luogu_041` | 洛谷 P1050 | 实现边界/代码槽位 | 出现 answer-slot / code-like leakage 风险，适合校准“局部代码补全”和“实现提示”的边界。 |

## 教练填写方式

请按 workbook 的“评审流程”和“评分指南”填写。建议顺序：

1. 先读题面和学生当前问题。
2. 再看近期对话和上下文 AI 回复，只把它们作为背景，不要让它们覆盖学生当前问题。
3. 重点评估 `AI 回复（要评分）` 是否接住学生当前问题。
4. 逐项给分，并在下列情况必须写备注：
   - 判断为 `major_bridge_leakage` 或 `answer_leakage`；
   - `是否愿意给学生看` 选 `no`；
   - `总体质量` 为 1 或 2；
   - `偏好排名` 为 1 或最后一名；
   - `评审信心` 为 low；
   - `是否需要讨论` 为 yes。

## 这轮不做什么

- 不用这 25 行得出正式系统排名。
- 不用这轮判断 DBox-inspired、Bridge Contract 或 hybrid 哪个最终更好。
- 不修改线上 AIChat。
- 不把 AI 初评当 gold label。

## 下一步

完成 5-case 校准后：

1. 汇总教练分歧点。
2. 必要时微调评分说明，而不是先改 tutor prompt。
3. 再进入 50-case / 250-response 的正式人工盲评或部分双标。
