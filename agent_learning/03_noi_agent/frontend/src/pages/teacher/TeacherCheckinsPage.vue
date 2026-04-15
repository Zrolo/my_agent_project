<script setup>
import { onMounted, ref } from 'vue';

import { getTeacherCheckins } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const checkins = ref([]);

async function loadCheckins() {
  loading.value = true;
  error.value = '';
  try {
    const result = await getTeacherCheckins(auth.token);
    checkins.value = result.checkins || [];
  } catch (err) {
    error.value = err.message || '加载打卡记录失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadCheckins);
</script>

<template>
  <div class="space-y-6">
    <section class="panel workspace-card-operator">
      <div class="flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">Checkins</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">打卡记录</h3>
        </div>
        <button class="button-secondary" type="button" @click="loadCheckins">刷新</button>
      </div>
    </section>

    <section v-if="loading" class="panel text-sm text-slate-500">正在加载打卡记录...</section>
    <section v-else-if="error" class="panel rounded-2xl bg-rose-50 text-sm font-medium text-rose-700">{{ error }}</section>
    <section v-else-if="checkins.length === 0" class="panel border-dashed border-cyan-200 bg-cyan-50/50 text-sm text-slate-600">
      暂无打卡记录
    </section>
    <section v-else class="space-y-4">
      <article v-for="item in checkins" :key="item.checkin_id" class="panel workspace-card-operator">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-700">Checkin #{{ item.checkin_id }}</p>
            <h4 class="mt-2 text-lg font-semibold text-slate-900">{{ item.problem_title }}</h4>
            <p class="mt-2 text-sm text-slate-500">{{ item.student_id }} · {{ item.problem_url || '无题目链接' }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span class="tag-pill bg-slate-100 text-slate-700">{{ item.review_status || 'pending' }}</span>
            <span class="tag-pill bg-slate-100 text-slate-700">{{ item.completion_status || 'unfinished' }}</span>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>
