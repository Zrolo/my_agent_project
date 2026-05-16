# 50-case Held-out Formal Preflight Report

日期：2026-05-13

本报告记录 `bridgebench_cp_heldout_v1_50_draft.jsonl` 在正式 50-case held-out 主实验前的 preflight 检查结果。它不是实验结果，也不是教练标注结果；它只判断当前数据集是否可以进入正式 headline run。

## 结论

当前结论：**No-go for formal held-out run；Go for coach review / freeze preparation**。

原因很简单：

- 数据结构检查通过：50 条、字段齐全、类别分布、近期对话分布、代码片段数量和 dev seed overlap 均满足当前草稿要求；
- 但正式 frozen-status 门禁未通过：50 条 case 的 `reference_label_status` 仍为 `draft_needs_coach_review`；
- 因此当前文件只能作为教练审查草稿，不能直接作为 `bridgebench_cp_heldout_v1_50_frozen.jsonl` 开跑正式主实验。

## 检查命令

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_formal_preflight_report.json \
  --require-frozen-status
```

## 结构检查摘要

| 项 | 结果 |
|---|---:|
| row count | 50 |
| expected count | 50 |
| dev seed overlap | 0 blocking errors |
| no recent dialogue | 10 |
| short recent dialogue | 25 |
| long recent dialogue | 15 |
| code excerpts present | 12 |
| code excerpts none | 38 |

类别分布：

| category | count |
|---|---:|
| binary_search_boundary | 4 |
| binary_search_predicate | 5 |
| data_structure_semantics | 5 |
| debugging_evidence | 4 |
| dp_state | 5 |
| dp_transition | 5 |
| graph_tree_modeling | 5 |
| greedy_correctness | 5 |
| implementation_boundary | 5 |
| policy_request | 7 |

这些结果说明：当前 50-case 草稿已经可以交给教练审查，不是数据格式层面的坏文件。

## Formal Gate 失败原因

开启 `--require-frozen-status` 后，validator 要求每条 case 的 `reference_label_status` 属于 frozen reference 状态，例如：

```text
adjudicated_reference
coach_reference
adjudicated_gold
single_coach_reference
coach_gold
```

当前 50 条全部为：

```text
draft_needs_coach_review
```

因此报告中有 50 条 `frozen_status_required` error。这是预期失败，不表示数据内容坏掉，而是说明它还没有完成教练审查、复标、裁决和冻结。

## 下一步

正式 50-case 主实验前必须完成：

1. Coach A 审查 / 标注全部 50 条；
2. Coach B 独立复标至少 20 条 overlap；
3. 对低置信、多桥梁、重大泄露边界样本进行裁决；
4. 导出 `bridgebench_cp_heldout_v1_50_frozen.jsonl`；
5. 再次运行 formal preflight，并要求 `ok=true`；
6. 只有 frozen preflight 通过后，才运行 `--condition-set heldout_main` 的 400-row 主实验。

推荐用导出器生成 frozen 文件，而不是手工改 JSONL：

```bash
python3 -m evals.aichat.export_heldout_frozen_reference \
  --draft-jsonl docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --coach-a-workbook docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx \
  --output-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --reference-status adjudicated_reference
```

当前未填写 workbook 运行该导出器会得到 `missing_labeled_reference`，这同样是预期失败。

## 论文使用边界

当前 draft 可以用于：

- 教练审查准备；
- 数据集 card / 标注说明；
- dry run 或工具链测试。

当前 draft 不能用于：

- 正式 held-out headline result；
- prompt / judge / rubric 进一步调参后的无污染 test claim；
- 论文中“50-case frozen test set”表述。

一句话：**50-case 的内容骨架已经准备好，但它还不是 frozen held-out gold/reference。**
