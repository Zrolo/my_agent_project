// NOI Agent 前端逻辑

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

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    if (token && userId && userRole) {
        showMainInterface();
    }
    
    // 登录表单
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    
    // 退出
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // 学生功能
    document.getElementById('check-quota-btn').addEventListener('click', studentCheckQuota);
    document.getElementById('send-btn').addEventListener('click', studentSendMessage);
    document.getElementById('clear-history-btn').addEventListener('click', clearChatHistory);
    
    // 教师功能
    document.getElementById('teacher-check-quota-btn').addEventListener('click', teacherCheckQuota);
    document.getElementById('reset-quota-btn').addEventListener('click', teacherResetQuota);
});

// 登录
async function handleLogin(e) {
    e.preventDefault();
    const userIdInput = document.getElementById('user-id').value.trim();
    const password = document.getElementById('password').value;
    
    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
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
        
        // 保存到 localStorage
        localStorage.setItem('noi_token', token);
        localStorage.setItem('noi_user_id', userId);
        localStorage.setItem('noi_user_role', userRole);
        
        showMainInterface();
    } catch (err) {
        showError('login-error', '网络错误，请检查服务是否运行');
    }
}

// 退出
function handleLogout() {
    token = null;
    userId = null;
    userRole = null;
    chatHistory = [];
    
    localStorage.removeItem('noi_token');
    localStorage.removeItem('noi_user_id');
    localStorage.removeItem('noi_user_role');
    
    // 清空所有显示区域（防止数据泄漏给下一个用户）
    document.getElementById('chat-history').innerHTML = '';
    document.getElementById('quota-info').innerHTML = '';
    document.getElementById('teacher-quota-result').innerHTML = '';
    document.getElementById('reset-result').innerHTML = '';
    document.getElementById('student-message').value = '';
    document.getElementById('query-student-id').value = '';
    document.getElementById('query-problem-id').value = 'P1001';
    document.getElementById('reset-student-id').value = '';
    document.getElementById('reset-problem-id').value = 'P1001';
    
    loginSection.classList.remove('hidden');
    studentSection.classList.add('hidden');
    teacherSection.classList.add('hidden');
    userBar.classList.add('hidden');
    
    document.getElementById('login-form').reset();
    document.getElementById('login-error').textContent = '';
}

// 显示主界面
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

// 学生查询配额（安全渲染）
async function studentCheckQuota() {
    const problemId = document.getElementById('student-problem-id').value.trim() || 'P1001';
    
    try {
        const res = await fetch(`${API_BASE}/quota/${userId}/${problemId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const quotaEl = document.getElementById('quota-info');
        
        if (!res.ok) {
            const err = await res.json();
            quotaEl.innerHTML = '';
            const span = document.createElement('span');
            span.className = 'error';
            span.textContent = err.detail || '查询失败';
            quotaEl.appendChild(span);
            return;
        }
        
        const data = await res.json();
        // 使用 textContent 安全渲染动态数据
        quotaEl.textContent = `题目: ${data.problem_id} | 已用: ${data.count}/${data.max} | 剩余: ${data.remaining}`;
    } catch (err) {
        const quotaEl = document.getElementById('quota-info');
        quotaEl.innerHTML = '';
        const span = document.createElement('span');
        span.className = 'error';
        span.textContent = '查询失败';
        quotaEl.appendChild(span);
    }
}

// 学生发送消息
async function studentSendMessage() {
    const problemId = document.getElementById('student-problem-id').value.trim() || 'P1001';
    const message = document.getElementById('student-message').value.trim();
    
    if (!message) return;
    
    // 显示用户消息
    addChatMessage('user', message);
    document.getElementById('student-message').value = '';
    
    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
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
        
        // 更新历史
        chatHistory = data.history;
        
        // 显示回复
        addChatMessage('assistant', data.reply);
        
        // 更新配额显示（安全渲染）
        const q = data.quota;
        document.getElementById('quota-info').textContent = 
            `题目: ${q.problem_id} | 已用: ${q.count}/${q.max} | 剩余: ${q.remaining}`;
    } catch (err) {
        addChatMessage('assistant', '网络错误，请稍后重试');
    }
}

// 添加聊天消息到界面（安全渲染，防XSS）
function addChatMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    const strong = document.createElement('strong');
    strong.textContent = role === 'user' ? '你:' : 'Agent:';
    
    const pre = document.createElement('pre');
    pre.textContent = content;  // 使用 textContent 防止 XSS
    
    div.appendChild(strong);
    div.appendChild(pre);
    
    document.getElementById('chat-history').appendChild(div);
    document.getElementById('chat-history').scrollTop = document.getElementById('chat-history').scrollHeight;
}

// 清空对话
function clearChatHistory() {
    chatHistory = [];
    document.getElementById('chat-history').innerHTML = '';
}

// 教师查询配额（安全渲染）
async function teacherCheckQuota() {
    const studentId = document.getElementById('query-student-id').value.trim();
    const problemId = document.getElementById('query-problem-id').value.trim() || 'P1001';
    
    const resultEl = document.getElementById('teacher-quota-result');
    
    if (!studentId) {
        resultEl.innerHTML = '';
        const span = document.createElement('span');
        span.className = 'error';
        span.textContent = '请输入学生 ID';
        resultEl.appendChild(span);
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/quota/${studentId}/${problemId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!res.ok) {
            const err = await res.json();
            resultEl.innerHTML = '';
            const span = document.createElement('span');
            span.className = 'error';
            span.textContent = err.detail || '查询失败';
            resultEl.appendChild(span);
            return;
        }
        
        const data = await res.json();
        // 使用 textContent 安全渲染动态数据
        resultEl.textContent = `学生: ${data.student_id} | 题目: ${data.problem_id} | 已用: ${data.count}/${data.max} | 剩余: ${data.remaining}`;
    } catch (err) {
        resultEl.innerHTML = '';
        const span = document.createElement('span');
        span.className = 'error';
        span.textContent = '查询失败';
        resultEl.appendChild(span);
    }
}

// 教师重置配额（安全渲染）
async function teacherResetQuota() {
    const studentId = document.getElementById('reset-student-id').value.trim();
    const problemId = document.getElementById('reset-problem-id').value.trim() || 'P1001';
    
    const resultEl = document.getElementById('reset-result');
    
    if (!studentId) {
        resultEl.innerHTML = '';
        const span = document.createElement('span');
        span.className = 'error';
        span.textContent = '请输入学生 ID';
        resultEl.appendChild(span);
        return;
    }
    
    if (!confirm(`确定要重置 ${studentId} 的 ${problemId} 配额吗？`)) return;
    
    try {
        const res = await fetch(`${API_BASE}/quota/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                student_id: studentId,
                problem_id: problemId
            })
        });
        
        if (!res.ok) {
            const err = await res.json();
            resultEl.innerHTML = '';
            const span = document.createElement('span');
            span.className = 'error';
            span.textContent = err.detail || '重置失败';
            resultEl.appendChild(span);
            return;
        }
        
        const data = await res.json();
        // 使用安全方式渲染
        resultEl.innerHTML = '';
        const span = document.createElement('span');
        span.className = 'success';
        span.textContent = `已重置！${data.student_id} / ${data.problem_id} | 剩余: ${data.remaining}/${data.max}`;
        resultEl.appendChild(span);
    } catch (err) {
        resultEl.innerHTML = '';
        const span = document.createElement('span');
        span.className = 'error';
        span.textContent = '重置失败';
        resultEl.appendChild(span);
    }
}

// 显示错误
function showError(elementId, message) {
    document.getElementById(elementId).textContent = message;
}
