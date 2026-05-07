# AIChat Problem Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a lightweight "我已理解，结束本题" flow that generates a targeted understanding check, records pass/fail, and nudges later review.

**Architecture:** Reuse existing LLM understanding-check generator/grader. Add a small persistence table and two student API endpoints. Render the flow inline in the existing AIChat page beside the current clear-session action.

**Tech Stack:** FastAPI, SQLite, Vue 3, existing AIChat service wrappers, pytest/unittest, node:test static UI tests.

---

### Task 1: Persistence

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_problem_closure_unit.py`

- [ ] Write failing tests for creating, grading, and listing closure rows.
- [ ] Add `aichat_problem_closures` table and indexes in `init_db`.
- [ ] Add `create_aichat_problem_closure`, `grade_aichat_problem_closure`, and `get_aichat_problem_closure`.
- [ ] Verify the tests pass.

### Task 2: API

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_aichat_problem_closure_unit.py`

- [ ] Write failing endpoint tests for start and grade.
- [ ] Add request models and endpoints.
- [ ] Use recent AIChat messages, problem context, and student code when generating the quiz.
- [ ] On grade, award 2 points only when `can_review` is true.
- [ ] Verify the tests pass.

### Task 3: Frontend

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/pages/student/ChatPage.vue`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/services/api.js`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_student_entry_ui.mjs`

- [ ] Write failing static UI tests for the button, API calls, and inline result card.
- [ ] Add API service wrappers.
- [ ] Add button beside "清空对话".
- [ ] Render the closure quiz inline.
- [ ] Show pass/fail feedback, points, and next review message.
- [ ] Verify frontend static tests and build.
