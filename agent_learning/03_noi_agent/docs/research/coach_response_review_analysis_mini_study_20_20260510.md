# Mini-Study 20 Response Blind Review Analysis (2026-05-10)

## Data Source

- Filled workbook: `/Users/kongyouli/Downloads/coach_response_review_workbook_mini_study_20_20260510_zh_filled.xlsx`
- Anonymous key: `docs/research/coach_response_review_workbook_mini_study_20_20260510.key.csv`
- Parsed labels: `docs/research/coach_response_review_labels_mini_study_20_20260510.jsonl`
- Review set: 20 cases × 5 system conditions = 100 responses; all 100 rows were labeled.

This remains a single-coach, small-sample blind review. It should be treated as preliminary evidence for Research v1, not as final gold-standard evaluation.

## Overall Results

| System | n | Core avg | With micro avg | Bridge ID | Scaffold fit | Leakage control | Micro-example | Any leakage | Major/answer leakage | Rank-1 count | Mean rank* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `current_system` | 20 | 1.408 | 1.375 | 1.700 | 0.550 | 0.750 | 1.125 | 70% | 55% | 0 | 2.667 |
| `single_llm_structured` | 20 | 1.800 | 1.782 | 1.850 | 1.550 | 1.700 | 1.667 | 25% | 5% | 8 | 1.750 |
| `bridge_contract` | 20 | 1.733 | 1.745 | 1.800 | 1.400 | 1.650 | 1.938 | 30% | 5% | 2 | 2.400 |
| `bridge_contract + guard` | 20 | 1.675 | 1.651 | 1.750 | 1.200 | 1.650 | 1.588 | 25% | 10% | 4 | 2.000 |
| `bridge_contract + guard + repair` | 20 | 1.733 | 1.717 | 1.650 | 1.450 | 1.850 | 1.706 | 15% | 0% | 6 | 1.500 |

\* Mean rank only uses numeric ranks. Rows marked as `tie` are excluded from mean-rank calculation.

## Leakage Labels

| System | no leakage | minor | major | answer |
|---|---:|---:|---:|---:|
| `current_system` | 6 | 3 | 11 | 0 |
| `single_llm_structured` | 15 | 4 | 1 | 0 |
| `bridge_contract` | 14 | 5 | 1 | 0 |
| `bridge_contract + guard` | 15 | 3 | 2 | 0 |
| `bridge_contract + guard + repair` | 17 | 3 | 0 | 0 |

## Main Findings

1. `current_system` is a strong negative baseline: it has the lowest core score (1.408), the highest major/answer leakage rate (55%), and zero rank-1 wins. This suggests that the current online AIChat prompt/self-reported-level gate does not sufficiently prevent critical bridge leakage.
2. `single_llm_structured` is surprisingly strong in this batch: it has the highest core score (1.800), the most rank-1 wins (8/20), and only 5% major/answer leakage. The paper must therefore include single-LLM structured prompting as a serious baseline.
3. `bridge_contract` has the highest bridge-oriented micro-example score (1.938), suggesting that the contract helps the tutor produce examples centered on the missing bridge. However, it wins only 2/20 cases, so a contract alone is not enough to maximize overall response quality.
4. `bridge_contract + guard` does not consistently outperform `bridge_contract`; its major/answer leakage rate is 10%. Current guard behavior should not yet be interpreted as a reliable quality improver.
5. `bridge_contract + guard + repair` has the best leakage-control profile: 0% major/answer leakage, 15% any leakage, and 6 rank-1 wins. However, `repair_applied_count=0` in this run, so the improvement cannot be attributed to Repair itself.

## Qualitative Findings

### 1. The current system often completes the key bridge

Coach notes repeatedly flag direct exposure of DP state, recurrence, feasibility judgments, and union-find code mapping. These are critical bridge leaks rather than merely full-code leaks.

### 2. Over-conservatism also hurts quality

Several weak responses simply asked the student for a problem ID or code line even when the student had already stated a clear learning bottleneck. This happened in cases such as reverse iteration in 0/1 knapsack and union-find operation mapping.

Follow-up inspection showed that this was not an intentional system-prompt requirement to always request a problem ID or code line. It was a hard-gate fallback artifact: rule-level misclassification lowered the turn to L1, and `enforce_level_gate()` replaced the candidate response with a fixed generic L1 fallback. Two concrete triggers were identified: same-focus contrast questions being treated as `multi_question`, and “the problem says..., I know..., but I do not know...” turns being treated as mere problem restatement.

### 3. Bridge Contract improves micro-example orientation

The `bridge_contract` condition received the strongest micro-example score. Good responses usually stated the relation to observe, gave a small near-domain example, and prompted a transferable rule.

### 4. Guard/Repair is not yet validated

No actual repair was applied in this mini-study. A separate Repair stress test is needed using deliberately leaky candidates.

## Implications For The Paper

This blind review supports three research claims:

1. Critical bridge leakage is a necessary metric because the current system mainly fails by exposing intermediate reasoning bridges, not only by giving complete code.
2. Single-LLM structured prompting must be a formal baseline because it performs strongly in this batch.
3. Bridge-oriented micro-example quality should be part of the response rubric because it distinguishes local fill-in tasks from transferable bridge understanding.

## Next Steps

1. Expand to 50 seed cases and double-label at least 15 cases to reduce single-coach subjectivity.
2. Run a dedicated Repair stress test with intentionally leaky candidates.
3. Keep `single_llm_structured` as a formal baseline.
4. Improve current-system leakage and hard-gate fallback misclassification through offline patching, not live prompt mutation.
