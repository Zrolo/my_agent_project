# Response Evaluation Protocol v3

本协议规定 Research v1 后续 dev ablation、50-case held-out 和 coach blind review 的 v3 全流程。它替代 v2 中“多项评分并列展示”的做法，把结果分成主指标、诊断指标和可靠性字段。

## 核心原则

1. 先定义 case-specific rubric，再评分回复。
2. 主表只展示少数主指标，避免指标堆叠。
3. 诊断指标用于解释错误，不直接当作唯一胜负依据。
4. micro-example 先判适用性，不适用时不扣分。
5. AI 预评只能用于 dev 筛查，不是 coach gold。
6. LLM Judge 只能做 calibrated grader，不能被当作最终真值。

## 教练评分流程

1. 看原题链接、必要题面和题目上下文。
2. 看 case-specific rubric：
   - `success_criteria`
   - `forbidden_content`
   - `critical_bridge_boundary`
   - `acceptable_reveal`
   - `expected_student_next_action`
3. 看近期对话与上下文 AI 回复，用来理解当前学生话语。
4. 看学生当前问题，这是本轮必须回应的核心。
5. 只评价“AI 回复（要评分）”。
6. 先填主指标：
   - 总体质量
   - 是否愿意给学生看
   - 泄露标签
   - 关键桥透露是否有教学理由
   - 帮助是否足够
   - 学生回复负担
7. 再填诊断指标。
8. 对强制备注样本写一句原因。

## 强制备注

以下情况必须写备注：

- `critical_leakage_label` 是 `major_bridge_leakage` 或 `answer_leakage`
- `would_show_to_student=no`
- `overall_quality<=2`
- 同题排序第一或最后
- `reviewer_confidence=low`
- `needs_discussion=yes`

## 分析输出

分析脚本输出四类结果。

### 主表

- overall
- student-ready pass
- safe-ready pass
- major/answer leakage
- scaffold sufficiency
- burden distribution
- dev-only `rubric_eval_score_v1`

### 诊断表

- bridge identification
- groundedness
- scaffold appropriateness
- next-step clarity
- single-focus coherence
- bridge-oriented micro-example

### 配对比较

同一 case 下不同 condition 的 paired comparison，包括：

- DBox clean vs Bridge Contract clean
- DBox guard vs Bridge-guided DBox guard
- Guard vs no Guard
- Repair vs no Repair

### Case memo

自动列出 major/answer leakage 样本，供人工归类：

- direct bridge completion：直接替学生补完当前认知桥；
- answer-slot compression：把当前关键桥压缩成填空、选择、true/false 后续动作或位置/方向问题；
- worked-trace completion：用完整 micro-example 或局部 trace 把关键关系演完；
- local implementation completion：补完关键局部实现、局部条件、更新语句或代码诊断；
- proof / invariant completion：替学生完成正确性、不变量、交换或支配关系证明；
- decision-rule completion：直接给出应保留哪边、走哪个分支、跳过哪个候选或采用哪个操作；
- debugging diagnosis completion：直接指出 bug 根因和修法，而不是引导收集最小证据；
- modeling-plan completion：一次性给出对象、关系、约束或结构映射方案；
- over-constrained scaffold：虽用问题形式，但把思考空间压到只剩当前关键桥；
- 上下文错配
- rubric 边界不清

`state_representation_semantics`、`predicate_check_semantics` 等 bridge bucket 是 Research v1 的 operational cognitive bridge families。DP state、binary-search check、lazy propagation、tree difference、local code 等才是 surface anchors，用来说明这些认知桥和泄露机制在具体算法语境中的实例。

## 与 Rubrics as Rewards 的关系

本项目只借鉴 rubric-based open-ended evaluation 的思想：开放式回复需要多维、样本特定的评价标准。我们不做 RL 训练，也不把 rubric 分数当作 reward。

在论文中应写成：

```text
We use case-specific rubrics for open-ended tutor-response evaluation, but do not perform rubric-reward RL training.
```

## 结果解释

- 如果 strong baseline 胜出，不说明论文失败；说明 CP-MissingBridgeBench 能揭示真实 trade-off。
- 如果某条件质量高但泄露也高，不能只按 overall 排名。
- 如果某条件无泄露但 sufficiency 低，也不能视为好 tutor。
- dev/regression 结果可以指导 prompt 修订；held-out 结果才进入 headline claim。
