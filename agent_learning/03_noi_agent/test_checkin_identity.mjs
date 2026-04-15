import test from 'node:test';
import assert from 'node:assert/strict';

import { buildArchiveDetailPath, resolveCheckinId } from './frontend/src/utils/checkinIdentity.js';

test('resolveCheckinId accepts both legacy checkin_id and list id shapes', () => {
  assert.equal(resolveCheckinId({ checkin_id: 12 }), 12);
  assert.equal(resolveCheckinId({ id: 34 }), 34);
  assert.equal(resolveCheckinId({}), null);
});

test('buildArchiveDetailPath uses the available checkin identifier', () => {
  assert.equal(buildArchiveDetailPath({ checkin_id: 12 }), '/app/archive/12');
  assert.equal(buildArchiveDetailPath({ id: 34 }), '/app/archive/34');
  assert.equal(buildArchiveDetailPath({}), '/app/archive');
});
