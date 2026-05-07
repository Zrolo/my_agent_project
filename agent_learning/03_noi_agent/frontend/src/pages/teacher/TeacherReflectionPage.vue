<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import TeacherCheckinsPage from '@/pages/teacher/TeacherCheckinsPage.vue';
import TeacherReviewPage from '@/pages/teacher/TeacherReviewPage.vue';

const route = useRoute();
const router = useRouter();

const tabs = [
  { key: 'review', label: '教学复盘', description: '先看复盘是否靠谱、学生卡在哪里；包含待人工复核。' },
  { key: 'checkins', label: '复盘生成队列', description: '像 OJ 评测队列一样，只用于排查生成中、失败或题目信息缺失。' },
];

const activeTab = computed(() => (route.query.tab === 'checkins' ? 'checkins' : 'review'));

function switchTab(tab) {
  router.replace({ path: '/app/teacher/reflection', query: { tab } });
}
</script>

<template>
  <div class="space-y-5">
    <section class="panel">
      <p class="section-eyebrow text-orange-600">复盘</p>
      <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">学生复盘与人工复核</h3>
      <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
        默认看教学复盘：学生这次没想明白什么、系统怎么帮了一步、是否需要老师介入。
        原始打卡只作为复盘生成队列保留，排查生成状态时再看。
      </p>
      <div class="mt-5 flex flex-wrap gap-2">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          :class="[
            'rounded-[8px] border px-4 py-3 text-left transition',
            activeTab === tab.key ? 'border-orange-300 bg-orange-50 text-orange-800' : 'border-slate-200 bg-white text-slate-600 hover:border-orange-200',
          ]"
          @click="switchTab(tab.key)"
        >
          <span class="block text-sm font-bold">{{ tab.label }}</span>
          <span class="mt-1 block text-xs">{{ tab.description }}</span>
        </button>
      </div>
    </section>

    <TeacherCheckinsPage v-if="activeTab === 'checkins'" />
    <TeacherReviewPage v-else />
  </div>
</template>
