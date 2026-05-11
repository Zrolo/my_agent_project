# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 12 |
| Completed Count | 12 |
| Error Count | 0 |
| Student State Accuracy | 0.833 |
| Bridge Family Accuracy | 1.000 |
| Known Focus Accuracy | 1.000 |
| Known Focus Accuracy On Registered | 1.000 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.667 |
| Allowed Help Level Accuracy | 0.917 |
| Leakage Rate | 0.083 |
| Critical Bridge Leakage Rate | 0.000 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.083 |
| Block Rate | 0.000 |
| Repair Rate | 0.083 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | 0.000 |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 481.417 |
| Average LLM Call Count | 2.750 |
| Avg Bridge Judge Confidence | 0.922 |
| Total Latency P50 ms | 14143.832 |
| Total Latency P95 ms | 34648.289 |

## Leakage Levels

```json
{
  "0": 11,
  "2": 1
}
```

## Safe Actions

```json
{
  "pass": 11,
  "rewrite": 1
}
```

## Stage Errors

```json
{}
```

## Groups

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.667 |
| Total Latency P50 ms | 19798.445 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.333 |
| Total Latency P50 ms | 16949.876 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 10843.644 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 12932.248 |
