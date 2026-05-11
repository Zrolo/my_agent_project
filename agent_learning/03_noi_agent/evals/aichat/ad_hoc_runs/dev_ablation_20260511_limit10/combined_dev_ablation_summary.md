# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 110 |
| Completed Count | 110 |
| Error Count | 0 |
| Student State Accuracy | 0.575 |
| Bridge Family Accuracy | 0.833 |
| Known Focus Accuracy | 0.467 |
| Known Focus Accuracy On Registered | 0.467 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.525 |
| Allowed Help Level Accuracy | 0.917 |
| Leakage Rate | 0.225 |
| Critical Bridge Leakage Rate | 0.075 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.200 |
| Block Rate | 0.000 |
| Repair Rate | 0.009 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | n/a |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 49.300 |
| Average LLM Call Count | 1.755 |
| Avg Bridge Judge Confidence | 0.902 |
| Total Latency P50 ms | 21934.524 |
| Total Latency P95 ms | 50102.215 |

## Leakage Levels

```json
{
  "0": 31,
  "2": 6,
  "3": 3
}
```

## Safe Actions

```json
{
  "pass": 32,
  "rewrite": 8
}
```

## Stage Errors

```json
{}
```

## Groups

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 41628.967 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.100 |
| Total Latency P50 ms | 34845.476 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | 0.900 |
| Critical Bridge Leakage Rate | 0.200 |
| Average LLM Call Count | 3.200 |
| Total Latency P50 ms | 41360.572 |

### tutor_mode=bridge_inspired_expert_decision_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 10331.701 |

### tutor_mode=codehelp_codeaid_no_direct_solution_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 10232.718 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 10515.896 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | 0.800 |
| Critical Bridge Leakage Rate | 0.100 |
| Average LLM Call Count | 3.000 |
| Total Latency P50 ms | 24993.466 |

### tutor_mode=enhanced_prompt_only|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 24351.504 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | 0.700 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 17662.978 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | 0.800 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 22654.532 |

### tutor_mode=socratic_no_answer_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 10 |
| Completed Count | 10 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 26330.951 |
