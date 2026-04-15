import test from 'node:test';
import assert from 'node:assert/strict';
import routes from './static/student_routes.js';

test('parseStudentRoute understands app home and history routes', () => {
  assert.deepEqual(routes.parseStudentRoute('/app'), { kind: 'chat' });
  assert.deepEqual(routes.parseStudentRoute('/app/chat'), { kind: 'chat' });
  assert.deepEqual(routes.parseStudentRoute('/app/workspace/chat'), { kind: 'chat' });
  assert.deepEqual(routes.parseStudentRoute('/app/checkin'), { kind: 'checkin' });
  assert.deepEqual(routes.parseStudentRoute('/app/workspace/checkin'), { kind: 'checkin' });
  assert.deepEqual(routes.parseStudentRoute('/app/history'), { kind: 'history-list' });
  assert.deepEqual(routes.parseStudentRoute('/app/archive'), { kind: 'history-list' });
  assert.deepEqual(routes.parseStudentRoute('/app/history/42'), { kind: 'history-detail', checkinId: 42 });
  assert.deepEqual(routes.parseStudentRoute('/app/archive/42'), { kind: 'history-detail', checkinId: 42 });
});

test('parseStudentRoute falls back to home for unsupported paths', () => {
  assert.deepEqual(routes.parseStudentRoute('/'), { kind: 'chat' });
  assert.deepEqual(routes.parseStudentRoute('/app/teacher'), { kind: 'chat' });
  assert.deepEqual(routes.parseStudentRoute('/app/history/not-a-number'), { kind: 'chat' });
});

test('buildStudentRoute emits canonical student routes', () => {
  assert.equal(routes.buildStudentRoute({ kind: 'chat' }), '/app/workspace/chat');
  assert.equal(routes.buildStudentRoute({ kind: 'checkin' }), '/app/workspace/checkin');
  assert.equal(routes.buildStudentRoute({ kind: 'history-list' }), '/app/archive');
  assert.equal(routes.buildStudentRoute({ kind: 'history-detail', checkinId: 7 }), '/app/archive/7');
});

test('shouldSeedHistoryParent detects direct history-detail entry without internal parent', () => {
  assert.equal(
    routes.shouldSeedHistoryParent(
      { kind: 'history-detail', checkinId: 7 },
      { pathname: '/app/archive/7', historyLength: 1, referrer: '' },
    ),
    true,
  );
  assert.equal(
    routes.shouldSeedHistoryParent(
      { kind: 'history-detail', checkinId: 7 },
      { pathname: '/app/archive/7', historyLength: 3, referrer: 'http://127.0.0.1:8000/app/archive' },
    ),
    false,
  );
});

test('getUnauthenticatedFallbackPath normalizes protected student paths to public entry', () => {
  assert.equal(routes.getUnauthenticatedFallbackPath('/app'), '/app/workspace/chat');
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/chat'), '/app/workspace/chat');
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/checkin'), '/app/workspace/chat');
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/history'), '/app/workspace/chat');
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/history/42'), '/app/workspace/chat');
});

test('matchesHistoryDetailRoute only matches the active detail pathname and checkin id', () => {
  assert.equal(routes.matchesHistoryDetailRoute('/app/archive/42', 42), true);
  assert.equal(routes.matchesHistoryDetailRoute('/app/archive/42', 7), false);
  assert.equal(routes.matchesHistoryDetailRoute('/app/archive', 42), false);
  assert.equal(routes.matchesHistoryDetailRoute('/app/checkin', 42), false);
});
