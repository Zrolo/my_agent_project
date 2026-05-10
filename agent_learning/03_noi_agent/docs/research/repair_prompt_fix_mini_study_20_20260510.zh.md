# Repair Prompt Fix 20 条复测报告（2026-05-10）

## 背景

上一轮定点复测发现：`repair_response_v1` 在修复过强 micro-example 时，可能会把被删除的关键桥换成另一个完整算完的小例子。这样虽然形式上“修复”了原回复，但仍可能替学生完成关键观察。

本次复测只验证 repair prompt 修复后的 `bridge_contract + guard + repair` 链路，不代表线上 AIChat 已接入该流程。

## 运行设置

- 输入：`docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- 输出：`evals/aichat/ad_hoc_runs/mini_study_20_20260510/bridge_contract_guard_repair_20_repairpromptfix_clean.jsonl`
- Summary：
  - `evals/aichat/ad_hoc_runs/mini_study_20_20260510/bridge_contract_guard_repair_20_repairpromptfix_clean_summary.json`
  - `evals/aichat/ad_hoc_runs/mini_study_20_20260510/bridge_contract_guard_repair_20_repairpromptfix_clean_summary.zh.md`
- Tutor：`deepseek_flash`
- Thinking：disabled
- Judge schema：`retrieval_augmented_compact_judge`
- Guard：predicted
- Pipeline：`tutor_plus_guard_plus_repair`

## 主要结果

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 错误数 | 0 |
| Bridge family agreement | 0.900 |
| Known focus agreement | 0.800 |
| Help level agreement | 0.950 |
| Candidate leakage rate | 0.300 |
| Candidate critical bridge leakage rate | 0.050 |
| Answer/code leakage rate | 0.000 |
| Rewrite / repair rate | 0.200 |
| Final blocked rate | 0.000 |
| 平均 LLM 调用次数 | 3.600 |
| 总延迟 P50 | 18.17s |
| 总延迟 P95 | 29.04s |

说明：这里的 leakage rate / critical bridge leakage rate 是 Leakage Judge 对“候选回复”的判断，不等于 repair 后的 `final_response_text` 仍然泄露。

## Repair 触发样例

本轮共有 4 条样例触发 rewrite/repair：

- `cp_bridge_003`：DP 状态语义。修复后让学生从 `dp[0] / dp[3] / dp[5]` 推断 `dp[t]` 含义。
- `cp_bridge_006`：Trie 共享前缀。修复后要求学生画 Trie 并观察哪些节点合并了前缀。
- `cp_bridge_008`：二分左边界。修复后让学生模拟含重复值数组，观察直接返回 `mid` 的问题。
- `cp_bridge_010`：01 背包倒序枚举。修复后不再替学生算完整结果，而是要求学生自己构造一个只有一件物品的小例子，并观察 `dp[c-w]` 是否已经被当前物品更新过。

## 关键观察

1. `cp_bridge_010` 已从“替学生算完整正反例”收敛到“给观察问题，让学生自己模拟”。这正好对应我们新增的 bridge-oriented micro-example 要求。
2. `repair_response_v1` 现在更像“当前回复修复器”，而不是第二个 tutor。它只应该删除泄露、保留意图、补一个半步脚手架。
3. 延迟仍然较高：p50 约 18s，p95 约 29s。这支持我们的论文主张：完整多阶段链路适合离线评测和高风险 turn，不适合作为每轮线上默认路径。
4. 新结果不能和旧结果做严格逐项因果对比，因为 LLM 输出存在随机性；本报告只作为 repair prompt fix 后的一次 clean rerun。

## 对论文的意义

这次复测支撑两个 Research v1 观点：

1. **Critical bridge leakage 不只发生在完整代码/完整题解中。** 一个完整算完的小例子也可能泄露当前关键桥。
2. **Repair 不能只是“换一种说法”。** 高质量 repair 应把过强回答转成 bridge-oriented micro-example：给学生一个观察对象、一个具体问题和一个可迁移总结目标。

## 下一步

建议下一步不要继续扩大线上逻辑，而是：

1. 把这 4 条 repair 样例加入 response-quality regression set。
2. 重新导出一个小型中文盲评表，只包含 repair 前后对比，让教练判断 repair 是否真的提高教学质量。
3. 在 50 条 seed 扩展前，先固定“bridge-oriented micro-example score”的评分说明。
