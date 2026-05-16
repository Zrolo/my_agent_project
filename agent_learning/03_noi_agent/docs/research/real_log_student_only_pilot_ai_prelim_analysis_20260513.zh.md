# 真实 AIChat student-only 8-case pilot AI 自评分析（2026-05-13）

本报告分析 8 个真实线上 AIChat student-only pilot cases、6 个匿名系统条件、46 条 AI 预评回复。它用于真实学生提问 dev realism check 和 EDF core 条件筛查，不是教练 gold label，也不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_real_log_pilot_20260513.ai_prelim.zh.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513/coach_response_review_workbook_dev_ablation.key.csv`

- 已标注回复：46 条
- case 数：8 个
- 总体泄露标签：{'no_leakage': 37, 'minor_bridge_leakage': 9}
- 关键桥透露正当性：{'no_reveal': 37, 'borderline': 9}
- 学生回复负担：{'low': 45, 'high': 1}
- 是否愿意给学生看：{'yes': 30, 'borderline': 16}

## 系统汇总

| condition | n | overall | core6 | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 8 | 3.75 | 1.9375 | 1.7143 | 0 | 6 | 6 | 6/2/0 | 7/1/0 | 0/1/0 | 8/0/0 |
| dbox_inspired_guard | 7 | 3.8571 | 1.9762 | 1.7551 | 0 | 6 | 6 | 6/1/0 | 6/1/0 | 0/1/0 | 7/0/0 |
| edf_inspired_clean | 7 | 3.4286 | 1.8571 | 1.5918 | 0 | 3 | 3 | 3/4/0 | 5/2/0 | 0/2/0 | 6/0/1 |
| edf_inspired_guard | 8 | 3.375 | 1.7917 | 1.5357 | 0 | 3 | 3 | 3/5/0 | 6/2/0 | 0/2/0 | 8/0/0 |
| bridge_contract_guard | 8 | 3.625 | 1.9375 | 1.8035 | 0 | 5 | 5 | 5/3/0 | 5/3/0 | 0/3/0 | 8/0/0 |
| bridge_contract_guard_repair | 8 | 3.875 | 1.9583 | 1.7857 | 0 | 7 | 7 | 7/1/0 | 8/0/0 | 0/0/0 | 8/0/0 |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_guard - dbox_inspired_guard | 7 | -0.1429 | -0.0238 | 0.0612 | 0/6/1 | [-0.4286, 0.0] |
| edf_inspired_guard - edf_inspired_clean | 7 | 0.0 | -0.0476 | -0.0408 | 1/5/1 | [-0.4286, 0.4286] |
| edf_inspired_guard - dbox_inspired_guard | 7 | -0.4286 | -0.1428 | -0.1836 | 0/4/3 | [-0.8571, -0.1429] |
| bridge_contract_guard - edf_inspired_guard | 8 | 0.25 | 0.1458 | 0.2678 | 3/4/1 | [-0.25, 0.75] |
| bridge_contract_guard_repair - edf_inspired_guard | 8 | 0.5 | 0.1667 | 0.25 | 4/4/0 | [0.125, 0.875] |
| bridge_contract_guard_repair - bridge_contract_guard | 8 | 0.25 | 0.0208 | -0.0179 | 2/6/0 | [0.0, 0.625] |

## Major Leakage 样例定位

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_contract_guard_repair`：7 / 8。
- 本轮使用 EDF core 条件集，但样本来源是真实线上 student-only pilot，不是构造 seed 10-case。
- 重点看真实学生提问下 enhanced prompt、DBox+Guard、EDF、Bridge Contract+Guard/Repair 是否能稳定生成低负担脚手架。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 出现 major/answer 级泄露的条件：无。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛查真实 student-only 提问在现有主 baseline 上是否可跑通，并观察 EDF-inspired 是否值得进入 appendix/dev 继续观察；按 AI 预评结果，它暂时弱于 DBox+Guard 和 Bridge Contract+Guard+Repair。

## 解释边界

这批 8-case 是真实日志 student-only pilot 子集。它可以用于发现真实学生提问下的生成稳定性、上下文缺失风险和 baseline 粗略表现；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
