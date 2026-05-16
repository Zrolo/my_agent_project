# Answer-slot Guard Patch 自盲评（2026-05-12）

本报告是开发阶段自盲评，不是正式 held-out 结果。目的：检查 `judge_patch_20260512_answer_slot_upstream_observation_split` 是否让 Leakage Judge 更可靠地识别答案槽位式泄露。

## 运行设置

输入：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/definition_first_regression_cases.jsonl
```

输出：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/bridge_contract_guard_repair_answer_slot_guard_patch_5cases.jsonl
```

运行条件：

```text
tutor_mode=bridge_contract
pipeline_mode=tutor_plus_guard_plus_repair
guard_mode=predicted
chat_model_provider=deepseek_flash
judge_provider=deepseek
max_retries=1
post_repair_fallback_on_leak=true
```

自盲评标签：

```text
docs/research/answer_slot_guard_patch_self_review_20260512.jsonl
```

## 自动指标

| metric | value |
| --- | ---: |
| cases | 5 |
| stage errors | 0 |
| automatic leakage rate | 0.400 |
| automatic critical bridge leakage rate | 0.000 |
| rewrite rate | 0.200 |
| repair rate | 0.200 |
| post-repair check rate | 0.200 |
| repair still leaks rate | 0.000 |
| average LLM call count | 3.400 |
| p50 latency ms | 34205.981 |
| p95 latency ms | 45179.932 |

## 自盲评结果

| case | auto decision | self leakage | student-ready | quality | interpretation |
| --- | --- | --- | --- | ---: | --- |
| `cp_bridge_001` | level 0 / pass | major bridge leakage | no | 2 | 回复直接设定端点 `+1` 标记并让学生计算偏差，把贡献/汇总桥压成端点标记实验。 |
| `cp_bridge_002` | level 1 / pass | major bridge leakage | no | 2 | 回复要求学生回答 `check(mid)` true/false，并填写可行/不可行对应返回值；这是 predicate semantics missing bridge。 |
| `cp_bridge_003` | level 1 / rewrite, post pass | no leakage | borderline | 3 | 修复后安全但泛化，只问 DP 维度和关键变量，贴合度不足。 |
| `cp_bridge_005` | level 0 / pass | major bridge leakage | no | 2 | 回复让学生填写 lazy 存储值、负责区间和“表示____/将来要____”；这是内部字段语义答案槽位。 |
| `cp_bridge_010` | level 0 / pass | major bridge leakage | no | 2 | 回复给出一维 DP 语义和更新公式，并要求模拟正序/倒序复用；基本演示了 rolling-array order bridge。 |

## 结论

这次 patch 没有解决根因。自动 Judge 报告：

```text
critical_bridge_leakage_rate = 0.000
repair_still_leaks_rate = 0.000
```

但自盲评显示：

```text
4 / 5 rows still have major bridge leakage.
```

这说明问题已经不只是 prompt 里有没有写“答案槽位也可能泄露”，而是：

```text
LLM Leakage Judge 对答案槽位、filled-table 和 fully-worked micro-example 的召回仍不可靠。
```

## 对下一步的影响

不要继续用同一种方式堆 Leakage Judge prompt。下一步应转向：

1. 建立 deterministic / rule-based high-risk lint，只作为离线诊断信号，不直接替代教练 gold。
2. 把 `answer_slot_risk_flag`、`filled_trace_risk_flag`、`worked_example_risk_flag` 写入结果行，帮助定位 Guard 漏检。
3. 在 10-20 case dev ablation 和 50-case held-out 中分别报告：
   - automatic Guard label；
   - deterministic risk lint；
   - coach leakage label。
4. 论文写法应明确：LLM Guard 本身是被校准对象，不是 ground truth。

更稳的下一步不是继续修生成 prompt，而是增加可解释的静态风险诊断，让后续盲评和 judge calibration 能看到 Guard 为什么漏。

## 后续实现记录

本报告之后，离线 runner 已增加诊断字段：

```text
candidate_static_leakage_risk_lint
final_static_leakage_risk_lint
```

它们只用于解释风险，不作为自动 gold，也不直接修改最终回复。summary 脚本会报告 candidate/final 的静态风险率，以及 answer-slot、filled-trace、worked-example 三类子风险率。

对本次 5-case 输出临时计算静态风险后，结果与自盲评更接近：

| case | static risk types |
| --- | --- |
| `cp_bridge_001` | answer_slot; filled_trace; worked_example |
| `cp_bridge_002` | answer_slot; worked_example |
| `cp_bridge_003` | none |
| `cp_bridge_005` | answer_slot; filled_trace |
| `cp_bridge_010` | filled_trace; worked_example |

这不是最终裁决，但说明静态 lint 可以帮助定位 automatic Guard 漏检。
