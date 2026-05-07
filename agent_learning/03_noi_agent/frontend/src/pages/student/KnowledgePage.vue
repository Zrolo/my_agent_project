<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const KNOWLEDGE_HANDOFF_KEY = 'noi-agent-knowledge-handoff';

function loadKnowledgeHandoff() {
  const raw = window.localStorage.getItem(KNOWLEDGE_HANDOFF_KEY);
  if (!raw) return {};
  try {
    return JSON.parse(raw) || {};
  } catch {
    window.localStorage.removeItem(KNOWLEDGE_HANDOFF_KEY);
    return {};
  }
}

const handoff = ref(loadKnowledgeHandoff());
const focus = ref(handoff.value.focus || handoff.value.suggested_focus || '');
const studentAnswer = ref('');
const checkFeedback = ref('');

const problemTitle = computed(() => handoff.value.problem_title || window.localStorage.getItem('noi-agent-chat-problem-title') || '当前题目');
const problemRef = computed(() => handoff.value.problem_ref || window.localStorage.getItem('noi-agent-chat-problem-id') || '');
const lastUserMessage = computed(() => handoff.value.last_user_message || '');
const bridgeFocus = computed(() => focus.value.trim() || '把听过的知识点接回当前题');

const miniExample = computed(() => {
  const text = `${bridgeFocus.value}\n${lastUserMessage.value}`;
  if (/直径|最远|树/.test(text)) {
    return '小例子：一条链 1-2-3-4-5，只选 1 个核心点时，最容易把最大距离撑大的就是两端。先看最难照顾的对象，再回到原题看哪些叶子或路径会撑大答案。';
  }
  if (/强连通|缩点|可达|明星奶牛/.test(text)) {
    return '小例子：1->2->3->1 是一团互相可达的点，3->4 是团外方向。团内可以先看成一个整体，再判断团与团之间谁能到谁。';
  }
  if (/二分|check|答案/.test(text)) {
    return '小例子：先试一个限制 D。如果 D 能做到，答案可能还能更小；如果 D 做不到，就只能放大。关键是说清 D 在当前题里限制了什么。';
  }
  return '小例子：先只保留 3 个对象和 1 个限制，判断这个知识点是在帮你分组、比较、排除，还是维护某个变化量。';
});

function submitLightCheck() {
  const answer = studentAnswer.value.trim();
  if (answer.length < 8) {
    checkFeedback.value = '再多写一句：这个知识点在原题里到底帮你判断什么？';
    return;
  }
  checkFeedback.value = '可以回原题继续了。下一步不用写完整题解，只把这个知识点负责的对象和判断关系说给 AIChat。';
}

function returnToChat() {
  router.push('/app/workspace/chat');
}
</script>

<template>
  <section class="panel workspace-card-chat mx-auto w-full max-w-5xl">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <p class="section-eyebrow text-chat-700">知识补全</p>
        <h2 class="mt-3 font-display text-3xl font-bold text-slate-900">先补一座应用桥</h2>
        <p class="mt-3 max-w-3xl text-sm leading-7 text-slate-600">
          这里不是完整课程。它只帮你把听过的知识点接到当前题的一小步，补完就回到原题继续问 AI。
        </p>
      </div>
      <button class="button-secondary" type="button" @click="returnToChat">回到原题继续问 AI</button>
    </div>

    <div class="mt-6 grid gap-4 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
      <div class="rounded-[24px] border border-chat-100 bg-chat-50/70 p-5">
        <p class="text-sm font-semibold text-chat-700">当前来源</p>
        <h3 class="mt-2 text-xl font-bold text-slate-900">{{ problemTitle }}</h3>
        <p v-if="problemRef" class="mt-2 break-words text-xs font-semibold text-slate-500">{{ problemRef }}</p>
        <p v-if="lastUserMessage" class="mt-4 rounded-[18px] bg-white/80 p-4 text-sm leading-7 text-slate-700">
          {{ lastUserMessage }}
        </p>
      </div>

      <div class="rounded-[24px] border border-slate-200 bg-white/90 p-5">
        <label class="mb-2 block text-sm font-semibold text-slate-700">这一步缺什么</label>
        <textarea
          v-model="focus"
          class="field min-h-28 resize-y"
          placeholder="例如：我知道要用树的直径，但不知道它在这题里负责什么。"
        />
      </div>
    </div>

    <div class="mt-5 grid gap-4 lg:grid-cols-3">
      <article class="rounded-[24px] border border-slate-200 bg-white/90 p-5">
        <p class="text-sm font-semibold text-slate-800">这个知识在原题里负责什么</p>
        <p class="mt-3 text-sm leading-7 text-slate-600">
          先别把它当成完整解法。只看它帮你处理哪一类对象、哪一个判断、或者哪种变化关系。
        </p>
      </article>
      <article class="rounded-[24px] border border-slate-200 bg-white/90 p-5">
        <p class="text-sm font-semibold text-slate-800">小例子</p>
        <p class="mt-3 text-sm leading-7 text-slate-600">{{ miniExample }}</p>
      </article>
      <article class="rounded-[24px] border border-slate-200 bg-white/90 p-5">
        <p class="text-sm font-semibold text-slate-800">轻验证</p>
        <p class="mt-3 text-sm leading-7 text-slate-600">
          用一句话写清：这个知识点回到原题后，先帮你判断什么？
        </p>
      </article>
    </div>

    <div class="mt-5 rounded-[24px] border border-emerald-100 bg-emerald-50/70 p-5">
      <label class="mb-2 block text-sm font-semibold text-slate-700">我的一句话验证</label>
      <textarea
        v-model="studentAnswer"
        class="field min-h-28 resize-y"
        placeholder="例如：树的直径先帮我找最难覆盖的远点，再判断核心城市怎么扩展。"
      />
      <div class="mt-4 flex flex-wrap gap-2">
        <button class="button-primary" type="button" @click="submitLightCheck">提交轻验证</button>
        <button class="button-secondary" type="button" @click="returnToChat">回到原题继续问 AI</button>
      </div>
      <p v-if="checkFeedback" class="mt-4 rounded-2xl bg-white/80 px-4 py-3 text-sm font-medium leading-6 text-slate-700">
        {{ checkFeedback }}
      </p>
    </div>
  </section>
</template>
