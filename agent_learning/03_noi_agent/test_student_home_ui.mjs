import fs from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';

const router = fs.readFileSync(
  new URL('./frontend/src/router/index.js', import.meta.url),
  'utf8',
);

const studentLayout = fs.readFileSync(
  new URL('./frontend/src/layouts/StudentLayout.vue', import.meta.url),
  'utf8',
);

const teacherLayout = fs.readFileSync(
  new URL('./frontend/src/layouts/TeacherLayout.vue', import.meta.url),
  'utf8',
);

const apiService = fs.readFileSync(
  new URL('./frontend/src/services/api.js', import.meta.url),
  'utf8',
);

const viteConfig = fs.readFileSync(
  new URL('./vite.config.js', import.meta.url),
  'utf8',
);

const studentHomePagePath = new URL('./frontend/src/pages/student/HomePage.vue', import.meta.url);
const teacherAnnouncementPagePath = new URL('./frontend/src/pages/teacher/TeacherAnnouncementsPage.vue', import.meta.url);

test('student app has a real home route before AIChat', () => {
  assert.match(router, /HomePage/);
  assert.match(router, /path: 'home'/);
  assert.match(router, /redirect: '\/app\/home'/);
  assert.match(studentLayout, /首页/);
  assert.match(studentLayout, /\/app\/home/);
});

test('router lazy-loads page components to keep the entry bundle small', () => {
  assert.match(router, /const HomePage = \(\) => import\('@\/pages\/student\/HomePage\.vue'\)/);
  assert.match(router, /const ChatPage = \(\) => import\('@\/pages\/student\/ChatPage\.vue'\)/);
  assert.match(router, /const TeacherReviewPage = \(\) => import\('@\/pages\/teacher\/TeacherReviewPage\.vue'\)/);
  assert.doesNotMatch(router, /import HomePage from/);
  assert.doesNotMatch(router, /import ChatPage from/);
  assert.doesNotMatch(router, /import TeacherReviewPage from/);
});

test('vite warning limit documents the intentionally lazy-loaded diagram chunk', () => {
  assert.match(viteConfig, /chunkSizeWarningLimit: 700/);
  assert.match(viteConfig, /Mermaid/);
});

test('student home page contains compact learning sections', () => {
  const homePage = fs.readFileSync(studentHomePagePath, 'utf8');

  assert.match(homePage, /教师公告/);
  assert.match(homePage, /继续学习/);
  assert.match(homePage, /我的学习数据/);
  assert.match(homePage, /最近做完的题/);
  assert.match(homePage, /完成方式变化/);
  assert.match(homePage, /support_fadeout_label/);
  assert.match(homePage, /借助 AI 后做出/);
  assert.match(homePage, /你写的是：/);
  assert.match(homePage, /还可以补一句/);
  assert.match(homePage, /最近需要多练的地方/);
  assert.match(homePage, /建议回顾的题/);
  assert.match(homePage, /getStudentHome/);
  assert.match(homePage, /primaryStats/);
  assert.match(homePage, /slice\(0, 4\)/);
  assert.doesNotMatch(homePage, /记录这题完成情况/);
  assert.doesNotMatch(homePage, /AIChat 帮助后完成/);
  assert.doesNotMatch(homePage, /支架撤离趋势/);
  assert.doesNotMatch(homePage, /最近没想明白的地方/);
  assert.doesNotMatch(homePage, /最近常卡的地方/);
  assert.doesNotMatch(homePage, /别让已经会的东西滑走/);
  assert.doesNotMatch(homePage, /这几处可以重点留意/);
  assert.doesNotMatch(homePage, /submitCompletionRecord/);
  assert.doesNotMatch(homePage, /createStudentProblemCompletion/);
  assert.match(apiService, /createStudentProblemCompletion/);
  assert.match(apiService, /\/api\/student\/problem-completions/);
  assert.match(homePage, /points_awarded/);
  assert.doesNotMatch(homePage, /排名第|排行榜第/);
});

test('teacher side exposes markdown announcement management', () => {
  const announcementPage = fs.readFileSync(teacherAnnouncementPagePath, 'utf8');

  assert.match(router, /TeacherAnnouncementsPage/);
  assert.match(router, /teacher-announcements/);
  assert.match(teacherLayout, /公告/);
  assert.match(teacherLayout, /\/app\/teacher\/announcements/);
  assert.match(announcementPage, /公告标题/);
  assert.match(announcementPage, /Markdown/);
  assert.match(announcementPage, /发布公告/);
});

test('api service exposes student home and teacher announcement calls', () => {
  assert.match(apiService, /export function getStudentHome/);
  assert.match(apiService, /\/api\/student\/home/);
  assert.match(apiService, /export function getTeacherAnnouncements/);
  assert.match(apiService, /\/api\/teacher\/announcements/);
  assert.match(apiService, /export function createTeacherAnnouncement/);
});
