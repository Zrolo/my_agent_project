# Single LLM 严格 Schema Smoke 中文报告（2026-05-10）

状态：3 条样本的 prompt ablation smoke test，不是最终论文结果。

## 目标

上一轮 `single_llm_structured` 证明了“一次 LLM 调用”很快，但也暴露了明显问题：模型会输出不在 schema 里的中文自由标签，例如 `树上差分标记位置`。

这次测试把 single-LLM prompt 收紧：

- 明确列出 `turn_type`、`algorithm_topic_l1`、`primary_bridge_family`、`max_scaffold_level`、`leakage_risk` 的合法枚举；
- 明确禁止输出中文自由 schema 标签；
- 把非 LLM 的 top-k `algorithm_topic` 和 `registered_focus` 候选注入给模型；
- 要求 `selected_focus_id` 只能从 top-k 候选里选，或输出 `unknown`。

## 设置

- Seed：`docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- 样本数：3
- Tutor 模型：`deepseek_flash`
- Thinking：`disabled`
- Pipeline：`tutor_only`
- 本轮不跑 Leakage Judge / Repair
- 输出目录：`evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/`

## 结果

| Single-LLM 版本 | 样本 | 错误 | 每轮 LLM 调用 | p50 延迟 | p95 延迟 | Bridge family 一致 | Focus 一致 | Help level 一致 | 非法标签率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| loose schema prompt | 3 | 0 | 1.0 | 5828.631 ms | 5908.953 ms | 0.0 | 0.0 | 0.333 | 1.0 |
| strict schema + top-k candidates | 3 | 0 | 1.0 | 6413.114 ms | 7712.401 ms | 1.0 | 1.0 | 0.0 | 0.0 |

## 解释

严格 prompt 解决了这 3 条样本里最严重的结构问题：

- 非法标签率从 `1.0` 降到 `0.0`；
- bridge family 一致率从 `0.0` 升到 `1.0`；
- focus 一致率从 `0.0` 升到 `1.0`。

代价是延迟略有上升，因为 prompt 变长，并且注入了 top-k 候选。不过它仍然是一轮 LLM 调用，整体仍比 Bridge Judge + Tutor 两次调用更快。

但严格 prompt 仍然有一个明显问题：帮助强度没有对齐。3 条样本里它都选择了 `L1`，而教练参考标签是 `L2`。这说明下一轮不应继续纠结 schema 合法性，而应该校准 `max_scaffold_level` 的判断标准。

## 对论文的价值

这轮结果能形成一个很干净的 ablation：

```text
single_llm_loose_schema：
  快，但标签漂移严重。

single_llm_strict_schema_topk：
  仍然只调用一次 LLM，标签漂移显著降低，但帮助强度校准仍弱。
```

这对论文很重要，因为它不是简单说“多层 LLM 更好”，而是先认真比较了单 LLM 能做到什么、做不到什么。

## 产物

- Strict JSONL：`evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/single_llm_structured_strict_tutor_only_smoke3.jsonl`
- Strict summary JSON：`evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/single_llm_structured_strict_tutor_only_smoke3_summary.json`
- Strict 英文 summary：`evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/single_llm_structured_strict_tutor_only_smoke3_summary.md`
- Strict 中文 summary：`evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/single_llm_structured_strict_tutor_only_smoke3_summary.zh.md`
