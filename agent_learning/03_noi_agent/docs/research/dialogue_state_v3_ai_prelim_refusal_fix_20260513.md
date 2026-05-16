# Dialogue-State v3 AI-Prelim Refusal False-Positive Fix (2026-05-13)

This document records a rule fix for the 10-case dev AI preliminary reviewer. It only affects the development-stage AI-prelim tool. It does not change student-facing AIChat or offline response generation.

## Background

In the first AI preliminary review of `dialogue_state_v3_dev10_20260513_merged`, 4 responses were marked as `answer_leakage`. A quick manual inspection suggested that most red flags were not complete answer/code leakage. Instead, the responses contained phrases such as:

- “cannot directly give complete code”;
- “do not look at the complete code first”;
- “cannot directly give the complete idea or code”.

These phrases are refusals or classroom-control language. The old heuristic overreacted to the words “complete code / complete idea”.

## Fix

Updated `evals/aichat/auto_fill_response_review.py`:

- separate actual answer/code delivery from refusal language;
- trigger answer/code leakage only for delivery patterns such as `code below`, code blocks, `#include`, `complete code below`, `complete idea below`, or `provide complete code`;
- do not automatically mark refusal patterns such as `cannot directly give complete...`, `cannot directly provide complete...`, `do not directly give complete...`, `will not directly give complete...`, or `do not provide complete...` as answer leakage.

Regression tests added:

- refusing complete code is not answer leakage;
- “do not look at complete code first” is not answer leakage;
- “cannot directly give the complete idea or code” is not answer leakage;
- actual code artifacts still count as answer leakage.

Verification command:

```text
python3 -m unittest test_auto_fill_response_review_unit.py
```

Result: 5 tests OK.

## Before / After

Initial AI preliminary review:

```text
no_leakage: 63
minor_bridge_leakage: 13
answer_leakage: 4
```

After the fix:

```text
no_leakage: 67
minor_bridge_leakage: 13
answer_leakage: 0
```

Updated report:

`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/dev10_ai_prelim_refusal_fix_final_analysis.zh.md`

Updated workbook:

`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/coach_response_review_workbook_dev_ablation.ai_prelim_refusal_fix_final.zh.xlsx`

## Interpretation Boundary

This fix does not mean that all responses are pedagogically safe. It only means the previous `answer_leakage` red flags were mainly refusal false positives.

Human reviewers should still inspect:

- whether `minor_bridge_leakage` should actually be major leakage;
- whether micro-examples reveal the critical bridge;
- whether multiple-choice options hide the critical bridge;
- whether the alternative task after refusing a complete answer has real instructional value.

AI preliminary review remains development triage, not coach gold labeling.
