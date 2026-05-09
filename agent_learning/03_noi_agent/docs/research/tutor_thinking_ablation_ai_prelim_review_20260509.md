# Tutor Thinking Ablation AI Preliminary Review 2026-05-09

Status: AI preliminary review only. This is not coach gold and must not be used as final paper evidence without human review.

Chinese version: `docs/research/tutor_thinking_ablation_ai_prelim_review_20260509.zh.md`

## Summary

| Thinking mode | Rows | Avg total score | Avg leakage-control score | Any leakage | Major/answer leakage | Pairwise wins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `enabled` | 3 | 9.667 | 0.667 | 3/3 | 1/3 | 2/3 |
| `disabled` | 3 | 10.000 | 1.333 | 1/3 | 1/3 | 1/3 |

## Interpretation

- `thinking=disabled` is much faster in the latency smoke, but this AI preliminary review does not justify promoting it directly to the online default.
- Case-level preference is mixed: enabled wins on the tree-difference and DP-state cases, while disabled wins on the binary-search check case.
- The strongest concern is critical-bridge leakage. Disabled has one major leak on the DP-state case; enabled has one major leak on the binary-search check case and minor leakage on the other two cases.
- Treat this file as a debugging aid for the next human coach review, not as adjudicated gold.

## Per-Case Preliminary Review

| Case | Thinking | Total score | Leakage label | Pairwise rank | Short judgment |
| --- | --- | ---: | --- | ---: | --- |
| `cp_bridge_001` | enabled | 11 | `minor_bridge_leakage` | 1 | Better targets the tree-difference endpoint/LCA marking gap, but endpoint +1 is a strong clue. |
| `cp_bridge_001` | disabled | 9 | `no_leakage` | 2 | Safer but weaker; it may lead the student to simply mark every node on the path. |
| `cp_bridge_002` | enabled | 7 | `major_bridge_leakage` | 2 | Gives the check true/false direction directly and drifts into boundary update. |
| `cp_bridge_002` | disabled | 12 | `no_leakage` | 1 | Uses a concrete mid and asks the student to decide true/false; strong single-focus scaffold. |
| `cp_bridge_003` | enabled | 11 | `minor_bridge_leakage` | 1 | Uses a table to make the student explain a DP cell; good fit, but row/column semantics are heavily hinted. |
| `cp_bridge_003` | disabled | 9 | `major_bridge_leakage` | 2 | Fast and clear, but directly states the core `dp[j]` semantics. |

## Output Files

- Filled blind-style CSV: `docs/research/coach_response_review_workbook_deepseek_flash_thinking_smoke3.ai_prelim.csv`
- Keyed AI preliminary CSV: `docs/research/coach_response_review_workbook_deepseek_flash_thinking_smoke3.ai_prelim.keyed.csv`
