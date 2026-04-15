export function resolveCheckinId(item) {
  if (!item || typeof item !== 'object') return null;
  return item.checkin_id ?? item.id ?? null;
}

export function buildArchiveDetailPath(item) {
  const id = resolveCheckinId(item);
  return id === null || id === undefined ? '/app/archive' : `/app/archive/${id}`;
}
