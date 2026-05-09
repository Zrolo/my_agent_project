# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 9 |
| Completed Count | 9 |
| Error Count | 0 |
| Student State Accuracy | 1.000 |
| Bridge Family Accuracy | 0.667 |
| Known Focus Accuracy | 0.667 |
| Known Focus Accuracy On Registered | 0.667 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.667 |
| Allowed Help Level Accuracy | 0.778 |
| Leakage Rate | n/a |
| Critical Bridge Leakage Rate | n/a |
| Answer Or Code Leakage Rate | n/a |
| Rewrite Rate | n/a |
| Block Rate | n/a |
| Repair Rate | 0.000 |
| Invalid Label Rate | 0.333 |
| Focus Out Of Registry Rate | 0.000 |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 377.222 |
| Average LLM Call Count | 1.667 |
| Avg Bridge Judge Confidence | 0.897 |
| Total Latency P50 ms | 11666.521 |
| Total Latency P95 ms | 14098.017 |

## Leakage Levels

```json
{}
```

## Safe Actions

```json
{}
```

## Stage Errors

```json
{}
```

## Groups

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 12114.546 |

### tutor_mode=current_system|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 11666.521 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Bridge Family Accuracy | 0.000 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 5828.631 |
