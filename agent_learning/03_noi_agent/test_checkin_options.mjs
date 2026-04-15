import test from 'node:test';
import assert from 'node:assert/strict';

import {
  COMPLETION_STATUS_OPTIONS,
  DEFAULT_ERROR_TYPES,
  SUBMISSION_RESULT_OPTIONS,
  inferOjSourceFromProblemRef,
  normalizeCheckinPayload,
} from './frontend/src/constants/checkinOptions.js';

test('checkin completion status options stay aligned with backend accepted values', () => {
  assert.deepEqual(
    COMPLETION_STATUS_OPTIONS.map((option) => option.value),
    ['unfinished', 'hinted', 'editorial', 'independent'],
  );
});

test('checkin submission result options stay aligned with backend accepted values', () => {
  assert.deepEqual(
    SUBMISSION_RESULT_OPTIONS.map((option) => option.value),
    ['not_submitted', 'wa', 'tle', 're', 'ce', 'unknown'],
  );
});

test('checkin payload normalization lets students submit without optional labels', () => {
  const payload = normalizeCheckinPayload({
    problem_url: 'P2249',
    submission_result: '',
    error_types: [],
  });

  assert.equal(payload.submission_result, 'not_submitted');
  assert.deepEqual(payload.error_types, DEFAULT_ERROR_TYPES);
});

test('checkin payload normalization infers oj source from pasted problem ref', () => {
  assert.equal(inferOjSourceFromProblemRef('P2922'), 'luogu');
  assert.equal(inferOjSourceFromProblemRef('https://www.luogu.com.cn/problem/P2922'), 'luogu');
  assert.equal(inferOjSourceFromProblemRef('https://codeforces.com/contest/4/problem/A'), 'codeforces');
  assert.equal(inferOjSourceFromProblemRef('https://atcoder.jp/contests/abc001/tasks/abc001_1'), 'atcoder');
  assert.equal(inferOjSourceFromProblemRef('https://example.com/problem/abc'), 'other');

  const payload = normalizeCheckinPayload({
    oj_source: 'luogu',
    problem_url: 'https://codeforces.com/contest/4/problem/A',
    submission_result: '',
    error_types: [],
  });

  assert.equal(payload.oj_source, 'codeforces');
});
