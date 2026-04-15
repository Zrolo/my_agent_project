# UI/UX Pro Max Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the student and teacher UI into a coherent education-first workspace with stronger layout hierarchy, richer color language, cleaner form alignment, and family-aware review presentation without changing core backend behavior.

**Architecture:** Keep one-page app architecture and existing API contracts. Concentrate changes in static shell/layout markup, CSS design tokens and layout systems, and light render ordering/label changes in frontend JS. Preserve current workflows while making the visual hierarchy intentional and easier to scan.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, existing FastAPI backend, Node test helpers, Python unittest regression.

---

### Task 1: Lock the new visual system and shell structure

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/index.html`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`

- [ ] Step 1: Rework the top-level app shell markup so login, student, and teacher sections use clearer workspace wrappers and title areas.
- [ ] Step 2: Add a consistent token layer in CSS for palette, typography, spacing, border, and shadow variables.
- [ ] Step 3: Replace remaining generic container/demo styling with a wider education-product shell and stronger masthead hierarchy.
- [ ] Step 4: Run `node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/review_family_ui.js /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/teacher_manual_review_ui.js`
- [ ] Step 5: Run `node --test /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`

### Task 2: Redesign the student workspace layout around function priority

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/index.html`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`

- [ ] Step 1: Reorganize student tab content so AI chat, check-in, and history feel like stages of one study workflow instead of isolated card piles.
- [ ] Step 2: Fix the check-in form alignment and field grouping so title/source/status/context/bottleneck/errors/code areas are visually aligned and grouped by task.
- [ ] Step 3: Reduce card overuse by turning form sections into editorial panels, split surfaces, and section dividers rather than many floating cards.
- [ ] Step 4: Keep current JS selectors working, adjusting markup only where `app.js` can still target the same IDs and tab content.
- [ ] Step 5: Run `node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

### Task 3: Rebuild the review workspace as the visual center

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/review_family_ui.js`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`

- [ ] Step 1: Restyle review output so the reading surface looks like a guided coaching board, not a generic archive card.
- [ ] Step 2: Strengthen family-aware visual differences between `failure_diagnosis` and `success_reflection`.
- [ ] Step 3: Make `next_step`, `transfer_signal`, and `key_bridge` emphasis match each family’s teaching intent.
- [ ] Step 4: Preserve current rendering order logic while improving block framing, labels, microcopy, and spacing.
- [ ] Step 5: Run `node --test /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`

### Task 4: Upgrade teacher analytics and manual review UI

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/index.html`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/teacher_manual_review_ui.js`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_stats_ui.mjs`

- [ ] Step 1: Redesign teacher stats and manual review surfaces so they read as evidence dashboards rather than plain admin cards.
- [ ] Step 2: Make breakdown cards, drill-down filters, and manual review forms feel visually connected.
- [ ] Step 3: Preserve existing teacher workflows and API-driven rendering while improving hierarchy, density, and readability.
- [ ] Step 4: Run `node --test /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_stats_ui.mjs`
- [ ] Step 5: Run `node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/teacher_manual_review_ui.js /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

### Task 5: Responsive polish, regression, and visual QA

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/index.html`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_stats_ui.mjs`
- Test: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py`

- [ ] Step 1: Clean up desktop/tablet/mobile layout breakpoints after the main redesign lands.
- [ ] Step 2: Ensure long Chinese text, dense form labels, stats cards, and review sections wrap cleanly.
- [ ] Step 3: Run `node --test /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_stats_ui.mjs`
- [ ] Step 4: Run `python3 -m unittest /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_async_api_unit.py /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_engine_messages_unit.py`
- [ ] Step 5: Run `bash /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh`
