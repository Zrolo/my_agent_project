# Teacher Learning Radar V2 Step 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add student completion records and surface them as teacher-facing learning evidence without turning them into a ranking metric.

**Architecture:** Store completion records in SQLite with a small API surface. Student pages can create and view the current student's records. Teacher stats and student pages consume aggregated rolling-window summaries and attention items.

**Tech Stack:** FastAPI, SQLite, Vue 3, node:test, Python unittest.

---

### Task 1: Student Completion Record Storage And API

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_student_completion_unit.py`

- [ ] Write failing tests for creating a completion record and reading rolling summaries.
- [ ] Add `student_problem_completions` table and helper functions.
- [ ] Add `POST /api/student/problem-completions` and include completion stats in `/api/student/home`.
- [ ] Verify unit tests pass.

### Task 2: Student UI Entry

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/services/api.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/pages/student/HomePage.vue`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/pages/student/ChatPage.vue`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_student_home_ui.mjs`

- [ ] Write failing static UI tests for “记录这题完成情况” and no leaderboard language.
- [ ] Add API service function.
- [ ] Add a compact completion record panel on student home and an entry near AIChat current problem actions.
- [ ] Verify UI tests pass.

### Task 3: Teacher Radar Surface

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/database.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/api_server.py`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/pages/teacher/TeacherStudentsPage.vue`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_vue_ui.mjs`

- [ ] Write failing tests for “今天先看谁”, “数据不足”, “支架撤离趋势”, and teacher-facing student identity.
- [ ] Add summary fields to teacher stats.
- [ ] Update teacher overview and student pages with actionable labels and evidence wording.
- [ ] Verify teacher UI tests pass.

### Task 4: Build Verification

**Files:**
- No new files.

- [ ] Run `python3 -m unittest test_student_completion_unit test_student_home_unit -v`.
- [ ] Run `node --test test_student_home_ui.mjs test_teacher_vue_ui.mjs`.
- [ ] Run `npm run build`.
- [ ] Record any skipped or failed checks in the final response.

