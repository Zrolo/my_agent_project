<script setup>
import { computed, reactive, ref, watch } from 'vue';
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router';

import LoginView from '@/components/LoginView.vue';
import { defaultPathForRole, normalizePendingPath } from '@/router/routeAccess';
import { changeTeacherPassword } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const showPasswordDialog = ref(false);
const passwordSaving = ref(false);
const passwordError = ref('');
const passwordMessage = ref('');
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});

watch(
  () => auth.role,
  (role) => {
    if (!auth.isAuthenticated) return;
    if (role === 'student') {
      router.replace(defaultPathForRole('student'));
    }
  },
  { immediate: true },
);

const navItems = [
  { label: '首页', to: '/app/teacher/overview', section: 'overview' },
  { label: '学生', to: '/app/teacher/students', section: 'students' },
  { label: '复盘', to: '/app/teacher/reflection', section: 'reflection' },
  { label: '研究标注', to: '/app/teacher/research-annotation', section: 'research-annotation' },
  { label: '回复盲评', to: '/app/teacher/response-review', section: 'response-review' },
  { label: '班级管理', to: '/app/teacher/class-management', section: 'class-management' },
];

const heroConfig = computed(() => {
  const section = route.meta.section || 'overview';
  if (section === 'reflection') {
    return {
      accent: 'from-orange-500 via-rose-500 to-red-500',
      eyebrow: '复盘闭环',
      title: '复盘',
    };
  }
  if (section === 'class-management') {
    return {
      accent: 'from-slate-500 via-cyan-600 to-teal-600',
      eyebrow: '班级管理',
      title: '班级管理',
    };
  }
  if (section === 'students' || section === 'aichat-history') {
    return {
      accent: 'from-slate-500 via-cyan-600 to-teal-600',
      eyebrow: '学生与记录',
      title:
        section === 'students'
          ? '学生'
          : '学习记录',
    };
  }
  if (section === 'research-annotation' || section === 'response-review') {
    return {
      accent: 'from-emerald-600 via-cyan-600 to-sky-600',
      eyebrow: 'BridgeBench',
      title: section === 'response-review' ? '回复盲评' : '研究标注',
    };
  }
  return {
    accent: 'from-indigo-600 via-violet-600 to-fuchsia-500',
    eyebrow: '教师总览',
    title: '总览',
  };
});

function navClass(section) {
  const active = route.meta.section === section;
  return active ? 'nav-link nav-link-active-operator' : 'nav-link nav-link-idle';
}

function handleLoginSuccess(result) {
  if (result.role === 'student') {
    router.replace(defaultPathForRole('student'));
    return;
  }
  router.replace(normalizePendingPath(auth.pendingPath, result.role));
}

function handleLogout() {
  auth.logout();
  router.replace(defaultPathForRole('student'));
}

function resetPasswordForm() {
  passwordForm.current_password = '';
  passwordForm.new_password = '';
  passwordForm.confirm_password = '';
}

function openPasswordDialog() {
  passwordError.value = '';
  passwordMessage.value = '';
  resetPasswordForm();
  showPasswordDialog.value = true;
}

function closePasswordDialog() {
  if (passwordSaving.value) return;
  showPasswordDialog.value = false;
  passwordError.value = '';
  passwordMessage.value = '';
  resetPasswordForm();
}

async function handlePasswordChange() {
  passwordError.value = '';
  passwordMessage.value = '';
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = '两次输入的新密码不一致';
    return;
  }
  passwordSaving.value = true;
  try {
    const result = await changeTeacherPassword(auth.token, {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
      confirm_password: passwordForm.confirm_password,
    });
    resetPasswordForm();
    passwordMessage.value = result?.message || '密码已修改，请妥善保存新密码';
  } catch (error) {
    passwordError.value = error?.message || '修改密码失败，请稍后再试';
  } finally {
    passwordSaving.value = false;
  }
}
</script>

<template>
  <LoginView
    v-if="!auth.isAuthenticated || auth.role !== 'teacher'"
    required-role="teacher"
    title="进入教师工作台"
    description="登录后进入你的当前教师入口。"
    accent="from-violet-600 via-fuchsia-500 to-orange-500"
    @success="handleLoginSuccess"
  />

  <div v-else class="teacher-shell px-4 py-6 md:px-6 lg:px-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <header class="glass-nav p-4 md:p-5">
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div class="flex items-center gap-4">
            <div class="flex h-14 w-14 items-center justify-center rounded-[22px] bg-gradient-to-br from-violet-600 to-orange-500 text-2xl font-bold text-white shadow-lg shadow-violet-500/25">
              T
            </div>
            <div>
              <p class="text-sm font-semibold tracking-[0.18em] text-slate-400">教师端</p>
              <h1 class="font-display text-2xl font-bold text-slate-900">运营工作台</h1>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-3">
            <nav class="flex flex-wrap gap-2">
              <RouterLink
                v-for="item in navItems"
                :key="item.to"
                :class="navClass(item.section)"
                :to="item.to"
                :aria-current="route.meta.section === item.section ? 'page' : undefined"
              >
                {{ item.label }}
              </RouterLink>
            </nav>
            <div class="rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-600">
              {{ auth.userId }}
            </div>
            <button class="button-secondary" type="button" @click="openPasswordDialog">修改密码</button>
            <button class="button-secondary" type="button" @click="handleLogout">退出</button>
          </div>
        </div>
      </header>

      <div
        v-if="showPasswordDialog"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4"
        role="dialog"
        aria-modal="true"
        aria-label="修改密码"
        @click.self="closePasswordDialog"
      >
        <form class="w-full max-w-md rounded-[8px] bg-white p-5 shadow-xl" @submit.prevent="handlePasswordChange">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-sm font-semibold tracking-[0.16em] text-slate-400">账号安全</p>
              <h2 class="mt-1 text-xl font-bold text-slate-900">修改密码</h2>
              <p class="mt-1 text-sm text-slate-500">请输入当前密码，并自己设置新的登录密码。</p>
            </div>
            <button class="button-secondary px-3 py-1 text-sm" type="button" @click="closePasswordDialog">关闭</button>
          </div>

          <div class="mt-5 space-y-4">
            <label class="block">
              <span class="text-sm font-semibold text-slate-700">当前密码</span>
              <input
                v-model="passwordForm.current_password"
                class="mt-2 w-full rounded-[8px] border border-slate-200 px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-100"
                type="password"
                autocomplete="current-password"
                required
              >
            </label>
            <label class="block">
              <span class="text-sm font-semibold text-slate-700">新密码</span>
              <input
                v-model="passwordForm.new_password"
                class="mt-2 w-full rounded-[8px] border border-slate-200 px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-100"
                type="password"
                autocomplete="new-password"
                minlength="4"
                required
              >
            </label>
            <label class="block">
              <span class="text-sm font-semibold text-slate-700">确认新密码</span>
              <input
                v-model="passwordForm.confirm_password"
                class="mt-2 w-full rounded-[8px] border border-slate-200 px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-100"
                type="password"
                autocomplete="new-password"
                minlength="4"
                required
              >
            </label>
          </div>

          <p v-if="passwordError" class="mt-4 rounded-[8px] bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">
            {{ passwordError }}
          </p>
          <p v-if="passwordMessage" class="mt-4 rounded-[8px] bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">
            {{ passwordMessage }}
          </p>

          <div class="mt-5 flex justify-end gap-3">
            <button class="button-secondary" type="button" :disabled="passwordSaving" @click="closePasswordDialog">取消</button>
            <button class="button-primary" type="submit" :disabled="passwordSaving">
              {{ passwordSaving ? '正在修改...' : '保存新密码' }}
            </button>
          </div>
        </form>
      </div>

      <section :class="['hero-band bg-gradient-to-br', heroConfig.accent]">
        <p class="section-eyebrow text-white/75">{{ heroConfig.eyebrow }}</p>
        <div class="mt-4 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 class="font-display text-3xl font-bold leading-tight lg:text-4xl">{{ heroConfig.title }}</h2>
          </div>
          <div class="rounded-full border border-white/20 bg-white/15 px-4 py-2 text-sm font-semibold text-white/90">
            {{ auth.userId }}
          </div>
        </div>
      </section>

      <RouterView />
    </div>
  </div>
</template>
