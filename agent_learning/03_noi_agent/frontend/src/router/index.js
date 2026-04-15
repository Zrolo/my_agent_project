import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { resolveRoleRoute } from '@/router/routeAccess';

import StudentLayout from '@/layouts/StudentLayout.vue';
import TeacherLayout from '@/layouts/TeacherLayout.vue';
import ChatPage from '@/pages/student/ChatPage.vue';
import CheckinPage from '@/pages/student/CheckinPage.vue';
import ArchiveListPage from '@/pages/student/ArchiveListPage.vue';
import ArchiveDetailPage from '@/pages/student/ArchiveDetailPage.vue';
import TeacherOverviewPage from '@/pages/teacher/TeacherOverviewPage.vue';
import TeacherReviewPage from '@/pages/teacher/TeacherReviewPage.vue';
import TeacherStudentsPage from '@/pages/teacher/TeacherStudentsPage.vue';
import TeacherCheckinsPage from '@/pages/teacher/TeacherCheckinsPage.vue';

const routes = [
  { path: '/app', redirect: '/app/workspace/chat' },
  { path: '/app/chat', redirect: '/app/workspace/chat' },
  { path: '/app/checkin', redirect: '/app/workspace/checkin' },
  { path: '/app/history', redirect: '/app/archive' },
  {
    path: '/app/history/:checkinId(\\d+)',
    redirect: (to) => `/app/archive/${to.params.checkinId}`,
  },
  {
    path: '/app',
    component: StudentLayout,
    meta: { shell: 'student', requiredRole: 'student' },
    children: [
      {
        path: 'workspace/chat',
        name: 'student-chat',
        component: ChatPage,
        meta: { section: 'chat' },
      },
      {
        path: 'workspace/checkin',
        name: 'student-checkin',
        component: CheckinPage,
        meta: { section: 'checkin' },
      },
      {
        path: 'archive',
        name: 'student-archive',
        component: ArchiveListPage,
        meta: { section: 'archive' },
      },
      {
        path: 'archive/:checkinId(\\d+)',
        name: 'student-archive-detail',
        component: ArchiveDetailPage,
        props: true,
        meta: { section: 'archive' },
      },
    ],
  },
  { path: '/app/teacher', redirect: '/app/teacher/overview' },
  { path: '/app/teacher/manual-review', redirect: '/app/teacher/review' },
  { path: '/app/teacher/stats', redirect: '/app/teacher/overview' },
  { path: '/app/teacher/quota', redirect: '/app/teacher/students' },
  { path: '/app/teacher/flags', redirect: '/app/teacher/students' },
  {
    path: '/app/teacher',
    component: TeacherLayout,
    meta: { shell: 'teacher', requiredRole: 'teacher' },
    children: [
      {
        path: 'overview',
        name: 'teacher-overview',
        component: TeacherOverviewPage,
        meta: { section: 'overview' },
      },
      {
        path: 'review',
        name: 'teacher-review',
        component: TeacherReviewPage,
        meta: { section: 'review' },
      },
      {
        path: 'students',
        name: 'teacher-students',
        component: TeacherStudentsPage,
        meta: { section: 'students' },
      },
      {
        path: 'checkins',
        name: 'teacher-checkins',
        component: TeacherCheckinsPage,
        meta: { section: 'checkins' },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/app/workspace/chat' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  auth.restore();

  if (!to.meta?.requiredRole) {
    return true;
  }

  if (!auth.isAuthenticated) {
    auth.setPendingPath(to.fullPath);
    return true;
  }

  return resolveRoleRoute({
    path: to.fullPath,
    role: auth.role,
    isAuthenticated: auth.isAuthenticated,
  }) || true;
});

export default router;
