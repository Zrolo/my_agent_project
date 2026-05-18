# Paper Table Source: Dialogue-State v3 20260518

## Scope

This document provides copy-ready table sources for the dialogue-state v3 manuscript. It adds no experiments, changes no data, and does not connect online active mode. Tables are copied or compressed from existing paper-ready result reports and must keep the interpretation boundaries below.

Global table boundaries:

- Main headline tables use `main_scaffold_eval` only.
- The primary reference view is `priority60 adjudicated + Coach A`, not final gold.
- all-50 averages are appendix / sensitivity only.
- Guard-only is instrumentation / runtime signal, not final-response rewrite.
- Repair causality comes from same-candidate stress testing.
- DBox+Repair is targeted fairness sensitivity, not a full main condition.
- DeepSeek LLM grader calibration is auxiliary only.

## Table 1. Benchmark Slices and Paper Use

| slice | case_n | paper use | headline? |
| --- | ---: | --- | --- |
| `main_scaffold_eval` | 31 | Main scaffold-quality, leakage, and burden comparison. | Yes |
| `main_eval_with_caution` | 5 | Sensitivity / appendix for caution cases. | No |
| `clarification_safety_slice` | 10 | Clarification, non-over-inference, and context-insufficient safety. | No |
| `policy_safety_slice` | 4 | Direct-answer / direct-code safety redirection. | No |

Caption draft:

```text
Dialogue-state v3 separates cases by paper use. The main headline uses only the 31-case main_scaffold_eval slice; other slices and all-50 aggregates are sensitivity or appendix views.
```

Source:

- `paper_methods_evaluation_dialogue_state_v3_20260518.md`
- `dialogue_state_v3_main_paper_ready_tables_20260517.md`
- `dialogue_state_v3_50_context_readiness_audit_20260515.jsonl`

## Table 2. Tutoring Harness Conditions and Interpretation Boundaries

| condition | role | interpretation boundary |
| --- | --- | --- |
| `enhanced_prompt_only_clean` | Strong prompt-only baseline | No case-specific Bridge Contract. |
| `codehelp_codeaid_clean` | No-direct-solution baseline | Tests whether no-direct-code / no-direct-solution guardrails are sufficient. |
| `dbox_inspired_clean` | Literature-inspired decomposition baseline | DBox-inspired single-turn scaffold; not a DBox reproduction. |
| `dbox_inspired_guard` | DBox-inspired + guard-instrumented variant | Guard-only provides runtime leakage signal; it does not rewrite final responses. |
| `bridge_guided_dbox_style_guard` | Bridge-guided decomposition variant | Uses bridge signal to guide a DBox-style response; still guard-instrumented. |
| `bridge_contract_compact_guard` | Bridge Contract compact + guard-instrumented method | Uses compact bridge contract and guard signal; Guard-only is not a rewrite condition. |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard/Repair method | Student-visible response may come from Repair; main means show condition-level trends. |

Caption draft:

```text
The 7 conditions are offline human-review harnesses, not online deployed modes. DBox-inspired conditions are literature-inspired baselines rather than DBox reproductions; Guard-only conditions are guard-instrumented rather than final-response rewriting conditions.
```

Source:

- `paper_methods_evaluation_dialogue_state_v3_20260518.md`
- `baseline_protocol_v1.md`
- `paper_results_interpretation_guardrails_20260517.md`

## Table 3. Main Scaffold Results

Primary view: `main_scaffold_eval` + `priority60 adjudicated + Coach A`.

| condition | n | overall | student-ready | safe-ready | no leakage | minor leakage | major+answer leakage | scaffold avg | burden low/med/high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `enhanced_prompt_only_clean` | 31 | 3.032 | 7 | 7 | 10 | 12 | 9 | 1.13 | 2/12/17 |
| `codehelp_codeaid_clean` | 31 | 3.710 | 19 | 19 | 23 | 6 | 2 | 1.58 | 2/27/2 |
| `dbox_inspired_clean` | 31 | 3.774 | 21 | 21 | 23 | 6 | 2 | 1.65 | 6/22/3 |
| `dbox_inspired_guard` | 31 | 3.774 | 23 | 23 | 27 | 2 | 2 | 1.71 | 8/22/1 |
| `bridge_guided_dbox_style_guard` | 31 | 3.742 | 20 | 20 | 20 | 9 | 2 | 1.65 | 2/28/1 |
| `bridge_contract_compact_guard` | 31 | 4.000 | 23 | 23 | 26 | 5 | 0 | 1.74 | 3/28/0 |
| `bridge_contract_compact_guard_repair` | 31 | 4.065 | 22 | 22 | 25 | 6 | 0 | 1.68 | 3/28/0 |

Caption draft:

```text
Main scaffold results under the primary human-review view. Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends, while DBox-inspired decomposition remains a strong baseline. These counts should be interpreted with paired uncertainty and rater-sensitivity analyses.
```

Required table note:

```text
Primary reference view is priority60 adjudicated + Coach A, not final gold. Student-ready and safe-ready are counts out of 31. Major+answer leakage combines major critical bridge leakage and answer/code leakage.
```

Source:

- `dialogue_state_v3_main_paper_ready_tables_20260517.md`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`

## Table 4. Paired W/T/L and Uncertainty

Primary view: `main_scaffold_eval` + `priority60 adjudicated + Coach A`.

| comparison | n | W/T/L | delta overall | 95% CI | paired p | delta safe-ready | delta major+answer | paper wording |
| --- | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | 31 | 14/10/7 | +0.290 | [-0.097, +0.645] | 0.2016 | -1 | -2 | Favorable trend / trade-off; not significant dominance. |
| `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | 31 | 7/18/6 | +0.065 | [-0.226, +0.355] | 0.8322 | -1 | +0 | Does not establish Repair causality. |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | 31 | 12/14/5 | +0.290 | [-0.032, +0.613] | 0.1358 | +1 | -2 | Favorable trend; CI crosses 0. |
| `dbox_inspired_guard` vs `dbox_inspired_clean` | 31 | 7/15/9 | +0.000 | [-0.355, +0.355] | 1.0000 | +2 | +0 | Guard-only is instrumentation, not repair. |
| `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | 31 | 18/10/3 | +0.677 | [+0.258, +1.065] | 0.0046 | +12 | -7 | Prompt-only is not a sufficient strong baseline. |
| `bridge_contract_compact_guard` vs `dbox_inspired_guard` | 31 | 12/12/7 | +0.226 | [-0.065, +0.548] | 0.2360 | +0 | -2 | Leakage-control trend; overall CI crosses 0. |

Caption draft:

```text
Same-case paired comparisons for main_scaffold_eval. Positive delta overall means the first condition scores higher; negative delta major+answer means fewer high-severity leaks for the first condition. CIs crossing 0 require trend / trade-off wording rather than significant-dominance wording.
```

Source:

- `dialogue_state_v3_pairwise_win_tie_loss_20260517.md`
- `dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.md`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`

## Table 5. Evidence Boundary Summary

| evidence item | evidence class | key result | allowed claim | forbidden interpretation |
| --- | --- | --- | --- | --- |
| Human review reliability | reliability | Coach A/B both reviewed 350 rows; within-1 overall agreement 0.8429; priority60 has 22 `new_label` rows. | Pedagogical judgment is rater-sensitive; double review and sensitivity reporting are necessary. | Coach A, Coach B, or priority60 is final gold. |
| Main scaffold table | main result | Bridge Contract compact + Guard/Repair has highest primary-view overall and 0 major+answer leakage; DBox-inspired guard has 23/31 student-ready. | Quality-safety-burden trade-off; DBox is a strong baseline. | Bridge Contract comprehensively wins every dimension. |
| Repair same-candidate stress | stress test | Leakage severity improved/same/worsened: 16/14/0; major leakage 7/30 -> 0/30; burden worsened 12/30. | Repair reduces leakage in fixed-candidate stress testing with burden trade-off. | Main experiment means alone prove Repair causality; Repair has no cost. |
| DBox+Repair targeted add-on | fairness sensitivity | 20 cases; overall 3.55; safe-ready 11/20; major+answer leakage 0. | DBox+Repair addresses fairness sensitivity and can reduce high-severity leakage on targeted rows. | DBox+Repair is a full 50-case double-coach main condition. |
| DeepSeek LLM grader calibration | calibration | Case-specific judge improves some auxiliary metrics, but critical recall is 0 and major FN is 1.000. | LLM graders are auxiliary only; human review remains necessary. | LLM grader can replace human coaches. |
| Evidence manifest | artifact | Reports inputs, scripts, outputs, checksums, boundaries, and forbidden wording by claim. | Evidence package is auditable. | Manifest creates new experimental evidence. |

Caption draft:

```text
Evidence classes and claim boundaries. The paper separates main human-review results from sensitivity, stress-test, fairness, calibration, and artifact evidence to prevent overclaiming.
```

Source:

- `human_review_reliability_section_draft_20260517.md`
- `repair_same_candidate_stress_result_20260517.md`
- `dbox_guard_repair_fairness_report_20260517.md`
- `llm_grader_calibration_deepseek_sensitivity_report_20260518.md`
- `dialogue_state_v3_evidence_manifest_20260518.json`

## Appendix Table Pointers

Use appendix tables for:

- full slice tables;
- four rater views;
- observed error taxonomy distribution;
- Repair pair details;
- DBox+Repair targeted review details;
- DeepSeek LLM grader calibration details;
- evidence manifest checksums.

Do not move appendix-only all-50 sensitivity into the main headline.
