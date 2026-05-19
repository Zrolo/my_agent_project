# Real-Student Online AIChat Pilot Reporting Template v1

## 使用边界

本模板用于报告 real-student online AIChat pilot validity check。报告只作为 Discussion / Appendix 的 ecological validity evidence，不作为 main result，不新增主实验，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，不把 pilot 写成 learning outcome study。

## 1. Scope Statement

固定边界句：

```text
This real-student online pilot examines whether CP-MissingBridgeBench cognitive bridge families, surface anchors, and case-specific rubric fields transfer to privacy-reviewed dialogue-state cases from our own AIChat / teaching system. It does not use public community or third-party platform data, does not compare the seven offline conditions, does not evaluate long-term learning outcomes, and is not used as a main result.
```

## 2. Pilot Case Summary

### 2.1 Data Funnel Table

| layer | reporting field | value | interpretation |
| --- | --- | ---: | --- |
| Layer 1: Online log corpus summary | raw AIChat message rows | 1156 | source-corpus background only |
| Layer 1: Online log corpus summary | sessions | 87 | source-corpus background only |
| Layer 1: Online log corpus summary | paired user-assistant turns | 578 | source-corpus background only |
| Layer 2: Substantial candidate-turn screening | substantial candidate turns | 137 | lightweight screening pool |
| Layer 2: Substantial candidate-turn screening | candidate sessions | 59 | lightweight screening pool |
| Layer 3: Deep pilot case annotation | selected pilot candidate cases | 30 | deep annotation sample after privacy review |
| Layer 3: Deep pilot case annotation | hashed students covered | 11 | coverage description only |
| Layer 3: Deep pilot case annotation | hashed problems covered | 15 | coverage description only |

Boundary statement:

```text
The 137 substantial candidate turns are a screening pool, not a deeply annotated sample. The 30 selected cases are a deep annotation sample, not the full online corpus. Neither layer is used as a main result or learning-outcome study.
```

### 2.2 Deep Pilot Case Summary

| reporting field | value |
| --- | --- |
| number of deep pilot cases | 30 |
| number of hashed students | 11 |
| number of hashed problems | 15 |
| source | our own online AIChat / teaching system |
| public community data used | no |
| third-party platform student data used | no |
| main-experiment conditions added | no |
| student-visible responses changed | no |

### 2.3 Candidate-Turn Screening Summary

Use this section for the 137 substantial candidate turns. This is a lightweight screening summary, not a full rubric annotation.

| screening field | count / summary | note |
| --- | ---: | --- |
| total substantial candidate turns | 137 | screening pool |
| candidate sessions | 59 | screening pool |
| context sufficient |  | lightweight screening only |
| context partial |  | lightweight screening only |
| context insufficient |  | lightweight screening only |
| context unclear |  | lightweight screening only |
| candidate for deep annotation: yes |  | selected using purposive coverage criteria |
| candidate for deep annotation: no |  | give exclusion reasons |

### 2.4 Stratified Purposive Sampling Explanation

Recommended wording:

```text
The 30 deep pilot cases were selected from the 137 substantial candidate turns using stratified purposive sampling. Selection aimed to cover bridge-family candidates, surface anchors, context-sufficiency levels, debugging / implementation / policy-risk situations, and different hashed students and problems. Cases were not selected by model performance or by whether they supported the paper's main claims.
```

## 3. Bridge Family Coverage

| cognitive bridge family | case_count | coverage note |
| --- | ---: | --- |
| `state_representation_bridge` |  |  |
| `transition_recurrence_bridge` |  |  |
| `predicate_check_bridge` |  |  |
| `boundary_order_bridge` |  |  |
| `modeling_bridge` |  |  |
| `aggregation_contribution_bridge` |  |  |
| `data_structure_bridge` |  |  |
| `correctness_bridge` |  |  |
| `implementation_bridge` |  |  |
| `debugging_bridge` |  |  |
| `policy_bridge` |  |  |

Narrative:

```text
[Summarize whether the existing cognitive bridge families covered the pilot cases. Do not claim full real-world coverage.]
```

## 4. Surface Anchor Coverage

| surface_anchor | case_count | note |
| --- | ---: | --- |
| DP state |  |  |
| recurrence source |  |  |
| binary-search check |  |  |
| boundary update order |  |  |
| tree-difference / contribution marking |  |  |
| data-structure operation |  |  |
| invariant proof |  |  |
| implementation boundary |  |  |
| debugging trace |  |  |
| direct-answer / code request |  |  |
| other |  |  |

## 5. Taxonomy Fit

| matches_existing_taxonomy | count | interpretation |
| --- | ---: | --- |
| `yes` |  | maps to existing taxonomy |
| `no` |  | candidate taxonomy boundary issue |
| `uncertain` |  | needs coach discussion or more context |

## 6. New Bridge Candidates

| candidate_id | case_count | candidate description | why existing taxonomy was insufficient | reporting boundary |
| --- | ---: | --- | --- | --- |
| `candidate_001` |  |  |  | validity discussion only; no main-experiment change |

Narrative:

```text
[Describe new bridge candidates conservatively. Do not modify the dialogue-state v3 taxonomy or main results in this report.]
```

## 7. Context Sufficiency And Clarification Need

| context_sufficiency | count | reporting note |
| --- | ---: | --- |
| `sufficient` |  | enough context for bridge/rubric annotation |
| `partial` |  | annotation possible with caution |
| `insufficient` |  | clarification would be required |
| `unclear` |  | cannot judge reliably |

Proportion requiring clarification:

```text
[number requiring clarification] / [number of pilot cases]
```

Boundary:

```text
Cases requiring clarification are interpreted as ecological-validity evidence about real dialogue ambiguity, not as model failure rates or learning outcome measures.
```

## 8. Current AIChat Critical-Bridge Leakage Notes

Optional reporting only. Use paraphrased / anonymized examples.

| case_id | leakage concern? | paraphrased example | boundary |
| --- | --- | --- | --- |
| `pilot_case_001` | yes / no / unclear |  | not a main-result label |

Do not publish full original student text, full AI response, full code, or identifiable problem/session details.

## 9. Observed Next-Turn Progress

| observed_next_turn_progress | count | interpretation boundary |
| --- | ---: | --- |
| `progress_observed` |  | possible rubric-fit signal |
| `partial_progress_observed` |  | partial rubric-fit signal |
| `no_progress_observed` |  | not a learning-outcome failure claim |
| `unavailable` |  | no next-turn data |
| `unclear` |  | cannot infer |

Boundary sentence:

```text
Observed next-turn progress is used only as a short-horizon validity signal for whether the expected next student action was observable. It is not a long-term learning outcome measure.
```

## 10. Examples After Paraphrase

| example_id | bridge_family | surface_anchor | paraphrased student issue | paraphrased rubric boundary |
| --- | --- | --- | --- | --- |
| `example_001` |  |  |  |  |

Rules:

- Use paraphrased / anonymized examples only.
- Do not include real names, school names, phone numbers, emails, accounts, exact timestamps, full student text, or full code.
- Do not include third-party community content.

## 11. Limitations

Include at least:

- The online log corpus summary reports 1156 message rows, 87 sessions, and 578 paired user-assistant turns.
- The 137 substantial candidate turns are a screening pool, not a deeply annotated sample.
- The 30 selected pilot cases are a deep annotation sample, not all online AIChat data.
- The deep pilot includes 30 curated real-student online AIChat cases, not a random sample of all CP tutoring interactions.
- The pilot uses only our own system data and excludes public communities and third-party platform data.
- The pilot is an ecological-validity check, not a main result.
- The pilot does not compare the 7 offline conditions.
- The pilot does not evaluate long-term learning outcomes.
- The pilot does not change student-visible responses.
- The pilot does not modify dialogue-state v3 main tables or evidence classes.

## 12. Claim Gate

| statement | allowed? | note |
| --- | --- | --- |
| The pilot provides ecological-validity evidence for taxonomy/rubric transfer. | yes, if supported by counts and examples | Discussion / Appendix only |
| The pilot reports bridge family coverage among collected real-student cases. | yes | Do not generalize to all CP tutoring |
| The pilot identifies candidate new bridge boundaries. | yes | Do not modify main taxonomy or main results here |
| The 137 candidate turns are a screening pool. | yes | Do not report as deep annotation |
| The 30 selected cases are a deep annotation sample. | yes | Do not report as all online data |
| The pilot is a main result. | no | Forbidden |
| The pilot compares the 7 conditions. | no | Forbidden |
| The pilot evaluates long-term learning effects. | no | Forbidden |
| The pilot changes dialogue-state v3 main results. | no | Forbidden |
| The pilot uses public community or third-party platform data. | no | Forbidden |

## 13. Closing Boundary Sentence

```text
The real-student online pilot is reported only as ecological-validity evidence. It is separate from the dialogue-state v3 main scaffold evaluation and does not add conditions, recompute tables, change evidence classes, deploy active mode, or alter student-visible responses.
```
