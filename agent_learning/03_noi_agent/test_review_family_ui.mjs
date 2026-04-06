import test from 'node:test';
import assert from 'node:assert/strict';
import ui from './static/review_family_ui.js';

test('reviewFieldOrder puts next_step before transfer_signal for failure family', () => {
  assert.deepEqual(
    ui.reviewFieldOrder('failure_diagnosis'),
    ['main_block', 'key_bridge', 'next_step', 'transfer_signal'],
  );
});

test('reviewFieldOrder puts transfer_signal before next_step for success family', () => {
  assert.deepEqual(
    ui.reviewFieldOrder('success_reflection'),
    ['main_block', 'key_bridge', 'transfer_signal', 'next_step'],
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
      main_block: 'A',
      key_bridge: 'B',
      next_step: 'C',
      transfer_signal: 'D',
    },
    'success_reflection',
  );
  assert.deepEqual(sections.map((item) => item.field), ['main_block', 'key_bridge', 'transfer_signal', 'next_step']);
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
