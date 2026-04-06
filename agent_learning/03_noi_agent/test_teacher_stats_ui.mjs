import fs from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';

function escapeHtmlText(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function createElementStub() {
  let textContentValue = '';
  return {
    style: {},
    dataset: {},
    value: '',
    innerHTML: '',
    classList: {
      add() {},
      remove() {},
      toggle() { return false; },
      contains() { return false; },
    },
    addEventListener() {},
    scrollIntoView() {},
    focus() {},
    setAttribute() {},
    getAttribute() { return null; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    set textContent(value) {
      textContentValue = String(value);
      this.innerHTML = escapeHtmlText(textContentValue);
    },
    get textContent() {
      return textContentValue;
    },
  };
}

function createDocumentStub() {
  const nodes = new Map();
  return {
    getElementById(id) {
      if (!nodes.has(id)) {
        nodes.set(id, createElementStub());
      }
      return nodes.get(id);
    },
    querySelector() {
      return null;
    },
    querySelectorAll() {
      return [];
    },
    addEventListener() {},
    createElement() {
      return createElementStub();
    },
  };
}

function createLocalStorageStub() {
  const store = new Map();
  return {
    getItem(key) {
      return store.has(key) ? store.get(key) : null;
    },
    setItem(key, value) {
      store.set(key, String(value));
    },
    removeItem(key) {
      store.delete(key);
    },
  };
}

function loadAppHooks() {
  const document = createDocumentStub();
  const localStorage = createLocalStorageStub();
  const window = {
    location: { origin: 'http://localhost' },
    document,
    localStorage,
    console,
    reviewFamilyUi: {
      resolveReviewFamily(item = {}) {
        if (item.review_family) return item.review_family;
        return item.review_mode === 'independent_reflect' ? 'success_reflection' : 'failure_diagnosis';
      },
    },
    teacherManualReviewUi: {
      renderTeacherReviewSamplesPanel() {
        return '';
      },
      buildTeacherManualReviewPayload(form) {
        return {
          mode_correct: form.elements.mode_correct.value,
          review_grounded: form.elements.review_grounded.value,
          student_can_move_next: form.elements.student_can_move_next.value,
          notes: String(form.elements.notes.value || '').trim(),
        };
      },
    },
    requestAnimationFrame(cb) {
      return setTimeout(cb, 0);
    },
    cancelAnimationFrame(id) {
      clearTimeout(id);
    },
  };
  const sandbox = {
    window,
    document,
    localStorage,
    console,
    setTimeout,
    clearTimeout,
    Math,
    Number,
    String,
    Boolean,
    Date,
    JSON,
    Promise,
    RegExp,
    Array,
    Object,
    Map,
    Set,
  };
  vm.runInNewContext(fs.readFileSync(new URL('./static/app.js', import.meta.url), 'utf8'), sandbox, {
    filename: 'static/app.js',
  });
  return sandbox.window.noiAppTestHooks;
}

const hooks = loadAppHooks();

test('buildReviewRequestSubmittedPayload keeps backend session data and review routing fields', () => {
  const payload = hooks.buildReviewRequestSubmittedPayload(
    {
      session_id: 'sess_backend_001',
      checkin_id: 42,
      review_mode: 'stuck_bridge',
      review_family: 'failure_diagnosis',
    },
    {
      problem_id: 'P1001',
      problem_title: 'P1001 A+B Problem',
      has_code: true,
      problem_context_length: 128,
      bottleneck_text_length: 36,
    },
  );

  assert.equal(payload.checkin_id, 42);
  assert.equal(payload.session_id, 'sess_backend_001');
  assert.equal(payload.event_name, 'review_request_submitted');
  assert.equal(payload.review_mode, 'stuck_bridge');
  assert.equal(payload.review_family, 'failure_diagnosis');
  assert.equal(payload.problem_id, 'P1001');
  assert.equal(payload.problem_title, 'P1001 A+B Problem');
  assert.equal(payload.has_code, true);
  assert.equal(payload.problem_context_length, 128);
  assert.equal(payload.bottleneck_text_length, 36);
  assert.equal(payload.app_version, '0.5.0');
  assert.match(payload.client_ts, /^\d{4}-\d{2}-\d{2}T/);
});

test('normalizeManualReviewRates and renderManualReviewRatesCard understand keyed stats', () => {
  const rows = hooks.normalizeManualReviewRates({
    mode_match_rate: { count: 8, total: 10 },
    grounded_rate: 0.75,
    can_move_next_rate: { label: '继续能力', rate: 0.5, note: '少量样本' },
  });

  assert.deepEqual(Array.from(rows, (row) => row.label), ['mode 正确率', '贴题率', '继续能力']);
  assert.equal(rows[0].displayValue, '8 / 10 (80%)');
  assert.equal(rows[1].displayValue, '75%');
  assert.equal(rows[2].displayValue, '50%');
  assert.equal(rows[2].note, '少量样本');

  const html = hooks.renderManualReviewRatesCard({
    manual_review_rates: rows,
  });

  assert.match(html, /人工复核统计/);
  assert.match(html, /8 \/ 10 \(80%\)/);
  assert.match(html, /75%/);
  assert.match(html, /继续能力/);
});

test('renderManualReviewRatesCard shows empty state when no stats are available', () => {
  const html = hooks.renderManualReviewRatesCard({});
  assert.match(html, /暂无人工复核统计数据/);
});

test('renderManualReviewBreakdownSection renders grouped mode and family stats', () => {
  const html = hooks.renderManualReviewBreakdownSection('按 mode 细分', {
    failed_verdict: {
      reviewed_count: 2,
      mode_correct_rate: 0.5,
      grounded_rate: 1.0,
      student_can_move_next_rate: 0.5,
    },
    independent_reflect: {
      reviewed_count: 1,
      mode_correct_rate: 1.0,
      grounded_rate: 1.0,
      student_can_move_next_rate: 0.0,
    },
  });

  assert.match(html, /按 mode 细分/);
  assert.match(html, /failed_verdict/);
  assert.match(html, /independent_reflect/);
  assert.match(html, /mode 正确率/);
  assert.match(html, /贴题率/);
  assert.match(html, /可继续率/);
});

test('filterTeacherReviewSamples filters by mode and family', () => {
  const samples = [
    { review_id: 1, review_mode: 'failed_verdict', review_family: 'failure_diagnosis' },
    { review_id: 2, review_mode: 'stuck_bridge', review_family: 'failure_diagnosis' },
    { review_id: 3, review_mode: 'independent_reflect', review_family: 'success_reflection' },
  ];

  assert.deepEqual(
    Array.from(hooks.filterTeacherReviewSamples(samples, { kind: 'mode', value: 'failed_verdict' }), (item) => item.review_id),
    [1],
  );
  assert.deepEqual(
    Array.from(hooks.filterTeacherReviewSamples(samples, { kind: 'family', value: 'failure_diagnosis' }), (item) => item.review_id),
    [1, 2],
  );
  assert.deepEqual(
    Array.from(hooks.filterTeacherReviewSamples(samples, { kind: '', value: '' }), (item) => item.review_id),
    [1, 2, 3],
  );
});

test('renderManualReviewFilterBanner shows active filter and clear action', () => {
  const html = hooks.renderManualReviewFilterBanner({ kind: 'mode', value: 'failed_verdict' });

  assert.match(html, /当前筛选/);
  assert.match(html, /failed_verdict/);
  assert.match(html, /清除筛选/);
});
