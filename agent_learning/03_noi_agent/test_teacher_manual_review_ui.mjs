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

test('renderTeacherReviewSampleCard follows family-aware review field order', () => {
  const successCard = ui.renderTeacherReviewSampleCard({
    review_id: 1,
    checkin_id: 2,
    student_id: 'student_a',
    review_mode: 'independent_reflect',
    review_family: 'success_reflection',
    review_status: 'completed',
    problem_title: '测试题',
    main_block: 'A',
    key_bridge: 'B',
    next_step: 'C',
    transfer_signal: 'D',
  });
  assert.ok(successCard.indexOf('下次提醒') < successCard.indexOf('现在先做'));

  const failureCard = ui.renderTeacherReviewSampleCard({
    review_id: 1,
    checkin_id: 2,
    student_id: 'student_a',
    review_mode: 'failed_verdict',
    review_family: 'failure_diagnosis',
    review_status: 'completed',
    problem_title: '测试题',
    main_block: 'A',
    key_bridge: 'B',
    next_step: 'C',
    transfer_signal: 'D',
  });
  assert.ok(failureCard.indexOf('现在先做') < failureCard.indexOf('下次提醒'));
});
