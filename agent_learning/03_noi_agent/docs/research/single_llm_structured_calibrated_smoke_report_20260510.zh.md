# Single-LLM Structured Baseline：帮助强度校准 Smoke

日期：2026-05-10

## 目的

上一轮 strict single-LLM structured baseline 已经解决了 schema 漂移问题，但它在 3 条可诊断学习轮次里全部选择 `L1`，过于保守。本轮测试要验证：加入明确的帮助强度校准规则后，单次 LLM baseline 能否在适合桥梁导向微型例子时选择 `L2`。

## 改动

`single_llm_structured` system prompt 新增了：

- 明确的 `L0/L1/L2/L3` 边界；
- 说明“学生卡点明确且上下文足够”时，可以使用 `L2` 的微型例子、半步关系或 partial trace；
- 增加“禁止内容不能包装成假设句”的泄露规则；
- 要求自检：如果学生可见回复直接或变相说出了 forbidden content，`self_check.predicted_leakage_risk` 必须标为 `medium` 或 `high`。

## 命令

```bash
NOI_CHAT_TIMEOUT_SECONDS=180 NOI_CHAT_MAX_COMPLETION_TOKENS=9000 \
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3.jsonl \
  --limit 3 \
  --tutor-mode single_llm_structured \
  --pipeline-mode tutor_only \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --judge-schema-mode retrieval_augmented_compact_judge
```

## 结果

| 版本 | 样本数 | 错误数 | 每轮 LLM 调用 | p50 延迟 | p95 延迟 | Bridge family 准确率 | Focus 准确率 | 帮助等级准确率 | 非法标签率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 宽松 one-call prompt | 3 | 0 | 1.0 | 5828.631 ms | 5908.953 ms | 0.0 | 0.0 | 0.333 | 1.0 |
| 严格枚举 + top-k focus | 3 | 0 | 1.0 | 6413.114 ms | 7712.401 ms | 1.0 | 1.0 | 0.0 | 0.0 |
| 帮助校准 + 防假设句泄露 | 3 | 0 | 1.0 | 8171.739 ms | 8410.813 ms | 1.0 | 1.0 | 1.0 | 0.0 |

## 解读

帮助强度校准修复了过度保守的 `L1` 问题。在这个 3 条 smoke 里，单次 LLM baseline 的 bridge family、registered focus、帮助等级都和教练参考标签对齐。

但这并不说明 single-LLM 就足够上线。它生成的回复里仍然有潜在泄露风险：第 2、3 条的 `self_check` 都把泄露风险标成了 `medium`。尤其 DP 状态设计那条，虽然没有给完整转移式，但仍然给了较强的状态内容线索。这反而说明：single-LLM 可以作为快速 baseline，但不能替代独立 Leakage Judge / Repair。

## 产物

- JSONL：`evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3.jsonl`
- Summary JSON：`evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3_summary.json`
- 英文 summary：`evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3_summary.md`
- 中文 summary：`evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3_summary.zh.md`

