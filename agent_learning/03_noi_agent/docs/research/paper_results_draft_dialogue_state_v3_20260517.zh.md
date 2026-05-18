# Paper Results Draft: Dialogue-State v3 20260517

## 1. Human Review Reliability

Dialogue-state v3 包含 50 个 reviewed candidate cases、7 个匿名 condition 和 350 条 AI 回复。Coach A 与 Coach B 都完成了 350 条全量盲评。A/B agreement 显示：`overall exact=0.2829`，但 `overall within 1=0.8429`；`leakage exact=0.6714`；`critical binary exact=0.9029`，但 `critical binary kappa=0.2511`；rank agreement 较低，top-1 / last-place agreement 均为 10/50，并有 244 条 flagged disagreement rows。

我们对 60 条高优先级分歧进行裁决，其中 `use_A=29`、`use_B=9`、`new_label=22`。这说明不能把任一教练视为 gold。论文应写成：pedagogical judgment is rater-sensitive；因此本文报告 double review、priority adjudication、slice analysis 和 sensitivity analysis。

## 2. Main Scaffold Evaluation

主论文 headline 应聚焦 `main_scaffold_eval` slice（31 cases），不把 clarification / policy safety cases 混成一个总分。在 `priority60 adjudicated + Coach A` 主口径下：

- `bridge_contract_compact_guard_repair` overall 最高：4.065；
- `bridge_contract_compact_guard` 与 `bridge_contract_compact_guard_repair` 的 major+answer leakage 都为 0；
- `dbox_inspired_guard` 的 student-ready / safe-ready 为 23，与 `bridge_contract_compact_guard` 并列或接近，说明 DBox-inspired decomposition 是强 baseline；
- `enhanced_prompt_only_clean` overall 较低且 major+answer leakage 较高，说明 strong prompt-only 在 dialogue-state CP tutoring 中不够稳定；
- `codehelp_codeaid_clean` 明显优于 enhanced prompt-only，但仍有 critical bridge leakage，说明 no-direct-solution 不等于 no critical bridge leakage。

## 3. Pairwise Uncertainty

同题配对比较显示，`bridge_contract_compact_guard_repair` 相对 `dbox_inspired_guard` 的 `Δ overall=+0.290`，W/T/L=14/10/7，major+answer leakage 少 2 条，但 bootstrap CI `[-0.097, +0.645]` 跨 0，paired p=0.2016。因此只能写 trend / trade-off advantage，不能写 significant dominance。

`bridge_contract_compact_guard_repair` 相对 `bridge_contract_compact_guard` 的 `Δ overall=+0.065`，W/T/L=7/18/6，major+answer leakage 相同。这说明主实验不支持 Repair 因果结论。

`codehelp_codeaid_clean` 相对 `enhanced_prompt_only_clean` 的 `Δ overall=+0.677`，CI `[+0.258, +1.065]`，提示 no-direct-solution baseline 比 prompt-only 更稳，但仍不是 critical leakage 的充分防线。

## 4. Sensitivity Analysis

四种评分口径包括 Coach A only、Coach B only、priority60 adjudicated + Coach A、priority60 adjudicated + Coach B。全 50-case sensitivity 中，`bridge_contract_compact_guard_repair` 在四种口径下 overall 都最高。但 all-case 平均混合了 clarification 和 policy slices，因此只作为 supplement。

在 `main_scaffold_eval` 中，overall 趋势较稳，但 student-ready / rank 对 rater strictness 敏感。Coach B 更严格，压缩了 ready 与 overall 差距；因此论文不能只给单一表格。

## 5. Slice Analysis

50 cases 分为：

| slice | case_n | paper use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | 主脚手架质量比较 |
| `main_eval_with_caution` | 5 | sensitivity / appendix |
| `clarification_safety_slice` | 10 | 澄清、不脑补、安全询问分析 |
| `policy_safety_slice` | 4 | 直接要答案/代码时的安全重定向分析 |

论文应按 slice 报告，不把所有 case 合成一个 headline。

## 6. Observed Error Taxonomy

Observed error taxonomy 使用三层结构：

```text
general tutoring failure type × operational cognitive bridge family × surface anchor
```

错误类型包括 critical bridge leakage、answer/code leakage、over-complete micro-example、wrong/shifted focus、under-scaffolded、excessive burden、context misalignment、over-safe refusal、factual/algorithmic error 和 policy handling failure。当前 observed errors 覆盖 representation semantics、transition/action mapping、predicate/decision semantics、ordering/dependency、modeling relation、aggregation/contribution、data-structure operation、correctness/invariant、implementation、debugging evidence 和 policy-request handling。DP state、binary-search check、lazy propagation、tree difference、local code 等是 surface anchors，不是 taxonomy 本体。

## 7. Repair Same-Candidate Stress Test Result

主实验只能说明 repair-enabled condition 表现较好，不能说明 Repair 对同一 candidate 有因果提升。我们补充了 30-pair same-candidate before/after stress test，固定 original candidate 与 repair output，盲化展示为 Response A / Response B。

结果显示：Repair 使 leakage severity 改善 16/30、持平 14/30、变差 0/30；major leakage 从 7/30 降为 0/30；overall 均值从 3.367 提升到 3.633，mean delta 为 +0.267；quality win/tie/loss 为 12/11/7；repair preferred/original preferred/tie 为 15/11/4。但 burden improved/same/worse 为 2/16/12，说明 Repair 的 leakage benefit 伴随学生负担变重的 trade-off。论文应写成 stress-test evidence，而不是把主实验均值解释为唯一因果证明。

## 8. DBox+Repair Fairness Add-On

为回应 “Bridge 有 Repair，而 DBox-inspired baseline 没有同等 Repair 机会” 的公平性风险，我们对已有 `dbox_inspired_guard_repair` 生成包做了 20-case headline-sensitive 补评。该集合是 targeted sensitivity set，不是随机抽样，也不是完整 50-case 双教练人审。

补评结果显示：DBox+Repair add-on 的 overall 为 3.55，safe-ready 为 11/20，no/minor/major+answer leakage 为 14/6/0，burden low/medium/high 为 8/9/3。与同一 20 cases 的主实验 DBox Guard（priority60 + Coach A）相比，DBox+Repair 的 overall 小幅提高（+0.15，W/T/L=6/9/5），major+answer leakage 从 2 降到 0；但它没有推翻 Bridge Contract compact + Guard/Repair 在同一 20 cases 上的趋势（Bridge+Repair 相对 DBox+Repair：+0.50，W/T/L=12/5/3，safe-ready +4）。

论文应把该结果写成 fairness sensitivity evidence：DBox+Repair 缓解了 “DBox 没有 Repair” 的公平性担忧，并显示 Repair 也能帮助 literature-inspired baseline 降低高风险泄露；但它不能替代主实验，也不能证明 Bridge 对所有 repair-enabled baselines 有确定优势。

## 9. LLM Grader Calibration Result

LLM grader 只作为 scalable auxiliary grader。我们比较 `likert_only_judge`、`generic_rubric_judge` 和 `case_specific_bridge_rubric_judge`，以 priority60 adjudicated labels 和 adj+CoachA/B sample20 为 reference，报告 overall agreement/correlation、leakage accuracy、critical binary precision/recall/F1、major leakage false negative rate、student-ready agreement、safe-ready agreement 和 unknown rate。

DeepSeek-backed priority60 adjudicated 主口径已完成 180/180 tasks。case-specific bridge-rubric judge 的 leakage accuracy 为 0.617，高于 generic rubric 的 0.583；ready agreement 为 0.467，高于 generic 的 0.433；safe-ready agreement 为 0.533，高于 generic 的 0.400。但 safety-critical 指标很弱：generic 和 case-specific DeepSeek grader 的 critical recall 都是 0，major leakage false-negative rate 都是 1.000。因此它不能替代人审。

DeepSeek-backed adj+CoachA sample20 与 adj+CoachB sample20 均已完成 60/60 tasks。两个 sample20 reference views 没有 human critical-positive rows，因此只用于 rater-view sensitivity 下的 overall、ready / safe-ready 和 non-critical leakage-label agreement，不用于 critical recall 结论。此前 Kimi-backed calibration 只保留为 exploratory/tooling record，因为它不符合主实验固定 DeepSeek judge stack。

## 10. What We Can And Cannot Claim

可以写：

- CP-MissingBridgeBench 能区分不同 tutoring harness 的 quality-safety-burden trade-off；
- DBox-inspired decomposition 是强 baseline；
- Bridge Contract compact + Guard/Repair 在主人工评审口径下呈现较有利的 overall 与 critical-leakage-control trend；
- student-ready 对评分者口径敏感；
- no-direct-code 不等于 no critical bridge leakage；
- prompt-only 在 dialogue-state CP tutoring 中不够稳定；
- concrete algorithm patterns 是 surface anchors，不是 taxonomy 本体。
- DBox+Repair 20-case targeted add-on 缓解了 fairness-add-on 风险，但仍只是 sensitivity evidence。
- case-specific bridge-rubric judge 在 DeepSeek 上改善部分 auxiliary grading signal，但 priority60 critical false-negative 风险仍高，不能替代人类教练或裁决。

不能写：

- Bridge Contract 全面显著优于所有 baseline；
- Guard-only 修复了最终输出；
- Repair 已完全解决泄露；
- Coach A / Coach B 是 gold；
- priority60 是 final gold；
- 50-case set 覆盖所有 CP tutoring 情景。
- DBox+Repair 已完成 full 50-case 双教练验证。
- LLM grader labels 可以替代 human review 或成为 gold。

## 11. Limitations

当前结果仍有五类限制：第一，50-case set 是 high-risk CP tutoring cognitive bridge families 的 evidence candidate，不覆盖所有 CP tutoring 情景；第二，student-ready / rank 对教练严格程度敏感；第三，Guard-only 在当前链路主要是 instrumentation，不是 rewrite；第四，Repair 因果解释已有 same-candidate stress 与 DBox+Repair targeted sensitivity 支撑，但 DBox+Repair 仍不是 full 50-case 双教练补评；第五，LLM grader calibration 显示 case-specific rubric 有帮助，但 DeepSeek-backed priority60 critical false negative 仍很高，automatic grader 不能替代人审。
