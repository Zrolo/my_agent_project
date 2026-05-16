# CP-MissingBridgeBench 外部审核包（2026-05-15）

本文档用于交给其他 AI 或教练审核当前项目。它不是论文正文，也不是最终实验报告；它的作用是把当前项目定位、已完成工作、待验证问题和下一步计划放在同一个文件里，方便外部评审判断研究路线是否稳妥。

## 1. 项目当前定位

当前项目不再定位为“证明某个多 Agent 架构一定最强”的系统论文，而是定位为：

> **CP-MissingBridgeBench：面向算法竞赛 LLM 辅导的逐轮评测框架。**

核心研究对象是算法竞赛辅导中每一轮学生卡住的“缺失桥梁”（missing bridge），以及 AI 是否过早补完这座桥导致“关键桥梁泄露”（critical bridge leakage）。

当前论文主张应保持克制：

- 我们提出 CP-specific missing bridge schema。
- 我们定义 critical bridge leakage，用来捕捉传统 answer/code leakage 看不到的过度提示。
- 我们构建 coach-reference 和 blind review 流程。
- 我们比较 strong prompt、DBox-inspired、CodeHelp/CodeAid-style、Bridge-inspired、Bridge Contract、Guard、Repair 等 tutoring harness 在质量、泄露、延迟、调用成本上的权衡。

不建议声称：

- Bridge Contract 一定优于所有 baseline。
- 多层 LLM 一定优于单 LLM。
- LLM Judge 是 gold truth。
- 当前线上 AIChat 已经是完整 Bridge-aware Tutor。

## 2. 当前完成到哪里

### 2.1 研究范围和 baseline 策略

已经建立的研究边界：

- `docs/research/paper_scope_v2.zh.md`
- `docs/research/baseline_strategy_v1.zh.md`
- `docs/research/baseline_protocol_v1.zh.md`
- `docs/research/dbox_reproduction_gap_v1.zh.md`
- `docs/research/dbox_official_materials_review_v1.zh.md`

关键结论：

- `current_system` 只能作为 deployment baseline，不能作为唯一科研 baseline。
- DBox 不能完整复现为本论文 baseline，因为 DBox 是交互式 learner-LLM co-decomposition 系统，包含 step tree UI、progressive hints、代码与 step 对齐和真实学生 study。当前只实现 DBox-inspired single-turn decomposition baseline。
- CodeHelp/CodeAid-style baseline 用来检验“不给完整代码/题解”是否已经足够。
- Bridge-inspired expert-decision baseline 用来检验通用专家决策 prompt 是否已经能达到效果。

### 2.2 prompt 与评价体系治理

已经推进：

- prompt patch log 和 judge prompt patch log 已建立。
- 评价体系已升级到 case-specific rubric v3。
- 盲评表要求显示题面、近期对话、上下文 AI 回复、学生当前问题、目标 AI 回复，并给教练明确“先看哪里、后评哪里”的流程。
- 主指标应收束为少数几个：overall quality、student-ready / safe-ready、critical leakage、scaffold sufficiency、student response burden。
- 诊断指标用于 error analysis，不作为论文唯一结论。

相关文件：

- `docs/research/response_review_rubric_v3.zh.md`
- `docs/research/evaluation_protocol_v3.zh.md`
- `docs/research/case_specific_rubric_policy_v1.zh.md`
- `docs/research/coach_blind_review_instructions_v1.zh.md`

### 2.3 当前 50-case 数据集状态

当前推荐继续推进的是 dialogue-state v3 版本：

- 数据文件：`docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- 中文审核表：`docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- 英文审核表：`docs/research/dialogue_state_v3_50_source_and_case_review.en.xlsx`
- 生成脚本：`evals/aichat/generate_dialogue_state_v3_50.py`
- 中文生成报告：`docs/research/dialogue_state_v3_generation_report_20260513.zh.md`
- 英文生成报告：`docs/research/dialogue_state_v3_generation_report_20260513.md`
- 刷新说明：`docs/research/dialogue_state_v3_50_refresh_20260515.zh.md`
- 上下文 readiness audit：`docs/research/dialogue_state_v3_50_context_readiness_audit_20260515.zh.md`

这版数据的定位：

- 50 条均绑定洛谷真实题源。
- 学生问题是 synthetic-but-grounded，即基于真实题面和真实学生语言风格合成，不声称来自真实学生原话。
- 旧线上 AI 回复不进入数据集，避免 current_system 污染评测。
- 当前状态是 `draft_needs_coach_review`，不能称为 gold。

2026-05-15 后续更新：中英文审核表已加入结构化 case/source 审核列，包括 `source_ok`、`context_coherent`、`student_message_realistic`、`missing_bridge_ok`、`forbidden_content_ok`、`success_criteria_ok`、`leakage_boundary_ok`、`case_decision`、`issue_type`、`coach_fix_suggestion` 和 `reviewer_confidence`。这些字段用于统计 accept/revise/drop/discuss，不是 AI 回复质量评分。

当前分布约束：

| 维度 | 当前设计 |
| --- | --- |
| 总数 | 50 |
| 题源平台 | Luogu 50 |
| 学生问题长度 | short 20 / medium_short 15 / medium_long 10 / long 5 |
| 近期对话 | none 10 / short 25 / long 15 |
| 初始提问 vs 后续辅导轮 | initial 10 / followup 40 |
| 学生跟随状态 | F1 6 / F2 19 / F3 10 / F4 5 / N/A 10 |
| 代码或错误代码场景 | 至少 10，当前约 17 |

桥梁桶配额：

| 桥梁桶 | 数量 |
| --- | ---: |
| 状态/表示语义 | 6 |
| 转移/递推来源 | 5 |
| 判定条件/check | 5 |
| 边界更新/循环方向 | 5 |
| 建模/对象关系 | 5 |
| 贡献汇总/差分/前缀 | 4 |
| 数据结构操作/维护语义 | 5 |
| 贪心/不变量/正确性 | 5 |
| 实现边界/初始化/类型 | 4 |
| 调试证据/最小反例 | 3 |
| 直接要答案/代码/确认 | 3 |

### 2.4 已经做过的实验类型

已经完成或部分完成的都是 dev / pilot 证据，不应作为最终 headline result：

- 20-case fair blind review：说明 Bridge Contract variants 曾经有正向信号，但样本少、已用于开发。
- prompt-controlled ablation：说明 prompt effect 很强，必须有 strong prompt baseline。
- DBox-inspired / CodeHelp / Bridge-inspired smoke：说明 literature-inspired baseline 能运行，但还不是正式结果。
- Repair stress：说明 Repair 需要 same-candidate before/after 设计才能证明因果效果。
- DBox-Bridge hybrid 50 generation-only 及人工 review：暴露了上下文一致性、盲评表字段理解、Guard/Repair 可解释性等问题，不能直接当最终结论。

## 3. 当前主要问题

### 3.1 DBox-inspired baseline 很强

这是好事，不是坏事。它说明我们不再只赢弱 baseline。但这也要求论文不能写成“Bridge Contract 一定最强”。如果 DBox-inspired 最终仍然最好，论文仍可成立，但结论应写为：

> CP-MissingBridgeBench 揭示 DBox-style decomposition 是算法编程辅导的强默认策略；missing bridge 的价值可能主要体现在评测、泄露校准、guard/routing 信号和高风险样本分析中。

### 3.2 数据集仍需教练审核

dialogue-state v3 解决了若干早期数据问题，但仍需教练检查：

- 题面是否足够判断学生问题。
- 近期对话是否真实连贯。
- 学生问题是否像真实学生。
- missing bridge 是否合理。
- forbidden content 是否过严或过松。
- success criteria 是否能指导后续盲评。

### 3.3 评价主观性仍需控制

人类教练盲评天然有主观性。接下来需要：

- 双教练部分复标。
- 计算 agreement。
- 分歧 adjudication。
- LLM grader calibration 只能作为辅助，不当作 gold。

### 3.4 leakage 不能过度严苛

critical bridge leakage 是核心创新，但不能把所有关键概念都一律禁止。每个 case 应显示：

- `critical_bridge_boundary`
- `forbidden_content`
- `acceptable_reveal`
- `expected_student_next_action`

这样教练能判断“这次透露是否真的损害学习”，而不是机械判泄露。

### 3.5 Guard/Repair 还没有充分证明因果效果

如果不同 condition 生成的 candidate 不同，则 Guard/Repair 的效果可能混入 run-to-run variance。Repair 最好用 same-candidate before/after stress test 证明：

- 泄露是否下降。
- 教学质量是否下降。
- 是否变得空泛。
- 是否仍有下一步行动。

### 3.6 prompt tuning 风险

当前 dev 阶段可以修 prompt，但正式 50-case held-out 前必须冻结：

- enhanced prompt
- DBox-inspired prompt
- Bridge Contract prompt
- Guard prompt
- Repair prompt
- review rubric
- offline grader prompt

正式 held-out 之后不能再根据结果回头调 prompt，否则结论会被污染。

## 4. 接下来建议路线

### Step 1：先做 case/source review

先让教练或外部 AI 审核 `dialogue_state_v3_50_source_and_case_review.zh.xlsx`：

1. 先看“评审说明”。
2. 按桥梁桶 sheet 审核。
3. 只审核 case 本身，不评价 AI 回复。
4. 重点判断题源、题面、近期对话、学生问题、missing bridge、forbidden content 和 success criteria 是否可用。
5. 在结构化审核列中给出 `accept / revise / drop / discuss`，并在需要修改时填写 `issue_type` 和 `coach_fix_suggestion`。

通过后再进入生成 AI 回复。

### Step 2：冻结主实验条件

建议主实验不要继续扩大。候选主表控制在 6-8 个：

- `enhanced_prompt_only_clean`
- `dbox_inspired_clean`
- `dbox_inspired_guard`
- `bridge_guided_dbox_style_guard`（如果保留 hybrid）
- `bridge_contract_compact_clean`
- `bridge_contract_compact_guard`
- `bridge_contract_compact_guard_repair`
- 可选：`codehelp_codeaid_no_direct_solution` 或 `bridge_inspired_expert_decision`

Appendix 可放更多消融，不要让主表失控。

### Step 3：生成 50-case response review workbook

生成时必须保证每个 condition 都看到同一份输入：

- problem statement / public summary
- recent dialogue
- context AI reply（若有上一轮 assistant）
- current student message
- student code excerpt（若有）
- case-specific rubric fields

盲评表必须隐藏 condition 和 model。

### Step 4：人类教练盲评 + AI 预评

建议流程：

1. AI 预评只做 dev 筛查，不作为 gold。
2. 人类教练评中文版 workbook。
3. 至少 20% 样本做第二教练复标。
4. 对 major leakage、show=no、overall<=2、rank 第一/最后要求备注。

### Step 5：分析方式

正式分析不要把 50 × N 条回复当独立样本，要按 case 做 paired analysis：

- win/tie/loss
- paired bootstrap CI
- student-ready pass
- safe-ready pass
- major/answer leakage
- p50/p95 latency
- LLM calls
- static lint 只作为风险筛查，不作为人工 gold

### Step 6：如果结果不如 DBox-inspired

这不是论文失败。论文可以写成：

- DBox-inspired decomposition 是强 baseline。
- CP-MissingBridgeBench 让我们看见强 baseline 的质量/泄露/负担权衡。
- missing bridge 作为评测和 guard/routing 信号仍有价值。
- Bridge Contract 不一定是默认生成架构，可以退到高风险样本、离线诊断、或 reviewer-facing annotation schema。

## 5. 外部审核时请重点检查的问题

请其他 AI 或教练重点回答：

1. 当前论文是否应继续定位为 evaluation framework，而非系统最强架构论文？
2. DBox-inspired、CodeHelp/CodeAid-style、Bridge-inspired baseline 是否足以避免 weak-baseline bias？
3. dialogue-state v3 的 synthetic-but-grounded 50-case 构造是否可接受？
4. 近期对话、学生问题、题面、missing bridge 是否一致？
5. critical bridge leakage 是否过严？`acceptable_reveal` 是否足够解决这个问题？
6. 主实验 condition 是否仍然过多？哪些应该放主表，哪些放 appendix？
7. 如果 DBox-inspired 最终胜出，论文贡献是否仍然成立？
8. 洛谷真实题源的使用是否需要额外版权或引用说明？
9. 教练盲评表是否足够易懂？字段是否仍有冗余或冲突？
10. 目前还有哪些会导致审稿人质疑的实验设计漏洞？

## 6. 当前建议给其他 AI 看的文件

优先阅读：

- `docs/research/external_review_packet_20260515.zh.md`
- `docs/research/dialogue_state_v3_50_refresh_20260515.zh.md`
- `docs/research/dialogue_state_v3_50_context_readiness_audit_20260515.zh.md`
- `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- `docs/research/response_review_rubric_v3.zh.md`
- `docs/research/evaluation_protocol_v3.zh.md`
- `docs/research/baseline_protocol_v1.zh.md`
- `docs/research/dbox_reproduction_gap_v1.zh.md`

如果审核英文材料，可读对应 `.md` 英文版本和 `dialogue_state_v3_50_source_and_case_review.en.xlsx`。

## 7. 当前一句话总结

项目已经从“功能堆叠”收束为“算法竞赛 LLM 辅导评测框架”。现在最重要的不是继续加新模块，而是先把 50-case dialogue-state v3 数据集审干净，再冻结 prompt/rubric，之后跑强 baseline 对照和盲评。最终论文不应押注 Bridge Contract 一定获胜，而应押注 CP-MissingBridgeBench 能严谨揭示不同 tutoring harness 的质量、泄露、延迟和学生负担权衡。
