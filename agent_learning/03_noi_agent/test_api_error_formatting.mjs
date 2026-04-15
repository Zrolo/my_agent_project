import test from 'node:test';
import assert from 'node:assert/strict';

import {
  createCheckin,
  formatApiErrorDetail,
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
