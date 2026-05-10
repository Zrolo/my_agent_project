# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 20 |
| Completed Count | 20 |
| Error Count | 0 |
| Student State Accuracy | 0.600 |
| Bridge Family Accuracy | 0.900 |
| Known Focus Accuracy | 0.800 |
| Known Focus Accuracy On Registered | 0.800 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.550 |
| Allowed Help Level Accuracy | 0.950 |
| Leakage Rate | 0.300 |
| Critical Bridge Leakage Rate | 0.050 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.200 |
| Block Rate | 0.000 |
| Repair Rate | 0.200 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | 0.000 |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 522.000 |
| Average LLM Call Count | 3.600 |
| Avg Bridge Judge Confidence | 0.894 |
| Total Latency P50 ms | 18169.894 |
| Total Latency P95 ms | 29043.382 |

## Leakage Levels

```json
{
  "0": 14,
  "1": 2,
  "2": 3,
  "3": 1
}
```

## Safe Actions

```json
{
  "pass": 16,
  "rewrite": 4
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
| Case Count | 20 |
| Completed Count | 20 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.050 |
| Average LLM Call Count | 3.600 |
| Total Latency P50 ms | 18169.894 |

