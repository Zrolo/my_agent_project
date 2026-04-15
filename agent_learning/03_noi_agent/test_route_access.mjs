import test from 'node:test';
import assert from 'node:assert/strict';

import {
  STUDENT_HOME_PATH,
  TEACHER_HOME_PATH,
  defaultPathForRole,
  isStudentPath,
  isTeacherPath,
  normalizePendingPath,
  resolveRoleRoute,
} from './frontend/src/router/routeAccess.js';

test('defaultPathForRole returns stable student and teacher homes', () => {
  assert.equal(defaultPathForRole('student'), STUDENT_HOME_PATH);
  assert.equal(defaultPathForRole('teacher'), TEACHER_HOME_PATH);
});

test('path helpers distinguish student and teacher shells', () => {
  assert.equal(isTeacherPath('/app/teacher/review'), true);
  assert.equal(isTeacherPath('/app/archive/12'), false);
  assert.equal(isStudentPath('/app/workspace/checkin'), true);
  assert.equal(isStudentPath('/app/teacher/overview'), false);
});

test('normalizePendingPath keeps pending route inside current role shell', () => {
  assert.equal(normalizePendingPath('/app/archive/24', 'student'), '/app/archive/24');
  assert.equal(normalizePendingPath('/app/teacher/review', 'student'), STUDENT_HOME_PATH);
  assert.equal(normalizePendingPath('/app/teacher/checkins', 'teacher'), '/app/teacher/checkins');
  assert.equal(normalizePendingPath('/app/workspace/chat', 'teacher'), TEACHER_HOME_PATH);
});

test('resolveRoleRoute redirects authenticated users away from the wrong shell', () => {
  assert.equal(
    resolveRoleRoute({
      path: '/app/teacher/overview',
      role: 'student',
      isAuthenticated: true,
    }),
    STUDENT_HOME_PATH,
  );
  assert.equal(
    resolveRoleRoute({
      path: '/app/archive/18',
      role: 'teacher',
      isAuthenticated: true,
    }),
    TEACHER_HOME_PATH,
  );
  assert.equal(
    resolveRoleRoute({
      path: '/app/workspace/chat',
      role: 'student',
      isAuthenticated: true,
    }),
    null,
  );
  assert.equal(
    resolveRoleRoute({
      path: '/app/workspace/chat',
      role: 'student',
      isAuthenticated: false,
    }),
    null,
  );
});
