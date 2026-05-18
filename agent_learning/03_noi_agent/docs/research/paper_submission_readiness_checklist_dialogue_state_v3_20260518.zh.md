# Paper Submission Readiness Checklist: Dialogue-State v3 20260518

## 使用边界

本文档总结 dialogue-state v3 论文包当前的投稿准备状态。它不新增实验、不修改数据、不接入线上 active mode。它用于指导 external AI review、人类合作者审查和最终 manuscript production。

## Overall Verdict

```text
Ready for external evidence audit and manuscript drafting.
Not yet camera-ready submission.
```

当前 evidence package 足以支持一篇边界克制的 evaluation-framework paper，但真正投稿前仍需要 venue-specific formatting、核对后的 BibTeX、渲染后的 figures/tables，以及对最终 assembled manuscript 做一次 claim-gate scan。

## 1. Evidence Readiness

| component | status | reason | remaining action |
| --- | --- | --- | --- |
| 50-case dialogue-state v3 package | ready as formal evidence candidate | 50 reviewed candidate cases、7 conditions、350 responses。 | 不要称为 full CP tutoring coverage 或 final gold。 |
| Human review | ready with reliability reporting | Coach A 和 Coach B 完成全部 350 reviews；priority60 adjudication 已完成。 | 报告 rater sensitivity，不把任一教练当 gold。 |
| Main result tables | ready | 已有 paper-ready tables 和 reproduction script。 | 只用 `main_scaffold_eval` 做 headline。 |
| Paired uncertainty | ready | 已有 W/T/L、mean deltas、CI 和 paired tests。 | CI 跨 0 时写 favorable trend / trade-off。 |
| Slice sensitivity | ready | Main、caution、clarification、policy 和 all-50 sensitivity views 已分开。 | all-50 aggregate 只放 appendix / sensitivity。 |
| Observed error taxonomy | ready | Taxonomy 已提升到 failure type x cognitive bridge family x surface anchor。 | 写成 observed operational taxonomy，不写成 universal taxonomy。 |
| Repair same-candidate stress | ready as stress evidence | 30-pair before/after review 支持 leakage reduction with burden trade-off。 | Repair 因果只引用该 stress test。 |
| DBox+Repair fairness | ready as targeted sensitivity | 已有 20-case headline-sensitive add-on。 | 不写成 full 50-case double-coach main condition。 |
| DeepSeek LLM grader calibration | ready as limitation evidence | Calibration 显示有辅助价值，但 critical recall 仍为 0。 | 不把 LLM grader 当作 human-review replacement。 |
| Evidence manifest / reproduction | ready | 已有 manifest、checksums、verify script、reproduce script 和 unit tests。 | 最终 artifact 上再跑一次命令。 |

## 2. Manuscript Draft Readiness

| artifact | status | file |
| --- | --- | --- |
| Abstract / Conclusion draft | ready as safe draft | `paper_abstract_conclusion_dialogue_state_v3_20260518.zh.md` |
| Introduction / Related Work draft | ready with candidate citation keys | `paper_intro_related_work_dialogue_state_v3_20260518.zh.md` |
| Citation checklist | ready for bibliography audit | `paper_citation_checklist_dialogue_state_v3_20260518.zh.md` |
| Methods / Evaluation draft | ready as draft source | `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md` |
| Results / Discussion compact draft | ready as draft source | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.zh.md` |
| Figure / Table plan | ready as production plan | `paper_figure_table_plan_dialogue_state_v3_20260518.zh.md` |
| Manuscript assembly map | ready | `paper_manuscript_assembly_map_dialogue_state_v3_20260518.zh.md` |
| Single-file manuscript skeleton | ready as review draft | `paper_submission_manuscript_dialogue_state_v3_20260518.zh.md` |
| Appendix skeleton | ready as supplement plan | `paper_appendix_skeleton_dialogue_state_v3_20260518.zh.md` |
| Claim gate | ready | `dialogue_state_v3_paper_claims_final_gate_20260518.zh.md` |

## 3. Not Yet Camera-Ready

真正投稿前仍需完成：

1. 将 candidate citation keys 转成最终 BibTeX entries。
2. 对照 source PDF / proceedings / DOI / official BibTeX 核对每个 citation。
3. 决定目标 venue 和 page limit。
4. 将超出主文篇幅的 tables 移入 appendix。
5. 渲染 Figure 1 和可选的 boundary / evidence-class figures。
6. 按 venue template 格式化 tables。
7. 对最终 assembled manuscript 跑 claim-gate scan。
8. 决定 public artifact packaging 是否需要明确 legacy bilingual-doc exemption。
9. 如果分发 web-review bundle，确保所需 test dependencies 已包含或在 README 中说明。

## 4. Current Safe Claims

可以写：

- CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
- Missing bridge and critical bridge leakage are useful evaluation objects beyond direct answer/code leakage.
- DBox-inspired decomposition is a strong baseline.
- No-direct-solution prompting does not eliminate critical bridge leakage.
- Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view.
- Repair reduces leakage in same-candidate stress testing, with a student-burden trade-off.
- DeepSeek LLM grader calibration supports auxiliary use only; human review remains necessary.

不能写：

- Bridge Contract significantly and comprehensively outperforms all baselines.
- Guard-only rewrites, repairs, or fixes final student-visible responses.
- Repair causality is proven by main-experiment condition means alone.
- Coach A、Coach B 或 priority60 labels 是 final gold。
- all-50 aggregate 是 headline result。
- DBox+Repair has full 50-case double-coach main validation.
- LLM graders can replace human coaches.
- The taxonomy only covers DP/check/lazy/tree/local-code scenes.

## 5. Recommended Review Order for Another AI

建议让外部 AI 按这个顺序审：

1. `docs/research/index.md`
2. `paper_submission_manuscript_dialogue_state_v3_20260518.zh.md`
3. `paper_appendix_skeleton_dialogue_state_v3_20260518.zh.md`
4. `dialogue_state_v3_paper_claims_final_gate_20260518.zh.md`
5. `dialogue_state_v3_evidence_manifest_20260518.json`
6. `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`
7. `dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md`
8. `repair_same_candidate_stress_result_20260517.zh.md`
9. `dbox_guard_repair_fairness_report_20260517.zh.md`
10. `llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md`

然后让它运行或检查这些命令输出：

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_submission.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 evals/aichat/validate_research_bilingual_docs.py --output-json /tmp/bilingual_docs_validation_submission.json
```

## 6. Known Non-Blocking Issues

- Bilingual docs validator 仍会报告 historical / legacy unpaired docs。
- 这不改变 dialogue-state v3 evidence numbers。
- 新增 paper-facing dialogue-state v3 docs 应保持中英文成对；当前 manuscript / appendix / checklist docs 已成对。
- 本地仍有一些旧的 `evals/aichat/ad_hoc_runs/` untracked directories，除非列入 manifest，否则不要把它们当作 paper-facing evidence。

## 7. Readiness Decision

当前阶段结论：

```text
Proceed to external evidence audit and manuscript editing.
Do not start new main experiments.
Do not connect online active mode.
Do not strengthen claims beyond the claim gate.
```
