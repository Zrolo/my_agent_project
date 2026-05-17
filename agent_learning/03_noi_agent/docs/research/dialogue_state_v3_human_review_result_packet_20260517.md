# Dialogue-State v3 Human Review Result Packet 20260517

中文版本：`dialogue_state_v3_human_review_result_packet_20260517.zh.md`

## Executive Summary

This note summarizes the response blind-review stage for the dialogue-state v3 50-case main experiment.

Current status:

- The 50 reviewed-candidate cases produced 350 anonymized responses across 7 conditions.
- Coach A completed the full 350-row blind review.
- Coach B completed the full 350-row overlap review.
- 60 high-priority Coach A/B disagreements were adjudicated.
- Sensitivity analysis and context-slice analysis have been generated.

These results can be treated as a **formal human-review evidence candidate**, but not as final gold. Sixty high-priority disagreements have been adjudicated; the remaining 290 rows still depend on the Coach A or Coach B baseline view. The paper should report agreement, adjudication, and sensitivity analysis instead of a single-score table alone.

## Main Conditions

| condition | Description |
| --- | --- |
| `enhanced_prompt_only_clean` | Strong pedagogical prompt baseline, no Guard / Repair |
| `codehelp_codeaid_clean` | CodeHelp / CodeAid-style no-direct-solution baseline |
| `dbox_inspired_clean` | DBox-inspired decomposition baseline, no Guard |
| `dbox_inspired_guard` | DBox-inspired decomposition baseline + Guard |
| `bridge_guided_dbox_style_guard` | Bridge-guided DBox-style baseline + Guard |
| `bridge_contract_compact_guard` | Bridge Contract compact + Guard |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard + Repair |

## Coach A / Coach B Overlap Review

Both coaches reviewed all 350 responses. Coach B was substantially stricter than Coach A, especially around `overall=3`, `show=borderline`, and `scaffold_sufficiency=1/0`.

A/B agreement summary:

| metric | value |
| --- | ---: |
| overlap rows | 350 |
| overall exact | 0.2829 |
| overall within 1 | 0.8429 |
| leakage exact | 0.6714 |
| critical binary exact | 0.9029 |
| critical binary kappa | 0.2511 |
| critical recall B vs A | 0.2 |
| rank mean Spearman by case | 0.0264 |
| top-1 agreement cases | 10 / 50 |
| last-place agreement cases | 10 / 50 |
| flagged disagreement rows | 244 |

Interpretation: overall quality scores mostly differ by at most one point, but student-ready, rank preference, and critical leakage judgments remain sensitive to rater strictness. Therefore A/B labels should not be naively averaged.

## High-Priority Adjudication

We adjudicated 60 high-priority rows from 244 severe A/B disagreements, covering 39 cases. Priority categories included critical leakage disagreement, show yes/no flip, overall delta >= 2, rank delta >= 4, and student-ready disagreement.

| Adjudication item | Count |
| --- | ---: |
| `use_A` | 29 |
| `use_B` | 9 |
| `new_label` | 22 |
| adjudicated `no_leakage` | 37 |
| adjudicated `minor_bridge_leakage` | 7 |
| adjudicated `major_bridge_leakage` | 16 |
| adjudicated `answer_leakage` | 0 |
| adjudicated student-ready `yes` | 27 |
| adjudicated student-ready `unclear` | 17 |
| adjudicated student-ready `no` | 16 |

The adjudication did not simply favor either coach: 22 rows required new labels. This supports reporting adjudication as a reliability-control step rather than treating either rater as absolute gold.

## Sensitivity Analysis

We compare four scoring views: Coach A only, Coach B only, priority60 adjudicated + Coach A, and priority60 adjudicated + Coach B.

Main observations:

- `bridge_contract_compact_guard_repair` has the highest overall score under all four views.
- Under Coach A and adjudicated+A, it is also best on ready / safe-ready.
- Under Coach B and adjudicated+B, ready / safe-ready favors `enhanced_prompt_only_clean` or `dbox_inspired_clean`.
- Overall conclusions are more stable than student-ready preference.

| scenario | best overall | best ready | best safe-ready | lowest major+answer |
| --- | --- | --- | --- | --- |
| Coach A only | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` |
| Coach B only | `bridge_contract_compact_guard_repair` | `enhanced_prompt_only_clean` | `enhanced_prompt_only_clean` | `codehelp_codeaid_clean` |
| priority60 adjudicated + Coach A | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard_repair` | `bridge_contract_compact_guard` |
| priority60 adjudicated + Coach B | `bridge_contract_compact_guard_repair` | `dbox_inspired_clean` | `dbox_inspired_clean` | `bridge_contract_compact_guard` |

A cautious paper statement is:

> Bridge Contract compact + Guard/Repair shows a stable advantage in overall quality and critical-leakage control across rater views, while student-ready preference is sensitive to rater strictness and should be reported with sensitivity analysis.

## Taxonomy Scope

The dialogue-state v3 50-case set is not an algorithm-topic checklist. It is an open-ended tutor-response evaluation sampled across Research v1 operational cognitive bridge families. Bridge buckets such as `state_representation_semantics`, `transition_recurrence_source`, `predicate_check_semantics`, and `boundary_update_order` are operational cognitive bridge family labels, not surface anchors.

Surface anchors are the concrete algorithm instances of those families, such as DP states, binary-search checks, lazy propagation, tree-difference marking, local code, greedy proofs, or debugging traces. Paper claims should be stated at the level of representation semantics, transition/action mapping, predicate/decision semantics, dependency/order control, modeling relations, aggregation/contribution accounting, data-structure operation mapping, correctness/invariant reasoning, implementation/debugging evidence, and policy-request handling.

Coverage limitations should be reported explicitly: dialogue-state v3 under-samples math property / modular invariant, counting / inclusion-exclusion, geometry predicate relation, search pruning / deduplication, and reflection / transfer cases. These should be treated as future extensions or supplementary stress sets, not as already fully covered.

## Slice Analysis

The context-readiness audit divides the 50 cases into:

| slice | Cases | Intended use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | Main scaffold-quality comparison |
| `main_eval_with_caution` | 5 | Sensitivity / cautious inclusion |
| `clarification_safety_slice` | 10 | Clarification and hallucination-avoidance behavior |
| `policy_safety_slice` | 4 | Safe redirection under direct-answer/code requests |

Under the current primary view `priority60 adjudicated + Coach A`, the `main_scaffold_eval` slice is:

| condition | overall | ready | safe-ready | major+answer |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.0323 | 7 | 7 | 9 |
| `codehelp_codeaid_clean` | 3.7097 | 19 | 19 | 2 |
| `dbox_inspired_clean` | 3.7742 | 21 | 21 | 2 |
| `dbox_inspired_guard` | 3.7742 | 23 | 23 | 2 |
| `bridge_guided_dbox_style_guard` | 3.7419 | 20 | 20 | 2 |
| `bridge_contract_compact_guard` | 4.0000 | 23 | 23 | 0 |
| `bridge_contract_compact_guard_repair` | 4.0645 | 22 | 22 | 0 |

This suggests that Bridge Contract compact + Guard/Repair is strongest on overall quality and major/answer leakage control within the main scaffold slice, while DBox-inspired + Guard remains a strong baseline on ready counts.

## Paper-Usable Claims

Candidate claims:

1. `critical bridge leakage` reveals over-helping beyond answer/code leakage.
2. DBox-inspired decomposition is a strong baseline and should not be treated as weak control.
3. Bridge Contract compact + Guard/Repair shows stable overall-quality and critical-leakage-control trends.
4. Student-ready and rank preference are sensitive to rater strictness; sensitivity analysis is necessary.
5. The paper should report a quality-safety-burden trade-off rather than declare a single universal winner.

Do not claim:

1. Bridge Contract universally and significantly outperforms all baselines.
2. Guard/Repair fully solves leakage.
3. Either Coach A or Coach B alone is gold.
4. The priority60 merged table is a final adjudicated reference.
5. All 50 cases should be collapsed into one headline average.

## Key Artifacts

- Coach A analysis: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_coach_A_round1_analysis_20260517.md`
- Coach B analysis: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_coach_B_round1_analysis_20260517.md`
- A/B agreement: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_coach_A_B_agreement_20260517.md`
- High-priority adjudication package: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_A_B_adjudication_priority60_20260517.zh.xlsx`
- Completed adjudication workbook: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_A_B_adjudication_priority60_20260517_zh1_adjudicated.xlsx`
- Priority60 adjudicated labels: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_adjudication_priority60_labels_20260517.jsonl`
- Priority60 adjudicated + Coach A labels: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_priority60_adjudicated_plus_coachA_labels_20260517.jsonl`
- Priority60 adjudicated + Coach B labels: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_priority60_adjudicated_plus_coachB_labels_20260517.jsonl`
- Sensitivity analysis: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_scoring_sensitivity_20260517.md`
- Slice analysis: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_slice_analysis_20260517.md`

## Next Steps

1. Send this packet to an external reviewer / AI reviewer to inspect scoring interpretation and statistics.
2. Draft the formal result section around the `main_scaffold_eval` slice, with clarification / policy slices as supplementary analyses.
3. Run LLM grader calibration comparing `likert_only_judge`, `generic_rubric_judge`, and `case_specific_bridge_rubric_judge` against adjudicated labels.
