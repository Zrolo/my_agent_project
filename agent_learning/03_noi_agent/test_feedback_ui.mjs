import fs from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';

const studentLayout = fs.readFileSync(
  new URL('./frontend/src/layouts/StudentLayout.vue', import.meta.url),
  'utf8',
);

const teacherLayout = fs.readFileSync(
  new URL('./frontend/src/layouts/TeacherLayout.vue', import.meta.url),
  'utf8',
);

const router = fs.readFileSync(
  new URL('./frontend/src/router/index.js', import.meta.url),
  'utf8',
);

const apiService = fs.readFileSync(
  new URL('./frontend/src/services/api.js', import.meta.url),
  'utf8',
);

const studentFeedbackPage = fs.readFileSync(
  new URL('./frontend/src/pages/student/FeedbackPage.vue', import.meta.url),
  'utf8',
);

const teacherFeedbackPage = fs.readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherFeedbackPage.vue', import.meta.url),
  'utf8',
);

test('student and teacher navigation expose feedback pages in Chinese', () => {
  assert.match(studentLayout, /使用反馈/);
  assert.match(studentLayout, /\/app\/workspace\/feedback/);
  assert.match(teacherLayout, /反馈/);
  assert.match(teacherLayout, /\/app\/teacher\/feedback/);
});

test('router registers student feedback and teacher feedback pages', () => {
  assert.match(router, /FeedbackPage/);
  assert.match(router, /TeacherFeedbackPage/);
  assert.match(router, /workspace\/feedback/);
  assert.match(router, /teacher-feedback/);
});

test('api service exposes feedback submit and teacher list calls', () => {
  assert.match(apiService, /export function submitStudentFeedback/);
  assert.match(apiService, /\/api\/student\/feedback/);
  assert.match(apiService, /export function getTeacherStudentFeedback/);
  assert.match(apiService, /\/api\/teacher\/student-feedback/);
});

test('student feedback page has a simple Chinese form and validation copy', () => {
  assert.match(studentFeedbackPage, /反馈建议/);
  assert.match(studentFeedbackPage, /这次想反馈什么/);
  assert.match(studentFeedbackPage, /整体感受/);
  assert.match(studentFeedbackPage, /至少写 5 个字/);
  assert.match(studentFeedbackPage, /提交反馈/);
  assert.doesNotMatch(studentFeedbackPage, /JSON\.stringify/);
});

test('teacher feedback page renders submitted feedback as a readable list', () => {
  assert.match(teacherFeedbackPage, /学生反馈/);
  assert.match(teacherFeedbackPage, /反馈内容/);
  assert.match(teacherFeedbackPage, /暂无学生反馈/);
  assert.match(teacherFeedbackPage, /加载反馈/);
  assert.doesNotMatch(teacherFeedbackPage, /<pre/);
  assert.doesNotMatch(teacherFeedbackPage, /JSON\.stringify/);
});
