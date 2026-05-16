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
- 含 v3 case-specific rubric 的回复：0 / 500

## 主指标

主表只保留少数结果指标；`rubric_eval_score_v1` 仅用于开发阶段筛选，不作为论文唯一结论。

| condition | n | overall | rubric_score_dev | ready | safe_ready | major+answer | sufficiency | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 3.46 | 46.51 | 27 | 27 | 4 | 1.66 | 3/45/2 |
| enhanced_prompt_only_guard | 50 | 3.54 | 46.24 | 25 | 25 | 2 | 1.62 | 4/43/3 |
| enhanced_prompt_only_guard_repair | 50 | 2.98 | 33.42 | 14 | 14 | 3 | 1.4 | 4/40/6 |
| dbox_inspired_clean | 50 | 3.76 | 54.95 | 29 | 29 | 1 | 1.78 | 24/24/2 |
| dbox_inspired_guard | 50 | 3.68 | 49.45 | 23 | 23 | 1 | 1.68 | 19/28/3 |
| dbox_inspired_guard_repair | 50 | 3.56 | 51.31 | 25 | 25 | 2 | 1.8 | 22/26/2 |
| bridge_contract_compact_clean | 50 | 3.62 | 53.36 | 31 | 31 | 1 | 1.78 | 13/37/0 |
| bridge_contract_compact_guard | 50 | 3.54 | 47.76 | 23 | 23 | 1 | 1.7 | 16/33/1 |
| bridge_contract_compact_guard_repair | 50 | 3.48 | 49.37 | 26 | 26 | 0 | 1.86 | 4/45/1 |
| bridge_guided_dbox_style_guard | 50 | 3.68 | 50.2 | 23 | 23 | 0 | 1.76 | 16/33/1 |

## 诊断指标

这些细项用于 error analysis、prompt 修订和 LLM Judge 校准；其中 micro-example 只在适用且已评分时计入。

| condition | n | core6 | bridge_id | groundedness | appropriateness | next_step | single_focus | micro mean (scored/applicable) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 1.5467 | 1.76 | 1.78 | 1.66 | 1.04 | 1.34 | 1.16 (50/50) |
| enhanced_prompt_only_guard | 50 | 1.56 | 1.8 | 1.78 | 1.58 | 1.06 | 1.46 | 1.26 (50/50) |
| enhanced_prompt_only_guard_repair | 50 | 1.4367 | 1.66 | 1.58 | 1.24 | 1.02 | 1.44 | 1.28 (50/50) |
| dbox_inspired_clean | 50 | 1.7067 | 1.74 | 1.66 | 1.76 | 1.48 | 1.8 | 1.1667 (48/48) |
| dbox_inspired_guard | 50 | 1.6433 | 1.64 | 1.56 | 1.66 | 1.34 | 1.86 | 1.22 (50/50) |
| dbox_inspired_guard_repair | 50 | 1.68 | 1.64 | 1.64 | 1.66 | 1.4 | 1.86 | 1.1837 (49/49) |
| bridge_contract_compact_clean | 50 | 1.6867 | 1.7 | 1.7 | 1.82 | 1.24 | 1.78 | 1.2449 (49/49) |
| bridge_contract_compact_guard | 50 | 1.6267 | 1.64 | 1.58 | 1.66 | 1.26 | 1.8 | 0.9184 (49/49) |
| bridge_contract_compact_guard_repair | 50 | 1.6467 | 1.76 | 1.7 | 1.64 | 1.06 | 1.8 | 1.1429 (49/49) |
| bridge_guided_dbox_style_guard | 50 | 1.6367 | 1.56 | 1.44 | 1.78 | 1.26 | 1.86 | 1.2 (50/50) |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 50 | -0.08 | -0.0633 | -0.0495 | 6/33/11 | [-0.28, 0.12] |
| enhanced_prompt_only_guard - enhanced_prompt_only_clean | 50 | 0.08 | 0.0133 | 0.0257 | 10/34/6 | [-0.16, 0.3] |
| enhanced_prompt_only_guard_repair - enhanced_prompt_only_guard | 50 | -0.56 | -0.1233 | -0.1028 | 7/18/25 | [-0.84, -0.28] |
| dbox_inspired_guard_repair - dbox_inspired_guard | 50 | -0.12 | 0.0367 | 0.0286 | 8/31/11 | [-0.4, 0.16] |
| bridge_contract_compact_guard - bridge_contract_compact_clean | 50 | -0.08 | -0.06 | -0.0971 | 8/28/14 | [-0.32, 0.18] |
| bridge_contract_compact_guard_repair - bridge_contract_compact_guard | 50 | -0.06 | 0.02 | 0.0486 | 12/25/13 | [-0.28, 0.16] |
| bridge_contract_compact_guard - dbox_inspired_guard | 50 | -0.14 | -0.0167 | -0.0548 | 12/21/17 | [-0.38, 0.1] |
| bridge_contract_compact_guard_repair - dbox_inspired_guard_repair | 50 | -0.08 | -0.0333 | -0.0348 | 10/24/16 | [-0.36, 0.22] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 50 | 0.0 | -0.0067 | -0.0086 | 11/28/11 | [-0.22, 0.24] |
| dbox_inspired_guard - bridge_guided_dbox_style_guard | 50 | 0.0 | 0.0067 | 0.0086 | 11/28/11 | [-0.24, 0.22] |

## Major/Answer Leakage Case Memo 草稿

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
- 若 `含 v3 case-specific rubric` 数量为 0，本报告只是 v3 指标重分析；case-specific grader 校准不能把这批旧表当作完整证据。
- 本轮没有包含 `bridge_contract_safe_scaffold` 常规条件；safe scaffold 只作为 block/fallback 机制和 appendix 候选。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 新增 `scaffold_sufficiency` 用于识别“低泄露但帮助不足”的过度保留回复；正式比较时应把 leakage 和 sufficiency 放在一起看。
- `学生回复负担` 只作为交互成本指标，不进入 core score；它用于识别学生需要输入过多而导致在线体验变差的回复。
- 出现 major/answer 级泄露的条件：{'enhanced_prompt_only_clean': 4, 'enhanced_prompt_only_guard': 2, 'enhanced_prompt_only_guard_repair': 3, 'dbox_inspired_clean': 1, 'dbox_inspired_guard': 1, 'dbox_inspired_guard_repair': 2, 'bridge_contract_compact_clean': 1, 'bridge_contract_compact_guard': 1}。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛选 50-case 主实验条件：强 prompt、DBox-inspired、DBox+Guard、Bridge Contract、Safe Scaffold 是否值得保留，要看它们在 paired W/T/L 和 student-ready pass 上是否稳定。

## 解释边界

这批 50-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
