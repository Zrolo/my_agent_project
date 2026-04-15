const APP_VERSION = '0.5.0';

const MANUAL_REVIEW_RATE_LABELS = {
  mode_match_rate: 'mode 正确率',
  grounded_rate: '贴题率',
  can_move_next_rate: '可继续率',
};

const MANUAL_REVIEW_FILTER_LABELS = {
  mode: 'mode',
  family: 'family',
};

const TOPIC_L1_LABELS = {
  dp: '动态规划',
  basic: '算法基础',
  string: '字符串',
  data_structure: '数据结构',
  graph: '图论',
  search: '搜索',
  math: '数学',
  unknown: '未归类',
};

const TOPIC_L2_LABELS = {
  dp_basic: '基础 DP',
  binary_search: '二分',
  trie: 'Trie',
  segment_tree: '线段树',
  tree_diameter: '树的直径',
  complexity: '复杂度',
  difference_constraints: '差分约束',
  greedy: '贪心',
  enumeration: '枚举',
  method_selection: '方法选择',
  general_modeling: '一般建模',
  unknown: '未归类',
};

const BRIDGE_LABELS = {
  state_design: '状态设计',
  'dp.state_design': '状态设计',
  transition_design: '状态转移',
  'dp.transition_design': '状态转移',
  check_condition: '判定函数语义',
  'binary_search.check_condition': '判定函数语义',
  left_bound_update: '最左边界更新',
  'binary_search.left_bound': '最左边界更新',
  lazy_semantics: '懒标记语义',
  'segment_tree.lazy_semantics': '懒标记语义',
  shared_prefix_merging: '共享前缀合并',
  'string.trie.shared_prefix_merging': '共享前缀合并',
  complexity_fit: '复杂度判断',
  'modeling.scale_estimation': '复杂度判断',
  method_selection: '方法选择',
  'modeling.method_selection': '方法选择',
  tree_diameter_candidates: '直径候选分类',
  greedy_basis: '贪心依据',
  constraint_modeling: '约束建模',
  general_modeling: '一般建模',
  unknown: '未归类',
};

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function toFiniteNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatManualReviewRateValue(row = {}) {
  const count = toFiniteNumber(row.count);
  const total = toFiniteNumber(row.total);
  const rate = toFiniteNumber(row.rate);
  if (count !== null && total !== null && total > 0) {
    return `${count} / ${total} (${Math.round((count / total) * 1000) / 10}%)`;
  }
  if (rate !== null) {
    const normalizedRate = Math.abs(rate) <= 1 ? rate * 100 : rate;
    const roundedRate = Math.round(normalizedRate * 10) / 10;
    return `${roundedRate % 1 === 0 ? roundedRate.toFixed(0) : roundedRate.toFixed(1)}%`;
  }
  if (count !== null) return String(count);
  return '';
}

function normalizeManualReviewRateRow(item, fallbackKey = '') {
  if (item === null || item === undefined) return null;
  const isObject = typeof item === 'object' && !Array.isArray(item);
  const source = isObject ? item : { value: item };
  const primitiveValue = isObject ? null : item;
  const label = String(
    source.label
      || source.name
      || source.metric
      || source.title
      || MANUAL_REVIEW_RATE_LABELS[fallbackKey]
      || source.key
      || fallbackKey
      || '',
  ).trim();
  const count = toFiniteNumber(source.count ?? source.n ?? source.pass_count ?? source.ok_count);
  const total = toFiniteNumber(source.total ?? source.denominator ?? source.sample_size ?? source.all_count);
  let rate = toFiniteNumber(source.rate ?? source.ratio ?? source.percent ?? source.value ?? primitiveValue);
  if (rate === null && count !== null && total !== null && total > 0) {
    rate = count / total;
  }
  if (rate !== null && rate > 1 && rate <= 100) {
    rate /= 100;
  }
  const width = rate === null ? null : Math.max(0, Math.min(100, Math.round((rate <= 1 ? rate * 100 : rate) * 10) / 10));
  return {
    label,
    count,
    total,
    rate,
    displayValue: formatManualReviewRateValue({ count, total, rate }),
    width,
    note: String(source.note || source.description || '').trim(),
  };
}

function extractManualReviewRatesSource(data = {}) {
  return data.manual_review_rates
    || data.manual_review_rate_summary
    || data.manual_review_summary
    || data.manual_review_stats
    || data.manual_review_rate_stats
    || data.manual_review
    || null;
}

function normalizeManualReviewRates(source = {}) {
  const candidates = Array.isArray(source)
    ? source
    : Array.isArray(source?.rows)
      ? source.rows
      : Array.isArray(source?.items)
        ? source.items
        : Array.isArray(source?.metrics)
          ? source.metrics
          : Array.isArray(source?.data)
            ? source.data
            : null;
  if (candidates) {
    return candidates.map((item, index) => normalizeManualReviewRateRow(item, `第 ${index + 1} 项`)).filter(Boolean);
  }

  if (!source || typeof source !== 'object') return [];
  const preferredOrder = ['mode_match_rate', 'grounded_rate', 'can_move_next_rate'];
  const orderedKeys = [
    ...preferredOrder.filter((key) => Object.prototype.hasOwnProperty.call(source, key)),
    ...Object.keys(source).filter((key) => !preferredOrder.includes(key) && !['rows', 'items', 'metrics', 'data', 'summary'].includes(key)),
  ];
  return orderedKeys.map((key) => normalizeManualReviewRateRow(source[key], key)).filter(Boolean);
}

function renderManualReviewRateRow(row) {
  const barStyle = ` style="width: ${row.width === null ? 0 : row.width}%"`;
  const noteHtml = row.note ? `<div class="manual-review-rate-note">${escapeHtml(row.note)}</div>` : '';
  const meta = [];
  if (row.count !== null && row.total !== null) meta.push(`${row.count} / ${row.total}`);
  if (row.rate !== null) meta.push(`${Math.round(row.rate * 1000) / 10}%`);
  return `
        <div class="manual-review-rate-row">
            <div class="manual-review-rate-head">
                <div>
                    <div class="manual-review-rate-label">${escapeHtml(row.label || '未命名指标')}</div>
                    ${meta.length ? `<div class="manual-review-rate-meta">${escapeHtml(meta.join(' · '))}</div>` : ''}
                </div>
                <div class="manual-review-rate-value">${escapeHtml(row.displayValue || '暂无数据')}</div>
            </div>
            <div class="manual-review-rate-bar">
                <div class="manual-review-rate-fill"${barStyle}></div>
            </div>
            ${noteHtml}
        </div>
    `;
}

function renderManualReviewRatesCard(source = {}) {
  const rows = normalizeManualReviewRates(extractManualReviewRatesSource(source) || source);
  if (!rows.length) {
    return `
            <div class="teacher-card">
                <h4>人工复核统计</h4>
                <p>暂无人工复核统计数据</p>
            </div>
        `;
  }
  return `
        <div class="teacher-card">
            <h4>人工复核统计</h4>
            <div class="manual-review-rates-grid">
                ${rows.map(renderManualReviewRateRow).join('')}
            </div>
        </div>
    `;
}

function normalizeDistributionRows(source = {}, labelMap = {}) {
  if (!source || typeof source !== 'object') return [];
  return Object.entries(source)
    .map(([key, raw]) => {
      const item = raw && typeof raw === 'object' ? raw : { count: raw };
      const count = toFiniteNumber(item.count) ?? 0;
      const total = toFiniteNumber(item.total);
      let rate = toFiniteNumber(item.rate);
      if (rate === null && total && total > 0) rate = count / total;
      const width = rate === null ? 0 : Math.max(0, Math.min(100, Math.round((rate <= 1 ? rate * 100 : rate) * 10) / 10));
      return {
        key,
        label: labelMap[key] || key,
        count,
        total,
        rate,
        width,
        displayValue: formatManualReviewRateValue({ count, total, rate }),
      };
    })
    .filter((row) => row.count > 0 || row.total !== null || row.rate !== null);
}

function renderDistributionCard(title, source = {}, labelMap = {}) {
  const rows = normalizeDistributionRows(source, labelMap);
  if (!rows.length) {
    return `
            <div class="teacher-card">
                <h4>${escapeHtml(title)}</h4>
                <p>暂无数据</p>
            </div>
        `;
  }
  return `
        <div class="teacher-card">
            <h4>${escapeHtml(title)}</h4>
            <div class="manual-review-rates-grid">
                ${rows.map((row) => `
                    <div class="manual-review-rate-row">
                        <div class="manual-review-rate-head">
                            <div>
                                <div class="manual-review-rate-label">${escapeHtml(row.label)}</div>
                                <div class="manual-review-rate-meta">${escapeHtml(String(row.count))}${row.total !== null ? ` / ${escapeHtml(String(row.total))}` : ''}</div>
                            </div>
                            <div class="manual-review-rate-value">${escapeHtml(row.displayValue || String(row.count))}</div>
                        </div>
                        <div class="manual-review-rate-bar">
                            <div class="manual-review-rate-fill" style="width: ${row.width}%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderBridgeStatsCard(stats = {}) {
  return renderDistributionCard('高频知识桥分布', stats, BRIDGE_LABELS);
}

function renderKnowledgeBailoutStatsCard(stats = {}) {
  return renderDistributionCard('知识卡介入分布', stats, {
    entered: '进入知识卡',
    not_entered: '未进入知识卡',
  });
}

function renderTopicStatsCard(kind, stats = {}) {
  const title = kind === 'topic_l2' ? '知识子域分布' : '知识域分布';
  return renderDistributionCard(title, stats, kind === 'topic_l2' ? TOPIC_L2_LABELS : TOPIC_L1_LABELS);
}

function renderManualReviewBreakdownSection(title, groups = {}, groupBy = 'mode') {
  const entries = Object.entries(groups || {});
  if (!entries.length) {
    return `
            <div class="teacher-card">
                <h4>${escapeHtml(title || '人工复核细分统计')}</h4>
                <p>暂无细分统计数据</p>
            </div>
        `;
  }
  return `
        <div class="teacher-card">
            <h4>${escapeHtml(title || '人工复核细分统计')}</h4>
            <div class="manual-review-breakdown-grid">
                ${entries.map(([groupKey, stats]) => `
                    <button
                        type="button"
                        class="manual-review-breakdown-card"
                        data-action="open-manual-review-filter"
                        data-filter-kind="${escapeHtml(groupBy === 'family' ? 'family' : 'mode')}"
                        data-filter-value="${escapeHtml(groupKey)}"
                    >
                        <div class="manual-review-breakdown-title">${escapeHtml(groupKey)}</div>
                        <div class="manual-review-breakdown-meta">样本数 ${escapeHtml(String(stats?.reviewed_count ?? 0))}</div>
                        <div class="manual-review-rates-grid">
                            ${normalizeManualReviewRates({
                              mode_match_rate: stats?.mode_correct_rate ?? 0,
                              grounded_rate: stats?.grounded_rate ?? 0,
                              can_move_next_rate: stats?.student_can_move_next_rate ?? 0,
                            }).map(renderManualReviewRateRow).join('')}
                        </div>
                    </button>
                `).join('')}
            </div>
        </div>
    `;
}

function normalizeTeacherManualReviewFilter(filter = {}) {
  const kind = String(filter.kind || '').trim();
  const value = String(filter.value || '').trim();
  if (!kind || !value) return { kind: '', value: '' };
  if (!['mode', 'family'].includes(kind)) return { kind: '', value: '' };
  return { kind, value };
}

function filterTeacherReviewSamples(samples = [], filter = {}) {
  const normalized = normalizeTeacherManualReviewFilter(filter);
  if (!normalized.kind || !normalized.value) return Array.isArray(samples) ? samples : [];
  const fieldName = normalized.kind === 'mode' ? 'review_mode' : 'review_family';
  return (Array.isArray(samples) ? samples : []).filter((sample) => String(sample?.[fieldName] || '') === normalized.value);
}

function renderManualReviewFilterBanner(filter = {}) {
  const normalized = normalizeTeacherManualReviewFilter(filter);
  if (!normalized.kind || !normalized.value) return '';
  return `
        <div class="teacher-manual-review-filter-banner">
            <div>
                <div class="teacher-manual-review-filter-label">当前筛选</div>
                <div class="teacher-manual-review-filter-value">${escapeHtml(MANUAL_REVIEW_FILTER_LABELS[normalized.kind] || normalized.kind)}: ${escapeHtml(normalized.value)}</div>
            </div>
            <button type="button" class="secondary" data-action="clear-manual-review-filter">清除筛选</button>
        </div>
    `;
}

function buildReviewRequestSubmittedPayload(checkinResponse = {}, formState = {}) {
  return {
    checkin_id: Number(checkinResponse.checkin_id || checkinResponse.id || 0),
    session_id: checkinResponse.session_id || formState.session_id || '',
    event_name: 'review_request_submitted',
    client_ts: new Date().toISOString(),
    app_version: APP_VERSION,
    user_id: formState.user_id || '',
    problem_id: formState.problem_id || '',
    problem_title: formState.problem_title || '',
    review_mode: checkinResponse.review_mode || formState.review_mode || '',
    review_family: checkinResponse.review_family || formState.review_family || '',
    has_code: Boolean(formState.has_code),
    problem_context_length: Number(formState.problem_context_length || 0),
    bottleneck_text_length: Number(formState.bottleneck_text_length || 0),
  };
}

const teacherStatsUi = {
  buildReviewRequestSubmittedPayload,
  extractManualReviewRatesSource,
  filterTeacherReviewSamples,
  formatManualReviewRateValue,
  normalizeManualReviewRateRow,
  normalizeManualReviewRates,
  renderBridgeStatsCard,
  renderKnowledgeBailoutStatsCard,
  renderManualReviewBreakdownSection,
  renderManualReviewFilterBanner,
  renderManualReviewRateRow,
  renderManualReviewRatesCard,
  renderTopicStatsCard,
};

export {
  buildReviewRequestSubmittedPayload,
  extractManualReviewRatesSource,
  filterTeacherReviewSamples,
  formatManualReviewRateValue,
  normalizeManualReviewRateRow,
  normalizeManualReviewRates,
  renderBridgeStatsCard,
  renderKnowledgeBailoutStatsCard,
  renderManualReviewBreakdownSection,
  renderManualReviewFilterBanner,
  renderManualReviewRateRow,
  renderManualReviewRatesCard,
  renderTopicStatsCard,
};

export default teacherStatsUi;
