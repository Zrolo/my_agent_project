# Research v1 Index

本文件是 `codex/bridge-research-annotation` 分支的 Research v1 总入口。它只描述当前研究线的边界、数据流和下一步实验，不表示这些能力已经接入线上学生 AIChat。

## Current Checkpoint

- Branch: `codex/bridge-research-annotation`
- Last pushed checkpoint before this cleanup: `42c17d5 Add bridge tutor evaluation workflow`
- Current online AIChat status: 仍以 `chat()` 为入口，主要由 rules、legacy learning phase judge、Pedagogical Judge v2 soft control、main LLM、自报 level hard gate 和 output guards 组成。
- Research v1 status: 已有离线 Bridge Judge、Bridge Contract Tutor、Leakage Judge、Repair、risk routing policy、response blind review 和 latency/error 统计雏形。

## Scope

Research v1 的目标是做出可标注、可评测、可消融的算法竞赛 AI 辅导研究框架。论文主线建议固定为：

```text
CP-MissingBridgeBench:
Turn-level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation
for LLM Tutors in Competitive Programming
```

Research v1 包含：

- CP-specific missing bridge schema；
- critical bridge leakage 定义与评测；
- 教练 turn-level 标注、双标与裁决流程；
- compact runtime bridge contract；
- current_system deployment baseline、strong prompt-only baseline、literature-inspired baseline、bridge_contract、guard、repair 的离线消融；
- response blind review；
- latency、LLM calls、stage errors 等产品可行性指标。

Research v1 不包含：

- full multi-judge every turn 的线上默认路径；
- Repair 自动修改 system prompt；
- 自动 prompt patch 上线；
- 长期学生 memory layer；
- 完整 NOI/OI 算法 ontology；
- 把控制论作为论文主创新点；
- 把 single-coach label 称为唯一真值。

详细边界见 [research_v1_scope_lock.md](research_v1_scope_lock.md)。

外部审查方案见 [research_v1_external_review_plan_20260511.zh.md](research_v1_external_review_plan_20260511.zh.md)。

## Core Documents

### Paper Scope And Evidence

- [paper_scope_v2.zh.md](paper_scope_v2.zh.md): 当前论文主线、研究问题、实验矩阵和不应声称的内容。
- [claims_and_evidence_matrix_v1.zh.md](claims_and_evidence_matrix_v1.zh.md): 每个论文 claim 对应的当前证据、缺口和下一步实验。
- [implementation_status_matrix_20260511.zh.md](implementation_status_matrix_20260511.zh.md): 当前线上、离线、shadow/proposed 和未实现模块的状态矩阵。
- [baseline_protocol_v1.zh.md](baseline_protocol_v1.zh.md): 中文 baseline protocol，定义 deployment baseline、强 prompt baseline、文献启发 baseline、Bridge Contract 方法组和 shuffled/oracle 负控。
- [baseline_protocol_v1.md](baseline_protocol_v1.md): English baseline protocol.
- [baseline_strategy_v1.zh.md](baseline_strategy_v1.zh.md): 中文 baseline strategy，说明为什么 `current_system` 不能作为唯一科研 baseline，以及强 baseline 胜出时论文结论如何保持稳健。
- [baseline_strategy_v1.md](baseline_strategy_v1.md): English baseline strategy.
- [dbox_reproduction_gap_v1.zh.md](dbox_reproduction_gap_v1.zh.md): 中文 DBox-inspired baseline 边界说明，明确当前实现不是 DBox reproduction。
- [dbox_reproduction_gap_v1.md](dbox_reproduction_gap_v1.md): English DBox-inspired baseline boundary note.
- [dbox_official_materials_review_v1.zh.md](dbox_official_materials_review_v1.zh.md): 中文 DBox 官方材料包 review，记录 prompts/source 对 DBox-inspired baseline 的影响。
- [dbox_official_materials_review_v1.md](dbox_official_materials_review_v1.md): English review of the official DBox supplementary package.

### Current System

- [aichat_current_flow_v1.md](aichat_current_flow_v1.md): 当前线上 AIChat 真实调用链快照。
- [field_usage_registry_v1.md](field_usage_registry_v1.md): bridge、focus、help level 等字段的定义、写入、读取和学生可见影响。
- [aichat_risk_routing_policy_v1.md](aichat_risk_routing_policy_v1.md): risk-triggered routing policy 草案。
- [control_harness_policy_v1.md](control_harness_policy_v1.md): feedback-control-inspired harness 的慢变量、中变量、快变量与上线边界。

### Annotation

- [coach_seed_labeling_workbook_v2.md](coach_seed_labeling_workbook_v2.md): 教练 seed 标注表说明。
- [annotation_reliability_protocol_v1.md](annotation_reliability_protocol_v1.md): single-coach reference、double annotation、adjudicated gold 的解释与流程。
- [schema_mapping_human_to_runtime_v1.md](schema_mapping_human_to_runtime_v1.md): 人类细标注 schema 与 runtime compact contract 的映射。
- [bridge_schema_annotation_guide_v1.md](bridge_schema_annotation_guide_v1.md): bridge schema 标注指导。
- [response_review_rubric_v2.zh.md](response_review_rubric_v2.zh.md): AIChat 回复盲评中文评分标准，包含新增总体质量、是否愿意给学生看、评分置信度和示例。
- [response_review_rubric_v2.md](response_review_rubric_v2.md): English response blind-review rubric v2.

### Runtime Contract And Registries

- [runtime_bridge_contract_schema_v1.json](runtime_bridge_contract_schema_v1.json): 运行时 compact bridge contract schema。
- [bridge_subtype_registry_v2.json](bridge_subtype_registry_v2.json): bridge subtype 与 family 的注册表。
- [focus_registry_v1.json](focus_registry_v1.json): 当前 focus registry。

### Offline Evaluation

- [bridge_judge_offline_eval_v1.md](bridge_judge_offline_eval_v1.md): 离线 Bridge Judge / Tutor / Guard / Repair 评测设计。
- [agent_eval_methodology_v1.zh.md](agent_eval_methodology_v1.zh.md): 基于 agent eval 文章整理的中文评测方法论。
- [agent_eval_methodology_v1.md](agent_eval_methodology_v1.md): English agent-eval methodology mapping for Research v1.
- [llm_judge_calibration_protocol_v1.zh.md](llm_judge_calibration_protocol_v1.zh.md): LLM Judge / Offline Grader 校准协议，包含 UNKNOWN、false positive/negative 和 prompt freeze 要求。
- [judge_schema_smoke_report_20260509.md](judge_schema_smoke_report_20260509.md): 20-case judge schema smoke 结果。
- [response_ablation_smoke_report_20260509.md](response_ablation_smoke_report_20260509.md): response ablation smoke 结果。
- [tutor_thinking_ablation_smoke_report_20260509.md](tutor_thinking_ablation_smoke_report_20260509.md): thinking mode smoke 结果。
- [single_llm_structured_smoke_report_20260510.zh.md](single_llm_structured_smoke_report_20260510.zh.md): single-LLM structured baseline 中文 smoke 报告。
- [single_llm_structured_smoke_report_20260510.md](single_llm_structured_smoke_report_20260510.md): single-LLM structured baseline English smoke report.
- [single_llm_structured_strict_schema_smoke_report_20260510.zh.md](single_llm_structured_strict_schema_smoke_report_20260510.zh.md): single-LLM strict schema 中文 smoke 报告。
- [single_llm_structured_strict_schema_smoke_report_20260510.md](single_llm_structured_strict_schema_smoke_report_20260510.md): single-LLM strict schema English smoke report.
- [single_llm_structured_calibrated_smoke_report_20260510.zh.md](single_llm_structured_calibrated_smoke_report_20260510.zh.md): single-LLM scaffold calibration 中文 smoke 报告。
- [single_llm_structured_calibrated_smoke_report_20260510.md](single_llm_structured_calibrated_smoke_report_20260510.md): single-LLM scaffold calibration English smoke report.
- [single_llm_guard_smoke_report_20260511.zh.md](single_llm_guard_smoke_report_20260511.zh.md): single-LLM + Guard/Repair 中文 smoke 报告。
- [single_llm_guard_smoke_report_20260511.md](single_llm_guard_smoke_report_20260511.md): single-LLM + Guard/Repair English smoke report.
- [fair_baseline_smoke3_report_20260511.zh.md](fair_baseline_smoke3_report_20260511.zh.md): 4 个 Guard-enabled baseline 的 3-case 中文 smoke 报告。
- [fair_baseline_smoke3_report_20260511.md](fair_baseline_smoke3_report_20260511.md): 3-case fair baseline smoke report in English.
- [fair_mini_study_20_report_20260511.zh.md](fair_mini_study_20_report_20260511.zh.md): 7 个系统的 20-case 公平 mini-study 中文报告，包含 single-LLM + Guard/Repair 对照。
- [fair_mini_study_20_report_20260511.md](fair_mini_study_20_report_20260511.md): English report for the 7-system fair 20-case mini-study.
- [fair_mini_study_20_paired_analysis_20260511.zh.md](fair_mini_study_20_paired_analysis_20260511.zh.md): 20-case fair 盲评的中文配对分析，按 case 计算 win/tie/loss、student-ready 指标和 bootstrap CI。
- [fair_mini_study_20_paired_analysis_20260511.md](fair_mini_study_20_paired_analysis_20260511.md): English paired analysis for the fair 20-case blind review.
- [prompt_controlled_ablation_smoke_report_20260511.zh.md](prompt_controlled_ablation_smoke_report_20260511.zh.md): prompt-controlled ablation 中文 smoke 报告，用于区分 prompt effect、diagnosis effect 和 contract validity。
- [prompt_controlled_ablation_smoke_report_20260511.md](prompt_controlled_ablation_smoke_report_20260511.md): English prompt-controlled ablation smoke report.
- [prompt_controlled_ablation_blind_review_20260511.zh.md](prompt_controlled_ablation_blind_review_20260511.zh.md): prompt-controlled ablation 3-case 中文盲评分析。当前 pilot 显示强 prompt wording 本身贡献明显，同时 predicted contract 明显好于 shuffled contract。
- [prompt_controlled_ablation_blind_review_20260511.md](prompt_controlled_ablation_blind_review_20260511.md): English blind-review analysis for the 3-case prompt-controlled ablation.
- [bridge_first_prompt_sanity_check_20260511.zh.md](bridge_first_prompt_sanity_check_20260511.zh.md): bridge-first / topic-second / focus-top-k prompt 原则的 3-case dev sanity check。
- [bridge_first_prompt_sanity_check_20260511.md](bridge_first_prompt_sanity_check_20260511.md): English bridge-first prompt sanity check.
- [literature_baseline_smoke1_report_20260511.zh.md](literature_baseline_smoke1_report_20260511.zh.md): 1-case 中文 smoke，检查 DBox-inspired、CodeHelp/CodeAid-style 和 Bridge-inspired baseline 的真实输出 schema 与早期泄露风险。
- [literature_baseline_smoke1_report_20260511.md](literature_baseline_smoke1_report_20260511.md): English 1-case smoke report for literature baselines.
- [mini_study_20_report_20260510.zh.md](mini_study_20_report_20260510.zh.md): 20 条 seed mini-study 中文初步报告。
- [mini_study_20_report_20260510.md](mini_study_20_report_20260510.md): 20-seed mini-study preliminary English report.
- [hard_gate_overfallback_rerun_20260510.zh.md](hard_gate_overfallback_rerun_20260510.zh.md): hard gate 过度兜底修复后的中文定点复测报告。
- [hard_gate_overfallback_rerun_20260510.md](hard_gate_overfallback_rerun_20260510.md): English targeted rerun report for the hard-gate overfallback fix.
- [repair_prompt_fix_mini_study_20_20260510.zh.md](repair_prompt_fix_mini_study_20_20260510.zh.md): Repair prompt 修复后的 20 条中文复测报告。
- [repair_prompt_fix_mini_study_20_20260510.md](repair_prompt_fix_mini_study_20_20260510.md): English 20-case rerun report after the repair prompt fix.
- [repair_stress_v1_smoke_report_20260511.zh.md](repair_stress_v1_smoke_report_20260511.zh.md): 12-case Repair stress 中文 smoke 报告，专门测试高泄露候选回复的 detect -> repair -> second-pass guard 链路。
- [repair_stress_v1_smoke_report_20260511.md](repair_stress_v1_smoke_report_20260511.md): English report for the 12-case Repair stress smoke.

### Response Blind Review

- [coach_response_review_analysis_20260509.zh.md](coach_response_review_analysis_20260509.zh.md): 中文盲评小样本分析。
- [coach_response_review_analysis_20260509.md](coach_response_review_analysis_20260509.md): English blind review mini-analysis.
- [coach_response_review_micro_example_policy_n10_20260510.zh.md](coach_response_review_micro_example_policy_n10_20260510.zh.md): micro-example policy 中文分析。
- [coach_response_review_micro_example_policy_n10_20260510.md](coach_response_review_micro_example_policy_n10_20260510.md): micro-example policy English analysis.
- [coach_response_review_analysis_mini_study_20_20260510.zh.md](coach_response_review_analysis_mini_study_20_20260510.zh.md): 20-case mini-study 回复盲评中文分析。
- [coach_response_review_analysis_mini_study_20_20260510.md](coach_response_review_analysis_mini_study_20_20260510.md): 20-case mini-study response blind-review English analysis.
- [coach_response_review_analysis_fair_mini_study_20_20260511.zh.md](coach_response_review_analysis_fair_mini_study_20_20260511.zh.md): 7-system fair 20-case 回复盲评中文分析，基于新版 v2 rubric。
- [coach_response_review_analysis_fair_mini_study_20_20260511.md](coach_response_review_analysis_fair_mini_study_20_20260511.md): English analysis for the 7-system fair 20-case response blind review.
- [coach_response_review_labels_fair_mini_study_20_20260511.jsonl](coach_response_review_labels_fair_mini_study_20_20260511.jsonl): 7-system fair 20-case 盲评标签 JSONL，保留匿名回复 ID 和系统 key 映射后的系统条件。
- [coach_response_review_workbook_repair_before_after_20260510.csv](coach_response_review_workbook_repair_before_after_20260510.csv): Repair 前后对照网页盲评 CSV，共 8 条。
- [coach_response_review_workbook_repair_before_after_20260510.zh.xlsx](coach_response_review_workbook_repair_before_after_20260510.zh.xlsx): Repair 前后对照中文 Excel 备份表。
- [repair_before_after_review_analysis_20260510.zh.md](repair_before_after_review_analysis_20260510.zh.md): Repair 前后对照中文盲评分析，导出评分后可重复生成。
- [repair_before_after_review_analysis_20260510.md](repair_before_after_review_analysis_20260510.md): Repair before/after English blind-review analysis.
- [coach_response_review_workbook_repair_stress_v1_20260511.zh.xlsx](coach_response_review_workbook_repair_stress_v1_20260511.zh.xlsx): Repair stress v1 的 before/after 中文盲评表，共 24 条匿名回复。
- [coach_response_review_workbook_repair_stress_v1_20260511.csv](coach_response_review_workbook_repair_stress_v1_20260511.csv): Repair stress v1 before/after CSV。
- [coach_response_review_workbook_repair_stress_v1_20260511.key.csv](coach_response_review_workbook_repair_stress_v1_20260511.key.csv): Repair stress v1 before/after 匿名 key。
- [coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.zh.xlsx](coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.zh.xlsx): prompt-controlled ablation 3-case 中文盲评表，共 15 条匿名回复。
- [coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.key.csv](coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.key.csv): prompt-controlled ablation 3-case 匿名 key。
- [coach_response_review_labels_prompt_controlled_ablation_smoke3_20260511.jsonl](coach_response_review_labels_prompt_controlled_ablation_smoke3_20260511.jsonl): prompt-controlled ablation 3-case 盲评标签 JSONL，已映射到匿名系统条件。
- [coach_response_review_workbook_fair_mini_study_20_20260511.zh.xlsx](coach_response_review_workbook_fair_mini_study_20_20260511.zh.xlsx): 7-system fair 20-case mini-study 的中文盲评表，共 140 条匿名回复。

### Patch Governance

- [prompt_patch_log.md](prompt_patch_log.md): slow-variable prompt/rubric/registry/router patch log.
- [judge_prompt_patch_log.md](judge_prompt_patch_log.md): runtime judge 与 offline grader prompt 的单独 patch log。

## Research Workflow

### 1. Seed Labeling

1. Export a blind coach workbook.
2. Coach A labels all cases.
3. Coach B labels 20%-30% independently.
4. Validate workbook fields.
5. Summarize agreement.
6. Adjudicate disagreements.
7. Export adjudicated reference JSONL for headline metrics.

### 2. Offline Baseline Evaluation

Run the same seed set across:

- `current_system`
- `enhanced_prompt_only`
- `socratic_no_answer_tutor`
- `codehelp_codeaid_no_direct_solution_tutor`
- `dbox_inspired_decomposition_tutor`
- `dbox_inspired_decomposition_tutor + guard`
- `bridge_inspired_expert_decision_tutor`
- `single_llm_structured`
- `bridge_contract`
- `bridge_contract_plus_guard`
- `bridge_contract_plus_guard_plus_repair`
- `risk_triggered_simulation`

For every row, preserve:

- `candidate_response_text`
- `final_response_text`
- `final_response_source`
- `runtime_bridge_contract`
- `leakage_judge_result`
- `repair_result`
- `latency_ms`
- `llm_call_count`
- `stage_errors`

### 3. Blind Response Review

Export an anonymized response review workbook. The coach should not see the baseline name while scoring:

- bridge identification
- groundedness
- scaffold appropriateness
- bridge leakage control
- next-step clarity
- single-focus coherence
- bridge-oriented micro-example quality
- micro-example applicability
- overall quality score
- would-show-to-student decision
- reviewer confidence
- needs-discussion flag
- actual leakage label
- overall quality band

### 4. Patch Only From Evidence

Do not patch prompts from one anecdotal case. A patch requires:

- repeated failure pattern;
- coach evidence or blind review;
- regression case;
- one-layer-only change;
- smoke/regression test;
- human approval.

## Next Experiments

Immediate next steps:

1. Finish Research v1 cleanup and path hygiene.
2. Expand the prompt-controlled ablation from 3 cases to 10-20 cases to separate prompt wording effects from concrete Bridge Contract effects.
3. Finish Repair stress before/after coach review and summarize quality-vs-leakage trade-offs.
4. Build the 50-case held-out set only after prompt/rubric versions are frozen on the dev/regression set.
5. Run partial double annotation and judge calibration before using any result as a headline paper claim.

## Reporting Rule

For reports meant for review, keep bilingual pairs:

- English: `*.md`
- Chinese: `*.zh.md`

For coach-facing use, the Chinese report is the primary reading surface. For external AI or paper collaborators, the English report is the companion artifact.
