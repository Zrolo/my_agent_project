# Paper Manuscript Assembly Map: Dialogue-State v3 20260518

## 使用边界

本文档是把 dialogue-state v3 研究报告组装成论文草稿的 assembly map。它不新增实验、不修改数据、不接入线上 active mode。它只说明每个论文 section 应该从哪些已有文档取材，以及每一类证据最多能支撑什么说法。

请和以下文件一起使用：

- `dialogue_state_v3_paper_claims_final_gate_20260518.zh.md`
- `dialogue_state_v3_evidence_manifest_20260518.json`
- `paper_figure_table_plan_dialogue_state_v3_20260518.zh.md`
- `paper_citation_checklist_dialogue_state_v3_20260518.zh.md`

## 1. Main Manuscript Assembly

| paper section | primary source docs | evidence class | allowed writing goal | required boundary |
| --- | --- | --- | --- | --- |
| Title / Abstract | `paper_abstract_conclusion_dialogue_state_v3_20260518.zh.md` | paper framing | 说明 missing bridge、critical bridge leakage、case-specific rubric 和克制的 trade-off 结果。 | 不写系统胜利或 broad significant dominance。 |
| 1 Introduction | `paper_intro_related_work_dialogue_state_v3_20260518.zh.md`; `paper_scope_v2.zh.md` | framing | 说明为什么 no-direct-answer 不足以评测算法竞赛辅导。 | 本文是 evaluation framework paper，不是线上部署论文。 |
| 2 Related Work | `paper_intro_related_work_dialogue_state_v3_20260518.zh.md`; `paper_citation_checklist_dialogue_state_v3_20260518.zh.md` | related work | 对齐 tutoring、programming help、DBox、EDF/Copa、LLM-as-judge 和 agent eval。 | 相关工作只能按已核对范围引用；不声称 reproduction。 |
| 3 Benchmark And Review Protocol | `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md`; `evaluation_protocol_v3.zh.md`; `response_review_rubric_v3.zh.md` | methods | 定义 missing bridge、critical bridge leakage、taxonomy framing、slices、case-specific rubric 和 blind review。 | 主 headline 只用 `main_scaffold_eval`；具体算法只是 surface anchors。 |
| 4 Experimental Setup | `paper_methods_evaluation_dialogue_state_v3_20260518.zh.md`; `baseline_protocol_v1.zh.md`; `model_runtime_configuration_v1.zh.md` | methods / setup | 描述 7 个 offline harness conditions 和模型/运行边界。 | Guard-only 是 instrumentation；DBox 是 literature-inspired，不是 reproduction。 |
| 5 Results | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.zh.md`; `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`; `dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md` | main result + support | 报告 human review reliability、main scaffold results、paired uncertainty 和 slice sensitivity。 | uncertainty 跨 0 时只写 favorable trend / trade-off。 |
| 6 Stress, Fairness, And Calibration | `repair_same_candidate_stress_result_20260517.zh.md`; `dbox_guard_repair_fairness_report_20260517.zh.md`; `llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md` | stress / sensitivity / calibration | 解释 Repair 因果证据、DBox+Repair fairness sensitivity 和 LLM grader 限制。 | 不把这些写成 main-condition evidence 或替代人审证据。 |
| 7 Discussion / Limitations | `paper_results_discussion_submission_compact_dialogue_state_v3_20260518.zh.md`; `dialogue_state_v3_paper_claims_final_gate_20260518.zh.md` | interpretation | 说明当前证据能支持什么、不能支持什么。 | Priority60 和 Coach labels 是 expert reference views，不是 gold。 |
| 8 Conclusion | `paper_abstract_conclusion_dialogue_state_v3_20260518.zh.md` | closing | 总结 benchmark contribution 和 future work。 | 不暗示 50-case set 覆盖所有算法竞赛辅导。 |

## 2. Recommended Main-Text Flow

除非目标 venue 有强制结构，建议使用：

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

最安全的叙事线：

```text
No-direct-answer 是必要但不充分 -> missing bridge 把局部教学风险显式化 -> case-specific rubric 让这个风险可评审 -> human review 揭示 quality-safety-burden trade-off -> Bridge Contract compact + Guard/Repair 呈现 favorable trends，同时 DBox 是强 baseline，若干结论必须通过 sensitivity / stress / calibration 限定。
```

## 3. Main Text vs Appendix

| item | main text use | appendix use |
| --- | --- | --- |
| `main_scaffold_eval` main table | 是，作为 headline result。 | 空间不足时放完整指标扩展。 |
| `main_eval_with_caution` | 只作为 sensitivity 提及。 | 完整 slice table。 |
| `clarification_safety_slice` | 作为独立 safety slice 提及。 | 完整 slice table 和 examples。 |
| `policy_safety_slice` | 作为独立 policy slice 提及。 | 完整 slice table 和 examples。 |
| all-50 aggregate | 不作为 headline。 | 只作为 robustness / sensitivity。 |
| Coach A/B agreement | Methods 或 Results 中摘要。 | 完整 reliability table。 |
| priority60 adjudication | 作为高优先级分歧处理摘要。 | 完整 adjudication outcome table。 |
| observed error taxonomy | 主文短段落。 | 完整 Level 1 x Level 2 distribution。 |
| Repair same-candidate stress | 如果篇幅允许应进主文，因为支撑 Repair causality。 | 完整 pair details 和 protocol。 |
| DBox+Repair 20-case add-on | 主文只作为 fairness sensitivity。 | 完整 targeted review details。 |
| DeepSeek LLM grader calibration | 主文作为 limitation，不作为主结果。 | 完整 calibration metrics。 |
| evidence manifest / checksums | reproducibility 中提及。 | 完整 artifact table。 |

## 4. Figure And Table Placement

推荐主文紧凑图表组合：

1. Figure 1: CP-MissingBridgeBench evaluation flow.
2. Table 1: benchmark slices and condition boundaries.
3. Table 2: main scaffold results.
4. Table 3: paired W/T/L and uncertainty.
5. Table 4: evidence-boundary summary for reliability, Repair stress, DBox+Repair sensitivity, and DeepSeek LLM grader calibration.

如果篇幅更宽：

- 增加单独的 human-review reliability table。
- 增加 Repair stress + DBox+Repair sensitivity table。
- 增加 critical-bridge leakage boundary figure。

## 5. Copy Editing Guardrails

任何段落放入正式 manuscript 前，检查：

- 是否把 50-case set 叫做 final gold？如果是，改写。
- 是否把 all 50 cases 混成 headline？如果是，改写。
- 是否说 Guard-only rewrites 或 repairs final responses？如果是，改写。
- 是否从 main-condition means 直接推出 Repair causality？如果是，改写。
- 是否把 DBox+Repair 写成 full main condition？如果是，改写。
- 是否把 DeepSeek 或任何 LLM grader 写成人审替代？如果是，改写。
- 是否把 taxonomy 降回 DP/check/lazy/tree/local-code 具体例子列表？如果是，改写。

## 6. Current Paper Package Status

已经可作为 section drafts：

- Abstract / Conclusion draft。
- Introduction / Related Work draft with candidate citation keys。
- Methods / Evaluation draft。
- Results / Discussion compact draft。
- Figure / Table plan。
- Citation checklist。
- Claim gate。
- Evidence manifest and reproduction scripts。

仍需要 manuscript-production work：

1. 将 candidate citation keys 转成最终 BibTeX 条目。
2. 决定目标 venue 篇幅，并把超出主文空间的表放入 appendix。
3. 根据 figure/table plan 绘制图。
4. 组装单一 manuscript file。
5. 对组装后的 manuscript 跑 claim-gate scan。
6. 决定 public artifact 是否清理 legacy bilingual-doc validator debt，或在 README 中明确 exemption。

## 7. Final Pre-Submission Commands

在项目根目录运行：

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_submission.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 evals/aichat/validate_research_bilingual_docs.py --output-json /tmp/bilingual_docs_validation_submission.json
rg -n -e "Guard fixes final output" -e "Guard repairs" -e "significantly outperforms all baselines" -e "all 50 cases headline" -e "stable\\s+advantage" docs/research evals/aichat
```

如果最后的 `rg` 命中 forbidden-wording lists 或历史负例，需要人工检查语境，不要把所有命中都视为 manuscript error。
