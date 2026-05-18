# Dialogue-State v3 Targeted Adjudication Extension Plan (20260517)

## Goal

Do not adjudicate all 350 rows. Add a targeted 30-40-row adjudication round from remaining Coach A/B disagreements, prioritizing cases that affect headline comparisons and safety claims.

## Outputs

- Candidate workbook: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/adjudication_extension_candidate_list_20260517.xlsx`
- CSV version: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/adjudication_extension_candidate_list_20260517.csv`

Selected candidates: 40. The existing priority60 adjudicated rows (60) were excluded.

## Selection Rule

Rows were prioritized for `main_scaffold_eval`, critical leakage disagreement, student-ready flip, would-show flip, rank delta >= 4, overall delta >= 2, headline conditions, and Bridge-vs-DBox relevance.

| reason | count |
| --- | --- |
| main_scaffold_eval | 40 |
| would-show flip | 40 |
| headline condition | 40 |
| student-ready flip | 39 |
| Bridge vs DBox comparison affected | 36 |
| rank delta >= 4 | 13 |
| overall delta >= 2 | 13 |

## Recommended Workflow

1. The adjudicator should see the student turn, response, and case-specific rubric, but not condition names.
2. Decide `adjudicated_leakage_label` and `adjudicated_would_show_to_student` first, then overall / sufficiency / burden.
3. Add one sentence of notes for rows affecting the main table, especially whether the issue is over-revealing, too vague, context-misaligned, or showable with minor edits.
4. After completion, generate `priority100_adjudicated_plus_coachA/B` sensitivity. The paper can then say that high-priority disagreements and an additional targeted set affecting headline comparisons were adjudicated.

## Boundary

This extension is still not final gold. It reduces uncertainty around the most consequential disagreements; it does not eliminate all rater variance.
