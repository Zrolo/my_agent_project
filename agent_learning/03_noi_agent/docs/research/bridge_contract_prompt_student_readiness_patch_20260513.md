# Bridge Contract Prompt Student-Readiness Patch (2026-05-13)

## Background

The `dev10` human blind review suggested that `bridge_contract_guard` controlled major leakage relatively well, but its student-ready rate and conversational naturalness were not stable enough. In particular, representation/state turns sometimes explained the target state semantics too directly, or produced rule-list-like hints instead of a teacher-like continuation of the current dialogue.

This patch only affects the offline research Bridge Contract Tutor prompt. It does not change the online student AIChat, the evaluation architecture, or any formal experimental claim.

## Change

Two constraint groups were added to the Bridge Contract Tutor system prompt in `evals/aichat/run_bridge_offline_eval.py`:

1. Student-visible response shape:
   - one sentence that connects to the student's current wording;
   - one small observation task;
   - one short-answer question;
   - do not respond like a rule checklist;
   - do not ask multiple follow-up questions in a row.

2. First-level hinting for representation/state bridges:
   - do not directly provide the full semantics, target quantity, optimality meaning, or feasibility meaning carried by a representation object;
   - do not pre-answer what the represented object means;
   - first ask which input factors, boundary objects, historical choices, or constraints affect later decisions;
   - ask the student to list factors that affect later decisions.

## Scope

This is not an expansion of algorithm-specific special cases. It abstracts representation/state bridge tutoring into a general instructional move: ask the student to observe which factors affect later decisions before forming the representation semantics. Concrete failure examples should be kept in regression cases, rubric examples, or error analysis, not copied into the generation prompt. Before the formal held-out study, this prompt must still be frozen and validated through coach blind review.

## Verification

New unit tests added and passed:

- `test_bridge_contract_tutor_prompt_blocks_state_definition_leakage`
- `test_bridge_contract_tutor_prompt_requires_teacher_like_response_shape`

Related regression tests passed:

```text
python3 -m unittest test_bridge_offline_eval_runner_unit.py test_dbox_inspired_decomposition_tutor_unit.py test_literature_baseline_tutors_unit.py
```

Result: `Ran 67 tests ... OK`.
