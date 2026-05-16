# Dev Ablation 50-case AI 初评分析

本报告分析 50 个 dev cases、5 个匿名系统条件、250 条 AI 预评回复。它用于开发阶段决策和 prompt/regression 修订，不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_dbox_bridge_hybrid_generation_only_50_20260515.ai_prelim.zh.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_dev_ablation.key.csv`

- 已标注回复：250 条
- case 数：50 个
- 总体泄露标签：{'no_leakage': 184, 'answer_leakage': 9, 'minor_bridge_leakage': 52, 'major_bridge_leakage': 5}
- 关键桥透露正当性：{'no_reveal': 184, 'unjustified': 14, 'borderline': 52}
- 学生回复负担：{'low': 230, 'high': 20}
- 是否愿意给学生看：{'yes': 181, 'no': 14, 'borderline': 55}

## 系统汇总

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 3.5 | 1.9133 | 1.94 | 1.7486 | 12 | 31 | 31 | 31/16/3 | 31/16/3 | 0/16/3 | 43/0/7 |
| dbox_inspired_clean | 50 | 3.66 | 1.9333 | 1.88 | 1.7086 | 11 | 37 | 37 | 37/10/3 | 38/9/3 | 0/9/3 | 49/0/1 |
| dbox_inspired_guard | 50 | 3.66 | 1.9367 | 1.94 | 1.7114 | 7 | 36 | 36 | 36/12/2 | 37/11/2 | 0/11/2 | 43/0/7 |
| bridge_contract_compact_guard | 50 | 3.6 | 1.9167 | 1.88 | 1.7057 | 8 | 36 | 36 | 36/10/4 | 37/9/4 | 0/9/4 | 48/0/2 |
| bridge_guided_dbox_style_guard | 50 | 3.74 | 1.9567 | 1.96 | 1.7771 | 12 | 41 | 41 | 41/7/2 | 41/7/2 | 0/7/2 | 47/0/3 |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 50 | 0.0 | 0.0033 | 0.0029 | 5/40/5 | [-0.22, 0.22] |
| bridge_contract_compact_guard - dbox_inspired_guard | 50 | -0.06 | -0.02 | -0.0057 | 7/35/8 | [-0.26, 0.14] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 50 | 0.08 | 0.02 | 0.0657 | 8/39/3 | [-0.1, 0.26] |

## Major Leakage 样例定位

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| heldout_v4_luogu_042 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_005 | dbox_inspired_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_006 | dbox_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_044 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_041 | dbox_inspired_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_001 | bridge_contract_compact_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_041 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_044 | bridge_guided_dbox_style_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_002 | dbox_inspired_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_044 | dbox_inspired_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_019 | bridge_contract_compact_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_041 | bridge_guided_dbox_style_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_044 | bridge_contract_compact_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_042 | bridge_contract_compact_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_guided_dbox_style_guard`：41 / 50。
- 本轮没有包含 `bridge_contract_safe_scaffold` 常规条件；safe scaffold 只作为 block/fallback 机制和 appendix 候选。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 新增 `scaffold_sufficiency` 用于识别“低泄露但帮助不足”的过度保留回复；正式比较时应把 leakage 和 sufficiency 放在一起看。
- 出现 major/answer 级泄露的条件：{'enhanced_prompt_only_clean': 3, 'dbox_inspired_clean': 3, 'dbox_inspired_guard': 2, 'bridge_contract_compact_guard': 4, 'bridge_guided_dbox_style_guard': 2}。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛选 50-case 主实验条件：强 prompt、DBox-inspired、DBox+Guard、Bridge Contract、Safe Scaffold 是否值得保留，要看它们在 paired W/T/L 和 student-ready pass 上是否稳定。

## 解释边界

这批 50-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
