const TOKEN_KEY = 'noi-agent-token';
let unauthorizedHandler = null;

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = typeof handler === 'function' ? handler : null;
}

function buildHeaders(token, extraHeaders = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...extraHeaders,
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

function responseContentType(response) {
  return response?.headers?.get?.('content-type') || '';
}

function looksLikeHtml(text) {
  const trimmed = String(text || '').trim().toLowerCase();
  return trimmed.startsWith('<!doctype html') || trimmed.startsWith('<html') || trimmed.startsWith('<body');
}

function parseJsonResponse(text, response) {
  if (!text) return null;
  const contentType = responseContentType(response).toLowerCase();
  if (contentType.includes('application/json')) {
    return JSON.parse(text);
  }
  if (looksLikeHtml(text)) {
    const error = new Error('服务器暂时没有返回可识别的接口数据，请刷新后重试；如果还不行，说明服务器接口可能出了问题。');
    error.status = response?.status;
    error.rawText = text;
    throw error;
  }
  try {
    return JSON.parse(text);
  } catch {
    const error = new Error('服务器返回的数据格式不对，请稍后再试。');
    error.status = response?.status;
    error.rawText = text;
    throw error;
  }
}

export function formatApiErrorDetail(detail, status) {
  if (status === 401) {
    return '登录已过期，请重新登录';
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message || String(item))
      .filter(Boolean)
      .join('；');
  }
  if (detail && typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }
  return detail || '';
}

async function request(path, { method = 'GET', token, body, headers } = {}) {
  const response = await fetch(path, {
    method,
    headers: buildHeaders(token, headers),
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: 'same-origin',
  });

  const text = await response.text();
  const payload = parseJsonResponse(text, response);

  if (!response.ok) {
    if (response.status === 401 && unauthorizedHandler) {
      unauthorizedHandler();
    }
    const error = new Error(
      formatApiErrorDetail(payload?.detail, response.status) || payload?.message || `Request failed: ${response.status}`,
    );
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

async function requestText(path, { method = 'GET', token, body, headers } = {}) {
  const response = await fetch(path, {
    method,
    headers: buildHeaders(token, headers),
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: 'same-origin',
  });
  const text = await response.text();
  if (!response.ok) {
    if (response.status === 401 && unauthorizedHandler) {
      unauthorizedHandler();
    }
    const error = new Error(text || `Request failed: ${response.status}`);
    error.status = response.status;
    throw error;
  }
  if (looksLikeHtml(text)) {
    const error = new Error('服务器暂时没有返回可识别的接口数据，请刷新后重试；如果还不行，说明服务器接口可能出了问题。');
    error.status = response.status;
    throw error;
  }
  return text;
}

export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_KEY) || '';
}

export function persistToken(token) {
  if (!token) {
    window.localStorage.removeItem(TOKEN_KEY);
    return;
  }
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function login(payload) {
  return request('/auth/login', { method: 'POST', body: payload });
}

export function sendChat(token, payload) {
  return request('/chat', { method: 'POST', token, body: payload });
}

export function getChatModels(token) {
  return request('/api/chat/models', { token });
}

export function getChatHistory(token, params = {}) {
  const query = new URLSearchParams();
  if (params.problem_id) query.set('problem_id', params.problem_id);
  if (params.session_id) query.set('session_id', params.session_id);
  if (params.limit) query.set('limit', String(params.limit));
  return request(`/api/chat/history?${query.toString()}`, { token });
}

export function generateUnderstandingCheck(token, payload) {
  return request('/api/chat/understanding-check/generate', { method: 'POST', token, body: payload });
}

export function gradeUnderstandingCheck(token, payload) {
  return request('/api/chat/understanding-check/grade', { method: 'POST', token, body: payload });
}

export function startProblemClosure(token, payload) {
  return request('/api/chat/problem-closure/start', { method: 'POST', token, body: payload });
}

export function gradeProblemClosure(token, payload) {
  return request('/api/chat/problem-closure/grade', { method: 'POST', token, body: payload });
}

export function getRunnerHealth(token) {
  return request('/api/health/runner', { token });
}

export function runStudentCode(token, payload) {
  return request('/api/student/code/run', { method: 'POST', token, body: payload });
}

export function submitStudentFeedback(token, payload) {
  return request('/api/student/feedback', { method: 'POST', token, body: payload });
}

export function importProblem(token, payload) {
  return request('/api/problem-import', { method: 'POST', token, body: payload });
}

export function createCheckin(token, payload) {
  return request('/api/checkins', { method: 'POST', token, body: payload });
}

export function getMyCheckins(token) {
  return request('/api/checkins/me', { token });
}

export function getCheckinDetail(token, checkinId) {
  return request(`/api/checkins/${checkinId}`, { token });
}

export function getStudentHome(token) {
  return request('/api/student/home', { token });
}

export function createStudentProblemCompletion(token, payload) {
  return request('/api/student/problem-completions', { method: 'POST', token, body: payload });
}

export function getStudentProblemCompletions(token, params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.set('limit', String(params.limit));
  if (params.days) query.set('days', String(params.days));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request(`/api/student/problem-completions${suffix}`, { token });
}

export function getTeacherStats(token) {
  return request('/api/teacher/stats', { token });
}

export function getTeacherClassLearningDiagnosis(token, params = {}) {
  const query = new URLSearchParams();
  if (params.days) query.set('days', String(params.days));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request(`/api/teacher/class-learning-diagnosis${suffix}`, { token });
}

export function getTeacherStudentDossier(token, studentId, params = {}) {
  const query = new URLSearchParams({ student_id: studentId || '' });
  if (params.days) query.set('days', String(params.days));
  return request(`/api/teacher/student-dossier?${query.toString()}`, { token });
}

export function getTeacherStudentNotes(token, studentId) {
  const query = new URLSearchParams({ student_id: studentId || '' });
  return request(`/api/teacher/student-notes?${query.toString()}`, { token });
}

export function createTeacherStudentNote(token, payload) {
  return request('/api/teacher/student-notes', { method: 'POST', token, body: payload });
}

export function getTeacherCheckins(token) {
  return request('/api/teacher/checkins', { token });
}

export function getTeacherStudents(token) {
  return request('/api/teacher/students', { token });
}

export function getTeacherStudentFeedback(token, params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.set('limit', String(params.limit));
  if (params.offset) query.set('offset', String(params.offset));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request(`/api/teacher/student-feedback${suffix}`, { token });
}

export function getTeacherAnnouncements(token, params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.set('limit', String(params.limit));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request(`/api/teacher/announcements${suffix}`, { token });
}

export function createTeacherAnnouncement(token, payload) {
  return request('/api/teacher/announcements', { method: 'POST', token, body: payload });
}

export function getTeacherAIChatObservations(token, params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.set('limit', String(params.limit));
  if (params.days) query.set('days', String(params.days));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request(`/api/teacher/aichat-observations${suffix}`, { token });
}

export function getTeacherAIChatStudents(token) {
  return request('/api/teacher/aichat_students', { token });
}

export function getTeacherAIChatSessions(token, studentId) {
  const query = new URLSearchParams({ student_id: studentId || '' });
  return request(`/api/teacher/aichat_sessions?${query.toString()}`, { token });
}

export function getTeacherAIChatSessionDetail(token, sessionId) {
  const query = new URLSearchParams({ session_id: sessionId || '' });
  return request(`/api/teacher/aichat_session_detail?${query.toString()}`, { token });
}

export function getTeacherAIChatSessionAnalysis(token, sessionId) {
  const query = new URLSearchParams({ session_id: sessionId || '' });
  return request(`/api/teacher/aichat_session_analysis?${query.toString()}`, { token });
}

export function retryTeacherAIChatSessionAnalysis(token, sessionId) {
  return request('/api/teacher/aichat_session_analysis/retry', {
    method: 'POST',
    token,
    body: { session_id: sessionId || '' },
  });
}

export function getTeacherAIChatSessionAnalysisHealth(token, params = {}) {
  const query = new URLSearchParams();
  if (params.days) query.set('days', String(params.days));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request(`/api/teacher/aichat_session_analysis/health${suffix}`, { token });
}

export function createTeacherStudent(token, payload) {
  return request('/api/teacher/students', { method: 'POST', token, body: payload });
}

export function createTeacherStudentsBulk(token, payload) {
  return request('/api/teacher/students/bulk', { method: 'POST', token, body: payload });
}

export function resetTeacherStudentPassword(token, studentId, payload = {}) {
  return request(`/api/teacher/students/${encodeURIComponent(studentId)}/reset-password`, {
    method: 'POST',
    token,
    body: payload,
  });
}

export function updateTeacherStudentStatus(token, studentId, active) {
  return request(`/api/teacher/students/${encodeURIComponent(studentId)}/status`, {
    method: 'POST',
    token,
    body: { active },
  });
}

export function getTeacherReviewSamples(token) {
  return request('/api/teacher/review-samples', { token });
}

export function submitTeacherManualReview(token, reviewId, payload) {
  return request(`/api/teacher/reviews/${reviewId}/manual-review`, {
    method: 'POST',
    token,
    body: payload,
  });
}

export function exportBridgeRuleDraft(token, payload) {
  const params = new URLSearchParams({
    route_kind: payload.route_kind,
    bridge_id: payload.bridge_id,
    days: String(payload.days || 30),
  });
  return requestText(`/api/teacher/bridge-rule-drafts/export?${params.toString()}`, { token });
}

export function submitBridgeRuleDraftDecision(token, payload) {
  return request('/api/teacher/bridge-rule-drafts/decision', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function getBridgeRuleDraftDecisions(token) {
  return request('/api/teacher/bridge-rule-drafts/decisions', { token });
}

export function createBridgeRegistryEntry(token, payload) {
  return request('/api/teacher/bridge-registry/entries', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function getBridgeRegistryEntries(token) {
  return request('/api/teacher/bridge-registry/entries', { token });
}

export function getResolverPatchDraft(token, entryId) {
  return request(`/api/teacher/bridge-registry/entries/${entryId}/resolver-patch-draft`, { token });
}

export function getTeacherFlags(token) {
  return request('/api/teacher/flags', { token });
}
