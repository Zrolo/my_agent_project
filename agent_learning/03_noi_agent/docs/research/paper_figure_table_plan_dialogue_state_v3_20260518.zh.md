# Paper Figure / Table Plan: Dialogue-State v3 20260518

## 使用边界

本文档只规划论文正文和附录图表，不新增实验、不修改数据、不改变结果解释口径。所有 headline 图表必须遵守：

- 主结果只使用 `main_scaffold_eval` + `priority60 adjudicated + Coach A`。
- all-50 aggregate 只能作为 sensitivity / appendix。
- Guard-only 必须标为 instrumentation / runtime signal，不是 rewrite。
- Repair 因果证据只来自 same-candidate stress test。
- DBox+Repair 是 targeted fairness sensitivity，不是 full main condition。
- LLM grader 是 auxiliary calibration，不是 human review replacement。

## 正文图

| id | title | goal | source | must show | must not imply |
| --- | --- | --- | --- | --- | --- |
| Figure 1 | CP-MissingBridgeBench evaluation flow | 展示从学生轮次到 case-specific rubric、人审和 evidence classes 的整体流程。 | `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md`; `dialogue_state_v3_evidence_manifest_20260518.json` | student turn -> missing bridge rubric -> tutor harness responses -> blind human review -> sensitivity / stress / calibration evidence。 | 不要画成线上 active-mode 部署流程；不要暗示 Guard-only 改写最终回复。 |
| Figure 2 | Critical bridge leakage boundary | 解释 answer leakage、critical bridge leakage、acceptable reveal 和 helpful scaffold 的边界。 | `response_review_rubric_v3.zh.md`; `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md` | 没给完整代码/题解也可能泄露关键中间推理；case-specific rubric 决定边界。 | 不要把所有有信息量的解释都画成泄露；不要把 taxonomy 画成具体算法列表。 |
| Figure 3 | Evidence classes and claim boundaries | 帮 reviewer 快速区分 main result、sensitivity、stress test、fairness add-on 和 calibration。 | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.zh.md`; `dialogue_state_v3_paper_claims_final_gate_20260518.zh.md` | main result = main scaffold; Repair = stress; DBox+Repair = sensitivity; LLM grader = calibration。 | 不要把 stress test 或 calibration 画成主实验 condition。 |

如果篇幅紧，正文只保留 Figure 1；Figure 2 和 Figure 3 放 appendix 或合并成一张 claim-boundary schematic。

## 正文表

| id | title | evidence class | source files / scripts | required fields | allowed claim | forbidden wording |
| --- | --- | --- | --- | --- | --- | --- |
| Table 1 | Benchmark slices and paper use | methods / scope | `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md`; `dialogue_state_v3_50_context_readiness_audit_20260515.jsonl` | slice, case_n, paper use | 主 headline 只来自 `main_scaffold_eval`；其他 slices 是 sensitivity / appendix。 | all 50 cases headline; full CP tutoring coverage。 |
| Table 2 | Tutoring harness conditions and interpretation boundaries | methods / baseline | `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md`; `baseline_protocol_v1.zh.md` | condition, role, final-response boundary, paper interpretation | 7 个 condition 是离线 human-review harness；DBox 是 literature-inspired strong baseline。 | online deployed system; faithful DBox reproduction; Guard-only rewrite。 |
| Table 3 | Main scaffold results | main result | `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`; `reproduce_dialogue_state_v3_tables.py`; `verify_dialogue_state_v3_reports.py` | condition, overall, student-ready, safe-ready, major+answer leakage, scaffold sufficiency, burden | Bridge Contract compact + Guard/Repair 呈现有利 overall / high-severity leakage-control trend；DBox-inspired 是强 baseline。 | Bridge Contract 全面显著胜出；all-case 平均作为 headline。 |
| Table 4 | Paired W/T/L and uncertainty | main result support | `dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md`; paired uncertainty CSV/JSON; `reproduce_dialogue_state_v3_tables.py` | comparison, n, W/T/L, mean overall delta, CI, p, safe-ready delta, major+answer delta | 关键比较多支持 trend / trade-off；CI 跨 0 时不能写 significant dominance。 | absolute winner; significant dominance when CI crosses 0。 |
| Table 5 | Human review reliability | reliability | `human_review_reliability_section_draft_20260517.zh.md`; Coach A/B agreement JSON; priority60 adjudication files | overall exact, within-1, leakage exact, critical binary exact/kappa, rank agreement, priority60 outcomes | pedagogical judgment rater-sensitive；需要 double review、adjudication 和 sensitivity。 | Coach A/B/priority60 是 gold。 |
| Table 6 | Repair stress and DBox+Repair sensitivity | stress + sensitivity | `repair_same_candidate_stress_result_20260517.zh.md`; `dbox_guard_repair_fairness_report_20260517.zh.md`; summary JSON files | repair before/after leakage and burden; DBox+Repair 20-case overall/safe-ready/leakage; same-case comparison | Repair 在 same-candidate stress 中降低 leakage，但增加 burden；DBox+Repair 缓解 fairness concern。 | Repair 因果由主实验均值证明；DBox+Repair 是 full main condition。 |

如果正文篇幅只能放 4 张表，建议 Table 5 合并进 Methods / Appendix，Table 6 只保留关键 stress + sensitivity 数字。

## 附录表

| appendix id | title | source | role |
| --- | --- | --- | --- |
| Table A1 | Full slice tables | `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md` | 报告 `main_eval_with_caution`、`clarification_safety_slice`、`policy_safety_slice` 和 all-case sensitivity。 |
| Table A2 | Four rater views sensitivity | `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`; `dialogue_state_v3_main_scoring_sensitivity_20260517.zh.md` | Coach A only、Coach B only、priority60+CoachA、priority60+CoachB。 |
| Table A3 | Observed error taxonomy distribution | `dialogue_state_v3_observed_error_taxonomy_20260517.zh.md` | Level 1 failure type x condition; Level 1 x Level 2 coverage。 |
| Table A4 | Repair same-candidate pair details | `repair_same_candidate_stress_result_20260517.zh.md`; candidate/key/summary CSV/JSON | before/after blind review details, leakage delta, burden delta。 |
| Table A5 | DBox+Repair 20-case targeted add-on details | `dbox_guard_repair_fairness_report_20260517.zh.md` | 说明 targeted sensitivity set 的抽样与 protocol mismatch。 |
| Table A6 | DeepSeek LLM grader calibration | `llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md` | likert-only、generic rubric、case-specific rubric 的 auxiliary metrics；强调 critical recall 风险。 |
| Table A7 | Evidence manifest checksums | `dialogue_state_v3_evidence_manifest_20260518.json` | 复核 report、input、script、output、checksum 和 interpretation boundary。 |

## 图表顺序建议

正文最稳顺序：

1. Figure 1：先给方法流程，降低 reviewer 对系统边界的误解。
2. Table 1：锁定 slices，防止 all-50 headline。
3. Table 2：锁定 conditions，防止把 Guard-only / DBox / online status 写错。
4. Table 3：主结果。
5. Table 4：paired uncertainty，紧跟主结果防止过度解读。
6. Table 5：human review reliability，或放 Methods 后半段。
7. Table 6：Repair stress + DBox+Repair sensitivity，放 Results 后段或 Discussion 前。

## 写作提醒

- 表题中优先使用 `main_scaffold_eval`、`sensitivity`、`stress test`、`calibration` 这些证据类别词。
- 表注必须写明 `priority60 adjudicated + Coach A` 是主参考口径，不是 final gold。
- Repair 表注必须写明 same-candidate stress，而不是主 condition 均值。
- LLM grader 表注必须写明 DeepSeek critical recall 为 0，不能替代人审。
- DBox+Repair 表注必须写明 20-case targeted add-on，不是 full 50-case double-coach validation。

## 最小投稿版本

如果目标是先快速产出一版短论文，最小图表集为：

1. Figure 1：evaluation flow。
2. Table 1：slices + conditions，可合并 slices 与 condition boundaries。
3. Table 2：main scaffold results。
4. Table 3：paired uncertainty。
5. Table 4：reliability + Repair stress + DBox+Repair + LLM grader limitations 的 compact evidence-boundary table。

这个最小版本仍然必须在正文或 appendix 中保留完整 sensitivity 和 reproduction references。
