# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 11 |
| Completed Count | 9 |
| Error Count | 2 |
| Student State Accuracy | 1.000 |
| Bridge Family Accuracy | 0.800 |
| Known Focus Accuracy | 0.600 |
| Known Focus Accuracy On Registered | 0.600 |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | 0.000 |
| Allowed Help Level Accuracy | 1.000 |
| Leakage Rate | 0.333 |
| Critical Bridge Leakage Rate | 0.000 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.333 |
| Block Rate | 0.000 |
| Repair Rate | 0.111 |
| Invalid Label Rate | 0.000 |
| Focus Out Of Registry Rate | n/a |
| Self Contradiction Rate | 0.000 |
| Average Prompt Tokens | 46.000 |
| Average LLM Call Count | 1.778 |
| Avg Bridge Judge Confidence | 0.923 |
| Total Latency P50 ms | 55155.098 |
| Total Latency P95 ms | 244735.074 |

## Leakage Levels

```json
{
  "0": 2,
  "2": 1
}
```

## Safe Actions

```json
{
  "pass": 2,
  "rewrite": 1
}
```

## Stage Errors

```json
{
  "tutor": 2
}
```

## Groups

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 244735.074 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 4.000 |
| Total Latency P50 ms | 175391.471 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.000 |
| Total Latency P50 ms | 80142.793 |

### tutor_mode=bridge_inspired_expert_decision_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 36465.784 |

### tutor_mode=codehelp_codeaid_no_direct_solution_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 5713.800 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 0 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | n/a |
| Total Latency P50 ms | n/a |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 0 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | n/a |
| Total Latency P50 ms | n/a |

### tutor_mode=enhanced_prompt_only|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 28146.812 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | 0.000 |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 103744.661 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | 1.000 |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 2.000 |
| Total Latency P50 ms | 36867.193 |

### tutor_mode=socratic_no_answer_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 1 |
| Completed Count | 1 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Total Latency P50 ms | 55155.098 |


## Error Cases

- cp_bridge_001
- cp_bridge_001
