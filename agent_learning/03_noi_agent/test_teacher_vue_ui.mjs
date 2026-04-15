import fs from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';

const overviewPage = fs.readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherOverviewPage.vue', import.meta.url),
  'utf8',
);

const reviewPage = fs.readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherReviewPage.vue', import.meta.url),
  'utf8',
);

const studentsPage = fs.readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherStudentsPage.vue', import.meta.url),
  'utf8',
);

const checkinsPage = fs.readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherCheckinsPage.vue', import.meta.url),
  'utf8',
);

test('teacher vue pages avoid raw json dumps in the primary UI', () => {
  for (const source of [overviewPage, reviewPage, studentsPage]) {
    assert.doesNotMatch(source, /JSON\.stringify/);
    assert.doesNotMatch(source, /<pre/);
  }
});

test('teacher pages expose stable product headings for real walkthroughs', () => {
  assert.match(overviewPage, /核心统计/);
  assert.match(overviewPage, /桥路由审查/);
  assert.match(reviewPage, /待人工复核样例/);
  assert.match(studentsPage, /学生维度/);
  assert.match(checkinsPage, /打卡记录/);
});

test('teacher pages show readable empty states instead of blank panels', () => {
  assert.match(reviewPage, /暂无待复核样例/);
  assert.match(studentsPage, /暂无学生记录/);
  assert.match(checkinsPage, /暂无打卡记录/);
});

test('teacher review page shows bridge routing as readable fields', () => {
  assert.match(reviewPage, /桥路由观测/);
  assert.match(reviewPage, /稳定桥/);
  assert.match(reviewPage, /候选桥/);
  assert.match(reviewPage, /置信度/);
  assert.match(reviewPage, /命中信号/);
  assert.match(reviewPage, /冲突信号/);
});

test('teacher review page can filter samples by bridge route status', () => {
  assert.match(reviewPage, /routeFilter/);
  assert.match(reviewPage, /全部样例/);
  assert.match(reviewPage, /只看候选桥/);
  assert.match(reviewPage, /只看开放桥/);
  assert.match(reviewPage, /只看稳定桥/);
});

test('teacher overview page shows bridge promotion suggestions as review-only', () => {
  assert.match(overviewPage, /转正规则建议/);
  assert.match(overviewPage, /需要教师确认/);
  assert.match(overviewPage, /不会自动转正/);
  assert.match(overviewPage, /草案文件/);
  assert.match(overviewPage, /草案状态/);
  assert.match(overviewPage, /下载草案/);
  assert.match(overviewPage, /确认进入草案池/);
  assert.match(overviewPage, /confirmBridgeRuleDraft/);
  assert.match(overviewPage, /草案审查历史/);
  assert.match(overviewPage, /加载历史/);
  assert.match(overviewPage, /正式 bridge registry/);
  assert.match(overviewPage, /登记到 registry/);
  assert.match(overviewPage, /resolver 未启用/);
  assert.match(overviewPage, /resolver patch 草案/);
  assert.match(overviewPage, /patch 草案未应用/);
  assert.match(overviewPage, /generateResolverPatchDraft/);
});
