<script setup>
import { onMounted, reactive, ref } from 'vue';

import { createTeacherAnnouncement, getTeacherAnnouncements } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const saving = ref(false);
const error = ref('');
const message = ref('');
const announcements = ref([]);

const form = reactive({
  title: '',
  body_markdown: '',
  pinned: true,
});

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

async function loadAnnouncements() {
  loading.value = true;
  error.value = '';
  try {
    const result = await getTeacherAnnouncements(auth.token, { limit: 30 });
    announcements.value = result.announcements || [];
  } catch (err) {
    error.value = err.message || '加载公告失败';
  } finally {
    loading.value = false;
  }
}

async function submitAnnouncement() {
  error.value = '';
  message.value = '';
  if (!form.title.trim()) {
    error.value = '请填写公告标题';
    return;
  }
  if (!form.body_markdown.trim()) {
    error.value = '请填写公告内容';
    return;
  }
  saving.value = true;
  try {
    await createTeacherAnnouncement(auth.token, {
      title: form.title.trim(),
      body_markdown: form.body_markdown.trim(),
      pinned: form.pinned,
      status: 'published',
    });
    message.value = '公告已发布，学生首页会看到。';
    form.title = '';
    form.body_markdown = '';
    form.pinned = true;
    await loadAnnouncements();
  } catch (err) {
    error.value = err.message || '发布公告失败';
  } finally {
    saving.value = false;
  }
}

onMounted(loadAnnouncements);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">公告管理</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">发布学生首页公告</h3>
          <p class="mt-2 text-sm leading-7 text-slate-500">
            支持 Markdown。建议只写本周训练安排、注意事项和下一步重点，别把首页写得太满。
          </p>
        </div>
        <button class="button-secondary self-start" type="button" @click="loadAnnouncements">
          {{ loading ? '刷新中...' : '刷新公告' }}
        </button>
      </div>
    </section>

    <section class="panel">
      <form class="space-y-5" @submit.prevent="submitAnnouncement">
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">公告标题</span>
          <input v-model="form.title" class="field mt-2" placeholder="例如：本周最短路训练安排" />
        </label>

        <label class="block">
          <span class="text-sm font-semibold text-slate-700">公告内容（Markdown）</span>
          <textarea
            v-model="form.body_markdown"
            class="field mt-2 min-h-56 resize-y"
            placeholder="例如：&#10;## 本周重点&#10;- 先复习 Floyd 的逐步放点思想&#10;- 完成 P1119 后做一道同类题"
          />
        </label>

        <label class="inline-flex items-center gap-2 text-sm font-semibold text-slate-600">
          <input v-model="form.pinned" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-cyan-600" />
          置顶显示
        </label>

        <p v-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
        <p v-if="message" class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">{{ message }}</p>

        <button class="button-primary w-full" :disabled="saving" type="submit">
          {{ saving ? '正在发布...' : '发布公告' }}
        </button>
      </form>
    </section>

    <section class="panel">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="section-eyebrow text-cyan-700">历史公告</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">最近发布</h3>
        </div>
      </div>

      <div v-if="announcements.length" class="mt-5 space-y-3">
        <article v-for="item in announcements" :key="item.id" class="rounded-[24px] border border-cyan-100 bg-white/80 p-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <h4 class="font-bold text-slate-900">{{ item.title }}</h4>
            <span class="tag-pill bg-cyan-50 text-cyan-700">{{ item.pinned ? '置顶' : '普通' }}</span>
          </div>
          <p class="mt-2 text-xs text-slate-400">{{ formatTime(item.published_at || item.created_at) }}</p>
          <p class="mt-3 line-clamp-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ item.body_markdown }}</p>
        </article>
      </div>
      <p v-else class="mt-5 text-sm text-slate-500">暂无公告</p>
    </section>
  </div>
</template>
