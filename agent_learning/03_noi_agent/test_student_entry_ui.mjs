import fs from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';

const chatPage = fs.readFileSync(
  new URL('./frontend/src/pages/student/ChatPage.vue', import.meta.url),
  'utf8',
);

const checkinPage = fs.readFileSync(
  new URL('./frontend/src/pages/student/CheckinPage.vue', import.meta.url),
  'utf8',
);

const archiveDetailPage = fs.readFileSync(
  new URL('./frontend/src/pages/student/ArchiveDetailPage.vue', import.meta.url),
  'utf8',
);

const archiveListPage = fs.readFileSync(
  new URL('./frontend/src/pages/student/ArchiveListPage.vue', import.meta.url),
  'utf8',
);

const loginView = fs.readFileSync(
  new URL('./frontend/src/components/LoginView.vue', import.meta.url),
  'utf8',
);

const apiService = fs.readFileSync(
  new URL('./frontend/src/services/api.js', import.meta.url),
  'utf8',
);

test('chat page does not expose session id as a student-facing field', () => {
  assert.doesNotMatch(chatPage, /会话 ID/);
  assert.doesNotMatch(chatPage, /v-model="sessionId"/);
});

test('checkin page emphasizes the main student inputs before optional supplements', () => {
  assert.match(checkinPage, /我卡在哪里/);
  assert.match(checkinPage, /我已经试过什么/);
  assert.match(checkinPage, /补充信息（可选）/);
  assert.match(checkinPage, /洛谷题号\/链接可自动读取/);
  assert.match(checkinPage, /其他平台请补题目标题和题面/);
});

test('archive detail avoids system-internal summary labels in the primary student view', () => {
  assert.doesNotMatch(archiveDetailPage, /复盘模式/);
  assert.doesNotMatch(archiveDetailPage, /复盘家族/);
  assert.doesNotMatch(archiveDetailPage, /学习状态/);
  assert.match(archiveDetailPage, /这次我卡在哪里/);
});

test('archive list and detail read like learning records instead of system logs', () => {
  assert.match(archiveListPage, /继续看这次复盘/);
  assert.match(archiveListPage, /最后更新/);
  assert.doesNotMatch(archiveListPage, /Archive List/);

  assert.match(archiveDetailPage, /我现在可以继续做什么/);
  assert.doesNotMatch(archiveDetailPage, /Quiz History/);
});

test('archive pages include mobile-safe wrapping for long problem content', () => {
  assert.match(archiveListPage, /min-w-0/);
  assert.match(archiveListPage, /break-words/);
  assert.match(archiveDetailPage, /min-w-0/);
  assert.match(archiveDetailPage, /break-words/);
});

test('archive detail gives pending reviews a clear student-facing state', () => {
  assert.match(archiveDetailPage, /系统正在整理复盘/);
  assert.match(archiveDetailPage, /刷新详情/);
  assert.doesNotMatch(archiveDetailPage, /复盘还在生成中，稍后刷新这里会出现完整内容。/);
});

test('chat and checkin pages prioritize the main student action over system form chrome', () => {
  assert.match(chatPage, /我这次卡在哪一步/);
  assert.equal((checkinPage.match(/完成状态/g) || []).length, 1);
  assert.equal((checkinPage.match(/提交结果/g) || []).length, 1);
});

test('chat page sends current problem context with the student question', () => {
  assert.match(chatPage, /const problemTitle = ref/);
  assert.match(chatPage, /const problemContext = ref/);
  assert.match(chatPage, /v-model="problemTitle"/);
  assert.match(chatPage, /v-model="problemContext"/);
  assert.match(chatPage, /problem_title: problemTitle\.value\.trim\(\)/);
  assert.match(chatPage, /problem_context: problemContext\.value\.trim\(\)/);
  assert.match(chatPage, /student_code: studentCode\.value\.trim\(\)/);
});

test('chat page can hand current problem context to checkin flow', () => {
  assert.match(chatPage, /useRouter/);
  assert.match(chatPage, /function goToCheckinWithCurrentProblem/);
  assert.match(chatPage, /persistProblemContext\(\)/);
  assert.match(chatPage, /router\.push\('\/app\/workspace\/checkin'\)/);
  assert.match(chatPage, /带着当前题去打卡复盘/);

  assert.match(checkinPage, /window\.localStorage\.getItem\('noi-agent-chat-problem-id'\)/);
  assert.match(checkinPage, /window\.localStorage\.getItem\('noi-agent-chat-problem-title'\)/);
  assert.match(checkinPage, /window\.localStorage\.getItem\('noi-agent-chat-problem-context'\)/);
  assert.match(checkinPage, /window\.localStorage\.getItem\('noi-agent-chat-student-code'\)/);
});

test('chat page can visibly import luogu problem context before asking AI', () => {
  assert.match(apiService, /export function importProblem/);
  assert.match(apiService, /\/api\/problem-import/);
  assert.match(chatPage, /importProblem/);
  assert.match(chatPage, /const importingProblem = ref\(false\)/);
  assert.match(chatPage, /async function importCurrentLuoguProblem/);
  assert.match(chatPage, /await importProblem\(auth\.token/);
  assert.match(chatPage, /problemTitle\.value = result\.problem_title/);
  assert.match(chatPage, /problemContext\.value = result\.problem_context/);
  assert.match(chatPage, /读取洛谷题目/);
});

test('chat page lets students clear stale current problem context without exposing session id', () => {
  assert.match(chatPage, /function clearProblemContext/);
  assert.match(chatPage, /problemId\.value = ''/);
  assert.match(chatPage, /problemTitle\.value = ''/);
  assert.match(chatPage, /problemContext\.value = ''/);
  assert.match(chatPage, /studentCode\.value = ''/);
  assert.match(chatPage, /清空当前题背景/);
});

test('login form labels are associated with their inputs for browser walkthroughs', () => {
  assert.match(loginView, /<label[^>]+for="login-user-id"[^>]*>账号<\/label>/);
  assert.match(loginView, /<input[^>]+id="login-user-id"/);
  assert.match(loginView, /<label[^>]+for="login-password"[^>]*>密码<\/label>/);
  assert.match(loginView, /<input[^>]+id="login-password"/);
});

test('checkin main student fields are label-addressable in browser walkthroughs', () => {
  assert.match(checkinPage, /<label[^>]+for="checkin-problem"[^>]*>题目链接 \/ 题号<\/label>/);
  assert.match(checkinPage, /<input[^>]+id="checkin-problem"/);
  assert.match(checkinPage, /<label[^>]+for="checkin-bottleneck"[^>]*>我卡在哪里<\/label>/);
  assert.match(checkinPage, /<textarea[^>]+id="checkin-bottleneck"/);
  assert.match(checkinPage, /<label[^>]+for="checkin-reflection"[^>]*>我已经试过什么<\/label>/);
  assert.match(checkinPage, /<textarea[^>]+id="checkin-reflection"/);
});
