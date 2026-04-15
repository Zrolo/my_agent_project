import fs from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';

const html = fs.readFileSync(
  new URL('./static/index.html', import.meta.url),
  'utf8',
);

test('index exposes a dedicated vue root shell', () => {
  assert.match(html, /<div id="app"><\/div>/);
});

test('index loads built vue assets instead of the legacy app runtime', () => {
  assert.match(html, /\/static\/dist\/assets\/app\.css/);
  assert.match(html, /\/static\/dist\/assets\/app\.js/);
  assert.doesNotMatch(html, /\/static\/app\.js/);
  assert.doesNotMatch(html, /\/static\/js\/main\.js/);
  assert.doesNotMatch(html, /\/static\/js\/router\.js/);
});
