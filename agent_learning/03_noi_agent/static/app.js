// NOI Agent 前端逻辑 - v0.5.0

const API_BASE = window.location.origin;
const APP_VERSION = window.NOI_APP_VERSION || '0.5.0';
const PENDING_REVIEW_POLL_FAST_INTERVAL_MS = 2000;
const PENDING_REVIEW_POLL_SLOW_INTERVAL_MS = 5000;
const PENDING_REVIEW_POLL_FAST_ATTEMPTS = 3;
const PENDING_REVIEW_POLL_TIMEOUT_MS = 60000;
const CHAT_CONTEXT_STORE_PREFIX = 'noi_chat_context_store';
const reviewFamilyUi = window.reviewFamilyUi || {
    resolveReviewFamily(item = {}) {
        if (item.review_family) return item.review_family;
        return item.review_mode === 'independent_reflect' ? 'success_reflection' : 'failure_diagnosis';
    },
    orderedReviewSections(review = {}, family = 'failure_diagnosis') {
        const order = family === 'success_reflection'
            ? ['main_block', 'key_bridge', 'transfer_signal', 'next_step']
            : ['main_block', 'key_bridge', 'next_step', 'transfer_signal'];
        const labels = {
            main_block: '你卡在哪',
            key_bridge: '关键一步',
            next_step: '现在先做',
            transfer_signal: '下次提醒',
        };
        return order.map((field) => ({ field, label: labels[field] || field, value: review[field] || '' }));
    },
    reviewFeedbackCopy(family = 'failure_diagnosis') {
        if (family === 'success_reflection') {
            return {
                title: '看完上面的解释，你现在能说清为什么这样做对了吗？',
                clearLabel: '我能自己说清为什么这样做对',
                guessedLabel: '大概明白，但还说不顺',
                confusedLabel: '还是说不清为什么对',
            };
        }
        return {
            title: '看完上面的解释，你现在知道先查哪一步了吗？',
            clearLabel: '我知道先查哪一步了',
            guessedLabel: '大概知道，但还不稳',
            confusedLabel: '还是不知道从哪下手',
        };
    },
    reviewWorkspaceSubtitle(item = {}) {
        if (item.review_status === 'failed') return '这条打卡的复盘生成失败了，你可以在右侧直接重新生成。';
        if (item.poll_timed_out) return '这条打卡的复盘生成时间较长，你可以先刷新或稍后回来查看。';
        if (item.review_status !== 'completed') return '这条打卡的复盘还在生成，生成完成后会自动更新到这里。';
        return this.resolveReviewFamily(item) === 'success_reflection'
            ? '右侧先看为什么这道题这样做对，再用中间的小测确认你能不能把这条思路说清楚。'
            : '右侧先看问题定位和最小下一步，再用中间的小测确认你知不知道该先查哪一步。';
    },
};
const checkinReviewUi = window.checkinReviewUi;
const teacherManualReviewUi = window.teacherManualReviewUi || {
    renderTeacherReviewSamplesPanel(samples = []) {
        return samples.length ? '<div></div>' : '<p>暂无可复核的 review 样本</p>';
    },
    buildTeacherManualReviewPayload(form) {
        return {
            mode_correct: form.elements.mode_correct.value,
            review_grounded: form.elements.review_grounded.value,
            student_can_move_next: form.elements.student_can_move_next.value,
            notes: String(form.elements.notes.value || '').trim(),
        };
    },
};

// 状态
let sessionId = localStorage.getItem('noi_session_id') || generateSessionId();
let authToken = localStorage.getItem('noi_auth_token') || '';
let currentUserId = localStorage.getItem('noi_user_id') || localStorage.getItem('noi_student_id') || '';
let problemId = localStorage.getItem('noi_problem_id') || 'P1001';
let userRole = localStorage.getItem('noi_user_role') || '';
let importedProblemMeta = {
    imported: false,
    problemPid: '',
    problemUrl: '',
    problemTags: [],
};
let luoguSupplementExpanded = false;
let myCheckinsCache = [];
let activeCheckinId = null;
let activeRelatedProblemPid = '';
let activeChatProblemRef = '';
let teacherReviewSamplesCache = [];
let teacherManualReviewFilter = { kind: '', value: '' };
const pendingReviewPolls = new Map();
const pendingReviewStreams = new Map();
const sentReviewEventKeys = new Set();

// DOM 元素
const loginSection = document.getElementById('login-section');
const studentSection = document.getElementById('student-section');
const teacherSection = document.getElementById('teacher-section');
const userBar = document.getElementById('user-bar');

// ============ 工具函数 ============

function generateSessionId() {
    return 'sess_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

function persistAuthState() {
    localStorage.setItem('noi_auth_token', authToken);
    localStorage.setItem('noi_user_id', currentUserId);
    localStorage.setItem('noi_user_role', userRole);
    localStorage.setItem('noi_problem_id', problemId);
    localStorage.setItem('noi_session_id', sessionId);
}

function chatContextStoreKey() {
    return `${CHAT_CONTEXT_STORE_PREFIX}:${currentUserId || 'anonymous'}`;
}

function loadChatContextStore() {
    try {
        return JSON.parse(localStorage.getItem(chatContextStoreKey()) || '{}');
    } catch (err) {
        return {};
    }
}

function saveChatContextStore(store) {
    localStorage.setItem(chatContextStoreKey(), JSON.stringify(store || {}));
}

function normalizeProblemRef(value) {
    const raw = String(value || '').trim();
    if (!raw) return '';
    const luoguMatch = raw.match(/\/problem\/([A-Za-z0-9_]+)/i) || raw.match(/\/problemnew\/show\/([A-Za-z0-9_]+)/i);
    if (luoguMatch) {
        return luoguMatch[1].toUpperCase();
    }
    if (/^[A-Za-z][A-Za-z0-9_]*$/.test(raw)) {
        return raw.toUpperCase();
    }
    return raw;
}

function cleanChatSnippet(text, limit = 140) {
    const normalized = String(text || '')
        .replace(/```[\s\S]*?```/g, '[代码]')
        .replace(/`([^`\n]+)`/g, '$1')
        .replace(/\s+/g, ' ')
        .trim();
    if (normalized.length <= limit) return normalized;
    return `${normalized.slice(0, Math.max(0, limit - 1))}…`;
}

function buildChatContextSummary(question, answer) {
    const questionSnippet = cleanChatSnippet(question, 90);
    const answerSnippet = cleanChatSnippet(answer, 140);
    if (!questionSnippet && !answerSnippet) return '';
    if (!answerSnippet) return `最近问到：${questionSnippet}`;
    if (!questionSnippet) return `最近 AI 提醒：${answerSnippet}`;
    return `最近问到：${questionSnippet}；AI 重点回答：${answerSnippet}`;
}

function buildProblemChatContextRecord(problemRef, question, answer, handoffPayload = null) {
    const normalizedRef = normalizeProblemRef(problemRef);
    if (!normalizedRef) return null;
    const record = {
        problemRef: normalizedRef,
        summary: buildChatContextSummary(question, answer),
        question: cleanChatSnippet(question, 120),
        answer: cleanChatSnippet(answer, 180),
        updatedAt: new Date().toISOString(),
    };
    if (handoffPayload && typeof handoffPayload === 'object') {
        record.handoffPayload = handoffPayload;
    }
    return record;
}

function rememberProblemChatContext(problemRef, question, answer, handoffPayload = null) {
    const record = buildProblemChatContextRecord(problemRef, question, answer, handoffPayload);
    if (!record) return;
    const store = loadChatContextStore();
    store[record.problemRef] = record;
    saveChatContextStore(store);
}

function removeProblemChatContext(problemRef) {
    const normalizedRef = normalizeProblemRef(problemRef);
    if (!normalizedRef) return;
    const store = loadChatContextStore();
    if (store[normalizedRef]) {
        delete store[normalizedRef];
        saveChatContextStore(store);
    }
}

function getProblemChatContext(problemRef) {
    const normalizedRef = normalizeProblemRef(problemRef);
    if (!normalizedRef) return null;
    return loadChatContextStore()[normalizedRef] || null;
}

function resolveCurrentCheckinProblemRef() {
    if (importedProblemMeta.problemPid) return normalizeProblemRef(importedProblemMeta.problemPid);
    const urlValue = document.getElementById('checkin-url')?.value.trim() || '';
    const normalizedUrlRef = normalizeProblemRef(urlValue);
    if (normalizedUrlRef) return normalizedUrlRef;

    const titleValue = document.getElementById('checkin-title')?.value.trim() || '';
    const titleMatch = titleValue.match(/\b([A-Za-z][A-Za-z0-9_]*)\b/);
    if (titleMatch) return normalizeProblemRef(titleMatch[1]);
    const studentProblemInput = document.getElementById('student-problem-id')?.value.trim() || problemId;
    return normalizeProblemRef(studentProblemInput);
}

function formatRelativeTimeLabel(timestamp) {
    if (!timestamp) return '';
    const deltaMs = Date.now() - new Date(timestamp).getTime();
    if (!Number.isFinite(deltaMs)) return '';
    const deltaMinutes = Math.max(1, Math.round(deltaMs / 60000));
    if (deltaMinutes < 60) return `${deltaMinutes} 分钟前`;
    const deltaHours = Math.round(deltaMinutes / 60);
    if (deltaHours < 24) return `${deltaHours} 小时前`;
    const deltaDays = Math.round(deltaHours / 24);
    return `${deltaDays} 天前`;
}

const MANUAL_REVIEW_RATE_LABELS = {
    mode_match_rate: 'mode 正确率',
    grounded_rate: '贴题率',
    can_move_next_rate: '可继续率',
};
const MANUAL_REVIEW_BREAKDOWN_TITLES = {
    mode: '人工复核（按 mode 细分）',
    family: '人工复核（按 family 细分）',
};
const MANUAL_REVIEW_FILTER_LABELS = {
    mode: 'mode',
    family: 'family',
};

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
    if (count !== null) {
        return String(count);
    }
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
        rate = rate / 100;
    }
    const displayValue = formatManualReviewRateValue({ count, total, rate });
    const width = rate === null ? null : Math.max(0, Math.min(100, Math.round((rate <= 1 ? rate * 100 : rate) * 10) / 10));
    const note = String(source.note || source.description || '').trim();
    return {
        label,
        count,
        total,
        rate,
        displayValue,
        width,
        note,
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
    return orderedKeys
        .map((key) => normalizeManualReviewRateRow(source[key], key))
        .filter(Boolean);
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

function renderTeacherManualReviewPanel(samples = []) {
    const filterEl = document.getElementById('teacher-manual-review-filter');
    const panelEl = document.getElementById('teacher-manual-review-panel');
    if (!panelEl) return;
    if (filterEl) {
        filterEl.innerHTML = renderManualReviewFilterBanner(teacherManualReviewFilter);
    }
    if (!samples.length) {
        panelEl.innerHTML = '<p>暂无可复核的 review 样本</p>';
        return;
    }
    const filtered = filterTeacherReviewSamples(samples, teacherManualReviewFilter);
    if (!filtered.length) {
        panelEl.innerHTML = '<p class="teacher-review-empty">当前筛选下暂无样本</p>';
        return;
    }
    panelEl.innerHTML = teacherManualReviewUi.renderTeacherReviewSamplesPanel(filtered);
}

function setTeacherManualReviewFilter(filter = {}) {
    teacherManualReviewFilter = normalizeTeacherManualReviewFilter(filter);
    renderTeacherManualReviewPanel(teacherReviewSamplesCache);
}

function clearAuthState() {
    authToken = '';
    currentUserId = '';
    userRole = '';
    sessionId = generateSessionId();

    [
        'noi_auth_token',
        'noi_user_id',
        'noi_user_role',
        'noi_problem_id',
        'noi_session_id',
        'noi_student_id',
    ].forEach((key) => localStorage.removeItem(key));
}

function redirectToLogin(message = '登录已失效，请重新登录') {
    clearAuthState();
    myCheckinsCache = [];
    activeCheckinId = null;
    activeRelatedProblemPid = '';
    activeChatProblemRef = '';
    teacherReviewSamplesCache = [];

    document.getElementById('chat-history').innerHTML = '';
    document.getElementById('quota-info').textContent = '';
    document.getElementById('teacher-quota-result').textContent = '';
    document.getElementById('reset-result').textContent = '';
    document.getElementById('checkin-history-list').innerHTML = '';
    document.getElementById('teacher-checkins-list').innerHTML = '';
    document.getElementById('error-stats').innerHTML = '';
    document.getElementById('usage-stats').innerHTML = '';
    document.getElementById('student-flags').innerHTML = '';
    document.getElementById('checkin-result').innerHTML = '';
    document.getElementById('checkin-result').classList.add('hidden');
    document.getElementById('active-review-quiz-slot').innerHTML = '';
    document.getElementById('active-review-report').innerHTML = '';
    document.getElementById('active-review-related').innerHTML = '';
    document.getElementById('teacher-manual-review-panel').innerHTML = '';
    document.getElementById('retry-pending-result').textContent = '';
    document.getElementById('retry-problem-analysis-result').textContent = '';
    document.getElementById('problem-analysis-failures').innerHTML = '';
    document.getElementById('login-password').value = '';

    loginSection.classList.remove('hidden');
    studentSection.classList.add('hidden');
    teacherSection.classList.add('hidden');
    userBar.classList.add('hidden');
    setReviewStageEmpty();
    showError('login-error', message);
}

function isLikelyLuoguProblemRef(value) {
    if (!value) return false;
    const raw = value.trim();
    return /^[A-Za-z][A-Za-z0-9_]*$/.test(raw) ||
        /^https?:\/\/(?:www\.)?luogu\.(?:com\.cn|com)\/(?:problem|problemnew\/show)\/[A-Za-z0-9_]+(?:[/?#].*)?$/i.test(raw);
}

function resetImportedProblemMeta() {
    importedProblemMeta = {
        imported: false,
        problemPid: '',
        problemUrl: '',
        problemTags: [],
    };
    luoguSupplementExpanded = false;
}

function updateProblemTagsPreview(tags = []) {
    const previewEl = document.getElementById('problem-tags-preview');
    if (!previewEl) return;
    const cleanTags = (tags || []).filter(Boolean);
    if (!cleanTags.length) {
        previewEl.classList.add('hidden');
        previewEl.textContent = '';
        return;
    }
    previewEl.classList.remove('hidden');
    previewEl.textContent = `已识别标签：${cleanTags.join(' / ')}`;
}

function setProblemImportStatus(message, tone = 'neutral') {
    const statusEl = document.getElementById('problem-import-status');
    if (!statusEl) return;
    statusEl.textContent = message;
    if (tone === 'success') {
        statusEl.style.color = '#1e8449';
    } else if (tone === 'error') {
        statusEl.style.color = '#c0392b';
    } else if (tone === 'warn') {
        statusEl.style.color = '#b9770e';
    } else {
        statusEl.style.color = '#666';
    }
}

function setLuoguSupplementExpanded(expanded) {
    luoguSupplementExpanded = Boolean(expanded);
    const groupEl = document.getElementById('problem-context-group');
    const toggleRowEl = document.getElementById('luogu-context-toggle-row');
    const toggleBtn = document.getElementById('toggle-luogu-context-btn');
    if (groupEl) {
        groupEl.classList.toggle('hidden', !luoguSupplementExpanded);
    }
    if (toggleRowEl) {
        toggleRowEl.classList.toggle('hidden', false);
    }
    if (toggleBtn) {
        toggleBtn.textContent = luoguSupplementExpanded
            ? '收起题意补充（可选）'
            : '补充我对题意的理解（可选）';
    }
}

function syncCheckinSourceInputs() {
    const ojSelect = document.getElementById('checkin-oj');
    const importGroup = document.getElementById('luogu-import-group');
    const toggleRowEl = document.getElementById('luogu-context-toggle-row');
    const contextGroupEl = document.getElementById('problem-context-group');
    const contextLabelEl = document.getElementById('problem-context-label');
    const contextHintEl = document.getElementById('context-hint');
    const requiredFlagEl = document.getElementById('context-required-flag');
    const contextInput = document.getElementById('checkin-problem-context');
    const urlInput = document.getElementById('checkin-url');
    if (!ojSelect) return;

    const isLuogu = ojSelect.value === 'luogu';
    const hasValidLuoguRef = isLuogu && isLikelyLuoguProblemRef(urlInput?.value.trim() || '');
    const canAutoUseOfficialStatement = isLuogu && (importedProblemMeta.imported || hasValidLuoguRef);
    if (importGroup) {
        importGroup.classList.toggle('hidden', !isLuogu);
    }
    if (!isLuogu) {
        luoguSupplementExpanded = false;
        if (toggleRowEl) toggleRowEl.classList.add('hidden');
        if (contextGroupEl) contextGroupEl.classList.remove('hidden');
        if (contextLabelEl) contextLabelEl.textContent = '题面 / Markdown';
        if (requiredFlagEl) {
            requiredFlagEl.textContent = '（必填）';
            requiredFlagEl.style.color = '#e74c3c';
        }
        if (contextHintEl) {
            contextHintEl.textContent = '至少10字，支持直接粘贴题面文本或 Markdown';
            contextHintEl.style.color = '#666';
        }
        if (contextInput) {
            contextInput.placeholder = '直接粘贴题面正文、网页复制内容或 Markdown。\n建议至少包含：题意、输入输出、样例或关键约束。';
        }
        setProblemImportStatus('当前仅在选择“洛谷”时支持自动导入标题、题面和标签。');
        updateProblemTagsPreview([]);
        resetImportedProblemMeta();
    } else {
        if (contextLabelEl) {
            contextLabelEl.textContent = canAutoUseOfficialStatement ? '题意补充' : '题面 / Markdown';
        }
        if (requiredFlagEl) {
            requiredFlagEl.textContent = canAutoUseOfficialStatement ? '（可选）' : '（没有题号 / 链接时可手动补充）';
            requiredFlagEl.style.color = canAutoUseOfficialStatement ? '#666' : '#b9770e';
        }
        if (contextHintEl) {
            contextHintEl.textContent = canAutoUseOfficialStatement
                ? '系统会直接使用洛谷官方题面；这里只在你想补充自己对题意的理解或误解时填写。'
                : '可输入洛谷题号 / 链接自动导入；如果暂时没有，也可以手动补题面。';
            contextHintEl.style.color = '#666';
        }
        if (contextInput) {
            contextInput.placeholder = canAutoUseOfficialStatement
                ? '可选：补充你当时误解了哪条条件、样例或限制。'
                : '来源为洛谷时，优先填写题号 / 链接；没有时也支持手动补题面 / Markdown。';
        }
        if (canAutoUseOfficialStatement) {
            setLuoguSupplementExpanded(luoguSupplementExpanded || Boolean(contextInput?.value.trim()));
        } else {
            luoguSupplementExpanded = false;
            if (toggleRowEl) toggleRowEl.classList.add('hidden');
            if (contextGroupEl) contextGroupEl.classList.remove('hidden');
        }
    }
    if (isLuogu && !urlInput?.value.trim()) {
        setProblemImportStatus('输入洛谷题号或公开题目链接后，可自动导入标题、题面和标签。');
    }
    renderLinkedChatContextCard();
}

function renderLinkedChatContextCard() {
    const cardEl = document.getElementById('linked-chat-context-card');
    const textEl = document.getElementById('linked-chat-context-text');
    const timeEl = document.getElementById('linked-chat-context-time');
    if (!cardEl || !textEl || !timeEl) return;

    const currentRef = resolveCurrentCheckinProblemRef();
    const context = getProblemChatContext(currentRef);
    if (!currentRef || !context?.summary) {
        cardEl.classList.add('hidden');
        textEl.textContent = '';
        timeEl.textContent = '';
        return;
    }

    cardEl.classList.remove('hidden');
    textEl.textContent = context.summary;
    timeEl.textContent = formatRelativeTimeLabel(context.updatedAt) || currentRef;
}

function renderReviewChatContext(item) {
    if (!item?.chat_context_summary) return '';
    const title = item.problem_title || extractProblemPidFromCheckin(item) || '当前题目';
    return `
        <div class="context-link-head">
            <div>
                <p class="panel-eyebrow">Linked Context</p>
                <h4>同题最近 AI 解答</h4>
            </div>
            <span class="status-pill">${escapeHtml(title)}</span>
        </div>
        <p class="context-link-body">${escapeHtml(item.chat_context_summary)}</p>
        <p class="input-hint">这份摘要来自你在 AI 解答里对同一道题的最近提问，复盘时会把它作为辅助线索一起参考。</p>
    `;
}

async function importProblemFromUrl() {
    const ojSelect = document.getElementById('checkin-oj');
    const urlInput = document.getElementById('checkin-url');
    const titleInput = document.getElementById('checkin-title');
    const contextInput = document.getElementById('checkin-problem-context');
    if (!ojSelect || !urlInput || !titleInput || !contextInput) return;

    const rawUrl = urlInput.value.trim();
    if (ojSelect.value !== 'luogu') {
        setProblemImportStatus('当前只有选择“洛谷”时才能自动导入题面。', 'warn');
        return;
    }
    if (!isLikelyLuoguProblemRef(rawUrl)) {
        setProblemImportStatus('请输入有效的洛谷题号或公开题目链接，例如 P1001 或 https://www.luogu.com.cn/problem/P1001', 'error');
        return;
    }

    setProblemImportStatus('正在读取洛谷题面...', 'neutral');
    try {
        const res = await apiFetch(`${API_BASE}/api/problem-import`, {
            method: 'POST',
            body: JSON.stringify({ url: rawUrl }),
        });
        const data = await res.json();
        urlInput.value = data.problem_url || rawUrl;
        titleInput.value = data.problem_title || '';
        if (!luoguSupplementExpanded) {
            contextInput.value = '';
        }
        importedProblemMeta = {
            imported: true,
            problemPid: data.problem_pid || '',
            problemUrl: data.problem_url || rawUrl,
            problemTags: data.problem_tags || [],
        };
        updateProblemTagsPreview(importedProblemMeta.problemTags);
        setProblemImportStatus(data.message || '已自动导入题目标题、题面和标签', 'success');
        syncCheckinSourceInputs();
        if (typeof window.validateCheckinForm === 'function') {
            window.validateCheckinForm();
        }
    } catch (error) {
        resetImportedProblemMeta();
        updateProblemTagsPreview([]);
        setProblemImportStatus(error.message || '自动导入失败，请手动补题面', 'error');
    }
}

function showStudentTab(targetId) {
    document.querySelectorAll('#student-section .tab-content').forEach((content) => content.classList.add('hidden'));
    const target = document.getElementById(targetId);
    if (target) {
        target.classList.remove('hidden');
    }
    document.querySelectorAll('#student-tabs .tab-btn').forEach((btn) => {
        btn.classList.toggle('active', btn.dataset.tab === targetId);
    });
    if (targetId === 'checkin-tab') {
        renderLinkedChatContextCard();
        const activeItem = activeCheckinId
            ? myCheckinsCache.find((candidate) => Number(candidate.id) === Number(activeCheckinId)) || null
            : null;
        if (activeItem) {
            renderActiveCheckinWorkspace(activeItem);
        } else {
            renderCheckinEntryStage();
        }
    } else if (targetId === 'history-tab') {
        renderCheckinHistoryList();
    }
}

function buildReviewView(review) {
    return {
        problem_focus: review?.problem_focus || review?.review_problem_focus || review?.main_block || review?.review_main_block || '',
        main_block: review?.main_block || review?.review_main_block || '',
        key_bridge: review?.key_bridge || review?.review_key_bridge || '',
        visual_hint: review?.visual_hint || review?.review_visual_hint || '',
        guided_walkthrough: review?.guided_walkthrough || review?.review_guided_walkthrough || '',
        try_now: review?.try_now || review?.review_try_now || review?.next_step || review?.review_next_step || '',
        next_step: review?.next_step || review?.review_next_step || '',
        transfer_signal: review?.transfer_signal || review?.review_transfer_signal || '',
        review_mode: review?.review_mode || review?.mode || '',
        review_family: review?.review_family || review?.family || '',
        error_tags: review?.error_tags || review?.review_error_tags || [],
        error_layer: review?.error_layer || review?.review_error_layer || 'insufficient',
        error_layer_confidence: review?.error_layer_confidence || review?.review_confidence || 'low',
        core_design_subtags: review?.core_design_subtags || review?.review_core_design_subtags || [],
        diagnosis: review?.diagnosis || review?.review_diagnosis || '',
        next_action: review?.next_action || review?.review_next_action || '',
        suggested_topic: review?.suggested_topic || review?.review_suggested_topic || '',
    };
}

function extractProblemPidFromCheckin(item) {
    const url = item?.problem_url || '';
    const urlMatch = url.match(/\/problem\/([A-Za-z0-9_]+)/i) || url.match(/\/problemnew\/show\/([A-Za-z0-9_]+)/i);
    if (urlMatch) return urlMatch[1];

    const title = item?.problem_title || '';
    const titleMatch = title.match(/\b([A-Za-z][A-Za-z0-9_]*)\b/);
    if (titleMatch && /^[A-Za-z][A-Za-z0-9_]*$/.test(titleMatch[1])) {
        return titleMatch[1];
    }
    return '';
}

function resolvedProblemTitleFromForm(problemTitle, problemPid) {
    if (problemTitle) return problemTitle;
    if (problemPid) return problemPid;
    return '新打卡题目';
}

function renderHistoryListItem(item, isActive) {
    const tone = reviewTimelineTone(item);
    const tags = (item.review_error_tags?.length ? item.review_error_tags : item.error_types || []).slice(0, 3);
    return `
        <div class="history-card ${isActive ? 'active' : ''}" onclick="selectCheckin(${Number(item.id)})">
            <div class="history-card-top">
                <span class="history-card-title">${escapeHtml(item.problem_title || '未命名题目')}</span>
                <span class="status-pill tone-${tone}">${escapeHtml(reviewLearningStateText(item, false))}</span>
            </div>
            <div class="history-card-meta">
                <span class="status-pill">${escapeHtml(ojSourceText(item.oj_source))}</span>
                <span class="status-pill">${escapeHtml(completionStatusText(item.completion_status))}</span>
                <span class="status-pill">${escapeHtml(formatDate(item.created_at))}</span>
            </div>
            ${tags.length ? `<div class="history-card-tags">${renderPillRow(tags, 'tag-pill ai-tag')}</div>` : ''}
            <div class="history-card-desc rich-text">${renderRichTextInline(item.bottleneck_text || '')}</div>
        </div>
    `;
}

function renderRelatedFallback(item) {
    const topic = item?.review_suggested_topic || '先围绕当前这座桥再练 1-2 题。';
    return `
        <div class="related-problems">
            <div class="related-problem-card">
                <strong>推荐练习方向</strong>
                <p>${renderRichTextInline(topic)}</p>
            </div>
        </div>
    `;
}

function renderRelatedProblems(cards = []) {
    if (!cards.length) return '';
    return `
        <div class="related-problems">
            ${cards.map((card) => `
                <div class="related-problem-card">
                    <a class="workspace-link" href="${escapeHtml(card.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(card.pid)} ${escapeHtml(card.title)}</a>
                    <p class="rich-text">${renderRichTextInline(card.reason || '')}</p>
                    <div class="related-problem-meta">
                        <span class="status-pill">难度 ${escapeHtml(String(card.difficulty ?? '-'))}</span>
                        ${(card.tags || []).map((tag) => `<span class="tag-pill subtle-tag">${escapeHtml(tag)}</span>`).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

async function loadRelatedProblems(item) {
    const container = document.getElementById('active-review-related');
    if (!container || !item) return;
    const pid = extractProblemPidFromCheckin(item);
    activeRelatedProblemPid = pid;
    if (!pid) {
        container.innerHTML = renderRelatedFallback(item);
        return;
    }

    container.innerHTML = '<div class="related-problems"><div class="related-problem-card"><strong>正在匹配同类题目...</strong><p>会优先按照题目算法标签和难度给你找更贴近的练习。</p></div></div>';

    try {
        const res = await apiFetch(`${API_BASE}/api/problems/related?pid=${encodeURIComponent(pid)}&limit=4`);
        const data = await res.json();
        if (activeRelatedProblemPid !== pid) return;
        const cards = data.related || [];
        container.innerHTML = cards.length ? renderRelatedProblems(cards) : renderRelatedFallback(item);
    } catch (err) {
        if (activeRelatedProblemPid !== pid) return;
        container.innerHTML = renderRelatedFallback(item);
    }
}

function setReviewStageEmpty() {
    const entryStage = document.getElementById('checkin-entry-stage');
    const reviewStage = document.getElementById('checkin-review-stage');
    const empty = document.getElementById('review-stage-empty');
    const content = document.getElementById('review-stage-content');
    const status = document.getElementById('workspace-stage-status');
    const context = document.getElementById('active-review-chat-context');
    const titleEl = document.getElementById('active-review-title');
    const subtitleEl = document.getElementById('active-review-subtitle');
    const metaEl = document.getElementById('active-review-meta');
    if (entryStage) entryStage.classList.remove('hidden');
    if (reviewStage) reviewStage.classList.add('hidden');
    if (empty) empty.classList.remove('hidden');
    if (content) content.classList.add('hidden');
    if (status) status.innerHTML = '';
    if (titleEl) titleEl.textContent = '这次打卡复盘';
    if (subtitleEl) subtitleEl.textContent = checkinReviewUi.entryStageLead();
    if (metaEl) metaEl.innerHTML = '';
    if (context) {
        context.classList.add('hidden');
        context.innerHTML = '';
    }
}

function renderCheckinEntryStage() {
    const entryStage = document.getElementById('checkin-entry-stage');
    const reviewStage = document.getElementById('checkin-review-stage');
    const empty = document.getElementById('review-stage-empty');
    const content = document.getElementById('review-stage-content');
    const status = document.getElementById('workspace-stage-status');
    const context = document.getElementById('active-review-chat-context');
    const titleEl = document.getElementById('active-review-title');
    const subtitleEl = document.getElementById('active-review-subtitle');
    const metaEl = document.getElementById('active-review-meta');
    const quizEl = document.getElementById('active-review-quiz-slot');
    const reportEl = document.getElementById('active-review-report');
    const relatedEl = document.getElementById('active-review-related');
    setReviewStageEmpty();
    if (entryStage) entryStage.classList.remove('hidden');
    if (reviewStage) reviewStage.classList.add('hidden');
    if (titleEl) titleEl.textContent = '这次打卡复盘';
    if (subtitleEl) subtitleEl.textContent = checkinReviewUi.entryStageLead();
    if (metaEl) metaEl.innerHTML = '';
    if (quizEl) quizEl.innerHTML = '';
    if (reportEl) reportEl.innerHTML = '';
    if (relatedEl) relatedEl.innerHTML = '';
    if (status) status.innerHTML = '';
    if (context) {
        context.classList.add('hidden');
        context.innerHTML = '';
    }
    if (empty) empty.classList.remove('hidden');
    if (content) content.classList.add('hidden');
}

function renderActiveCheckinWorkspace(item) {
    const entryStage = document.getElementById('checkin-entry-stage');
    const reviewStage = document.getElementById('checkin-review-stage');
    const empty = document.getElementById('review-stage-empty');
    const content = document.getElementById('review-stage-content');
    const titleEl = document.getElementById('active-review-title');
    const subtitleEl = document.getElementById('active-review-subtitle');
    const metaEl = document.getElementById('active-review-meta');
    const statusEl = document.getElementById('workspace-stage-status');
    const quizEl = document.getElementById('active-review-quiz-slot');
    const reportEl = document.getElementById('active-review-report');
    const relatedEl = document.getElementById('active-review-related');
    const chatContextEl = document.getElementById('active-review-chat-context');

    if (!item) {
        setReviewStageEmpty();
        if (quizEl) quizEl.innerHTML = '';
        if (reportEl) reportEl.innerHTML = '';
        if (relatedEl) relatedEl.innerHTML = '';
        if (chatContextEl) {
            chatContextEl.classList.add('hidden');
            chatContextEl.innerHTML = '';
        }
        return;
    }

    if (entryStage) entryStage.classList.add('hidden');
    if (reviewStage) reviewStage.classList.remove('hidden');
    if (empty) empty.classList.add('hidden');
    if (content) content.classList.remove('hidden');
    if (titleEl) titleEl.textContent = item.problem_title || '复盘工作区';
    if (subtitleEl) {
        subtitleEl.textContent = reviewFamilyUi.reviewWorkspaceSubtitle(item);
    }
    if (metaEl) {
        metaEl.innerHTML = `
            <span class="status-pill">${escapeHtml(ojSourceText(item.oj_source))}</span>
            <span class="status-pill">${escapeHtml(completionStatusText(item.completion_status))}</span>
            <span class="status-pill tone-${reviewTimelineTone(item)}">${escapeHtml(reviewLearningStateText(item, false))}</span>
        `;
    }
    if (statusEl) {
        statusEl.innerHTML = `
            <span class="status-pill">${escapeHtml(formatDate(item.created_at))}</span>
            ${item.problem_url ? `<a class="workspace-link status-pill" href="${escapeHtml(item.problem_url)}" target="_blank" rel="noopener noreferrer">打开原题</a>` : ''}
        `;
    }
    if (quizEl) {
        quizEl.innerHTML = renderLearningSection(item) || renderLearningPathPlaceholder(item);
    }
    if (reportEl) {
        if (item.review_status === 'completed') {
            reportEl.innerHTML = renderReviewHtml(buildReviewView(item), reviewFamilyUi.resolveReviewFamily(item));
            markReviewShown(item, reportEl.textContent?.trim().length || 0);
        } else if (item.review_status === 'failed') {
            reportEl.innerHTML = renderFailedReviewNotice(item);
        } else if (item.poll_timed_out) {
            reportEl.innerHTML = renderReviewTimeoutNotice(item);
        } else {
            reportEl.innerHTML = renderPendingReviewNotice(item);
        }
    }
    if (chatContextEl) {
        const contextHtml = renderReviewChatContext(item);
        chatContextEl.classList.toggle('hidden', !contextHtml);
        chatContextEl.innerHTML = contextHtml;
    }
    if (relatedEl) {
        relatedEl.innerHTML = renderRelatedFallback(item);
        loadRelatedProblems(item);
    }
}

function selectCheckin(checkinId) {
    activeCheckinId = Number(checkinId);
    const item = myCheckinsCache.find((candidate) => Number(candidate.id) === activeCheckinId) || null;
    renderCheckinHistoryList();
    showStudentTab('checkin-tab');
    renderActiveCheckinWorkspace(item);
}

function renderCheckinHistoryList() {
    const listEl = document.getElementById('checkin-history-list');
    if (!listEl) return;
    if (!myCheckinsCache.length) {
        listEl.innerHTML = '<p>还没有打卡记录</p>';
        return;
    }
    listEl.innerHTML = myCheckinsCache
        .map((item) => renderHistoryListItem(item, Number(item.id) === Number(activeCheckinId)))
        .join('');
}

async function apiFetch(url, options = {}) {
    const fetchOptions = { ...options };
    const requiresAuth = fetchOptions.auth !== false;
    fetchOptions.headers = { ...(fetchOptions.headers || {}) };

    if (!fetchOptions.headers['Content-Type'] && fetchOptions.body) {
        fetchOptions.headers['Content-Type'] = 'application/json';
    }

    if (requiresAuth && authToken) {
        fetchOptions.headers.Authorization = `Bearer ${authToken}`;
    }
    delete fetchOptions.auth;

    const res = await fetch(url, fetchOptions);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
        if (requiresAuth && res.status === 401) {
            redirectToLogin('登录已失效，请重新登录');
        }
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res;
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function formatInlineRichText(text) {
    if (text === null || text === undefined) return '';
    return escapeHtml(normalizeColloquialMath(String(text)))
        .replace(/`([^`\n]+)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

function formatBlockRichText(text) {
    if (text === null || text === undefined) return '';
    const raw = normalizeColloquialMath(String(text)).replace(/\r\n?/g, '\n');
    const codeBlocks = [];
    let tokenized = raw.replace(/```([\s\S]*?)```/g, (_, code) => {
        const html = `<pre class="rich-code-block"><code>${escapeHtml(code.trim())}</code></pre>`;
        const index = codeBlocks.push(html) - 1;
        return `@@RICH_CODE_${index}@@`;
    });
    tokenized = escapeHtml(tokenized)
        .replace(/`([^`\n]+)`/g, '<code>$1</code>');

    let html = tokenized
        .split(/\n{2,}/)
        .map((paragraph) => `<p>${paragraph.replace(/\n/g, '<br>')}</p>`)
        .join('');

    html = html.replace(/@@RICH_CODE_(\d+)@@/g, (_, idx) => codeBlocks[Number(idx)] || '');
    return html;
}

function normalizePlainMathSegment(segment) {
    if (!segment) return '';
    let output = segment;
    const token = '[A-Za-z][A-Za-z0-9_]*(?:\\[[^\\]\\n]+\\])*|\\d+';
    const replacements = [
        [new RegExp(`(${token})\\s*大于等于\\s*(${token}|(?:max|min)\\()`, 'g'), '$1 \\\\ge $2'],
        [new RegExp(`(${token})\\s*小于等于\\s*(${token}|(?:max|min)\\()`, 'g'), '$1 \\\\le $2'],
        [new RegExp(`(${token})\\s*严格大于\\s*(${token}|(?:max|min)\\()`, 'g'), '$1 > $2'],
        [new RegExp(`(${token})\\s*严格小于\\s*(${token}|(?:max|min)\\()`, 'g'), '$1 < $2'],
        [new RegExp(`(${token})\\s*等于\\s*(${token}|(?:max|min)\\()`, 'g'), '$1 = $2'],
        [new RegExp(`(\\d+)\\s*倍\\s*(${token})`, 'g'), '$1 \\\\times $2'],
        [new RegExp(`(${token})\\s*乘以\\s*(${token})`, 'g'), '$1 \\\\times $2'],
        [new RegExp(`(${token})\\s*乘\\s*(${token})`, 'g'), '$1 \\\\times $2'],
        [new RegExp(`(${token})\\s*加上\\s*(${token})`, 'g'), '$1 + $2'],
        [new RegExp(`(${token})\\s*加\\s*(${token})`, 'g'), '$1 + $2'],
        [new RegExp(`(${token})\\s*减去\\s*(${token})`, 'g'), '$1 - $2'],
        [new RegExp(`(${token})\\s*减\\s*(${token})`, 'g'), '$1 - $2'],
        [new RegExp(`(${token})\\s*除以\\s*(${token})`, 'g'), '$1 \\\\div $2'],
        [new RegExp(`(${token})\\s*除\\s*(${token})`, 'g'), '$1 \\\\div $2'],
    ];

    replacements.forEach(([pattern, replacement]) => {
        output = output.replace(pattern, replacement);
    });

    output = output
        .replace(/\bmax\(/g, '\\max(')
        .replace(/\bmin\(/g, '\\min(');

    output = output.replace(
        /([A-Za-z0-9_\[\]\(\),\\ ]+(?:=|\\times|\\div|\\ge|\\le|\+|\-|>|<)[A-Za-z0-9_\[\]\(\),\\ +\-><]+)/g,
        (match) => {
            const trimmed = match.trim().replace(/\s{2,}/g, ' ');
            if (!trimmed || trimmed.startsWith('$') || trimmed.endsWith('$')) return match;
            return `$${trimmed}$`;
        },
    );

    return output;
}

function normalizeColloquialMath(text) {
    if (!text) return '';
    const protectedPattern = /(```[\s\S]*?```|`[^`\n]+`|\$\$[\s\S]*?\$\$|\$[^$\n]+\$)/g;
    let result = '';
    let lastIndex = 0;
    let match;

    while ((match = protectedPattern.exec(text)) !== null) {
        result += normalizePlainMathSegment(text.slice(lastIndex, match.index));
        result += match[0];
        lastIndex = match.index + match[0].length;
    }
    result += normalizePlainMathSegment(text.slice(lastIndex));
    return result;
}

function renderRichTextInline(text, className = '') {
    if (!text) return '';
    const extra = className ? ` ${className}` : '';
    return `<span class="rich-text rich-text-inline${extra}" data-rich-ready="0">${formatInlineRichText(text)}</span>`;
}

function renderRichTextBlock(text, className = '') {
    if (!text) return '';
    const extra = className ? ` ${className}` : '';
    return `<div class="rich-text${extra}" data-rich-ready="0">${formatBlockRichText(text)}</div>`;
}

function renderReviewNoteSection(section) {
    const emphasisClass = section.field === 'try_now'
        ? 'is-action'
        : section.field === 'transfer_signal'
            ? 'is-aside'
            : '';
    const content = section.field === 'visual_hint'
        ? `<pre class="review-visual-hint review-note-visual">${escapeHtml(section.value || '')}</pre>`
        : renderRichTextBlock(section.value || '', 'review-inline-rich-block');
    return `
        <article class="review-note-section${emphasisClass ? ` ${emphasisClass}` : ''}">
            <div class="review-note-label">${escapeHtml(section.label || '')}</div>
            <div class="review-note-content">
                ${content}
            </div>
        </article>
    `;
}

function renderReviewDetailsDrawer(item = {}) {
    const errorTags = item.error_tags || item.review_error_tags || [];
    const subTags = item.core_design_subtags || item.review_core_design_subtags || [];
    const parts = [];

    if (errorTags.length) {
        parts.push(`
            <div class="review-note-drawer-row">
                <div class="review-note-drawer-label">错误标签</div>
                <div class="archive-chip-row">${renderPillRow(errorTags, 'tag-pill ai-tag')}</div>
            </div>
        `);
    }
    if (item.error_layer) {
        parts.push(`
            <div class="review-note-drawer-row">
                <div class="review-note-drawer-label">统一归类</div>
                <div class="review-note-drawer-value">${escapeHtml(errorLayerText(item.error_layer))}</div>
            </div>
        `);
    }
    if (item.error_layer_confidence) {
        parts.push(`
            <div class="review-note-drawer-row">
                <div class="review-note-drawer-label">判断把握</div>
                <div class="review-note-drawer-value">${escapeHtml(confidenceText(item.error_layer_confidence))}</div>
            </div>
        `);
    }
    if (subTags.length) {
        parts.push(`
            <div class="review-note-drawer-row">
                <div class="review-note-drawer-label">核心设计子标签</div>
                <div class="archive-chip-row">${renderPillRow(subTags, 'tag-pill subtle-tag')}</div>
            </div>
        `);
    }
    if (item.diagnosis) {
        parts.push(`
            <div class="review-note-drawer-row">
                <div class="review-note-drawer-label">问题诊断</div>
                <div class="review-note-drawer-value">${renderRichTextInline(item.diagnosis || '')}</div>
            </div>
        `);
    }
    if (item.next_action) {
        parts.push(`
            <div class="review-note-drawer-row">
                <div class="review-note-drawer-label">下一步行动</div>
                <div class="review-note-drawer-value">${renderRichTextInline(item.next_action || '')}</div>
            </div>
        `);
    }
    if (item.suggested_topic) {
        parts.push(`
            <div class="review-note-drawer-row">
                <div class="review-note-drawer-label">推荐专题</div>
                <div class="review-note-drawer-value">${renderRichTextInline(item.suggested_topic || '')}</div>
            </div>
        `);
    }

    if (!parts.length) return '';

    return `
        <details class="review-note-drawer">
            <summary>展开看老师批注</summary>
            <div class="review-note-drawer-body">
                ${parts.join('')}
            </div>
        </details>
    `;
}

function hydrateMath(root = document) {
    if (typeof window.renderMathInElement !== 'function' || !root?.querySelectorAll) return;
    root.querySelectorAll('.rich-text[data-rich-ready="0"]').forEach((node) => {
        node.setAttribute('data-rich-ready', '1');
        try {
            window.renderMathInElement(node, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false },
                    { left: '\\(', right: '\\)', display: false },
                    { left: '\\[', right: '\\]', display: true },
                ],
                throwOnError: false,
            });
        } catch (err) {
            console.warn('KaTeX render skipped:', err);
        }
    });
}

function setupRichTextObserver() {
    const observer = new MutationObserver(() => {
        window.requestAnimationFrame(() => hydrateMath(document));
    });
    observer.observe(document.body, { childList: true, subtree: true });
    hydrateMath(document);
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleString('zh-CN');
}

function completionStatusText(status) {
    const map = {
        independent: '独立完成',
        hinted: '需要提示',
        editorial: '看题解',
        unfinished: '未完成',
    };
    return map[status] || status || '未知';
}

function reviewStatusText(status) {
    const map = {
        pending: '待生成',
        completed: '已生成',
        failed: '最终失败',
    };
    return map[status] || '未生成';
}

function errorLayerText(layer) {
    const map = {
        reading: '读题理解',
        method: '方向判断',
        modeling: '建模转化',
        core_design: '核心设计',
        implementation: '实现调试',
        insufficient: '信息不足',
    };
    return map[layer] || layer || '未归类';
}

function coreDesignSubtagText(subtag) {
    const map = {
        state_design: '状态设计',
        transition_design: '转移设计',
        check_condition: 'check 条件',
        greedy_basis: '贪心依据',
        enumeration_order: '枚举顺序',
    };
    return map[subtag] || subtag || '';
}

function confidenceText(level) {
    const map = {
        high: '高',
        medium: '中',
        low: '低',
    };
    return map[level] || level || '未知';
}

function renderPendingReviewNotice(item = {}) {
    const phaseTextMap = {
        received: '已收到打卡',
        queued: '已进入生成队列',
        llm_start: '正在调用模型',
        llm_done: '模型已返回，正在整理内容',
        review_parse: '正在整理复盘内容',
        review_saved: '复盘已生成，正在准备理解检查',
        quiz_generating: '正在准备理解检查',
        completed: '复盘已就绪',
        failed: '复盘生成失败',
    };
    const phase = String(item.review_stream_phase || '').trim();
    const stageText = phaseTextMap[phase] || 'AI 正在整理复盘';
    const streamMessage = String(item.review_stream_message || '').trim();
    const elapsedSeconds = Number(item.review_stream_elapsed_seconds || 0);
    const elapsedText = elapsedSeconds > 0 ? `已等待 ${Math.max(1, Math.round(elapsedSeconds))} 秒` : '刚刚开始';
    const draftRows = [
        ['你卡在哪', item.review_stream_draft_main_block],
        ['关键一步', item.review_stream_draft_key_bridge],
        ['现在先做', item.review_stream_draft_next_step],
        ['下次提醒', item.review_stream_draft_transfer_signal],
    ].filter(([, value]) => String(value || '').trim());
    return `
        <div style="margin-top: 10px; padding: 14px 16px; background: #fff8e1; border: 1px solid #f1c40f; border-radius: 10px;">
            <div style="font-weight: 700; color: #8a6d3b;">AI 正在整理复盘</div>
            <div style="margin-top: 8px; color: #8a6d3b;">当前阶段：${escapeHtml(stageText)}</div>
            ${streamMessage ? `<div style="margin-top: 6px; color: #8a6d3b;">${escapeHtml(streamMessage)}</div>` : ''}
            <div style="margin-top: 8px; color: #8a6d3b;">题目：${escapeHtml(item.problem_title || '未命名题目')}</div>
            <div style="margin-top: 6px; color: #8a6d3b;">提交时间：${escapeHtml(formatDate(item.created_at) || '刚刚')}</div>
            <div style="margin-top: 6px; color: #8a6d3b;">进度提示：${escapeHtml(elapsedText)}</div>
            ${draftRows.length ? `
                <div style="margin-top: 12px; padding: 12px; background: rgba(255,255,255,0.65); border-radius: 8px;">
                    <div style="font-weight: 700; color: #8a6d3b; margin-bottom: 8px;">AI 草稿预览</div>
                    ${draftRows.map(([label, value]) => `
                        <div style="margin-top: 6px; color: #8a6d3b;"><strong>${escapeHtml(label)}：</strong>${renderRichTextInline(value || '')}</div>
                    `).join('')}
                </div>
            ` : ''}
            <div style="margin-top: 10px;">
                <button class="secondary" onclick="refreshPendingCheckin(${Number(item.id || item.checkin_id || 0)})">如超过 1 分钟未出现，点此刷新</button>
            </div>
        </div>
    `;
}

function renderFailedReviewNotice(item = {}) {
    return `
        <div style="margin-top: 10px; padding: 14px 16px; background: #fff3f2; border: 1px solid #e67e73; border-radius: 10px;">
            <div style="font-weight: 700; color: #c0392b;">复盘生成失败</div>
            <div style="margin-top: 8px; color: #8c2d25;">你的打卡已经保存，可以稍后重新生成。</div>
            <div style="margin-top: 10px;">
                <button class="secondary" onclick="retryReviewGeneration(${Number(item.id || item.checkin_id || 0)})">重新生成</button>
            </div>
        </div>
    `;
}

function renderReviewTimeoutNotice(item = {}) {
    return `
        <div style="margin-top: 10px; padding: 14px 16px; background: #f7f9fb; border: 1px solid #b8c6db; border-radius: 10px;">
            <div style="font-weight: 700; color: #4a5a6a;">复盘生成时间较长</div>
            <div style="margin-top: 8px; color: #4a5a6a;">请刷新页面或稍后在历史记录里查看。</div>
            <div style="margin-top: 10px;">
                <button class="secondary" onclick="refreshPendingCheckin(${Number(item.id || item.checkin_id || 0)})">刷新页面</button>
            </div>
        </div>
    `;
}

function ojSourceText(source) {
    const map = {
        luogu: '洛谷',
        codeforces: 'Codeforces',
        atcoder: 'AtCoder',
        other: '其他',
    };
    return map[source] || source || '未知来源';
}

function renderPillRow(values, className = 'tag-pill') {
    if (!values?.length) {
        return '<span class="tag-pill muted">暂无</span>';
    }
    return values.map((value) => `<span class="${className}">${escapeHtml(value)}</span>`).join('');
}

function reviewLearningStateText(item, isTeacher = false) {
    if (item.review_status === 'pending') return 'AI 正在整理复盘';
    if (item.review_status === 'failed') return isTeacher ? '复盘生成失败' : '复盘生成失败，可稍后重试';
    if (item.review_learning_status === 'self_check_required') {
        return isTeacher ? '已答对，等待理解确认' : '这一步先别急着结束，再确认一下';
    }
    if (item.review_learning_status === 'resolved') return isTeacher ? '这一步已过桥' : '这一步你已经过桥了';
    if (item.review_learning_status === 'needs_teacher_followup') return isTeacher ? '建议老师跟进' : '这一步需要老师一起看';
    if (item.review_learning_status === 'remedy_available' || item.review_learning_status === 'remedy_in_progress') {
        return '这一步还在继续拆小讲';
    }
    if (item.quiz_status === 'pending') return '正在做理解检查';
    if (item.review_status === 'completed') return '复盘已生成，可以继续理解检查';
    return '等待生成复盘';
}

function reviewTimelineTone(item) {
    if (item.review_status === 'pending') return 'pending';
    if (item.review_status === 'failed') return 'followup';
    if (item.review_learning_status === 'self_check_required') return 'quiz';
    if (item.review_learning_status === 'resolved') return 'resolved';
    if (item.review_learning_status === 'needs_teacher_followup') return 'followup';
    if (item.review_learning_status === 'remedy_available' || item.review_learning_status === 'remedy_in_progress') {
        return 'remedy';
    }
    if (item.quiz_status === 'pending') return 'quiz';
    if (item.review_status === 'completed') return 'reviewed';
    return 'idle';
}

function resolveRemedyTransition({ understandingSelfCheck, quizRole, feedbackText, explanation }) {
    if (understandingSelfCheck === 'confused') {
        return {
            title: '你已经发现这一步还没站稳，我们先把它再拆小一点。',
            explanation: explanation || '',
        };
    }

    if (understandingSelfCheck === 'guessed') {
        if (quizRole === 'confirm' && feedbackText) {
            return {
                title: feedbackText,
                explanation: explanation || '',
            };
        }
        return {
            title: '你已经感觉到这一步还有点虚，我们先换一种方式继续讲。',
            explanation: explanation || '',
        };
    }

    if (quizRole === 'followup') {
        return {
            title: feedbackText || '这一步还差一点，我们先换一种方式再带你过一遍。',
            explanation: explanation || '',
        };
    }

    if (quizRole === 'confirm') {
        return {
            title: feedbackText || '这一步还没真正站稳，我们换个角度再补一下。',
            explanation: explanation || '',
        };
    }

    return {
        title: feedbackText || '这一步还没完全打通，我们先换一种方式继续。',
        explanation: explanation || '',
    };
}

function renderRemedyTransitionCard(config) {
    if (!config?.title) return '';
    return `
        <div class="learning-stage-card learning-path-feedback warn">
            <div class="learning-stage-header">
                <div class="learning-stage-kicker">补救过渡</div>
                <div class="learning-stage-question">我们换一种带法，继续过这一步</div>
                <div class="learning-stage-subtitle">${escapeHtml(config.title)}</div>
            </div>
            ${config.explanation ? `<div class="learning-path-feedback-explanation">${escapeHtml(config.explanation)}</div>` : ''}
        </div>
    `;
}

async function fetchMyCheckinById(checkinId) {
    const res = await apiFetch(`${API_BASE}/api/checkins/${checkinId}`);
    return res.json();
}

async function postReviewEvent(item, eventName, extra = {}) {
    if (!item?.id) return;
    const normalizedCheckinId = Number(item.id || item.checkin_id);
    const payload = {
        checkin_id: normalizedCheckinId,
        session_id: item.session_id || `checkin_${normalizedCheckinId}`,
        event_name: eventName,
        client_ts: new Date().toISOString(),
        app_version: APP_VERSION,
        user_id: currentUserId || '',
        problem_id: item.problem_id || '',
        problem_title: item.problem_title || '',
        review_mode: item.review_mode || '',
        review_family: item.review_family || '',
        ...extra,
    };
    try {
        await apiFetch(`${API_BASE}/api/review-events`, {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    } catch (err) {
        console.warn('review event failed:', err);
    }
}

function markReviewShown(item, reviewTextLength = 0) {
    if (!item?.id || item.review_status !== 'completed') return;
    const sessionKey = item.session_id || `checkin_${item.id || item.checkin_id}`;
    const eventKey = `${sessionKey}:review_shown`;
    if (sentReviewEventKeys.has(eventKey)) return;
    sentReviewEventKeys.add(eventKey);
    void postReviewEvent(item, 'review_shown', {
        latency_ms: 0,
        review_text_length: Math.max(0, Number(reviewTextLength || 0)),
    });
}

function stopCheckinReviewStream(checkinId) {
    const state = pendingReviewStreams.get(Number(checkinId));
    if (state?.abortController) {
        state.closed = true;
        state.abortController.abort();
    }
    pendingReviewStreams.delete(Number(checkinId));
}

function stopCheckinPoll(checkinId) {
    const state = pendingReviewPolls.get(Number(checkinId));
    if (state?.timerId) {
        clearTimeout(state.timerId);
    }
    pendingReviewPolls.delete(Number(checkinId));
}

function mergeCheckinStreamPayloadIntoCache(checkinId, payload = {}) {
    const draft = payload.draft_review || {};
    const normalizedId = Number(checkinId || payload.checkin_id || payload.id);
    return mergeCheckinDetailIntoCache({
        id: normalizedId,
        checkin_id: normalizedId,
        review_status: payload.review_status || 'pending',
        review_stream_phase: payload.phase || '',
        review_stream_message: payload.message || '',
        review_stream_elapsed_seconds: payload.elapsed_seconds || 0,
        review_stream_updated_at: payload.updated_at || '',
        review_stream_draft_main_block: draft.main_block || '',
        review_stream_draft_key_bridge: draft.key_bridge || '',
        review_stream_draft_next_step: draft.next_step || '',
        review_stream_draft_transfer_signal: draft.transfer_signal || '',
        poll_timed_out: false,
    });
}

function mergeCheckinDetailIntoCache(detail) {
    const nestedReview = detail.review || {};
    const normalized = {
        ...detail,
        id: detail.id ?? detail.checkin_id,
        poll_timed_out: detail.poll_timed_out === true,
        review_mode: detail.review_mode || '',
        review_family: detail.review_family || '',
        review_error_layer: detail.review_error_layer || nestedReview.error_layer || '',
        review_confidence: detail.review_confidence || nestedReview.error_layer_confidence || '',
        review_core_design_subtags: detail.review_core_design_subtags || nestedReview.core_design_subtags || [],
        review_main_block: detail.review_main_block || nestedReview.main_block || '',
        review_key_bridge: detail.review_key_bridge || nestedReview.key_bridge || '',
        review_next_step: detail.review_next_step || nestedReview.next_step || '',
        review_transfer_signal: detail.review_transfer_signal || nestedReview.transfer_signal || '',
        review_diagnosis: detail.review_diagnosis || nestedReview.diagnosis || '',
        review_next_action: detail.review_next_action || nestedReview.next_action || '',
        review_suggested_topic: detail.review_suggested_topic || nestedReview.suggested_topic || '',
        review_error_tags: detail.review_error_tags || nestedReview.error_tags || [],
        review_stream_phase: detail.review_stream_phase || '',
        review_stream_message: detail.review_stream_message || '',
        review_stream_elapsed_seconds: detail.review_stream_elapsed_seconds || 0,
        review_stream_updated_at: detail.review_stream_updated_at || '',
        review_stream_draft_main_block: detail.review_stream_draft_main_block || '',
        review_stream_draft_key_bridge: detail.review_stream_draft_key_bridge || '',
        review_stream_draft_next_step: detail.review_stream_draft_next_step || '',
        review_stream_draft_transfer_signal: detail.review_stream_draft_transfer_signal || '',
    };
    const targetId = Number(normalized.id);
    const index = myCheckinsCache.findIndex((item) => Number(item.id || item.checkin_id) === targetId);
    if (index >= 0) {
        myCheckinsCache[index] = { ...myCheckinsCache[index], ...normalized };
    } else {
        myCheckinsCache.unshift(normalized);
    }
    return myCheckinsCache[index >= 0 ? index : 0];
}

async function refreshPendingCheckin(checkinId) {
    const item = await fetchMyCheckinById(checkinId);
    const merged = mergeCheckinDetailIntoCache(item);
    activeCheckinId = Number(checkinId);
    renderCheckinHistoryList();
    renderActiveCheckinWorkspace(merged);
    return merged;
}

function parseSseFrame(frameText) {
    const lines = String(frameText || '').split(/\r?\n/);
    let eventName = 'message';
    const dataLines = [];
    lines.forEach((line) => {
        if (!line) return;
        if (line.startsWith('event:')) {
            eventName = line.slice(6).trim() || 'message';
            return;
        }
        if (line.startsWith('data:')) {
            dataLines.push(line.slice(5).trimStart());
        }
    });
    let payload = null;
    const dataText = dataLines.join('\n').trim();
    if (dataText) {
        try {
            payload = JSON.parse(dataText);
        } catch (err) {
            payload = { raw: dataText };
        }
    }
    return { eventName, payload };
}

function schedulePollFallback(checkinId, resultEl) {
    const state = pendingReviewStreams.get(Number(checkinId));
    if (state) {
        state.fallbackStarted = true;
    }
    pollCheckinReviewStatus(checkinId, resultEl);
}

async function subscribeCheckinReviewStream(checkinId, resultEl) {
    stopCheckinPoll(checkinId);
    stopCheckinReviewStream(checkinId);

    const abortController = new AbortController();
    const streamState = {
        abortController,
        closed: false,
        terminal: false,
        fallbackStarted: false,
    };
    pendingReviewStreams.set(Number(checkinId), streamState);

    try {
        const res = await apiFetch(`${API_BASE}/api/checkins/${checkinId}/stream`, {
            signal: abortController.signal,
            headers: {
                Accept: 'text/event-stream',
            },
        });
        if (!res.body || typeof res.body.getReader !== 'function') {
            throw new Error('当前浏览器不支持流式读取');
        }
        const reader = res.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const frames = buffer.split(/\r?\n\r?\n/);
            buffer = frames.pop() || '';

            for (const frame of frames) {
                const trimmed = frame.trim();
                if (!trimmed) continue;
                const { eventName, payload } = parseSseFrame(trimmed);
                if (eventName === 'keepalive' || !payload) continue;

                const merged = mergeCheckinStreamPayloadIntoCache(checkinId, payload);
                activeCheckinId = Number(checkinId);
                renderCheckinHistoryList();
                renderActiveCheckinWorkspace(merged);

                if (eventName === 'review_ready' || payload.review_status === 'completed') {
                    streamState.terminal = true;
                    stopCheckinReviewStream(checkinId);
                    await refreshPendingCheckin(checkinId);
                    if (resultEl) {
                        resultEl.classList.remove('hidden');
                        resultEl.innerHTML = `
                            <div style="color: green; margin-bottom: 10px;">打卡成功，复盘已生成 (ID: ${escapeHtml(checkinId)})</div>
                            <div>右侧复盘工作区已经更新，可以继续做理解检查。</div>
                        `;
                    }
                    return;
                }

                if (eventName === 'error' || payload.review_status === 'failed') {
                    streamState.terminal = true;
                    stopCheckinReviewStream(checkinId);
                    await refreshPendingCheckin(checkinId);
                    if (resultEl) {
                        resultEl.classList.remove('hidden');
                        resultEl.innerHTML = `
                            <div style="color: #c0392b; margin-bottom: 10px;">复盘生成失败 (ID: ${escapeHtml(checkinId)})</div>
                            <div>右侧工作区可以直接重试。</div>
                        `;
                    }
                    return;
                }
            }
        }
    } catch (err) {
        if (abortController.signal.aborted || streamState.closed) return;
        console.warn('review stream fallback to polling:', err);
    } finally {
        const latest = pendingReviewStreams.get(Number(checkinId));
        if (latest === streamState) {
            pendingReviewStreams.delete(Number(checkinId));
        }
        if (!streamState.terminal && !streamState.closed && !streamState.fallbackStarted) {
            schedulePollFallback(checkinId, resultEl);
        }
    }
}

async function retryReviewGeneration(checkinId) {
    const res = await apiFetch(`${API_BASE}/api/checkins/${checkinId}/review/retry`, {
        method: 'POST',
        body: JSON.stringify({}),
    });
    const data = await res.json();
    const merged = mergeCheckinDetailIntoCache({
        id: data.checkin_id,
        checkin_id: data.checkin_id,
        review_status: data.review_status,
        poll_timed_out: false,
    });
    activeCheckinId = Number(checkinId);
    renderCheckinHistoryList();
    renderActiveCheckinWorkspace(merged);
    const resultEl = document.getElementById('checkin-result');
    if (resultEl) {
        resultEl.classList.remove('hidden');
        resultEl.style.color = '';
        resultEl.innerHTML = `
            <div style="color: green; margin-bottom: 10px;">${escapeHtml(data.message)}</div>
            <div style="margin-top: 8px; color: #666;">右侧工作区会自动刷新。</div>
        `;
    }
    subscribeCheckinReviewStream(checkinId, resultEl);
}

function pollCheckinReviewStatus(checkinId, resultEl) {
    stopCheckinReviewStream(checkinId);
    stopCheckinPoll(checkinId);
    const startedAt = Date.now();

    const step = async (attempt) => {
        try {
            const item = await fetchMyCheckinById(checkinId);
            const merged = mergeCheckinDetailIntoCache(item);
            activeCheckinId = Number(checkinId);
            renderCheckinHistoryList();
            renderActiveCheckinWorkspace(merged);

            if (merged.review_status === 'completed') {
                stopCheckinPoll(checkinId);
                if (resultEl) {
                    resultEl.classList.remove('hidden');
                    resultEl.innerHTML = `
                        <div style="color: green; margin-bottom: 10px;">打卡成功，复盘已生成 (ID: ${escapeHtml(checkinId)})</div>
                        <div>右侧复盘工作区已经更新，可以继续做理解检查。</div>
                    `;
                }
                loadMyCheckins(activeCheckinId);
                return;
            }

            if (merged.review_status === 'failed') {
                stopCheckinPoll(checkinId);
                if (resultEl) {
                    resultEl.classList.remove('hidden');
                    resultEl.innerHTML = `
                        <div style="color: #c0392b; margin-bottom: 10px;">复盘生成失败 (ID: ${escapeHtml(checkinId)})</div>
                        <div>右侧工作区可以直接重试。</div>
                    `;
                }
                return;
            }

            if (Date.now() - startedAt >= PENDING_REVIEW_POLL_TIMEOUT_MS) {
                stopCheckinPoll(checkinId);
                const timedOut = mergeCheckinDetailIntoCache({ ...merged, poll_timed_out: true });
                renderCheckinHistoryList();
                renderActiveCheckinWorkspace(timedOut);
                if (resultEl) {
                    resultEl.classList.remove('hidden');
                    resultEl.innerHTML = `
                        <div style="color: #8a6d3b; margin-bottom: 10px;">复盘生成时间较长 (ID: ${escapeHtml(checkinId)})</div>
                        <div>请刷新页面或稍后在历史记录里查看。</div>
                    `;
                }
                return;
            }

            const delay = attempt < PENDING_REVIEW_POLL_FAST_ATTEMPTS
                ? PENDING_REVIEW_POLL_FAST_INTERVAL_MS
                : PENDING_REVIEW_POLL_SLOW_INTERVAL_MS;
            const timerId = setTimeout(() => step(attempt + 1), delay);
            pendingReviewPolls.set(Number(checkinId), { timerId });
        } catch (err) {
            stopCheckinPoll(checkinId);
            if (resultEl) {
                resultEl.classList.remove('hidden');
                resultEl.innerHTML = `
                    <div style="color: #8a6d3b; margin-bottom: 10px;">打卡已提交 (ID: ${escapeHtml(checkinId)})</div>
                    <div style="margin-top: 8px; color: #c0392b;">自动刷新暂时失败：${escapeHtml(err.message)}</div>
                `;
            }
        }
    };

    step(0);
}

function showError(elementId, message) {
    document.getElementById(elementId).textContent = message;
}

function toggleExample() {
    const content = document.getElementById('example-content');
    const icon = document.querySelector('.toggle-icon');
    if (!content || !icon) return;
    content.classList.toggle('hidden');
    icon.textContent = content.classList.contains('hidden') ? '▼' : '▲';
}

window.toggleExample = toggleExample;

// ============ 初始化 ============

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('student-id').value = currentUserId || '';
    document.getElementById('login-problem-id').value = problemId;
    document.getElementById('student-problem-id').value = problemId;

    document.getElementById('enter-btn').addEventListener('click', handleEnter);
    document.getElementById('login-password').addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            handleEnter();
        }
    });
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    setupTabs();

    document.getElementById('check-quota-btn').addEventListener('click', studentCheckQuota);
    document.getElementById('student-problem-id').addEventListener('input', () => {
        activeChatProblemRef = normalizeProblemRef(document.getElementById('student-problem-id').value.trim());
        renderLinkedChatContextCard();
    });
    document.getElementById('send-btn').addEventListener('click', studentSendMessage);
    document.getElementById('clear-history-btn').addEventListener('click', clearChatHistory);
    document.getElementById('submit-checkin-btn').addEventListener('click', submitCheckin);
    document.getElementById('load-my-checkins-btn').addEventListener('click', loadMyCheckins);
    document.getElementById('open-history-tab-btn')?.addEventListener('click', () => showStudentTab('history-tab'));
    document.getElementById('import-problem-btn')?.addEventListener('click', importProblemFromUrl);
    document.getElementById('toggle-luogu-context-btn')?.addEventListener('click', () => {
        setLuoguSupplementExpanded(!luoguSupplementExpanded);
    });
    document.getElementById('checkin-oj')?.addEventListener('change', () => {
        syncCheckinSourceInputs();
        if (typeof window.validateCheckinForm === 'function') {
            window.validateCheckinForm();
        }
    });
    document.getElementById('checkin-url')?.addEventListener('input', () => {
        if (document.getElementById('checkin-url').value.trim() !== importedProblemMeta.problemUrl) {
            resetImportedProblemMeta();
            updateProblemTagsPreview([]);
            if (document.getElementById('checkin-oj')?.value === 'luogu') {
                setProblemImportStatus('链接已更新，可重新自动导入题面和标签。');
            }
        }
        if (typeof window.validateCheckinForm === 'function') {
            window.validateCheckinForm();
        }
    });

    setupCheckinValidation();
    activeChatProblemRef = normalizeProblemRef(problemId);
    syncCheckinSourceInputs();
    renderLinkedChatContextCard();

    document.getElementById('teacher-check-quota-btn').addEventListener('click', teacherCheckQuota);
    document.getElementById('reset-quota-btn').addEventListener('click', teacherResetQuota);
    document.getElementById('load-all-checkins-btn').addEventListener('click', loadAllCheckins);
    document.getElementById('load-stats-btn').addEventListener('click', loadErrorStats);
    document.getElementById('load-flags-btn').addEventListener('click', loadStudentFlags);
    document.getElementById('load-usage-btn').addEventListener('click', loadUsageStats);
    document.getElementById('load-manual-review-btn').addEventListener('click', loadTeacherReviewSamples);
    document.getElementById('retry-pending-btn').addEventListener('click', retryPendingReviews);
    document.getElementById('retry-problem-analysis-btn').addEventListener('click', retryProblemAnalysis);
    document.getElementById('load-analysis-failures-btn').addEventListener('click', loadProblemAnalysisFailures);

    setupRichTextObserver();
    setupTeacherManualReviewPanel();
    setupTeacherStatsInteractions();

    if (authToken && currentUserId && userRole) {
        showMainInterface();
    }
});

function setupTabs() {
    const studentTabs = document.querySelectorAll('#student-tabs .tab-btn');
    studentTabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            showStudentTab(tab.dataset.tab);
        });
    });

    const teacherTabs = document.querySelectorAll('#teacher-tabs .tab-btn');
    teacherTabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            showTeacherTab(tab.dataset.tab);
        });
    });
}

function showTeacherTab(targetId) {
    const teacherTabs = document.querySelectorAll('#teacher-tabs .tab-btn');
    document.querySelectorAll('#teacher-section .tab-content').forEach((content) => content.classList.add('hidden'));
    document.getElementById(targetId)?.classList.remove('hidden');
    teacherTabs.forEach((btn) => btn.classList.toggle('active', btn.dataset.tab === targetId));
    if (targetId === 'manual-review-tab') {
        loadTeacherReviewSamples();
    }
}

// ============ 登录 / 退出 ============

async function handleEnter() {
    const userIdInput = document.getElementById('student-id').value.trim();
    const password = document.getElementById('login-password').value.trim();
    const loginProblemId = document.getElementById('login-problem-id').value.trim() || 'P1001';

    if (!userIdInput) {
        showError('login-error', '请输入账号 ID');
        return;
    }
    if (!password) {
        showError('login-error', '请输入密码');
        return;
    }

    try {
        const res = await apiFetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            auth: false,
            body: JSON.stringify({
                user_id: userIdInput,
                password,
            }),
        });
        const data = await res.json();

        currentUserId = data.user_id;
        userRole = data.role;
        authToken = data.token;
        problemId = loginProblemId;
        sessionId = generateSessionId();
        persistAuthState();

        document.getElementById('login-error').textContent = '';
        document.getElementById('login-password').value = '';
        showMainInterface();
    } catch (err) {
        showError('login-error', '登录失败: ' + err.message);
    }
}

function handleLogout() {
    document.getElementById('student-id').value = '';
    redirectToLogin('');
    document.getElementById('login-error').textContent = '';
}

function showMainInterface() {
    loginSection.classList.add('hidden');
    userBar.classList.remove('hidden');

    document.getElementById('current-user').textContent = currentUserId;
    document.getElementById('current-role').textContent = userRole === 'teacher' ? '教师' : '学生';
    document.getElementById('student-problem-id').value = problemId;
    document.getElementById('login-problem-id').value = problemId;

    if (userRole === 'teacher') {
        studentSection.classList.add('hidden');
        teacherSection.classList.remove('hidden');
        loadAllCheckins();
        loadErrorStats();
        loadUsageStats();
        loadStudentFlags();
        loadProblemAnalysisFailures();
    } else {
        studentSection.classList.remove('hidden');
        teacherSection.classList.add('hidden');
        showStudentTab(document.querySelector('#student-tabs .tab-btn.active')?.dataset.tab || 'chat-tab');
        studentCheckQuota();
        loadMyCheckins();
    }
}

// ============ 学生功能 ============

async function studentCheckQuota() {
    const pid = document.getElementById('student-problem-id').value.trim() || problemId;
    problemId = pid;
    activeChatProblemRef = normalizeProblemRef(pid);
    localStorage.setItem('noi_problem_id', problemId);
    renderLinkedChatContextCard();

    try {
        const res = await apiFetch(`${API_BASE}/quota/${currentUserId}/${pid}`);
        const data = await res.json();
        document.getElementById('quota-info').textContent =
            `题目: ${data.problem_id} | 已用: ${data.count}/${data.max} | 剩余: ${data.remaining}`;
    } catch (err) {
        document.getElementById('quota-info').textContent = '查询失败: ' + err.message;
    }
}

async function studentSendMessage() {
    const pid = document.getElementById('student-problem-id').value.trim() || problemId;
    const message = document.getElementById('student-message').value.trim();
    if (!message) return;

    problemId = pid;
    activeChatProblemRef = normalizeProblemRef(pid);
    localStorage.setItem('noi_problem_id', problemId);

    addChatMessage('user', message);
    document.getElementById('student-message').value = '';

    try {
        const res = await apiFetch(`${API_BASE}/chat`, {
            method: 'POST',
            body: JSON.stringify({
                student_id: currentUserId,
                problem_id: pid,
                message,
                session_id: sessionId,
            }),
        });
        const data = await res.json();
        addChatMessage('assistant', data.reply);
        rememberProblemChatContext(activeChatProblemRef || pid, message, data.reply, data.handoff_payload);
        renderLinkedChatContextCard();
        document.getElementById('quota-info').textContent =
            `剩余配额: ${data.remaining_quota} | 本次级别: ${data.level}`;
    } catch (err) {
        addChatMessage('assistant', '错误: ' + err.message);
    }
}

function addChatMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const strong = document.createElement('strong');
    strong.textContent = role === 'user' ? '你:' : 'Agent:';

    const pre = document.createElement('pre');
    pre.textContent = content;

    div.appendChild(strong);
    div.appendChild(pre);
    document.getElementById('chat-history').appendChild(div);
    document.getElementById('chat-history').scrollTop = document.getElementById('chat-history').scrollHeight;
}

function clearChatHistory() {
    document.getElementById('chat-history').innerHTML = '';
    removeProblemChatContext(activeChatProblemRef || document.getElementById('student-problem-id').value.trim() || problemId);
    renderLinkedChatContextCard();
    sessionId = generateSessionId();
    localStorage.setItem('noi_session_id', sessionId);
}

let isSubmittingCheckin = false;

function setupCheckinValidation() {
    const bottleneckInput = document.getElementById('checkin-bottleneck');
    const contextInput = document.getElementById('checkin-problem-context');
    const titleInput = document.getElementById('checkin-title');
    const urlInput = document.getElementById('checkin-url');
    const ojSelect = document.getElementById('checkin-oj');
    const countEl = document.getElementById('bottleneck-count');
    const contextCountEl = document.getElementById('context-count');
    const hintEl = document.getElementById('bottleneck-hint');
    const contextHintEl = document.getElementById('context-hint');
    const submitBtn = document.getElementById('submit-checkin-btn');
    const invalidKeywords = ['不会', '没思路', '不知道', '不懂', '太难了'];
    const detailSignalKeywords = [
        '题意', '条件', '样例', '状态', '转移', '边界', '特判', '数组', '越界', '溢出',
        '复杂度', '代码', '报错', '提交', 'check', '贪心', '背包', '二分', 'dp', '图',
        '建模', '递归', '枚举', '排序', '最短路', '前缀和', '并查集', 'dfs', 'bfs',
        'wa', 'tle', 're',
    ];

    function validate() {
        // 卡点描述校验
        const text = bottleneckInput.value.trim();
        const len = text.length;
        const lowered = text.toLowerCase();
        const hasInvalidKeyword = invalidKeywords.some((kw) => text.includes(kw));
        const hasDetailSignal = detailSignalKeywords.some((kw) => lowered.includes(kw));

        countEl.textContent = `${len} 字`;

        let bottleneckOk = true;
        let hint = '';

        if (len < 15) {
            bottleneckOk = false;
            hint = `还需要 ${15 - len} 字`;
            countEl.style.color = '#e74c3c';
        } else if (len < 35 && hasInvalidKeyword && !hasDetailSignal) {
            bottleneckOk = false;
            hint = '请补充方法、卡住的步骤或报错现象';
            countEl.style.color = '#f39c12';
        } else {
            countEl.style.color = '#27ae60';
        }

        hintEl.textContent = hint || '✓ 长度达标';
        hintEl.style.color = bottleneckOk ? '#27ae60' : (len < 15 ? '#e74c3c' : '#f39c12');

        const ojSource = ojSelect ? ojSelect.value : 'other';
        const problemUrl = urlInput ? urlInput.value.trim() : '';
        const hasValidLuoguUrl = ojSource === 'luogu' && isLikelyLuoguProblemRef(problemUrl);

        // 题面 / Markdown 校验
        const ctxText = contextInput ? contextInput.value.trim() : '';
        const ctxLen = ctxText.length;
        const contextOk = ojSource === 'luogu' ? (ctxLen >= 10 || hasValidLuoguUrl) : ctxLen >= 10;

        if (contextCountEl) {
            contextCountEl.textContent = `${ctxLen} 字`;
            contextCountEl.style.color = contextOk ? '#27ae60' : '#e74c3c';
        }
        if (contextHintEl) {
            if (ojSource === 'luogu') {
                if (ctxLen >= 10) {
                    contextHintEl.textContent = '✓ 已填写或已导入题面';
                    contextHintEl.style.color = '#27ae60';
                } else if (hasValidLuoguUrl) {
                    contextHintEl.textContent = '✓ 已填写洛谷链接，提交时可自动导入题面';
                    contextHintEl.style.color = '#27ae60';
                } else {
                    contextHintEl.textContent = '请输入有效洛谷题号 / 链接，或手动补充题面 / Markdown';
                    contextHintEl.style.color = '#e74c3c';
                }
            } else {
                contextHintEl.textContent = contextOk ? '✓ 已填写' : `还需要 ${10 - ctxLen} 字`;
                contextHintEl.style.color = contextOk ? '#27ae60' : '#e74c3c';
            }
        }

        const hasTitle = !!titleInput.value.trim() || hasValidLuoguUrl;
        const hasErrorType = document.querySelector('input[name="error_type"]:checked');
        submitBtn.disabled = !(bottleneckOk && contextOk && hasTitle && hasErrorType);
        renderLinkedChatContextCard();
    }

    bottleneckInput.addEventListener('input', validate);
    if (contextInput) contextInput.addEventListener('input', validate);
    if (titleInput) titleInput.addEventListener('input', validate);
    if (urlInput) urlInput.addEventListener('input', validate);
    if (ojSelect) ojSelect.addEventListener('change', validate);

    document.querySelectorAll('input[name="error_type"]').forEach((cb) => {
        cb.addEventListener('change', validate);
    });

    window.validateCheckinForm = validate;
    validate();
}

function renderReviewHtml(review, family = reviewFamilyUi.resolveReviewFamily(review)) {
    if (!review) return '';
    const orderedSections = reviewFamilyUi
        .orderedReviewSections(review, family)
        .filter((section) => String(section?.value || '').trim());
    const detailsDrawerHtml = renderReviewDetailsDrawer(review);

    return `
        <div class="review-note-flow family-${escapeHtml(family)}">
            <section class="review-note-sheet review-note-sheet-primary">
                <div class="review-note-body">
                    ${orderedSections.map((section) => renderReviewNoteSection(section)).join('')}
                </div>
            </section>
            ${detailsDrawerHtml}
        </div>
    `;
}

function renderLearningPathPlaceholder(item = {}) {
    if (item.review_status === 'failed') {
        return `
            <div class="learning-stage-card learning-stage-entry">
                <div class="learning-stage-header">
                    <div class="learning-stage-kicker">学习路径暂停</div>
                    <div class="learning-stage-question">这次复盘暂时没有生成成功</div>
                    <div class="learning-stage-subtitle">你的打卡已经保存下来了，可以先看右侧提示，稍后重新生成后再继续这条路径。</div>
                </div>
            </div>
        `;
    }
    if (item.poll_timed_out) {
        return `
            <div class="learning-stage-card learning-stage-entry">
                <div class="learning-stage-header">
                    <div class="learning-stage-kicker">学习路径等待中</div>
                    <div class="learning-stage-question">这次复盘生成时间有点长</div>
                    <div class="learning-stage-subtitle">可以先刷新，或者稍后从历史记录回来继续；理解检查会在复盘就绪后接上。</div>
                </div>
            </div>
        `;
    }
    return `
        <div class="learning-stage-card learning-stage-entry">
            <div class="learning-stage-header">
                <div class="learning-stage-kicker">学习路径入口</div>
                <div class="learning-stage-question">复盘生成后，这里会出现这一小步的理解检查</div>
                <div class="learning-stage-subtitle">我们会把讲义、自评和补救收成同一条路径，等复盘出来就能继续往下走。</div>
            </div>
        </div>
    `;
}

function dynamicRemedyLabel(errorLayer) {
    const map = {
        reading: '我还是没看清这题到底要我做什么',
        method: '我还是看不出来为什么该用这个方法',
        modeling: '我还是不知道怎么把题目变成模型',
        core_design: '我还是不明白这一步为什么这样设计',
        implementation: '我还是不知道这一步代码怎么写',
        insufficient: '我还是说不清自己具体卡在哪',
    };
    return map[errorLayer] || map.insufficient;
}

function selfCheckLabel(status) {
    const map = {
        clear: '我能自己说一遍这一步',
        guessed: '感觉对，但有点蒙',
        confused: '还是没懂',
    };
    return map[status] || '';
}

function bridgePathDisplayText(path) {
    const map = {
        main_clear: '首轮答对，学生自评能讲清',
        main_guessed_confirm: '首轮答对，但自评有点蒙；确认后过桥',
        main_guessed_remedy: '首轮答对，但自评有点蒙；最终进入补救',
        main_confused_remedy: '首轮答对，但学生主动承认没懂；进入补救',
        followup_correct: '首轮未过，在微提示后过桥',
        followup_remedy: '首轮未过，最终进入补救',
    };
    return map[path] || path || '';
}

function bridgePathTeacherBadge(path) {
    const map = {
        main_clear: { label: '独立过桥', className: 'teacher-evidence strong' },
        main_guessed_confirm: { label: '确认后过桥', className: 'teacher-evidence medium' },
        main_guessed_remedy: { label: '补救后过桥', className: 'teacher-evidence support' },
        main_confused_remedy: { label: '主动承认没懂后补救', className: 'teacher-evidence honest' },
        followup_correct: { label: '提示后过桥', className: 'teacher-evidence prompted' },
        followup_remedy: { label: '提示后仍需补救', className: 'teacher-evidence support' },
    };
    return map[path] || null;
}

function bridgePathTeacherNote(path) {
    const map = {
        main_clear: '这次主要证据来自首轮答对和学生自评，说明这一步更像是学生自己先站稳了。',
        main_guessed_confirm: '学生首轮答对，但自己承认“有点蒙”，最后通过换角度确认才过桥，说明理解是后来补稳的。',
        main_guessed_remedy: '学生首轮虽然答对，但自评并不稳，最终还是进入补救，不能把这次判断成独立掌握。',
        main_confused_remedy: '学生首轮答对后主动承认没懂，这类记录对老师很有价值，说明学生愿意暴露真实困惑，补救才是关键证据。',
        followup_correct: '这一步是在微提示之后过桥的，说明学生需要脚手架支持，不能按“完全独立起步”理解。',
        followup_remedy: '首轮和 follow-up 都没打通，最后还要靠补救，这通常意味着这座桥对学生来说还不稳。',
    };
    return map[path] || '';
}

function teacherBridgeKey(item) {
    if (item.review_status !== 'completed' || !item.review_error_layer) return '';
    if (item.review_error_layer === 'core_design' && item.review_core_design_subtags?.length) {
        return `core_design:${item.review_core_design_subtags[0]}`;
    }
    return item.review_error_layer;
}

function teacherBridgeLabel(item) {
    if (item.review_error_layer === 'core_design' && item.review_core_design_subtags?.length) {
        return `${errorLayerText(item.review_error_layer)} / ${coreDesignSubtagText(item.review_core_design_subtags[0])}`;
    }
    return errorLayerText(item.review_error_layer);
}

function annotateTeacherCheckins(items) {
    const totals = new Map();
    for (const item of items) {
        const key = teacherBridgeKey(item);
        if (!key || !item.student_id) continue;
        const compound = `${item.student_id}::${key}`;
        totals.set(compound, (totals.get(compound) || 0) + 1);
    }

    const seen = new Set();
    return items.map((item) => {
        const key = teacherBridgeKey(item);
        if (!key || !item.student_id) return item;
        const compound = `${item.student_id}::${key}`;
        const total = totals.get(compound) || 0;
        if (total >= 2 && !seen.has(compound)) {
            seen.add(compound);
            return {
                ...item,
                teacher_repeat_bridge_hint: `在最近加载的记录里，这已经是该生第 ${total} 次卡在「${teacherBridgeLabel(item)}」相关桥梁。`,
            };
        }
        seen.add(compound);
        return item;
    });
}

function reviewQualityFlagText(flag) {
    const map = {
        algorithm_name_leaked: '学生端复盘里提前出现了算法名，建议回看这条复盘是否“教得太满”了。',
    };
    return map[flag] || flag || '';
}

function renderReviewQualityFlags(flags) {
    if (!flags?.length) return '';
    const chips = flags
        .map((flag) => `<span class="tag-pill subtle-tag teacher-quality-chip">${escapeHtml(flag)}</span>`)
        .join('');
    const notes = flags
        .map((flag) => `<p class="archive-note teacher-quality-note"><strong>质检提示：</strong>${escapeHtml(reviewQualityFlagText(flag))}</p>`)
        .join('');
    return `
        <div class="archive-chip-row">${chips}</div>
        ${notes}
    `;
}

function renderQuizOptions(quiz, reviewId) {
    if (!quiz) return '';
    if (quiz.quiz_type === 'short_fill') {
        return `
            <input type="text" id="quiz-answer-${reviewId}" class="quiz-input" placeholder="输入你的答案">
        `;
    }
    return `
        <div class="quiz-options">
            ${(quiz.options || []).map((option, idx) => {
                const optionValue = typeof option === 'object' && option !== null ? option.value : option;
                const optionLabel = typeof option === 'object' && option !== null ? option.label : option;
                return `
                <label class="quiz-option">
                    <input type="radio" name="quiz-option-${reviewId}" value="${escapeHtml(optionValue)}">
                    <span>${renderRichTextInline(optionLabel)}</span>
                </label>
            `;
            }).join('')}
        </div>
    `;
}

function quizCardTitle(quiz) {
    return learningQuizStageCopy(quiz).title;
}

function quizCardLead(quiz) {
    const level = normalizeLearningQuizStage(quiz);
    if (level === 'followup') {
        return '我们只再盯这一小步，不把整题一下子展开。';
    }
    if (level === 'confirm') {
        return '换个角度再看一眼，确认你真的抓住了。';
    }
    if (level === 'knowledge_confirm') {
        return '先看讲解，再把这一问收一收。';
    }
    if (level === 'final_micro_confirm') {
        return '只做最后一个最小确认，看看这一步是不是已经稳了。';
    }
    return '先把这一小步抓稳，我们再往下。';
}

function normalizeLearningQuizStage(quiz) {
    const rawLevel = String(quiz?.meta?.difficulty_level || quiz?.difficulty_level || 'main').trim();
    if (rawLevel === 'easier') return 'followup';
    return rawLevel || 'main';
}

function learningQuizStageCopy(quiz) {
    const stage = normalizeLearningQuizStage(quiz);
    const copy = {
        main: {
            label: '主线确认',
            title: '先确认你是不是已经抓住了这一步了',
            subtitle: '我们先只盯这一小步，不把整题一下子铺开。',
        },
        followup: {
            label: '再拆小一点',
            title: '这一步还差一点，我们再拆小一点',
            subtitle: '先把这一步缩到更具体的动作，再来确认一次。',
        },
        confirm: {
            label: '换个角度',
            title: '换个角度，再确认一次',
            subtitle: '这不是重讲一遍，而是换一条路再看你有没有真的抓住。',
        },
        knowledge_confirm: {
            label: '讲解后确认',
            title: '看完上面的讲解，再做最后一次确认',
            subtitle: '先把讲义里的解释吃透，再用这一题收个尾。',
        },
        final_micro_confirm: {
            label: '最小收尾',
            title: '最后用一个最小问题收尾确认',
            subtitle: '只做最后一个最小确认，看看这一小步是不是已经稳了。',
        },
    };
    return { stage, ...((copy[stage] || copy.main)) };
}

function renderLearningStageHeader(quiz) {
    const stageCopy = learningQuizStageCopy(quiz);
    return `
        <div class="learning-stage-header">
            <div class="learning-stage-kicker">理解检查 · ${escapeHtml(stageCopy.label)}</div>
            <div class="learning-stage-question">${escapeHtml(stageCopy.title)}</div>
            <div class="learning-stage-subtitle">${escapeHtml(stageCopy.subtitle)}</div>
        </div>
    `;
}

function renderQuizCard(quiz, reviewId) {
    if (!quiz) return '';
    const stageCopy = learningQuizStageCopy(quiz);
    const knowledgeBailoutCard = stageCopy.stage === 'knowledge_confirm' && quiz.meta?.knowledge_bailout && quiz.meta?.knowledge_card
        ? renderKnowledgeBailoutCard(quiz.meta.knowledge_card)
        : '';
    const microHint = quiz.meta?.micro_hint
        ? `<div class="learning-stage-note">先提醒一句：${renderRichTextInline(quiz.meta.micro_hint)}</div>`
        : '';
    const lead = quizCardLead(quiz)
        ? `<div class="learning-stage-lead">${escapeHtml(quizCardLead(quiz))}</div>`
        : '';
    return `
        <div class="learning-stage-card learning-stage-quiz" data-quiz-stage="${escapeHtml(stageCopy.stage)}">
            ${renderLearningStageHeader(quiz)}
            ${knowledgeBailoutCard}
            ${lead}
            ${microHint}
            <div class="learning-stage-question">${renderRichTextBlock(quiz.question_text)}</div>
            <div class="learning-stage-body">
                ${renderQuizOptions(quiz, reviewId)}
            </div>
            <div class="learning-stage-submit">
                <button class="secondary learning-stage-submit-btn" onclick="submitQuizAnswer(${Number(quiz.quiz_id)}, ${Number(reviewId)})">提交答案</button>
            </div>
        </div>
    `;
}

function renderQuizFeedbackBlock({ title, feedbackText = '', bridgeFeedback = '', explanation = '', tone = 'success' }) {
    return `
        <div class="learning-stage-card learning-path-feedback ${escapeHtml(tone)}">
            <div class="learning-stage-header">
                <div class="learning-stage-kicker">讲义批注</div>
                <div class="learning-stage-question">${escapeHtml(title)}</div>
                <div class="learning-stage-subtitle">这里不是在重新判分，只是在这一步上多写一条批注，帮你把路走顺。</div>
            </div>
            ${feedbackText ? `<div class="learning-path-feedback-text">${renderRichTextBlock(feedbackText)}</div>` : ''}
            ${bridgeFeedback ? `<div class="learning-path-feedback-bridge"><strong>这里真正抓住的是：</strong>${renderRichTextInline(bridgeFeedback)}</div>` : ''}
            ${explanation ? `<div class="learning-path-feedback-explanation">${renderRichTextBlock(explanation)}</div>` : ''}
        </div>
    `;
}

function renderKnowledgeBailoutCard(card = {}) {
    if (!card || typeof card !== 'object') return '';

    const opening = String(card.opening || card.knowledge_opening || '').trim();
    const bridge = String(card.bridge_explanation || card.bridge || '').trim();
    const wrongThinking = String(card.wrong_thinking || card.common_misunderstanding || '').trim();
    const rightThinking = String(card.right_thinking || card.correct_understanding || '').trim();
    const visualHint = String(card.visual_hint || '').trim();
    const microAction = String(card.micro_action || card.micro_action_text || '').trim();
    const overview = String(card.algorithm_overview || card.overview || '').trim();

    const comparisonHtml = (wrongThinking || rightThinking) ? `
        <div class="knowledge-note-comparison">
            <div class="knowledge-note-comparison-col">
                <div class="knowledge-note-section-title">常见误解</div>
                <div class="knowledge-note-comparison-body">${wrongThinking ? renderRichTextBlock(wrongThinking) : '<p class="mb-0 text-slate-400">先看这一步容易想偏在哪里。</p>'}</div>
            </div>
            <div class="knowledge-note-comparison-col">
                <div class="knowledge-note-section-title">正确理解</div>
                <div class="knowledge-note-comparison-body">${rightThinking ? renderRichTextBlock(rightThinking) : '<p class="mb-0 text-slate-400">这里才是这一步真正要抓住的意思。</p>'}</div>
            </div>
        </div>
    ` : '';

    const visualHtml = visualHint ? `
        <div class="knowledge-note-visual">
            <div class="knowledge-note-section-title">看一眼图景</div>
            <pre>${escapeHtml(visualHint)}</pre>
        </div>
    ` : '';

    const summaryHtml = microAction ? `
        <div class="knowledge-note-summary">
            <div class="knowledge-note-section-title">你现在先做</div>
            <div>${renderRichTextInline(microAction)}</div>
        </div>
    ` : '';

    const overviewHtml = overview ? `
        <div class="knowledge-note-overview">
            <div class="knowledge-note-section-title">整体收束</div>
            <div>${renderRichTextBlock(overview)}</div>
        </div>
    ` : '';

    return `
        <div class="knowledge-note-sheet">
            <div class="knowledge-note-header">
                <div class="learning-kicker">知识兜底 · 学习手册</div>
                <div class="knowledge-note-title">先把这块知识单独讲清楚</div>
                <div class="knowledge-note-opening">${opening ? renderRichTextBlock(opening) : '我们先把这块知识拆出来单独看，再回到题目里收口。'}</div>
            </div>
            <div class="knowledge-note-body">
                ${bridge ? `
                    <div class="knowledge-note-bridge">
                        <div class="knowledge-note-section-title">这一步怎么接上</div>
                        <div>${renderRichTextBlock(bridge)}</div>
                    </div>
                ` : ''}
                ${comparisonHtml}
                ${visualHtml}
                ${summaryHtml}
                ${overviewHtml}
            </div>
        </div>
    `;
}

function renderSelfCheckCard(reviewId, family = 'failure_diagnosis') {
    const copy = reviewFamilyUi.reviewFeedbackCopy(family);
    const subtitle = family === 'success_reflection'
        ? '试着用自己的话说清这条思路为什么成立，再决定要不要继续往下走。'
        : '先判断你现在是不是真的知道该先查哪一步，再决定下一步怎么走。';
    return `
        <div class="learning-stage-card self-check-card-v2">
            <div class="learning-stage-header">
                <div class="learning-stage-kicker">自我确认</div>
                <div class="learning-stage-question">${escapeHtml(copy.title)}</div>
                <div class="learning-stage-subtitle">${escapeHtml(subtitle)}</div>
            </div>
            <div class="self-check-actions-v2">
                <button class="self-check-option-v2 tone-clear" onclick="submitSelfCheck(${Number(reviewId)}, 'clear')">${escapeHtml(copy.clearLabel)}</button>
                <button class="self-check-option-v2 tone-guessed" onclick="submitSelfCheck(${Number(reviewId)}, 'guessed')">${escapeHtml(copy.guessedLabel)}</button>
                <button class="self-check-option-v2 tone-confused" onclick="submitSelfCheck(${Number(reviewId)}, 'confused')">${escapeHtml(copy.confusedLabel)}</button>
            </div>
        </div>
    `;
}

function renderRemedyButtons(reviewId, errorLayer, options = {}) {
    const dynamicLabel = options.dynamicLabel || dynamicRemedyLabel(errorLayer);
    const includeResolve = options.includeResolve === true;
    return `
        <div class="learning-stage-card learning-remedy-card">
            <div class="learning-stage-header">
                <div class="learning-stage-kicker">继续带一遍</div>
                <div class="learning-stage-question">我们换一种带法，继续过这一步</div>
                <div class="learning-stage-subtitle">不用一次把整题推完，我们先沿着这一小步往前走。</div>
            </div>
            <div class="learning-remedy-actions">
                ${includeResolve ? `<button class="secondary" onclick="resolveRemedy(${Number(reviewId)}, 'resolved')">这一步我现在懂了</button>` : ''}
                <button class="secondary" onclick="triggerRemedy(${Number(reviewId)}, 'rephrase')">换个说法再讲一遍</button>
                <button class="secondary" onclick="triggerRemedy(${Number(reviewId)}, 'smaller_example')">先换一个更小的例子</button>
                <button class="secondary" onclick="triggerRemedy(${Number(reviewId)}, 'easier_quiz')">再来一道更小的问题</button>
                <button class="secondary" onclick="triggerRemedy(${Number(reviewId)}, 'dynamic_bridge_help')">${escapeHtml(dynamicLabel)}</button>
            </div>
        </div>
    `;
}

function renderLearningSection(item) {
    const reviewId = item.review_id;
    if (!reviewId) return '';
    const reviewFamily = reviewFamilyUi.resolveReviewFamily(item);

    const sectionId = `review-quiz-${reviewId}`;
    let content = '';

    if (item.review_status !== 'completed') {
        content = renderLearningPathPlaceholder(item);
    } else if (item.review_learning_status === 'self_check_required') {
        content = `
            ${renderQuizFeedbackBlock({
                title: item.quiz_latest_feedback || '答对了，这一步你跨过去了。',
                bridgeFeedback: item.quiz_bridge_feedback,
                explanation: item.quiz_explanation,
                tone: 'success',
            })}
            ${renderSelfCheckCard(reviewId, reviewFamily)}
        `;
    } else if (item.review_learning_status === 'resolved') {
        content = renderQuizFeedbackBlock({
            title: '答对了，这一步你跨过去了。',
            feedbackText: item.quiz_latest_feedback,
            bridgeFeedback: item.quiz_bridge_feedback,
            explanation: item.quiz_explanation,
            tone: 'success',
        });
    } else if (item.review_learning_status === 'needs_teacher_followup') {
        content = renderQuizFeedbackBlock({
            title: '这道题我们先停在这里，你的老师会来和你一起看一看。',
            feedbackText: item.quiz_latest_feedback,
            bridgeFeedback: item.quiz_bridge_feedback,
            explanation: item.quiz_explanation,
            tone: 'final',
        });
    } else if (item.quiz_status === 'pending' && item.quiz_id) {
        content = renderQuizCard({
            quiz_id: item.quiz_id,
            quiz_type: item.quiz_type,
            question_text: item.quiz_question_text,
            options: item.quiz_options,
            meta: item.quiz_meta || {},
        }, reviewId);
    } else if (item.review_learning_status === 'remedy_available' || item.review_learning_status === 'remedy_in_progress') {
        const remedyTransition = resolveRemedyTransition({
            understandingSelfCheck: item.review_understanding_self_check,
            quizRole: item.quiz_role,
            feedbackText: item.quiz_latest_feedback,
            explanation: item.quiz_explanation,
        });
        content = `
            ${renderRemedyTransitionCard(remedyTransition)}
            ${renderRemedyButtons(reviewId, item.review_error_layer)}
        `;
    } else {
        content = `
            <div class="learning-stage-card learning-stage-entry">
                <div class="learning-stage-header">
                    <div class="learning-stage-kicker">学习路径入口</div>
                    <div class="learning-stage-question">复盘看完后，再来一道小题确认你是不是已经懂了</div>
                    <div class="learning-stage-subtitle">先点开这一小步，我们会继续沿着同一条路径往下走。</div>
                </div>
                <div class="learning-stage-submit">
                    <button class="secondary learning-stage-submit-btn" onclick="startReviewQuiz(${Number(reviewId)})">开始这一小步的理解检查</button>
                </div>
            </div>
        `;
    }

    return `<div id="${sectionId}" class="review-learning-section">${content}</div>`;
}

async function submitCheckin() {
    if (isSubmittingCheckin) return;
    isSubmittingCheckin = true;

    const submitBtn = document.getElementById('submit-checkin-btn');
    const resultEl = document.getElementById('checkin-result');
    submitBtn.disabled = true;
    submitBtn.textContent = '提交中...';
    if (resultEl) {
        resultEl.classList.add('hidden');
        resultEl.innerHTML = '';
        resultEl.style.color = '';
    }

    const problemUrl = document.getElementById('checkin-url')?.value.trim() || '';
    const problemTitle = document.getElementById('checkin-title').value.trim();
    const ojSource = document.getElementById('checkin-oj').value;
    const completionStatus = document.getElementById('checkin-status').value;
    const submissionResult = document.getElementById('checkin-submission-result')?.value || null;
    const bottleneckText = document.getElementById('checkin-bottleneck').value.trim();
    const problemContext = document.getElementById('checkin-problem-context')?.value.trim() || '';
    const studentCode = document.getElementById('checkin-student-code')?.value.trim() || null;
    const reflection = document.getElementById('checkin-reflection').value.trim();
    const errorTypes = [];
    document.querySelectorAll('input[name="error_type"]:checked').forEach((cb) => {
        errorTypes.push(cb.value);
    });
    const hasLuoguUrl = ojSource === 'luogu' && isLikelyLuoguProblemRef(problemUrl);
    const linkedProblemRef = resolveCurrentCheckinProblemRef();
    const linkedChatContext = getProblemChatContext(linkedProblemRef);
    const chatContextSummary = linkedChatContext?.summary || '';
    const handoffPayload = linkedChatContext?.handoffPayload || null;

    if (!problemTitle && !hasLuoguUrl) {
        resultEl.classList.remove('hidden');
        resultEl.textContent = '请填写题目标题，或提供可自动导入的洛谷链接';
        resultEl.style.color = 'red';
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
        return;
    }
    if (ojSource !== 'luogu' && problemContext.length < 10) {
        resultEl.classList.remove('hidden');
        resultEl.textContent = ojSource === 'other'
            ? '来源为未区分 / 其他时，题面 / Markdown 至少10个字'
            : '当前来源暂不支持自动导入，请至少粘贴10个字的题面 / Markdown';
        resultEl.style.color = 'red';
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
        return;
    }
    if (ojSource === 'luogu' && problemContext.length < 10 && !hasLuoguUrl) {
        resultEl.classList.remove('hidden');
        resultEl.textContent = '请填写有效的洛谷题号 / 链接，或手动补充题面 / Markdown';
        resultEl.style.color = 'red';
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
        return;
    }
    if (bottleneckText.length < 15) {
        resultEl.classList.remove('hidden');
        resultEl.textContent = '卡点描述至少15个字';
        resultEl.style.color = 'red';
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
        return;
    }
    if (errorTypes.length === 0) {
        resultEl.classList.remove('hidden');
        resultEl.textContent = '请至少选择一个错误类型';
        resultEl.style.color = 'red';
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
        return;
    }

    try {
        const res = await apiFetch(`${API_BASE}/api/checkins`, {
            method: 'POST',
            body: JSON.stringify({
                problem_url: problemUrl,
                problem_title: problemTitle,
                oj_source: ojSource,
                completion_status: completionStatus,
                bottleneck_text: bottleneckText,
                error_types: errorTypes,
                reflection: reflection || null,
                problem_context: problemContext,
                problem_tags: importedProblemMeta.problemTags || [],
                chat_context_summary: chatContextSummary,
                handoff_payload: handoffPayload,
                submission_result: submissionResult,
                student_code: studentCode || null,
            }),
        });
        const data = await res.json();
        void postReviewEvent(data, 'review_request_submitted', buildReviewRequestSubmittedPayload(data, {
            problem_id: linkedProblemRef || '',
            problem_title: resolvedProblemTitleFromForm(problemTitle, importedProblemMeta.problemPid),
            review_mode: data.review_mode || '',
            review_family: data.review_family || '',
            has_code: Boolean(studentCode && String(studentCode).trim()),
            problem_context_length: problemContext.length,
            bottleneck_text_length: bottleneckText.length,
        }));
        showStudentTab('checkin-tab');
        const draftItem = {
            id: data.checkin_id,
            checkin_id: data.checkin_id,
            problem_title: resolvedProblemTitleFromForm(problemTitle, importedProblemMeta.problemPid),
            problem_url: importedProblemMeta.problemUrl || problemUrl,
            oj_source: ojSource,
            completion_status: completionStatus,
            bottleneck_text: bottleneckText,
            review_status: data.review_status,
            review_mode: data.review_mode || '',
            review_family: data.review_family || '',
            review_error_tags: data.review?.error_tags || [],
            review_error_layer: data.review?.error_layer || 'insufficient',
            review_confidence: data.review?.error_layer_confidence || 'low',
            review_core_design_subtags: data.review?.core_design_subtags || [],
            review_diagnosis: data.review?.diagnosis || '',
            review_next_action: data.review?.next_action || '',
            review_suggested_topic: data.review?.suggested_topic || '',
            review_main_block: data.review?.main_block || '',
            review_key_bridge: data.review?.key_bridge || '',
            review_next_step: data.review?.next_step || '',
            review_transfer_signal: data.review?.transfer_signal || '',
            review_id: data.review?.review_id || null,
            review_learning_status: 'not_started',
            quiz_status: 'not_started',
            error_types: errorTypes,
            problem_tags: importedProblemMeta.problemTags || [],
            chat_context_summary: chatContextSummary,
            created_at: new Date().toISOString(),
            poll_timed_out: false,
            review_stream_phase: data.review_status === 'pending' ? 'received' : '',
            review_stream_message: data.review_status === 'pending' ? '已收到打卡' : '',
            review_stream_elapsed_seconds: 0,
        };
        activeCheckinId = Number(data.checkin_id);
        renderActiveCheckinWorkspace(draftItem);
        document.querySelector('.workspace-stage')?.scrollIntoView({ behavior: 'smooth', block: 'start' });

        if (data.review_status === 'pending') {
            resultEl.classList.remove('hidden');
            resultEl.style.color = '';
            resultEl.innerHTML = `
                <div style="color: green; margin-bottom: 10px;">${escapeHtml(data.message)} (ID: ${escapeHtml(data.checkin_id)})</div>
                <div style="margin-top: 8px; color: #666;">复盘正在生成中，右侧工作区会自动刷新。</div>
            `;
        } else {
            resultEl.classList.remove('hidden');
            resultEl.style.color = '';
            resultEl.innerHTML = `
                <div style="color: green; margin-bottom: 10px;">${escapeHtml(data.message)} (ID: ${escapeHtml(data.checkin_id)})</div>
                <div>复盘已生成，右侧可以直接看报告并继续做理解检查。</div>
            `;
        }

        const urlEl = document.getElementById('checkin-url');
        if (urlEl) urlEl.value = '';
        document.getElementById('checkin-title').value = '';
        document.getElementById('checkin-bottleneck').value = '';
        document.getElementById('checkin-reflection').value = '';
        const ctxEl = document.getElementById('checkin-problem-context');
        if (ctxEl) ctxEl.value = '';
        const srEl = document.getElementById('checkin-submission-result');
        if (srEl) srEl.value = 'not_submitted';
        const codeEl = document.getElementById('checkin-student-code');
        if (codeEl) codeEl.value = '';
        resetImportedProblemMeta();
        updateProblemTagsPreview([]);
        syncCheckinSourceInputs();
        document.querySelectorAll('input[name="error_type"]').forEach((cb) => { cb.checked = false; });
        document.getElementById('bottleneck-count').textContent = '0 字';
        document.getElementById('bottleneck-count').style.color = '#333';
        document.getElementById('bottleneck-hint').textContent = '至少15字，越具体越好';
        document.getElementById('bottleneck-hint').style.color = '#666';
        const ccEl = document.getElementById('context-count');
        if (ccEl) { ccEl.textContent = '0 字'; ccEl.style.color = '#333'; }
        syncCheckinSourceInputs();

        loadMyCheckins(activeCheckinId);
        if (data.review_status === 'pending') {
            subscribeCheckinReviewStream(data.checkin_id, resultEl);
        }
    } catch (err) {
        resultEl.classList.remove('hidden');
        resultEl.textContent = '错误: ' + err.message;
        resultEl.style.color = 'red';
    } finally {
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
    }
}

function renderCheckinCard(item, isTeacher = false) {
    const studentLabel = isTeacher ? `<strong>学生：</strong>${escapeHtml(item.student_id || '')}` : '';
    const studentTags = renderPillRow(item.error_types, 'tag-pill student-tag');
    const aiTags = renderPillRow(item.review_error_tags, 'tag-pill ai-tag');
    const aiSubtags = renderPillRow(item.review_core_design_subtags, 'tag-pill subtle-tag');
    const timelineTone = reviewTimelineTone(item);
    const stateText = reviewLearningStateText(item, isTeacher);

    let reviewBlock = `
        <div class="archive-panel archive-panel-ai">
            <div class="archive-label">${isTeacher ? 'AI 诊断' : 'AI 帮我指出'}</div>
            <div class="archive-body">
                <div class="archive-inline-meta">
                    <span class="status-pill review-pill tone-${timelineTone}">${escapeHtml(reviewStatusText(item.review_status))}</span>
                    ${item.review_status === 'completed' ? `<span class="status-pill subtle-pill">${escapeHtml(errorLayerText(item.review_error_layer))}</span>` : ''}
                </div>
    `;
    if (item.review_status === 'completed') {
        if (isTeacher) {
            const bridgeBadge = bridgePathTeacherBadge(item.review_bridge_path);
            reviewBlock += `
                <p class="archive-line"><strong>判断把握：</strong>${escapeHtml(confidenceText(item.review_confidence))}</p>
                <div class="archive-chip-row">${aiTags}</div>
                ${item.review_core_design_subtags?.length ? `<div class="archive-chip-row">${aiSubtags}</div>` : ''}
                <div class="archive-line">${renderRichTextInline(item.review_diagnosis || '')}</div>
                <div class="archive-line"><strong>下一步行动：</strong>${renderRichTextInline(item.review_next_action || '')}</div>
                ${item.teacher_repeat_bridge_hint ? `<div class="archive-chip-row"><span class="tag-pill teacher-repeat-chip">近期重复出现</span></div><p class="archive-note teacher-repeat-note"><strong>重复提示：</strong>${escapeHtml(item.teacher_repeat_bridge_hint)}</p>` : ''}
                ${item.review_understanding_self_check ? `<p class="archive-line"><strong>学生自评：</strong>${escapeHtml(selfCheckLabel(item.review_understanding_self_check))}</p>` : ''}
                ${item.review_bridge_path ? `<p class="archive-line"><strong>过桥路径：</strong>${escapeHtml(bridgePathDisplayText(item.review_bridge_path))}</p>` : ''}
                ${bridgeBadge ? `<div class="archive-chip-row"><span class="tag-pill ${escapeHtml(bridgeBadge.className)}">${escapeHtml(bridgeBadge.label)}</span></div>` : ''}
                ${item.review_bridge_path ? `<p class="archive-note"><strong>老师解读：</strong>${escapeHtml(bridgePathTeacherNote(item.review_bridge_path))}</p>` : ''}
                ${renderReviewQualityFlags(item.review_quality_flags)}
                <div class="archive-note"><strong>推荐专题：</strong>${renderRichTextInline(item.review_suggested_topic || '')}</div>
            `;
        } else {
            const reviewFamily = reviewFamilyUi.resolveReviewFamily(item);
            const orderedSections = reviewFamilyUi
                .orderedReviewSections({
                    main_block: item.review_main_block || '',
                    key_bridge: item.review_key_bridge || '',
                    next_step: item.review_next_step || '',
                    transfer_signal: item.review_transfer_signal || '',
                }, reviewFamily)
                .filter((section) => String(section?.value || '').trim());
            reviewBlock += `
                ${orderedSections.map((section) => `
                    <div class="${section.field === 'transfer_signal' ? 'archive-note' : 'archive-line'}"><strong>${escapeHtml(section.label)}：</strong>${renderRichTextInline(section.value || '')}</div>
                `).join('')}
                <details class="archive-detail">
                    <summary>查看完整诊断</summary>
                    <div class="archive-detail-body">
                        <div class="archive-chip-row">${aiTags}</div>
                        <div class="archive-line"><strong>推荐专题：</strong>${renderRichTextInline(item.review_suggested_topic || '')}</div>
                        <p class="archive-line"><strong>AI 归类：</strong>${escapeHtml(errorLayerText(item.review_error_layer))}</p>
                    </div>
                </details>
            `;
        }
    } else if (item.review_status === 'pending') {
        reviewBlock += renderPendingReviewNotice(item);
    } else if (item.review_status === 'failed') {
        reviewBlock += renderFailedReviewNotice(item);
    } else if (item.poll_timed_out) {
        reviewBlock += renderReviewTimeoutNotice(item);
    }
    reviewBlock += `
            </div>
        </div>
    `;

    const learningPanel = !isTeacher ? `
        <div class="archive-panel archive-panel-learning full-width">
            <div class="archive-label">理解检查进度</div>
            <div class="archive-progress-head">
                <span class="status-pill learning-pill tone-${timelineTone}">${escapeHtml(stateText)}</span>
                ${item.quiz_status === 'pending' ? '<span class="micro-badge">小测进行中</span>' : ''}
            </div>
            ${renderLearningSection(item)}
        </div>
    ` : '';

    const bottleneckPanel = `
        <div class="archive-panel archive-panel-bottleneck">
            <div class="archive-label">${isTeacher ? '学生原始记录' : '我当时卡住的地方'}</div>
            ${studentLabel ? `<div class="archive-note">${studentLabel}</div>` : ''}
            <div class="archive-chip-row">${studentTags}</div>
            <p class="archive-line">${escapeHtml(item.bottleneck_text)}</p>
        </div>
    `;

    return `
        <div class="teacher-card checkin-card timeline-card tone-${timelineTone}" data-review-id="${escapeHtml(item.review_id || '')}" data-checkin-id="${escapeHtml(item.id || '')}">
            <div class="timeline-rail">
                <span class="timeline-node"></span>
            </div>
            <div class="checkin-card-shell">
                <div class="checkin-card-top">
                    <div class="checkin-title-block">
                        <div class="checkin-title-row">
                            <span class="checkin-title">${escapeHtml(item.problem_title)}</span>
                            <span class="status-pill source-pill">${escapeHtml(ojSourceText(item.oj_source))}</span>
                            <span class="status-pill completion-pill">${escapeHtml(completionStatusText(item.completion_status))}</span>
                        </div>
                        <div class="checkin-subline">
                            <span>打卡时间：${escapeHtml(formatDate(item.created_at))}</span>
                            ${item.problem_url ? `<span class="checkin-link-preview">${escapeHtml(item.problem_url)}</span>` : ''}
                        </div>
                    </div>
                    <div class="checkin-state-badge">
                        <span class="status-pill state-pill tone-${timelineTone}">${escapeHtml(stateText)}</span>
                    </div>
                </div>

                <div class="archive-grid">
                    ${bottleneckPanel}
                    ${reviewBlock}
                    ${learningPanel}
                </div>
            </div>
        </div>
    `;
}

async function loadMyCheckins(preferredCheckinId = null) {
    const listEl = document.getElementById('checkin-history-list');
    if (listEl) {
        listEl.innerHTML = '<p>加载中...</p>';
    }

    try {
        const res = await apiFetch(`${API_BASE}/api/checkins/me?limit=50`);
        const data = await res.json();
        myCheckinsCache = data.checkins || [];
        if (!myCheckinsCache.length) {
            activeCheckinId = null;
            renderCheckinEntryStage();
            if (listEl) {
                listEl.innerHTML = '<p>还没有打卡记录</p>';
            }
            return;
        }

        if (preferredCheckinId) {
            activeCheckinId = Number(preferredCheckinId);
        } else if (!activeCheckinId || !myCheckinsCache.some((item) => Number(item.id) === Number(activeCheckinId))) {
            activeCheckinId = Number(myCheckinsCache[0].id);
        }

        renderCheckinHistoryList();
        const activeItem = myCheckinsCache.find((item) => Number(item.id) === Number(activeCheckinId)) || myCheckinsCache[0];
        renderActiveCheckinWorkspace(activeItem);
    } catch (err) {
        if (listEl) {
            listEl.innerHTML = `<p style="color:red">加载失败: ${escapeHtml(err.message)}</p>`;
        }
    }
}

async function startReviewQuiz(reviewId) {
    const container = document.getElementById(`review-quiz-${reviewId}`);
    if (container) {
        container.innerHTML = `
            <div class="learning-stage-card learning-stage-entry">
                <div class="learning-stage-header">
                    <div class="learning-stage-kicker">理解检查</div>
                    <div class="learning-stage-question">正在生成这一小步的小测...</div>
                    <div class="learning-stage-subtitle">我们先把这一步收进同一条路径里，很快就好。</div>
                </div>
            </div>
        `;
    }

    try {
        const res = await apiFetch(`${API_BASE}/api/reviews/${reviewId}/quiz/generate`, {
            method: 'POST',
            body: JSON.stringify({}),
        });
        const data = await res.json();
        if (container) {
            container.innerHTML = renderQuizCard(data.quiz, reviewId);
        }
        loadMyCheckins();
    } catch (err) {
        if (container && err.message === '请先完成这一步的理解确认') {
            const checkinId = itemCheckinIdFromReview(reviewId);
            const checkinItem = checkinId ? await fetchMyCheckinById(checkinId) : null;
            const reviewFamily = reviewFamilyUi.resolveReviewFamily(checkinItem || {});
            container.innerHTML = `
                ${renderQuizFeedbackBlock({
                    title: checkinItem?.quiz_latest_feedback || '答对了，这一步你跨过去了。',
                    bridgeFeedback: checkinItem?.quiz_bridge_feedback,
                    explanation: checkinItem?.quiz_explanation,
                    tone: 'success',
                })}
                ${renderSelfCheckCard(reviewId, reviewFamily)}
            `;
            loadMyCheckins();
            return;
        }
        if (container) {
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback final">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">生成失败</div>
                        <div class="learning-stage-question">这一小步的小测没生成成功</div>
                    </div>
                    <div class="learning-path-feedback-explanation" style="color:#c0392b">${escapeHtml(err.message)}</div>
                </div>
            `;
        }
    }
}

async function submitQuizAnswer(quizId, reviewId) {
    const textInput = document.getElementById(`quiz-answer-${reviewId}`);
    let answerText = textInput ? textInput.value.trim() : '';
    if (!answerText) {
        const checked = document.querySelector(`input[name="quiz-option-${reviewId}"]:checked`);
        answerText = checked ? checked.value : '';
    }
    if (!answerText) {
        alert('请先选择或填写答案');
        return;
    }

    const container = document.getElementById(`review-quiz-${reviewId}`);
    if (container) {
        container.innerHTML = `
            <div class="learning-stage-card learning-stage-entry">
                <div class="learning-stage-header">
                    <div class="learning-stage-kicker">理解检查</div>
                    <div class="learning-stage-question">正在检查你这一小步的答案...</div>
                    <div class="learning-stage-subtitle">我们先看这一层是不是已经抓稳了。</div>
                </div>
            </div>
        `;
    }

    try {
        const res = await apiFetch(`${API_BASE}/api/quizzes/${quizId}/answer`, {
            method: 'POST',
            body: JSON.stringify({ answer_text: answerText }),
        });
        const data = await res.json();
        const currentCheckinItem = await fetchMyCheckinById(itemCheckinIdFromReview(reviewId));
        const reviewFamily = reviewFamilyUi.resolveReviewFamily(currentCheckinItem || {});

        if (data.next_state === 'self_check_required') {
            container.innerHTML = `
                ${renderQuizFeedbackBlock({
                    title: data.feedback_text,
                    bridgeFeedback: data.bridge_feedback,
                    explanation: data.explanation || '',
                    tone: 'success',
                })}
                ${renderSelfCheckCard(reviewId, reviewFamily)}
            `;
            loadMyCheckins();
        } else if (data.next_state === 'resolved') {
            container.innerHTML = renderQuizFeedbackBlock({
                title: data.feedback_text,
                bridgeFeedback: data.bridge_feedback,
                explanation: data.explanation || '',
                tone: 'success',
            });
            loadMyCheckins();
        } else if (data.next_state === 'followup_quiz') {
            container.innerHTML = `
                ${renderQuizFeedbackBlock({
                    title: data.feedback_text,
                    // deliberate: don't reveal the full correct explanation
                    // before the student gets the smaller follow-up attempt
                    explanation: '',
                    tone: 'warn',
                })}
                ${renderQuizCard(data.quiz, reviewId)}
            `;
        } else if (data.next_state === 'remedy_available') {
            const checkinItem = await fetchMyCheckinById(itemCheckinIdFromReview(reviewId));
            const errorLayer = checkinItem?.review_error_layer || 'insufficient';
            const remedyTransition = resolveRemedyTransition({
                understandingSelfCheck: checkinItem?.review_understanding_self_check,
                quizRole: checkinItem?.quiz_role,
                feedbackText: data.feedback_text || checkinItem?.quiz_latest_feedback,
                explanation: data.explanation || checkinItem?.quiz_explanation,
            });
            container.innerHTML = `
                ${renderRemedyTransitionCard(remedyTransition)}
                ${renderRemedyButtons(reviewId, errorLayer, {
                    dynamicLabel: data.dynamic_button_label,
                })}
            `;
            loadMyCheckins();
        } else {
            container.innerHTML = renderQuizFeedbackBlock({
                title: data.feedback_text,
                bridgeFeedback: data.bridge_feedback,
                explanation: data.explanation || '',
                tone: 'final',
            });
            loadMyCheckins();
        }
    } catch (err) {
        if (container) {
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback final">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">提交失败</div>
                        <div class="learning-stage-question">答案还没成功送出去</div>
                    </div>
                    <div class="learning-path-feedback-explanation" style="color:#c0392b">${escapeHtml(err.message)}</div>
                </div>
            `;
        }
    }
}

async function submitSelfCheck(reviewId, status) {
    const container = document.getElementById(`review-quiz-${reviewId}`);
    if (container) {
        container.innerHTML = `
            <div class="learning-stage-card learning-stage-entry">
                <div class="learning-stage-header">
                    <div class="learning-stage-kicker">自我确认</div>
                    <div class="learning-stage-question">正在记录你刚才的自我确认...</div>
                    <div class="learning-stage-subtitle">这会帮我们接上后面的下一步。</div>
                </div>
            </div>
        `;
    }
    const checkinId = itemCheckinIdFromReview(reviewId);

    try {
        const res = await apiFetch(`${API_BASE}/api/reviews/${reviewId}/self-check`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        });
        const data = await res.json();

        if (data.next_state === 'resolved') {
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback success">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">已确认</div>
                        <div class="learning-stage-question">${escapeHtml(data.feedback_text || '答对了，这一步你跨过去了。')}</div>
                    </div>
                </div>
            `;
        } else if (data.next_state === 'confirm_quiz') {
            container.innerHTML = renderQuizCard(data.quiz, reviewId);
        } else if (data.next_state === 'remedy_available') {
            const checkinItem = await fetchMyCheckinById(itemCheckinIdFromReview(reviewId));
            const errorLayer = checkinItem?.review_error_layer || 'insufficient';
            const remedyTransition = resolveRemedyTransition({
                understandingSelfCheck: status,
                quizRole: checkinItem?.quiz_role,
                feedbackText: data.feedback_text || '',
                explanation: data.explanation || checkinItem?.quiz_explanation,
            });
            container.innerHTML = `
                ${renderRemedyTransitionCard(remedyTransition)}
                ${renderRemedyButtons(reviewId, errorLayer, {
                    dynamicLabel: data.dynamic_button_label,
                })}
            `;
        }
        const checkinItem = checkinId ? await fetchMyCheckinById(checkinId) : null;
        if (checkinItem) {
            const reviewFamily = reviewFamilyUi.resolveReviewFamily(checkinItem);
            await postReviewEvent(
                checkinItem,
                'review_feedback_submitted',
                reviewFamilyUi.feedbackEventFields(reviewFamily, status),
            );
        }
        loadMyCheckins();
    } catch (err) {
        if (container) {
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback final">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">提交失败</div>
                        <div class="learning-stage-question">自我确认还没有记录上</div>
                    </div>
                    <div class="learning-path-feedback-explanation" style="color:#c0392b">${escapeHtml(err.message)}</div>
                </div>
            `;
        }
    }
}

function itemCheckinIdFromReview(reviewId) {
    const item = myCheckinsCache.find((candidate) => Number(candidate.review_id) === Number(reviewId));
    return item ? Number(item.id) : null;
}

async function triggerRemedy(reviewId, actionType) {
    const container = document.getElementById(`review-quiz-${reviewId}`);
    if (container) {
        container.innerHTML = `
            <div class="learning-stage-card learning-stage-entry">
                <div class="learning-stage-header">
                    <div class="learning-stage-kicker">继续带一遍</div>
                    <div class="learning-stage-question">正在换一种方式帮你拆这一步...</div>
                    <div class="learning-stage-subtitle">我们先把这一小步换个讲法，再往下接。</div>
                </div>
            </div>
        `;
    }

    try {
        const res = await apiFetch(`${API_BASE}/api/reviews/${reviewId}/remedy`, {
            method: 'POST',
            body: JSON.stringify({ action_type: actionType }),
        });
        const data = await res.json();
        if (data.mode === 'quiz') {
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback warn">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">再缩小一点</div>
                        <div class="learning-stage-question">我们把这一步再缩小一点，试一题更简单的小题。</div>
                    </div>
                </div>
                ${renderQuizCard(data.quiz, reviewId)}
            `;
            loadMyCheckins();
        } else if (data.mode === 'final') {
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback final">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">补救结束</div>
                        <div class="learning-stage-question">${escapeHtml(data.feedback_text)}</div>
                    </div>
                </div>
            `;
            loadMyCheckins();
        } else {
            const checkinItem = await fetchMyCheckinById(itemCheckinIdFromReview(reviewId));
            const errorLayer = checkinItem?.review_error_layer || 'insufficient';
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback info">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">只讲这一步</div>
                        <div class="learning-stage-question">我们先把这一小步讲顺</div>
                    </div>
                    <div class="learning-path-feedback-text">${escapeHtml(data.remedy_text || '')}</div>
                    <div class="learning-path-feedback-explanation"><strong>你现在先做：</strong>${escapeHtml(data.micro_action || '')}</div>
                    ${renderRemedyButtons(reviewId, errorLayer, {
                        includeResolve: true,
                    })}
                </div>
            `;
        }
    } catch (err) {
        if (container) {
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback final">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">补救失败</div>
                        <div class="learning-stage-question">这一步的补救暂时没接上</div>
                    </div>
                    <div class="learning-path-feedback-explanation" style="color:#c0392b">${escapeHtml(err.message)}</div>
                </div>
            `;
        }
    }
}

async function resolveRemedy(reviewId, status) {
    const container = document.getElementById(`review-quiz-${reviewId}`);
    try {
        await apiFetch(`${API_BASE}/api/reviews/${reviewId}/remedy/resolve`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        });
        if (container) {
            container.innerHTML = status === 'resolved'
                ? `
                    <div class="learning-stage-card learning-path-feedback success">
                        <div class="learning-stage-header">
                            <div class="learning-stage-kicker">已收束</div>
                            <div class="learning-stage-question">好，这一步我们先走到这里。</div>
                        </div>
                    </div>
                `
                : `
                    <div class="learning-stage-card learning-path-feedback info">
                        <div class="learning-stage-header">
                            <div class="learning-stage-kicker">继续停留</div>
                            <div class="learning-stage-question">我们继续留在这一步，等你准备好了再往下走。</div>
                        </div>
                    </div>
                `;
        }
        loadMyCheckins();
    } catch (err) {
        if (container) {
            container.innerHTML = `
                <div class="learning-stage-card learning-path-feedback final">
                    <div class="learning-stage-header">
                        <div class="learning-stage-kicker">提交失败</div>
                        <div class="learning-stage-question">这一步暂时没法收束</div>
                    </div>
                    <div class="learning-path-feedback-explanation" style="color:#c0392b">${escapeHtml(err.message)}</div>
                </div>
            `;
        }
    }
}

window.startReviewQuiz = startReviewQuiz;
window.submitQuizAnswer = submitQuizAnswer;
window.submitSelfCheck = submitSelfCheck;
window.triggerRemedy = triggerRemedy;
window.resolveRemedy = resolveRemedy;
window.selectCheckin = selectCheckin;

// ============ 教师功能 ============

async function teacherCheckQuota() {
    const queryStudentId = document.getElementById('query-student-id').value.trim();
    const queryProblemId = document.getElementById('query-problem-id').value.trim() || 'P1001';
    const resultEl = document.getElementById('teacher-quota-result');

    if (!queryStudentId) {
        resultEl.textContent = '请输入学生 ID';
        return;
    }

    try {
        const res = await apiFetch(`${API_BASE}/quota/${queryStudentId}/${queryProblemId}`);
        const data = await res.json();
        resultEl.textContent = `学生: ${data.student_id} | 题目: ${data.problem_id} | 已用: ${data.count}/${data.max} | 剩余: ${data.remaining}`;
    } catch (err) {
        resultEl.textContent = '查询失败: ' + err.message;
    }
}

async function teacherResetQuota() {
    const queryStudentId = document.getElementById('reset-student-id').value.trim();
    const queryProblemId = document.getElementById('reset-problem-id').value.trim() || 'P1001';
    const teacherSecret = document.getElementById('teacher-secret').value.trim();
    const resultEl = document.getElementById('reset-result');

    if (!queryStudentId) {
        resultEl.textContent = '请输入学生 ID';
        return;
    }
    if (!teacherSecret) {
        resultEl.textContent = '请输入教师密钥';
        return;
    }
    if (!confirm(`确定要重置 ${queryStudentId} 的 ${queryProblemId} 配额吗？`)) return;

    try {
        const res = await apiFetch(`${API_BASE}/quota/reset`, {
            method: 'POST',
            body: JSON.stringify({
                student_id: queryStudentId,
                problem_id: queryProblemId,
                teacher_secret: teacherSecret,
            }),
        });
        const data = await res.json();
        resultEl.innerHTML = `<span style="color:green">已重置！${escapeHtml(data.student_id)} / ${escapeHtml(data.problem_id)} | 剩余: ${escapeHtml(data.remaining)}/${escapeHtml(data.max)}</span>`;
    } catch (err) {
        resultEl.innerHTML = `<span style="color:red">重置失败: ${escapeHtml(err.message)}</span>`;
    }
}

async function loadAllCheckins() {
    const listEl = document.getElementById('teacher-checkins-list');
    listEl.innerHTML = '<p>加载中...</p>';

    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/checkins?limit=100&offset=0`);
        const data = await res.json();
        if (!data.checkins?.length) {
            listEl.innerHTML = '<p>暂无打卡记录</p>';
            return;
        }
        const annotated = annotateTeacherCheckins(data.checkins);
        listEl.innerHTML = annotated.map((item) => renderCheckinCard(item, true)).join('');
    } catch (err) {
        listEl.innerHTML = `<p style="color:red">加载失败: ${escapeHtml(err.message)}</p>`;
    }
}

async function loadTeacherReviewSamples() {
    const panelEl = document.getElementById('teacher-manual-review-panel');
    if (!panelEl) return;
    panelEl.innerHTML = '<p>加载中...</p>';

    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/review-samples`);
        const data = await res.json();
        teacherReviewSamplesCache = data.samples || [];
        renderTeacherManualReviewPanel(teacherReviewSamplesCache);
    } catch (err) {
        panelEl.innerHTML = `<p style="color:red">加载失败: ${escapeHtml(err.message)}</p>`;
    }
}

async function submitTeacherManualReview(reviewId, form) {
    const cardEl = form.closest('.teacher-review-sample-card');
    const statusEl = cardEl?.querySelector('[data-role="status"]');
    const submitBtn = form.querySelector('button[type="submit"]');
    const payload = teacherManualReviewUi.buildTeacherManualReviewPayload(form);

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = '提交中...';
    }
    if (statusEl) {
        statusEl.textContent = '正在提交复核...';
    }

    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/reviews/${Number(reviewId)}/manual-review`, {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        await res.json().catch(() => ({}));
        if (statusEl) {
            statusEl.textContent = '复核已提交，正在刷新列表...';
        }
        await loadTeacherReviewSamples();
    } catch (err) {
        if (statusEl) {
            statusEl.textContent = `提交失败: ${err.message}`;
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = '提交复核';
        }
    }
}

function setupTeacherManualReviewPanel() {
    const tabEl = document.getElementById('manual-review-tab');
    if (!tabEl || tabEl.dataset.bound === '1') return;
    tabEl.dataset.bound = '1';
    tabEl.addEventListener('submit', (event) => {
        const form = event.target.closest('.teacher-manual-review-form');
        if (!form) return;
        event.preventDefault();
        const reviewId = form.dataset.reviewId;
        if (!reviewId) return;
        submitTeacherManualReview(reviewId, form);
    });
    tabEl.addEventListener('click', (event) => {
        const clearBtn = event.target.closest('[data-action="clear-manual-review-filter"]');
        if (clearBtn) {
            setTeacherManualReviewFilter({});
        }
    });
}

function openTeacherManualReviewFilter(kind, value) {
    setTeacherManualReviewFilter({ kind, value });
    showTeacherTab('manual-review-tab');
}

function renderSimpleStats(title, rows, rowRenderer) {
    if (!rows?.length) {
        return `<div class="teacher-card"><h4>${escapeHtml(title)}</h4><p>暂无数据</p></div>`;
    }
    return `
        <div class="teacher-card">
            <h4>${escapeHtml(title)}</h4>
            ${rows.map(rowRenderer).join('')}
        </div>
    `;
}

function buildReviewRequestSubmittedPayload(checkinResponse = {}, formState = {}) {
    const resolvedSessionId = checkinResponse.session_id || sessionId;
    const resolvedCheckinId = Number(checkinResponse.checkin_id || checkinResponse.id || 0);
    const resolvedReviewMode = checkinResponse.review_mode || formState.review_mode || '';
    const resolvedReviewFamily = checkinResponse.review_family || formState.review_family || '';
    return {
        checkin_id: resolvedCheckinId,
        session_id: resolvedSessionId,
        event_name: 'review_request_submitted',
        client_ts: new Date().toISOString(),
        app_version: APP_VERSION,
        user_id: currentUserId || '',
        problem_id: formState.problem_id || '',
        problem_title: formState.problem_title || '',
        review_mode: resolvedReviewMode,
        review_family: resolvedReviewFamily,
        has_code: Boolean(formState.has_code),
        problem_context_length: Number(formState.problem_context_length || 0),
        bottleneck_text_length: Number(formState.bottleneck_text_length || 0),
    };
}

async function loadErrorStats() {
    const statsEl = document.getElementById('error-stats');
    statsEl.innerHTML = '<p>加载中...</p>';

    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/stats?days=30`);
        const data = await res.json();

        const studentStatsHtml = renderSimpleStats(
            '学生自报错误统计',
            data.student_reported_stats,
            (item) => `<p><strong>${escapeHtml(item.error_type)}</strong>：${escapeHtml(item.count)} 次，平均完成度 ${escapeHtml(item.avg_completion_score)}</p>`
        );

        const reviewStatsHtml = renderSimpleStats(
            'AI 统一归类统计',
            data.review_layer_stats,
            (item) => `<p><strong>${escapeHtml(errorLayerText(item.error_layer))}</strong>：${escapeHtml(item.count)} 次，平均完成度 ${escapeHtml(item.avg_completion_score)}</p>`
        );

        const statusSummaryHtml = renderSimpleStats(
            '复盘状态统计',
            data.review_status_summary,
            (item) => `<p><strong>${escapeHtml(reviewStatusText(item.review_status))}</strong>：${escapeHtml(item.count)} 条</p>`
        );

        const manualReviewRatesHtml = renderManualReviewRatesCard(extractManualReviewRatesSource(data));
        const manualReviewByModeHtml = renderManualReviewBreakdownSection(
            MANUAL_REVIEW_BREAKDOWN_TITLES.mode,
            data.manual_review_stats_by_mode || {},
            'mode',
        );
        const manualReviewByFamilyHtml = renderManualReviewBreakdownSection(
            MANUAL_REVIEW_BREAKDOWN_TITLES.family,
            data.manual_review_stats_by_family || {},
            'family',
        );

        statsEl.innerHTML =
            studentStatsHtml
            + reviewStatsHtml
            + statusSummaryHtml
            + manualReviewRatesHtml
            + manualReviewByModeHtml
            + manualReviewByFamilyHtml;
    } catch (err) {
        statsEl.innerHTML = `<p style="color:red">加载失败: ${escapeHtml(err.message)}</p>`;
    }
}

function setupTeacherStatsInteractions() {
    const statsEl = document.getElementById('error-stats');
    if (!statsEl || statsEl.dataset.bound === '1') return;
    statsEl.dataset.bound = '1';
    statsEl.addEventListener('click', (event) => {
        const filterCard = event.target.closest('[data-action="open-manual-review-filter"]');
        if (!filterCard) return;
        openTeacherManualReviewFilter(filterCard.dataset.filterKind, filterCard.dataset.filterValue);
    });
}

async function loadUsageStats() {
    const usageEl = document.getElementById('usage-stats');
    usageEl.innerHTML = '<p>加载中...</p>';

    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/usage?days=7`);
        const data = await res.json();
        if (!data.usage?.length) {
            usageEl.innerHTML = '<p>暂无使用统计</p>';
            return;
        }
        usageEl.innerHTML = data.usage.map((item) => `
            <div class="teacher-card">
                <p><strong>日期:</strong> ${escapeHtml(item.date)}</p>
                <p><strong>有效打卡:</strong> ${escapeHtml(item.checkins)}</p>
                <p><strong>被拒打卡:</strong> ${escapeHtml(item.rejected)}</p>
                <p><strong>平均描述字数:</strong> ${escapeHtml(item.avg_chars)}</p>
            </div>
        `).join('');
    } catch (err) {
        usageEl.innerHTML = `<p style="color:red">加载失败: ${escapeHtml(err.message)}</p>`;
    }
}

async function loadStudentFlags() {
    const flagsEl = document.getElementById('student-flags');
    flagsEl.innerHTML = '<p>加载中...</p>';

    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/flags`);
        const data = await res.json();
        if (!data.flags?.length) {
            flagsEl.innerHTML = '<p>暂无需要关注的学员</p>';
            return;
        }
        flagsEl.innerHTML = data.flags.map((item) => `
            <div class="teacher-card">
                <p><strong>学生:</strong> ${escapeHtml(item.student_id)}</p>
                <p><strong>类型:</strong> ${escapeHtml(item.flag_type)}</p>
                <p><strong>说明:</strong> ${escapeHtml(item.description)}</p>
                <p><strong>严重度:</strong> ${escapeHtml(item.severity)}</p>
            </div>
        `).join('');
    } catch (err) {
        flagsEl.innerHTML = `<p style="color:red">加载失败: ${escapeHtml(err.message)}</p>`;
    }
}

async function retryPendingReviews() {
    const limit = Number(document.getElementById('retry-pending-limit').value) || 10;
    const resultEl = document.getElementById('retry-pending-result');
    resultEl.textContent = '重试中...';

    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/reviews/retry-pending`, {
            method: 'POST',
            body: JSON.stringify({ limit }),
        });
        const data = await res.json();
        resultEl.innerHTML = `<span style="color:green">${escapeHtml(data.message || '重试完成')}</span>`;
        loadAllCheckins();
        loadErrorStats();
    } catch (err) {
        resultEl.innerHTML = `<span style="color:red">重试失败: ${escapeHtml(err.message)}</span>`;
    }
}

async function loadProblemAnalysisFailures() {
    const listEl = document.getElementById('problem-analysis-failures');
    if (!listEl) return;
    listEl.innerHTML = '<p>加载中...</p>';

    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/problems/analysis-failures?limit=20`);
        const data = await res.json();
        if (!data.failures?.length) {
            listEl.innerHTML = '<p>暂无失败的题目分析</p>';
            return;
        }
        listEl.innerHTML = data.failures.map((item) => `
            <div class="teacher-card">
                <p><strong>${escapeHtml(item.luogu_pid)}</strong> ${escapeHtml(item.title || '')}</p>
                <p><strong>状态:</strong> ${escapeHtml(item.status || 'failed')} | <strong>重试次数:</strong> ${escapeHtml(item.retry_count ?? 0)}</p>
                <p><strong>最近错误:</strong> ${escapeHtml(item.last_error || '未知错误')}</p>
                <p><strong>更新时间:</strong> ${escapeHtml(item.updated_at || '-')}</p>
            </div>
        `).join('');
    } catch (err) {
        listEl.innerHTML = `<p style="color:red">加载失败: ${escapeHtml(err.message)}</p>`;
    }
}

async function retryProblemAnalysis() {
    const pidInput = document.getElementById('retry-problem-analysis-pid');
    const resultEl = document.getElementById('retry-problem-analysis-result');
    const rawPid = pidInput?.value.trim() || '';
    if (!rawPid) {
        resultEl.innerHTML = '<span style="color:red">请先输入要重试的洛谷题号</span>';
        return;
    }

    resultEl.textContent = '重试中...';
    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/problems/analysis/retry`, {
            method: 'POST',
            body: JSON.stringify({ luogu_pid: rawPid }),
        });
        const data = await res.json();
        const okColor = data.ok ? 'green' : 'red';
        const statusText = data.analysis_status
            ? `（状态：${escapeHtml(data.analysis_status.status || '-')}，重试次数：${escapeHtml(data.analysis_status.retry_count ?? 0)}）`
            : '';
        resultEl.innerHTML = `<span style="color:${okColor}">${escapeHtml(data.message || '已处理')}${statusText}</span>`;
        loadProblemAnalysisFailures();
    } catch (err) {
        resultEl.innerHTML = `<span style="color:red">重试失败: ${escapeHtml(err.message)}</span>`;
    }
}

const noiAppTestHooks = {
    buildReviewRequestSubmittedPayload,
    extractManualReviewRatesSource,
    filterTeacherReviewSamples,
    formatManualReviewRateValue,
    normalizeManualReviewRateRow,
    normalizeManualReviewRates,
    renderManualReviewFilterBanner,
    renderManualReviewBreakdownSection,
    renderManualReviewRateRow,
    renderManualReviewRatesCard,
};

if (typeof window !== 'undefined') {
    window.noiAppTestHooks = Object.assign(window.noiAppTestHooks || {}, noiAppTestHooks);
}
