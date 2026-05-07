# Student Home Learning Records Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the student homepage a compact entry page, move problem completion recording into a learning-record workflow, and demote the unfinished knowledge补全 page from the primary navigation.

**Architecture:** Keep existing backend APIs and data structures. Change only student-facing Vue routes/layout/tests: homepage reads the same snapshot but displays fewer metrics and no form; checkin page becomes the student learning-record hub with tabs for 完成记录 / 打卡复盘 / 历史记录; knowledge补全 remains routable but is removed from the main nav.

**Tech Stack:** Vue 3, Vite, static Node UI tests, existing FastAPI endpoints.

---

### Task 1: Lock New Student Navigation And Homepage Contract

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_student_home_ui.mjs`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_student_entry_ui.mjs`

- [ ] **Step 1: Write failing tests**

Add expectations that:
- Home page does not render the completion form.
- Home page limits learning metrics to four items.
- Student navigation no longer exposes 知识补全 as a primary tab.
- Student navigation exposes 学习记录 instead of only 打卡复盘.
- Checkin page includes tabs for 完成记录 / 打卡复盘 / 历史记录.

- [ ] **Step 2: Run tests to verify red**

Run:

```bash
node --test test_student_home_ui.mjs test_student_entry_ui.mjs
```

Expected: FAIL because current homepage contains `submitCompletionRecord` and nav still includes `知识补全`.

### Task 2: Implement Compact Home And Learning Records Hub

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/pages/student/HomePage.vue`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/pages/student/CheckinPage.vue`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/frontend/src/layouts/StudentLayout.vue`

- [ ] **Step 1: Update navigation**

Change nav labels:
- Remove `知识补全` from `navItems`.
- Rename `打卡复盘` nav label to `学习记录`.

- [ ] **Step 2: Compact homepage**

Remove `createStudentProblemCompletion`, completion form state, and `submitCompletionRecord` from `HomePage.vue`. Render only the first four stats in a stable four-card grid and keep completion trend as a small summary/record evidence card instead of a form.

- [ ] **Step 3: Add learning-record tabs to CheckinPage**

Add local tab state with three tabs: `完成记录`, `打卡复盘`, `历史记录`. Move completion-record form behavior into the first tab using the existing `createStudentProblemCompletion` API. Keep the existing checkin form under `打卡复盘`, and add a link to `/app/archive` under `历史记录`.

### Task 3: Verify

**Files:**
- Test/build only.

- [ ] **Step 1: Run targeted UI tests**

```bash
node --test test_student_home_ui.mjs test_student_entry_ui.mjs test_student_routes.mjs
```

Expected: PASS.

- [ ] **Step 2: Run production build**

```bash
npm run build
```

Expected: PASS.
