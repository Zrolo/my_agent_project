import fs from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';

const appJs = fs.readFileSync(new URL('./static/app.js', import.meta.url), 'utf8');

test('chat response handoff payload is stored with linked chat context', () => {
  assert.match(appJs, /function buildProblemChatContextRecord/);
  assert.match(appJs, /handoffPayload/);
  assert.match(
    appJs,
    /rememberProblemChatContext\(activeChatProblemRef \|\| pid, message, data\.reply, data\.handoff_payload\)/,
  );
});

test('checkin submission sends linked handoff payload when present', () => {
  assert.match(appJs, /const handoffPayload = linkedChatContext\?\.handoffPayload \|\| null/);
  assert.match(appJs, /handoff_payload: handoffPayload/);
});
