# Research Annotation Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a teacher-only research annotation page that turns real AIChat conversations into expert-labeled BridgeBench data.

**Architecture:** Add a small backend research annotation surface over the existing `aichat_messages` table, with a new annotation table keyed by `sample_id`. The frontend adds a standalone teacher route that lists student turns, saves coach labels, and downloads JSONL/CSV exports.

**Tech Stack:** FastAPI, SQLite, Vue 3, existing teacher auth and API service patterns.

---

### Task 1: Backend Research Annotation API

**Files:**
- Modify: `database.py`
- Modify: `api_server.py`
- Test: `test_teacher_research_annotation_api_unit.py`

- [ ] Add failing tests for listing annotatable AIChat turns, saving one annotation, and exporting JSONL/CSV.
- [ ] Add `bridge_research_annotations` table and database helpers.
- [ ] Add teacher-only endpoints:
  - `GET /api/teacher/research/aichat-samples`
  - `POST /api/teacher/research/bridge-annotations`
  - `GET /api/teacher/research/bridge-annotations/export`
- [ ] Verify tests pass.

### Task 2: Frontend Research Annotation Page

**Files:**
- Modify: `frontend/src/services/api.js`
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/layouts/TeacherLayout.vue`
- Create: `frontend/src/pages/teacher/TeacherResearchAnnotationPage.vue`
- Test: `test_teacher_routes.mjs`

- [ ] Add route and navigation entry for `/app/teacher/research-annotation`.
- [ ] Add API client functions for sample list, annotation save, and export URLs.
- [ ] Build a standalone page with sample list, conversation view, label form, save button, and export buttons.
- [ ] Verify route tests and frontend build.

### Task 3: Verification

**Files:**
- Run existing targeted backend and frontend tests.
- Run compile/build checks that are already used by the repo.

- [ ] Run backend targeted tests.
- [ ] Run route tests.
- [ ] Run frontend build or available UI tests.
- [ ] Report exact files changed and verification evidence.
