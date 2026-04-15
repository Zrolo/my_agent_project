<script setup>
import { computed, onMounted, reactive, ref } from 'vue';

import { getTeacherReviewSamples, submitTeacherManualReview } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const submitting = ref({});
const error = ref('');
const samples = ref([]);
const routeFilter = ref('all');

const draftByReview = reactive({});

const routeFilters = [
  { value: 'all', label: '全部样例' },
  { value: 'candidate_bridge', label: '只看候选桥' },
  { value: 'open_bridge', label: '只看开放桥' },
  { value: 'known_bridge', label: '只看稳定桥' },
];

const routeStatusLabels = {
  known_bridge: '稳定桥',
  candidate_bridge: '候选桥',
  open_bridge: '开放桥',
};

function ensureDraft(reviewId) {
  if (!draftByReview[reviewId]) {
    draftByReview[reviewId] = {
      mode_correct: true,
      review_grounded: true,
      student_can_move_next: true,
      notes: '',
    };
  }
  return draftByReview[reviewId];
}

async function loadSamples() {
  loading.value = true;
  error.value = '';
  try {
    const result = await getTeacherReviewSamples(auth.token);
    samples.value = result.samples || [];
    samples.value.forEach((sample) => ensureDraft(sample.review_id));
  } catch (err) {
    error.value = err.message || '加载复核样例失败';
  } finally {
    loading.value = false;
  }
}

async function submit(reviewId) {
  const draft = ensureDraft(reviewId);
  submitting.value = { ...submitting.value, [reviewId]: true };
  try {
    await submitTeacherManualReview(auth.token, reviewId, draft);
  } catch (err) {
    error.value = err.message || '提交复核失败';
  } finally {
    submitting.value = { ...submitting.value, [reviewId]: false };
  }
}

function bridgeRouteMeta(sample) {
  return sample.bridge_route_meta || {};
}

function routeStatusLabel(sample) {
  const status = bridgeRouteMeta(sample).status;
  return routeStatusLabels[status] || '未记录';
}

function routeText(sample, key) {
  return bridgeRouteMeta(sample)[key] || '—';
}

function routeSignals(sample) {
  const signals = bridgeRouteMeta(sample).matched_signals || [];
  return signals.length > 0 ? signals.slice(0, 4).join(' / ') : '—';
}

function routeConflictSignals(sample) {
  const signals = bridgeRouteMeta(sample).conflict_signals || [];
  return signals.length > 0 ? signals.slice(0, 3).join(' / ') : '—';
}

const filteredSamples = computed(() => {
  if (routeFilter.value === 'all') return samples.value;
  return samples.value.filter((sample) => bridgeRouteMeta(sample).status === routeFilter.value);
});

function routeFilterCount(status) {
  if (status === 'all') return samples.value.length;
  return samples.value.filter((sample) => bridgeRouteMeta(sample).status === status).length;
}

onMounted(loadSamples);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-orange-600">Manual Review</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">待人工复核样例</h3>
        </div>
        <button class="button-secondary" type="button" @click="loadSamples">刷新</button>
      </div>
      <div class="mt-5 flex flex-wrap gap-2">
        <button
          v-for="filter in routeFilters"
          :key="filter.value"
          type="button"
          class="tag-pill transition"
          :class="routeFilter === filter.value ? 'bg-orange-500 text-white' : 'bg-white text-slate-600'"
          @click="routeFilter = filter.value"
        >
          {{ filter.label }} · {{ routeFilterCount(filter.value) }}
        </button>
      </div>
      <p v-if="error" class="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
    </section>

    <section v-if="loading" class="panel text-sm text-slate-500">正在加载复核样例...</section>
    <section v-else-if="filteredSamples.length === 0" class="panel border-dashed border-orange-200 bg-orange-50/50 text-sm text-slate-600">
      暂无待复核样例
    </section>
    <section v-else class="space-y-4">
      <article v-for="sample in filteredSamples" :key="sample.review_id" class="panel workspace-card-operator space-y-4">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-orange-600">Review #{{ sample.review_id }}</p>
            <h4 class="mt-2 text-lg font-semibold text-slate-900">{{ sample.problem_title }}</h4>
            <p class="mt-2 text-sm text-slate-500">{{ sample.student_id }} · {{ sample.review_mode }} · {{ sample.review_family }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span class="tag-pill bg-orange-50 text-orange-700">{{ sample.completion_status || 'unfinished' }}</span>
            <span class="tag-pill bg-slate-100 text-slate-600">{{ sample.submission_result || '—' }}</span>
          </div>
        </div>

        <div class="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
          <div class="bento-card border-slate-200 bg-white space-y-4">
            <p class="text-sm font-semibold text-slate-700">样例摘要</p>
            <div class="grid gap-3 sm:grid-cols-2">
              <div class="rounded-[20px] border border-slate-100 bg-slate-50/80 p-4">
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">学生卡点</p>
                <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">{{ sample.problem_focus || sample.bottleneck_text || '—' }}</p>
              </div>
              <div class="rounded-[20px] border border-slate-100 bg-slate-50/80 p-4">
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">知识桥</p>
                <p class="mt-2 break-words text-sm leading-6 text-slate-700">{{ sample.key_bridge || '—' }}</p>
              </div>
            </div>
            <div class="rounded-[20px] border border-orange-100 bg-orange-50/60 p-4">
              <p class="text-xs font-semibold uppercase tracking-[0.16em] text-orange-600">系统建议</p>
              <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">{{ sample.try_now || sample.next_action || '—' }}</p>
            </div>
            <div class="rounded-[20px] border border-cyan-100 bg-cyan-50/70 p-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-700">桥路由观测</p>
                <span class="tag-pill bg-white text-cyan-700">{{ routeStatusLabel(sample) }}</span>
              </div>
              <div class="mt-3 grid gap-3 sm:grid-cols-3">
                <div>
                  <p class="text-xs font-semibold text-slate-400">稳定桥</p>
                  <p class="mt-1 break-words text-sm font-medium text-slate-700">{{ routeText(sample, 'stable_focus') }}</p>
                </div>
                <div>
                  <p class="text-xs font-semibold text-slate-400">候选桥</p>
                  <p class="mt-1 break-words text-sm font-medium text-slate-700">{{ routeText(sample, 'candidate_bridge_id') }}</p>
                </div>
                <div>
                  <p class="text-xs font-semibold text-slate-400">置信度</p>
                  <p class="mt-1 break-words text-sm font-medium text-slate-700">{{ routeText(sample, 'route_confidence') }}</p>
                </div>
              </div>
              <div class="mt-3 grid gap-3 sm:grid-cols-2">
                <div>
                  <p class="text-xs font-semibold text-slate-400">命中信号</p>
                  <p class="mt-1 break-words text-sm leading-6 text-slate-700">{{ routeSignals(sample) }}</p>
                </div>
                <div>
                  <p class="text-xs font-semibold text-slate-400">冲突信号</p>
                  <p class="mt-1 break-words text-sm leading-6 text-slate-700">{{ routeConflictSignals(sample) }}</p>
                </div>
              </div>
            </div>
            <div class="grid gap-3 sm:grid-cols-2">
              <div class="rounded-[20px] border border-slate-100 bg-white p-4">
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">错误层级</p>
                <p class="mt-2 text-sm font-medium text-slate-700">{{ sample.error_layer || '—' }}</p>
              </div>
              <div class="rounded-[20px] border border-slate-100 bg-white p-4">
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">掌握状态</p>
                <p class="mt-2 text-sm font-medium text-slate-700">{{ sample.mastery_status || '—' }}</p>
              </div>
            </div>
          </div>
          <form class="space-y-3 rounded-[28px] border border-orange-100 bg-gradient-to-br from-white via-orange-50/55 to-rose-50/45 p-5 shadow-inner" @submit.prevent="submit(sample.review_id)">
            <label class="flex items-center gap-3 text-sm font-medium text-slate-700">
              <input v-model="draftByReview[sample.review_id].mode_correct" type="checkbox" />
              模式判断正确
            </label>
            <label class="flex items-center gap-3 text-sm font-medium text-slate-700">
              <input v-model="draftByReview[sample.review_id].review_grounded" type="checkbox" />
              复盘结论有依据
            </label>
            <label class="flex items-center gap-3 text-sm font-medium text-slate-700">
              <input v-model="draftByReview[sample.review_id].student_can_move_next" type="checkbox" />
              学生可以继续下一步
            </label>
            <textarea
              v-model="draftByReview[sample.review_id].notes"
              class="field min-h-32 resize-y"
              placeholder="教师备注"
            />
            <button class="button-primary w-full bg-gradient-to-r from-orange-500 to-rose-500" :disabled="submitting[sample.review_id]" type="submit">
              {{ submitting[sample.review_id] ? '正在提交...' : '提交人工复核' }}
            </button>
          </form>
        </div>
      </article>
    </section>
  </div>
</template>
