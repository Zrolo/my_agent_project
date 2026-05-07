<script setup>
import { computed, onMounted, ref } from 'vue';

import { getTeacherCheckins } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const checkins = ref([]);
const currentPage = ref(1);
const pageSize = 5;

const reviewStatusLabels = {
  pending: '复盘生成中',
  completed: '复盘已完成',
  failed: '复盘生成失败',
};

const completionStatusLabels = {
  unfinished: '还没做完',
  independent: '独立完成',
  assisted: '在帮助下完成',
  gave_up: '暂时放弃',
};

function reviewStatusText(status) {
  return reviewStatusLabels[status] || '复盘生成中';
}

function completionStatusText(status) {
  return completionStatusLabels[status] || '还没做完';
}

function hasProblemInfo(item) {
  return Boolean((item.problem_title || '').trim() && (item.problem_url || '').trim());
}

function queueReasonText(item) {
  if (item.review_status === 'failed') return '复盘生成失败';
  if (!hasProblemInfo(item)) return '题目信息缺失';
  if (item.review_status === 'pending' || item.review_status === 'queued') return '复盘还在生成中';
  if (item.review_status === 'completed') return '复盘已完成，可去教学复盘里看质量';
  return '等待系统确认复盘状态';
}

function queueNextActionText(item) {
  if (item.review_status === 'failed') return '检查原始打卡内容，必要时让学生补题号、卡点或重新提交。';
  if (!hasProblemInfo(item)) return '让学生补题号、题目链接和具体卡点，否则复盘很难变成教学证据。';
  if (item.review_status === 'pending' || item.review_status === 'queued') return '暂时不用处理；如果长时间不变，再排查生成任务。';
  if (item.review_status === 'completed') return '回到教学复盘页，看学生是否通过验证、是否需要老师跟进。';
  return '先确认该条记录是否真的需要老师介入。';
}

const totalPages = computed(() => Math.max(1, Math.ceil(checkins.value.length / pageSize)));

const visibleCheckins = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return checkins.value.slice(start, start + pageSize);
});

function previousPage() {
  if (currentPage.value > 1) currentPage.value -= 1;
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1;
}

async function loadCheckins() {
  loading.value = true;
  error.value = '';
  try {
    const result = await getTeacherCheckins(auth.token);
    checkins.value = result.checkins || [];
    currentPage.value = 1;
  } catch (err) {
    error.value = err.message || '加载复盘生成队列失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadCheckins);
</script>

<template>
  <div class="space-y-6">
    <section class="panel workspace-card-operator">
      <div class="flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">深入复盘</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">复盘生成队列</h3>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            这里像 OJ 的评测队列，只用来排查复盘有没有生成、是否失败、题目信息是否缺失；教学判断请回到“教学复盘”。
          </p>
        </div>
        <button class="button-secondary" type="button" @click="loadCheckins">刷新</button>
      </div>
    </section>

    <section v-if="loading" class="panel text-sm text-slate-500">正在加载复盘生成队列...</section>
    <section v-else-if="error" class="panel rounded-2xl bg-rose-50 text-sm font-medium text-rose-700">{{ error }}</section>
    <section v-else-if="checkins.length === 0" class="panel border-dashed border-cyan-200 bg-cyan-50/50 text-sm text-slate-600">
      暂无复盘生成队列记录
    </section>
    <section v-else class="space-y-4">
      <div class="panel flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm font-medium text-slate-600">共 {{ checkins.length }} 条，第 {{ currentPage }} / {{ totalPages }} 页</p>
        <div class="flex gap-2">
          <button class="button-secondary" type="button" :disabled="currentPage <= 1" @click="previousPage">上一页</button>
          <button class="button-secondary" type="button" :disabled="currentPage >= totalPages" @click="nextPage">下一页</button>
        </div>
      </div>
      <article v-for="item in visibleCheckins" :key="item.checkin_id" class="panel workspace-card-operator">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-semibold tracking-[0.12em] text-cyan-700">队列编号 {{ item.checkin_id }}</p>
            <h4 class="mt-2 text-lg font-semibold text-slate-900">{{ item.problem_title }}</h4>
            <p class="mt-2 text-sm text-slate-500">{{ item.student_id }} · {{ item.problem_url || '无题目链接' }}</p>
            <p class="mt-3 text-sm leading-6 text-slate-600">
              <span class="font-semibold text-slate-700">队列原因：</span>{{ queueReasonText(item) }}
            </p>
            <p class="mt-2 rounded-[8px] border border-cyan-100 bg-cyan-50/60 p-3 text-sm leading-6 text-slate-600">
              <span class="font-semibold text-slate-700">下一步：</span>{{ queueNextActionText(item) }}
            </p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span class="tag-pill bg-cyan-50 text-cyan-700">状态</span>
            <span class="tag-pill bg-slate-100 text-slate-700">{{ reviewStatusText(item.review_status) }}</span>
            <span class="tag-pill bg-slate-100 text-slate-700">{{ completionStatusText(item.completion_status) }}</span>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>
