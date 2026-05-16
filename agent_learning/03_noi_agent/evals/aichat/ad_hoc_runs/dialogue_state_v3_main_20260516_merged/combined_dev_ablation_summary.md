# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 350 |
| Completed Count | 350 |
| Error Count | 0 |
| Automatic Headline Ready | False |
| Dev Gate Review Required | True |
| Dev Gate Reasons | critical_bridge_leakage, repair_still_leaks, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Student State Accuracy | n/a |
| Bridge Family Accuracy | n/a |
| Known Focus Accuracy | n/a |
| Known Focus Accuracy On Registered | n/a |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | n/a |
| Allowed Help Level Accuracy | n/a |
| Leakage Rate | 0.345 |
| Critical Bridge Leakage Rate | 0.115 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.320 |
| Block Rate | 0.000 |
| Repair Rate | 0.037 |
| Post Repair Check Rate | 0.034 |
| Repair Still Leaks Rate | 0.083 |
| Post Repair Rewrite Or Block Rate | 0.167 |
| Invalid Label Rate | n/a |
| Focus Out Of Registry Rate | n/a |
| Self Contradiction Rate | n/a |
| Average Prompt Tokens | 101.720 |
| Average LLM Call Count | 2.294 |
| Candidate Static Risk Rate | 0.369 |
| Candidate Static Answer Slot Risk Rate | 0.094 |
| Candidate Static Filled Trace Risk Rate | 0.203 |
| Candidate Static Worked Example Risk Rate | 0.106 |
| Final Static Risk Rate | 0.366 |
| Final Static Answer Slot Risk Rate | 0.094 |
| Final Static Filled Trace Risk Rate | 0.200 |
| Final Static Worked Example Risk Rate | 0.106 |
| Avg Bridge Judge Confidence | 0.848 |
| Total Latency P50 ms | 19157.898 |
| Total Latency P95 ms | 42791.170 |

## Leakage Levels

```json
{
  "0": 131,
  "1": 16,
  "2": 30,
  "3": 23
}
```

## Safe Actions

```json
{
  "pass": 136,
  "rewrite": 64
}
```

## Stage Errors

```json
{}
```

## Groups

### tutor_mode=bridge_contract_compact|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | 0.080 |
| Average LLM Call Count | 3.540 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | critical_bridge_leakage, repair_still_leaks, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.420 |
| Final Static Answer Slot Risk Rate | 0.120 |
| Final Static Filled Trace Risk Rate | 0.240 |
| Final Static Worked Example Risk Rate | 0.080 |
| Total Latency P50 ms | 20850.630 |

### tutor_mode=bridge_contract_compact|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | 0.100 |
| Average LLM Call Count | 3.080 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | critical_bridge_leakage, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.360 |
| Final Static Answer Slot Risk Rate | 0.120 |
| Final Static Filled Trace Risk Rate | 0.200 |
| Final Static Worked Example Risk Rate | 0.080 |
| Total Latency P50 ms | 17349.247 |

### tutor_mode=bridge_guided_dbox_style_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | 0.160 |
| Average LLM Call Count | 3.180 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | critical_bridge_leakage, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.300 |
| Final Static Answer Slot Risk Rate | 0.080 |
| Final Static Filled Trace Risk Rate | 0.180 |
| Final Static Worked Example Risk Rate | 0.080 |
| Total Latency P50 ms | 25739.477 |

### tutor_mode=codehelp_codeaid_no_direct_solution_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.080 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.440 |
| Final Static Answer Slot Risk Rate | 0.060 |
| Final Static Filled Trace Risk Rate | 0.160 |
| Final Static Worked Example Risk Rate | 0.300 |
| Total Latency P50 ms | 8454.553 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.040 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.340 |
| Final Static Answer Slot Risk Rate | 0.120 |
| Final Static Filled Trace Risk Rate | 0.180 |
| Final Static Worked Example Risk Rate | 0.060 |
| Total Latency P50 ms | 11906.860 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | 0.120 |
| Average LLM Call Count | 3.140 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | critical_bridge_leakage, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.340 |
| Final Static Answer Slot Risk Rate | 0.080 |
| Final Static Filled Trace Risk Rate | 0.240 |
| Final Static Worked Example Risk Rate | 0.020 |
| Total Latency P50 ms | 24052.604 |

### tutor_mode=enhanced_prompt_only|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.000 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.360 |
| Final Static Answer Slot Risk Rate | 0.080 |
| Final Static Filled Trace Risk Rate | 0.200 |
| Final Static Worked Example Risk Rate | 0.120 |
| Total Latency P50 ms | 23636.265 |

