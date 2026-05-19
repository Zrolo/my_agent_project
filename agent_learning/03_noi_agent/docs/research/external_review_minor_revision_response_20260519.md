# External Review Minor-Revision Response 20260519

## Scope

This note records the response to the external web-AI review of the `f3f281b`
dialogue-state v3 evidence bundle. It is a packaging and reproducibility note,
not a new experiment.

## Reviewer Verdict

```text
needs minor revision
```

The reviewer found no blocking issue that overturns the dialogue-state v3
evidence package. The core `verify` and `reproduce` commands passed, and the
reproduced JSON matched the bundled output.

## Issue Addressed

The web reviewer could not run the focused unit tests in an environment without
the `openai` package. The failure came from an import-time dependency chain:

```text
test_llm_grader_calibration_pack_unit.py
-> evals/aichat/run_llm_grader_calibration.py
-> evals.review.run_review_case_kimi_cli
-> review_engine.py
-> openai.OpenAI
```

This dependency is only needed for live model calls, not for dry-run unit tests,
report verification, or table reproduction.

## Fix

- Moved live-backend imports in `evals/aichat/run_llm_grader_calibration.py` into
  the functions that actually call those backends.
- Added a local JSON-fence stripping helper so dry-run and parser tests do not
  import the Kimi review runner.
- Added `requirements-for-web-review.txt`, which states that the review
  reproduction commands require Python 3.10+ standard library only; `openai` is
  optional for live model calls outside the evidence bundle.

## Evidence Boundary

This change does not modify:

- main experiment data;
- human-review labels;
- paper-facing result numbers;
- prompts;
- online AIChat;
- experimental conditions.

## Remaining Interpretation Boundary

DeepSeek LLM grader calibration remains same-backend-coupled auxiliary
limitation evidence. GPT-5.4 subagent review remains method review /
reproducibility audit only, not an experimental calibration result.
