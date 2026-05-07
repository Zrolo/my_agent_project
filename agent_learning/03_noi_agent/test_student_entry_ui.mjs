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

const knowledgePage = fs.readFileSync(
  new URL('./frontend/src/pages/student/KnowledgePage.vue', import.meta.url),
  'utf8',
);

const loginView = fs.readFileSync(
  new URL('./frontend/src/components/LoginView.vue', import.meta.url),
  'utf8',
);

const studentLayout = fs.readFileSync(
  new URL('./frontend/src/layouts/StudentLayout.vue', import.meta.url),
  'utf8',
);

const studentRouter = fs.readFileSync(
  new URL('./frontend/src/router/index.js', import.meta.url),
  'utf8',
);

const teacherStudentsPage = fs.readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherStudentsPage.vue', import.meta.url),
  'utf8',
);

const teacherAccountsPage = fs.readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherAccountsPage.vue', import.meta.url),
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

const apiServer = fs.readFileSync(
  new URL('./api_server.py', import.meta.url),
  'utf8',
);

const frontendStyles = fs.readFileSync(
  new URL('./frontend/src/styles.css', import.meta.url),
  'utf8',
);

function extractBetween(source, start, end) {
  const startIndex = source.indexOf(start);
  const endIndex = source.indexOf(end, startIndex + start.length);
  assert.notEqual(startIndex, -1, `missing start marker: ${start}`);
  assert.notEqual(endIndex, -1, `missing end marker: ${end}`);
  return source.slice(startIndex, endIndex);
}

test('chat page does not expose session id as a student-facing field', () => {
  assert.doesNotMatch(chatPage, /会话 ID/);
  assert.doesNotMatch(chatPage, /v-model="sessionId"/);
});

test('chat page does not require crypto.randomUUID for Windows browser compatibility', () => {
  assert.match(chatPage, /function createChatSessionId/);
  assert.doesNotMatch(chatPage, /\|\| crypto\.randomUUID\(\)/);
  assert.doesNotMatch(chatPage, /sessionId\.value = crypto\.randomUUID\(\)/);
  assert.match(chatPage, /window\.crypto\?\.randomUUID/);
  assert.match(chatPage, /Date\.now\(\)/);
});

test('checkin page emphasizes the main student inputs before optional supplements', () => {
  assert.match(checkinPage, /我哪里没想明白/);
  assert.match(checkinPage, /我已经试过什么/);
  assert.match(checkinPage, /补充信息（可选）/);
  assert.match(checkinPage, /洛谷和 JMYSOJ 链接可自动读取/);
  assert.match(checkinPage, /其他平台请补题目标题和题面/);
  assert.match(checkinPage, /workspace-card-checkin mx-auto w-full max-w-5xl/);
  assert.doesNotMatch(checkinPage, /Check-in Flow/);
  assert.doesNotMatch(checkinPage, /先写什么/);
  assert.doesNotMatch(checkinPage, /提交后会发生什么/);
});

test('student-facing pages avoid internal bottleneck wording', () => {
  const visibleStudentPages = [
    chatPage,
    checkinPage,
    archiveDetailPage,
    archiveListPage,
    knowledgePage,
  ].join('\n');
  assert.doesNotMatch(visibleStudentPages, /卡点/);
  assert.match(checkinPage, /问题类型/);
  assert.match(chatPage, /问题类型/);
  assert.match(archiveDetailPage, /和我这次问题的关系/);
});

test('checkin page uses an explicit collapsible optional section', () => {
  assert.match(checkinPage, /const optionalFieldsOpen = ref\(false\)/);
  assert.match(checkinPage, /optionalFieldsOpen = !optionalFieldsOpen/);
  assert.match(checkinPage, /展开补充信息/);
  assert.match(checkinPage, /收起补充信息/);
  assert.match(checkinPage, /v-if="optionalFieldsOpen"/);
  assert.doesNotMatch(checkinPage, /<details/);
  assert.doesNotMatch(checkinPage, /<summary/);
});

test('archive detail avoids system-internal summary labels in the primary student view', () => {
  assert.doesNotMatch(archiveDetailPage, /复盘模式/);
  assert.doesNotMatch(archiveDetailPage, /复盘家族/);
  assert.doesNotMatch(archiveDetailPage, /学习状态/);
  assert.match(archiveDetailPage, /这次我哪里没想明白/);
});

test('archive detail localizes statuses and avoids internal English labels', () => {
  assert.match(archiveDetailPage, /function reviewStatusLabel/);
  assert.match(archiveDetailPage, /function completionStatusLabel/);
  assert.match(archiveDetailPage, /function submissionResultLabel/);
  assert.match(archiveDetailPage, /复盘已生成/);
  assert.match(archiveDetailPage, /独立完成/);
  assert.match(archiveDetailPage, /已通过 AC/);
  assert.doesNotMatch(archiveDetailPage, /Archive Detail/);
  assert.doesNotMatch(archiveDetailPage, /Check-in/);
  assert.doesNotMatch(archiveDetailPage, /Learning Chain/);
  assert.doesNotMatch(archiveDetailPage, /系统是怎么一步步带我过桥的/);
  assert.doesNotMatch(archiveDetailPage, /\{\{\s*detail\.completion_status \|\| '—'\s*\}\}/);
  assert.doesNotMatch(archiveDetailPage, /\{\{\s*detail\.submission_result \|\| '—'\s*\}\}/);
});

test('archive list localizes status and stage labels for students', () => {
  assert.match(archiveListPage, /const RUNTIME_STAGE_LABELS/);
  assert.match(archiveListPage, /function stageLabel/);
  assert.match(archiveListPage, /复盘生成中/);
  assert.match(archiveListPage, /已完成复盘/);
  assert.doesNotMatch(archiveListPage, /Learning Archive/);
  assert.doesNotMatch(archiveListPage, /Checkin #/);
});

test('archive detail renders problem and review content as markdown', () => {
  assert.match(archiveDetailPage, /import MarkdownIt from 'markdown-it'/);
  assert.match(archiveDetailPage, /import katex from 'katex'/);
  assert.match(archiveDetailPage, /function renderMarkdownContent/);
  assert.match(archiveDetailPage, /v-html="renderMarkdownContent\(detail\.problem_context \|\| ''\)"/);
  assert.match(archiveDetailPage, /v-html="renderReviewSection\(section\)"/);
  assert.match(archiveDetailPage, /function looksLikePlainDiagram/);
  assert.match(archiveDetailPage, /font-mono/);
});

test('archive detail reframes review as three dense learning cards', () => {
  assert.match(archiveDetailPage, /错题复盘/);
  assert.match(archiveDetailPage, /把这题变成下次能用的经验/);
  assert.match(archiveDetailPage, /这类题在考什么/);
  assert.match(archiveDetailPage, /这道题怎么做通/);
  assert.match(archiveDetailPage, /下次怎么迁移/);
  assert.match(archiveDetailPage, /topic_commonality/);
  assert.match(archiveDetailPage, /solution_walkthrough/);
  assert.match(archiveDetailPage, /transfer_checklist/);
  assert.doesNotMatch(archiveDetailPage, /我原来怎么想 \/ 现在怎么想/);
  assert.doesNotMatch(archiveDetailPage, /下次遇到同类题先看什么/);
});

test('archive detail makes the problem context collapsible', () => {
  assert.match(archiveDetailPage, /const problemInfoOpen = ref\(false\)/);
  assert.match(archiveDetailPage, /problemInfoOpen = !problemInfoOpen/);
  assert.match(archiveDetailPage, /展开题面/);
  assert.match(archiveDetailPage, /收起题面/);
  assert.match(archiveDetailPage, /v-if="problemInfoOpen"/);
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
  assert.match(chatPage, /student_code: includeCodeInNextMessage\.value \? studentCode\.value\.trim\(\) : ''/);
});

test('chat page restores persisted AIChat history for the current problem session', () => {
  assert.match(apiService, /export function getChatHistory/);
  assert.match(apiService, /\/api\/chat\/history/);
  assert.match(chatPage, /getChatHistory/);
  assert.match(chatPage, /async function loadChatHistory/);
  assert.match(chatPage, /await getChatHistory\(auth\.token/);
  assert.match(chatPage, /messages\.value = result\.messages/);
  assert.match(chatPage, /loadChatHistory\(\)/);
});

test('chat page can hand current problem context to checkin flow', () => {
  assert.match(chatPage, /useRouter/);
  assert.match(chatPage, /function goToCheckinWithCurrentProblem/);
  assert.match(chatPage, /persistProblemContext\(\)/);
  assert.match(chatPage, /risk_type: 'manual_deep_review'/);
  assert.match(chatPage, /latestUserChatMessage\(\)/);
  assert.match(chatPage, /router\.push\('\/app\/workspace\/checkin'\)/);
  assert.match(chatPage, /带着当前题去深入复盘/);

  assert.match(checkinPage, /window\.localStorage\.getItem\('noi-agent-chat-problem-id'\)/);
  assert.match(checkinPage, /window\.localStorage\.getItem\('noi-agent-chat-problem-title'\)/);
  assert.match(checkinPage, /window\.localStorage\.getItem\('noi-agent-chat-problem-context'\)/);
  assert.match(checkinPage, /window\.localStorage\.getItem\('noi-agent-chat-student-code'\)/);
});

test('chat page stores AIChat handoff payload for checkin review', () => {
  assert.match(chatPage, /noi-agent-chat-handoff-payload/);
  assert.match(chatPage, /function persistHandoffPayload/);
  assert.match(chatPage, /persistHandoffPayload\(result\.handoff_payload\)/);
});

test('chat page gates understanding quiz behind evidence from AIChat response', () => {
  assert.match(apiServer, /understanding_state: str = "not_ready"/);
  assert.match(apiServer, /understanding_evidence: List\[str\] = Field\(default_factory=list\)/);
  assert.match(apiService, /export function generateUnderstandingCheck/);
  assert.match(apiService, /export function gradeUnderstandingCheck/);
  assert.match(apiService, /\/api\/chat\/understanding-check\/generate/);
  assert.match(apiService, /\/api\/chat\/understanding-check\/grade/);
  assert.match(chatPage, /const understandingState = ref\('not_ready'\)/);
  assert.match(chatPage, /const canVerifyUnderstanding = computed/);
  assert.match(chatPage, /验证一下/);
  assert.match(chatPage, /:disabled="!canVerifyUnderstanding \|\| verificationLoading"/);
  assert.match(chatPage, /function openUnderstandingQuiz/);
  assert.match(chatPage, /function submitUnderstandingQuiz/);
  assert.match(chatPage, /await generateUnderstandingCheck/);
  assert.match(chatPage, /await gradeUnderstandingCheck/);
  assert.match(chatPage, /v-model="verificationAnswer"/);
  assert.match(chatPage, /整理这题复盘/);
  assert.match(chatPage, /result\.understanding_state \|\| 'not_ready'/);
  assert.match(chatPage, /result\.understanding_evidence \|\| \[\]/);
  assert.doesNotMatch(chatPage, /哪一种表现最能说明/);
  assert.doesNotMatch(chatPage, /我说“懂了”/);
  assert.doesNotMatch(chatPage, /verificationQuiz\.value = \\{\\s*question:/);
});

test('chat page lets students finish a problem with a stored understanding check', () => {
  assert.match(apiService, /export function startProblemClosure/);
  assert.match(apiService, /export function gradeProblemClosure/);
  assert.match(apiService, /\/api\/chat\/problem-closure\/start/);
  assert.match(apiService, /\/api\/chat\/problem-closure\/grade/);
  assert.match(chatPage, /startProblemClosure/);
  assert.match(chatPage, /gradeProblemClosure/);
  assert.match(chatPage, /const problemClosure = ref/);
  assert.match(chatPage, /async function startFinishProblemFlow/);
  assert.match(chatPage, /async function submitProblemClosureAnswer/);
  assert.match(chatPage, /我已理解，结束本题/);
  assert.match(chatPage, /结束本题验证/);
  assert.match(chatPage, /closureFeedback/);
  assert.match(chatPage, /closurePanelOpen/);
  assert.match(chatPage, /points_awarded/);
  assert.match(chatPage, /next_review_message/);
  const resetSessionFunction = chatPage.match(/function resetSession\(\) \{[\s\S]*?\n\}/)?.[0] || '';
  assert.match(resetSessionFunction, /problemClosure\.value = null/);
  assert.match(resetSessionFunction, /closurePanelOpen\.value = false/);
});

test('floating chat keeps verification helpers out of the always-visible composer path', () => {
  assert.match(chatPage, /const showUnderstandingPanel = computed/);
  assert.match(chatPage, /const showProblemClosurePanel = computed/);
  assert.match(chatPage, /v-if="showUnderstandingPanel"/);
  assert.doesNotMatch(chatPage, /closure-floating-card/);
  assert.doesNotMatch(chatPage, /showProblemClosurePanel && chatFloating/);
  assert.doesNotMatch(chatPage, /showProblemClosurePanel && !chatFloating/);
  assert.match(chatPage, /chatFloating \? 'compact-floating-chat-header'/);
  assert.match(chatPage, /chatFloating \? 'mt-3 space-y-2'/);
});

test('problem closure verification uses a dedicated panel instead of blocking the chat composer', () => {
  assert.match(chatPage, /const PROBLEM_CLOSURE_STORAGE_KEY/);
  assert.match(chatPage, /function persistProblemClosureState/);
  assert.match(chatPage, /function restoreProblemClosureState/);
  assert.match(chatPage, /watch\(\[problemClosure, closureAnswer, closureFeedback\]/);
  assert.match(chatPage, /restoreProblemClosureState\(\)/);
  assert.match(chatPage, /const canStartProblemClosure = computed/);
  assert.match(chatPage, /:disabled=\"!canStartProblemClosure\"/);
  assert.match(chatPage, /problem-closure-panel/);
  assert.match(chatPage, /closure-bottom-drawer/);
  assert.match(chatPage, /showProblemClosurePanel && closurePanelOpen/);
  assert.match(chatPage, /继续结束验证/);
  assert.match(chatPage, /贴合当前这一步/);
  assert.match(chatPage, /30-90 秒/);
  assert.match(chatPage, /问题类型/);
  assert.match(chatPage, /验证题型/);
  assert.match(chatPage, /quizBottleneckLabel/);
  assert.match(chatPage, /quizFormatLabel/);
  assert.match(chatPage, /继续问 AIChat/);
});

test('collapsed problem closure verification keeps a visible reopen button', () => {
  assert.match(chatPage, /closure-reopen-button/);
  assert.match(chatPage, /showProblemClosurePanel && !closurePanelOpen/);
  assert.match(chatPage, /打开结束验证/);
  assert.match(chatPage, /@click="closurePanelOpen = true"/);
});

test('failed problem closure followup stays inside quiz panel instead of chat stream', () => {
  const submitFunction = extractBetween(
    chatPage,
    'async function submitProblemClosureAnswer()',
    'function continueFromClosureFeedback()',
  );

  assert.doesNotMatch(submitFunction, /messages\.value\.push/);
  assert.doesNotMatch(submitFunction, /scrollChatToBottom/);
  assert.match(submitFunction, /question:[\s\S]*result\.followup/);
  assert.match(submitFunction, /closureAnswer\.value\s*=\s*''/);
});

test('passed problem closure can hand the solved problem into checkin review', () => {
  assert.match(chatPage, /function buildProblemClosureHandoffPayload/);
  assert.match(chatPage, /risk_type: 'problem_closure_passed'/);
  assert.match(chatPage, /closure_answer: closureAnswer\.value\.trim\(\)/);
  assert.match(chatPage, /function goToCheckinFromProblemClosure/);
  assert.match(chatPage, /completionRecordOpen\.value = true/);
  assert.match(chatPage, /记录做题结果/);
  assert.doesNotMatch(chatPage, /整理本题复盘/);

  assert.match(checkinPage, /function applyClosureHandoffToForm/);
  assert.match(checkinPage, /problem_closure_passed/);
  assert.match(checkinPage, /form\.completion_status = 'independent'/);
  assert.match(checkinPage, /form\.bottleneck_text =/);
  assert.match(checkinPage, /form\.reflection =/);
});

test('floating chat keeps a compact model switcher visible', () => {
  assert.match(chatPage, /v-if="chatFloating"/);
  assert.match(chatPage, /floating-model-switcher/);
  assert.match(chatPage, /当前模型/);
  assert.match(chatPage, /<select[^>]+v-model="selectedChatModel"/);
  assert.match(chatPage, /v-for="option in chatModels"/);
});

test('chat page lazy-loads CodeMirror only when code mode is used', () => {
  assert.doesNotMatch(chatPage, /import \{ EditorView, basicSetup \} from 'codemirror'/);
  assert.doesNotMatch(chatPage, /import \{ cpp \} from '@codemirror\/lang-cpp'/);
  assert.match(chatPage, /let codeMirrorModulesPromise = null/);
  assert.match(chatPage, /async function getCodeMirrorModules/);
  assert.match(chatPage, /import\('codemirror'\)/);
  assert.match(chatPage, /import\('@codemirror\/lang-cpp'\)/);
  assert.match(chatPage, /await initializeCodeMirror\(\)/);
});

test('checkin page submits AIChat handoff payload when present', () => {
  assert.match(checkinPage, /function loadHandoffPayload/);
  assert.match(checkinPage, /parsed && parsed\.source === 'aichat'/);
  assert.match(checkinPage, /const handoffPayload = ref\(loadHandoffPayload\(\)\)/);
  assert.match(checkinPage, /handoff_payload: handoffPayload\.value/);
  assert.match(checkinPage, /chat_context_summary: chatContextSummary\.value/);
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
  assert.match(chatPage, /读取题目/);
  assert.doesNotMatch(chatPage, /读取洛谷题目/);
});

test('chat page lets students clear stale current problem context without exposing session id', () => {
  assert.match(chatPage, /function clearProblemContext/);
  assert.match(chatPage, /problemId\.value = ''/);
  assert.match(chatPage, /problemTitle\.value = ''/);
  assert.match(chatPage, /problemContext\.value = ''/);
  assert.match(chatPage, /studentCode\.value = ''/);
  assert.match(chatPage, /清空当前题背景/);
});

test('chat page uses dual study modes instead of a cramped three-pane desktop layout', () => {
  assert.match(chatPage, /const workspaceMode = ref\('read'\)/);
  assert.match(chatPage, /读题问 AI/);
  assert.match(chatPage, /写代码问 AI/);
  assert.match(chatPage, /activeWorkspaceTab/);
  assert.match(chatPage, /题目/);
  assert.match(chatPage, /AI/);
  assert.match(chatPage, /代码/);
  assert.doesNotMatch(chatPage, /xl:grid-cols-\[minmax\(0,0\.9fr\)_minmax\(0,1\.1fr\)_minmax\(0,1fr\)\]/);
  assert.match(chatPage, /read-mode-grid/);
  assert.match(chatPage, /code-mode-grid/);
  assert.match(chatPage, /当前题目/);
  assert.match(chatPage, /AI 对话/);
  assert.match(chatPage, /代码练习/);
});

test('chat page offers one AIChat that can switch between fixed and floating display', () => {
  assert.match(chatPage, /const chatFloating = ref\(false\)/);
  assert.match(chatPage, /const chatWindowSize = ref/);
  assert.match(chatPage, /const chatWindowRef = ref\(null\)/);
  assert.match(chatPage, /function toggleChatFloating/);
  assert.match(chatPage, /function beginChatDrag/);
  assert.match(chatPage, /ResizeObserver/);
  assert.match(chatPage, /syncChatWindowSizeFromElement/);
  assert.match(chatPage, /width: `\$\{chatWindowSize\.value\.width\}px`/);
  assert.match(chatPage, /height: `\$\{chatWindowSize\.value\.height\}px`/);
  assert.doesNotMatch(chatPage, /width: 'min\\(34rem, calc\\(100vw - 2rem\\)\\)'/);
  assert.doesNotMatch(chatPage, /height: 'min\\(42rem, calc\\(100vh - 7rem\\)\\)'/);
  assert.match(chatPage, /悬浮对话/);
  assert.match(chatPage, /回到右侧/);
  assert.match(chatPage, /floating-chat-grid/);
  assert.match(chatPage, /floating-chat-window/);
  assert.doesNotMatch(chatPage, /floating-chat-window relative/);
  assert.doesNotMatch(chatPage, /AI 教练正在悬浮窗口中/);
  assert.match(chatPage, /chatFloating \? 'fixed'/);
  assert.match(chatPage, /chatFloating \? 'xl:grid-cols-1'/);
  assert.match(chatPage, /resize/);
  assert.match(chatPage, /min-w-\[24rem\]/);
  assert.match(chatPage, /floating-chat-resize-hint/);
  assert.match(chatPage, /拖动标题移动，拖动右下角缩放/);
  const aiHeadingCount = (chatPage.match(/AI 对话/g) || []).length;
  assert.equal(aiHeadingCount, 1);
});

test('student layout hides the large hero on the AIChat route', () => {
  assert.match(studentLayout, /const showHero = computed/);
  assert.match(studentLayout, /route\.meta\.section !== 'chat'/);
  assert.match(studentLayout, /v-if="showHero"/);
});

test('student app exposes knowledge补全 as a bounded fallback page', () => {
  assert.match(studentRouter, /KnowledgePage/);
  assert.match(studentRouter, /workspace\/knowledge/);
  assert.match(studentRouter, /section: 'knowledge'/);
  assert.doesNotMatch(studentLayout, /label: '知识补全'/);
  assert.match(studentLayout, /nav-link-active-knowledge/);
  assert.doesNotMatch(chatPage, /KNOWLEDGE_HANDOFF_KEY/);
  assert.doesNotMatch(chatPage, /function goToKnowledgeWithCurrentProblem/);
  assert.doesNotMatch(chatPage, /补一下这步知识/);
  assert.match(knowledgePage, /这一步缺什么/);
  assert.match(knowledgePage, /这个知识在原题里负责什么/);
  assert.match(knowledgePage, /小例子/);
  assert.match(knowledgePage, /轻验证/);
  assert.match(knowledgePage, /回到原题继续问 AI/);
  assert.match(knowledgePage, /不是完整课程/);
});

test('student layout treats checkin as a learning records hub', () => {
  assert.match(studentLayout, /label: '学习记录'/);
  assert.match(studentLayout, /\/app\/workspace\/checkin/);
  assert.doesNotMatch(studentLayout, /label: '打卡复盘'/);
  assert.doesNotMatch(studentLayout, /label: '历史打卡'/);
});

test('checkin page combines completion records, checkin review, and history as tabs', () => {
  assert.match(checkinPage, /recordTabs/);
  assert.match(checkinPage, /activeRecordTab/);
  assert.match(checkinPage, /记录做完的题/);
  assert.match(checkinPage, /深入复盘/);
  assert.match(checkinPage, /历史记录/);
  assert.match(checkinPage, /记录一道做完的题/);
  assert.match(checkinPage, /下次我会先想什么/);
  assert.match(checkinPage, /给未来的自己留一句提醒/);
  assert.match(checkinPage, /classroom_taught/);
  assert.match(checkinPage, /老师讲过后做出来/);
  assert.match(checkinPage, /submitCompletionRecord/);
  assert.match(checkinPage, /createStudentProblemCompletion/);
  assert.match(checkinPage, /to="\{ path: '\/app\/archive', query: \{ tab: 'records' \} \}"/);
  assert.match(checkinPage, /to="\{ path: '\/app\/archive', query: \{ tab: 'reviews' \} \}"/);
  assert.match(checkinPage, /查看做题记录/);
  assert.match(checkinPage, /查看深入复盘/);
  assert.doesNotMatch(checkinPage, /一句话总结：这题最关键的一步是什么/);
  assert.doesNotMatch(checkinPage, /历史打卡/);
  assert.doesNotMatch(checkinPage, /打卡复盘提交/);
});

test('archive list separates deep reviews from quick problem records', () => {
  assert.match(apiService, /export function getStudentProblemCompletions/);
  assert.match(apiService, /\/api\/student\/problem-completions/);
  assert.match(archiveListPage, /useRoute/);
  assert.match(archiveListPage, /route\.query\.tab === 'records'/);
  assert.match(archiveListPage, /watch\(/);
  assert.match(archiveListPage, /activeHistoryTab\.value = tab === 'records' \? 'records' : 'reviews'/);
  assert.match(archiveListPage, /historyTabs/);
  assert.match(archiveListPage, /activeHistoryTab/);
  assert.match(archiveListPage, /completionRecords/);
  assert.match(archiveListPage, /深入复盘/);
  assert.match(archiveListPage, /做题记录/);
  assert.match(archiveListPage, /只想快速留痕/);
  assert.doesNotMatch(archiveListPage, /历史打卡/);
});

test('chat completion record form uses stable full-width controls', () => {
  assert.match(chatPage, /rounded-\[24px\] border border-emerald-100/);
  assert.match(chatPage, /grid gap-3 md:grid-cols-2/);
  assert.match(chatPage, /下次我会先想什么/);
  assert.match(chatPage, /classroom_taught/);
  assert.match(chatPage, /payload\?\.message/);
  assert.match(chatPage, /class="field w-full"/);
  assert.match(chatPage, /class="field mt-3 min-h-\[112px\] w-full resize-y"/);
  assert.match(chatPage, /保存做题记录/);
});

test('chat page exposes C++ sample running and code-to-chat controls', () => {
  assert.match(apiService, /export function getRunnerHealth/);
  assert.match(apiService, /export function runStudentCode/);
  assert.match(apiService, /\/api\/health\/runner/);
  assert.match(apiService, /\/api\/student\/code\/run/);
  assert.match(chatPage, /CodeMirror/);
  assert.match(chatPage, /indentWithTab/);
  assert.match(chatPage, /keymap\.of\(\[\s*indentWithTab/);
  assert.match(chatPage, /sampleInput/);
  assert.match(chatPage, /actualOutput/);
  assert.match(chatPage, /运行代码/);
  assert.match(chatPage, /带着这段代码提问/);
  assert.match(chatPage, /本次问题将带上当前代码/);
  assert.match(chatPage, /本次问题未带代码/);
  assert.match(chatPage, /当前环境暂不支持代码运行/);
});

test('chat page validates missing problem before sending instead of relying on quota gating', () => {
  assert.match(chatPage, /const hasProblemIdentity = computed/);
  assert.match(chatPage, /const canSend = computed\(\(\) => Boolean\(message\.value\.trim\(\) && !sending\.value\)\)/);
  assert.match(chatPage, /请先填写题目链接或题号/);
  assert.match(chatPage, /if \(!hasProblemIdentity\.value\)/);
  assert.doesNotMatch(chatPage, /剩余配额/);
  assert.doesNotMatch(chatPage, /remainingQuota/);
});

test('chat page shows thinking state inside the conversation flow instead of only on the send button', () => {
  assert.match(chatPage, /const THINKING_MESSAGE = 'AI 教练正在思考\.\.\.'/);
  assert.match(chatPage, /const thinkingMessage = \{ role: 'assistant', content: THINKING_MESSAGE, isThinking: true \};/);
  assert.match(chatPage, /messages\.value\.push\(thinkingMessage\)/);
  assert.match(chatPage, /messages\.value\[thinkingIndex\] = \{ role: 'assistant', content: result\.reply ?\};/);
  assert.match(chatPage, /item\.isThinking/);
  assert.match(chatPage, /AI 教练正在思考\.\.\./);
  assert.doesNotMatch(chatPage, /\{\{ sending \? '正在思考\.\.\.' : '发送给 AIChat' \}\}/);
  assert.match(chatPage, /\{\{ sending \? '发送中' : '发送给 AIChat' \}\}/);
});

test('chat page keeps the message box at a stable base height instead of stretching with workspace layout changes', () => {
  assert.match(chatPage, /class="field min-h-\[7\.5rem\] max-h-48 flex-none resize-none overflow-y-auto"/);
  assert.doesNotMatch(chatPage, /id="chat-message-input"[\s\S]*class="field min-h-28 resize-y"/);
  assert.match(chatPage, /xl:self-start/);
  assert.match(chatPage, /xl:h-\[42rem\]/);
});

test('chat page renders imported problem context as markdown instead of raw textarea first', () => {
  assert.match(chatPage, /MarkdownIt/);
  assert.match(chatPage, /katex/);
  assert.match(chatPage, /renderedProblemContext/);
  assert.match(chatPage, /v-html="renderedProblemContext"/);
  assert.match(chatPage, /题面 Markdown 预览/);
  assert.match(chatPage, /编辑题面原文/);
});

test('chat page renders assistant replies with markdown and math support', () => {
  assert.match(chatPage, /const renderedChatMessage = \(content\) => renderMarkdownContent\(content\);/);
  assert.match(chatPage, /v-html="renderedChatMessage\(cleanChatMessageContent\(item\.content\)\)"/);
  assert.doesNotMatch(chatPage, /<span v-else class="whitespace-pre-wrap break-words">\{\{ item\.content \}\}<\/span>/);
});

test('chat code panel follows OJ-style editor self-test and output areas', () => {
  assert.match(chatPage, /代码编辑/);
  assert.match(chatPage, /样例输入/);
  assert.match(chatPage, /程序输出/);
  assert.match(chatPage, /运行信息/);
  assert.match(chatPage, /editor-toolbar/);
  assert.match(chatPage, /code-runner-panels mt-4 grid gap-3 md:grid-cols-2/);
  assert.match(chatPage, /Ctrl \+ Enter 运行/);
});

test('chat code editor is tall enough for real code and does not expose expected output', () => {
  assert.match(chatPage, /code-editor-shell/);
  assert.match(chatPage, /min-h-\[28rem\]/);
  assert.doesNotMatch(chatPage, /期望输出/);
  assert.doesNotMatch(chatPage, /expectedOutput/);
  assert.doesNotMatch(chatPage, /expected_output:/);
});

test('chat page marks code for the next question instead of auto-sending it', () => {
  assert.match(chatPage, /includeCodeInNextMessage/);
  assert.match(chatPage, /function attachCodeToNextQuestion/);
  assert.match(chatPage, /function clearCodeAttachment\(\)/);
  assert.match(chatPage, /student_code: includeCodeInNextMessage\.value \? studentCode\.value\.trim\(\) : ''/);
  assert.match(chatPage, /includeCodeInNextMessage\.value = false/);
  assert.match(chatPage, /清除带代码/);
  const attachCodeFunction = chatPage.match(/function attachCodeToNextQuestion\(\) \{[\s\S]*?\n\}/)?.[0] || '';
  assert.doesNotMatch(attachCodeFunction, /submitMessage|sendChat|runStudentCode/);
});

test('chat page lets students choose an AIChat model provider', () => {
  assert.match(apiService, /export function getChatModels/);
  assert.match(apiService, /\/api\/chat\/models/);
  assert.match(chatPage, /getChatModels/);
  assert.match(chatPage, /selectedChatModel/);
  assert.match(chatPage, /chat_model_provider: selectedChatModel\.value/);
  assert.match(chatPage, /模型/);
  assert.match(chatPage, /快速/);
  assert.match(chatPage, /专业/);
  assert.doesNotMatch(chatPage, /MiMo/);
  assert.doesNotMatch(chatPage, /Kimi/);
});

test('chat page clears pending code attachment when resetting the conversation context', () => {
  const resetSessionFunction = chatPage.match(/function resetSession\(\) \{[\s\S]*?\n\}/)?.[0] || '';
  const clearProblemContextFunction = chatPage.match(/function clearProblemContext\(\) \{[\s\S]*?\n\}/)?.[0] || '';
  assert.match(resetSessionFunction, /includeCodeInNextMessage\.value = false/);
  assert.match(clearProblemContextFunction, /includeCodeInNextMessage\.value = false/);
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
  assert.match(checkinPage, /<label[^>]+for="checkin-bottleneck"[^>]*>我哪里没想明白<\/label>/);
  assert.match(checkinPage, /<textarea[^>]+id="checkin-bottleneck"/);
  assert.match(checkinPage, /<label[^>]+for="checkin-reflection"[^>]*>我已经试过什么<\/label>/);
  assert.match(checkinPage, /<textarea[^>]+id="checkin-reflection"/);
});

test('teacher students page contains a usable Chinese student account creation panel', () => {
  assert.match(apiService, /export function getTeacherStudents/);
  assert.match(apiService, /export function createTeacherStudent/);
  assert.match(apiService, /export function resetTeacherStudentPassword/);
  assert.match(apiService, /export function updateTeacherStudentStatus/);
  assert.match(teacherAccountsPage, /创建学生账号/);
  assert.match(teacherAccountsPage, /显示姓名/);
  assert.match(teacherAccountsPage, /登录账号/);
  assert.match(teacherAccountsPage, /初始密码/);
  assert.match(teacherAccountsPage, /停用/);
  assert.match(teacherAccountsPage, /启用/);
  assert.match(teacherAccountsPage, /重置密码/);
  assert.doesNotMatch(teacherStudentsPage, /创建学生账号/);
  assert.doesNotMatch(teacherStudentsPage, />Students</);
  assert.doesNotMatch(teacherLayout, /Review Ops|Records & Students|Teacher Overview/);
});

test('teacher students page supports bulk student account creation', () => {
  assert.match(teacherAccountsPage, /批量创建账号/);
  assert.match(teacherAccountsPage, /粘贴表格/);
  assert.match(teacherAccountsPage, /CSV/);
  assert.match(teacherAccountsPage, /batchAccountText/);
  assert.match(teacherAccountsPage, /function parseBatchAccountRows/);
  assert.match(teacherAccountsPage, /function submitBatchAccounts/);
  assert.match(apiService, /export function createTeacherStudentsBulk/);
  assert.match(apiService, /\/api\/teacher\/students\/bulk/);
});

test('primary buttons have a visible default background', () => {
  const primaryButtonRule = frontendStyles.match(/\.button-primary\s*\{[\s\S]*?\n\s*\}/)?.[0] || '';
  assert.match(primaryButtonRule, /bg-cyan-600/);
  assert.match(primaryButtonRule, /hover:bg-cyan-700/);
  assert.match(primaryButtonRule, /disabled:bg-slate-300/);
});

test('frontend entry uses cache-busted dist assets instead of a fixed app.js path', () => {
  assert.match(viteConfig, /base:\s*'\/static\/dist\/'/);
  assert.doesNotMatch(viteConfig, /entryFileNames:\s*'assets\/app\.js'/);
  assert.doesNotMatch(viteConfig, /return 'assets\/app\.css'/);
  assert.match(apiServer, /os\.path\.join\(BASE_DIR,\s*"static",\s*"dist",\s*"index\.html"\)/);
  assert.match(apiServer, /Cache-Control/);
});

test('chat page routes diagram code blocks into a collapsible side panel', () => {
  assert.match(chatPage, /parseDiagramBlocks/);
  assert.match(chatPage, /diagram-ascii/);
  assert.match(chatPage, /mermaid/);
  assert.match(chatPage, /activeDiagram/);
  assert.match(chatPage, /diagramPanelOpen/);
  assert.match(chatPage, /查看图示/);
  assert.match(chatPage, /AI 图示/);
  assert.match(chatPage, /renderMermaidDiagram/);
  assert.match(chatPage, /diagramZoom/);
  assert.match(chatPage, /cleanChatMessageContent/);
});
