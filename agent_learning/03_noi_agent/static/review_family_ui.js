const globalContext = typeof window !== 'undefined' ? window : globalThis;
    const FAILURE_FAMILY = 'failure_diagnosis';
    const SUCCESS_FAMILY = 'success_reflection';

    function reviewFamilyFromMode(mode) {
        return mode === 'independent_reflect' ? SUCCESS_FAMILY : FAILURE_FAMILY;
    }

    function resolveReviewFamily(source = {}) {
        if (source.review_family) return source.review_family;
        if (source.family) return source.family;
        const mode = source.review_mode || source.mode || '';
        return reviewFamilyFromMode(mode);
    }

    function reviewFieldOrder(family) {
        return ['problem_focus', 'key_bridge', 'visual_hint', 'guided_walkthrough', 'try_now', 'transfer_signal'];
    }

    function isVisualHintDiagramLike(value) {
        const text = String(value || '').trim();
        if (!text) return false;
        const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean);
        if (lines.length < 2) return false;
        const structuredLineCount = lines.filter((line) => /[:：=→←↔|├└┌┐┘─\-×]/.test(line)).length;
        const compactLineCount = lines.filter((line) => line.length <= 30).length;
        return structuredLineCount >= 2 || (structuredLineCount >= 1 && compactLineCount >= 2 && lines.length >= 3);
    }

    function reviewFieldLabel(field, value = '') {
        if (field === 'visual_hint') {
            return isVisualHintDiagramLike(value) ? '看图想一想' : '先看这个对比';
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
    }

    function orderedReviewSections(review = {}, family) {
        return reviewFieldOrder(family).map((field) => {
            const value = review[field]
                || (field === 'problem_focus' ? review.main_block : '')
                || (field === 'try_now' ? review.next_step : '')
                || '';
            return {
            field,
                label: reviewFieldLabel(field, value),
                value,
            };
        });
    }

    function reviewFeedbackCopy(family) {
        if (family === SUCCESS_FAMILY) {
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
    }

    function feedbackEventFields(family, status) {
        const normalizedStatus = String(status || '').trim().toLowerCase();
        const studentFeedback = normalizedStatus === 'clear'
            ? 'understood'
            : normalizedStatus === 'guessed'
                ? 'neutral'
                : 'confused';
        let badReason = 'none';
        if (studentFeedback === 'confused') {
            badReason = family === SUCCESS_FAMILY ? 'still_cant_apply' : 'no_next_step';
        }
        return {
            student_feedback: studentFeedback,
            bad_reason: badReason,
            followup_clicked: false,
            followup_question_count: 0,
        };
    }

    function reviewWorkspaceSubtitle(item = {}) {
        if (item.review_status === 'failed') {
            return '这条打卡的复盘生成失败了，你可以在右侧直接重新生成。';
        }
        if (item.poll_timed_out) {
            return '这条打卡的复盘生成时间较长，你可以先刷新或稍后回来查看。';
        }
        if (item.review_status !== 'completed') {
            return '这条打卡的复盘还在生成，生成完成后会自动更新到这里。';
        }
        const family = resolveReviewFamily(item);
        if (family === SUCCESS_FAMILY) {
            return '右侧先看为什么这道题这样做对，再用中间的小测确认你能不能把这条思路说清楚。';
        }
        return '右侧先看问题定位和最小下一步，再用中间的小测确认你知不知道该先查哪一步。';
    }

    const api = {
        FAILURE_FAMILY,
        SUCCESS_FAMILY,
        orderedReviewSections,
        resolveReviewFamily,
        feedbackEventFields,
        isVisualHintDiagramLike,
        reviewFamilyFromMode,
        reviewFeedbackCopy,
        reviewFieldLabel,
        reviewFieldOrder,
        reviewWorkspaceSubtitle,
    };

if (typeof window !== 'undefined') {
    globalContext.reviewFamilyUi = api;
}

export default api;
