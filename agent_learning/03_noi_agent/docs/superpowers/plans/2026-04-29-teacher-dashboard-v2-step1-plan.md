# Teacher Dashboard v2 Step 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move teacher-facing navigation toward teaching actions by separating account management and system maintenance from learning monitoring.

**Architecture:** Keep the existing Vue/FastAPI API surface. Add two focused teacher pages: one for account lifecycle and one for advanced system maintenance. Slim `TeacherStudentsPage.vue` into a learning-monitoring table/observation page, while preserving existing account API calls in the new account page.

**Tech Stack:** Vue 3 single-file components, Vue Router, existing `frontend/src/services/api.js`, Node test runner, Vite.

---

### Task 1: Navigation And Routes

**Files:**
- Modify: `frontend/src/layouts/TeacherLayout.vue`
- Modify: `frontend/src/router/index.js`
- Test: `test_teacher_vue_ui.mjs`

- [ ] Add tests requiring teacher navigation to include `首页 / 学生 / 账号 / 复盘 / 复核 / 公告 / 反馈 / 高级`.
- [ ] Add tests requiring `/app/teacher/accounts` and `/app/teacher/advanced` routes.
- [ ] Update `TeacherLayout.vue` nav labels and hero labels.
- [ ] Update `frontend/src/router/index.js` with lazy imports and child routes for accounts and advanced.
- [ ] Run `node --test test_teacher_vue_ui.mjs`.

### Task 2: Account Management Page

**Files:**
- Create: `frontend/src/pages/teacher/TeacherAccountsPage.vue`
- Modify: `frontend/src/pages/teacher/TeacherStudentsPage.vue`
- Test: `test_teacher_vue_ui.mjs`

- [ ] Add tests requiring account creation/bulk creation/reset/enable-disable content to live in `TeacherAccountsPage.vue`.
- [ ] Add tests requiring `TeacherStudentsPage.vue` not to render account creation headings.
- [ ] Move existing account lifecycle UI and functions from `TeacherStudentsPage.vue` to `TeacherAccountsPage.vue`.
- [ ] Leave student learning observations in `TeacherStudentsPage.vue`.
- [ ] Run `node --test test_teacher_vue_ui.mjs`.

### Task 3: Advanced System Maintenance Page

**Files:**
- Create: `frontend/src/pages/teacher/TeacherAdvancedPage.vue`
- Modify: `frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Test: `test_teacher_vue_ui.mjs`

- [ ] Add tests requiring system-rule terms to live in `TeacherAdvancedPage.vue`.
- [ ] Add tests requiring `TeacherOverviewPage.vue` not to render rule draft/registry sections.
- [ ] Move rule draft, registry, resolver patch draft, and raw knowledge distribution sections from overview into advanced.
- [ ] Keep `TeacherOverviewPage.vue` focused on daily teaching signals and stable trends.
- [ ] Run `node --test test_teacher_vue_ui.mjs`.

### Task 4: Build Verification

**Files:**
- Generated: `static/dist/**`

- [ ] Run `npm run build`.
- [ ] Check route bundle generation succeeds.
- [ ] Report changed files and verification output.

