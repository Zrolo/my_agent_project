# Paper Results / Discussion Submission Compact: Dialogue-State v3 20260518

## 使用边界

本文档是投稿正文压缩版 Results / Discussion 草稿，不新增实验、不修改数据。它复用 dialogue-state v3 evidence package 中的 human review、priority60 adjudication、paired uncertainty、Repair same-candidate stress、DBox+Repair targeted fairness sensitivity 和 DeepSeek LLM grader calibration。

主结果口径固定为：

```text
main_scaffold_eval slice + priority60 adjudicated + Coach A
```

Coach A only、Coach B only、priority60 + Coach B、all-50 aggregate 和非主 slices 只作为 sensitivity / appendix。本文中所有 “trend” 都指在该 evidence package 边界内的人工评审趋势，不表示广泛显著优势。

## 4 Results

### 4.1 Human Review Reliability

Dialogue-state v3 包含 50 个 reviewed candidate cases、7 个匿名 tutoring harness conditions 和 350 条 AI 回复。Coach A 与 Coach B 都完成了 350 条全量盲评。两位教练在 `overall_quality` 上 exact agreement 为 0.2829，within-1 agreement 为 0.8429；leakage-label exact agreement 为 0.6714；critical-binary exact agreement 为 0.9029，但 kappa 为 0.2511。rank preference 分歧更明显，top-1 与 last-place agreement 均为 10/50。

我们对 60 条高优先级分歧进行 priority adjudication，其中 `use_A=29`、`use_B=9`、`new_label=22`。这说明单一教练标签不应被视为 gold，也说明 student-ready、safe-ready 和 rank 是 rater-sensitive outcomes。后续结果因此同时报告主口径、paired uncertainty、slice analysis 和 rater-view sensitivity。

### 4.2 Main Scaffold Evaluation

主结果只使用 31-case `main_scaffold_eval` slice。表 1 给出 `priority60 adjudicated + Coach A` 口径下的主指标。

| condition | overall | student-ready | safe-ready | major+answer leakage |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.032 | 7/31 | 7/31 | 9 |
| `codehelp_codeaid_clean` | 3.710 | 19/31 | 19/31 | 2 |
| `dbox_inspired_clean` | 3.774 | 21/31 | 21/31 | 2 |
| `dbox_inspired_guard` | 3.774 | 23/31 | 23/31 | 2 |
| `bridge_guided_dbox_style_guard` | 3.742 | 20/31 | 20/31 | 2 |
| `bridge_contract_compact_guard` | 4.000 | 23/31 | 23/31 | 0 |
| `bridge_contract_compact_guard_repair` | 4.065 | 22/31 | 22/31 | 0 |

`bridge_contract_compact_guard_repair` 在该主口径下 overall 最高，两个 Bridge Contract compact 条件的 major+answer leakage 均为 0。与此同时，`dbox_inspired_guard` 在 student-ready / safe-ready 上达到 23/31，接近或并列 Bridge Contract compact guard。因此结果应写成 quality-safety-burden trade-off：Bridge Contract compact + Guard/Repair 呈现有利的 overall 和 high-severity leakage-control trend，DBox-inspired decomposition 仍是强 baseline。

`codehelp_codeaid_clean` 相比 `enhanced_prompt_only_clean` 明显更稳，但仍有 2 条 major+answer leakage。这支持 critical bridge leakage 的核心动机：不直接给代码或完整题解，并不等于不会提前补完学生当前应自行推出的关键桥。

### 4.3 Pairwise Uncertainty

同题配对比较限制了可写的强度。`bridge_contract_compact_guard_repair` 相对 `dbox_inspired_guard` 的 mean overall delta 为 +0.290，W/T/L 为 14/10/7，major+answer leakage 少 2 条；但 paired bootstrap 95% CI 为 [-0.097, +0.645]，paired permutation p=0.2016。该比较支持 favorable trend / trade-off wording，不支持 significant dominance。

`bridge_contract_compact_guard_repair` 相对 `bridge_contract_compact_guard` 的 mean overall delta 为 +0.065，W/T/L 为 7/18/6，major+answer leakage 相同。因此主实验 condition 均值不能单独证明 Repair 的因果作用。

`codehelp_codeaid_clean` 相对 `enhanced_prompt_only_clean` 的 mean overall delta 为 +0.677，95% CI 为 [+0.258, +1.065]，paired p=0.0046，safe-ready 多 12 条，major+answer leakage 少 7 条。这说明 prompt-only 在 dialogue-state CP tutoring 中不够稳定，但 no-direct-solution 仍不是 safety-complete。

### 4.4 Slice And Sensitivity Analysis

50 cases 被分为 `main_scaffold_eval`、`main_eval_with_caution`、`clarification_safety_slice` 和 `policy_safety_slice`。all-50 aggregate 在 Coach A only、Coach B only、priority60+CoachA 和 priority60+CoachB 四种口径下都显示 `bridge_contract_compact_guard_repair` overall 最高，但该平均混合了不同用途的 slices，因此只作为 supplemental robustness。

Main scaffold slice 上 overall trend 相对一致；student-ready、safe-ready 和 rank 对 rater strictness 更敏感。论文不应只报告单一 rater view。

### 4.5 Observed Error Taxonomy

Observed error taxonomy 使用：

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

Level 1 包括 critical bridge leakage、answer/code leakage、over-complete micro-example、wrong/shifted focus、under-scaffolded、excessive burden、context misalignment、over-safe refusal、factual/algorithmic error 和 policy/direct-answer handling failure。Level 2 包括 representation semantics、transition/action mapping、predicate/decision semantics、ordering/dependency control、modeling relation、aggregation/contribution accounting、data-structure operation mapping、correctness/invariant reasoning、implementation boundary、debugging evidence 和 policy-request handling。DP state、binary-search check、lazy propagation、tree difference、local code、greedy proof 和 debugging trace 是 Level 3 surface anchors。

因此，taxonomy 不是具体算法场景列表。它是 observed operational taxonomy，不是 universal taxonomy。

### 4.6 Repair And DBox+Repair Sensitivity

Repair 的因果证据来自 30-pair same-candidate before/after stress test。Repair 使 leakage severity 改善 16/30、持平 14/30、变差 0/30；major leakage 从 7/30 降到 0/30；overall 均值从 3.367 提升到 3.633。代价是学生负担：burden improved / same / worse 为 2/16/12。

DBox+Repair targeted fairness add-on 覆盖 20 个 headline-sensitive cases，不是完整 50-case 双教练主实验。DBox+Repair overall 为 3.55，safe-ready 为 11/20，no/minor/major+answer leakage 为 14/6/0。相对同 case DBox Guard，overall 小幅提升 +0.15，major+answer leakage 从 2 降到 0；相对同 case Bridge Contract compact + Guard/Repair，Bridge+Repair 仍高 +0.50 overall，W/T/L 为 12/5/3，safe-ready 多 4 条。

这两项结果支持：Repair 能在固定 candidate 压力测试中降低 leakage，并且也能帮助 DBox-inspired baseline；但它伴随 burden trade-off，且 DBox+Repair add-on 只能作为 sensitivity evidence。

### 4.7 DeepSeek LLM Grader Calibration

LLM grader calibration 只评估 automatic grader 是否能作为 scalable auxiliary signal。Paper-facing calibration 使用 DeepSeek `deepseek-v4-flash` 且 thinking disabled。

在 priority60 reference 上，case-specific bridge-rubric judge 相比 generic rubric 改善了部分辅助指标：leakage-label accuracy 为 0.617 vs 0.583，student-ready agreement 为 0.467 vs 0.433，safe-ready agreement 为 0.533 vs 0.400。但 safety-critical 指标仍不可接受：generic 与 case-specific DeepSeek graders 的 critical recall 都是 0，major leakage false-negative rate 都是 1.000。

因此，LLM grader 不能替代 human review 或 adjudication。Kimi-backed calibration 只保留为 exploratory/tooling record，因为它使用不同 backend，并显示 backend sensitivity。

## 5 Discussion

### 5.1 What The Benchmark Shows

CP-MissingBridgeBench 的主要贡献不是证明某个 harness 绝对胜出，而是把 missing bridge 和 critical bridge leakage 变成可标注、可复核的 evaluation objects。当前 evidence package 显示：prompt-only 不够稳；no-direct-solution 不等于 no critical bridge leakage；DBox-inspired decomposition 是强 baseline；Bridge Contract compact + Guard/Repair 在主人工评审口径下呈现有利的 overall-quality 与 high-severity leakage-control trends。

### 5.2 Why Critical Bridge Leakage Matters

传统 “不要直接给答案/代码” 过于粗糙。Tutor 可以不写完整代码，也不说最终答案，却提前完成学生当前应自行跨过的中间推理桥。CP-MissingBridgeBench 通过 case-specific rubric 明确 success criteria、forbidden content、acceptable reveal 和 expected student next action，从而区分有帮助的脚手架与过早泄露。

### 5.3 Guard And Repair

Guard-only 条件在当前主实验中是 instrumentation / runtime signal。Leakage Judge 返回 `rewrite` 时不会改写 `final_response_text`；只有 `block` 会触发 fallback，而本轮主实验 block=0。因此 Guard-only 不能写成修复了最终输出。

Repair 可以写成有 same-candidate stress evidence 的 leakage-reduction intervention，但不能写成主实验 condition 均值已经单独证明其因果作用。它降低 leakage severity，同时常增加学生负担。

### 5.4 Limitations

本研究仍有明确限制。第一，50-case set 是 high-risk dialogue-state CP tutoring evidence candidate，不覆盖所有 CP tutoring 情景。第二，student-ready、safe-ready 和 rank 对评分者严格程度敏感。第三，priority60 adjudication 不是 gold；它只降低高优先级分歧的不确定性。第四，DBox+Repair 是 20-case targeted sensitivity，不是完整主实验条件。第五，DeepSeek-backed LLM grader 的 critical false-negative risk 很高，不能替代人审。

## Paper-Safe Takeaway

```text
CP-MissingBridgeBench reveals quality-safety-burden trade-offs in dialogue-state competitive-programming tutoring. DBox-inspired decomposition is a strong baseline. Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity critical-leakage-control trends under the primary human-review view, while student-ready, rank preference, Repair interpretation, DBox+Repair fairness, and LLM grader calibration require explicit sensitivity or stress-test reporting.
```
