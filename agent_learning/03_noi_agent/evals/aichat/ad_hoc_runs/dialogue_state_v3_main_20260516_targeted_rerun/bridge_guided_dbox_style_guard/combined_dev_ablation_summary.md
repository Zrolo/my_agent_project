# Bridge Offline Eval Summary

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Error Count | 0 |
| Automatic Headline Ready | False |
| Dev Gate Review Required | True |
| Dev Gate Reasons | final_static_filled_trace_risk |
| Student State Accuracy | n/a |
| Bridge Family Accuracy | n/a |
| Known Focus Accuracy | n/a |
| Known Focus Accuracy On Registered | n/a |
| Unknown Focus Recall | n/a |
| Help Seeking Type Accuracy | n/a |
| Allowed Help Level Accuracy | n/a |
| Leakage Rate | 0.333 |
| Critical Bridge Leakage Rate | 0.000 |
| Answer Or Code Leakage Rate | 0.000 |
| Rewrite Rate | 0.333 |
| Block Rate | 0.000 |
| Repair Rate | 0.000 |
| Post Repair Check Rate | 0.000 |
| Repair Still Leaks Rate | n/a |
| Post Repair Rewrite Or Block Rate | n/a |
| Invalid Label Rate | n/a |
| Focus Out Of Registry Rate | n/a |
| Self Contradiction Rate | n/a |
| Average Prompt Tokens | 97.667 |
| Average LLM Call Count | 3.667 |
| Candidate Static Risk Rate | 0.333 |
| Candidate Static Answer Slot Risk Rate | 0.000 |
| Candidate Static Filled Trace Risk Rate | 0.333 |
| Candidate Static Worked Example Risk Rate | 0.000 |
| Final Static Risk Rate | 0.333 |
| Final Static Answer Slot Risk Rate | 0.000 |
| Final Static Filled Trace Risk Rate | 0.333 |
| Final Static Worked Example Risk Rate | 0.000 |
| Avg Bridge Judge Confidence | 0.850 |
| Total Latency P50 ms | 31836.043 |
| Total Latency P95 ms | 32105.571 |

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
{}
```

## Groups

### tutor_mode=bridge_guided_dbox_style_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| Metric | Value |
| --- | ---: |
| Case Count | 3 |
| Completed Count | 3 |
| Bridge Family Accuracy | n/a |
| Critical Bridge Leakage Rate | 0.000 |
| Average LLM Call Count | 3.667 |
| Automatic Headline Ready | False |
| Dev Gate Reasons | final_static_filled_trace_risk |
| Final Static Risk Rate | 0.333 |
| Final Static Answer Slot Risk Rate | 0.000 |
| Final Static Filled Trace Risk Rate | 0.333 |
| Final Static Worked Example Risk Rate | 0.000 |
| Total Latency P50 ms | 31836.043 |

