# Fair 20-case Response Blind-Review Analysis (2026-05-11)

This report analyzes the filled coach workbook `coach_response_review_workbook_fair_mini_study_20_20260511_zh_filled.xlsx`. The raw Excel file is not committed; this report uses anonymized response ids merged with the key file.

## Data Completeness

- Reviewed rows: 140, corresponding to `20 cases × 7 systems`.
- Review status: labeled=140.
- Micro-example applicability: applicable=130, not_applicable=10.
- Reviewer confidence: high=127, medium=13.
- Needs discussion: no=114, yes=26.

The 140 rows are not independent samples; they are seven system responses for each of 20 cases. Main analysis should use paired comparisons by `case_id`.

## System Comparison

| System | N | Core-6 mean | Core-7 mean | Overall mean | Would show yes | Would not show | Major leakage | Rank=1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current_system | 20 | 1.675 | 1.555 | 3.35 | 9 | 5 | 7 | 0 |
| single_llm | 20 | 1.592 | 1.540 | 3.35 | 6 | 3 | 1 | 0 |
| single_llm+guard | 20 | 1.808 | 1.765 | 3.95 | 11 | 1 | 1 | 1 |
| single_llm+guard+repair | 20 | 1.742 | 1.671 | 3.75 | 10 | 1 | 0 | 2 |
| bridge_contract | 20 | 1.875 | 1.843 | 4.20 | 12 | 1 | 2 | 5 |
| bridge_contract+guard | 20 | 1.867 | 1.835 | 4.20 | 12 | 2 | 2 | 6 |
| bridge_contract+guard+repair | 20 | 1.875 | 1.857 | 4.40 | 13 | 0 | 1 | 6 |

## Main Findings

1. `bridge_contract + guard + repair` is strongest overall in this blind review: overall quality 4.40, 13/20 directly showable responses, 0 not-show responses, and 6 rank-1 cases.
2. `bridge_contract` and `bridge_contract + guard` are also strong, with 5 and 6 rank-1 cases respectively, suggesting a positive signal from Bridge Contract.
3. Raw `single_llm_structured` is not a weak baseline, but `single_llm + guard` performs better in this human review: overall quality rises from 3.35 to 3.95.
4. `current_system` remains useful as the online baseline, but it has 7 major bridge leakage labels and 5 not-show responses.
5. There is no answer/code leakage in these 140 rows; the main problem is critical bridge leakage, not complete-code leakage.
6. Bridge-oriented micro-example quality is a meaningful dimension: Bridge Contract variants score higher than current_system and raw single-LLM.

## Guard / Repair Interpretation

Guard and Repair help, but they are not complete solutions. `bridge_contract + guard + repair` still has one human-labeled major leakage case (`cp_bridge_010`), showing that runtime guard can miss fully worked micro-examples that reveal the bridge. `single_llm + guard + repair` removes major leakage but still has six minor leakage labels and lower quality than `single_llm + guard`, suggesting that repair may sometimes reduce naturalness or instructional effectiveness.

A safer paper claim is: Guard/Repair improve some high-risk responses, but they need coach-calibrated leakage graders and a dedicated repair stress test.

## Next Steps

1. Treat this 20-case set as dev/regression evidence, not final held-out test results.
2. Build repair stress cases around `cp_bridge_010`, `cp_bridge_001`, `cp_bridge_005`, and `cp_bridge_011`.
3. Update the Leakage Judge rubric to include: fully worked micro-examples can leak the bridge.
4. Freeze prompts and graders before the 50-case held-out test.
5. Future reports should jointly present human response quality, critical bridge leakage, would-show decisions, and latency/call-count metrics.
