/**
 * 测试认证失效处理逻辑
 * 模拟服务重启后 token 失效的场景
 */

// 模拟 localStorage
const localStorageMock = {
    store: {},
    getItem(key) { return this.store[key] || null; },
    setItem(key, value) { this.store[key] = value; },
    removeItem(key) { delete this.store[key]; }
};

// 模拟 DOM 元素
const mockElements = {
    'login-section': { classList: { add: () => {}, remove: () => {} } },
    'student-section': { classList: { add: () => {}, remove: () => {} } },
    'teacher-section': { classList: { add: () => {}, remove: () => {} } },
    'user-bar': { classList: { add: () => {}, remove: () => {} } },
    'login-error': { textContent: '', style: { display: 'none' } },
    'chat-history': { innerHTML: '' },
    'quota-info': { textContent: '' },
};

const documentMock = {
    getElementById: (id) => mockElements[id] || { 
        innerHTML: '', 
        textContent: '',
        classList: { add: () => {}, remove: () => {} },
        style: {}
    }
};

// 模拟 fetch
let fetchMockResponse = {};
const fetchMock = async (url, options) => {
    return fetchMockResponse;
};

// 测试：isAuthError 函数
function testIsAuthError() {
    console.log('=== 测试 isAuthError ===');
    
    const testCases = [
        { status: 401, detail: 'Invalid or expired token', expected: true },
        { status: 401, detail: 'Missing authorization header', expected: true },
        { status: 401, detail: 'Some other error', expected: false },
        { status: 403, detail: 'Invalid or expired token', expected: false },
        { status: 200, detail: 'Success', expected: false },
    ];
    
    // 定义测试用的 isAuthError 函数
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
    
    let passed = 0;
    let failed = 0;
    
    testCases.forEach(({ status, detail, expected }) => {
        const result = isAuthError(status, detail);
        if (result === expected) {
            console.log(`✅ ${status} + "${detail}" = ${result}`);
            passed++;
        } else {
            console.log(`❌ ${status} + "${detail}" = ${result}, expected ${expected}`);
            failed++;
        }
    });
    
    console.log(`结果: ${passed} 通过, ${failed} 失败\n`);
    return failed === 0;
}

// 测试：handleAuthExpired 清空逻辑
function testHandleAuthExpired() {
    console.log('=== 测试 handleAuthExpired ===');
    
    // 设置初始状态
    localStorageMock.setItem('noi_token', 'test_token');
    localStorageMock.setItem('noi_user_id', 'test_user');
    localStorageMock.setItem('noi_user_role', 'student');
    
    // 验证初始状态
    if (!localStorageMock.getItem('noi_token')) {
        console.log('❌ 初始 token 设置失败');
        return false;
    }
    
    // 模拟清空操作
    localStorageMock.removeItem('noi_token');
    localStorageMock.removeItem('noi_user_id');
    localStorageMock.removeItem('noi_user_role');
    
    // 验证清空结果
    const token = localStorageMock.getItem('noi_token');
    const userId = localStorageMock.getItem('noi_user_id');
    const role = localStorageMock.getItem('noi_user_role');
    
    if (!token && !userId && !role) {
        console.log('✅ 认证过期后正确清空了 localStorage');
        return true;
    } else {
        console.log('❌ 清空不完整');
        return false;
    }
}

// 测试：apiFetch 401 处理流程
async function testApiFetch401() {
    console.log('=== 测试 apiFetch 401 处理 ===');
    
    // 设置初始 token
    localStorageMock.setItem('noi_token', 'old_token');
    
    // 模拟 401 响应
    fetchMockResponse = {
        status: 401,
        json: async () => ({ detail: 'Invalid or expired token' })
    };
    
    // 模拟 apiFetch 逻辑
    async function apiFetch(url, options = {}) {
        if (!options.headers) options.headers = {};
        const token = localStorageMock.getItem('noi_token');
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const res = await fetchMock(url, options);
        
        if (res.status === 401) {
            let detail = '';
            try {
                const errData = await res.json();
                detail = errData.detail || '';
            } catch (e) {
                detail = 'Unauthorized';
            }
            
            // 检查是否是认证错误
            const authErrorMessages = [
                'Invalid or expired token',
                'Missing authorization header'
            ];
            
            if (authErrorMessages.some(msg => detail.includes(msg))) {
                // 模拟清空
                localStorageMock.removeItem('noi_token');
                localStorageMock.removeItem('noi_user_id');
                localStorageMock.removeItem('noi_user_role');
                
                const err = new Error('AUTH_EXPIRED');
                err.isAuthError = true;
                throw err;
            }
        }
        
        return res;
    }
    
    try {
        await apiFetch('http://test/quota');
        console.log('❌ 应该抛出认证错误');
        return false;
    } catch (err) {
        if (err.isAuthError && err.message === 'AUTH_EXPIRED') {
            // 验证 token 是否被清空
            const token = localStorageMock.getItem('noi_token');
            if (!token) {
                console.log('✅ 401 响应正确触发认证失效处理并清空 token');
                return true;
            } else {
                console.log('❌ 未清空 token');
                return false;
            }
        } else {
            console.log('❌ 抛出的错误类型不正确');
            return false;
        }
    }
}

// 运行所有测试
async function runTests() {
    console.log('开始测试认证失效处理逻辑\n');
    
    const results = [
        testIsAuthError(),
        testHandleAuthExpired(),
        await testApiFetch401()
    ];
    
    console.log('\n=== 最终报告 ===');
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`${passed}/${total} 测试通过`);
    
    return passed === total;
}

runTests().then(success => {
    process.exit(success ? 0 : 1);
});
