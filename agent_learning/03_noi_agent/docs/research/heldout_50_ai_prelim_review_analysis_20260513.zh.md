# Dev Ablation 50-case AI 初评分析

本报告分析 50 个 dev cases、8 个匿名系统条件、400 条 AI 预评回复。它用于开发阶段决策和 prompt/regression 修订，不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged/coach_response_review_workbook_dev_ablation.key.csv`

- 已标注回复：400 条
- case 数：50 个
- 总体泄露标签：{'no_leakage': 300, 'minor_bridge_leakage': 75, 'major_bridge_leakage': 9, 'answer_leakage': 16}
- 关键桥透露正当性：{'no_reveal': 300, 'borderline': 75, 'unjustified': 25}
- 学生回复负担：{'low': 386, 'high': 14}
- 是否愿意给学生看：{'yes': 282, 'borderline': 93, 'no': 25}

## 系统汇总

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_system_deployment | 50 | 3.5 | 1.9067 | 1.88 | 1.7371 | 0 | 36 | 36 | 36/8/6 | 36/8/6 | 0/8/6 | 45/0/5 |
| enhanced_prompt_only_clean | 50 | 3.44 | 1.9 | 1.9 | 1.7314 | 0 | 30 | 30 | 30/16/4 | 31/15/4 | 0/15/4 | 49/0/1 |
| socratic_no_answer_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| codehelp_codeaid_clean | 50 | 3.62 | 1.92 | 1.88 | 1.7543 | 0 | 36 | 36 | 36/10/4 | 38/8/4 | 0/8/4 | 50/0/0 |
| dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| dbox_inspired_guard | 50 | 3.7 | 1.94 | 1.94 | 1.74 | 0 | 37 | 37 | 37/12/1 | 38/11/1 | 0/11/1 | 46/0/4 |
| edf_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| bridge_inspired_expert_decision_clean | 50 | 3.68 | 1.9067 | 1.78 | 1.68 | 0 | 36 | 36 | 36/13/1 | 44/5/1 | 0/5/1 | 50/0/0 |
| single_llm_structured_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| single_llm_structured_guard | 50 | 3.68 | 1.9267 | 1.88 | 1.7086 | 0 | 35 | 35 | 35/14/1 | 40/9/1 | 0/9/1 | 49/0/1 |
| bridge_contract_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| bridge_contract_guard | 50 | 3.5 | 1.9067 | 1.84 | 1.7314 | 0 | 34 | 34 | 34/10/6 | 34/10/6 | 0/10/6 | 49/0/1 |
| bridge_contract_guard_repair | 50 | 3.7 | 1.9433 | 1.94 | 1.7628 | 0 | 38 | 38 | 38/10/2 | 39/9/2 | 0/9/2 | 48/0/2 |
| bridge_contract_safe_scaffold | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_safe_scaffold - bridge_contract_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - bridge_contract_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard - dbox_inspired_guard | 50 | -0.2 | -0.0333 | -0.0086 | 3/38/9 | [-0.4, -0.02] |
| edf_inspired_guard - edf_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| edf_inspired_guard - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard - edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard_repair - edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard_repair - bridge_contract_guard | 50 | 0.2 | 0.0367 | 0.0314 | 8/39/3 | [0.0, 0.42] |
| bridge_contract_clean - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| dbox_inspired_guard - dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| single_llm_structured_guard - single_llm_structured_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |

## Major Leakage 样例定位

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| heldout_cp_035 | current_system_deployment | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | codehelp_codeaid_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_014 | bridge_contract_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_048 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_019 | bridge_contract_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | bridge_inspired_expert_decision_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | bridge_contract_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_019 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_045 | codehelp_codeaid_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_039 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | bridge_contract_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | codehelp_codeaid_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_003 | bridge_contract_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | dbox_inspired_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | single_llm_structured_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | bridge_contract_guard_repair | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_024 | codehelp_codeaid_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_039 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_036 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_014 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | bridge_contract_guard_repair | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_039 | bridge_contract_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_contract_guard_repair`：38 / 50。
- 本轮没有包含 `bridge_contract_safe_scaffold` 常规条件；safe scaffold 只作为 block/fallback 机制和 appendix 候选。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 新增 `scaffold_sufficiency` 用于识别“低泄露但帮助不足”的过度保留回复；正式比较时应把 leakage 和 sufficiency 放在一起看。
- 出现 major/answer 级泄露的条件：{'current_system_deployment': 6, 'enhanced_prompt_only_clean': 4, 'codehelp_codeaid_clean': 4, 'dbox_inspired_guard': 1, 'bridge_inspired_expert_decision_clean': 1, 'single_llm_structured_guard': 1, 'bridge_contract_guard': 6, 'bridge_contract_guard_repair': 2}。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛选 50-case 主实验条件：强 prompt、DBox-inspired、DBox+Guard、Bridge Contract、Safe Scaffold 是否值得保留，要看它们在 paired W/T/L 和 student-ready pass 上是否稳定。

## 解释边界

这批 50-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
