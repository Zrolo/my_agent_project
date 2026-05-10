# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Error Count | 0 |
| Student State Accuracy | 0.650 |
| Bridge Family Accuracy | 0.900 |
| Known Focus Accuracy | 0.800 |
| Known Focus Accuracy On Registered | 0.800 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.500 |
| Allowed Help Level Accuracy | 0.950 |
| Leakage Rate | 0.050 |
| Critical Bridge Leakage Rate | 0.000 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.000 |
| Block Rate | 0.000 |
| Repair Rate | 0.000 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | 0.000 |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 523.100 |
| Average LLM Call Count | 3.350 |
| Avg Bridge Judge Confidence | 0.904 |
| Total Latency P50 ms | 17094.474 |
| Total Latency P95 ms | 23998.282 |

## Leakage Levels

```json
{
  "0": 18,
  "1": 1,
  "unknown": 1
}
```

## Safe Actions

```json
{
  "pass": 19,
  "unknown": 1
}
```

## Stage Errors

```json
{
  "leakage_judge": 1
}
```

## Groups

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.350 |
| Total Latency P50 ms | 17094.474 |

