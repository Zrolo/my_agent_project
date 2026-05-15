# Formal Evaluation Protocol v1

日期：2026-05-14

本文件是 CP-MissingBridgeBench 的正式评测协议草案。它的作用不是汇报实验结果，而是在看正式 held-out 结果之前，固定哪些实验是主实验、哪些是辅助实验、哪些只能作为探索性分析，降低 cherry-picking、p-hacking、benchmark overfitting 和 test-set contamination 风险。

## 核心原则

数据应当影响结论，但不能反过来影响已经声明为正式的实验设计。

允许：

- 在 dev set 上发现问题、修 runner、修导出表、修数据质量；
- 在 dev set 上比较 prompt、condition、follow-up 形式和 AI-student simulation 可行性；
- 根据 dev evidence 冻结正式协议；
- 在正式结果出来后诚实报告负结果、失败模式和不确定性。

不允许：

- 看完正式 held-out 结果后更换主实验；
- 看见某 condition 分数高后把它升为主方法；
- 看见某指标不好后删除该指标；
- 看见某 prompt 失败后回头修改同一批正式测试再声称是 held-out；
- 把 AI 自评写成 coach gold；
- 把 draft 数据或 context-contaminated run 写成正式论文 headline。

## 数据分层

### Dev / Regression Set

用途：

- prompt 调试；
- runner 修复；
- workbook 字段修复；
- condition 选择；
- follow-up / AI-student simulation 可行性测试；
- leakage rubric 和 static lint 的开发。

允许反复运行和修改，但所有修改必须记录在 `prompt_patch_log.md`、`judge_prompt_patch_log.md` 或相应 runbook 中。

### Draft Held-out Cases

当前 clean draft：

```text
docs/research/bridgebench_cp_heldout_v3_50_draft.jsonl
```

该版本修复了 v2 的 `recent_dialogue` / `student_message` 错配问题，但仍是 `draft_needs_coach_review`，不能称为 gold。

用途：

- 数据质量复核；
- generation-only stability check；
- 确认题源、题面、学生问题、近期对话和代码片段是否足够自然、可评审。

不能用于：

- 正式论文 headline；
- prompt 结果调优后再称为 held-out；
- 直接替代 Coach A / Coach B 标注。

### Frozen Held-out Reference

正式主实验必须使用 frozen reference JSONL，例如：

```text
docs/research/bridgebench_cp_heldout_v3_50_frozen.jsonl
```

Go 条件：

- 50 条 case 完成题源和上下文复核；
- Coach A 完成全量 reference 标注；
- Coach B 完成至少 20 条 overlap 复标；
- 低置信、多桥梁和重大分歧完成裁决或单独标记；
- `validate_heldout_50_dataset --require-frozen-status` 通过；
- prompt / judge / repair / review rubric / model runtime 已冻结。

## 实验层级

### Primary Experiment: Single-turn Held-out Evaluation

主实验仍是单轮 50-case evaluation。

目的：

- 评估 turn-level missing bridge diagnosis；
- 评估 critical bridge leakage；
- 比较不同 tutoring harness 在质量、泄露、延迟和调用成本上的权衡。

主实验不声称：

- 等同真实长期课堂学习收益；
- 证明某框架在所有交互场景中最优；
- 证明多轮学生学习效果。

推荐主表条件应在正式运行前固定，例如：

```text
current_system_deployment
enhanced_prompt_only_clean
codehelp_codeaid_clean
dbox_inspired_guard
bridge_inspired_expert_decision_clean
single_llm_structured_guard
bridge_contract_compact_guard
bridge_contract_compact_guard_repair
```

实际条件以 frozen runbook 为准。正式运行后不得因为结果不理想替换主表条件。

### Secondary Experiment: Controlled Follow-up Stress Test

受控追问压力测试是 secondary，不是主实验替代品。

目的：

- 检查学生短回复后，系统能否接住上下文；
- 检查系统是否重复无效问题、跳步、过早泄露关键桥；
- 比较不同 condition 在相同 follow-up probe 下的稳定性。

设计建议：

- 10-15 个 dev/frozen follow-up cases；
- 每个 case 固定 1-2 个学生短回复 probe；
- 同一个 probe 给所有 condition；
- 评估 continuity、scaffold adjustment、leakage、student-ready。

论文表述：

```text
controlled follow-up stress test
```

不能表述为：

```text
真实学生多轮学习实验
```

### Exploratory Experiment: AI-student Dynamic Simulation

AI-student simulation 只能作为 exploratory / appendix，除非未来单独设计并冻结 simulator protocol。

用途：

- 发现多轮交互失败模式；
- 观察 F1-F4 学生跟随状态下系统是否会重复、跳步或过早泄露；
- 产生 error analysis 案例。

风险：

- simulator bias；
- 不同 condition 轨迹分叉，难以严格配对；
- 学生模拟器可能过度配合或过度挑剔；
- 不能替代真实学生研究。

论文中如果使用，必须写：

```text
exploratory simulated dialogue analysis
```

不能写：

```text
student learning outcome
```

## Prompt / Judge Freeze

正式 held-out 前必须冻结：

- enhanced prompt-only prompt；
- DBox-inspired prompt；
- CodeHelp/CodeAid-style prompt；
- Bridge-inspired expert-decision prompt；
- Bridge Contract prompt；
- Leakage Guard prompt；
- Repair prompt；
- offline response grader prompt；
- offline leakage grader prompt；
- response review rubric；
- model/runtime configuration。

冻结后：

- 不根据正式 held-out 结果修改同一批 prompt；
- 如果必须修工程 bug，例如 context injection、空回复、JSON 解析、内部标签泄露，必须记录为 infrastructure fix；
- 如果修的是教学策略或泄露策略，则旧正式结果作废，必须重新声明为 dev run。

## Context Integrity

正式生成必须满足：

- `recent_dialogue` 和 `student_message` 不错配；
- generation runner 看到的上下文与教练盲评看到的上下文一致；
- `recent_dialogue` 解析为真实 `user/assistant` messages；
- `student_message` 作为最后一轮 user message；
- `problem_context`、`problem_title`、`problem_url`、`student_code_excerpt` 进入当前 user message；
- 结果记录 `generation_context_source` 和 `generation_message_count`；
- 学生可见回复不得残留 `[LEVEL:Lx]` 内部标签。

旧 v2 / zh5 上下文错配结果只能作为 development diagnostic，不能作为正式上下文盲评。

## Metrics

Primary metrics：

- overall quality；
- core6；
- scaffold appropriateness；
- bridge-oriented micro-example；
- student-ready pass；
- critical bridge leakage；
- answer/code leakage；
- p50 / p95 latency；
- LLM call count。

Secondary metrics：

- response burden；
- safe_ready；
- guard rewrite/block rate；
- repair_success_rate；
- repair_still_leaks_rate；
- static lint flags；
- stage errors。

Exploratory metrics：

- AI-student progress；
- simulated followability；
- episode-level coherence；
- repeated-question loop；
- simulator-reported confusion。

## Statistical Reporting

正式报告不得把 `cases × conditions` 的所有行当作独立样本。

必须优先使用 case-level paired reporting：

- win / tie / loss；
- mean paired difference；
- paired bootstrap confidence interval；
- Friedman test；
- Wilcoxon signed-rank with Holm correction；
- McNemar / paired categorical comparison for leakage where applicable。

20-case 或更小样本只能写作：

```text
pilot / dev evidence
```

不能写作：

```text
statistically proven headline result
```

## Result Interpretation Rules

如果强 baseline 胜出：

- 不能隐藏；
- 论文结论应转为：该 baseline 是强默认策略，missing bridge / critical leakage 仍作为评测和高风险控制信号有价值。

如果 Bridge Contract 只在高风险 subset 胜出：

- 可支持 risk-triggered routing；
- 不得声称它应无条件作为默认生成路径。

如果 Guard / Repair 降低泄露但降低质量：

- 报告质量-安全 trade-off；
- 不得写成“解决泄露”。

如果所有 strong baselines 都低泄露高质量：

- 需要弱化系统贡献；
- 强化 benchmark / evaluation framework 贡献；
- 分析 critical bridge leakage 是否只在特定高风险场景出现。

## Exclusion Rules

可排除：

- 缺题面或题源不可追溯；
- `recent_dialogue` 和 `student_message` 错配；
- final response 为空且定向重跑仍失败；
- 教练认为题面/学生问题不构成可评审教学场景；
- 明显重复 case。

不可排除：

- 某 condition 分数低；
- 某 case 对 Bridge Contract 不利；
- 某 baseline 意外很强；
- Guard/Repair 失败；
- 静态 lint 或人工评分暴露了论文不想看到的风险。

## Required Artifacts Before Paper Claims

正式论文结论前至少需要：

```text
formal_eval_protocol_v1.zh.md / .md
frozen dataset JSONL
frozen prompt / judge / rubric version notes
Coach A full labels
Coach B overlap labels
adjudication or disagreement report
generation integrity report
blind review workbook and hidden key
paired analysis report
judge calibration report
error analysis report
```

## Current Status

截至 2026-05-14：

- 单轮 held-out 仍是 primary；
- controlled follow-up stress test 是 secondary，仍待设计；
- AI-student simulation 是 exploratory，不能替代主实验；
- clean v3 draft 已生成，但仍需教练复核和 frozen export；
- 后续 50-case generation-only 必须使用 AIChat-compatible context injection；
- 旧 context-contaminated run 不进入正式 headline。
