# DBox / Bridge Hybrid v4 50-case Generation-only Integrity 20260514

中文版本：`dbox_bridge_hybrid_generation_only_v4_50_integrity_20260514.zh.md`

This report records a 50-case × 5-condition generation-only run on `bridgebench_cp_heldout_v4_50_draft.jsonl`. It checks generation completeness, context fields, and automatic risk diagnostics only. It is not a paper-level quality result.

## Input and Output

- Input data: `docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl`
- Final merged output directory: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged`
- Review workbook: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/coach_response_review_workbook_dev_ablation.zh.xlsx`
- Key file: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/coach_response_review_workbook_dev_ablation.key.csv`
- Conditions: 5
- Cases: 50
- Expected responses: 250
- Final responses: 250

The review workbook includes `problem_statement`, `context_ai_reply`, `recent_dialogue`, and `response_text`, so coaches can see the original problem, contextual AI reply, recent dialogue, and the target response to score.

## Conditions

| condition | role |
| --- | --- |
| `enhanced_prompt_only_clean` | strong prompt-only baseline |
| `dbox_inspired_clean` | DBox-inspired no-Guard baseline |
| `dbox_inspired_guard` | DBox-inspired + Leakage Guard baseline |
| `bridge_contract_compact_guard` | current Bridge Contract main candidate |
| `bridge_guided_dbox_style_guard` | hybrid dev / appendix candidate |

## Integrity Result

Final merged integrity check:

- `expected_row_count=250`
- `combined_row_count=250`
- `final_response_row_count=250`
- `review_row_count=250`
- `missing_pairs=[]`
- `duplicate_pairs=[]`
- `empty_final_response_rows=[]`
- `stage_warning_rows=[]`
- `analysis_ready=true`

The original run had 12 empty responses in `bridge_guided_dbox_style_guard`: five from `hint_level must be general_question` schema errors and seven from `APIConnectionError`. Targeted rerun recovered 11 rows; `heldout_v4_luogu_029` needed a second targeted rerun with more retries. This indicates that the hybrid condition is less structurally stable than the other four conditions and is better treated as appendix/dev analysis rather than a core main-table condition.

## Automatic Diagnostics

The following numbers come from runtime Guard and static lint. They are development diagnostics, not coach review or paper-level conclusions.

| condition | p50 latency | p95 latency | avg LLM calls | runtime critical leakage | final static risk |
| --- | ---: | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 16.23s | 39.87s | 1.00 | N/A | 0.36 |
| `dbox_inspired_clean` | 11.99s | 43.31s | 1.04 | N/A | 0.26 |
| `dbox_inspired_guard` | 17.33s | 37.61s | 3.02 | 0.10 | 0.28 |
| `bridge_contract_compact_guard` | 15.31s | 25.59s | 3.02 | 0.06 | 0.26 |
| `bridge_guided_dbox_style_guard` | 22.28s | 73.53s | 3.26 | 0.10 | 0.30 |

Overall automatic diagnostics:

- runtime leakage rate: 0.287
- runtime critical bridge leakage rate: 0.087
- answer/code leakage rate: 0.0
- final static risk rate: 0.292
- total p50 latency: 16.36s
- total p95 latency: 43.43s

## Interpretation Boundary

- This is not human coach review and must not be used as a headline result.
- No-Guard conditions do not have runtime leakage-judge metrics, so their runtime leakage fields are N/A; compare them through static lint and later coach review.
- Guard conditions record intervention signals, but this run does not include Repair conditions and cannot prove Repair effects.
- `bridge_contract_compact_guard` has lower automatic critical leakage than `dbox_inspired_guard`, but this must be verified by coach review, especially for over-complete micro-examples and definition-first leakage.

## Next Steps

1. Run AI preliminary review on the 250 responses for development screening only.
2. Keep an unfilled coach blind-review workbook for human review.
3. For formal Guard / Repair claims, run a separate fair matrix including `enhanced_prompt_only_guard`, `enhanced_prompt_only_guard_repair`, `dbox_inspired_guard_repair`, `bridge_contract_compact_clean`, and `bridge_contract_compact_guard_repair`.
4. Do not put `bridge_guided_dbox_style_guard` in the core main table unless coach review reverses the current stability concern.
