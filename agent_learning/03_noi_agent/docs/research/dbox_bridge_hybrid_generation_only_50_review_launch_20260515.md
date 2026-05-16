# DBox / Bridge Hybrid 50-case Review Launch Checklist

This run is a development / regression-stage 50-case generation-only evaluation, not a final paper headline result. Its goal is to decide which conditions should enter the later frozen held-out evaluation and to locate the main failure modes of Bridge Contract, DBox-inspired scaffolding, and Guard.

## Generation Outputs

- Clean run pack: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged`
- Manifest: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/manifest.json`
- Combined JSONL: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/combined_dev_ablation.jsonl`
- Chinese summary: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/combined_dev_ablation_summary.zh.md`
- English summary: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/combined_dev_ablation_summary.md`
- Integrity report: `docs/research/dbox_bridge_hybrid_generation_only_50_integrity_20260515.zh.md`

Integrity status:

- 50 cases x 5 conditions = 250 rows
- Non-empty final responses: 250 / 250
- Stage errors: 0
- `[LEVEL:...]` internal tag hits: 0
- `heldout_v4_luogu_018 x bridge_guided_dbox_style_guard` was fixed via targeted rerun and merged

## Conditions

1. `enhanced_prompt_only_clean`
2. `dbox_inspired_clean`
3. `dbox_inspired_guard`
4. `bridge_contract_compact_guard`
5. `bridge_guided_dbox_style_guard`

`bridge_guided_dbox_style_guard` is the current hybrid candidate: it keeps Bridge missing-bridge / forbidden-content control signals while adopting a DBox-style current-substep scaffold.

## Human Blind Review File

Give coaches this file:

- `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_dev_ablation.zh.xlsx`

Do not give coaches this file:

- `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_dev_ablation.key.csv`

The key file contains the real condition labels and should not be visible during blind review.

## AI Preliminary Review Files

AI-prelim filled workbook:

- `docs/research/coach_response_review_workbook_dbox_bridge_hybrid_generation_only_50_20260515.ai_prelim.zh.xlsx`

AI-prelim labels:

- `docs/research/coach_response_review_labels_dbox_bridge_hybrid_generation_only_50_20260515.ai_prelim.csv`
- `docs/research/coach_response_review_labels_dbox_bridge_hybrid_generation_only_50_20260515.ai_prelim.jsonl`

AI-prelim analysis reports:

- `docs/research/dbox_bridge_hybrid_generation_only_50_ai_prelim_analysis_20260515.zh.md`
- `docs/research/dbox_bridge_hybrid_generation_only_50_ai_prelim_analysis_20260515.md`

Important: AI-prelim labels are heuristic dev triage only. They are not coach gold labels and should not be used as paper results.

## Main AI-prelim Signals

The AI-prelim pass suggests:

- `bridge_guided_dbox_style_guard` has the highest student-ready pass: 41 / 50.
- `bridge_guided_dbox_style_guard` also currently has the highest overall / core6 / micro7 scores.
- `bridge_contract_compact_guard` does not exceed `dbox_inspired_guard` in this preliminary pass.
- All conditions still have minor / major / answer-risk flags that require human review.
- Guard should not be interpreted from means alone; high-risk rows need case-level inspection.

The next review should focus on:

1. Whether `bridge_guided_dbox_style_guard` is actually more missing-bridge-aware than plain DBox.
2. Whether `bridge_contract_compact_guard` is too mechanical or contract-bound.
3. Whether DBox-style scaffolding scores better because it feels closer to real tutoring dialogue.
4. Whether static risk flags over-detect worked examples and filled traces.
5. Whether Guard rewrites actually reduce leakage or only make responses more conservative.

## Suggested Human Review Order

Coaches should avoid reviewing the 250 rows as a flat list. A better workflow:

1. For each case, compare the 5 anonymous responses and fill `coach_preference_rank`.
2. Then label `would_show_to_student`, `leakage_label`, and `overall_quality_score`.
3. Finally add `coach_notes` only for boundary cases, especially leakage, over-withholding, or context mismatch.

Priority rows:

- Rows AI-prelim labeled as `major_bridge_leakage` or `answer_leakage`.
- Rows with `show=no` or `show=borderline`.
- Cases where the 5 conditions differ strongly.
- Cases where `bridge_contract_compact_guard` and `bridge_guided_dbox_style_guard` disagree in ranking.

## Next Step

1. Human coach completes the blind-review workbook.
2. Merge human labels with the hidden key file.
3. Compare:
   - `dbox_inspired_guard` vs `dbox_inspired_clean`
   - `bridge_contract_compact_guard` vs `dbox_inspired_guard`
   - `bridge_guided_dbox_style_guard` vs `dbox_inspired_guard`
   - `bridge_guided_dbox_style_guard` vs `bridge_contract_compact_guard`
4. Decide whether `bridge_guided_dbox_style_guard` should enter the formal 50-case held-out main table.
