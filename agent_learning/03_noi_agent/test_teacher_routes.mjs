import test from 'node:test';
import assert from 'node:assert/strict';
import routes from './static/teacher_routes.js';

test('parseTeacherRoute understands canonical teacher routes', () => {
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/overview'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/stats'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/quota'), { kind: 'students' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/checkins'), { kind: 'checkins' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/manual-review'), { kind: 'review' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/review'), { kind: 'review' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/flags'), { kind: 'students' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/students'), { kind: 'students' });
});

test('parseTeacherRoute falls back to quota for unsupported paths', () => {
  assert.deepEqual(routes.parseTeacherRoute('/app'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/unknown'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/foo'), { kind: 'overview' });
});

test('buildTeacherRoute emits canonical teacher routes', () => {
  assert.equal(routes.buildTeacherRoute({ kind: 'overview' }), '/app/teacher/overview');
  assert.equal(routes.buildTeacherRoute({ kind: 'checkins' }), '/app/teacher/checkins');
  assert.equal(routes.buildTeacherRoute({ kind: 'review' }), '/app/teacher/review');
  assert.equal(routes.buildTeacherRoute({ kind: 'students' }), '/app/teacher/students');
  assert.equal(routes.buildTeacherRoute({ kind: 'stats' }), '/app/teacher/overview');
  assert.equal(routes.buildTeacherRoute({ kind: 'manual-review' }), '/app/teacher/review');
  assert.equal(routes.buildTeacherRoute({ kind: 'flags' }), '/app/teacher/students');
});

test('getUnauthenticatedFallbackPath normalizes teacher pages to public student entry', () => {
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/teacher'), '/app/workspace/chat');
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/teacher/checkins'), '/app/workspace/chat');
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/teacher/stats'), '/app/workspace/chat');
});
