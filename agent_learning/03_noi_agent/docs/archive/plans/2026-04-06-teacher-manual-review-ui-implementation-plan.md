# Teacher Manual Review UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a minimal teacher-facing manual review tab that loads review samples, shows the sample details plus four review fields, and submits manual judgment back to the teacher review API.

**Architecture:** Extend the existing teacher tab strip with one new tab and keep the feature self-contained in `static/app.js`, `static/index.html`, and `static/style.css`. The new tab will use the existing authenticated `apiFetch()` helper, render a compact list of review samples from `GET /api/teacher/review-samples`, and render a simple form per selected sample that posts the three enum fields plus notes to `POST /api/teacher/reviews/{review_id}/manual-review`.

**Tech Stack:** Plain browser JavaScript, server-rendered HTML, CSS, and the existing Node test harness for frontend helper checks.

---

### Task 1: Add the teacher tab shell

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/index.html`

- [ ] **Step 1: Add the new tab button and tab content containers**

```html
<button class="tab-btn" data-tab="manual-review-tab">人工复核</button>

<div id="manual-review-tab" class="tab-content hidden">
    <div id="teacher-manual-review-panel"></div>
</div>
```

- [ ] **Step 2: Keep the markup minimal and aligned with the existing teacher sections**

```html
<!-- Place the new tab next to the existing teacher tabs -->
```

- [ ] **Step 3: Verify the HTML still loads and the teacher tab strip has one more tab**

Run: `node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
Expected: no syntax errors from the HTML-linked script.

### Task 2: Render and submit manual reviews

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

- [ ] **Step 1: Add small helper functions for sample rendering and payload normalization**

```javascript
function manualReviewSelectOptions(name, value) {
    const options = {
        mode_correct: ['correct', 'incorrect', 'unsure'],
        review_grounded: ['grounded', 'mixed', 'vague'],
        student_can_move_next: ['yes', 'no', 'unsure'],
    };
    const labels = {
        mode_correct: { correct: 'correct', incorrect: 'incorrect', unsure: 'unsure' },
        review_grounded: { grounded: 'grounded', mixed: 'mixed', vague: 'vague' },
        student_can_move_next: { yes: 'yes', no: 'no', unsure: 'unsure' },
    };
    return options[name].map((option) => `
        <option value="${option}" ${option === value ? 'selected' : ''}>${labels[name][option]}</option>
    `).join('');
}
```

- [ ] **Step 2: Add a loader for `GET /api/teacher/review-samples`**

```javascript
async function loadTeacherReviewSamples() {
    const panel = document.getElementById('teacher-manual-review-panel');
    if (!panel) return;
    panel.innerHTML = '<p>加载中...</p>';
    const res = await apiFetch(`${API_BASE}/api/teacher/review-samples`);
    const data = await res.json();
    panel.innerHTML = renderTeacherReviewSamplesPanel(data.samples || []);
}
```

- [ ] **Step 3: Render one sample card with basic info, four review fields, and the manual review form**

```javascript
function renderTeacherReviewSampleCard(sample) {
    return `
        <article class="teacher-review-sample-card">
            <h3>${escapeHtml(sample.problem_title || '未命名题目')}</h3>
            <p class="teacher-review-meta">review_id: ${escapeHtml(sample.review_id)} | checkin_id: ${escapeHtml(sample.checkin_id)} | student_id: ${escapeHtml(sample.student_id)}</p>
            <div class="teacher-review-columns">
                <div>
                    <strong>四段 review</strong>
                    <div class="teacher-review-quad">
                        <div><span>main_block</span><p>${escapeHtml(sample.main_block || '')}</p></div>
                        <div><span>key_bridge</span><p>${escapeHtml(sample.key_bridge || '')}</p></div>
                        <div><span>next_step</span><p>${escapeHtml(sample.next_step || '')}</p></div>
                        <div><span>transfer_signal</span><p>${escapeHtml(sample.transfer_signal || '')}</p></div>
                    </div>
                </div>
                <form class="teacher-manual-review-form" data-review-id="${escapeHtml(sample.review_id)}">
                    <label>mode_correct<select name="mode_correct">${manualReviewSelectOptions('mode_correct', sample.manual_review?.mode_correct || 'unsure')}</select></label>
                    <label>review_grounded<select name="review_grounded">${manualReviewSelectOptions('review_grounded', sample.manual_review?.review_grounded || 'mixed')}</select></label>
                    <label>student_can_move_next<select name="student_can_move_next">${manualReviewSelectOptions('student_can_move_next', sample.manual_review?.student_can_move_next || 'unsure')}</select></label>
                    <label>notes<textarea name="notes" rows="3">${escapeHtml(sample.manual_review?.notes || '')}</textarea></label>
                    <button type="submit">提交复核</button>
                </form>
            </div>
        </article>
    `;
}
```

- [ ] **Step 4: Wire form submission to `POST /api/teacher/reviews/{review_id}/manual-review`**

```javascript
async function submitTeacherManualReview(reviewId, form) {
    const payload = {
        mode_correct: form.elements.mode_correct.value,
        review_grounded: form.elements.review_grounded.value,
        student_can_move_next: form.elements.student_can_move_next.value,
        notes: form.elements.notes.value.trim(),
    };
    const res = await apiFetch(`${API_BASE}/api/teacher/reviews/${reviewId}/manual-review`, {
        method: 'POST',
        body: JSON.stringify(payload),
    });
    await res.json().catch(() => ({}));
}
```

- [ ] **Step 5: Hook the new tab into the existing teacher tab switcher and initialize the loader when the tab is shown**

```javascript
if (targetId === 'manual-review-tab') {
    loadTeacherReviewSamples();
}
```

- [ ] **Step 6: Verify the script still parses**

Run: `node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
Expected: no syntax errors.

### Task 3: Add minimal styling for the review panel

**Files:**
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/style.css`

- [ ] **Step 1: Add a compact card layout for review samples**

```css
.teacher-review-sample-card {
    background: #fff;
    border: 1px solid #e6d8b5;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
}
```

- [ ] **Step 2: Add a two-column layout for sample details and the form**

```css
.teacher-review-columns {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(320px, 1fr);
    gap: 16px;
}
```

- [ ] **Step 3: Add readable styles for the four review fields and the select/textarea controls**

```css
.teacher-review-quad > div {
    margin-top: 8px;
    padding: 10px;
    background: #faf7ef;
    border-radius: 6px;
}
```

- [ ] **Step 4: Make the form stack on narrow screens**

```css
@media (max-width: 860px) {
    .teacher-review-columns {
        grid-template-columns: 1fr;
    }
}
```

- [ ] **Step 5: Keep the styles consistent with the existing teacher tooling**

```css
/* Use the same warm teacher-panel treatment as the other teacher tools */
```

### Task 4: Add a frontend test for the manual-review form payload helper

**Files:**
- Create: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`
- Modify: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`

- [ ] **Step 1: Export a tiny pure helper from `static/app.js` for payload normalization**

```javascript
function buildTeacherManualReviewPayload(form) {
    return {
        mode_correct: form.elements.mode_correct.value,
        review_grounded: form.elements.review_grounded.value,
        student_can_move_next: form.elements.student_can_move_next.value,
        notes: form.elements.notes.value.trim(),
    };
}
```

- [ ] **Step 2: Add a Node test that proves the helper trims notes and preserves enum values**

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import ui from './static/app.js';

test('buildTeacherManualReviewPayload trims notes and keeps enum fields', () => {
    const payload = ui.buildTeacherManualReviewPayload({
        elements: {
            mode_correct: { value: 'correct' },
            review_grounded: { value: 'grounded' },
            student_can_move_next: { value: 'yes' },
            notes: { value: '  need a quick follow-up  ' },
        },
    });
    assert.deepEqual(payload, {
        mode_correct: 'correct',
        review_grounded: 'grounded',
        student_can_move_next: 'yes',
        notes: 'need a quick follow-up',
    });
});
```

- [ ] **Step 3: Run the test and confirm it passes**

Run: `node --test /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`
Expected: PASS

### Task 5: Final verification

**Files:**
- None

- [ ] **Step 1: Run syntax and test checks**

Run:
`node --check /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/static/app.js`
`node --test /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_review_family_ui.mjs`
`node --test /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/test_teacher_manual_review_ui.mjs`

Expected:
- `app.js` parses cleanly
- both Node tests pass

- [ ] **Step 2: Verify only frontend files changed**

Run: `git -C /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent status --short`
Expected: only `static/index.html`, `static/app.js`, `static/style.css`, and the new frontend test file are modified by this task

