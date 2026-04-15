# Open Bridge Observability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add P0 bridge route metadata for known, candidate, and open bridge cases without changing student-facing behavior.

**Architecture:** Wrap the existing `_detect_quiz_focus(...)` with `_resolve_bridge_decision(...)`. Store the resolver output as `reviews.bridge_route_meta`, expose it to teacher review samples, and render it as audit metadata only.

**Tech Stack:** Python, SQLite migrations, FastAPI response dictionaries, Vue teacher page, unittest, Node/Vite regression.

---

### Task 1: Bridge Decision Resolver

**Files:**
- Modify: `review_engine.py`
- Test: `test_review_engine_messages_unit.py`

- [x] Write tests for `_resolve_bridge_decision(...)` covering `known_bridge`, `candidate_bridge`, and `open_bridge`.
- [x] Implement a small resolver that returns stable focus plus observation-only metadata.
- [x] Verify existing `generate_bridge_quiz(...)` output remains unchanged.

### Task 2: Persistence

**Files:**
- Modify: `database.py`
- Modify: `api_server.py`
- Test: `test_review_async_api_unit.py`

- [x] Add `bridge_route_meta` migration to `reviews`.
- [x] Let `create_review(...)` accept a dict and store it as JSON.
- [x] Pass `review_result["bridge_route_meta"]` from review generation into persistence.
- [x] Return `bridge_route_meta` in review detail and teacher sample dictionaries.

### Task 3: Teacher Visibility

**Files:**
- Modify: `frontend/src/pages/teacher/TeacherReviewPage.vue`
- Test: `test_teacher_vue_ui.mjs`

- [x] Render stable focus, route confidence, candidate bridge, and conflict signals in teacher review samples.
- [x] Keep this teacher-only; do not show it in student pages.

### Task 4: Verification

**Commands:**
- [x] `python3 -m unittest test_review_engine_messages_unit.py`
- [x] `python3 -m unittest test_review_async_api_unit.py`
- [x] `node --test test_teacher_vue_ui.mjs`
- [x] `bash run_test.sh`

**Expected:** All commands pass. No student-facing route behavior changes.

### Task 5: P1 Teacher Aggregated Review

**Files:**
- Modify: `database.py`
- Modify: `api_server.py`
- Modify: `frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Modify: `frontend/src/pages/teacher/TeacherReviewPage.vue`
- Test: `test_review_async_api_unit.py`
- Test: `test_teacher_vue_ui.mjs`

- [x] Add `bridge_route_stats` to `/api/teacher/stats`.
- [x] Aggregate status, stable focus, candidate bridge, open bridge, and conflict signals.
- [x] Add a teacher overview card for route observability.
- [x] Add teacher review sample filters for all / candidate / open / known bridge cases.
- [x] Verify with targeted backend + teacher UI tests.
- [x] Verify with Vite production build.

### Task 6: P2 Promotion Suggestions

**Files:**
- Modify: `database.py`
- Modify: `api_server.py`
- Modify: `frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Test: `test_review_async_api_unit.py`
- Test: `test_teacher_vue_ui.mjs`

- [x] Add `bridge_route_promotion_suggestions` to `/api/teacher/stats`.
- [x] Generate suggestions only from candidate/open bridge observations.
- [x] Mark every suggestion with `decision_policy=teacher_review_required`.
- [x] Mark every suggestion with `auto_promote=false`.
- [x] Show suggestions in teacher overview as review-only cards.
- [x] Verify with targeted backend + teacher UI tests.
- [x] Verify with Vite production build.

### Task 7: P3 Rule Drafts

**Files:**
- Modify: `database.py`
- Modify: `frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Test: `test_review_async_api_unit.py`
- Test: `test_teacher_vue_ui.mjs`

- [x] Attach `rule_draft` to every bridge promotion suggestion.
- [x] Generate a deterministic draft filename from `bridge_id`.
- [x] Mark every draft with `integration_status=draft_only`.
- [x] Mark every draft with `auto_apply=false`.
- [x] Include trigger signals, conflict signals, and teacher acceptance checks.
- [x] Show draft filename and draft status in teacher overview.
- [x] Verify with targeted backend + teacher UI tests.
- [x] Verify with Vite production build.

### Task 8: P4 Teacher Decision And Draft Export

**Files:**
- Modify: `database.py`
- Modify: `api_server.py`
- Modify: `frontend/src/services/api.js`
- Modify: `frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Test: `test_review_async_api_unit.py`
- Test: `test_teacher_vue_ui.mjs`

- [x] Add `bridge_rule_draft_decisions` table.
- [x] Add markdown export endpoint for current rule drafts.
- [x] Add teacher decision endpoint for confirmed / rejected / needs_changes.
- [x] Persist teacher decisions as review records with `auto_promote=false`.
- [x] Add teacher overview actions for downloading and confirming drafts.
- [x] Verify with targeted backend + teacher UI tests.
- [x] Verify with Vite production build.

### Task 9: P5 Draft Decision History

**Files:**
- Modify: `database.py`
- Modify: `api_server.py`
- Modify: `frontend/src/services/api.js`
- Modify: `frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Test: `test_review_async_api_unit.py`
- Test: `test_teacher_vue_ui.mjs`

- [x] Add `list_bridge_rule_draft_decisions(...)`.
- [x] Add `/api/teacher/bridge-rule-drafts/decisions`.
- [x] Return current teacher's recent draft decisions.
- [x] Add teacher overview history card.
- [x] Refresh history after confirming a draft.
- [x] Verify with targeted backend + teacher UI tests.
- [x] Verify with Vite production build.

### Task 10: P6 Registry-Only Intake

**Files:**
- Modify: `database.py`
- Modify: `api_server.py`
- Modify: `frontend/src/services/api.js`
- Modify: `frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Test: `test_review_async_api_unit.py`
- Test: `test_teacher_vue_ui.mjs`

- [x] Add `bridge_registry_entries` table.
- [x] Add registry-only intake endpoint from confirmed draft decisions.
- [x] Add registry list endpoint.
- [x] Keep every registry entry at `registry_status=registry_only`.
- [x] Keep every registry entry at `resolver_enabled=false`.
- [x] Add teacher overview registry card and “register to registry” action.
- [x] Verify with targeted backend + teacher UI tests.
- [x] Verify with Vite production build.

### Task 11: P7 Resolver Patch Draft

**Files:**
- Modify: `database.py`
- Modify: `api_server.py`
- Modify: `frontend/src/services/api.js`
- Modify: `frontend/src/pages/teacher/TeacherOverviewPage.vue`
- Test: `test_review_async_api_unit.py`
- Test: `test_teacher_vue_ui.mjs`

- [x] Add resolver patch draft endpoint for registry entries.
- [x] Generate patch drafts that point to `review_engine.py`.
- [x] Mark every patch draft with `patch_status=patch_draft_only`.
- [x] Mark every patch draft with `auto_apply=false`.
- [x] Mark every patch draft with `resolver_enabled=false`.
- [x] Add teacher overview action and preview for resolver patch drafts.
- [x] Verify with targeted backend + teacher UI tests.
- [x] Verify with Vite production build.
