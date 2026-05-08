<script setup>
import { computed, onMounted, ref, watch } from 'vue';

import {
  exportTeacherBridgeAnnotations,
  getTeacherResearchAIChatSamples,
  saveTeacherBridgeAnnotation,
} from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();

const loading = ref(false);
const saving = ref(false);
const exporting = ref('');
const error = ref('');
const message = ref('');
const samples = ref([]);
const selectedSampleId = ref('');
const annotatedFilter = ref('all');
const pageSize = 12;
const currentPage = ref(1);

const studentStates = [
  ['text_comprehension_blocked', '题面读不懂'],
  ['problem_representation_unclear', '表征不清'],
  ['strategy_generation_blocked', '没有思路'],
  ['strategy_misconception', '思路误判'],
  ['strategy_application_gap', '思路落地卡住'],
  ['implementation_execution_gap', '代码实现卡住'],
  ['debugging_verification_gap', '调试验证卡住'],
  ['reflection_transfer_gap', '迁移总结卡住'],
];

const bridgeFamilies = [
  ['representation_bridge', '题意表征桥梁'],
  ['transition_bridge', '状态转移桥梁'],
  ['predicate_bridge', '条件判断桥梁'],
  ['modeling_bridge', '建模转化桥梁'],
  ['selection_bridge', '方法选择桥梁'],
  ['aggregation_bridge', '统计汇总桥梁'],
  ['ordering_bridge', '顺序组织桥梁'],
  ['mapping_bridge', '映射关系桥梁'],
  ['boundary_bridge', '边界细节桥梁'],
  ['complexity_bridge', '复杂度判断桥梁'],
  ['unknown_bridge', '暂不确定'],
];

const knownFocuses = [
  ['state_design', '状态设计'],
  ['transition_design', '转移设计'],
  ['check_condition', '条件判断'],
  ['enumeration_order', '枚举顺序'],
  ['greedy_basis', '贪心依据'],
  ['tree_path_difference', '树上路径差分'],
  ['tree_diameter_candidates', '树的直径候选'],
  ['lazy_semantics', '懒标记语义'],
  ['shared_prefix_merging', '公共前缀合并'],
  ['left_bound_update', '左边界更新'],
  ['general_modeling', '一般建模'],
  ['constraint_modeling', '约束建模'],
  ['method_selection', '方法选择'],
  ['complexity_fit', '复杂度匹配'],
  ['data_type', '数据类型'],
  ['loop_boundary', '循环边界'],
  ['recursion_structure', '递归结构'],
  ['boundary_debug', '边界调试'],
  ['implementation_debug', '实现调试'],
  ['unknown', '暂不确定/无法归类'],
];

const helpSeekingTypes = [
  ['instrumental_help', '参与式求助'],
  ['executive_help', '接管式求助'],
  ['help_avoidance', '回避求助'],
  ['unclear', '不确定'],
];

const helpLevels = [
  ['L1', 'L1 轻提示'],
  ['L2', 'L2 半步支架'],
  ['L3', 'L3 强支架'],
];

const confidenceOptions = [
  [0, '0 无法判断'],
  [1, '1 很不确定'],
  [2, '2 略有把握'],
  [3, '3 基本确定'],
  [4, '4 比较确定'],
  [5, '5 非常确定'],
];

const form = ref(emptyForm());

function emptyForm() {
  return {
    student_state: 'strategy_application_gap',
    bridge_family: 'unknown_bridge',
    known_focus: 'unknown',
    help_seeking_type: 'instrumental_help',
    missing_link: '',
    allowed_help_level: 'L2',
    forbidden_completion: '',
    needs_new_focus: false,
    confidence: 3,
    notes: '',
  };
}

const selectedSample = computed(() =>
  samples.value.find((sample) => sample.sample_id === selectedSampleId.value) || null,
);

const contextMessages = computed(() => {
  const sample = selectedSample.value;
  if (!sample) return [];
  if (Array.isArray(sample.context_messages) && sample.context_messages.length) {
    return sample.context_messages;
  }
  return [
    {
      id: sample.student_message_id,
      role: 'user',
      content: sample.student_message,
      created_at: sample.created_at,
      is_current_student: true,
      is_target_assistant: false,
    },
    {
      id: sample.assistant_message_id || `${sample.student_message_id}-assistant`,
      role: 'assistant',
      content: sample.assistant_reply || '这一轮还没有后续 AI 回复。',
      created_at: sample.created_at,
      is_current_student: false,
      is_target_assistant: true,
    },
  ];
});

const annotatedCount = computed(() => samples.value.filter((sample) => sample.annotated).length);
const totalPages = computed(() => Math.max(1, Math.ceil(samples.value.length / pageSize)));
const pageStart = computed(() => (currentPage.value - 1) * pageSize);
const pageEnd = computed(() => Math.min(samples.value.length, pageStart.value + pageSize));
const pagedSamples = computed(() => samples.value.slice(pageStart.value, pageEnd.value));

function formatTime(value) {
  if (!value) return '暂无时间';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString('zh-CN', { hour12: false });
}

function shortText(value, max = 64) {
  const text = String(value || '').replace(/\s+/g, ' ').trim();
  if (text.length <= max) return text;
  return `${text.slice(0, max)}...`;
}

function contextRoleLabel(role) {
  return role === 'assistant' ? 'AIChat' : '学生';
}

function contextBadgeLabel(message) {
  if (message.is_current_student) return '当前学生轮次';
  if (message.is_target_assistant) return '对应 AI 回复';
  return contextRoleLabel(message.role);
}

function selectedSampleIndex() {
  return samples.value.findIndex((sample) => sample.sample_id === selectedSampleId.value);
}

function clampCurrentPage() {
  if (currentPage.value > totalPages.value) currentPage.value = totalPages.value;
  if (currentPage.value < 1) currentPage.value = 1;
}

function goToPage(page) {
  currentPage.value = Math.max(1, Math.min(Number(page) || 1, totalPages.value));
}

function loadFormFromSample(sample) {
  if (!sample) {
    form.value = emptyForm();
    return;
  }
  form.value = {
    student_state: sample.student_state || 'strategy_application_gap',
    bridge_family: sample.bridge_family || 'unknown_bridge',
    known_focus: sample.known_focus || 'unknown',
    help_seeking_type: sample.help_seeking_type || 'instrumental_help',
    missing_link: sample.missing_link || '',
    allowed_help_level: sample.allowed_help_level || 'L2',
    forbidden_completion: sample.forbidden_completion || '',
    needs_new_focus: Boolean(sample.needs_new_focus),
    confidence: Number(sample.confidence || 3),
    notes: sample.notes || '',
  };
}

async function loadSamples() {
  loading.value = true;
  error.value = '';
  message.value = '';
  try {
    const payload = await getTeacherResearchAIChatSamples(auth.token, {
      limit: 200,
      annotated: annotatedFilter.value,
    });
    samples.value = payload.samples || [];
    clampCurrentPage();
    if (!samples.value.some((sample) => sample.sample_id === selectedSampleId.value)) {
      selectedSampleId.value = samples.value[0]?.sample_id || '';
      currentPage.value = 1;
    }
    loadFormFromSample(selectedSample.value);
  } catch (err) {
    error.value = err.message || '加载研究样本失败';
  } finally {
    loading.value = false;
  }
}

function selectSample(sampleId) {
  selectedSampleId.value = sampleId;
  loadFormFromSample(selectedSample.value);
}

function selectNextSample() {
  if (!samples.value.length) return;
  const currentIndex = selectedSampleIndex();
  const nextIndex = Math.min(samples.value.length - 1, Math.max(0, currentIndex + 1));
  const nextSample = samples.value[nextIndex];
  if (!nextSample) return;
  selectedSampleId.value = nextSample.sample_id;
  currentPage.value = Math.floor(nextIndex / pageSize) + 1;
  loadFormFromSample(nextSample);
}

async function saveAnnotation() {
  const sample = selectedSample.value;
  if (!sample) return;
  saving.value = true;
  error.value = '';
  message.value = '';
  try {
    const payload = await saveTeacherBridgeAnnotation(auth.token, {
      sample_id: sample.sample_id,
      student_message_id: sample.student_message_id,
      ...form.value,
      confidence: Number(form.value.confidence || 0),
    });
    const annotation = payload.annotation || {};
    samples.value = samples.value.map((item) => {
      if (item.sample_id !== sample.sample_id) return item;
      return {
        ...item,
        annotated: true,
        student_state: annotation.student_state,
        bridge_family: annotation.bridge_family,
        known_focus: annotation.known_focus,
        help_seeking_type: annotation.help_seeking_type,
        missing_link: annotation.missing_link,
        allowed_help_level: annotation.allowed_help_level,
        forbidden_completion: annotation.forbidden_completion,
        needs_new_focus: annotation.needs_new_focus,
        confidence: annotation.confidence,
        notes: annotation.notes,
      };
    });
    message.value = '标注已保存';
    selectNextSample();
  } catch (err) {
    error.value = err.message || '保存标注失败';
  } finally {
    saving.value = false;
  }
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

async function exportAnnotations(format) {
  exporting.value = format;
  error.value = '';
  message.value = '';
  try {
    const text = await exportTeacherBridgeAnnotations(auth.token, format);
    const stamp = new Date().toISOString().slice(0, 19).replaceAll(/[-:T]/g, '');
    downloadText(
      text,
      `bridge_annotations_${stamp}.${format === 'csv' ? 'csv' : 'jsonl'}`,
      format === 'csv' ? 'text/csv;charset=utf-8' : 'application/x-ndjson;charset=utf-8',
    );
    message.value = '导出已生成';
  } catch (err) {
    error.value = err.message || '导出失败';
  } finally {
    exporting.value = '';
  }
}

watch(annotatedFilter, () => {
  currentPage.value = 1;
  loadSamples();
});
onMounted(loadSamples);
</script>

<template>
  <div class="space-y-6">
    <section class="panel">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p class="section-eyebrow text-cyan-700">BridgeBench-CP</p>
          <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">AIChat 研究标注</h3>
          <p class="mt-2 text-sm leading-7 text-slate-500">
            {{ samples.length }} 条样本，当前列表已标注 {{ annotatedCount }} 条。
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <select v-model="annotatedFilter" class="field min-w-[140px]">
            <option value="all">全部样本</option>
            <option value="unannotated">未标注</option>
            <option value="annotated">已标注</option>
          </select>
          <button class="button-secondary" type="button" :disabled="loading" @click="loadSamples">
            {{ loading ? '刷新中...' : '刷新' }}
          </button>
          <button class="button-secondary" type="button" :disabled="Boolean(exporting)" @click="exportAnnotations('jsonl')">
            {{ exporting === 'jsonl' ? '导出中...' : '导出 JSONL' }}
          </button>
          <button class="button-secondary" type="button" :disabled="Boolean(exporting)" @click="exportAnnotations('csv')">
            {{ exporting === 'csv' ? '导出中...' : '导出 CSV' }}
          </button>
        </div>
      </div>
      <p v-if="error" class="mt-4 rounded-lg border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {{ error }}
      </p>
      <p v-if="message" class="mt-4 rounded-lg border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
        {{ message }}
      </p>
    </section>

    <section class="panel">
      <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="section-eyebrow text-slate-500">样本选择</p>
          <p class="mt-1 text-sm text-slate-500">
            第 {{ currentPage }} / {{ totalPages }} 页，显示 {{ pageStart + 1 }}-{{ pageEnd }} 条
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button class="button-secondary" type="button" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
            上一页
          </button>
          <button class="button-secondary" type="button" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
            下一页
          </button>
        </div>
      </div>

      <div class="mt-4 max-h-[360px] overflow-y-auto pr-1">
        <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          <button
            v-for="sample in pagedSamples"
            :key="sample.sample_id"
            type="button"
            :class="[
              'w-full rounded-lg border p-3 text-left transition',
              selectedSampleId === sample.sample_id
                ? 'border-cyan-300 bg-cyan-50'
                : 'border-slate-100 bg-white hover:border-cyan-200',
            ]"
            @click="selectSample(sample.sample_id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-sm font-semibold text-slate-900">{{ sample.problem_ref || '未记录题号' }}</p>
                <p class="mt-1 text-xs text-slate-400">{{ formatTime(sample.created_at) }}</p>
              </div>
              <span
                :class="[
                  'rounded-full px-2 py-1 text-xs font-semibold',
                  sample.annotated ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500',
                ]"
              >
                {{ sample.annotated ? '已标注' : '未标注' }}
              </span>
            </div>
            <p class="mt-2 text-sm leading-6 text-slate-600">{{ shortText(sample.student_message, 54) }}</p>
          </button>
        </div>
      </div>
      <p v-if="!loading && !samples.length" class="mt-4 text-sm leading-7 text-slate-500">暂无可标注样本。</p>
    </section>

    <main v-if="selectedSample" class="space-y-6">
      <section class="panel">
        <div class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <p class="section-eyebrow text-slate-500">{{ selectedSample.problem_ref || '未记录题号' }}</p>
            <h3 class="mt-2 font-display text-2xl font-bold text-slate-900">
              {{ selectedSample.problem_title || '未记录题目' }}
            </h3>
          </div>
          <p class="text-sm text-slate-400">{{ selectedSample.sample_id }}</p>
        </div>

        <div class="mt-5 rounded-lg border border-slate-100 bg-slate-50/70 p-4">
          <div class="flex flex-col gap-1 md:flex-row md:items-end md:justify-between">
            <div>
              <p class="text-sm font-semibold text-slate-800">上下文窗口</p>
              <p class="mt-1 text-xs leading-5 text-slate-500">标注当前这一轮，但判断时结合前后文；蓝色是当前要标注的学生轮次。</p>
            </div>
            <p class="text-xs text-slate-400">同一 session 最近对话</p>
          </div>
          <div class="mt-4 max-h-[520px] overflow-y-auto space-y-3 pr-1">
            <article
              v-for="message in contextMessages"
              :key="message.id"
              :class="[
                'rounded-lg border bg-white p-4',
                message.is_current_student
                  ? 'border-cyan-300 bg-cyan-50/80'
                  : message.is_target_assistant
                    ? 'border-emerald-200 bg-emerald-50/70'
                    : 'border-slate-100',
              ]"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span
                  :class="[
                    'rounded-full px-2.5 py-1 text-xs font-semibold',
                    message.is_current_student
                      ? 'bg-cyan-600 text-white'
                      : message.is_target_assistant
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-slate-100 text-slate-600',
                  ]"
                >
                  {{ contextBadgeLabel(message) }}
                </span>
                <span class="text-xs text-slate-400">{{ formatTime(message.created_at) }}</span>
              </div>
              <p class="mt-3 whitespace-pre-wrap break-words text-sm leading-7 text-slate-800">{{ message.content }}</p>
            </article>
          </div>
        </div>
      </section>

      <form class="panel space-y-5" @submit.prevent="saveAnnotation">
          <div>
            <p class="section-eyebrow text-cyan-700">Coach Label</p>
            <h3 class="mt-2 font-display text-xl font-bold text-slate-900">专家标注</h3>
          </div>

          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <label class="block">
              <span class="text-sm font-semibold text-slate-700">学生状态</span>
              <select v-model="form.student_state" class="field mt-2 w-full">
                <option v-for="[value, label] in studentStates" :key="value" :value="value">{{ label }}</option>
              </select>
            </label>

            <label class="block">
              <span class="text-sm font-semibold text-slate-700">桥梁类型</span>
              <p class="mt-1 text-xs leading-5 text-slate-500">学生缺的是哪一类“从当前理解走到下一步”的过渡能力。</p>
              <select v-model="form.bridge_family" class="field mt-2 w-full">
                <option v-for="[value, label] in bridgeFamilies" :key="value" :value="value">{{ label }}</option>
              </select>
            </label>

            <label class="block">
              <span class="text-sm font-semibold text-slate-700">已知知识点/关注点</span>
              <p class="mt-1 text-xs leading-5 text-slate-500">如果这条卡点能归到已有教学关注点，就在这里选择。</p>
              <select v-model="form.known_focus" class="field mt-2 w-full">
                <option v-for="[value, label] in knownFocuses" :key="value" :value="value">{{ label }}</option>
              </select>
            </label>

            <label class="block">
              <span class="text-sm font-semibold text-slate-700">求助类型</span>
              <select v-model="form.help_seeking_type" class="field mt-2 w-full">
                <option v-for="[value, label] in helpSeekingTypes" :key="value" :value="value">{{ label }}</option>
              </select>
            </label>
          </div>

          <div class="grid gap-4 lg:grid-cols-2">
            <label class="block">
              <span class="text-sm font-semibold text-slate-700">学生缺的关键一步</span>
              <p class="mt-1 text-xs leading-5 text-slate-500">
                写学生现在差的那一小步，而不是写完整解法。
              </p>
              <textarea
                v-model="form.missing_link"
                class="field mt-2 min-h-[120px] w-full resize-y"
                placeholder="例：已经知道要排序，但还不能解释为什么优先选小的能让数量最多。"
                required
              />
            </label>

            <label class="block">
              <span class="text-sm font-semibold text-slate-700">AI 不应直接给出的部分</span>
              <p class="mt-1 text-xs leading-5 text-slate-500">
                写为了保持脚手架教学，AI 这一轮不能直接替学生完成什么。
              </p>
              <textarea
                v-model="form.forbidden_completion"
                class="field mt-2 min-h-[120px] w-full resize-y"
                placeholder="例：不要直接给完整代码；不要直接写出 sort(a + 1, a + n + 1) 和最终循环。"
                required
              />
            </label>
          </div>

          <div class="grid gap-3 sm:grid-cols-4">
            <label class="block">
              <span class="text-sm font-semibold text-slate-700">本轮建议帮助强度</span>
              <p class="mt-1 text-xs leading-5 text-slate-500">
                只判断当前这一轮学生消息下 AI 应给到多强脚手架；下一轮可根据学生理解变化升降级。
              </p>
              <select v-model="form.allowed_help_level" class="field mt-2 w-full">
                <option v-for="[value, label] in helpLevels" :key="value" :value="value">{{ label }}</option>
              </select>
            </label>
            <label class="block">
              <span class="text-sm font-semibold text-slate-700">标注把握度</span>
              <p class="mt-1 text-xs leading-5 text-slate-500">这是教练对本次标注的确定程度，不是 AI 的自信程度。</p>
              <select v-model.number="form.confidence" class="field mt-2 w-full">
                <option v-for="[value, label] in confidenceOptions" :key="value" :value="value">{{ label }}</option>
              </select>
            </label>
            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3">
              <input v-model="form.needs_new_focus" class="h-4 w-4 rounded border-slate-300 text-cyan-600" type="checkbox" />
              <span>
                <span class="block text-sm font-semibold text-slate-700">发现新的知识点/问题类型</span>
                <span class="mt-1 block text-xs leading-5 text-slate-500">现有关注点无法准确覆盖时勾选。</span>
              </span>
            </label>
            <label class="block sm:col-span-1">
              <span class="text-sm font-semibold text-slate-700">备注</span>
              <input v-model="form.notes" class="field mt-2 w-full" placeholder="可选：写判断依据或特殊情况" />
            </label>
          </div>

          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <button class="button-secondary" type="button" @click="selectNextSample">跳过到下一条</button>
            <button class="button-primary justify-center sm:min-w-[180px]" type="submit" :disabled="saving">
              {{ saving ? '保存中...' : '保存并下一条' }}
            </button>
          </div>
      </form>
    </main>

    <section v-else class="panel">
      <p class="text-sm leading-7 text-slate-500">请选择一条样本。</p>
    </section>
  </div>
</template>
