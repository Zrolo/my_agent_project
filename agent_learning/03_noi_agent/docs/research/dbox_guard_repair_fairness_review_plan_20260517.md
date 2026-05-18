# DBox Guard+Repair Fairness Add-On Review Plan 20260517

## Current Status

The `dbox_inspired_guard_repair` generation package exists:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/
```

Generation data exists, but no completed human-review label JSONL was found. Therefore DBox+Repair cannot be added to the main result table yet, and we cannot claim that Bridge+Repair beats all fair repair-enabled baselines.

## Generation Summary

| metric | value |
| --- | ---: |
| generated_rows | 50 |
| repair_applied | 17 |
| repair_still_leaks | 1 |
| post_repair_rewrite_or_block | 4 |
| final_static_risk | 19 |

Supplementary review candidate files:

- `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_candidate_list_20260517.xlsx`
- `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_candidate_list_20260517.csv`

Current candidate count: 20.

Coach-facing direct-fill workbook:

- `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.zh.xlsx`
- hidden key: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.key.csv`
- source review CSV: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.csv`

This workbook uses `盲评表` as the only fill-in entry point; downstream summarization reads `盲评表`. Do not send the internal candidate list or hidden key to coaches.

## Minimal Review Plan

Best case: review all 50 `dbox_inspired_guard_repair` cases.

If time is limited: review 15-20 headline-sensitive cases, prioritizing:

1. Cases where DBox clean / DBox guard had leakage.
2. Cases where DBox guard and Bridge repair are close or conclusion-sensitive.
3. Cases with student-ready flips.
4. `main_scaffold_eval` cases affecting headline comparisons.
5. Cases where DBox repair fired, post-repair was still flagged, or final static risk is high.

## Review Design

1. Coaches fill only the yellow columns in `盲评表` inside `dbox_guard_repair_fairness_review20_workbook_20260517.zh.xlsx`.
2. Show only the final response; hide the `dbox_inspired_guard_repair` condition name.
3. Use the same dialogue-state v3 rubric: overall, would-show, leakage label, student burden, notes.
4. Show the same case-specific rubric as the main experiment.
5. Compare:
   - `dbox_inspired_guard`
   - `dbox_inspired_guard_repair`
   - `bridge_contract_compact_guard_repair`

Minimum fields to fill:

- `coach_overall_quality_score`
- `coach_would_show_to_student`
- `coach_leakage_label`
- `coach_bridge_reveal_justification`
- `coach_scaffold_sufficiency_score`
- `coach_student_response_burden`
- `coach_reviewer_confidence`
- `coach_needs_discussion`
- `coach_notes`
- `review_status`

Major leakage, answer leakage, not-show, overall 1/2, low confidence, and discussion-needed rows require notes.

## Questions To Answer

| question | interpretation |
| --- | --- |
| Does DBox+Repair improve over DBox guard? | If yes, Repair may help literature-inspired baselines too. |
| Does DBox+Repair approach Bridge+Repair? | If yes, weaken Bridge-specific claims and emphasize repair-enabled guard pipelines. |
| Does DBox+Repair exceed Bridge+Repair? | If yes, report fairly and avoid Bridge victory framing. |
| Does DBox+Repair still have higher leakage / burden? | This can support Bridge Contract compact's incremental value, but still needs paired uncertainty. |

## Current Paper Wording

Before this supplemental review is complete, write:

```text
We generated a DBox-inspired Guard+Repair fairness add-on and include it as a planned supplementary human-review check.
```

Do not write:

```text
Bridge+Repair has a confirmed advantage over every repair-enabled fair baseline.
```
