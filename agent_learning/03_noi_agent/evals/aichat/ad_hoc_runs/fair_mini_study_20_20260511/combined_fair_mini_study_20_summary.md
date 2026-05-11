# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 140 |
| Completed Count | 140 |
| Error Count | 0 |
| Student State Accuracy | 0.567 |
| Bridge Family Accuracy | 0.900 |
| Known Focus Accuracy | 0.800 |
| Known Focus Accuracy On Registered | 0.800 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.533 |
| Allowed Help Level Accuracy | 0.908 |
| Leakage Rate | 0.100 |
| Critical Bridge Leakage Rate | 0.037 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.100 |
| Block Rate | 0.000 |
| Repair Rate | 0.029 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | 0.000 |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 406.436 |
| Average LLM Call Count | 2.193 |
| Avg Bridge Judge Confidence | 0.892 |
| Total Latency P50 ms | 12490.538 |
| Total Latency P95 ms | 31250.261 |

## Leakage Levels

```json
{
  "0": 72,
  "1": 1,
  "2": 4,
  "3": 2,
  "4": 1
}
```

## Safe Actions

```json
{
  "pass": 72,
  "rewrite": 8
}
```

## Stage Errors

```json
{}
```

## Groups

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 13848.969 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.700 |
| Total Latency P50 ms | 20432.824 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.050 |
| Average LLM Call Count | 3.400 |
| Total Latency P50 ms | 21726.513 |

### tutor_mode=current_system|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 6241.816 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.050 |
| Total Latency P50 ms | 6843.860 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.100 |
| Average LLM Call Count | 2.150 |
| Total Latency P50 ms | 12014.984 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 2.050 |
| Total Latency P50 ms | 12043.094 |

