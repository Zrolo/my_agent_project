# DBox/Bridge Hybrid 10-case Human Coach Review Report (2026-05-14)

This report is based on the human coach revision of `coach_response_review_workbook_dev_ablation_ai_prelim_zh_human_reviewed.xlsx`. It is development evidence only and not a formal 50-case held-out result.

## Inputs And Analysis Files

- Human-reviewed workbook: `/Users/kongyouli/Downloads/coach_response_review_workbook_dev_ablation_ai_prelim_zh_human_reviewed.xlsx`
- Anonymous key: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/coach_response_review_workbook_dev_ablation.key.csv`
- Output labels: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/human_reviewed_labels.jsonl`
- Output analysis: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/human_reviewed_analysis.md`

## Human Review Summary

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `enhanced_prompt_only_clean` | 10 | 3.0 | 1.5167 | 1.6 | 1.3857 | 2 | 3 | 3 | 4/5/1 | 5/3/2 |
| `dbox_inspired_clean` | 10 | 3.3 | 1.6667 | 1.4 | 1.4428 | 3 | 4 | 2 | 5/5/0 | 6/4/0 |
| `dbox_inspired_guard` | 10 | 3.1 | 1.6333 | 1.4 | 1.4143 | 1 | 3 | 2 | 3/7/0 | 7/2/1 |
| `bridge_contract_compact_guard` | 10 | 3.4 | 1.6 | 1.4 | 1.4143 | 4 | 5 | 3 | 5/4/1 | 6/4/0 |
| `bridge_guided_dbox_style_guard` | 10 | 2.4 | 1.35 | 0.8 | 1.2572 | 0 | 0 | 0 | 1/7/2 | 7/2/1 |

## Main Differences From AI Preliminary Review

The AI preliminary review was generally optimistic, especially for `bridge_guided_dbox_style_guard` and `bridge_contract_compact_guard`.

| condition | AI overall | Human overall | AI safe_ready | Human safe_ready | Main change |
| --- | ---: | ---: | ---: | ---: | --- |
| `bridge_contract_compact_guard` | 4.0 | 3.4 | 10/10 | 3/10 | Human review found 4 minor leakage cases and several borderline responses. |
| `bridge_guided_dbox_style_guard` | 3.9 | 2.4 | 9/10 | 0/10 | Human review judged the hybrid responses as under-scaffolded/template-like and sometimes leaking. |
| `dbox_inspired_clean` | 3.4 | 3.3 | 6/10 | 2/10 | Overall quality stayed similar, but safe_ready dropped substantially. |
| `dbox_inspired_guard` | 3.5 | 3.1 | 6/10 | 2/10 | Guard did not reliably improve the DBox baseline. |
| `enhanced_prompt_only_clean` | 3.8 | 3.0 | 8/10 | 3/10 | Human review identified 2 major leakage cases missed by AI preliminary review. |

## Key Observations

1. `bridge_contract_compact_guard` remains the strongest main-method candidate in this 10-case dev review, but the margin is small: overall 3.4, ready 5/10, safe_ready 3/10.
2. `dbox_inspired_clean` is a strong baseline and should remain in the main experiment. It had no major leakage in this human review.
3. `dbox_inspired_guard` did not reliably outperform `dbox_inspired_clean`, so Guard benefits need larger-sample or same-candidate validation.
4. `bridge_guided_dbox_style_guard` should not enter the main table. It had 0/10 ready and 0/10 safe_ready under human review.
5. Human review is more sensitive than AI preliminary review to two failures: responses that look safe but are not helpful enough, and micro-examples that quietly complete the critical bridge.

## Major Leakage Examples

| case | condition | Human note summary |
| --- | --- | --- |
| `heldout_v2_luogu_004` | `enhanced_prompt_only_clean` | Directly exposes the two state dimensions, leaving only a fill-in task for the student. |
| `heldout_v2_luogu_005` | `enhanced_prompt_only_clean` | Gives too much of the mapping function, edge legality, and node mapping bridge. |
| `heldout_v2_luogu_009` | `bridge_guided_dbox_style_guard` | Provides state definition, initialization, child dp, and group-knapsack merging, turning discovery into substitution. |
| `heldout_v2_luogu_005` | `dbox_inspired_guard` | Reveals the core state relation that tree nodes correspond to graph nodes. |

## Impact On Experiment Design

Recommended main-table candidates for the 50-case held-out study:

- `enhanced_prompt_only_clean`
- `dbox_inspired_clean`
- `dbox_inspired_guard`
- `bridge_contract_compact_guard`

Do not put `bridge_guided_dbox_style_guard` in the main table for now. It can remain as an appendix or error-analysis condition showing that simply combining Bridge Contract with DBox-style decomposition does not automatically improve tutoring quality.

## Next Steps

1. Do not keep heavily tuning prompts from this 10-case dev result; only record narrow regression risks.
2. Use this human review as development evidence for condition selection.
3. Before scaling up, verify the 50-case dataset composition and problem/context completeness.
4. The formal 50-case result must rely on coach blind review; AI preliminary review should remain a triage tool only.
