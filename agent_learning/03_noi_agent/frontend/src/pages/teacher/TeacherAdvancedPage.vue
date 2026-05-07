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
const defaultDraftIntegrationStatus = 'draft_only';

const readableLabelMap = {
  known_bridge: '已稳定引导',
  candidate_bridge: '待确认引导',
  open_bridge: '新发现引导',
  confirmed: '已确认',
  rejected: '已退回',
  draft_only: '仅保存草案',
  registered: '已登记',
  active: '启用',
  inactive: '停用',
  'candidate-suggestion': '待确认建议',
  'route-known': '已确认路径',
  'mastery-stats': '掌握情况统计',
};

function readableLabel(value, fallback = '未记录') {
  const text = String(value || '').trim();
  if (!text) return fallback;
  if (readableLabelMap[text]) return readableLabelMap[text];
  if (/^[a-z0-9_-]+$/i.test(text) && /[_-]/.test(text)) return fallback;
  return text;
}

function statRows(bucket) {
  if (!bucket) return [];
  if (Array.isArray(bucket)) {
    return bucket.map((item, index) => ({
      id: item.key || item.label || item.name || `${index}`,
      label: readableLabel(item.label || item.key || item.name || item.topic_l1 || item.topic_l2 || item.bridge || item.bucket, '未命名'),
      count: item.count ?? item.reviewed_count ?? 0,
      total: item.total,
      rate: item.rate,
    }));
  }
  return Object.entries(bucket).map(([key, value]) => ({
    id: key,
    label: readableLabel(value?.label || key, '未命名'),
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

function draftIntegrationStatusText(item) {
  return readableLabel(item?.rule_draft?.integration_status || defaultDraftIntegrationStatus);
}

function automaticMatchingText(item) {
  return item?.resolver_enabled ? '已启用' : '暂未启用';
}

function patchStatusText(draft) {
  return readableLabel(draft?.patch_status);
}

const bridgeRouteStatusRows = computed(() => statRows(stats.value?.bridge_route_stats?.status));
const candidateBridgeRows = computed(() => statRows(stats.value?.bridge_route_stats?.candidate_bridge));
const openBridgeRows = computed(() => statRows(stats.value?.bridge_route_stats?.open_bridge));
const bridgePromotionSuggestions = computed(() => stats.value?.bridge_route_promotion_suggestions || []);
const topicL1Rows = computed(() => statRows(stats.value?.topic_l1_stats));
const topicL2Rows = computed(() => statRows(stats.value?.topic_l2_stats));
const knowledgeBailoutRows = computed(() => statRows(stats.value?.knowledge_bailout_stats));
const rulePatchDraft = computed(() => resolverPatchDraft.value);

async function loadAdvancedData() {
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
    error.value = err.message || '加载系统维护数据失败';
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
    draftMessage.value = '已登记到人工规则簿，自动匹配暂未启用。';
  } catch (err) {
    error.value = err.message || '登记到人工规则簿失败';
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
    draftMessage.value = '代码改动草稿已生成，仅供教师审查，当前不会影响学生使用。';
  } catch (err) {
    error.value = err.message || '生成代码改动草稿失败';
  } finally {
    draftSubmitting.value = { ...draftSubmitting.value, [`patch-${item.id}`]: false };
  }
}

onMounted(loadAdvancedData);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p class="section-eyebrow text-indigo-700">高级</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">系统维护</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">
            这里放系统排查、规则草稿和旧统计观察；普通带班先看首页、学生和复盘页面。
          </p>
        </div>
        <button class="button-secondary" type="button" @click="loadAdvancedData">刷新</button>
      </div>
      <p v-if="loading" class="text-sm text-slate-500">正在加载系统维护数据...</p>
      <p v-else-if="error" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{{ error }}</p>
      <p v-if="draftMessage" class="rounded-2xl bg-emerald-100 px-4 py-3 text-sm font-medium text-emerald-800">{{ draftMessage }}</p>
    </section>

    <section class="grid gap-6 xl:grid-cols-2">
      <div class="space-y-4">
        <div class="bento-card border-cyan-100 bg-gradient-to-br from-white via-cyan-50/70 to-sky-50/60">
          <p class="text-sm font-semibold text-cyan-700">系统规则健康检查</p>
          <div v-if="bridgeRouteStatusRows.length" class="mt-4 grid gap-3 sm:grid-cols-3">
            <div v-for="row in bridgeRouteStatusRows" :key="row.id" class="rounded-[20px] border border-cyan-100 bg-white/85 p-4">
              <p class="break-words text-sm font-semibold text-slate-800">{{ row.label }}</p>
              <p class="mt-2 text-xs text-slate-500">{{ row.count }} 条 · {{ formatRate(row.rate) }}</p>
            </div>
          </div>
          <div class="mt-4 grid gap-3 sm:grid-cols-2">
            <div class="rounded-[20px] border border-cyan-100 bg-white/80 p-4">
              <p class="text-xs font-semibold tracking-[0.12em] text-cyan-700">待确认引导最多</p>
              <p v-if="candidateBridgeRows.length" class="mt-2 break-words text-sm text-slate-700">{{ candidateBridgeRows[0].label }} · {{ candidateBridgeRows[0].count }} 条</p>
              <p v-else class="mt-2 text-sm text-slate-500">暂无待确认引导</p>
            </div>
            <div class="rounded-[20px] border border-sky-100 bg-white/80 p-4">
              <p class="text-xs font-semibold tracking-[0.12em] text-sky-700">新发现引导最多</p>
              <p v-if="openBridgeRows.length" class="mt-2 break-words text-sm text-slate-700">{{ openBridgeRows[0].label }} · {{ openBridgeRows[0].count }} 条</p>
              <p v-else class="mt-2 text-sm text-slate-500">暂无新发现引导</p>
            </div>
          </div>
        </div>

        <div class="bento-card border-emerald-100 bg-gradient-to-br from-white via-emerald-50/70 to-lime-50/50">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <p class="text-sm font-semibold text-emerald-700">AI 规则草稿</p>
            <span class="tag-pill bg-white text-emerald-700">需要教师确认</span>
          </div>
          <p class="mt-2 text-xs text-slate-500">这些只是候选规则线索，不会自动应用。</p>
          <div v-if="bridgePromotionSuggestions.length" class="mt-4 space-y-3">
            <div v-for="item in bridgePromotionSuggestions.slice(0, 4)" :key="`${item.route_kind}-${item.bridge_id}`" class="rounded-[20px] border border-emerald-100 bg-white/85 p-4">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="break-words text-sm font-semibold text-slate-800">{{ readableLabel(item.bridge_id, '未命名规则') }}</p>
                  <p class="mt-1 text-xs text-slate-500">{{ readableLabel(item.route_kind) }} · {{ item.parent_focus || item.stable_focus || '未记录来源' }} · {{ item.count }} 条</p>
                </div>
                <span class="tag-pill bg-emerald-100 text-emerald-700">不会自动应用</span>
              </div>
              <p class="mt-3 break-words text-xs leading-5 text-slate-500">
                证据：{{ (item.evidence_signals || []).slice(0, 3).join(' / ') || '暂无' }}
              </p>
              <div class="mt-3 grid gap-2 sm:grid-cols-2">
                <p class="break-words text-xs text-slate-500">草案文件：{{ item.rule_draft?.filename || '待生成' }}</p>
                <p class="break-words text-xs text-slate-500">草案状态：{{ draftIntegrationStatusText(item) }}</p>
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
          <p v-else class="mt-4 rounded-[22px] border border-dashed border-emerald-200 bg-white/70 p-4 text-sm text-slate-500">暂无 AI 规则草稿</p>
        </div>

        <div class="bento-card border-teal-100 bg-gradient-to-br from-white via-teal-50/70 to-cyan-50/50">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <p class="text-sm font-semibold text-teal-700">草案审查历史</p>
            <button class="button-secondary text-xs" type="button" @click="loadAdvancedData">加载历史</button>
          </div>
          <div v-if="draftDecisions.length" class="mt-4 space-y-3">
            <div v-for="item in draftDecisions.slice(0, 5)" :key="item.id" class="rounded-[20px] border border-teal-100 bg-white/85 p-4">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="break-words text-sm font-semibold text-slate-800">{{ readableLabel(item.bridge_id, '未命名规则') }}</p>
                  <p class="mt-1 text-xs text-slate-500">{{ readableLabel(item.route_kind) }} · {{ item.parent_focus || '未记录来源' }}</p>
                </div>
                <span class="tag-pill bg-teal-100 text-teal-700">{{ readableLabel(item.decision) }}</span>
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
                {{ draftSubmitting[`registry-${item.id}`] ? '正在登记...' : '登记到人工规则簿' }}
              </button>
            </div>
          </div>
          <p v-else class="mt-4 rounded-[22px] border border-dashed border-teal-200 bg-white/70 p-4 text-sm text-slate-500">暂无草案审查历史</p>
        </div>
      </div>

      <div class="space-y-4">
        <div class="bento-card border-indigo-100 bg-gradient-to-br from-white via-indigo-50/70 to-blue-50/50">
          <p class="text-sm font-semibold text-indigo-700">人工确认规则</p>
          <p class="mt-2 text-xs text-slate-500">这里是人工确认后的规则登记簿，自动匹配暂未启用。</p>
          <div v-if="registryEntries.length" class="mt-4 space-y-3">
            <div v-for="item in registryEntries.slice(0, 5)" :key="item.id" class="rounded-[20px] border border-indigo-100 bg-white/85 p-4">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="break-words text-sm font-semibold text-slate-800">{{ readableLabel(item.bridge_id, '未命名规则') }}</p>
                  <p class="mt-1 text-xs text-slate-500">{{ readableLabel(item.route_kind) }} · {{ item.parent_focus || '未记录来源' }}</p>
                </div>
                <span class="tag-pill bg-indigo-100 text-indigo-700">{{ readableLabel(item.registry_status) }}</span>
              </div>
              <p class="mt-3 break-words text-xs leading-5 text-slate-500">自动匹配：{{ automaticMatchingText(item) }}</p>
              <p class="mt-1 break-words text-xs leading-5 text-slate-500">草案文件：{{ item.draft_filename || '—' }}</p>
              <button
                class="button-secondary mt-3 text-xs"
                type="button"
                :disabled="draftSubmitting[`patch-${item.id}`]"
                @click="generateResolverPatchDraft(item)"
              >
                {{ draftSubmitting[`patch-${item.id}`] ? '正在生成...' : '生成代码改动草稿' }}
              </button>
            </div>
          </div>
          <div v-if="rulePatchDraft" class="mt-4 rounded-[20px] border border-indigo-100 bg-white/85 p-4">
            <p class="text-xs font-semibold tracking-[0.12em] text-indigo-700">代码改动草稿</p>
            <p class="mt-2 break-words text-sm font-semibold text-slate-800">{{ readableLabel(rulePatchDraft.bridge_id, '未命名规则') }}</p>
            <p class="mt-2 text-xs text-slate-500">草稿未应用 · {{ rulePatchDraft.target_file }} · {{ patchStatusText(rulePatchDraft) }}</p>
          </div>
          <p v-else class="mt-4 rounded-[22px] border border-dashed border-indigo-200 bg-white/70 p-4 text-sm text-slate-500">暂无人工规则记录</p>
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
    </section>
  </div>
</template>
