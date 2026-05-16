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

const accountsPagePath = new URL('./frontend/src/pages/teacher/TeacherAccountsPage.vue', import.meta.url);
const accountsPage = fs.existsSync(accountsPagePath) ? fs.readFileSync(accountsPagePath, 'utf8') : '';

const advancedPagePath = new URL('./frontend/src/pages/teacher/TeacherAdvancedPage.vue', import.meta.url);
const advancedPage = fs.existsSync(advancedPagePath) ? fs.readFileSync(advancedPagePath, 'utf8') : '';

const teacherLayout = fs.readFileSync(
  new URL('./frontend/src/layouts/TeacherLayout.vue', import.meta.url),
  'utf8',
);

const routerSource = fs.readFileSync(
  new URL('./frontend/src/router/index.js', import.meta.url),
  'utf8',
);

const apiService = fs.readFileSync(
  new URL('./frontend/src/services/api.js', import.meta.url),
  'utf8',
);

const checkinsPage = fs.readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherCheckinsPage.vue', import.meta.url),
  'utf8',
);

const reflectionPagePath = new URL('./frontend/src/pages/teacher/TeacherReflectionPage.vue', import.meta.url);
const reflectionPage = fs.existsSync(reflectionPagePath) ? fs.readFileSync(reflectionPagePath, 'utf8') : '';

const classManagementPagePath = new URL('./frontend/src/pages/teacher/TeacherClassManagementPage.vue', import.meta.url);
const classManagementPage = fs.existsSync(classManagementPagePath) ? fs.readFileSync(classManagementPagePath, 'utf8') : '';

const aichatHistoryPagePath = new URL('./frontend/src/pages/teacher/TeacherAIChatHistoryPage.vue', import.meta.url);
const aichatHistoryPage = fs.existsSync(aichatHistoryPagePath) ? fs.readFileSync(aichatHistoryPagePath, 'utf8') : '';

const studentDossierPagePath = new URL('./frontend/src/pages/teacher/TeacherStudentDossierPage.vue', import.meta.url);
const studentDossierPage = fs.existsSync(studentDossierPagePath) ? fs.readFileSync(studentDossierPagePath, 'utf8') : '';

test('teacher vue pages avoid raw json dumps in the primary UI', () => {
  for (const source of [overviewPage, reviewPage, studentsPage]) {
    assert.doesNotMatch(source, /JSON\.stringify/);
    assert.doesNotMatch(source, /<pre/);
  }
});

test('teacher pages expose stable product headings for real walkthroughs', () => {
  assert.match(overviewPage, /今日带班/);
  assert.match(overviewPage, /今天先看谁/);
  assert.match(overviewPage, /班级最近主要问题/);
  assert.match(reviewPage, /待人工复核样例/);
  assert.match(studentsPage, /学生档案入口/);
  assert.match(accountsPage, /创建学生账号/);
  assert.match(advancedPage, /系统维护/);
  assert.match(checkinsPage, /复盘生成队列/);
});

test('teacher navigation keeps only daily teaching workflows in the main nav', () => {
  for (const label of ['首页', '学生', '复盘', '班级管理']) {
    assert.match(teacherLayout, new RegExp(`label: '${label}'`));
  }
  for (const oldLabel of ['学习记录', '账号', '复核', '公告', '反馈', '高级']) {
    assert.doesNotMatch(teacherLayout, new RegExp(`label: '${oldLabel}'`));
  }
  assert.doesNotMatch(teacherLayout, /to="\/app\/teacher\/advanced"/);
  assert.match(routerSource, /TeacherAccountsPage/);
  assert.match(routerSource, /TeacherAIChatHistoryPage/);
  assert.match(routerSource, /TeacherReflectionPage/);
  assert.match(routerSource, /TeacherClassManagementPage/);
  assert.match(routerSource, /path: 'reflection'/);
  assert.match(routerSource, /path: 'class-management'/);
  assert.match(routerSource, /\/app\/teacher\/advanced/);
  assert.match(routerSource, /tab: 'advanced'/);
  assert.match(routerSource, /path: 'aichat-history'/);
});

test('teacher reflection page merges checkin records and manual review', () => {
  assert.match(reflectionPage, /教学复盘/);
  assert.match(reflectionPage, /待人工复核/);
  assert.match(reflectionPage, /复盘生成队列/);
  assert.match(reflectionPage, /const activeTab = computed\(\(\) => \(route\.query\.tab === 'checkins' \? 'checkins' : 'review'\)\)/);
  assert.match(reflectionPage, /TeacherCheckinsPage/);
  assert.match(reflectionPage, /TeacherReviewPage/);
});

test('teacher class management page merges account announcement and feedback tools', () => {
  assert.match(classManagementPage, /学生账号/);
  assert.match(classManagementPage, /公告/);
  assert.match(classManagementPage, /学生反馈/);
  assert.match(classManagementPage, /系统维护/);
  assert.match(classManagementPage, /TeacherAccountsPage/);
  assert.match(classManagementPage, /TeacherAnnouncementsPage/);
  assert.match(classManagementPage, /TeacherFeedbackPage/);
  assert.match(classManagementPage, /TeacherAdvancedPage/);
});

test('teacher AIChat evidence page presents a teacher diagnosis workflow', () => {
  assert.match(apiService, /export function getTeacherAIChatStudents/);
  assert.match(apiService, /\/api\/teacher\/aichat_students/);
  assert.match(apiService, /export function getTeacherAIChatSessions/);
  assert.match(apiService, /\/api\/teacher\/aichat_sessions/);
  assert.match(apiService, /export function getTeacherAIChatSessionDetail/);
  assert.match(apiService, /\/api\/teacher\/aichat_session_detail/);
  assert.match(apiService, /export function getTeacherAIChatSessionAnalysisHealth/);
  assert.match(aichatHistoryPage, /AI 对话学习记录/);
  assert.match(aichatHistoryPage, /总结状态/);
  assert.match(aichatHistoryPage, /关注队列/);
  assert.match(aichatHistoryPage, /会话概况/);
  assert.match(aichatHistoryPage, /教师诊断/);
  assert.match(aichatHistoryPage, /老师可以怎么帮/);
  assert.match(aichatHistoryPage, /展开完整对话/);
  assert.match(aichatHistoryPage, /展开系统证据/);
  assert.match(aichatHistoryPage, /理解证据/);
  assert.match(aichatHistoryPage, /同点打转/);
  assert.match(aichatHistoryPage, /系统判断的引导方式/);
  assert.doesNotMatch(aichatHistoryPage, /AIChat 学习证据/);
  assert.doesNotMatch(aichatHistoryPage, />完整对话</);
  assert.doesNotMatch(aichatHistoryPage, /judge_action_subtype/);
});

test('teacher overview focuses on class learning diagnosis sections', () => {
  assert.match(apiService, /export function getTeacherClassLearningDiagnosis/);
  assert.match(apiService, /\/api\/teacher\/class-learning-diagnosis/);
  assert.match(overviewPage, /getTeacherClassLearningDiagnosis/);
  assert.match(overviewPage, /今天建议关注/);
  assert.match(overviewPage, /班级最近主要问题/);
  assert.match(overviewPage, /最近练习概况/);
  assert.match(overviewPage, /查看学生详情/);
  assert.doesNotMatch(overviewPage, /完整对话/);
});

test('teacher student dossier page separates recent learning data into tabs', () => {
  assert.match(apiService, /export function getTeacherStudentDossier/);
  assert.match(apiService, /\/api\/teacher\/student-dossier/);
  assert.match(apiService, /export function createTeacherStudentNote/);
  assert.match(apiService, /\/api\/teacher\/student-notes/);
  assert.match(routerSource, /TeacherStudentDossierPage/);
  assert.match(routerSource, /path: 'students\/:studentId'/);
  for (const label of ['概况', '做题记录', '理解与复盘', 'AIChat 证据', '老师记录']) {
    assert.match(studentDossierPage, new RegExp(label));
  }
  assert.match(studentDossierPage, /最近 15 天完成题数/);
  assert.match(studentDossierPage, /独立程度趋势/);
  assert.match(studentDossierPage, /基本能独立完成/);
  assert.match(studentDossierPage, /少量提示能完成/);
  assert.match(studentDossierPage, /需要较多帮助/);
  assert.match(studentDossierPage, /缺少完成证据/);
  assert.match(studentDossierPage, /完成方式占比/);
  assert.match(studentDossierPage, /methodShareRows/);
  assert.match(studentDossierPage, /下一道巩固题/);
  assert.match(studentDossierPage, /practiceRecommendations/);
  assert.match(studentDossierPage, /与上个 15 天相比/);
  assert.match(studentDossierPage, /periodComparison/);
  assert.match(studentDossierPage, /完成质量概览/);
  assert.match(studentDossierPage, /toggleSessionDetail/);
  assert.match(studentDossierPage, /getTeacherAIChatSessionDetail/);
  assert.match(studentDossierPage, /getTeacherAIChatSessionAnalysis/);
  assert.match(studentDossierPage, /retryTeacherAIChatSessionAnalysis/);
  assert.match(studentDossierPage, /会话总结分析器/);
  assert.match(studentDossierPage, /重新生成会话总结/);
  assert.match(studentDossierPage, /生成中/);
  assert.match(studentDossierPage, /AI 教练/);
  assert.match(studentDossierPage, /保存老师记录/);
  assert.match(studentDossierPage, /干预记录/);
  assert.match(studentDossierPage, /干预方式/);
  assert.match(studentDossierPage, /针对问题/);
  assert.match(studentDossierPage, /后续观察/);
});

test('teacher pages show readable empty states instead of blank panels', () => {
  assert.match(reviewPage, /暂无待复核样例/);
  assert.match(studentsPage, /暂无学生记录/);
  assert.match(studentsPage, /暂无明确关注原因/);
  assert.match(checkinsPage, /暂无复盘生成队列记录/);
});

test('teacher students page is a slim student dossier entry, not another evidence dashboard', () => {
  assert.match(apiService, /export function getTeacherAIChatObservations/);
  assert.match(apiService, /\/api\/teacher\/aichat-observations/);
  assert.match(studentsPage, /getTeacherAIChatObservations/);
  assert.match(studentsPage, /学生档案入口/);
  assert.match(studentsPage, /学生：/);
  assert.match(studentsPage, /账号：/);
  assert.match(studentsPage, /查看学习记录/);
  assert.match(studentsPage, /查看复盘/);
  assert.match(studentsPage, /进入学生档案/);
  assert.match(studentsPage, /`\/app\/teacher\/students\/\$\{row.student_id\}`/);
  assert.doesNotMatch(studentsPage, /AIChat 学习观察/);
  assert.doesNotMatch(studentsPage, /visibleAichatObservations/);
  assert.doesNotMatch(studentsPage, /observationCurrentPage/);
  assert.doesNotMatch(studentsPage, /最近学生问题/);
});

test('teacher account lifecycle lives on the account page instead of the student diagnosis page', () => {
  assert.match(accountsPage, /createTeacherStudent/);
  assert.match(accountsPage, /createTeacherStudentsBulk/);
  assert.match(accountsPage, /resetTeacherStudentPassword/);
  assert.match(accountsPage, /updateTeacherStudentStatus/);
  assert.match(accountsPage, /创建学生账号/);
  assert.match(accountsPage, /批量创建账号/);
  assert.match(accountsPage, /学生账号状态/);
  assert.match(accountsPage, /修改学生密码/);
  assert.match(accountsPage, /新学生密码/);
  assert.match(accountsPage, /确认学生密码/);
  assert.match(accountsPage, /passwordEditForm\.password/);
  assert.match(accountsPage, /password: passwordEditForm\.password\.trim\(\)/);
  assert.doesNotMatch(accountsPage, /resetTeacherStudentPassword\(auth\.token,\s*student\.user_id,\s*\{\}\s*\)/);
  assert.doesNotMatch(studentsPage, /创建学生账号/);
  assert.doesNotMatch(studentsPage, /批量创建账号/);
});

test('teacher shell lets teachers change their own password explicitly', () => {
  assert.match(apiService, /export function changeTeacherPassword/);
  assert.match(apiService, /\/api\/teacher\/change-password/);
  assert.match(teacherLayout, /修改密码/);
  assert.match(teacherLayout, /当前密码/);
  assert.match(teacherLayout, /新密码/);
  assert.match(teacherLayout, /确认新密码/);
  assert.match(teacherLayout, /changeTeacherPassword/);
  assert.doesNotMatch(teacherLayout, /随机生成/);
});

test('teacher overview uses learning issue categories instead of raw keyword frequency', () => {
  assert.match(overviewPage, /learningIssueRows/);
  assert.match(overviewPage, /teachingSliceRows/);
  assert.match(overviewPage, /题意没读透/);
  assert.match(overviewPage, /知道算法但不会落题/);
  assert.match(overviewPage, /代码实现卡住/);
  assert.match(overviewPage, /调试定位困难/);
  assert.match(overviewPage, /复杂度判断薄弱/);
  assert.match(overviewPage, /同类迁移困难/);
  assert.match(overviewPage, /涉及学生/);
  assert.match(overviewPage, /建议讲法/);
  assert.match(overviewPage, /推荐练习/);
  assert.match(overviewPage, /讲解要点/);
  assert.match(overviewPage, /课堂活动/);
  assert.doesNotMatch(overviewPage, /关键转化没接上/);
  assert.doesNotMatch(overviewPage, /复杂度 \/ 边界问题/);
  assert.doesNotMatch(overviewPage, /高频引导点分布/);
});

test('teacher overview turns data into actionable attention and suggestions', () => {
  assert.match(overviewPage, /attentionStudents/);
  assert.match(overviewPage, /今天建议关注/);
  assert.match(overviewPage, /学习证据不足/);
  assert.match(overviewPage, /已验证理解/);
  assert.match(overviewPage, /缺少验证证据/);
  assert.match(overviewPage, /独立完成比例/);
  assert.match(overviewPage, /independence_ratio/);
  assert.match(overviewPage, /本周教学建议/);
  assert.match(overviewPage, /最多 3 条/);
});

test('teacher students page explains student status and completion evidence', () => {
  assert.match(studentsPage, /当前状态/);
  assert.match(studentsPage, /最近信号/);
  assert.match(studentsPage, /老师下一步/);
  assert.match(studentsPage, /做题记录/);
  assert.doesNotMatch(studentsPage, /支架撤离趋势/);
  assert.match(studentsPage, /暂时无法判断学习情况/);
});

test('teacher students page shows attention reasons with evidence and next action', () => {
  assert.match(studentsPage, /getTeacherClassLearningDiagnosis/);
  assert.match(studentsPage, /关注原因/);
  assert.match(studentsPage, /证据来源/);
  assert.match(studentsPage, /老师下一步建议/);
  assert.match(studentsPage, /人工标记，暂无具体原因/);
  assert.doesNotMatch(studentsPage, /需要关注标记/);
  assert.doesNotMatch(studentsPage, /暂无说明/);
});

test('teacher students page paginates long learning cards', () => {
  assert.match(studentsPage, /const pageSize = 5/);
  assert.match(studentsPage, /visibleStudentRows/);
  assert.match(studentsPage, /visibleAttentionRows/);
  assert.match(studentsPage, /上一页/);
  assert.match(studentsPage, /下一页/);
});

test('teacher review page shows bridge routing as readable fields', () => {
  assert.match(reviewPage, /引导方式观察/);
  assert.match(reviewPage, /已稳定引导/);
  assert.match(reviewPage, /待确认引导/);
  assert.match(reviewPage, /置信度/);
  assert.match(reviewPage, /命中信号/);
  assert.match(reviewPage, /冲突信号/);
});

test('teacher review page can filter samples by bridge route status', () => {
  assert.match(reviewPage, /routeFilter/);
  assert.match(reviewPage, /全部样例/);
  assert.match(reviewPage, /只看待确认引导/);
  assert.match(reviewPage, /只看新发现引导/);
  assert.match(reviewPage, /只看已稳定引导/);
});

test('teacher review page supports student and problem filtering', () => {
  assert.match(reviewPage, /studentFilter/);
  assert.match(reviewPage, /problemFilter/);
  assert.match(reviewPage, /masteryFilter/);
  assert.match(reviewPage, /按学生账号或姓名筛选/);
  assert.match(reviewPage, /按题号或题目筛选/);
  assert.match(reviewPage, /需要老师跟进/);
  assert.match(reviewPage, /暂未掌握/);
  assert.match(reviewPage, /已掌握/);
});

test('teacher review page paginates and collapses review cards', () => {
  assert.match(reviewPage, /const pageSize = 5/);
  assert.match(reviewPage, /visibleSamples/);
  assert.match(reviewPage, /currentPage/);
  assert.match(reviewPage, /上一页/);
  assert.match(reviewPage, /下一页/);
  assert.match(reviewPage, /展开详情/);
  assert.match(reviewPage, /收起详情/);
  assert.match(reviewPage, /isSampleExpanded/);
});

test('teacher checkins page paginates record cards', () => {
  assert.match(checkinsPage, /const pageSize = 5/);
  assert.match(checkinsPage, /visibleCheckins/);
  assert.match(checkinsPage, /currentPage/);
  assert.match(checkinsPage, /上一页/);
  assert.match(checkinsPage, /下一页/);
  assert.match(checkinsPage, /生成失败/);
  assert.match(checkinsPage, /题目信息缺失/);
  assert.match(checkinsPage, /下一步/);
});

test('teacher review page presents review cards as teacher-facing summaries', () => {
  assert.match(reviewPage, /复盘概况/);
  assert.match(reviewPage, /这次复盘概况/);
  assert.match(reviewPage, /学生这次没想明白什么/);
  assert.match(reviewPage, /系统怎么帮他走了一步/);
  assert.match(reviewPage, /复盘是否靠谱/);
  assert.match(reviewPage, /系统调试信息/);
  assert.doesNotMatch(reviewPage, /样例摘要/);
});

test('teacher overview keeps legacy rule operations out of the primary dashboard', () => {
  assert.doesNotMatch(overviewPage, /高级：系统规则与旧统计/);
  assert.doesNotMatch(overviewPage, /AI 规则草稿/);
  assert.doesNotMatch(overviewPage, /人工确认规则/);
  assert.doesNotMatch(overviewPage, /转正规则建议/);
  assert.doesNotMatch(overviewPage, /引导方式审查/);
  assert.match(advancedPage, /系统维护/);
  assert.match(advancedPage, /AI 规则草稿/);
  assert.match(advancedPage, /需要教师确认/);
  assert.match(advancedPage, /不会自动应用/);
  assert.match(advancedPage, /草案文件/);
  assert.match(advancedPage, /草案状态/);
  assert.match(advancedPage, /下载草案/);
  assert.match(advancedPage, /确认进入草案池/);
  assert.match(advancedPage, /confirmBridgeRuleDraft/);
  assert.match(advancedPage, /草案审查历史/);
  assert.match(advancedPage, /加载历史/);
  assert.match(advancedPage, /人工确认规则/);
  assert.match(advancedPage, /登记到人工规则簿/);
  assert.match(advancedPage, /自动匹配暂未启用/);
  assert.match(advancedPage, /代码改动草稿/);
  assert.match(advancedPage, /草稿未应用/);
  assert.match(advancedPage, /generateResolverPatchDraft/);
});

test('teacher pages avoid exposing internal English status words as visible labels', () => {
  for (const source of [overviewPage, reviewPage, checkinsPage]) {
    const template = source.split('<template>')[1] || source;
    assert.doesNotMatch(template, />\\s*(Overview|Manual Review|Checkins|Review #|Checkin #)\\s*</);
    assert.doesNotMatch(template, /registry 未启用|resolver|patch 草案|draft_only|unknown|unfinished|pending/);
    assert.match(source, /状态/);
  }
  assert.match(reviewPage, /completionStatusText/);
  assert.match(reviewPage, /submissionResultText/);
  assert.match(reviewPage, /errorLayerText/);
  assert.match(reviewPage, /masteryStatusText/);
  assert.match(checkinsPage, /reviewStatusText/);
  assert.match(checkinsPage, /completionStatusText/);
});
