# Knowledge Bailout Implementation Plan

## Summary

Implement a minimal student-first knowledge bailout path after final micro confirm failure.

## Implementation

- Extend learning flow constants and routing with:
  - `knowledge_bailout`
  - `knowledge_confirm`
- Add deterministic knowledge-card selection and deterministic knowledge-confirm generation in `review_engine.py`.
- On final micro confirm failure:
  - create one `knowledge_confirm` quiz
  - embed card data in quiz meta
  - return `next_state = knowledge_bailout`
- On knowledge confirm:
  - correct -> `resolved`
  - incorrect -> `needs_teacher_followup`
- Extend bridge-path inference with:
  - `knowledge_bailout_success`
  - `knowledge_bailout_failed`
- Update detail serialization and UI timeline rendering so the knowledge card appears below prior quiz history and survives refresh.
- Update teacher display text/badges to explain knowledge bailout outcomes.

## Tests

- API: failing final micro confirm returns `knowledge_bailout` and a `knowledge_confirm` quiz.
- API: knowledge confirm correct resolves to `assisted_success`.
- API: knowledge confirm incorrect resolves to `not_mastered`.
- Engine: knowledge card selection and confirm generation are deterministic for at least:
  - `state_design`
  - `method_selection / trie`
- Frontend: review detail timeline renders the knowledge card block and keeps earlier quiz history visible.
- Full regression: `run_test.sh`.

## Defaults

- Card content is prebuilt in code.
- Card content is middle-school-friendly.
- V1 stores bailout content in quiz meta instead of a dedicated table.
