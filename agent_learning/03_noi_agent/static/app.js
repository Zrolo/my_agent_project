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
    isVisualHintDiagramLike(value = '') {
        const text = String(value || '').trim();
        if (!text) return false;
        const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean);
        if (lines.length < 2) return false;
        const structuredLineCount = lines.filter((line) => /[:：=→←↔|├└┌┐┘─\-×]/.test(line)).length;
        const compactLineCount = lines.filter((line) => line.length <= 30).length;
        return structuredLineCount >= 2 || (structuredLineCount >= 1 && compactLineCount >= 2 && lines.length >= 3);
    },
    reviewFieldLabel(field, value = '') {
        if (field === 'visual_hint') {
            return this.isVisualHintDiagramLike(value) ? '看图想一想' : '先看这个对比';
        }
        const labels = {
            problem_focus: '你卡在哪',
            main_block: '你卡在哪',
            key_bridge: '先抓住什么',
            guided_walkthrough: '跟我走一遍',
            try_now: '现在你来试',
            next_step: '现在你来试',
            transfer_signal: '下次怎么认出来',
        };
        return labels[field] || field;
    },
    orderedReviewSections(review = {}, family = 'failure_diagnosis') {
        const order = ['problem_focus', 'key_bridge', 'visual_hint', 'guided_walkthrough', 'try_now', 'transfer_signal'];
        return order.map((field) => ({
            field,
            label: this.reviewFieldLabel(
                field,
                review[field]
                || (field === 'problem_focus' ? review.main_block : '')
                || (field === 'try_now' ? review.next_step : '')
                || '',
            ),
            value: review[field]
                || (field === 'problem_focus' ? review.main_block : '')
                || (field === 'try_now' ? review.next_step : '')
                || '',
        }));
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
const checkinReviewUi = window.checkinReviewUi || {
    INPUT_STAGE: 'input',
    REVIEW_STAGE: 'review',
    checkinStage(item = null) {
        return item ? 'review' : 'input';
    },
    checkinSummaryPills(item = {}) {
        const pills = [];
        if (item.problem_title) pills.push({ label: '题目', value: item.problem_title });
        if (item.completion_status_text) pills.push({ label: '状态', value: item.completion_status_text });
        if (item.submission_result_text) pills.push({ label: '提交', value: item.submission_result_text });
        if (item.oj_source_text) pills.push({ label: '来源', value: item.oj_source_text });
        return pills;
    },
    compactStudentInputSections(item = {}) {
        return [
            { label: '题面 / 题意', value: item.problem_context || '' },
            { label: '卡点描述', value: item.bottleneck_text || '' },
            { label: '反思总结', value: item.reflection || '' },
            { label: '代码', value: item.student_code || '' },
        ].filter((section) => String(section.value || '').trim());
    },
    reviewStageHeading(item = {}) {
        return item.problem_title || '这次打卡复盘';
    },
    entryStageLead() {
        return '把这次卡住的地方记下来，我们会把它整理成一页可继续往下学的复盘讲义。';
    },
    reviewStageLead(item = {}) {
        if (item.review_status === 'failed') return '这次复盘暂时没有成功生成，你可以先看错误提示，稍后再回来继续。';
        if (item.review_status !== 'completed') return '复盘讲义正在生成中，生成完成后这里会自动更新。';
        return '先读这次复盘，再继续做下面这一小步。';
    },
};
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
let activeCheckinStage = checkinReviewUi.INPUT_STAGE;
let historySearchKeyword = '';
let historySearchAlgorithm = '';
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

// Sidebar collapse state
let sidebarCollapsed = localStorage.getItem('noi_sidebar_collapsed') === 'true';

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    
    if (!sidebar || !toggleBtn) return;
    
    // Apply initial state
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
    }
    
    // Toggle on click
    toggleBtn.addEventListener('click', () => {
        sidebarCollapsed = !sidebarCollapsed;
        sidebar.classList.toggle('collapsed', sidebarCollapsed);
        localStorage.setItem('noi_sidebar_collapsed', sidebarCollapsed);
    });
}

function toggleSidebar(collapsed) {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    
    sidebarCollapsed = collapsed !== undefined ? collapsed : !sidebarCollapsed;
    sidebar.classList.toggle('collapsed', sidebarCollapsed);
    localStorage.setItem('noi_sidebar_collapsed', sidebarCollapsed);
}

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

function rememberProblemChatContext(problemRef, question, answer) {
    const normalizedRef = normalizeProblemRef(problemRef);
    if (!normalizedRef) return;
    const store = loadChatContextStore();
    store[normalizedRef] = {
        problemRef: normalizedRef,
        summary: buildChatContextSummary(question, answer),
        question: cleanChatSnippet(question, 120),
        answer: cleanChatSnippet(answer, 180),
        updatedAt: new Date().toISOString(),
    };
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
const MASTERY_STATUS_STATS_LABELS = {
    independent_success: '独立过桥',
    assisted_success: '辅助后过桥',
    not_mastered: '仍未掌握',
    not_assessed: '尚未评估',
};
const BRIDGE_PATH_STATS_LABELS = {
    main_clear: '首轮直接过桥',
    main_guessed_confirm: '确认后过桥',
    main_guessed_remedy: '首轮答对但最终补救',
    main_confused_remedy: '主动承认没懂后补救',
    followup_correct: '提示后过桥',
    followup_remedy: '补救后过桥',
    knowledge_bailout_success: '知识卡后过桥',
    knowledge_bailout_failed: '知识卡后仍未掌握',
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

function renderDistributionStatsCard(title, source = {}, labels = {}) {
    if (!source || typeof source !== 'object' || !Object.keys(source).length) {
        return `
            <div class="teacher-card">
                <h4>${escapeHtml(title || '分布统计')}</h4>
                <p>暂无分布统计数据</p>
            </div>
        `;
    }
    const rows = Object.entries(source)
        .map(([key, item]) => normalizeManualReviewRateRow({
            ...(item || {}),
            label: labels[key] || key,
            count: item?.count ?? 0,
            total: item?.total ?? null,
            rate: item?.rate ?? null,
        }, key))
        .filter(Boolean);
    if (!rows.length) {
        return `
            <div class="teacher-card">
                <h4>${escapeHtml(title || '分布统计')}</h4>
                <p>暂无分布统计数据</p>
            </div>
        `;
    }
    return `
        <div class="teacher-card">
            <h4>${escapeHtml(title || '分布统计')}</h4>
            <div class="manual-review-rates-grid">
                ${rows.map(renderManualReviewRateRow).join('')}
            </div>
        </div>
    `;
}

function renderMasteryStatusCard(source = {}) {
    return renderDistributionStatsCard('过桥结果分布', source, MASTERY_STATUS_STATS_LABELS);
}

function renderBridgePathStatsCard(source = {}) {
    return renderDistributionStatsCard('过桥路径分布', source, BRIDGE_PATH_STATS_LABELS);
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
    document.getElementById('main-app').classList.add('hidden');
    document.getElementById('student-section').classList.add('hidden');
    document.getElementById('teacher-section').classList.add('hidden');
    document.getElementById('student-nav').classList.add('hidden');
    document.getElementById('teacher-nav').classList.add('hidden');
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
    // Hide all tab contents
    document.querySelectorAll('#student-section .tab-content').forEach((content) => {
        content.classList.add('hidden');
        content.classList.remove('active');
    });
    
    // Show target tab
    const target = document.getElementById(targetId);
    if (target) {
        target.classList.remove('hidden');
        target.classList.add('active');
    }
    
    // Update sidebar active state
    document.querySelectorAll('#student-nav .sidebar-link').forEach((link) => {
        link.classList.toggle('active', link.dataset.tab === targetId);
    });
    if (targetId === 'checkin-tab') {
        loadCheckinStats();
        renderLinkedChatContextCard();
        if (activeCheckinStage === checkinReviewUi.REVIEW_STAGE && activeCheckinId) {
            const item = myCheckinsCache.find((candidate) => Number(candidate.id) === Number(activeCheckinId)) || null;
            renderActiveCheckinWorkspace(item);
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
    const date = new Date(item.created_at);
    const dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
    const timeStr = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    
    // Status emoji mapping
    const statusEmoji = {
        'completed': '✅',
        'pending': '⏳',
        'failed': '❌'
    };
    
    // Completion status emoji - colorful
    const completionEmoji = {
        'independent': '🟢',
        'hinted': '🔵', 
        'editorial': '🟠',
        'unfinished': '🟡'
    };
    
    // Color mapping for completion status
    const completionColor = {
        'independent': '#34C759',  // green
        'hinted': '#5856D6',       // indigo
        'editorial': '#FF9500',    // orange
        'unfinished': '#FFCC00'    // yellow
    };
    
    const reviewStatus = item.review_status || 'pending';
    const reviewEmoji = statusEmoji[reviewStatus] || '⏳';
    const completionIcon = completionEmoji[item.completion_status] || '📝';
    
    // Get status color
    const statusColor = {
        'completed': 'var(--system-green)',
        'pending': 'var(--system-orange)',
        'failed': 'var(--system-red)'
    }[reviewStatus] || 'var(--text-tertiary)';
    
    const completionBgColor = completionColor[item.completion_status] || '#8E8E93';
    
    return `
        <details class="history-item ${isActive ? 'active' : ''}" data-checkin-id="${Number(item.id)}" ${isActive ? 'open' : ''}>
            <summary class="history-item-summary">
                <div class="history-item-indicator" style="background-color: ${completionBgColor};"></div>
                <div class="history-item-main">
                    <div class="history-item-title-row">
                        <span class="history-item-title">${escapeHtml(item.problem_title || '未命名题目')}</span>
                        <span class="history-item-status" style="color: ${statusColor};">${reviewEmoji}</span>
                    </div>
                    <div class="history-item-meta">
                        <span class="badge" style="background: ${completionBgColor}20; color: ${completionBgColor};">${escapeHtml(completionStatusText(item.completion_status))}</span>
                        <span class="badge badge-gray">${escapeHtml(ojSourceText(item.oj_source))}</span>
                        <span class="badge" style="background: rgba(0,122,255,0.15); color: var(--system-blue);">${dateStr} ${timeStr}</span>
                        ${tags.length ? tags.slice(0, 2).map(t => `<span class="badge" style="background: rgba(175,82,222,0.15); color: var(--system-purple);">${escapeHtml(t)}</span>`).join('') : ''}
                    </div>
                </div>
                <svg class="history-item-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 18l6-6-6-6"/>
                </svg>
            </summary>
            <div class="history-item-content">
                <div class="history-item-section">
                    <div class="history-item-label">📝 卡点描述</div>
                    <div class="history-item-text">${escapeHtml(item.bottleneck_text || '无描述')}</div>
                </div>
                
                ${item.review_status === 'completed' ? `
                    <div class="history-item-section">
                        <div class="history-item-label">🤖 AI 复盘</div>
                        ${item.review_problem_focus || item.review_main_block ? `<div class="history-item-text"><strong>你卡在哪：</strong>${escapeHtml(item.review_problem_focus || item.review_main_block)}</div>` : ''}
                        ${item.review_key_bridge ? `<div class="history-item-text"><strong>先抓住什么：</strong>${escapeHtml(item.review_key_bridge)}</div>` : ''}
                        ${item.review_visual_hint ? `<div class="history-item-text"><strong>${escapeHtml(reviewFamilyUi.reviewFieldLabel('visual_hint', item.review_visual_hint))}：</strong><pre class="review-visual-hint history-visual-hint">${escapeHtml(item.review_visual_hint)}</pre></div>` : ''}
                        ${item.review_guided_walkthrough ? `<div class="history-item-text"><strong>跟我走一遍：</strong>${renderRichTextBlock(item.review_guided_walkthrough, 'review-inline-rich-block')}</div>` : ''}
                        ${item.review_try_now || item.review_next_step ? `<div class="history-item-text"><strong>现在你来试：</strong>${escapeHtml(item.review_try_now || item.review_next_step)}</div>` : ''}
                    </div>
                ` : item.review_status === 'pending' ? `
                    <div class="history-item-section">
                        <div class="alert alert-info" style="margin: 0;">
                            <span>⏳ AI 复盘生成中，请稍候...</span>
                        </div>
                    </div>
                ` : `
                    <div class="history-item-section">
                        <div class="alert alert-error" style="margin: 0;">
                            <span>❌ 复盘生成失败，请重新提交</span>
                        </div>
                    </div>
                `}
                
                <div class="history-item-actions">
                    <button class="sm" onclick="selectCheckin(${Number(item.id)}); showStudentTab('checkin-tab');">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                            <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                        </svg>
                        查看详情
                    </button>
                    ${item.review_status === 'completed' ? `
                        <button class="secondary sm" onclick="selectCheckin(${Number(item.id)}); startReviewQuiz(${Number(item.review_id)});">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 11l3 3L22 4"/>
                                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
                            </svg>
                            理解检查
                        </button>
                    ` : ''}
                </div>
            </div>
        </details>
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
    const empty = document.getElementById('review-stage-empty');
    const content = document.getElementById('review-stage-content');
    const status = document.getElementById('workspace-stage-status');
    const context = document.getElementById('active-review-chat-context');
    const titleEl = document.getElementById('active-review-title');
    const subtitleEl = document.getElementById('active-review-subtitle');
    const metaEl = document.getElementById('active-review-meta');
    if (empty) empty.classList.remove('hidden');
    if (content) content.classList.add('hidden');
    if (status) status.innerHTML = '';
    if (titleEl) titleEl.textContent = '这次打卡复盘';
    if (subtitleEl) subtitleEl.textContent = checkinReviewUi.entryStageLead();
    if (metaEl) metaEl.innerHTML = '';
    renderActiveCheckinSummary(null);
    renderActiveCheckinInputs(null);
    setCheckinStage(checkinReviewUi.INPUT_STAGE);
    if (context) {
        context.classList.add('hidden');
        context.innerHTML = '';
    }
}

function renderCheckinEntryStage() {
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

    setCheckinStage(checkinReviewUi.INPUT_STAGE);
    if (empty) empty.classList.add('hidden');
    if (content) content.classList.add('hidden');
    if (status) status.innerHTML = '';
    if (titleEl) titleEl.textContent = '这次打卡复盘';
    if (subtitleEl) subtitleEl.textContent = checkinReviewUi.entryStageLead();
    if (metaEl) metaEl.innerHTML = '';
    if (quizEl) quizEl.innerHTML = '';
    if (reportEl) reportEl.innerHTML = '';
    if (relatedEl) relatedEl.innerHTML = '';
    renderActiveCheckinSummary(null);
    renderActiveCheckinInputs(null);
    if (context) {
        context.classList.add('hidden');
        context.innerHTML = '';
    }
}

function renderActiveCheckinWorkspace(item) {
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
        renderCheckinEntryStage();
        return;
    }

    setCheckinStage(checkinReviewUi.REVIEW_STAGE);
    if (empty) empty.classList.add('hidden');
    if (content) content.classList.remove('hidden');
    if (titleEl) titleEl.textContent = checkinReviewUi.reviewStageHeading(item);
    if (subtitleEl) {
        subtitleEl.textContent = item.review_status === 'completed'
            ? reviewFamilyUi.reviewWorkspaceSubtitle(item)
            : checkinReviewUi.reviewStageLead(item);
    }
    if (metaEl) {
        metaEl.innerHTML = `
            <span class="status-pill">${escapeHtml(ojSourceText(item.oj_source))}</span>
            <span class="status-pill">${escapeHtml(completionStatusText(item.completion_status))}</span>
            <span class="status-pill tone-${reviewTimelineTone(item)}">${escapeHtml(reviewLearningStateText(item, false))}</span>
        `;
    }
    renderActiveCheckinSummary(item);
    renderActiveCheckinInputs(item);
    if (statusEl) {
        statusEl.innerHTML = `
            <span class="status-pill">${escapeHtml(formatDate(item.created_at))}</span>
            ${item.problem_url ? `<a class="workspace-link status-pill" href="${escapeHtml(item.problem_url)}" target="_blank" rel="noopener noreferrer">打开原题</a>` : ''}
        `;
    }
    if (quizEl) {
        quizEl.innerHTML = renderLearningSection(item) || '<div class="quiz-card"><div class="quiz-title">复盘生成后，这里会出现小测。</div></div>';
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
    activeCheckinStage = checkinReviewUi.REVIEW_STAGE;
    const item = myCheckinsCache.find((candidate) => Number(candidate.id) === activeCheckinId) || null;
    renderCheckinHistoryList();
    showStudentTab('checkin-tab');
    showCheckinReviewDetail(item);
    void fetchMyCheckinById(activeCheckinId)
        .then((detail) => {
            const merged = mergeCheckinDetailIntoCache(detail);
            renderCheckinHistoryList();
            if (shouldRenderReviewUpdate(activeCheckinId)) {
                renderReviewDetailContent(merged);
            }
            if (merged.review_status === 'pending') {
                startCheckinReviewStream(activeCheckinId);
            } else {
                stopCheckinPoll(activeCheckinId);
                stopCheckinReviewStream(activeCheckinId);
            }
        })
        .catch((err) => {
            console.warn('failed to refresh selected checkin detail:', err);
            if (item?.review_status === 'pending') {
                startCheckinReviewStream(activeCheckinId);
            }
        });
}

function showCheckinReviewDetail(item) {
    const headerActions = document.getElementById('checkin-header-actions');
    const pageTitle = document.getElementById('checkin-page-title');
    const pageSubtitle = document.getElementById('checkin-page-subtitle');

    if (headerActions) headerActions.style.display = 'flex';
    if (pageTitle) pageTitle.textContent = '复盘详情';
    if (pageSubtitle) pageSubtitle.textContent = item?.problem_title || '查看打卡记录和 AI 复盘';

    renderActiveCheckinWorkspace(item);
}

function showCheckinForm() {
    const formContainer = document.getElementById('checkin-form-container');
    const headerActions = document.getElementById('checkin-header-actions');
    const pageTitle = document.getElementById('checkin-page-title');
    const pageSubtitle = document.getElementById('checkin-page-subtitle');

    if (!formContainer) return;

    if (headerActions) headerActions.style.display = 'none';
    if (pageTitle) pageTitle.textContent = '打卡复盘';
    if (pageSubtitle) pageSubtitle.textContent = checkinReviewUi.entryStageLead();
    
    // Reset active checkin
    activeCheckinId = null;
    activeCheckinStage = checkinReviewUi.INPUT_STAGE;
    renderCheckinHistoryList();
}

function renderReviewDetailContent(item) {
    const workspaceEl = document.getElementById('review-stage-content');
    if (workspaceEl) {
        renderActiveCheckinWorkspace(item);
        return;
    }

    const loadingEl = document.getElementById('review-detail-loading');
    const bodyEl = document.getElementById('review-detail-body');
    const titleEl = document.getElementById('active-review-title');
    const metaEl = document.getElementById('active-review-meta');
    
    // Color mapping for completion status
    const completionColor = {
        'independent': '#34C759',  // green
        'hinted': '#5856D6',       // indigo
        'editorial': '#FF9500',    // orange
        'unfinished': '#FFCC00'    // yellow
    };
    
    if (!item) {
        if (loadingEl) loadingEl.classList.remove('hidden');
        if (bodyEl) bodyEl.classList.add('hidden');
        return;
    }
    
    if (loadingEl) loadingEl.classList.add('hidden');
    if (bodyEl) bodyEl.classList.remove('hidden');
    
    // Title
    if (titleEl) titleEl.textContent = item.problem_title || '复盘详情';
    
    // Meta badges
    if (metaEl) {
        const date = new Date(item.created_at);
        const dateStr = `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        metaEl.innerHTML = `
            <span class="badge" style="background: ${completionColor[item.completion_status] || '#8E8E93'}20; color: ${completionColor[item.completion_status] || '#8E8E93'};">${escapeHtml(completionStatusText(item.completion_status))}</span>
            <span class="badge badge-gray">${escapeHtml(ojSourceText(item.oj_source))}</span>
            <span class="badge" style="background: rgba(0,122,255,0.15); color: var(--system-blue);">${dateStr}</span>
        `;
    }
    
    // Problem info
    const problemEl = document.getElementById('review-detail-problem');
    if (problemEl) {
        const tags = (item.problem_tags || []).slice(0, 3);
        problemEl.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                ${item.problem_url ? `<a href="${escapeHtml(item.problem_url)}" target="_blank" rel="noopener noreferrer" style="color: var(--system-blue); text-decoration: none;">🔗 ${escapeHtml(item.problem_url)}</a>` : '<span style="color: var(--text-secondary);">无链接</span>'}
            </div>
            ${tags.length ? `<div style="margin-top: 8px; display: flex; gap: 6px; flex-wrap: wrap;">${tags.map(t => `<span class="tag-pill subtle-tag">${escapeHtml(t)}</span>`).join('')}</div>` : ''}
        `;
    }
    
    // Bottleneck
    const bottleneckEl = document.getElementById('review-detail-bottleneck');
    if (bottleneckEl) {
        bottleneckEl.textContent = item.bottleneck_text || '无描述';
    }
    
    // Error types
    const errorTypesEl = document.getElementById('review-detail-error-types');
    if (errorTypesEl) {
        const errorTypes = item.error_types || [];
        if (errorTypes.length) {
            errorTypesEl.innerHTML = errorTypes.map(t => `<span class="badge" style="background: rgba(255,59,48,0.15); color: var(--system-red); margin-right: 6px;">${escapeHtml(t)}</span>`).join('');
        } else {
            errorTypesEl.innerHTML = '';
        }
    }
    
    // AI Review
    const aiSection = document.getElementById('review-detail-ai-section');
    const aiContent = document.getElementById('review-detail-ai-content');
    if (aiSection && aiContent) {
        if (item.review_status === 'completed' && (item.review_problem_focus || item.review_main_block)) {
            aiSection.classList.remove('hidden');
            aiContent.innerHTML = `
                ${item.review_problem_focus || item.review_main_block ? `<div style="margin-bottom: 12px;"><strong style="color: var(--text-primary);">你卡在哪：</strong><span style="color: var(--text-secondary);">${escapeHtml(item.review_problem_focus || item.review_main_block)}</span></div>` : ''}
                ${item.review_key_bridge ? `<div style="margin-bottom: 12px;"><strong style="color: var(--text-primary);">先抓住什么：</strong><span style="color: var(--text-secondary);">${escapeHtml(item.review_key_bridge)}</span></div>` : ''}
                ${item.review_visual_hint ? `<div style="margin-bottom: 12px;"><strong style="color: var(--text-primary);">${escapeHtml(reviewFamilyUi.reviewFieldLabel('visual_hint', item.review_visual_hint))}：</strong><pre class="review-visual-hint history-visual-hint">${escapeHtml(item.review_visual_hint)}</pre></div>` : ''}
                ${item.review_guided_walkthrough ? `<div style="margin-bottom: 12px;"><strong style="color: var(--text-primary);">跟我走一遍：</strong>${renderRichTextBlock(item.review_guided_walkthrough, 'review-inline-rich-block')}</div>` : ''}
                ${item.review_try_now || item.review_next_step ? `<div><strong style="color: var(--text-primary);">现在你来试：</strong><span style="color: var(--text-secondary);">${escapeHtml(item.review_try_now || item.review_next_step)}</span></div>` : ''}
            `;
        } else if (item.review_status === 'pending') {
            aiSection.classList.remove('hidden');
            aiContent.innerHTML = '<div class="alert alert-info">⏳ AI 复盘生成中，请稍候...</div>';
        } else if (item.review_status === 'failed') {
            aiSection.classList.remove('hidden');
            aiContent.innerHTML = '<div class="alert alert-error">❌ 复盘生成失败，请重新提交</div>';
        } else {
            aiSection.classList.add('hidden');
        }
    }
    
    // Code
    const codeSection = document.getElementById('review-detail-code-section');
    const codeEl = document.getElementById('review-detail-code');
    if (codeSection && codeEl) {
        if (item.student_code) {
            codeSection.classList.remove('hidden');
            codeEl.textContent = item.student_code;
        } else {
            codeSection.classList.add('hidden');
        }
    }
    
    // Reflection
    const reflectionSection = document.getElementById('review-detail-reflection-section');
    const reflectionEl = document.getElementById('review-detail-reflection');
    if (reflectionSection && reflectionEl) {
        if (item.reflection_text) {
            reflectionSection.classList.remove('hidden');
            reflectionEl.textContent = item.reflection_text;
        } else {
            reflectionSection.classList.add('hidden');
        }
    }
    
    // Quiz - render learning section based on current state
    const quizSection = document.getElementById('review-detail-quiz-section');
    const quizEl = document.getElementById('review-detail-quiz');
    if (quizSection && quizEl) {
        const reviewId = item.review_id;
        if (item.review_status === 'completed' && reviewId) {
            quizSection.classList.remove('hidden');
            quizEl.innerHTML = renderReviewDetailQuizTimeline(item);
        } else {
            quizSection.classList.add('hidden');
        }
    }
}

function filterCheckinsBySearch(checkins) {
    if (!historySearchKeyword && !historySearchAlgorithm) return checkins;
    
    const keyword = historySearchKeyword.toLowerCase().trim();
    const algorithm = historySearchAlgorithm.toLowerCase().trim();
    
    return checkins.filter(item => {
        // 关键词搜索：题目名称、题号
        let matchesKeyword = true;
        if (keyword) {
            const title = (item.problem_title || '').toLowerCase();
            const pid = (item.problem_id || '').toLowerCase();
            const url = (item.problem_url || '').toLowerCase();
            matchesKeyword = title.includes(keyword) || 
                           pid.includes(keyword) || 
                           url.includes(keyword);
        }
        
        // 算法标签搜索
        let matchesAlgorithm = true;
        if (algorithm) {
            const tags = (item.problem_tags || []).map(t => t.toLowerCase());
            const title = (item.problem_title || '').toLowerCase();
            // 检查标签或题目中是否包含算法关键词
            matchesAlgorithm = tags.some(tag => tag.includes(algorithm)) ||
                             title.includes(algorithm);
        }
        
        return matchesKeyword && matchesAlgorithm;
    });
}

function renderCheckinHistoryList() {
    const listEl = document.getElementById('checkin-history-list');
    const resultInfoEl = document.getElementById('history-search-result-info');
    if (!listEl) return;
    if (!myCheckinsCache.length) {
        listEl.innerHTML = `
            <div class="history-empty">
                <div class="history-empty-icon">📝</div>
                <div class="history-empty-text">还没有打卡记录</div>
                <div style="margin-top: 16px;">
                    <button onclick="showStudentTab('checkin-tab')">去打卡</button>
                </div>
            </div>
        `;
        if (resultInfoEl) resultInfoEl.textContent = '';
        return;
    }
    
    // 应用搜索过滤
    const filteredCheckins = filterCheckinsBySearch(myCheckinsCache);
    
    // 更新搜索结果信息
    if (resultInfoEl) {
        if (historySearchKeyword || historySearchAlgorithm) {
            const filterDesc = [];
            if (historySearchKeyword) filterDesc.push(`关键词"${historySearchKeyword}"`);
            if (historySearchAlgorithm) filterDesc.push(`算法"${historySearchAlgorithm}"`);
            resultInfoEl.innerHTML = `🔍 搜索 ${filterDesc.join(' + ')}，找到 <strong>${filteredCheckins.length}</strong> 条记录 / 共 ${myCheckinsCache.length} 条`;
        } else {
            resultInfoEl.textContent = `共 ${myCheckinsCache.length} 条打卡记录`;
        }
    }
    
    if (!filteredCheckins.length) {
        listEl.innerHTML = `
            <div class="history-empty">
                <div class="history-empty-icon">🔍</div>
                <div class="history-empty-text">没有找到匹配的记录</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 8px;">尝试调整搜索条件</div>
            </div>
        `;
        return;
    }
    
    // Group by date
    const grouped = filteredCheckins.reduce((acc, item) => {
        const date = new Date(item.created_at);
        const dateKey = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
        if (!acc[dateKey]) acc[dateKey] = [];
        acc[dateKey].push(item);
        return acc;
    }, {});
    
    // Sort dates descending
    const sortedDates = Object.keys(grouped).sort((a, b) => new Date(b) - new Date(a));
    
    let html = '';
    sortedDates.forEach(dateKey => {
        const items = grouped[dateKey];
        const date = new Date(dateKey);
        const today = new Date();
        const isToday = date.toDateString() === today.toDateString();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const isYesterday = date.toDateString() === yesterday.toDateString();
        
        let dateLabel = `${date.getMonth() + 1}月${date.getDate()}日`;
        if (isToday) dateLabel = '今天';
        if (isYesterday) dateLabel = '昨天';
        
        html += `<div class="history-group">`;
        html += `<div class="history-group-title">${dateLabel} · ${items.length} 条记录</div>`;
        html += items
            .map((item) => renderHistoryListItem(item, Number(item.id) === Number(activeCheckinId)))
            .join('');
        html += `</div>`;
    });
    
    listEl.innerHTML = html;
}

function setCheckinStage(stage) {
    activeCheckinStage = stage;
    const entryStage = document.getElementById('checkin-entry-stage');
    const reviewStage = document.getElementById('checkin-review-stage');
    entryStage?.classList.toggle('hidden', stage !== checkinReviewUi.INPUT_STAGE);
    reviewStage?.classList.toggle('hidden', stage !== checkinReviewUi.REVIEW_STAGE);
}

function renderActiveCheckinSummary(item) {
    const summaryEl = document.getElementById('active-checkin-summary');
    if (!summaryEl) return;
    if (!item) {
        summaryEl.innerHTML = '';
        summaryEl.classList.add('hidden');
        return;
    }
    const pills = checkinReviewUi.checkinSummaryPills({
        ...item,
        completion_status_text: completionStatusText(item?.completion_status),
        submission_result_text: item?.submission_result ? reviewStatusLabel(item.submission_result) : '',
        oj_source_text: ojSourceText(item?.oj_source),
    });
    if (!pills.length) {
        summaryEl.innerHTML = '';
        summaryEl.classList.add('hidden');
        return;
    }
    summaryEl.innerHTML = pills
        .map((pill) => `<span class="status-pill"><strong>${escapeHtml(pill.label)}：</strong>${escapeHtml(pill.value)}</span>`)
        .join('');
    summaryEl.classList.remove('hidden');
}

function renderActiveCheckinInputs(item) {
    const detailsEl = document.getElementById('active-checkin-inputs');
    const bodyEl = document.getElementById('active-checkin-inputs-body');
    if (!detailsEl || !bodyEl) return;
    const sections = checkinReviewUi.compactStudentInputSections(item);
    if (!sections.length) {
        bodyEl.innerHTML = '';
        detailsEl.classList.add('hidden');
        detailsEl.open = false;
        return;
    }
    bodyEl.innerHTML = sections.map((section) => `
        <div class="student-input-recall-item">
            <strong>${escapeHtml(section.label)}</strong>
            <div>${renderRichTextBlock(section.value)}</div>
        </div>
    `).join('');
    detailsEl.classList.remove('hidden');
}

function reviewStatusLabel(status) {
    const map = {
        not_submitted: '未提交',
        wa: 'WA',
        tle: 'TLE',
        re: 'RE',
        ce: 'CE',
        ac: 'AC',
        unknown: '不确定',
    };
    return map[status] || status || '';
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
        ['你卡在哪', item.review_stream_draft_problem_focus || item.review_stream_draft_main_block],
        ['关键一步', item.review_stream_draft_key_bridge],
        [reviewFamilyUi.reviewFieldLabel('visual_hint', item.review_stream_draft_visual_hint), item.review_stream_draft_visual_hint],
        ['跟我走一遍', item.review_stream_draft_guided_walkthrough],
        ['现在你来试', item.review_stream_draft_try_now || item.review_stream_draft_next_step],
        ['下次怎么认出来', item.review_stream_draft_transfer_signal],
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
    if (item.review_learning_status === 'knowledge_bailout') {
        return isTeacher ? '知识卡兜底中' : '这一步先换成知识讲解再过一遍';
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
    if (item.review_learning_status === 'knowledge_bailout') return 'remedy';
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
    const explanation = [config.title, config.explanation].filter(Boolean).join('\n\n');
    return renderQuizStageNotice({
        title: '这一步还没完全打通，我们先换一种方式继续。',
        explanation,
        tone: 'warn',
        kicker: '理解检查',
    });
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

function shouldRenderReviewUpdate(checkinId) {
    // Check if we're in review stage or showing the review workspace
    const workspaceContainer = document.getElementById('review-stage-content');
    const isDetailVisible = workspaceContainer && !workspaceContainer.classList.contains('hidden');
    return (
        (activeCheckinStage === checkinReviewUi.REVIEW_STAGE || isDetailVisible) &&
        Number(activeCheckinId) === Number(checkinId)
    );
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
        review_stream_draft_problem_focus: draft.problem_focus || draft.main_block || '',
        review_stream_draft_main_block: draft.main_block || '',
        review_stream_draft_key_bridge: draft.key_bridge || '',
        review_stream_draft_visual_hint: draft.visual_hint || '',
        review_stream_draft_guided_walkthrough: draft.guided_walkthrough || '',
        review_stream_draft_try_now: draft.try_now || draft.next_step || '',
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
        review_problem_focus: detail.review_problem_focus || nestedReview.problem_focus || nestedReview.main_block || '',
        review_main_block: detail.review_main_block || nestedReview.main_block || '',
        review_key_bridge: detail.review_key_bridge || nestedReview.key_bridge || '',
        review_visual_hint: detail.review_visual_hint || nestedReview.visual_hint || '',
        review_guided_walkthrough: detail.review_guided_walkthrough || nestedReview.guided_walkthrough || '',
        review_try_now: detail.review_try_now || nestedReview.try_now || nestedReview.next_step || '',
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
        review_stream_draft_problem_focus: detail.review_stream_draft_problem_focus || '',
        review_stream_draft_main_block: detail.review_stream_draft_main_block || '',
        review_stream_draft_key_bridge: detail.review_stream_draft_key_bridge || '',
        review_stream_draft_visual_hint: detail.review_stream_draft_visual_hint || '',
        review_stream_draft_guided_walkthrough: detail.review_stream_draft_guided_walkthrough || '',
        review_stream_draft_try_now: detail.review_stream_draft_try_now || '',
        review_stream_draft_next_step: detail.review_stream_draft_next_step || '',
        review_stream_draft_transfer_signal: detail.review_stream_draft_transfer_signal || '',
        quiz_history: Array.isArray(detail.quiz_history) ? detail.quiz_history : undefined,
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

async function refreshReviewDetailByReviewId(reviewId) {
    const checkinId = itemCheckinIdFromReview(reviewId);
    if (!checkinId) {
        await loadMyCheckins();
        return null;
    }
    const item = await fetchMyCheckinById(checkinId);
    const merged = mergeCheckinDetailIntoCache(item);
    renderCheckinHistoryList();
    if (shouldRenderReviewUpdate(checkinId)) {
        renderReviewDetailContent(merged);
    }
    return merged;
}

async function refreshPendingCheckin(checkinId) {
    const item = await fetchMyCheckinById(checkinId);
    const merged = mergeCheckinDetailIntoCache(item);
    renderCheckinHistoryList();
    if (shouldRenderReviewUpdate(checkinId)) {
        renderActiveCheckinWorkspace(merged);
    }
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

function startCheckinReviewStream(checkinId) {
    const workspaceContainer = document.getElementById('review-stage-content');
    const isDetailVisible = workspaceContainer && !workspaceContainer.classList.contains('hidden');
    
    // If showing detail view, subscribe to stream and update detail view
    if (isDetailVisible) {
        subscribeCheckinReviewStreamForDetail(checkinId);
    } else {
        subscribeCheckinReviewStream(checkinId, null);
    }
}

async function subscribeCheckinReviewStreamForDetail(checkinId) {
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
                renderCheckinHistoryList();
                if (shouldRenderReviewUpdate(checkinId)) {
                    // Update detail view instead of workspace
                    renderReviewDetailContent(merged);
                }

                if (eventName === 'review_ready' || payload.review_status === 'completed') {
                    streamState.terminal = true;
                    stopCheckinReviewStream(checkinId);
                    await refreshPendingCheckin(checkinId);
                    return;
                }

                if (eventName === 'error' || payload.review_status === 'failed') {
                    streamState.terminal = true;
                    stopCheckinReviewStream(checkinId);
                    await refreshPendingCheckin(checkinId);
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
            schedulePollFallbackForDetail(checkinId);
        }
    }
}

function schedulePollFallbackForDetail(checkinId) {
    const state = pendingReviewStreams.get(Number(checkinId));
    if (state) {
        state.fallbackStarted = true;
    }
    pollCheckinReviewStatusForDetail(checkinId);
}

async function pollCheckinReviewStatusForDetail(checkinId) {
    const checkinIdNum = Number(checkinId);
    const pollState = pendingReviewPolls.get(checkinIdNum);
    if (pollState && pollState.polling) return;

    pendingReviewPolls.set(checkinIdNum, { polling: true, timer: null });

    const doPoll = async () => {
        try {
            const item = await fetchMyCheckinById(checkinIdNum);
            const merged = mergeCheckinDetailIntoCache(item);
            renderCheckinHistoryList();
            if (shouldRenderReviewUpdate(checkinIdNum)) {
                renderReviewDetailContent(merged);
            }

            if (item.review_status === 'completed' || item.review_status === 'failed') {
                stopCheckinPoll(checkinIdNum);
                return;
            }

            if (!pendingReviewPolls.get(checkinIdNum)?.polling) return;
            const timer = setTimeout(doPoll, 3000);
            pendingReviewPolls.set(checkinIdNum, { polling: true, timer });
        } catch (err) {
            console.warn('poll error:', err);
            if (!pendingReviewPolls.get(checkinIdNum)?.polling) return;
            const timer = setTimeout(doPoll, 5000);
            pendingReviewPolls.set(checkinIdNum, { polling: true, timer });
        }
    };

    doPoll();
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
                renderCheckinHistoryList();
                if (shouldRenderReviewUpdate(checkinId)) {
                    renderActiveCheckinWorkspace(merged);
                }

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
            renderCheckinHistoryList();
            if (shouldRenderReviewUpdate(checkinId)) {
                renderActiveCheckinWorkspace(merged);
            }

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
                if (shouldRenderReviewUpdate(checkinId)) {
                    renderActiveCheckinWorkspace(timedOut);
                }
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
    document.getElementById('student-problem-id').value = problemId;

    document.getElementById('enter-btn').addEventListener('click', handleEnter);
    document.getElementById('login-password').addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            handleEnter();
        }
    });
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    setupTabs();
    setupThemeToggle();
    initSidebar();

    document.getElementById('check-quota-btn').addEventListener('click', studentCheckQuota);
    document.getElementById('student-problem-id').addEventListener('input', () => {
        activeChatProblemRef = normalizeProblemRef(document.getElementById('student-problem-id').value.trim());
        renderLinkedChatContextCard();
    });
    document.getElementById('send-btn').addEventListener('click', studentSendMessage);
    document.getElementById('clear-history-btn').addEventListener('click', clearChatHistory);
    
    // Setup chat input auto-resize and enter-to-send
    const chatInput = document.getElementById('student-message');
    const sendBtn = document.getElementById('send-btn');
    if (chatInput && sendBtn) {
        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';
            // Enable/disable send button
            sendBtn.disabled = chatInput.value.trim().length === 0;
        });
        
        // Enter to send, Shift+Enter for new line
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!sendBtn.disabled) {
                    studentSendMessage();
                }
            }
        });
    }
    document.getElementById('submit-checkin-btn').addEventListener('click', submitCheckin);
    document.getElementById('load-my-checkins-btn').addEventListener('click', loadMyCheckins);
    
    // History search
    document.getElementById('history-search-btn')?.addEventListener('click', () => {
        historySearchKeyword = document.getElementById('history-search-keyword')?.value.trim() || '';
        historySearchAlgorithm = document.getElementById('history-search-algorithm')?.value.trim() || '';
        renderCheckinHistoryList();
    });
    
    // Enter key to search in history
    document.getElementById('history-search-keyword')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            historySearchKeyword = e.target.value.trim();
            historySearchAlgorithm = document.getElementById('history-search-algorithm')?.value.trim() || '';
            renderCheckinHistoryList();
        }
    });
    
    document.getElementById('history-search-algorithm')?.addEventListener('change', () => {
        historySearchKeyword = document.getElementById('history-search-keyword')?.value.trim() || '';
        historySearchAlgorithm = document.getElementById('history-search-algorithm')?.value.trim() || '';
        renderCheckinHistoryList();
    });
    
    // Code editor line numbers sync
    const codeTextarea = document.getElementById('checkin-student-code');
    const lineNumbersEl = document.getElementById('code-line-numbers');
    if (codeTextarea && lineNumbersEl) {
        function updateLineNumbers() {
            const lines = codeTextarea.value.split('\n').length;
            const lineNumbers = Array.from({ length: Math.max(lines, 1) }, (_, i) => i + 1).join('\n');
            lineNumbersEl.textContent = lineNumbers;
        }
        
        codeTextarea.addEventListener('input', updateLineNumbers);
        codeTextarea.addEventListener('scroll', () => {
            lineNumbersEl.scrollTop = codeTextarea.scrollTop;
        });
        
        // Support Tab key for indentation
        codeTextarea.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = codeTextarea.selectionStart;
                const end = codeTextarea.selectionEnd;
                codeTextarea.value = codeTextarea.value.substring(0, start) + '    ' + codeTextarea.value.substring(end);
                codeTextarea.selectionStart = codeTextarea.selectionEnd = start + 4;
                updateLineNumbers();
            }
        });
        
        // Initial line numbers
        updateLineNumbers();
    }
    document.getElementById('open-history-tab-btn')?.addEventListener('click', () => showStudentTab('history-tab'));
    document.getElementById('back-to-checkin-form-btn')?.addEventListener('click', () => {
        const previousCheckinId = activeCheckinId;
        if (previousCheckinId) {
            stopCheckinReviewStream(previousCheckinId);
            stopCheckinPoll(previousCheckinId);
        }
        activeCheckinId = null;
        activeCheckinStage = checkinReviewUi.INPUT_STAGE;
        activeRelatedProblemPid = '';
        const resultEl = document.getElementById('checkin-result');
        if (resultEl) {
            resultEl.classList.add('hidden');
            resultEl.innerHTML = '';
        }
        renderCheckinHistoryList();
        renderCheckinEntryStage();
        document.getElementById('checkin-entry-stage')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
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
    setupCheckinChatInterface();

    if (authToken && currentUserId && userRole) {
        showMainInterface();
    }
});

function setupTabs() {
    // Sidebar navigation
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach((link) => {
        link.addEventListener('click', () => {
            const tab = link.dataset.tab;
            const section = link.dataset.section;
            if (section === 'student') {
                showStudentTab(tab);
            } else if (section === 'teacher') {
                showTeacherTab(tab);
            }
        });
    });
}

function showTeacherTab(targetId) {
    // Hide all tab contents
    document.querySelectorAll('#teacher-section .tab-content').forEach((content) => {
        content.classList.add('hidden');
        content.classList.remove('active');
    });
    
    // Show target tab
    const target = document.getElementById(targetId);
    if (target) {
        target.classList.remove('hidden');
        target.classList.add('active');
    }
    
    // Update sidebar active state
    document.querySelectorAll('#teacher-nav .sidebar-link').forEach((link) => {
        link.classList.toggle('active', link.dataset.tab === targetId);
    });
    
    if (targetId === 'manual-review-tab') {
        loadTeacherReviewSamples();
    }
}

// ============ 主题切换 ============

function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    // Update UI based on current theme
    updateThemeUI();
    
    // Add click handler
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        if (newTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
        
        updateThemeUI();
    });
}

function updateThemeUI() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const isDark = currentTheme === 'dark';
    
    const sunIcon = themeToggle.querySelector('.sun-icon');
    const moonIcon = themeToggle.querySelector('.moon-icon');
    
    if (isDark) {
        if (sunIcon) sunIcon.style.display = 'block';
        if (moonIcon) moonIcon.style.display = 'none';
        themeToggle.title = '切换为浅色模式';
        themeToggle.style.background = 'var(--bg-tertiary)';
    } else {
        if (sunIcon) sunIcon.style.display = 'none';
        if (moonIcon) moonIcon.style.display = 'block';
        themeToggle.title = '切换为深色模式';
        themeToggle.style.background = '';
    }
}

// ============ 打卡复盘聊天界面 ============

function setupCheckinChatInterface() {
    // Input panel toggle
    const inputToggle = document.getElementById('checkin-input-toggle');
    const inputPanel = document.getElementById('checkin-input-panel');
    
    if (inputToggle && inputPanel) {
        inputToggle.addEventListener('click', () => {
            inputPanel.classList.toggle('expanded');
        });
    }
    
    // Quick message input auto-resize
    const quickMessage = document.getElementById('checkin-quick-message');
    if (quickMessage) {
        quickMessage.addEventListener('input', () => {
            quickMessage.style.height = 'auto';
            quickMessage.style.height = Math.min(quickMessage.scrollHeight, 150) + 'px';
            
            // Sync to bottleneck textarea
            const bottleneck = document.getElementById('checkin-bottleneck');
            if (bottleneck && !bottleneck.value) {
                bottleneck.value = quickMessage.value;
            }
            
            // Enable submit button if there's content
            const submitBtn = document.getElementById('submit-checkin-btn');
            if (submitBtn) {
                submitBtn.disabled = quickMessage.value.trim().length === 0;
            }
        });
        
        // Enter to submit, Shift+Enter for new line
        quickMessage.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const submitBtn = document.getElementById('submit-checkin-btn');
                if (submitBtn && !submitBtn.disabled) {
                    submitCheckinFromChat();
                }
            }
        });
    }
    
    // Clear button
    const clearBtn = document.getElementById('clear-checkin-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            clearCheckinChat();
        });
    }
    
    // Update submit button handler
    const submitBtn = document.getElementById('submit-checkin-btn');
    if (submitBtn) {
        // Remove old listener and add new
        const newBtn = submitBtn.cloneNode(true);
        submitBtn.parentNode.replaceChild(newBtn, submitBtn);
        newBtn.addEventListener('click', submitCheckinFromChat);
    }
}

function submitCheckinFromChat() {
    const quickMessage = document.getElementById('checkin-quick-message');
    const bottleneck = document.getElementById('checkin-bottleneck');
    
    // Sync quick message to bottleneck if bottleneck is empty
    if (quickMessage && quickMessage.value.trim() && !bottleneck.value.trim()) {
        bottleneck.value = quickMessage.value.trim();
    }
    
    // Add user message to chat
    const message = quickMessage ? quickMessage.value.trim() : '';
    if (message) {
        addCheckinUserMessage(message);
        quickMessage.value = '';
        quickMessage.style.height = 'auto';
    }
    
    // Show loading
    addCheckinLoadingMessage();
    
    // Call original submit function
    submitCheckin();
}

function addCheckinUserMessage(text) {
    const messagesContainer = document.getElementById('checkin-messages');
    if (!messagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'checkin-message user';
    messageDiv.innerHTML = `
        <div class="checkin-avatar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
        </div>
        <div class="checkin-bubble">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addCheckinLoadingMessage() {
    const messagesContainer = document.getElementById('checkin-messages');
    if (!messagesContainer) return;
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'checkin-message ai checkin-loading-message';
    loadingDiv.innerHTML = `
        <div class="checkin-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
        </div>
        <div class="checkin-loading">
            <div class="checkin-loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span>正在分析你的问题...</span>
        </div>
    `;
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeCheckinLoadingMessage() {
    const loadingMsg = document.querySelector('.checkin-loading-message');
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

function addCheckinAIResponse(response) {
    removeCheckinLoadingMessage();
    
    const messagesContainer = document.getElementById('checkin-messages');
    if (!messagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'checkin-message ai';
    messageDiv.innerHTML = `
        <div class="checkin-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
        </div>
        <div class="checkin-bubble">
            ${response}
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function clearCheckinChat() {
    const messagesContainer = document.getElementById('checkin-messages');
    if (messagesContainer) {
        messagesContainer.innerHTML = `
            <div class="checkin-message ai">
                <div class="checkin-avatar">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                </div>
                <div class="checkin-bubble">
                    <p>你好！我是你的打卡复盘助手。请告诉我你当前做题遇到的问题，我会帮你分析并给出建议。</p>
                    <p style="margin-top: 8px;">你可以直接描述，或者使用下方的快捷输入来填写详细信息。</p>
                </div>
            </div>
        `;
    }
    
    // Clear form fields
    const fields = ['checkin-title', 'checkin-bottleneck', 'checkin-problem-context', 'checkin-reflection', 'checkin-student-code', 'checkin-quick-message'];
    fields.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    
    // Clear error types
    document.querySelectorAll('input[name="error_type"]').forEach(cb => {
        cb.checked = false;
    });
}

// ============ 登录 / 退出 ============

async function handleEnter() {
    const userIdInput = document.getElementById('student-id').value.trim();
    const password = document.getElementById('login-password').value.trim();

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
    document.getElementById('main-app').classList.remove('hidden');

    document.getElementById('current-user').textContent = currentUserId;
    document.getElementById('current-role').textContent = userRole === 'teacher' ? '教师' : '学生';
    
    // Update user avatar
    const avatarEl = document.getElementById('user-avatar');
    if (avatarEl) {
        avatarEl.textContent = currentUserId.charAt(0).toUpperCase();
        // Set gradient based on role
        if (userRole === 'teacher') {
            avatarEl.style.background = 'linear-gradient(135deg, #AF52DE 0%, #5856D6 100%)';
        } else {
            avatarEl.style.background = 'linear-gradient(135deg, #FF2D55 0%, #FF9500 100%)';
        }
    }
    document.getElementById('student-problem-id').value = problemId;

    if (userRole === 'teacher') {
        document.getElementById('student-section').classList.add('hidden');
        document.getElementById('student-nav').classList.add('hidden');
        document.getElementById('teacher-section').classList.remove('hidden');
        document.getElementById('teacher-nav').classList.remove('hidden');
        showTeacherTab('quota-tab');
        loadAllCheckins();
        loadErrorStats();
        loadUsageStats();
        loadStudentFlags();
        loadProblemAnalysisFailures();
    } else {
        document.getElementById('teacher-section').classList.add('hidden');
        document.getElementById('teacher-nav').classList.add('hidden');
        document.getElementById('student-section').classList.remove('hidden');
        document.getElementById('student-nav').classList.remove('hidden');
        showStudentTab('chat-tab');
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
        const quotaInfo = document.getElementById('quota-info');
        if (quotaInfo) {
            quotaInfo.innerHTML = `
                <span class="badge badge-primary">${data.problem_id}</span>
                <span class="badge badge-info">已用 ${data.count}/${data.max}</span>
                <span class="badge badge-success">剩余 ${data.remaining}</span>
            `;
        }
    } catch (err) {
        const quotaInfo = document.getElementById('quota-info');
        if (quotaInfo) {
            quotaInfo.innerHTML = `<span class="badge badge-error">查询失败</span>`;
        }
    }
}

async function studentSendMessage() {
    const pid = document.getElementById('student-problem-id').value.trim() || problemId;
    const messageInput = document.getElementById('student-message');
    const message = messageInput.value.trim();
    const sendBtn = document.getElementById('send-btn');
    
    if (!message) return;

    problemId = pid;
    activeChatProblemRef = normalizeProblemRef(pid);
    localStorage.setItem('noi_problem_id', problemId);

    // Add user message
    addChatMessage('user', message);
    
    // Clear input and reset height
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Show loading
    addLoadingMessage();

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
        removeLoadingMessage();
        addChatMessage('assistant', data.reply);
        rememberProblemChatContext(activeChatProblemRef || pid, message, data.reply);
        renderLinkedChatContextCard();
        
        // Update quota display
        const quotaInfo = document.getElementById('quota-info');
        if (quotaInfo) {
            quotaInfo.innerHTML = `
                <span class="badge badge-primary">剩余 ${data.remaining_quota} 次</span>
                <span class="badge badge-info">级别 ${data.level}</span>
            `;
        }
    } catch (err) {
        removeLoadingMessage();
        addChatMessage('assistant', '抱歉，发生了错误：' + err.message + '。请稍后重试。');
    }
}

function addChatMessage(role, content) {
    const chatHistory = document.getElementById('chat-history');
    const div = document.createElement('div');
    
    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    if (role === 'user') {
        div.className = 'user-message';
        div.innerHTML = `
            <div class="user-avatar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>
            </div>
            <div class="user-message-content">
                <div class="user-message-header">
                    <span class="user-name">你</span>
                    <span class="user-time">${timeStr}</span>
                </div>
                <div class="user-message-body">
                    <p>${escapeHtml(content)}</p>
                </div>
            </div>
        `;
    } else {
        div.className = 'ai-message';
        div.innerHTML = `
            <div class="ai-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <div class="ai-message-content">
                <div class="ai-message-header">
                    <span class="ai-name">AI 竞赛教练</span>
                    <span class="ai-time">${timeStr}</span>
                </div>
                <div class="ai-message-body">
                    <p>${escapeHtml(content)}</p>
                </div>
            </div>
        `;
    }
    
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function addLoadingMessage() {
    const chatHistory = document.getElementById('chat-history');
    const div = document.createElement('div');
    div.className = 'ai-message ai-message-loading';
    div.id = 'ai-loading-message';
    div.innerHTML = `
        <div class="ai-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
        </div>
        <div class="ai-message-loading">
            <div class="ai-loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span style="color: var(--text-secondary);">正在思考...</span>
        </div>
    `;
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function removeLoadingMessage() {
    const loadingMsg = document.getElementById('ai-loading-message');
    if (loadingMsg) {
        loadingMsg.remove();
    }
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
    const tags = review.error_tags?.length ? review.error_tags.join(', ') : '';
    const subtags = review.core_design_subtags?.length ? review.core_design_subtags.join(', ') : '';
    
    // 定义每个字段的图标和样式
    const fieldConfig = {
        problem_focus: { icon: '🎯', title: '问题定位', gradient: 'focus' },
        main_block: { icon: '🎯', title: '问题定位', gradient: 'focus' },
        key_bridge: { icon: '💡', title: '关键桥梁', gradient: 'bridge' },
        visual_hint: { icon: '👀', title: '看图想一想', gradient: 'bridge' },
        guided_walkthrough: { icon: '👣', title: '跟我走一遍', gradient: 'walkthrough' },
        try_now: { icon: '✏️', title: '现在你来试', gradient: 'try' },
        next_step: { icon: '✏️', title: '现在你来试', gradient: 'try' },
        transfer_signal: { icon: '🔮', title: '下次怎么认出来', gradient: 'transfer' },
    };
    
    // 生成对话式卡片流
    const messageCards = reviewFamilyUi
        .orderedReviewSections(review, family)
        .filter((section) => String(section.value || '').trim())
        .map((section, index, arr) => {
            const config = fieldConfig[section.field] || { icon: '•', title: section.label, gradient: 'focus' };
            const isVisualHint = section.field === 'visual_hint';
            const content = isVisualHint
                ? `<pre class="review-visual-hint" style="margin-top: 12px;">${escapeHtml(section.value || '')}</pre>`
                : `<div class="review-message-content" style="margin-top: 8px;">${renderRichTextInline(section.value || '')}</div>`;
            
            // 连接线（除最后一个）
            const connector = index < arr.length - 1 ? '<div class="review-message-connector">↓</div>' : '';
            
            return `
                <div class="review-message-card">
                    <div class="review-message-header">
                        <div class="review-message-icon ${config.gradient}">${config.icon}</div>
                        <div class="review-message-title">${escapeHtml(config.title)}</div>
                    </div>
                    ${content}
                </div>
                ${connector}
            `;
        })
        .join('');

    // 结构化诊断层（折叠展示，保持原样但样式优化）
    const detailRows = [];
    if (tags) detailRows.push(`<p><strong>错误标签:</strong> ${escapeHtml(tags)}</p>`);
    if (review.error_layer) detailRows.push(`<p><strong>统一归类:</strong> ${escapeHtml(errorLayerText(review.error_layer))}</p>`);
    if (review.error_layer_confidence) detailRows.push(`<p><strong>判断把握:</strong> ${escapeHtml(confidenceText(review.error_layer_confidence))}</p>`);
    if (subtags) detailRows.push(`<p><strong>核心设计子标签:</strong> ${escapeHtml(subtags)}</p>`);
    if (review.diagnosis) detailRows.push(`<div><strong>问题诊断:</strong> ${renderRichTextInline(review.diagnosis || '')}</div>`);
    if (review.next_action) detailRows.push(`<div><strong>下一步行动:</strong> ${renderRichTextInline(review.next_action || '')}</div>`);
    if (review.suggested_topic) detailRows.push(`<div><strong>推荐专题:</strong> ${renderRichTextInline(review.suggested_topic || '')}</div>`);

    const diagnosisHtml = detailRows.length ? `
        <details class="review-diagnosis-detail" style="margin-top: 20px; opacity: 0.8;">
            <summary style="font-size: 13px; color: var(--text-secondary);">查看诊断依据</summary>
            <div style="padding-top: 12px; font-size: 13px;">
                ${detailRows.join('')}
            </div>
        </details>
    ` : '';

    // 尝试使用 Tailwind UI
    if (typeof window.TwUI !== 'undefined') {
        try {
            return window.TwUI.renderReviewSection(review, family);
        } catch (e) {
            console.warn('Tailwind UI 复盘渲染失败:', e);
        }
    }

    return `
        <div class="review-box-v2 family-${escapeHtml(family)}">
            <h4 style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px;">
                <span style="font-size: 20px;">🤖</span>
                ${family === 'success_reflection' ? 'AI 理解复盘' : 'AI 复盘报告'}
            </h4>
            <div class="review-message-flow">
                ${messageCards}
            </div>
            ${diagnosisHtml}
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
        knowledge_bailout_success: '知识卡后过桥',
        knowledge_bailout_failed: '知识卡后仍未掌握',
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
        knowledge_bailout_success: { label: '知识卡后过桥', className: 'teacher-evidence support' },
        knowledge_bailout_failed: { label: '知识卡后仍未掌握', className: 'teacher-evidence risk' },
    };
    return map[path] || null;
}

function masteryStatusTeacherBadge(status) {
    const map = {
        independent_success: { label: '独立过桥', className: 'teacher-evidence strong' },
        assisted_success: { label: '辅助后过桥', className: 'teacher-evidence support' },
        not_mastered: { label: '仍未掌握', className: 'teacher-evidence risk' },
    };
    return map[status] || null;
}

function bridgePathTeacherNote(path) {
    const map = {
        main_clear: '这次主要证据来自首轮答对和学生自评，说明这一步更像是学生自己先站稳了。',
        main_guessed_confirm: '学生首轮答对，但自己承认“有点蒙”，最后通过换角度确认才过桥，说明理解是后来补稳的。',
        main_guessed_remedy: '学生首轮虽然答对，但自评并不稳，最终还是进入补救，不能把这次判断成独立掌握。',
        main_confused_remedy: '学生首轮答对后主动承认没懂，这类记录对老师很有价值，说明学生愿意暴露真实困惑，补救才是关键证据。',
        followup_correct: '这一步是在微提示之后过桥的，说明学生需要脚手架支持，不能按“完全独立起步”理解。',
        followup_remedy: '首轮和 follow-up 都没打通，最后还要靠补救，这通常意味着这座桥对学生来说还不稳。',
        knowledge_bailout_success: '前三轮都没站稳，最后靠知识卡兜底后才过桥。这说明学生需要概念级讲解支持，但至少已经把这座桥重新站起来了。',
        knowledge_bailout_failed: '即使换成知识卡单独讲解，这一步仍然没有站稳。对老师来说，这通常意味着需要更个别化地回到前置知识或思维断点。',
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
            <div class="quiz-input-wrap" style="margin: 16px 0;">
                <label class="quiz-input-label" for="quiz-answer-${reviewId}" style="display: block; margin-bottom: 8px; font-size: 13px; color: var(--text-secondary);">写下你的答案</label>
                <input type="text" id="quiz-answer-${reviewId}" class="quiz-input" placeholder="输入你的答案" style="width: 100%; padding: 12px 16px; border: 2px solid var(--border-light); border-radius: 12px; font-size: 14px;">
            </div>
        `;
    }
    
    // 生成选项卡片的 onclick 处理
    const optionsHtml = (quiz.options || []).map((option, idx) => {
        const optionValue = typeof option === 'object' && option !== null ? option.value : option;
        const optionLabel = typeof option === 'object' && option !== null ? option.label : option;
        const optionMark = String.fromCharCode(65 + idx);
        return `
            <div class="quiz-option-card" onclick="selectQuizOption(this, '${escapeHtml(optionValue)}', ${reviewId})" data-value="${escapeHtml(optionValue)}">
                <div class="quiz-option-badge">${escapeHtml(optionMark)}</div>
                <div class="quiz-option-text">${renderRichTextInline(optionLabel)}</div>
            </div>
        `;
    }).join('');
    
    return `
        <div class="quiz-options-list">
            ${optionsHtml}
        </div>
        <input type="hidden" id="quiz-selected-${reviewId}" value="">
    `;
}

// 选项选择处理函数
function selectQuizOption(element, value, reviewId) {
    // 移除同组其他选项的选中状态
    const parent = element.parentElement;
    parent.querySelectorAll('.quiz-option-card').forEach(el => el.classList.remove('selected'));
    // 添加当前选项的选中状态
    element.classList.add('selected');
    // 更新隐藏字段
    const hiddenInput = document.getElementById(`quiz-selected-${reviewId}`);
    if (hiddenInput) hiddenInput.value = value;
}

function quizCardTitle(quiz) {
    const level = quiz?.meta?.difficulty_level || quiz?.difficulty_level || 'main';
    if (level === 'followup') return '这一步还差一点，我们再拆小一点';
    if (level === 'confirm') return '你刚才像是有点蒙，我们换个角度再确认一下';
    if (level === 'easier') return '再来一道更小的小题';
    if (level === 'knowledge_confirm') return '知识卡后确认';
    return '试试看你是不是已经懂这一步了';
}

function quizCardLead(quiz) {
    const level = quiz?.meta?.difficulty_level || quiz?.difficulty_level || 'main';
    if (level === 'followup') {
        return '我们不重讲整题，只再盯这一小步。';
    }
    if (level === 'confirm') {
        return '这不是更简单的一题，而是换个角度确认你是不是真的懂了。';
    }
    if (level === 'easier') {
        return '如果刚才那题还是有点卡，我们先做一个更小、更具体的小题。';
    }
    if (level === 'knowledge_confirm') {
        return '先看完上面的知识讲解，再用这题确认这座桥有没有重新站稳。';
    }
    return '';
}

function renderKnowledgeBailoutCard(card = {}) {
    if (!card || typeof card !== 'object') return '';
    const opening = String(card.opening || '').trim();
    const bridgeExplanation = String(card.bridge_explanation || '').trim();
    const visualHint = String(card.visual_hint || '').trim();
    const algorithmOverview = String(card.algorithm_overview || '').trim();
    const microAction = String(card.micro_action || '').trim();
    if (!opening && !bridgeExplanation && !algorithmOverview && !microAction && !visualHint) return '';
    
    // 对比表格（如果有对比内容）
    const hasComparison = card.wrong_thinking && card.right_thinking;
    const comparisonHtml = hasComparison ? `
        <div class="knowledge-comparison-table">
            <div class="knowledge-comparison-item wrong">
                <div class="knowledge-comparison-label">❌ 这样想</div>
                <div>${renderRichTextInline(card.wrong_thinking)}</div>
            </div>
            <div class="knowledge-comparison-item right">
                <div class="knowledge-comparison-label">✅ 其实应该</div>
                <div>${renderRichTextInline(card.right_thinking)}</div>
            </div>
        </div>
    ` : '';
    
    // 算法全景（可折叠）
    const overviewHtml = algorithmOverview ? `
        <div class="knowledge-expandable" id="knowledge-overview-${Date.now()}">
            <div class="knowledge-expandable-header" onclick="this.parentElement.classList.toggle('expanded')">
                <span>🗺️ 在知识地图里的位置</span>
                <span class="knowledge-expandable-icon">▼</span>
            </div>
            <div class="knowledge-expandable-content">
                ${renderRichTextInline(algorithmOverview)}
            </div>
        </div>
    ` : '';
    
    return `
        <div class="knowledge-bailout-card-v2">
            <div class="knowledge-bailout-header">
                <div class="knowledge-bailout-kicker-v2">📚 补课时间</div>
            </div>
            ${opening ? `<div class="knowledge-bailout-opening">${renderRichTextBlock(opening)}</div>` : ''}
            
            <div style="margin-top: 16px;">
                <div style="font-weight: 600; font-size: 14px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                    <span>🎯</span> 当前这座桥
                </div>
                ${bridgeExplanation ? `<div style="font-size: 14px; line-height: 1.7; color: var(--text-secondary);">${renderRichTextInline(bridgeExplanation)}</div>` : ''}
                ${comparisonHtml}
                ${visualHint ? `<pre class="review-visual-hint" style="margin-top: 12px; background: rgba(255,255,255,0.5);">${escapeHtml(visualHint)}</pre>` : ''}
            </div>
            
            ${overviewHtml}
            
            ${microAction ? `<div style="margin-top: 16px; padding-top: 16px; border-top: 1px dashed rgba(0,0,0,0.1);"><strong>💡 看完后先记住：</strong>${renderRichTextInline(microAction)}</div>` : ''}
        </div>
    `;
}

function renderQuizCard(quiz, reviewId) {
    if (!quiz) return '';
    const microHint = quiz.meta?.micro_hint
        ? `<div class="quiz-hint" style="margin-bottom: 12px; padding: 10px 14px; background: rgba(0,122,255,0.06); border-radius: 10px; font-size: 13px; color: var(--text-secondary);">💡 先提醒一句：${renderRichTextInline(quiz.meta.micro_hint)}</div>`
        : '';
    const lead = quizCardLead(quiz)
        ? `<div class="quiz-lead" style="margin-bottom: 12px; font-size: 13px; color: var(--text-secondary); line-height: 1.6;">${escapeHtml(quizCardLead(quiz))}</div>`
        : '';
    
    // 确定题型徽章
    const level = quiz?.meta?.difficulty_level || quiz?.difficulty_level || 'main';
    const badgeClass = level === 'followup' ? 'followup' : level === 'confirm' ? 'confirm' : level === 'final_micro_confirm' ? 'final' : level === 'knowledge_confirm' ? 'knowledge' : 'main';
    const badgeText = level === 'followup' ? '再拆小一点' : level === 'confirm' ? '换个角度确认' : level === 'final_micro_confirm' ? '最终确认' : level === 'knowledge_confirm' ? '知识卡后' : '理解检查';
    
    return `
        <div class="quiz-card-v2">
            <div class="quiz-card-header">
                <div class="quiz-card-badge ${badgeClass}">${escapeHtml(badgeText)}</div>
            </div>
            ${lead}
            ${microHint}
            <div class="quiz-question-v2">
                ${renderRichTextBlock(quiz.question_text)}
            </div>
            ${renderQuizOptions(quiz, reviewId)}
            <div class="quiz-actions" style="margin-top: 20px;">
                <button class="primary" style="width: 100%; padding: 12px; border-radius: 12px; font-size: 15px; font-weight: 500;" onclick="submitQuizAnswer(${Number(quiz.quiz_id)}, ${Number(reviewId)})">提交答案</button>
            </div>
        </div>
    `;
}

function renderQuizFeedbackBlock({ title, feedbackText = '', bridgeFeedback = '', explanation = '', tone = 'success' }) {
    const icon = tone === 'success' ? '🎉' : tone === 'final' ? '📌' : '💡';
    const bgStyle = tone === 'success' 
        ? 'background: linear-gradient(135deg, rgba(52,199,89,0.08) 0%, rgba(34,197,94,0.05) 100%); border-color: rgba(52,199,89,0.25);'
        : tone === 'final'
            ? 'background: linear-gradient(135deg, rgba(175,82,222,0.08) 0%, rgba(139,92,246,0.05) 100%); border-color: rgba(175,82,222,0.25);'
            : 'background: linear-gradient(135deg, rgba(0,122,255,0.08) 0%, rgba(59,130,246,0.05) 100%); border-color: rgba(0,122,255,0.25);';
    
    return `
        <div class="quiz-card-v2" style="${bgStyle} margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-weight: 600;">
                <span style="font-size: 20px;">${icon}</span>
                <span>${escapeHtml(title)}</span>
            </div>
            ${feedbackText ? `<div style="font-size: 14px; line-height: 1.6; margin-bottom: 12px;">${renderRichTextBlock(feedbackText)}</div>` : ''}
            ${bridgeFeedback ? `<div style="font-size: 13px; padding: 10px 14px; background: rgba(255,255,255,0.5); border-radius: 10px; margin-top: 10px;"><strong>✅ 你刚才真正答对的是：</strong>${renderRichTextInline(bridgeFeedback)}</div>` : ''}
            ${explanation ? `<div style="font-size: 13px; color: var(--text-secondary); margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--border-light);">${renderRichTextBlock(explanation)}</div>` : ''}
        </div>
    `;
}

function quizHistoryStepTitle(quiz, index) {
    const level = quiz?.meta?.difficulty_level || quiz?.difficulty_level || '';
    if (level === 'followup') return `第 ${index + 1} 题 · 再拆小一点`;
    if (level === 'confirm') return `第 ${index + 1} 题 · 换个角度确认`;
    if (level === 'easier') return `第 ${index + 1} 题 · 更小的小题`;
    if (level === 'final_micro_confirm') return `第 ${index + 1} 题 · 最后一小题确认`;
    if (level === 'knowledge_confirm') return `第 ${index + 1} 题 · 知识卡后确认`;
    return `第 ${index + 1} 题 · 理解检查`;
}

function quizAnswerLabel(quiz, answerText = '') {
    const normalized = String(answerText || '').trim();
    if (!normalized) return '';
    const match = (quiz?.options || []).find((option) => {
        if (typeof option === 'object' && option !== null) {
            return String(option.value || '').trim() === normalized;
        }
        return false;
    });
    if (match && typeof match === 'object') {
        return match.label || normalized;
    }
    return normalized;
}

function renderAnsweredQuizHistoryStep(quiz, index) {
    if (!quiz) return '';
    const tone = quiz.latest_is_correct ? 'success' : 'warn';
    const answerLabel = quizAnswerLabel(quiz, quiz.latest_answer_text);
    const resultLabel = quiz.latest_is_correct ? '这一步答对了' : '这一步还没过';
    const knowledgeCard = quiz?.meta?.knowledge_card;
    return `
        <div class="quiz-history-step tone-${escapeHtml(tone)}">
            <div class="quiz-history-step-head">
                <div class="quiz-history-step-title">${escapeHtml(quizHistoryStepTitle(quiz, index))}</div>
                <span class="quiz-history-step-badge">${escapeHtml(resultLabel)}</span>
            </div>
            ${quiz?.meta?.knowledge_bailout ? renderKnowledgeBailoutCard(knowledgeCard) : ''}
            <div class="quiz-question-card">
                <div class="quiz-question-kicker">题目</div>
                <div class="quiz-question">${renderRichTextBlock(quiz.question_text)}</div>
            </div>
            ${answerLabel ? `<div class="quiz-history-answer"><strong>你的回答：</strong>${renderRichTextInline(answerLabel)}</div>` : ''}
            ${quiz.latest_feedback_text ? `<div class="quiz-history-feedback">${renderRichTextBlock(quiz.latest_feedback_text)}</div>` : ''}
        </div>
    `;
}

function renderQuizTimelineStatus(item, reviewId, reviewFamily) {
    if (item.review_learning_status === 'self_check_required') {
        return renderSelfCheckCard(reviewId, reviewFamily);
    }
    if (item.review_learning_status === 'resolved') {
        const title = item.review_mastery_status === 'assisted_success'
            ? '这一步在提示后已经站稳了。'
            : '这一步已经站稳了。';
        return renderQuizStageNotice({
            title,
            explanation: item.quiz_latest_feedback || '',
            tone: 'info',
            kicker: '当前结果',
        });
    }
    if (item.review_learning_status === 'needs_teacher_followup') {
        return renderQuizStageNotice({
            title: '这一步先停在这里，老师会接着和你一起看。',
            explanation: item.quiz_latest_feedback || '',
            tone: 'warn',
            kicker: '当前结果',
        });
    }
    if (item.review_learning_status === 'knowledge_bailout') {
        return renderQuizStageNotice({
            title: '前三轮题先留在上面，我们换成知识讲解把这一步单独讲清楚。',
            explanation: '这次不是继续追问，而是先把当前桥换成知识卡，再做最后一次最小确认。',
            tone: 'info',
            kicker: '知识兜底',
        });
    }
    if (item.review_learning_status === 'remedy_available' || item.review_learning_status === 'remedy_in_progress') {
        const remedyTransition = resolveRemedyTransition({
            understandingSelfCheck: item.review_understanding_self_check,
            quizRole: item.quiz_role,
            feedbackText: item.quiz_latest_feedback,
            explanation: item.quiz_explanation,
        });
        return `
            ${renderRemedyTransitionCard(remedyTransition)}
            ${renderRemedyButtons(reviewId, item.review_error_layer)}
        `;
    }
    return '';
}

function renderReviewDetailQuizTimeline(item) {
    const reviewId = Number(item.review_id || 0);
    if (!reviewId) return '';
    const reviewFamily = reviewFamilyUi.resolveReviewFamily(item);
    const quizHistory = Array.from(item.quiz_history || []).filter((quiz) => quiz && quiz.status !== 'replaced');

    if (!quizHistory.length) {
        if (item.quiz_status === 'pending' && item.quiz_id) {
            return `
                <div class="learning-path-timeline">
                    <div class="timeline-step current">
                        <div class="step-badge current">📍 第 1 步</div>
                        ${renderQuizCard({
                            quiz_id: item.quiz_id,
                            question_text: item.quiz_question_text || item.question_text,
                            quiz_type: item.quiz_question_type || item.question_type || item.quiz_type,
                            options: item.quiz_options || item.options,
                            meta: item.quiz_meta || item.meta,
                            difficulty_level: item.quiz_difficulty_level || item.difficulty_level,
                        }, reviewId)}
                    </div>
                </div>
            `;
        }
        return renderQuizTimelineStatus(item, reviewId, reviewFamily) || `
            <button class="secondary" onclick="startReviewQuiz(${reviewId})">开始理解检查</button>
        `;
    }

    const currentQuizId = Number(item.quiz_id || 0);
    const totalSteps = quizHistory.length + (item.quiz_status === 'pending' ? 1 : 0);
    
    const html = quizHistory.map((quiz, index) => {
        const isPending = quiz.status === 'pending' && (!currentQuizId || Number(quiz.quiz_id) === currentQuizId);
        const stepNumber = index + 1;
        const stepClass = isPending ? 'current' : quiz.latest_is_correct ? 'completed' : 'completed';
        const badgeClass = isPending ? 'current' : 'completed';
        
        if (isPending) {
            const level = quiz?.meta?.difficulty_level || quiz?.difficulty_level || '';
            const notice = level === 'followup'
                ? renderQuizStageNotice({
                    title: '上一题先留在上面，我们把这一步再拆小一点。',
                    explanation: '这次只盯当前这一小步，不回到整题大结论。',
                    tone: 'warn',
                    kicker: 'follow-up',
                    })
                : level === 'knowledge_confirm'
                    ? renderQuizStageNotice({
                        title: '前三轮题先留在上面，我们先把这一步单独讲清楚，再做最后一题确认。',
                        explanation: '这不是重新开一轮 quiz，而是换成知识讲解把当前这座桥补稳。',
                        tone: 'info',
                        kicker: '知识兜底',
                    })
                : level === 'final_micro_confirm'
                    ? renderQuizStageNotice({
                        title: '前面几题先留在上面，我们用最后一个最小问题做收尾确认。',
                        explanation: '这题只确认刚才那座桥是不是真的站稳了。',
                        tone: 'info',
                        kicker: '最终确认',
                    })
                    : '';
            return `
                <div class="timeline-step ${stepClass}">
                    <div class="step-badge ${badgeClass}">📍 第 ${stepNumber} 步</div>
                    ${notice}
                    ${quiz?.meta?.knowledge_bailout ? renderKnowledgeBailoutCard(quiz?.meta?.knowledge_card) : ''}
                    ${renderQuizCard(quiz, reviewId)}
                </div>
            `;
        }
        // 已完成的步骤折叠显示
        return renderCollapsedQuizStep(quiz, index);
    }).join('');

    return `
        <div class="learning-path-timeline">
            ${html}
            ${renderQuizTimelineStatus(item, reviewId, reviewFamily)}
        </div>
    `;
}

// 折叠的已完成题目
function renderCollapsedQuizStep(quiz, index) {
    if (!quiz) return '';
    const stepNumber = index + 1;
    const isCorrect = quiz.latest_is_correct;
    const resultIcon = isCorrect ? '✅' : '❌';
    const resultText = isCorrect ? '答对了' : '未通过';
    const level = quiz?.meta?.difficulty_level || quiz?.difficulty_level || '';
    const levelText = level === 'followup' ? '拆小' : level === 'confirm' ? '确认' : level === 'final_micro_confirm' ? '最终' : level === 'knowledge_confirm' ? '知识卡后' : '理解';
    
    return `
        <div class="timeline-step completed" onclick="this.classList.toggle('expanded'); this.querySelector('.collapsed-content').style.display = this.classList.contains('expanded') ? 'block' : 'none';" style="cursor: pointer;">
            <div class="step-badge completed">${resultIcon} 第 ${stepNumber} 步 · ${levelText}</div>
            <div class="quiz-history-step-collapsed">
                <span style="font-size: 13px; color: var(--text-secondary);">${escapeHtml(quiz.question_text?.substring(0, 40) || '...')}...</span>
                <span class="quiz-history-step-result ${isCorrect ? 'correct' : 'incorrect'}">${resultText}</span>
            </div>
            <div class="collapsed-content" style="display: none; margin-top: 12px;">
                <div style="opacity: 0.8;">
                    ${renderQuizCard(quiz, 0)}
                </div>
            </div>
        </div>
    `;
}

function renderQuizStageNotice({ title, explanation = '', tone = 'warn', kicker = '继续拆这一步' }) {
    return `
        <div class="quiz-stage-note ${escapeHtml(tone)}">
            <div class="quiz-stage-kicker">${escapeHtml(kicker)}</div>
            <div class="quiz-stage-title">${escapeHtml(title)}</div>
            ${explanation ? `<div class="quiz-stage-copy">${renderRichTextBlock(explanation)}</div>` : ''}
        </div>
    `;
}

function renderSelfCheckCard(reviewId, family = 'failure_diagnosis') {
    const copy = reviewFamilyUi.reviewFeedbackCopy(family);
    return `
        <div class="self-check-card-v2">
            <div class="self-check-title-v2">${escapeHtml(copy.title)}</div>
            <div class="self-check-options-v2">
                <div class="self-check-option-v2 tone-clear" onclick="submitSelfCheck(${Number(reviewId)}, 'clear')">
                    <div class="self-check-option-icon">✅</div>
                    <div class="self-check-option-text">${escapeHtml(copy.clearLabel)}</div>
                </div>
                <div class="self-check-option-v2 tone-guessed" onclick="submitSelfCheck(${Number(reviewId)}, 'guessed')">
                    <div class="self-check-option-icon">🤔</div>
                    <div class="self-check-option-text">${escapeHtml(copy.guessedLabel)}</div>
                </div>
                <div class="self-check-option-v2 tone-confused" onclick="submitSelfCheck(${Number(reviewId)}, 'confused')">
                    <div class="self-check-option-icon">😵</div>
                    <div class="self-check-option-text">${escapeHtml(copy.confusedLabel)}</div>
                </div>
            </div>
        </div>
    `;
}

function renderRemedyButtons(reviewId, errorLayer, options = {}) {
    const dynamicLabel = options.dynamicLabel || dynamicRemedyLabel(errorLayer);
    const includeResolve = options.includeResolve === true;
    return `
        <div class="quiz-card-v2" style="background: linear-gradient(135deg, rgba(255,149,0,0.05) 0%, rgba(255,204,0,0.05) 100%); border: 1px solid rgba(255,149,0,0.2);">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px; font-weight: 600;">
                <span>🔄</span> 这一步还没完全打通
            </div>
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">
                我们换一种方式继续带你一下：
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                ${includeResolve ? `<button class="secondary" style="justify-content: flex-start; padding: 12px 16px; border-radius: 12px;" onclick="resolveRemedy(${Number(reviewId)}, 'resolved')">✅ 我懂了，继续下一题</button>` : ''}
                <button class="secondary" style="justify-content: flex-start; padding: 12px 16px; border-radius: 12px;" onclick="triggerRemedy(${Number(reviewId)}, 'rephrase')">📝 再换一种说法讲这一步</button>
                <button class="secondary" style="justify-content: flex-start; padding: 12px 16px; border-radius: 12px;" onclick="triggerRemedy(${Number(reviewId)}, 'smaller_example')">🔍 给我一个更小的例子</button>
                <button class="secondary" style="justify-content: flex-start; padding: 12px 16px; border-radius: 12px;" onclick="triggerRemedy(${Number(reviewId)}, 'easier_quiz')">🎯 再出一道更简单的小题</button>
                <button class="secondary" style="justify-content: flex-start; padding: 12px 16px; border-radius: 12px;" onclick="triggerRemedy(${Number(reviewId)}, 'dynamic_bridge_help')">💡 ${escapeHtml(dynamicLabel)}</button>
            </div>
        </div>
    `;
}

function renderLearningSection(item) {
    const reviewId = item.review_id;
    if (!reviewId || item.review_status !== 'completed') return '';
    
    const sectionId = `review-quiz-${reviewId}`;
    
    // 使用新的 Tailwind UI（如果可用）
    if (typeof window.TwUI !== 'undefined') {
        try {
            const twContent = window.TwUI.renderLearningSection(item);
            return `<div id="${sectionId}" class="review-learning-section">${twContent}</div>`;
        } catch (e) {
            console.warn('Tailwind UI 渲染失败，回退到默认 UI:', e);
        }
    }
    
    // 降级到原有 UI
    const reviewFamily = reviewFamilyUi.resolveReviewFamily(item);
    let content = '';

    if (item.review_learning_status === 'self_check_required') {
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
    } else if (item.review_learning_status === 'knowledge_bailout') {
        content = renderReviewDetailQuizTimeline(item);
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
            <div class="quiz-card">
                <div class="quiz-title">复盘看完后，再来一道小题确认你是不是真的懂了</div>
                <div class="quiz-actions">
                    <button class="secondary" onclick="startReviewQuiz(${Number(reviewId)})">试试看你是不是已经懂这一步了</button>
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
            submission_result: submissionResult,
            bottleneck_text: bottleneckText,
            problem_context: problemContext,
            reflection: reflection || '',
            student_code: studentCode || '',
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
            review_problem_focus: data.review?.problem_focus || data.review?.main_block || '',
            review_main_block: data.review?.main_block || '',
            review_key_bridge: data.review?.key_bridge || '',
            review_visual_hint: data.review?.visual_hint || '',
            review_guided_walkthrough: data.review?.guided_walkthrough || '',
            review_try_now: data.review?.try_now || data.review?.next_step || '',
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
        activeCheckinStage = checkinReviewUi.REVIEW_STAGE;
        
        // Show review detail view instead of form
        showCheckinReviewDetail(draftItem);
        
        // Start polling for review updates
        if (data.review_status === 'pending') {
            startCheckinReviewStream(activeCheckinId);
        }

        // Show AI response in chat interface
        removeCheckinLoadingMessage();
        
        if (data.review_status === 'pending') {
            addCheckinAIResponse(`
                <p>✅ ${escapeHtml(data.message)}</p>
                <p style="margin-top: 8px; color: var(--text-secondary);">复盘正在生成中，请稍候...</p>
            `);
        } else {
            // Build review response
            const review = data.review || {};
            let responseHtml = `<p>✅ ${escapeHtml(data.message)}</p>`;
            
            if (review.problem_focus || review.main_block || review.diagnosis) {
                responseHtml += `<div class="checkin-ai-response" style="margin-top: 16px;">`;
                
                if (review.problem_focus || review.main_block) {
                    responseHtml += `
                        <div class="checkin-ai-section">
                            <div class="checkin-ai-section-title">你卡在哪</div>
                            <div class="checkin-ai-section-content">${escapeHtml(review.problem_focus || review.main_block)}</div>
                        </div>
                    `;
                }
                
                if (review.key_bridge) {
                    responseHtml += `
                        <div class="checkin-ai-section">
                            <div class="checkin-ai-section-title">先抓住什么</div>
                            <div class="checkin-ai-section-content">${escapeHtml(review.key_bridge)}</div>
                        </div>
                    `;
                }

                if (review.visual_hint) {
                    responseHtml += `
                        <div class="checkin-ai-section">
                            <div class="checkin-ai-section-title">${escapeHtml(reviewFamilyUi.reviewFieldLabel('visual_hint', review.visual_hint))}</div>
                            <pre class="review-visual-hint">${escapeHtml(review.visual_hint)}</pre>
                        </div>
                    `;
                }

                if (review.guided_walkthrough) {
                    responseHtml += `
                        <div class="checkin-ai-section">
                            <div class="checkin-ai-section-title">跟我走一遍</div>
                            ${renderRichTextBlock(review.guided_walkthrough, 'review-inline-rich-block')}
                        </div>
                    `;
                }
                
                if (review.try_now || review.next_step) {
                    responseHtml += `
                        <div class="checkin-ai-section">
                            <div class="checkin-ai-section-title">现在你来试</div>
                            <div class="checkin-ai-section-content">${escapeHtml(review.try_now || review.next_step)}</div>
                        </div>
                    `;
                }
                
                responseHtml += `</div>`;
            }
            
            addCheckinAIResponse(responseHtml);
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
        removeCheckinLoadingMessage();
        addCheckinAIResponse(`
            <div class="alert alert-error">
                <strong>提交失败</strong>
                <p style="margin-top: 4px;">${escapeHtml(err.message)}</p>
            </div>
        `);
        if (resultEl) {
            resultEl.classList.remove('hidden');
            resultEl.textContent = '错误: ' + err.message;
        }
    } finally {
        isSubmittingCheckin = false;
        const submitBtnIcon = document.querySelector('#submit-checkin-btn');
        if (submitBtnIcon) {
            submitBtnIcon.disabled = true;
        }
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
            const masteryBadge = masteryStatusTeacherBadge(item.review_mastery_status);
            reviewBlock += `
                <p class="archive-line"><strong>判断把握：</strong>${escapeHtml(confidenceText(item.review_confidence))}</p>
                <div class="archive-chip-row">${aiTags}</div>
                ${item.review_core_design_subtags?.length ? `<div class="archive-chip-row">${aiSubtags}</div>` : ''}
                <div class="archive-line">${renderRichTextInline(item.review_diagnosis || '')}</div>
                <div class="archive-line"><strong>下一步行动：</strong>${renderRichTextInline(item.review_next_action || '')}</div>
                ${item.teacher_repeat_bridge_hint ? `<div class="archive-chip-row"><span class="tag-pill teacher-repeat-chip">近期重复出现</span></div><p class="archive-note teacher-repeat-note"><strong>重复提示：</strong>${escapeHtml(item.teacher_repeat_bridge_hint)}</p>` : ''}
                ${item.review_understanding_self_check ? `<p class="archive-line"><strong>学生自评：</strong>${escapeHtml(selfCheckLabel(item.review_understanding_self_check))}</p>` : ''}
                ${item.review_bridge_path ? `<p class="archive-line"><strong>过桥路径：</strong>${escapeHtml(bridgePathDisplayText(item.review_bridge_path))}</p>` : ''}
                ${masteryBadge ? `<div class="archive-chip-row"><span class="tag-pill ${escapeHtml(masteryBadge.className)}">${escapeHtml(masteryBadge.label)}</span></div>` : ''}
                ${bridgeBadge ? `<div class="archive-chip-row"><span class="tag-pill ${escapeHtml(bridgeBadge.className)}">${escapeHtml(bridgeBadge.label)}</span></div>` : ''}
                ${item.review_bridge_path ? `<p class="archive-note"><strong>老师解读：</strong>${escapeHtml(bridgePathTeacherNote(item.review_bridge_path))}</p>` : ''}
                ${renderReviewQualityFlags(item.review_quality_flags)}
                <div class="archive-note"><strong>推荐专题：</strong>${renderRichTextInline(item.review_suggested_topic || '')}</div>
            `;
        } else {
            const reviewFamily = reviewFamilyUi.resolveReviewFamily(item);
            const orderedSections = reviewFamilyUi.orderedReviewSections({
                problem_focus: item.review_problem_focus || item.review_main_block || '',
                main_block: item.review_main_block || '',
                key_bridge: item.review_key_bridge || '',
                visual_hint: item.review_visual_hint || '',
                guided_walkthrough: item.review_guided_walkthrough || '',
                try_now: item.review_try_now || item.review_next_step || '',
                next_step: item.review_next_step || '',
                transfer_signal: item.review_transfer_signal || '',
            }, reviewFamily);
            reviewBlock += `
                ${orderedSections
                    .filter((section) => String(section.value || '').trim())
                    .map((section) => `
                    <div class="${section.field === 'transfer_signal' ? 'archive-note' : 'archive-line'}"><strong>${escapeHtml(section.label)}：</strong>${section.field === 'visual_hint' ? `<pre class="review-visual-hint history-visual-hint">${escapeHtml(section.value || '')}</pre>` : renderRichTextInline(section.value || '')}</div>
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

// Motivational quotes
const motivationalQuotes = [
    "算法是编程的灵魂，坚持打卡，每天进步一点点！",
    "每一个 AC 的背后，都是无数次 WA 的积累。",
    "不要害怕犯错，每一次错误都是成长的机会。",
    "代码如诗，算法如画，编程是一场美的修行。",
    "今天的努力，是明天 AC 的基石。",
    "复杂问题简单化，简单问题极致化。",
    "调试是一门艺术，耐心是最好的工具。",
    "思路清晰，代码自然流畅。",
    "没有过不去的题，只有想不通的点。",
    "坚持就是胜利，打卡成就未来！",
    "每一行代码，都是通往梦想的阶梯。",
    "思考比编码更重要，理解比记忆更持久。",
];

function updateMotivationalQuote() {
    const quoteEl = document.getElementById('motivational-quote');
    if (quoteEl) {
        const randomQuote = motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)];
        quoteEl.textContent = `"${randomQuote}"`;
    }
}

async function loadCheckinStats() {
    // Update quote
    updateMotivationalQuote();
    
    // Update user's checkin count from cache
    const userCountEl = document.getElementById('user-checkin-count');
    if (userCountEl) {
        userCountEl.textContent = myCheckinsCache.length;
    }
    
    // Calculate streak
    const streakEl = document.getElementById('user-streak');
    if (streakEl && myCheckinsCache.length > 0) {
        const dates = [...new Set(myCheckinsCache.map(item => {
            const date = new Date(item.created_at);
            return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
        }))];
        
        let streak = 0;
        const today = new Date();
        for (let i = 0; i < 365; i++) {
            const checkDate = new Date(today);
            checkDate.setDate(checkDate.getDate() - i);
            const dateStr = `${checkDate.getFullYear()}-${checkDate.getMonth()}-${checkDate.getDate()}`;
            if (dates.includes(dateStr)) {
                streak++;
            } else if (i > 0) {
                break;
            }
        }
        
        streakEl.innerHTML = streak > 0 ? `${streak} <span style="font-size:14px;">天</span>` : '🔥';
    }
    
    // Try to fetch global stats
    try {
        const res = await apiFetch(`${API_BASE}/api/stats/global`, { method: 'GET' });
        if (res.ok) {
            const data = await res.json();
            const globalEl = document.getElementById('global-checkin-count');
            if (globalEl && data.total_checkins) {
                globalEl.textContent = data.total_checkins.toLocaleString();
            }
        }
    } catch (err) {
        // Silent fail, show placeholder
        const globalEl = document.getElementById('global-checkin-count');
        if (globalEl) globalEl.textContent = '---';
    }
}

async function loadMyCheckins(preferredCheckinId = null) {
    const listEl = document.getElementById('checkin-history-list');
    if (listEl) {
        listEl.innerHTML = `
            <div class="history-loading">
                <div class="ai-loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span>加载中...</span>
            </div>
        `;
    }

    try {
        const res = await apiFetch(`${API_BASE}/api/checkins/me?limit=50`);
        const data = await res.json();
        myCheckinsCache = data.checkins || [];
        if (!myCheckinsCache.length) {
            activeCheckinId = null;
            activeCheckinStage = checkinReviewUi.INPUT_STAGE;
            setReviewStageEmpty();
            if (listEl) {
                listEl.innerHTML = `
                    <div class="history-empty">
                        <div class="history-empty-icon">📝</div>
                        <div class="history-empty-text">还没有打卡记录</div>
                        <div style="margin-top: 16px;">
                            <button onclick="showStudentTab('checkin-tab')">去打卡</button>
                        </div>
                    </div>
                `;
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
        if (activeCheckinStage === checkinReviewUi.REVIEW_STAGE && activeItem) {
            renderActiveCheckinWorkspace(activeItem);
        } else {
            renderCheckinEntryStage();
        }
    } catch (err) {
        if (listEl) {
            listEl.innerHTML = `
                <div class="alert alert-error" style="text-align: center; padding: 32px;">
                    <div style="font-size: 32px; margin-bottom: 12px;">⚠️</div>
                    <div>加载失败</div>
                    <div style="font-size: 12px; margin-top: 8px; opacity: 0.8;">${escapeHtml(err.message)}</div>
                    <button onclick="loadMyCheckins()" style="margin-top: 16px;">重试</button>
                </div>
            `;
        }
    }
}

async function startReviewQuiz(reviewId) {
    // First ensure we're in the review detail view
    const detailContainer = document.getElementById('review-stage-content');
    const checkinId = itemCheckinIdFromReview(reviewId);
    
    // If in detail view, update the quiz section
    if (detailContainer && !detailContainer.classList.contains('hidden') && checkinId) {
        const item = myCheckinsCache.find(c => Number(c.id) === Number(checkinId));
        if (item) {
            showCheckinReviewDetail(item);
        }
    }
    
    const container = document.getElementById(`review-quiz-${reviewId}`) || document.getElementById('review-detail-quiz');
    if (container) container.innerHTML = '<div class="quiz-card"><div class="quiz-title">正在生成理解小测...</div></div>';

    try {
        const res = await apiFetch(`${API_BASE}/api/reviews/${reviewId}/quiz/generate`, {
            method: 'POST',
            body: JSON.stringify({}),
        });
        const data = await res.json();
        if (container) {
            container.innerHTML = renderQuizCard(data.quiz, reviewId);
        }
        await refreshReviewDetailByReviewId(reviewId);
    } catch (err) {
        if (container && err.message === '请先完成这一步的理解确认') {
            const checkinId = itemCheckinIdFromReview(reviewId);
            const checkinItem = checkinId ? await fetchMyCheckinById(checkinId) : null;
            container.innerHTML = `
                ${renderQuizFeedbackBlock({
                    title: checkinItem?.quiz_latest_feedback || '答对了，这一步你跨过去了。',
                    bridgeFeedback: checkinItem?.quiz_bridge_feedback,
                    explanation: checkinItem?.quiz_explanation,
                    tone: 'success',
                })}
                ${renderSelfCheckCard(reviewId)}
            `;
            loadMyCheckins();
            return;
        }
        if (container) {
            container.innerHTML = `<div class="quiz-card quiz-result final"><div class="quiz-title" style="color:#c0392b">生成失败：${escapeHtml(err.message)}</div></div>`;
        }
    }
}

async function submitQuizAnswer(quizId, reviewId) {
    const textInput = document.getElementById(`quiz-answer-${reviewId}`);
    let answerText = textInput ? textInput.value.trim() : '';
    if (!answerText) {
        // 尝试新的隐藏字段方式
        const hiddenInput = document.getElementById(`quiz-selected-${reviewId}`);
        answerText = hiddenInput ? hiddenInput.value.trim() : '';
    }
    if (!answerText) {
        // 兼容旧的 radio 方式
        const checked = document.querySelector(`input[name="quiz-option-${reviewId}"]:checked`);
        answerText = checked ? checked.value : '';
    }
    if (!answerText) {
        alert('请先选择或填写答案');
        return;
    }

    // Support both history list view and detail view containers
    const container = document.getElementById(`review-quiz-${reviewId}`) || document.getElementById('review-detail-quiz');
    if (container) container.innerHTML = '<div class="quiz-card"><div class="quiz-title">正在检查你的答案...</div></div>';

    try {
        const res = await apiFetch(`${API_BASE}/api/quizzes/${quizId}/answer`, {
            method: 'POST',
            body: JSON.stringify({ answer_text: answerText }),
        });
        const data = await res.json();

        if (data.next_state === 'self_check_required') {
            container.innerHTML = `
                ${renderQuizFeedbackBlock({
                    title: data.feedback_text,
                    bridgeFeedback: data.bridge_feedback,
                    explanation: data.explanation || '',
                    tone: 'success',
                })}
                ${renderSelfCheckCard(reviewId)}
            `;
            await refreshReviewDetailByReviewId(reviewId);
        } else if (data.next_state === 'resolved') {
            container.innerHTML = renderQuizFeedbackBlock({
                title: data.feedback_text,
                bridgeFeedback: data.bridge_feedback,
                explanation: data.explanation || '',
                tone: 'success',
            });
            await refreshReviewDetailByReviewId(reviewId);
        } else if (data.next_state === 'followup_quiz') {
            await refreshReviewDetailByReviewId(reviewId);
        } else if (data.next_state === 'knowledge_bailout') {
            await refreshReviewDetailByReviewId(reviewId);
        } else if (data.next_state === 'remedy_available') {
            const checkinItem = await refreshReviewDetailByReviewId(reviewId);
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
            await refreshReviewDetailByReviewId(reviewId);
        } else {
            container.innerHTML = renderQuizFeedbackBlock({
                title: data.feedback_text,
                bridgeFeedback: data.bridge_feedback,
                explanation: data.explanation || '',
                tone: 'final',
            });
            await refreshReviewDetailByReviewId(reviewId);
        }
    } catch (err) {
        if (container) {
            container.innerHTML = `<div class="quiz-card quiz-result final"><div class="quiz-title" style="color:#c0392b">提交失败：${escapeHtml(err.message)}</div></div>`;
        }
    }
}

async function submitSelfCheck(reviewId, status) {
    // Support both history list view and detail view containers
    const container = document.getElementById(`review-quiz-${reviewId}`) || document.getElementById('review-detail-quiz');
    if (container) container.innerHTML = '<div class="quiz-card"><div class="quiz-title">正在记录你的理解状态...</div></div>';
    const checkinId = itemCheckinIdFromReview(reviewId);

    try {
        const res = await apiFetch(`${API_BASE}/api/reviews/${reviewId}/self-check`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        });
        const data = await res.json();

        if (data.next_state === 'resolved') {
            container.innerHTML = `
                <div class="quiz-card quiz-result success">
                    <div class="quiz-title">${escapeHtml(data.feedback_text || '答对了，这一步你跨过去了。')}</div>
                </div>
            `;
        } else if (data.next_state === 'confirm_quiz') {
            await refreshReviewDetailByReviewId(reviewId);
        } else if (data.next_state === 'remedy_available') {
            const checkinItem = await refreshReviewDetailByReviewId(reviewId);
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
        await refreshReviewDetailByReviewId(reviewId);
    } catch (err) {
        if (container) {
            container.innerHTML = `<div class="quiz-card quiz-result final"><div class="quiz-title" style="color:#c0392b">提交失败：${escapeHtml(err.message)}</div></div>`;
        }
    }
}

function itemCheckinIdFromReview(reviewId) {
    const item = myCheckinsCache.find((candidate) => Number(candidate.review_id) === Number(reviewId));
    return item ? Number(item.id) : null;
}

async function triggerRemedy(reviewId, actionType) {
    // Support both history list view and detail view containers
    const container = document.getElementById(`review-quiz-${reviewId}`) || document.getElementById('review-detail-quiz');
    if (container) container.innerHTML = '<div class="quiz-card"><div class="quiz-title">正在换一种方式帮你拆这一步...</div></div>';

    try {
        const res = await apiFetch(`${API_BASE}/api/reviews/${reviewId}/remedy`, {
            method: 'POST',
            body: JSON.stringify({ action_type: actionType }),
        });
        const data = await res.json();
        if (data.mode === 'quiz') {
            await refreshReviewDetailByReviewId(reviewId);
        } else if (data.mode === 'final') {
            container.innerHTML = `
                <div class="quiz-card quiz-result final">
                    <div class="quiz-title">${escapeHtml(data.feedback_text)}</div>
                </div>
            `;
            await refreshReviewDetailByReviewId(reviewId);
        } else {
            const checkinItem = await refreshReviewDetailByReviewId(reviewId);
            const errorLayer = checkinItem?.review_error_layer || 'insufficient';
            container.innerHTML = `
                <div class="quiz-card quiz-result info">
                    <div class="quiz-title">我们只讲这一步</div>
                    <div class="quiz-explanation">${escapeHtml(data.remedy_text || '')}</div>
                    ${data.visual_hint ? `<pre class="review-visual-hint remedy-visual-hint">${escapeHtml(data.visual_hint)}</pre>` : ''}
                    <div class="quiz-explanation"><strong>你现在先做：</strong>${escapeHtml(data.micro_action || '')}</div>
                    ${renderRemedyButtons(reviewId, errorLayer, {
                        includeResolve: true,
                        includeResolveLabel: '我来试最后一题',
                    })}
                </div>
            `;
            await refreshReviewDetailByReviewId(reviewId);
        }
    } catch (err) {
        if (container) {
            container.innerHTML = `<div class="quiz-card quiz-result final"><div class="quiz-title" style="color:#c0392b">补救失败：${escapeHtml(err.message)}</div></div>`;
        }
    }
}

async function resolveRemedy(reviewId, status) {
    // Support both history list view and detail view containers
    const container = document.getElementById(`review-quiz-${reviewId}`) || document.getElementById('review-detail-quiz');
    try {
        const res = await apiFetch(`${API_BASE}/api/reviews/${reviewId}/remedy/resolve`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        });
        const data = await res.json();
        if (container) {
            if (data.next_state === 'final_micro_confirm') {
                await refreshReviewDetailByReviewId(reviewId);
            } else {
                container.innerHTML = status === 'resolved'
                    ? `<div class="quiz-card quiz-result success"><div class="quiz-title">${escapeHtml(data.feedback_text || '答对了，这一步你跨过去了。')}</div></div>`
                    : `<div class="quiz-card quiz-result final"><div class="quiz-title">这道题我们先停在这里，你的老师会来和你一起看一看。</div></div>`;
            }
        }
        await refreshReviewDetailByReviewId(reviewId);
    } catch (err) {
        if (container) {
            container.innerHTML = `<div class="quiz-card quiz-result final"><div class="quiz-title" style="color:#c0392b">提交失败：${escapeHtml(err.message)}</div></div>`;
        }
    }
}

window.startReviewQuiz = startReviewQuiz;
window.submitQuizAnswer = submitQuizAnswer;
window.submitSelfCheck = submitSelfCheck;
window.triggerRemedy = triggerRemedy;
window.resolveRemedy = resolveRemedy;
window.selectCheckin = selectCheckin;
window.showCheckinForm = showCheckinForm;

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

        const masteryStatusHtml = renderMasteryStatusCard(data.mastery_status_stats || {});
        const bridgePathStatsHtml = renderBridgePathStatsCard(data.bridge_path_stats || {});
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
            + masteryStatusHtml
            + bridgePathStatsHtml
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
    renderMasteryStatusCard,
    renderBridgePathStatsCard,
    renderQuizCard,
    renderReviewDetailQuizTimeline,
    renderQuizStageNotice,
};

if (typeof window !== 'undefined') {
    window.noiAppTestHooks = Object.assign(window.noiAppTestHooks || {}, noiAppTestHooks);
}
