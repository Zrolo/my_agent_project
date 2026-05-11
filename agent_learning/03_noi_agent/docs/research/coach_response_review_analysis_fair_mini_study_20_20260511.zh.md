# Fair 20-case 回复盲评分析（2026-05-11）

本报告分析教练填写的 `coach_response_review_workbook_fair_mini_study_20_20260511_zh_filled.xlsx`。原始 Excel 不提交进仓库；本报告使用匿名回复编号与 key 文件合并后统计。

## 数据完整性

- 评分行数：140，对应 `20 cases × 7 systems`。
- key 匹配缺失：0。
- 评审状态：labeled=140。
- 微型例子适用性：applicable=130, not_applicable=10。
- 评分置信度：high=127, medium=13。
- 需讨论：no=114, yes=26。

注意：140 行不是独立样本，而是 20 个 case 的 7 个系统回复。正式统计应优先做 paired comparison。

## 系统对比

| 系统 | 样本 | 核心6项均分 | 含微例7项均分 | 总体质量均分 | 愿意给学生看 | 不建议给学生看 | major 泄露 | rank=1 数 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current_system | 20 | 1.675 | 1.555 | 3.35 | 9 | 5 | 7 | 0 |
| single_llm | 20 | 1.592 | 1.540 | 3.35 | 6 | 3 | 1 | 0 |
| single_llm+guard | 20 | 1.808 | 1.765 | 3.95 | 11 | 1 | 1 | 1 |
| single_llm+guard+repair | 20 | 1.742 | 1.671 | 3.75 | 10 | 1 | 0 | 2 |
| bridge_contract | 20 | 1.875 | 1.843 | 4.20 | 12 | 1 | 2 | 5 |
| bridge_contract+guard | 20 | 1.867 | 1.835 | 4.20 | 12 | 2 | 2 | 6 |
| bridge_contract+guard+repair | 20 | 1.875 | 1.857 | 4.40 | 13 | 0 | 1 | 6 |

## 维度分布

- 是否抓住卡点：2=120, 1=20。
- 是否贴合上下文：2=122, 1=18。
- 帮助强度合适：2=84, 1=48, 0=8。
- 关键桥泄露控制：2=94, 1=32, 0=14。
- 下一步清楚：2=121, 1=19。
- 单一焦点：2=133, 1=7。
- 桥梁导向微型例子：2=74, 1=37, 0=19。
- 泄露标签：no_leakage=94, minor_bridge_leakage=32, major_bridge_leakage=14。
- 总体质量：5=48, 3=36, 4=42, 2=14。
- 是否愿意给学生看：yes=73, borderline=54, no=13。

## 主要发现

1. `bridge_contract + guard + repair` 在总体质量均分、愿意给学生看的数量、rank=1 数量上综合最好：总体质量 4.40，13/20 条可直接给学生看，0 条“不建议给学生看”，6 个 case 排名第一。
2. `bridge_contract` 和 `bridge_contract + guard` 也很强，分别有 5 和 6 个 case 排名第一；这说明 Bridge Contract 对回复质量有明显正向信号。
3. `single_llm_structured` 原始版本不是弱基线，但在本次人类盲评中低于加 Guard 后的版本。`single_llm + guard` 从总体质量 3.35 提升到 3.95，说明 Guard 可能不只是安全模块，也间接帮助筛掉部分过强回复。
4. `current_system` 有 7 条 major bridge leakage，且 5 条“不建议给学生看”；它仍适合作为当前线上 baseline，但不应作为最终研究系统。
5. 全部 140 条没有 answer/code leakage，问题主要集中在 major/minor critical bridge leakage，而不是完整代码泄露。
6. `bridge-oriented micro-example` 是有效区分维度：Bridge Contract 组的微型例子分明显高于 current_system 和原始 single-LLM。

## Guard / Repair 的人类审查结论

Guard/Repair 有帮助，但不是万能：

- `bridge_contract + guard + repair` 仍有 1 条 major leakage（`cp_bridge_010`），说明 runtime guard 对“例子讲得太完整导致说穿桥梁”的情况还会漏判。
- `single_llm + guard + repair` 没有 major leakage，但有 6 条 minor leakage，且总体质量低于 `single_llm + guard`，说明 repair 可能降低部分回复的自然度或教学有效性。
- 人类评审发现了一些 runtime guard false positive：例如 runtime 判断需要 rewrite，但教练认为没有泄露，只是回复质量一般或例子设计不好。

因此论文里不能写“Guard/Repair 已完全解决泄露”，更稳的说法是：Guard/Repair 改善了部分高风险回复，但仍需要 coach-calibrated leakage grader 和 repair stress test。

## 低分与争议样本

- 总体质量 <=2 的回复：14 条。
- major/answer leakage：14 条，其中 answer/code leakage 为 0 条。
- 需要讨论或低置信样本：26 条。

低分样本主要来自两类：

1. **关键桥讲穿**：如直接给 lazy 完整语义、check 条件、01 背包正序复用现象、树上差分端点/LCA 标记规则。
2. **微型例子设计失败**：例子没有暴露关键差异，学生做完临时任务仍无法理解桥梁，例如 01 背包中选择的重量/容量无法体现正序复用问题。

## 下一步建议

1. 把本次 20-case 作为 dev/regression evidence，不要直接作为最终投稿 test。
2. 先针对 `cp_bridge_010`、`cp_bridge_001`、`cp_bridge_005`、`cp_bridge_011` 建 repair stress cases，因为这些最能暴露“讲太完整即泄露”的问题。
3. 改进 Leakage Judge rubric：显式加入“fully worked micro-example can leak the bridge”。
4. 正式 50-case test 前冻结 prompt 和 grader，不再用这 20 条继续调 headline 结果。
5. 后续报告应同时呈现：人类盲评质量、关键桥泄露、是否愿意给学生看、延迟/调用次数。
