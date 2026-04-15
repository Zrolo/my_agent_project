const CHAT_KIND = 'chat';
const HOME_KIND = CHAT_KIND;
const CHECKIN_KIND = 'checkin';
const HISTORY_LIST_KIND = 'history-list';
const HISTORY_DETAIL_KIND = 'history-detail';

function normalizePathname(pathname = '/app') {
  const raw = String(pathname || '/app').trim();
  if (!raw) return '/app';
  if (raw.length > 1 && raw.endsWith('/')) {
    return raw.slice(0, -1);
  }
  return raw;
}

function parseStudentRoute(pathname = '/app') {
  const normalized = normalizePathname(pathname);
  if (normalized === '/app' || normalized === '/app/chat' || normalized === '/app/workspace/chat') {
    return { kind: CHAT_KIND };
  }
  if (normalized === '/app/checkin' || normalized === '/app/workspace/checkin') {
    return { kind: CHECKIN_KIND };
  }
  if (normalized === '/app/history' || normalized === '/app/archive') {
    return { kind: HISTORY_LIST_KIND };
  }
  const historyMatch = normalized.match(/^\/app\/(?:history|archive)\/(\d+)$/);
  if (historyMatch) {
    return { kind: HISTORY_DETAIL_KIND, checkinId: Number(historyMatch[1]) };
  }
  return { kind: HOME_KIND };
}

function buildStudentRoute(route = { kind: HOME_KIND }) {
  const kind = route?.kind || HOME_KIND;
  if (kind === CHAT_KIND || kind === HOME_KIND) {
    return '/app/workspace/chat';
  }
  if (kind === CHECKIN_KIND) {
    return '/app/workspace/checkin';
  }
  if (kind === HISTORY_LIST_KIND) {
    return '/app/archive';
  }
  if (kind === HISTORY_DETAIL_KIND && Number.isFinite(Number(route.checkinId))) {
    return `/app/archive/${Number(route.checkinId)}`;
  }
  return '/app/workspace/chat';
}

function shouldSeedHistoryParent(route, context = {}) {
  const kind = route?.kind || HOME_KIND;
  if (kind !== HISTORY_DETAIL_KIND) return false;
  const pathname = normalizePathname(context.pathname || buildStudentRoute(route));
  const expectedPath = buildStudentRoute(route);
  if (pathname !== expectedPath) return false;

  const historyLength = Number(context.historyLength || 0);
  if (historyLength > 1) return false;

  const referrer = String(context.referrer || '').trim();
  if (!referrer) return true;
  return !/\/app\/(?:history|archive)(?:\/|$)/.test(referrer);
}

function getUnauthenticatedFallbackPath(_pathname = '/app') {
  return '/app/workspace/chat';
}

function matchesHistoryDetailRoute(pathname = '/app', checkinId = null) {
  const route = parseStudentRoute(pathname);
  if (route.kind !== HISTORY_DETAIL_KIND) return false;
  if (checkinId === null || checkinId === undefined) return true;
  return Number(route.checkinId) === Number(checkinId);
}

const api = {
  HOME_KIND,
  CHAT_KIND,
  CHECKIN_KIND,
  HISTORY_LIST_KIND,
  HISTORY_DETAIL_KIND,
  normalizePathname,
  parseStudentRoute,
  buildStudentRoute,
  shouldSeedHistoryParent,
  getUnauthenticatedFallbackPath,
  matchesHistoryDetailRoute,
};

if (typeof window !== 'undefined') {
  window.studentRoutes = api;
}

export default api;
