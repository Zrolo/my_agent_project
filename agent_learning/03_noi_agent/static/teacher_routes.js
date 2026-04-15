const OVERVIEW_KIND = 'overview';
const QUOTA_KIND = OVERVIEW_KIND;
const CHECKINS_KIND = 'checkins';
const STATS_KIND = OVERVIEW_KIND;
const MANUAL_REVIEW_KIND = 'review';
const FLAGS_KIND = 'students';
const STUDENTS_KIND = 'students';
const REVIEW_KIND = 'review';

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
  if (normalized === '/app/teacher/quota' || normalized === '/app/teacher/flags' || normalized === '/app/teacher/students') {
    return { kind: STUDENTS_KIND };
  }
  if (normalized === '/app/teacher/checkins') return { kind: CHECKINS_KIND };
  if (normalized === '/app/teacher/manual-review' || normalized === '/app/teacher/review') return { kind: REVIEW_KIND };
  return { kind: OVERVIEW_KIND };
}

function buildTeacherRoute(route = { kind: OVERVIEW_KIND }) {
  const kind = route?.kind || OVERVIEW_KIND;
  if (kind === OVERVIEW_KIND || kind === STATS_KIND || kind === QUOTA_KIND || kind === 'stats' || kind === 'quota') {
    return '/app/teacher/overview';
  }
  if (kind === STUDENTS_KIND || kind === FLAGS_KIND || kind === 'students' || kind === 'flags') {
    return '/app/teacher/students';
  }
  if (kind === CHECKINS_KIND) return '/app/teacher/checkins';
  if (kind === REVIEW_KIND || kind === MANUAL_REVIEW_KIND || kind === 'review' || kind === 'manual-review') {
    return '/app/teacher/review';
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
  normalizePathname,
  parseTeacherRoute,
  buildTeacherRoute,
  getUnauthenticatedFallbackPath,
};

if (typeof window !== 'undefined') {
  window.teacherRoutes = api;
}

export default api;
