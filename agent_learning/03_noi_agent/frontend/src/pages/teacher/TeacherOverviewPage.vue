<script setup>
import { computed, onMounted, ref } from 'vue';

import {
  createBridgeRegistryEntry,
  exportBridgeRuleDraft,
  getBridgeRuleDraftDecisions,
  getBridgeRegistryEntries,
  getTeacherStats,
  getResolverPatchDraft,
  submitBridgeRuleDraftDecision,
} from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const loading = ref(false);
const error = ref('');
const stats = ref(null);
const draftMessage = ref('');
const draftSubmitting = ref({});
const draftDecisions = ref([]);
const registryEntries = ref([]);
const resolverPatchDraft = ref(null);

function statRows(bucket) {
  if (!bucket) return [];
  if (Array.isArray(bucket)) {
    return bucket.map((item, index) => ({
      id: item.key || item.label || item.name || `${index}`,
      label: item.label || item.key || item.name || item.topic_l1 || item.topic_l2 || item.bridge || item.bucket || '未命名',
      count: item.count ?? item.reviewed_count ?? 0,
      total: item.total,
      rate: item.rate,
    }));
  }
  return Object.entries(bucket).map(([key, value]) => ({
    id: key,
    label: value?.label || key,
    count: value?.count ?? value?.reviewed_count ?? 0,
    total: value?.total,
    rate: value?.rate,
  }));
}

function formatRate(rate) {
  const value = Number(rate);
  if (!Number.isFinite(value)) return '—';
  return `${Math.round(value * 100)}%`;
}

function statCount(bucket) {
  return statRows(bucket).length;
}

const bridgeRows = computed(() => statRows(stats.value?.bridge_stats));
const bridgeRouteStatusRows = computed(() => statRows(stats.value?.bridge_route_stats?.status));
const candidateBridgeRows = computed(() => statRows(stats.value?.bridge_route_stats?.candidate_bridge));
const openBridgeRows = computed(() => statRows(stats.value?.bridge_route_stats?.open_bridge));
const bridgePromotionSuggestions = computed(() => stats.value?.bridge_route_promotion_suggestions || []);
const topicL1Rows = computed(() => statRows(stats.value?.topic_l1_stats));
const topicL2Rows = computed(() => statRows(stats.value?.topic_l2_stats));
const knowledgeBailoutRows = computed(() => statRows(stats.value?.knowledge_bailout_stats));

async function loadStats() {
  loading.value = true;
  error.value = '';
  try {
    const [statsResult, decisionsResult, registryResult] = await Promise.all([
      getTeacherStats(auth.token),
      getBridgeRuleDraftDecisions(auth.token),
      getBridgeRegistryEntries(auth.token),
    ]);
    stats.value = statsResult;
    draftDecisions.value = decisionsResult.decisions || [];
    registryEntries.value = registryResult.entries || [];
  } catch (err) {
    error.value = err.message || '加载统计失败';
  } finally {
    loading.value = false;
  }
}

async function confirmBridgeRuleDraft(item) {
  draftMessage.value = '';
  draftSubmitting.value = { ...draftSubmitting.value, [item.bridge_id]: true };
  try {
    await submitBridgeRuleDraftDecision(auth.token, {
      route_kind: item.route_kind,
      bridge_id: item.bridge_id,
      decision: 'confirmed',
      notes: '教师已确认进入人工规则草案池；不自动转正。',
      days: 30,
    });
    draftMessage.value = '草案确认已保存，不会自动转正。';
    const result = await getBridgeRuleDraftDecisions(auth.token);
    draftDecisions.value = result.decisions || [];
  } catch (err) {
    error.value = err.message || '保存草案确认失败';
  } finally {
    draftSubmitting.value = { ...draftSubmitting.value, [item.bridge_id]: false };
  }
}

async function downloadBridgeRuleDraft(item) {
  draftMessage.value = '';
  try {
    const markdown = await exportBridgeRuleDraft(auth.token, {
      route_kind: item.route_kind,
      bridge_id: item.bridge_id,
      days: 30,
    });
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = item.rule_draft?.filename || 'bridge_rule_draft.md';
    anchor.click();
    URL.revokeObjectURL(url);
    draftMessage.value = '草案文件已生成下载。';
  } catch (err) {
    error.value = err.message || '下载草案失败';
  }
}

async function registerBridgeRuleDraft(item) {
  draftMessage.value = '';
  draftSubmitting.value = { ...draftSubmitting.value, [`registry-${item.id}`]: true };
  try {
    await createBridgeRegistryEntry(auth.token, { decision_id: item.id });
    const result = await getBridgeRegistryEntries(auth.token);
    registryEntries.value = result.entries || [];
    draftMessage.value = '已登记到 registry，resolver 未启用。';
  } catch (err) {
    error.value = err.message || '登记到 registry 失败';
  } finally {
    draftSubmitting.value = { ...draftSubmitting.value, [`registry-${item.id}`]: false };
  }
}

async function generateResolverPatchDraft(item) {
  draftMessage.value = '';
  draftSubmitting.value = { ...draftSubmitting.value, [`patch-${item.id}`]: true };
  try {
    const result = await getResolverPatchDraft(auth.token, item.id);
    resolverPatchDraft.value = result.patch_draft || null;
    draftMessage.value = 'resolver patch 草案已生成，patch 草案未应用。';
  } catch (err) {
    error.value = err.message || '生成 resolver patch 草案失败';
  } finally {
    draftSubmitting.value = { ...draftSubmitting.value, [`patch-${item.id}`]: false };
  }
}

onMounted(loadStats);
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 lg:grid-cols-4">
      <article class="metric-tile">
        <p class="text-sm text-slate-400">Bridge 统计</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ stats ? statCount(stats.bridge_stats) : '—' }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">Topic L1</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ stats ? statCount(stats.topic_l1_stats) : '—' }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">知识卡介入</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ stats ? statCount(stats.knowledge_bailout_stats) : '—' }}</p>
      </article>
      <article class="metric-tile">
        <p class="text-sm text-slate-400">人工复核</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900">{{ stats?.manual_review_stats?.length ?? '—' }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <p class="section-eyebrow text-operator-700">Overview</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">核心统计</h3>
        </div>
        <button class="button-secondary" type="button" @click="loadStats">刷新</button>
      </div>
      <p v-if="loading" class="text-sm text-slate-500">正在加载统计...</p>
      <p v-else-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
      <div v-else class="grid gap-6 xl:grid-cols-2">
        <div class="space-y-4">
          <div class="bento-card workspace-card-operator">
            <p class="text-sm font-semibold text-operator-700">高频知识桥分布</p>
            <div v-if="bridgeRows.length" class="mt-4 space-y-3">
              <div v-for="row in bridgeRows" :key="row.id" class="rounded-[22px] border border-white/70 bg-white/85 p-4">
                <div class="flex items-center justify-between gap-3">
                  <p class="min-w-0 break-words text-sm font-semibold text-slate-800">{{ row.label }}</p>
                  <span class="tag-pill bg-operator-100 text-operator-700">{{ row.count }} 次</span>
                </div>
                <p class="mt-2 text-xs text-slate-500">占比 {{ formatRate(row.rate) }}<span v-if="row.total"> · 共 {{ row.total }} 条</span></p>
              </div>
            </div>
            <p v-else class="mt-4 rounded-[22px] border border-dashed border-operator-200 bg-white/70 p-4 text-sm text-slate-500">暂无统计数据</p>
          </div>
          <div class="bento-card border-cyan-100 bg-gradient-to-br from-white via-cyan-50/70 to-sky-50/60">
            <p class="text-sm font-semibold text-cyan-700">桥路由审查</p>
            <div v-if="bridgeRouteStatusRows.length" class="mt-4 grid gap-3 sm:grid-cols-3">
              <div v-for="row in bridgeRouteStatusRows" :key="row.id" class="rounded-[20px] border border-cyan-100 bg-white/85 p-4">
                <p class="break-words text-sm font-semibold text-slate-800">{{ row.label }}</p>
                <p class="mt-2 text-xs text-slate-500">{{ row.count }} 条 · {{ formatRate(row.rate) }}</p>
              </div>
            </div>
            <div class="mt-4 grid gap-3 sm:grid-cols-2">
              <div class="rounded-[20px] border border-cyan-100 bg-white/80 p-4">
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-700">候选桥 Top</p>
                <p v-if="candidateBridgeRows.length" class="mt-2 break-words text-sm text-slate-700">{{ candidateBridgeRows[0].label }} · {{ candidateBridgeRows[0].count }} 条</p>
                <p v-else class="mt-2 text-sm text-slate-500">暂无候选桥</p>
              </div>
              <div class="rounded-[20px] border border-sky-100 bg-white/80 p-4">
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-sky-700">开放桥 Top</p>
                <p v-if="openBridgeRows.length" class="mt-2 break-words text-sm text-slate-700">{{ openBridgeRows[0].label }} · {{ openBridgeRows[0].count }} 条</p>
                <p v-else class="mt-2 text-sm text-slate-500">暂无开放桥</p>
              </div>
            </div>
          </div>
          <div class="bento-card border-emerald-100 bg-gradient-to-br from-white via-emerald-50/70 to-lime-50/50">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <p class="text-sm font-semibold text-emerald-700">转正规则建议</p>
              <span class="tag-pill bg-white text-emerald-700">需要教师确认</span>
            </div>
            <p class="mt-2 text-xs text-slate-500">这些只是候选规则线索，不会自动转正。</p>
            <p v-if="draftMessage" class="mt-3 rounded-2xl bg-emerald-100 px-4 py-3 text-sm font-medium text-emerald-800">{{ draftMessage }}</p>
            <div v-if="bridgePromotionSuggestions.length" class="mt-4 space-y-3">
              <div v-for="item in bridgePromotionSuggestions.slice(0, 4)" :key="`${item.route_kind}-${item.bridge_id}`" class="rounded-[20px] border border-emerald-100 bg-white/85 p-4">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div class="min-w-0">
                    <p class="break-words text-sm font-semibold text-slate-800">{{ item.bridge_id }}</p>
                    <p class="mt-1 text-xs text-slate-500">{{ item.route_kind }} · {{ item.parent_focus || item.stable_focus || 'unknown' }} · {{ item.count }} 条</p>
                  </div>
                  <span class="tag-pill bg-emerald-100 text-emerald-700">不会自动转正</span>
                </div>
                <p class="mt-3 break-words text-xs leading-5 text-slate-500">
                  证据：{{ (item.evidence_signals || []).slice(0, 3).join(' / ') || '暂无' }}
                </p>
                <div class="mt-3 grid gap-2 sm:grid-cols-2">
                  <p class="break-words text-xs text-slate-500">草案文件：{{ item.rule_draft?.filename || '待生成' }}</p>
                  <p class="break-words text-xs text-slate-500">草案状态：{{ item.rule_draft?.integration_status || 'draft_only' }}</p>
                </div>
                <div class="mt-4 flex flex-wrap gap-2">
                  <button class="button-secondary text-xs" type="button" @click="downloadBridgeRuleDraft(item)">下载草案</button>
                  <button
                    class="button-primary bg-gradient-to-r from-emerald-500 to-teal-500 text-xs"
                    type="button"
                    :disabled="draftSubmitting[item.bridge_id]"
                    @click="confirmBridgeRuleDraft(item)"
                  >
                    {{ draftSubmitting[item.bridge_id] ? '正在确认...' : '确认进入草案池' }}
                  </button>
                </div>
              </div>
            </div>
            <p v-else class="mt-4 rounded-[22px] border border-dashed border-emerald-200 bg-white/70 p-4 text-sm text-slate-500">暂无转正规则建议</p>
          </div>
          <div class="bento-card border-teal-100 bg-gradient-to-br from-white via-teal-50/70 to-cyan-50/50">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <p class="text-sm font-semibold text-teal-700">草案审查历史</p>
              <button class="button-secondary text-xs" type="button" @click="loadStats">加载历史</button>
            </div>
            <div v-if="draftDecisions.length" class="mt-4 space-y-3">
              <div v-for="item in draftDecisions.slice(0, 5)" :key="item.id" class="rounded-[20px] border border-teal-100 bg-white/85 p-4">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div class="min-w-0">
                    <p class="break-words text-sm font-semibold text-slate-800">{{ item.bridge_id }}</p>
                    <p class="mt-1 text-xs text-slate-500">{{ item.route_kind }} · {{ item.parent_focus || 'unknown' }}</p>
                  </div>
                  <span class="tag-pill bg-teal-100 text-teal-700">{{ item.decision }}</span>
                </div>
                <p class="mt-3 break-words text-xs leading-5 text-slate-500">草案文件：{{ item.draft_filename || '—' }}</p>
                <p class="mt-1 break-words text-xs leading-5 text-slate-500">备注：{{ item.notes || '—' }}</p>
                <button
                  v-if="item.decision === 'confirmed'"
                  class="button-secondary mt-3 text-xs"
                  type="button"
                  :disabled="draftSubmitting[`registry-${item.id}`]"
                  @click="registerBridgeRuleDraft(item)"
                >
                  {{ draftSubmitting[`registry-${item.id}`] ? '正在登记...' : '登记到 registry' }}
                </button>
              </div>
            </div>
            <p v-else class="mt-4 rounded-[22px] border border-dashed border-teal-200 bg-white/70 p-4 text-sm text-slate-500">暂无草案审查历史</p>
          </div>
          <div class="bento-card border-indigo-100 bg-gradient-to-br from-white via-indigo-50/70 to-blue-50/50">
            <p class="text-sm font-semibold text-indigo-700">正式 bridge registry</p>
            <p class="mt-2 text-xs text-slate-500">这里是人工登记簿，resolver 未启用。</p>
            <div v-if="registryEntries.length" class="mt-4 space-y-3">
              <div v-for="item in registryEntries.slice(0, 5)" :key="item.id" class="rounded-[20px] border border-indigo-100 bg-white/85 p-4">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div class="min-w-0">
                    <p class="break-words text-sm font-semibold text-slate-800">{{ item.bridge_id }}</p>
                    <p class="mt-1 text-xs text-slate-500">{{ item.route_kind }} · {{ item.parent_focus || 'unknown' }}</p>
                  </div>
                  <span class="tag-pill bg-indigo-100 text-indigo-700">{{ item.registry_status }}</span>
                </div>
                <p class="mt-3 break-words text-xs leading-5 text-slate-500">resolver 未启用：{{ item.resolver_enabled ? '否' : '是' }}</p>
                <p class="mt-1 break-words text-xs leading-5 text-slate-500">草案文件：{{ item.draft_filename || '—' }}</p>
                <button
                  class="button-secondary mt-3 text-xs"
                  type="button"
                  :disabled="draftSubmitting[`patch-${item.id}`]"
                  @click="generateResolverPatchDraft(item)"
                >
                  {{ draftSubmitting[`patch-${item.id}`] ? '正在生成...' : '生成 resolver patch 草案' }}
                </button>
              </div>
            </div>
            <div v-if="resolverPatchDraft" class="mt-4 rounded-[20px] border border-indigo-100 bg-white/85 p-4">
              <p class="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-700">resolver patch 草案</p>
              <p class="mt-2 break-words text-sm font-semibold text-slate-800">{{ resolverPatchDraft.bridge_id }}</p>
              <p class="mt-2 text-xs text-slate-500">patch 草案未应用 · {{ resolverPatchDraft.target_file }} · {{ resolverPatchDraft.patch_status }}</p>
            </div>
            <p v-else class="mt-4 rounded-[22px] border border-dashed border-indigo-200 bg-white/70 p-4 text-sm text-slate-500">暂无 registry 记录</p>
          </div>
          <div class="bento-card border-slate-200 bg-white">
            <p class="text-sm font-semibold text-slate-700">知识域分布</p>
            <div v-if="topicL1Rows.length" class="mt-4 grid gap-3 sm:grid-cols-2">
              <div v-for="row in topicL1Rows" :key="row.id" class="rounded-[20px] border border-slate-100 bg-slate-50/80 p-4">
                <p class="break-words text-sm font-semibold text-slate-800">{{ row.label }}</p>
                <p class="mt-2 text-xs text-slate-500">{{ row.count }} 次 · {{ formatRate(row.rate) }}</p>
              </div>
            </div>
            <p v-else class="mt-4 rounded-[22px] border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">暂无统计数据</p>
          </div>
        </div>
        <div class="space-y-4">
          <div class="bento-card border-fuchsia-100 bg-gradient-to-br from-white via-fuchsia-50/65 to-violet-50/50">
            <p class="text-sm font-semibold text-fuchsia-700">知识子域分布</p>
            <div v-if="topicL2Rows.length" class="mt-4 space-y-3">
              <div v-for="row in topicL2Rows" :key="row.id" class="rounded-[20px] border border-fuchsia-100 bg-white/80 p-4">
                <p class="break-words text-sm font-semibold text-slate-800">{{ row.label }}</p>
                <p class="mt-2 text-xs text-slate-500">{{ row.count }} 次 · {{ formatRate(row.rate) }}</p>
              </div>
            </div>
            <p v-else class="mt-4 rounded-[22px] border border-dashed border-fuchsia-200 bg-white/70 p-4 text-sm text-slate-500">暂无统计数据</p>
          </div>
          <div class="bento-card border-orange-100 bg-gradient-to-br from-white via-orange-50/70 to-amber-50/60">
            <p class="text-sm font-semibold text-orange-700">知识卡介入分布</p>
            <div v-if="knowledgeBailoutRows.length" class="mt-4 space-y-3">
              <div v-for="row in knowledgeBailoutRows" :key="row.id" class="rounded-[20px] border border-orange-100 bg-white/80 p-4">
                <div class="flex items-center justify-between gap-3">
                  <p class="break-words text-sm font-semibold text-slate-800">{{ row.label }}</p>
                  <span class="tag-pill bg-orange-100 text-orange-700">{{ formatRate(row.rate) }}</span>
                </div>
                <p class="mt-2 text-xs text-slate-500">{{ row.count }} 次<span v-if="row.total"> · 共 {{ row.total }} 条</span></p>
              </div>
            </div>
            <p v-else class="mt-4 rounded-[22px] border border-dashed border-orange-200 bg-white/70 p-4 text-sm text-slate-500">暂无统计数据</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
