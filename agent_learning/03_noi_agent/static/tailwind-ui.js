/**
 * Tailwind UI Components for NOI Agent
 * 全新的学习产品风格 UI
 */

// 确保依赖函数存在
if (typeof escapeHtml === 'undefined') {
    window.escapeHtml = function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };
}

if (typeof renderRichTextInline === 'undefined') {
    window.renderRichTextInline = function(text) {
        if (!text) return '';
        return escapeHtml(text)
            .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 rounded text-xs font-mono text-slate-700 dark:text-slate-300">$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    };
}

if (typeof renderRichTextBlock === 'undefined') {
    window.renderRichTextBlock = function(text) {
        if (!text) return '';
        const lines = text.split('\n');
        const html = lines.map(line => {
            line = renderRichTextInline(line);
            if (line.startsWith('- ') || line.startsWith('* ')) {
                return `<li class="ml-4">${line.substring(2)}</li>`;
            }
            return `<p class="mb-2 last:mb-0">${line}</p>`;
        }).join('');
        return html;
    };
}

// ========== 图标定义 ==========
const Icons = {
    robot: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>`,
    target: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>`,
    lightbulb: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>`,
    footstep: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>`,
    pencil: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>`,
    crystal: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>`,
    book: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>`,
    check: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`,
    x: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`,
    question: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    arrowDown: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>`,
    map: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 7m0 13V7m0 0L9 7"/></svg>`,
    refresh: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>`,
};

// ========== AI 复盘区（对话式卡片流） ==========
function renderTwReviewSection(review, family) {
    if (!review) return '';
    
    const sections = [
        { field: 'problem_focus', icon: 'target', title: '问题定位', color: 'from-violet-500 to-purple-600', iconBg: 'bg-violet-100 text-violet-600' },
        { field: 'main_block', icon: 'target', title: '问题定位', color: 'from-violet-500 to-purple-600', iconBg: 'bg-violet-100 text-violet-600' },
        { field: 'key_bridge', icon: 'lightbulb', title: '关键桥梁', color: 'from-amber-400 to-orange-500', iconBg: 'bg-amber-100 text-amber-600' },
        { field: 'visual_hint', icon: 'question', title: '看图想一想', color: 'from-blue-400 to-cyan-500', iconBg: 'bg-blue-100 text-blue-600' },
        { field: 'guided_walkthrough', icon: 'footstep', title: '跟我走一遍', color: 'from-emerald-400 to-teal-500', iconBg: 'bg-emerald-100 text-emerald-600' },
        { field: 'try_now', icon: 'pencil', title: '现在先做', color: 'from-rose-400 to-pink-500', iconBg: 'bg-rose-100 text-rose-600' },
        { field: 'next_step', icon: 'pencil', title: '现在先做', color: 'from-rose-400 to-pink-500', iconBg: 'bg-rose-100 text-rose-600' },
        { field: 'transfer_signal', icon: 'crystal', title: '下次怎么认出来', color: 'from-indigo-400 to-violet-500', iconBg: 'bg-indigo-100 text-indigo-600' },
    ];
    
    const cards = sections
        .map((section, index, arr) => {
            const value = review[section.field];
            if (!value) return '';
            
            const isVisualHint = section.field === 'visual_hint';
            const content = isVisualHint
                ? `<pre class="mt-3 p-3 bg-slate-800 rounded-lg text-sm font-mono text-slate-200 overflow-x-auto">${escapeHtml(value)}</pre>`
                : `<div class="mt-2 text-slate-600 dark:text-slate-300 leading-relaxed text-sm">${renderRichTextInline(value)}</div>`;
            
            // 连接线（最后一个不显示）
            const connector = index < arr.length - 1 ? `
                <div class="flex justify-center my-1">
                    <div class="w-0.5 h-4 bg-gradient-to-b ${section.color} to-slate-200 dark:to-slate-700 opacity-60"></div>
                </div>
            ` : '';
            
            return `
                <div class="relative">
                    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                        <div class="flex items-center gap-3 mb-2">
                            <div class="w-10 h-10 rounded-xl ${section.iconBg} flex items-center justify-center shadow-sm">
                                ${Icons[section.icon]}
                            </div>
                            <div>
                                <div class="text-sm font-semibold text-slate-800 dark:text-slate-100">${section.title}</div>
                                <div class="w-12 h-0.5 rounded-full bg-gradient-to-r ${section.color} mt-1"></div>
                            </div>
                        </div>
                        ${content}
                    </div>
                    ${connector}
                </div>
            `;
        })
        .filter(Boolean)
        .join('');
    
    return `
        <div class="space-y-1">
            <div class="flex items-center gap-2 mb-4">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white shadow-lg shadow-primary-500/25">
                    ${Icons.robot}
                </div>
                <h3 class="text-base font-bold text-slate-800 dark:text-slate-100">复盘讲义</h3>
            </div>
            ${cards}
        </div>
    `;
}

// ========== 测验卡片（带步骤徽章） ==========
function renderTwQuizCard(quiz, reviewId) {
    if (!quiz) return '';
    
    const level = quiz?.meta?.difficulty_level || quiz?.difficulty_level || 'main';
    const badgeConfig = {
        main: { text: '第 1 步', color: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300', border: 'border-primary-200 dark:border-primary-800' },
        followup: { text: '再拆小', color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300', border: 'border-amber-200 dark:border-amber-800' },
        confirm: { text: '确认', color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300', border: 'border-emerald-200 dark:border-emerald-800' },
        final_micro_confirm: { text: '最终确认', color: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300', border: 'border-violet-200 dark:border-violet-800' },
        knowledge_confirm: { text: '知识卡后', color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300', border: 'border-orange-200 dark:border-orange-800' },
    };
    const badge = badgeConfig[level] || badgeConfig.main;
    
    const microHint = quiz.meta?.micro_hint
        ? `<div class="mb-4 p-3 bg-primary-50 dark:bg-primary-900/20 border border-primary-100 dark:border-primary-800 rounded-xl text-sm text-primary-700 dark:text-primary-300 flex items-start gap-2">
            <span class="text-lg">💡</span>
            <span>${renderRichTextInline(quiz.meta.micro_hint)}</span>
           </div>`
        : '';
    
    // 选项卡片
    const optionsHtml = (quiz.options || []).map((option, idx) => {
        const optionValue = typeof option === 'object' && option !== null ? option.value : option;
        const optionLabel = typeof option === 'object' && option !== null ? option.label : option;
        const letter = String.fromCharCode(65 + idx);
        return `
            <div class="tw-quiz-option group relative flex items-start gap-3 p-4 bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-xl cursor-pointer hover:border-primary-400 dark:hover:border-primary-500 hover:shadow-md transition-all"
                 onclick="selectTwQuizOption(this, '${escapeHtml(optionValue)}', ${reviewId})">
                <div class="option-letter w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-bold text-sm flex items-center justify-center flex-shrink-0 group-hover:bg-primary-500 group-hover:text-white transition-colors">
                    ${letter}
                </div>
                <div class="option-text text-sm text-slate-700 dark:text-slate-300 pt-1">${renderRichTextInline(optionLabel)}</div>
                <div class="option-check absolute right-4 top-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div class="w-5 h-5 rounded-full bg-primary-500 flex items-center justify-center">
                        <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    return `
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-lg shadow-slate-200/50 dark:shadow-none border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div class="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <span class="text-lg">📝</span>
                    <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">理解检查</span>
                </div>
                <span class="px-3 py-1 rounded-full text-xs font-bold ${badge.color} border ${badge.border}">${badge.text}</span>
            </div>
            <div class="p-5">
                ${microHint}
                <div class="text-base text-slate-800 dark:text-slate-100 font-medium leading-relaxed mb-5">
                    ${renderRichTextBlock(quiz.question_text)}
                </div>
                <div class="space-y-2 mb-5">
                    ${optionsHtml}
                </div>
                <input type="hidden" id="tw-quiz-selected-${reviewId}" value="">
                <button onclick="submitTwQuizAnswer(${Number(quiz.quiz_id)}, ${Number(reviewId)})" 
                        class="w-full py-3.5 px-4 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-xl shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 transform hover:-translate-y-0.5 transition-all">
                    提交答案
                </button>
            </div>
        </div>
    `;
}

// 选项选择
function selectTwQuizOption(element, value, reviewId) {
    const parent = element.closest('.space-y-2');
    parent.querySelectorAll('.tw-quiz-option').forEach(el => {
        el.classList.remove('selected', 'border-primary-500', 'bg-primary-50', 'dark:border-primary-400', 'dark:bg-primary-900/20');
        el.classList.add('border-slate-200', 'dark:border-slate-700');
        el.querySelector('.option-letter').classList.remove('bg-primary-500', 'text-white');
        el.querySelector('.option-letter').classList.add('bg-slate-100', 'dark:bg-slate-700', 'text-slate-600', 'dark:text-slate-300');
    });
    element.classList.remove('border-slate-200', 'dark:border-slate-700');
    element.classList.add('selected', 'border-primary-500', 'bg-primary-50', 'dark:border-primary-400', 'dark:bg-primary-900/20');
    element.querySelector('.option-letter').classList.remove('bg-slate-100', 'dark:bg-slate-700', 'text-slate-600', 'dark:text-slate-300');
    element.querySelector('.option-letter').classList.add('bg-primary-500', 'text-white');
    document.getElementById(`tw-quiz-selected-${reviewId}`).value = value;
}

// ========== 知识兜底卡 ==========
function renderTwKnowledgeCard(card = {}) {
    if (!card || typeof card !== 'object') return '';
    
    const opening = String(card.opening || '').trim();
    const bridgeExplanation = String(card.bridge_explanation || '').trim();
    const visualHint = String(card.visual_hint || '').trim();
    const microAction = String(card.micro_action || card.micro_action_text || '').trim();
    const algorithmOverview = String(card.algorithm_overview || '').trim();
    
    // 对比表格
    const comparisonHtml = card.wrong_thinking && card.right_thinking ? `
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
            <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 rounded-r-xl p-4">
                <div class="flex items-center gap-2 text-red-600 dark:text-red-400 font-bold text-xs uppercase tracking-wider mb-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    常见误解
                </div>
                <div class="text-sm text-slate-700 dark:text-slate-300">${renderRichTextInline(card.wrong_thinking)}</div>
            </div>
            <div class="bg-emerald-50 dark:bg-emerald-900/20 border-l-4 border-emerald-400 rounded-r-xl p-4">
                <div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-xs uppercase tracking-wider mb-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    正确理解
                </div>
                <div class="text-sm text-slate-700 dark:text-slate-300">${renderRichTextInline(card.right_thinking)}</div>
            </div>
        </div>
    ` : '';
    
    // 可折叠的算法全景
    const overviewHtml = algorithmOverview ? `
        <div class="mt-4 pt-4 border-t border-amber-200/50 dark:border-amber-800/50">
            <button onclick="this.nextElementSibling.classList.toggle('hidden'); this.querySelector('.chevron').classList.toggle('rotate-180')" 
                    class="flex items-center justify-between w-full text-left text-sm text-amber-700 dark:text-amber-300 hover:text-amber-800 dark:hover:text-amber-200 transition-colors">
                <span class="flex items-center gap-2">
                    ${Icons.map}
                    在知识地图里的位置
                </span>
                <span class="chevron transition-transform">${Icons.arrowDown}</span>
            </button>
            <div class="hidden mt-3 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                ${renderRichTextInline(algorithmOverview)}
            </div>
        </div>
    ` : '';
    
    return `
        <div class="bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-amber-900/20 dark:via-orange-900/20 dark:to-yellow-900/20 rounded-2xl border border-amber-200 dark:border-amber-800/50 overflow-hidden shadow-lg shadow-amber-500/10">
            <div class="px-5 py-4 bg-amber-100/50 dark:bg-amber-900/30 border-b border-amber-200 dark:border-amber-800/50 flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-white shadow-lg shadow-amber-500/30">
                    ${Icons.book}
                </div>
                <div>
                    <div class="text-sm font-bold text-amber-800 dark:text-amber-200">先把这块知识单独讲清楚</div>
                    <div class="text-xs text-amber-600 dark:text-amber-400">换个方式讲清楚这一步</div>
                </div>
            </div>
            <div class="p-5">
                ${opening ? `<div class="text-sm text-slate-600 dark:text-slate-400 mb-4 italic">"${renderRichTextInline(opening)}"</div>` : ''}
                
                <div class="bg-white/70 dark:bg-slate-800/50 rounded-xl p-4 border border-amber-200/50 dark:border-amber-800/30">
                    <div class="flex items-center gap-2 mb-3">
                        <div class="w-6 h-6 rounded-lg bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 flex items-center justify-center">
                            ${Icons.target}
                        </div>
                        <span class="text-sm font-bold text-slate-800 dark:text-slate-200">当前这座桥</span>
                    </div>
                    ${bridgeExplanation ? `<div class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">${renderRichTextInline(bridgeExplanation)}</div>` : ''}
                    ${comparisonHtml}
                    ${visualHint ? `<pre class="mt-4 p-3 bg-slate-800 rounded-lg text-xs font-mono text-slate-200 overflow-x-auto">${escapeHtml(visualHint)}</pre>` : ''}
                    ${microAction ? `<div class="mt-4 text-sm text-slate-600 dark:text-slate-400 leading-relaxed"><strong class="text-slate-800 dark:text-slate-200">你现在先做：</strong>${renderRichTextInline(microAction)}</div>` : ''}
                </div>
                
                ${overviewHtml}
            </div>
        </div>
    `;
}

// ========== 学习路径时间轴 ==========
function renderTwLearningTimeline(item) {
    const reviewId = Number(item.review_id || 0);
    if (!reviewId) return '';
    
    const quizHistory = Array.from(item.quiz_history || []).filter(q => q && q.status !== 'replaced');
    const currentQuizId = Number(item.quiz_id || 0);
    
    // 生成步骤
    const stepsHtml = quizHistory.map((quiz, index) => {
        const isPending = quiz.status === 'pending' && (!currentQuizId || Number(quiz.quiz_id) === currentQuizId);
        const isCorrect = quiz.latest_is_correct;
        const stepNum = index + 1;
        
        if (isPending) {
            // 当前步骤
            return `
                <div class="relative">
                    <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary-500 to-slate-200 dark:to-slate-700"></div>
                    <div class="relative flex gap-4">
                        <div class="relative z-10">
                            <div class="w-8 h-8 rounded-full bg-primary-500 text-white flex items-center justify-center font-bold text-sm shadow-lg shadow-primary-500/40 animate-pulse">
                                ${stepNum}
                            </div>
                        </div>
                        <div class="flex-1 pb-6">
                            <div class="text-xs font-bold text-primary-600 dark:text-primary-400 uppercase tracking-wider mb-2">当前步骤</div>
                            ${quiz?.meta?.knowledge_bailout ? renderTwKnowledgeCard(quiz?.meta?.knowledge_card) : ''}
                            ${renderTwQuizCard(quiz, reviewId)}
                        </div>
                    </div>
                </div>
            `;
        } else {
            // 已完成步骤（折叠）
            const statusIcon = isCorrect ? '✅' : '❌';
            const statusColor = isCorrect ? 'text-emerald-500' : 'text-red-500';
            return `
                <div class="relative">
                    <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700"></div>
                    <div class="relative flex gap-4">
                        <div class="relative z-10">
                            <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 ${statusColor} flex items-center justify-center text-sm">
                                ${statusIcon}
                            </div>
                        </div>
                        <div class="flex-1 pb-4">
                            <div class="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-3 border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
                                 onclick="this.nextElementSibling.classList.toggle('hidden'); this.querySelector('.chevron').classList.toggle('rotate-180')">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-slate-600 dark:text-slate-400">第 ${stepNum} 步 · ${escapeHtml(quiz.question_text?.substring(0, 30) || '...')}...</span>
                                    <span class="chevron transition-transform text-slate-400">${Icons.arrowDown}</span>
                                </div>
                            </div>
                            <div class="hidden mt-2">
                                ${renderTwQuizCard(quiz, reviewId)}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }).join('');
    
    return `
        <div class="py-4">
            ${stepsHtml}
        </div>
    `;
}

// ========== 自我检查卡片 ==========
function renderTwSelfCheck(reviewId, family = 'failure_diagnosis') {
    const copy = reviewFamilyUi.reviewFeedbackCopy(family);
    const options = [
        { value: 'clear', icon: '✅', label: copy.clearLabel, color: 'from-emerald-400 to-teal-500', bg: 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800 hover:border-emerald-400' },
        { value: 'guessed', icon: '🤔', label: copy.guessedLabel, color: 'from-amber-400 to-orange-500', bg: 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800 hover:border-amber-400' },
        { value: 'confused', icon: '😵', label: copy.confusedLabel, color: 'from-rose-400 to-pink-500', bg: 'bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800 hover:border-rose-400' },
    ];
    
    const optionsHtml = options.map(opt => `
        <button onclick="submitSelfCheck(${Number(reviewId)}, '${opt.value}')" 
                class="group w-full p-4 rounded-xl border-2 ${opt.bg} transition-all hover:shadow-lg hover:-translate-y-0.5">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br ${opt.color} text-white flex items-center justify-center text-xl shadow-lg group-hover:scale-110 transition-transform">
                    ${opt.icon}
                </div>
                <div class="text-left">
                    <div class="text-sm font-semibold text-slate-800 dark:text-slate-200">${escapeHtml(opt.label)}</div>
                </div>
                <div class="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
                    <div class="w-6 h-6 rounded-full bg-white dark:bg-slate-700 flex items-center justify-center shadow">
                        <svg class="w-3 h-3 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                    </div>
                </div>
            </div>
        </button>
    `).join('');
    
    return `
        <div class="bg-gradient-to-br from-primary-50 to-violet-50 dark:from-primary-900/20 dark:to-violet-900/20 rounded-2xl border border-primary-200 dark:border-primary-800/50 p-5">
            <div class="text-center mb-5">
                <div class="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-violet-500 text-white flex items-center justify-center mx-auto mb-3 shadow-lg shadow-primary-500/30">
                    ${Icons.question}
                </div>
                <h4 class="text-base font-bold text-slate-800 dark:text-slate-100">${escapeHtml(copy.title)}</h4>
            </div>
            <div class="space-y-3">
                ${optionsHtml}
            </div>
        </div>
    `;
}

// ========== 结果反馈卡片 ==========
function renderTwFeedback({ title, feedbackText = '', bridgeFeedback = '', explanation = '', tone = 'success' }) {
    const config = {
        success: { icon: '🎉', gradient: 'from-emerald-400 to-teal-500', border: 'border-emerald-200 dark:border-emerald-800', bg: 'bg-emerald-50 dark:bg-emerald-900/20' },
        final: { icon: '📌', gradient: 'from-violet-400 to-purple-500', border: 'border-violet-200 dark:border-violet-800', bg: 'bg-violet-50 dark:bg-violet-900/20' },
        warn: { icon: '⚠️', gradient: 'from-amber-400 to-orange-500', border: 'border-amber-200 dark:border-amber-800', bg: 'bg-amber-50 dark:bg-amber-900/20' },
    };
    const cfg = config[tone] || config.success;
    
    return `
        <div class="rounded-2xl border ${cfg.border} ${cfg.bg} p-5">
            <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br ${cfg.gradient} text-white flex items-center justify-center text-lg shadow-lg">
                    ${cfg.icon}
                </div>
                <h4 class="text-base font-bold text-slate-800 dark:text-slate-100">${escapeHtml(title)}</h4>
            </div>
            ${feedbackText ? `<div class="text-sm text-slate-700 dark:text-slate-300 mb-3">${renderRichTextBlock(feedbackText)}</div>` : ''}
            ${bridgeFeedback ? `<div class="bg-white/70 dark:bg-slate-800/50 rounded-xl p-3 border border-slate-200 dark:border-slate-700 text-sm"><strong class="text-emerald-600 dark:text-emerald-400">✅ 你刚才真正答对的是：</strong> ${renderRichTextInline(bridgeFeedback)}</div>` : ''}
            ${explanation ? `<div class="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-sm text-slate-500 dark:text-slate-400">${renderRichTextBlock(explanation)}</div>` : ''}
        </div>
    `;
}

// ========== 补救按钮组 ==========
function renderTwRemedyButtons(reviewId, errorLayer, options = {}) {
    const dynamicLabel = options.dynamicLabel || dynamicRemedyLabel(errorLayer);
    const includeResolve = options.includeResolve === true;
    const includeResolveLabel = options.includeResolveLabel || '我懂了';
    
    const buttons = [
        includeResolve ? { action: `resolveRemedy(${Number(reviewId)}, 'resolved')`, icon: '✅', label: includeResolveLabel, color: 'bg-emerald-500 hover:bg-emerald-600' } : null,
        { action: `triggerRemedy(${Number(reviewId)}, 'rephrase')`, icon: '📝', label: '再换一种说法讲这一步', color: 'bg-slate-700 hover:bg-slate-600 dark:bg-slate-600 dark:hover:bg-slate-500' },
        { action: `triggerRemedy(${Number(reviewId)}, 'smaller_example')`, icon: '🔍', label: '给我一个更小的例子', color: 'bg-slate-700 hover:bg-slate-600 dark:bg-slate-600 dark:hover:bg-slate-500' },
        { action: `triggerRemedy(${Number(reviewId)}, 'easier_quiz')`, icon: '🎯', label: '再出一道更简单的小题', color: 'bg-slate-700 hover:bg-slate-600 dark:bg-slate-600 dark:hover:bg-slate-500' },
        { action: `triggerRemedy(${Number(reviewId)}, 'dynamic_bridge_help')`, icon: '💡', label: dynamicLabel, color: 'bg-slate-700 hover:bg-slate-600 dark:bg-slate-600 dark:hover:bg-slate-500' },
    ].filter(Boolean);
    
    const buttonsHtml = buttons.map(btn => `
        <button onclick="${btn.action}" class="w-full group flex items-center gap-3 p-3 rounded-xl ${btn.color} text-white transition-all hover:shadow-lg hover:-translate-y-0.5">
            <span class="text-lg">${btn.icon}</span>
            <span class="text-sm font-medium">${escapeHtml(btn.label)}</span>
            <svg class="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
    `).join('');
    
    return `
        <div class="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-2xl border border-amber-200 dark:border-amber-800/50 p-5">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 text-white flex items-center justify-center shadow-lg">
                    ${Icons.refresh}
                </div>
                <div>
                    <h4 class="text-base font-bold text-slate-800 dark:text-slate-100">这一步还没完全打通</h4>
                    <p class="text-xs text-slate-500 dark:text-slate-400">我们换一种方式继续带你一下</p>
                </div>
            </div>
            <div class="space-y-2">
                ${buttonsHtml}
            </div>
        </div>
    `;
}

// ========== 主渲染函数 ==========
function renderTwLearningSection(item) {
    const reviewId = item.review_id;
    if (!reviewId || item.review_status !== 'completed') return '';
    const reviewFamily = reviewFamilyUi.resolveReviewFamily(item);
    
    let content = '';
    
    if (item.review_learning_status === 'self_check_required') {
        content = `
            ${renderTwFeedback({
                title: item.quiz_latest_feedback || '答对了，这一步你跨过去了。',
                bridgeFeedback: item.quiz_bridge_feedback,
                explanation: item.quiz_explanation,
                tone: 'success',
            })}
            ${renderTwSelfCheck(reviewId, reviewFamily)}
        `;
    } else if (item.review_learning_status === 'resolved') {
        content = renderTwFeedback({
            title: '答对了，这一步你跨过去了。',
            feedbackText: item.quiz_latest_feedback,
            bridgeFeedback: item.quiz_bridge_feedback,
            explanation: item.quiz_explanation,
            tone: 'success',
        });
    } else if (item.review_learning_status === 'needs_teacher_followup') {
        content = renderTwFeedback({
            title: '这道题我们先停在这里，老师会接着和你一起看。',
            feedbackText: item.quiz_latest_feedback,
            bridgeFeedback: item.quiz_bridge_feedback,
            explanation: item.quiz_explanation,
            tone: 'final',
        });
    } else if (item.review_learning_status === 'knowledge_bailout') {
        content = renderTwLearningTimeline(item);
    } else if (item.quiz_status === 'pending' && item.quiz_id) {
        content = renderTwQuizCard({
            quiz_id: item.quiz_id,
            quiz_type: item.quiz_type,
            question_text: item.quiz_question_text,
            options: item.quiz_options,
            meta: item.quiz_meta || item.meta,
            difficulty_level: item.quiz_difficulty_level || item.difficulty_level,
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
            ${renderTwRemedyButtons(reviewId, item.review_error_layer)}
        `;
    } else {
        content = `
            <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 p-8 text-center">
                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-400 to-violet-500 text-white flex items-center justify-center mx-auto mb-4 text-2xl shadow-lg shadow-primary-500/30">
                    📝
                </div>
                <h4 class="text-lg font-bold text-slate-800 dark:text-slate-100 mb-2">复盘看完后，再来一道小题确认</h4>
                <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">看看你是不是真的懂了这一步</p>
                <button onclick="startReviewQuiz(${Number(reviewId)})" class="px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-xl shadow-lg shadow-primary-500/25 transition-all hover:-translate-y-0.5">
                    试试看你是不是已经懂这一步了
                </button>
            </div>
        `;
    }
    
    return `<div class="space-y-4">${content}</div>`;
}

// ========== 提交答案（兼容新 UI） ==========
function submitTwQuizAnswer(quizId, reviewId) {
    const hiddenInput = document.getElementById(`tw-quiz-selected-${reviewId}`);
    const answerText = hiddenInput ? hiddenInput.value.trim() : '';
    
    if (!answerText) {
        alert('请先选择一个答案');
        return;
    }
    
    // 调用原有的提交函数，但传入答案
    const container = document.getElementById(`review-quiz-${reviewId}`) || document.getElementById('review-detail-quiz');
    if (container) {
        container.innerHTML = '<div class="p-8 text-center"><div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto"></div><p class="mt-3 text-sm text-slate-500">正在检查你的答案...</p></div>';
    }
    
    // 直接调用原有 API
    apiFetch(`${API_BASE}/api/quizzes/${quizId}/answer`, {
        method: 'POST',
        body: JSON.stringify({ answer_text: answerText }),
    }).then(res => res.json()).then(data => {
        // 刷新页面或更新 UI
        if (container && data.next_state) {
            // 简化处理：重新加载当前学习状态
            location.reload();
        }
    }).catch(err => {
        console.error('提交失败:', err);
        alert('提交失败，请重试');
    });
}

// 兼容函数映射
if (typeof resolveRemedyTransition === 'undefined') {
    window.resolveRemedyTransition = function({ understandingSelfCheck, quizRole, feedbackText, explanation }) {
        if (understandingSelfCheck === 'confused') {
            return {
                title: '你已经发现这一步还没站稳，我们先把它再拆小一点。',
                explanation: explanation || '',
            };
        }
        if (understandingSelfCheck === 'guessed') {
            return {
                title: feedbackText || '你已经感觉到这一步还有点虚，我们先换一种方式继续讲。',
                explanation: explanation || '',
            };
        }
        return {
            title: '这一步还没完全打通，我们先把它再拆小一点。',
            explanation: explanation || '',
        };
    };
}

if (typeof renderRemedyTransitionCard === 'undefined') {
    window.renderRemedyTransitionCard = function(transition) {
        return `
            <div class="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl mb-4">
                <div class="text-amber-800 dark:text-amber-200 font-medium">${transition.title}</div>
                ${transition.explanation ? `<div class="text-amber-600 dark:text-amber-400 text-sm mt-2">${transition.explanation}</div>` : ''}
            </div>
        `;
    };
}

if (typeof apiFetch === 'undefined') {
    window.apiFetch = async function(url, options = {}) {
        const API_BASE = window.API_BASE || '';
        const res = await fetch(`${API_BASE}${url}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });
        return res;
    };
}

// 导出函数供外部使用
window.TwUI = {
    renderReviewSection: renderTwReviewSection,
    renderQuizCard: renderTwQuizCard,
    renderKnowledgeCard: renderTwKnowledgeCard,
    renderLearningTimeline: renderTwLearningTimeline,
    renderSelfCheck: renderTwSelfCheck,
    renderFeedback: renderTwFeedback,
    renderRemedyButtons: renderTwRemedyButtons,
    renderLearningSection: renderTwLearningSection,
    selectQuizOption: selectTwQuizOption,
    submitQuizAnswer: submitTwQuizAnswer,
};

// 调试日志
console.log('[TwUI] tailwind-ui.js 已加载');
if (window.TwUI) {
    console.log('[TwUI] TwUI 对象已导出:', Object.keys(window.TwUI));
}
