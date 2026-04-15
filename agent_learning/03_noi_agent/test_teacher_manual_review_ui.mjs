import test from 'node:test';
import assert from 'node:assert/strict';
import ui from './static/teacher_manual_review_ui.js';

test('buildTeacherManualReviewPayload trims notes and keeps enum values', () => {
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

test('buildTeacherManualReviewPayload normalizes invalid enum values', () => {
  const payload = ui.buildTeacherManualReviewPayload({
    elements: {
      mode_correct: { value: 'maybe' },
      review_grounded: { value: 'unknown' },
      student_can_move_next: { value: 'later' },
      notes: { value: '' },
    },
  });

  assert.deepEqual(payload, {
    mode_correct: 'unsure',
    review_grounded: 'mixed',
    student_can_move_next: 'unsure',
    notes: '',
  });
});

test('renderTeacherReviewSampleCard shows guided walkthrough before try-now task', () => {
  const successCard = ui.renderTeacherReviewSampleCard({
    review_id: 1,
    checkin_id: 2,
    student_id: 'student_a',
    review_mode: 'independent_reflect',
    review_family: 'success_reflection',
    review_status: 'completed',
    problem_title: '测试题',
    problem_focus: 'A',
    key_bridge: 'B',
    visual_hint: '消息数：M = 50000\n查询数：N = 50000\n\n直接枚举：\n每来一条查询，都要去碰很多条消息',
    guided_walkthrough: 'C',
    try_now: 'D',
    transfer_signal: 'E',
  });
  assert.ok(successCard.indexOf('看图想一想') < successCard.indexOf('跟我走一遍'));
  assert.ok(successCard.indexOf('跟我走一遍') < successCard.indexOf('现在你来试'));

  const failureCard = ui.renderTeacherReviewSampleCard({
    review_id: 1,
    checkin_id: 2,
    student_id: 'student_a',
    review_mode: 'failed_verdict',
    review_family: 'failure_diagnosis',
    review_status: 'completed',
    problem_title: '测试题',
    problem_focus: 'A',
    key_bridge: 'B',
    visual_hint: '消息数：M = 50000\n查询数：N = 50000\n\n直接枚举：\n每来一条查询，都要去碰很多条消息',
    guided_walkthrough: 'C',
    try_now: 'D',
    transfer_signal: 'E',
  });
  assert.ok(failureCard.indexOf('看图想一想') < failureCard.indexOf('跟我走一遍'));
  assert.ok(failureCard.indexOf('跟我走一遍') < failureCard.indexOf('现在你来试'));
});

test('renderTeacherReviewSampleCard uses content-aware label for prose visual_hint', () => {
  const card = ui.renderTeacherReviewSampleCard({
    review_id: 3,
    checkin_id: 4,
    student_id: 'student_a',
    review_mode: 'stuck_bridge',
    review_family: 'failure_diagnosis',
    review_status: 'completed',
    problem_title: '测试题',
    problem_focus: 'A',
    key_bridge: 'B',
    visual_hint: '先比较暴力和 trie 的工作量：一个要反复碰很多消息，一个只沿前缀往下走。',
    guided_walkthrough: 'C',
    try_now: 'D',
    transfer_signal: 'E',
  });

  assert.match(card, /先看这个对比/);
  assert.doesNotMatch(card, /看图想一想/);
});

test('renderTeacherReviewSampleCard shows mastery badge when mastery_status is present', () => {
  const card = ui.renderTeacherReviewSampleCard({
    review_id: 9,
    checkin_id: 10,
    student_id: 'student_a',
    review_mode: 'stuck_bridge',
    review_family: 'failure_diagnosis',
    review_status: 'completed',
    mastery_status: 'assisted_success',
    problem_title: '测试题',
    problem_focus: 'A',
    key_bridge: 'B',
    guided_walkthrough: 'C',
    try_now: 'D',
    transfer_signal: 'E',
  });

  assert.match(card, /辅助后过桥/);
});
