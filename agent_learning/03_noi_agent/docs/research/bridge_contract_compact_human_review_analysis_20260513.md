# Bridge Contract Compact 10-case Human Blind Review Analysis (2026-05-13)

This report analyzes the filled by-case review workbook: `coach_response_review_workbook_prompt_compression_by_case_20260513_zh_reviewed.xlsx`. This is **development / prompt-compression human-review evidence** for deciding whether `bridge_contract_compact_guard` should replace the long Bridge Contract prompt in later held-out experiments. It is not a final headline result.

## Completeness

- Review rows: 40
- Merged rows: 40
- Cases: 10
- Conditions: 4
- Rows with missing score fields: 25 (all are blank `coach_bridge_oriented_micro_example_score` cells for rows marked not applicable, not missing core scores)
- Review status counts: {'labeled': 40}

## System Summary

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 10 | 3.2 | 1.4833 | 1.6 | 1.3286 | 1 | 4 | 2 | 4/4/2 | 5/2/3 | 6/4/0 |
| single_llm_structured_guard | 10 | 3.7 | 1.7 | 1.7 | 1.5286 | 1 | 7 | 6 | 7/3/0 | 8/2/0 | 5/5/0 |
| dbox_inspired_guard | 10 | 4.2 | 1.85 | 1.8 | 1.6572 | 6 | 7 | 7 | 7/3/0 | 9/1/0 | 7/3/0 |
| bridge_contract_compact_guard | 10 | 3.0 | 1.4333 | 1.1 | 1.2714 | 2 | 3 | 2 | 3/5/2 | 8/2/0 | 7/3/0 |

## Key Paired Comparisons

### Overall Quality Difference

| comparison | cases | mean diff | W/T/L | CI95 |
| --- | --- | --- | --- | --- |
| bridge_contract_compact_guard - enhanced_prompt_only_clean | 10 | -0.2 | 4/2/4 | [-1.1, 0.7] |
| bridge_contract_compact_guard - single_llm_structured_guard | 10 | -0.7 | 2/1/7 | [-1.4, 0.1] |
| bridge_contract_compact_guard - dbox_inspired_guard | 10 | -1.2 | 2/2/6 | [-2.3, 0.0] |
| dbox_inspired_guard - enhanced_prompt_only_clean | 10 | 1.0 | 5/3/2 | [-0.1, 2.1] |
| single_llm_structured_guard - enhanced_prompt_only_clean | 10 | 0.5 | 6/1/3 | [-0.2, 1.2] |

### Core6 Difference

| comparison | cases | mean diff | W/T/L | CI95 |
| --- | --- | --- | --- | --- |
| bridge_contract_compact_guard - enhanced_prompt_only_clean | 10 | -0.05 | 4/1/5 | [-0.3, 0.2167] |
| bridge_contract_compact_guard - single_llm_structured_guard | 10 | -0.2666 | 2/1/7 | [-0.5, 0.0] |
| bridge_contract_compact_guard - dbox_inspired_guard | 10 | -0.4167 | 2/1/7 | [-0.7333, -0.1] |
| dbox_inspired_guard - enhanced_prompt_only_clean | 10 | 0.3667 | 7/1/2 | [0.0167, 0.7167] |
| single_llm_structured_guard - enhanced_prompt_only_clean | 10 | 0.2167 | 6/1/3 | [-0.0667, 0.5166] |

### Micro7 Difference

| comparison | cases | mean diff | W/T/L | CI95 |
| --- | --- | --- | --- | --- |
| bridge_contract_compact_guard - enhanced_prompt_only_clean | 10 | -0.0572 | 4/0/6 | [-0.3, 0.2] |
| bridge_contract_compact_guard - single_llm_structured_guard | 10 | -0.2571 | 3/1/6 | [-0.5, -0.0] |
| bridge_contract_compact_guard - dbox_inspired_guard | 10 | -0.3857 | 2/0/8 | [-0.7143, -0.0429] |
| dbox_inspired_guard - enhanced_prompt_only_clean | 10 | 0.3286 | 6/2/2 | [-0.0143, 0.7] |
| single_llm_structured_guard - enhanced_prompt_only_clean | 10 | 0.2 | 7/1/2 | [-0.0572, 0.4571] |

## Rank-1 Counts

| condition | rank1 count |
| --- | --- |
| bridge_contract_compact_guard | 2 |
| dbox_inspired_guard | 6 |
| enhanced_prompt_only_clean | 1 |
| single_llm_structured_guard | 1 |

## Major / Answer Leakage Cases

| case | condition | label | overall | show | note |
| --- | --- | --- | --- | --- | --- |
| dialogue_v3_008_transition_recurrence_source | enhanced_prompt_only_clean | major_bridge_leakage | 3.0 | borderline | 解释是准确的，但已经把 dp[u][k] 的含义和 dp[v][j] 组合关系都说出来了，基本替学生补完了当前桥。作为讲解可以，作为盲评里的引导回复偏强。 |
| dialogue_v3_012_predicate_check_semantics | enhanced_prompt_only_clean | major_bridge_leakage | 2.0 | no | 例子清楚，但问题是太早把“这是匹配问题”直接告诉学生了。学生这一轮本来应该自己把可行性检查抽象出来，看完基本不用搭这座桥了。 |
| dialogue_v3_043_implementation_boundary | enhanced_prompt_only_clean | major_bridge_leakage | 2.0 | no | 这条太重了，把一个简单的按键计数题讲成状态路径和可行性判断，还直接规定“当前按哪个键、按几次”这种状态。学生可能听懂术语，但会被带到过度建模。 |

## Development Interpretation

- The human blind review identifies `dbox_inspired_guard` as the strongest condition in this run: overall=4.2, core6=1.85, rank1=6/10, safe_ready=7/10, and no major/answer leakage.
- `bridge_contract_compact_guard` has no major/answer leakage, but overall=3.0, scaffold_sufficiency=1.1, and student_ready_pass=3/10. It is safer than over-complete responses, but currently under-scaffolds.
- Prompt compression is cleaner than the long Bridge Contract prompt, but the compact version is not yet a strong baseline. The next issue is likely the action-planning/scaffolding behavior of Bridge Contract, not a need for more prohibitions.
- `enhanced_prompt_only_clean` produced 3 major_bridge_leakage labels, showing that strong prompt-only tutoring can still be unsafe under critical-bridge leakage criteria.
- This is a 10-case development review only. Final claims still require 50 held-out cases, prompt/grader freeze, partial double annotation, and judge calibration.

## Recommended Next Steps

1. Do not use the long `bridge_contract_guard` as the main candidate. If the Bridge Contract family is retained, use `bridge_contract_compact_guard` as the cleaner candidate, but mark it as under-scaffolded.
2. Do not add more prohibitions. The next revision should make Bridge Contract first identify the current substep, then ask one useful micro-task/question that does not complete the bridge.
3. The 50-case main study should at least keep `enhanced_prompt_only_clean`, `single_llm_structured_guard`, `dbox_inspired_guard`, and `bridge_contract_compact_guard`. If Bridge Contract remains clearly weaker than DBox after development revision, it should be framed as an ablation/mechanism condition rather than a guaranteed winning architecture.
