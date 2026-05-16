# Post-repair fallback smoke（2026-05-12）

本报告是开发阶段 smoke，不是正式 held-out 结果。目的：验证离线 runner 新增的 `--post-repair-fallback-on-leak` 路径，并检查它在真实模型输出中的触发情况。

## 运行设置

输入：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/definition_first_regression_cases.jsonl
```

输出：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/bridge_contract_guard_repair_post_repair_fallback_5cases.jsonl
```

命令条件：

```text
tutor_mode=bridge_contract
pipeline_mode=tutor_plus_guard_plus_repair
guard_mode=predicted
chat_model_provider=deepseek_flash
judge_provider=deepseek
max_retries=1
post_repair_fallback_on_leak=true
```

## 自动指标

| metric | value |
| --- | ---: |
| cases | 5 |
| stage errors | 0 |
| leakage rate | 0.800 |
| critical bridge leakage rate | 0.000 |
| rewrite rate | 0.600 |
| repair rate | 0.600 |
| post-repair check rate | 0.600 |
| repair still leaks rate | 0.000 |
| post-repair rewrite/block rate | 0.000 |
| average LLM call count | 4.200 |
| p50 latency ms | 28875.869 |
| p95 latency ms | 47958.449 |

## Final Response Source

| case | final source | initial action | post-repair action | repair still leaks | interpretation |
| --- | --- | --- | --- | --- | --- |
| `cp_bridge_001` | repair | rewrite | pass | false | 未触发 fallback；自动 post-repair judge 认为修复版安全。 |
| `cp_bridge_002` | repair | rewrite | pass | false | 未触发 fallback；但自检仍认为 check true/false 填空接近 missing predicate bridge。 |
| `cp_bridge_003` | candidate | pass | n/a | n/a | 未进入 repair。 |
| `cp_bridge_005` | repair | rewrite | pass | false | 未触发 fallback；但自检认为 lazy 语义仍被答案槽位化，post-repair judge 可能 false negative。 |
| `cp_bridge_010` | candidate | pass | n/a | n/a | 未进入 repair；自检认为仍有轻微正序复用提示风险。 |

## 结论

`--post-repair-fallback-on-leak` 的代码路径已经有单测覆盖：如果 post-repair judge 仍判 rewrite/block，runner 会把 `final_response_source` 切到 `safe_fallback_after_repair`。但这次真实 5-case smoke 中没有触发 fallback，因为 post-repair judge 全部判 pass。

这说明该开关只解决一种失败：

```text
Repair 仍泄露，且 post-repair judge 抓到了。
```

它不能解决另一种更难的问题：

```text
Repair 仍泄露，但 post-repair judge 漏检。
```

因此下一步不应把安全希望全部押在 fallback 开关上，而应继续校准 Leakage Judge / Repair 对以下模式的识别：

1. answer-slot question：把关键桥变成 true/false、填表或候选动作选择题；
2. internal-field-update：把懒标记、状态格子、边界更新等内部字段关系包装成学生填写任务；
3. fully worked micro-example：例子没有直接给公式，但已经演示了学生本应抽象出的关键关系。

论文写法上应保持克制：

> Post-repair fallback is an offline safety policy that prevents known unsafe repairs from becoming final responses, but it remains limited by post-repair guard recall.

中文：

> post-repair fallback 可以防止“已被二次检测抓到的坏 Repair”成为最终回复，但它仍然受限于 post-repair Guard 的召回率。
