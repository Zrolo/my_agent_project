# Hard Gate 过度兜底定点复测报告（2026-05-10）

## 复测目标

本次复测只针对前一轮盲评中最差的两条样例：

- `cp_bridge_010`：01 背包为什么容量要倒着枚举？正着枚举不是也能更新吗？
- `cp_bridge_017`：题目说合并两个集合，我知道可能是并查集，但不知道这个操作在代码里对应哪一步。

复测目标不是重新评估全部系统，而是验证：

1. `current_system` 是否还会被 hard gate 替换成“把题号或代码行发我”的泛化兜底。
2. `bridge_contract + guard` 是否能拦截过强回复。
3. `repair` 是否会把被删除的关键桥换一个例子又直接讲完。

## 复测数据

输入子集：

`evals/aichat/ad_hoc_runs/hard_gate_overfallback_20260510/seed_010_017.jsonl`

输出结果：

- `evals/aichat/ad_hoc_runs/hard_gate_overfallback_20260510/current_system_010_017.jsonl`
- `evals/aichat/ad_hoc_runs/hard_gate_overfallback_20260510/bridge_contract_guard_010_017.jsonl`
- `evals/aichat/ad_hoc_runs/hard_gate_overfallback_20260510/bridge_contract_guard_repair_010_017_promptfix.jsonl`

## 结果摘要

| Pipeline | cp_bridge_010 | cp_bridge_017 | 结论 |
| --- | --- | --- | --- |
| `current_system / tutor_only_no_diagnosis` | L2 回复，不再出现旧兜底 | L2 回复，不再出现旧兜底 | hard gate 过度兜底问题已修复 |
| `bridge_contract / tutor_plus_guard` | Leakage Judge 判 `block`，`final_response_text` 为空 | `pass`，保留候选回复 | guard 能识别 01 背包过强例子 |
| `bridge_contract / tutor_plus_guard_plus_repair`（修复后重跑） | `pass`，让学生自己算 `dp[2]` / `dp[4]` | `pass`，让学生映射 union 参数 | 比直接讲完桥梁更接近 bridge-oriented micro-example |

## 发现

1. 前一轮“题号/代码行”的最差回复不是 system prompt 的正常意图，而是 hard gate fallback 被错误触发。
2. `cp_bridge_010` 仍然是高风险样例：如果模型直接算完整正反例，很容易泄露“正序会重复使用当前物品”这座关键桥。
3. Repair prompt 原先不够硬：当 Leakage Judge 要求“让学生自己构造/计算例子”时，Repair Generator 可能替学生把替代例子也算完。
4. 本次已增强 Repair 约束：如果 repair instruction 要求学生自己构造、计算、比较或观察，修复回复不得替学生完成该小任务，只能给例子输入、观察问题和需要填写的空位。

## 已加回归保护

新增/更新测试：

- `test_aichat_hard_gate_fallback_regression_unit.py`
- `test_repair_response_v1_unit.py::test_repair_prompt_forbids_solving_replacement_micro_task`

验证命令：

```bash
python3 -m unittest test_repair_response_v1_unit.py \
  test_aichat_hard_gate_fallback_regression_unit.py \
  test_aichat_control_precedence_unit.py \
  test_aichat_risk_routing_policy_unit.py \
  test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_level_gate_fallback_should_not_use_removed_small_sample_template -v
```

结果：24 个相关测试通过。

## 后续建议

下一步不要立刻扩大功能，而应该把这两条样例加入 response quality regression set。后续每次改 tutor prompt、repair prompt 或 leakage judge prompt，都应检查：

- 是否又出现“安全但无用”的泛化兜底。
- 是否直接讲完关键桥。
- micro-example 是否带有观察问题和可迁移总结，而不是只让学生完成临时任务。
