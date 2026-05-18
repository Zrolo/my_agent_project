# Project Status After Taxonomy Revision 20260517

## Current Stage

Current project state:

```text
formal human-review evidence candidate + taxonomy framing stabilized
```

`taxonomy_specificity_revision_20260517` locks the paper framing as:

```text
cognitive bridge family + leakage mechanism + surface anchor
```

Bridge buckets are Research v1 operational cognitive bridge families. DP states, binary-search checks, lazy propagation, tree difference, and local code are surface anchors.

## Completed

| area | status |
| --- | --- |
| 50-case generation | dialogue-state v3 50-case reviewed candidate completed |
| response generation | 7-condition main table, 350 rows completed |
| Coach A review | all 350 rows reviewed |
| Coach B review | all 350 rows reviewed |
| priority60 adjudication | 60 high-priority A/B disagreements adjudicated |
| sensitivity analysis | Coach A/B only and adj+CoachA/B completed |
| slice analysis | main scaffold / caution / clarification / policy slices completed |
| taxonomy specificity wording | P0/P1 reviewer-facing wording completed and pushed |
| paired uncertainty | main_scaffold_eval W/T/L, bootstrap CI, permutation outputs exist |
| DBox repair add-on generation | `dbox_inspired_guard_repair` 50-row generation package exists |
| repair stress template | 30-row same-candidate natural repair template and blind workbook exist |
| DBox+Repair fairness add-on human review | 20-case headline-sensitive review completed and fairness sensitivity report generated |
| LLM grader calibration prompt packs | priority60 adjudicated 60-row pack and adj+CoachA/B sample20 packs generated; CoachB sample20 prompt context filled |
| LLM grader calibration results | DeepSeek-backed priority60 180/180 ok; adj+CoachA sample20 60/60 ok; adj+CoachB sample20 60/60 ok. Earlier Kimi-backed results are downgraded to exploratory/tooling records |

## Still To Complete

| task | current state | priority |
| --- | --- | --- |
| paper-ready tables | main table and pairwise docs prepared in this pass | P0 complete / maintain |
| Repair same-candidate stress labels | 30/30 blind before/after pairs completed; leakage improved 16/30, worsened 0/30, major leakage 7 -> 0, but burden worsened 12/30 | P0 complete |
| DBox+Repair fairness add-on full review | 20-case targeted review completed; optional full 50-case review or second review for risk cases if time allows | P1 optional |
| LLM grader calibration | DeepSeek-backed three reference views completed; case-specific rubrics improve some auxiliary metrics, but priority60 critical recall remains 0 | P1 complete / paper wording conservative |
| Results / Discussion prose | dialogue-state v3 draft updated; manuscript-style compressed prose and formal section draft added as `paper_results_discussion_section_dialogue_state_v3_20260518.zh.md` / `.md` | P1 complete / needs final paper editing |
| targeted adjudication extension | plan and candidate workbook exist; optional depending on time | P1 optional |

## Claim Boundary

The paper should frame the work as an evaluation framework and trade-off analysis, not a system victory narrative:

```text
CP-MissingBridgeBench reveals quality, critical-bridge leakage, and student-burden trade-offs across LLM tutors.
```

Can write:

- DBox-inspired decomposition is a strong baseline.
- Bridge Contract compact + Guard/Repair shows favorable overall and critical-leakage-control trends under the primary human-review view.
- No-direct-solution does not imply no critical bridge leakage.
- Student-ready / rank are rater-sensitive.
- Repair causality now has same-candidate stress support; DBox+Repair fairness is targeted sensitivity, not a full 50-case double-coach add-on.

Cannot write:

- Bridge Contract significantly and comprehensively beats all baselines.
- Guard-only fixes final outputs.
- Repair causality is proven by the main experiment.
- Coach A/B or priority60 is final gold.
- The 50-case set covers all CP tutoring situations.

## Next Execution Order

1. Use `paper_results_discussion_section_dialogue_state_v3_20260518.zh.md` / `.md` as the base for final manuscript editing.
2. Decide whether to expand DBox+Repair to 50 cases or second-review the risk cases.
3. Decide whether to run the targeted adjudication extension.
4. Final pass on claim wording, table captions, limitations, and appendix boundaries.
