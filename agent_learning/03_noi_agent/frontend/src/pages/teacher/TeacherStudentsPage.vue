<script setup>
import { computed, onMounted, ref } from 'vue';

import { getTeacherCheckins, getTeacherFlags } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const checkins = ref([]);
const flags = ref([]);

const studentRows = computed(() => {
  const grouped = new Map();
  for (const item of checkins.value) {
    const row = grouped.get(item.student_id) || {
      student_id: item.student_id,
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

async function loadData() {
  loading.value = true;
  error.value = '';
  try {
    const [checkinResult, flagResult] = await Promise.all([
      getTeacherCheckins(auth.token),
      getTeacherFlags(auth.token),
    ]);
    checkins.value = checkinResult.checkins || [];
    flags.value = flagResult.flags || [];
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
    <section class="grid gap-4 lg:grid-cols-3">
      <article class="metric-tile">
        <p class="text-sm text-slate-400">学生数</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ studentRows.length }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">标记数</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ flags.length }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">记录源</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ checkins.length }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">Students</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">学生维度</h3>
        </div>
        <button class="button-secondary" type="button" @click="loadData">刷新</button>
      </div>
      <p v-if="loading" class="text-sm text-slate-500">正在加载学生数据...</p>
      <p v-else-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
      <div v-else class="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <div class="space-y-4">
          <article v-for="row in studentRows" :key="row.student_id" class="bento-card border-cyan-100 bg-gradient-to-br from-white via-cyan-50/50 to-teal-50/45">
            <div class="flex items-center justify-between gap-3">
              <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-700">{{ row.student_id }}</p>
                <p class="mt-2 text-lg font-semibold text-slate-900">{{ row.latest_problem_title || '暂无最近题目' }}</p>
              </div>
              <span class="tag-pill bg-slate-100 text-slate-700">{{ row.total_checkins }} 条记录</span>
            </div>
            <p class="mt-3 text-sm text-slate-500">最近复盘状态：{{ row.latest_review_status || '—' }}</p>
          </article>
          <div v-if="studentRows.length === 0" class="rounded-[24px] border border-dashed border-cyan-200 bg-cyan-50/50 p-5 text-sm text-slate-600">
            暂无学生记录
          </div>
        </div>
        <div class="bento-card border-slate-200 bg-white">
          <p class="text-sm font-semibold text-slate-700">学生标记</p>
          <div v-if="flags.length" class="mt-4 space-y-3">
            <article v-for="flag in flags" :key="`${flag.student_id}-${flag.flag_type}`" class="rounded-[22px] border border-slate-100 bg-slate-50/80 p-4">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="break-words text-sm font-semibold text-slate-900">{{ flag.student_id || '未知学生' }}</p>
                  <p class="mt-1 break-words text-sm text-slate-600">{{ flag.flag_type || '需要关注' }}</p>
                </div>
                <span class="tag-pill bg-cyan-50 text-cyan-700">{{ flag.severity || 'medium' }}</span>
              </div>
              <p class="mt-3 whitespace-pre-wrap break-words text-sm leading-6 text-slate-500">{{ flag.description || '暂无说明' }}</p>
            </article>
          </div>
          <p v-else class="mt-4 rounded-[22px] border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">暂无学生标记</p>
        </div>
      </div>
    </section>
  </div>
</template>
