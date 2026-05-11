# Prompt-Controlled Ablation Smoke Report 2026-05-11

本报告回答一个关键方法论问题：

> Bridge Contract 组质量提升，究竟来自模块化架构，还是来自更强的 prompt wording？

本次只做 3-case smoke，目的是验证实验链路和盲评表生成，不作为最终论文结论。

## 实验设计

同一批 case 跑 5 个变体：

| Variant | 目的 |
| --- | --- |
| `single_llm_structured` | 当前 strong single-LLM structured baseline |
| `enhanced_prompt_only` | 只加入更强教学提示词，不给具体 Bridge Contract，用来估计 prompt effect |
| `bridge_contract_predicted` | 使用 Bridge Judge 预测 contract，用来估计实际 diagnosis effect |
| `bridge_contract_shuffled` | 使用其他 case 的 oracle contract，用来检测模型是否真的依赖 contract |
| `bridge_contract_oracle` | 使用 coach/gold contract，作为 contract 信息上界 |

解释逻辑：

- 如果 `enhanced_prompt_only` 接近 `bridge_contract_predicted`，说明质量提升可能主要来自 prompt wording。
- 如果 `bridge_contract_predicted` 明显好于 `enhanced_prompt_only`，说明 Bridge Judge 提供的诊断信息有额外价值。
- 如果 `bridge_contract_shuffled` 仍然很好，说明 contract 可能只是“提示词装饰”，模型没有真正使用具体诊断。
- 如果 `bridge_contract_oracle` 明显好于 `bridge_contract_predicted`，说明瓶颈可能在 Bridge Judge 诊断准确性。

## 产物

- Runner: [run_prompt_controlled_ablation.py](../../evals/aichat/run_prompt_controlled_ablation.py)
- Output JSONL: [prompt_controlled_ablation_smoke3_20260511.jsonl](../../evals/aichat/ad_hoc_runs/prompt_controlled_ablation_smoke3_20260511.jsonl)
- Blind review workbook: [coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.zh.xlsx](coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.zh.xlsx)
- Anonymous key: [coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.key.csv](coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.key.csv)
- Blind review labels: [coach_response_review_labels_prompt_controlled_ablation_smoke3_20260511.jsonl](coach_response_review_labels_prompt_controlled_ablation_smoke3_20260511.jsonl)
- Blind review analysis: [prompt_controlled_ablation_blind_review_20260511.zh.md](prompt_controlled_ablation_blind_review_20260511.zh.md)

## 运行配置

```bash
NOI_CHAT_THINKING_MODE=disabled \
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=40 \
NOI_CHAT_TIMEOUT_SECONDS=90 \
python3 -m evals.aichat.run_prompt_controlled_ablation \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/prompt_controlled_ablation_smoke3_20260511.jsonl \
  --limit 3 \
  --chat-model-provider deepseek \
  --judge-provider deepseek \
  --max-retries 1
```

## 自动运行结果

| Variant | Rows | Avg latency | Avg response length | Stage errors |
| --- | ---: | ---: | ---: | ---: |
| `single_llm_structured` | 3 | 16.29s | 228.7 chars | 0 |
| `enhanced_prompt_only` | 3 | 14.55s | 349.7 chars | 0 |
| `bridge_contract_predicted` | 3 | 26.35s | 509.0 chars | 0 |
| `bridge_contract_shuffled` | 3 | 17.17s | 474.7 chars | 0 |
| `bridge_contract_oracle` | 3 | 14.67s | 347.7 chars | 0 |

`bridge_contract_predicted` 最慢，因为它额外调用 Bridge Judge；其余 contract/prompt-only 组只调用 tutor。

## 初步人工自检

这次 smoke 只确认链路可运行，不替代教练盲评。粗看样本，有两个值得注意的信号：

1. `enhanced_prompt_only` 已经能生成比较像 Bridge Contract 的教学回复，说明 prompt wording 很可能贡献了相当一部分质量提升。
2. `bridge_contract_shuffled` 在部分 case 上仍能输出表面不错的回复，说明我们必须用盲评判断模型是否真的使用了“具体 contract”，而不是只受到了“请用微型例子、不要泄露”的通用提示影响。

因此，下一步不能简单说“架构带来提升”，而要做 prompt-controlled blind review。

## 下一步

1. 3-case 盲评已经完成。结果显示 `enhanced_prompt_only` 平均质量很强，说明 prompt wording 本身可能解释相当一部分提升；但 `bridge_contract_predicted` 明显好于 `bridge_contract_shuffled`，说明具体 contract 内容仍可能有额外价值。
2. 扩到 10-20 case，并继续使用相同的匿名盲评流程。
3. 把正式报告分成三类 effect：
   - prompt effect: `enhanced_prompt_only - single_llm_structured`
   - predicted diagnosis effect: `bridge_contract_predicted - enhanced_prompt_only`
   - contract validity effect: `bridge_contract_predicted - bridge_contract_shuffled`
   - oracle upper-bound sanity check: `bridge_contract_oracle - bridge_contract_predicted`
4. 若 shuffled contract 仍然高分，需要修 Bridge Contract prompt，让它更明确依赖具体 missing bridge，而不是只套通用教学模板。
5. 在论文里明确：当前 pilot 的 Bridge Contract 增益可能混合了 prompt wording、diagnosis information 和 modular decomposition，必须通过本消融分开解释。
