<script setup>
import { reactive, ref } from 'vue';

import { submitStudentFeedback } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const message = ref('');
const error = ref('');

const form = reactive({
  category: 'aichat',
  rating: 5,
  content: '',
});

const categoryOptions = [
  { value: 'aichat', label: 'AIChat 对话' },
  { value: 'checkin', label: '深入复盘' },
  { value: 'code', label: '代码编辑 / 运行' },
  { value: 'page', label: '页面使用' },
  { value: 'other', label: '其他建议' },
];

async function submit() {
  error.value = '';
  message.value = '';
  const content = form.content.trim();
  if (content.length < 5) {
    error.value = '至少写 5 个字，老师才能看懂你的具体感受。';
    return;
  }
  loading.value = true;
  try {
    const result = await submitStudentFeedback(auth.token, {
      category: form.category,
      rating: Number(form.rating),
      content,
      page_context: window.location.pathname,
    });
    message.value = result.message || '反馈已提交，谢谢你告诉我们真实感受。';
    form.content = '';
    form.rating = 5;
    form.category = 'aichat';
  } catch (err) {
    error.value = err.message || '提交反馈失败，请稍后再试。';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="space-y-6">
    <section class="panel mx-auto w-full max-w-4xl">
      <div class="mb-6">
        <p class="section-eyebrow text-cyan-700">反馈建议</p>
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">告诉老师哪里好用，哪里不好用</h3>
        <p class="mt-3 text-sm leading-7 text-slate-500">
          你可以写 AIChat、深入复盘、代码区或页面使用的问题。真实反馈会帮助我们把系统改得更适合你。
        </p>
      </div>

      <form class="space-y-5" @submit.prevent="submit">
        <div class="grid gap-4 md:grid-cols-2">
          <label class="block">
            <span class="text-sm font-semibold text-slate-700">这次想反馈什么</span>
            <select v-model="form.category" class="field mt-2">
              <option v-for="option in categoryOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
          <label class="block">
            <span class="text-sm font-semibold text-slate-700">整体感受</span>
            <select v-model="form.rating" class="field mt-2">
              <option :value="5">很好用</option>
              <option :value="4">比较好用</option>
              <option :value="3">一般</option>
              <option :value="2">有点不好用</option>
              <option :value="1">很影响使用</option>
            </select>
          </label>
        </div>

        <label class="block">
          <span class="text-sm font-semibold text-slate-700">反馈内容</span>
          <textarea
            v-model="form.content"
            class="field mt-2 min-h-44 resize-y"
            placeholder="例如：AIChat 有时候一直反问，我希望它先解释我上一句哪里对、哪里还差一点。至少写 5 个字。"
          />
        </label>

        <p v-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
        <p v-if="message" class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">{{ message }}</p>

        <button class="button-primary w-full" :disabled="loading" type="submit">
          {{ loading ? '正在提交...' : '提交反馈' }}
        </button>
      </form>
    </section>
  </div>
</template>
