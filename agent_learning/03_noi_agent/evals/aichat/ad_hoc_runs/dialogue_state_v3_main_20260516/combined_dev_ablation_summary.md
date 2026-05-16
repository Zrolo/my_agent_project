# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 350 |
| Completed Count | 340 |
| Error Count | 10 |
| Automatic Headline Ready | False |
| Dev Gate Review Required | True |
| Dev Gate Reasons | incomplete_or_error_rows, critical_bridge_leakage, repair_still_leaks, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Student State Accuracy | n/a |
| Bridge Family Accuracy | n/a |
| Known Focus Accuracy | n/a |
| Known Focus Accuracy On Registered | n/a |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | n/a |
| Allowed Help Level Accuracy | n/a |
| Leakage Rate | 0.349 |
| Critical Bridge Leakage Rate | 0.118 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.323 |
| Block Rate | 0.000 |
| Repair Rate | 0.038 |
| Post Repair Check Rate | 0.035 |
| Repair Still Leaks Rate | 0.083 |
| Post Repair Rewrite Or Block Rate | 0.167 |
| Invalid Label Rate | n/a |
| Focus Out Of Registry Rate | n/a |
| Self Contradiction Rate | n/a |
| Average Prompt Tokens | 101.903 |
| Average LLM Call Count | 2.294 |
| Candidate Static Risk Rate | 0.362 |
| Candidate Static Answer Slot Risk Rate | 0.091 |
| Candidate Static Filled Trace Risk Rate | 0.197 |
| Candidate Static Worked Example Risk Rate | 0.106 |
| Final Static Risk Rate | 0.359 |
| Final Static Answer Slot Risk Rate | 0.091 |
| Final Static Filled Trace Risk Rate | 0.194 |
| Final Static Worked Example Risk Rate | 0.106 |
| Avg Bridge Judge Confidence | 0.848 |
| Total Latency P50 ms | 19157.898 |
| Total Latency P95 ms | 42791.170 |

## Leakage Levels

```json
{
  "0": 127,
  "1": 16,
  "2": 29,
  "3": 23
}
```

## Safe Actions

```json
{
  "pass": 132,
  "rewrite": 63
}
```

## Stage Errors

```json
{
  "bridge_judge": 2,
  "tutor": 8
}
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
| Final Static Risk Rate | 0.400 |
| Final Static Answer Slot Risk Rate | 0.100 |
| Final Static Filled Trace Risk Rate | 0.240 |
| Final Static Worked Example Risk Rate | 0.080 |
| Total Latency P50 ms | 20850.630 |

### tutor_mode=bridge_contract_compact|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 48 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | 0.104 |
| Average LLM Call Count | 3.083 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | incomplete_or_error_rows, critical_bridge_leakage, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.354 |
| Final Static Answer Slot Risk Rate | 0.125 |
| Final Static Filled Trace Risk Rate | 0.188 |
| Final Static Worked Example Risk Rate | 0.083 |
| Total Latency P50 ms | 17349.247 |

### tutor_mode=bridge_guided_dbox_style_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 47 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | 0.170 |
| Average LLM Call Count | 3.149 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | incomplete_or_error_rows, critical_bridge_leakage, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.298 |
| Final Static Answer Slot Risk Rate | 0.085 |
| Final Static Filled Trace Risk Rate | 0.170 |
| Final Static Worked Example Risk Rate | 0.085 |
| Total Latency P50 ms | 24263.981 |

### tutor_mode=codehelp_codeaid_no_direct_solution_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 45 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | n/a |
| Average LLM Call Count | 1.067 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | incomplete_or_error_rows, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.422 |
| Final Static Answer Slot Risk Rate | 0.044 |
| Final Static Filled Trace Risk Rate | 0.133 |
| Final Static Worked Example Risk Rate | 0.311 |
| Total Latency P50 ms | 8572.612 |

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


## Error Cases

- dialogue_v3_012_predicate_check_semantics
- dialogue_v3_013_predicate_check_semantics
- dialogue_v3_017_boundary_update_order
- dialogue_v3_020_boundary_update_order
- dialogue_v3_029_aggregation_contribution_summary
- dialogue_v3_011_transition_recurrence_source
- dialogue_v3_018_boundary_update_order
- dialogue_v3_043_implementation_boundary
- dialogue_v3_025_modeling_object_relation
- dialogue_v3_032_data_structure_operation_semantics
