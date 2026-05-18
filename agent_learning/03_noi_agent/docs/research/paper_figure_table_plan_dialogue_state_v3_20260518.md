# Paper Figure / Table Plan: Dialogue-State v3 20260518

## Scope

This document only plans manuscript figures and tables. It adds no experiments, modifies no data, and does not change result interpretation. All headline figures and tables must follow these boundaries:

- The main result uses only `main_scaffold_eval` + priority60 adjudicated + Coach A.
- The all-50 aggregate is sensitivity / appendix only.
- Guard-only must be labeled as instrumentation / runtime signal, not rewrite.
- Repair causality comes only from the same-candidate stress test.
- DBox+Repair is targeted fairness sensitivity, not a full main condition.
- The LLM grader is auxiliary calibration, not a human-review replacement.

## Main-Text Figures

| id | title | goal | source | must show | must not imply |
| --- | --- | --- | --- | --- | --- |
| Figure 1 | CP-MissingBridgeBench evaluation flow | Show the full path from student turn to case-specific rubric, human review, and evidence classes. | `paper_methods_evaluation_dialogue_state_v3_20260518.md`; `dialogue_state_v3_evidence_manifest_20260518.json` | student turn -> missing bridge rubric -> tutor harness responses -> blind human review -> sensitivity / stress / calibration evidence. | Do not draw it as online active-mode deployment; do not imply Guard-only rewrites final responses. |
| Figure 2 | Critical bridge leakage boundary | Explain the boundary between answer leakage, critical bridge leakage, acceptable reveal, and helpful scaffold. | `response_review_rubric_v3.md`; `paper_methods_evaluation_dialogue_state_v3_20260518.md` | A response can avoid full code/solution and still leak intermediate reasoning; the case-specific rubric defines the boundary. | Do not treat all informative explanation as leakage; do not reduce the taxonomy to concrete algorithms. |
| Figure 3 | Evidence classes and claim boundaries | Help reviewers separate main result, sensitivity, stress test, fairness add-on, and calibration. | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.md`; `dialogue_state_v3_paper_claims_final_gate_20260518.md` | main result = main scaffold; Repair = stress; DBox+Repair = sensitivity; LLM grader = calibration. | Do not frame stress tests or calibration as main experiment conditions. |

If space is tight, keep only Figure 1 in the main text; Figure 2 and Figure 3 can move to the appendix or be merged into one claim-boundary schematic.

## Main-Text Tables

| id | title | evidence class | source files / scripts | required fields | allowed claim | forbidden wording |
| --- | --- | --- | --- | --- | --- | --- |
| Table 1 | Benchmark slices and paper use | methods / scope | `paper_methods_evaluation_dialogue_state_v3_20260518.md`; `dialogue_state_v3_50_context_readiness_audit_20260515.jsonl` | slice, case_n, paper use | The main headline comes only from `main_scaffold_eval`; other slices are sensitivity / appendix. | all 50 cases headline; full CP tutoring coverage. |
| Table 2 | Tutoring harness conditions and interpretation boundaries | methods / baseline | `paper_methods_evaluation_dialogue_state_v3_20260518.md`; `baseline_protocol_v1.md` | condition, role, final-response boundary, paper interpretation | The 7 conditions are offline human-review harnesses; DBox is a literature-inspired strong baseline. | online deployed system; faithful DBox reproduction; Guard-only rewrite. |
| Table 3 | Main scaffold results | main result | `dialogue_state_v3_main_paper_ready_tables_20260517.md`; `reproduce_dialogue_state_v3_tables.py`; `verify_dialogue_state_v3_reports.py` | condition, overall, student-ready, safe-ready, major+answer leakage, scaffold sufficiency, burden | Bridge Contract compact + Guard/Repair shows favorable overall / high-severity leakage-control trends; DBox-inspired is a strong baseline. | Bridge Contract comprehensively and significantly wins; all-case mean as headline. |
| Table 4 | Paired W/T/L and uncertainty | main result support | `dialogue_state_v3_pairwise_win_tie_loss_20260517.md`; paired uncertainty CSV/JSON; `reproduce_dialogue_state_v3_tables.py` | comparison, n, W/T/L, mean overall delta, CI, p, safe-ready delta, major+answer delta | Key comparisons support trend / trade-off wording; CIs crossing 0 block significant-dominance wording. | absolute winner; significant dominance when CI crosses 0. |
| Table 5 | Human review reliability | reliability | `human_review_reliability_section_draft_20260517.md`; Coach A/B agreement JSON; priority60 adjudication files | overall exact, within-1, leakage exact, critical binary exact/kappa, rank agreement, priority60 outcomes | Pedagogical judgment is rater-sensitive; double review, adjudication, and sensitivity are necessary. | Coach A/B/priority60 is gold. |
| Table 6 | Repair stress and DBox+Repair sensitivity | stress + sensitivity | `repair_same_candidate_stress_result_20260517.md`; `dbox_guard_repair_fairness_report_20260517.md`; summary JSON files | repair before/after leakage and burden; DBox+Repair 20-case overall/safe-ready/leakage; same-case comparison | Repair reduces leakage in same-candidate stress but increases burden; DBox+Repair mitigates the fairness concern. | Repair causality is proven by main-experiment means; DBox+Repair is a full main condition. |

If the main text can only include four tables, move Table 5 into Methods / Appendix and keep Table 6 as a compact stress + sensitivity summary.

## Appendix Tables

| appendix id | title | source | role |
| --- | --- | --- | --- |
| Table A1 | Full slice tables | `dialogue_state_v3_main_paper_ready_tables_20260517.md` | Report `main_eval_with_caution`, `clarification_safety_slice`, `policy_safety_slice`, and all-case sensitivity. |
| Table A2 | Four rater views sensitivity | `dialogue_state_v3_main_paper_ready_tables_20260517.md`; `dialogue_state_v3_main_scoring_sensitivity_20260517.zh.md` | Coach A only, Coach B only, priority60+CoachA, priority60+CoachB. |
| Table A3 | Observed error taxonomy distribution | `dialogue_state_v3_observed_error_taxonomy_20260517.md` | Level 1 failure type x condition; Level 1 x Level 2 coverage. |
| Table A4 | Repair same-candidate pair details | `repair_same_candidate_stress_result_20260517.md`; candidate/key/summary CSV/JSON | before/after blind review details, leakage delta, burden delta. |
| Table A5 | DBox+Repair 20-case targeted add-on details | `dbox_guard_repair_fairness_report_20260517.md` | Explain the targeted sensitivity set and protocol mismatch. |
| Table A6 | DeepSeek LLM grader calibration | `llm_grader_calibration_deepseek_sensitivity_report_20260518.md` | Auxiliary metrics for likert-only, generic rubric, and case-specific rubric; highlight critical recall risk. |
| Table A7 | Evidence manifest checksums | `dialogue_state_v3_evidence_manifest_20260518.json` | Audit report, input, script, output, checksum, and interpretation boundary. |

## Recommended Figure / Table Order

The safest main-text order is:

1. Figure 1: evaluation flow, to prevent misunderstanding the system boundary.
2. Table 1: slices, to prevent an all-50 headline.
3. Table 2: conditions, to prevent Guard-only / DBox / online-status misinterpretation.
4. Table 3: main result.
5. Table 4: paired uncertainty, immediately after the main result to prevent overclaiming.
6. Table 5: human review reliability, either in Methods or early Results.
7. Table 6: Repair stress + DBox+Repair sensitivity, late Results or before Discussion.

## Writing Notes

- Prefer evidence-class words in titles: `main_scaffold_eval`, `sensitivity`, `stress test`, and `calibration`.
- Table notes must state that `priority60 adjudicated + Coach A` is the primary reference view, not final gold.
- Repair table notes must state same-candidate stress, not main condition means.
- LLM grader table notes must state that DeepSeek critical recall is 0 and cannot replace human review.
- DBox+Repair table notes must state 20-case targeted add-on, not full 50-case double-coach validation.

## Minimal Submission Version

For a short-paper draft, the minimal figure/table set is:

1. Figure 1: evaluation flow.
2. Table 1: slices + conditions, combining slice and condition boundaries.
3. Table 2: main scaffold results.
4. Table 3: paired uncertainty.
5. Table 4: compact evidence-boundary table covering reliability, Repair stress, DBox+Repair, and LLM grader limitations.

This minimal version should still keep full sensitivity and reproduction references in the main text or appendix.
