# Dev Ablation 20-case 盲评分析

本报告分析 20 个 dev cases、1 个匿名系统条件、20 条 盲审回复。它用于开发阶段决策和 prompt/regression 修订，不作为最终 held-out test 结论。

- 盲审表：`dbox_guard_repair_fairness_review20_workbook_20260517_reviewed.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.key.csv`

- 已标注回复：20 条
- case 数：20 个
- 总体泄露标签：{'minor_bridge_leakage': 6, 'no_leakage': 14}
- 关键桥透露正当性：{'borderline': 5, 'pedagogically_justified': 4, 'no_reveal': 11}
- 学生回复负担：{'medium': 9, 'high': 3, 'low': 8}
- 是否愿意给学生看：{'borderline': 9, 'yes': 11}
- 含 v3 case-specific rubric 的回复：20 / 20

## 主指标

主表只保留少数结果指标；`rubric_eval_score_v1` 仅用于开发阶段筛选，不作为论文唯一结论。

| condition | n | overall | rubric_score_dev | ready | safe_ready | major+answer | sufficiency | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| enhanced_prompt_only_guard | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| enhanced_prompt_only_guard_repair | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| dbox_inspired_clean | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| dbox_inspired_guard | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| dbox_inspired_guard_repair | 20 | 3.55 | 52.075 | 10 | 10 | 0 | 1.8 | 8/9/3 |
| bridge_contract_compact_clean | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| bridge_contract_compact_guard | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| bridge_contract_compact_guard_repair | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| bridge_guided_dbox_style_guard | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |

## 诊断指标

这些细项用于 error analysis、prompt 修订和 LLM Judge 校准；其中 micro-example 只在适用且已评分时计入。

| condition | n | core6 | bridge_id | groundedness | appropriateness | next_step | single_focus | micro mean (scored/applicable) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| enhanced_prompt_only_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| enhanced_prompt_only_guard_repair | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| dbox_inspired_guard_repair | 20 | 1.7083 | 1.85 | 1.7 | 1.5 | 1.7 | 1.8 | 1.5 (10/10) |
| bridge_contract_compact_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| bridge_contract_compact_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| bridge_contract_compact_guard_repair | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| bridge_guided_dbox_style_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| enhanced_prompt_only_guard - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| enhanced_prompt_only_guard_repair - enhanced_prompt_only_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| dbox_inspired_guard_repair - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_compact_guard - bridge_contract_compact_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_compact_guard_repair - bridge_contract_compact_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_compact_guard - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_compact_guard_repair - dbox_inspired_guard_repair | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| dbox_inspired_guard - bridge_guided_dbox_style_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |

## Major/Answer Leakage Case Memo 草稿

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |

## 初步观察

- `student_ready_pass` 最高的是 `dbox_inspired_guard_repair`：10 / 20。
- 若 `含 v3 case-specific rubric` 数量为 0，本报告只是 v3 指标重分析；case-specific grader 校准不能把这批旧表当作完整证据。
- 本轮没有包含 `bridge_contract_safe_scaffold` 常规条件；safe scaffold 只作为 block/fallback 机制和 appendix 候选。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 新增 `scaffold_sufficiency` 用于识别“低泄露但帮助不足”的过度保留回复；正式比较时应把 leakage 和 sufficiency 放在一起看。
- `学生回复负担` 只作为交互成本指标，不进入 core score；它用于识别学生需要输入过多而导致在线体验变差的回复。
- 出现 major/answer 级泄露的条件：无。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛选 50-case 主实验条件：强 prompt、DBox-inspired、DBox+Guard、Bridge Contract、Safe Scaffold 是否值得保留，要看它们在 paired W/T/L 和 student-ready pass 上是否稳定。

## 解释边界

这批 20-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
