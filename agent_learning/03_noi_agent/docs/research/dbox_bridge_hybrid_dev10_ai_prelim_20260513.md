# DBox/Bridge Hybrid 10-case AI Preliminary Review Report (2026-05-13)

This report summarizes the `dbox_bridge_hybrid` 10-case development ablation. It is for development triage only. It is not a held-out result and not a coach gold label.

## Setup

- Data: first 10 rows from `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`.
- Generation model: `deepseek_flash`, `chat_thinking_mode=disabled`.
- Judges: default `deepseek`, thinking disabled.
- Raw results: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/combined_dev_ablation.jsonl`.
- Review workbook: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx`.
- Analysis report: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/ai_prelim_analysis.md`.

## Conditions

| condition | Purpose |
| --- | --- |
| `enhanced_prompt_only_clean` | Strong prompt-only baseline without Bridge Judge or Guard. |
| `dbox_inspired_clean` | DBox-inspired single-turn step-tree-style decomposition baseline without Guard. |
| `dbox_inspired_guard` | DBox-inspired baseline plus Leakage Guard. |
| `bridge_contract_compact_guard` | Current compact Bridge Contract plus Guard. |
| `bridge_guided_dbox_style_guard` | New hybrid: Bridge Contract supplies diagnosis/forbidden content, while DBox-style decomposition supplies the visible scaffold. |

## AI Preliminary Summary

| condition | n | overall | core6 | sufficiency | micro7 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `enhanced_prompt_only_clean` | 10 | 3.8 | 1.95 | 2.0 | 1.7571 | 8 | 8 | 8/2/0 | 8/2/0 |
| `dbox_inspired_clean` | 10 | 3.4 | 1.8667 | 1.8 | 1.6714 | 6 | 6 | 6/2/2 | 6/2/2 |
| `dbox_inspired_guard` | 10 | 3.5 | 1.9 | 1.9 | 1.7285 | 6 | 6 | 6/3/1 | 6/3/1 |
| `bridge_contract_compact_guard` | 10 | 4.0 | 2.0 | 2.0 | 1.8428 | 10 | 10 | 10/0/0 | 10/0/0 |
| `bridge_guided_dbox_style_guard` | 10 | 3.9 | 1.9833 | 2.0 | 1.8285 | 9 | 9 | 9/1/0 | 9/1/0 |

## Latency And Stability

| condition | LLM calls/turn | P50 latency |
| --- | ---: | ---: |
| `enhanced_prompt_only_clean` | 1.0 | 7.45s |
| `dbox_inspired_clean` | 1.0 | 3.96s |
| `dbox_inspired_guard` | 3.4 | 14.99s |
| `bridge_contract_compact_guard` | 3.0 | 11.35s |
| `bridge_guided_dbox_style_guard` | 3.6 | 17.44s |

All 50 merged rows have final responses. `bridge_guided_dbox_style_guard` had one Leakage Judge timeout; the response is still reviewable, but the timeout should be recorded as a stability risk.

## Preliminary Takeaways

1. `dbox_inspired_clean` is a viable no-Guard DBox-inspired baseline, but it is not the strongest condition in this AI preliminary review: it has 2 major bridge leakage cases and 6/10 student-ready pass.
2. `dbox_inspired_guard` slightly improves over `dbox_inspired_clean`, but still has 1 major bridge leakage case. This makes the guard-instrumented decomposition variant worth keeping, but the difference should not be interpreted as Guard rewriting or repairing the final output.
3. `bridge_contract_compact_guard` is best in this AI preliminary review: overall 4.0, safe_ready 10/10, and no major/answer leakage. This supports keeping compact Bridge Contract plus Guard as a main experiment candidate.
4. `bridge_guided_dbox_style_guard` is close to `bridge_contract_compact_guard`, but slower, with 1 minor leakage and 1 Leakage Judge timeout. It is better treated as an appendix/dev candidate unless coach review shows stable gains.
5. These findings are only for development decisions. Formal claims require coach blind review, 50-case held-out evaluation, partial double annotation, and Judge calibration.

## Impact On Next Experiments

- Keep DBox original-style no-Guard baseline as `dbox_inspired_clean` to test whether DBox-style decomposition alone is sufficient.
- Keep `dbox_inspired_guard` in the main comparison as the fair guard-instrumented decomposition baseline.
- Keep `bridge_contract_compact_guard` as the current main method candidate.
- Do not expand `bridge_guided_dbox_style_guard` into the default path unless human review shows stable improvement over compact Bridge Contract.
