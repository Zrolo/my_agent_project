import test from 'node:test';
import assert from 'node:assert/strict';
import ui from './static/review_family_ui.js';

test('reviewFieldOrder puts guided_walkthrough before try_now for failure family', () => {
  assert.deepEqual(
    ui.reviewFieldOrder('failure_diagnosis'),
    ['problem_focus', 'key_bridge', 'visual_hint', 'guided_walkthrough', 'try_now', 'transfer_signal'],
  );
});

test('reviewFieldOrder keeps guided walkthrough central for success family', () => {
  assert.deepEqual(
    ui.reviewFieldOrder('success_reflection'),
    ['problem_focus', 'key_bridge', 'visual_hint', 'guided_walkthrough', 'try_now', 'transfer_signal'],
  );
});

test('reviewFeedbackCopy returns family-aware wording', () => {
  const failureCopy = ui.reviewFeedbackCopy('failure_diagnosis');
  assert.match(failureCopy.title, /先查哪一步/);
  const successCopy = ui.reviewFeedbackCopy('success_reflection');
  assert.match(successCopy.title, /为什么这样做对/);
});

test('resolveReviewFamily prefers explicit family and otherwise falls back to mode', () => {
  assert.equal(ui.resolveReviewFamily({ review_family: 'success_reflection' }), 'success_reflection');
  assert.equal(ui.resolveReviewFamily({ review_mode: 'editorial_transfer' }), 'failure_diagnosis');
  assert.equal(ui.resolveReviewFamily({ review_mode: 'independent_reflect' }), 'success_reflection');
});

test('orderedReviewSections follows success family order', () => {
  const sections = ui.orderedReviewSections(
    {
      problem_focus: 'A',
      key_bridge: 'B',
      visual_hint: 'B.5',
      guided_walkthrough: 'C',
      try_now: 'D',
      transfer_signal: 'E',
    },
    'success_reflection',
  );
  assert.deepEqual(
    sections.map((item) => item.field),
    ['problem_focus', 'key_bridge', 'visual_hint', 'guided_walkthrough', 'try_now', 'transfer_signal'],
  );
});

test('orderedReviewSections falls back from legacy fields', () => {
  const sections = ui.orderedReviewSections(
    {
      main_block: 'legacy focus',
      key_bridge: 'bridge',
      next_step: 'legacy step',
      transfer_signal: 'signal',
    },
    'failure_diagnosis',
  );
  assert.equal(sections.find((item) => item.field === 'problem_focus').value, 'legacy focus');
  assert.equal(sections.find((item) => item.field === 'try_now').value, 'legacy step');
  assert.equal(sections.find((item) => item.field === 'guided_walkthrough').value, '');
});

test('reviewFieldLabel returns readable label for visual_hint', () => {
  assert.equal(
    ui.reviewFieldLabel(
      'visual_hint',
      '消息数：M = 50000\n查询数：N = 50000\n\n直接枚举：\n每来一条查询，都要去碰很多条消息',
    ),
    '看图想一想',
  );
});

test('reviewFieldLabel downgrades prose visual_hint to comparison wording', () => {
  assert.equal(
    ui.reviewFieldLabel(
      'visual_hint',
      '先比较暴力和 trie 的工作量：一个要反复碰很多消息，一个只沿前缀往下走。',
    ),
    '先看这个对比',
  );
});

test('orderedReviewSections uses content-aware label for visual_hint', () => {
  const sections = ui.orderedReviewSections(
    {
      problem_focus: 'A',
      key_bridge: 'B',
      visual_hint: '先比较暴力和 trie 的工作量：一个要反复碰很多消息，一个只沿前缀往下走。',
      guided_walkthrough: 'C',
      try_now: 'D',
      transfer_signal: 'E',
    },
    'failure_diagnosis',
  );
  assert.equal(sections.find((item) => item.field === 'visual_hint').label, '先看这个对比');
});

test('feedbackEventFields maps confused failure feedback to no_next_step', () => {
  assert.deepEqual(
    ui.feedbackEventFields('failure_diagnosis', 'confused'),
    {
      student_feedback: 'confused',
      bad_reason: 'no_next_step',
      followup_clicked: false,
      followup_question_count: 0,
    },
  );
});

test('feedbackEventFields maps confused success feedback to still_cant_apply', () => {
  assert.deepEqual(
    ui.feedbackEventFields('success_reflection', 'confused'),
    {
      student_feedback: 'confused',
      bad_reason: 'still_cant_apply',
      followup_clicked: false,
      followup_question_count: 0,
    },
  );
});
