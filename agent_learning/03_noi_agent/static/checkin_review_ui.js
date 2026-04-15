const globalContext = typeof window !== 'undefined' ? window : globalThis;
    const INPUT_STAGE = 'input';
    const REVIEW_STAGE = 'review';

    function checkinStage(item = null) {
        return item ? REVIEW_STAGE : INPUT_STAGE;
    }

    function checkinSummaryPills(item = {}) {
        const pills = [];
        if (item.problem_title) pills.push({ label: '题目', value: item.problem_title });
        if (item.completion_status_text) pills.push({ label: '状态', value: item.completion_status_text });
        if (item.submission_result_text) pills.push({ label: '提交', value: item.submission_result_text });
        if (item.oj_source_text) pills.push({ label: '来源', value: item.oj_source_text });
        return pills;
    }

    function compactStudentInputSections(item = {}) {
        return [
            { label: '题面 / 题意', value: item.problem_context || '' },
            { label: '卡点描述', value: item.bottleneck_text || '' },
            { label: '反思总结', value: item.reflection || '' },
            { label: '代码', value: item.student_code || '' },
        ].filter((section) => String(section.value || '').trim());
    }

    function reviewStageHeading(item = {}) {
        return item.problem_title || '这次打卡复盘';
    }

    function entryStageLead() {
        return '把这次卡住的地方记下来，我们会把它整理成一页可继续往下学的复盘讲义。';
    }

    function reviewStageLead(item = {}) {
        if (item.review_status === 'failed') {
            return '这次复盘暂时没有成功生成，你可以先看错误提示，稍后再回来继续。';
        }
        if (item.review_status !== 'completed') {
            return '复盘讲义正在生成中，生成完成后这里会自动更新。';
        }
        return '先读这次复盘，再继续做下面这一小步。';
    }

    const api = {
        INPUT_STAGE,
        REVIEW_STAGE,
        checkinStage,
        checkinSummaryPills,
        compactStudentInputSections,
        reviewStageHeading,
        entryStageLead,
        reviewStageLead,
    };

if (typeof window !== 'undefined') {
    globalContext.checkinReviewUi = api;
}

export default api;
