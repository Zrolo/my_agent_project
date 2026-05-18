# Paper Manuscript Assembly Map: Dialogue-State v3 20260518

## Scope

This document is an assembly map for turning the dialogue-state v3 research reports into a paper draft. It adds no experiments, changes no data, and does not connect online active mode. It only specifies which existing documents should feed each manuscript section and which evidence class each section may claim.

Use this together with:

- `dialogue_state_v3_paper_claims_final_gate_20260518.md`
- `dialogue_state_v3_evidence_manifest_20260518.json`
- `paper_figure_table_plan_dialogue_state_v3_20260518.md`
- `paper_citation_checklist_dialogue_state_v3_20260518.md`

## 1. Main Manuscript Assembly

| paper section | primary source docs | evidence class | allowed writing goal | required boundary |
| --- | --- | --- | --- | --- |
| Title / Abstract | `paper_abstract_conclusion_dialogue_state_v3_20260518.md` | paper framing | State missing bridge, critical bridge leakage, case-specific rubric, and bounded trade-off findings. | Do not write system victory or broad significant dominance. |
| 1 Introduction | `paper_intro_related_work_dialogue_state_v3_20260518.md`; `paper_scope_v2.zh.md` | framing | Motivate why no-direct-answer is not enough for CP tutoring. | This is an evaluation framework paper, not online deployment. |
| 2 Related Work | `paper_intro_related_work_dialogue_state_v3_20260518.md`; `paper_citation_checklist_dialogue_state_v3_20260518.md` | related work | Position against tutoring, programming help, DBox, EDF/Copa, LLM-as-judge, and agent eval. | Cite prior work only within the checked scope; do not claim reproduction. |
| 3 Benchmark And Review Protocol | `paper_methods_evaluation_dialogue_state_v3_20260518.md`; `evaluation_protocol_v3.md`; `response_review_rubric_v3.md` | methods | Define missing bridge, critical bridge leakage, taxonomy framing, slices, case-specific rubric, and blind review. | Main headline only uses `main_scaffold_eval`; concrete algorithms are surface anchors. |
| 4 Experimental Setup | `paper_methods_evaluation_dialogue_state_v3_20260518.md`; `baseline_protocol_v1.md`; `model_runtime_configuration_v1.md` | methods / setup | Describe the 7 offline harness conditions and model/runtime boundaries. | Guard-only is instrumentation; DBox is literature-inspired, not a reproduction. |
| 5 Results | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.md`; `dialogue_state_v3_main_paper_ready_tables_20260517.md`; `dialogue_state_v3_pairwise_win_tie_loss_20260517.md` | main result + support | Report human review reliability, main scaffold results, paired uncertainty, and slice sensitivity. | Use favorable trend / trade-off wording when uncertainty crosses zero. |
| 6 Stress, Fairness, And Calibration | `repair_same_candidate_stress_result_20260517.md`; `dbox_guard_repair_fairness_report_20260517.md`; `llm_grader_calibration_deepseek_sensitivity_report_20260518.md` | stress / sensitivity / calibration | Explain Repair causal evidence, DBox+Repair fairness sensitivity, and LLM grader limits. | Do not turn these into main-condition evidence or human-review replacement evidence. |
| 7 Discussion / Limitations | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.md`; `dialogue_state_v3_paper_claims_final_gate_20260518.md` | interpretation | State what the evidence supports and does not support. | Priority60 and Coach labels are expert reference views, not gold. |
| 8 Conclusion | `paper_abstract_conclusion_dialogue_state_v3_20260518.md` | closing | Summarize benchmark contribution and future work. | Do not imply the 50-case set covers all CP tutoring. |

## 2. Recommended Main-Text Flow

Use this section order unless a target venue requires a different structure:

1. Abstract.
2. Introduction.
3. Related Work.
4. CP-MissingBridgeBench: Task, concepts, and rubric.
5. Human Review Protocol and Conditions.
6. Main Results.
7. Pairwise Uncertainty and Sensitivity.
8. Stress / Fairness / Calibration.
9. Discussion and Limitations.
10. Conclusion.

The safest narrative is:

```text
No-direct-answer is necessary but not enough -> missing bridge makes the local tutoring risk explicit -> case-specific rubrics make the risk reviewable -> human review reveals quality-safety-burden trade-offs -> Bridge Contract compact + Guard/Repair shows favorable trends, while DBox is strong and several claims require sensitivity / stress / calibration boundaries.
```

## 3. Main Text vs Appendix

| item | main text use | appendix use |
| --- | --- | --- |
| `main_scaffold_eval` main table | Yes, headline result. | Full metric expansion if space is limited. |
| `main_eval_with_caution` | Mention as sensitivity only. | Full slice table. |
| `clarification_safety_slice` | Mention as separate safety slice. | Full slice table and examples. |
| `policy_safety_slice` | Mention as separate policy slice. | Full slice table and examples. |
| all-50 aggregate | No headline use. | Robustness / sensitivity only. |
| Coach A/B agreement | Summarize in Methods or Results. | Full reliability table. |
| priority60 adjudication | Summarize as high-priority disagreement handling. | Full adjudication outcome table. |
| observed error taxonomy | Short main-text paragraph. | Full Level 1 x Level 2 distribution. |
| Repair same-candidate stress | Main text if space allows, because it supports Repair causality. | Full pair details and protocol. |
| DBox+Repair 20-case add-on | Main text only as fairness sensitivity. | Full targeted review details. |
| DeepSeek LLM grader calibration | Main text limitation, not main result. | Full calibration metrics. |
| evidence manifest / checksums | Mention in reproducibility. | Full artifact table. |

## 4. Figure And Table Placement

Recommended compact main-text package:

1. Figure 1: CP-MissingBridgeBench evaluation flow.
2. Table 1: benchmark slices and condition boundaries.
3. Table 2: main scaffold results.
4. Table 3: paired W/T/L and uncertainty.
5. Table 4: evidence-boundary summary for reliability, Repair stress, DBox+Repair sensitivity, and DeepSeek LLM grader calibration.

If the paper has more space:

- Add a separate human-review reliability table.
- Add a Repair stress + DBox+Repair sensitivity table.
- Add a critical-bridge leakage boundary figure.

## 5. Copy Editing Guardrails

Before moving any paragraph into the manuscript, check:

- Does it call the 50-case set final gold? If yes, rewrite.
- Does it pool all 50 cases into the headline? If yes, rewrite.
- Does it say Guard-only rewrites or repairs final responses? If yes, rewrite.
- Does it infer Repair causality from main-condition means alone? If yes, rewrite.
- Does it describe DBox+Repair as a full main condition? If yes, rewrite.
- Does it treat DeepSeek or any LLM grader as a human-review replacement? If yes, rewrite.
- Does it reduce the taxonomy to DP/check/lazy/tree/local-code examples? If yes, rewrite.

## 6. Current Paper Package Status

Ready as section drafts:

- Abstract / Conclusion draft.
- Introduction / Related Work draft with candidate citation keys.
- Methods / Evaluation draft.
- Results / Discussion compact draft.
- Figure / Table plan.
- Citation checklist.
- Claim gate.
- Evidence manifest and reproduction scripts.

Still needs manuscript-production work:

1. Convert candidate citation keys into final BibTeX entries.
2. Decide venue-specific length and move overflow tables into appendix.
3. Render figures from the figure/table plan.
4. Assemble a single manuscript file.
5. Run the claim-gate scan on the assembled manuscript.
6. Decide whether to clean or explicitly exempt legacy bilingual-doc validator debt in any public artifact.

## 7. Final Pre-Submission Commands

Run from the project root:

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_submission.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 evals/aichat/validate_research_bilingual_docs.py --output-json /tmp/bilingual_docs_validation_submission.json
rg -n -e "Guard fixes final output" -e "Guard repairs" -e "significantly outperforms all baselines" -e "all 50 cases headline" -e "stable\\s+advantage" docs/research evals/aichat
```

If the final `rg` command hits forbidden-wording lists or historical negative examples, inspect them manually instead of treating every hit as a manuscript error.
