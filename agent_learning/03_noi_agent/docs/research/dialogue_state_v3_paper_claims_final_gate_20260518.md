# Dialogue-State v3 Paper Claims Final Gate 20260518

This file is the pre-submission claim gate. It adds no experiment, changes no main-experiment data, and does not connect to the online active mode. Its only purpose is to keep the dialogue-state v3 evidence package from being written as an over-strong paper result.

## Claim Gate

| allowed wording | required evidence | forbidden wording |
| --- | --- | --- |
| CP-MissingBridgeBench reveals quality-safety-burden trade-offs across LLM tutoring harnesses. | `dialogue_state_v3_main_paper_ready_tables_20260517.md`; `dialogue_state_v3_pairwise_win_tie_loss_20260517.md`; Coach A/B human review plus priority60 adjudication. | CP-MissingBridgeBench fully covers all CP tutoring scenarios; all 50 cases are the single headline average. |
| The main headline uses the 31-case `main_scaffold_eval` slice; other slices are sensitivity / appendix views. | `dialogue_state_v3_main_paper_ready_tables_20260517.md`; `dialogue_state_v3_50_context_readiness_audit_20260515.jsonl`. | Pooling `main_eval_with_caution`, `clarification_safety_slice`, `policy_safety_slice`, and main scaffold into one headline mean. |
| Bridge Contract compact + Guard/Repair shows favorable trends in overall quality and critical-leakage control. | Main scaffold table; paired W/T/L; paired CI; sensitivity tables. | Bridge Contract significantly and comprehensively outperforms every baseline. |
| DBox-inspired decomposition is a strong baseline. | DBox clean / guard results in main scaffold tables and paired comparisons. | DBox is weak, or Bridge only wins against weak baselines. |
| No-direct-code / no-direct-solution baselines may still produce critical bridge leakage. | Leakage comparisons for `codehelp_codeaid_clean`, prompt-only, DBox, and Bridge conditions. | Not giving direct code means no critical bridge leakage. |
| Guard-only is a guard-instrumented / guard-checked condition that mainly provides a runtime leakage signal. | `paper_results_interpretation_guardrails_20260517.md`; `run_bridge_offline_eval.py` tutor_plus_guard path; main-run block=0. | Guard-only fixes final output; Guard-only rewrite changed the student-visible response. |
| Repair causal evidence comes only from the same-candidate stress test. | `repair_same_candidate_stress_result_20260517.md`; 30-pair before/after blind review; summary JSON. | Main experiment condition means alone causally prove Repair; Repair fully solves leakage. |
| Repair reduces leakage but introduces a student-burden trade-off. | Same-candidate stress: leakage improved 16/30, major leakage 7->0, burden worsened 12/30. | Repair improves quality at no cost; Repair is always better. |
| DBox+Repair is targeted fairness sensitivity evidence. | `dbox_guard_repair_fairness_report_20260517.md`; 20-case targeted review; same-case comparison summary. | DBox+Repair has complete 50-case double-coach main-experiment validation; Bridge+Repair has a definitive advantage over all repair-enabled baselines. |
| Coach A/B and priority60 adjudication are expert references / adjudicated sensitivity views. | A/B 350-row blind review; priority60 adjudication; agreement and sensitivity analyses. | Coach A is gold; Coach B is gold; priority60 + Coach A/B is final gold. |
| The LLM grader is only a scalable auxiliary grader. | DeepSeek calibration: priority60 case-specific judge critical recall 0, major FN 1.000. | LLM graders can replace human coaches; DeepSeek grader reliably detects critical bridge leakage; LLM grader labels are gold. |
| The taxonomy is cognitive bridge family + leakage mechanism + surface anchor. | `taxonomy_specificity_revision_summary_20260517.md`; `dialogue_state_v3_observed_error_taxonomy_20260517.md`. | The benchmark only evaluates concrete algorithm scenarios such as DP state, binary-search check, lazy propagation, tree difference, or local code. |

## Pre-Submission Check

Before every Results / Discussion edit, re-check:

1. The headline comes only from `main_scaffold_eval`.
2. Guard-only is still described as instrumentation, not rewrite.
3. Repair causal evidence is limited to same-candidate stress.
4. DBox+Repair remains an appendix / fairness-sensitivity view.
5. priority60, Coach A, and Coach B are not called gold.
6. The LLM grader is not written as a replacement for human review.
7. The taxonomy has not collapsed back into concrete algorithm tuning.
