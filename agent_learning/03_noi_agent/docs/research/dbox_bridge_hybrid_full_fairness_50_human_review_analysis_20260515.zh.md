# Dev Ablation 50-case 盲评分析

本报告分析 50 个 dev cases、10 个匿名系统条件、500 条 盲审回复。它用于开发阶段决策和 prompt/regression 修订，不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_dev_ablation_zh7_human_coach_reviewed.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_full_fairness_50_20260514/coach_response_review_workbook_dev_ablation.key.csv`

- 已标注回复：500 条
- case 数：50 个
- 总体泄露标签：{'no_leakage': 419, 'minor_bridge_leakage': 66, 'major_bridge_leakage': 5, 'answer_leakage': 10}
- 关键桥透露正当性：{'no_reveal': 419, 'borderline': 66, 'unjustified': 15}
- 学生回复负担：{'medium': 354, 'low': 125, 'high': 21}
- 是否愿意给学生看：{'borderline': 210, 'yes': 248, 'no': 42}

## 系统汇总

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 3.46 | 1.5467 | 1.66 | 1.4914 | 2 | 27 | 27 | 28/15/7 | 39/7/4 | 0/7/4 | 3/45/2 |
| enhanced_prompt_only_guard | 50 | 3.54 | 1.56 | 1.62 | 1.5171 | 0 | 25 | 25 | 25/21/4 | 36/12/2 | 0/12/2 | 4/43/3 |
| enhanced_prompt_only_guard_repair | 50 | 2.98 | 1.4367 | 1.4 | 1.4143 | 0 | 14 | 14 | 14/21/15 | 37/10/3 | 0/10/3 | 4/40/6 |
| dbox_inspired_clean | 50 | 3.76 | 1.7067 | 1.78 | 1.6228 | 9 | 29 | 29 | 29/20/1 | 41/8/1 | 0/8/1 | 24/24/2 |
| dbox_inspired_guard | 50 | 3.68 | 1.6433 | 1.68 | 1.5829 | 8 | 23 | 23 | 23/26/1 | 41/8/1 | 0/8/1 | 19/28/3 |
| dbox_inspired_guard_repair | 50 | 3.56 | 1.68 | 1.8 | 1.6057 | 11 | 25 | 25 | 25/23/2 | 46/2/2 | 0/2/2 | 22/26/2 |
| bridge_contract_compact_clean | 50 | 3.62 | 1.6867 | 1.78 | 1.62 | 10 | 31 | 31 | 31/15/4 | 45/4/1 | 0/4/1 | 13/37/0 |
| bridge_contract_compact_guard | 50 | 3.54 | 1.6267 | 1.7 | 1.5229 | 2 | 23 | 23 | 23/23/4 | 42/7/1 | 0/7/1 | 16/33/1 |
| bridge_contract_compact_guard_repair | 50 | 3.48 | 1.6467 | 1.86 | 1.5714 | 3 | 26 | 26 | 26/20/4 | 46/4/0 | 0/4/0 | 4/45/1 |
| bridge_guided_dbox_style_guard | 50 | 3.68 | 1.6367 | 1.76 | 1.5743 | 5 | 23 | 23 | 24/26/0 | 46/4/0 | 0/4/0 | 16/33/1 |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 50 | -0.08 | -0.0633 | -0.04 | 6/33/11 | [-0.28, 0.12] |
| enhanced_prompt_only_guard - enhanced_prompt_only_clean | 50 | 0.08 | 0.0133 | 0.0257 | 10/34/6 | [-0.16, 0.3] |
| enhanced_prompt_only_guard_repair - enhanced_prompt_only_guard | 50 | -0.56 | -0.1233 | -0.1028 | 7/18/25 | [-0.84, -0.28] |
| dbox_inspired_guard_repair - dbox_inspired_guard | 50 | -0.12 | 0.0367 | 0.0229 | 8/31/11 | [-0.4, 0.16] |
| bridge_contract_compact_guard - bridge_contract_compact_clean | 50 | -0.08 | -0.06 | -0.0971 | 8/28/14 | [-0.32, 0.18] |
| bridge_contract_compact_guard_repair - bridge_contract_compact_guard | 50 | -0.06 | 0.02 | 0.0486 | 12/25/13 | [-0.28, 0.16] |
| bridge_contract_compact_guard - dbox_inspired_guard | 50 | -0.14 | -0.0167 | -0.06 | 12/21/17 | [-0.38, 0.1] |
| bridge_contract_compact_guard_repair - dbox_inspired_guard_repair | 50 | -0.08 | -0.0333 | -0.0343 | 10/24/16 | [-0.36, 0.22] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 50 | 0.0 | -0.0067 | -0.0086 | 11/28/11 | [-0.22, 0.24] |

## Major Leakage 样例定位

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| heldout_v2_luogu_011 | enhanced_prompt_only_clean | 2.0 | no | unjustified | 抓到点了，但转移合法性的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_027 | bridge_contract_compact_guard | 2.0 | no | unjustified | 抓到点了，但差分标记位置的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_044 | enhanced_prompt_only_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_033 | dbox_inspired_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是数据结构维护量，不能直接把成品塞过去。 |
| heldout_v2_luogu_044 | bridge_contract_compact_clean | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_037 | enhanced_prompt_only_guard | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是策略背后的不变量，不能直接把成品塞过去。 |
| heldout_v2_luogu_041 | enhanced_prompt_only_clean | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_049 | enhanced_prompt_only_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是拒绝整题答案后的下一步入口，不能直接把成品塞过去。 |
| heldout_v2_luogu_009 | enhanced_prompt_only_clean | 2.0 | no | unjustified | 抓到点了，但DP 转移来源的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_020 | enhanced_prompt_only_guard | 2.0 | no | unjustified | 抓到点了，但二分对象和边界方向的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_041 | dbox_inspired_guard | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_012 | enhanced_prompt_only_clean | 2.0 | no | unjustified | 抓到点了，但check 判定条件的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_043 | enhanced_prompt_only_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_050 | dbox_inspired_clean | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是拒绝整题答案后的下一步入口，不能直接把成品塞过去。 |
| heldout_v2_luogu_021 | dbox_inspired_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是边界更新顺序，不能直接把成品塞过去。 |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_contract_compact_clean`：31 / 50。
- 本轮没有包含 `bridge_contract_safe_scaffold` 常规条件；safe scaffold 只作为 block/fallback 机制和 appendix 候选。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 新增 `scaffold_sufficiency` 用于识别“低泄露但帮助不足”的过度保留回复；正式比较时应把 leakage 和 sufficiency 放在一起看。
- 出现 major/answer 级泄露的条件：{'enhanced_prompt_only_clean': 4, 'enhanced_prompt_only_guard': 2, 'enhanced_prompt_only_guard_repair': 3, 'dbox_inspired_clean': 1, 'dbox_inspired_guard': 1, 'dbox_inspired_guard_repair': 2, 'bridge_contract_compact_clean': 1, 'bridge_contract_compact_guard': 1}。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛选 50-case 主实验条件：强 prompt、DBox-inspired、DBox+Guard、Bridge Contract、Safe Scaffold 是否值得保留，要看它们在 paired W/T/L 和 student-ready pass 上是否稳定。

## 解释边界

这批 50-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
