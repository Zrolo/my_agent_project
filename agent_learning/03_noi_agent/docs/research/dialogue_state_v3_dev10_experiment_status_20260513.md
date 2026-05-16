# Dialogue-State v3 10-case Dev Experiment Status (2026-05-13)

This document records the current status of the dialogue-state v3 data experiment. It is a development-stage record, not a formal paper result.

## Goal

This round pauses paper writing and checks whether the dialogue-state v3 dataset can run through the existing offline ablation pipeline and produce coach-reviewable response workbooks.

This round checks whether:

- v3 follow-up cases can enter the `heldout_main` condition set;
- review workbooks include the original problem statement, recent dialogue, context AI reply, current student reply, and target AI response;
- all 8 main experiment conditions produce reviewable responses;
- there are empty responses, missing condition-case pairs, or stage errors;
- AI preliminary review can support development triage.

## Data And Conditions

Input dataset:

`docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`

The dev subset contains 10 cases, covering:

- initial question;
- F1 follows the tutor;
- F2 partially follows;
- F3 follows incorrectly;
- F4 has prerequisite gaps;
- code-attempt turns;
- direct-answer/code risk turns.

Condition set:

`heldout_main`

The run includes 8 conditions:

- `current_system_deployment`
- `enhanced_prompt_only_clean`
- `codehelp_codeaid_clean`
- `dbox_inspired_guard`
- `bridge_inspired_expert_decision_clean`
- `single_llm_structured_guard`
- `bridge_contract_guard`
- `bridge_contract_guard_repair`

## Issues Fixed

The smoke run surfaced two data-pipeline issues. Both have been fixed and covered by unit tests.

1. `context_ai_reply` was not extracted from Chinese recent-dialogue text.
   - Cause: the runner recognized `assistant:` / `ai:` but not Chinese `AI：`.
   - Fix: `run_bridge_offline_eval.py` now accepts Chinese prefixes such as `AI：` and `助手：`.
   - The v3 generator also writes `context_ai_reply` explicitly.

2. The combined JSONL did not preserve problem-source and v3 follow-up metadata.
   - Impact: review workbooks could have empty original problem links, problem statements, followability labels, and prior AI scaffold columns.
   - Fix: runner result rows now preserve problem-source fields and dialogue-state v3 metadata.

Verification command:

```text
python3 -m unittest \
  test_dialogue_state_v3_generation_unit.py \
  test_dialogue_state_v3_validation_unit.py \
  test_bridge_offline_eval_runner_unit.py \
  test_coach_response_review_workbook_unit.py \
  test_coach_response_review_xlsx_unit.py
```

Result: 64 tests OK.

## Outputs

Clean 10-case dev run:

`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/`

Key files:

- `manifest.json`
- `combined_dev_ablation.jsonl`
- `combined_dev_ablation_summary.zh.md`
- `combined_dev_ablation_summary.md`
- `coach_response_review_workbook_dev_ablation.zh.xlsx`
- `coach_response_review_workbook_dev_ablation.key.csv`
- `coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx`
- `dev10_ai_prelim_analysis.zh.md`
- `dev10_ai_prelim_analysis.md`
- `integrity_report.json`

## Integrity Result

Final merged run pack:

```json
{
  "expected_row_count": 80,
  "combined_row_count": 80,
  "final_response_row_count": 80,
  "review_row_count": 80,
  "blocking_reasons": [],
  "warning_reasons": [],
  "analysis_ready": true,
  "headline_ready": true
}
```

Here `headline_ready=true` only means the run pack has no missing rows or empty final responses. It does not mean the run is ready for paper headline claims.

## AI Preliminary Review Boundary

AI preliminary review file:

`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/dev10_ai_prelim_analysis.zh.md`

This AI preliminary review is development triage only. It is not coach gold labeling.

Preliminary signals:

- all 80 responses were auto-filled;
- `single_llm_structured_guard` is strongest under the heuristic AI preliminary review;
- `bridge_contract_guard_repair` slightly improves over `bridge_contract_guard`;
- `dbox_inspired_guard` still has borderline leakage risk;
- major/answer-level risk cases require human review, especially to distinguish true leakage, legitimate local explanation, and heuristic false positives.

Do not report these as formal conclusions. Formal results still require:

- coach blind review;
- 50-case held-out evaluation;
- prompt / grader freeze;
- judge calibration;
- partial double annotation.

## Next Step

Recommended order:

1. Inspect the major/answer-risk examples from the 10-case AI preliminary review and decide whether they are heuristic false positives.
2. Have a coach fill or review `coach_response_review_workbook_dev_ablation.zh.xlsx`, at least for these 10 cases.
3. Use coach feedback to decide whether one final prompt/rubric patch is needed; then freeze prompts and rubrics.
4. Run the 50-case held-out main experiment.
5. Before 50-case formal blind review, do not add more baselines or new modules.
