<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import { importProblem, sendChat } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const router = useRouter();

const problemId = ref(window.localStorage.getItem('noi-agent-chat-problem-id') || '');
const problemTitle = ref(window.localStorage.getItem('noi-agent-chat-problem-title') || '');
const problemContext = ref(window.localStorage.getItem('noi-agent-chat-problem-context') || '');
const studentCode = ref(window.localStorage.getItem('noi-agent-chat-student-code') || '');
const sessionId = ref(window.localStorage.getItem('noi-agent-chat-session-id') || crypto.randomUUID());
const message = ref('');
const sending = ref(false);
const importingProblem = ref(false);
const error = ref('');
const problemImportMessage = ref('');
const remainingQuota = ref(null);
const level = ref('');
const messages = ref([]);

window.localStorage.setItem('noi-agent-chat-session-id', sessionId.value);
const HANDOFF_PAYLOAD_KEY = 'noi-agent-chat-handoff-payload';

const canSend = computed(() => Boolean(problemId.value.trim() && message.value.trim() && !sending.value));
const normalizedProblemUrl = computed(() => {
  const raw = problemId.value.trim();
  return /^https?:\/\//i.test(raw) ? raw : '';
});

function resetSession() {
  sessionId.value = crypto.randomUUID();
  messages.value = [];
  window.localStorage.setItem('noi-agent-chat-session-id', sessionId.value);
}

function persistProblemContext() {
  window.localStorage.setItem('noi-agent-chat-problem-id', problemId.value.trim());
  window.localStorage.setItem('noi-agent-chat-problem-title', problemTitle.value.trim());
  window.localStorage.setItem('noi-agent-chat-problem-context', problemContext.value.trim());
  window.localStorage.setItem('noi-agent-chat-student-code', studentCode.value.trim());
}

function persistHandoffPayload(payload) {
  if (payload && typeof payload === 'object') {
    window.localStorage.setItem(HANDOFF_PAYLOAD_KEY, JSON.stringify(payload));
    return;
  }
  window.localStorage.removeItem(HANDOFF_PAYLOAD_KEY);
}

function clearProblemContext() {
  problemId.value = '';
  problemTitle.value = '';
  problemContext.value = '';
  studentCode.value = '';
  problemImportMessage.value = '';
  persistProblemContext();
  persistHandoffPayload(null);
}

function goToCheckinWithCurrentProblem() {
  persistProblemContext();
  router.push('/app/workspace/checkin');
}

async function importCurrentLuoguProblem() {
  const rawRef = problemId.value.trim();
  if (!rawRef || importingProblem.value) return;
  importingProblem.value = true;
  error.value = '';
  problemImportMessage.value = '';
  try {
    const result = await importProblem(auth.token, { url: rawRef });
    problemId.value = result.problem_url || rawRef;
    problemTitle.value = result.problem_title || '';
    problemContext.value = result.problem_context || '';
    persistProblemContext();
    problemImportMessage.value = result.message || '已读取洛谷题目';
  } catch (err) {
    error.value = err.message || '读取题目失败，请手动补题目背景';
  } finally {
    importingProblem.value = false;
  }
}

async function submitMessage() {
  if (!canSend.value) return;
  sending.value = true;
  error.value = '';
  persistProblemContext();
  const userMessage = message.value.trim();
  messages.value.push({ role: 'user', content: userMessage });
  message.value = '';
  try {
    const result = await sendChat(auth.token, {
      student_id: auth.userId,
      problem_id: problemId.value.trim(),
      session_id: sessionId.value,
      message: userMessage,
      problem_url: normalizedProblemUrl.value,
      problem_title: problemTitle.value.trim(),
      problem_context: problemContext.value.trim(),
      student_code: studentCode.value.trim(),
    });
    messages.value.push({ role: 'assistant', content: result.reply });
    persistHandoffPayload(result.handoff_payload);
    remainingQuota.value = result.remaining_quota;
    level.value = result.level;
  } catch (err) {
    error.value = err.message || '发送失败，请稍后重试';
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <div class="grid gap-6 xl:grid-cols-[0.78fr_1.22fr]">
    <section class="panel workspace-card-chat space-y-5">
      <div>
        <p class="section-eyebrow text-chat-700">Workspace Context</p>
        <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">我这次卡在哪一步</h3>
        <p class="mt-3 text-sm leading-7 text-slate-600">
          先写题号，再把你卡住的那一步直接说出来。越具体，系统越容易顺着你的真实卡点往下带。
        </p>
      </div>
      <div class="editorial-rule"></div>
      <div class="grid gap-4 md:grid-cols-1">
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-600">题号 / 题目链接</label>
          <input v-model="problemId" class="field" placeholder="例如 P2922、P2678，或直接贴题目链接" />
          <div class="mt-3 flex flex-wrap items-center gap-3">
            <button class="button-secondary px-4 py-2 text-sm" :disabled="!problemId.trim() || importingProblem" type="button" @click="importCurrentLuoguProblem">
              {{ importingProblem ? '正在读取...' : '读取洛谷题目' }}
            </button>
            <span v-if="problemImportMessage" class="text-xs font-semibold text-emerald-600">{{ problemImportMessage }}</span>
          </div>
        </div>
      </div>
      <details class="rounded-[28px] border border-chat-100 bg-white/70 p-4">
        <summary class="cursor-pointer list-none text-sm font-semibold text-chat-700">
          当前题背景（可选）
        </summary>
        <div class="mt-4 space-y-4">
          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-600">题目标题</label>
            <input v-model="problemTitle" class="field" placeholder="例如 P3128 Max Flow" />
          </div>
          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-600">题面 / 关键约束</label>
            <textarea
              v-model="problemContext"
              class="field min-h-28 resize-y"
              placeholder="贴题意、数据范围，或你整理出的关键限制。"
            />
          </div>
          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-600">相关代码</label>
            <textarea
              v-model="studentCode"
              class="field min-h-28 resize-y font-mono text-xs"
              placeholder="如果问题和代码有关，贴相关片段即可。"
            />
          </div>
        </div>
      </details>
      <div class="grid gap-4 md:grid-cols-3">
        <div class="metric-tile">
          <p class="text-sm text-slate-400">当前账号</p>
          <p class="mt-2 text-lg font-semibold text-slate-900">{{ auth.userId }}</p>
        </div>
        <div class="metric-tile">
          <p class="text-sm text-slate-400">剩余配额</p>
          <p class="mt-2 text-lg font-semibold text-slate-900">{{ remainingQuota ?? '—' }}</p>
        </div>
        <div class="metric-tile">
          <p class="text-sm text-slate-400">当前层级</p>
          <p class="mt-2 text-lg font-semibold text-slate-900">{{ level || '—' }}</p>
        </div>
      </div>
      <div class="rounded-[24px] border border-dashed border-chat-200 bg-white/70 p-4 text-sm leading-7 text-slate-600">
        可以直接写：
        <span class="font-semibold text-slate-900">“我知道这题要二分，但我不明白 check(mid) 返回 true 之后为什么应该往右缩。”</span>
      </div>
      <button class="button-secondary w-full" type="button" @click="resetSession">清空当前对话，重新开始</button>
      <button class="button-secondary w-full" type="button" @click="clearProblemContext">清空当前题背景</button>
      <button class="button-primary w-full bg-gradient-to-r from-checkin-500 via-amber-500 to-orange-500" type="button" @click="goToCheckinWithCurrentProblem">
        带着当前题去打卡复盘
      </button>
    </section>

    <section class="panel workspace-card-chat flex min-h-[36rem] flex-col">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-chat-700">Dialogue</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">把问题发给 AI</h3>
          <p class="mt-3 text-sm leading-7 text-slate-600">先问清当前这一步，再看系统怎么陪你把它讲明白。</p>
        </div>
      </div>
      <div class="flex-1 space-y-4 overflow-auto rounded-[28px] border border-chat-100 bg-white/90 p-4">
        <div v-if="messages.length === 0" class="rounded-[28px] border border-dashed border-chat-200 bg-chat-50/60 p-6 text-sm leading-7 text-slate-500">
          你发出问题后，这里会按对话顺序显示你的提问和 AI 的回答。
        </div>
        <article
          v-for="(item, index) in messages"
          :key="`${item.role}-${index}`"
          :class="item.role === 'user' ? 'ml-auto max-w-[85%] rounded-[28px] bg-gradient-to-br from-chat-500 to-cyan-500 px-5 py-4 text-sm leading-7 text-white shadow-lg shadow-chat-500/20' : 'mr-auto max-w-[85%] rounded-[28px] border border-slate-200 bg-white px-5 py-4 text-sm leading-7 text-slate-700 shadow-sm'"
        >
          {{ item.content }}
        </article>
      </div>
      <div class="mt-4 space-y-3">
        <textarea
          v-model="message"
          class="field min-h-32 resize-y"
          placeholder="例如：我知道这题要二分，但我不明白 check(mid) 返回 true 之后为什么应该往右缩。"
        />
        <p v-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
          {{ error }}
        </p>
        <button
          class="button-primary w-full bg-gradient-to-r from-chat-500 via-sky-500 to-cyan-500"
          :disabled="!canSend"
          type="button"
          @click="submitMessage"
        >
          {{ sending ? '正在发送...' : '把这一步问题发给 AI' }}
        </button>
      </div>
    </section>
  </div>
</template>
