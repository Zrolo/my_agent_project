<script setup>
import MarkdownIt from 'markdown-it';
import katex from 'katex';
import 'katex/dist/katex.min.css';
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
const problemInfoOpen = ref(false);

const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});

const REVIEW_STATUS_LABELS = {
  pending: '复盘生成中',
  queued: '等待整理',
  running: '复盘整理中',
  completed: '复盘已生成',
  failed: '复盘生成失败',
};

const COMPLETION_STATUS_LABELS = {
  independent: '独立完成',
  assisted: '提示后完成',
  hinted: '提示后完成',
  partial: '做到一部分',
  unfinished: '还没做完',
  editorial: '看题解后完成',
  unknown: '不确定',
};

const SUBMISSION_RESULT_LABELS = {
  ac: '已通过 AC',
  accepted: '已通过 AC',
  wa: '答案错误 WA',
  tle: '运行超时 TLE',
  re: '运行错误 RE',
  ce: '编译错误 CE',
  pe: '格式错误 PE',
  not_submitted: '还没提交',
  unknown: '不确定',
};

const OJ_SOURCE_LABELS = {
  luogu: '洛谷',
  jm_oj: '校内 OJ',
  jm: '校内 OJ',
  local: '校内 OJ',
  other: '其他来源',
};

const QUIZ_ROLE_LABELS = {
  main: '主验证',
  followup: '追问验证',
  remedy: '补救小题',
  confirm: '迁移确认',
  knowledge_confirm: '知识确认',
  final_micro_confirm: '收尾验证',
};

const QUIZ_TYPE_LABELS = {
  judge_explain: '判断并解释',
  small_case_explain: '小样例迁移',
  trace_one_step: '手算一步',
  code_trace: '代码行为核对',
  find_counterexample: '错误辨析',
  complexity_estimate: '复杂度估算',
  self_explain: '用自己的话说',
};

function fallbackLabel(value) {
  return String(value || '').trim() || '—';
}

function reviewStatusLabel(value) {
  return REVIEW_STATUS_LABELS[value] || fallbackLabel(value);
}

function completionStatusLabel(value) {
  return COMPLETION_STATUS_LABELS[value] || fallbackLabel(value);
}

function submissionResultLabel(value) {
  return SUBMISSION_RESULT_LABELS[value] || fallbackLabel(value);
}

function ojSourceLabel(value) {
  return OJ_SOURCE_LABELS[value] || fallbackLabel(value);
}

function quizRoleLabel(value) {
  return QUIZ_ROLE_LABELS[value] || QUIZ_TYPE_LABELS[value] || fallbackLabel(value);
}

function escapeHtml(text) {
  return String(text || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderMath(expression, displayMode) {
  try {
    return katex.renderToString(expression.trim(), {
      displayMode,
      throwOnError: false,
      strict: 'ignore',
    });
  } catch {
    return `<code>${escapeHtml(expression)}</code>`;
  }
}

function renderMarkdownContent(source) {
  const text = String(source || '').trim();
  if (!text) return '';
  const mathHtml = [];
  const withBlockMath = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, expression) => {
    const token = `@@NOI_MATH_${mathHtml.length}@@`;
    mathHtml.push(renderMath(expression, true));
    return token;
  });
  const withInlineMath = withBlockMath.replace(/(^|[^$])\$([^$\n]+?)\$(?!\$)/g, (match, prefix, expression) => {
    const token = `@@NOI_MATH_${mathHtml.length}@@`;
    mathHtml.push(renderMath(expression, false));
    return `${prefix}${token}`;
  });
  let rendered = markdown.render(withInlineMath);
  mathHtml.forEach((html, index) => {
    rendered = rendered.replaceAll(`@@NOI_MATH_${index}@@`, html);
  });
  return rendered;
}

function looksLikePlainDiagram(text) {
  const lines = String(text || '').split('\n').map((line) => line.trimEnd()).filter(Boolean);
  if (lines.length < 2) return false;
  if (String(text).includes('```') || String(text).includes('|')) return false;
  const diagramLines = lines.filter((line) => /(\s{2,}|->|=>|≤|>=|<|>|\d+\s+\d+)/.test(line));
  return diagramLines.length >= 2;
}

function renderReviewSection(section) {
  const value = section?.value || '';
  if (section?.kind === 'example' && looksLikePlainDiagram(value)) {
    return `<pre>${escapeHtml(value)}</pre>`;
  }
  return renderMarkdownContent(value);
}

const reviewSummary = computed(() => {
  if (!detail.value) return [];
  return [
    { label: '当前进度', value: reviewStatusLabel(detail.value.review_status) },
    { label: '这次完成到哪', value: completionStatusLabel(detail.value.completion_status) },
    { label: '提交结果', value: submissionResultLabel(detail.value.submission_result) },
  ];
});

const reviewSections = computed(() => {
  const review = detail.value?.review;
  if (!review) return [];
  const topicCommonality = review.topic_commonality || [
    review.transfer_signal ? `**这类题的共性：**${review.transfer_signal}` : '',
    review.key_bridge ? `**回到这道题：**${review.key_bridge}` : '',
  ].filter(Boolean).join('\n\n');
  const solutionWalkthrough = review.solution_walkthrough || [
    review.key_bridge ? `**核心抓手：**${review.key_bridge}` : '',
    review.guided_walkthrough || '',
    review.visual_hint ? `**小例子 / 小图：**\n\n${review.visual_hint}` : '',
    review.problem_focus ? `**和我这次问题的关系：**${review.problem_focus}` : '',
  ].filter(Boolean).join('\n\n');
  const transferChecklist = review.transfer_checklist || [
    review.transfer_signal ? `**下次先看：**${review.transfer_signal}` : '',
    review.try_now ? `**现在验证：**${review.try_now}` : '',
  ].filter(Boolean).join('\n\n');
  return [
    { label: '这类题在考什么', value: topicCommonality, kind: 'text' },
    { label: '这道题怎么做通', value: solutionWalkthrough, kind: 'example' },
    { label: '下次怎么迁移', value: transferChecklist, kind: 'text' },
  ].filter((section) => section.value);
});

const nextAction = computed(() => {
  const review = detail.value?.review;
  if (review?.try_now) return review.try_now;
  const latestQuiz = (detail.value?.quiz_history || []).slice(-1)[0];
  if (latestQuiz?.question_text || latestQuiz?.question) {
    return latestQuiz.question_text || latestQuiz.question;
  }
  return '先回到上面的复盘链路，挑最靠近当前问题的那一步重新试一遍。';
});

function summarizeQuiz(quiz) {
  if (!quiz) return '';
  const label = quizRoleLabel(quiz.quiz_role || quiz.quiz_type || 'quiz');
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
          <p class="section-eyebrow text-archive-700">错题复盘</p>
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
            <p class="section-eyebrow text-archive-700">提交记录</p>
            <h4 class="mt-2 text-xl font-semibold text-slate-900">我当时是怎么提交的</h4>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-500">这次我哪里没想明白</p>
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
              <p class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{{ completionStatusLabel(detail.completion_status) }}</p>
            </div>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div>
              <p class="text-sm font-semibold text-slate-500">提交结果</p>
              <p class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{{ submissionResultLabel(detail.submission_result) }}</p>
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-500">来源</p>
              <p class="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{{ ojSourceLabel(detail.oj_source) }}</p>
            </div>
          </div>
          <section class="rounded-[24px] border border-archive-100 bg-white/70 p-4">
            <button
              class="flex w-full items-center justify-between gap-3 text-left text-sm font-semibold text-slate-600"
              type="button"
              @click="problemInfoOpen = !problemInfoOpen"
            >
              <span>题面 / 背景</span>
              <span class="rounded-full bg-archive-50 px-3 py-1 text-xs text-archive-800">
                {{ problemInfoOpen ? '收起题面' : '展开题面' }}
              </span>
            </button>
            <div
              v-if="problemInfoOpen"
              class="prose-content mt-3 max-w-none break-words text-sm leading-7 text-slate-700"
              v-html="renderMarkdownContent(detail.problem_context || '')"
            />
            <p v-else class="mt-2 text-xs leading-5 text-slate-500">题面较长时可以收起，先把注意力放在自己没想明白的地方。</p>
          </section>
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
            <p class="section-eyebrow text-archive-700">错题复盘</p>
            <h4 class="mt-2 text-xl font-semibold text-slate-900">把这题变成下次能用的经验</h4>
            <p class="mt-2 text-sm leading-7 text-slate-500">重点不是把 AI 的话抄下来，而是看清：我原来卡在哪，下次遇到同类题先抓哪一步。</p>
          </div>
          <div v-if="reviewSections.length" class="space-y-4">
            <div
              v-for="section in reviewSections"
              :key="section.label"
              class="rounded-[24px] border border-archive-100 bg-white/90 p-4"
            >
              <p class="text-sm font-semibold text-slate-500">{{ section.label }}</p>
              <div
                class="prose-content mt-2 max-w-none break-words text-sm leading-7 text-slate-700 [&_pre]:overflow-auto [&_pre]:rounded-2xl [&_pre]:bg-slate-950 [&_pre]:p-4 [&_pre]:font-mono [&_pre]:text-xs [&_pre]:leading-6 [&_pre]:text-slate-100 [&_table]:w-full [&_table]:border-collapse [&_td]:border [&_td]:border-slate-200 [&_td]:px-3 [&_td]:py-2 [&_th]:border [&_th]:border-slate-200 [&_th]:bg-slate-50 [&_th]:px-3 [&_th]:py-2"
                v-html="renderReviewSection(section)"
              />
            </div>
          </div>
          <div v-else class="rounded-[24px] border border-dashed border-archive-200 bg-white/80 p-4 text-sm leading-7 text-slate-600">
            <p class="font-semibold text-archive-800">系统正在整理复盘</p>
            <p class="mt-2">你已经提交成功了。复盘生成完成后，这里会显示“卡在哪里、关键一步、下次怎么认出来”。</p>
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
