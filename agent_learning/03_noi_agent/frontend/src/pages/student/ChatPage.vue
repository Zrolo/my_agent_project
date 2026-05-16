<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import MarkdownIt from 'markdown-it';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { useRouter } from 'vue-router';

import {
  generateUnderstandingCheck,
  createStudentProblemCompletion,
  getChatHistory,
  getChatModels,
  getRunnerHealth,
  gradeUnderstandingCheck,
  gradeProblemClosure,
  importProblem,
  runStudentCode,
  sendChat,
  startProblemClosure,
} from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const router = useRouter();
const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});
let mermaidRendererPromise = null;
let codeMirrorModulesPromise = null;

const problemId = ref(window.localStorage.getItem('noi-agent-chat-problem-id') || '');
const problemTitle = ref(window.localStorage.getItem('noi-agent-chat-problem-title') || '');
const problemContext = ref(window.localStorage.getItem('noi-agent-chat-problem-context') || '');
const studentCode = ref(window.localStorage.getItem('noi-agent-chat-student-code') || '');
const sessionId = ref(window.localStorage.getItem('noi-agent-chat-session-id') || createChatSessionId());
const message = ref('');
const sending = ref(false);
const importingProblem = ref(false);
const error = ref('');
const problemImportMessage = ref('');
const level = ref('');
const messages = ref([]);
const workspaceMode = ref('read');
const activeWorkspaceTab = ref('ai');
const includeCodeInNextMessage = ref(false);
const composingMessage = ref(false);
const chatFloating = ref(false);
const chatWindowPosition = ref({
  x: Math.max(24, window.innerWidth - 560),
  y: 96,
});
const chatWindowSize = ref({
  width: Math.min(544, Math.max(384, window.innerWidth - 32)),
  height: Math.min(672, Math.max(448, window.innerHeight - 112)),
});
const chatDragOffset = ref({ x: 0, y: 0 });

const codeEditorHost = ref(null);
const chatListRef = ref(null);
const chatWindowRef = ref(null);
let codeEditor = null;
let chatResizeObserver = null;

const runnerHealth = ref(null);
const runnerLoading = ref(false);
const runningCode = ref(false);
const sampleInput = ref(window.localStorage.getItem('noi-agent-chat-sample-input') || '');
const actualOutput = ref('');
const compileOutput = ref('');
const runMessage = ref('');
const runStatus = ref('');
const CHAT_MODEL_STORAGE_KEY = 'noi-agent-chat-model-provider';
const CHAT_MODEL_FALLBACK_LABELS = {
  deepseek_flash: '快速',
  deepseek_pro: '专业',
  deepseek: '专业',
};
const CHAT_PROMPT_MODE_STORAGE_KEY = 'noi-agent-chat-prompt-mode';
const storedChatPromptMode = window.localStorage.getItem(CHAT_PROMPT_MODE_STORAGE_KEY);
const CHAT_PROMPT_MODE_OPTIONS = [
  {
    value: 'current_system',
    label: '简洁提示',
    description: '沿用当前回答方式，适合小问题和局部确认。',
  },
  {
    value: 'dbox_inspired_clean',
    label: '教练引导',
    description: '分解成一个当前小步骤，适合真正卡住时使用。',
  },
];
const QUIZ_BOTTLENECK_LABELS = {
  problem_translation: '题意翻译',
  concept_boundary: '概念边界',
  representation_modeling: '表示建模',
  relation_alignment: '约束关系',
  process_tracing: '操作过程',
  strategy_choice: '策略选择',
  transfer_unstable: '迁移不稳',
  code_semantics: '代码语义',
  debugging: '调试定位',
  complexity_awareness: '复杂度意识',
  metacognitive: '元认知',
  affective_load: '情绪负荷',
};
const QUIZ_FORMAT_LABELS = {
  judge_explain: '判断并解释',
  small_case_explain: '小样例迁移',
  trace_one_step: '手算一步',
  code_trace: '代码行为核对',
  find_counterexample: '错误辨析',
  complexity_estimate: '复杂度估算',
  self_explain: '自我解释',
};
const chatModels = ref([]);
const selectedChatModel = ref(window.localStorage.getItem(CHAT_MODEL_STORAGE_KEY) || '');
const selectedChatPromptMode = ref(
  storedChatPromptMode === 'enhanced_prompt_only_clean'
    ? 'dbox_inspired_clean'
    : storedChatPromptMode || 'current_system',
);
const chatModelsLoading = ref(false);
const understandingState = ref('not_ready');
const understandingEvidence = ref([]);
const verificationQuiz = ref(null);
const verificationAnswer = ref('');
const verificationFeedback = ref('');
const verificationLoading = ref(false);
const verificationChecking = ref(false);
const problemClosure = ref(null);
const closureAnswer = ref('');
const closureFeedback = ref('');
const closurePanelOpen = ref(false);
const closureLoading = ref(false);
const closureChecking = ref(false);
const diagramPanelOpen = ref(false);
const activeDiagram = ref(null);
const diagramSvg = ref('');
const completionRecordOpen = ref(false);
const completionRecordMessage = ref('');
const completionRecordForm = ref({
  reported_completion: 'self_solved',
  result_status: 'accepted',
  key_step_summary: '',
});
const diagramError = ref('');
const diagramZoom = ref(1);
let diagramRenderCounter = 0;

window.localStorage.setItem('noi-agent-chat-session-id', sessionId.value);
const HANDOFF_PAYLOAD_KEY = 'noi-agent-chat-handoff-payload';
const CODE_CACHE_INDEX_KEY = 'noi:code:index';
const PROBLEM_CLOSURE_STORAGE_KEY = 'noi-agent-chat-problem-closure-state';
const MAX_CODE_CACHE_ITEMS = 50;
const THINKING_MESSAGE = 'AI 教练正在思考...';

const hasProblemIdentity = computed(() => Boolean(problemId.value.trim() || problemTitle.value.trim() || problemContext.value.trim()));
const canSend = computed(() => Boolean(message.value.trim() && !sending.value));
const runnerAvailable = computed(() => Boolean(runnerHealth.value?.available));
const canRunCode = computed(() => Boolean(runnerAvailable.value && studentCode.value.trim() && !runningCode.value));
const renderedProblemContext = computed(() => renderMarkdownContent(problemContext.value));
const renderedChatMessage = (content) => renderMarkdownContent(content);
const selectedChatModelInfo = computed(() => chatModels.value.find((item) => item.provider_id === selectedChatModel.value) || null);
const canVerifyUnderstanding = computed(() => understandingState.value === 'evidence_seen');
const showUnderstandingPanel = computed(() => Boolean(canVerifyUnderstanding.value || verificationQuiz.value || verificationFeedback.value || understandingState.value === 'quiz_passed'));
const showProblemClosurePanel = computed(() => Boolean(problemClosure.value || closureFeedback.value));
const canStartProblemClosure = computed(() => Boolean(hasProblemIdentity.value && !closureLoading.value && !closureChecking.value && !problemClosure.value));
const problemClosureButtonLabel = computed(() => {
  if (closureLoading.value) return '生成验证中';
  if (problemClosure.value) return '验证进行中';
  return '我已理解，结束本题';
});
const floatingChatStyle = computed(() => {
  if (!chatFloating.value) return null;
  return {
    left: `${chatWindowPosition.value.x}px`,
    top: `${chatWindowPosition.value.y}px`,
    width: `${chatWindowSize.value.width}px`,
    height: `${chatWindowSize.value.height}px`,
  };
});
const normalizedProblemUrl = computed(() => {
  const raw = problemId.value.trim();
  return /^https?:\/\//i.test(raw) ? raw : '';
});

function quizBottleneckLabel(quiz) {
  const key = String(quiz?.bottleneck_type || '').trim();
  return QUIZ_BOTTLENECK_LABELS[key] || '当前这一步';
}

function quizFormatLabel(quiz) {
  const key = String(quiz?.quiz_format || '').trim();
  return QUIZ_FORMAT_LABELS[key] || '小验证';
}

function createChatSessionId() {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }
  const randomPart = Math.random().toString(36).slice(2, 10);
  return `session-${Date.now()}-${randomPart}`;
}

function escapeHtml(text) {
  return String(text || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderMath(expression, displayMode) {
  try {
    return katex.renderToString(expression.trim(), {
      displayMode,
      throwOnError: false,
      strict: 'ignore',
    });
  } catch {
    return `<code>${escapeHtml(expression)}</code>`;
  }
}

function renderMarkdownContent(source) {
  const text = (source || '').trim();
  if (!text) return '';
  const mathHtml = [];
  const withBlockMath = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, expression) => {
    const token = `@@NOI_MATH_${mathHtml.length}@@`;
    mathHtml.push(renderMath(expression, true));
    return token;
  });
  const withInlineMath = withBlockMath.replace(/(^|[^$])\$([^$\n]+?)\$(?!\$)/g, (match, prefix, expression) => {
    const token = `@@NOI_MATH_${mathHtml.length}@@`;
    mathHtml.push(renderMath(expression, false));
    return `${prefix}${token}`;
  });
  let rendered = markdown.render(withInlineMath);
  mathHtml.forEach((html, index) => {
    rendered = rendered.replaceAll(`@@NOI_MATH_${index}@@`, html);
  });
  return rendered;
}

function parseDiagramBlocks(source) {
  const text = String(source || '');
  const blocks = [];
  const pieces = [];
  const fencePattern = /```([^\n`]*)\n([\s\S]*?)```/g;
  let cursor = 0;
  let match;
  while ((match = fencePattern.exec(text)) !== null) {
    const [fullMatch, rawInfo, rawCode] = match;
    const info = String(rawInfo || '').trim().toLowerCase();
    const isMermaid = info.split(/\s+/).includes('mermaid');
    const isAsciiDiagram = info.includes('diagram-ascii') || info.includes('ascii-diagram') || info.includes('text-diagram');
    if (!isMermaid && !isAsciiDiagram) continue;
    pieces.push(text.slice(cursor, match.index));
    blocks.push({
      type: isMermaid ? 'mermaid' : 'diagram-ascii',
      code: String(rawCode || '').trim(),
      title: isMermaid ? '流程图' : '文字图',
    });
    cursor = match.index + fullMatch.length;
  }
  pieces.push(text.slice(cursor));
  return {
    text: pieces.join('').trim(),
    blocks: blocks.filter((block) => block.code),
  };
}

function cleanChatMessageContent(content) {
  return parseDiagramBlocks(content).text;
}

function messageDiagramBlocks(content) {
  return parseDiagramBlocks(content).blocks;
}

function diagramButtonLabel(block, index) {
  if (block.type === 'mermaid') {
    return index > 0 ? `查看图示 ${index + 1}` : '查看图示';
  }
  return index > 0 ? `查看文字图 ${index + 1}` : '查看文字图';
}

async function renderMermaidDiagram(block) {
  diagramSvg.value = '';
  diagramError.value = '';
  if (!block || block.type !== 'mermaid') return;
  const renderId = `noi-aichat-diagram-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const currentRender = ++diagramRenderCounter;
  try {
    const mermaid = await getMermaidRenderer();
    const result = await mermaid.render(renderId, block.code);
    if (currentRender === diagramRenderCounter) {
      diagramSvg.value = result.svg;
    }
  } catch {
    if (currentRender === diagramRenderCounter) {
      diagramError.value = '这张图暂时没有渲染成功，下面保留原始图示代码。';
    }
  }
}

async function getMermaidRenderer() {
  if (!mermaidRendererPromise) {
    mermaidRendererPromise = import('mermaid').then((module) => {
      const mermaid = module.default;
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        theme: 'neutral',
      });
      return mermaid;
    });
  }
  return mermaidRendererPromise;
}

function openDiagramPanel(block, messageIndex = 0, blockIndex = 0) {
  activeDiagram.value = {
    ...block,
    messageIndex,
    blockIndex,
  };
  diagramPanelOpen.value = true;
  diagramZoom.value = 1;
  renderMermaidDiagram(activeDiagram.value);
}

function closeDiagramPanel() {
  diagramPanelOpen.value = false;
  activeDiagram.value = null;
  diagramSvg.value = '';
  diagramError.value = '';
}

function adjustDiagramZoom(delta) {
  diagramZoom.value = Math.min(1.8, Math.max(0.7, Number((diagramZoom.value + delta).toFixed(2))));
}

const codeCacheKey = computed(() => {
  const student = auth.userId || 'anonymous';
  const problem = problemId.value.trim() || 'unspecified';
  return `noi:code:${student}:${problem}`;
});

function resetSession() {
  sessionId.value = createChatSessionId();
  messages.value = [];
  includeCodeInNextMessage.value = false;
  understandingState.value = 'not_ready';
  understandingEvidence.value = [];
  verificationQuiz.value = null;
  verificationAnswer.value = '';
  verificationFeedback.value = '';
  problemClosure.value = null;
  closureAnswer.value = '';
  closureFeedback.value = '';
  closurePanelOpen.value = false;
  closeDiagramPanel();
  window.localStorage.setItem('noi-agent-chat-session-id', sessionId.value);
  persistProblemClosureState();
}

function rememberCodeCacheKey(key) {
  const raw = window.localStorage.getItem(CODE_CACHE_INDEX_KEY);
  let index = [];
  try {
    index = raw ? JSON.parse(raw) : [];
  } catch {
    index = [];
  }
  const nextIndex = [key, ...index.filter((item) => item !== key)];
  window.localStorage.setItem(CODE_CACHE_INDEX_KEY, JSON.stringify(nextIndex.slice(0, MAX_CODE_CACHE_ITEMS)));
  for (const staleKey of nextIndex.slice(MAX_CODE_CACHE_ITEMS)) {
    window.localStorage.removeItem(staleKey);
  }
}

function persistCodeForCurrentProblem() {
  const code = studentCode.value;
  window.localStorage.setItem(codeCacheKey.value, code);
  rememberCodeCacheKey(codeCacheKey.value);
  window.localStorage.setItem('noi-agent-chat-student-code', code);
}

function loadCodeForCurrentProblem() {
  const cached = window.localStorage.getItem(codeCacheKey.value);
  if (cached !== null) {
    studentCode.value = cached;
  }
}

function persistProblemContext() {
  window.localStorage.setItem('noi-agent-chat-problem-id', problemId.value.trim());
  window.localStorage.setItem('noi-agent-chat-problem-title', problemTitle.value.trim());
  window.localStorage.setItem('noi-agent-chat-problem-context', problemContext.value.trim());
  persistCodeForCurrentProblem();
  window.localStorage.setItem('noi-agent-chat-sample-input', sampleInput.value);
  window.localStorage.removeItem('noi-agent-chat-expected-output');
}

function persistHandoffPayload(payload) {
  if (payload && typeof payload === 'object') {
    window.localStorage.setItem(HANDOFF_PAYLOAD_KEY, JSON.stringify(payload));
    return;
  }
  window.localStorage.removeItem(HANDOFF_PAYLOAD_KEY);
}

function buildProblemClosureHandoffPayload() {
  return {
    handoff_type: 'checkin_reflection',
    source: 'aichat',
    risk_type: 'problem_closure_passed',
    problem_ref: problemId.value.trim(),
    problem_title: problemTitle.value.trim(),
    session_id: sessionId.value,
    last_user_message: closureAnswer.value.trim(),
    suggested_focus: '把这题已经说清楚的关键点整理成复盘，留下可迁移的方法和容易错的地方。',
    closure_question: problemClosure.value?.question || '',
    closure_answer: closureAnswer.value.trim(),
    closure_feedback: closureFeedback.value,
    points_awarded: problemClosure.value?.points_awarded || 0,
    next_review_at: problemClosure.value?.next_review_at || '',
  };
}

function problemClosureStorageContext() {
  return {
    user_id: auth.userId || '',
    problem_id: problemId.value.trim(),
    session_id: sessionId.value,
  };
}

function persistProblemClosureState() {
  if (!problemClosure.value && !closureAnswer.value && !closureFeedback.value) {
    window.localStorage.removeItem(PROBLEM_CLOSURE_STORAGE_KEY);
    return;
  }
  const payload = {
    ...problemClosureStorageContext(),
    problemClosure: problemClosure.value,
    closureAnswer: closureAnswer.value,
    closureFeedback: closureFeedback.value,
  };
  window.localStorage.setItem(PROBLEM_CLOSURE_STORAGE_KEY, JSON.stringify(payload));
}

function restoreProblemClosureState() {
  const raw = window.localStorage.getItem(PROBLEM_CLOSURE_STORAGE_KEY);
  if (!raw) return;
  try {
    const payload = JSON.parse(raw);
    const context = problemClosureStorageContext();
    if (payload.user_id && payload.user_id !== context.user_id) return;
    if (payload.problem_id && context.problem_id && payload.problem_id !== context.problem_id) return;
    if (payload.session_id && payload.session_id !== context.session_id) return;
    problemClosure.value = payload.problemClosure || null;
    closureAnswer.value = payload.closureAnswer || '';
    closureFeedback.value = payload.closureFeedback || '';
    closurePanelOpen.value = Boolean(problemClosure.value || closureFeedback.value);
  } catch {
    window.localStorage.removeItem(PROBLEM_CLOSURE_STORAGE_KEY);
  }
}

function clearProblemContext() {
  problemId.value = '';
  problemTitle.value = '';
  problemContext.value = '';
  studentCode.value = '';
  sampleInput.value = '';
  actualOutput.value = '';
  compileOutput.value = '';
  runMessage.value = '';
  runStatus.value = '';
  problemImportMessage.value = '';
  includeCodeInNextMessage.value = false;
  problemClosure.value = null;
  closureAnswer.value = '';
  closureFeedback.value = '';
  closurePanelOpen.value = false;
  persistProblemContext();
  persistProblemClosureState();
  persistHandoffPayload(null);
}

function goToCheckinWithCurrentProblem() {
  persistProblemContext();
  persistHandoffPayload({
    handoff_type: 'checkin_reflection',
    source: 'aichat',
    risk_type: 'manual_deep_review',
    problem_ref: problemId.value.trim(),
    problem_title: problemTitle.value.trim(),
    session_id: sessionId.value,
    last_user_message: latestUserChatMessage(),
    suggested_focus: '把这题还没想明白的地方整理清楚；如果你说不清，就先从最近一次提问开始。',
  });
  router.push('/app/workspace/checkin');
}

async function submitProblemCompletionRecord() {
  completionRecordMessage.value = '';
  const summary = completionRecordForm.value.key_step_summary.trim();
  if (!summary) {
    completionRecordMessage.value = '给未来的自己留一句提醒，老师也能知道你这题是不是真的收住了。';
    return;
  }
  try {
    const payload = await createStudentProblemCompletion(auth.token, {
      problem_id: problemId.value.trim(),
      problem_title: problemTitle.value.trim(),
      problem_url: normalizedProblemUrl.value,
      session_id: sessionId.value,
      reported_completion: completionRecordForm.value.reported_completion,
      result_status: completionRecordForm.value.result_status,
      key_step_summary: summary,
    });
    completionRecordMessage.value = payload?.message || '做题记录已保存。';
    completionRecordForm.value.key_step_summary = '';
  } catch (err) {
    completionRecordMessage.value = err.message || '做题记录保存失败，请稍后再试。';
  }
}

function latestUserChatMessage() {
  const latest = [...messages.value].reverse().find((item) => item?.role === 'user' && item?.content);
  return latest?.content || message.value.trim();
}

function goToCheckinFromProblemClosure() {
  persistProblemContext();
  completionRecordOpen.value = true;
  completionRecordForm.value.reported_completion = 'aichat_assisted';
  completionRecordForm.value.result_status = 'accepted';
  if (!completionRecordForm.value.key_step_summary.trim()) {
    completionRecordForm.value.key_step_summary = closureAnswer.value.trim();
  }
  completionRecordMessage.value = '这题已经通过结束验证，可以在这里记录做题结果。';
  closurePanelOpen.value = false;
}

function currentUnderstandingPayload() {
  return {
    problem_id: problemId.value.trim(),
    session_id: sessionId.value,
    problem_title: problemTitle.value.trim(),
    problem_context: problemContext.value.trim(),
    student_code: studentCode.value.trim(),
    chat_model_provider: selectedChatModel.value,
  };
}

async function openUnderstandingQuiz() {
  if (!canVerifyUnderstanding.value) return;
  verificationLoading.value = true;
  verificationAnswer.value = '';
  verificationFeedback.value = '';
  try {
    const result = await generateUnderstandingCheck(auth.token, currentUnderstandingPayload());
    if (result.status !== 'ok') {
      verificationQuiz.value = null;
      verificationFeedback.value = result.message || '这一步还没准备好验证，先继续问 AIChat。';
      return;
    }
    verificationQuiz.value = result;
    understandingState.value = 'quiz_ready';
  } catch (err) {
    verificationQuiz.value = null;
    verificationFeedback.value = err.message || '这一步还没准备好验证，先继续问 AIChat。';
  } finally {
    verificationLoading.value = false;
  }
}

async function submitUnderstandingQuiz() {
  if (!verificationQuiz.value || !verificationAnswer.value.trim()) return;
  verificationChecking.value = true;
  verificationFeedback.value = '';
  try {
    const result = await gradeUnderstandingCheck(auth.token, {
      ...currentUnderstandingPayload(),
      question: verificationQuiz.value.question,
      answer: verificationAnswer.value.trim(),
      target_focus: verificationQuiz.value.target_focus || '',
      quiz_format: verificationQuiz.value.quiz_format || '',
    });
    verificationFeedback.value = result.feedback || '已检查你的回答。';
    if (result.status === 'passed' && result.can_review) {
      understandingState.value = 'quiz_passed';
      return;
    }
    understandingState.value = result.status === 'partial' ? 'needs_more_help' : 'not_ready';
    if (result.followup) {
      verificationFeedback.value = `${verificationFeedback.value}\n${result.followup}`;
    }
  } catch (err) {
    understandingState.value = 'needs_more_help';
    verificationFeedback.value = err.message || '这次验证暂时没有批改成功，先继续问 AIChat。';
  } finally {
    verificationChecking.value = false;
  }
}

async function startFinishProblemFlow() {
  if (!canStartProblemClosure.value) return;
  if (!hasProblemIdentity.value) {
    error.value = '请先填写题目链接或题号，再结束本题。';
    return;
  }
  closureLoading.value = true;
  closureFeedback.value = '';
  closureAnswer.value = '';
  persistProblemContext();
  try {
    const result = await startProblemClosure(auth.token, currentUnderstandingPayload());
    if (result.status !== 'ok') {
      problemClosure.value = null;
      closureFeedback.value = result.message || '这题暂时还不能结束，先继续问 AIChat。';
      closurePanelOpen.value = true;
      return;
    }
    problemClosure.value = {
      ...result,
      points_awarded: 0,
      next_review_message: '',
    };
    closurePanelOpen.value = true;
  } catch (err) {
    problemClosure.value = null;
    closureFeedback.value = err.message || '结束本题验证暂时生成失败，先继续问 AIChat。';
    closurePanelOpen.value = true;
  } finally {
    closureLoading.value = false;
  }
}

async function submitProblemClosureAnswer() {
  if (!problemClosure.value?.closure_id || !closureAnswer.value.trim()) return;
  closureChecking.value = true;
  closureFeedback.value = '';
  try {
    const result = await gradeProblemClosure(auth.token, {
      ...currentUnderstandingPayload(),
      closure_id: problemClosure.value.closure_id,
      answer: closureAnswer.value.trim(),
      quiz_format: problemClosure.value.quiz_format || '',
    });
    problemClosure.value = {
      ...problemClosure.value,
      ...result,
      question: result.can_start_next_problem
        ? problemClosure.value.question
        : (result.followup || problemClosure.value.question),
    };
    const feedbackParts = [
      result.feedback,
      result.next_review_message,
    ].filter(Boolean);
    closureFeedback.value = feedbackParts.join('\n');
    if (!result.can_start_next_problem && result.followup) {
      closureAnswer.value = '';
      closurePanelOpen.value = true;
    }
  } catch (err) {
    closureFeedback.value = err.message || '这次验证暂时没有批改成功，先继续问 AIChat。';
  } finally {
    closureChecking.value = false;
  }
}

function continueFromClosureFeedback() {
  const followup = problemClosure.value?.followup || '我刚才的结束验证哪里还没说清楚？';
  message.value = followup;
  activeWorkspaceTab.value = 'ai';
  nextTick(() => {
    document.getElementById('chat-message-input')?.focus();
  });
}

async function loadRunnerHealth() {
  runnerLoading.value = true;
  try {
    runnerHealth.value = await getRunnerHealth(auth.token);
  } catch (err) {
    runnerHealth.value = {
      available: false,
      message: err.message || '当前服务器暂不支持代码运行，仍然可以把代码发给 AIChat 讨论。',
    };
  } finally {
    runnerLoading.value = false;
  }
}

async function loadChatHistory() {
  const currentProblemId = problemId.value.trim();
  if (!currentProblemId || !sessionId.value) return;
  try {
    const result = await getChatHistory(auth.token, {
      problem_id: currentProblemId,
      session_id: sessionId.value,
      limit: 80,
    });
    if (Array.isArray(result?.messages) && result.messages.length > 0) {
      messages.value = result.messages.filter((item) => item?.role && item?.content);
      await scrollChatToBottom();
    }
  } catch (err) {
    console.warn('load chat history failed', err);
  }
}

async function importCurrentLuoguProblem() {
  const rawRef = problemId.value.trim();
  if (!rawRef || importingProblem.value) return;
  importingProblem.value = true;
  error.value = '';
  problemImportMessage.value = '';
  try {
    const result = await importProblem(auth.token, { url: rawRef });
    problemId.value = result.problem_url || rawRef;
    problemTitle.value = result.problem_title || '';
    problemContext.value = result.problem_context || '';
    persistProblemContext();
    problemImportMessage.value = result.message || '已读取题目内容';
  } catch (err) {
    error.value = err.message || '读取题目失败，请手动补题目背景';
  } finally {
    importingProblem.value = false;
  }
}

function attachCodeToNextQuestion() {
  if (!studentCode.value.trim()) {
    runMessage.value = '右侧还没有代码，先写一点再带给 AIChat。';
    return;
  }
  includeCodeInNextMessage.value = true;
  activeWorkspaceTab.value = 'ai';
  nextTick(() => {
    document.getElementById('chat-message-input')?.focus();
  });
}

function clearCodeAttachment() {
  includeCodeInNextMessage.value = false;
}

function chatModelShortLabel(option) {
  return CHAT_MODEL_FALLBACK_LABELS[option?.provider_id] || option?.label || '模型';
}

function selectChatModel(providerId) {
  const option = chatModels.value.find((item) => item.provider_id === providerId);
  if (!option?.available) return;
  selectedChatModel.value = providerId;
  window.localStorage.setItem(CHAT_MODEL_STORAGE_KEY, providerId);
}

function selectChatPromptMode(promptMode) {
  const option = CHAT_PROMPT_MODE_OPTIONS.find((item) => item.value === promptMode);
  if (!option) return;
  selectedChatPromptMode.value = promptMode;
  window.localStorage.setItem(CHAT_PROMPT_MODE_STORAGE_KEY, promptMode);
}

async function loadChatModels() {
  chatModelsLoading.value = true;
  try {
    const result = await getChatModels(auth.token);
    chatModels.value = Array.isArray(result?.models) ? result.models : [];
    const selected = chatModels.value.find((item) => item.provider_id === selectedChatModel.value && item.available);
    const fallback = chatModels.value.find((item) => item.provider_id === result?.default_provider && item.available)
      || chatModels.value.find((item) => item.available);
    if (!selected && fallback) {
      selectedChatModel.value = fallback.provider_id;
      window.localStorage.setItem(CHAT_MODEL_STORAGE_KEY, fallback.provider_id);
    }
  } catch (err) {
    chatModels.value = [
      { provider_id: 'deepseek_flash', label: '快速模式', model: 'deepseek-v4-flash', available: false, reason: '模型列表暂时不可用' },
      { provider_id: 'deepseek_pro', label: '专业模式', model: 'deepseek-v4-pro', available: false, reason: '模型列表暂时不可用' },
    ];
  } finally {
    chatModelsLoading.value = false;
  }
}

function clampChatWindowPosition(x, y) {
  return {
    x: Math.min(Math.max(16, x), Math.max(16, window.innerWidth - chatWindowSize.value.width - 16)),
    y: Math.min(Math.max(16, y), Math.max(16, window.innerHeight - 320)),
  };
}

function clampChatWindowSize(width, height) {
  const minWidth = Math.min(384, Math.max(300, window.innerWidth - 32));
  const minHeight = Math.min(448, Math.max(360, window.innerHeight - 32));
  return {
    width: Math.min(Math.max(minWidth, Math.round(width)), Math.max(minWidth, window.innerWidth - 32)),
    height: Math.min(Math.max(minHeight, Math.round(height)), Math.max(minHeight, window.innerHeight - 32)),
  };
}

function syncChatWindowSizeFromElement() {
  if (!chatFloating.value || !chatWindowRef.value) return;
  const rect = chatWindowRef.value.getBoundingClientRect();
  const next = clampChatWindowSize(rect.width, rect.height);
  if (
    Math.abs(next.width - chatWindowSize.value.width) > 1
    || Math.abs(next.height - chatWindowSize.value.height) > 1
  ) {
    chatWindowSize.value = next;
  }
}

function stopChatResizeObserver() {
  chatResizeObserver?.disconnect();
  chatResizeObserver = null;
}

function startChatResizeObserver() {
  stopChatResizeObserver();
  if (!chatFloating.value || !chatWindowRef.value || !window.ResizeObserver) return;
  chatResizeObserver = new ResizeObserver(() => {
    syncChatWindowSizeFromElement();
  });
  chatResizeObserver.observe(chatWindowRef.value);
}

function handleWindowResize() {
  if (!chatFloating.value) return;
  chatWindowSize.value = clampChatWindowSize(chatWindowSize.value.width, chatWindowSize.value.height);
  chatWindowPosition.value = clampChatWindowPosition(chatWindowPosition.value.x, chatWindowPosition.value.y);
}

async function toggleChatFloating() {
  chatFloating.value = !chatFloating.value;
  if (chatFloating.value) {
    activeWorkspaceTab.value = workspaceMode.value === 'code' ? 'code' : 'problem';
    await nextTick();
    startChatResizeObserver();
  } else {
    syncChatWindowSizeFromElement();
    stopChatResizeObserver();
    activeWorkspaceTab.value = 'ai';
  }
  await scrollChatToBottom();
}

function moveFloatingChat(event) {
  if (!chatFloating.value) return;
  const next = clampChatWindowPosition(
    event.clientX - chatDragOffset.value.x,
    event.clientY - chatDragOffset.value.y,
  );
  chatWindowPosition.value = next;
}

function stopChatDrag() {
  window.removeEventListener('pointermove', moveFloatingChat);
  window.removeEventListener('pointerup', stopChatDrag);
}

function beginChatDrag(event) {
  if (!chatFloating.value || event.button !== 0) return;
  chatDragOffset.value = {
    x: event.clientX - chatWindowPosition.value.x,
    y: event.clientY - chatWindowPosition.value.y,
  };
  window.addEventListener('pointermove', moveFloatingChat);
  window.addEventListener('pointerup', stopChatDrag);
}

async function switchWorkspaceMode(mode) {
  workspaceMode.value = mode;
  activeWorkspaceTab.value = mode === 'code' ? 'code' : 'problem';
  if (mode === 'code') {
    await nextTick();
    await initializeCodeMirror();
    codeEditor?.requestMeasure();
  }
}

async function runCode() {
  if (!canRunCode.value) return;
  runningCode.value = true;
  actualOutput.value = '';
  compileOutput.value = '';
  runMessage.value = '';
  runStatus.value = '';
  persistProblemContext();
  try {
    const result = await runStudentCode(auth.token, {
      language: 'cpp17',
      code: studentCode.value,
      stdin: sampleInput.value,
      problem_ref: problemId.value.trim(),
    });
    actualOutput.value = result.stdout || '';
    compileOutput.value = [result.compile_output, result.stderr].filter(Boolean).join('\n');
    runMessage.value = result.message || '运行完成';
    runStatus.value = result.status || '';
  } catch (err) {
    runMessage.value = err.message || '运行失败，请稍后再试';
    runStatus.value = 'runtime_error';
  } finally {
    runningCode.value = false;
  }
}

async function scrollChatToBottom() {
  await nextTick();
  const el = chatListRef.value;
  if (el) {
    el.scrollTop = el.scrollHeight;
  }
}

async function submitMessage() {
  if (!canSend.value) return;
  if (!hasProblemIdentity.value) {
    error.value = '请先填写题目链接或题号，这样 AIChat 才能结合题意继续帮你看。';
    return;
  }
  sending.value = true;
  error.value = '';
  persistProblemContext();
  const userMessage = message.value.trim();
  messages.value.push({ role: 'user', content: userMessage });
  const thinkingMessage = { role: 'assistant', content: THINKING_MESSAGE, isThinking: true };
  messages.value.push(thinkingMessage);
  message.value = '';
  await scrollChatToBottom();
  try {
    const result = await sendChat(auth.token, {
      student_id: auth.userId,
      problem_id: problemId.value.trim(),
      session_id: sessionId.value,
      message: userMessage,
      problem_url: normalizedProblemUrl.value,
      problem_title: problemTitle.value.trim(),
      problem_context: problemContext.value.trim(),
      student_code: includeCodeInNextMessage.value ? studentCode.value.trim() : '',
      chat_model_provider: selectedChatModel.value,
      aichat_prompt_mode: selectedChatPromptMode.value,
    });
    includeCodeInNextMessage.value = false;
    const thinkingIndex = messages.value.findIndex((item) => item?.isThinking);
    if (thinkingIndex >= 0) {
      messages.value[thinkingIndex] = { role: 'assistant', content: result.reply };
    } else {
      messages.value.push({ role: 'assistant', content: result.reply });
    }
    persistHandoffPayload(result.handoff_payload);
    understandingState.value = result.understanding_state || 'not_ready';
    understandingEvidence.value = result.understanding_evidence || [];
    verificationQuiz.value = null;
    verificationAnswer.value = '';
    verificationFeedback.value = '';
    level.value = result.level;
  } catch (err) {
    messages.value = messages.value.filter((item) => !item?.isThinking);
    error.value = err.message || '发送失败，请稍后重试';
  } finally {
    sending.value = false;
    await scrollChatToBottom();
  }
}

function handleMessageKeydown(event) {
  if (event.isComposing || composingMessage.value) return;
  if (event.key === 'Enter' && !event.shiftKey && !event.metaKey && !event.ctrlKey && !event.altKey) {
    event.preventDefault();
    submitMessage();
  }
}

async function getCodeMirrorModules() {
  if (!codeMirrorModulesPromise) {
    codeMirrorModulesPromise = Promise.all([
      import('codemirror'),
      import('@codemirror/view'),
      import('@codemirror/commands'),
      import('@codemirror/lang-cpp'),
    ]).then(([codemirrorModule, viewModule, commandsModule, cppModule]) => ({
      EditorView: codemirrorModule.EditorView,
      basicSetup: codemirrorModule.basicSetup,
      keymap: viewModule.keymap,
      indentWithTab: commandsModule.indentWithTab,
      cpp: cppModule.cpp,
    }));
  }
  return codeMirrorModulesPromise;
}

async function initializeCodeMirror() {
  if (!codeEditorHost.value || codeEditor) return;
  const { EditorView, basicSetup, keymap, indentWithTab, cpp } = await getCodeMirrorModules();
  if (!codeEditorHost.value || codeEditor) return;
  codeEditor = new EditorView({
    doc: studentCode.value,
    extensions: [
      basicSetup,
      cpp(),
      EditorView.lineWrapping,
      keymap.of([
        indentWithTab,
        {
          key: 'Ctrl-Enter',
          run: () => {
            runCode();
            return true;
          },
        },
      ]),
      EditorView.updateListener.of((update) => {
        if (!update.docChanged) return;
        studentCode.value = update.state.doc.toString();
        persistCodeForCurrentProblem();
      }),
    ],
    parent: codeEditorHost.value,
  });
}

watch(messages, scrollChatToBottom, { deep: true });
watch(sampleInput, persistProblemContext);
watch([problemClosure, closureAnswer, closureFeedback], persistProblemClosureState, { deep: true });
watch(workspaceMode, async (mode) => {
  if (mode !== 'code') return;
  await nextTick();
  await initializeCodeMirror();
  codeEditor?.requestMeasure();
});
watch(codeCacheKey, () => {
  loadCodeForCurrentProblem();
});
watch(studentCode, (value) => {
  if (codeEditor && codeEditor.state.doc.toString() !== value) {
    codeEditor.dispatch({
      changes: { from: 0, to: codeEditor.state.doc.length, insert: value },
    });
  }
});

onMounted(() => {
  loadCodeForCurrentProblem();
  restoreProblemClosureState();
  loadChatModels();
  loadRunnerHealth();
  loadChatHistory();
  scrollChatToBottom();
  window.addEventListener('resize', handleWindowResize);
});

onBeforeUnmount(() => {
  codeEditor?.destroy();
  codeEditor = null;
  stopChatDrag();
  stopChatResizeObserver();
  window.removeEventListener('resize', handleWindowResize);
});
</script>

<template>
  <div class="space-y-5">
    <section class="panel workspace-card-chat">
      <div class="grid gap-3 xl:grid-cols-[minmax(0,1fr)_auto_auto] xl:items-end">
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-600">题号 / 题目链接</label>
          <input v-model="problemId" class="field" placeholder="例如 P2922、P2678，或直接贴题目链接" />
        </div>
        <div>
          <p class="mb-2 text-sm font-semibold text-slate-600">学习模式</p>
          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              :class="['tag-pill border transition', workspaceMode === 'read' ? 'border-chat-500 bg-chat-500 text-white' : 'border-slate-200 bg-white text-slate-600']"
              @click="switchWorkspaceMode('read')"
            >
              读题问 AI
            </button>
            <button
              type="button"
              :class="['tag-pill border transition', workspaceMode === 'code' ? 'border-chat-500 bg-chat-500 text-white' : 'border-slate-200 bg-white text-slate-600']"
              @click="switchWorkspaceMode('code')"
            >
              写代码问 AI
            </button>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <button class="button-secondary px-4 py-3 text-sm" :disabled="!problemId.trim() || importingProblem" type="button" @click="importCurrentLuoguProblem">
            {{ importingProblem ? '正在读取...' : '读取题目' }}
          </button>
          <button class="button-secondary px-4 py-3 text-sm" type="button" @click="clearProblemContext">清空当前题背景</button>
          <button class="button-secondary px-4 py-3 text-sm" type="button" @click="completionRecordOpen = !completionRecordOpen">
            记录做完的题
          </button>
          <button class="button-primary bg-gradient-to-r from-checkin-500 via-amber-500 to-orange-500 px-4 py-3 text-sm" type="button" @click="goToCheckinWithCurrentProblem">
            带着当前题去深入复盘
          </button>
        </div>
      </div>
      <div class="mt-3 flex flex-wrap items-center gap-3 text-xs font-semibold text-slate-500">
        <span>当前账号：{{ auth.userId }}</span>
        <span>当前层级：{{ level || '—' }}</span>
        <span v-if="problemImportMessage" class="text-emerald-600">{{ problemImportMessage }}</span>
      </div>
      <div v-if="completionRecordOpen" class="mt-4 rounded-[24px] border border-emerald-100 bg-white/90 p-4 shadow-sm">
        <div class="flex flex-col gap-1">
          <p class="font-semibold text-slate-900">做题记录</p>
          <p class="text-xs leading-5 text-slate-500">这不和别人比较，只是帮老师了解你这题是怎么做出来的。</p>
        </div>
        <div class="mt-4 grid gap-3 md:grid-cols-2">
          <label class="block text-sm font-semibold text-slate-600">
            <span class="mb-2 block">我是怎么完成的</span>
            <select v-model="completionRecordForm.reported_completion" class="field w-full">
              <option value="self_solved">我自己做出来了</option>
              <option value="small_hint">看了少量提示后做出来</option>
              <option value="classroom_taught">老师讲过后做出来</option>
              <option value="aichat_assisted">AIChat 帮助后做出来</option>
              <option value="editorial_completed">看题解后补完</option>
              <option value="unsure">还没完全确定</option>
            </select>
          </label>
          <label class="block text-sm font-semibold text-slate-600">
            <span class="mb-2 block">结果</span>
            <select v-model="completionRecordForm.result_status" class="field w-full">
              <option value="accepted">AC</option>
              <option value="sample_passed">样例通过，还没提交</option>
              <option value="unsure">还不确定</option>
            </select>
          </label>
        </div>
        <label class="mt-3 block text-sm font-semibold text-slate-600">
          <span class="mb-2 block">下次我会先想什么</span>
          <textarea
            v-model="completionRecordForm.key_step_summary"
            class="field mt-3 min-h-[112px] w-full resize-y"
            placeholder="例如：遇到按时间变化的最短路，先想能不能按时间顺序逐步更新，而不是每次询问都重算。"
          />
        </label>
        <div class="mt-3 flex flex-wrap items-center gap-3">
          <button class="button-primary px-4 py-2 text-sm" type="button" @click="submitProblemCompletionRecord">保存做题记录</button>
          <p v-if="completionRecordMessage" class="text-sm font-medium text-slate-600">{{ completionRecordMessage }}</p>
        </div>
      </div>
    </section>

    <div class="flex gap-2 xl:hidden">
      <button
        v-for="tab in [
          { id: 'problem', label: '题目' },
          { id: 'ai', label: 'AI' },
          { id: 'code', label: '代码' },
        ]"
        :key="tab.id"
        type="button"
        :class="['tag-pill border transition', activeWorkspaceTab === tab.id ? 'border-chat-500 bg-chat-500 text-white' : 'border-slate-200 bg-white text-slate-600']"
        @click="activeWorkspaceTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div
      :class="[
        'grid gap-5',
        chatFloating ? 'floating-chat-grid' : '',
        chatFloating ? 'xl:grid-cols-1' : workspaceMode === 'read'
          ? 'read-mode-grid xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]'
          : 'code-mode-grid xl:grid-cols-[minmax(0,1.35fr)_minmax(0,0.9fr)]',
      ]"
    >
      <section :class="[activeWorkspaceTab === 'problem' ? 'block' : 'hidden', workspaceMode === 'read' ? 'xl:block' : 'xl:hidden', 'panel workspace-card-chat min-h-[34rem] xl:order-1']">
        <p class="section-eyebrow text-chat-700">当前题目</p>
        <input v-model="problemTitle" class="field mt-4" placeholder="题目标题，可自动读取或手动补充" />
        <div class="mt-4 min-h-[24rem] overflow-auto rounded-[24px] border border-chat-100 bg-white/90 p-5">
          <p class="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-chat-700">题面 Markdown 预览</p>
          <p v-if="!problemContext.trim()" class="text-sm leading-7 text-slate-500">
            读取题目后，题面会放在这里。也可以手动贴题意、数据范围、样例解释。
          </p>
          <article v-else class="problem-markdown text-sm leading-7 text-slate-700" v-html="renderedProblemContext"></article>
        </div>
        <details class="mt-4 rounded-[20px] border border-chat-100 bg-white/75 p-4">
          <summary class="cursor-pointer text-sm font-semibold text-chat-700">编辑题面原文</summary>
          <textarea
            v-model="problemContext"
            class="field mt-3 min-h-40 resize-y"
            placeholder="如果自动读取不完整，可以在这里补题面、数据范围、样例。"
          />
        </details>
      </section>

      <section
        ref="chatWindowRef"
        :class="[
          chatFloating ? 'fixed' : '',
          chatFloating ? 'floating-chat-window z-50 flex min-h-[28rem] min-w-[24rem] max-h-[calc(100vh-2rem)] max-w-[calc(100vw-2rem)] resize overflow-hidden rounded-[24px] border border-chat-200 bg-white/95 p-5 shadow-2xl shadow-slate-900/20 backdrop-blur' : 'panel workspace-card-chat min-h-[34rem] xl:order-2 xl:self-start xl:h-[42rem]',
          chatFloating ? 'flex' : activeWorkspaceTab === 'ai' ? 'flex' : 'hidden',
          'flex-col xl:flex',
        ]"
        :style="floatingChatStyle"
      >
        <div
          :class="[
            'mb-4 flex items-start justify-between gap-3',
            chatFloating ? 'compact-floating-chat-header' : '',
            chatFloating ? 'cursor-move select-none' : '',
          ]"
          @pointerdown="beginChatDrag"
        >
          <div>
            <p class="section-eyebrow text-chat-700">AI 对话</p>
            <h3 :class="[chatFloating ? 'mt-1 text-xl' : 'mt-2 text-2xl', 'font-display font-bold text-slate-900']">把问题发给 AI</h3>
            <p v-if="!chatFloating" class="mt-3 text-sm leading-7 text-slate-600">我这次卡在哪一步？先讲清这一步，再让 AIChat 顺着你的思路帮你拆。</p>
            <div v-if="!chatFloating" class="mt-3 flex flex-wrap items-center gap-2 text-xs font-semibold">
              <span class="text-slate-500">模型</span>
              <button
                v-for="option in chatModels"
                :key="option.provider_id"
                type="button"
                :disabled="!option.available"
                :title="option.reason"
                :class="[
                  'rounded-lg border px-3 py-1.5 transition',
                  selectedChatModel === option.provider_id
                    ? 'border-chat-500 bg-chat-500 text-white'
                    : option.available
                      ? 'border-slate-200 bg-white text-slate-600 hover:border-chat-300 hover:text-chat-700'
                      : 'cursor-not-allowed border-slate-100 bg-slate-50 text-slate-300',
                ]"
                @pointerdown.stop
                @click="selectChatModel(option.provider_id)"
              >
                {{ chatModelShortLabel(option) }}
              </button>
              <span v-if="chatModelsLoading" class="text-slate-400">加载中...</span>
              <span v-else-if="selectedChatModelInfo" class="text-slate-400">当前：{{ selectedChatModelInfo.label }}</span>
            </div>
            <div v-if="!chatFloating" class="mt-2 flex flex-wrap items-center gap-2 text-xs font-semibold">
              <span class="text-slate-500">回答方式</span>
              <button
                v-for="option in CHAT_PROMPT_MODE_OPTIONS"
                :key="option.value"
                type="button"
                :title="option.description"
                :class="[
                  'rounded-lg border px-3 py-1.5 transition',
                  selectedChatPromptMode === option.value
                    ? 'border-emerald-500 bg-emerald-500 text-white'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-emerald-300 hover:text-emerald-700',
                ]"
                @pointerdown.stop
                @click="selectChatPromptMode(option.value)"
              >
                {{ option.label }}
              </button>
              <span class="basis-full text-[11px] font-medium leading-5 text-slate-400 sm:basis-auto">
                教练引导会把当前问题拆成一个小步骤，适合真正卡住时使用。
              </span>
            </div>
            <div v-if="chatFloating" class="floating-model-switcher mt-2 flex flex-wrap items-center gap-2 text-xs font-semibold" @pointerdown.stop>
              <span class="text-slate-500">当前模型</span>
              <select
                v-model="selectedChatModel"
                class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-semibold text-slate-700 outline-none transition focus:border-chat-400"
                @change="selectChatModel(selectedChatModel)"
              >
                <option
                  v-for="option in chatModels"
                  :key="option.provider_id"
                  :value="option.provider_id"
                  :disabled="!option.available"
                >
                  {{ chatModelShortLabel(option) }}
                </option>
              </select>
              <span class="text-slate-500">回答方式</span>
              <select
                v-model="selectedChatPromptMode"
                class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-semibold text-slate-700 outline-none transition focus:border-emerald-400"
                @change="selectChatPromptMode(selectedChatPromptMode)"
              >
                <option
                  v-for="option in CHAT_PROMPT_MODE_OPTIONS"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </div>
            <p v-if="chatFloating" class="mt-1 text-xs font-semibold text-slate-400">拖动标题移动，拖动右下角缩放</p>
          </div>
          <div class="flex shrink-0 flex-wrap gap-2">
            <button class="button-secondary hidden px-3 py-2 text-xs xl:inline-flex" type="button" @pointerdown.stop @click="toggleChatFloating">
              {{ chatFloating ? '回到右侧' : '悬浮对话' }}
            </button>
            <button v-if="showProblemClosurePanel" class="button-primary px-3 py-2 text-xs" type="button" @pointerdown.stop @click="closurePanelOpen = true">
              继续结束验证
            </button>
            <button v-else class="button-primary px-3 py-2 text-xs" type="button" :disabled="!canStartProblemClosure" @pointerdown.stop @click="startFinishProblemFlow">
              {{ problemClosureButtonLabel }}
            </button>
            <button class="button-secondary px-3 py-2 text-xs" type="button" @pointerdown.stop @click="resetSession">清空对话</button>
          </div>
        </div>

        <div ref="chatListRef" class="flex-1 space-y-4 overflow-auto rounded-[24px] border border-chat-100 bg-white/90 p-4">
          <div v-if="messages.length === 0" class="rounded-[24px] border border-dashed border-chat-200 bg-chat-50/60 p-5 text-sm leading-7 text-slate-500">
            可以问：“这题为什么要二分，直接枚举会慢在哪里？”也可以先写代码，再把代码带进问题里。
          </div>
          <article
            v-for="(item, index) in messages"
            :key="`${item.role}-${index}`"
            :class="item.role === 'user'
              ? 'ml-auto max-w-[88%] rounded-[24px] bg-gradient-to-br from-chat-500 to-cyan-500 px-5 py-4 text-sm leading-7 text-white shadow-lg shadow-chat-500/20'
              : item.isThinking
                ? 'mr-auto max-w-[88%] rounded-[24px] border border-sky-100 bg-sky-50/80 px-5 py-4 text-sm leading-7 text-slate-600 shadow-sm'
                : 'mr-auto max-w-[88%] rounded-[24px] border border-slate-200 bg-white px-5 py-4 text-sm leading-7 text-slate-700 shadow-sm'"
          >
            <div v-if="item.isThinking" class="space-y-2">
              <span class="block whitespace-pre-wrap break-words font-medium">{{ item.content }}</span>
              <div class="flex items-center gap-1 text-sky-500">
                <span class="h-2 w-2 animate-pulse rounded-full bg-current"></span>
                <span class="h-2 w-2 animate-pulse rounded-full bg-current [animation-delay:120ms]"></span>
                <span class="h-2 w-2 animate-pulse rounded-full bg-current [animation-delay:240ms]"></span>
              </div>
            </div>
            <span v-else-if="item.role === 'user'" class="whitespace-pre-wrap break-words">{{ item.content }}</span>
            <template v-else>
              <div
                v-if="cleanChatMessageContent(item.content)"
                class="problem-markdown text-sm leading-7 text-slate-700"
                v-html="renderedChatMessage(cleanChatMessageContent(item.content))"
              ></div>
              <div v-if="messageDiagramBlocks(item.content).length" class="mt-3 flex flex-wrap gap-2">
                <button
                  v-for="(block, blockIndex) in messageDiagramBlocks(item.content)"
                  :key="`${index}-${block.type}-${blockIndex}`"
                  class="inline-flex items-center rounded-lg border border-chat-100 bg-chat-50 px-3 py-2 text-xs font-semibold text-chat-700 transition hover:border-chat-300 hover:bg-chat-100"
                  type="button"
                  @click="openDiagramPanel(block, index, blockIndex)"
                >
                  {{ diagramButtonLabel(block, blockIndex) }}
                </button>
              </div>
            </template>
          </article>
        </div>

        <div :class="[chatFloating ? 'mt-3 space-y-2' : 'mt-4 space-y-3']">
          <div v-if="showUnderstandingPanel" class="rounded-[24px] border border-chat-100 bg-chat-50/60 p-4">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p class="text-sm font-semibold text-slate-800">小验证</p>
                <p class="mt-1 text-xs leading-5 text-slate-500">
                  {{ canVerifyUnderstanding ? '让 AI 根据当前题和对话出一个小问题，检查你是不是真的说清楚。' : understandingState === 'quiz_passed' ? '这一步已经验证通过，可以整理复盘。' : '先把对象、操作或判断关系说清楚，按钮就会亮起。' }}
                </p>
              </div>
              <button
                class="button-primary shrink-0 px-4 py-2 text-sm"
                :disabled="!canVerifyUnderstanding || verificationLoading"
                type="button"
                @click="openUnderstandingQuiz"
              >
                {{ verificationLoading ? '生成中...' : '验证一下' }}
              </button>
            </div>
            <div v-if="verificationQuiz" class="mt-4 rounded-[20px] border border-white bg-white/90 p-4 shadow-sm">
              <p class="text-sm font-semibold text-slate-800">{{ verificationQuiz.question }}</p>
              <textarea
                v-model="verificationAnswer"
                class="field mt-3 min-h-[6rem] resize-y text-sm"
                placeholder="用自己的话回答这一小问，不用写完整题解。"
              />
              <div class="mt-3 flex flex-wrap gap-2">
                <button class="button-secondary px-4 py-2 text-sm" type="button" :disabled="!verificationAnswer.trim() || verificationChecking" @click="submitUnderstandingQuiz">
                  {{ verificationChecking ? '检查中...' : '让 AI 检查一下' }}
                </button>
                <button v-if="understandingState === 'quiz_passed'" class="button-primary px-4 py-2 text-sm" type="button" @click="goToCheckinWithCurrentProblem">
                  整理这题复盘
                </button>
              </div>
              <p v-if="verificationFeedback" class="mt-3 rounded-2xl bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700">
                {{ verificationFeedback }}
              </p>
            </div>
          </div>
          <p v-if="includeCodeInNextMessage" class="rounded-2xl bg-cyan-50 px-4 py-3 text-sm font-medium text-cyan-700">
            下一条问题会带上右侧代码。你只要补一句：想让 AIChat 帮你看哪里。
            <button class="ml-3 inline-flex text-sm font-semibold text-cyan-800 underline decoration-cyan-300 underline-offset-4" type="button" @click="clearCodeAttachment">
              清除带代码
            </button>
          </p>
          <textarea
            id="chat-message-input"
            v-model="message"
            class="field min-h-[7.5rem] max-h-48 flex-none resize-none overflow-y-auto"
            placeholder="例如：我这段 check(mid) 不知道 true 后该往哪边缩。"
            @compositionstart="composingMessage = true"
            @compositionend="composingMessage = false"
            @keydown="handleMessageKeydown"
          />
          <p v-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
            {{ error }}
          </p>
          <button
            class="button-primary w-full bg-gradient-to-r from-chat-500 via-sky-500 to-cyan-500"
            :disabled="!canSend"
            type="button"
            @click="submitMessage"
          >
            {{ sending ? '发送中' : '发送给 AIChat' }}
          </button>
        </div>
        <div v-if="chatFloating" class="floating-chat-resize-hint pointer-events-none absolute bottom-3 right-3 h-5 w-5 rounded-br-[8px] border-b-2 border-r-2 border-chat-300/80"></div>
      </section>

      <section :class="[activeWorkspaceTab === 'code' ? 'block' : 'hidden', workspaceMode === 'code' ? 'xl:block' : 'xl:hidden', 'panel workspace-card-chat min-h-[34rem] xl:order-1']">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="section-eyebrow text-chat-700">代码练习</p>
            <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">代码编辑</h3>
          </div>
          <span class="tag-pill bg-white text-slate-600">CodeMirror</span>
        </div>

        <p v-if="runnerLoading" class="mt-3 text-sm text-slate-500">正在检查代码运行环境...</p>
        <p v-else-if="!runnerAvailable" class="mt-3 rounded-2xl bg-amber-50 px-4 py-3 text-sm font-medium text-amber-700">
          {{ runnerHealth?.message || '当前环境暂不支持代码运行，仍然可以把代码发给 AIChat 讨论。' }}
        </p>

        <div class="editor-toolbar mt-4 flex flex-wrap items-center justify-between gap-2 rounded-[18px] border border-slate-200 bg-white/85 px-3 py-2">
          <div class="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-500">
            <span class="tag-pill bg-slate-100 text-slate-700">C++17</span>
            <span>Ctrl + Enter 运行</span>
            <span>{{ includeCodeInNextMessage ? '本次问题将带上当前代码' : '本次问题未带代码' }}</span>
          </div>
          <div class="flex flex-wrap gap-2">
            <button class="button-secondary px-3 py-2 text-xs" type="button" @click="switchWorkspaceMode('read')">查看题面</button>
            <button class="button-secondary px-3 py-2 text-xs" type="button" @click="attachCodeToNextQuestion">提交给 AIChat</button>
          </div>
        </div>

        <div ref="codeEditorHost" class="code-editor-shell mt-3 min-h-[28rem] overflow-hidden rounded-[18px] border border-slate-200 bg-white text-sm shadow-inner"></div>

        <div class="code-runner-panels mt-4 grid gap-3 md:grid-cols-2">
          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-600">样例输入</label>
            <textarea v-model="sampleInput" class="field min-h-28 resize-y font-mono text-xs" placeholder="把样例输入贴在这里" />
          </div>
          <div>
            <p class="mb-2 text-sm font-semibold text-slate-600">程序输出</p>
            <pre class="min-h-28 whitespace-pre-wrap break-words rounded-[18px] border border-slate-200 bg-white p-4 text-xs text-slate-700">{{ actualOutput || '运行后会显示输出。' }}</pre>
          </div>
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
          <button class="button-primary bg-gradient-to-r from-chat-500 to-cyan-500" :disabled="!canRunCode" type="button" @click="runCode">
            {{ runningCode ? '正在运行...' : '运行代码' }}
          </button>
          <button class="button-secondary" type="button" @click="attachCodeToNextQuestion">带着这段代码提问</button>
        </div>

        <div class="mt-4 space-y-3">
          <p v-if="runMessage" :class="['rounded-2xl px-4 py-3 text-sm font-medium', runStatus === 'ok' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700']">
            {{ runMessage }}
          </p>
          <div v-if="compileOutput">
            <p class="mb-2 text-sm font-semibold text-slate-600">运行信息</p>
            <pre class="max-h-48 overflow-auto whitespace-pre-wrap break-words rounded-[18px] border border-amber-100 bg-amber-50 p-4 text-xs text-amber-800">{{ compileOutput }}</pre>
          </div>
          <p class="text-xs leading-6 text-slate-500">这里是样例运行，不是正式 OJ 提交。真正提交结果还要以 OJ 为准。</p>
        </div>
      </section>
    </div>

    <button
      v-if="showProblemClosurePanel && !closurePanelOpen"
      class="closure-reopen-button fixed bottom-4 right-4 z-50 rounded-lg border border-emerald-200 bg-emerald-600 px-4 py-3 text-sm font-bold text-white shadow-xl shadow-emerald-900/20 transition hover:bg-emerald-700 xl:bottom-6 xl:right-6"
      type="button"
      @click="closurePanelOpen = true"
    >
      打开结束验证
    </button>

    <aside
      v-if="showProblemClosurePanel && closurePanelOpen"
      class="problem-closure-panel fixed bottom-6 right-6 top-24 z-50 hidden w-[min(26rem,calc(100vw-3rem))] flex-col overflow-hidden rounded-[24px] border border-emerald-100 bg-white/95 shadow-2xl shadow-slate-900/20 backdrop-blur xl:flex"
    >
      <div class="flex items-start justify-between gap-3 border-b border-emerald-100 p-4">
        <div>
          <p class="section-eyebrow text-emerald-700">结束本题验证</p>
          <h3 class="mt-1 text-lg font-bold text-slate-900">一题一卡，确认真的会了</h3>
          <p class="mt-2 text-xs leading-5 text-slate-500">贴合当前这一步，30-90 秒完成；只看这一小步，不要求完整题解。</p>
        </div>
        <button class="button-secondary px-3 py-2 text-xs" type="button" @click="closurePanelOpen = false">收起</button>
      </div>
      <div class="flex-1 overflow-auto bg-emerald-50/40 p-4">
        <div class="rounded-[20px] border border-emerald-100 bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <p class="text-xs font-semibold text-emerald-700">请先确认这一小步</p>
            <span v-if="problemClosure?.points_awarded" class="tag-pill bg-emerald-50 text-emerald-700">
              +{{ problemClosure.points_awarded }} 分
            </span>
          </div>
          <div v-if="problemClosure" class="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
            <span class="tag-pill bg-emerald-50 text-emerald-700">问题类型：{{ quizBottleneckLabel(problemClosure) }}</span>
            <span class="tag-pill bg-cyan-50 text-cyan-700">验证题型：{{ quizFormatLabel(problemClosure) }}</span>
          </div>
          <p v-if="problemClosure" class="mt-3 text-sm font-semibold leading-7 text-slate-800">{{ problemClosure.question }}</p>
          <p v-else class="mt-3 text-sm leading-7 text-slate-600">{{ closureFeedback || '验证正在准备中，稍等一下。' }}</p>
          <textarea
            v-if="problemClosure"
            v-model="closureAnswer"
            class="field mt-4 min-h-[8rem] resize-y text-sm"
            placeholder="用自己的话回答，不用写完整题解。"
            :disabled="problemClosure.status === 'passed'"
          />
          <div v-if="problemClosure" class="mt-4 flex flex-wrap gap-2">
            <button
              class="button-secondary px-4 py-2 text-sm"
              type="button"
              :disabled="!closureAnswer.trim() || closureChecking || problemClosure.status === 'passed'"
              @click="submitProblemClosureAnswer"
            >
              {{ closureChecking ? '检查中...' : '提交结束验证' }}
            </button>
            <button v-if="problemClosure.status !== 'passed'" class="button-secondary px-4 py-2 text-sm" type="button" @click="continueFromClosureFeedback">
              继续问 AIChat
            </button>
            <button v-if="problemClosure.status === 'passed'" class="button-primary px-4 py-2 text-sm" type="button" @click="goToCheckinFromProblemClosure">
              记录做题结果
            </button>
            <button v-if="problemClosure.status === 'passed'" class="button-secondary px-4 py-2 text-sm" type="button" @click="resetSession">
              开始下一题
            </button>
          </div>
        </div>
        <p v-if="closureFeedback" class="mt-3 whitespace-pre-wrap rounded-2xl border border-white bg-white/90 px-4 py-3 text-sm font-medium leading-6 text-slate-700">
          {{ closureFeedback }}
        </p>
        <p class="mt-3 rounded-2xl bg-white/80 px-4 py-3 text-xs leading-5 text-slate-500">
          质量标准：贴合当前这一步、能迁移到一个小变体、回答后可以判断是否说清楚。
        </p>
      </div>
    </aside>

    <div
      v-if="showProblemClosurePanel && closurePanelOpen"
      class="closure-bottom-drawer fixed inset-x-3 bottom-3 z-50 max-h-[74vh] overflow-hidden rounded-[24px] border border-emerald-100 bg-white shadow-2xl shadow-slate-900/20 xl:hidden"
    >
      <div class="flex items-start justify-between gap-3 border-b border-emerald-100 p-4">
        <div>
          <p class="section-eyebrow text-emerald-700">结束本题验证</p>
          <h3 class="mt-1 text-base font-bold text-slate-900">一题一卡，确认真的会了</h3>
          <p class="mt-2 text-xs leading-5 text-slate-500">贴合当前这一步，30-90 秒完成。</p>
        </div>
        <button class="button-secondary px-3 py-2 text-xs" type="button" @click="closurePanelOpen = false">收起</button>
      </div>
      <div class="max-h-[58vh] overflow-auto bg-emerald-50/40 p-4">
        <div class="rounded-[20px] border border-emerald-100 bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <p class="text-xs font-semibold text-emerald-700">请先确认这一小步</p>
            <span v-if="problemClosure?.points_awarded" class="tag-pill bg-emerald-50 text-emerald-700">
              +{{ problemClosure.points_awarded }} 分
            </span>
          </div>
          <div v-if="problemClosure" class="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
            <span class="tag-pill bg-emerald-50 text-emerald-700">问题类型：{{ quizBottleneckLabel(problemClosure) }}</span>
            <span class="tag-pill bg-cyan-50 text-cyan-700">验证题型：{{ quizFormatLabel(problemClosure) }}</span>
          </div>
          <p v-if="problemClosure" class="mt-3 text-sm font-semibold leading-7 text-slate-800">{{ problemClosure.question }}</p>
          <p v-else class="mt-3 text-sm leading-7 text-slate-600">{{ closureFeedback || '验证正在准备中，稍等一下。' }}</p>
          <textarea
            v-if="problemClosure"
            v-model="closureAnswer"
            class="field mt-4 min-h-[7rem] resize-y text-sm"
            placeholder="用自己的话回答，不用写完整题解。"
            :disabled="problemClosure.status === 'passed'"
          />
          <div v-if="problemClosure" class="mt-4 flex flex-wrap gap-2">
            <button
              class="button-secondary px-4 py-2 text-sm"
              type="button"
              :disabled="!closureAnswer.trim() || closureChecking || problemClosure.status === 'passed'"
              @click="submitProblemClosureAnswer"
            >
              {{ closureChecking ? '检查中...' : '提交结束验证' }}
            </button>
            <button v-if="problemClosure.status !== 'passed'" class="button-secondary px-4 py-2 text-sm" type="button" @click="continueFromClosureFeedback">
              继续问 AIChat
            </button>
            <button v-if="problemClosure.status === 'passed'" class="button-primary px-4 py-2 text-sm" type="button" @click="goToCheckinFromProblemClosure">
              记录做题结果
            </button>
            <button v-if="problemClosure.status === 'passed'" class="button-secondary px-4 py-2 text-sm" type="button" @click="resetSession">
              开始下一题
            </button>
          </div>
        </div>
        <p v-if="closureFeedback" class="mt-3 whitespace-pre-wrap rounded-2xl border border-white bg-white/90 px-4 py-3 text-sm font-medium leading-6 text-slate-700">
          {{ closureFeedback }}
        </p>
      </div>
    </div>

    <aside
      v-if="diagramPanelOpen && activeDiagram"
      class="diagram-side-panel fixed bottom-6 right-6 top-24 z-40 hidden w-[min(28rem,calc(100vw-3rem))] flex-col overflow-hidden rounded-[24px] border border-chat-100 bg-white/95 shadow-2xl shadow-slate-900/20 backdrop-blur xl:flex"
    >
      <div class="flex items-start justify-between gap-3 border-b border-slate-100 p-4">
        <div>
          <p class="section-eyebrow text-chat-700">AI 图示</p>
          <h3 class="mt-1 text-lg font-bold text-slate-900">{{ activeDiagram.title }}</h3>
        </div>
        <button class="button-secondary px-3 py-2 text-xs" type="button" @click="closeDiagramPanel">收起</button>
      </div>
      <div class="flex items-center justify-between border-b border-slate-100 px-4 py-2 text-xs font-semibold text-slate-500">
        <span>{{ activeDiagram.type === 'mermaid' ? '可缩放流程图' : '等宽文字图' }}</span>
        <div v-if="activeDiagram.type === 'mermaid'" class="flex gap-2">
          <button class="rounded-lg border border-slate-200 px-2 py-1" type="button" @click="adjustDiagramZoom(-0.1)">缩小</button>
          <button class="rounded-lg border border-slate-200 px-2 py-1" type="button" @click="adjustDiagramZoom(0.1)">放大</button>
        </div>
      </div>
      <div class="flex-1 overflow-auto bg-slate-50/80 p-4">
        <pre v-if="activeDiagram.type === 'diagram-ascii'" class="whitespace-pre overflow-auto rounded-[18px] bg-white p-4 font-mono text-sm leading-6 text-slate-800">{{ activeDiagram.code }}</pre>
        <div v-else class="min-h-full min-w-full overflow-auto rounded-[18px] bg-white p-4">
          <p v-if="diagramError" class="mb-3 rounded-2xl bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">{{ diagramError }}</p>
          <div v-if="diagramSvg" class="mermaid-rendered origin-top-left" :style="{ transform: `scale(${diagramZoom})` }" v-html="diagramSvg"></div>
          <pre v-else class="whitespace-pre overflow-auto font-mono text-xs leading-5 text-slate-700">{{ activeDiagram.code }}</pre>
        </div>
      </div>
    </aside>

    <div
      v-if="diagramPanelOpen && activeDiagram"
      class="diagram-bottom-drawer fixed inset-x-3 bottom-3 z-40 max-h-[70vh] overflow-hidden rounded-[24px] border border-chat-100 bg-white shadow-2xl shadow-slate-900/20 xl:hidden"
    >
      <div class="flex items-center justify-between gap-3 border-b border-slate-100 p-4">
        <div>
          <p class="section-eyebrow text-chat-700">AI 图示</p>
          <h3 class="mt-1 text-base font-bold text-slate-900">{{ activeDiagram.title }}</h3>
        </div>
        <button class="button-secondary px-3 py-2 text-xs" type="button" @click="closeDiagramPanel">收起</button>
      </div>
      <div class="max-h-[52vh] overflow-auto bg-slate-50/80 p-4">
        <pre v-if="activeDiagram.type === 'diagram-ascii'" class="whitespace-pre overflow-auto rounded-[18px] bg-white p-4 font-mono text-xs leading-5 text-slate-800">{{ activeDiagram.code }}</pre>
        <div v-else class="overflow-auto rounded-[18px] bg-white p-4">
          <p v-if="diagramError" class="mb-3 rounded-2xl bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">{{ diagramError }}</p>
          <div v-if="diagramSvg" class="mermaid-rendered" v-html="diagramSvg"></div>
          <pre v-else class="whitespace-pre overflow-auto font-mono text-xs leading-5 text-slate-700">{{ activeDiagram.code }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>
