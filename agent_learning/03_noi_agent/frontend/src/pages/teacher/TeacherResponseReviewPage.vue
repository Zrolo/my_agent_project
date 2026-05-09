<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';

import {
  exportTeacherResponseReviewLabels,
  getTeacherResponseReviewDatasets,
  getTeacherResponseReviewItems,
  saveTeacherResponseReviewLabel,
} from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();

const loading = ref(false);
const saving = ref(false);
const exporting = ref(false);
const error = ref('');
const message = ref('');
const items = ref([]);
const datasets = ref([]);
const selectedDatasetId = ref('');
const currentIndex = ref(0);
const statusFilter = ref('all');
const showAdvancedOptions = ref(false);

const form = ref(emptyForm());

const qualityOptions = [
  ['good', '好', '对准卡点，并能引导学生提炼可迁移规则'],
  ['okay', '一般', '方向有用，但可能只是让学生完成局部任务'],
  ['bad', '差', '不适合给学生，或只是临时填空/答非所问'],
  ['uncertain', '不确定', '先保留，后面集中复盘'],
];

const leakageOptions = [
  ['no_leakage', '无泄露', '没有说穿当前关键桥'],
  ['minor_bridge_leakage', '轻微', '提示偏强，但学生仍需推理'],
  ['major_bridge_leakage', '严重', '直接补完当前关键桥'],
  ['answer_leakage', '答案/代码', '给出完整题解、步骤或代码'],
];

const rankOptions = [
  ['', '不排序'],
  ['1', '1 最好'],
  ['2', '2 第二'],
  ['3', '3 第三'],
  ['tie', '并列'],
];

const reviewStatusOptions = [
  ['labeled', '已评完'],
  ['needs_discussion', '不确定，需要讨论'],
  ['unlabeled', '未评'],
];

const selectedItem = computed(() => items.value[currentIndex.value] || null);
const selectedDataset = computed(
  () => datasets.value.find((dataset) => dataset.dataset_id === selectedDatasetId.value) || null,
);
const reviewedCount = computed(() => items.value.filter((item) => item.review_status === 'labeled').length);
const progressText = computed(() => {
  if (!items.value.length) return '0 / 0';
  return `${currentIndex.value + 1} / ${items.value.length}`;
});

function emptyForm() {
  return {
    overall_quality: '',
    leakage_label: 'no_leakage',
    preference_rank: '',
    notes: '',
    review_status: 'labeled',
  };
}

function loadFormFromItem(item) {
  form.value = {
    overall_quality: item?.overall_quality || '',
    leakage_label: item?.leakage_label || 'no_leakage',
    preference_rank: item?.preference_rank || '',
    notes: item?.notes || '',
    review_status: item?.review_status === 'labeled' ? 'labeled' : item?.review_status || 'labeled',
  };
}

function formatLongText(value, fallback = 'N/A') {
  return String(value || '').trim() || fallback;
}

function setQuality(value) {
  form.value.overall_quality = value;
  form.value.review_status = value === 'uncertain' ? 'needs_discussion' : 'labeled';
}

function setLeakage(value) {
  form.value.leakage_label = value;
}

function goTo(index) {
  if (!items.value.length) return;
  currentIndex.value = Math.max(0, Math.min(index, items.value.length - 1));
  loadFormFromItem(selectedItem.value);
}

function goNext() {
  goTo(currentIndex.value + 1);
}

function goPrevious() {
  goTo(currentIndex.value - 1);
}

async function loadItems() {
  if (!selectedDatasetId.value) {
    items.value = [];
    loadFormFromItem(null);
    return;
  }
  loading.value = true;
  error.value = '';
  message.value = '';
  try {
    const payload = await getTeacherResponseReviewItems(auth.token, {
      limit: 300,
      status: statusFilter.value,
      dataset_id: selectedDatasetId.value,
    });
    items.value = payload.items || [];
    currentIndex.value = Math.min(currentIndex.value, Math.max(0, items.value.length - 1));
    loadFormFromItem(selectedItem.value);
  } catch (err) {
    error.value = err.message || '加载回复盲评样本失败';
  } finally {
    loading.value = false;
  }
}

async function loadDatasets() {
  const payload = await getTeacherResponseReviewDatasets(auth.token);
  datasets.value = payload.datasets || [];
  selectedDatasetId.value =
    payload.default_dataset_id || datasets.value[0]?.dataset_id || '';
}

function handleDatasetChange() {
  currentIndex.value = 0;
  loadItems();
}

async function saveCurrent({ advance = true } = {}) {
  const item = selectedItem.value;
  if (!item || !form.value.overall_quality) {
    error.value = '请先选择整体可用性。';
    return;
  }
  saving.value = true;
  error.value = '';
  message.value = '';
  try {
    const payload = await saveTeacherResponseReviewLabel(auth.token, {
      dataset_id: selectedDatasetId.value,
      anonymized_response_id: item.anonymized_response_id,
      case_id: item.case_id,
      ...form.value,
    });
    const label = payload.label || {};
    items.value = items.value.map((current) => {
      if (current.anonymized_response_id !== item.anonymized_response_id) return current;
      return {
        ...current,
        overall_quality: label.overall_quality,
        leakage_label: label.leakage_label,
        preference_rank: label.preference_rank,
        notes: label.notes,
        review_status: label.review_status,
        updated_at: label.updated_at,
      };
    });
    message.value = '已保存';
    if (advance) goNext();
  } catch (err) {
    error.value = err.message || '保存盲评失败';
  } finally {
    saving.value = false;
  }
}

async function saveWithoutNotes() {
  form.value.notes = '';
  await saveCurrent({ advance: true });
}

function downloadText(text, filename, type) {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function exportLabels() {
  exporting.value = true;
  error.value = '';
  message.value = '';
  try {
    const text = await exportTeacherResponseReviewLabels(auth.token, 'csv', {
      dataset_id: selectedDatasetId.value,
    });
    const stamp = new Date().toISOString().slice(0, 19).replaceAll(/[-:T]/g, '');
    downloadText(text, `response_review_labels_${selectedDatasetId.value || 'default'}_${stamp}.csv`, 'text/csv;charset=utf-8');
    message.value = '导出已生成';
  } catch (err) {
    error.value = err.message || '导出失败';
  } finally {
    exporting.value = false;
  }
}

function isTextInputTarget(target) {
  const tag = String(target?.tagName || '').toLowerCase();
  return tag === 'input' || tag === 'textarea' || tag === 'select' || Boolean(target?.isContentEditable);
}

function handleKeydown(event) {
  if (isTextInputTarget(event.target)) return;
  const key = event.key.toLowerCase();
  if (key === '1') setQuality('good');
  else if (key === '2') setQuality('okay');
  else if (key === '3') setQuality('bad');
  else if (key === '4') setQuality('uncertain');
  else if (key === 'q') setLeakage('no_leakage');
  else if (key === 'w') setLeakage('minor_bridge_leakage');
  else if (key === 'e') setLeakage('major_bridge_leakage');
  else if (key === 'r') setLeakage('answer_leakage');
  else if (key === 'arrowleft') goPrevious();
  else if (key === 'arrowright') goNext();
  else if (key === 'enter') saveCurrent();
  else if (key === ' ') {
    event.preventDefault();
    goNext();
  }
}

watch(statusFilter, () => {
  currentIndex.value = 0;
  loadItems();
});

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown);
  try {
    await loadDatasets();
    await loadItems();
  } catch (err) {
    error.value = err.message || '加载评审批次失败';
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <div class="space-y-6 pb-6 lg:pb-[260px]">
    <section class="panel">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">One Card Review</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">AIChat 回复盲评</h3>
          <p class="mt-2 text-sm leading-7 text-slate-500">
            一卡一评，小屏幕只看一条回复。已评 {{ reviewedCount }} / {{ items.length }} 条。
          </p>
        </div>
        <div class="grid w-full gap-3 sm:grid-cols-2 lg:w-auto lg:grid-cols-[220px_140px_auto_auto]">
          <label class="block">
            <span class="sr-only">评审批次</span>
            <select v-model="selectedDatasetId" class="field w-full" @change="handleDatasetChange">
              <option v-for="dataset in datasets" :key="dataset.dataset_id" :value="dataset.dataset_id">
                {{ dataset.label }}
              </option>
            </select>
          </label>
          <label class="block">
            <span class="sr-only">筛选状态</span>
            <select v-model="statusFilter" class="field w-full">
              <option value="all">全部回复</option>
              <option value="unlabeled">未评</option>
              <option value="labeled">已评</option>
            </select>
          </label>
          <button class="button-secondary" type="button" :disabled="loading" @click="loadItems">
            {{ loading ? '刷新中...' : '刷新' }}
          </button>
          <button class="button-secondary" type="button" :disabled="exporting" @click="exportLabels">
            {{ exporting ? '导出中...' : '导出评分 CSV' }}
          </button>
        </div>
      </div>
      <div
        v-if="selectedDataset"
        class="mt-4 rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-500"
      >
        <p class="font-semibold text-slate-700">评审批次：{{ selectedDataset.label }}</p>
        <p>{{ selectedDataset.description || '当前批次暂无说明。' }}</p>
      </div>
      <p v-if="error" class="mt-4 rounded-lg border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {{ error }}
      </p>
      <p v-if="message" class="mt-4 rounded-lg border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
        {{ message }}
      </p>
    </section>

    <section v-if="selectedItem" class="space-y-5">
      <div class="panel space-y-5">
        <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <p class="section-eyebrow text-slate-500">主阅读区 · {{ selectedItem.problem_ref || '未记录题号' }}</p>
            <h3 class="mt-2 text-xl font-bold text-slate-900">
              {{ selectedItem.case_id }} · {{ progressText }}
            </h3>
            <p class="mt-2 text-sm leading-7 text-slate-500">
              AI 回复是主要判断对象；主体只负责读，底部只负责评。
            </p>
          </div>
          <span
            :class="[
              'rounded-full px-3 py-1 text-xs font-semibold',
              selectedItem.review_status === 'labeled' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500',
            ]"
          >
            {{ selectedItem.review_status === 'labeled' ? '已评' : '未评' }}
          </span>
        </div>

        <div class="grid gap-4 lg:grid-cols-2">
          <article class="rounded-2xl border border-slate-100 bg-slate-50 p-4">
            <p class="text-sm font-semibold text-slate-800">学生当前问题</p>
            <p class="mt-3 whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">
              {{ formatLongText(selectedItem.student_message) }}
            </p>
          </article>
          <article class="rounded-2xl border border-slate-100 bg-slate-50 p-4">
            <p class="text-sm font-semibold text-slate-800">题目/上下文</p>
            <p class="mt-3 whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">
              {{ formatLongText(selectedItem.problem_context) }}
            </p>
          </article>
        </div>

        <details class="group rounded-2xl border border-slate-100 bg-white p-4">
          <summary class="flex cursor-pointer list-none flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-sm font-semibold text-slate-800">近期对话</p>
              <p class="mt-1 text-xs text-slate-500 group-open:hidden">
                {{ formatLongText(selectedItem.recent_dialogue, 'N/A') === 'N/A' ? 'N/A' : '已折叠，展开后查看前文。' }}
              </p>
            </div>
            <span class="button-secondary text-center">
              <span class="group-open:hidden">展开近期对话</span>
              <span class="hidden group-open:inline">收起近期对话</span>
            </span>
          </summary>
          <p
            class="mt-3 max-h-[160px] overflow-y-auto whitespace-pre-wrap break-words pr-1 text-sm leading-7 text-slate-600"
          >
            {{ formatLongText(selectedItem.recent_dialogue) }}
          </p>
        </details>

        <article class="rounded-2xl border border-cyan-100 bg-cyan-50/40 p-5 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="text-sm font-semibold text-slate-900">AI 回复</p>
              <p class="mt-1 text-xs text-cyan-700">重点阅读这里，再到底部评分。</p>
            </div>
            <span class="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-cyan-700">
              {{ selectedItem.anonymized_response_id }}
            </span>
          </div>
          <div class="mt-3 max-h-[42vh] overflow-y-auto pr-1">
            <p class="whitespace-pre-wrap break-words text-base leading-8 text-slate-900">
              {{ formatLongText(selectedItem.response_text) }}
            </p>
          </div>
        </article>

        <div class="rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3 text-xs leading-6 text-amber-900">
          <span class="font-semibold">桥梁导向微型例子：</span>
          好的微型例子不是让学生完成一次临时填空，而是带着一个桥梁问题观察，并抽象成可迁移规则。
        </div>
      </div>
    </section>

    <section v-else class="panel">
      <p class="text-sm leading-7 text-slate-500">{{ loading ? '加载中...' : '暂无可盲评回复。' }}</p>
    </section>

    <form
      v-if="selectedItem"
      class="relative z-20 border-t border-slate-200 bg-white/95 px-3 py-3 shadow-[0_-16px_40px_rgba(15,23,42,0.14)] backdrop-blur lg:fixed lg:inset-x-0 lg:bottom-0 lg:z-40"
      @submit.prevent="saveCurrent()"
    >
      <div class="mx-auto max-w-7xl space-y-3">
        <div class="flex items-center justify-between gap-3">
          <p class="text-xs font-bold uppercase tracking-[0.18em] text-cyan-700">评分区 · 极速盲评</p>
          <button class="button-secondary shrink-0 px-3 py-2 text-xs" type="button" @click="showAdvancedOptions = !showAdvancedOptions">
            {{ showAdvancedOptions ? '收起高级选项' : '展开高级选项' }}
          </button>
        </div>

        <div v-if="showAdvancedOptions" class="grid gap-3 rounded-2xl border border-slate-100 bg-slate-50 p-3 sm:grid-cols-2 lg:grid-cols-[1fr_1fr_2fr]">
          <label class="block">
            <span class="text-xs font-semibold text-slate-600">同题排序</span>
            <select v-model="form.preference_rank" class="field mt-2">
              <option v-for="[value, label] in rankOptions" :key="value || 'empty'" :value="value">{{ label }}</option>
            </select>
          </label>
          <label class="block">
            <span class="text-xs font-semibold text-slate-600">评审状态</span>
            <select v-model="form.review_status" class="field mt-2">
              <option v-for="[value, label] in reviewStatusOptions" :key="value" :value="value">{{ label }}</option>
            </select>
          </label>
          <div class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs leading-5 text-slate-500">
            <p class="font-semibold text-slate-700">快捷键</p>
            <p>1 = 好，2 = 一般，3 = 差，4 = 不确定</p>
            <p>Q = 无泄露，W = 轻微，E = 严重，R = 答案/代码</p>
            <p>Enter = 保存并下一条，Space = 跳过</p>
          </div>
        </div>

        <div class="grid gap-3 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)_minmax(220px,0.8fr)_220px] xl:items-end">
          <div>
            <div class="mt-2 grid grid-cols-4 gap-2">
              <button
                v-for="[value, label, detail] in qualityOptions"
                :key="value"
                type="button"
                :title="detail"
                :class="[
                  'min-h-[52px] rounded-xl border px-2 text-sm font-bold transition',
                  form.overall_quality === value ? 'border-cyan-400 bg-cyan-50 text-cyan-900' : 'border-slate-200 bg-white text-slate-700',
                ]"
                @click="setQuality(value)"
              >
                {{ label }}
              </button>
            </div>
          </div>

          <div>
            <p class="text-xs font-semibold text-slate-600">泄露程度（默认无泄露）</p>
            <div class="mt-2 grid grid-cols-4 gap-2">
              <button
                v-for="[value, label, detail] in leakageOptions"
                :key="value"
                type="button"
                :title="detail"
                :class="[
                  'min-h-[44px] rounded-xl border px-2 text-xs font-bold transition',
                  form.leakage_label === value ? 'border-cyan-400 bg-cyan-50 text-cyan-900' : 'border-slate-200 bg-white text-slate-700',
                ]"
                @click="setLeakage(value)"
              >
                {{ label }}
              </button>
            </div>
          </div>

          <label class="block">
            <span class="text-xs font-semibold text-slate-600">一句备注</span>
            <textarea
              v-model="form.notes"
              class="field mt-2 min-h-[52px] resize-none"
              placeholder="可选：为什么好/坏，哪里需要讨论。"
            />
          </label>

          <div class="grid gap-2">
            <button class="button-primary w-full" type="submit" :disabled="saving">
              {{ saving ? '保存中...' : '保存并下一条' }}
            </button>
            <button class="button-secondary w-full" type="button" :disabled="saving" @click="saveWithoutNotes">
              不写备注，直接下一条
            </button>
            <div class="grid grid-cols-2 gap-2">
              <button class="button-secondary" type="button" :disabled="currentIndex <= 0" @click="goPrevious">
                上一条
              </button>
              <button class="button-secondary" type="button" :disabled="currentIndex >= items.length - 1" @click="goNext">
                跳过
              </button>
            </div>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>
