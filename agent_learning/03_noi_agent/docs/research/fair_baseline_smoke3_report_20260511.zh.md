# Fair Baseline Smoke 3 Report

Date: 2026-05-11

本报告记录 3-case dev/regression smoke。目标不是判断最终质量，而是确认主实验需要的公平 baseline 组合能在同一套 runner、Guard、Repair、summary 中稳定运行。

## 为什么做这个 smoke

外部审查指出：如果只比较 `single_llm_structured` 和 `bridge_contract + guard + repair`，审稿人会问：

```text
Guard / Repair 的收益是不是也能直接加在 single-LLM baseline 上？
为什么一定要 Bridge Contract？
```

因此 Research v1 主实验必须支持：

```text
single_llm_structured
single_llm_structured + guard
single_llm_structured + guard + repair
bridge_contract
bridge_contract + guard
bridge_contract + guard + repair
```

这次 smoke 先验证其中 4 个带 Guard 的路径。

## Input

- Seed: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Limit: 3
- Cases: `cp_bridge_001`、`cp_bridge_002`、`cp_bridge_003`
- Guard mode: `predicted`
- Judge schema mode: `retrieval_augmented_compact_judge`
- Tutor model provider: `deepseek_flash`
- Chat thinking mode: `disabled`
- Judge provider: `deepseek`
- Max retries: `1`

## Systems

| System | Runner Settings |
|---|---|
| `single_llm_structured + guard` | `--tutor-mode single_llm_structured --pipeline-mode tutor_plus_guard` |
| `single_llm_structured + guard + repair` | `--tutor-mode single_llm_structured --pipeline-mode tutor_plus_guard_plus_repair` |
| `bridge_contract + guard` | `--tutor-mode bridge_contract --pipeline-mode tutor_plus_guard` |
| `bridge_contract + guard + repair` | `--tutor-mode bridge_contract --pipeline-mode tutor_plus_guard_plus_repair` |

## Results

Combined files:

- Results JSONL: `evals/aichat/ad_hoc_runs/fair_baseline_smoke3_20260511/combined_fair_baseline_smoke3.jsonl`
- Summary JSON: `evals/aichat/ad_hoc_runs/fair_baseline_smoke3_20260511/combined_fair_baseline_smoke3_summary.json`
- Chinese summary: `evals/aichat/ad_hoc_runs/fair_baseline_smoke3_20260511/combined_fair_baseline_smoke3_summary.zh.md`
- English summary: `evals/aichat/ad_hoc_runs/fair_baseline_smoke3_20260511/combined_fair_baseline_smoke3_summary.md`

Overall:

| Metric | Value |
|---|---:|
| Rows | 12 |
| Completed | 12 |
| Error count | 0 |
| Stage errors | 0 |
| Bridge family accuracy | 1.000 |
| Known focus accuracy | 1.000 |
| Critical bridge leakage rate | 0.000 |
| Answer/code leakage rate | 0.000 |
| Rewrite rate | 0.083 |
| Repair rate | 0.083 |
| Average LLM calls | 2.750 |
| Total latency p50 | 14.144s |
| Total latency p95 | 34.648s |

By group:

| Group | Cases | Safe Actions | Repair Rate | Avg LLM Calls | p50 Latency | p95 Latency |
|---|---:|---|---:|---:|---:|---:|
| `single_llm_structured + guard` | 3 | pass: 3 | 0.000 | 2.000 | 12.932s | 13.406s |
| `single_llm_structured + guard + repair` | 3 | pass: 3 | 0.000 | 2.000 | 10.844s | 12.472s |
| `bridge_contract + guard` | 3 | pass: 3 | 0.000 | 3.333 | 16.950s | 24.326s |
| `bridge_contract + guard + repair` | 3 | pass: 2, rewrite: 1 | 0.333 | 3.667 | 19.798s | 34.648s |

## Repair Trigger

唯一一次 repair 出现在：

```text
case: cp_bridge_001
system: bridge_contract + guard + repair
leakage_level: 2
safe_action: rewrite
leaked_elements: 直接给出了端点和 LCA 的标记规则
final_response_source: repair
```

这说明 Repair 链路可以真实触发并输出 `final_response_source=repair`。但这仍然只是 smoke，不代表 Repair 已被证明有效。Repair 的正式证据仍需要 20-30 条高泄露 stress candidates 和 before/after blind review。

## Interpretation

这次 smoke 支撑三个结论：

1. `single_llm_structured + guard` 和 `single_llm_structured + guard + repair` 已经能跑通，支持公平消融。
2. Bridge Contract 路径调用更多 LLM，延迟明显更高；这支持后续把 latency / LLM calls 作为论文的一等指标。
3. 在这 3 个样本上，single-LLM 路径没有触发 rewrite；Bridge Contract full path 触发 1 次 rewrite。这不是质量结论，只说明后续需要更多样本和盲评。

## Limitations

- 只有 3 个 dev/regression 样本，不是 held-out test。
- 模型输出有随机性，同一 case 可能在不同 run 中触发不同 Guard action。
- 没有 coach blind review，因此不能判断最终回复质量。
- 没有 `pass^3` 稳定性实验。

## Next Step

下一步可以进入 20-case dev/regression mini-study，建议矩阵：

```text
current_system
single_llm_structured
single_llm_structured + guard
single_llm_structured + guard + repair
bridge_contract
bridge_contract + guard
bridge_contract + guard + repair
```

跑完后导出新的中文盲评表，让教练只评 `final_response_text`。
