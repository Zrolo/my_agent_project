export const COMPLETION_STATUS_OPTIONS = [
  { value: 'unfinished', label: '未完成' },
  { value: 'hinted', label: '在提示帮助下完成' },
  { value: 'editorial', label: '看题解后完成' },
  { value: 'independent', label: '独立完成但还不稳' },
];

export const SUBMISSION_RESULT_OPTIONS = [
  { value: 'not_submitted', label: '未提交 / 未说明' },
  { value: 'wa', label: 'WA' },
  { value: 'tle', label: 'TLE' },
  { value: 're', label: 'RE' },
  { value: 'ce', label: 'CE' },
  { value: 'unknown', label: '不确定' },
];

export const DEFAULT_ERROR_TYPES = ['未说明'];

export function inferOjSourceFromProblemRef(problemRef = '') {
  const raw = String(problemRef || '').trim();
  const lower = raw.toLowerCase();
  if (!raw) return 'other';
  if (/^[a-z][a-z0-9_]*$/i.test(raw)) return 'luogu';
  if (lower.includes('luogu.com.cn/problem/') || lower.includes('luogu.com/problem/')) return 'luogu';
  if (lower.includes('codeforces.com/')) return 'codeforces';
  if (lower.includes('atcoder.jp/')) return 'atcoder';
  return 'other';
}

export function ojSourceLabel(source = 'other') {
  return {
    luogu: '洛谷：可自动读取题面',
    codeforces: 'Codeforces：请补标题和题面',
    atcoder: 'AtCoder：请补标题和题面',
    other: '其他来源：请补标题和题面',
  }[source] || '其他来源：请补标题和题面';
}

export function normalizeCheckinPayload(form) {
  const inferredOjSource = inferOjSourceFromProblemRef(form.problem_url);
  return {
    ...form,
    oj_source: inferredOjSource,
    submission_result: form.submission_result || 'not_submitted',
    error_types: form.error_types?.length ? form.error_types : DEFAULT_ERROR_TYPES,
  };
}
