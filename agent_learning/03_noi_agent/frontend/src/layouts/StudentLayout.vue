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
    if (role === 'teacher') {
      router.replace('/app/teacher/overview');
    }
  },
  { immediate: true },
);

const navItems = [
  { label: '首页', to: '/app/home', section: 'home' },
  { label: 'AI 解答', to: '/app/workspace/chat', section: 'chat' },
  { label: '学习记录', to: '/app/workspace/checkin', section: 'checkin' },
  { label: '使用反馈', to: '/app/workspace/feedback', section: 'feedback' },
];

const heroConfig = computed(() => {
  const section = route.meta.section || 'chat';
  if (section === 'home') {
    return {
      accent: 'from-cyan-500 via-sky-500 to-emerald-500',
      eyebrow: 'Home',
      title: '首页',
    };
  }
  if (section === 'checkin') {
    return {
      accent: 'from-checkin-500 via-amber-400 to-orange-600',
      eyebrow: 'Learning Records',
      title: '学习记录',
    };
  }
  if (section === 'archive') {
    return {
      accent: 'from-archive-500 via-violet-500 to-fuchsia-500',
      eyebrow: 'Archive Deck',
      title: '历史记录',
    };
  }
  if (section === 'knowledge') {
    return {
      accent: 'from-emerald-500 via-sky-500 to-cyan-500',
      eyebrow: 'Knowledge Bridge',
      title: '知识补全',
    };
  }
  if (section === 'feedback') {
    return {
      accent: 'from-emerald-500 via-cyan-500 to-sky-500',
      eyebrow: 'Feedback',
      title: '使用反馈',
    };
  }
  return {
    accent: 'from-sky-500 via-cyan-500 to-teal-500',
    eyebrow: 'Workspace',
    title: 'AI 解答',
  };
});

const showHero = computed(() => route.meta.section !== 'chat');

function navClass(section) {
  const active = route.meta.section === section;
  if (!active) return 'nav-link nav-link-idle';
  if (section === 'checkin') return 'nav-link nav-link-active-checkin';
  if (section === 'archive') return 'nav-link nav-link-active-archive';
  if (section === 'knowledge') return 'nav-link nav-link-active-knowledge';
  if (section === 'feedback') return 'nav-link nav-link-active-chat';
  if (section === 'home') return 'nav-link nav-link-active-chat';
  return 'nav-link nav-link-active-chat';
}

function handleLoginSuccess(result) {
  if (result.role === 'teacher') {
    router.replace(defaultPathForRole('teacher'));
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
    v-if="!auth.isAuthenticated || auth.role !== 'student'"
    required-role="student"
    title="进入学生工作台"
    description="登录后进入你的当前学习入口。"
    accent="from-sky-500 via-cyan-500 to-indigo-500"
    @success="handleLoginSuccess"
  />

  <div v-else class="app-shell px-4 py-6 md:px-6 lg:px-8">
    <div :class="['mx-auto flex max-w-7xl flex-col', showHero ? 'gap-6' : 'gap-4']">
      <header class="glass-nav p-4 md:p-5">
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div class="flex items-center gap-4">
            <div class="flex h-14 w-14 items-center justify-center rounded-[22px] bg-gradient-to-br from-sky-500 to-indigo-500 text-2xl font-bold text-white shadow-lg shadow-sky-500/25">
              N
            </div>
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.26em] text-slate-400">NOI Agent Student</p>
              <h1 class="font-display text-2xl font-bold text-slate-900">竞赛学习工作台</h1>
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

      <section v-if="showHero" :class="['hero-band bg-gradient-to-br', heroConfig.accent]">
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
