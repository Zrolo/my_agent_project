<script setup>
import { computed, ref } from 'vue';

import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  requiredRole: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  accent: {
    type: String,
    default: 'from-chat-500 to-archive-500',
  },
});

const emit = defineEmits(['success']);

const auth = useAuthStore();

const userId = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

const roleLabel = computed(() => (props.requiredRole === 'teacher' ? '教师' : '学生'));

async function handleSubmit() {
  loading.value = true;
  error.value = '';
  try {
    const result = await auth.login({
      user_id: userId.value.trim(),
      password: password.value,
    });
    emit('success', result);
  } catch (err) {
    error.value = err.message || '登录失败，请稍后重试';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-100 px-4 py-10">
    <div class="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <section :class="['hero-band bg-gradient-to-br', accent]">
        <p class="mb-3 text-sm font-semibold uppercase tracking-[0.24em] text-white/75">NOI Agent</p>
        <h1 class="font-display text-4xl font-bold leading-tight">
          {{ title }}
        </h1>
        <p class="mt-4 max-w-2xl text-base leading-7 text-white/88">
          {{ description }}
        </p>
        <div class="mt-8 grid gap-4 md:grid-cols-3">
          <div class="rounded-3xl bg-white/15 p-4">
            <p class="text-sm text-white/75">状态</p>
            <p class="mt-2 text-lg font-semibold">整站 Vue 新壳</p>
          </div>
          <div class="rounded-3xl bg-white/15 p-4">
            <p class="text-sm text-white/75">当前入口</p>
            <p class="mt-2 text-lg font-semibold">{{ roleLabel }}工作台</p>
          </div>
          <div class="rounded-3xl bg-white/15 p-4">
            <p class="text-sm text-white/75">体验目标</p>
            <p class="mt-2 text-lg font-semibold">稳定路由 + 更清楚页面壳层</p>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="mb-6">
          <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">{{ roleLabel }}登录</p>
          <h2 class="mt-2 font-display text-3xl font-bold text-slate-900">进入新的工作台</h2>
          <p class="mt-3 text-sm leading-6 text-slate-500">
            我们会保留你当前的目标页面，登录成功后直接回到它，不再把你带去错页。
          </p>
        </div>

        <form class="space-y-4" @submit.prevent="handleSubmit">
          <div>
            <label for="login-user-id" class="mb-2 block text-sm font-semibold text-slate-600">账号</label>
            <input
              id="login-user-id"
              v-model="userId"
              class="field"
              autocomplete="username"
              placeholder="请输入 user_id"
              required
            />
          </div>
          <div>
            <label for="login-password" class="mb-2 block text-sm font-semibold text-slate-600">密码</label>
            <input
              id="login-password"
              v-model="password"
              class="field"
              type="password"
              autocomplete="current-password"
              placeholder="请输入密码"
              required
            />
          </div>
          <p v-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
            {{ error }}
          </p>
          <button
            :class="['button-primary w-full bg-gradient-to-r', accent]"
            :disabled="loading"
            type="submit"
          >
            <span v-if="loading">正在登录...</span>
            <span v-else>进入{{ roleLabel }}工作台</span>
          </button>
        </form>
      </section>
    </div>
  </div>
</template>
