<script setup>
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';

import { getTeacherClassLearningDiagnosis } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const stats = ref(null);

const learningIssueFallbackRows = [
  { id: 'problem_understanding', label: '题意没读透', count: 0, rate: 0, student_count: 0 },
  { id: 'method_selection', label: '方法选择困难', count: 0, rate: 0, student_count: 0 },
  { id: 'key_transformation', label: '知道算法但不会落题', count: 0, rate: 0, student_count: 0 },
  { id: 'implementation', label: '代码实现卡住', count: 0, rate: 0, student_count: 0 },
  { id: 'debugging', label: '调试定位困难', count: 0, rate: 0, student_count: 0 },
  { id: 'complexity_boundary', label: '复杂度判断薄弱', count: 0, rate: 0, student_count: 0 },
  { id: 'knowledge_transfer', label: '同类迁移困难', count: 0, rate: 0, student_count: 0 },
];

function readableLabel(value, fallback = '未命名') {
  const text = String(value || '').trim();
  if (!text) return fallback;
  if (/^[a-z0-9_-]+$/i.test(text) && /[_-]/.test(text)) return fallback;
  return text;
}

function statRows(bucket) {
  if (!bucket) return [];
  if (Array.isArray(bucket)) {
    return bucket.map((item, index) => ({
      id: item.key || item.label || item.name || `${index}`,
      label: readableLabel(item.label || item.category || item.key || item.name || item.topic_l1 || item.topic_l2 || item.bucket, '未命名'),
      count: item.count ?? item.reviewed_count ?? 0,
      total: item.total,
      rate: item.rate,
      student_count: item.student_count || 0,
      teacher_action: item.teacher_action || item.teaching_suggestion,
      resource_suggestions: item.resource_suggestions || {},
      students: item.students || [],
      typical_problems: item.typical_problems || [],
    }));
  }
  return Object.entries(bucket).map(([key, value]) => ({
    id: key,
    label: readableLabel(value?.label || key, '未命名'),
    count: value?.count ?? value?.reviewed_count ?? 0,
    total: value?.total,
    rate: value?.rate,
    student_count: value?.student_count || 0,
    teacher_action: value?.teacher_action,
    resource_suggestions: value?.resource_suggestions || {},
  }));
}

function formatRate(rate) {
  const value = Number(rate);
  if (!Number.isFinite(value)) return '—';
  return `${Math.round(value * 100)}%`;
}

function statCount(bucket) {
  return statRows(bucket).length;
}

const learningIssueRows = computed(() => {
  const rows = statRows(stats.value?.class_issue_summary || stats.value?.learning_issue_stats);
  return rows.length ? rows : learningIssueFallbackRows;
});

const attentionStudents = computed(() => stats.value?.attention_students || []);
const completionSummary = computed(() => stats.value?.practice_summary || stats.value?.completion_summary || {});
const teachingSuggestions = computed(() => {
  if (stats.value?.teaching_suggestions?.length) return stats.value.teaching_suggestions.slice(0, 3);
  return learningIssueRows.value
    .filter((row) => (Number(row.count) || 0) > 0)
    .slice(0, 3)
    .map((row) => ({
      title: row.label,
      reason: `近 15 天有 ${row.student_count || 0} 名学生出现这一类问题。`,
      how_to_teach: row.teacher_action || '用一个 3-5 个对象的小例子讲清关键关系。',
      students: row.students || [],
    }));
});
const teachingSliceRows = computed(() =>
  learningIssueRows.value
    .filter((row) => (Number(row.student_count) || 0) >= 3 || (Number(row.count) || 0) > 0)
    .slice(0, 5),
);

const topLearningIssueCount = computed(() => Math.max(1, ...learningIssueRows.value.map((row) => Number(row.count) || 0)));

const overviewMetrics = computed(() => [
  {
    label: '今天建议关注',
    value: attentionStudents.value.length,
    hint: '按验证失败、支架依赖和学习证据不足聚合',
  },
  {
    label: '已验证理解',
    value: stats.value?.resolved_learning_count ?? statCount(stats.value?.mastery_status_stats),
    hint: '完成结束验证或复盘闭环的学生证据',
  },
  {
    label: '缺少验证证据',
    value: Math.max(0, (stats.value?.active_learning_count || 0) - (stats.value?.resolved_learning_count || 0)),
    hint: '可能已经会了，但还没有留下可靠证据',
  },
      {
        label: '独立完成比例',
        value: `${Math.round((Number(completionSummary.value.independence_ratio) || 0) * 100)}%`,
    hint: completionSummary.value.support_fadeout_label || '近 15 天自己做出或少量提示后完成的比例',
  },
]);

async function loadStats() {
  loading.value = true;
  error.value = '';
  try {
    stats.value = await getTeacherClassLearningDiagnosis(auth.token, { days: 15 });
  } catch (err) {
    error.value = err.message || '加载统计失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadStats);
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 lg:grid-cols-4">
      <article v-for="metric in overviewMetrics" :key="metric.label" class="metric-tile">
        <p class="text-sm text-slate-400">{{ metric.label }}</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ metric.value }}</p>
        <p class="mt-2 text-xs leading-5 text-slate-400">{{ metric.hint }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-operator-700">首页</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">今日带班</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">
            首页只帮你决定今天先看哪些学生、班级状态有什么变化，以及本周最多讲 3 条什么。
          </p>
        </div>
        <button class="button-secondary" type="button" @click="loadStats">刷新</button>
      </div>
      <p v-if="loading" class="text-sm text-slate-500">正在加载统计...</p>
      <p v-else-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
      <div v-else class="grid gap-6 xl:grid-cols-2">
        <div class="bento-card border-rose-100 bg-gradient-to-br from-white via-rose-50/60 to-orange-50/40 xl:col-span-2">
          <div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
            <div>
              <p class="text-sm font-semibold text-rose-700">今天建议关注</p>
              <h4 class="mt-2 font-display text-xl font-bold text-slate-900">今天先看谁：按证据排序，不按 AIChat 次数排序</h4>
            </div>
            <span class="tag-pill bg-white text-rose-700">数据不足也会提示</span>
          </div>
          <div v-if="attentionStudents.length" class="mt-4 grid gap-3 lg:grid-cols-2">
            <article v-for="item in attentionStudents" :key="item.student_id" class="rounded-[22px] border border-white/80 bg-white/85 p-4">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p class="text-xs font-semibold tracking-[0.12em] text-slate-400">涉及学生</p>
                  <p class="mt-1 font-semibold text-slate-900">{{ item.student_id }}</p>
                </div>
                <span class="tag-pill bg-rose-100 text-rose-700">{{ item.status || '建议看看' }}</span>
              </div>
              <p class="mt-3 text-sm font-semibold text-slate-800">{{ item.reason || '学习证据不足，建议课堂观察。' }}</p>
              <p class="mt-2 text-xs leading-5 text-slate-500">证据：{{ item.evidence || item.problem_title || '暂无明确证据' }}</p>
              <p class="mt-2 text-xs leading-5 text-slate-600">老师下一步：{{ item.teacher_action || '先看最近对话，再决定是否当面追问。' }}</p>
              <RouterLink class="mt-3 inline-flex rounded-[8px] bg-white px-3 py-2 text-xs font-semibold text-rose-700 ring-1 ring-rose-100" :to="`/app/teacher/students/${item.student_id}`">
                查看学生详情
              </RouterLink>
            </article>
          </div>
          <p v-else class="mt-4 rounded-[22px] border border-dashed border-rose-200 bg-white/70 p-4 text-sm text-slate-500">
            暂无需要优先关注的学生；如果某些学生记录很少，建议从学生页看“数据不足”。
          </p>
        </div>

        <div class="bento-card border-cyan-100 bg-gradient-to-br from-white via-cyan-50/70 to-sky-50/50">
          <p class="text-sm font-semibold text-cyan-700">最近练习概况</p>
          <h4 class="mt-2 font-display text-xl font-bold text-slate-900">看完成量，也看完成方式</h4>
          <div class="mt-4 grid gap-3 sm:grid-cols-2">
            <div class="rounded-[8px] border border-white/80 bg-white/85 p-4">
              <p class="text-xs font-semibold text-slate-400">最近 15 天完成题数</p>
              <p class="mt-2 text-2xl font-semibold text-slate-900">{{ completionSummary.completed_count || completionSummary.total_15_days || 0 }}</p>
            </div>
            <div class="rounded-[8px] border border-white/80 bg-white/85 p-4">
              <p class="text-xs font-semibold text-slate-400">独立 / 少量提示比例</p>
              <p class="mt-2 text-2xl font-semibold text-slate-900">{{ Math.round((Number(completionSummary.independence_ratio) || 0) * 100) }}%</p>
            </div>
            <div class="rounded-[8px] border border-white/80 bg-white/85 p-4">
              <p class="text-xs font-semibold text-slate-400">AIChat 后完成</p>
              <p class="mt-2 text-2xl font-semibold text-slate-900">{{ completionSummary.aichat_assisted_count || completionSummary.aichat_assisted_15_days || 0 }}</p>
            </div>
            <div class="rounded-[8px] border border-white/80 bg-white/85 p-4">
              <p class="text-xs font-semibold text-slate-400">AC / 验证证据</p>
              <p class="mt-2 text-2xl font-semibold text-slate-900">{{ completionSummary.accepted_count || completionSummary.accepted_15_days || 0 }}</p>
            </div>
          </div>
          <p class="mt-4 rounded-[8px] border border-cyan-100 bg-white/80 p-3 text-sm leading-6 text-slate-600">
            {{ completionSummary.support_fadeout_label || '先看最近 15 天是否有独立完成和验证证据。' }}
          </p>
        </div>

        <div class="bento-card workspace-card-operator">
          <p class="text-sm font-semibold text-operator-700">班级最近主要问题</p>
          <p class="mt-2 text-xs text-slate-500">按“知识点 + 教学切片”看，不再按词语出现次数统计。涉及学生少于阈值的问题不挤到首页。</p>
          <div v-if="teachingSliceRows.length" class="mt-4 space-y-3">
            <div v-for="row in teachingSliceRows" :key="row.id" class="rounded-[22px] border border-white/70 bg-white/85 p-4">
              <div class="flex items-center justify-between gap-3">
                <p class="min-w-0 break-words text-sm font-semibold text-slate-800">{{ row.label }}</p>
                <span class="tag-pill bg-operator-100 text-operator-700">{{ row.count }} 次</span>
              </div>
              <div class="mt-3 h-2 overflow-hidden rounded-full bg-operator-50">
                <div class="h-full rounded-full bg-operator-500" :style="{ width: `${Math.max(8, Math.round((Number(row.count) || 0) / topLearningIssueCount * 100))}%` }" />
              </div>
              <p class="mt-2 text-xs text-slate-500">
                涉及学生 {{ row.student_count || 0 }} 人 · 占比 {{ formatRate(row.rate) }}
              </p>
              <p class="mt-2 text-xs leading-5 text-slate-600">建议讲法：{{ row.teacher_action || '用一个 3-5 个对象的小例子讲清关键关系。' }}</p>
              <div class="mt-3 grid gap-2 text-xs leading-5 text-slate-600">
                <p>推荐练习：{{ row.resource_suggestions?.recommended_exercise || '安排一道同类低难度题。' }}</p>
                <p>讲解要点：{{ row.resource_suggestions?.mini_lesson || row.teacher_action || '先讲清关键关系。' }}</p>
                <p>课堂活动：{{ row.resource_suggestions?.classroom_activity || '让学生先口头说出关键步骤，再写代码。' }}</p>
              </div>
            </div>
          </div>
          <p v-else class="mt-4 rounded-[22px] border border-dashed border-operator-200 bg-white/70 p-4 text-sm text-slate-500">
            暂无学习问题分类数据
          </p>
        </div>

        <div class="bento-card border-emerald-100 bg-gradient-to-br from-white via-emerald-50/70 to-teal-50/50">
          <p class="text-sm font-semibold text-emerald-700">本周教学建议</p>
          <h4 class="mt-2 font-display text-xl font-bold text-slate-900">最多 3 条，避免每个问题都要讲</h4>
          <div v-if="teachingSuggestions.length" class="mt-4 space-y-3">
            <div v-for="row in teachingSuggestions" :key="`advice-${row.title}`" class="rounded-[20px] border border-emerald-100 bg-white/85 p-4">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <p class="break-words text-sm font-semibold text-slate-800">{{ row.title }}</p>
                <span class="tag-pill bg-emerald-100 text-emerald-700">{{ row.students?.length || 0 }} 名学生</span>
              </div>
              <p class="mt-2 text-xs leading-5 text-slate-600">为什么讲：{{ row.reason }}</p>
              <p class="mt-1 text-xs leading-5 text-slate-600">怎么讲：{{ row.how_to_teach }}</p>
            </div>
          </div>
          <p v-else class="mt-4 rounded-[20px] border border-dashed border-emerald-200 bg-white/70 p-4 text-sm text-slate-500">
            暂无需要优先介入的问题。
          </p>
        </div>
      </div>
    </section>
  </div>
</template>
