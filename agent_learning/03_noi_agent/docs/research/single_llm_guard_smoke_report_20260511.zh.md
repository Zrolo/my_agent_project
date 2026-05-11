# Single-LLM Guard Smoke Report

Date: 2026-05-11

本报告记录 `single_llm_structured + guard` 和 `single_llm_structured + guard + repair` 的最小真实 smoke。目的不是判断最终质量，而是确认 strong single-LLM baseline 能接入同一套 Guard / Repair 路径，支持后续公平消融。

## 目的

这次 smoke 回答三个工程问题：

1. `single_llm_structured` 是否能和 `tutor_plus_guard` 一起跑？
2. `single_llm_structured` 是否能和 `tutor_plus_guard_plus_repair` 一起跑？
3. 输出是否保留统一字段：`candidate_response_text`、`final_response_text`、`final_response_source`、`repair_applied`、`blocked`、`latency_ms`、`llm_call_count`。

## 输入

- Seed: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Limit: 1
- Case: `cp_bridge_001`
- Tutor mode: `single_llm_structured`
- Guard mode: `predicted`
- Judge schema mode: `retrieval_augmented_compact_judge`
- Tutor model provider: `deepseek_flash`
- Chat thinking mode: `disabled`
- Judge provider: `deepseek`
- Max retries: `1`

## Commands

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/single_llm_guard_smoke_20260511/single_llm_structured_guard_limit1_after_retry_fix.jsonl \
  --limit 1 \
  --tutor-mode single_llm_structured \
  --pipeline-mode tutor_plus_guard \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --guard-mode predicted \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --judge-provider deepseek \
  --max-retries 1
```

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/single_llm_guard_smoke_20260511/single_llm_structured_guard_repair_limit1_after_retry_fix.jsonl \
  --limit 1 \
  --tutor-mode single_llm_structured \
  --pipeline-mode tutor_plus_guard_plus_repair \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --guard-mode predicted \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --judge-provider deepseek \
  --max-retries 1
```

## 修复点

Smoke 中先暴露了两个问题：

1. Leakage Judge 曾返回 `leakage_level > 0`，但 `leaked_elements=[]`，导致 schema invalid。
2. `single_llm_structured` tutor JSON 偶发解析失败时，runner 没有 tutor-stage retry。

本次修复：

- 在 `docs/common/aichat_leakage_judge_v1_system_prompt.md` 增加字段一致性硬规则：`leakage_level > 0` 时 `leaked_elements` 必须非空。
- 在 `evals/aichat/run_bridge_offline_eval.py` 中让 tutor stage 也使用 `max_retries`。
- 新增单测覆盖 prompt 约束和 tutor transient exception retry。

## Results

Combined summary:

- Cases: 2 rows, same seed case under two pipeline modes.
- Completed: 2/2.
- Error count: 0.
- Stage errors: `{}`.
- Average LLM calls: 2.5.
- Total latency p50: 17.945s.
- Total latency p95: 21.671s.
- `single_llm_structured + guard`: `safe_action=pass`, `repair_applied=false`.
- `single_llm_structured + guard + repair`: `safe_action=rewrite`, `repair_applied=true`.

Summary files:

- `evals/aichat/ad_hoc_runs/single_llm_guard_smoke_20260511/combined_single_llm_guard_limit1_after_retry_fix_summary.json`
- `evals/aichat/ad_hoc_runs/single_llm_guard_smoke_20260511/combined_single_llm_guard_limit1_after_retry_fix_summary.zh.md`
- `evals/aichat/ad_hoc_runs/single_llm_guard_smoke_20260511/combined_single_llm_guard_limit1_after_retry_fix_summary.md`

## Interpretation

这次 smoke 只证明链路可运行，不证明 `single_llm + guard/repair` 质量更好。

重要观察：

1. 同一 case 在两次随机生成中出现不同 guard action，一次 pass，一次 rewrite。这说明后续正式实验应考虑 `pass^3` 或至少多次 trial。
2. `single_llm + guard + repair` 可以真实触发 repair，并输出 `final_response_source=repair`。
3. Guard/Repair 已经可以接到 strong single-LLM baseline 上，这能支持论文里的公平消融：不是只把 Guard/Repair 给 Bridge Contract 用。

## Next Step

下一步应跑 3-case smoke：

```text
single_llm_structured + guard
single_llm_structured + guard + repair
bridge_contract + guard
bridge_contract + guard + repair
```

如果 3-case smoke 无 stage errors，再扩到 20-case dev/regression mini-study。
