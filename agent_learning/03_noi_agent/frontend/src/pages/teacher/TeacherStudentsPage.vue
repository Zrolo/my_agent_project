<script setup>
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';

import {
  getTeacherAIChatObservations,
  getTeacherCheckins,
  getTeacherClassLearningDiagnosis,
  getTeacherFlags,
  getTeacherStudents,
} from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const checkins = ref([]);
const flags = ref([]);
const students = ref([]);
const aichatObservations = ref([]);
const classDiagnosis = ref(null);
const pageSize = 5;
const studentRowsCurrentPage = ref(1);
const attentionCurrentPage = ref(1);

const studentNameById = computed(() => {
  const map = new Map();
  for (const student of students.value) {
    map.set(student.user_id, student.display_name || student.user_id);
  }
  return map;
});

const observationsByStudent = computed(() => {
  const map = new Map();
  for (const item of aichatObservations.value) {
    if (!map.has(item.student_id)) {
      map.set(item.student_id, item);
    }
  }
  return map;
});

const studentRows = computed(() => {
  const grouped = new Map();
  for (const student of students.value) {
    grouped.set(student.user_id, {
      student_id: student.user_id,
      display_name: student.display_name || student.user_id,
      total_checkins: 0,
      latest_problem_title: '',
      latest_review_status: '',
    });
  }
  for (const item of checkins.value) {
    const row = grouped.get(item.student_id) || {
      student_id: item.student_id,
      display_name: studentDisplayName(item.student_id),
      total_checkins: 0,
      latest_problem_title: item.problem_title || '',
      latest_review_status: item.review_status || '',
    };
    row.total_checkins += 1;
    if (!row.latest_problem_title) row.latest_problem_title = item.problem_title || '';
    if (!row.latest_review_status) row.latest_review_status = item.review_status || '';
    grouped.set(item.student_id, row);
  }
  return Array.from(grouped.values());
});

const activeStudentCount = computed(() =>
  studentRows.value.filter((row) => row.total_checkins > 0 || observationsByStudent.value.has(row.student_id)).length,
);

const attentionRows = computed(() => {
  const rows = [];
  const seen = new Set();
  for (const item of classDiagnosis.value?.attention_students || []) {
    const studentId = item.student_id || '';
    if (!studentId) continue;
    seen.add(studentId);
    rows.push({
      student_id: studentId,
      display_name: item.display_name || studentDisplayName(studentId),
      reason: item.reason || '需要老师看一眼',
      evidence: item.evidence || '系统没有留下具体证据，请进入学生档案核对最近记录。',
      teacher_action: item.teacher_action || '进入学生档案，先看最近 AIChat、做题记录和复盘证据。',
      severity: item.severity || 'medium',
      source: '学习诊断',
    });
  }
  for (const flag of flags.value) {
    const studentId = flag.student_id || '';
    if (!studentId || seen.has(studentId)) continue;
    rows.push({
      student_id: studentId,
      display_name: studentDisplayName(studentId),
      reason: flag.description ? flagTypeText(flag.flag_type) : '人工标记，暂无具体原因',
      evidence: flag.description || '这条旧标记没有写明原因，建议进入学生档案补看最近证据。',
      teacher_action: flag.description
        ? '根据标记说明进入学生档案核对证据，再决定是否继续关注。'
        : '不要只凭这个标签判断学生；先看学生详情里的 AIChat、做题记录和复盘。',
      severity: flag.severity || 'medium',
      source: '人工标记',
    });
  }
  return rows;
});

function pageCount(items) {
  return Math.max(1, Math.ceil(items.length / pageSize));
}

function pageSlice(items, currentPage) {
  const start = (currentPage.value - 1) * pageSize;
  return items.slice(start, start + pageSize);
}

const studentRowsPageCount = computed(() => pageCount(studentRows.value));
const attentionPageCount = computed(() => pageCount(attentionRows.value));
const visibleStudentRows = computed(() => pageSlice(studentRows.value, studentRowsCurrentPage));
const visibleAttentionRows = computed(() => pageSlice(attentionRows.value, attentionCurrentPage));

function previousPage(pageRef) {
  pageRef.value = Math.max(1, pageRef.value - 1);
}

function nextPage(pageRef, totalPages) {
  pageRef.value = Math.min(totalPages.value, pageRef.value + 1);
}

function reviewStatusText(status) {
  const map = {
    pending: '生成中',
    completed: '已完成',
    failed: '生成失败',
    queued: '排队中',
  };
  return map[status] || '暂无';
}

function severityText(severity) {
  const map = {
    low: '低',
    medium: '中',
    high: '高',
  };
  return map[severity] || '中';
}

function flagTypeText(flagType) {
  const map = {
    quiz_bridge_not_passed: '测验未通过',
    needs_teacher_followup: '需要老师跟进',
    not_mastered: '暂未掌握',
  };
  return map[flagType] || '需要关注';
}

function studentDisplayName(studentId) {
  return studentNameById.value.get(studentId) || studentId || '未知学生';
}

function studentObservation(row) {
  return observationsByStudent.value.get(row.student_id) || null;
}

function studentDossierPath(row) {
  return `/app/teacher/students/${row.student_id}`;
}

function studentStatusText(row) {
  if (row.total_checkins > 0) return '有复盘证据';
  if (studentObservation(row)) return '有 AI 对话记录';
  return '暂时无法判断学习情况';
}

function studentSignalText(row) {
  if (row.latest_problem_title) return `最近在 ${row.latest_problem_title} 留下学习记录。`;
  const observation = studentObservation(row);
  if (observation) return observation.evidence || observation.latest_student_message || '最近有 AI 对话，需要去学习记录页看证据。';
  return 'AI 对话、复盘、做题记录都偏少，建议结合课堂观察。';
}

function studentNextActionText(row) {
  if (row.total_checkins > 0) return '先看最近复盘和理解验证，再决定是否布置同类题。';
  const observation = studentObservation(row);
  if (observation) return observation.teacher_action || observation.suggested_teacher_action || '去学习记录页看最近对话，确认学生是否只是缺少验证证据。';
  return '课堂上点一次口头解释，或让学生补一条做题记录。';
}

async function loadData() {
  loading.value = true;
  error.value = '';
  try {
    const [studentResult, checkinResult, flagResult, observationResult, diagnosisResult] = await Promise.all([
      getTeacherStudents(auth.token),
      getTeacherCheckins(auth.token),
      getTeacherFlags(auth.token),
      getTeacherAIChatObservations(auth.token, { limit: 30, days: 30 }),
      getTeacherClassLearningDiagnosis(auth.token, { days: 15 }),
    ]);
    students.value = studentResult.students || [];
    checkins.value = checkinResult.checkins || [];
    flags.value = flagResult.flags || [];
    aichatObservations.value = observationResult.observations || [];
    classDiagnosis.value = diagnosisResult || null;
    studentRowsCurrentPage.value = 1;
    attentionCurrentPage.value = 1;
  } catch (err) {
    error.value = err.message || '加载学生数据失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-3">
      <article class="metric-tile">
        <p class="text-sm text-slate-400">学生人数</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ students.length }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">最近有学习记录</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ activeStudentCount }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">有明确关注原因</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ attentionRows.length }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">学生</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">学生档案入口</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">
            这里只负责找学生和进入档案；具体 AI 对话证据去学习记录页，复盘质量去复盘页。
          </p>
        </div>
        <button class="button-secondary" type="button" @click="loadData">刷新</button>
      </div>
      <p v-if="loading" class="text-sm text-slate-500">正在加载学生数据...</p>
      <p v-else-if="error" class="rounded-[8px] bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
      <div v-else class="grid gap-6 xl:grid-cols-[1fr_0.75fr]">
        <div class="space-y-4">
          <article v-for="row in visibleStudentRows" :key="row.student_id" class="bento-card border-cyan-100 bg-gradient-to-br from-white via-cyan-50/50 to-teal-50/45">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-cyan-700">学生：{{ row.display_name }}</p>
                <p class="mt-1 text-xs text-slate-400">账号：{{ row.student_id }}</p>
                <p class="mt-2 text-lg font-semibold text-slate-900">{{ row.latest_problem_title || '暂无最近题目' }}</p>
              </div>
              <span class="tag-pill bg-slate-100 text-slate-700">{{ row.total_checkins }} 条复盘</span>
            </div>
            <div class="mt-4 grid gap-3 md:grid-cols-3">
              <div class="rounded-[8px] border border-white/80 bg-white/80 p-3">
                <p class="text-xs font-semibold text-slate-400">当前状态</p>
                <p class="mt-1 text-sm font-semibold text-slate-700">{{ studentStatusText(row) }}</p>
              </div>
              <div class="rounded-[8px] border border-white/80 bg-white/80 p-3 md:col-span-2">
                <p class="text-xs font-semibold text-slate-400">最近信号</p>
                <p class="mt-1 text-sm leading-6 text-slate-700">{{ studentSignalText(row) }}</p>
              </div>
            </div>
            <p class="mt-3 text-sm text-slate-500">最近复盘状态：{{ reviewStatusText(row.latest_review_status) }}</p>
            <p class="mt-3 rounded-[8px] border border-cyan-100 bg-white/80 p-3 text-sm leading-6 text-slate-600">
              老师下一步：{{ studentNextActionText(row) }}
            </p>
            <div class="mt-4 flex flex-wrap gap-2">
              <RouterLink class="button-primary px-3 py-2 text-xs" :to="studentDossierPath(row)">进入学生档案</RouterLink>
              <RouterLink class="button-secondary px-3 py-2 text-xs" to="/app/teacher/aichat-history">查看学习记录</RouterLink>
              <RouterLink class="button-secondary px-3 py-2 text-xs" :to="{ path: '/app/teacher/reflection', query: { tab: 'checkins' } }">查看复盘</RouterLink>
            </div>
            <p class="mt-2 text-xs text-slate-400">做题记录会进入学生档案；没有记录时不要直接判断学生没问题。</p>
          </article>
          <div v-if="studentRows.length === 0" class="rounded-[8px] border border-dashed border-cyan-200 bg-cyan-50/50 p-5 text-sm text-slate-600">
            暂无学生记录
          </div>
          <div v-if="studentRows.length > pageSize" class="flex items-center justify-between rounded-[8px] bg-slate-50 px-4 py-3 text-sm text-slate-500">
            <span>第 {{ studentRowsCurrentPage }} / {{ studentRowsPageCount }} 页</span>
            <div class="flex gap-2">
              <button class="button-secondary px-3 py-2 text-xs" type="button" :disabled="studentRowsCurrentPage <= 1" @click="previousPage(studentRowsCurrentPage)">上一页</button>
              <button class="button-secondary px-3 py-2 text-xs" type="button" :disabled="studentRowsCurrentPage >= studentRowsPageCount" @click="nextPage(studentRowsCurrentPage, studentRowsPageCount)">下一页</button>
            </div>
          </div>
        </div>

        <aside class="bento-card border-slate-200 bg-white">
          <p class="text-sm font-semibold text-slate-700">关注原因</p>
          <p class="mt-2 text-sm leading-6 text-slate-500">这里只放能解释“为什么要看”的学生；没有原因的标签不能单独作为教学判断。</p>
          <div v-if="attentionRows.length" class="mt-4 space-y-3">
            <article v-for="item in visibleAttentionRows" :key="`${item.student_id}-${item.reason}`" class="rounded-[8px] border border-slate-100 bg-slate-50/80 p-4">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="break-words text-sm font-semibold text-slate-900">{{ item.display_name }}</p>
                  <p class="mt-1 break-words text-sm font-semibold text-slate-700">关注原因：{{ item.reason }}</p>
                </div>
                <span class="tag-pill bg-cyan-50 text-cyan-700">{{ item.source }} · {{ severityText(item.severity) }}</span>
              </div>
              <p class="mt-3 whitespace-pre-wrap break-words text-sm leading-6 text-slate-600">
                <span class="font-semibold text-slate-700">证据来源：</span>{{ item.evidence }}
              </p>
              <p class="mt-3 rounded-[8px] border border-white/80 bg-white/80 p-3 text-sm leading-6 text-slate-600">
                <span class="font-semibold text-slate-700">老师下一步建议：</span>{{ item.teacher_action }}
              </p>
              <RouterLink class="mt-3 inline-flex rounded-[8px] border border-cyan-100 bg-cyan-50 px-3 py-2 text-xs font-semibold text-cyan-800" :to="`/app/teacher/students/${item.student_id}`">
                查看学生详情
              </RouterLink>
            </article>
          </div>
          <div v-if="attentionRows.length > pageSize" class="mt-4 flex items-center justify-between rounded-[8px] bg-slate-50 px-4 py-3 text-sm text-slate-500">
            <span>第 {{ attentionCurrentPage }} / {{ attentionPageCount }} 页</span>
            <div class="flex gap-2">
              <button class="button-secondary px-3 py-2 text-xs" type="button" :disabled="attentionCurrentPage <= 1" @click="previousPage(attentionCurrentPage)">上一页</button>
              <button class="button-secondary px-3 py-2 text-xs" type="button" :disabled="attentionCurrentPage >= attentionPageCount" @click="nextPage(attentionCurrentPage, attentionPageCount)">下一页</button>
            </div>
          </div>
          <p v-else class="mt-4 rounded-[8px] border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">暂无明确关注原因</p>
        </aside>
      </div>
    </section>
  </div>
</template>
