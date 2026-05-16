# DBox/Bridge 混合消融 10-case 人类教练复核报告（2026-05-14）

本报告基于教练对 `coach_response_review_workbook_dev_ablation_ai_prelim_zh_human_reviewed.xlsx` 的人工修订。它用于开发阶段判断，不作为正式 50-case held-out 结论。

## 输入与分析文件

- 人类复核表：`/Users/kongyouli/Downloads/coach_response_review_workbook_dev_ablation_ai_prelim_zh_human_reviewed.xlsx`
- 匿名 key：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/coach_response_review_workbook_dev_ablation.key.csv`
- 输出标签：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/human_reviewed_labels.jsonl`
- 输出分析：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/human_reviewed_analysis.zh.md`

## 人类复核汇总

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `enhanced_prompt_only_clean` | 10 | 3.0 | 1.5167 | 1.6 | 1.3857 | 2 | 3 | 3 | 4/5/1 | 5/3/2 |
| `dbox_inspired_clean` | 10 | 3.3 | 1.6667 | 1.4 | 1.4428 | 3 | 4 | 2 | 5/5/0 | 6/4/0 |
| `dbox_inspired_guard` | 10 | 3.1 | 1.6333 | 1.4 | 1.4143 | 1 | 3 | 2 | 3/7/0 | 7/2/1 |
| `bridge_contract_compact_guard` | 10 | 3.4 | 1.6 | 1.4 | 1.4143 | 4 | 5 | 3 | 5/4/1 | 6/4/0 |
| `bridge_guided_dbox_style_guard` | 10 | 2.4 | 1.35 | 0.8 | 1.2572 | 0 | 0 | 0 | 1/7/2 | 7/2/1 |

## 与 AI 初评的主要差异

AI 初评整体偏乐观，尤其高估了 `bridge_guided_dbox_style_guard` 和 `bridge_contract_compact_guard` 的可直接给学生看比例。

| condition | AI overall | Human overall | AI safe_ready | Human safe_ready | 主要变化 |
| --- | ---: | ---: | ---: | ---: | --- |
| `bridge_contract_compact_guard` | 4.0 | 3.4 | 10/10 | 3/10 | 人类认为仍有 4 条 minor leakage，且部分回复只能 borderline 给学生看。 |
| `bridge_guided_dbox_style_guard` | 3.9 | 2.4 | 9/10 | 0/10 | 人类认为 hybrid 回复过于模板化/不足，且出现关键桥过早透露。 |
| `dbox_inspired_clean` | 3.4 | 3.3 | 6/10 | 2/10 | 总体质量接近 AI 初评，但 safe_ready 明显下降。 |
| `dbox_inspired_guard` | 3.5 | 3.1 | 6/10 | 2/10 | Guard 没有稳定提高 DBox baseline。 |
| `enhanced_prompt_only_clean` | 3.8 | 3.0 | 8/10 | 3/10 | 人类发现 2 条 major leakage，AI 初评漏判。 |

## 关键观察

1. `bridge_contract_compact_guard` 仍是本轮最好的主方案候选，但优势不大：overall 3.4，ready 5/10，safe_ready 3/10。
2. `dbox_inspired_clean` 是强 baseline，且不加 Guard 时反而没有 major leakage；它应保留为主实验 baseline。
3. `dbox_inspired_guard` 没有稳定优于 `dbox_inspired_clean`，说明 Guard 的价值需要跨 generator 做 same-candidate 或更大样本验证。
4. `bridge_guided_dbox_style_guard` 不应进入主表；它在人类复核中 ready/safe_ready 都是 0/10，适合降级为 dev negative lesson 或 appendix。
5. 人类教练比 AI 初评更能识别“回复看似安全但帮助不足”和“微型例子把关键桥讲满”的问题。后续正式结论必须以教练盲评为准，AI 自评只能做 dev 筛查。

## Major Leakage 样例

| case | condition | 人类备注摘要 |
| --- | --- | --- |
| `heldout_v2_luogu_004` | `enhanced_prompt_only_clean` | 直接摆出两个状态维度，学生只剩复述，状态桥基本被替他搭好。 |
| `heldout_v2_luogu_005` | `enhanced_prompt_only_clean` | 把映射函数、边合法性、节点映射等核心桥铺得过完整。 |
| `heldout_v2_luogu_009` | `bridge_guided_dbox_style_guard` | 状态定义、初始化、子节点 dp、分组背包合并都摆出来，学生是在代入计算。 |
| `heldout_v2_luogu_005` | `dbox_inspired_guard` | 直接说出“树节点对应图点”这个状态核心，训练价值不高。 |

## 对实验设计的影响

建议 50-case held-out 主表保留：

- `enhanced_prompt_only_clean`
- `dbox_inspired_clean`
- `dbox_inspired_guard`
- `bridge_contract_compact_guard`

暂时不建议把 `bridge_guided_dbox_style_guard` 放进主表。它可以作为 appendix 或 error analysis，用来说明“把 Bridge Contract 和 DBox-style decomposition 简单拼接，并不自动提升教学质量”。

## 下一步

1. 不再因为这 10 条 dev 结果继续大改 prompt；只允许记录少量回归风险。
2. 使用这份人类复核作为 dev evidence，更新主实验 condition 选择。
3. 进入更大样本前，先确认 50-case 数据构成和题面/上下文完整性。
4. 正式 50-case 必须做教练盲评，AI 自评只用于初筛。
