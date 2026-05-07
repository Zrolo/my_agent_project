<script setup>
import MarkdownIt from 'markdown-it';
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';

import { getStudentHome } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const home = ref(null);

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});

const announcementHtml = computed(() => {
  const body = home.value?.announcement?.body_markdown || '';
  return body ? md.render(body) : '';
});

const stats = computed(() => home.value?.stats || []);
const primaryStats = computed(() => stats.value.slice(0, 4));
const continueLearning = computed(() => home.value?.continue_learning || null);
const bottlenecks = computed(() => home.value?.recent_bottlenecks || []);
const reminders = computed(() => home.value?.review_reminders || []);
const completionSummary = computed(() => home.value?.completion_summary || null);
const recentCompletions = computed(() => home.value?.recent_completions || []);

async function loadHome() {
  loading.value = true;
  error.value = '';
  try {
    home.value = await getStudentHome(auth.token);
  } catch (err) {
    error.value = err.message || '加载首页失败，请稍后再试。';
  } finally {
    loading.value = false;
  }
}

onMounted(loadHome);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">今日入口</p>
          <h2 class="mt-2 font-display text-3xl font-bold text-slate-900">先看一眼，再开始做题</h2>
          <p class="mt-2 max-w-2xl text-sm leading-7 text-slate-500">
            这里放老师提醒、你最近的学习状态和下一步，不需要翻很多页面。
          </p>
        </div>
        <button class="button-secondary self-start" type="button" @click="loadHome">
          {{ loading ? '刷新中...' : '刷新首页' }}
        </button>
      </div>
    </section>

    <section v-if="error" class="panel rounded-2xl bg-rose-50 text-sm font-medium text-rose-700">{{ error }}</section>

    <section class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <article class="panel">
        <p class="section-eyebrow text-cyan-700">教师公告</p>
        <template v-if="home?.announcement">
          <h3 class="mt-3 font-display text-2xl font-bold text-slate-900">{{ home.announcement.title }}</h3>
          <div class="mt-4 max-w-none text-sm leading-7 text-slate-700 [&_a]:text-cyan-700 [&_li]:ml-5 [&_li]:list-disc [&_strong]:font-bold" v-html="announcementHtml" />
        </template>
        <div v-else class="mt-4 rounded-[24px] border border-dashed border-cyan-200 bg-cyan-50/50 p-5 text-sm leading-7 text-slate-500">
          暂无公告。可以直接进入 AIChat 开始今天的题目。
        </div>
      </article>

      <article class="panel">
        <p class="section-eyebrow text-emerald-700">继续学习</p>
        <template v-if="continueLearning">
          <h3 class="mt-3 font-display text-2xl font-bold text-slate-900">{{ continueLearning.title }}</h3>
          <p class="mt-3 text-sm leading-7 text-slate-600">{{ continueLearning.description }}</p>
          <RouterLink class="button-primary mt-5 inline-flex" :to="continueLearning.action_path">
            {{ continueLearning.action_label }}
          </RouterLink>
        </template>
      </article>
    </section>

    <section>
      <div class="mb-4 px-1">
        <p class="section-eyebrow text-slate-500">我的学习数据</p>
      </div>
      <div class="grid gap-4 md:grid-cols-4">
        <article v-for="item in primaryStats" :key="item.label" class="metric-tile">
          <p class="text-sm text-slate-400">{{ item.label }}</p>
          <p class="mt-2 text-3xl font-bold text-slate-900">{{ item.value }}</p>
        </article>
      </div>
    </section>

    <section>
      <article class="panel">
        <p class="section-eyebrow text-cyan-700">最近做完的题</p>
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">这段时间完成了哪些题</h3>
        <template v-if="completionSummary">
          <div class="mt-5 grid gap-3 sm:grid-cols-3">
            <div class="rounded-[20px] border border-cyan-100 bg-cyan-50/50 p-4">
              <p class="text-xs text-slate-500">近 15 天做题记录</p>
              <p class="mt-2 text-2xl font-bold text-slate-900">{{ completionSummary.last_15_days }}</p>
            </div>
            <div class="rounded-[20px] border border-emerald-100 bg-emerald-50/50 p-4">
              <p class="text-xs text-slate-500">自己做出来</p>
              <p class="mt-2 text-2xl font-bold text-slate-900">{{ completionSummary.self_solved_15_days }}</p>
            </div>
            <div class="rounded-[20px] border border-amber-100 bg-amber-50/50 p-4">
              <p class="text-xs text-slate-500">借助 AI 后做出</p>
              <p class="mt-2 text-2xl font-bold text-slate-900">{{ completionSummary.aichat_assisted_15_days }}</p>
            </div>
          </div>
          <p class="mt-4 rounded-[20px] border border-slate-100 bg-slate-50 p-4 text-sm leading-7 text-slate-600">
            {{ completionSummary.support_trend }}
          </p>
          <div class="mt-3 rounded-[20px] border border-emerald-100 bg-emerald-50/50 p-4">
            <p class="text-xs font-semibold text-emerald-700">完成方式变化</p>
            <p class="mt-2 text-sm leading-7 text-slate-600">{{ completionSummary.support_fadeout_label }}</p>
          </div>
        </template>
        <div v-if="recentCompletions.length" class="mt-4 space-y-3">
          <article v-for="item in recentCompletions" :key="item.id" class="rounded-[20px] border border-white bg-white/80 p-4">
            <p class="font-semibold text-slate-900">{{ item.problem_title || item.problem_id || '未命名题目' }}</p>
            <p v-if="item.points_awarded" class="mt-2 inline-flex rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
              +{{ item.points_awarded }} 积分
            </p>
            <p class="mt-2 text-sm leading-6 text-slate-600">你写的是：{{ item.key_step_summary || '还没有补充关键做法' }}</p>
            <p class="mt-1 text-sm leading-6 text-slate-500">还可以补一句：为什么这一步是这题的关键？</p>
            <p class="mt-2 text-xs text-slate-400">{{ item.confidence_note }}</p>
          </article>
        </div>
      </article>
    </section>

    <section class="grid gap-6 lg:grid-cols-2">
      <article class="panel">
        <p class="section-eyebrow text-cyan-700">最近需要多练的地方</p>
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">问 AI 或复盘时经常出现的问题</h3>
        <div v-if="bottlenecks.length" class="mt-5 flex flex-wrap gap-3">
          <span v-for="item in bottlenecks" :key="item.label" class="tag-pill bg-cyan-50 text-cyan-700">
            {{ item.label }} × {{ item.count }}
          </span>
        </div>
        <p v-else class="mt-5 text-sm leading-7 text-slate-500">还没有记录。先做一道题，有问题就问 AIChat。</p>
      </article>

      <article class="panel">
        <p class="section-eyebrow text-emerald-700">建议回顾的题</p>
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">这些题可以再看一眼</h3>
        <div v-if="reminders.length" class="mt-5 space-y-3">
          <RouterLink
            v-for="item in reminders"
            :key="`${item.title}-${item.next_review_at}`"
            class="block rounded-[24px] border border-emerald-100 bg-emerald-50/50 p-4 transition hover:border-emerald-300"
            :to="item.action_path"
          >
            <p class="font-semibold text-slate-900">{{ item.title }}</p>
            <p class="mt-1 text-sm leading-6 text-slate-600">{{ item.description }}</p>
          </RouterLink>
        </div>
        <p v-else class="mt-5 text-sm leading-7 text-slate-500">暂无需要回顾的题。完成验证后，这里会出现提醒。</p>
      </article>
    </section>
  </div>
</template>
