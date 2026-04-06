## Prompt Layout

This directory holds prompt templates for the quiz generation pipeline.

Goals:
- keep one LLM call per quiz generation
- separate stable rules from per-request context
- make focus-specific rules additive instead of editing one giant f-string

Current structure:
- `quiz-content/system.md`: fixed rules for structural quiz generation
- `quiz-content/user.md`: per-request context variables
- `snippets/`: reusable rule fragments

Current migration scope:
- structural quiz generation for:
  - `state_design`
  - `transition_design`
  - `check_condition`
  - `enumeration_order`
  - `greedy_basis`
  - `general_modeling`
  - `constraint_modeling`
  - `boundary_debug`
  - `method_selection`
  - `data_type`
  - `loop_boundary`
  - `recursion_structure`
  - `complexity_fit`

Expansion order:
1. Keep Batch A stable.
2. Add more focus snippets.
3. Only then expand Batch B focus detection.

Implementation note:
- Prompt responsibilities are split in files.
- Runtime still performs a single prompt assembly and a single LLM request.
