# Research Schema v1

## Purpose

`research_schema_v1` defines the turn-level data shape for **CP-MissingBridgeBench**: a benchmark and evaluation dataset for bridge-aware competitive-programming tutoring.

The goal is to make the paper variables explicit before changing the AIChat runtime. This schema separates:

- what the student said;
- what the coach thinks the missing bridge is;
- what the system predicted;
- what the system answered;
- whether the answer was useful, grounded, and non-leaking;
- whether the next student turn shows learning progress.

## Unit Of Analysis

The primary unit is one student turn plus the tutor response that follows it.

One record should correspond to:

```text
recent dialogue context
+ current student message
+ one system response
+ optional next student message for learning evidence
```

The coach should label the current student turn, not the whole session. The help level can rise or fall across turns.

## JSONL Row Shape

Each row follows [turn_annotation_schema_v1.json](turn_annotation_schema_v1.json).

Top-level fields:

| Field | Meaning | Paper use |
| --- | --- | --- |
| `schema_version` | Fixed value: `turn_annotation_v1`. | Allows later schema migration. |
| `turn` | Hashed session/student ids, problem id, turn index, and `baseline_group`. | Grouping, split construction, baseline comparison. |
| `context` | Current student message, recent dialogue, problem ref, optional code excerpt. | Input to Bridge Judge and human annotation. |
| `coach_label` | Human reference label. | Gold label for bridge diagnosis and allowed scaffold. |
| `system_prediction` | Bridge Judge or current system prediction. | Model output to compare against coach labels. |
| `system_response` | Actual tutor reply and self-reported help level. | Response-quality and leakage evaluation. |
| `response_evaluation` | Rubric scores and leakage label. | Main offline outcome variables. |
| `next_turn_learning_evidence` | Optional next-turn progress scores. | Process-level learning signal. |
| `privacy` | De-identification metadata. | Controls export and public-release eligibility. |

## Core Variables

### `coach_label`

`coach_label` is the reference annotation. It should be produced by a competition coach, not by the same LLM being evaluated.

Required fields:

- `problem_solving_state`: where the student is blocked.
- `missing_bridge.family`: broad bridge family.
- `missing_bridge.subtype`: domain-specific subtype, such as `dp_state_design`, `check_condition`, or `tree_path_difference`.
- `missing_bridge.description`: one-sentence missing relation.
- `missing_bridge.evidence`: one or more quotes or observations from the turn.
- `help_seeking_type`: instrumental, executive, help avoidance, or unclear.
- `allowed_help_level_gold`: the maximum appropriate scaffold for this turn.
- `forbidden_content`: what the tutor must not directly complete.
- `confidence`: 1-5 annotator confidence.

### `system_prediction`

`system_prediction` stores the model or controller diagnosis before or alongside response generation.

For the current project, this can be filled by:

- `current_system`: rules plus existing pedagogical control fields;
- `pedagogical_judge_v2`: the existing Pedagogical Judge v2 fields, with missing bridge set to `unknown_bridge` when unavailable;
- `bridge_judge`: the future explicit Bridge Judge.

This field is what lets the paper answer:

```text
Does an explicit Bridge Judge match coach labels better than rules or generic LLM prompting?
```

### `response_evaluation`

`response_evaluation` records response quality, independent of whether the diagnosis was correct.

The six 0-2 scores are:

- bridge identification;
- groundedness;
- scaffold appropriateness;
- bridge leakage control;
- next-step clarity;
- single-focus coherence.

`leakage_label` uses:

- `no_leakage`;
- `minor_bridge_leakage`;
- `major_bridge_leakage`;
- `answer_leakage`.

This supports both total-score comparison and leakage-rate reporting.

### `next_turn_learning_evidence`

This field is optional in meaning but required in shape. If there is no next student reply, set:

```json
{
  "available": false,
  "student_uptake": null,
  "self_explanation": null,
  "transfer_signal": null,
  "error_correction": null,
  "independence": null,
  "notes": ""
}
```

When available, each score is 0-2. These scores are process-level signals, not proof of long-term contest ability.

## Baseline Groups

Use `baseline_group` to record which system produced the response:

| Group | Meaning |
| --- | --- |
| `generic_llm_tutor` | A plain LLM prompt such as "you are a programming tutor". |
| `socratic_prompt_tutor` | A prompt-only tutor that asks guiding questions and avoids direct answers. |
| `current_system` | Current AIChat rules, legacy pedagogical phase judge, prompt control, and hard gate. |
| `pedagogical_judge_v2` | Current system with Pedagogical Judge v2 enabled. |
| `bridge_judge` | Future system with explicit missing-bridge diagnosis. |
| `bridge_judge_with_leakage_judge` | Future full system with Bridge Judge plus independent leakage judge. |
| `human_coach` | Coach-written ideal response or upper-bound reference. |

## Relation To Current Implementation

The current implementation can already populate some fields:

- `turn`: from AIChat message/session metadata;
- `context`: from recent AIChat messages;
- `coach_label`: from the research annotation page;
- `system_response`: from AIChat reply logs;
- `system_prediction`: partially from rules and Pedagogical Judge v2 logs;
- `response_evaluation`: from coach review or Eval Judge;
- `next_turn_learning_evidence`: from the next student turn when present.

The current implementation cannot yet fully populate:

- explicit `missing_bridge` predictions from the live AIChat controller;
- bridge-specific `forbidden_content` generated before response;
- independent content-level leakage judgement.

These gaps define the next implementation stage.

## Recommended Dataset Splits

For the first paper iteration:

| Split | Suggested size | Use |
| --- | --- | --- |
| Seed calibration | 30-50 turns | Refine labels and coach instructions. |
| Development | 100-200 turns | Tune Bridge Judge prompt and leakage rubric. |
| Test | 100-200 turns | Report final baseline comparison. |
| Student pilot | 300-900 turns | Optional process-level usage evidence. |

Keep all turns from one session in the same split to avoid context leakage.

## Minimal Paper Claims Supported By This Schema

This schema supports conservative, testable claims:

1. Coaches can label turn-level missing bridges with an explicit taxonomy.
2. Bridge Judge predictions can be compared against coach labels.
3. Bridge-aware controllers can be compared against prompt-only or current-system baselines.
4. Leakage can be measured separately from general response quality.
5. Next-turn progress can be reported as a process signal.

It does not by itself prove long-term learning gains or contest-score improvement.
