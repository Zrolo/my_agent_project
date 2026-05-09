# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Error Count | 0 |
| Student State Accuracy | 0.600 |
| Bridge Family Accuracy | 0.900 |
| Known Focus Accuracy | 0.700 |
| Known Focus Accuracy On Registered | 0.700 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.500 |
| Allowed Help Level Accuracy | 0.950 |
| Leakage Rate | n/a |
| Critical Bridge Leakage Rate | n/a |
| Answer Or Code Leakage Rate | n/a |
| Rewrite Rate | n/a |
| Block Rate | n/a |
| Repair Rate | 0.000 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | 0.000 |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 521.850 |
| Average LLM Call Count | 2.050 |
| Avg Bridge Judge Confidence | 0.899 |
| Total Latency P50 ms | 21120.987 |
| Total Latency P95 ms | 43397.752 |

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
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 2.100 |
| Total Latency P50 ms | 14732.092 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=enabled

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 32169.317 |
