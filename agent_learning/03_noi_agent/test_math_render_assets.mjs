import fs from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';

const html = fs.readFileSync(
  new URL('./static/index.html', import.meta.url),
  'utf8',
);

test('index includes local KaTeX stylesheet, local auto-render assets, and Mermaid runtime', () => {
  assert.match(html, /\/static\/vendor\/katex\/katex\.min\.css/);
  assert.match(html, /\/static\/vendor\/katex\/katex\.min\.js/);
  assert.match(html, /\/static\/vendor\/katex\/auto-render\.min\.js/);
  assert.match(html, /mermaid(\.min)?\.js/);
});

test('local KaTeX assets exist in static vendor directory', () => {
  const base = new URL('./static/vendor/katex/', import.meta.url);
  [
    'katex.min.css',
    'katex.min.js',
    'auto-render.min.js',
  ].forEach((file) => {
    const filePath = path.resolve(base.pathname, file);
    assert.equal(fs.existsSync(filePath), true, `${file} should exist`);
  });
});
