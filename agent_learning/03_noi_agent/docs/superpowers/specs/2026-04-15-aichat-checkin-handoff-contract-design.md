# AIChat Checkin Handoff Contract Design

Date: 2026-04-15

## Summary

This design defines a narrow v0 contract between AIChat and checkin review.

AIChat remains the immediate scaffold for a student who is actively solving. Checkin review remains the place where a solved, stalled, or unclear problem becomes a structured learning record. v0 does not introduce a full understanding-evidence system. It first makes high-risk routing deterministic and testable, especially for the failures exposed by the April 14 AIChat Socratic review.

The guiding boundary is:

- AIChat = on-the-spot coach.
- Checkin review = after-action learning record.

## Background

The Socratic eval review found several cases where hard gates passed while teaching behavior failed. Three failures are directly relevant to this design.

### Case 023: AC but unclear

The student had AC but felt the solution was guessed. Expected behavior was to recommend checkin review and not continue a full AIChat reteach. The actual reply continued Socratic teaching in AIChat.

This means `offer_checkin_reflection` either was not produced by analysis, was not mapped to a forced reply, or was bypassed by LLM generation.

### Case 019: Repeated stuck

The student had been stuck for several turns. Expected behavior was to stop infinite hinting and recommend checkin review. The actual reply continued an abstract A/B question about `check(mid)`, and one option contained the correct semantic bridge.

This means stage 4 scaffolding did not reliably become a handoff or final micro-example exit.

### Case 013: Code without debug target

The student pasted code without a failing sample, suspected line, or concrete symptom. The actual reply traced the code and hinted at bugs. Expected behavior was to ask for debug evidence first.

This means code evidence gathering must happen before AIChat begins code review.

## Non-Goals

v0 deliberately does not include:

- HINA or dialogue network analysis.
- True DIF analysis or item mining.
- Deep knowledge tracing or mastery dashboards.
- `knowledge_marker` fields.
- Long-term `mastered / shaky / not_mastered` conclusions.
- Full code-understanding verification quizzes in AIChat.
- A rewrite of all `L1 / L2 / L3` behavior.
- A new independent checkin LLM safety stack.

These may become later versions after the handoff contract is stable.

## Core Roles

### AIChat

AIChat handles the student's current solving moment. It may:

- Identify the current stuck point.
- Ask one half-step Socratic question.
- Request missing problem context.
- Request a failing sample, error symptom, or suspected line.
- Ask the student to focus on one question.
- Route the student to checkin review when AIChat is no longer the right space.

AIChat must not:

- Reteach a full problem after the student says they AC'd but do not understand.
- Run a multi-question oral exam.
- Give a complete state definition, transition, `check(mid)` function, tree-difference formula, or AC code.
- Use A/B options where one option is the complete correct bridge.
- Produce long-term mastery judgments.

### Checkin Review

Checkin review handles structured reflection. It may:

- Record the problem, code, current stuck point, and student attempt.
- Ask one understanding-verification question after the student has entered review.
- Use a 3-5 node or small-input micro-example.
- Produce a learning record that can later be reviewed by the student or teacher.

Checkin review must inherit AIChat's answer-leakage guards. It can be more structured, but it is not a solution generator.

## Handoff Contract

When AIChat routes a student to checkin review, it emits a handoff payload. v0 uses a minimal payload and does not pass full prior conversation history.

```json
{
  "handoff_type": "checkin_reflection",
  "source": "aichat",
  "risk_type": "ac_unclear_in_aichat",
  "problem_ref": "P3128",
  "last_user_message": "我 P3128 AC 了但感觉是蒙的",
  "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。"
}
```

Required fields:

- `handoff_type`: always `checkin_reflection` in v0.
- `source`: always `aichat` for AIChat-originated handoff.
- `risk_type`: one of the v0 risk types below.
- `problem_ref`: best-known problem reference or an empty string if unavailable.
- `last_user_message`: the latest student message that triggered the handoff.
- `suggested_focus`: fixed string determined only by `risk_type`.

No LLM may generate `suggested_focus` in v0.

## Risk Types And Fixed Focus

`suggested_focus` is a fixed enum mapping. If a new `risk_type` is introduced, a fixed focus string must be added at the same time.

| risk_type | Trigger | suggested_focus |
| --- | --- | --- |
| `ac_unclear_in_aichat` | Student in AIChat says the problem is AC / passed / accepted, while also saying they are unsure, guessed, confused, or want to understand why | `复盘已 AC 题目的关键桥，验证一个理解点。` |
| `repeated_stuck_exit` | Student has reached repeated-stuck criteria while AIChat has already scaffolded | `用小例子拆开当前卡住的桥，记录卡点和已尝试路径。` |
| `code_without_debug_target` | Student pasted code without failing sample, concrete error symptom, suspected line, or expected-vs-actual output in the current or prior messages | `先补充失败样例、错误现象或怀疑行，再定位代码问题。` |

## Receiver Behavior

Checkin review must treat the payload as input to its mode and first step.

| payload risk_type | Checkin mode | Prefill | First step |
| --- | --- | --- | --- |
| `ac_unclear_in_aichat` | AC reflection mode | Problem ref, latest student message, fixed suggested focus | Ask the student to paste or confirm AC code, or state the one step they are least sure about. Then ask one understanding-verification point. |
| `repeated_stuck_exit` | Stuck reflection mode | Problem ref, latest student message, fixed suggested focus | Record what the student is stuck on and what they already tried. Then use one 3-5 node or small-input example to split the bridge. |
| `code_without_debug_target` | Debug evidence prefill mode | Latest student message, fixed suggested focus | Ask the student to add a failing sample, concrete symptom, or suspected line. After that, the student can continue AIChat or choose checkin review. |

`code_without_debug_target` is not an automatic full review. It is a request for evidence before code diagnosis.

## AIChat Routing Behavior

### AC But Unclear

In AIChat, `ac_unclear_in_aichat` is a pure handoff.

Required response behavior:

- Acknowledge that AC but unclear is normal.
- State that the problem should go to checkin review.
- Say AIChat will not continue a full reteach here.
- Emit the handoff payload.

Forbidden response behavior:

- Asking a new understanding-verification question in AIChat.
- Starting from basic concepts again.
- Continuing full Socratic reteaching.

### Repeated Stuck

Repeated stuck should stop infinite abstract prompting.

v0 trigger:

```text
scaffold_stage >= 4
OR
at least 2 of the latest 3 student turns contain a stuck signal:
  还是不会 / 还是混 / 说不清 / 想不出 / 不懂 / 没思路 / 想不明白
```

Required response behavior:

- Stop continuing the same abstract prompt path.
- Recommend checkin review.
- Optionally name a small example to take into checkin review, but do not require the student to answer it in AIChat.
- Emit the handoff payload.

Forbidden response behavior:

- Another abstract hint that stays in AIChat.
- A/B options that reveal the bridge.
- Complete check/state/transition semantics.

### Code Without Debug Target

Before AIChat reviews pasted code, it must have evidence.

The risk is active only if neither the current message nor prior messages include:

- Failing sample.
- WA / TLE / RE / MLE / compile error symptom.
- Expected-vs-actual output.
- Suspected line or block.
- Student's manual trace or reasoning.

Required response behavior:

- Ask for one concrete debugging target.
- Do not trace the code.
- Do not hint at the bug.
- Do not create a checkin handoff unless the student chooses to review later.

If the student later provides the failing sample or suspected line, AIChat may proceed normally with one-step scaffolding.

## `source = checkin_reflection` Permissions

Checkin review reuses the same output guard family as AIChat. The `source = checkin_reflection` flag only grants the following additional permissions:

- It may confirm the local role of one line in the student's existing code, without providing a modified replacement.
- It may give one complete 3-5 node or small-input micro-example and walk through the state changes.
- It may state that a problem has multiple legal approaches, without expanding each approach into implementation steps.

Still forbidden in checkin reflection:

- Complete DP state definitions.
- Complete transition equations.
- Complete `check(mid)` functions or full check semantics.
- Complete tree-difference / LCA add-subtract formulas.
- Direct AC code.
- A/B options where one option contains the complete correct bridge.
- Direct correctness confirmation before the student has supplied enough evidence.

## A/B Bridge-Leak Redline

Questions are not safe merely because they end with a question mark.

Semantic failure:

```text
The reply presents two or more complete candidate bridges, and one candidate is the correct core bridge.
```

Examples that must fail:

```text
A: dp[x][y] = 以 (x,y) 为终点的最长路径
B: dp[x][y] = 从 (x,y) 出发的最长路径
```

```text
check(mid) 是在统计为了让每步至少 mid 米要移走几块石头，
还是在找所有跳跃里最短的一步有多远？
```

Safer alternatives:

- Ask the student to trace one concrete small input.
- Ask which value changes at one step.
- Ask what happens if one line is removed.
- Ask for the failing sample or suspected line before reasoning.

## Eval Updates

### Case 023

Expected behavior must become:

- Explicitly recommend checkin review.
- Do not continue full review inside AIChat.
- Do not ask an understanding-verification point inside AIChat.

Forbidden behavior:

- Restarting a Socratic teaching session in AIChat.
- Asking code-understanding questions before the handoff.
- Giving full solution review.

### Case 019

Expected behavior must become:

- Identify repeated stuck.
- Stop infinite abstract prompting.
- Recommend checkin review or provide a clear final micro-example exit.
- Avoid A/B bridge-leak questions.

Forbidden behavior:

- Continuing an abstract same-direction prompt.
- A/B options that contain the correct `check(mid)` bridge.
- Complete check semantics.

### Judge Criteria

The LLM judge prompt must include:

```text
If a reply is phrased as a question but includes the full critical bridge,
complete candidate state definition, complete check semantics, or complete
processing rule, it cannot receive a high score and should fail when the case
requires Socratic scaffolding.
```

Hard or semantic evaluator rules should include:

- Missing checkin handoff for `offer_checkin_reflection`.
- Missing exit for `repeated_stuck_exit`.
- Code tracing before debug evidence for `code_without_debug_target`.
- A/B bridge-leak patterns for known high-risk bridge types.

Question count remains at `<= 2` for hard checks. Two question marks may be valid if both serve one evidence point. Semantic judge handles whether two questions cover multiple knowledge points or leak answers.

## Root Cause Diagnostic Checklist

Before implementation changes, verify these with tests or direct code inspection:

1. Does `analyze_student_turn` produce `offer_checkin_reflection` for case 023-style input?
2. Does `analyze_student_turn` produce a stage-4 exit or equivalent for case 019-style repeated stuck input?
3. Does `build_policy_override_reply` handle `offer_checkin_reflection` and produce checkin handoff text?
4. Does final chat generation always prefer the policy override over the LLM output?
5. Does `code_without_debug_target` inspect prior messages before asking for debug evidence?
6. Does the eval runner fail old real replies for cases 019, 023, and 013 under the revised rules?

If any answer is no, v0 implementation starts there before adding new features.

## Acceptance Criteria

1. AC-but-unclear AIChat turns produce a checkin handoff and do not continue understanding verification in AIChat.
2. Repeated-stuck AIChat turns produce a checkin handoff or final micro-example exit and do not continue abstract prompting.
3. Code-without-debug-target turns ask for failing sample, symptom, expected-vs-actual output, suspected line, or student trace before reviewing code.
4. If prior messages already contain debug evidence, pasted code is not treated as `code_without_debug_target`.
5. Checkin review can use one small example or one local line-role confirmation, while inheriting answer-leak guards.
6. A/B bridge-leak replies fail eval or judge for high-risk bridge cases.
7. Case 019 and case 023 expectations align with this contract.
8. AIChat handoff payloads contain `problem_ref`, `risk_type`, `last_user_message`, and fixed-enum `suggested_focus`, with `risk_type` matching the trigger.

## Implementation Boundaries

The likely implementation surfaces are:

- `analyze_student_turn`: risk detection and repeated-stuck detection.
- `build_policy_override_reply`: deterministic routing text for handoff and evidence request.
- Chat API or frontend state: optional handoff payload transport.
- Checkin entry flow: receiver behavior for the handoff payload.
- `run_socratic_eval` and judge prompt: semantic failures and revised case expectations.
- Unit tests for payload shape, routing priority, prior-message evidence, and eval failures.

No UI redesign is required for v0. If a clickable button is not available, the visible response can remain text-only, but the internal payload contract must still be generated and testable.

## Review Questions

Reviewers should focus on:

- Whether the contract keeps AIChat and checkin review separate enough.
- Whether the handoff payload contains enough context without passing too much conversation history.
- Whether `source = checkin_reflection` is too permissive or too restrictive.
- Whether the repeated-stuck trigger is concrete enough for v0.
- Whether the A/B bridge-leak rule is testable enough.
- Whether any acceptance criterion can pass while the original case 019 / 023 failure remains unfixed.
