# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 100 |
| Completed Count | 100 |
| Error Count | 0 |
| Student State Accuracy | 0.650 |
| Bridge Family Accuracy | 0.900 |
| Known Focus Accuracy | 0.812 |
| Known Focus Accuracy On Registered | 0.812 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.583 |
| Allowed Help Level Accuracy | 0.912 |
| Leakage Rate | 0.100 |
| Critical Bridge Leakage Rate | 0.000 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.025 |
| Block Rate | 0.000 |
| Repair Rate | 0.000 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | 0.000 |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 405.030 |
| Average LLM Call Count | 2.160 |
| Avg Bridge Judge Confidence | 0.897 |
| Total Latency P50 ms | 13497.609 |
| Total Latency P95 ms | 22471.240 |

## Leakage Levels

```json
{
  "0": 34,
  "1": 3,
  "2": 1,
  "unknown": 2
}
```

## Safe Actions

```json
{
  "pass": 37,
  "rewrite": 1,
  "unknown": 2
}
```

## Stage Errors

```json
{
  "leakage_judge": 2
}
```

## Groups

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 2.100 |
| Total Latency P50 ms | 13691.467 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.350 |
| Total Latency P50 ms | 17094.474 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.350 |
| Total Latency P50 ms | 18157.722 |

### tutor_mode=current_system|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 7631.893 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 7159.394 |

