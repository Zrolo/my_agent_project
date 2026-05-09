# Single LLM Structured Smoke 中文报告（2026-05-10）

状态：3 条样本的结构性 smoke test，不是最终论文结果。

## 目标

这次测试是为了确认新增的 `single_llm_structured` baseline 能不能和现有 `current_system`、`bridge_contract` 放到同一个离线评测格式里比较。

它回答的研究问题是：

```text
是否可以只用一个 LLM，一次性完成 bridge contract 诊断、学生回复生成和泄露自检？
```

## 实验设置

- Seed：`docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- 样本数：3
- Tutor 模型：`deepseek_flash`
- Thinking：`disabled`
- Pipeline：`tutor_only`
- 本轮不跑 Leakage Judge / Repair
- 输出目录：`evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/`

## 结果概览

| Tutor mode | 样本 | 错误 | 每轮 LLM 调用 | p50 延迟 | p95 延迟 | Bridge family 一致 | Focus 一致 | Help level 一致 | 非法标签率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `current_system` | 3 | 0 | 2.0 | 11666.521 ms | 14098.017 ms | 1.0 | 1.0 | 1.0 | 0.0 |
| `bridge_contract` | 3 | 0 | 2.0 | 12114.546 ms | 12832.904 ms | 1.0 | 1.0 | 1.0 | 0.0 |
| `single_llm_structured` | 3 | 0 | 1.0 | 5828.631 ms | 5908.953 ms | 0.0 | 0.0 | 0.333 | 1.0 |

## 主要发现

1. `single_llm_structured` 明显更快，因为它每轮只调用一个 LLM。
2. 它 3 条样本都能输出 JSON 和学生可见回复，结构上跑通了。
3. 但它的标签漂移很明显：`invalid_label_rate=1.0`。例如它会把 `primary_bridge_family` 写成“树上差分标记位置”这种中文自由文本，而不是 schema 中的合法枚举 `aggregation_contribution_bridge`。
4. 我已经顺手修了 summary：现在 single-LLM 的 `runtime_bridge_contract` 也会参与 bridge/focus/help-level agreement 计算，并且会把越界枚举计入非法标签。
5. 这个结果说明：single LLM 是必要 baseline，但不能直接假设它可以稳定替代 Bridge Judge。

## 对论文的意义

这轮 smoke 很有价值，因为它初步支持一个论文对比点：

```text
Single LLM 更快、更便宜；
Bridge Judge + Contract 更慢，但结构标签更稳定。
```

但现在只有 3 条样本，所以不能写成最终结论。下一步应该扩到 20 条 mini-study，并加入教练盲评回复质量。

## 产物

- 合并 JSONL：`evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/combined_tutor_only_smoke3.jsonl`
- Summary JSON：`evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/combined_tutor_only_smoke3_summary.json`
- 英文 summary：`evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/combined_tutor_only_smoke3_summary.md`
- 中文 summary：`evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/combined_tutor_only_smoke3_summary.zh.md`
