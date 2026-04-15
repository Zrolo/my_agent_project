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
  const payload = text ? JSON.parse(text) : null;

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

export function getTeacherStats(token) {
  return request('/api/teacher/stats', { token });
}

export function getTeacherCheckins(token) {
  return request('/api/teacher/checkins', { token });
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
