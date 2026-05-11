# Research v1 外部审查方案（2026-05-11）

这份文档用于给其他 AI 或研究合作者审查当前 GitHub 分支。请注意：当前分支的目标不是把完整多 Judge 链路直接上线，而是先形成一个可标注、可评测、可消融的算法竞赛 AI 辅导研究框架。

## 仓库与分支

- Repository: `Zrolo/my_agent_project`
- Branch: `codex/bridge-research-annotation`
- Main workspace: `agent_learning/03_noi_agent`
- Research entry: `docs/research/index.md`

## 当前项目定位

论文方向建议固定为：

```text
CP-MissingBridgeBench:
Turn-level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation
for LLM Tutors in Competitive Programming
```

中文表述：

```text
CP-MissingBridgeBench：
面向算法竞赛 LLM 辅导的逐轮缺失桥梁诊断与关键桥梁泄露评测框架
```

当前线上 AIChat 仍然主要是：

```text
rules
+ legacy learning phase judge
+ Pedagogical Judge v2 soft control
+ main LLM
+ self-reported level hard gate
+ output guards
```

当前 Research v1 工具链已经包含：

```text
Bridge Judge
Bridge Contract Tutor
Leakage Judge
Repair
risk routing policy
coach seed annotation
response blind review
latency/error metrics
repair before/after review dataset
agent eval methodology docs
```

因此，论文里不应声称当前线上系统已经完整实现 Bridge-aware Tutor。更严谨的说法是：当前线上 AIChat 是 baseline，Research v1 是离线评测与消融框架。

## 研究创新点

建议把创新收束为五点：

1. **CP-specific missing bridge schema**
   将算法竞赛学生卡点从算法标签细化为“当前缺失的推理桥”。

2. **Critical bridge leakage**
   定义关键桥梁泄露，区分“完整代码/答案泄露”和“直接补完当前关键中间推理”的泄露。

3. **Coach reference workflow**
   通过教练 turn-level 标注、盲评、双标和裁决，建立 expert reference，而不是把单一 gold label 视为绝对真理。

4. **Compact Bridge Contract**
   将细粒度人类标注蒸馏为运行时可用的小型 contract，包括 missing bridge、help level、help forms、must-not-reveal 和 next student action。

5. **Risk-triggered evaluation/control harness**
   比较 current system、single LLM structured、bridge contract、guard、repair 和 risk-triggered routing 在质量、泄露与延迟之间的权衡。

## Agent Eval 方法论

参考 Anthropic Engineering 的《Demystifying evals for AI agents》，Research v1 将 AIChat 视为 agent-like tutoring harness，而不是单句回复模型。

我们采用以下映射：

| Agent Eval 概念 | 本项目对应物 |
|---|---|
| Task | 一个学生 turn + 题目上下文 + 近期对话 + 成功标准 |
| Trial | 某个系统版本在一个 task 上的一次运行 |
| Transcript / trace | Bridge Judge、Tutor candidate、Leakage Judge、Repair、final response、latency、LLM call count |
| Outcome | 学生最终看到的回复及其教学质量、泄露情况 |
| Grader | deterministic checks、LLM Judge、coach reference |
| Eval harness | offline runner、response review workbook、summary scripts |
| Agent harness | rules、Bridge Contract、Tutor、Guard、Repair |

重要原则：

- 能用 deterministic grader 判断的，不交给 LLM Judge。
- LLM Judge 只评开放式语义维度，例如 missing bridge、leakage、scaffold appropriateness。
- Coach label 是 expert reference，不是唯一绝对真值。
- Capability eval 和 regression eval 必须分开。
- 学生端更应关注稳定性指标 `pass^k`，而不只是 `pass@k`。

详见：

- `docs/research/agent_eval_methodology_v1.zh.md`
- `docs/research/agent_eval_methodology_v1.md`

## 当前已有关键实验与发现

### 1. 20-case mini-study

已有 20 条 seed 的多 baseline 初步实验与盲评分析。核心发现：

- `current_system` 是重要 baseline，但关键桥梁泄露较多。
- `single_llm_structured` 表现强，必须作为正式 baseline。
- `bridge_contract` 对 bridge-oriented micro-example 有正向信号。
- `guard + repair` 需要更严格的 stress test，不能只凭自然触发样本判断。

相关文档：

- `docs/research/mini_study_20_report_20260510.zh.md`
- `docs/research/coach_response_review_analysis_mini_study_20_20260510.zh.md`

### 2. Hard-gate fallback 修复

盲评发现部分差回复不是架构问题，而是 hard gate / fallback 误降级导致系统泛泛要求题号或代码行，未回应学生核心问题。

相关文档：

- `docs/research/hard_gate_overfallback_rerun_20260510.zh.md`

### 3. Repair prompt 修复与前后对照

已有 Repair prompt 修复后的 20-case rerun，以及 4 个触发 repair 的 before/after 盲评数据集。网页端默认批次现在是：

```text
Repair 前后对照 20260510
```

相关文件：

- `docs/research/coach_response_review_workbook_repair_before_after_20260510.csv`
- `docs/research/coach_response_review_workbook_repair_before_after_20260510.zh.xlsx`
- `evals/aichat/summarize_repair_before_after_review.py`
- `docs/research/repair_before_after_review_analysis_20260510.zh.md`

## 当前最重要的方法论问题

### Prompt effect vs architecture effect

如果 prompt 修正后效果变好，不能直接说明架构有效，也不能直接说明架构无效。它说明之前结果至少部分受 prompt 限制。

后续必须采用：

```text
dev set 调 prompt
prompt patch log 记录改动
freeze prompt version
held-out test set 比较架构
同时报告质量、泄露和延迟
```

论文应避免：

```text
多层 LLM 天然更好。
```

更严谨的论文主张是：

```text
我们评估 explicit bridge contract、leakage guard 和 repair loop
是否能在 prompt-tuned single LLM baseline 之外，
提供额外的稳定性、泄露控制和可解释控制信号。
```

## 下一步计划

### Phase 1: 完成 Repair before/after 盲评

1. 在网页端评完 8 条 Repair 前后对照。
2. 导出评分 CSV。
3. 使用 `evals/aichat/summarize_repair_before_after_review.py` 生成中英文报告。
4. 判断 Repair 是否真正提升质量、降低泄露，还是只是变得更保守。

### Phase 2: 冻结 prompt_v1.0-dev

冻结：

- Bridge Judge prompt；
- Tutor prompt；
- Leakage Judge prompt；
- Repair prompt；
- bridge-oriented micro-example policy；
- fallback policy。

之后所有 prompt 改动进入：

```text
docs/research/prompt_patch_log.md
```

### Phase 3: dev / regression / test 分离

- dev set：允许调 prompt；
- regression set：每次改 prompt 都跑，防止旧失败复现；
- test set：冻结后才跑，用于论文结果。

### Phase 4: 扩展到 50 条 seed

覆盖：

- DP / state / transition；
- binary search / check / boundary；
- graph / tree / modeling；
- greedy / correctness；
- data structure；
- implementation / boundary / type；
- debugging；
- direct answer / type confirmation / local completion。

### Phase 5: 双教练标注与裁决

- Coach A 标全部 50 条；
- Coach B 独立标 15 条以上；
- 计算 agreement；
- 分歧裁决；
- 输出 adjudicated reference。

### Phase 6: pass^3 稳定性评测

同一 task 对同一系统跑 3 次，评估：

- `pass^3_no_critical_leakage`
- `pass^3_scaffold_appropriate`
- `pass^3_valid_contract`

学生端比 `pass@k` 更需要 `pass^k`。

## 希望外部 AI 重点审查的问题

请审查者重点回答：

1. 当前论文主线是否过宽？是否应该进一步收束？
2. `missing bridge` 与已有教育/AI tutor 工作相比，差异是否足够清楚？
3. `critical bridge leakage` 是否是有价值的新评测维度？
4. single-LLM structured baseline 是否设计公平？
5. 当前 coach reference workflow 是否足够严谨，是否需要更多双标？
6. 当前 response blind review rubric 是否足够支持论文结论？
7. Repair before/after 对照是否能证明 Repair 的实际价值，还是需要更强 stress set？
8. 如何更清楚地区分 prompt 改进收益与架构收益？
9. 风险触发式 routing 是否能作为论文中的系统贡献？
10. 哪些当前文档或代码仍然混淆了“已实现线上系统”和“离线研究框架”？

## 不希望外部 AI 做的事

请不要直接建议：

- 立刻把完整多 Judge 接入线上学生 AIChat；
- 每轮自动修改 system prompt；
- 把单教练标签称为绝对 gold truth；
- 把控制论作为主创新；
- 继续无限扩展算法 ontology；
- 只凭单个 case 修改全局 prompt。

Research v1 当前最重要的是：可标注、可评测、可消融、可复现。
