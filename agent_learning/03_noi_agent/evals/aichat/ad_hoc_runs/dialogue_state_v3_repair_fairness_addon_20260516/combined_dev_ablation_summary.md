# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
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
| Leakage Rate | 0.420 |
| Critical Bridge Leakage Rate | 0.180 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.340 |
| Block Rate | 0.000 |
| Repair Rate | 0.340 |
| Post Repair Check Rate | 0.300 |
| Repair Still Leaks Rate | 0.067 |
| Post Repair Rewrite Or Block Rate | 0.267 |
| Invalid Label Rate | n/a |
| Focus Out Of Registry Rate | n/a |
| Self Contradiction Rate | n/a |
| Average Prompt Tokens | 101.720 |
| Average LLM Call Count | 3.820 |
| Candidate Static Risk Rate | 0.340 |
| Candidate Static Answer Slot Risk Rate | 0.040 |
| Candidate Static Filled Trace Risk Rate | 0.200 |
| Candidate Static Worked Example Risk Rate | 0.120 |
| Final Static Risk Rate | 0.380 |
| Final Static Answer Slot Risk Rate | 0.100 |
| Final Static Filled Trace Risk Rate | 0.220 |
| Final Static Worked Example Risk Rate | 0.120 |
| Avg Bridge Judge Confidence | 0.850 |
| Total Latency P50 ms | 29179.504 |
| Total Latency P95 ms | 72499.112 |

## Leakage Levels

```json
{
  "0": 29,
  "1": 7,
  "2": 5,
  "3": 9
}
```

## Safe Actions

```json
{
  "pass": 33,
  "rewrite": 17
}
```

## Stage Errors

```json
{}
```

## Groups

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 50 |
| Completed Count | 50 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | 0.180 |
| Average LLM Call Count | 3.820 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | critical_bridge_leakage, repair_still_leaks, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| Final Static Risk Rate | 0.380 |
| Final Static Answer Slot Risk Rate | 0.100 |
| Final Static Filled Trace Risk Rate | 0.220 |
| Final Static Worked Example Risk Rate | 0.120 |
| Total Latency P50 ms | 29179.504 |

