# EDF-inspired 10-case AI 自评分析（2026-05-12）

本报告分析 10 个 dev cases、6 个匿名系统条件、60 条 AI 预评回复。它用于 EDF-inspired baseline 开发阶段筛查，不是教练 gold label，也不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/edf_core_ablation_20260512/coach_response_review_workbook_dev_ablation.key.csv`

- 已标注回复：60 条
- case 数：10 个
- 总体泄露标签：{'no_leakage': 33, 'minor_bridge_leakage': 19, 'major_bridge_leakage': 8}
- 关键桥透露正当性：{'no_reveal': 33, 'borderline': 19, 'unjustified': 8}
- 学生回复负担：{'low': 59, 'high': 1}
- 是否愿意给学生看：{'yes': 25, 'borderline': 27, 'no': 8}

## 系统汇总

| condition | n | overall | core6 | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 10 | 3.4 | 1.8833 | 1.7286 | 0 | 5 | 5 | 5/4/1 | 5/4/1 | 0/4/1 | 10/0/0 |
| dbox_inspired_guard | 10 | 3.4 | 1.8833 | 1.6857 | 0 | 5 | 5 | 5/4/1 | 5/4/1 | 0/4/1 | 10/0/0 |
| edf_inspired_clean | 10 | 3.1 | 1.7333 | 1.5 | 0 | 3 | 3 | 3/5/2 | 6/2/2 | 0/2/2 | 10/0/0 |
| edf_inspired_guard | 10 | 2.9 | 1.65 | 1.4286 | 0 | 2 | 2 | 2/5/3 | 6/1/3 | 0/1/3 | 10/0/0 |
| bridge_contract_guard | 10 | 3.4 | 1.8833 | 1.7429 | 0 | 4 | 4 | 4/6/0 | 5/5/0 | 0/5/0 | 9/0/1 |
| bridge_contract_guard_repair | 10 | 3.5 | 1.9 | 1.7428 | 0 | 6 | 6 | 6/3/1 | 6/3/1 | 0/3/1 | 10/0/0 |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_guard - dbox_inspired_guard | 10 | 0.0 | 0.0 | 0.0571 | 1/8/1 | [-0.3, 0.3] |
| edf_inspired_guard - edf_inspired_clean | 10 | -0.2 | -0.0833 | -0.0714 | 1/6/3 | [-0.6, 0.2] |
| edf_inspired_guard - dbox_inspired_guard | 10 | -0.5 | -0.2333 | -0.2571 | 0/5/5 | [-0.8, -0.2] |
| bridge_contract_guard - edf_inspired_guard | 10 | 0.5 | 0.2333 | 0.3143 | 6/3/1 | [0.1, 0.9] |
| bridge_contract_guard_repair - edf_inspired_guard | 10 | 0.6 | 0.25 | 0.3143 | 5/5/0 | [0.2, 1.0] |
| bridge_contract_guard_repair - bridge_contract_guard | 10 | 0.1 | 0.0167 | -0.0 | 2/7/1 | [-0.2, 0.4] |

## Major Leakage 样例定位

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| cp_bridge_010 | bridge_contract_guard_repair | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_001 | edf_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_010 | edf_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_001 | edf_inspired_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_005 | edf_inspired_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_002 | enhanced_prompt_only_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_005 | edf_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_010 | dbox_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_contract_guard_repair`：6 / 10。
- 本轮是 EDF core 条件集：重点看 EDF 是否接近 enhanced prompt / DBox+Guard，以及 guard-instrumented EDF 变体是否值得继续保留；不能把不同 run 的差异直接解释为 Guard 已修复最终输出。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 出现 major/answer 级泄露的条件：{'enhanced_prompt_only_clean': 1, 'dbox_inspired_guard': 1, 'edf_inspired_clean': 2, 'edf_inspired_guard': 3, 'bridge_contract_guard_repair': 1}。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛查 EDF-inspired 是否值得进入 appendix/dev 继续观察；按 AI 预评结果，它暂时弱于 DBox+Guard 和 Bridge Contract+Guard+Repair。

## 解释边界

这批 10-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
