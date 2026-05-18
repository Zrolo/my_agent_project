# Research v1 Index

本文件是 `codex/bridge-research-annotation` 分支的 Research v1 总入口。它只描述当前研究线的边界、数据流和下一步实验，不表示这些能力已经接入线上学生 AIChat。

## Current Checkpoint

- Branch: `codex/bridge-research-annotation`
- Current review entrypoint: branch tip of `codex/bridge-research-annotation` for handoff / prompt wording.
- Primary evidence-package review target: `33a5dd7 Add dialogue-state v3 evidence package gates`; if branch tip is newer, audit this fixed evidence package first and separately note whether later commits change evidence files, scripts, or paper wording.
- Checkpoint interpretation: `dbbbd5c` may appear in machine-readable manifest metadata as the evidence-content base; `33a5dd7` is the evidence-package gates checkpoint; later branch-tip commits primarily tighten reviewer-facing handoff / prompt wording unless explicitly stated otherwise.
- Dialogue-state v3 status: `formal human-review evidence candidate`；它不是 `final gold`，也不能把 Coach A、Coach B 或 priority60 adjudicated merge 当作唯一真值。
- Headline rule: 论文主 headline 只能使用 `main_scaffold_eval` slice；`main_eval_with_caution`、`clarification_safety_slice`、`policy_safety_slice` 和 all-50 aggregate 只能作为 sensitivity / appendix，不混成一个 headline 平均。
- Current online AIChat status: 仍以 `chat()` 为入口，主要由 rules、legacy learning phase judge、Pedagogical Judge v2 soft control、main LLM、自报 level hard gate 和 output guards 组成。
- 2026-05-12 online update: 学生端已增加“回答方式”切换。默认 `简洁提示=current_system` 仍保留当前线上行为；可选 `教练引导=enhanced_prompt_only_clean` 只加入 prompt-only 教练引导，不接入 Bridge Judge、Leakage Guard、Repair 或 risk-triggered routing。
- 2026-05-16 data gate: dialogue-state v3 50-case 已完成 Coach A case/source review gate，并导出 `reviewed_candidate` 版本；该状态只表示 case/source 可用于后续 prompt/rubric freeze 与 response generation，不表示 gold/reference label 或 AI response review 已完成。
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
- [claims_and_evidence_matrix_v1.md](claims_and_evidence_matrix_v1.md): English claims and evidence matrix.
- [formal_eval_protocol_v1.zh.md](formal_eval_protocol_v1.zh.md): 中文正式评测协议，固定 primary / secondary / exploratory 实验层级、dev/held-out 分离、prompt freeze、context integrity 和结果解释规则，降低 cherry-picking / p-hacking 风险。
- [formal_eval_protocol_v1.md](formal_eval_protocol_v1.md): English formal evaluation protocol for experiment hierarchy, held-out discipline, freeze rules, context integrity, and bias control.
- [evaluation_protocol_v2.zh.md](evaluation_protocol_v2.zh.md): 中文 coach-calibrated response evaluation protocol，规定校准轮、强制备注、部分双标、agreement、adjudication 和 AI 初筛边界。
- [evaluation_protocol_v2.md](evaluation_protocol_v2.md): English coach-calibrated response evaluation protocol for calibration, required notes, double annotation, agreement, adjudication, and AI-prelim boundaries.
- [evaluation_protocol_v3.zh.md](evaluation_protocol_v3.zh.md): 中文 v3 回复评测协议，将评价拆成主指标、诊断指标和可靠性字段，并要求 case-specific rubric 先于评分。
- [evaluation_protocol_v3.md](evaluation_protocol_v3.md): English v3 response evaluation protocol with primary outcomes, diagnostic dimensions, reliability fields, and case-specific rubric workflow.
- [implementation_status_matrix_20260511.zh.md](implementation_status_matrix_20260511.zh.md): 当前线上、离线、shadow/proposed 和未实现模块的状态矩阵。
- [implementation_status_matrix_20260511.md](implementation_status_matrix_20260511.md): English implementation status matrix.
- [baseline_protocol_v1.zh.md](baseline_protocol_v1.zh.md): 中文 baseline protocol，定义 deployment baseline、强 prompt baseline、文献启发 baseline、Bridge Contract 方法组和 shuffled/oracle 负控。
- [baseline_protocol_v1.md](baseline_protocol_v1.md): English baseline protocol.
- [baseline_strategy_v1.zh.md](baseline_strategy_v1.zh.md): 中文 baseline strategy，说明为什么 `current_system` 不能作为唯一科研 baseline，以及强 baseline 胜出时论文结论如何保持稳健。
- [baseline_strategy_v1.md](baseline_strategy_v1.md): English baseline strategy.
- [model_runtime_configuration_v1.zh.md](model_runtime_configuration_v1.zh.md): 中文模型与运行配置协议，规定主消融固定 tutor / judge / repair 模型、thinking mode 和盲审可见性。
- [model_runtime_configuration_v1.md](model_runtime_configuration_v1.md): English model/runtime configuration protocol for fixed-model harness ablations.
- [online_aichat_prompt_mode_rollout_20260512.zh.md](online_aichat_prompt_mode_rollout_20260512.zh.md): 中文线上 AIChat 回答方式上线记录，说明 `简洁提示=current_system` 与 `教练引导=enhanced_prompt_only_clean` 的产品边界和研究日志解释方式。
- [online_aichat_prompt_mode_rollout_20260512.md](online_aichat_prompt_mode_rollout_20260512.md): English online AIChat prompt-mode rollout note.
- [real_aichat_log_screening_20260512.zh.md](real_aichat_log_screening_20260512.zh.md): 中文真实线上 AIChat 日志候选筛选记录，包含数据量、筛选规则、候选分布、隐私边界和后续教练审查建议。
- [real_aichat_log_screening_20260512.md](real_aichat_log_screening_20260512.md): English real AIChat log screening note.
- [real_aichat_legacy_context_contamination_screen_20260512.zh.md](real_aichat_legacy_context_contamination_screen_20260512.zh.md): 中文真实日志旧 AI 上下文污染筛选记录，区分 main eval、dev/contextual 和 exclude 候选，并记录 student-only v3 审查表策略。
- [real_aichat_legacy_context_contamination_screen_20260512.md](real_aichat_legacy_context_contamination_screen_20260512.md): English legacy-context contamination screen for real AIChat log candidates, including the student-only v3 workbook policy.
- [real_aichat_ai_prelim_review_20260513.zh.md](real_aichat_ai_prelim_review_20260513.zh.md): 中文真实 AIChat student-only 候选 AI 预标注报告，记录 33 条候选中 8 条通过严格门禁，并强调这些样本只作为 real-log pilot / dev realism check。
- [real_aichat_ai_prelim_review_20260513.md](real_aichat_ai_prelim_review_20260513.md): English AI preliminary review report for the real AIChat student-only candidate workbook.
- [real_log_student_only_pilot_ai_prelim_analysis_20260513.zh.md](real_log_student_only_pilot_ai_prelim_analysis_20260513.zh.md): 中文真实 AIChat student-only 8-case pilot AI 自评分析，比较 EDF core 六个匿名条件的质量、泄露和 student-ready 指标。
- [real_log_student_only_pilot_ai_prelim_analysis_20260513.md](real_log_student_only_pilot_ai_prelim_analysis_20260513.md): English AI self-review analysis for the real AIChat student-only 8-case pilot run.
- [real_log_student_only_pilot_integrity_20260513.zh.md](real_log_student_only_pilot_integrity_20260513.zh.md): 中文真实 AIChat student-only pilot 消融完整性检查，说明本 run 有 2 条空最终回复，只能作为 dev realism check。
- [real_log_student_only_pilot_integrity_20260513.md](real_log_student_only_pilot_integrity_20260513.md): English integrity report for the real AIChat student-only pilot ablation run.
- [real_log_student_only_pilot_merged_integrity_20260513.zh.md](real_log_student_only_pilot_merged_integrity_20260513.zh.md): 中文真实 AIChat student-only merged pilot 完整性检查，记录定向补跑后 48/48 条目标回复齐全，但仍有 stage warning，不能作为 headline。
- [real_log_student_only_pilot_merged_integrity_20260513.md](real_log_student_only_pilot_merged_integrity_20260513.md): English integrity report for the merged real AIChat student-only pilot ablation run.
- [real_log_student_only_pilot_merged_ai_prelim_analysis_20260513.zh.md](real_log_student_only_pilot_merged_ai_prelim_analysis_20260513.zh.md): 中文真实 AIChat student-only 8-case merged pilot AI 自评分析，基于完整 48 条回复，仅作为 dev realism check。
- [real_log_student_only_pilot_merged_ai_prelim_analysis_20260513.md](real_log_student_only_pilot_merged_ai_prelim_analysis_20260513.md): English AI self-review analysis for the merged real AIChat student-only 8-case pilot run.
- [real_log_student_only_pilot_merged_timeout25_integrity_20260513.zh.md](real_log_student_only_pilot_merged_timeout25_integrity_20260513.zh.md): 中文真实 AIChat student-only timeout25 merged pilot 完整性检查，记录保持 max token 默认、只提高 leakage judge timeout 后已无 stage warning。
- [real_log_student_only_pilot_merged_timeout25_integrity_20260513.md](real_log_student_only_pilot_merged_timeout25_integrity_20260513.md): English integrity report for the timeout25 merged real AIChat student-only pilot run.
- [real_log_student_only_pilot_timeout25_ai_prelim_analysis_20260513.zh.md](real_log_student_only_pilot_timeout25_ai_prelim_analysis_20260513.zh.md): 中文真实 AIChat student-only 8-case timeout25 pilot AI 自评分析，基于无 stage warning 的完整 48 条回复。
- [real_log_student_only_pilot_timeout25_ai_prelim_analysis_20260513.md](real_log_student_only_pilot_timeout25_ai_prelim_analysis_20260513.md): English AI self-review analysis for the timeout25 real AIChat student-only 8-case pilot run.
- [bilingual_documentation_policy_v1.zh.md](bilingual_documentation_policy_v1.zh.md): 中文 Research v1 双语文档规范，要求新增研究 Markdown 保持 `*.md` / `*.zh.md` 成对。
- [bilingual_documentation_policy_v1.md](bilingual_documentation_policy_v1.md): English bilingual documentation policy for Research v1 Markdown artifacts.
- [dbox_reproduction_gap_v1.zh.md](dbox_reproduction_gap_v1.zh.md): 中文 DBox-inspired baseline 边界说明，明确当前实现不是 DBox reproduction。
- [dbox_reproduction_gap_v1.md](dbox_reproduction_gap_v1.md): English DBox-inspired baseline boundary note.
- [dbox_official_materials_review_v1.zh.md](dbox_official_materials_review_v1.zh.md): 中文 DBox 官方材料包 review，记录 prompts/source 对 DBox-inspired baseline 的影响。
- [dbox_official_materials_review_v1.md](dbox_official_materials_review_v1.md): English review of the official DBox supplementary package.
- [edf_official_materials_review_v1.zh.md](edf_official_materials_review_v1.zh.md): 中文 EDF / Copa 官方材料扫描报告，说明其只适合 EDF-inspired adaptive scaffolding baseline，不适合作为可运行 Copa 复现。
- [edf_official_materials_review_v1.md](edf_official_materials_review_v1.md): English scan report for the official EDF / Copa supplementary materials.
- [edf_inspired_ablation_10case_ai_self_review_20260512.zh.md](edf_inspired_ablation_10case_ai_self_review_20260512.zh.md): 中文 EDF-inspired 10-case dev 消融 AI 预评报告，比较 enhanced prompt、DBox+Guard、EDF、Bridge Contract+Guard/Repair；仅用于 dev 筛查，不是教练 gold。
- [edf_inspired_ablation_10case_ai_self_review_20260512.md](edf_inspired_ablation_10case_ai_self_review_20260512.md): English EDF-inspired 10-case development ablation AI self-review report.

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
- [bridge_taxonomy_abstraction_policy_v1.zh.md](bridge_taxonomy_abstraction_policy_v1.zh.md): 中文 bridge subtype / forbidden content 抽象粒度政策，说明具体算法进入 topic/focus/context，桥梁细分保持可迁移推理形状。
- [bridge_taxonomy_abstraction_policy_v1.md](bridge_taxonomy_abstraction_policy_v1.md): English abstraction policy for bridge subtype and forbidden-content granularity.
- [bridge_taxonomy_coverage_review_v1.zh.md](bridge_taxonomy_coverage_review_v1.zh.md): 中文算法竞赛知识覆盖评审，将 CP-Algorithms、OI Wiki、USACO Guide 等资料压缩为可标注的抽象桥梁形状。
- [bridge_taxonomy_coverage_review_v1.md](bridge_taxonomy_coverage_review_v1.md): English coverage review for abstract bridge shapes across competitive-programming topics.
- [response_review_rubric_v2.zh.md](response_review_rubric_v2.zh.md): AIChat 回复盲评中文评分标准，包含总体质量、是否愿意给学生看、帮助是否足够、学生回复负担、评分置信度和示例。
- [response_review_rubric_v2.md](response_review_rubric_v2.md): English response blind-review rubric v2.
- [response_review_rubric_v3.zh.md](response_review_rubric_v3.zh.md): AIChat 回复盲评 v3 中文评分标准，主指标包括 overall、student-ready、critical leakage、sufficiency 和 burden；micro-example 不适用时不扣分。
- [response_review_rubric_v3.md](response_review_rubric_v3.md): English response blind-review rubric v3.
- [case_specific_rubric_policy_v1.zh.md](case_specific_rubric_policy_v1.zh.md): 中文 case-specific rubric 政策，规定 success criteria、forbidden content、critical bridge boundary、acceptable reveal 和 expected next action。
- [case_specific_rubric_policy_v1.md](case_specific_rubric_policy_v1.md): English case-specific rubric policy.
- [coach_blind_review_instructions_v1.zh.md](coach_blind_review_instructions_v1.zh.md): 给不熟悉系统的外部教练使用的中文盲审说明，解释 missing bridge、critical bridge leakage、评分维度和常见边界情况。
- [coach_blind_review_instructions_v1.md](coach_blind_review_instructions_v1.md): English external coach blind-review instructions.
- [critical_bridge_leakage_calibration_policy_v1.zh.md](critical_bridge_leakage_calibration_policy_v1.zh.md): 中文 critical bridge leakage 校准策略，区分桥梁信息、桥梁透露和无正当性关键桥泄露。
- [critical_bridge_leakage_calibration_policy_v1.md](critical_bridge_leakage_calibration_policy_v1.md): English critical bridge leakage calibration policy.
- [short_student_reply_interaction_policy_v1.zh.md](short_student_reply_interaction_policy_v1.zh.md): 中文最低足够学生努力策略，说明在线学生回复通常较短，但 Tutor 下一步仍需保留认知价值和诊断价值。
- [short_student_reply_interaction_policy_v1.md](short_student_reply_interaction_policy_v1.md): English minimal sufficient student effort policy.
- [response_review_problem_statement_and_length_policy_v1.zh.md](response_review_problem_statement_and_length_policy_v1.zh.md): 中文回复盲评题面与学生问题长度分布政策，要求后续盲评表包含原题题面/必要题面，并按 20/15/10/5 控制 50-case 学生问题长度分布。
- [response_review_problem_statement_and_length_policy_v1.md](response_review_problem_statement_and_length_policy_v1.md): English policy for problem statements and student-message length buckets in response-review workbooks.
- [real_student_language_style_guide_v1.zh.md](real_student_language_style_guide_v1.zh.md): 中文真实学生提问语言风格指南，记录线上学生短问、贴代码、半成型思路和 recent_dialogue 写法边界，用于后续 synthetic-but-grounded case 编写。
- [real_student_language_style_guide_v1.md](real_student_language_style_guide_v1.md): English real-student language style guide for writing synthetic-but-grounded cases and natural recent dialogue.
- [heldout_50_real_problem_source_completion_workflow_v1.zh.md](heldout_50_real_problem_source_completion_workflow_v1.zh.md): 中文 50-case 真实题源补全流程，规定如何导出题源补全表、填写洛谷/Codeforces/AtCoder 等真实来源、合并回 JSONL 并校验。
- [heldout_50_real_problem_source_completion_workflow_v1.md](heldout_50_real_problem_source_completion_workflow_v1.md): English workflow for completing real problem-source metadata in the 50-case held-out dataset.
- [luogu_problem_source_snapshot_v1.zh.md](luogu_problem_source_snapshot_v1.zh.md): 中文洛谷本地题库快照记录，说明 `latest.ndjson` 的本地路径、行数、checksum、版权/公开边界和不提交 Git 的原则。
- [luogu_problem_source_snapshot_v1.md](luogu_problem_source_snapshot_v1.md): English Luogu source snapshot record for the local problem bank used by held-out v2.
- [bridgebench_cp_heldout_v2_50_generation_report_20260513.zh.md](bridgebench_cp_heldout_v2_50_generation_report_20260513.zh.md): 中文洛谷真实题源 held-out v2 50-case 生成报告，记录桥梁配额、学生问题长度、近期对话和代码片段分布。
- [bridgebench_cp_heldout_v2_50_generation_report_20260513.md](bridgebench_cp_heldout_v2_50_generation_report_20260513.md): English generation report for the Luogu-grounded held-out v2 50-case draft.
- [dialogue_state_v3_generation_report_20260513.zh.md](dialogue_state_v3_generation_report_20260513.zh.md): 中文 dialogue-state v3 50-case 生成报告，在 v2 真实题源基础上加入 40 条后续辅导轮、F1-F4 学生跟随状态、固定上一轮 AI 脚手架和期望教学动作；仍为 draft，需教练复核。
- [dialogue_state_v3_generation_report_20260513.md](dialogue_state_v3_generation_report_20260513.md): English generation report for the dialogue-state v3 50-case draft with follow-up tutoring turns and scaffold-followability labels.
- [coach_seed_labeling_workbook_dialogue_state_v3_50.zh.xlsx](coach_seed_labeling_workbook_dialogue_state_v3_50.zh.xlsx): dialogue-state v3 教练标注工作簿，包含原题、上下文、上一轮 AI 脚手架、学生对脚手架的回答、F1-F4 跟随状态和常规 missing-bridge 标注列。
- [dialogue_state_v3_case_source_gate_pass_20260516.zh.md](dialogue_state_v3_case_source_gate_pass_20260516.zh.md): 中文 dialogue-state v3 50-case case/source gate 通过记录，汇总 Coach A full review、18-case re-check、3-case replacement re-check 和 reviewed_candidate 导出边界。
- [dialogue_state_v3_case_source_gate_pass_20260516.md](dialogue_state_v3_case_source_gate_pass_20260516.md): English case/source gate pass record for the dialogue-state v3 50-case reviewed candidate set.
- [bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl](bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl): dialogue-state v3 50-case reviewed candidate JSONL；case/source 已通过 Coach A review gate，但仍不是 gold/adjudicated/frozen reference。
- [dialogue_state_v3_50_reviewed_candidate_validation_report_20260516.json](dialogue_state_v3_50_reviewed_candidate_validation_report_20260516.json): reviewed candidate JSONL 的结构校验报告。
- [dialogue_state_v3_prompt_rubric_freeze_gate_20260516.zh.md](dialogue_state_v3_prompt_rubric_freeze_gate_20260516.zh.md): 中文 dialogue-state v3 prompt/rubric freeze gate，固定 reviewed candidate response generation 的 7-condition 主表、DBox+Repair appendix add-on、模型配置、rubric/workbook 边界和 Go/No-go。
- [dialogue_state_v3_prompt_rubric_freeze_gate_20260516.md](dialogue_state_v3_prompt_rubric_freeze_gate_20260516.md): English prompt/rubric freeze gate for the dialogue-state v3 reviewed candidate response generation run.
- [dialogue_state_v3_main_generation_integrity_20260516.zh.md](dialogue_state_v3_main_generation_integrity_20260516.zh.md): 中文 dialogue-state v3 主实验生成完整性记录，说明 7-condition 主表 350 行和 DBox+Repair 附录 50 行均已通过完整性检查，可进入后续盲评。
- [dialogue_state_v3_main_generation_integrity_20260516.md](dialogue_state_v3_main_generation_integrity_20260516.md): English integrity record for the dialogue-state v3 main response generation pack and DBox+Repair fairness add-on.
- [dialogue_state_v3_human_review_result_packet_20260517.zh.md](dialogue_state_v3_human_review_result_packet_20260517.zh.md): 中文 dialogue-state v3 人类盲评结果总包，汇总 Coach A/B 全量评审、一致性、60 条高优先级裁决、敏感性分析和按 case-use slice 的分层分析；当前是 formal human-review evidence candidate，不是 final gold。
- [dialogue_state_v3_human_review_result_packet_20260517.md](dialogue_state_v3_human_review_result_packet_20260517.md): English dialogue-state v3 human-review result packet summarizing Coach A/B reviews, agreement, high-priority adjudication, sensitivity analysis, and slice analysis.
- [dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.zh.md](dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.zh.md): 中文 main_scaffold_eval 配对不确定性报告，按 priority60 adjudicated + Coach A 主口径和 Coach A/B 敏感性计算 W/T/L、mean delta、bootstrap CI 与 paired permutation。
- [dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.md](dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.md): English paired uncertainty report for dialogue-state v3 main_scaffold_eval headline comparisons.
- [dialogue_state_v3_targeted_adjudication_extension_plan_20260517.zh.md](dialogue_state_v3_targeted_adjudication_extension_plan_20260517.zh.md): 中文 targeted adjudication extension 计划，从剩余未裁决分歧中追加 40 条 headline-sensitive 样本，配套输出裁决候选工作簿。
- [dialogue_state_v3_targeted_adjudication_extension_plan_20260517.md](dialogue_state_v3_targeted_adjudication_extension_plan_20260517.md): English plan for a targeted 40-row adjudication extension focused on headline-sensitive disagreements.
- [paper_results_interpretation_guardrails_20260517.zh.md](paper_results_interpretation_guardrails_20260517.zh.md): 中文论文结果解释 guardrails，明确 Guard-only 是 instrumentation、Repair 因果效果需要 same-candidate stress、主张应写 trade-off。
- [paper_results_interpretation_guardrails_20260517.md](paper_results_interpretation_guardrails_20260517.md): English paper-result interpretation guardrails for Guard-only, Repair, rater sensitivity, and safe claims.
- [taxonomy_specificity_revision_summary_20260517.zh.md](taxonomy_specificity_revision_summary_20260517.zh.md): 中文 taxonomy specificity revision 摘要，记录 P0/P1 文件如何从具体算法场景上提为 operational cognitive bridge families、leakage mechanisms 和 surface anchors。
- [taxonomy_specificity_revision_summary_20260517.md](taxonomy_specificity_revision_summary_20260517.md): English summary of the taxonomy specificity revision.
- [dialogue_state_v3_result_claims_lock_20260517.zh.md](dialogue_state_v3_result_claims_lock_20260517.zh.md): 中文 dialogue-state v3 结果声明锁，列出可以写、不能写和推荐论文表述。
- [dialogue_state_v3_result_claims_lock_20260517.md](dialogue_state_v3_result_claims_lock_20260517.md): English dialogue-state v3 result claims lock.
- [dialogue_state_v3_main_paper_ready_tables_20260517.zh.md](dialogue_state_v3_main_paper_ready_tables_20260517.zh.md): 中文 paper-ready 主表，按 main scaffold / caution / clarification / policy slice 分开报告。
- [dialogue_state_v3_main_paper_ready_tables_20260517.md](dialogue_state_v3_main_paper_ready_tables_20260517.md): English paper-ready main tables for dialogue-state v3.
- [dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md](dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md): 中文 main_scaffold_eval 配对 W/T/L 与不确定性解释。
- [dialogue_state_v3_pairwise_win_tie_loss_20260517.md](dialogue_state_v3_pairwise_win_tie_loss_20260517.md): English pairwise win/tie/loss interpretation.
- [human_review_reliability_section_draft_20260517.zh.md](human_review_reliability_section_draft_20260517.zh.md): 中文 human review reliability 论文小节草稿。
- [human_review_reliability_section_draft_20260517.md](human_review_reliability_section_draft_20260517.md): English human-review reliability section draft.
- [dialogue_state_v3_observed_error_taxonomy_20260517.zh.md](dialogue_state_v3_observed_error_taxonomy_20260517.zh.md): 中文 observed error taxonomy，将错误分为 failure type、cognitive bridge family 与 surface anchor。
- [dialogue_state_v3_observed_error_taxonomy_20260517.md](dialogue_state_v3_observed_error_taxonomy_20260517.md): English observed error taxonomy.
- [paper_results_draft_dialogue_state_v3_20260517.zh.md](paper_results_draft_dialogue_state_v3_20260517.zh.md): 中文 dialogue-state v3 Results / Discussion 初稿。
- [paper_results_draft_dialogue_state_v3_20260517.md](paper_results_draft_dialogue_state_v3_20260517.md): English dialogue-state v3 Results / Discussion draft.
- [paper_results_discussion_manuscript_dialogue_state_v3_20260518.zh.md](paper_results_discussion_manuscript_dialogue_state_v3_20260518.zh.md): 中文 manuscript-style Results / Discussion 压缩正文，整合人审可靠性、main scaffold、paired uncertainty、Repair stress、DBox fairness 和 DeepSeek-backed LLM grader calibration。
- [paper_results_discussion_manuscript_dialogue_state_v3_20260518.md](paper_results_discussion_manuscript_dialogue_state_v3_20260518.md): English manuscript-style Results / Discussion draft with paper-safe claims and limitations.
- [paper_results_discussion_section_dialogue_state_v3_20260518.zh.md](paper_results_discussion_section_dialogue_state_v3_20260518.zh.md): 中文论文正文版 Results / Discussion section 草稿，按 `4 Results` / `5 Discussion` 组织，可作为论文写作基底。
- [paper_results_discussion_section_dialogue_state_v3_20260518.md](paper_results_discussion_section_dialogue_state_v3_20260518.md): English paper-section draft for Results / Discussion, organized as `4 Results` / `5 Discussion`.
- [project_status_after_taxonomy_revision_20260517.zh.md](project_status_after_taxonomy_revision_20260517.zh.md): 中文 taxonomy revision 后项目状态和下一步执行顺序。
- [project_status_after_taxonomy_revision_20260517.md](project_status_after_taxonomy_revision_20260517.md): English project status after taxonomy revision.
- [dialogue_state_v3_external_review_handoff_20260518.zh.md](dialogue_state_v3_external_review_handoff_20260518.zh.md): 中文外部复核 handoff，给 AI / 人类 reviewer 的阅读顺序、复算命令、审稿问题和解释边界。
- [dialogue_state_v3_external_review_handoff_20260518.md](dialogue_state_v3_external_review_handoff_20260518.md): English external-review handoff with reading order, reproduction commands, reviewer questions, and interpretation boundaries.
- [dialogue_state_v3_external_reviewer_prompt_20260518.zh.md](dialogue_state_v3_external_reviewer_prompt_20260518.zh.md): 中文可复制外部 reviewer 提示词，要求从 GitHub 真实文件复核 evidence package。
- [dialogue_state_v3_external_reviewer_prompt_20260518.md](dialogue_state_v3_external_reviewer_prompt_20260518.md): English copy-paste external reviewer prompt for auditing the evidence package from GitHub files.
- [dialogue_state_v3_evidence_manifest_20260518.json](dialogue_state_v3_evidence_manifest_20260518.json): dialogue-state v3 evidence manifest，列出每个 paper-facing 结果表的报告、输入、脚本、输出、checksum、解释边界和禁止表述。
- [dialogue_state_v3_paper_claims_final_gate_20260518.zh.md](dialogue_state_v3_paper_claims_final_gate_20260518.zh.md): 中文论文 claim final gate，按 allowed wording / required evidence / forbidden wording 锁定投稿前表述边界。
- [dialogue_state_v3_paper_claims_final_gate_20260518.md](dialogue_state_v3_paper_claims_final_gate_20260518.md): English paper-claim final gate for dialogue-state v3.
- [dbox_repair_fairness_extension_plan_20260518.zh.md](dbox_repair_fairness_extension_plan_20260518.zh.md): 中文 DBox+Repair fairness extension plan，列出第二教练 20-case 复评、50-case full review、保持 appendix sensitivity 三个选择。
- [dbox_repair_fairness_extension_plan_20260518.md](dbox_repair_fairness_extension_plan_20260518.md): English DBox+Repair fairness extension plan.

### Runtime Contract And Registries

- [runtime_bridge_contract_schema_v1.json](runtime_bridge_contract_schema_v1.json): 运行时 compact bridge contract schema。
- [bridge_subtype_registry_v2.json](bridge_subtype_registry_v2.json): bridge subtype 与 family 的注册表。
- [focus_registry_v1.json](focus_registry_v1.json): 当前 focus registry。

### Offline Evaluation

- [bridge_judge_offline_eval_v1.md](bridge_judge_offline_eval_v1.md): 离线 Bridge Judge / Tutor / Guard / Repair 评测设计。
- [agent_eval_methodology_v1.zh.md](agent_eval_methodology_v1.zh.md): 基于 agent eval 文章整理的中文评测方法论。
- [agent_eval_methodology_v1.md](agent_eval_methodology_v1.md): English agent-eval methodology mapping for Research v1.
- [llm_judge_calibration_protocol_v1.zh.md](llm_judge_calibration_protocol_v1.zh.md): LLM Judge / Offline Grader 校准协议，包含 UNKNOWN、false positive/negative 和 prompt freeze 要求。
- [llm_grader_calibration_protocol_v2.zh.md](llm_grader_calibration_protocol_v2.zh.md): 中文 LLM Grader v2 校准协议，比较 Likert-only、generic rubric 和 case-specific bridge rubric grader。
- [llm_grader_calibration_protocol_v2.md](llm_grader_calibration_protocol_v2.md): English LLM Grader calibration protocol v2.
- [llm_grader_calibration_plan_20260517.zh.md](llm_grader_calibration_plan_20260517.zh.md): 中文 LLM grader calibration 计划，以 priority60 adjudicated labels 和 adjudicated+Coach A/B 为参考，比较 Likert-only、generic rubric、case-specific bridge rubric judge。
- [llm_grader_calibration_plan_20260517.md](llm_grader_calibration_plan_20260517.md): English LLM grader calibration plan for Likert-only, generic rubric, and case-specific bridge rubric judges.
- [llm_grader_calibration_plan_or_report_20260517.zh.md](llm_grader_calibration_plan_or_report_20260517.zh.md): 中文 LLM grader calibration plan/report 状态，记录 DeepSeek-backed priority60、adj+CoachA sample20、adj+CoachB sample20 完整结果，并将 Kimi run 标为 exploratory。
- [llm_grader_calibration_plan_or_report_20260517.md](llm_grader_calibration_plan_or_report_20260517.md): English LLM grader calibration plan/report status with complete DeepSeek-backed priority60 and adj+CoachA/B sample20 results; Kimi runs are exploratory.
- [llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl](llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl): priority60 adjudicated 60-row × 3 judge prompt pack for LLM grader calibration; predictions not included.
- [llm_grader_calibration_pack_adj_coachA_sample20_20260517.jsonl](llm_grader_calibration_pack_adj_coachA_sample20_20260517.jsonl): adj+CoachA sample20 × 3 judge prompt pack for rater-view sensitivity.
- [llm_grader_calibration_pack_adj_coachB_sample20_20260517.jsonl](llm_grader_calibration_pack_adj_coachB_sample20_20260517.jsonl): adj+CoachB sample20 × 3 judge prompt pack for rater-view sensitivity.
- [llm_grader_calibration_smoke12_priority60_20260517.zh.md](llm_grader_calibration_smoke12_priority60_20260517.zh.md): 中文 LLM grader calibration priority60 smoke12 工具链记录，确认 runner、strict schema、retry 和 summarizer 可用；不是正式 calibration evidence。
- [llm_grader_calibration_smoke12_priority60_20260517.md](llm_grader_calibration_smoke12_priority60_20260517.md): English LLM grader calibration priority60 smoke12 toolchain note; not formal calibration evidence.
- [llm_grader_calibration_priority60_report_20260517.zh.md](llm_grader_calibration_priority60_report_20260517.zh.md): 中文 Kimi exploratory priority60 LLM grader calibration 记录；不是论文主 calibration evidence。
- [llm_grader_calibration_priority60_report_20260517.md](llm_grader_calibration_priority60_report_20260517.md): English Kimi exploratory priority60 LLM grader calibration record; not paper-facing calibration evidence.
- [llm_grader_calibration_sensitivity_report_20260518.zh.md](llm_grader_calibration_sensitivity_report_20260518.zh.md): 中文 Kimi exploratory LLM grader calibration sensitivity 记录，说明 backend-sensitive；不是论文主 evidence。
- [llm_grader_calibration_sensitivity_report_20260518.md](llm_grader_calibration_sensitivity_report_20260518.md): English Kimi exploratory LLM grader calibration sensitivity record; backend-sensitive and not paper-facing evidence.
- [llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md](llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md): 中文 DeepSeek-backed LLM grader calibration 主报告，汇总 priority60、adj+CoachA sample20、adj+CoachB sample20 完整结果。
- [llm_grader_calibration_deepseek_sensitivity_report_20260518.md](llm_grader_calibration_deepseek_sensitivity_report_20260518.md): English DeepSeek-backed LLM grader calibration main report for complete priority60 and adj+CoachA/B sample20 runs.
- [repair_same_candidate_stress_protocol_20260517.zh.md](repair_same_candidate_stress_protocol_20260517.zh.md): 中文 Repair same-candidate stress protocol，固定同一 candidate 比较 before/after repair，并配套 30-row workbook template。
- [repair_same_candidate_stress_protocol_20260517.md](repair_same_candidate_stress_protocol_20260517.md): English same-candidate Repair stress protocol and workbook-template description.
- [repair_same_candidate_stress_result_20260517.zh.md](repair_same_candidate_stress_result_20260517.zh.md): 中文 Repair same-candidate stress 30-pair 人审结果，报告 leakage、quality、burden before/after delta。
- [repair_same_candidate_stress_result_20260517.md](repair_same_candidate_stress_result_20260517.md): English 30-pair same-candidate Repair stress result.
- [dbox_guard_repair_fairness_review_plan_20260517.zh.md](dbox_guard_repair_fairness_review_plan_20260517.zh.md): 中文 DBox+Guard+Repair fairness add-on 人审方案，基于已有 50-row 生成包抽取 20 个敏感 case。
- [dbox_guard_repair_fairness_review_plan_20260517.md](dbox_guard_repair_fairness_review_plan_20260517.md): English DBox+Guard+Repair fairness add-on review plan with a 20-case candidate list.
- [dbox_guard_repair_fairness_coach_instructions_20260517.zh.md](dbox_guard_repair_fairness_coach_instructions_20260517.zh.md): 中文 DBox+Guard+Repair 20-case 补评教练说明，明确只填写 direct-fill workbook 的 `盲评表`。
- [dbox_guard_repair_fairness_coach_instructions_20260517.md](dbox_guard_repair_fairness_coach_instructions_20260517.md): English coach instructions for the DBox+Guard+Repair 20-case direct-fill review workbook.
- [dbox_guard_repair_fairness_report_20260517.zh.md](dbox_guard_repair_fairness_report_20260517.zh.md): 中文 DBox+Guard+Repair 20-case 补评结果报告，汇总 targeted fairness sensitivity、同 case 主实验对照和论文口径。
- [dbox_guard_repair_fairness_report_20260517.md](dbox_guard_repair_fairness_report_20260517.md): English DBox+Guard+Repair 20-case fairness sensitivity report with same-case main-experiment comparisons.
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`: 离线复算 dialogue-state v3 paper-facing tables / paired WTL / sensitivity / Repair stress / DBox fairness / DeepSeek LLM grader calibration 的脚本。
- `evals/aichat/verify_dialogue_state_v3_reports.py`: 离线 report verification gate，检查 Markdown 报告中的核心数字是否与机器可读证据一致。
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
- [prompt_freeze_readiness_report_20260512.zh.md](prompt_freeze_readiness_report_20260512.zh.md): 中文 prompt / judge / rubric freeze readiness checkpoint，说明哪些条件可进入 50-case held-out，哪些只能作为 dev/appendix。
- [prompt_freeze_readiness_report_20260512.md](prompt_freeze_readiness_report_20260512.md): English prompt / judge / rubric freeze readiness checkpoint.
- [prompt_freeze_decision_20260512.zh.md](prompt_freeze_decision_20260512.zh.md): 中文 prompt freeze 决策记录，固定 50-case 主实验候选矩阵，并将 EDF-inspired 降级为 dev / appendix 候选。
- [prompt_freeze_decision_20260512.md](prompt_freeze_decision_20260512.md): English prompt freeze decision record.
- [heldout_50_prelaunch_checklist_v1.zh.md](heldout_50_prelaunch_checklist_v1.zh.md): 中文 50-case held-out 发车前检查清单，定义 Go/No-go、数据、标注、日志和 headline claim 条件。
- [heldout_50_prelaunch_checklist_v1.md](heldout_50_prelaunch_checklist_v1.md): English 50-case held-out prelaunch checklist.
- [heldout_50_main_experiment_runbook_v1.zh.md](heldout_50_main_experiment_runbook_v1.zh.md): 中文 50-case held-out 主实验 runbook，固定 `heldout_main` 条件集、timeout、完整性检查、定向重跑/合并和盲评导出流程。
- [heldout_50_main_experiment_runbook_v1.md](heldout_50_main_experiment_runbook_v1.md): English 50-case held-out main experiment runbook.
- [heldout_50_generation_only_runbook_20260514.zh.md](heldout_50_generation_only_runbook_20260514.zh.md): 中文 50-case generation-only runbook，先用 5 个候选 condition 生成 250 条回复，只检查稳定性、空回复、延迟和完整性，不做评分结论。
- [heldout_50_generation_only_runbook_20260514.md](heldout_50_generation_only_runbook_20260514.md): English 50-case generation-only runbook for the 5-condition stability run before coach review.
- [context_aware_generation_smoke_20260514.zh.md](context_aware_generation_smoke_20260514.zh.md): 中文上下文感知生成 smoke 报告，记录 v3 数据和离线 runner 修复后，无上下文与 follow-up 上下文 case 的完整性检查和剩余泄露风险。
- [context_aware_generation_smoke_20260514.md](context_aware_generation_smoke_20260514.md): English context-aware generation smoke report for the v3 dataset and offline runner context-injection fix.
- [heldout_v3_50_context_readiness_audit_20260514.zh.md](heldout_v3_50_context_readiness_audit_20260514.zh.md): 中文 v3 50-case 上下文充分性审计，区分 main scaffold eval、clarification safety slice 和谨慎使用样本，避免把短问无上下文的数据问题误归因为模型/架构问题。
- [heldout_v3_50_context_readiness_audit_20260514.md](heldout_v3_50_context_readiness_audit_20260514.md): English context-readiness audit for the v3 50-case draft, separating main scaffold cases from clarification/safety slices.
- [bridgebench_cp_heldout_v4_50_generation_report_20260514.zh.md](bridgebench_cp_heldout_v4_50_generation_report_20260514.zh.md): 中文 v4 50-case follow-up scaffold 版本生成报告，说明 v3 前 10 条短问无上下文样本如何补入最小 synthetic-but-grounded 上一轮 AI probe。
- [bridgebench_cp_heldout_v4_50_generation_report_20260514.md](bridgebench_cp_heldout_v4_50_generation_report_20260514.md): English generation report for the v4 follow-up scaffold draft derived from v3.
- [heldout_v4_50_context_readiness_audit_20260514.zh.md](heldout_v4_50_context_readiness_audit_20260514.zh.md): 中文 v4 50-case 上下文充分性审计；当前 v4 已无 `insufficient` 样本，更适合 generation-only 和主 scaffolding dev run。
- [heldout_v4_50_context_readiness_audit_20260514.md](heldout_v4_50_context_readiness_audit_20260514.md): English context-readiness audit for the v4 follow-up scaffold draft.
- [v4_context_generation_smoke2_20260514.zh.md](v4_context_generation_smoke2_20260514.zh.md): 中文 v4 2-case × 5-condition generation smoke 报告，确认上下文注入链路可用，同时记录状态/表示类回复仍有 definition-first 风险。
- [v4_context_generation_smoke2_20260514.md](v4_context_generation_smoke2_20260514.md): English v4 2-case × 5-condition generation smoke report.
- [dbox_bridge_hybrid_generation_only_v4_50_integrity_20260514.zh.md](dbox_bridge_hybrid_generation_only_v4_50_integrity_20260514.zh.md): 中文 v4 50-case × 5-condition generation-only 完整性报告，记录 250/250 回复、targeted rerun 和自动风险诊断。
- [dbox_bridge_hybrid_generation_only_v4_50_integrity_20260514.md](dbox_bridge_hybrid_generation_only_v4_50_integrity_20260514.md): English integrity report for the v4 50-case × 5-condition generation-only run.
- [dbox_bridge_hybrid_generation_only_50_integrity_20260515.zh.md](dbox_bridge_hybrid_generation_only_50_integrity_20260515.zh.md): 中文 DBox / Bridge hybrid 50-case × 5-condition generation-only 完整性报告，记录 clean merged 250-row dev run、targeted rerun 和静态风险摘要。
- [dbox_bridge_hybrid_generation_only_50_integrity_20260515.md](dbox_bridge_hybrid_generation_only_50_integrity_20260515.md): English integrity report for the clean merged 50-case × 5-condition DBox / Bridge hybrid generation-only run.
- [dbox_bridge_hybrid_generation_only_50_review_launch_20260515.zh.md](dbox_bridge_hybrid_generation_only_50_review_launch_20260515.zh.md): 中文 50-case × 5-condition 教练盲评启动说明，列出 review workbook、hidden key、评分流程和开发阶段边界。
- [dbox_bridge_hybrid_generation_only_50_review_launch_20260515.md](dbox_bridge_hybrid_generation_only_50_review_launch_20260515.md): English review launch note for the 50-case × 5-condition DBox / Bridge hybrid workbook.
- [dbox_bridge_hybrid_generation_only_50_ai_prelim_analysis_20260515.zh.md](dbox_bridge_hybrid_generation_only_50_ai_prelim_analysis_20260515.zh.md): 中文 250-row AI 预评分析，仅作为开发筛查，比较五个匿名 condition 的质量、泄露和 student-ready 趋势。
- [dbox_bridge_hybrid_generation_only_50_ai_prelim_analysis_20260515.md](dbox_bridge_hybrid_generation_only_50_ai_prelim_analysis_20260515.md): English AI-preliminary analysis for the 250-row DBox / Bridge hybrid dev run.
- [dbox_bridge_hybrid_calibration5_launch_20260515.zh.md](dbox_bridge_hybrid_calibration5_launch_20260515.zh.md): 中文 5-case 教练校准盲评包说明，解释选取理由、评分流程和不作为正式结果的边界。
- [dbox_bridge_hybrid_calibration5_launch_20260515.md](dbox_bridge_hybrid_calibration5_launch_20260515.md): English launch note for the 5-case coach-calibration blind review pack.
- [dbox_bridge_hybrid_full_fairness_50_human_review_analysis_20260515.zh.md](dbox_bridge_hybrid_full_fairness_50_human_review_analysis_20260515.zh.md): 中文 50-case × 10-condition 人工盲评分析，合并 hidden key 后汇总 overall/core6/sufficiency/micro7/student-ready/leakage 和配对比较。
- [dbox_bridge_hybrid_full_fairness_50_human_review_analysis_20260515.md](dbox_bridge_hybrid_full_fairness_50_human_review_analysis_20260515.md): English human-review analysis for the 50-case × 10-condition full fairness dev ablation.
- [dbox_bridge_hybrid_full_fairness_50_human_review_analysis_v3_20260515.zh.md](dbox_bridge_hybrid_full_fairness_50_human_review_analysis_v3_20260515.zh.md): 中文 v3 主指标/诊断指标重分析报告，基于同一 500-row 人工盲评表。
- [dbox_bridge_hybrid_full_fairness_50_human_review_analysis_v3_20260515.md](dbox_bridge_hybrid_full_fairness_50_human_review_analysis_v3_20260515.md): English v3 primary/diagnostic reanalysis for the same 500-row human review.
- [dbox_bridge_hybrid_full_fairness_50_human_review_memo_20260515.zh.md](dbox_bridge_hybrid_full_fairness_50_human_review_memo_20260515.zh.md): 中文人工盲评备忘，解释 DBox-inspired、Bridge Contract compact、Bridge-guided DBox-style Guard、Guard 和 Repair 的主要取舍。
- [dbox_bridge_hybrid_full_fairness_50_human_review_memo_20260515.md](dbox_bridge_hybrid_full_fairness_50_human_review_memo_20260515.md): English memo interpreting the 50-case full fairness human-review results.
- [v4_generation_only_ai_prelim_review_20260514.zh.md](v4_generation_only_ai_prelim_review_20260514.zh.md): 中文 v4 250-row AI 预评摘要，记录 GPT-5.5/xhigh dev triage、主要风险模式和 19-case 高风险教练复核包。
- [v4_generation_only_ai_prelim_review_20260514.md](v4_generation_only_ai_prelim_review_20260514.md): English summary of the v4 250-row AI preliminary review and high-risk coach-review pack.
- [heldout_50_formal_preflight_report_20260513.zh.md](heldout_50_formal_preflight_report_20260513.zh.md): 中文 50-case held-out formal preflight 报告，说明当前草稿结构合格但因 `draft_needs_coach_review` 状态未通过 frozen-status 门禁。
- [heldout_50_formal_preflight_report_20260513.md](heldout_50_formal_preflight_report_20260513.md): English formal preflight report for the 50-case held-out draft.
- [heldout_50_readiness_20260513.zh.md](heldout_50_readiness_20260513.zh.md): 中文 50-case held-out readiness 报告，汇总 Coach A/B 标注、frozen JSONL 和 formal preflight 当前 blocker。
- [heldout_50_readiness_20260513.md](heldout_50_readiness_20260513.md): English readiness report for the 50-case held-out launch gate.
- [coach_a_heldout_50_ai_labeled_v1_20260513.zh.md](coach_a_heldout_50_ai_labeled_v1_20260513.zh.md): 中文 Coach A 50-case AI 初标摘要，列出 subtype/family 分布、低置信、needs_new_focus 和 schema 痛点。
- [coach_a_heldout_50_ai_labeled_v1_20260513.md](coach_a_heldout_50_ai_labeled_v1_20260513.md): English summary of the Coach A AI-assisted 50-case draft labels.
- [coach_a_heldout_50_ai_label_quality_check_20260513.zh.md](coach_a_heldout_50_ai_label_quality_check_20260513.zh.md): 中文 Coach A 50-case AI 初标质量检查，确认行数、case_id、deprecated subtype、family-subtype、needs_new_focus 和优先人工复核样本。
- [coach_a_heldout_50_ai_label_quality_check_20260513.md](coach_a_heldout_50_ai_label_quality_check_20260513.md): English quality check for the Coach A AI-assisted 50-case draft labels.
- [heldout_50_ai_reference_smoke1_integrity_20260513.zh.md](heldout_50_ai_reference_smoke1_integrity_20260513.zh.md): 中文 heldout_main 1-case × 8-condition smoke 完整性检查，确认回复和盲评表可正常生成。
- [heldout_50_ai_reference_smoke1_integrity_20260513.md](heldout_50_ai_reference_smoke1_integrity_20260513.md): English integrity report for the heldout_main 1-case × 8-condition smoke.
- [heldout_50_ai_reference_dev_merged_integrity_20260513.zh.md](heldout_50_ai_reference_dev_merged_integrity_20260513.zh.md): 中文 50-case × 8-condition AI draft reference dev run 合并后完整性检查，确认定向补跑后 400/400 条目标回复齐全。
- [heldout_50_ai_reference_dev_merged_integrity_20260513.md](heldout_50_ai_reference_dev_merged_integrity_20260513.md): English integrity report for the merged 50-case × 8-condition AI draft reference dev run.
- [heldout_50_ai_prelim_review_analysis_20260513.zh.md](heldout_50_ai_prelim_review_analysis_20260513.zh.md): 中文 50-case × 8-condition AI 初评分析，汇总系统质量、student-ready、泄露标签和 paired comparisons；仅用于 dev 筛查，不作为 coach gold。
- [heldout_50_ai_prelim_review_analysis_20260513.md](heldout_50_ai_prelim_review_analysis_20260513.md): English AI preliminary review analysis for the 50-case × 8-condition dev run.
- [heldout_50_ai_prelim_high_risk_review_pack_20260513.zh.md](heldout_50_ai_prelim_high_risk_review_pack_20260513.zh.md): 中文 50-case AI 预评高风险教练复核包说明，抽出 25 条高风险回复和 11-case / 88-row 同题比较包，供教练优先确认泄露与误报。
- [heldout_50_ai_prelim_high_risk_review_pack_20260513.md](heldout_50_ai_prelim_high_risk_review_pack_20260513.md): English note for the 50-case AI preliminary high-risk coach review pack.
- [heldout_50_high_risk_case_pack_review_analysis_20260513.zh.md](heldout_50_high_risk_case_pack_review_analysis_20260513.zh.md): 中文 11-case / 88-row 高风险 case pack 教练盲审分析，显示 AI 预评偏保守，`bridge_contract_guard` 在该 slice 上综合最稳。
- [heldout_50_high_risk_case_pack_review_analysis_20260513.md](heldout_50_high_risk_case_pack_review_analysis_20260513.md): English coach-review analysis for the 11-case / 88-row high-risk case pack.
- [heldout_50_coach_labeling_launch_20260512.zh.md](heldout_50_coach_labeling_launch_20260512.zh.md): 中文 50-case held-out 教练审查启动说明，列出 Coach A 全量表、Coach B 20 条复标表和标注边界。
- [heldout_50_coach_labeling_launch_20260512.md](heldout_50_coach_labeling_launch_20260512.md): English 50-case held-out coach labeling launch note.
- `evals/aichat/summarize_coach_label_agreement.py`: Coach A / Coach B JSONL agreement summary 工具，可输出 JSON 与中英文 Markdown 报告，用于 adjudication planning。
- `evals/aichat/export_coach_adjudication_workbook.py`: Coach A / Coach B overlap 裁决表导出工具，把 disagreement case 的 A/B 标签并排展示，供最终 reference 裁决。
- [bridge_contract_prompt_abstraction_smoke_20260512.zh.md](bridge_contract_prompt_abstraction_smoke_20260512.zh.md): Bridge Contract prompt 抽象化与 clean offline prompt 的中文 smoke 报告，记录 clean prompt 修掉线上污染但高风险 contribution/aggregation bridge 仍会产生 answer-bearing micro-example。
- [bridge_contract_prompt_abstraction_smoke_20260512.md](bridge_contract_prompt_abstraction_smoke_20260512.md): English smoke report for Bridge Contract prompt abstraction and the clean offline prompt path.
- [literature_baseline_smoke1_report_20260511.zh.md](literature_baseline_smoke1_report_20260511.zh.md): 1-case 中文 smoke，检查 DBox-inspired、CodeHelp/CodeAid-style 和 Bridge-inspired baseline 的真实输出 schema 与早期泄露风险。
- [literature_baseline_smoke1_report_20260511.md](literature_baseline_smoke1_report_20260511.md): English 1-case smoke report for literature baselines.
- [dev_ablation_suite_smoke_report_20260511.zh.md](dev_ablation_suite_smoke_report_20260511.zh.md): P1 dev ablation suite 中文 smoke，验证 shared runner、summary 和盲评导出链路。
- [dev_ablation_suite_smoke_report_20260511.md](dev_ablation_suite_smoke_report_20260511.md): English P1 dev ablation suite smoke report.
- [dev_ablation_limit10_report_20260511.zh.md](dev_ablation_limit10_report_20260511.zh.md): P1 10-case dev ablation 中文执行报告，包含 11 个条件、110 条回复、自动 leakage/latency 摘要和盲评入口。
- [dev_ablation_limit10_report_20260511.md](dev_ablation_limit10_report_20260511.md): English P1 10-case dev ablation execution report.
- [dev_ablation_safe_scaffold_limit10_report_20260512.zh.md](dev_ablation_safe_scaffold_limit10_report_20260512.zh.md): P1 10-case dev ablation + safe scaffold 中文执行报告，包含 12 个条件、120 条回复和 high-risk safe fallback appendix condition。
- [dev_ablation_safe_scaffold_limit10_report_20260512.md](dev_ablation_safe_scaffold_limit10_report_20260512.md): English P1 10-case dev ablation report with the safe scaffold appendix condition.
- [dev_ablation_safe_scaffold_blind_review_analysis_20260512.zh.md](dev_ablation_safe_scaffold_blind_review_analysis_20260512.zh.md): 10-case dev ablation + safe scaffold 中文盲评分析，合并匿名 key 后比较 12 个条件的 quality/leakage/student-ready/pass。
- [dev_ablation_safe_scaffold_blind_review_analysis_20260512.md](dev_ablation_safe_scaffold_blind_review_analysis_20260512.md): English blind-review analysis for the 10-case dev ablation + safe scaffold run.
- [dev_ablation_response_burden_analysis_20260512.zh.md](dev_ablation_response_burden_analysis_20260512.zh.md): 10-case dev ablation 的中文回复负担分析，启发式标注学生下一轮需要输入的 low/medium/high 负担。
- [dev_ablation_response_burden_analysis_20260512.md](dev_ablation_response_burden_analysis_20260512.md): English response-burden analysis for the 10-case dev ablation labels.
- [dev_ablation_static_lint_reanalysis_20260512.zh.md](dev_ablation_static_lint_reanalysis_20260512.zh.md): 10-case dev ablation 的中文 static lint 复分析，比较自动 Guard 标签和 answer-slot / filled-trace / worked-example 风险信号。
- [dev_ablation_static_lint_reanalysis_20260512.md](dev_ablation_static_lint_reanalysis_20260512.md): English static lint reanalysis for the 10-case dev ablation.
- [dev_ablation_major_leakage_self_review_20260512.zh.md](dev_ablation_major_leakage_self_review_20260512.zh.md): 10-case dev ablation 中 8 条 major bridge leakage 的中文自盲评与 prompt/rubric 修复记录。
- [dev_ablation_major_leakage_self_review_20260512.md](dev_ablation_major_leakage_self_review_20260512.md): English self-review and patch record for major leakage patterns in the 10-case dev ablation.
- [definition_first_regression_smoke_20260512.zh.md](definition_first_regression_smoke_20260512.zh.md): definition-first / worked-example 修复后的 5-case targeted smoke 中文记录，显示 answer-slot question 仍是剩余风险。
- [definition_first_regression_smoke_20260512.md](definition_first_regression_smoke_20260512.md): English targeted smoke after the definition-first / worked-example prompt patch.
- [definition_first_post_repair_self_review_20260512.zh.md](definition_first_post_repair_self_review_20260512.zh.md): definition-first / post-repair 二次检测的中文自盲评，记录 Repair 失败和 `repair_still_leaks_rate`。
- [definition_first_post_repair_self_review_20260512.md](definition_first_post_repair_self_review_20260512.md): English self-review of post-repair leakage checks on the definition-first regression cases.
- [definition_first_post_repair_self_review_20260512.jsonl](definition_first_post_repair_self_review_20260512.jsonl): post-repair 二次检测自盲评标签 JSONL。
- [post_repair_fallback_smoke_20260512.zh.md](post_repair_fallback_smoke_20260512.zh.md): `--post-repair-fallback-on-leak` 中文 smoke 报告，说明 fallback 只能处理被二次检测抓到的坏 Repair，不能弥补 post-repair Guard 漏检。
- [post_repair_fallback_smoke_20260512.md](post_repair_fallback_smoke_20260512.md): English smoke report for the optional post-repair fallback-on-leak path.
- [answer_slot_guard_patch_self_review_20260512.zh.md](answer_slot_guard_patch_self_review_20260512.zh.md): answer-slot Guard patch 后的中文自盲评，显示 prompt-only Guard 校准仍漏掉 4/5 个 major bridge leakage。
- [answer_slot_guard_patch_self_review_20260512.md](answer_slot_guard_patch_self_review_20260512.md): English self-review showing that the answer-slot Guard prompt patch still misses most major bridge leakage cases.
- [answer_slot_guard_patch_self_review_20260512.jsonl](answer_slot_guard_patch_self_review_20260512.jsonl): answer-slot Guard patch 自盲评标签 JSONL。
- [short_constructed_response_smoke_20260512.zh.md](short_constructed_response_smoke_20260512.zh.md): 短生成式回复策略与 answer-slot guard 后的中文 smoke 报告，显示“少写一点”本身不能可靠避免把关键桥改写成答案槽位。
- [short_constructed_response_smoke_20260512.md](short_constructed_response_smoke_20260512.md): English smoke report for the short constructed response policy and answer-slot guard patch.
- [mini_study_20_report_20260510.zh.md](mini_study_20_report_20260510.zh.md): 20 条 seed mini-study 中文初步报告。
- [mini_study_20_report_20260510.md](mini_study_20_report_20260510.md): 20-seed mini-study preliminary English report.
- [hard_gate_overfallback_rerun_20260510.zh.md](hard_gate_overfallback_rerun_20260510.zh.md): hard gate 过度兜底修复后的中文定点复测报告。
- [hard_gate_overfallback_rerun_20260510.md](hard_gate_overfallback_rerun_20260510.md): English targeted rerun report for the hard-gate overfallback fix.
- [repair_prompt_fix_mini_study_20_20260510.zh.md](repair_prompt_fix_mini_study_20_20260510.zh.md): Repair prompt 修复后的 20 条中文复测报告。
- [repair_prompt_fix_mini_study_20_20260510.md](repair_prompt_fix_mini_study_20_20260510.md): English 20-case rerun report after the repair prompt fix.
- [repair_stress_v1_smoke_report_20260511.zh.md](repair_stress_v1_smoke_report_20260511.zh.md): 12-case Repair stress 中文 smoke 报告，专门测试高泄露候选回复的 detect -> repair -> second-pass guard 链路。
- [repair_stress_v1_smoke_report_20260511.md](repair_stress_v1_smoke_report_20260511.md): English report for the 12-case Repair stress smoke.
- [repair_stress_v1_all20_report_20260511.zh.md](repair_stress_v1_all20_report_20260511.zh.md): 20-case Repair stress 中文报告，扩展 KMP、贪心正确性、单调结构、初始化、局部补全、调试反例、前缀和和算法确认等高泄露压力样本。
- [repair_stress_v1_all20_report_20260511.md](repair_stress_v1_all20_report_20260511.md): English report for the 20-case Repair stress run.

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
- [coach_response_review_workbook_repair_stress_v1_all20_20260511.zh.xlsx](coach_response_review_workbook_repair_stress_v1_all20_20260511.zh.xlsx): Repair stress v1 all20 before/after 中文盲评表，共 40 条匿名回复。
- [coach_response_review_workbook_repair_stress_v1_all20_20260511.csv](coach_response_review_workbook_repair_stress_v1_all20_20260511.csv): Repair stress v1 all20 before/after CSV。
- [coach_response_review_workbook_repair_stress_v1_all20_20260511.key.csv](coach_response_review_workbook_repair_stress_v1_all20_20260511.key.csv): Repair stress v1 all20 before/after 匿名 key。
- [coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.zh.xlsx](coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.zh.xlsx): prompt-controlled ablation 3-case 中文盲评表，共 15 条匿名回复。
- [coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.key.csv](coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.key.csv): prompt-controlled ablation 3-case 匿名 key。
- [coach_response_review_labels_prompt_controlled_ablation_smoke3_20260511.jsonl](coach_response_review_labels_prompt_controlled_ablation_smoke3_20260511.jsonl): prompt-controlled ablation 3-case 盲评标签 JSONL，已映射到匿名系统条件。
- [coach_response_review_workbook_fair_mini_study_20_20260511.zh.xlsx](coach_response_review_workbook_fair_mini_study_20_20260511.zh.xlsx): 7-system fair 20-case mini-study 的中文盲评表，共 140 条匿名回复。
- [coach_response_review_labels_dev_ablation_safe_scaffold_20260512.jsonl](coach_response_review_labels_dev_ablation_safe_scaffold_20260512.jsonl): 10-case dev ablation + safe scaffold 盲评标签 JSONL，已映射到 12 个匿名系统条件。
- [coach_response_review_labels_dev_ablation_safe_scaffold_20260512.with_burden.jsonl](coach_response_review_labels_dev_ablation_safe_scaffold_20260512.with_burden.jsonl): 同一批盲评标签的启发式回复负担增强版，包含 `student_response_burden`、`burden_reasons` 和匹配模式。
- [coach_response_review_labels_dbox_bridge_hybrid_full_fairness_50_v3_20260515.jsonl](coach_response_review_labels_dbox_bridge_hybrid_full_fairness_50_v3_20260515.jsonl): 50-case × 10-condition 人工盲评的 v3 merged labels，包含主指标、诊断指标和 case-specific rubric 字段。
- [llm_grader_calibration_pack_20row_v3_20260515.jsonl](llm_grader_calibration_pack_20row_v3_20260515.jsonl): 从 v3 merged labels 抽取的 20-row / 60-task LLM grader calibration prompt pack，不含真实 LLM 输出。

### Held-out Dataset Draft

- [bridgebench_cp_heldout_v1_50_draft.jsonl](bridgebench_cp_heldout_v1_50_draft.jsonl): Research v1 50-case held-out 草稿数据集，状态为 `draft_needs_coach_review`，不可直接作为 adjudicated gold。
- [bridgebench_cp_heldout_v1_50_ai_reference_draft_20260513.jsonl](bridgebench_cp_heldout_v1_50_ai_reference_draft_20260513.jsonl): 50-case held-out 草稿与 Coach A AI 初标合并后的 AI-assisted draft reference，便于 dev-stage response generation；不可称为 final gold。
- [coach_seed_labeling_workbook_heldout_v1_50_draft.zh.xlsx](coach_seed_labeling_workbook_heldout_v1_50_draft.zh.xlsx): 50-case held-out 草稿的中文教练审查/标注 workbook，包含近期对话列和空白标签列，供 Coach A 审查后再冻结。
- [coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx](coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx): Coach A 全量 50-case 标注 workbook。
- [bridgebench_cp_heldout_v1_50_coach_b_overlap_20.jsonl](bridgebench_cp_heldout_v1_50_coach_b_overlap_20.jsonl): Coach B 20-case overlap 子集，覆盖 10 个 category，并包含 8 条代码样本。
- [coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx](coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx): Coach B 20-case overlap 复标 workbook，包含 `student_code_excerpt` 列。
- [bridgebench_cp_heldout_v1_50_card.zh.md](bridgebench_cp_heldout_v1_50_card.zh.md): 中文 50-case held-out dataset card，说明字段、类别分布、代码片段分布、使用规则和下一步教练审查流程。
- [bridgebench_cp_heldout_v1_50_card.md](bridgebench_cp_heldout_v1_50_card.md): English 50-case held-out dataset card.
- [bridgebench_cp_heldout_v1_50_validation_report.json](bridgebench_cp_heldout_v1_50_validation_report.json): held-out 草稿结构校验报告，检查 50 条数量、必填字段、代码样本数量、草稿状态和 dev seed id overlap。
- [bridgebench_cp_heldout_v1_50_formal_preflight_report.json](bridgebench_cp_heldout_v1_50_formal_preflight_report.json): held-out formal preflight JSON，当前预期失败于 `frozen_status_required`，用于防止草稿数据直接进入 headline run。

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

For the Research v1 development ablation, use the shared suite runner instead of hand-running each baseline:

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10 \
  --limit 10 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

The suite writes per-condition JSONL files, `combined_dev_ablation.jsonl`, bilingual summary files, an anonymized coach-review CSV, a key CSV, and a Chinese XLSX workbook. This is the preferred P1 path for comparing `enhanced_prompt_only`, DBox-inspired, DBox-inspired + Guard, Bridge-inspired, single-LLM, and Bridge Contract variants.

For the smaller EDF-inspired development matrix, keep the run intentionally narrow:

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/edf_core_ablation_YYYYMMDD \
  --limit 10 \
  --condition-set edf_core \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

The `edf_core` condition set contains only `enhanced_prompt_only_clean`, `dbox_inspired_guard`, `edf_inspired_clean`, `edf_inspired_guard`, `bridge_contract_guard`, and `bridge_contract_guard_repair`. It is for EDF dev screening and appendix decisions, not a new default main matrix.

If you want to include the dev-only deterministic safe scaffold as an appendix / stress condition, add:

```bash
  --include-safe-scaffold
```

This appends `bridge_contract_safe_scaffold` with `pipeline_mode=deterministic_safe_scaffold`. It is intentionally not part of the default main suite and does not affect online AIChat.

For every row, preserve:

- `candidate_response_text`
- `final_response_text`
- `context_ai_reply`
- `final_response_source`
- `runtime_bridge_contract`
- `leakage_judge_result`
- `repair_result`
- `post_repair_leakage_judge_result`
- `repair_still_leaks`
- `safe_fallback_after_repair_result` when `--post-repair-fallback-on-leak` is enabled and Repair still leaks
- `candidate_static_leakage_risk_lint`
- `final_static_leakage_risk_lint`
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
4. Use the EDF-inspired 10-case AI self-review only as dev screening; do not promote EDF to the 50-case main table unless coach review confirms quality and leakage are competitive with strong prompt and DBox+Guard.
5. Build the 50-case held-out set only after prompt/rubric versions are frozen on the dev/regression set.
6. Run partial double annotation and judge calibration before using any result as a headline paper claim.

## Reporting Rule

For reports meant for review, keep bilingual pairs:

- English: `*.md`
- Chinese: `*.zh.md`

For coach-facing use, the Chinese report is the primary reading surface. For external AI or paper collaborators, the English report is the companion artifact.

Validate new research Markdown documents with:

```bash
python3 -m evals.aichat.validate_research_bilingual_docs \
  --root docs/research \
  --output-json docs/research/bilingual_docs_validation_report.json
```

The validator allows current legacy unpaired Markdown debt but fails on newly added single-language research docs.
