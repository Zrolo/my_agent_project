<script setup>
import { computed, watch } from 'vue';
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router';

import LoginView from '@/components/LoginView.vue';
import { defaultPathForRole, normalizePendingPath } from '@/router/routeAccess';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

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
  if (section === 'research-annotation') {
    return {
      accent: 'from-emerald-600 via-cyan-600 to-sky-600',
      eyebrow: 'BridgeBench',
      title: '研究标注',
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
            <button class="button-secondary" type="button" @click="handleLogout">退出</button>
          </div>
        </div>
      </header>

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
