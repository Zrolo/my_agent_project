# Dialogue-State v3 Result Claims Lock 20260517

## 目的

本文件锁定 dialogue-state v3 50-case human review 当前能写和不能写的论文结论。当前结果是 formal human-review evidence candidate，不是 final gold。所有结论都必须按 slice、rater sensitivity 和 paired uncertainty 报告。

## 可以写的结论

1. CP-MissingBridgeBench 能揭示不同 LLM tutoring harness 的 quality-safety-burden trade-off。
2. DBox-inspired decomposition 是强 baseline，不能被写成弱对照。
3. Bridge Contract compact + Guard/Repair 在主人工评审口径下呈现较有利的 overall-quality 和 critical-leakage-control trend。
4. no-direct-code / no-direct-solution baseline 仍可能出现 critical bridge leakage；不直接给完整代码或题解，不等于没有提前补完关键认知桥。
5. student-ready、safe-ready 和 rank preference 对评分者严格程度敏感，必须报告 Coach A/B agreement、priority60 adjudication 和 sensitivity analysis。
6. Guard-only 条件在当前主实验中是 guard-instrumented / guard signal；除非触发 block fallback，否则不会改写最终学生可见回复。
7. Repair-enabled condition 表现好；新增 same-candidate stress test 显示 Repair 在固定 candidate 下可降低 leakage severity，但同时带来 student-burden trade-off。
8. DBox+Repair targeted fairness add-on 显示，Repair 也能帮助 DBox-inspired baseline 降低高风险泄露；但它是 20-case sensitivity evidence，不是主实验新 condition。

## 不能写的结论

1. Bridge Contract 全面显著优于所有 baseline。
2. Guard-only 修复了最终输出。
3. Repair 的因果效果已由主实验证明。
4. Coach A 或 Coach B 是 gold。
5. priority60 adjudicated labels 是 final gold。
6. 所有 50 cases 可以混成一个 headline 平均。
7. 50-case set 覆盖所有 CP tutoring 情景。
8. DBox / CodeHelp / CodeAid 条件是原论文系统复现；它们只能写成 literature-inspired baselines。
9. DBox+Repair 已完成 full 50-case 双教练人审，或已经证明 Bridge+Repair 对所有 repair-enabled baseline 有确定优势。

## 推荐论文表述

推荐使用：

```text
trade-off
trend
favorable overall-quality trend
favorable critical-leakage-control trend
rater-sensitive student-ready preference
formal human-review evidence candidate
```

避免使用：

```text
absolute winner
fully solved
significant dominance
final gold
Guard-only rewrite / repair claim
Repair causally proven by the main experiment
```

## 建议段落

```text
CP-MissingBridgeBench distinguishes tutor harnesses by their quality-safety-burden trade-offs rather than by a single global winner. In the dialogue-state v3 human-review candidate evidence, DBox-inspired decomposition is a strong baseline, while Bridge Contract compact + Guard/Repair shows favorable overall-quality and critical-leakage-control trends under the primary human-review view. Same-candidate Repair stress testing and the targeted DBox+Repair fairness add-on support Repair as a leakage-reduction mechanism with burden / over-strong-hint trade-offs. However, student-ready and rank preferences are rater-sensitive, Guard-only variants are instrumentation rather than rewrite conditions, and DBox+Repair remains sensitivity evidence rather than a full main condition.
```

## 使用边界

主论文 headline 应优先使用 `main_scaffold_eval` slice。`main_eval_with_caution`、`clarification_safety_slice`、`policy_safety_slice` 应单独报告或放入 sensitivity / appendix。all-case 平均只能作为补充敏感性，不应成为无分层 headline。

Repair 的精确写法：same-candidate stress test 支持“Repair reduces leakage under fixed-candidate stress testing, with burden trade-offs”；主实验仍只能支持 repair-enabled condition-level trend。

DBox+Repair 的精确写法：20-case targeted fairness add-on 支持“DBox+Repair reduces major/answer leakage on headline-sensitive cases and does not overturn the Bridge+Repair trend”，但不能写成 full 50-case fair baseline 结论。
