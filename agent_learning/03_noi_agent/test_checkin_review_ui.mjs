import test from 'node:test';
import assert from 'node:assert/strict';
import ui from './static/checkin_review_ui.js';

test('checkinStage returns input when no active item exists', () => {
  assert.equal(ui.checkinStage(null), 'input');
});

test('checkinStage returns review when an active item exists', () => {
  assert.equal(ui.checkinStage({ id: 1 }), 'review');
});

test('checkinSummaryPills keeps only compact summary fields', () => {
  assert.deepEqual(
    ui.checkinSummaryPills({
      problem_title: 'P1001 A+B Problem',
      completion_status_text: '独立完成',
      submission_result_text: 'WA',
      oj_source_text: '洛谷',
    }).map((item) => item.label),
    ['题目', '状态', '提交', '来源'],
  );
});

test('compactStudentInputSections removes empty student input blocks', () => {
  assert.deepEqual(
    ui.compactStudentInputSections({
      problem_context: '题面内容',
      bottleneck_text: '我卡在状态设计',
      reflection: '',
      student_code: '',
    }).map((item) => item.label),
    ['题面 / 题意', '卡点描述'],
  );
});

test('reviewStageLead reflects review status', () => {
  assert.match(ui.reviewStageLead({ review_status: 'completed' }), /先读这次复盘/);
  assert.match(ui.reviewStageLead({ review_status: 'failed' }), /暂时没有成功生成/);
});

test('reviewStageLead uses learning-canvas wording for the completed state', () => {
  assert.match(
    ui.reviewStageLead({ review_status: 'completed' }),
    /先读这次复盘，再继续做下面这一小步/,
  );
});

test('entryStageLead describes the learning record flow', () => {
  assert.match(ui.entryStageLead(), /记下来/);
  assert.match(ui.entryStageLead(), /复盘讲义/);
});
