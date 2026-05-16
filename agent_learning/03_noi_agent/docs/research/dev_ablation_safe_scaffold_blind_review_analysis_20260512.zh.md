# Dev Ablation + Safe Scaffold 10-case 盲评分析（2026-05-12）

本报告分析 10 个 dev cases、12 个匿名系统条件、120 条盲审回复。它用于开发阶段决策和 prompt/regression 修订，不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_dev_ablation_zh3_blind_reviewed.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.key.csv`

- 已标注回复：120 条
- case 数：10 个
- 总体泄露标签：{'minor_bridge_leakage': 53, 'no_leakage': 59, 'major_bridge_leakage': 8}
- 是否愿意给学生看：{'yes': 65, 'no': 15, 'borderline': 40}

## 系统汇总

| condition | n | overall | core6 | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 10 | 3.8 | 1.65 | 1.5857 | 1 | 6 | 3 | 6/3/1 | 3/5/2 |
| socratic_no_answer_clean | 10 | 2.3 | 1.4333 | 1.3 | 0 | 1 | 1 | 1/8/1 | 9/1/0 |
| codehelp_codeaid_clean | 10 | 3.6 | 1.5667 | 1.5143 | 3 | 5 | 3 | 5/4/1 | 6/4/0 |
| dbox_inspired_clean | 10 | 3.2 | 1.5833 | 1.3714 | 0 | 4 | 0 | 4/5/1 | 2/6/2 |
| dbox_inspired_guard | 10 | 3.5 | 1.6666 | 1.4714 | 0 | 7 | 1 | 7/2/1 | 3/6/1 |
| bridge_inspired_expert_decision_clean | 10 | 3.6 | 1.6667 | 1.4714 | 0 | 5 | 2 | 5/5/0 | 4/5/1 |
| single_llm_structured_clean | 10 | 3.7 | 1.7167 | 1.5857 | 0 | 7 | 2 | 7/3/0 | 4/6/0 |
| single_llm_structured_guard | 10 | 3.6 | 1.7333 | 1.5714 | 1 | 5 | 2 | 5/5/0 | 6/4/0 |
| bridge_contract_clean | 10 | 4.0 | 1.7666 | 1.7 | 1 | 8 | 2 | 8/2/0 | 2/8/0 |
| bridge_contract_guard | 10 | 4.4 | 1.8167 | 1.7857 | 1 | 8 | 5 | 8/2/0 | 5/3/2 |
| bridge_contract_guard_repair | 10 | 4.3 | 1.8833 | 1.8428 | 3 | 9 | 4 | 9/1/0 | 5/5/0 |
| bridge_contract_safe_scaffold | 10 | 1.0 | 0.6667 | 0.5714 | 0 | 0 | 0 | 0/0/10 | 10/0/0 |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_safe_scaffold - bridge_contract_clean | 10 | -3.0 | -1.1 | -1.1286 | 0/0/10 | [-3.4, -2.5] |
| bridge_contract_safe_scaffold - bridge_contract_guard | 10 | -3.4 | -1.15 | -1.2143 | 0/0/10 | [-3.8, -2.9] |
| bridge_contract_safe_scaffold - enhanced_prompt_only_clean | 10 | -2.8 | -0.9833 | -1.0143 | 0/0/10 | [-3.3, -2.2] |
| bridge_contract_safe_scaffold - dbox_inspired_guard | 10 | -2.5 | -1.0 | -0.9 | 0/1/9 | [-3.0, -1.8] |
| bridge_contract_guard - dbox_inspired_guard | 10 | 0.9 | 0.15 | 0.3143 | 8/0/2 | [0.2, 1.7] |
| bridge_contract_guard_repair - bridge_contract_guard | 10 | -0.1 | 0.0667 | 0.0571 | 3/4/3 | [-0.7, 0.4] |
| bridge_contract_clean - enhanced_prompt_only_clean | 10 | 0.2 | 0.1167 | 0.1143 | 4/4/2 | [-0.3, 0.6] |
| dbox_inspired_guard - dbox_inspired_clean | 10 | 0.3 | 0.0833 | 0.1 | 3/7/0 | [0.0, 0.6] |
| single_llm_structured_guard - single_llm_structured_clean | 10 | -0.1 | 0.0167 | -0.0143 | 1/7/2 | [-0.4, 0.2] |

## Major Leakage 样例定位

| case | condition | overall | show | coach note |
| --- | --- | --- | --- | --- |
| cp_bridge_010 | enhanced_prompt_only_clean | 3.0 | borderline | 讲解很清楚，但已经把正序为什么错、倒序为什么对、dp 值变化全部算完了；作为提示基本把关键桥说穿。 |
| cp_bridge_005 | bridge_contract_guard | 3.0 | borderline | 例子完整、贴题，但开头直接定义 lazy 是“还没传到子节点的加法”，已经把学生本轮要悟出的语义说穿了。 |
| cp_bridge_005 | dbox_inspired_clean | 3.0 | borderline | “节点本身已经正确更新，子节点还没有得到增量”几乎就是 lazy 语义答案，适合讲解但不太适合盲审里的提示控制。 |
| cp_bridge_002 | bridge_contract_guard | 3.0 | borderline | 长例子贴题且推导完整，但已经替学生判断 mid=3 不可行，还要求给边界方向，泄露和信息量都偏大。 |
| cp_bridge_001 | enhanced_prompt_only_clean | 2.0 | no | 试图让学生比较两种标记方式，但方式 B 直接给到 parent(LCA) 这类关键位置，而且还故意留下“不对怎么办”，整体容易把学生带乱。 |
| cp_bridge_003 | bridge_inspired_expert_decision_clean | 3.0 | borderline | 开头直接给出经典定义“前 i 个物品容量 j 下最大价值”，对学生当前缺的状态桥来说有点说穿了。 |
| cp_bridge_001 | dbox_inspired_guard | 3.0 | borderline | 直接把“u、v +1，LCA 和父亲 -1”这种核心规则摆出来了，虽然内容贴题，但作为本轮提示已经把关键桥补完。 |
| cp_bridge_003 | dbox_inspired_clean | 3.0 | borderline | 这条像把背包状态模板直接搬给学生，相关但偏模板化；学生要自己建立的 dp[i][j] 语义已经被说得太完整。 |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_contract_guard_repair`：9 / 10。
- `bridge_contract_safe_scaffold` 10/10 都没有泄露，但 overall=1.0，10/10 都不建议给学生看；它应作为兜底 fallback / appendix condition，不适合做常规 tutor baseline。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 出现 major/answer 级泄露的条件：{'enhanced_prompt_only_clean': 2, 'dbox_inspired_clean': 2, 'dbox_inspired_guard': 1, 'bridge_inspired_expert_decision_clean': 1, 'bridge_contract_guard': 2}。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛选 50-case 主实验条件：强 prompt、DBox-inspired、DBox+Guard、Bridge Contract、Safe Scaffold 是否值得保留，要看它们在 paired W/T/L 和 student-ready pass 上是否稳定。

## 解释边界

这批 10-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
