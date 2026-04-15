import fs from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';

import teacherStatsUi from './static/teacher_stats_ui.js';

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
  const payload = teacherStatsUi.buildReviewRequestSubmittedPayload(
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
  const rows = teacherStatsUi.normalizeManualReviewRates({
    mode_match_rate: { count: 8, total: 10 },
    grounded_rate: 0.75,
    can_move_next_rate: { label: '继续能力', rate: 0.5, note: '少量样本' },
  });

  assert.deepEqual(Array.from(rows, (row) => row.label), ['mode 正确率', '贴题率', '继续能力']);
  assert.equal(rows[0].displayValue, '8 / 10 (80%)');
  assert.equal(rows[1].displayValue, '75%');
  assert.equal(rows[2].displayValue, '50%');
  assert.equal(rows[2].note, '少量样本');

  const html = teacherStatsUi.renderManualReviewRatesCard({
    manual_review_rates: rows,
  });

  assert.match(html, /人工复核统计/);
  assert.match(html, /8 \/ 10 \(80%\)/);
  assert.match(html, /75%/);
  assert.match(html, /继续能力/);
});

test('renderManualReviewRatesCard shows empty state when no stats are available', () => {
  const html = teacherStatsUi.renderManualReviewRatesCard({});
  assert.match(html, /暂无人工复核统计数据/);
});

test('renderBridgeStatsCard and renderKnowledgeBailoutStatsCard show new teacher stats sections', () => {
  const bridgeHtml = teacherStatsUi.renderBridgeStatsCard({
    'dp.state_design': { count: 3, total: 6, rate: 0.5 },
    'binary_search.check_condition': { count: 2, total: 6, rate: 0.333 },
  });
  const bailoutHtml = teacherStatsUi.renderKnowledgeBailoutStatsCard({
    entered: { count: 2, total: 6, rate: 0.333 },
    not_entered: { count: 4, total: 6, rate: 0.667 },
  });

  assert.match(bridgeHtml, /高频知识桥分布/);
  assert.match(bridgeHtml, /状态设计/);
  assert.match(bridgeHtml, /判定函数语义/);
  assert.match(bridgeHtml, /3 \/ 6 \(50%\)/);
  assert.match(bailoutHtml, /知识卡介入分布/);
  assert.match(bailoutHtml, /进入知识卡/);
  assert.match(bailoutHtml, /未进入知识卡/);
  assert.match(bailoutHtml, /2 \/ 6 \(33(?:\.3)?%\)/);
});

test('renderTopicStatsCard shows topic_l1 and topic_l2 teacher stats sections', () => {
  const topicL1Html = teacherStatsUi.renderTopicStatsCard('topic_l1', {
    dp: { count: 3, total: 7, rate: 0.429 },
    string: { count: 2, total: 7, rate: 0.286 },
  });
  const topicL2Html = teacherStatsUi.renderTopicStatsCard('topic_l2', {
    dp_basic: { count: 3, total: 7, rate: 0.429 },
    trie: { count: 2, total: 7, rate: 0.286 },
  });

  assert.match(topicL1Html, /知识域分布/);
  assert.match(topicL1Html, /动态规划/);
  assert.match(topicL1Html, /字符串/);
  assert.match(topicL2Html, /知识子域分布/);
  assert.match(topicL2Html, /基础 DP/);
  assert.match(topicL2Html, /Trie/);
});

test('renderManualReviewBreakdownSection renders grouped mode and family stats', () => {
  const html = teacherStatsUi.renderManualReviewBreakdownSection('按 mode 细分', {
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
    Array.from(teacherStatsUi.filterTeacherReviewSamples(samples, { kind: 'mode', value: 'failed_verdict' }), (item) => item.review_id),
    [1],
  );
  assert.deepEqual(
    Array.from(teacherStatsUi.filterTeacherReviewSamples(samples, { kind: 'family', value: 'failure_diagnosis' }), (item) => item.review_id),
    [1, 2],
  );
  assert.deepEqual(
    Array.from(teacherStatsUi.filterTeacherReviewSamples(samples, { kind: '', value: '' }), (item) => item.review_id),
    [1, 2, 3],
  );
});

test('renderManualReviewFilterBanner shows active filter and clear action', () => {
  const html = teacherStatsUi.renderManualReviewFilterBanner({ kind: 'mode', value: 'failed_verdict' });

  assert.match(html, /当前筛选/);
  assert.match(html, /failed_verdict/);
  assert.match(html, /清除筛选/);
});

test('renderQuizCard lays out question and options as structured quiz panels', () => {
  const html = hooks.renderQuizCard(
    {
      quiz_id: 11,
      quiz_type: 'single_choice',
      question_text: '在判断是否可以直接逐条比对时，哪个观察最关键？',
      options: [
        '两个 5×10^4 级别的集合做全量交叉比对，会产生约 2.5×10^9 次配对',
        '单条串长度不超过 20，所以暴力一定没问题',
      ],
      meta: {
        difficulty_level: 'main',
        micro_hint: '先别急着想 trie，先看规模。',
      },
    },
    99,
  );

  assert.match(html, /quiz-question-card/);
  assert.match(html, /quiz-options/);
  assert.match(html, /quiz-option-mark/);
  assert.match(html, /quiz-option-body/);
  assert.match(html, /先别急着想 trie，先看规模/);
});

test('renderQuizStageNotice keeps follow-up guidance out of the question card', () => {
  const html = hooks.renderQuizStageNotice({
    title: '这一步还差一点，我们先只盯住“查一条串时会不会重看所有消息”这件事。',
    explanation: '先别回到整题复杂度，我们先把查询过程这一小步说清楚。',
    tone: 'warn',
  });

  assert.match(html, /quiz-stage-note/);
  assert.match(html, /quiz-stage-kicker/);
  assert.match(html, /这一步还差一点/);
  assert.doesNotMatch(html, /quiz-card quiz-result warn/);
});

test('renderPendingStageCard renders a styled loading stage card', () => {
  const html = hooks.renderPendingStageCard({
    kicker: '理解检查',
    status: '正在准备',
    title: '正在生成这一小步的小测...',
    subtitle: '我们先把这一步收进同一条路径里，很快就好。',
  });

  assert.match(html, /learning-stage-pending/);
  assert.match(html, /learning-stage-status-chip/);
  assert.match(html, /learning-stage-pending-loader/);
  assert.match(html, /learning-stage-pending-progress-fill/);
  assert.match(html, /正在准备/);
});

test('renderReviewNoteSection keeps visual hint on rich-text math path', () => {
  const html = hooks.renderReviewNoteSection({
    field: 'visual_hint',
    label: '先看这个对比',
    value: 'M × N = 50000 × 50000',
  });

  assert.match(html, /review-visual-hint/);
  assert.match(html, /data-rich-ready="0"/);
  assert.match(html, /rich-text/);
  assert.doesNotMatch(html, /<pre/);
});

test('renderKnowledgeBailoutCard keeps visual hint on rich-text math path', () => {
  const html = hooks.renderKnowledgeBailoutCard({
    visual_hint: 'M × N = 50000 × 50000',
    bridge_explanation: '先看规模。',
  });

  assert.match(html, /knowledge-note-visual/);
  assert.match(html, /data-rich-ready="0"/);
  assert.match(html, /rich-text/);
  assert.doesNotMatch(html, /<pre/);
});

test('renderReviewNoteSection renders Mermaid visual hints as diagram containers', () => {
  const html = hooks.renderReviewNoteSection({
    field: 'visual_hint',
    label: '看图想一想',
    value: '```mermaid\nflowchart TD\nA[看规模] --> B[选方法]\n```',
  });

  assert.match(html, /visual-hint-diagram/);
  assert.match(html, /visual-hint-mermaid mermaid/);
  assert.match(html, /flowchart TD/);
});

test('renderReviewNoteSection keeps arithmetic expressions intact for KaTeX hydration', () => {
  const html = hooks.renderReviewNoteSection({
    field: 'visual_hint',
    label: '看图想一想',
    value: '暴力枚举：N 条拦截 × M 条信息 = 50000×50000 = 2.5×10^9 次比对',
  });

  assert.doesNotMatch(html, /\$×\$/);
  assert.doesNotMatch(html, /2\$\.5/);
  assert.match(html, /\$50000/);
  assert.match(html, /2\.5/);
  assert.match(html, /10\^9\$/);
});

test('renderReviewNoteSection wraps standalone power notation for KaTeX hydration', () => {
  const html = hooks.renderReviewNoteSection({
    field: 'guided_walkthrough',
    label: '跟我走一遍',
    value: '再除以 10^8（大约一秒能跑的运算次数），看看需要多少秒。',
  });

  assert.match(html, /\$10\^8\$/);
});

test('renderKnowledgeBailoutCard renders table visual hints as structured tables', () => {
  const html = hooks.renderKnowledgeBailoutCard({
    bridge_explanation: '先看候选。',
    visual_hint: `| 候选 | 是否需要比较 |
| --- | --- |
| 左边内部 | 是 |
| 经过新边 | 是 |`,
  });

  assert.match(html, /visual-hint-table-wrap/);
  assert.match(html, /<table/);
  assert.match(html, /左边内部/);
});

test('renderVisualHintContent renders grid visual hints as grid cards', () => {
  const html = hooks.renderVisualHintContent(`\`\`\`grid
1 2 3
4 5 6
\`\`\``);

  assert.match(html, /visual-hint-grid-wrap/);
  assert.match(html, /visual-hint-grid/);
  assert.match(html, /visual-hint-grid-cell/);
});

test('renderVisualHintContent renders array visual hints as array chips', () => {
  const html = hooks.renderVisualHintContent(`\`\`\`array
dp[0] | dp[1] | dp[2]
\`\`\``);

  assert.match(html, /visual-hint-array-wrap/);
  assert.match(html, /visual-hint-array/);
  assert.match(html, /visual-hint-array-cell/);
  assert.match(html, /dp\[1\]/);
});

test('renderVisualHintContent renders dp table visual hints as structured state tables', () => {
  const html = hooks.renderVisualHintContent(`\`\`\`dptable
i/j | 0 | 1 | 2
0 | 0 | 1 | 2
1 | 1 | 2 | 3
\`\`\``);

  assert.match(html, /visual-hint-dp-table-wrap/);
  assert.match(html, /<table class="visual-hint-dp-table">/);
  assert.match(html, /<th>/);
  assert.match(html, /i\/j/);
});

test('renderVisualHintContent renders board visual hints as chessboard-like grids', () => {
  const html = hooks.renderVisualHintContent(`\`\`\`board
S . .
. # .
. . T
\`\`\``);

  assert.match(html, /visual-hint-board-wrap/);
  assert.match(html, /visual-hint-board/);
  assert.match(html, /visual-hint-board-cell/);
  assert.match(html, /S/);
  assert.match(html, /T/);
});

test('renderReviewDetailQuizTimeline keeps earlier questions visible above the current one', () => {
  const html = hooks.renderReviewDetailQuizTimeline({
    review_id: 77,
    review_status: 'completed',
    review_learning_status: 'quiz_in_progress',
    quiz_id: 102,
    quiz_history: [
      {
        quiz_id: 101,
        status: 'incorrect',
        quiz_type: 'choice',
        question_text: '第一轮：为什么暴力不行？',
        latest_answer_text: 'B',
        latest_is_correct: false,
        latest_feedback_text: '这一步还没过，我们先缩小一点。',
        meta: { difficulty_level: 'main' },
        options: [{ value: 'A', label: '看规模' }, { value: 'B', label: '直接猜方法' }],
      },
      {
        quiz_id: 102,
        status: 'pending',
        quiz_type: 'choice',
        question_text: '第二轮：查询时会不会重看所有消息？',
        meta: { difficulty_level: 'followup' },
        options: [{ value: 'A', label: '不会，只沿前缀走' }, { value: 'B', label: '会' }],
      },
    ],
  });

  assert.match(html, /第一轮：为什么暴力不行/);
  assert.match(html, /第二轮：查询时会不会重看所有消息/);
  assert.match(html, /上一题先留在上面/);
  assert.match(html, /你的回答/);
});

test('renderReviewDetailQuizTimeline shows knowledge bailout card below earlier quiz history', () => {
  const html = hooks.renderReviewDetailQuizTimeline({
    review_id: 88,
    review_status: 'completed',
    review_learning_status: 'knowledge_bailout',
    quiz_id: 203,
    quiz_history: [
      {
        quiz_id: 201,
        status: 'incorrect',
        quiz_type: 'choice',
        question_text: '第一轮：为什么 trie 更快？',
        latest_answer_text: 'B',
        latest_is_correct: false,
        latest_feedback_text: '这一步还没过。',
        meta: { difficulty_level: 'main' },
        options: [{ value: 'A', label: '看规模' }, { value: 'B', label: '直接猜方法' }],
      },
      {
        quiz_id: 202,
        status: 'incorrect',
        quiz_type: 'choice',
        question_text: '第三轮：查询时是不是还要重看所有消息？',
        latest_answer_text: 'B',
        latest_is_correct: false,
        latest_feedback_text: '我们换成知识讲解再过一遍。',
        meta: { difficulty_level: 'final_micro_confirm' },
        options: [{ value: 'A', label: '是' }, { value: 'B', label: '不是' }],
      },
      {
        quiz_id: 203,
        status: 'pending',
        quiz_type: 'choice',
        question_text: '知识卡后确认：查询一条串时更像在做什么？',
        meta: {
          difficulty_level: 'knowledge_confirm',
          knowledge_bailout: true,
          knowledge_card: {
            opening: '你刚才已经试了几种方式，现在我们把这一步单独讲清楚。',
            bridge_explanation: 'trie 把相同开头的消息并到一条路上，所以查询时不用重看所有消息。',
            algorithm_overview: '整个 trie 的作用，就是把公共前缀提前合并。',
          },
        },
        options: [{ value: 'A', label: '只沿前缀往下走' }, { value: 'B', label: '重看所有消息' }],
      },
    ],
  });

  assert.match(html, /第一轮：为什么 trie 更快/);
  assert.match(html, /我们把这一步单独讲清楚/);
  assert.match(html, /公共前缀提前合并/);
  assert.match(html, /知识卡后确认/);
});

test('renderMasteryStatusCard renders mastery distribution summary', () => {
  const html = hooks.renderMasteryStatusCard({
    independent_success: { count: 6, total: 12, rate: 0.5 },
    assisted_success: { count: 4, total: 12, rate: 0.333 },
    not_mastered: { count: 2, total: 12, rate: 0.167 },
  });

  assert.match(html, /过桥结果分布/);
  assert.match(html, /独立过桥/);
  assert.match(html, /辅助后过桥/);
  assert.match(html, /仍未掌握/);
  assert.match(html, /6 \/ 12/);
  assert.match(html, /33.3%/);
});

test('renderBridgePathStatsCard renders bridge path distribution summary', () => {
  const html = hooks.renderBridgePathStatsCard({
    main_clear: { count: 3, total: 10, rate: 0.3 },
    followup_remedy: { count: 4, total: 10, rate: 0.4 },
    knowledge_bailout_success: { count: 2, total: 10, rate: 0.2 },
    knowledge_bailout_failed: { count: 1, total: 10, rate: 0.1 },
  });

  assert.match(html, /过桥路径分布/);
  assert.match(html, /首轮直接过桥/);
  assert.match(html, /补救后过桥/);
  assert.match(html, /知识卡后过桥/);
  assert.match(html, /知识卡后仍未掌握/);
  assert.match(html, /4 \/ 10/);
});
