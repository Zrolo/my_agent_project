import test from 'node:test';
import assert from 'node:assert/strict';
import routes from './static/teacher_routes.js';

test('parseTeacherRoute understands canonical teacher routes', () => {
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/overview'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/stats'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/quota'), { kind: 'class-management' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/accounts'), { kind: 'class-management' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/announcements'), { kind: 'class-management' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/feedback'), { kind: 'class-management' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/class-management'), { kind: 'class-management' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/checkins'), { kind: 'reflection' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/manual-review'), { kind: 'reflection' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/review'), { kind: 'reflection' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/reflection'), { kind: 'reflection' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/flags'), { kind: 'students' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/students'), { kind: 'students' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/aichat-history'), { kind: 'aichat-history' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/advanced'), { kind: 'advanced' });
});

test('parseTeacherRoute falls back to quota for unsupported paths', () => {
  assert.deepEqual(routes.parseTeacherRoute('/app'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/app/teacher/unknown'), { kind: 'overview' });
  assert.deepEqual(routes.parseTeacherRoute('/foo'), { kind: 'overview' });
});

test('buildTeacherRoute emits canonical teacher routes', () => {
  assert.equal(routes.buildTeacherRoute({ kind: 'overview' }), '/app/teacher/overview');
  assert.equal(routes.buildTeacherRoute({ kind: 'checkins' }), '/app/teacher/reflection');
  assert.equal(routes.buildTeacherRoute({ kind: 'review' }), '/app/teacher/reflection');
  assert.equal(routes.buildTeacherRoute({ kind: 'reflection' }), '/app/teacher/reflection');
  assert.equal(routes.buildTeacherRoute({ kind: 'students' }), '/app/teacher/students');
  assert.equal(routes.buildTeacherRoute({ kind: 'stats' }), '/app/teacher/overview');
  assert.equal(routes.buildTeacherRoute({ kind: 'manual-review' }), '/app/teacher/reflection');
  assert.equal(routes.buildTeacherRoute({ kind: 'flags' }), '/app/teacher/students');
  assert.equal(routes.buildTeacherRoute({ kind: 'aichat-history' }), '/app/teacher/aichat-history');
  assert.equal(routes.buildTeacherRoute({ kind: 'accounts' }), '/app/teacher/class-management');
  assert.equal(routes.buildTeacherRoute({ kind: 'class-management' }), '/app/teacher/class-management');
  assert.equal(routes.buildTeacherRoute({ kind: 'advanced' }), '/app/teacher/advanced');
});

test('getUnauthenticatedFallbackPath normalizes teacher pages to public student entry', () => {
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/teacher'), '/app/workspace/chat');
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/teacher/checkins'), '/app/workspace/chat');
  assert.equal(routes.getUnauthenticatedFallbackPath('/app/teacher/stats'), '/app/workspace/chat');
});
