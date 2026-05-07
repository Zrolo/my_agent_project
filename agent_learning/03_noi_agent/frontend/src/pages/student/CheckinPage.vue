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
import { createCheckin, createStudentProblemCompletion } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const router = useRouter();

const errorOptions = ['方法选择', '状态设计', '转移设计', '二分边界', '判定函数', '数据结构语义'];
const recordTabs = [
  { id: 'completion', label: '记录做完的题' },
  { id: 'checkin', label: '深入复盘' },
  { id: 'history', label: '历史记录' },
];

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

const completionForm = reactive({
  reported_completion: 'self_solved',
  result_status: 'accepted',
  key_step_summary: '',
});

const loading = ref(false);
const completionSaving = ref(false);
const successMessage = ref('');
const error = ref('');
const completionMessage = ref('');
const optionalFieldsOpen = ref(false);
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
const activeRecordTab = ref(handoffPayload.value ? 'checkin' : 'completion');
const chatContextSummary = computed(() => {
  if (!handoffPayload.value) return '';
  const focus = handoffPayload.value.suggested_focus || 'AIChat 建议转入深入复盘';
  const lastMessage = handoffPayload.value.last_user_message || '';
  return [focus, lastMessage].filter(Boolean).join('；');
});

function applyClosureHandoffToForm(payload) {
  if (!payload || payload.risk_type !== 'problem_closure_passed') return;
  if (!form.problem_title && payload.problem_title) {
    form.problem_title = payload.problem_title;
  }
  form.completion_status = 'independent';
  if (!form.bottleneck_text.trim()) {
    form.bottleneck_text = payload.suggested_focus || 'AIChat 结束验证已经通过，整理这题的关键理解点和可迁移方法。';
  }
  if (!form.reflection?.trim()) {
    form.reflection = [
      payload.closure_question ? `结束验证问题：${payload.closure_question}` : '',
      payload.closure_answer ? `我的回答：${payload.closure_answer}` : '',
      payload.closure_feedback ? `AI 反馈：${payload.closure_feedback}` : '',
    ].filter(Boolean).join('\n');
  }
}

applyClosureHandoffToForm(handoffPayload.value);

async function submitCompletionRecord() {
  completionMessage.value = '';
  const summary = completionForm.key_step_summary.trim();
  if (!summary) {
    completionMessage.value = '给未来的自己留一句提醒，老师也能知道你这题是不是真的收住了。';
    return;
  }
  completionSaving.value = true;
  try {
    const payload = await createStudentProblemCompletion(auth.token, {
      problem_id: form.problem_url || '',
      problem_title: form.problem_title || '',
      problem_url: form.problem_url || '',
      session_id: handoffPayload.value?.session_id || '',
      reported_completion: completionForm.reported_completion,
      result_status: completionForm.result_status,
      key_step_summary: summary,
    });
    completionMessage.value = payload?.message || '做题记录已保存。';
    completionForm.key_step_summary = '';
  } catch (err) {
    completionMessage.value = err.message || '做题记录保存失败，请稍后再试。';
  } finally {
    completionSaving.value = false;
  }
}

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
  <div class="space-y-6">
    <section class="panel workspace-card-checkin mx-auto w-full max-w-5xl">
      <p class="section-eyebrow text-checkin-700">学习记录</p>
      <h2 class="mt-2 font-display text-3xl font-bold text-slate-900">做完题后，留下有用证据</h2>
      <p class="mt-3 max-w-3xl text-sm leading-7 text-slate-500">
        做完就先记一条；如果这题错过、卡过、靠 AIChat 才想明白，再进入深入复盘。
      </p>
      <div class="mt-5 flex flex-wrap gap-2">
        <button
          v-for="tab in recordTabs"
          :key="tab.id"
          :class="activeRecordTab === tab.id ? 'button-primary px-4 py-2 text-sm' : 'button-secondary px-4 py-2 text-sm'"
          type="button"
          @click="activeRecordTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
    </section>

    <section v-if="activeRecordTab === 'completion'" class="panel workspace-card-checkin mx-auto w-full max-w-5xl">
      <div class="mb-5">
        <p class="section-eyebrow text-emerald-700">做题记录</p>
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">记录一道做完的题</h3>
        <p class="mt-3 text-sm leading-7 text-slate-500">
          简单写下你怎么完成的。老师会用它判断你更适合独立练，还是需要再补一道同类题。
        </p>
      </div>
      <div class="grid gap-4 md:grid-cols-2">
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-600">题目链接 / 题号</label>
          <input v-model="form.problem_url" class="field" placeholder="例如 P1119 或题目链接" />
        </div>
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-600">题目标题</label>
          <input v-model="form.problem_title" class="field" placeholder="没有链接时请补标题" />
        </div>
      </div>
      <div class="mt-4 grid gap-4 md:grid-cols-2">
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-600">我是怎么完成的</label>
          <select v-model="completionForm.reported_completion" class="field w-full">
            <option value="self_solved">我自己做出来了</option>
            <option value="small_hint">看了少量提示后做出来</option>
            <option value="classroom_taught">老师讲过后做出来</option>
            <option value="aichat_assisted">AIChat 帮助后做出来</option>
            <option value="editorial_completed">看题解后补完</option>
            <option value="unsure">还没完全确定</option>
          </select>
        </div>
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-600">结果</label>
          <select v-model="completionForm.result_status" class="field w-full">
            <option value="accepted">AC</option>
            <option value="sample_passed">样例通过，还没提交</option>
            <option value="unsure">还不确定</option>
          </select>
        </div>
      </div>
      <label class="mt-4 block text-sm font-semibold text-slate-600">
        <span class="block">下次我会先想什么</span>
        <span class="mt-1 block text-xs font-medium leading-5 text-slate-500">给未来的自己留一句提醒，不用写完整题解。</span>
        <textarea
          v-model="completionForm.key_step_summary"
          class="field mt-2 min-h-[120px] resize-y"
          placeholder="例如：遇到按时间变化的最短路，先想能不能按时间顺序逐步更新，而不是每次询问都重算。"
        />
      </label>
      <div class="mt-4 flex flex-wrap items-center gap-3">
        <button class="button-primary" type="button" :disabled="completionSaving" @click="submitCompletionRecord">
          {{ completionSaving ? '正在保存...' : '保存做题记录' }}
        </button>
        <p v-if="completionMessage" class="text-sm font-medium text-slate-600">{{ completionMessage }}</p>
      </div>
    </section>

    <section v-if="activeRecordTab === 'history'" class="panel workspace-card-checkin mx-auto w-full max-w-5xl">
      <p class="section-eyebrow text-archive-700">历史记录</p>
      <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">回看以前整理过的题</h3>
      <p class="mt-3 text-sm leading-7 text-slate-500">
        历史里会分开保存“深入复盘”和“做题记录”：前者看完整整理，后者看做题留痕。
      </p>
      <div class="mt-5 flex flex-wrap gap-3">
        <RouterLink class="button-secondary inline-flex" :to="{ path: '/app/archive', query: { tab: 'records' } }">查看做题记录</RouterLink>
        <RouterLink class="button-secondary inline-flex" :to="{ path: '/app/archive', query: { tab: 'reviews' } }">查看深入复盘</RouterLink>
      </div>
    </section>

    <section class="panel workspace-card-checkin mx-auto w-full max-w-5xl">
      <template v-if="activeRecordTab === 'checkin'">
      <div class="mb-5">
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">深入复盘这道题</h3>
        <p class="mt-3 text-sm leading-7 text-slate-500">适合错过、卡过、靠 AIChat 才想明白的题。把没想明白的地方和你已经试过的内容写清楚，就可以开始整理。</p>
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
              {{ ojSourceLabel(detectedOjSource) }}。洛谷和 JMYSOJ 链接可自动读取；其他平台请补题目标题和题面。
            </p>
          </div>
          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-600">题目标题</label>
            <input v-model="form.problem_title" class="field" placeholder="没有链接时请补标题" />
          </div>
        </div>
        <div>
          <label for="checkin-bottleneck" class="mb-2 block text-sm font-semibold text-slate-600">我哪里没想明白</label>
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
        <section class="rounded-[28px] border border-checkin-100 bg-white/70 p-4">
          <button
            class="flex w-full items-center justify-between gap-3 text-left text-sm font-semibold text-checkin-700"
            type="button"
            @click="optionalFieldsOpen = !optionalFieldsOpen"
          >
            <span>补充信息（可选）</span>
            <span class="rounded-full bg-checkin-50 px-3 py-1 text-xs text-checkin-800">
              {{ optionalFieldsOpen ? '收起补充信息' : '展开补充信息' }}
            </span>
          </button>
          <p class="mt-2 text-xs leading-5 text-slate-500">
            AIChat 带来的内容只作为草稿，提交前请尽量改成自己的话。
          </p>
          <div v-if="optionalFieldsOpen" class="mt-4 space-y-4">
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
              <p class="mb-3 text-sm font-semibold text-slate-600">如果你愿意，也可以补充问题类型</p>
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
              <textarea v-model="form.student_code" class="field min-h-32 resize-y font-mono text-xs" placeholder="如果这次问题和代码实现有关，再把代码贴进来。"/>
            </div>
            <button class="button-secondary w-full" type="button" @click="resetOptionalFields">清空补充信息</button>
          </div>
        </section>
        <p v-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
        <p v-if="successMessage" class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">{{ successMessage }}</p>
        <button class="button-primary w-full bg-gradient-to-r from-checkin-500 via-amber-500 to-orange-500" :disabled="loading" type="submit">
          {{ loading ? '正在提交...' : '提交并进入复盘详情' }}
        </button>
      </form>
      </template>
    </section>
  </div>
</template>
