(function (global) {
    const reviewFamilyUi = global.reviewFamilyUi || {
        resolveReviewFamily(source = {}) {
            if (source.review_family) return source.review_family;
            if (source.review_mode === 'independent_reflect') return 'success_reflection';
            return 'failure_diagnosis';
        },
        reviewFieldOrder(family) {
            if (family === 'success_reflection') {
                return ['main_block', 'key_bridge', 'transfer_signal', 'next_step'];
            }
            return ['main_block', 'key_bridge', 'next_step', 'transfer_signal'];
        },
        reviewFieldLabel(field) {
            const labels = {
                main_block: '你卡在哪',
                key_bridge: '关键一步',
                next_step: '现在先做',
                transfer_signal: '下次提醒',
            };
            return labels[field] || field;
        },
    };

    const FIELD_CONFIG = {
        mode_correct: {
            label: 'mode_correct',
            options: [
                { value: 'correct', label: 'correct / 正确' },
                { value: 'incorrect', label: 'incorrect / 错误' },
                { value: 'unsure', label: 'unsure / 不确定' },
            ],
            defaultValue: 'unsure',
        },
        review_grounded: {
            label: 'review_grounded',
            options: [
                { value: 'grounded', label: 'grounded / 贴题' },
                { value: 'mixed', label: 'mixed / 一般' },
                { value: 'vague', label: 'vague / 空泛' },
            ],
            defaultValue: 'mixed',
        },
        student_can_move_next: {
            label: 'student_can_move_next',
            options: [
                { value: 'yes', label: 'yes / 能继续' },
                { value: 'no', label: 'no / 不能继续' },
                { value: 'unsure', label: 'unsure / 不确定' },
            ],
            defaultValue: 'unsure',
        },
    };

    function escapeHtml(value) {
        if (value === null || value === undefined) return '';
        const div = global.document ? global.document.createElement('div') : null;
        if (div) {
            div.textContent = String(value);
            return div.innerHTML;
        }
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function getFieldConfig(field) {
        return FIELD_CONFIG[field] || FIELD_CONFIG.mode_correct;
    }

    function normalizeFieldValue(field, value) {
        const config = getFieldConfig(field);
        const candidate = String(value || '').trim();
        return config.options.some((option) => option.value === candidate)
            ? candidate
            : config.defaultValue;
    }

    function manualReviewSelectOptions(field, value) {
        const config = getFieldConfig(field);
        const selectedValue = normalizeFieldValue(field, value);
        return config.options.map((option) => `
            <option value="${escapeHtml(option.value)}"${option.value === selectedValue ? ' selected' : ''}>${escapeHtml(option.label)}</option>
        `).join('');
    }

    function manualReviewMeta(sample = {}) {
        const pieces = [
            sample.review_mode ? `mode: ${sample.review_mode}` : '',
            sample.review_family ? `family: ${sample.review_family}` : '',
            sample.review_status ? `status: ${sample.review_status}` : '',
        ].filter(Boolean);
        return pieces.join(' | ');
    }

    function renderReviewBlock(title, value) {
        return `
            <div class="teacher-review-block">
                <div class="teacher-review-block-label">${escapeHtml(title)}</div>
                <div class="teacher-review-block-body">${escapeHtml(value || '（空）')}</div>
            </div>
        `;
    }

    function renderOrderedReviewBlocks(sample = {}) {
        const family = reviewFamilyUi.resolveReviewFamily(sample);
        return reviewFamilyUi.reviewFieldOrder(family).map((field) =>
            renderReviewBlock(reviewFamilyUi.reviewFieldLabel(field), sample[field]),
        ).join('');
    }

    function renderManualReviewForm(sample) {
        const manual = sample.manual_review || {};
        return `
            <form class="teacher-manual-review-form" data-review-id="${escapeHtml(sample.review_id)}">
                <div class="form-group">
                    <label>${escapeHtml(FIELD_CONFIG.mode_correct.label)}</label>
                    <select name="mode_correct">
                        ${manualReviewSelectOptions('mode_correct', manual.mode_correct)}
                    </select>
                </div>
                <div class="form-group">
                    <label>${escapeHtml(FIELD_CONFIG.review_grounded.label)}</label>
                    <select name="review_grounded">
                        ${manualReviewSelectOptions('review_grounded', manual.review_grounded)}
                    </select>
                </div>
                <div class="form-group">
                    <label>${escapeHtml(FIELD_CONFIG.student_can_move_next.label)}</label>
                    <select name="student_can_move_next">
                        ${manualReviewSelectOptions('student_can_move_next', manual.student_can_move_next)}
                    </select>
                </div>
                <div class="form-group">
                    <label>notes</label>
                    <textarea name="notes" rows="4" placeholder="补一句最关键的原因即可">${escapeHtml(manual.notes || '')}</textarea>
                </div>
                <button type="submit" class="primary">提交复核</button>
                <div class="teacher-manual-review-status" data-role="status">
                    ${manual?.updated_at ? `已保存于 ${escapeHtml(manual.updated_at)}` : '尚未提交人工复核'}
                </div>
            </form>
        `;
    }

    function renderTeacherReviewSampleCard(sample) {
        const manual = sample.manual_review || {};
        return `
            <article class="teacher-review-sample-card" data-review-id="${escapeHtml(sample.review_id)}">
                <div class="teacher-review-sample-head">
                    <div>
                        <h4>${escapeHtml(sample.problem_title || '未命名题目')}</h4>
                        <p class="teacher-review-meta">${escapeHtml(manualReviewMeta(sample) || '暂无状态')}</p>
                    </div>
                    <div class="teacher-review-pill-row">
                        <span class="status-pill">review_id ${escapeHtml(sample.review_id)}</span>
                        <span class="status-pill">checkin_id ${escapeHtml(sample.checkin_id)}</span>
                        <span class="status-pill">${escapeHtml(sample.student_id || 'unknown')}</span>
                    </div>
                </div>

                <div class="teacher-review-sample-submeta">
                    <span class="status-pill">${escapeHtml(sample.oj_source || 'unknown')}</span>
                    <span class="status-pill">${escapeHtml(sample.completion_status || 'unknown')}</span>
                    <span class="status-pill">${escapeHtml(sample.review_mode || 'unknown')}</span>
                    <span class="status-pill">${escapeHtml(sample.review_family || 'unknown')}</span>
                    <span class="status-pill">${escapeHtml(sample.review_created_at || '')}</span>
                </div>

                <div class="teacher-review-grid">
                    ${renderOrderedReviewBlocks(sample)}
                </div>

                <div class="teacher-review-text-group">
                    <div class="teacher-review-text-card">
                        <h5>卡点描述</h5>
                        <p>${escapeHtml(sample.bottleneck_text || '（空）')}</p>
                    </div>
                    <details class="teacher-review-context-details teacher-review-text-card">
                        <summary>题面摘要</summary>
                        <p>${escapeHtml(sample.problem_context || '（空）')}</p>
                    </details>
                </div>

                <div class="teacher-review-form-wrap">
                    ${renderManualReviewForm(sample)}
                </div>
            </article>
        `;
    }

    function renderTeacherReviewSamplesPanel(samples = []) {
        if (!samples.length) {
            return '<p class="teacher-review-empty">暂无可复核的 review 样本</p>';
        }
        return samples.map(renderTeacherReviewSampleCard).join('');
    }

    function buildTeacherManualReviewPayload(form) {
        return {
            mode_correct: normalizeFieldValue('mode_correct', form.elements.mode_correct.value),
            review_grounded: normalizeFieldValue('review_grounded', form.elements.review_grounded.value),
            student_can_move_next: normalizeFieldValue('student_can_move_next', form.elements.student_can_move_next.value),
            notes: String(form.elements.notes.value || '').trim(),
        };
    }

    const api = {
        buildTeacherManualReviewPayload,
        manualReviewSelectOptions,
        renderTeacherReviewSampleCard,
        renderTeacherReviewSamplesPanel,
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
    global.teacherManualReviewUi = api;
})(typeof window !== 'undefined' ? window : globalThis);
