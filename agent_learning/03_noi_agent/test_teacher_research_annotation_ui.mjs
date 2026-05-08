import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const source = readFileSync(
  new URL('./frontend/src/pages/teacher/TeacherResearchAnnotationPage.vue', import.meta.url),
  'utf8',
);

test('research annotation page uses paginated sample selection', () => {
  assert.match(source, /const pageSize =/);
  assert.match(source, /currentPage/);
  assert.match(source, /pagedSamples/);
  assert.match(source, /上一页/);
  assert.match(source, /下一页/);
});

test('research annotation page keeps evidence in fixed scroll regions', () => {
  assert.match(source, /max-h-\[360px\] overflow-y-auto/);
  assert.match(source, /max-h-\[520px\] overflow-y-auto/);
  assert.doesNotMatch(source, /xl:grid-cols-\[360px_minmax\(0,1fr\)\]/);
  assert.doesNotMatch(source, /lg:grid-cols-\[minmax\(0,1fr\)_420px\]/);
});

test('research annotation page shows session context for turn-level judgement', () => {
  assert.match(source, /contextMessages/);
  assert.match(source, /上下文窗口/);
  assert.match(source, /标注当前这一轮，但判断时结合前后文/);
  assert.match(source, /当前学生轮次/);
  assert.match(source, /对应 AI 回复/);
  assert.match(source, /context_messages/);
});

test('research annotation form uses coach-facing labels and visible fields', () => {
  assert.match(source, /桥梁类型/);
  assert.match(source, /已知知识点/);
  assert.match(source, /学生缺的关键一步/);
  assert.match(source, /AI 不应直接给出的部分/);
  assert.match(source, /本轮建议帮助强度/);
  assert.match(source, /只判断当前这一轮学生消息/);
  assert.match(source, /下一轮可根据学生理解变化升降级/);
  assert.match(source, /L1 轻提示/);
  assert.match(source, /L2 半步支架/);
  assert.match(source, /L3 强支架/);
  assert.doesNotMatch(source, />可给帮助程度</);
  assert.match(source, /标注把握度/);
  assert.match(source, /发现新的知识点/);
  assert.match(source, /class="field mt-2 w-full"/);
  assert.match(source, /class="field mt-2 min-h-\[120px\] w-full resize-y"/);
  assert.doesNotMatch(source, />Bridge Family</);
  assert.doesNotMatch(source, />Known Focus</);
  assert.doesNotMatch(source, />Missing Link</);
  assert.doesNotMatch(source, />Forbidden Completion</);
  assert.doesNotMatch(source, />Help Level</);
  assert.doesNotMatch(source, />Notes</);
  assert.doesNotMatch(source, />新 Focus</);
});
