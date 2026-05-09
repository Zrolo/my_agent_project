const OVERVIEW_KIND = 'overview';
const QUOTA_KIND = 'class-management';
const CHECKINS_KIND = 'reflection';
const STATS_KIND = OVERVIEW_KIND;
const MANUAL_REVIEW_KIND = 'reflection';
const FLAGS_KIND = 'students';
const STUDENTS_KIND = 'students';
const REVIEW_KIND = 'reflection';
const AICHAT_HISTORY_KIND = 'aichat-history';
const RESEARCH_ANNOTATION_KIND = 'research-annotation';
const RESPONSE_REVIEW_KIND = 'response-review';
const REFLECTION_KIND = 'reflection';
const CLASS_MANAGEMENT_KIND = 'class-management';
const ADVANCED_KIND = 'advanced';

function normalizePathname(pathname = '/app/teacher') {
  const raw = String(pathname || '/app/teacher').trim();
  if (!raw) return '/app/teacher';
  if (raw.length > 1 && raw.endsWith('/')) return raw.slice(0, -1);
  return raw;
}

function parseTeacherRoute(pathname = '/app/teacher') {
  const normalized = normalizePathname(pathname);
  if (normalized === '/app/teacher' || normalized === '/app/teacher/overview' || normalized === '/app/teacher/stats') {
    return { kind: OVERVIEW_KIND };
  }
  if (normalized === '/app/teacher/flags' || normalized === '/app/teacher/students') {
    return { kind: STUDENTS_KIND };
  }
  if (normalized === '/app/teacher/checkins' || normalized === '/app/teacher/manual-review' || normalized === '/app/teacher/review' || normalized === '/app/teacher/reflection') {
    return { kind: REFLECTION_KIND };
  }
  if (normalized === '/app/teacher/quota' || normalized === '/app/teacher/accounts' || normalized === '/app/teacher/announcements' || normalized === '/app/teacher/feedback' || normalized === '/app/teacher/class-management') {
    return { kind: CLASS_MANAGEMENT_KIND };
  }
  if (normalized === '/app/teacher/aichat-history') return { kind: AICHAT_HISTORY_KIND };
  if (normalized === '/app/teacher/research-annotation') return { kind: RESEARCH_ANNOTATION_KIND };
  if (normalized === '/app/teacher/response-review') return { kind: RESPONSE_REVIEW_KIND };
  if (normalized === '/app/teacher/advanced') return { kind: ADVANCED_KIND };
  return { kind: OVERVIEW_KIND };
}

function buildTeacherRoute(route = { kind: OVERVIEW_KIND }) {
  const kind = route?.kind || OVERVIEW_KIND;
  if (kind === OVERVIEW_KIND || kind === STATS_KIND || kind === 'stats') {
    return '/app/teacher/overview';
  }
  if (kind === STUDENTS_KIND || kind === FLAGS_KIND || kind === 'students' || kind === 'flags') {
    return '/app/teacher/students';
  }
  if (kind === CHECKINS_KIND || kind === REVIEW_KIND || kind === MANUAL_REVIEW_KIND || kind === REFLECTION_KIND || kind === 'checkins' || kind === 'review' || kind === 'manual-review' || kind === 'reflection') {
    return '/app/teacher/reflection';
  }
  if (kind === AICHAT_HISTORY_KIND || kind === 'aichat-history') {
    return '/app/teacher/aichat-history';
  }
  if (kind === RESEARCH_ANNOTATION_KIND || kind === 'research-annotation') {
    return '/app/teacher/research-annotation';
  }
  if (kind === RESPONSE_REVIEW_KIND || kind === 'response-review') {
    return '/app/teacher/response-review';
  }
  if (kind === CLASS_MANAGEMENT_KIND || kind === QUOTA_KIND || kind === 'accounts' || kind === 'announcements' || kind === 'feedback' || kind === 'quota' || kind === 'class-management') {
    return '/app/teacher/class-management';
  }
  if (kind === ADVANCED_KIND || kind === 'advanced') {
    return '/app/teacher/advanced';
  }
  return '/app/teacher/overview';
}

function getUnauthenticatedFallbackPath(_pathname = '/app/teacher') {
  return '/app/workspace/chat';
}

const api = {
  OVERVIEW_KIND,
  QUOTA_KIND,
  CHECKINS_KIND,
  STATS_KIND,
  MANUAL_REVIEW_KIND,
  FLAGS_KIND,
  STUDENTS_KIND,
  REVIEW_KIND,
  AICHAT_HISTORY_KIND,
  RESEARCH_ANNOTATION_KIND,
  RESPONSE_REVIEW_KIND,
  REFLECTION_KIND,
  CLASS_MANAGEMENT_KIND,
  ADVANCED_KIND,
  normalizePathname,
  parseTeacherRoute,
  buildTeacherRoute,
  getUnauthenticatedFallbackPath,
};

if (typeof window !== 'undefined') {
  window.teacherRoutes = api;
}

export default api;
