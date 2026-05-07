import test from 'node:test';
import assert from 'node:assert/strict';

import {
  createCheckin,
  formatApiErrorDetail,
  login,
  setUnauthorizedHandler,
} from './frontend/src/services/api.js';

test('api error formatter turns validation arrays into readable text', () => {
  assert.equal(
    formatApiErrorDetail([
      { msg: 'List should have at least 1 item after validation, not 0' },
      { msg: "Input should be 'not_submitted'" },
    ]),
    "List should have at least 1 item after validation, not 0；Input should be 'not_submitted'",
  );
});

test('api error formatter keeps simple string details readable', () => {
  assert.equal(formatApiErrorDetail('请填写题目标题'), '请填写题目标题');
});

test('api error formatter localizes expired token responses', () => {
  assert.equal(formatApiErrorDetail('Invalid or expired token', 401), '登录已过期，请重新登录');
});

test('api request invokes unauthorized handler on expired token', async () => {
  const originalFetch = globalThis.fetch;
  let called = false;
  globalThis.fetch = async () => ({
    ok: false,
    status: 401,
    text: async () => JSON.stringify({ detail: 'Invalid or expired token' }),
  });
  setUnauthorizedHandler(() => {
    called = true;
  });

  try {
    await assert.rejects(
      () => createCheckin('expired-token', {}),
      /登录已过期，请重新登录/,
    );
    assert.equal(called, true);
  } finally {
    setUnauthorizedHandler(null);
    globalThis.fetch = originalFetch;
  }
});

test('api request turns html error pages into readable Chinese errors', async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => ({
    ok: false,
    status: 502,
    headers: {
      get(name) {
        return name.toLowerCase() === 'content-type' ? 'text/html; charset=utf-8' : null;
      },
    },
    text: async () => '<html><h1>502 Bad Gateway</h1></html>',
  });

  try {
    await assert.rejects(
      () => createCheckin('token', {}),
      /服务器暂时没有返回可识别的接口数据/,
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('api request turns unexpected html success pages into readable Chinese errors', async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    headers: {
      get(name) {
        return name.toLowerCase() === 'content-type' ? 'text/html; charset=utf-8' : null;
      },
    },
    text: async () => '<html><body>login page</body></html>',
  });

  try {
    await assert.rejects(
      () => login({ user_id: 'student', password: 'pw' }),
      /服务器暂时没有返回可识别的接口数据/,
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});
