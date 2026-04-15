<script setup>
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  COMPLETION_STATUS_OPTIONS,
  SUBMISSION_RESULT_OPTIONS,
  inferOjSourceFromProblemRef,
  normalizeCheckinPayload,
  ojSourceLabel,
} from '@/constants/checkinOptions';
import { createCheckin } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const router = useRouter();

const errorOptions = ['方法选择', '状态设计', '转移设计', '二分边界', '判定函数', '数据结构语义'];

const form = reactive({
  oj_source: 'other',
  problem_url: window.localStorage.getItem('noi-agent-chat-problem-id') || '',
  problem_title: window.localStorage.getItem('noi-agent-chat-problem-title') || '',
  problem_context: window.localStorage.getItem('noi-agent-chat-problem-context') || '',
  completion_status: 'unfinished',
  bottleneck_text: '',
  reflection: '',
  submission_result: 'not_submitted',
  student_code: window.localStorage.getItem('noi-agent-chat-student-code') || '',
  error_types: [],
});

const loading = ref(false);
const successMessage = ref('');
const error = ref('');
const detectedOjSource = computed(() => inferOjSourceFromProblemRef(form.problem_url));
const HANDOFF_PAYLOAD_KEY = 'noi-agent-chat-handoff-payload';

function loadHandoffPayload() {
  const raw = window.localStorage.getItem(HANDOFF_PAYLOAD_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    return parsed && parsed.source === 'aichat' ? parsed : null;
  } catch {
    return null;
  }
}

const handoffPayload = ref(loadHandoffPayload());
const chatContextSummary = computed(() => {
  if (!handoffPayload.value) return '';
  const focus = handoffPayload.value.suggested_focus || 'AIChat 建议转打卡复盘';
  const lastMessage = handoffPayload.value.last_user_message || '';
  return [focus, lastMessage].filter(Boolean).join('；');
});

function toggleError(option) {
  if (form.error_types.includes(option)) {
    form.error_types = form.error_types.filter((item) => item !== option);
    return;
  }
  form.error_types = [...form.error_types, option];
}

function resetOptionalFields() {
  form.problem_context = '';
  form.submission_result = 'not_submitted';
  form.student_code = '';
  form.error_types = [];
}

async function submit() {
  loading.value = true;
  error.value = '';
  successMessage.value = '';
  try {
    const result = await createCheckin(auth.token, {
      ...normalizeCheckinPayload(form),
      chat_context_summary: chatContextSummary.value,
      problem_tags: [],
      handoff_payload: handoffPayload.value,
    });
    successMessage.value = result.message;
    router.push(`/app/archive/${result.checkin_id}`);
  } catch (err) {
    error.value = err.message || '提交失败，请稍后重试';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="grid gap-6 xl:grid-cols-[0.72fr_1.28fr]">
    <section class="panel workspace-card-checkin space-y-5">
      <div>
        <p class="section-eyebrow text-checkin-700">Check-in Flow</p>
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">先把这次卡点记清楚，系统再帮你往下带。</h3>
        <p class="mt-3 text-sm leading-7 text-slate-600">
          最关键的是三件事：这道题是谁、你卡在哪里、你已经试过什么。剩下的信息可以按需要再补。
        </p>
      </div>
      <div class="grid gap-4 md:grid-cols-2">
        <div class="metric-tile">
          <p class="text-sm text-slate-400">先写什么</p>
          <p class="mt-2 text-lg font-semibold text-slate-900">题目、卡点、已尝试思路</p>
        </div>
        <div class="metric-tile">
          <p class="text-sm text-slate-400">提交后会发生什么</p>
          <p class="mt-2 text-lg font-semibold text-slate-900">AI 复盘 -> 历史详情</p>
        </div>
      </div>
      <div class="rounded-[24px] border border-dashed border-checkin-200 bg-white/70 p-4 text-sm leading-7 text-slate-600">
        不需要一次把所有信息都填满。主区先把“这题是谁、我卡在哪、我试过什么”说清楚，就已经足够开始复盘。
      </div>
    </section>

    <section class="panel workspace-card-checkin">
      <div class="mb-5">
        <p class="section-eyebrow text-checkin-700">Submission Form</p>
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">打卡复盘提交</h3>
      </div>
      <form class="space-y-4" @submit.prevent="submit">
        <div class="grid gap-4 md:grid-cols-2">
          <div>
            <label for="checkin-problem" class="mb-2 block text-sm font-semibold text-slate-600">题目链接 / 题号</label>
            <input
              id="checkin-problem"
              v-model="form.problem_url"
              class="field"
              placeholder="例如 P2922 或洛谷链接"
            />
            <p class="mt-2 text-xs leading-5 text-slate-500">
              {{ ojSourceLabel(detectedOjSource) }}。洛谷题号/链接可自动读取；其他平台请补题目标题和题面。
            </p>
          </div>
          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-600">题目标题</label>
            <input v-model="form.problem_title" class="field" placeholder="没有链接时请补标题" />
          </div>
        </div>
        <div>
          <label for="checkin-bottleneck" class="mb-2 block text-sm font-semibold text-slate-600">我卡在哪里</label>
          <textarea
            id="checkin-bottleneck"
            v-model="form.bottleneck_text"
            class="field min-h-32 resize-y"
            placeholder="尽量写成一句具体的话，例如：我不知道 check(mid) 返回 true 时区间应该往哪边缩。"
          />
        </div>
        <div>
          <label for="checkin-reflection" class="mb-2 block text-sm font-semibold text-slate-600">我已经试过什么</label>
          <textarea
            id="checkin-reflection"
            v-model="form.reflection"
            class="field min-h-28 resize-y"
            placeholder="写你试过的思路、你为什么觉得它不对，或者你已经写到哪一步。"
          />
        </div>
        <details class="rounded-[28px] border border-checkin-100 bg-white/70 p-4">
          <summary class="cursor-pointer list-none text-sm font-semibold text-checkin-700">
            补充信息（可选）
          </summary>
          <div class="mt-4 space-y-4">
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-600">完成状态</label>
                <select v-model="form.completion_status" class="field">
                  <option
                    v-for="option in COMPLETION_STATUS_OPTIONS"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>
              <div>
                <label class="mb-2 block text-sm font-semibold text-slate-600">提交结果</label>
                <select v-model="form.submission_result" class="field">
                  <option
                    v-for="option in SUBMISSION_RESULT_OPTIONS"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>
            </div>
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-600">题面 / 关键背景</label>
              <textarea v-model="form.problem_context" class="field min-h-28 resize-y" placeholder="如果题面里有关键数据范围、限制条件，贴在这里会更有帮助。"/>
            </div>
            <div>
              <p class="mb-3 text-sm font-semibold text-slate-600">如果你愿意，也可以补充卡点标签</p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="option in errorOptions"
                  :key="option"
                  :class="form.error_types.includes(option) ? 'tag-pill bg-checkin-500 text-white' : 'tag-pill bg-slate-100 text-slate-600'"
                  type="button"
                  @click="toggleError(option)"
                >
                  {{ option }}
                </button>
              </div>
            </div>
            <div>
              <label class="mb-2 block text-sm font-semibold text-slate-600">相关代码（可选）</label>
              <textarea v-model="form.student_code" class="field min-h-32 resize-y font-mono text-xs" placeholder="如果这次卡点和代码实现有关，再把代码贴进来。"/>
            </div>
            <button class="button-secondary w-full" type="button" @click="resetOptionalFields">清空补充信息</button>
          </div>
        </details>
        <p v-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
        <p v-if="successMessage" class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">{{ successMessage }}</p>
        <button class="button-primary w-full bg-gradient-to-r from-checkin-500 via-amber-500 to-orange-500" :disabled="loading" type="submit">
          {{ loading ? '正在提交...' : '提交并进入复盘详情' }}
        </button>
      </form>
    </section>
  </div>
</template>
