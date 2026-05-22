# CP-MissingBridgeBench v4 Dev20 Stabilization Audit

Date: 2026-05-22

Scope: v4 prompt stabilization on the 20-case dev set only.

This audit records dev-stage prompt stabilization for the bridge-aware DBox hybrid design. It is not a paper result, not a holdout result, not a 100-case result, and not online AIChat evidence.

## Boundary

- Did not modify dialogue-state v3 main experiment.
- Did not recompute dialogue-state v3 main tables.
- Did not add a dialogue-state v3 main condition.
- Did not modify online AIChat, active mode, production prompt, or student-visible replies.
- Did not generate 30-case holdout or 100-case final responses.
- Did not use raw student text, full student code, full observed AIChat responses, identity fields, hash salts, or reversible mappings.
- Used de-identified freeze/rubric summaries from the v2 100-case case-freeze CSV.

## Files

Implemented runner:

- `evals/aichat/run_cp_missingbridgebench_v4_dev20.py`

Prompt drafts created during stabilization:

- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_2_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_3_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_4_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_5_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_6_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_7_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_8_20260522.md`

Generated dev-run outputs are stored under `evals/aichat/ad_hoc_runs/` and should remain internal dev artifacts unless a separate release decision is made.

## Dev20 Design

The runner evaluates a four-stage offline chain:

1. Bridge Judge: drafts private missing-bridge target and tutor-visible boundary.
2. Tutor: generates a Chinese student-facing scaffold.
3. Leakage Guard: checks bridge leakage using coach-aligned labels.
4. Targeted Repair: runs only when Guard marks `needs_repair=yes`.

The chain is intentionally separate from online AIChat and from dialogue-state v3 result generation.

## Main Issue Found In v0.1

The first complete dev20 run was JSON-stable but not prompt-stable. Summary:

- Rows: 20
- Validation errors: 0
- Leakage labels: `no_leakage=19`, `answer_leakage=1`
- Repairs: 1

Manual spot check found a serious title-only context failure: the Tutor could invent problem-specific details that were not present in the public freeze packet, such as illustrative samples, coordinates, candidate state dimensions, data-structure cues, or object counts. This made v0.1 not freeze-ready.

## Stabilization Changes

v0.2 added anti-hallucination rules for unsupported specificity.

v0.3 tightened candidate-answer-shape leakage:

- no candidate state dimensions,
- no suggested structure choice,
- no invented examples,
- no fabricated coordinates/counterexamples/proof skeletons.

v0.4 added explicit `public_context_level`.

v0.5 tightened Bridge Judge, because unsafe specificity could enter through tutor-visible `allowed_support`.

v0.6 added title-only scaffold templates.

v0.7 made title-only mode near-template-based.

v0.8 added explicit `title_only_forbidden_terms`, including `比如`, `例如`, `插入`, `查询`, `合并`, `距离`, `点集`, `节点`, `字段`, `cnt`, `end`, `dp[`, `Trie`, and `线段树`.

## v0.8 Dev20 Run Summary

Run directory:

- `evals/aichat/ad_hoc_runs/cp_missingbridgebench_v4_dev20_20260522_v0_8/`

Summary:

- Rows: 20
- Unique cases: 20
- Provider: `deepseek_flash`
- Total LLM calls: 60
- Validation error cases: none
- Leakage labels: `no_leakage=20`
- `needs_repair`: `no=20`
- Final response source: `candidate=20`
- Vagueness self-check: `low=18`, `medium=2`
- Public reporting allowed: `no=20`

Forbidden-term check on final responses:

- Flagged rows: 0

## Interpretation

v0.8 is a dev stabilization candidate for safe title-only behavior. It is cleaner than v0.1--v0.7 because it no longer introduces unsupported examples or forbidden operation-specific terms in the final responses.

However, v0.8 is intentionally conservative and template-like. It should not be considered a final frozen prompt until a coach-style dev review checks whether the responses are still useful enough for students. In particular, repeated template replies may reduce case-specific helpfulness and student-ready quality.

## Next Gate

Before moving to 30-case holdout:

1. Run a coach-style dev review on the v0.8 20-case outputs.
2. Check whether the template-like responses are too weak or too generic.
3. If too weak, revise only on the 20-case dev set and rerun dev20.
4. Freeze the prompt only after the dev review passes.
5. Then select and run the 30-case holdout without further prompt tuning.

Do not tune on the 30-case holdout or the 100-case set.
