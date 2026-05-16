# DBox / Bridge Hybrid Full Fairness 50-case Human Review Memo

Date: 2026-05-15

This memo is based on the local coach-reviewed workbook:

`/Users/kongyouli/Downloads/coach_response_review_workbook_dev_ablation_zh7_human_coach_reviewed.xlsx`

Hidden key:

`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_full_fairness_50_20260514/coach_response_review_workbook_dev_ablation.key.csv`

Full machine-generated analysis:

- `docs/research/dbox_bridge_hybrid_full_fairness_50_human_review_analysis_20260515.zh.md`
- `docs/research/dbox_bridge_hybrid_full_fairness_50_human_review_analysis_20260515.md`

## Data Status

- 50 dev cases.
- 10 anonymous conditions.
- 500 human-reviewed tutor responses.
- Core fields such as overall quality, leakage label, and student-readiness are filled for all 500 rows.
- `coach_bridge_oriented_micro_example_score` is missing for 6 rows, which affects the exact `micro7` mean but not the main overall, core6, leakage, or student-ready findings.

This is still dev/regression evidence, not a formal held-out headline result.

## Key Findings

### 1. DBox-inspired clean is the strongest quality baseline so far

`dbox_inspired_clean`:

- overall: 3.76, highest.
- core6: 1.7067, highest.
- ready: 29/50.
- major/answer leakage: 1/50.

Interpretation: DBox-style decomposition is a strong baseline and should be treated as such in the paper.

### 2. Bridge Contract compact clean has the highest student-ready count

`bridge_contract_compact_clean`:

- overall: 3.62.
- core6: 1.6867.
- ready: 31/50, highest.
- major/answer leakage: 1/50.
- rank1: 10.

Interpretation: Bridge Contract has not failed. It is strong on student-readiness, but still has hard leakage cases and should not be framed as inherently safe.

### 3. Bridge-guided DBox-style guard is the safest stable candidate

`bridge_guided_dbox_style_guard`:

- overall: 3.68.
- ready: 23/50.
- show no: 0/50.
- major/answer leakage: 0/50.
- no/minor/major+answer leakage: 46/4/0.

Interpretation: This hybrid is not the highest-quality condition, but it avoids hard failures. It is a strong candidate for a conservative safety-oriented condition.

### 4. Guard should not be framed as a stable quality-improvement module

Paired results:

- `dbox_inspired_guard - dbox_inspired_clean`: overall -0.08.
- `bridge_contract_compact_guard - bridge_contract_compact_clean`: overall -0.08.
- `enhanced_prompt_only_guard - enhanced_prompt_only_clean`: overall +0.08.

Interpretation: Guard does not reliably improve instructional quality. Its claim should be limited to risk control and deployment safety.

### 5. Repair remains risky

Most notably:

- `enhanced_prompt_only_guard_repair - enhanced_prompt_only_guard`: overall -0.56, W/T/L = 7/18/25.
- `bridge_contract_compact_guard_repair` has the highest sufficiency, but does not improve overall quality.

Interpretation: Repair can reduce leakage in some cases, but may harm naturalness, targeting, or student-readiness. It should stay in same-candidate before/after stress testing rather than the default main method.

## Implication for the Paper

This review does not mean the framework is poor, nor does it prove Bridge Contract wins. It supports a more robust claim:

> CP-MissingBridgeBench reveals the quality, critical-bridge-leakage, and student-readiness trade-offs among strong decomposition baselines, Bridge Contract variants, Guard, and Repair.

The paper should not claim:

> Bridge Contract beats the DBox-inspired baseline.

A stronger claim is:

> DBox-inspired decomposition is a strong baseline. Bridge Contract compact and bridge-guided DBox-style variants provide different quality/safety trade-offs, especially around critical bridge leakage.

## Recommended Conditions for the Next Round

Recommended main-table conditions:

1. `enhanced_prompt_only_clean`: strong prompt baseline.
2. `dbox_inspired_clean`: strongest decomposition baseline by quality.
3. `dbox_inspired_guard`: fair test of Guard applied to DBox.
4. `bridge_contract_compact_clean`: pure Bridge Contract compact generation.
5. `bridge_guided_dbox_style_guard`: safest current hybrid candidate.

Recommended appendix or stress-test conditions:

1. `bridge_contract_compact_guard_repair`: useful for Repair/sufficiency analysis, not a default main method.
2. `dbox_inspired_guard_repair`: useful for testing whether Repair transfers across generators.
3. `enhanced_prompt_only_guard_repair`: useful as a cautionary case showing Repair can hurt quality.

## Required Fixes / Follow-up

1. Fill or explicitly account for the 6 missing `bridge_oriented_micro_example_score` cells.
2. Write a case memo for the 15 major/answer leakage rows, distinguishing:
   - over-complete micro-example;
   - direct critical bridge completion;
   - local implementation/code-slot leakage;
   - post-repair leakage.
3. Do not make broad tutor-prompt changes yet. First fix reporting, case memos, and condition selection.
4. Keep Repair in same-candidate before/after stress testing rather than the default main method.
5. Freeze prompts and graders before the next formal held-out run.

## Bottom Line

This result is not bad for the paper. It moves the study away from “prove our internal framework wins” and toward a stronger framing:

> CP-MissingBridgeBench rigorously evaluates the quality, safety, and student-readiness trade-offs of strong baselines and tutoring harnesses.

The fact that DBox-inspired is strong improves the credibility of the paper, because the benchmark is no longer only comparing against a weak baseline.

