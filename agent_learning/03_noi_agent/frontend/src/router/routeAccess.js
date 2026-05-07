export const STUDENT_HOME_PATH = '/app/home';
export const TEACHER_HOME_PATH = '/app/teacher/overview';

export function isTeacherPath(path = '') {
  return typeof path === 'string' && path.startsWith('/app/teacher');
}

export function isStudentPath(path = '') {
  return typeof path === 'string' && path.startsWith('/app') && !isTeacherPath(path);
}

export function defaultPathForRole(role) {
  return role === 'teacher' ? TEACHER_HOME_PATH : STUDENT_HOME_PATH;
}

export function normalizePendingPath(path, role) {
  if (typeof path !== 'string' || !path.startsWith('/app')) {
    return defaultPathForRole(role);
  }

  if (role === 'teacher') {
    return isTeacherPath(path) ? path : TEACHER_HOME_PATH;
  }

  return isTeacherPath(path) ? STUDENT_HOME_PATH : path;
}

export function resolveRoleRoute({ path, role, isAuthenticated }) {
  if (!isAuthenticated || typeof path !== 'string' || !path.startsWith('/app')) {
    return null;
  }

  if (role === 'teacher' && isStudentPath(path)) {
    return TEACHER_HOME_PATH;
  }

  if (role === 'student' && isTeacherPath(path)) {
    return STUDENT_HOME_PATH;
  }

  return null;
}
