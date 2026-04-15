<script setup>
import { onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';

import { getMyCheckins } from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { buildArchiveDetailPath, resolveCheckinId } from '@/utils/checkinIdentity';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const checkins = ref([]);

function reviewStatusLabel(item) {
  if (item.review_status === 'completed') return '复盘已生成';
  if (item.review_status === 'failed') return '复盘生成失败';
  return '正在生成复盘';
}

function completionLabel(item) {
  const value = item.completion_status || 'unfinished';
  if (value === 'independent') return '独立完成但还不稳';
  if (value === 'editorial') return '看题解后完成';
  if (value === 'hinted') return '在提示帮助下完成';
  return '还没完成';
}

function stageLabel(item) {
  return item.runtime_stage_label || '等待继续处理';
}

async function loadCheckins() {
  loading.value = true;
  error.value = '';
  try {
    const result = await getMyCheckins(auth.token);
    checkins.value = result.checkins || [];
  } catch (err) {
    error.value = err.message || '加载历史失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadCheckins);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="min-w-0">
          <p class="section-eyebrow text-archive-700">Learning Archive</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">历史打卡</h3>
          <p class="mt-3 text-sm leading-7 text-slate-600">
            这里保留的是你每次提交后的学习记录。点进去可以继续看复盘、回顾自己当时卡住的地方。
          </p>
        </div>
        <button class="button-secondary" type="button" @click="loadCheckins">刷新列表</button>
      </div>
    </section>

    <section class="panel">
      <p v-if="loading" class="text-sm text-slate-500">正在加载历史记录...</p>
      <p v-else-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
      <div v-else-if="checkins.length === 0" class="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm leading-7 text-slate-500">
        你还没有历史打卡。可以先去“打卡复盘”提交第一条记录。
      </div>
      <div v-else class="space-y-4">
        <RouterLink
          v-for="item in checkins"
          :key="resolveCheckinId(item) || item.problem_title"
          :to="buildArchiveDetailPath(item)"
          class="block min-w-0 rounded-[28px] border border-archive-100 bg-gradient-to-br from-white via-archive-50/65 to-fuchsia-50/60 p-5 transition hover:-translate-y-0.5 hover:border-archive-300 hover:shadow-lg"
        >
          <div class="grid min-w-0 gap-5 lg:grid-cols-[1.2fr_0.8fr]">
            <div class="min-w-0">
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-archive-600">Checkin #{{ resolveCheckinId(item) }}</p>
              <h4 class="mt-2 break-words text-lg font-semibold text-slate-900">{{ item.problem_title }}</h4>
              <p class="mt-2 break-words text-sm text-slate-500">{{ item.problem_url || '无题目链接' }}</p>
              <div class="mt-4 grid gap-3 md:grid-cols-2">
                <div class="rounded-2xl bg-white/85 px-4 py-3">
                  <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">当前进度</p>
                  <p class="mt-2 text-sm font-semibold text-slate-800">{{ reviewStatusLabel(item) }}</p>
                </div>
                <div class="rounded-2xl bg-white/85 px-4 py-3">
                  <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">这次完成到哪</p>
                  <p class="mt-2 text-sm font-semibold text-slate-800">{{ completionLabel(item) }}</p>
                </div>
              </div>
            </div>
            <div class="min-w-0 flex flex-col justify-between gap-4 rounded-[24px] border border-white/80 bg-white/80 p-4">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">最后更新</p>
                <p class="mt-2 text-sm font-medium text-slate-700">{{ item.created_at || '—' }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">当前阶段</p>
                <p class="mt-2 text-sm font-medium text-slate-700">{{ stageLabel(item) }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <span class="tag-pill bg-archive-50 text-archive-700">{{ reviewStatusLabel(item) }}</span>
                <span class="tag-pill bg-slate-100 text-slate-600">{{ stageLabel(item) }}</span>
              </div>
              <span class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white">
                继续看这次复盘
              </span>
            </div>
          </div>
        </RouterLink>
      </div>
    </section>
  </div>
</template>
