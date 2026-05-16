# Definition-first / Post-repair 自盲评（2026-05-12）

本报告是开发阶段自盲评，不是正式 held-out 结果。目的不是证明系统有效，而是检查新增的 `post_repair_leakage_judge_result`、`repair_still_leaks` 是否能暴露 Repair 失败。

## 输入与输出

输入：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/definition_first_regression_cases.jsonl
```

运行条件：

```text
tutor_mode=bridge_contract
pipeline_mode=tutor_plus_guard_plus_repair
guard_mode=predicted
chat_model_provider=deepseek_flash
judge_provider=deepseek
max_retries=1
```

输出：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/bridge_contract_guard_repair_with_post_repair_check_5cases.jsonl
```

自盲评标签：

```text
docs/research/definition_first_post_repair_self_review_20260512.jsonl
```

## 自动指标

| metric | value |
| --- | ---: |
| cases | 5 |
| stage errors | 0 |
| leakage rate | 0.600 |
| critical bridge leakage rate | 0.400 |
| rewrite rate | 0.600 |
| repair rate | 0.600 |
| post-repair check rate | 0.600 |
| repair still leaks rate | 0.333 |
| post-repair rewrite/block rate | 0.333 |
| avg LLM call count | 4.400 |
| p50 latency ms | 42308.399 |
| p95 latency ms | 45699.191 |

## 自盲评结果

| case | auto guard | post repair | self leakage | student-ready | quality | interpretation |
| --- | --- | --- | --- | --- | ---: | --- |
| `cp_bridge_001` | level 3 / rewrite | pass | minor bridge leakage | yes | 4 | 修复版删除完整端点/LCA 公式，只保留端点标记观察与空表；仍给出端点 `+1` 这一半思路，有轻微提示风险。 |
| `cp_bridge_002` | pass | n/a | major bridge leakage | borderline | 3 | 回复要求学生判断 `check(4)` 返回 true/false，并总结 true 代表可行还是不可行；这是学生当前卡住的布尔语义桥，属于答案槽位型 Guard false negative。 |
| `cp_bridge_003` | pass | n/a | no leakage | yes | 5 | 只让学生解释二维表一个格子的含义，没有直接给完整 DP 定义或转移，桥梁导向清楚。 |
| `cp_bridge_005` | level 3 / rewrite | level 3 / rewrite | major bridge leakage | no | 2 | Repair 后仍要求填写 lazy 语义，并保留 `sum/lazy/当前值/目标值` 关系的强约束表格；post-repair judge 也判仍需 rewrite。 |
| `cp_bridge_010` | level 1 / rewrite | pass | minor bridge leakage | yes | 4 | 修复版让学生自选极小例子并模拟正序更新，没有直接给倒序模板；但仍提示观察同一物品是否可能被计入多次。 |

## 关键发现

1. `post_repair_leakage_judge_result` 有价值：它明确抓出了 `cp_bridge_005` 的 Repair failure。
2. Guard 仍有 false negative：`cp_bridge_002` 的 check true/false 语义被包装成学生填空问题，自动 Guard 判 pass，但自盲评认为是 major bridge leakage。
3. Repair 不是安全终点：3 个触发 repair 的 case 中，1 个修复后仍泄露，开发集 `repair_still_leaks_rate=0.333`。
4. 质量和安全仍有权衡：`cp_bridge_001` 和 `cp_bridge_010` 的修复版教学体验可以接受，但仍存在轻微 bridge hint。

## 对下一步的影响

不要继续只加生成 prompt 规则。下一步应做：

1. 把 `cp_bridge_002` 加入 Guard false-negative regression set，重点校准 answer-slot / predicate-semantics 检测。
2. 把 `cp_bridge_005` 加入 Repair failure regression set，重点校准 internal-field-update 和 filled-table leakage。
3. 离线 runner 已增加可选实验条件：`--post-repair-fallback-on-leak`。当 post-repair judge 仍判 rewrite/block 时，不再把 repair 文本作为最终回复，而是切到 deterministic safe fallback。后续报告见 [post_repair_fallback_smoke_20260512.zh.md](post_repair_fallback_smoke_20260512.zh.md)。
4. 在正式报告中单独报告 `repair_still_leaks_rate`，不能只报告 `repair_rate`。
