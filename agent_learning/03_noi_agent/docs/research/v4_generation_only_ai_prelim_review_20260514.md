# v4 Generation-only AI Preliminary Review 20260514

中文版本：`v4_generation_only_ai_prelim_review_20260514.zh.md`

This report summarizes the development-stage AI preliminary review for `dbox_bridge_hybrid_generation_only_v4_50_20260514_merged`. It is for risk screening and coach-review prioritization only. It is not coach gold, does not replace human coach blind review, and must not be used as a paper headline result.

## Inputs

- Run directory: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged`
- Raw responses: `combined_dev_ablation.jsonl`
- Unfilled review workbook: `coach_response_review_workbook_dev_ablation.zh.xlsx`
- AI-filled review workbook: `coach_response_review_workbook_dev_ablation.ai_prelim_gpt55_xhigh.zh.xlsx`
- AI labels: `ai_prelim_gpt55_xhigh_labels.jsonl`
- AI analysis: `ai_prelim_gpt55_xhigh_analysis.zh.md`

## Integrity

- AI labels: 250 rows
- AI-filled CSV: 250 rows
- unique `(case_id, condition_id)`: 250
- coverage: 50 cases × 5 conditions

## Main AI-prelim Results

| condition | overall | core6 | ready | safe_ready | leak no/minor/major+answer | show yes/border/no | burden low/medium/high |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `enhanced_prompt_only_clean` | 3.04 | 1.63 | 12 | 10 | 25/14/11 | 12/27/11 | 0/34/16 |
| `dbox_inspired_clean` | 3.44 | 1.81 | 27 | 25 | 30/15/5 | 27/18/5 | 14/35/1 |
| `dbox_inspired_guard` | 3.38 | 1.79 | 25 | 22 | 28/16/6 | 25/19/6 | 22/27/1 |
| `bridge_contract_compact_guard` | 3.56 | 1.8467 | 29 | 28 | 39/11/0 | 29/20/1 | 8/35/7 |
| `bridge_guided_dbox_style_guard` | 3.62 | 1.8833 | 34 | 33 | 41/6/3 | 34/12/4 | 8/40/2 |

AI-prelim observations:

- `bridge_contract_compact_guard` has no major / answer leakage in the AI prelim review, but has many medium/high-burden responses; coaches should decide whether it is safe but too demanding.
- `bridge_guided_dbox_style_guard` has the highest ready count, but still has three major-risk responses and showed structured-output instability during generation. Treat it as a dev / appendix candidate.
- `enhanced_prompt_only_clean` has higher major-risk and high-burden counts in the AI prelim review, mostly from complete micro-examples, complete proofs, or direct boundary-update hints.
- These numbers are development triage only. Formal interpretation requires human coach blind review.

## High-risk Human Review Pack

The selection rule is:

```text
case selected if any response has AI-prelim major/answer/code leakage or would_show_to_student=no
```

Outputs:

- High-risk blind review workbook: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/coach_response_review_workbook_v4_high_risk_case_pack_blind.zh.xlsx`
- High-risk key: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/coach_response_review_workbook_v4_high_risk_case_pack_blind.key.csv`
- High-risk summary: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/v4_high_risk_case_pack_summary.json`

Pack size:

- selected case count: 19
- selected row count: 95
- risk response count: 27

Recommended coach-review priorities:

1. Rows AI-labeled as major / no-show, to verify whether they are true critical bridge leaks.
2. Medium/high-burden `bridge_contract_compact_guard` rows, to judge whether they are safe but too heavy.
3. High-ready but major-risk `bridge_guided_dbox_style_guard` rows, to decide whether the hybrid should remain appendix-only.
4. Factual-error rows such as `heldout_v4_luogu_046 / bridge_contract_compact_guard`, to use as prompt / regression negatives.

## Next Step

Generation-only and AI preliminary review are now complete. The next step should be human coach review of the high-risk pack, not immediate full 250-row review. After the high-risk review, decide whether to:

- continue to full 250-row coach blind review;
- remove or downgrade `bridge_guided_dbox_style_guard`;
- add the fair Guard / Repair matrix;
- patch prompts and re-enter development, rather than proceeding to formal held-out evaluation.
