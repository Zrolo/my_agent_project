<script setup>
import { onMounted, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

import { getMyCheckins, getStudentProblemCompletions } from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { buildArchiveDetailPath, resolveCheckinId } from '@/utils/checkinIdentity';

const auth = useAuthStore();
const route = useRoute();
const loading = ref(false);
const error = ref('');
const checkins = ref([]);
const completionRecords = ref([]);
const activeHistoryTab = ref(route.query.tab === 'records' ? 'records' : 'reviews');
const historyTabs = [
  { id: 'reviews', label: '深入复盘' },
  { id: 'records', label: '做题记录' },
];

watch(
  () => route.query.tab,
  (tab) => {
    activeHistoryTab.value = tab === 'records' ? 'records' : 'reviews';
  },
);

const REVIEW_STATUS_LABELS = {
  pending: '复盘生成中',
  queued: '等待整理',
  running: '复盘整理中',
  completed: '复盘已生成',
  failed: '复盘生成失败',
};

const COMPLETION_STATUS_LABELS = {
  independent: '独立完成但还不稳',
  assisted: '提示后完成',
  hinted: '在提示帮助下完成',
  partial: '做到一部分',
  unfinished: '还没完成',
  editorial: '看题解后完成',
};

const PROBLEM_COMPLETION_METHOD_LABELS = {
  self_solved: '自己做出来',
  small_hint: '少量提示后完成',
  classroom_taught: '课堂讲解后完成',
  aichat_assisted: 'AIChat 帮助后完成',
  editorial_completed: '看题解后补完',
  unsure: '还没完全确定',
};

const PROBLEM_COMPLETION_RESULT_LABELS = {
  accepted: 'AC',
  sample_passed: '样例通过，还没提交',
  unsure: '还不确定',
};

const RUNTIME_STAGE_LABELS = {
  pending: '等待整理',
  generation_pending: '等待整理',
  generation_running: '正在整理',
  review_ready: '已完成复盘',
  completed: '已完成复盘',
  quiz_pending: '等待小测',
  quiz_passed: '小测已通过',
  quiz_failed: '小测待修正',
  followup_needed: '需要老师跟进',
  failed: '整理失败',
};

function reviewStatusLabel(item) {
  return REVIEW_STATUS_LABELS[item.review_status] || '复盘生成中';
}

function completionLabel(item) {
  const value = item.completion_status || 'unfinished';
  return COMPLETION_STATUS_LABELS[value] || '还没完成';
}

function stageLabel(item) {
  const raw = String(item.runtime_stage_label || item.runtime_stage || '').trim();
  return RUNTIME_STAGE_LABELS[raw] || raw || '等待继续处理';
}

function problemCompletionMethodLabel(item) {
  return PROBLEM_COMPLETION_METHOD_LABELS[item.reported_completion] || '未记录';
}

function problemCompletionResultLabel(item) {
  return PROBLEM_COMPLETION_RESULT_LABELS[item.result_status] || '未记录';
}

async function loadCheckins() {
  loading.value = true;
  error.value = '';
  try {
    const [checkinResult, completionResult] = await Promise.all([
      getMyCheckins(auth.token),
      getStudentProblemCompletions(auth.token, { limit: 80, days: 365 }),
    ]);
    checkins.value = checkinResult.checkins || [];
    completionRecords.value = completionResult.records || [];
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
          <p class="section-eyebrow text-archive-700">复盘记录</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">历史记录</h3>
          <p class="mt-3 text-sm leading-7 text-slate-600">
            深入复盘用来回看完整整理；只想快速留痕的题，会放在做题记录里。
          </p>
        </div>
        <button class="button-secondary" type="button" @click="loadCheckins">刷新列表</button>
      </div>
      <div class="mt-5 flex flex-wrap gap-2">
        <button
          v-for="tab in historyTabs"
          :key="tab.id"
          :class="activeHistoryTab === tab.id ? 'button-primary px-4 py-2 text-sm' : 'button-secondary px-4 py-2 text-sm'"
          type="button"
          @click="activeHistoryTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
    </section>

    <section class="panel">
      <p v-if="loading" class="text-sm text-slate-500">正在加载历史记录...</p>
      <p v-else-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
      <div v-else-if="activeHistoryTab === 'reviews' && checkins.length === 0" class="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm leading-7 text-slate-500">
        你还没有深入复盘。遇到错过、卡过、靠 AIChat 才想明白的题，可以去“学习记录”里整理一次。
      </div>
      <div v-else-if="activeHistoryTab === 'records' && completionRecords.length === 0" class="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm leading-7 text-slate-500">
        你还没有做题记录。做完一道题后，可以先记一条 30 秒的小记录。
      </div>
      <div v-else-if="activeHistoryTab === 'reviews'" class="space-y-4">
        <RouterLink
          v-for="item in checkins"
          :key="resolveCheckinId(item) || item.problem_title"
          :to="buildArchiveDetailPath(item)"
          class="block min-w-0 rounded-[28px] border border-archive-100 bg-gradient-to-br from-white via-archive-50/65 to-fuchsia-50/60 p-5 transition hover:-translate-y-0.5 hover:border-archive-300 hover:shadow-lg"
        >
          <div class="grid min-w-0 gap-5 lg:grid-cols-[1.2fr_0.8fr]">
            <div class="min-w-0">
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-archive-600">打卡 #{{ resolveCheckinId(item) }}</p>
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
      <div v-else class="space-y-4">
        <article
          v-for="item in completionRecords"
          :key="item.id || `${item.problem_id}-${item.created_at}`"
          class="rounded-[28px] border border-emerald-100 bg-gradient-to-br from-white via-emerald-50/60 to-cyan-50/50 p-5"
        >
          <div class="grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
            <div class="min-w-0">
              <p class="section-eyebrow text-emerald-700">做题记录</p>
              <h4 class="mt-2 break-words text-lg font-semibold text-slate-900">{{ item.problem_title || item.problem_id || '未命名题目' }}</h4>
              <p class="mt-2 break-words text-sm text-slate-500">{{ item.problem_url || '无题目链接' }}</p>
              <p class="mt-4 rounded-[20px] border border-white bg-white/85 p-4 text-sm leading-7 text-slate-700">
                {{ item.key_step_summary || '还没有写学习收获。' }}
              </p>
            </div>
            <div class="rounded-[24px] border border-white bg-white/80 p-4">
              <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">完成方式</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ problemCompletionMethodLabel(item) }}</p>
              <p class="mt-4 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">结果</p>
              <p class="mt-2 text-sm font-semibold text-slate-800">{{ problemCompletionResultLabel(item) }}</p>
              <p class="mt-4 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">记录时间</p>
              <p class="mt-2 text-sm font-medium text-slate-700">{{ item.created_at || '—' }}</p>
              <p class="mt-4 rounded-2xl bg-emerald-50 px-4 py-3 text-xs leading-5 text-emerald-700">
                {{ item.confidence_note || '老师会结合你的 AIChat 和复盘记录一起判断。' }}
              </p>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
