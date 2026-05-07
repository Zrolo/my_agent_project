<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';

import {
  getTeacherAIChatSessionAnalysisHealth,
  getTeacherAIChatSessionAnalysis,
  getTeacherAIChatSessionDetail,
  getTeacherAIChatSessions,
  getTeacherAIChatStudents,
  retryTeacherAIChatSessionAnalysis,
} from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();

const loadingStudents = ref(false);
const loadingSessions = ref(false);
const loadingDetail = ref(false);
const showConversation = ref(false);
const showSystemEvidence = ref(false);
const error = ref('');
const students = ref([]);
const sessions = ref([]);
const detail = ref(null);
const sessionAnalysis = ref(null);
const analysisHealth = ref(null);
const analysisPollingTimer = ref(null);
const selectedStudentId = ref('');
const selectedSessionId = ref('');

const evidenceLabels = [
  ['problem_goal', '已表达题目目标'],
  ['object_relation', '已提出对象关系'],
  ['method_sketch', '已有方法雏形'],
  ['debug_evidence', '已提供错误样例'],
  ['self_correction', '出现自我修正'],
  ['quiz_passed', '已通过 quiz'],
];

const actionTextMap = {
  give_micro_scaffold: '给了半步提示',
  give_micro_example: '给了小例子',
  offer_checkin_reflection: '建议进入复盘',
  offer_micro_example_or_checkin: '给小例子后建议整理',
  ask_one_question: '追问一个关键点',
  ask_baseline_attempt: '请学生先说初步想法',
  ask_slot_question: '追问缺失信息',
  build_application_bridge: '帮学生接上应用步骤',
  summarize_and_bridge: '先收拢再过渡',
  diagnose_code_locally: '围绕局部代码诊断',
  ask_debug_evidence: '请学生补充错误样例',
  ask_code_evidence: '请学生补充代码证据',
  request_problem_context: '请学生补充题目背景',
  refuse_injection: '拉回题目本身',
};

function formatTime(value) {
  if (!value) return '暂无时间';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString('zh-CN', { hour12: false });
}

function studentName(row) {
  return row?.student_real_name || row?.student_username || row?.student_id || '未命名学生';
}

function evidenceFlag(flags, key) {
  return Boolean(flags && flags[key]);
}

function evidenceCount(flags) {
  return evidenceLabels.filter(([key]) => evidenceFlag(flags, key)).length;
}

function actionText(action) {
  if (!action) return '暂无判断';
  return actionTextMap[action] || String(action).replaceAll('_', ' ');
}

function studentAttentionReason(row) {
  if (!row) return '暂无学习证据';
  if (!row.total_messages) return '还没有可判断的对话';
  return `最近在 ${row.recent_problem_id || '未记录题目'} 留下 ${row.total_messages} 条对话，可先看最近一次。`;
}

function sessionTitle(session) {
  return session?.problem_title || session?.problem_id || '未记录题目';
}

function sessionSituation(session) {
  if (!session) return '暂无会话概况';
  if (session.same_point_loop_detected) {
    return `学生在同一个地方反复卡住，建议先看教师诊断。`;
  }
  const count = evidenceCount(session.evidence_flags);
  if (count >= 3) return '已有一些理解证据，适合确认能否独立复述关键步骤。';
  if (count > 0) return '出现少量理解证据，需要老师帮他把关键关系说完整。';
  return '暂时缺少理解证据，不建议直接让学生复盘整题。';
}

function messageClass(role) {
  if (role === 'student') return 'border-sky-100 bg-sky-50/80 text-slate-900';
  if (role === 'ai_coach') return 'border-slate-200 bg-white text-slate-800';
  return 'border-slate-100 bg-slate-50 text-slate-500';
}

function roleLabel(role) {
  if (role === 'student') return '学生';
  if (role === 'ai_coach') return 'AI 教练';
  if (role === 'student_quiz_answer') return '学生验证回答';
  if (role === 'ai_quiz_question') return 'AI 验证题';
  if (role === 'ai_quiz_feedback') return 'AI 验证反馈';
  return '系统';
}

function codeParts(content) {
  const text = String(content || '');
  const parts = [];
  const pattern = /```([a-zA-Z0-9+#-]*)?\s*\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;
  while ((match = pattern.exec(text))) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: text.slice(lastIndex, match.index) });
    }
    parts.push({ type: 'code', lang: match[1] || 'code', value: match[2] || '' });
    lastIndex = pattern.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push({ type: 'text', value: text.slice(lastIndex) });
  }
  return parts.length ? parts : [{ type: 'text', value: text }];
}

function judgeAction(event) {
  return event?.[`judge_${'action_subtype'}`];
}

function judgeIntent(event) {
  return event?.judge_primary_intent;
}

function judgeForMessage(message) {
  const events = detail.value?.judge_events || [];
  return events.find((event) => Number(event.conversation_message_id) === Number(message.id))
    || events.find((event) => event.user_input && message.content && String(message.content).includes(event.user_input.slice(0, 20)));
}

const selectedStudent = computed(() =>
  students.value.find((row) => row.student_id === selectedStudentId.value) || null,
);

const selectedSession = computed(() =>
  sessions.value.find((row) => row.session_id === selectedSessionId.value) || null,
);

const selectedSummary = computed(() => detail.value?.summary || null);
const analysisPayload = computed(() => sessionAnalysis.value?.analysis || sessionAnalysis.value?.analysis_json || null);
const visibleMessages = computed(() =>
  (detail.value?.messages || []).filter((message) => message.role !== 'system'),
);
const systemMessages = computed(() =>
  (detail.value?.messages || []).filter((message) => message.role === 'system'),
);

const teacherDiagnosis = computed(() => {
  const summary = selectedSummary.value;
  if (!summary) {
    return {
      status: '请选择一段会话',
      issue: '暂时没有可判断的学习证据。',
      action: '先从左侧选择学生，再选择一段对话。',
    };
  }
  const count = evidenceCount(summary.evidence_flags);
  const latestAction = actionText(summary.latest_tutor_action);
  if (summary.same_point_loop_detected) {
    return {
      status: '学生在同一个地方反复卡住。',
      issue: `卡住类型：${summary.same_gap_loop_type || '需要老师看上下文确认'}。`,
      action: '先让学生说出他卡住的那一步，再给一个更小的例子让他模仿。',
    };
  }
  if (count >= 3) {
    return {
      status: '学生已经留下较多理解证据。',
      issue: `最近 AI 动作是：${latestAction}。`,
      action: '让学生独立复述关键步骤，或布置一道同类低难度题确认迁移。',
    };
  }
  if (count > 0) {
    return {
      status: '学生有一点进展，但证据还不完整。',
      issue: `目前只有 ${count} 类理解证据，容易出现“感觉懂了但说不清”。`,
      action: '围绕一个关键关系追问，让学生用自己的话补全，而不是马上讲完整题解。',
    };
  }
  return {
    status: '学生暂时没有留下足够理解证据。',
    issue: '现在不适合要求学生做整题复盘，复盘会变成空话。',
    action: '先在 AIChat 或课堂里给一个更小的 worked example，帮助学生建立方法雏形。',
  };
});

async function loadStudents() {
  loadingStudents.value = true;
  error.value = '';
  try {
    const [payload, healthPayload] = await Promise.all([
      getTeacherAIChatStudents(auth.token),
      getTeacherAIChatSessionAnalysisHealth(auth.token, { days: 7 }),
    ]);
    students.value = payload.students || [];
    analysisHealth.value = healthPayload;
    if (!selectedStudentId.value && students.value.length) {
      await selectStudent(students.value[0].student_id);
    }
  } catch (err) {
    error.value = err.message || '加载学生学习记录失败';
  } finally {
    loadingStudents.value = false;
  }
}

async function selectStudent(studentId) {
  selectedStudentId.value = studentId;
  selectedSessionId.value = '';
  detail.value = null;
  sessionAnalysis.value = null;
  stopAnalysisPolling();
  loadingSessions.value = true;
  error.value = '';
  try {
    const payload = await getTeacherAIChatSessions(auth.token, studentId);
    sessions.value = payload.sessions || [];
    if (sessions.value.length) {
      await selectSession(sessions.value[0].session_id);
    }
  } catch (err) {
    error.value = err.message || '加载学生会话失败';
  } finally {
    loadingSessions.value = false;
  }
}

async function selectSession(sessionId) {
  selectedSessionId.value = sessionId;
  showConversation.value = false;
  showSystemEvidence.value = false;
  sessionAnalysis.value = null;
  stopAnalysisPolling();
  loadingDetail.value = true;
  error.value = '';
  try {
    detail.value = await getTeacherAIChatSessionDetail(auth.token, sessionId);
    sessionAnalysis.value = detail.value?.session_analysis || null;
    await loadSessionAnalysis(sessionId);
  } catch (err) {
    error.value = err.message || '加载会话详情失败';
  } finally {
    loadingDetail.value = false;
  }
}

function stopAnalysisPolling() {
  if (analysisPollingTimer.value) {
    window.clearTimeout(analysisPollingTimer.value);
    analysisPollingTimer.value = null;
  }
}

async function loadSessionAnalysis(sessionId, { silent = false } = {}) {
  if (!sessionId) return;
  try {
    const payload = await getTeacherAIChatSessionAnalysis(auth.token, sessionId);
    if (selectedSessionId.value !== sessionId) return;
    sessionAnalysis.value = payload;
    stopAnalysisPolling();
    if (payload?.status === 'processing') {
      analysisPollingTimer.value = window.setTimeout(() => {
        loadSessionAnalysis(sessionId, { silent: true });
      }, 2000);
    }
  } catch (err) {
    if (!silent) {
      error.value = err.message || '加载会话总结失败';
    }
  }
}

async function retrySessionAnalysis() {
  const sessionId = selectedSessionId.value;
  if (!sessionId) return;
  stopAnalysisPolling();
  sessionAnalysis.value = { status: 'processing', analysis: null };
  try {
    const payload = await retryTeacherAIChatSessionAnalysis(auth.token, sessionId);
    if (selectedSessionId.value !== sessionId) return;
    sessionAnalysis.value = payload;
    if (payload?.status === 'processing') {
      analysisPollingTimer.value = window.setTimeout(() => {
        loadSessionAnalysis(sessionId, { silent: true });
      }, 2000);
    }
  } catch (err) {
    error.value = err.message || '重新生成会话总结失败';
  }
}

onMounted(loadStudents);
onUnmounted(stopAnalysisPolling);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="section-eyebrow text-operator-700">AI 对话学习记录</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">先看谁，再看怎么帮</h3>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            先看需要关注的学生，再看会话概况，最后按需展开原始对话和系统证据。
          </p>
        </div>
        <button class="button-secondary" type="button" @click="loadStudents">刷新</button>
      </div>
      <div v-if="analysisHealth" class="mt-4 grid gap-3 md:grid-cols-4">
        <div class="rounded-[8px] border border-slate-100 bg-white px-4 py-3">
          <p class="text-xs font-semibold text-slate-400">总结状态</p>
          <p class="mt-1 text-lg font-bold text-slate-900">{{ analysisHealth.total || 0 }}</p>
        </div>
        <div class="rounded-[8px] border border-emerald-100 bg-emerald-50 px-4 py-3">
          <p class="text-xs font-semibold text-emerald-700">已生成</p>
          <p class="mt-1 text-lg font-bold text-emerald-900">{{ analysisHealth.completed_count || 0 }}</p>
        </div>
        <div class="rounded-[8px] border border-amber-100 bg-amber-50 px-4 py-3">
          <p class="text-xs font-semibold text-amber-700">生成中</p>
          <p class="mt-1 text-lg font-bold text-amber-900">{{ analysisHealth.processing_count || 0 }}</p>
        </div>
        <div class="rounded-[8px] border border-rose-100 bg-rose-50 px-4 py-3">
          <p class="text-xs font-semibold text-rose-700">失败</p>
          <p class="mt-1 text-lg font-bold text-rose-900">{{ analysisHealth.failed_count || 0 }}</p>
        </div>
      </div>
      <p v-if="error" class="mt-4 rounded-[18px] bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{{ error }}</p>
    </section>

    <section class="grid gap-4 xl:grid-cols-[300px_420px_minmax(0,1fr)]">
      <aside class="panel min-h-[560px]">
        <div class="flex items-center justify-between">
          <div>
            <p class="section-eyebrow text-operator-700">关注队列</p>
            <h4 class="mt-1 font-display text-xl font-bold text-slate-900">先看这些学生</h4>
          </div>
          <span class="tag-pill bg-slate-100 text-slate-600">{{ students.length }} 人</span>
        </div>
        <p v-if="loadingStudents" class="mt-4 text-sm text-slate-500">正在加载学生...</p>
        <p v-else-if="!students.length" class="mt-4 rounded-[16px] border border-dashed border-slate-200 p-4 text-sm text-slate-500">
          暂无 AI 对话学习记录。
        </p>
        <div v-else class="mt-4 space-y-3">
          <button
            v-for="row in students"
            :key="row.student_id"
            type="button"
            :class="[
              'w-full rounded-[8px] border p-4 text-left transition',
              selectedStudentId === row.student_id ? 'border-operator-300 bg-operator-50' : 'border-slate-200 bg-white hover:border-operator-200',
            ]"
            @click="selectStudent(row.student_id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-semibold text-slate-900">{{ studentName(row) }}</p>
                <p class="mt-1 text-xs text-slate-500">账号：{{ row.student_id }}</p>
              </div>
              <span class="rounded-full bg-white px-2 py-1 text-xs font-semibold text-slate-500">{{ row.total_sessions }} 次</span>
            </div>
            <p class="mt-3 text-sm leading-6 text-slate-600">{{ studentAttentionReason(row) }}</p>
            <p class="mt-2 text-xs text-slate-400">最近：{{ formatTime(row.last_session_at) }}</p>
          </button>
        </div>
      </aside>

      <aside class="panel min-h-[560px]">
        <div class="flex items-center justify-between">
          <div>
            <p class="section-eyebrow text-emerald-700">会话概况</p>
            <h4 class="mt-1 font-display text-xl font-bold text-slate-900">这次发生了什么</h4>
          </div>
          <span class="tag-pill bg-slate-100 text-slate-600">{{ sessions.length }} 次</span>
        </div>
        <p v-if="selectedStudent" class="mt-2 text-xs text-slate-500">
          当前学生：{{ studentName(selectedStudent) }}，账号：{{ selectedStudent.student_id }}
        </p>
        <p v-if="loadingSessions" class="mt-4 text-sm text-slate-500">正在加载会话...</p>
        <p v-else-if="selectedStudentId && !sessions.length" class="mt-4 rounded-[16px] border border-dashed border-slate-200 p-4 text-sm text-slate-500">
          这个学生暂时没有 AI 对话记录。
        </p>
        <div v-else class="mt-4 space-y-3">
          <button
            v-for="session in sessions"
            :key="session.session_id"
            type="button"
            :class="[
              'w-full rounded-[8px] border p-4 text-left transition',
              selectedSessionId === session.session_id ? 'border-emerald-300 bg-emerald-50' : 'border-slate-200 bg-white hover:border-emerald-200',
            ]"
            @click="selectSession(session.session_id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-semibold text-slate-900">{{ sessionTitle(session) }}</p>
                <p class="mt-1 text-xs text-slate-400">{{ formatTime(session.started_at || session.updated_at) }}</p>
              </div>
              <span class="rounded-full bg-white px-2 py-1 text-xs font-semibold text-slate-500">{{ session.total_turns || 0 }} 轮</span>
            </div>
            <p class="mt-3 text-sm leading-6 text-slate-600">{{ sessionSituation(session) }}</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span class="rounded-full bg-white px-2 py-1 text-xs font-semibold text-emerald-700">
                理解证据 {{ evidenceCount(session.evidence_flags) }}/6
              </span>
              <span v-if="session.same_point_loop_detected" class="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800">
                同点打转
              </span>
              <span class="rounded-full bg-white px-2 py-1 text-xs font-semibold text-slate-500">
                {{ actionText(session.last_ai_action) }}
              </span>
            </div>
          </button>
        </div>
      </aside>

      <main class="panel min-h-[560px]">
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="section-eyebrow text-slate-500">教师诊断</p>
            <h4 class="mt-1 font-display text-xl font-bold text-slate-900">老师可以怎么帮</h4>
          </div>
          <span v-if="selectedSession" class="tag-pill bg-slate-100 text-slate-600">{{ selectedSession.problem_id || '未记录题目' }}</span>
        </div>
        <p v-if="loadingDetail" class="mt-4 text-sm text-slate-500">正在整理诊断...</p>
        <p v-else-if="!selectedSummary" class="mt-4 rounded-[16px] border border-dashed border-slate-200 p-4 text-sm text-slate-500">
          请选择一个会话查看教师诊断。
        </p>
        <div v-else class="mt-4 space-y-4">
          <section class="rounded-[8px] border border-operator-100 bg-operator-50/70 p-4">
            <p class="text-sm font-semibold text-slate-900">
              {{ selectedSummary.student_real_name || selectedSummary.student_username || selectedSummary.student_id }}
              <span class="text-slate-400">|</span>
              账号：{{ selectedSummary.student_id }}
              <span class="text-slate-400">|</span>
              题目：{{ selectedSummary.problem_id || '暂无' }}
              <span class="text-slate-400">|</span>
              总轮数：{{ selectedSummary.message_count || 0 }}
            </p>
            <div
              v-if="sessionAnalysis"
              class="mt-4 rounded-[8px] border bg-white p-3"
              :class="sessionAnalysis.status === 'completed' ? 'border-emerald-100' : sessionAnalysis.status === 'failed' ? 'border-rose-100' : 'border-amber-100'"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="text-xs font-semibold tracking-[0.12em] text-slate-400">会话总结分析器</p>
                <div class="flex flex-wrap items-center gap-2">
                  <button
                    v-if="sessionAnalysis.status !== 'processing'"
                    class="rounded-full bg-white px-2 py-1 text-xs font-semibold text-slate-600"
                    type="button"
                    @click="retrySessionAnalysis"
                  >
                    重新生成会话总结
                  </button>
                  <span
                    class="rounded-full px-2 py-1 text-xs font-semibold"
                    :class="sessionAnalysis.status === 'completed' ? 'bg-emerald-100 text-emerald-700' : sessionAnalysis.status === 'failed' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800'"
                  >
                    {{ sessionAnalysis.status === 'completed' ? '已生成' : sessionAnalysis.status === 'failed' ? '生成失败' : '生成中' }}
                  </span>
                </div>
              </div>
              <p v-if="sessionAnalysis.status === 'processing'" class="mt-3 text-sm leading-6 text-amber-800">
                正在根据本次完整对话和后台标签生成教师总结，完成后这里会自动刷新。
              </p>
              <p v-else-if="sessionAnalysis.status === 'failed'" class="mt-3 text-sm leading-6 text-rose-700">
                暂时没生成成功：{{ sessionAnalysis.failure_reason || '未知原因' }}。你可以稍后刷新重试。
              </p>
              <div v-else-if="analysisPayload" class="mt-3 grid gap-3 lg:grid-cols-3">
                <div class="rounded-[8px] bg-emerald-50 p-3">
                  <p class="text-xs font-semibold text-emerald-700">主要问题</p>
                  <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ analysisPayload.main_issue || sessionAnalysis.main_issue || '暂无' }}</p>
                  <p v-if="analysisPayload.issue_detail" class="mt-2 text-xs leading-5 text-slate-500">{{ analysisPayload.issue_detail }}</p>
                </div>
                <div class="rounded-[8px] bg-sky-50 p-3">
                  <p class="text-xs font-semibold text-sky-700">老师下一步</p>
                  <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ analysisPayload.teacher_next_action || sessionAnalysis.teacher_next_action || '暂无建议' }}</p>
                </div>
                <div class="rounded-[8px] bg-slate-50 p-3">
                  <p class="text-xs font-semibold text-slate-500">练习方向</p>
                  <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ analysisPayload.recommended_practice_type || '暂无推荐' }}</p>
                  <p class="mt-2 text-xs text-slate-500">置信度：{{ analysisPayload.confidence ?? '暂无' }}</p>
                </div>
              </div>
            </div>
            <div class="mt-4 grid gap-3 lg:grid-cols-3">
              <div class="rounded-[8px] bg-white p-3">
                <p class="text-xs font-semibold text-slate-400">学生当前状态</p>
                <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ teacherDiagnosis.status }}</p>
              </div>
              <div class="rounded-[8px] bg-white p-3">
                <p class="text-xs font-semibold text-slate-400">这次主要问题</p>
                <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ teacherDiagnosis.issue }}</p>
              </div>
              <div class="rounded-[8px] bg-white p-3">
                <p class="text-xs font-semibold text-slate-400">建议下一步</p>
                <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ teacherDiagnosis.action }}</p>
              </div>
            </div>
          </section>

          <section class="rounded-[8px] border border-slate-200 bg-white p-4">
            <div class="flex items-center justify-between">
              <p class="font-semibold text-slate-900">理解证据</p>
              <span class="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-500">
                {{ evidenceCount(selectedSummary.evidence_flags) }}/6
              </span>
            </div>
            <div class="mt-3 grid gap-2 md:grid-cols-2">
              <p
                v-for="[key, label] in evidenceLabels"
                :key="key"
                :class="['text-sm font-semibold', evidenceFlag(selectedSummary.evidence_flags, key) ? 'text-emerald-700' : 'text-slate-400']"
              >
                {{ evidenceFlag(selectedSummary.evidence_flags, key) ? '[✓]' : '[✗]' }} {{ label }}
              </p>
            </div>
            <p v-if="selectedSummary.same_point_loop_detected" class="mt-3 rounded-[8px] bg-amber-100 px-3 py-2 text-sm font-semibold text-amber-800">
              [!] 同点打转：{{ selectedSummary.same_gap_loop_type || '需要老师看看上下文' }}
            </p>
            <p class="mt-3 text-sm text-slate-600">最近 AI 动作：{{ actionText(selectedSummary.latest_tutor_action) }}</p>
          </section>

          <section class="rounded-[8px] border border-slate-200 bg-white">
            <button
              type="button"
              class="flex w-full items-center justify-between px-4 py-3 text-left font-semibold text-slate-900"
              @click="showConversation = !showConversation"
            >
              <span>{{ showConversation ? '收起完整对话' : '展开完整对话' }}</span>
              <span class="text-sm text-slate-400">{{ visibleMessages.length }} 条</span>
            </button>
            <div v-if="showConversation" class="border-t border-slate-100 p-4">
              <article
                v-for="message in visibleMessages"
                :key="message.id"
                :class="['mb-4 flex', message.role === 'student' ? 'justify-start' : 'justify-end']"
              >
                <div :class="['max-w-[82%] rounded-[8px] border p-4 shadow-sm', messageClass(message.role)]">
                  <div class="mb-2 flex items-center justify-between gap-3">
                    <p class="text-xs font-semibold tracking-[0.12em] text-slate-400">{{ roleLabel(message.role) }}</p>
                    <p class="text-xs text-slate-400">{{ formatTime(message.created_at) }}</p>
                  </div>
                  <template v-for="(part, index) in codeParts(message.content)" :key="`${message.id}-${index}`">
                    <p v-if="part.type === 'text'" class="whitespace-pre-wrap break-words text-sm leading-7">{{ part.value }}</p>
                    <pre v-else class="mt-3 overflow-auto rounded-[8px] bg-slate-950 p-3 text-xs leading-6 text-emerald-100"><code>{{ part.value }}</code></pre>
                  </template>
                </div>
              </article>
            </div>
          </section>

          <section class="rounded-[8px] border border-slate-200 bg-white">
            <button
              type="button"
              class="flex w-full items-center justify-between px-4 py-3 text-left font-semibold text-slate-900"
              @click="showSystemEvidence = !showSystemEvidence"
            >
              <span>{{ showSystemEvidence ? '收起系统证据' : '展开系统证据' }}</span>
              <span class="text-sm text-slate-400">{{ (detail?.judge_events || []).length }} 条判断</span>
            </button>
            <div v-if="showSystemEvidence" class="space-y-3 border-t border-slate-100 p-4">
              <div
                v-for="message in visibleMessages.filter((row) => row.role === 'student')"
                :key="`judge-${message.id}`"
                class="rounded-[8px] bg-slate-50 p-3 text-xs leading-5 text-slate-600"
              >
                <template v-if="judgeForMessage(message)">
                  <p class="font-semibold text-slate-800">系统判断</p>
                  <p>主要意图：{{ judgeIntent(judgeForMessage(message)) || '暂无' }}</p>
                  <p>系统判断的引导方式：{{ actionText(judgeAction(judgeForMessage(message))) }}</p>
                  <p>判断置信度：{{ judgeForMessage(message).judge_confidence ?? '暂无' }}</p>
                  <p>动作是否一致：{{ judgeForMessage(message).agreement_action_family ? '是' : '否' }}</p>
                </template>
                <p v-else>暂无对应系统判断记录</p>
              </div>
              <div v-if="systemMessages.length" class="rounded-[8px] bg-slate-50 p-3 text-xs leading-5 text-slate-500">
                <p class="font-semibold text-slate-700">系统消息</p>
                <p v-for="message in systemMessages" :key="`system-${message.id}`" class="mt-2 whitespace-pre-wrap break-words">
                  {{ message.content }}
                </p>
              </div>
            </div>
          </section>
        </div>
      </main>
    </section>
  </div>
</template>
