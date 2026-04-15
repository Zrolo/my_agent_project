import fs from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';

const html = fs.readFileSync(new URL('./static/index.html', import.meta.url), 'utf8');

test('review stage uses summary + main + related layout structure', () => {
  assert.match(html, /class="review-stage-summary/);
  assert.match(html, /class="review-stage-main/);
  assert.match(html, /class="review-stage-related/);
});

test('review stage keeps related practice after the main dual-column area', () => {
  const summaryIndex = html.indexOf('class="review-stage-summary');
  const mainIndex = html.indexOf('class="review-stage-main');
  const relatedIndex = html.indexOf('class="review-stage-related');

  assert.ok(summaryIndex >= 0);
  assert.ok(mainIndex > summaryIndex);
  assert.ok(relatedIndex > mainIndex);
});

test('history tab contains explicit list stage and detail stage containers', () => {
  assert.match(html, /id="history-list-stage"/);
  assert.match(html, /id="history-detail-stage"/);
});

test('history detail stage exposes an explicit back-to-history control', () => {
  assert.match(html, /id="history-back-btn"/);
});

test('student workspace exposes route-aware shell heading ids', () => {
  assert.match(html, /id="student-shell-kicker"/);
  assert.match(html, /id="student-shell-title"/);
  assert.match(html, /id="student-shell-subtitle"/);
});

test('student chat and checkin pages use dedicated layout shells', () => {
  assert.match(html, /class="student-workspace"/);
  assert.match(html, /class="checkin-canvas-page"/);
});

test('history list page uses dedicated archive shell blocks', () => {
  assert.match(html, /class="history-page-stack"/);
  assert.match(html, /class="history-page-surface student-surface"/);
  assert.match(html, /class="checkin-history-stack"/);
});

test('login page no longer exposes a default problem id field', () => {
  assert.doesNotMatch(html, /id="login-problem-id"/);
});
