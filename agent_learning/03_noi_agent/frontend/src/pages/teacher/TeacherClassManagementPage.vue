<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import TeacherAccountsPage from '@/pages/teacher/TeacherAccountsPage.vue';
import TeacherAdvancedPage from '@/pages/teacher/TeacherAdvancedPage.vue';
import TeacherAnnouncementsPage from '@/pages/teacher/TeacherAnnouncementsPage.vue';
import TeacherFeedbackPage from '@/pages/teacher/TeacherFeedbackPage.vue';

const route = useRoute();
const router = useRouter();

const tabs = [
  { key: 'accounts', label: '学生账号', description: '创建账号、重置密码、停用或启用学生。' },
  { key: 'announcements', label: '公告', description: '发布学生首页公告和查看历史公告。' },
  { key: 'feedback', label: '学生反馈', description: '查看学生主动提交的使用问题和建议。' },
  { key: 'advanced', label: '系统维护', description: '查看低频系统排查、规则草稿和旧统计。' },
];

const activeTab = computed(() => {
  if (route.query.tab === 'announcements') return 'announcements';
  if (route.query.tab === 'feedback') return 'feedback';
  if (route.query.tab === 'advanced') return 'advanced';
  return 'accounts';
});

function switchTab(tab) {
  router.replace({ path: '/app/teacher/class-management', query: { tab } });
}
</script>

<template>
  <div class="space-y-5">
    <section class="panel">
      <p class="section-eyebrow text-cyan-700">班级管理</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">账号、公告、反馈与维护</h3>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
        这里放低频管理动作；日常带班从首页、学生和复盘进入，系统维护也藏在这里。
      </p>
      <div class="mt-5 flex flex-wrap gap-2">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          :class="[
            'rounded-[8px] border px-4 py-3 text-left transition',
            activeTab === tab.key ? 'border-cyan-300 bg-cyan-50 text-cyan-800' : 'border-slate-200 bg-white text-slate-600 hover:border-cyan-200',
          ]"
          @click="switchTab(tab.key)"
        >
          <span class="block text-sm font-bold">{{ tab.label }}</span>
          <span class="mt-1 block text-xs">{{ tab.description }}</span>
        </button>
      </div>
    </section>

    <TeacherAccountsPage v-if="activeTab === 'accounts'" />
    <TeacherAnnouncementsPage v-else-if="activeTab === 'announcements'" />
    <TeacherFeedbackPage v-else-if="activeTab === 'feedback'" />
    <TeacherAdvancedPage v-else />
  </div>
</template>
