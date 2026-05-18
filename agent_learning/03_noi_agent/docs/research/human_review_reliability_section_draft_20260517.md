# Human Review Reliability Section Draft 20260517

## Draft Section

The dialogue-state v3 response review uses double expert review and high-priority adjudication rather than treating any single rater as gold. Coach A and Coach B both reviewed the full 50 cases × 7 conditions, for 350 anonymized responses. We then adjudicated 60 high-priority A/B disagreement rows, prioritizing critical leakage disagreement, student-ready flips, would-show flips, overall delta >= 2, rank delta >= 4, and headline-comparison relevance.

A/B agreement shows that open-ended pedagogical judgment is rater-sensitive. Overall exact agreement is 0.2829, while overall within-1 agreement is 0.8429, indicating that most overall scores differ by at most one point. Leakage exact agreement is 0.6714. Critical-binary exact agreement is 0.9029, but critical-binary kappa is only 0.2511, suggesting high raw agreement but limited chance-corrected agreement under low base rates and different strictness. Rank mean Spearman by case is 0.0264, with top-1 and last-place agreement both 10/50. There are 244 flagged disagreement rows.

Priority60 adjudication further shows that neither Coach A nor Coach B can be treated as gold. Among the 60 adjudicated rows, the adjudicator selected `use_A=29`, `use_B=9`, and `new_label=22`. The 22 new labels show that high-disagreement cases often required independent relabeling rather than simply choosing the more reliable coach.

Accordingly, we treat human review as expert reference rather than absolute truth. Main results are reported under Coach A only, Coach B only, priority60 adjudicated + Coach A, and priority60 adjudicated + Coach B. Results are also separated by `main_scaffold_eval`, `main_eval_with_caution`, `clarification_safety_slice`, and `policy_safety_slice`. We do not call the priority60 merged labels final gold and do not report only a single mean table.

## Method Framing

This disagreement should not be framed as an evaluation failure. A more accurate interpretation is that pedagogical judgment is inherently rater-sensitive. Whether a response is ready to show to a student, whether it over-completes the student's missing bridge, and whether it imposes too much next-turn burden all depend on expert judgment about student state and timing. We therefore use double review, priority adjudication, slice analysis, and sensitivity reporting.

## Short Paper Version

```text
Human review was intentionally treated as rater-sensitive expert judgment rather than gold truth. Both coaches reviewed all 350 anonymized responses. Exact overall agreement was low, but most overall scores were within one point. Critical-leakage binary agreement was high in raw exact agreement but modest under kappa, and rank agreement was low. We therefore adjudicated 60 high-priority disagreement rows and report all main results under both original and adjudicated sensitivity views.
```

## Do Not Write

- Coach A is gold.
- Coach B is gold.
- The priority60 adjudicated merge is final gold.
- A/B disagreement invalidates the evaluation.
- Only one `priority60 adjudicated + Coach A` table is sufficient.
