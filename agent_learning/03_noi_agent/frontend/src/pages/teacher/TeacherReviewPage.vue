<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue';

import { getTeacherReviewSamples, submitTeacherManualReview } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const submitting = ref({});
const error = ref('');
const samples = ref([]);
const routeFilter = ref('all');
const studentFilter = ref('');
const problemFilter = ref('');
const masteryFilter = ref('all');
const expandedSamples = ref({});
const currentPage = ref(1);
const pageSize = 5;

const draftByReview = reactive({});

const routeFilters = [
  { value: 'all', label: '全部样例' },
  { value: 'candidate_bridge', label: '只看待确认引导' },
  { value: 'open_bridge', label: '只看新发现引导' },
  { value: 'known_bridge', label: '只看已稳定引导' },
];

const masteryFilters = [
  { value: 'all', label: '全部复盘结果' },
  { value: 'needs_teacher_followup', label: '需要老师跟进' },
  { value: 'not_mastered', label: '暂未掌握' },
  { value: 'mastered', label: '已掌握' },
  { value: 'failed', label: '生成失败' },
];

const routeStatusLabels = {
  known_bridge: '已稳定引导',
  candidate_bridge: '待确认引导',
  open_bridge: '新发现引导',
};

const completionStatusLabels = {
  unfinished: '还没做完',
  independent: '独立完成',
  assisted: '在帮助下完成',
  gave_up: '暂时放弃',
};

const submissionResultLabels = {
  not_submitted: '还没提交',
  accepted: '已通过',
  wrong_answer: '答案错误',
  time_limit_exceeded: '超时',
  runtime_error: '运行错误',
  compile_error: '编译错误',
};

const reviewModeLabels = {
  failure_diagnosis: '错误诊断',
  success_reflection: '通过后复盘',
  stuck_reflection: '做题卡住复盘',
  independent_reflect: '独立复盘',
};

const reviewFamilyLabels = {
  failure_diagnosis: '错误诊断',
  success_reflection: '通过后复盘',
  stuck_reflection: '做题卡住复盘',
};

const errorLayerLabels = {
  reading: '题意理解',
  method: '方法选择',
  modeling: '建模表示',
  core_design: '核心设计',
  implementation: '代码实现',
  insufficient: '信息不足',
};

const masteryStatusLabels = {
  independent_success: '能独立完成',
  assisted_success: '在帮助下掌握',
  not_mastered: '暂未掌握',
  needs_teacher_followup: '需要老师跟进',
};

const routeValueLabels = {
  'candidate-suggestion': '待确认建议',
  'route-known': '已确认路径',
  'mastery-stats': '掌握情况统计',
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
  const value = String(bridgeRouteMeta(sample)[key] || '').trim();
  if (!value) return '—';
  if (routeValueLabels[value]) return routeValueLabels[value];
  if (/^[a-z0-9_-]+$/i.test(value) && /[_-]/.test(value)) return '内部记录';
  return value;
}

function completionStatusText(status) {
  return completionStatusLabels[status] || '还没做完';
}

function submissionResultText(status) {
  return submissionResultLabels[status] || '暂无提交结果';
}

function reviewModeText(status) {
  return reviewModeLabels[status] || '复盘样例';
}

function reviewFamilyText(status) {
  return reviewFamilyLabels[status] || '复盘类型';
}

function errorLayerText(status) {
  return errorLayerLabels[status] || '暂未判断';
}

function masteryStatusText(status) {
  return masteryStatusLabels[status] || '暂未判断';
}

function reviewOutcomeText(sample) {
  if (sample.review_status === 'failed') return '复盘生成失败';
  return masteryStatusText(sample.mastery_status);
}

function normalizeText(value) {
  return String(value || '').trim().toLowerCase();
}

function matchesText(source, keyword) {
  const query = normalizeText(keyword);
  if (!query) return true;
  return normalizeText(source).includes(query);
}

function studentSearchText(sample) {
  return [
    sample.student_id,
    sample.student_name,
    sample.display_name,
    sample.account_name,
  ].filter(Boolean).join(' ');
}

function problemSearchText(sample) {
  return [
    sample.problem_title,
    sample.problem_ref,
    sample.problem_url,
    sample.problem_id,
  ].filter(Boolean).join(' ');
}

function matchesMasteryFilter(sample) {
  if (masteryFilter.value === 'all') return true;
  if (masteryFilter.value === 'failed') return sample.review_status === 'failed';
  if (masteryFilter.value === 'mastered') {
    return ['independent_success', 'assisted_success'].includes(sample.mastery_status);
  }
  return sample.mastery_status === masteryFilter.value;
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
  return samples.value.filter((sample) => {
    const routeMatches = routeFilter.value === 'all' || bridgeRouteMeta(sample).status === routeFilter.value;
    return routeMatches
      && matchesText(studentSearchText(sample), studentFilter.value)
      && matchesText(problemSearchText(sample), problemFilter.value)
      && matchesMasteryFilter(sample);
  });
});

const totalPages = computed(() => Math.max(1, Math.ceil(filteredSamples.value.length / pageSize)));

const visibleSamples = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredSamples.value.slice(start, start + pageSize);
});

function routeFilterCount(status) {
  if (status === 'all') return samples.value.length;
  return samples.value.filter((sample) => bridgeRouteMeta(sample).status === status).length;
}

function isSampleExpanded(sample) {
  return Boolean(expandedSamples.value[sample.review_id]);
}

function toggleSample(sample) {
  expandedSamples.value = {
    ...expandedSamples.value,
    [sample.review_id]: !isSampleExpanded(sample),
  };
}

function previousPage() {
  if (currentPage.value > 1) currentPage.value -= 1;
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1;
}

watch([routeFilter, studentFilter, problemFilter, masteryFilter], () => {
  currentPage.value = 1;
});

watch(totalPages, (pages) => {
  if (currentPage.value > pages) currentPage.value = pages;
});

onMounted(loadSamples);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-orange-600">人工复核</p>
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
      <div class="mt-5 grid gap-3 lg:grid-cols-[1fr_1fr_220px]">
        <label class="block">
          <span class="text-xs font-semibold text-slate-500">学生筛选</span>
          <input
            v-model="studentFilter"
            class="field mt-2"
            type="search"
            placeholder="按学生账号或姓名筛选"
          />
        </label>
        <label class="block">
          <span class="text-xs font-semibold text-slate-500">题目筛选</span>
          <input
            v-model="problemFilter"
            class="field mt-2"
            type="search"
            placeholder="按题号或题目筛选"
          />
        </label>
        <label class="block">
          <span class="text-xs font-semibold text-slate-500">复盘结果</span>
          <select v-model="masteryFilter" class="field mt-2">
            <option v-for="filter in masteryFilters" :key="filter.value" :value="filter.value">
              {{ filter.label }}
            </option>
          </select>
        </label>
      </div>
      <p v-if="error" class="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
    </section>

    <section v-if="loading" class="panel text-sm text-slate-500">正在加载复核样例...</section>
    <section v-else-if="filteredSamples.length === 0" class="panel border-dashed border-orange-200 bg-orange-50/50 text-sm text-slate-600">
      暂无待复核样例
    </section>
    <section v-else class="space-y-4">
      <div class="panel flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm font-medium text-slate-600">共 {{ filteredSamples.length }} 条，第 {{ currentPage }} / {{ totalPages }} 页</p>
        <div class="flex gap-2">
          <button class="button-secondary" type="button" :disabled="currentPage <= 1" @click="previousPage">上一页</button>
          <button class="button-secondary" type="button" :disabled="currentPage >= totalPages" @click="nextPage">下一页</button>
        </div>
      </div>
      <article v-for="sample in visibleSamples" :key="sample.review_id" class="panel workspace-card-operator space-y-4">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-semibold tracking-[0.12em] text-orange-600">复核编号 {{ sample.review_id }}</p>
            <h4 class="mt-2 text-lg font-semibold text-slate-900">{{ sample.problem_title }}</h4>
            <p class="mt-2 text-sm text-slate-500">{{ sample.student_id }} · {{ reviewModeText(sample.review_mode) }} · {{ reviewFamilyText(sample.review_family) }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span class="tag-pill bg-rose-50 text-rose-700">{{ reviewOutcomeText(sample) }}</span>
            <span class="tag-pill bg-orange-50 text-orange-700">{{ completionStatusText(sample.completion_status) }}</span>
            <span class="tag-pill bg-slate-100 text-slate-600">{{ submissionResultText(sample.submission_result) }}</span>
            <button class="button-secondary text-xs" type="button" @click="toggleSample(sample)">
              {{ isSampleExpanded(sample) ? '收起详情' : '展开详情' }}
            </button>
          </div>
        </div>

        <div class="rounded-[24px] border border-orange-100 bg-white/85 p-4">
          <p class="text-sm font-semibold text-slate-800">这次复盘概况</p>
          <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-slate-600">
            {{ sample.problem_focus || sample.bottleneck_text || '这条复盘暂时没有写明学生具体没想明白的地方。' }}
          </p>
          <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-slate-600">
            老师建议先看：{{ sample.try_now || sample.next_action || sample.key_bridge || '复盘内容是否和学生题目、代码、对话一致。' }}
          </p>
        </div>

        <div v-if="isSampleExpanded(sample)" class="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
          <div class="bento-card border-slate-200 bg-white space-y-4">
            <p class="text-sm font-semibold text-slate-700">复盘概况</p>
            <div class="grid gap-3 sm:grid-cols-2">
              <div class="rounded-[20px] border border-slate-100 bg-slate-50/80 p-4">
                <p class="text-xs font-semibold tracking-[0.12em] text-slate-400">学生这次没想明白什么</p>
                <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">{{ sample.problem_focus || sample.bottleneck_text || '—' }}</p>
              </div>
              <div class="rounded-[20px] border border-slate-100 bg-slate-50/80 p-4">
                <p class="text-xs font-semibold tracking-[0.12em] text-slate-400">系统怎么帮他走了一步</p>
                <p class="mt-2 break-words text-sm leading-6 text-slate-700">{{ sample.key_bridge || '—' }}</p>
              </div>
            </div>
            <div class="rounded-[20px] border border-orange-100 bg-orange-50/60 p-4">
              <p class="text-xs font-semibold tracking-[0.12em] text-orange-600">老师可以怎么处理</p>
              <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">{{ sample.try_now || sample.next_action || '—' }}</p>
            </div>
            <div class="rounded-[20px] border border-slate-100 bg-white p-4">
              <p class="text-xs font-semibold tracking-[0.12em] text-slate-500">复盘是否靠谱</p>
              <div class="mt-3 grid gap-3 sm:grid-cols-2">
                <div>
                  <p class="text-xs font-semibold text-slate-400">问题层级</p>
                  <p class="mt-1 text-sm font-medium text-slate-700">{{ errorLayerText(sample.error_layer) }}</p>
                </div>
                <div>
                  <p class="text-xs font-semibold text-slate-400">掌握状态</p>
                  <p class="mt-1 text-sm font-medium text-slate-700">{{ masteryStatusText(sample.mastery_status) }}</p>
                </div>
              </div>
            </div>
            <details class="rounded-[20px] border border-cyan-100 bg-cyan-50/70 p-4">
              <summary class="cursor-pointer text-xs font-semibold tracking-[0.12em] text-cyan-700">系统调试信息</summary>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="mt-3 text-xs font-semibold tracking-[0.12em] text-cyan-700">引导方式观察</p>
                <span class="tag-pill bg-white text-cyan-700">{{ routeStatusLabel(sample) }}</span>
              </div>
              <div class="mt-3 grid gap-3 sm:grid-cols-3">
                <div>
                  <p class="text-xs font-semibold text-slate-400">已稳定引导</p>
                  <p class="mt-1 break-words text-sm font-medium text-slate-700">{{ routeText(sample, 'stable_focus') }}</p>
                </div>
                <div>
                  <p class="text-xs font-semibold text-slate-400">待确认引导</p>
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
            </details>
          </div>
          <form class="space-y-3 rounded-[28px] border border-orange-100 bg-gradient-to-br from-white via-orange-50/55 to-rose-50/45 p-5 shadow-inner" @submit.prevent="submit(sample.review_id)">
            <p class="text-sm font-semibold text-slate-800">老师审核</p>
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
