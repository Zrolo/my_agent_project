# Bridge Contract Compact 10-case 人工盲评分析（2026-05-13）

本报告分析用户填写后的按题分 sheet 盲评表：`coach_response_review_workbook_prompt_compression_by_case_20260513_zh_reviewed.xlsx`。本轮是 **dev / prompt compression human review**，用于判断 `bridge_contract_compact_guard` 是否比原长 prompt 更适合进入后续 50-case held-out 候选，不作为正式论文 headline 结果。

## 数据完整性

- 盲评行数：40
- 合并 key 后行数：40
- case 数：10
- condition 数：4
- 缺失评分行数：25（均为 `coach_bridge_oriented_micro_example_score` 在“不适用”行留空，不是核心评分缺失）
- review_status 分布：{'labeled': 40}

## 系统汇总

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 10 | 3.2 | 1.4833 | 1.6 | 1.3286 | 1 | 4 | 2 | 4/4/2 | 5/2/3 | 6/4/0 |
| single_llm_structured_guard | 10 | 3.7 | 1.7 | 1.7 | 1.5286 | 1 | 7 | 6 | 7/3/0 | 8/2/0 | 5/5/0 |
| dbox_inspired_guard | 10 | 4.2 | 1.85 | 1.8 | 1.6572 | 6 | 7 | 7 | 7/3/0 | 9/1/0 | 7/3/0 |
| bridge_contract_compact_guard | 10 | 3.0 | 1.4333 | 1.1 | 1.2714 | 2 | 3 | 2 | 3/5/2 | 8/2/0 | 7/3/0 |

## 关键配对比较

### Overall Quality 差值

| comparison | cases | mean diff | W/T/L | CI95 |
| --- | --- | --- | --- | --- |
| bridge_contract_compact_guard - enhanced_prompt_only_clean | 10 | -0.2 | 4/2/4 | [-1.1, 0.7] |
| bridge_contract_compact_guard - single_llm_structured_guard | 10 | -0.7 | 2/1/7 | [-1.4, 0.1] |
| bridge_contract_compact_guard - dbox_inspired_guard | 10 | -1.2 | 2/2/6 | [-2.3, 0.0] |
| dbox_inspired_guard - enhanced_prompt_only_clean | 10 | 1.0 | 5/3/2 | [-0.1, 2.1] |
| single_llm_structured_guard - enhanced_prompt_only_clean | 10 | 0.5 | 6/1/3 | [-0.2, 1.2] |

### Core6 差值

| comparison | cases | mean diff | W/T/L | CI95 |
| --- | --- | --- | --- | --- |
| bridge_contract_compact_guard - enhanced_prompt_only_clean | 10 | -0.05 | 4/1/5 | [-0.3, 0.2167] |
| bridge_contract_compact_guard - single_llm_structured_guard | 10 | -0.2666 | 2/1/7 | [-0.5, 0.0] |
| bridge_contract_compact_guard - dbox_inspired_guard | 10 | -0.4167 | 2/1/7 | [-0.7333, -0.1] |
| dbox_inspired_guard - enhanced_prompt_only_clean | 10 | 0.3667 | 7/1/2 | [0.0167, 0.7167] |
| single_llm_structured_guard - enhanced_prompt_only_clean | 10 | 0.2167 | 6/1/3 | [-0.0667, 0.5166] |

### Micro7 差值

| comparison | cases | mean diff | W/T/L | CI95 |
| --- | --- | --- | --- | --- |
| bridge_contract_compact_guard - enhanced_prompt_only_clean | 10 | -0.0572 | 4/0/6 | [-0.3, 0.2] |
| bridge_contract_compact_guard - single_llm_structured_guard | 10 | -0.2571 | 3/1/6 | [-0.5, -0.0] |
| bridge_contract_compact_guard - dbox_inspired_guard | 10 | -0.3857 | 2/0/8 | [-0.7143, -0.0429] |
| dbox_inspired_guard - enhanced_prompt_only_clean | 10 | 0.3286 | 6/2/2 | [-0.0143, 0.7] |
| single_llm_structured_guard - enhanced_prompt_only_clean | 10 | 0.2 | 7/1/2 | [-0.0572, 0.4571] |

## 逐题第一名数量

| condition | rank1 count |
| --- | --- |
| bridge_contract_compact_guard | 2 |
| dbox_inspired_guard | 6 |
| enhanced_prompt_only_clean | 1 |
| single_llm_structured_guard | 1 |

## Major / Answer Leakage 定位

| case | condition | label | overall | show | note |
| --- | --- | --- | --- | --- | --- |
| dialogue_v3_008_transition_recurrence_source | enhanced_prompt_only_clean | major_bridge_leakage | 3.0 | borderline | 解释是准确的，但已经把 dp[u][k] 的含义和 dp[v][j] 组合关系都说出来了，基本替学生补完了当前桥。作为讲解可以，作为盲评里的引导回复偏强。 |
| dialogue_v3_012_predicate_check_semantics | enhanced_prompt_only_clean | major_bridge_leakage | 2.0 | no | 例子清楚，但问题是太早把“这是匹配问题”直接告诉学生了。学生这一轮本来应该自己把可行性检查抽象出来，看完基本不用搭这座桥了。 |
| dialogue_v3_043_implementation_boundary | enhanced_prompt_only_clean | major_bridge_leakage | 2.0 | no | 这条太重了，把一个简单的按键计数题讲成状态路径和可行性判断，还直接规定“当前按哪个键、按几次”这种状态。学生可能听懂术语，但会被带到过度建模。 |

## 初步判断

- 本轮人工盲评显示 `dbox_inspired_guard` 是最强条件：overall=4.2、core6=1.85、rank1=6/10、safe_ready=7/10，且没有 major/answer 级泄露。
- `bridge_contract_compact_guard` 没有 major/answer 级泄露，但 overall=3.0、scaffold_sufficiency=1.1、student_ready_pass=3/10，说明它更像“安全但帮助不足”的保守回复。
- 压缩 prompt 的方向比原长 prompt 更干净，但当前 compact 版本还没有达到强 baseline 水平；问题更可能在 Bridge Contract 的“动作规划/脚手架生成方式”，而不是继续往 prompt 里加禁令。
- `enhanced_prompt_only_clean` 出现 3 条 major_bridge_leakage，说明 strong prompt-only 质量未必稳定安全；这支持保留 critical bridge leakage 指标。
- 本轮只包含 10 个 dev cases，正式结论仍需要 50-case held-out、prompt/grader freeze、部分双教练标注和 judge calibration。

## 下一步建议

1. 不要再用原长版 `bridge_contract_guard` 作为主候选；若保留 Bridge Contract 系列，暂以 `bridge_contract_compact_guard` 作为更干净的候选，但必须标记为“帮助不足待修”。
2. 下一轮不要继续增加禁令，而要把 Bridge Contract 的输出动作改得更像“先定位当前子步骤，再给一个足够有用但不补完桥的微任务/问题”。
3. 50-case 主实验应至少保留 `enhanced_prompt_only_clean`、`single_llm_structured_guard`、`dbox_inspired_guard`、`bridge_contract_compact_guard`。如果 Bridge Contract 在 dev 修订后仍明显弱于 DBox，则它应作为消融/机制分析条件，而不是主方法胜负叙事。
