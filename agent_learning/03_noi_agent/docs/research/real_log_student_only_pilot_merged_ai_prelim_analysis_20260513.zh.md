# 真实 AIChat student-only 8-case merged pilot AI 自评分析（2026-05-13）

本报告分析 8 个真实线上学生提问的 student-only pilot cases、6 个匿名系统条件、48 条 AI 预评回复。它用于真实日志 dev realism check 和 EDF core 条件筛查，不是教练 gold label，也不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_real_log_pilot_merged_20260513.ai_prelim.zh.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_merged/coach_response_review_workbook_dev_ablation.key.csv`

- 已标注回复：48 条
- case 数：8 个
- 总体泄露标签：{'no_leakage': 38, 'minor_bridge_leakage': 10}
- 关键桥透露正当性：{'no_reveal': 38, 'borderline': 10}
- 学生回复负担：{'low': 47, 'high': 1}
- 是否愿意给学生看：{'yes': 31, 'borderline': 17}

## 系统汇总

| condition | n | overall | core6 | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 8 | 3.75 | 1.9375 | 1.7143 | 0 | 6 | 6 | 6/2/0 | 7/1/0 | 0/1/0 | 8/0/0 |
| dbox_inspired_guard | 8 | 3.75 | 1.9583 | 1.7321 | 0 | 6 | 6 | 6/2/0 | 6/2/0 | 0/2/0 | 8/0/0 |
| edf_inspired_clean | 8 | 3.5 | 1.875 | 1.625 | 0 | 4 | 4 | 4/4/0 | 6/2/0 | 0/2/0 | 7/0/1 |
| edf_inspired_guard | 8 | 3.375 | 1.7917 | 1.5357 | 0 | 3 | 3 | 3/5/0 | 6/2/0 | 0/2/0 | 8/0/0 |
| bridge_contract_guard | 8 | 3.625 | 1.9375 | 1.8035 | 0 | 5 | 5 | 5/3/0 | 5/3/0 | 0/3/0 | 8/0/0 |
| bridge_contract_guard_repair | 8 | 3.875 | 1.9583 | 1.7857 | 0 | 7 | 7 | 7/1/0 | 8/0/0 | 0/0/0 | 8/0/0 |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_guard - dbox_inspired_guard | 8 | -0.125 | -0.0208 | 0.0714 | 0/7/1 | [-0.375, 0.0] |
| edf_inspired_guard - edf_inspired_clean | 8 | -0.125 | -0.0833 | -0.0893 | 1/5/2 | [-0.5, 0.375] |
| edf_inspired_guard - dbox_inspired_guard | 8 | -0.375 | -0.1666 | -0.1964 | 0/5/3 | [-0.75, -0.125] |
| bridge_contract_guard - edf_inspired_guard | 8 | 0.25 | 0.1458 | 0.2678 | 3/4/1 | [-0.25, 0.625] |
| bridge_contract_guard_repair - edf_inspired_guard | 8 | 0.5 | 0.1667 | 0.25 | 4/4/0 | [0.125, 0.875] |
| bridge_contract_guard_repair - bridge_contract_guard | 8 | 0.25 | 0.0208 | -0.0179 | 2/6/0 | [0.0, 0.625] |

## Major Leakage 样例定位

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_contract_guard_repair`：7 / 8。
- 本轮是 EDF core 条件集：重点看 EDF 是否接近 enhanced prompt / DBox+Guard，以及 Guard 是否改善 EDF。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 出现 major/answer 级泄露的条件：无。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛查 EDF-inspired 是否值得进入 appendix/dev 继续观察；按 AI 预评结果，它暂时弱于 DBox+Guard 和 Bridge Contract+Guard+Repair。

## 解释边界

这批 8-case 是真实日志 student-only pilot / dev realism check。可以据此发现真实学生问题形态、修 prompt、修 rubric、决定主实验候选条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
