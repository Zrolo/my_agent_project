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
- current_system、single_llm_structured、bridge_contract、guard、repair 的离线消融；
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

## Core Documents

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

### Runtime Contract And Registries

- [runtime_bridge_contract_schema_v1.json](runtime_bridge_contract_schema_v1.json): 运行时 compact bridge contract schema。
- [bridge_subtype_registry_v2.json](bridge_subtype_registry_v2.json): bridge subtype 与 family 的注册表。
- [focus_registry_v1.json](focus_registry_v1.json): 当前 focus registry。

### Offline Evaluation

- [bridge_judge_offline_eval_v1.md](bridge_judge_offline_eval_v1.md): 离线 Bridge Judge / Tutor / Guard / Repair 评测设计。
- [judge_schema_smoke_report_20260509.md](judge_schema_smoke_report_20260509.md): 20-case judge schema smoke 结果。
- [response_ablation_smoke_report_20260509.md](response_ablation_smoke_report_20260509.md): response ablation smoke 结果。
- [tutor_thinking_ablation_smoke_report_20260509.md](tutor_thinking_ablation_smoke_report_20260509.md): thinking mode smoke 结果。

### Response Blind Review

- [coach_response_review_analysis_20260509.zh.md](coach_response_review_analysis_20260509.zh.md): 中文盲评小样本分析。
- [coach_response_review_analysis_20260509.md](coach_response_review_analysis_20260509.md): English blind review mini-analysis.
- [coach_response_review_micro_example_policy_n10_20260510.zh.md](coach_response_review_micro_example_policy_n10_20260510.zh.md): micro-example policy 中文分析。
- [coach_response_review_micro_example_policy_n10_20260510.md](coach_response_review_micro_example_policy_n10_20260510.md): micro-example policy English analysis.

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
2. Add `single_llm_structured` baseline if missing.
3. Run a 20-case mini-study across current_system / single_llm_structured / bridge_contract / guard / repair.
4. Export Chinese and English reports for the mini-study.
5. Expand to 50 coach-labeled seed cases only after the 20-case pipeline is stable.

## Reporting Rule

For reports meant for review, keep bilingual pairs:

- English: `*.md`
- Chinese: `*.zh.md`

For coach-facing use, the Chinese report is the primary reading surface. For external AI or paper collaborators, the English report is the companion artifact.
