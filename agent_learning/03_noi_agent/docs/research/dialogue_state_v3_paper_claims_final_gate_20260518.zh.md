# Dialogue-State v3 Paper Claims Final Gate 20260518

本文件是投稿前的 claim gate。它不新增实验、不修改主实验数据、不接入线上 active mode；作用是防止 dialogue-state v3 evidence package 被写成过强论文结论。

## Claim Gate

| allowed wording | required evidence | forbidden wording |
| --- | --- | --- |
| CP-MissingBridgeBench 能揭示不同 LLM tutoring harness 的 quality-safety-burden trade-off。 | `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`；`dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md`；human review A/B + priority60 adjudication。 | CP-MissingBridgeBench 已完整覆盖所有 CP tutoring 场景；all 50 cases 可作为唯一 headline。 |
| 主 headline 使用 `main_scaffold_eval` 31 cases；其他 slices 分开作为 sensitivity / appendix。 | `dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`；`dialogue_state_v3_50_context_readiness_audit_20260515.jsonl`。 | 把 `main_eval_with_caution`、`clarification_safety_slice`、`policy_safety_slice` 和 main scaffold 混成一个 headline 平均。 |
| Bridge Contract compact + Guard/Repair 在 overall 和 critical-leakage control 上呈现稳定趋势优势。 | main scaffold table；paired W/T/L；paired CI；sensitivity tables。 | Bridge Contract 显著、全面、无条件优于所有 baseline。 |
| DBox-inspired decomposition 是强 baseline。 | DBox clean / guard 在 main scaffold 表和 paired comparison 中的表现。 | DBox baseline 很弱，或 Bridge 只是在弱 baseline 上取胜。 |
| no-direct-code / no-direct-solution baseline 仍可能出现 critical bridge leakage。 | `codehelp_codeaid_clean` 与 `enhanced_prompt_only_clean`、DBox / Bridge 条件的 leakage 对比。 | 不直接给代码就等于不会 critical bridge leakage。 |
| Guard-only 是 guard-instrumented / guard-checked condition，主要提供 runtime leakage signal。 | `paper_results_interpretation_guardrails_20260517.zh.md`；`run_bridge_offline_eval.py` 中 tutor_plus_guard 链路；主实验 block=0。 | Guard-only 修复了最终输出；Guard-only rewrite 已改写 student-visible response。 |
| Repair 的因果证据只来自 same-candidate stress test。 | `repair_same_candidate_stress_result_20260517.zh.md`；30-pair before/after blind review；summary JSON。 | 主实验 condition 均值已经单独证明 Repair 因果有效；Repair 已完全解决泄露。 |
| Repair 降低 leakage，但伴随 student burden trade-off。 | same-candidate stress：leakage improved 16/30，major leakage 7->0，burden worse 12/30。 | Repair 无代价提升质量；Repair 总是更好。 |
| DBox+Repair 是 targeted fairness sensitivity evidence。 | `dbox_guard_repair_fairness_report_20260517.zh.md`；20-case targeted review；same-case comparison summary。 | DBox+Repair 已完成完整 50-case 双教练主实验；Bridge+Repair 对所有 repair-enabled baselines 有确定优势。 |
| Coach A/B 和 priority60 adjudication 是 expert reference / adjudicated sensitivity view。 | A/B 350-row blind review；priority60 adjudication；agreement 和 sensitivity analysis。 | Coach A 是 gold；Coach B 是 gold；priority60 + Coach A/B 是 final gold。 |
| LLM grader 只能作为 scalable auxiliary grader。 | DeepSeek calibration：priority60 case-specific judge critical recall 0，major FN 1.000。 | LLM grader 可以替代人类教练；DeepSeek grader 已可靠识别 critical bridge leakage；LLM grader labels 是 gold。 |
| taxonomy 表述为 cognitive bridge family + leakage mechanism + surface anchor。 | `taxonomy_specificity_revision_summary_20260517.zh.md`；`dialogue_state_v3_observed_error_taxonomy_20260517.zh.md`。 | 本 benchmark 只评 DP state、binary-search check、lazy propagation、tree difference、local code 这些具体算法场景。 |

## 投稿前检查

投稿前每次改 Results / Discussion，都要重新检查：

1. headline 是否只来自 `main_scaffold_eval`。
2. Guard-only 是否仍写成 instrumentation，而不是 rewrite。
3. Repair 是否只把 same-candidate stress 写成因果证据。
4. DBox+Repair 是否仍在 appendix / fairness sensitivity 口径。
5. priority60、Coach A、Coach B 是否没有被称为 gold。
6. LLM grader 是否没有被写成替代人审。
7. taxonomy 是否没有退回到具体算法特调。
