# Real-Student Pilot Validity Reporting Template v1

## 使用边界

本模板用于报告 20-30 个真实学生 dialogue-state cases 的 pilot validity check。报告只用于补充真实教育场景效度，不作为 CP-MissingBridgeBench 主结果，不评估长期学习效果，不新增 baseline，不修改 dialogue-state v3 evidence package。

## 1. Pilot Scope

请填写：

- Collection window:
- Case count planned: 20-30
- Case count collected:
- Case count privacy-passed:
- Case count excluded for privacy:
- Case count excluded for insufficient context:

固定边界句：

```text
This pilot validity check examines whether the CP-MissingBridgeBench bridge-family taxonomy and case-specific rubric can be applied to real student dialogue-state cases. It is not a main experiment, does not evaluate long-term learning outcomes, and does not modify the dialogue-state v3 evidence package.
```

## 2. Data Governance Summary

| item | report |
| --- | --- |
| direct identifiers removed | yes / no / needs review |
| real names stored | no |
| schools stored | no |
| phone numbers stored | no |
| account identifiers stored | no |
| code excerpts redacted | yes / no / not applicable |
| privacy review completed | yes / no |

Narrative summary:

```text
[Describe the redaction process, privacy review status, and exclusion reasons. Do not include direct identifiers.]
```

## 3. Case-Level Inventory Summary

| case_id | bridge_family | rubric_fit | taxonomy_fit | privacy_status | note |
| --- | --- | --- | --- | --- | --- |
| `pilot_case_001` |  |  |  |  |  |
| `pilot_case_002` |  |  |  |  |  |

Allowed values:

- `rubric_fit`: `fits_existing_fields` / `needs_minor_clarification` / `does_not_fit_current_rubric`
- `taxonomy_fit`: `fits_existing_family` / `fits_with_subtype_note` / `candidate_new_family_or_boundary`
- `privacy_status`: `passed` / `needs_redaction` / `excluded_privacy_risk`

## 4. Taxonomy Fit Summary

| bridge_family | case_count | fit_summary | examples_without_identifiers |
| --- | ---: | --- | --- |
| `state_representation_bridge` |  |  |  |
| `transition_recurrence_bridge` |  |  |  |
| `predicate_check_bridge` |  |  |  |
| `boundary_order_bridge` |  |  |  |
| `modeling_bridge` |  |  |  |
| `aggregation_contribution_bridge` |  |  |  |
| `data_structure_bridge` |  |  |  |
| `correctness_bridge` |  |  |  |
| `implementation_bridge` |  |  |  |
| `debugging_bridge` |  |  |  |
| `policy_bridge` |  |  |  |

Summary text:

```text
[State whether the existing bridge-family taxonomy was usable for the collected real-student cases. If not, describe the mismatch as a candidate validity concern, not as a change to the main experiment.]
```

## 5. Rubric Fit Summary

| rubric field | fit judgment | common issue | proposed reporting note |
| --- | --- | --- | --- |
| `coach_missing_bridge_instance` |  |  |  |
| `coach_forbidden_content` |  |  |  |
| `expected_next_student_action` |  |  |  |
| `observed_next_turn_progress` |  |  |  |

Summary text:

```text
[Describe whether case-specific rubric fields were sufficient for real student dialogue-state cases. Do not claim learning outcome effects.]
```

## 6. Observed Next-Turn Progress

This section is optional and only used when next-turn data are available.

| observed_next_turn_progress | count | interpretation boundary |
| --- | ---: | --- |
| `progress_observed` |  | rubric may have matched the student's next actionable step |
| `partial_progress_observed` |  | rubric may have been partly actionable |
| `no_progress_observed` |  | no next-turn progress observed; not a learning-outcome failure claim |
| `unclear` |  | cannot infer progress |
| `unavailable` |  | no next-turn data |

Boundary sentence:

```text
Observed next-turn progress is used only as a pilot validity signal for rubric fit. It is not a long-term learning outcome measure.
```

## 7. Validity Interpretation

Use conservative wording:

```text
The pilot provides ecological-validity support if real student dialogue-state cases can be mapped to existing bridge families and case-specific rubric fields without substantial redesign. Cases that do not fit are reported as taxonomy or rubric boundary cases and do not change the dialogue-state v3 main results.
```

## 8. Limitations

Include at least:

- The pilot contains 20-30 curated real-student dialogue-state cases, not a random sample of all CP tutoring interactions.
- The pilot does not evaluate long-term learning outcomes.
- The pilot does not compare tutor conditions or baselines.
- The pilot does not modify dialogue-state v3 main experiment results.
- The pilot depends on privacy-preserving redaction, which may remove some contextual detail.

## 9. Claim Gate For Reporting

| reporting claim | allowed? | note |
| --- | --- | --- |
| The taxonomy was usable for many / most pilot cases. | yes, if supported by counts | Report as pilot validity evidence only. |
| The rubric fields helped identify missing bridges in real dialogue-state cases. | yes, if supported by annotation notes | Do not claim learning gains. |
| The pilot proves CP-MissingBridgeBench covers real tutoring broadly. | no | Too broad. |
| The pilot validates online AIChat deployment. | no | Out of scope. |
| The pilot changes main result tables. | no | Forbidden. |
| The pilot introduces a new baseline or condition. | no | Forbidden. |

## 10. Appendix Boundary Sentence

Use this sentence if the pilot is included in an EAIT appendix:

```text
This real-student pilot is reported as an ecological-validity check for the benchmark construct. It is separate from the dialogue-state v3 main scaffold evaluation and does not change the main experimental conditions, numerical results, or evidence classes.
```
