<script setup>
import { computed, onMounted, ref } from 'vue';

import { getTeacherStudentFeedback } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const feedback = ref([]);

const categoryLabels = {
  aichat: 'AIChat 对话',
  checkin: '深入复盘',
  code: '代码编辑 / 运行',
  page: '页面使用',
  other: '其他建议',
};

const averageRating = computed(() => {
  if (!feedback.value.length) return '暂无';
  const total = feedback.value.reduce((sum, item) => sum + Number(item.rating || 0), 0);
  return (total / feedback.value.length).toFixed(1);
});

function categoryLabel(value) {
  return categoryLabels[value] || '其他建议';
}

function ratingLabel(value) {
  const map = {
    5: '很好用',
    4: '比较好用',
    3: '一般',
    2: '有点不好用',
    1: '很影响使用',
  };
  return map[Number(value)] || '未评分';
}

function formatTime(value) {
  if (!value) return '暂无时间';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

async function loadFeedback() {
  loading.value = true;
  error.value = '';
  try {
    const result = await getTeacherStudentFeedback(auth.token, { limit: 100 });
    feedback.value = result.feedback || [];
  } catch (err) {
    error.value = err.message || '加载学生反馈失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadFeedback);
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-3">
      <article class="metric-tile">
        <p class="text-sm text-slate-400">反馈条数</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ feedback.length }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">平均感受</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ averageRating }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">最新反馈</p>
        <p class="mt-2 text-sm font-semibold text-slate-700">{{ feedback[0] ? formatTime(feedback[0].created_at) : '暂无' }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">学生反馈</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">学生使用反馈表</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">这里显示学生主动提交的使用问题和建议，方便你判断下一步要优先改哪里。</p>
        </div>
        <button class="button-secondary" type="button" @click="loadFeedback">加载反馈</button>
      </div>
    </section>

    <section v-if="loading" class="panel text-sm text-slate-500">正在加载学生反馈...</section>
    <section v-else-if="error" class="panel rounded-2xl bg-rose-50 text-sm font-medium text-rose-700">{{ error }}</section>
    <section v-else-if="feedback.length === 0" class="panel border-dashed border-cyan-200 bg-cyan-50/50 text-sm text-slate-600">
      暂无学生反馈
    </section>
    <section v-else class="grid gap-4 xl:grid-cols-2">
      <article
        v-for="item in feedback"
        :key="item.id"
        class="rounded-[28px] border border-cyan-100 bg-gradient-to-br from-white via-cyan-50/40 to-teal-50/40 p-5 shadow-sm"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="text-sm font-semibold text-cyan-700">{{ item.student_id }}</p>
            <h4 class="mt-2 text-lg font-bold text-slate-900">{{ categoryLabel(item.category) }}</h4>
            <p class="mt-1 text-xs text-slate-400">{{ formatTime(item.created_at) }}</p>
          </div>
          <span class="tag-pill bg-cyan-50 text-cyan-700">{{ ratingLabel(item.rating) }}</span>
        </div>
        <div class="mt-4 rounded-[20px] border border-white/80 bg-white/85 p-4">
          <p class="text-xs font-semibold text-slate-400">反馈内容</p>
          <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">{{ item.content }}</p>
        </div>
        <p v-if="item.page_context" class="mt-3 break-words text-xs text-slate-400">来源页面：{{ item.page_context }}</p>
      </article>
    </section>
  </div>
</template>
