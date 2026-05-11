# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 2 |
| Completed Count | 2 |
| Error Count | 0 |
| Student State Accuracy | n/a |
| Bridge Family Accuracy | 1.000 |
| Known Focus Accuracy | 1.000 |
| Known Focus Accuracy On Registered | 1.000 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | n/a |
| Allowed Help Level Accuracy | 1.000 |
| Leakage Rate | 0.500 |
| Critical Bridge Leakage Rate | 0.000 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.500 |
| Block Rate | 0.000 |
| Repair Rate | 0.500 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | 0.000 |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 412.000 |
| Average LLM Call Count | 2.500 |
| Avg Bridge Judge Confidence | n/a |
| Total Latency P50 ms | 17945.299 |
| Total Latency P95 ms | 21671.033 |

## Leakage Levels

```json
{
  "0": 1,
  "2": 1
}
```

## Safe Actions

```json
{
  "pass": 1,
  "rewrite": 1
}
```

## Stage Errors

```json
{}
```

## Groups

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.000 |
| Total Latency P50 ms | 21671.033 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 14219.564 |
