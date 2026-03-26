// NOI Agent 前端逻辑 - v0.3.0 Training Loop

const API_BASE = window.location.origin;

// 状态
let token = localStorage.getItem('noi_token') || null;
let userId = localStorage.getItem('noi_user_id') || null;
let userRole = localStorage.getItem('noi_user_role') || null;
let chatHistory = [];

// DOM 元素
const loginSection = document.getElementById('login-section');
const studentSection = document.getElementById('student-section');
const teacherSection = document.getElementById('teacher-section');
const userBar = document.getElementById('user-bar');

// ============ 认证失效处理 ============

/**
 * 检查错误是否是认证失效
 */
function isAuthError(status, detail) {
    if (status !== 401) return false;
    
    const authErrorMessages = [
        'Invalid or expired token',
        'Missing authorization header',
        'Invalid authentication credentials',
        'Not authenticated'
    ];
    
    return authErrorMessages.some(msg => 
        detail && detail.includes(msg)
    );
}

/**
 * 处理认证过期/失效
 * - 清空本地 token
 * - 回到登录页
 * - 提示用户
 */
function handleAuthExpired(message = '登录状态已失效，请重新登录') {
    // 先清空所有状态（复用 handleLogout 的清空逻辑，但不完全复用，因为要避免循环）
    token = null;
    userId = null;
    userRole = null;
    chatHistory = [];
    
    localStorage.removeItem('noi_token');
    localStorage.removeItem('noi_user_id');
    localStorage.removeItem('noi_user_role');
    
    // 清空显示
    document.getElementById('chat-history').innerHTML = '';
    document.getElementById('quota-info').textContent = '';
    document.getElementById('teacher-quota-result').textContent = '';
    document.getElementById('reset-result').textContent = '';
    document.getElementById('checkin-history-list').innerHTML = '';
    document.getElementById('teacher-checkins-list').innerHTML = '';
    document.getElementById('error-stats').innerHTML = '';
    document.getElementById('student-flags').innerHTML = '';
    document.getElementById('checkin-result').innerHTML = '';
    
    // 显示登录区，隐藏主界面
    loginSection.classList.remove('hidden');
    studentSection.classList.add('hidden');
    teacherSection.classList.add('hidden');
    userBar.classList.add('hidden');
    
    // 显示认证失效提示
    const errorEl = document.getElementById('login-error');
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    
    // 3秒后自动隐藏错误提示
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 5000);
}

/**
 * 统一的 API 请求包装
 * 自动处理 401 认证失效
 */
async function apiFetch(url, options = {}) {
    // 确保 headers 存在
    if (!options.headers) {
        options.headers = {};
    }
    
    // 如果有 token，自动添加
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    const res = await fetch(url, options);
    
    // 处理 401 认证失效
    if (res.status === 401) {
        let detail = '';
        try {
            const errData = await res.json();
            detail = errData.detail || '';
        } catch (e) {
            detail = 'Unauthorized';
        }
        
        if (isAuthError(res.status, detail)) {
            // 服务重启后的典型场景
            if (detail.includes('Invalid or expired token')) {
                handleAuthExpired('服务刚刚重启，请重新登录');
            } else {
                handleAuthExpired('登录状态已失效，请重新登录');
            }
            // 抛出特殊错误，让调用方知道已经处理了认证失效
            const authError = new Error('AUTH_EXPIRED');
            authError.isAuthError = true;
            throw authError;
        }
    }
    
    return res;
}

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', async () => {
    if (token && userId && userRole) {
        // 先显示界面，然后异步验证 token 是否还有效
        showMainInterface();
        
        // 验证 token 有效性（服务重启后会失效）
        try {
            // 用一个轻量接口验证（配额查询）
            const res = await apiFetch(`${API_BASE}/quota/${userId}/P1001`);
            if (!res.ok && res.status !== 401) {
                // 其他错误（如网络问题），保持登录态
                console.warn('Token validation failed:', res.status);
            }
        } catch (err) {
            if (err.isAuthError) {
                // 已经由 handleAuthExpired 处理，不需要额外操作
                console.log('Token expired, redirected to login');
            } else {
                // 网络错误，给用户一个提示但不强制退出
                console.error('Network error during token validation:', err);
            }
        }
    }
    
    // 登录
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // 标签切换
    setupTabs();
    
    // 学生功能
    document.getElementById('check-quota-btn').addEventListener('click', studentCheckQuota);
    document.getElementById('send-btn').addEventListener('click', studentSendMessage);
    document.getElementById('clear-history-btn').addEventListener('click', clearChatHistory);
    document.getElementById('submit-checkin-btn').addEventListener('click', submitCheckin);
    document.getElementById('load-my-checkins-btn').addEventListener('click', loadMyCheckins);
    
    // 打卡表单实时验证
    setupCheckinValidation();
    
    // 教师功能
    document.getElementById('teacher-check-quota-btn').addEventListener('click', teacherCheckQuota);
    document.getElementById('reset-quota-btn').addEventListener('click', teacherResetQuota);
    document.getElementById('load-all-checkins-btn').addEventListener('click', loadAllCheckins);
    document.getElementById('load-stats-btn').addEventListener('click', loadErrorStats);
    document.getElementById('load-flags-btn').addEventListener('click', loadStudentFlags);
    document.getElementById('load-usage-btn').addEventListener('click', loadUsageStats);
});

function setupTabs() {
    // 学生标签
    const studentTabs = document.querySelectorAll('#student-tabs .tab-btn');
    studentTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.tab;
            document.querySelectorAll('#student-section .tab-content').forEach(c => c.classList.add('hidden'));
            document.getElementById(targetId).classList.remove('hidden');
            studentTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });
    
    // 教师标签
    const teacherTabs = document.querySelectorAll('#teacher-tabs .tab-btn');
    teacherTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.tab;
            document.querySelectorAll('#teacher-section .tab-content').forEach(c => c.classList.add('hidden'));
            document.getElementById(targetId).classList.remove('hidden');
            teacherTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });
}

// ============ 登录/退出 ============
async function handleLogin(e) {
    e.preventDefault();
    const userIdInput = document.getElementById('user-id').value.trim();
    const password = document.getElementById('password').value;
    
    try {
        const res = await apiFetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userIdInput, password })
        });
        
        if (!res.ok) {
            const err = await res.json();
            showError('login-error', err.detail || '登录失败');
            return;
        }
        
        const data = await res.json();
        token = data.token;
        userId = data.user_id;
        userRole = data.role;
        
        localStorage.setItem('noi_token', token);
        localStorage.setItem('noi_user_id', userId);
        localStorage.setItem('noi_user_role', userRole);
        
        showMainInterface();
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        showError('login-error', '网络错误，请检查服务是否运行');
    }
}

function handleLogout() {
    token = null;
    userId = null;
    userRole = null;
    chatHistory = [];
    
    localStorage.removeItem('noi_token');
    localStorage.removeItem('noi_user_id');
    localStorage.removeItem('noi_user_role');
    
    // 清空显示
    document.getElementById('chat-history').innerHTML = '';
    document.getElementById('quota-info').textContent = '';
    document.getElementById('teacher-quota-result').textContent = '';
    document.getElementById('reset-result').textContent = '';
    document.getElementById('checkin-history-list').innerHTML = '';
    document.getElementById('teacher-checkins-list').innerHTML = '';
    document.getElementById('error-stats').innerHTML = '';
    document.getElementById('student-flags').innerHTML = '';
    document.getElementById('checkin-result').innerHTML = '';
    
    loginSection.classList.remove('hidden');
    studentSection.classList.add('hidden');
    teacherSection.classList.add('hidden');
    userBar.classList.add('hidden');
    
    document.getElementById('login-form').reset();
    document.getElementById('login-error').textContent = '';
}

function showMainInterface() {
    loginSection.classList.add('hidden');
    userBar.classList.remove('hidden');
    
    document.getElementById('current-user').textContent = userId;
    document.getElementById('current-role').textContent = userRole === 'teacher' ? '教师' : '学生';
    
    if (userRole === 'student') {
        studentSection.classList.remove('hidden');
        teacherSection.classList.add('hidden');
        studentCheckQuota();
    } else if (userRole === 'teacher') {
        studentSection.classList.add('hidden');
        teacherSection.classList.remove('hidden');
    }
}

// ============ 学生功能 ============
async function studentCheckQuota() {
    const problemId = document.getElementById('student-problem-id').value.trim() || 'P1001';
    
    try {
        const res = await apiFetch(`${API_BASE}/quota/${userId}/${problemId}`);
        
        const quotaEl = document.getElementById('quota-info');
        
        if (!res.ok) {
            const err = await res.json();
            quotaEl.textContent = err.detail || '查询失败';
            quotaEl.style.color = 'red';
            return;
        }
        
        const data = await res.json();
        quotaEl.textContent = `题目: ${data.problem_id} | 已用: ${data.count}/${data.max} | 剩余: ${data.remaining}`;
        quotaEl.style.color = data.remaining === 0 ? 'orange' : '#333';
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        document.getElementById('quota-info').textContent = '查询失败';
    }
}

async function studentSendMessage() {
    const problemId = document.getElementById('student-problem-id').value.trim() || 'P1001';
    const message = document.getElementById('student-message').value.trim();
    
    if (!message) return;
    
    addChatMessage('user', message);
    document.getElementById('student-message').value = '';
    
    try {
        const res = await apiFetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                problem_id: problemId,
                message: message,
                history: chatHistory
            })
        });
        
        if (!res.ok) {
            const err = await res.json();
            addChatMessage('assistant', `错误: ${err.detail}`);
            return;
        }
        
        const data = await res.json();
        chatHistory = data.history;
        addChatMessage('assistant', data.reply);
        
        const q = data.quota;
        document.getElementById('quota-info').textContent = 
            `题目: ${q.problem_id} | 已用: ${q.count}/${q.max} | 剩余: ${q.remaining}`;
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        addChatMessage('assistant', '网络错误，请稍后重试');
    }
}

// ============ 打卡表单验证 ============
function setupCheckinValidation() {
    const bottleneckInput = document.getElementById('checkin-bottleneck');
    const countEl = document.getElementById('bottleneck-count');
    const hintEl = document.getElementById('bottleneck-hint');
    const submitBtn = document.getElementById('submit-checkin-btn');
    
    // 无效关键词（后端同步）
    const invalidKeywords = ['不会', '没思路', '不知道', '不懂', '太难了'];
    
    bottleneckInput.addEventListener('input', () => {
        const text = bottleneckInput.value.trim();
        const len = text.length;
        
        // 更新字数显示
        countEl.textContent = `${len} 字`;
        
        // 检查有效性
        let isValid = true;
        let hint = '';
        
        if (len < 15) {
            isValid = false;
            hint = `还需要 ${15 - len} 字`;
            countEl.style.color = '#e74c3c';
        } else if (len < 30 && invalidKeywords.some(kw => text.includes(kw))) {
            isValid = false;
            hint = '描述有点笼统，请具体说明你卡在哪一步';
            countEl.style.color = '#f39c12';
        } else {
            countEl.style.color = '#27ae60';
        }
        
        hintEl.textContent = hint || '✓ 长度达标';
        hintEl.style.color = isValid ? '#27ae60' : (len < 15 ? '#e74c3c' : '#f39c12');
        
        // 检查其他必填项
        const hasUrl = document.getElementById('checkin-url').value.trim();
        const hasTitle = document.getElementById('checkin-title').value.trim();
        const hasErrorType = document.querySelector('input[name="error_type"]:checked');
        
        submitBtn.disabled = !(isValid && hasUrl && hasTitle && hasErrorType);
    });
    
    // 监听其他字段变化
    ['checkin-url', 'checkin-title'].forEach(id => {
        document.getElementById(id).addEventListener('input', () => {
            bottleneckInput.dispatchEvent(new Event('input'));
        });
    });
    
    document.querySelectorAll('input[name="error_type"]').forEach(cb => {
        cb.addEventListener('change', () => {
            bottleneckInput.dispatchEvent(new Event('input'));
        });
    });
}

// 展开/收起示例
function toggleExample() {
    const content = document.getElementById('example-content');
    const icon = document.querySelector('.toggle-icon');
    content.classList.toggle('hidden');
    icon.textContent = content.classList.contains('hidden') ? '▼' : '▲';
}

// 防重复提交锁
let isSubmittingCheckin = false;

async function submitCheckin() {
    // 防重复提交
    if (isSubmittingCheckin) return;
    isSubmittingCheckin = true;
    
    const submitBtn = document.getElementById('submit-checkin-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = '提交中...';
    
    const problemUrl = document.getElementById('checkin-url').value.trim();
    const problemTitle = document.getElementById('checkin-title').value.trim();
    const ojSource = document.getElementById('checkin-oj').value;
    const completionStatus = document.getElementById('checkin-status').value;
    const bottleneckText = document.getElementById('checkin-bottleneck').value.trim();
    const reflection = document.getElementById('checkin-reflection').value.trim();
    
    const resultEl = document.getElementById('checkin-result');
    
    // 收集错误类型
    const errorTypes = [];
    document.querySelectorAll('input[name="error_type"]:checked').forEach(cb => {
        errorTypes.push(cb.value);
    });
    
    // 验证
    if (!problemUrl || !problemTitle) {
        resultEl.textContent = '请填写题目链接和标题';
        resultEl.style.color = 'red';
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
        return;
    }
    if (bottleneckText.length < 15) {
        resultEl.textContent = '卡点描述至少15个字';
        resultEl.style.color = 'red';
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
        return;
    }
    if (errorTypes.length === 0) {
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
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                problem_url: problemUrl,
                problem_title: problemTitle,
                oj_source: ojSource,
                completion_status: completionStatus,
                bottleneck_text: bottleneckText,
                error_types: errorTypes,
                reflection: reflection || null
            })
        });
        
        if (!res.ok) {
            const err = await res.json();
            resultEl.textContent = err.detail || '打卡失败';
            resultEl.style.color = 'red';
            isSubmittingCheckin = false;
            submitBtn.disabled = false;
            submitBtn.textContent = '提交打卡';
            return;
        }
        
        const data = await res.json();
        
        // 显示复盘
        let reviewHtml = '';
        if (data.review) {
            reviewHtml = `
                <div class="review-box">
                    <h4>AI 复盘报告</h4>
                    <p><strong>错误标签:</strong> ${escapeHtml(data.review.error_tags?.join(', ') || '')}</p>
                    <p><strong>问题诊断:</strong> ${escapeHtml(data.review.diagnosis || '')}</p>
                    <p><strong>下一步行动:</strong> ${escapeHtml(data.review.next_action || '')}</p>
                    <p><strong>推荐专题:</strong> ${escapeHtml(data.review.suggested_topic || '')}</p>
                </div>
            `;
        }
        
        resultEl.innerHTML = `
            <div style="color: green; margin-bottom: 10px;">${data.message} (ID: ${data.checkin_id})</div>
            ${reviewHtml}
        `;
        
        // 清空表单
        document.getElementById('checkin-url').value = '';
        document.getElementById('checkin-title').value = '';
        document.getElementById('checkin-bottleneck').value = '';
        document.getElementById('checkin-reflection').value = '';
        document.querySelectorAll('input[name="error_type"]').forEach(cb => cb.checked = false);
        
        // 重置字数统计
        document.getElementById('bottleneck-count').textContent = '0 字';
        document.getElementById('bottleneck-count').style.color = '#333';
        document.getElementById('bottleneck-hint').textContent = '至少15字，越具体越好';
        document.getElementById('bottleneck-hint').style.color = '#666';
        
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        resultEl.textContent = '网络错误';
        resultEl.style.color = 'red';
    } finally {
        // 重置提交状态
        isSubmittingCheckin = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '提交打卡';
    }
}

async function loadMyCheckins() {
    const listEl = document.getElementById('checkin-history-list');
    listEl.innerHTML = '<p>加载中...</p>';
    
    try {
        const res = await apiFetch(`${API_BASE}/api/checkins/me`, {
            
        });
        
        if (!res.ok) {
            listEl.innerHTML = '<p style="color:red">加载失败</p>';
            return;
        }
        
        const data = await res.json();
        
        if (data.checkins.length === 0) {
            listEl.innerHTML = '<p>暂无打卡记录</p>';
            return;
        }
        
        listEl.innerHTML = data.checkins.map(c => `
            <div class="checkin-card">
                <div class="checkin-header">
                    <span class="checkin-title">${escapeHtml(c.problem_title)}</span>
                    <span class="checkin-source">${c.oj_source}</span>
                    <span class="checkin-status status-${c.completion_status}">${statusText(c.completion_status)}</span>
                    ${c.has_review ? '<span class="review-badge">已复盘</span>' : ''}
                </div>
                <div class="checkin-meta">${formatDate(c.created_at)}</div>
                <div class="checkin-bottleneck">卡点: ${escapeHtml(c.bottleneck_text)}</div>
                <div class="error-tags">
                    ${c.error_types.map(t => `<span class="error-tag">${escapeHtml(t)}</span>`).join('')}
                </div>
            </div>
        `).join('');
        
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        listEl.innerHTML = '<p style="color:red">加载失败</p>';
    }
}

// ============ 教师功能 ============
async function teacherCheckQuota() {
    const studentId = document.getElementById('query-student-id').value.trim();
    const problemId = document.getElementById('query-problem-id').value.trim() || 'P1001';
    
    const resultEl = document.getElementById('teacher-quota-result');
    
    if (!studentId) {
        resultEl.textContent = '请输入学生 ID';
        return;
    }
    
    try {
        const res = await apiFetch(`${API_BASE}/quota/${studentId}/${problemId}`, {
            
        });
        
        if (!res.ok) {
            const err = await res.json();
            resultEl.textContent = err.detail || '查询失败';
            return;
        }
        
        const data = await res.json();
        resultEl.textContent = `学生: ${data.student_id} | 题目: ${data.problem_id} | 已用: ${data.count}/${data.max} | 剩余: ${data.remaining}`;
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        resultEl.textContent = '查询失败';
    }
}

async function teacherResetQuota() {
    const studentId = document.getElementById('reset-student-id').value.trim();
    const problemId = document.getElementById('reset-problem-id').value.trim() || 'P1001';
    
    const resultEl = document.getElementById('reset-result');
    
    if (!studentId) {
        resultEl.textContent = '请输入学生 ID';
        return;
    }
    
    if (!confirm(`确定要重置 ${studentId} 的 ${problemId} 配额吗？`)) return;
    
    try {
        const res = await apiFetch(`${API_BASE}/quota/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ student_id: studentId, problem_id: problemId })
        });
        
        if (!res.ok) {
            const err = await res.json();
            resultEl.textContent = err.detail || '重置失败';
            return;
        }
        
        const data = await res.json();
        resultEl.innerHTML = `<span style="color:green">已重置！${data.student_id} / ${data.problem_id} | 剩余: ${data.remaining}/${data.max}</span>`;
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        resultEl.textContent = '重置失败';
    }
}

async function loadAllCheckins() {
    const listEl = document.getElementById('teacher-checkins-list');
    listEl.innerHTML = '<p>加载中...</p>';
    
    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/checkins`, {
            
        });
        
        if (!res.ok) {
            listEl.innerHTML = '<p style="color:red">加载失败</p>';
            return;
        }
        
        const data = await res.json();
        
        if (data.checkins.length === 0) {
            listEl.innerHTML = '<p>暂无打卡记录</p>';
            return;
        }
        
        listEl.innerHTML = data.checkins.map(c => `
            <div class="checkin-card teacher-card">
                <div class="checkin-header">
                    <span class="student-id">${escapeHtml(c.student_id)}</span>
                    <span class="checkin-title">${escapeHtml(c.problem_title)}</span>
                    <span class="checkin-status status-${c.completion_status}">${statusText(c.completion_status)}</span>
                    ${c.has_review ? '<span class="review-badge">已复盘</span>' : '<span class="pending-badge">待复盘</span>'}
                </div>
                <div class="checkin-meta">${c.oj_source} · ${formatDate(c.created_at)}</div>
                <div class="checkin-bottleneck">卡点: ${escapeHtml(c.bottleneck_text)}</div>
                <div class="error-tags">
                    ${c.error_types.map(t => `<span class="error-tag">${escapeHtml(t)}</span>`).join('')}
                </div>
            </div>
        `).join('');
        
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        listEl.innerHTML = '<p style="color:red">加载失败</p>';
    }
}

async function loadErrorStats() {
    const statsEl = document.getElementById('error-stats');
    statsEl.innerHTML = '<p>加载中...</p>';
    
    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/stats`, {
            
        });
        
        if (!res.ok) {
            statsEl.innerHTML = '<p style="color:red">加载失败</p>';
            return;
        }
        
        const data = await res.json();
        
        if (data.stats.length === 0) {
            statsEl.innerHTML = '<p>暂无统计数据</p>';
            return;
        }
        
        statsEl.innerHTML = `
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>错误类型</th>
                        <th>出现次数</th>
                        <th>平均完成度</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.stats.map(s => `
                        <tr>
                            <td>${escapeHtml(s.error_type)}</td>
                            <td>${s.count}</td>
                            <td>${s.avg_completion_score}/3</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        statsEl.innerHTML = '<p style="color:red">加载失败</p>';
    }
}

async function loadUsageStats() {
    const usageEl = document.getElementById('usage-stats');
    usageEl.innerHTML = '<p>加载中...</p>';
    
    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/usage`, {
            
        });
        
        if (!res.ok) {
            usageEl.innerHTML = '<p style="color:red">加载失败</p>';
            return;
        }
        
        const data = await res.json();
        
        if (data.usage.length === 0) {
            usageEl.innerHTML = '<p>暂无使用数据</p>';
            return;
        }
        
        usageEl.innerHTML = `
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>打卡数</th>
                        <th>被拒绝</th>
                        <th>拒绝率</th>
                        <th>平均卡点字数</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.usage.map(u => {
                        const total = u.checkins + u.rejected;
                        const rejectRate = total > 0 
                            ? Math.round((u.rejected / total) * 100) 
                            : 0;
                        return `
                            <tr>
                                <td>${escapeHtml(u.date)}</td>
                                <td>${u.checkins}</td>
                                <td>${u.rejected}</td>
                                <td>${rejectRate}%</td>
                                <td>${u.avg_chars}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
        
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        usageEl.innerHTML = '<p style="color:red">加载失败</p>';
    }
}

async function loadStudentFlags() {
    const flagsEl = document.getElementById('student-flags');
    flagsEl.innerHTML = '<p>加载中...</p>';
    
    try {
        const res = await apiFetch(`${API_BASE}/api/teacher/flags`, {
            
        });
        
        if (!res.ok) {
            flagsEl.innerHTML = '<p style="color:red">加载失败</p>';
            return;
        }
        
        const data = await res.json();
        
        if (data.flags.length === 0) {
            flagsEl.innerHTML = '<p>暂无需要关注的学员</p>';
            return;
        }
        
        flagsEl.innerHTML = data.flags.map(f => `
            <div class="flag-card severity-${f.severity}">
                <div class="flag-header">
                    <span class="student-id">${escapeHtml(f.student_id)}</span>
                    <span class="flag-type">${escapeHtml(f.flag_type)}</span>
                </div>
                <div class="flag-description">${escapeHtml(f.description)}</div>
            </div>
        `).join('');
        
    } catch (err) {
        if (err.isAuthError) return; // 已由 handleAuthExpired 处理
        flagsEl.innerHTML = '<p style="color:red">加载失败</p>';
    }
}

// ============ 辅助函数 ============
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
    chatHistory = [];
    document.getElementById('chat-history').innerHTML = '';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function statusText(status) {
    const map = {
        independent: '独立完成',
        hinted: '需要提示',
        editorial: '看题解',
        unfinished: '未完成'
    };
    return map[status] || status;
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleString('zh-CN');
}

function showError(elementId, message) {
    document.getElementById(elementId).textContent = message;
}
