import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const pageSource = readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherResponseReviewPage.vue', import.meta.url),
  'utf8',
);
const routerSource = readFileSync(new URL('./frontend/src/router/index.js', import.meta.url), 'utf8');
const layoutSource = readFileSync(new URL('./frontend/src/layouts/TeacherLayout.vue', import.meta.url), 'utf8');
const apiSource = readFileSync(new URL('./frontend/src/services/api.js', import.meta.url), 'utf8');

test('response review page is a small-screen one-card workflow', () => {
  assert.match(pageSource, /一卡一评/);
  assert.match(pageSource, /整体可用性/);
  assert.match(pageSource, /泄露程度/);
  assert.match(pageSource, /AI 回复/);
  assert.match(pageSource, /保存并下一条/);
  assert.match(pageSource, /max-h-\[42vh\] overflow-y-auto/);
});

test('response review page reminds coaches to judge bridge-oriented micro-examples', () => {
  assert.match(pageSource, /桥梁导向微型例子/);
  assert.match(pageSource, /临时填空/);
  assert.match(pageSource, /带着一个桥梁问题观察/);
  assert.match(pageSource, /可迁移规则/);
});

test('response review page supports keyboard shortcuts for quick labeling', () => {
  assert.match(pageSource, /handleKeydown/);
  assert.match(pageSource, /1 = 好/);
  assert.match(pageSource, /Q = 无泄露/);
  assert.match(pageSource, /Enter = 保存并下一条/);
  assert.match(pageSource, /window\.addEventListener\('keydown'/);
});

test('response review page supports dataset batch switching', () => {
  assert.match(pageSource, /评审批次/);
  assert.match(pageSource, /selectedDatasetId/);
  assert.match(pageSource, /getTeacherResponseReviewDatasets/);
  assert.match(pageSource, /dataset_id/);
  assert.match(apiSource, /getTeacherResponseReviewDatasets/);
  assert.match(apiSource, /response-review-datasets/);
});

test('response review page has fast review mode with notes kept visible', () => {
  assert.match(pageSource, /极速盲评/);
  assert.match(pageSource, /评分区/);
  assert.match(pageSource, /不确定/);
  assert.match(pageSource, /一句备注/);
  assert.match(pageSource, /不写备注，直接下一条/);
  assert.match(pageSource, /showAdvancedOptions/);
  assert.match(pageSource, /高级选项/);
});

test('response review page separates reading area from bottom scoring controls', () => {
  assert.match(pageSource, /主阅读区/);
  assert.match(pageSource, /AI 回复是主要判断对象/);
  assert.match(pageSource, /<details class="group/);
  assert.match(pageSource, /展开近期对话/);
  assert.match(pageSource, /收起近期对话/);
  assert.match(pageSource, /主体只负责读/);
  assert.doesNotMatch(pageSource, /max-w-5xl/);
  assert.doesNotMatch(pageSource, /xl:grid-cols-\[minmax\(0,1fr\)_320px\]/);
});

test('response review route and api service are registered', () => {
  assert.match(routerSource, /TeacherResponseReviewPage/);
  assert.match(routerSource, /path: 'response-review'/);
  assert.match(layoutSource, /回复盲评/);
  assert.match(apiSource, /getTeacherResponseReviewItems/);
  assert.match(apiSource, /saveTeacherResponseReviewLabel/);
  assert.match(apiSource, /exportTeacherResponseReviewLabels/);
});
