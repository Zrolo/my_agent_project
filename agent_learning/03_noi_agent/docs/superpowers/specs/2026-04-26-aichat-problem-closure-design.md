# AIChat Problem Closure Design

## Goal

Give students a natural way to end an AIChat problem session without losing the learning trail: they click "我已理解，结束本题", answer one targeted LLM-generated check, and the system records whether this problem is ready for later review.

## Product Decision

AIChat remains the main learning surface. Checkin review is not forced after every problem.

The closure flow is lightweight:

1. Student clicks "我已理解，结束本题" near "清空对话".
2. Backend reads the current problem, code, and recent AIChat messages.
3. Backend generates one short open-ended understanding check using the existing AIChat understanding-check generator.
4. Student answers in an inline card.
5. Backend grades with the existing LLM grader and stores the result.
6. Passing gives a small score and a next-review timestamp; failing routes the student back to AIChat with a concrete focus.

## Data

Store one row per closure attempt in `aichat_problem_closures`.

Core fields:

- `student_id`
- `problem_id`
- `session_id`
- `problem_title`
- `status`: `quiz_ready`, `passed`, `partial`, `failed`, `unavailable`
- `question`
- `target_focus`
- `answer`
- `feedback`
- `followup`
- `points_awarded`
- `next_review_at`

v1 schedules only one reminder timestamp after passing. More advanced spaced review queues can build on the same rows later.

## Rules

- Passing requires `grade_understanding_check(...).can_review == true`.
- Passed attempts award `2` points.
- Passed attempts set `next_review_at` to three days later.
- Partial/failed attempts award `0` points and tell the student what to ask AIChat next.
- Opening the closure quiz is not a substitute for checkin review; it is a small "leave this problem responsibly" gate.

## Interfaces

`POST /api/chat/problem-closure/start`

Generates and stores a pending closure quiz.

`POST /api/chat/problem-closure/grade`

Grades the answer, updates the closure row, and returns status, feedback, points, and next review info.

## Frontend

AIChat adds a secondary button beside "清空对话": "我已理解，结束本题".

The quiz is shown inline in the AIChat area. If passed, the student sees points and the next review prompt. If not passed, the card asks them to continue with AIChat using the failed focus.
