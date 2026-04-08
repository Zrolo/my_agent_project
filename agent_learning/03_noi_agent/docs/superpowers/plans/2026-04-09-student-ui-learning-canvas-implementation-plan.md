# Student UI Learning Canvas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the student-facing `打卡复盘` experience into a learning-canvas UI with a lecture-note tone, without changing any business logic, API contracts, or learning-state transitions.

**Architecture:** Keep the existing student information architecture and learning state machine intact, but reorganize the checkin page into a left context rail, center learning stage, and right review rail. Implement the redesign as a front-end-only refactor across the existing static HTML shell, CSS design system, and rendering helpers in `static/app.js`, with small helper expansions in `static/checkin_review_ui.js` and focused UI tests.

**Tech Stack:** Static HTML, vanilla JavaScript, CSS, existing `static/app.js` render pipeline, `static/checkin_review_ui.js`, `static/tailwind-ui.js`, Node test runner, existing `.mjs` UI unit tests

---

## File Structure

### Existing files to modify

- `agent_learning/03_noi_agent/static/index.html`
  - Student `打卡复盘` page shell
  - Current checkin form layout and right-column stats/tips cards
  - Needs new learning-canvas DOM structure and dedicated workspace slots

- `agent_learning/03_noi_agent/static/style.css`
  - Existing layout system, checkin page layout, review cards, quiz cards, knowledge bailout cards
  - Needs new page-level tokens, learning-canvas layout, lecture-note styling, responsive rules

- `agent_learning/03_noi_agent/static/app.js`
  - Current student render orchestration
  - Owns `renderCheckinEntryStage`, `renderActiveCheckinWorkspace`, `renderReviewHtml`, `renderLearningSection`, `renderQuizCard`, `renderKnowledgeBailoutCard`, `renderPendingReviewNotice`
  - Needs DOM-slot migration plus component-level UI rewrite without touching fetch/state logic

- `agent_learning/03_noi_agent/static/checkin_review_ui.js`
  - Small view-model helper module for headings / pills / compact sections
  - Good place to centralize new stage copy and lightweight layout metadata

- `agent_learning/03_noi_agent/static/tailwind-ui.js`
  - Contains useful modern card render patterns for review and quiz components
  - May be selectively borrowed from, but should not become the hard dependency for the whole page

- `agent_learning/03_noi_agent/test_checkin_review_ui.mjs`
  - Unit coverage for `checkin_review_ui.js`
  - Extend for new learning-canvas copy and helper behavior

- `agent_learning/03_noi_agent/test_review_family_ui.mjs`
  - Existing review wording / field ordering coverage
  - Keep passing to ensure the redesign does not break family-aware wording assumptions

### Optional existing files to inspect during implementation

- `agent_learning/03_noi_agent/static/review_family_ui.js`
  - Field labels and family-aware copy

- `agent_learning/03_noi_agent/static/test-tw.html`
  - Existing experiment surface for `TwUI` ideas

### No new production JS modules required

Avoid introducing a new student-page controller unless `static/app.js` becomes impossible to reason about. This redesign should fit in the current file layout by:

- moving page-shell markup in `index.html`
- adding presentational CSS in `style.css`
- incrementally refactoring render helpers in `app.js`
- keeping tiny copy/view helpers in `checkin_review_ui.js`

---

## Task 1: Lock The Learning-Canvas Shell

**Files:**
- Modify: `agent_learning/03_noi_agent/static/index.html`
- Modify: `agent_learning/03_noi_agent/static/checkin_review_ui.js`
- Test: `agent_learning/03_noi_agent/test_checkin_review_ui.mjs`

- [ ] **Step 1: Write the failing helper test for the new page-stage copy**

Add a new test to `agent_learning/03_noi_agent/test_checkin_review_ui.mjs`:

```js
test('reviewStageLead uses learning-canvas wording for the completed state', () => {
  assert.match(
    ui.reviewStageLead({ review_status: 'completed' }),
    /先读这次复盘，再继续做下面这一小步/,
  );
});
```

- [ ] **Step 2: Run the targeted UI helper test and verify it fails**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --test test_checkin_review_ui.mjs
```

Expected:

```text
not ok 6 - reviewStageLead uses learning-canvas wording for the completed state
```

- [ ] **Step 3: Update helper copy in `static/checkin_review_ui.js`**

Adjust `reviewStageLead` to use the learning-canvas wording and add one small helper for the entry-stage subtitle:

```js
function entryStageLead() {
    return '把这次卡住的地方记下来，我们会把它整理成一页可继续往下学的复盘讲义。';
}

function reviewStageLead(item = {}) {
    if (item.review_status === 'failed') {
        return '这次复盘暂时没有成功生成，你可以先看错误提示，稍后再回来继续。';
    }
    if (item.review_status !== 'completed') {
        return '复盘讲义正在生成中，生成完成后这里会自动更新。';
    }
    return '先读这次复盘，再继续做下面这一小步。';
}
```

- [ ] **Step 4: Update the test file to assert the new helper**

Keep the old assertions and extend them:

```js
test('entryStageLead describes the learning record flow', () => {
  assert.match(ui.entryStageLead(), /记下来/);
  assert.match(ui.entryStageLead(), /复盘讲义/);
});
```

- [ ] **Step 5: Run helper tests and verify they pass**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --test test_checkin_review_ui.mjs
```

Expected:

```text
# tests 6
# pass 6
ok
```

- [ ] **Step 6: Replace the old checkin page shell in `static/index.html`**

Rewrite the `#checkin-tab` body to remove the current right-column stats stack and add dedicated learning-canvas regions:

```html
<div class="checkin-canvas-page">
  <section class="learning-record-shell">
    <div class="learning-record-header">
      <div>
        <p class="learning-kicker">学习记录</p>
        <h2 class="learning-record-title">把这次卡住的地方记下来</h2>
        <p class="learning-record-subtitle" id="checkin-page-subtitle">
          把这道题当前卡住的位置写清楚，我们会把它整理成一页可继续往下学的复盘讲义。
        </p>
      </div>
    </div>
    <!-- existing form cards stay here, reordered but not renamed -->
  </section>

  <section class="learning-workspace-shell">
    <div id="review-stage-empty" class="learning-workspace-empty"></div>
    <div id="review-stage-content" class="learning-workspace hidden">
      <aside class="workspace-context-rail">
        <div id="workspace-stage-status"></div>
        <div id="active-review-chat-context" class="hidden"></div>
        <div id="active-review-related"></div>
      </aside>
      <main class="workspace-learning-stage">
        <div id="active-review-quiz-slot"></div>
      </main>
      <aside class="workspace-review-rail">
        <div class="workspace-review-header">
          <p class="learning-kicker">复盘讲义</p>
          <h3 id="active-review-title">这次打卡复盘</h3>
          <p id="active-review-subtitle"></p>
          <div id="active-review-meta"></div>
        </div>
        <div id="active-review-report"></div>
      </aside>
    </div>
  </section>
</div>
```

- [ ] **Step 7: Wire the new subtitle usage in `static/app.js`**

Update the entry-stage resets to use the helper:

```js
if (subtitleEl) subtitleEl.textContent = checkinReviewUi.entryStageLead();
```

and keep the existing review-stage title assignment:

```js
if (subtitleEl) {
    subtitleEl.textContent = item.review_status === 'completed'
        ? reviewFamilyUi.reviewWorkspaceSubtitle(item)
        : checkinReviewUi.reviewStageLead(item);
}
```

- [ ] **Step 8: Run static syntax checks**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --check static/app.js
```

Expected:

```text
(no output)
```

- [ ] **Step 9: Commit the shell and helper changes**

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
git add static/index.html static/checkin_review_ui.js test_checkin_review_ui.mjs static/app.js
git commit -m "feat: add learning canvas shell for student checkins"
```

---

## Task 2: Rebuild The Checkin Page Layout And Lecture-Note Styling

**Files:**
- Modify: `agent_learning/03_noi_agent/static/style.css`
- Test: `agent_learning/03_noi_agent/static/index.html`

- [ ] **Step 1: Add the failing CSS verification checkpoint**

Document the target selectors in the plan-first scratch check by adding these selectors to your working notes and verifying they do not yet exist:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
rg -n "checkin-canvas-page|learning-record-shell|workspace-learning-stage|workspace-review-rail" static/style.css
```

Expected:

```text
(no matches or only partial matches)
```

- [ ] **Step 2: Add page-level learning-canvas tokens near the checkin layout rules**

Insert:

```css
.checkin-canvas-page {
  display: grid;
  grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}

.learning-kicker {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #5f7c84;
}

.learning-record-shell,
.learning-workspace-shell {
  background: linear-gradient(180deg, #f8fbfc 0%, #ffffff 100%);
  border: 1px solid rgba(132, 160, 168, 0.18);
  border-radius: 24px;
  box-shadow: 0 18px 48px rgba(25, 56, 67, 0.08);
}
```

- [ ] **Step 3: Add form-page styling that removes dashboard energy**

Add styles for:

```css
.learning-record-header {
  padding: 28px 28px 8px;
}

.learning-record-title {
  font-size: 28px;
  line-height: 1.2;
  color: #17323a;
  margin-top: 6px;
}

.learning-record-subtitle {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.7;
  color: #5f7278;
}
```

- [ ] **Step 4: Add workspace three-rail styling**

Add:

```css
.learning-workspace {
  display: grid;
  grid-template-columns: minmax(240px, 0.8fr) minmax(0, 1.25fr) minmax(300px, 0.95fr);
  gap: 20px;
  padding: 24px;
}

.workspace-context-rail,
.workspace-review-rail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.workspace-learning-stage {
  min-width: 0;
}
```

- [ ] **Step 5: Add lecture-note surface styles for the review rail**

Add:

```css
.workspace-review-header {
  padding: 20px 20px 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #eef6f7 0%, #ffffff 100%);
  border: 1px solid rgba(123, 154, 163, 0.22);
}

.workspace-review-header h3 {
  font-size: 22px;
  line-height: 1.3;
  color: #15333a;
  margin-top: 6px;
}
```

- [ ] **Step 6: Replace the old right-column stats card selectors by hiding or deleting their markup-specific dependency**

Do not keep styles that assume the checkin page still has:

```css
#user-checkin-count,
#global-checkin-count,
#user-streak,
#motivational-quote
```

The production implementation can leave unrelated global styles in place, but the checkin page must no longer render those cards in the student flow.

- [ ] **Step 7: Add responsive collapse rules that preserve the invariant order**

Add:

```css
@media (max-width: 1100px) {
  .checkin-canvas-page,
  .learning-workspace {
    grid-template-columns: 1fr;
  }

  .workspace-review-rail { order: 1; }
  .workspace-learning-stage { order: 2; }
  .workspace-context-rail { order: 3; }
}
```

- [ ] **Step 8: Run a selector sanity check**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
rg -n "checkin-canvas-page|learning-record-shell|workspace-learning-stage|workspace-review-rail" static/style.css
```

Expected:

```text
1:.checkin-canvas-page {
7:.learning-record-shell,
18:.workspace-learning-stage {
24:.workspace-review-rail {
```

- [ ] **Step 9: Commit the layout styling**

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
git add static/style.css
git commit -m "feat: add lecture-note layout for student checkin page"
```

---

## Task 3: Convert The Review Rail Into A Lecture-Note Review Surface

**Files:**
- Modify: `agent_learning/03_noi_agent/static/app.js`
- Modify: `agent_learning/03_noi_agent/static/style.css`
- Modify: `agent_learning/03_noi_agent/static/tailwind-ui.js`
- Test: `agent_learning/03_noi_agent/test_review_family_ui.mjs`

- [ ] **Step 1: Freeze the review field-order contract with the existing tests**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --test test_review_family_ui.mjs
```

Expected:

```text
ok
```

- [ ] **Step 2: Refactor `renderReviewHtml` to emit a lecture-note section flow**

Update the render to wrap the existing ordered sections inside a new shell:

```js
return `
  <div class="review-note-flow">
    <section class="review-note-sheet review-note-sheet-primary">
      <div class="review-note-body">
        ${orderedSections.map((section) => renderReviewNoteSection(section)).join('')}
      </div>
    </section>
    ${renderReviewDetailsDrawer(review)}
  </div>
`;
```

and add the helper signature nearby:

```js
function renderReviewNoteSection(section) {
    const emphasisClass = section.field === 'try_now' ? 'is-action' : section.field === 'transfer_signal' ? 'is-aside' : '';
    return `
        <article class="review-note-section ${emphasisClass}">
            <div class="review-note-label">${escapeHtml(section.label)}</div>
            <div class="review-note-content">
                ${section.field === 'visual_hint'
                    ? `<pre class="review-visual-hint review-note-visual">${escapeHtml(section.value || '')}</pre>`
                    : renderRichTextBlock(section.value || '', 'review-inline-rich-block')}
            </div>
        </article>
    `;
}
```

- [ ] **Step 3: Move teacher-only and folded detail fields into an explicit drawer**

Keep the same data, but move the current `<details class="archive-detail">` logic into:

```js
function renderReviewDetailsDrawer(item) {
    const aiTags = renderPillRow(item.review_error_tags, 'tag-pill ai-tag');
    const aiSubtags = renderPillRow(item.review_core_design_subtags, 'tag-pill subtle-tag');
    return `
        <details class="review-note-drawer">
            <summary>展开看老师批注</summary>
            <div class="review-note-drawer-body">
                <div class="archive-chip-row">${aiTags}</div>
                ${item.review_core_design_subtags?.length ? `<div class="archive-chip-row">${aiSubtags}</div>` : ''}
                ${item.review_suggested_topic ? `<div class="archive-line"><strong>推荐专题：</strong>${renderRichTextInline(item.review_suggested_topic)}</div>` : ''}
                ${item.review_error_layer ? `<div class="archive-line"><strong>AI 归类：</strong>${escapeHtml(errorLayerText(item.review_error_layer))}</div>` : ''}
            </div>
        </details>
    `;
}
```

- [ ] **Step 4: Add review-rail styles**

In `static/style.css`, add:

```css
.review-note-flow {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-note-sheet {
  background: linear-gradient(180deg, #f7fbfc 0%, #ffffff 100%);
  border: 1px solid rgba(120, 150, 158, 0.22);
  border-radius: 22px;
  padding: 20px;
}

.review-note-section {
  padding: 16px 0;
  border-bottom: 1px dashed rgba(126, 153, 160, 0.22);
}

.review-note-section.is-action {
  background: rgba(22, 88, 106, 0.05);
  border: 1px solid rgba(22, 88, 106, 0.14);
  border-radius: 16px;
  padding: 16px;
}
```

- [ ] **Step 5: Keep `TwUI` useful but optional**

If the current `window.TwUI.renderReviewSection(review, family)` path is retained, update it so its card output follows the same review-note vocabulary:

```js
<h3 class="text-base font-bold text-slate-800 dark:text-slate-100">复盘讲义</h3>
```

and ensure the section titles match the spec order:

```js
{ field: 'try_now', title: '现在先做' }
{ field: 'transfer_signal', title: '下次怎么认出来' }
```

- [ ] **Step 6: Re-run the review-family tests**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --test test_review_family_ui.mjs
```

Expected:

```text
ok
```

- [ ] **Step 7: Run JS syntax checks**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --check static/app.js
node --check static/tailwind-ui.js
```

Expected:

```text
(no output)
```

- [ ] **Step 8: Commit the review surface work**

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
git add static/app.js static/style.css static/tailwind-ui.js
git commit -m "feat: restyle student review rail as lecture notes"
```

---

## Task 4: Turn The Quiz Chain Into A Single-Stage Learning Path

**Files:**
- Modify: `agent_learning/03_noi_agent/static/app.js`
- Modify: `agent_learning/03_noi_agent/static/style.css`

- [ ] **Step 1: Identify the current render entry points**

Confirm the current functions before editing:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
rg -n "renderQuizCard|renderReviewDetailQuizTimeline|renderQuizTimelineStatus|renderCollapsedQuizStep|renderSelfCheckCard|renderRemedyButtons" static/app.js
```

Expected:

```text
3710:function renderQuizCard(quiz, reviewId) {
3811:function renderQuizTimelineStatus(item, reviewId, reviewFamily) {
3857:function renderReviewDetailQuizTimeline(item) {
3976:function renderSelfCheckCard(reviewId, family = 'failure_diagnosis') {
3999:function renderRemedyButtons(reviewId, errorLayer, options = {}) {
```

- [ ] **Step 2: Add a stage header helper ahead of `renderQuizCard`**

Insert:

```js
function renderLearningStageHeader(quiz = {}, stateText = '') {
    const level = quiz?.meta?.difficulty_level || quiz?.difficulty_level || 'main';
    const titleMap = {
        main: '先确认你是不是已经抓住这一步了',
        followup: '这一步还差一点，我们再拆小一点',
        confirm: '换个角度，再确认一次',
        knowledge_confirm: '看完上面的讲解，再做最后一次确认',
        final_micro_confirm: '最后用一个最小问题收尾确认',
    };
    return `
        <div class="learning-stage-header">
            <p class="learning-kicker">理解检查</p>
            <h3>${escapeHtml(titleMap[level] || '继续拆这一步')}</h3>
            ${stateText ? `<p class="learning-stage-subtitle">${escapeHtml(stateText)}</p>` : ''}
        </div>
    `;
}
```

- [ ] **Step 3: Wrap the active quiz in a single-focus learning-stage shell**

Update `renderQuizCard`:

```js
return `
  <div class="learning-stage-card">
    ${renderLearningStageHeader(quiz)}
    <div class="learning-stage-question">
      ${renderRichTextBlock(quiz.question_text)}
    </div>
    ${renderQuizOptions(quiz, reviewId)}
    <div class="quiz-actions">
      <button class="primary learning-stage-submit" onclick="submitQuizAnswer(${Number(quiz.quiz_id)}, ${Number(reviewId)})">提交这一小步</button>
    </div>
  </div>
`;
```

- [ ] **Step 4: Collapse historical steps into a compact path rail**

Update `renderCollapsedQuizStep` to become a compact summary row:

```js
return `
  <div class="learning-path-step is-complete" onclick="this.classList.toggle('expanded')">
    <div class="learning-path-step-summary">
      <span class="learning-path-step-index">第 ${stepNumber} 步</span>
      <span class="learning-path-step-label">${escapeHtml(levelText)}</span>
      <span class="learning-path-step-result ${isCorrect ? 'correct' : 'incorrect'}">${resultText}</span>
    </div>
    <div class="learning-path-step-detail">${renderQuizCard(quiz, 0)}</div>
  </div>
`;
```

- [ ] **Step 5: Restyle self-check and remedy as next steps in the same path**

Keep the logic, but change the framing copy:

```js
<div class="self-check-card-v2">
  <div class="self-check-title-v2">你现在觉得，这一步是真的懂了，还是刚才有点猜中？</div>
  <div class="self-check-options-v2">
    <div class="self-check-option-v2 tone-clear" onclick="submitSelfCheck(${Number(reviewId)}, 'clear')">
      <div class="self-check-option-icon">✅</div>
      <div class="self-check-option-text">我现在可以自己继续往下做</div>
    </div>
  </div>
</div>
```

and:

```js
<div class="quiz-card-v2 learning-remedy-card">
  <div class="learning-remedy-title">我们换一种带法，继续过这一步</div>
  <div class="learning-remedy-actions">
    <button class="secondary" onclick="triggerRemedy(${Number(reviewId)}, 'rephrase')">再换一种说法讲这一步</button>
    <button class="secondary" onclick="triggerRemedy(${Number(reviewId)}, 'smaller_example')">给我一个更小的例子</button>
    <button class="secondary" onclick="triggerRemedy(${Number(reviewId)}, 'easier_quiz')">再出一道更简单的小题</button>
  </div>
</div>
```

- [ ] **Step 6: Add learning-path CSS**

Add:

```css
.learning-stage-card {
  background: #ffffff;
  border: 1px solid rgba(120, 150, 158, 0.18);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 14px 36px rgba(26, 54, 62, 0.08);
}

.learning-stage-header h3 {
  font-size: 22px;
  line-height: 1.3;
  color: #15333a;
  margin-top: 6px;
}

.learning-path-step {
  border: 1px solid rgba(120, 150, 158, 0.16);
  border-radius: 16px;
  background: #f8fbfb;
}
```

- [ ] **Step 7: Run JS syntax validation**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --check static/app.js
```

Expected:

```text
(no output)
```

- [ ] **Step 8: Commit the quiz-chain work**

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
git add static/app.js static/style.css
git commit -m "feat: turn review quiz chain into a learning path"
```

---

## Task 5: Recast Knowledge Bailout As A Study-Handbook Insert

**Files:**
- Modify: `agent_learning/03_noi_agent/static/app.js`
- Modify: `agent_learning/03_noi_agent/static/style.css`
- Modify: `agent_learning/03_noi_agent/static/tailwind-ui.js`

- [ ] **Step 1: Inspect the current bailout render contract before changing it**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
rg -n "function renderKnowledgeBailoutCard|knowledge-bailout-card-v2|wrong_thinking|right_thinking|micro_action" static/app.js static/style.css static/tailwind-ui.js
```

Expected:

```text
3650:function renderKnowledgeBailoutCard(card = {}) {
2427:.knowledge-bailout-card-v2 {
241:.knowledge-comparison-item.wrong {
```

- [ ] **Step 2: Rebuild `renderKnowledgeBailoutCard` into a handbook insert**

Keep all existing fields, but reorder them:

```js
return `
  <section class="knowledge-note-sheet">
    <div class="knowledge-note-header">
      <p class="learning-kicker">补充讲解</p>
      <h3>先把这块知识单独讲清楚</h3>
    </div>
    ${opening ? `<div class="knowledge-note-opening">${renderRichTextBlock(opening)}</div>` : ''}
    <div class="knowledge-note-bridge">
      <div class="knowledge-note-section-title">当前这座桥</div>
      <div>${renderRichTextInline(bridgeExplanation)}</div>
    </div>
    ${comparisonHtml}
    ${visualHint ? `<pre class="knowledge-note-visual">${escapeHtml(visualHint)}</pre>` : ''}
    ${microAction ? `<div class="knowledge-note-summary"><strong>看完先记住：</strong>${renderRichTextInline(microAction)}</div>` : ''}
    ${overviewHtml}
  </section>
`;
```

- [ ] **Step 3: Rename the comparison labels to lecture-note wording**

Replace:

```js
'❌ 这样想'
'✅ 其实应该'
```

with:

```js
'常见误解'
'正确理解'
```

- [ ] **Step 4: Add handbook styles**

Add:

```css
.knowledge-note-sheet {
  background: linear-gradient(180deg, #fffdf5 0%, #fffaf0 100%);
  border: 1px solid rgba(226, 194, 111, 0.38);
  border-radius: 22px;
  padding: 22px;
}

.knowledge-note-section-title {
  font-size: 13px;
  font-weight: 700;
  color: #7b6b20;
  margin-bottom: 8px;
}

.knowledge-note-summary {
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(247, 222, 144, 0.18);
}
```

- [ ] **Step 5: Keep `TwUI` bailout output aligned**

Update the `renderTwKnowledgeCard` header:

```js
<span class="flex items-center gap-2">
  ${Icons.book}
  先把这块知识单独讲清楚
</span>
```

and use the same comparison wording:

```js
常见误解
正确理解
```

- [ ] **Step 6: Run syntax checks**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --check static/app.js
node --check static/tailwind-ui.js
```

Expected:

```text
(no output)
```

- [ ] **Step 7: Commit the bailout redesign**

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
git add static/app.js static/style.css static/tailwind-ui.js
git commit -m "feat: restyle knowledge bailout as study handbook insert"
```

---

## Task 6: Final Integration And Regression Pass

**Files:**
- Modify: `agent_learning/03_noi_agent/static/app.js`
- Modify: `agent_learning/03_noi_agent/static/index.html`
- Modify: `agent_learning/03_noi_agent/static/style.css`
- Modify: `agent_learning/03_noi_agent/static/checkin_review_ui.js`
- Modify: `agent_learning/03_noi_agent/static/tailwind-ui.js`
- Test: `agent_learning/03_noi_agent/test_checkin_review_ui.mjs`
- Test: `agent_learning/03_noi_agent/test_review_family_ui.mjs`

- [ ] **Step 1: Run the focused JS and helper test suite**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --check static/app.js
node --check static/checkin_review_ui.js
node --check static/tailwind-ui.js
node --test test_checkin_review_ui.mjs
node --test test_review_family_ui.mjs
```

Expected:

```text
(syntax checks print nothing)
ok
```

- [ ] **Step 2: Run the existing broader frontend-adjacent smoke coverage**

Run:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
node --test test_checkin_review_ui.mjs test_review_family_ui.mjs test_teacher_manual_review_ui.mjs
```

Expected:

```text
ok
```

- [ ] **Step 3: Manually verify the student flow in browser**

Run the app if not already running:

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

Then manually verify at `http://127.0.0.1:8000/app`:

```text
1. 登录 student_a
2. 打开“打卡复盘”
3. 确认首屏是学习记录页，不再出现统计/励志卡主视觉
4. 提交一条已有样例或选择已有记录
5. 确认工作台是左上下文 / 中主舞台 / 右复盘讲义
6. 确认 AI 复盘默认只突出四块主内容
7. 确认 quiz 当前题最大，历史步骤折叠
8. 确认 knowledge bailout 像插页讲解
9. 缩小到移动宽度，确认顺序仍是 右 -> 中 -> 左
```

Expected:

```text
所有状态均可见，且学习链逻辑不变
```

- [ ] **Step 4: Update harness docs only if implementation really changes current truth**

If and only if the shipped UI changes the code-truth descriptions, update:

```text
docs/harness/current_system_state.md
docs/harness/active_work_item.md
```

For this redesign, likely updates are:

- student checkin page no longer foregrounds stats/motivation cards
- student workspace visually recenters on learning stage while preserving existing data and ordering rules

- [ ] **Step 5: Create the final integration commit**

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
git add static/index.html static/style.css static/app.js static/checkin_review_ui.js static/tailwind-ui.js test_checkin_review_ui.mjs test_review_family_ui.mjs docs/harness/current_system_state.md docs/harness/active_work_item.md
git commit -m "feat: redesign student review workspace as learning canvas"
```

---

## Self-Review

### Spec coverage

- Overall learning-canvas page restructure: covered by Tasks 1-2
- AI review rail lecture-note redesign: covered by Task 3
- Quiz chain as learning path: covered by Task 4
- Knowledge bailout as study-handbook insert: covered by Task 5
- Verification without business-logic changes: covered by Task 6

No spec gaps found.

### Placeholder scan

Checked for:

- `TODO`
- `TBD`
- “implement later”
- “write tests for the above”

None intentionally left in the task steps.

### Type consistency

Helper names introduced in the plan:

- `entryStageLead`
- `renderLearningStageHeader`
- `renderReviewNoteSection`
- `renderReviewDetailsDrawer`

These names are reused consistently within the tasks and do not conflict with known existing helper names.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-09-student-ui-learning-canvas-implementation-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
