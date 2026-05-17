# Paper Results Interpretation Guardrails (20260517)

## 可以写

- CP-MissingBridgeBench 揭示不同 LLM tutoring harness 的质量、安全和学生负担 trade-off。
- DBox-inspired decomposition 是强 baseline，不能被当作弱对照。
- 在 `main_scaffold_eval` + `priority60 adjudicated + Coach A` 主口径下，`bridge_contract_compact_guard_repair` 的 overall 最高，critical/answer leakage 控制较稳；但 paired CI 多数跨 0，应写为趋势/权衡优势。
- `bridge_contract_compact_guard` 与 `bridge_contract_compact_guard_repair` 都能把主 slice 的 critical/answer leakage 控到 0；Repair 条件 overall 略高，但因果效果未由主实验证明。
- student-ready、rank preference、would-show 对 rater strictness 敏感，必须报告 Coach A/B agreement、adjudication 和 sensitivity analysis。

## 不能写

- Bridge Contract 显著、全面优于所有 baseline。
- Guard-only 已经降低最终学生可见回复的泄露。
- Repair 的因果效果已由 50-case 主实验证明。
- Coach A 或 Coach B 任一方就是 gold。
- priority60 裁决后就是 final adjudicated gold。
- DBox/CodeHelp/CodeAid 是原论文复现；它们只能写作 literature-inspired baselines。

## Guard-only 的精确口径

当前 `tutor_plus_guard` 链路中，Leakage Judge 返回 `rewrite` 时不会改 `final_response_text`；只有 `block` 会触发 deterministic safe fallback。本轮主实验 `block=0`。因此 `dbox_inspired_guard`、`bridge_guided_dbox_style_guard`、`bridge_contract_compact_guard` 应称为 guard-instrumented / guard-checked variants，而不是 guard-rewritten variants。

推荐写法：Guard-only 条件主要提供泄露风险检测信号；除非触发 block fallback，否则不改写最终学生可见回复。因此 guard-only 结果不能解释为 Guard 已实际修复输出。

## Repair 的精确口径

`bridge_contract_compact_guard_repair` 是 repair-enabled condition，且在主结果中表现最好；但 Repair 只触发部分 case，且不同 condition 的 candidate 不同。主实验只能支持 condition-level trade-off，不支持 same-candidate causal Repair claim。

推荐写法：Repair-enabled Bridge Contract condition shows the strongest overall/leakage trade-off in the current human-review candidate evidence. A same-candidate stress test is required to estimate the causal Repair effect.

## Taxonomy / Coverage Guardrail

不要写成：CP-MissingBridgeBench 只评估 DP 状态、转移、check、边界、lazy、差分和局部代码。

可以写成：这些是具体算法语境中的 surface anchors；主 taxonomy 是 Research v1 operational cognitive bridge families 与 tutor leakage mechanisms。`state_representation_semantics`、`predicate_check_semantics` 等 bridge bucket 是 operational cognitive bridge family，不是 surface anchor。

论文应强调当前 50-case set 覆盖 representation、transition/action mapping、predicate/decision semantics、ordering/dependency、modeling、aggregation/contribution、data-structure operation、correctness/invariant、implementation、debugging evidence 和 policy request 等 family。coverage limitations 也要正面报告：math property / modular invariant、counting / inclusion-exclusion、geometry predicate relation、search pruning / deduplication、reflection / transfer 覆盖仍有限。

## 下一步优先级

1. 报告 paired uncertainty：W/T/L、mean delta、bootstrap CI、paired permutation。
2. 追加 targeted adjudication 30-40 条 headline-sensitive 分歧。
3. 完成 Repair same-candidate stress test。
4. 给 DBox+Repair 做最小补充人审，堵住 fairness add-on 风险。
5. 做 LLM grader calibration，只把自动评审写成 auxiliary grader。
