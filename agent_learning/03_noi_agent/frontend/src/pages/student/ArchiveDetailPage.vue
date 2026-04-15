<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';

import { getCheckinDetail } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  checkinId: {
    type: [String, Number],
    required: true,
  },
});

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const detail = ref(null);

const reviewSummary = computed(() => {
  if (!detail.value) return [];
  return [
    { label: '当前进度', value: detail.value.review_status || 'pending' },
    { label: '这次完成到哪', value: detail.value.completion_status || '—' },
    { label: '提交结果', value: detail.value.submission_result || '—' },
  ];
});

const reviewSections = computed(() => {
  const review = detail.value?.review;
  if (!review) return [];
  return [
    { label: '这次我卡在哪里', value: review.problem_focus || review.main_block || '' },
    { label: '系统先帮我站稳哪一步', value: review.key_bridge || '' },
    { label: '我脑子里该先看到什么图', value: review.visual_hint || '' },
    { label: '系统带我过了一遍什么', value: review.guided_walkthrough || '' },
    { label: '我现在可以先试什么', value: review.try_now || '' },
  ].filter((section) => section.value);
});

const nextAction = computed(() => {
  const review = detail.value?.review;
  if (review?.try_now) return review.try_now;
  const latestQuiz = (detail.value?.quiz_history || []).slice(-1)[0];
  if (latestQuiz?.question_text || latestQuiz?.question) {
    return latestQuiz.question_text || latestQuiz.question;
  }
  return '先回到上面的复盘链路，挑最靠近当前卡点的那一步重新试一遍。';
});

function summarizeQuiz(quiz) {
  if (!quiz) return '';
  const label = quiz.quiz_role || quiz.quiz_type || 'quiz';
  const question = quiz.question_text || quiz.question || '';
  return `${label} · ${question}`;
}

async function loadDetail() {
  loading.value = true;
  error.value = '';
  try {
    detail.value = await getCheckinDetail(auth.token, props.checkinId);
  } catch (err) {
    error.value = err.message || '加载详情失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadDetail);
watch(() => props.checkinId, loadDetail);
watch(() => auth.token, (token) => {
  if (token && !detail.value && !loading.value) loadDetail();
});
</script>

<template>
  <div class="space-y-6">
    <section class="panel workspace-card-archive">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="min-w-0">
          <p class="section-eyebrow text-archive-700">Archive Detail</p>
          <h3 class="mt-2 break-words font-display text-2xl font-bold text-slate-900">打卡详情 #{{ checkinId }}</h3>
          <p v-if="detail?.created_at" class="mt-2 text-sm text-slate-500">{{ detail.created_at }}</p>
        </div>
        <RouterLink class="button-secondary" to="/app/archive">返回历史列表</RouterLink>
      </div>
    </section>

    <section v-if="loading" class="panel text-sm text-slate-500">正在加载详情...</section>
    <section v-else-if="error" class="panel rounded-2xl bg-rose-50 text-sm font-medium text-rose-700">{{ error }}</section>
    <template v-else-if="detail">
      <section class="grid gap-4 lg:grid-cols-4">
        <article class="metric-tile min-w-0">
          <p class="text-sm text-slate-400">题目</p>
          <p class="mt-2 break-words text-lg font-semibold text-slate-900">{{ detail.problem_title }}</p>
        </article>
        <article
          v-for="item in reviewSummary"
          :key="item.label"
          class="metric-tile min-w-0"
        >
          <p class="text-sm text-slate-400">{{ item.label }}</p>
          <p class="mt-2 text-lg font-semibold text-slate-900">{{ item.value }}</p>
        </article>
      </section>

      <section class="grid gap-6 xl:grid-cols-[0.88fr_1.12fr]">
        <article class="panel workspace-card-archive min-w-0 space-y-4">
          <div>
            <p class="section-eyebrow text-archive-700">Check-in</p>
            <h4 class="mt-2 text-xl font-semibold text-slate-900">我当时是怎么提交的</h4>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">这次我卡在哪里</p>
            <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">{{ detail.bottleneck_text || '—' }}</p>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div>
              <p class="text-sm font-semibold text-slate-500">题号 / 链接</p>
              <a
                v-if="detail.problem_url"
                :href="detail.problem_url"
                class="mt-2 inline-flex break-all text-sm font-medium leading-7 text-archive-700 hover:text-archive-800"
                target="_blank"
                rel="noreferrer"
              >
                {{ detail.problem_url }}
              </a>
              <p v-else class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">—</p>
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-500">这次完成到哪</p>
              <p class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{{ detail.completion_status || '—' }}</p>
            </div>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div>
              <p class="text-sm font-semibold text-slate-500">提交结果</p>
              <p class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{{ detail.submission_result || '—' }}</p>
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-500">来源</p>
              <p class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{{ detail.oj_source || '—' }}</p>
            </div>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">题面 / 背景</p>
            <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">{{ detail.problem_context || '—' }}</p>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">我已经试过什么</p>
            <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">{{ detail.reflection || '—' }}</p>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">错误类型</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <span
                v-for="tag in detail.error_types || []"
                :key="tag"
                class="tag-pill bg-slate-100 text-slate-700"
              >
                {{ tag }}
              </span>
              <span v-if="!(detail.error_types || []).length" class="text-sm text-slate-500">—</span>
            </div>
          </div>
        </article>

        <article class="panel workspace-card-archive min-w-0 space-y-4">
        <div>
          <p class="section-eyebrow text-archive-700">Learning Chain</p>
          <h4 class="mt-2 text-xl font-semibold text-slate-900">系统是怎么一步步带我过桥的</h4>
        </div>
          <div v-if="reviewSections.length" class="space-y-4">
            <div
              v-for="section in reviewSections"
              :key="section.label"
              class="rounded-[24px] border border-archive-100 bg-white/90 p-4"
            >
              <p class="text-sm font-semibold text-slate-500">{{ section.label }}</p>
              <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">{{ section.value }}</p>
            </div>
          </div>
          <div v-else class="rounded-[24px] border border-dashed border-archive-200 bg-white/80 p-4 text-sm leading-7 text-slate-600">
            <p class="font-semibold text-archive-800">系统正在整理复盘</p>
            <p class="mt-2">你已经提交成功了。复盘生成完成后，这里会显示“卡在哪里、先站稳哪一步、现在该试什么”。</p>
            <button class="button-secondary mt-4" type="button" @click="loadDetail">刷新详情</button>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">我是怎么一步步确认理解的</p>
            <div v-if="(detail.quiz_history || []).length" class="mt-2 space-y-3">
              <div
                v-for="(quiz, index) in detail.quiz_history"
                :key="quiz.quiz_id || index"
                class="rounded-[24px] border border-slate-200 bg-white/90 p-4"
              >
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-archive-600">第 {{ index + 1 }} 步</p>
                <p class="mt-2 text-sm leading-7 text-slate-700">{{ summarizeQuiz(quiz) }}</p>
              </div>
            </div>
            <div v-else class="mt-2 rounded-[24px] border border-dashed border-slate-200 bg-white/70 p-4 text-sm text-slate-500">
              还没有生成理解检查记录。
            </div>
          </div>
          <div class="rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
            <p class="text-sm font-semibold text-emerald-800">我现在可以继续做什么</p>
            <p class="mt-2 whitespace-pre-wrap text-sm leading-7 text-emerald-900">{{ nextAction }}</p>
          </div>
          <div v-if="detail.student_code" class="rounded-[24px] border border-slate-200 bg-slate-950 p-4">
            <p class="text-sm font-semibold text-slate-300">相关代码</p>
            <pre class="mt-3 overflow-auto text-xs leading-6 text-slate-100">{{ detail.student_code }}</pre>
          </div>
        </article>
      </section>
    </template>
  </div>
</template>
