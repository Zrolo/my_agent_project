# Fair 20-case Paired Analysis 2026-05-11

This report treats the 20 cases as paired samples rather than treating the 140 response rows as independent observations. It is development / pilot evidence, not a final held-out result.

## System Summary

| System | Overall Quality Mean | student_ready_pass | student_ready_safe_pass | rank=1 | major/answer leakage | repair_applied |
| --- | --- | --- | --- | --- | --- | --- |
| current_system | 3.35 | 9 | 9 | 0 | 7 | 0 |
| single_llm | 3.35 | 6 | 6 | 0 | 1 | 0 |
| single_llm+guard | 3.95 | 11 | 11 | 1 | 1 | 0 |
| single_llm+guard+repair | 3.75 | 10 | 10 | 2 | 0 | 3 |
| bridge_contract | 4.2 | 12 | 12 | 5 | 2 | 0 |
| bridge_contract+guard | 4.2 | 12 | 12 | 6 | 2 | 0 |
| bridge_contract+guard+repair | 4.4 | 13 | 13 | 6 | 1 | 1 |

## Key Paired Comparisons (Overall Quality)

| Comparison | Mean Diff | Bootstrap 95% CI | Win/Tie/Loss | Paired Cases |
| --- | --- | --- | --- | --- |
| bridge_contract+guard+repair - single_llm+guard | 0.45 | [-0.05, 0.95] | 8/9/3 | 20 |
| bridge_contract+guard+repair - single_llm+guard+repair | 0.65 | [0.25, 1.05] | 12/5/3 | 20 |
| bridge_contract - single_llm | 0.85 | [0.2, 1.4] | 13/4/3 | 20 |
| bridge_contract+guard+repair - current_system | 1.05 | [0.65, 1.45] | 14/6/0 | 20 |

## Interpretation Boundary

- The higher score of `single_llm+guard` over `single_llm` should not be attributed to Guard itself; in the current guard-only condition, the guard did not modify the final response, so the difference is more plausibly run-to-run generation variance.
- The causal effect of Guard/Repair requires a paired before/after ablation that reuses the same candidate response.
- The most stable pilot signal is that Bridge Contract variants are stronger on case-level preference and student-ready metrics, while critical bridge leakage remains unsolved.
