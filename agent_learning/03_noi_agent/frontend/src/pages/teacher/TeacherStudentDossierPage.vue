<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

import {
  createTeacherStudentNote,
  getTeacherAIChatSessionAnalysis,
  getTeacherAIChatSessionDetail,
  getTeacherStudentDossier,
  retryTeacherAIChatSessionAnalysis,
} from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const tabs = ['概况', '做题记录', '理解与复盘', 'AIChat 证据', '老师记录'];

const route = useRoute();
const auth = useAuthStore();
const activeTab = ref('概况');
const loading = ref(false);
const saving = ref(false);
const error = ref('');
const dossier = ref(null);
const noteText = ref('');
const noteStatus = ref('continue_followup');
const nextFollowupAt = ref('');
const interventionType = ref('mini_lesson');
const targetIssue = ref('');
const expandedSessionId = ref('');
const loadingSessionId = ref('');
const sessionDetailsById = ref({});
const sessionAnalysisById = ref({});
const analysisTimersById = ref({});

const studentId = computed(() => String(route.params.studentId || ''));
const dailySeries = computed(() => dossier.value?.daily_series || []);
const summary = computed(() => dossier.value?.summary || {});
const issues = computed(() => dossier.value?.issue_summary || []);
const completions = computed(() => dossier.value?.problem_completions || []);
const reviews = computed(() => dossier.value?.reviews || []);
const aichatSessions = computed(() => dossier.value?.aichat_sessions || []);
const notes = computed(() => dossier.value?.teacher_notes || []);
const periodComparison = computed(() => dossier.value?.period_comparison || {});
const practiceRecommendations = computed(() => dossier.value?.next_practice_recommendations || []);

const maxCompleted = computed(() => Math.max(1, ...dailySeries.value.map((row) => Number(row.completed_count) || 0)));
const methodShareRows = computed(() => {
  const rows = [
    { key: 'self_solved', label: '自己做出', count: Number(summary.value.self_solved_count) || 0, color: 'bg-emerald-500' },
    { key: 'small_hint', label: '少量提示', count: Number(summary.value.small_hint_count) || 0, color: 'bg-cyan-500' },
    { key: 'classroom_taught', label: '课堂讲后', count: Number(summary.value.classroom_taught_count) || 0, color: 'bg-blue-500' },
    { key: 'aichat_assisted', label: 'AIChat 后', count: Number(summary.value.aichat_assisted_count) || 0, color: 'bg-amber-500' },
    { key: 'editorial_completed', label: '看题解后', count: Number(summary.value.editorial_completed_count) || 0, color: 'bg-slate-400' },
  ];
  const knownCount = rows.reduce((total, row) => total + row.count, 0);
  const unknownCount = Math.max(0, (Number(summary.value.completed_count) || 0) - knownCount);
  if (unknownCount) {
    rows.push({ key: 'unknown', label: '未注明', count: unknownCount, color: 'bg-slate-300' });
  }
  const total = Math.max(1, rows.reduce((sum, row) => sum + row.count, 0));
  return rows.map((row) => ({
    ...row,
    percent: Math.round((row.count / total) * 100),
  }));
});
const linePoints = computed(() => {
  if (!dailySeries.value.length) return '';
  const width = 260;
  const height = 80;
  const step = dailySeries.value.length <= 1 ? width : width / (dailySeries.value.length - 1);
  return dailySeries.value
    .map((row, index) => {
      const score = Math.max(0, Math.min(4, Number(row.independence_score) || 0));
      const x = Math.round(index * step);
      const y = Math.round(height - (score / 4) * height);
      return `${x},${y}`;
    })
    .join(' ');
});

function formatDate(value) {
  return String(value || '').slice(0, 16).replace('T', ' ');
}

function methodLabel(value) {
  const map = {
    self_solved: '自己做出',
    small_hint: '少量提示',
    classroom_taught: '课堂讲后',
    aichat_assisted: 'AIChat 后',
    editorial_completed: '看题解后',
    unsure: '不确定',
  };
  return map[value] || value || '未记录';
}

function resultLabel(value) {
  const map = {
    accepted: 'AC',
    sample_passed: '样例通过',
    unsure: '不确定',
  };
  return map[value] || value || '未记录';
}

function bridgePathLabel(value) {
  const map = {
    main_clear: 'main_clear',
    remedy_clear: 'remedy_clear',
    bottom_out_clear: 'bottom_out',
    knowledge_bailout: 'bailout',
  };
  return map[value] || value || '未记录';
}

function signedNumber(value, digits = 1) {
  const number = Number(value) || 0;
  const fixed = number.toFixed(digits);
  return number > 0 ? `+${fixed}` : fixed;
}

function interventionTypeLabel(value) {
  const map = {
    mini_lesson: '讲一个小例子',
    similar_problem: '布置同类题',
    oral_check: '口头追问',
    difficulty_downshift: '降低难度',
    emotional_support: '情绪鼓励',
    classroom_observation: '课堂观察',
  };
  return map[value] || value || '未注明';
}

function roleLabel(role) {
  const map = {
    student: '学生',
    ai_coach: 'AI 教练',
    student_quiz_answer: '学生验证回答',
    ai_quiz_question: 'AI 验证题',
    ai_quiz_feedback: 'AI 验证反馈',
    system: '系统',
  };
  return map[role] || '系统';
}

function messageClass(role) {
  if (role === 'student' || role === 'student_quiz_answer') return 'border-sky-100 bg-sky-50/80 text-slate-900';
  if (role === 'ai_coach' || role === 'ai_quiz_question' || role === 'ai_quiz_feedback') return 'border-slate-200 bg-white text-slate-800';
  return 'border-slate-100 bg-slate-50 text-slate-500';
}

function sessionMessages(sessionId) {
  return (sessionDetailsById.value[sessionId]?.messages || []).filter((message) => message.role !== 'system');
}

function sessionAnalysis(sessionId) {
  return sessionAnalysisById.value[sessionId] || sessionDetailsById.value[sessionId]?.session_analysis || null;
}

function sessionAnalysisPayload(sessionId) {
  const analysis = sessionAnalysis(sessionId);
  return analysis?.analysis || analysis?.analysis_json || null;
}

function judgeForMessage(sessionId, message) {
  const events = sessionDetailsById.value[sessionId]?.judge_events || [];
  return events.find((event) => Number(event.conversation_message_id) === Number(message.id))
    || events.find((event) => event.user_input && message.content && String(message.content).includes(String(event.user_input).slice(0, 20)));
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

async function loadDossier() {
  if (!studentId.value) return;
  loading.value = true;
  error.value = '';
  try {
    dossier.value = await getTeacherStudentDossier(auth.token, studentId.value, { days: 15 });
  } catch (err) {
    error.value = err.message || '加载学生详情失败';
  } finally {
    loading.value = false;
  }
}

function clearAnalysisTimer(sessionId) {
  const timer = analysisTimersById.value[sessionId];
  if (timer) {
    window.clearTimeout(timer);
    const next = { ...analysisTimersById.value };
    delete next[sessionId];
    analysisTimersById.value = next;
  }
}

function clearAllAnalysisTimers() {
  for (const sessionId of Object.keys(analysisTimersById.value)) {
    window.clearTimeout(analysisTimersById.value[sessionId]);
  }
  analysisTimersById.value = {};
}

async function loadSessionAnalysis(sessionId, { silent = false } = {}) {
  if (!sessionId) return;
  try {
    const payload = await getTeacherAIChatSessionAnalysis(auth.token, sessionId);
    sessionAnalysisById.value = {
      ...sessionAnalysisById.value,
      [sessionId]: payload,
    };
    clearAnalysisTimer(sessionId);
    if (payload?.status === 'processing') {
      analysisTimersById.value = {
        ...analysisTimersById.value,
        [sessionId]: window.setTimeout(() => {
          loadSessionAnalysis(sessionId, { silent: true });
        }, 2000),
      };
    }
  } catch (err) {
    if (!silent) {
      error.value = err.message || '加载会话总结失败';
    }
  }
}

async function retrySessionAnalysis(sessionId) {
  if (!sessionId) return;
  clearAnalysisTimer(sessionId);
  sessionAnalysisById.value = {
    ...sessionAnalysisById.value,
    [sessionId]: { status: 'processing', analysis: null },
  };
  try {
    const payload = await retryTeacherAIChatSessionAnalysis(auth.token, sessionId);
    sessionAnalysisById.value = {
      ...sessionAnalysisById.value,
      [sessionId]: payload,
    };
    if (payload?.status === 'processing') {
      analysisTimersById.value = {
        ...analysisTimersById.value,
        [sessionId]: window.setTimeout(() => {
          loadSessionAnalysis(sessionId, { silent: true });
        }, 2000),
      };
    }
  } catch (err) {
    error.value = err.message || '重新生成会话总结失败';
  }
}

async function toggleSessionDetail(item) {
  const sessionId = item?.session_id;
  if (!sessionId) return;
  if (expandedSessionId.value === sessionId) {
    expandedSessionId.value = '';
    return;
  }
  expandedSessionId.value = sessionId;
  if (sessionDetailsById.value[sessionId]) return;
  loadingSessionId.value = sessionId;
  error.value = '';
  try {
    const detail = await getTeacherAIChatSessionDetail(auth.token, sessionId);
    sessionDetailsById.value = {
      ...sessionDetailsById.value,
      [sessionId]: detail,
    };
  } catch (err) {
    error.value = err.message || '加载完整对话失败';
  } finally {
    loadingSessionId.value = '';
  }
  await loadSessionAnalysis(sessionId);
}

async function saveNote() {
  const text = noteText.value.trim();
  if (!text || saving.value) return;
  saving.value = true;
  error.value = '';
  try {
    await createTeacherStudentNote(auth.token, {
      student_id: studentId.value,
      note: text,
      status: noteStatus.value,
      next_followup_at: nextFollowupAt.value,
      intervention_type: interventionType.value,
      target_issue: targetIssue.value,
    });
    noteText.value = '';
    nextFollowupAt.value = '';
    targetIssue.value = '';
    await loadDossier();
  } catch (err) {
    error.value = err.message || '保存老师记录失败';
  } finally {
    saving.value = false;
  }
}

onMounted(loadDossier);
onUnmounted(clearAllAnalysisTimers);
watch(studentId, loadDossier);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">学生详情卡</p>
          <h2 class="mt-2 font-display text-3xl font-bold text-slate-900">
            {{ dossier?.student?.display_name || studentId }}
          </h2>
          <p class="mt-2 text-sm text-slate-500">账号：{{ dossier?.student?.username || studentId }} · 最近 {{ dossier?.window_days || 15 }} 天</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <RouterLink class="button-secondary" to="/app/teacher/students">返回学生列表</RouterLink>
          <button class="button-secondary" type="button" @click="loadDossier">刷新</button>
        </div>
      </div>
      <p v-if="loading" class="mt-4 text-sm text-slate-500">正在加载学生详情...</p>
      <p v-else-if="error" class="mt-4 rounded-[8px] bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
    </section>

    <section v-if="dossier" class="panel">
      <div class="flex flex-wrap gap-2 border-b border-slate-100 pb-4">
        <button
          v-for="tab in tabs"
          :key="tab"
          type="button"
          class="rounded-[8px] px-4 py-2 text-sm font-semibold transition"
          :class="activeTab === tab ? 'bg-cyan-600 text-white shadow-sm' : 'bg-slate-50 text-slate-500 hover:bg-cyan-50 hover:text-cyan-700'"
          @click="activeTab = tab"
        >
          {{ tab }}
        </button>
      </div>

      <div v-if="activeTab === '概况'" class="mt-6 space-y-6">
        <div class="grid gap-4 md:grid-cols-4">
          <article class="metric-tile">
            <p class="text-sm text-slate-400">最近 15 天完成题数</p>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ summary.completed_count || 0 }}</p>
          </article>
          <article class="metric-tile">
            <p class="text-sm text-slate-400">自己做出</p>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ summary.self_solved_count || 0 }}</p>
          </article>
          <article class="metric-tile">
            <p class="text-sm text-slate-400">AIChat 后完成</p>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ summary.aichat_assisted_count || 0 }}</p>
          </article>
          <article class="metric-tile">
            <p class="text-sm text-slate-400">复盘验证通过</p>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ summary.review_passed_count || 0 }}</p>
          </article>
        </div>

        <article class="bento-card border-emerald-100 bg-emerald-50/40">
          <div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
            <div>
              <p class="text-sm font-semibold text-emerald-700">与上个 15 天相比</p>
              <p class="mt-1 text-xs text-slate-500">只看变化方向，不把它当成因果结论。</p>
            </div>
            <span class="tag-pill bg-white text-emerald-700">{{ periodComparison.independence_trend_label || '暂无变化数据' }}</span>
          </div>
          <div class="mt-4 grid gap-3 md:grid-cols-3">
            <div class="rounded-[8px] border border-white/80 bg-white/85 p-4">
              <p class="text-xs font-semibold text-slate-400">完成题数变化</p>
              <p class="mt-2 text-xl font-semibold text-slate-900">{{ signedNumber(periodComparison.completed_delta, 0) }}</p>
            </div>
            <div class="rounded-[8px] border border-white/80 bg-white/85 p-4">
              <p class="text-xs font-semibold text-slate-400">独立程度变化</p>
              <p class="mt-2 text-xl font-semibold text-slate-900">{{ signedNumber(periodComparison.independence_delta) }}</p>
            </div>
            <div class="rounded-[8px] border border-white/80 bg-white/85 p-4">
              <p class="text-xs font-semibold text-slate-400">完成质量变化</p>
              <p class="mt-2 text-xl font-semibold text-slate-900">{{ signedNumber(periodComparison.quality_delta) }}</p>
            </div>
          </div>
        </article>

        <div class="grid gap-6 xl:grid-cols-2">
          <article class="bento-card border-cyan-100 bg-white">
            <p class="text-sm font-semibold text-cyan-700">最近 15 天完成题数</p>
            <div class="mt-5 flex h-32 items-end gap-2">
              <div v-for="row in dailySeries" :key="row.date" class="flex flex-1 flex-col items-center gap-2">
                <div class="w-full rounded-t-[6px] bg-cyan-500" :style="{ height: `${Math.max(4, (Number(row.completed_count) || 0) / maxCompleted * 96)}px` }" />
                <span class="text-[10px] text-slate-400">{{ row.date.slice(5) }}</span>
              </div>
            </div>
          </article>
          <article class="bento-card border-emerald-100 bg-white">
            <p class="text-sm font-semibold text-emerald-700">独立程度趋势</p>
            <div class="mt-5 grid grid-cols-[88px_1fr] gap-3">
              <div class="flex h-32 flex-col justify-between text-[10px] leading-4 text-slate-400">
                <span>基本能独立完成</span>
                <span>少量提示能完成</span>
                <span>需要较多帮助</span>
                <span>缺少完成证据</span>
              </div>
              <svg class="h-32 w-full overflow-visible" viewBox="0 0 260 100" preserveAspectRatio="none">
                <line x1="0" y1="0" x2="260" y2="0" stroke="#f1f5f9" stroke-width="1" />
                <line x1="0" y1="27" x2="260" y2="27" stroke="#f1f5f9" stroke-width="1" />
                <line x1="0" y1="53" x2="260" y2="53" stroke="#f1f5f9" stroke-width="1" />
                <line x1="0" y1="80" x2="260" y2="80" stroke="#e2e8f0" stroke-width="1" />
                <polyline :points="linePoints" fill="none" stroke="#059669" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </div>
            <p class="mt-2 text-xs text-slate-500">页面不显示内部分数，只看趋势：越高说明越接近独立完成。</p>
          </article>
        </div>

        <div class="grid gap-6 xl:grid-cols-3">
          <article class="bento-card border-cyan-100 bg-white xl:col-span-3">
            <div class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <p class="text-sm font-semibold text-cyan-700">完成方式占比</p>
                <p class="mt-1 text-xs text-slate-500">看学生最近是自己推进，还是主要依赖 AIChat、课堂讲解或题解。</p>
              </div>
              <p class="text-xs text-slate-400">共 {{ summary.completed_count || 0 }} 条做题记录</p>
            </div>
            <div class="mt-4 flex h-4 overflow-hidden rounded-[8px] bg-slate-100">
              <div
                v-for="row in methodShareRows"
                :key="row.key"
                class="h-full"
                :class="row.color"
                :style="{ width: `${row.percent}%` }"
                :title="`${row.label}: ${row.count}`"
              />
            </div>
            <div class="mt-3 grid gap-2 md:grid-cols-3 xl:grid-cols-6">
              <div v-for="row in methodShareRows" :key="`${row.key}-legend`" class="flex items-center gap-2 text-xs text-slate-500">
                <span class="h-2.5 w-2.5 rounded-full" :class="row.color" />
                <span>{{ row.label }} · {{ row.count }}</span>
              </div>
            </div>
          </article>
          <article class="bento-card border-slate-200 bg-white">
            <p class="text-sm font-semibold text-slate-700">完成质量概览</p>
            <p class="mt-2 text-sm leading-6 text-slate-500">AC、样例通过和复盘验证共同构成质量证据。</p>
            <p class="mt-4 text-lg font-semibold text-slate-900">AC：{{ summary.accepted_count || 0 }} · 复盘通过：{{ summary.review_passed_count || 0 }}</p>
          </article>
          <article class="bento-card border-amber-100 bg-amber-50/50 xl:col-span-2">
            <p class="text-sm font-semibold text-amber-700">最近主要问题</p>
            <div v-if="issues.length" class="mt-3 flex flex-wrap gap-2">
              <span v-for="item in issues" :key="item.category" class="tag-pill bg-white text-amber-700">
                {{ item.category }} · {{ item.count }}
              </span>
            </div>
            <p v-else class="mt-3 text-sm text-slate-500">暂无明确问题分类。</p>
            <p class="mt-4 rounded-[8px] border border-amber-100 bg-white/80 p-3 text-sm leading-6 text-slate-700">
              老师下一步建议：{{ dossier.next_teacher_action }}
            </p>
            <div v-if="practiceRecommendations.length" class="mt-3 rounded-[8px] border border-amber-100 bg-white/80 px-3 py-2">
              <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div class="min-w-0">
                  <p class="text-xs font-semibold text-amber-700">下一道巩固题</p>
                  <p class="mt-1 truncate text-sm font-semibold text-slate-900">
                    {{ practiceRecommendations[0].pid }} {{ practiceRecommendations[0].title }}
                  </p>
                  <p class="mt-1 text-xs leading-5 text-slate-500">{{ practiceRecommendations[0].reason }}</p>
                </div>
                <a
                  class="inline-flex shrink-0 rounded-[8px] bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700 ring-1 ring-amber-100"
                  :href="practiceRecommendations[0].url"
                  target="_blank"
                  rel="noreferrer"
                >
                  打开题目
                </a>
              </div>
            </div>
          </article>
        </div>

        <article class="bento-card border-violet-100 bg-violet-50/40">
          <p class="text-sm font-semibold text-violet-700">最近一条典型证据</p>
          <p class="mt-3 text-sm leading-6 text-slate-700">
            {{ issues[0]?.evidence || aichatSessions[0]?.latest_student_message || '暂无典型证据。' }}
          </p>
        </article>
      </div>

      <div v-else-if="activeTab === '做题记录'" class="mt-6 space-y-3">
        <article v-for="item in completions" :key="item.id" class="bento-card border-slate-200 bg-white">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="font-semibold text-slate-900">{{ item.problem_title || item.problem_id || '未命名题目' }}</p>
              <p class="mt-1 text-xs text-slate-400">{{ formatDate(item.created_at) }}</p>
            </div>
            <span class="tag-pill bg-cyan-50 text-cyan-700">{{ methodLabel(item.reported_completion) }}</span>
          </div>
          <p class="mt-3 text-sm text-slate-600">结果：{{ resultLabel(item.result_status) }} · 积分：{{ item.points_awarded || 0 }}</p>
          <p class="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">一句话总结：{{ item.key_step_summary || '暂未填写' }}</p>
        </article>
        <p v-if="!completions.length" class="rounded-[8px] border border-dashed border-slate-200 p-4 text-sm text-slate-500">暂无做题记录。</p>
      </div>

      <div v-else-if="activeTab === '理解与复盘'" class="mt-6 space-y-3">
        <article v-for="item in reviews" :key="item.id" class="bento-card border-slate-200 bg-white">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="font-semibold text-slate-900">{{ item.problem_title || '未命名复盘' }}</p>
              <p class="mt-1 text-xs text-slate-400">{{ formatDate(item.created_at) }}</p>
            </div>
            <span class="tag-pill bg-emerald-50 text-emerald-700">{{ bridgePathLabel(item.bridge_path) }}</span>
          </div>
          <p class="mt-3 text-sm leading-6 text-slate-700">最近没想明白的关键点：{{ item.main_block || item.key_bridge || item.bottleneck_text || '暂无' }}</p>
          <p class="mt-2 text-sm leading-6 text-slate-500">诊断：{{ item.diagnosis || '暂无诊断' }}</p>
        </article>
        <p v-if="!reviews.length" class="rounded-[8px] border border-dashed border-slate-200 p-4 text-sm text-slate-500">暂无复盘验证记录。</p>
      </div>

      <div v-else-if="activeTab === 'AIChat 证据'" class="mt-6 space-y-3">
        <article v-for="item in aichatSessions" :key="item.session_id" class="bento-card border-slate-200 bg-white">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="font-semibold text-slate-900">{{ item.problem_id || '未绑定题目' }}</p>
              <p class="mt-1 text-xs text-slate-400">{{ formatDate(item.started_at || item.updated_at) }} · {{ item.total_turns || item.message_count || 0 }} 轮</p>
            </div>
            <span class="tag-pill" :class="item.same_point_loop_detected ? 'bg-rose-50 text-rose-700' : 'bg-slate-100 text-slate-600'">
              {{ item.same_point_loop_detected ? '同点打转' : '暂无打转' }}
            </span>
          </div>
          <p class="mt-3 text-sm text-slate-600">暴露的问题类型：{{ item.latest_tutor_action || item.last_ai_action || '暂无' }}</p>
          <p class="mt-2 text-sm text-slate-500">理解证据数：{{ item.evidence_count || 0 }}</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <button class="rounded-[8px] bg-cyan-50 px-3 py-2 text-xs font-semibold text-cyan-700" type="button" @click="toggleSessionDetail(item)">
              {{ expandedSessionId === item.session_id ? '收起完整对话' : '展开完整对话' }}
            </button>
            <RouterLink class="inline-flex rounded-[8px] bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600" to="/app/teacher/aichat-history">
              去学习记录页查看全部
            </RouterLink>
          </div>
          <div v-if="expandedSessionId === item.session_id" class="mt-4 rounded-[16px] border border-slate-100 bg-slate-50/70 p-3">
            <p v-if="loadingSessionId === item.session_id" class="text-sm text-slate-500">正在加载完整对话...</p>
            <div v-else-if="sessionMessages(item.session_id).length" class="space-y-3">
              <section
                v-if="sessionAnalysis(item.session_id)"
                class="rounded-[8px] border bg-white p-3"
                :class="sessionAnalysis(item.session_id).status === 'completed' ? 'border-emerald-100' : sessionAnalysis(item.session_id).status === 'failed' ? 'border-rose-100' : 'border-amber-100'"
              >
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <p class="text-xs font-semibold tracking-[0.12em] text-slate-400">会话总结分析器</p>
                  <div class="flex flex-wrap items-center gap-2">
                    <button
                      v-if="sessionAnalysis(item.session_id).status !== 'processing'"
                      class="rounded-full bg-white px-2 py-1 text-xs font-semibold text-slate-600"
                      type="button"
                      @click="retrySessionAnalysis(item.session_id)"
                    >
                      重新生成会话总结
                    </button>
                    <span
                      class="rounded-full px-2 py-1 text-xs font-semibold"
                      :class="sessionAnalysis(item.session_id).status === 'completed' ? 'bg-emerald-100 text-emerald-700' : sessionAnalysis(item.session_id).status === 'failed' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800'"
                    >
                      {{ sessionAnalysis(item.session_id).status === 'completed' ? '已生成' : sessionAnalysis(item.session_id).status === 'failed' ? '生成失败' : '生成中' }}
                    </span>
                  </div>
                </div>
                <p v-if="sessionAnalysis(item.session_id).status === 'processing'" class="mt-2 text-sm leading-6 text-amber-800">
                  正在生成这段对话的教师总结，完成后会自动刷新。
                </p>
                <p v-else-if="sessionAnalysis(item.session_id).status === 'failed'" class="mt-2 text-sm leading-6 text-rose-700">
                  生成失败：{{ sessionAnalysis(item.session_id).failure_reason || '未知原因' }}
                </p>
                <div v-else-if="sessionAnalysisPayload(item.session_id)" class="mt-3 grid gap-3 md:grid-cols-3">
                  <div class="rounded-[8px] bg-emerald-50 p-3">
                    <p class="text-xs font-semibold text-emerald-700">主要问题</p>
                    <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ sessionAnalysisPayload(item.session_id).main_issue || '暂无' }}</p>
                  </div>
                  <div class="rounded-[8px] bg-sky-50 p-3">
                    <p class="text-xs font-semibold text-sky-700">老师下一步</p>
                    <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ sessionAnalysisPayload(item.session_id).teacher_next_action || '暂无建议' }}</p>
                  </div>
                  <div class="rounded-[8px] bg-slate-50 p-3">
                    <p class="text-xs font-semibold text-slate-500">练习方向</p>
                    <p class="mt-2 text-sm font-semibold leading-6 text-slate-800">{{ sessionAnalysisPayload(item.session_id).recommended_practice_type || '暂无推荐' }}</p>
                  </div>
                </div>
              </section>
              <article
                v-for="message in sessionMessages(item.session_id)"
                :key="message.id"
                class="rounded-[14px] border p-3"
                :class="messageClass(message.role)"
              >
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <span class="text-xs font-semibold text-slate-500">{{ roleLabel(message.role) }}</span>
                  <span class="text-[11px] text-slate-400">{{ formatDate(message.created_at) }}</span>
                </div>
                <div class="mt-2 space-y-2 text-sm leading-6">
                  <template v-for="(part, index) in codeParts(message.content)" :key="index">
                    <pre v-if="part.type === 'code'" class="overflow-auto rounded-[8px] bg-slate-950 p-3 text-xs leading-5 text-slate-50"><code>{{ part.value }}</code></pre>
                    <p v-else class="whitespace-pre-wrap">{{ part.value }}</p>
                  </template>
                </div>
                <p v-if="judgeForMessage(item.session_id, message)" class="mt-2 rounded-[8px] bg-white/75 px-3 py-2 text-xs text-slate-500">
                  系统判断：{{ judgeForMessage(item.session_id, message).judge_primary_intent || '暂无' }}
                  · {{ judgeForMessage(item.session_id, message).judge_action_subtype || '暂无动作' }}
                  · 置信度 {{ judgeForMessage(item.session_id, message).judge_confidence ?? '—' }}
                </p>
              </article>
            </div>
            <p v-else class="text-sm text-slate-500">这段会话暂时没有可展示的完整消息。</p>
          </div>
        </article>
        <p v-if="!aichatSessions.length" class="rounded-[8px] border border-dashed border-slate-200 p-4 text-sm text-slate-500">暂无 AIChat 证据。</p>
      </div>

      <div v-else class="mt-6 grid gap-6 xl:grid-cols-[1fr_0.8fr]">
        <form class="bento-card border-cyan-100 bg-white" @submit.prevent="saveNote">
          <p class="text-sm font-semibold text-cyan-700">干预记录</p>
          <p class="mt-2 text-xs leading-5 text-slate-500">记录“你做了什么”和“针对什么问题”，系统后续只做观察，不直接宣称因果。</p>
          <div class="mt-4 grid gap-3 md:grid-cols-2">
            <label class="text-xs font-semibold text-slate-500">
              干预方式
              <select v-model="interventionType" class="mt-2 w-full rounded-[8px] border border-slate-200 px-3 py-2 text-sm">
                <option value="mini_lesson">讲一个小例子</option>
                <option value="similar_problem">布置同类题</option>
                <option value="oral_check">口头追问</option>
                <option value="difficulty_downshift">降低难度</option>
                <option value="emotional_support">情绪鼓励</option>
                <option value="classroom_observation">课堂观察</option>
              </select>
            </label>
            <label class="text-xs font-semibold text-slate-500">
              针对问题
              <input v-model="targetIssue" class="mt-2 w-full rounded-[8px] border border-slate-200 px-3 py-2 text-sm" placeholder="如：代码实现卡住" />
            </label>
          </div>
          <textarea v-model="noteText" class="mt-4 min-h-32 w-full rounded-[8px] border border-slate-200 px-4 py-3 text-sm outline-none focus:border-cyan-400" placeholder="记录你下次要怎么跟进这个学生。" />
          <div class="mt-3 grid gap-3 md:grid-cols-2">
            <select v-model="noteStatus" class="rounded-[8px] border border-slate-200 px-3 py-2 text-sm">
              <option value="continue_followup">继续关注</option>
              <option value="handled">已处理</option>
              <option value="watch">观察</option>
              <option value="resolved">暂时结束</option>
            </select>
            <input v-model="nextFollowupAt" class="rounded-[8px] border border-slate-200 px-3 py-2 text-sm" placeholder="下次跟进时间，可选" />
          </div>
          <button class="button-primary mt-4" type="submit" :disabled="saving || !noteText.trim()">保存老师记录</button>
        </form>
        <div class="space-y-3">
          <article v-for="item in notes" :key="item.id" class="bento-card border-slate-200 bg-white">
            <div class="flex items-center justify-between gap-3">
              <span class="tag-pill bg-cyan-50 text-cyan-700">{{ interventionTypeLabel(item.intervention_type) }}</span>
              <span class="text-xs text-slate-400">{{ formatDate(item.created_at) }}</span>
            </div>
            <p v-if="item.target_issue" class="mt-2 text-xs font-semibold text-slate-500">针对问题：{{ item.target_issue }}</p>
            <p class="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{{ item.note }}</p>
            <p v-if="item.next_followup_at" class="mt-2 text-xs text-slate-500">下次跟进：{{ item.next_followup_at }}</p>
            <p class="mt-2 rounded-[8px] bg-slate-50 px-3 py-2 text-xs leading-5 text-slate-600">
              后续观察：{{ item.followup_observation?.detail || item.followup_observation?.label || '观察中' }}
            </p>
          </article>
          <p v-if="!notes.length" class="rounded-[8px] border border-dashed border-slate-200 p-4 text-sm text-slate-500">暂无老师记录。</p>
        </div>
      </div>
    </section>
  </div>
</template>
