# Prompt-Controlled Ablation Smoke Report 2026-05-11

This report addresses a key methodology question:

> Are Bridge Contract quality gains caused by modular architecture, or by stronger prompt wording?

This is a 3-case smoke run. It validates the experiment path and blind-review export, but it is not a final paper result.

## Design

The same cases are run through five variants:

| Variant | Purpose |
| --- | --- |
| `single_llm_structured` | Current strong single-LLM structured baseline |
| `enhanced_prompt_only` | Adds stronger tutoring instructions but no specific Bridge Contract; estimates prompt effect |
| `bridge_contract_predicted` | Uses Bridge Judge predicted contract; estimates practical diagnosis effect |
| `bridge_contract_shuffled` | Uses another case's oracle contract; checks whether the model truly depends on the contract |
| `bridge_contract_oracle` | Uses coach/gold contract as an upper bound for contract information |

Interpretation logic:

- If `enhanced_prompt_only` approaches `bridge_contract_predicted`, gains may mostly come from prompt wording.
- If `bridge_contract_predicted` beats `enhanced_prompt_only`, Bridge Judge diagnosis adds value.
- If `bridge_contract_shuffled` is still strong, the contract may be functioning as generic prompt decoration.
- If `bridge_contract_oracle` beats `bridge_contract_predicted`, the bottleneck may be Bridge Judge diagnosis accuracy.

## Artifacts

- Runner: [run_prompt_controlled_ablation.py](../../evals/aichat/run_prompt_controlled_ablation.py)
- Output JSONL: [prompt_controlled_ablation_smoke3_20260511.jsonl](../../evals/aichat/ad_hoc_runs/prompt_controlled_ablation_smoke3_20260511.jsonl)
- Blind review workbook: [coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.zh.xlsx](coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.zh.xlsx)
- Anonymous key: [coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.key.csv](coach_response_review_workbook_prompt_controlled_ablation_smoke3_20260511.key.csv)
- Blind review labels: [coach_response_review_labels_prompt_controlled_ablation_smoke3_20260511.jsonl](coach_response_review_labels_prompt_controlled_ablation_smoke3_20260511.jsonl)
- Blind review analysis: [prompt_controlled_ablation_blind_review_20260511.md](prompt_controlled_ablation_blind_review_20260511.md)

## Run Command

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

## Automatic Run Results

| Variant | Rows | Avg latency | Avg response length | Stage errors |
| --- | ---: | ---: | ---: | ---: |
| `single_llm_structured` | 3 | 16.29s | 228.7 chars | 0 |
| `enhanced_prompt_only` | 3 | 14.55s | 349.7 chars | 0 |
| `bridge_contract_predicted` | 3 | 26.35s | 509.0 chars | 0 |
| `bridge_contract_shuffled` | 3 | 17.17s | 474.7 chars | 0 |
| `bridge_contract_oracle` | 3 | 14.67s | 347.7 chars | 0 |

`bridge_contract_predicted` is slowest because it invokes Bridge Judge before tutor generation. The other prompt/contract variants only invoke the tutor.

## Preliminary Self-Check

This smoke run only confirms the workflow. It does not replace coach blind review. Two early signals are worth tracking:

1. `enhanced_prompt_only` already produces tutoring responses that resemble Bridge Contract outputs, so prompt wording may explain part of the quality gain.
2. `bridge_contract_shuffled` can still produce superficially reasonable responses in some cases, so blind review must test whether the model actually uses the specific contract rather than only the generic “use micro-examples and avoid leakage” instruction.

Therefore, the next step is prompt-controlled blind review, not a stronger architectural claim.

## Next Steps

1. The 3-case blind review is complete. It suggests that `enhanced_prompt_only` is already strong, so prompt wording likely explains a substantial part of the observed quality gain; however, `bridge_contract_predicted` outperforms `bridge_contract_shuffled`, so concrete contract content still appears meaningful.
2. Scale the same setup to 10-20 cases with the same anonymized blind-review flow.
3. Report three effects:
   - prompt effect: `enhanced_prompt_only - single_llm_structured`
   - predicted diagnosis effect: `bridge_contract_predicted - enhanced_prompt_only`
   - contract validity effect: `bridge_contract_predicted - bridge_contract_shuffled`
   - oracle upper-bound sanity check: `bridge_contract_oracle - bridge_contract_predicted`
4. If shuffled contracts still score highly, revise Bridge Contract prompting so that it relies more strongly on the specific missing bridge rather than generic tutoring style.
5. In the paper, state that current Bridge Contract gains may mix prompt wording, diagnosis information, and modular decomposition; this ablation is needed to separate them.
