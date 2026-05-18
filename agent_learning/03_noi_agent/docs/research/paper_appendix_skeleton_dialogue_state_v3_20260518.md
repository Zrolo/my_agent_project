# Paper Appendix Skeleton: Dialogue-State v3 20260518

## Scope

This document is a supplementary-material skeleton for the dialogue-state v3 manuscript. It adds no experiments, changes no data, and does not connect online active mode. Its purpose is to keep appendix evidence organized by evidence class so that sensitivity, stress-test, fairness, calibration, and artifact evidence are not accidentally written as main results.

Use this appendix skeleton with:

- `paper_submission_manuscript_dialogue_state_v3_20260518.md`
- `paper_manuscript_assembly_map_dialogue_state_v3_20260518.md`
- `paper_figure_table_plan_dialogue_state_v3_20260518.md`
- `dialogue_state_v3_evidence_manifest_20260518.json`
- `dialogue_state_v3_paper_claims_final_gate_20260518.md`

## Appendix A. Evidence Package Overview

Purpose: document what the dialogue-state v3 package contains and what it is not.

Include:

- Branch and checkpoint notes:
  - evidence-content base may appear as `dbbbd5c`;
  - evidence-package gates checkpoint is `33a5dd7`;
  - later branch-tip commits tighten paper wording and handoff docs unless explicitly stated otherwise.
- Evidence package status:
  - `formal human-review evidence candidate`;
  - not final gold;
  - not online active-mode validation.
- Main headline rule:
  - `main_scaffold_eval` only;
  - all-50 aggregate is sensitivity / robustness only.

Primary sources:

- `docs/research/index.md`
- `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`
- `docs/research/dialogue_state_v3_paper_claims_final_gate_20260518.md`

## Appendix B. Dataset Slices and Case Use

Purpose: prevent readers from interpreting the 50 cases as one undifferentiated headline set.

Recommended table:

| slice | case_n | appendix use | headline use |
| --- | ---: | --- | --- |
| `main_scaffold_eval` | 31 | Full metrics and paired comparisons. | Yes. |
| `main_eval_with_caution` | 5 | Sensitivity only. | No. |
| `clarification_safety_slice` | 10 | Clarification and context-insufficient safety analysis. | No. |
| `policy_safety_slice` | 4 | Direct-answer / policy redirection analysis. | No. |

Primary sources:

- `paper_methods_evaluation_dialogue_state_v3_20260518.md`
- `dialogue_state_v3_main_paper_ready_tables_20260517.md`
- `dialogue_state_v3_50_context_readiness_audit_20260515.jsonl`

## Appendix C. Human Review Reliability

Purpose: make rater sensitivity visible instead of hiding it behind a single score table.

Include:

- Coach A and Coach B both reviewed all 350 AI responses.
- Overall-quality exact agreement: 0.2829.
- Overall-quality within-1 agreement: 0.8429.
- Leakage-label exact agreement: 0.6714.
- Critical-binary exact agreement: 0.9029.
- Critical-binary kappa: 0.2511.
- Rank top-1 agreement: 10/50.
- Rank last-place agreement: 10/50.
- priority60 adjudication outcomes:
  - `use_A=29`;
  - `use_B=9`;
  - `new_label=22`.

Required interpretation:

- Coach A, Coach B, and priority60 adjudication are expert reference / adjudicated sensitivity views, not gold.
- Student-ready, safe-ready, and rank should be reported as rater-sensitive.

Primary sources:

- `human_review_reliability_section_draft_20260517.md`
- `dialogue_state_v3_main_coach_A_B_agreement_20260517.zh.md`
- priority60 adjudication JSONL files under `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/`

## Appendix D. Full Slice and Rater-View Sensitivity

Purpose: show that the main claim is not based on a hidden all-50 average.

Include tables for:

- `main_scaffold_eval` under:
  - Coach A only;
  - Coach B only;
  - priority60 adjudicated + Coach A;
  - priority60 adjudicated + Coach B.
- `main_eval_with_caution`.
- `clarification_safety_slice`.
- `policy_safety_slice`.
- all-50 aggregate as sensitivity only.

Required interpretation:

- The main text may use `main_scaffold_eval + priority60 adjudicated + Coach A` as the primary view.
- all-50 aggregate is appendix robustness only because it mixes slices with different paper uses.

Primary sources:

- `dialogue_state_v3_main_paper_ready_tables_20260517.md`
- `dialogue_state_v3_main_scoring_sensitivity_20260517.zh.md`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`

## Appendix E. Paired Comparisons and Uncertainty

Purpose: make same-case uncertainty visible and block overclaiming.

Minimum comparisons:

1. `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard`
2. `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard`
3. `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean`
4. `dbox_inspired_guard` vs `dbox_inspired_clean`
5. `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean`
6. `bridge_contract_compact_guard` vs `dbox_inspired_guard`

Required fields:

- `n`
- W/T/L
- mean overall delta
- bootstrap CI
- paired permutation p
- safe-ready delta
- major+answer leakage delta
- paper interpretation

Key boundary:

- If the CI crosses 0, use favorable trend / trade-off wording, not significant dominance.

Primary sources:

- `dialogue_state_v3_pairwise_win_tie_loss_20260517.md`
- `dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.md`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`

## Appendix F. Observed Error Taxonomy

Purpose: show that the taxonomy is not tuned only to DP/check/lazy/tree/local-code examples.

Report taxonomy as:

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

Include:

- Level 1 failure type definitions.
- Level 2 cognitive bridge family coverage.
- Level 3 surface-anchor examples.
- Condition-level error distribution.
- Level 1 x Level 2 coverage table.

Required interpretation:

- This is an observed operational taxonomy, not a universal taxonomy.
- DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, and debugging trace are surface anchors, not the taxonomy itself.

Primary sources:

- `dialogue_state_v3_observed_error_taxonomy_20260517.md`
- `taxonomy_specificity_revision_summary_20260517.md`
- `response_review_rubric_v3.md`

## Appendix G. Repair Same-Candidate Stress Test

Purpose: separate Repair causal evidence from main-condition means.

Report:

- 30 before/after pairs.
- Leakage severity improved / same / worsened: 16/14/0.
- Major leakage: 7/30 before -> 0/30 after.
- Mean overall: 3.367 before -> 3.633 after.
- Burden improved / same / worsened: 2/16/12.

Required interpretation:

- Repair reduces leakage under fixed-candidate stress testing.
- Repair may increase student burden.
- Main experiment condition means alone do not prove Repair causality.

Primary sources:

- `repair_same_candidate_stress_protocol_20260517.md`
- `repair_same_candidate_stress_result_20260517.md`
- repair stress summary files listed in the evidence manifest.

## Appendix H. DBox+Repair Fairness Sensitivity

Purpose: answer the fairness concern that only Bridge Contract received Repair in the main table.

Report:

- 20 headline-sensitive cases.
- DBox+Repair overall: 3.55.
- DBox+Repair safe-ready: 11/20.
- DBox+Repair no/minor/major+answer leakage: 14/6/0.
- Same-case DBox Guard comparison:
  - overall +0.15;
  - major+answer leakage 2 -> 0.
- Same-case Bridge+Repair comparison:
  - Bridge+Repair remains +0.50 overall;
  - W/T/L 12/5/3;
  - +4 safe-ready.

Required interpretation:

- DBox+Repair is targeted fairness sensitivity, not a full 50-case double-coach main condition.
- The result should be reported fairly even though it does not replace the main-condition design.

Primary sources:

- `dbox_guard_repair_fairness_report_20260517.md`
- `dbox_repair_fairness_extension_plan_20260518.md`
- DBox+Repair review workbook / summary files listed in the evidence manifest.

## Appendix I. DeepSeek LLM Grader Calibration

Purpose: show that automatic graders are auxiliary and cannot replace human review.

Report:

- Backend: DeepSeek `deepseek-v4-flash`, thinking disabled.
- Judge variants:
  - likert-only;
  - generic rubric;
  - case-specific bridge rubric.
- Priority60 key metrics:
  - case-specific leakage-label accuracy 0.617 vs generic 0.583;
  - case-specific student-ready agreement 0.467 vs generic 0.433;
  - case-specific safe-ready agreement 0.533 vs generic 0.400;
  - critical recall 0;
  - major leakage false-negative rate 1.000.

Required interpretation:

- LLM graders may be scalable auxiliary signals.
- They are not gold and cannot replace human coaches for critical bridge leakage.
- Kimi-backed calibration records are exploratory/tooling evidence only.

Primary sources:

- `llm_grader_calibration_deepseek_sensitivity_report_20260518.md`
- `llm_grader_calibration_plan_or_report_20260517.md`
- `evals/aichat/run_llm_grader_calibration.py`
- `evals/aichat/summarize_llm_grader_calibration.py`

## Appendix J. Evidence Manifest and Reproduction

Purpose: make the evidence package auditable.

Include:

- Manifest entry table:
  - claim_id;
  - report_file;
  - input_files;
  - script_used;
  - output_files;
  - checksum;
  - interpretation_boundary;
  - forbidden_wording.
- Reproduction commands:

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_submission.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 evals/aichat/validate_research_bilingual_docs.py --output-json /tmp/bilingual_docs_validation_submission.json
```

Known validator note:

- The bilingual docs validator may fail on historical / legacy unpaired docs.
- New dialogue-state v3 paper-facing docs should remain paired.
- The historical pairing debt does not change the main evidence package numbers.

Primary sources:

- `dialogue_state_v3_evidence_manifest_20260518.json`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`
- `evals/aichat/verify_dialogue_state_v3_reports.py`
- `evals/aichat/validate_research_bilingual_docs.py`

## Appendix K. Claim Gate

Purpose: keep reviewers, collaborators, and external AIs from over-reading the appendix.

Forbidden appendix interpretations:

- The 50-case set is final gold.
- all-50 aggregate is the main headline.
- Guard-only rewrites or repairs final student-visible responses.
- Repair causality is proven by main-condition means alone.
- DBox+Repair is a full main condition.
- DeepSeek or any LLM grader replaces human review.
- The taxonomy is only DP/check/lazy/tree/local-code.

Required final sentence for the appendix:

```text
The appendix provides sensitivity, stress-test, calibration, and artifact evidence for the dialogue-state v3 human-review package; it does not change the main headline slice, gold-label boundary, Guard/Repair interpretation, or LLM-grader limitation stated in the main paper.
```
