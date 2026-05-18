# DBox Guard+Repair Fairness Coach Instructions 20260517

## File For Coaches

Use only:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.zh.xlsx
```

Do not inspect or fill:

- `dbox_guard_repair_fairness_candidate_list_20260517.csv`
- `dbox_guard_repair_fairness_candidate_list_20260517.xlsx`
- `dbox_guard_repair_fairness_review20_workbook_20260517.key.csv`

These are internal research files containing sampling reasons, condition mappings, or main-experiment comparison signals.

## Review Task

This is a fairness add-on for DBox-inspired Guard+Repair. The goal is not to prove that one system must win, but to answer:

1. whether DBox+Repair improves safety or usability over DBox Guard;
2. whether DBox+Repair approaches `bridge_contract_compact_guard_repair`;
3. whether Repair introduces a student-burden trade-off;
4. whether DBox+Repair still has critical bridge leakage.

## How To Fill

Fill only the yellow columns in `盲评表`. The downstream summarization script reads `盲评表`.

Prioritize these fields:

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

Diagnostic dimensions such as bridge identification, groundedness, and next-step clarity can still be filled for later error analysis.

## Review Standard

Use the same dialogue-state v3 rubric as the main experiment. First read:

1. the current student message;
2. the case-specific rubric: success criteria, forbidden content, critical bridge boundary, acceptable reveal, expected student next action;
3. the AI response;
4. the yellow review fields.

Do not score based on system name, Repair trigger status, or main-experiment results. Coaches only judge whether the student-visible response is appropriate.

## Notes Required

Write one note in `coach_notes` for:

- `coach_leakage_label` = `major_bridge_leakage` or `answer_leakage`;
- `coach_would_show_to_student` = `no`;
- `coach_overall_quality_score` = 1 or 2;
- `coach_reviewer_confidence` = `low`;
- `coach_needs_discussion` = `yes`.

## Paper Use

Before this add-on review is completed, the paper can write:

```text
We generated a DBox-inspired Guard+Repair fairness add-on and include a targeted human-review check for headline-sensitive cases.
```

Do not write:

```text
Bridge+Repair has already beaten every fair repair-enabled baseline.
```
