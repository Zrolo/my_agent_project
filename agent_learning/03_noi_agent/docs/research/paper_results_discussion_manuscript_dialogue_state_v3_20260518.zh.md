# Paper Results And Discussion Manuscript Draft: Dialogue-State v3

## 使用边界

本文档是论文 Results / Discussion 的压缩正文草稿，不是新的实验报告。它复用既有人审、priority60 裁决、paired uncertainty、Repair same-candidate stress、DBox+Repair fairness add-on 和 DeepSeek-backed LLM grader calibration 结果。

论文主口径应是：

```text
main_scaffold_eval slice + priority60 adjudicated + Coach A labels
```

全 50-case 平均、Coach A/B 单独口径、priority60+CoachB、clarification / policy slices 只作为 sensitivity 或 appendix。

Evidence classes:

| Evidence item | Class | Paper role |
| --- | --- | --- |
| `main_scaffold_eval` + priority60 adjudicated + Coach A | main result | 论文 headline human-review result。 |
| Coach A only / Coach B only / priority60+CoachB | sensitivity analysis | rater strictness sensitivity。 |
| all-50 aggregate 与非主 slices | sensitivity / appendix | robustness 与 targeted safety discussion，不作为 headline。 |
| Pairwise W/T/L 与 paired uncertainty | main result support | 量化 headline comparison 的不确定性。 |
| Repair same-candidate before/after review | stress test | 固定 candidate 下的 Repair 因果证据。 |
| DBox+Repair 20-case add-on | sensitivity analysis | fairness add-on check，不是 main condition。 |
| DeepSeek LLM grader calibration | calibration | auxiliary-grader assessment，不替代 human review。 |

## Results

### Human Review Reliability

Dialogue-state v3 包含 50 个 reviewed candidate cases、7 个匿名 tutoring harness condition 和 350 条 AI 回复。Coach A 与 Coach B 都完成了 350 条全量盲评。两位教练在 overall 上 exact agreement 较低（0.2829），但 within-1 agreement 较高（0.8429）；leakage label exact agreement 为 0.6714；critical binary exact agreement 为 0.9029，但 kappa 只有 0.2511。rank agreement 较弱，top-1 与 last-place agreement 均为 10/50，并产生 244 条 flagged disagreement rows。

我们对 60 条高优先级分歧进行 priority adjudication，其中 `use_A=29`、`use_B=9`、`new_label=22`。这说明任一教练都不能被视为 gold，也说明 pedagogical judgment 本身具有 rater sensitivity。因此本文不报告单一分数表，而是报告 double review、priority adjudication、slice analysis 和 sensitivity analysis。

### Main Scaffold Evaluation

主结果聚焦 `main_scaffold_eval` 31 cases，而不是把 clarification / policy safety cases 混入 headline。在 `priority60 adjudicated + Coach A` 主口径下，`bridge_contract_compact_guard_repair` 的 overall 最高（4.065），`bridge_contract_compact_guard` 为 4.000，`dbox_inspired_guard` 和 `dbox_inspired_clean` 均为 3.774。`bridge_contract_compact_guard` 与 `bridge_contract_compact_guard_repair` 的 major+answer leakage 均为 0；`dbox_inspired_guard` 仍有 2 条 major+answer leakage，但 student-ready / safe-ready 为 23/31，与 `bridge_contract_compact_guard` 并列或接近。

这支持两个结论。第一，DBox-inspired decomposition 是强 baseline，不能被写成弱对照。第二，Bridge Contract compact + Guard/Repair 在 overall quality 与 high-severity leakage control 上呈现更稳的 trade-off，但不能写成全面显著胜出。

`enhanced_prompt_only_clean` 在 main scaffold slice 上 overall 为 3.032，major+answer leakage 为 9；`codehelp_codeaid_clean` overall 提升到 3.710，major+answer leakage 降为 2。这个对比说明：no-direct-code / no-direct-solution policy 比 prompt-only 更稳，但“不直接给代码/题解”并不等于不会发生 critical bridge leakage。

### Pairwise Uncertainty

同题配对比较要求我们避免只看均值排名。`bridge_contract_compact_guard_repair` 相对 `dbox_inspired_guard` 的 mean overall delta 为 +0.290，W/T/L 为 14/10/7，major+answer leakage 少 2 条；但 paired bootstrap 95% CI 为 [-0.097, +0.645]，paired permutation p=0.2016。因此论文只能写 trend 或 trade-off advantage，不能写 statistically significant dominance。

`bridge_contract_compact_guard_repair` 相对 `bridge_contract_compact_guard` 的 mean overall delta 只有 +0.065，W/T/L 为 7/18/6，major+answer leakage 相同。主实验 condition 均值本身不能证明 Repair 的因果作用。相反，它提示 Repair 需要 same-candidate before/after stress test 才能讨论因果效果。

`codehelp_codeaid_clean` 相对 `enhanced_prompt_only_clean` 的 mean overall delta 为 +0.677，95% CI 为 [+0.258, +1.065]，paired p=0.0046，safe-ready 多 12 条，major+answer leakage 少 7 条。该结果支持 prompt-only 在 dialogue-state CP tutoring 中不够稳定，但仍不能把 no-direct-solution baseline 写成 safety-complete。

### Slice And Sensitivity Analysis

50 cases 被分为 `main_scaffold_eval`（31 cases）、`main_eval_with_caution`（5 cases）、`clarification_safety_slice`（10 cases）和 `policy_safety_slice`（4 cases）。论文 headline 应来自 `main_scaffold_eval`；其他 slices 应用于 appendix 或特定错误类型讨论。

四种评分口径包括 Coach A only、Coach B only、priority60 adjudicated + Coach A 和 priority60 adjudicated + Coach B。全 50-case sensitivity 中，`bridge_contract_compact_guard_repair` 在四种口径下 overall 都最高，但 all-case 平均混入 clarification 和 policy slices，因此只能作为 supplemental robustness。main scaffold slice 上 overall 趋势相对稳定，但 student-ready、safe-ready 和 rank 对 rater strictness 敏感，不能只报单一 rater view。

### Observed Error Taxonomy

本文 taxonomy 不应写成只覆盖 DP state、binary-search check、lazy propagation、tree difference 或 local code。修订后的 reviewer-facing taxonomy 是：

```text
general tutoring failure type × operational cognitive bridge family × surface anchor
```

Level 1 是 general tutoring failure type，例如 critical bridge leakage、answer/code leakage、over-complete micro-example、wrong/shifted focus、under-scaffolded、excessive burden、context misalignment、over-safe refusal、factual/algorithmic error 和 policy/direct-answer handling failure。Level 2 是 operational cognitive bridge family，例如 representation semantics、transition/action mapping、predicate/decision semantics、ordering/dependency control、modeling relation、aggregation/contribution accounting、data-structure operation mapping、correctness/invariant reasoning、implementation boundary、debugging evidence 和 policy-request handling。Level 3 才是 surface anchor，例如 DP state、binary-search check、lazy propagation、tree difference、local code、greedy proof 或 debugging trace。

因此论文应描述为 observed taxonomy，而不是 universal taxonomy。当前 50-case set 覆盖了多个 cognitive bridge families，但仍欠采样 geometry predicates、counting / inclusion-exclusion、modular invariants、search pruning / deduplication 和更丰富的 multi-turn debugging diagnosis。

### Repair Same-Candidate Stress Test

主实验只显示 repair-enabled condition 表现较好，不能单独证明 Repair 对同一 candidate 有因果提升。为此我们补充了 30-pair same-candidate before/after stress test，固定 original candidate 与 repair output，并盲化为 Response A / Response B。

结果显示，Repair 使 leakage severity 改善 16/30、持平 14/30、变差 0/30；major leakage 从 7/30 降到 0/30；overall 均值从 3.367 提升到 3.633，mean delta 为 +0.267；quality W/T/L 为 12/11/7；repair preferred / original preferred / tie 为 15/11/4。代价是 student burden：burden improved / same / worse 为 2/16/12。

因此可写成：Repair 在 same-candidate stress setting 下能降低 leakage severity，尤其能消除本样本中的 major leakage，但常以更高学生负担为代价。不能写成 Repair 已完全解决泄露。

### DBox+Repair Fairness Add-On

为了回应 “Bridge 有 Repair，而 DBox-inspired baseline 没有同等 Repair 机会” 的公平性风险，我们对已有 `dbox_inspired_guard_repair` 生成包做了 20-case headline-sensitive 补评。该集合是 targeted sensitivity set，不是随机抽样，也不是完整 50-case 双教练人审。

DBox+Repair add-on 的 overall 为 3.55，safe-ready 为 11/20，no/minor/major+answer leakage 为 14/6/0。与同一 20 cases 的主实验 DBox Guard（priority60 + Coach A）相比，DBox+Repair overall 小幅提高（+0.15，W/T/L=6/9/5），major+answer leakage 从 2 降到 0。与 Bridge Contract compact + Guard/Repair 相比，Bridge+Repair 在同一 20 cases 上仍有 +0.50 overall，W/T/L=12/5/3，safe-ready +4。

这个结果应写成 fairness sensitivity evidence。它缓解了 DBox 没有 Repair 的公平性担忧，并显示 Repair 也能帮助 literature-inspired baseline 降低高风险泄露；但它不能替代主实验，也不能证明 Bridge 对所有 repair-enabled baselines 有确定优势。

### LLM Grader Calibration

LLM grader calibration 只用于检验 automatic grader 能否作为 scalable auxiliary signal，不能替代 human review。本轮 paper-facing calibration 使用 DeepSeek offline judge profile，与主实验 judge stack 对齐：

```text
backend = deepseek
model = deepseek-v4-flash
thinking = disabled
```

DeepSeek-backed priority60 run 完成 180/180 tasks。case-specific bridge-rubric judge 相比 generic rubric 改善了部分辅助指标：leakage-label accuracy 为 0.617 vs 0.583，student-ready agreement 为 0.467 vs 0.433，safe-ready agreement 为 0.533 vs 0.400。但在 safety-critical 指标上，generic 与 case-specific DeepSeek grader 的 critical recall 都是 0，major leakage false-negative rate 都是 1.000。也就是说，DeepSeek automatic grader 没有恢复人类裁决为 `major_bridge_leakage` / `answer_leakage` 的 priority60 rows。

因此论文应写：case-specific bridge rubrics improve some auxiliary grading signals, but DeepSeek-backed LLM graders remain unreliable for high-stakes critical-bridge leakage evaluation. Earlier Kimi-backed results are retained only as exploratory/tooling evidence because they use a different backend and show backend sensitivity.

## Discussion

### What CP-MissingBridgeBench Shows

CP-MissingBridgeBench 的主要贡献不是证明某个 tutor harness 绝对胜利，而是让 missing bridge 与 critical bridge leakage 变成可讨论、可标注、可复核的 evaluation object。它揭示了 LLM tutoring harness 之间的 quality-safety-burden trade-off：prompt-only 不够稳，no-direct-solution 不等于 no leakage，DBox-inspired decomposition 是强 baseline，Bridge Contract compact + Guard/Repair 在 overall 与 high-severity leakage control 上呈现稳定但非绝对的优势。

### Why Critical Bridge Leakage Matters

传统 “不要直接给答案/代码” 不足以定义安全教学。AI 可以不写完整代码，也不说最终答案，却提前说穿学生应该自己跨过的关键中间推理。CP-MissingBridgeBench 将这种风险定义为 critical bridge leakage，并通过 case-specific rubric 规定 success criteria、forbidden content、acceptable reveal 和 expected student next action。这使评测能够区分 “有帮助的脚手架” 与 “提前完成学生关键推理”。

### Guard And Repair Interpretation

Guard-only 条件在当前主实验中主要是 instrumentation / runtime signal；除非触发 block fallback，否则不会改写最终学生可见回复。因此 guard-only 结果不能解释为 Guard 已修复输出。

Repair 的因果作用不能只由主实验 condition 均值证明。same-candidate stress test 提供了更直接的 before/after evidence：Repair 能降低 leakage severity，但可能增加学生负担。论文应把 Repair 写成 promising but trade-off-bearing intervention，而不是 fully solved safety mechanism。

### Limitations

本研究仍有五类限制。第一，50-case set 是 high-risk CP tutoring evidence candidate，不覆盖所有 CP tutoring 场景。第二，student-ready、safe-ready 和 rank 对 rater strictness 敏感，因此结果必须报告 sensitivity，而不是只报单一分数。第三，priority60 adjudication 不是 final gold；它降低了高优先级分歧的不确定性，但没有消除所有 rater variance。第四，DBox+Repair fairness add-on 是 20-case targeted sensitivity，不是完整 50-case 双教练补评。第五，DeepSeek-backed LLM grader calibration 显示 automatic grader 的 critical false-negative 风险很高，不能替代 human review。

## Paper-Safe Claim

最稳的论文主张是：

```text
CP-MissingBridgeBench reveals quality-safety-burden trade-offs in dialogue-state competitive-programming tutoring. DBox-inspired decomposition is a strong baseline. Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity critical-leakage-control trends under the primary human-review view, but student-ready, rank preference, and automatic grader agreement remain rater- and backend-sensitive. Guard-only is instrumentation in the current pipeline, and Repair requires same-candidate evidence to support causal claims.
```
