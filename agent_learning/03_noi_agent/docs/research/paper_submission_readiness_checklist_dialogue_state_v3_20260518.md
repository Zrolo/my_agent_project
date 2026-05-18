# Paper Submission Readiness Checklist: Dialogue-State v3 20260518

## Scope

This checklist summarizes the current submission readiness of the dialogue-state v3 paper package. It adds no experiments, changes no data, and does not connect online active mode. It is meant to guide external AI review, human collaborator review, and final manuscript production.

## Overall Verdict

```text
Ready for external evidence audit and manuscript drafting.
Not yet camera-ready submission.
```

The evidence package is strong enough to support a bounded evaluation-framework paper, but final submission still needs venue-specific formatting, checked BibTeX entries, rendered figures/tables, and one final claim-gate scan on the assembled manuscript.

## 1. Evidence Readiness

| component | status | reason | remaining action |
| --- | --- | --- | --- |
| 50-case dialogue-state v3 package | ready as formal evidence candidate | 50 reviewed candidate cases, 7 conditions, 350 responses. | Do not call it full CP tutoring coverage or final gold. |
| Human review | ready with reliability reporting | Coach A and Coach B completed all 350 reviews; priority60 adjudication done. | Report rater sensitivity and do not treat one coach as gold. |
| Main result tables | ready | Paper-ready tables and reproduction script exist. | Use only `main_scaffold_eval` as headline. |
| Paired uncertainty | ready | W/T/L, mean deltas, CI, and paired tests available. | Use favorable trend / trade-off wording when CI crosses 0. |
| Slice sensitivity | ready | Main, caution, clarification, policy, and all-50 sensitivity views are separated. | Keep all-50 aggregate in appendix / sensitivity. |
| Observed error taxonomy | ready | Taxonomy lifted to failure type x cognitive bridge family x surface anchor. | Describe as observed operational taxonomy, not universal taxonomy. |
| Repair same-candidate stress | ready as stress evidence | 30-pair before/after review supports leakage reduction with burden trade-off. | Attribute Repair causality only to this stress test. |
| DBox+Repair fairness | ready as targeted sensitivity | 20-case headline-sensitive add-on exists. | Do not write as full 50-case double-coach main condition. |
| DeepSeek LLM grader calibration | ready as limitation evidence | Calibration shows auxiliary promise but critical recall remains 0. | Do not use LLM grader as human-review replacement. |
| Evidence manifest / reproduction | ready | Manifest, checksums, verify script, reproduce script, and unit tests exist. | Run commands again on final artifact. |

## 2. Manuscript Draft Readiness

| artifact | status | file |
| --- | --- | --- |
| Abstract / Conclusion draft | ready as safe draft | `paper_abstract_conclusion_dialogue_state_v3_20260518.md` |
| Introduction / Related Work draft | ready with candidate citation keys | `paper_intro_related_work_dialogue_state_v3_20260518.md` |
| Citation checklist | ready for bibliography audit | `paper_citation_checklist_dialogue_state_v3_20260518.md` |
| Methods / Evaluation draft | ready as draft source | `paper_methods_evaluation_dialogue_state_v3_20260518.md` |
| Results / Discussion compact draft | ready as draft source | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.md` |
| Figure / Table plan | ready as production plan | `paper_figure_table_plan_dialogue_state_v3_20260518.md` |
| Manuscript assembly map | ready | `paper_manuscript_assembly_map_dialogue_state_v3_20260518.md` |
| Single-file manuscript skeleton | ready as review draft | `paper_submission_manuscript_dialogue_state_v3_20260518.md` |
| Appendix skeleton | ready as supplement plan | `paper_appendix_skeleton_dialogue_state_v3_20260518.md` |
| Claim gate | ready | `dialogue_state_v3_paper_claims_final_gate_20260518.md` |

## 3. Not Yet Camera-Ready

These tasks remain before real submission:

1. Convert candidate citation keys into final BibTeX entries.
2. Verify each citation against source PDF / proceedings / DOI / official BibTeX.
3. Decide target venue and page limit.
4. Move overflow tables from main text into appendix.
5. Render Figure 1 and any optional boundary / evidence-class figures.
6. Format tables for the venue template.
7. Run the final claim-gate scan on the assembled manuscript.
8. Decide whether public artifact packaging should include an explicit legacy bilingual-doc exemption.
9. If distributing a web-review bundle, ensure required test dependencies are included or documented.

## 4. Current Safe Claims

Can write:

- CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
- Missing bridge and critical bridge leakage are useful evaluation objects beyond direct answer/code leakage.
- DBox-inspired decomposition is a strong baseline.
- No-direct-solution prompting does not eliminate critical bridge leakage.
- Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view.
- Repair reduces leakage in same-candidate stress testing, with a student-burden trade-off.
- DeepSeek LLM grader calibration supports auxiliary use only; human review remains necessary.

Must not write:

- Bridge Contract significantly and comprehensively outperforms all baselines.
- Guard-only rewrites, repairs, or fixes final student-visible responses.
- Repair causality is proven by main-experiment condition means alone.
- Coach A, Coach B, or priority60 labels are final gold.
- all-50 aggregate is the headline result.
- DBox+Repair has full 50-case double-coach main validation.
- LLM graders can replace human coaches.
- The taxonomy only covers DP/check/lazy/tree/local-code scenes.

## 5. Recommended Review Order for Another AI

Ask the external AI to review in this order:

1. `docs/research/index.md`
2. `paper_submission_manuscript_dialogue_state_v3_20260518.md`
3. `paper_appendix_skeleton_dialogue_state_v3_20260518.md`
4. `dialogue_state_v3_paper_claims_final_gate_20260518.md`
5. `dialogue_state_v3_evidence_manifest_20260518.json`
6. `dialogue_state_v3_main_paper_ready_tables_20260517.md`
7. `dialogue_state_v3_pairwise_win_tie_loss_20260517.md`
8. `repair_same_candidate_stress_result_20260517.md`
9. `dbox_guard_repair_fairness_report_20260517.md`
10. `llm_grader_calibration_deepseek_sensitivity_report_20260518.md`

Then ask it to run or inspect outputs from:

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_submission.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 evals/aichat/validate_research_bilingual_docs.py --output-json /tmp/bilingual_docs_validation_submission.json
```

## 6. Known Non-Blocking Issues

- The bilingual docs validator still reports historical / legacy unpaired docs.
- This does not change the dialogue-state v3 evidence numbers.
- New paper-facing dialogue-state v3 docs should remain paired, and the current manuscript / appendix / checklist docs are paired.
- Some older `evals/aichat/ad_hoc_runs/` directories remain untracked locally and should not be confused with paper-facing evidence unless listed in the manifest.

## 7. Readiness Decision

For the current phase:

```text
Proceed to external evidence audit and manuscript editing.
Do not start new main experiments.
Do not connect online active mode.
Do not strengthen claims beyond the claim gate.
```
