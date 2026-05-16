# 50-case 高风险 case pack 11-case 盲评分析

本报告分析从 50-case × 8-condition AI 预评中抽出的 11 个高风险 cases、8 个匿名系统条件、88 条教练盲审回复。它用于开发阶段决策、AI 预评校准和 prompt/regression 修订，不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_dev_ablation_ai_prelim_high_risk_case_pack_zh_blind_reviewed.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged/coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_case_pack.key.csv`

- 已标注回复：88 条
- case 数：11 个
- 总体泄露标签：{'no_leakage': 66, 'minor_bridge_leakage': 15, 'major_bridge_leakage': 7}
- 关键桥透露正当性：{'no_reveal': 66, 'borderline': 15, 'unjustified': 7}
- 学生回复负担：{'medium': 48, 'low': 31, 'high': 9}
- 是否愿意给学生看：{'yes': 37, 'borderline': 45, 'no': 6}

## AI 预评 vs 教练复核

这份 case pack 来自 AI 预评高风险抽样。教练复核显示，AI 预评偏保守，尤其容易把 answer-slot / worked-example 风险判成 `answer_leakage`。

| 对比项 | 结果 |
| --- | --- |
| AI 判 severe，教练也判 severe | 2 |
| AI 判 severe，教练不判 severe | 23 |
| AI 不判 severe，教练判 severe | 5 |
| AI 不判 severe，教练也不判 severe | 58 |

原始 25 条 AI 高风险行中，教练复核后：

| 教练复核结果 | 数量 |
| --- | ---: |
| `major_bridge_leakage` | 2 |
| `minor_bridge_leakage` | 7 |
| `no_leakage` | 16 |
| `would_show_to_student=no` | 1 |
| 总体质量为 1/2 | 2 |

这说明 AI 预评适合做“召回式 triage”，但不能当作最终泄露标签。正式论文中必须把它写成 dev screening / candidate selection tool，而不是 coach reference。

## 系统汇总

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_system_deployment | 11 | 3.3636 | 1.4394 | 1.9091 | 1.3117 | 1 | 3 | 3 | 3/5/3 | 4/5/2 | 0/5/2 | 5/3/3 |
| enhanced_prompt_only_clean | 11 | 3.5455 | 1.6364 | 1.8182 | 1.5065 | 3 | 6 | 6 | 6/3/2 | 7/1/3 | 0/1/3 | 6/5/0 |
| socratic_no_answer_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| codehelp_codeaid_clean | 11 | 3.2727 | 1.5151 | 1.6364 | 1.3766 | 0 | 3 | 2 | 3/8/0 | 7/3/1 | 0/3/1 | 0/8/3 |
| dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| dbox_inspired_guard | 11 | 3.7273 | 1.7727 | 1.5455 | 1.5714 | 2 | 7 | 7 | 7/4/0 | 10/0/1 | 0/0/1 | 9/2/0 |
| edf_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| bridge_inspired_expert_decision_clean | 11 | 3.0909 | 1.5455 | 1.2727 | 1.3377 | 0 | 3 | 2 | 3/7/1 | 8/3/0 | 0/3/0 | 4/7/0 |
| single_llm_structured_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| single_llm_structured_guard | 11 | 2.7273 | 1.4242 | 0.8182 | 1.2208 | 0 | 2 | 2 | 2/9/0 | 11/0/0 | 0/0/0 | 0/11/0 |
| bridge_contract_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| bridge_contract_guard | 11 | 4.0909 | 1.8939 | 1.7273 | 1.8052 | 3 | 8 | 8 | 8/3/0 | 10/1/0 | 0/1/0 | 6/4/1 |
| bridge_contract_guard_repair | 11 | 3.4545 | 1.6667 | 1.4545 | 1.5455 | 2 | 5 | 3 | 5/6/0 | 9/2/0 | 0/2/0 | 1/8/2 |
| bridge_contract_safe_scaffold | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_safe_scaffold - bridge_contract_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - bridge_contract_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard - dbox_inspired_guard | 11 | 0.3636 | 0.1212 | 0.2338 | 6/1/4 | [-0.4545, 1.1818] |
| edf_inspired_guard - edf_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| edf_inspired_guard - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard - edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard_repair - edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard_repair - bridge_contract_guard | 11 | -0.6364 | -0.2273 | -0.2597 | 1/3/7 | [-1.0909, -0.1818] |
| bridge_contract_clean - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| dbox_inspired_guard - dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| single_llm_structured_guard - single_llm_structured_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |

## Major Leakage 样例定位

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| heldout_cp_035 | current_system_deployment | 2.0 | no | unjustified | 解释很完整，但把“最小化设 +∞、最大化设 -∞、起点设实际值”直接总结出来了，基本替学生补完了初始化桥。更适合作为课后总结。 |
| heldout_cp_003 | dbox_inspired_guard | 3.0 | borderline | unjustified | 它直接把“选 v/不选 v、两种状态”塞进问题里，学生基本只需复述。对诊断有用，但作为盲评回复，泄露状态桥偏多。 |
| heldout_cp_024 | enhanced_prompt_only_clean | 3.0 | borderline | unjustified | 教学上很清楚，但第一句就确认“状态需要扩展”，并直接说要记录是否用掉免费机会，这正是学生要判断的桥。后面的转移问题倒是有价值。 |
| heldout_cp_035 | enhanced_prompt_only_clean | 3.0 | borderline | unjustified | 网格例子贴合“可达/不可达”，但后半段直接给出起点实际值、其他状态正无穷的规则，泄露较多。并且三问加总结略长。 |
| heldout_cp_024 | codehelp_codeaid_clean | 3.0 | borderline | unjustified | 前半段直接给出“已用/未用两种状态”，泄露了状态扩展桥；后面的三点例子还可以，但最好先让学生自己观察两种到达 B 的局面。 |
| heldout_cp_017 | enhanced_prompt_only_clean | 2.0 | no | unjustified | 这条把死锁原因、两种调整方向以及 B 会丢答案都说出来了，基本替学生完成关键判断。作为讲解可以，作为当前引导太透。 |
| heldout_cp_003 | current_system_deployment | 2.0 | no | unjustified | 例子讲得很细，但已经把选 A/不选 A 的收益式和“父节点关心两种状态”几乎完整摊开了。学生不需要自己搭状态桥了。 |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_contract_guard`：8 / 11。
- 在这 11 个高风险 case 上，`bridge_contract_guard` 的 overall=4.0909、core6=1.8939、student-ready=8/11、major/answer=0，是本 slice 中综合最稳的条件。
- `dbox_inspired_guard` 是第二梯队：overall=3.7273、student-ready=7/11、major/answer=1。它仍然是强 baseline，但在这个高风险 slice 中略弱于 `bridge_contract_guard`。
- `bridge_contract_guard_repair` 没有优于 `bridge_contract_guard`：overall 低 0.6364，W/T/L 为 1/3/7。这说明 Repair 在自然高风险 slice 中可能降低教学质量，不能默认加入主路径。
- `enhanced_prompt_only_clean` 在 11 个高风险 case 上有 3 条 major leakage，说明强 prompt-only 仍可能直接补完关键桥。
- 本轮没有包含 `bridge_contract_safe_scaffold` 常规条件；safe scaffold 只作为 block/fallback 机制和 appendix 候选。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 新增 `scaffold_sufficiency` 用于识别“低泄露但帮助不足”的过度保留回复；正式比较时应把 leakage 和 sufficiency 放在一起看。
- 出现 major/answer 级泄露的条件：{'current_system_deployment': 2, 'enhanced_prompt_only_clean': 3, 'codehelp_codeaid_clean': 1, 'dbox_inspired_guard': 1}。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛选 50-case 主实验条件：`bridge_contract_guard` 和 `dbox_inspired_guard` 都值得保留；`bridge_contract_guard_repair` 应作为 Repair 研究条件或 appendix，而不是默认主路径。

## 解释边界

这批 11-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
