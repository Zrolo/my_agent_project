import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { resolveRoleRoute } from '@/router/routeAccess';

import StudentLayout from '@/layouts/StudentLayout.vue';
import TeacherLayout from '@/layouts/TeacherLayout.vue';

const HomePage = () => import('@/pages/student/HomePage.vue');
const ChatPage = () => import('@/pages/student/ChatPage.vue');
const CheckinPage = () => import('@/pages/student/CheckinPage.vue');
const ArchiveListPage = () => import('@/pages/student/ArchiveListPage.vue');
const ArchiveDetailPage = () => import('@/pages/student/ArchiveDetailPage.vue');
const FeedbackPage = () => import('@/pages/student/FeedbackPage.vue');
const KnowledgePage = () => import('@/pages/student/KnowledgePage.vue');
const TeacherOverviewPage = () => import('@/pages/teacher/TeacherOverviewPage.vue');
const TeacherReviewPage = () => import('@/pages/teacher/TeacherReviewPage.vue');
const TeacherStudentsPage = () => import('@/pages/teacher/TeacherStudentsPage.vue');
const TeacherStudentDossierPage = () => import('@/pages/teacher/TeacherStudentDossierPage.vue');
const TeacherAccountsPage = () => import('@/pages/teacher/TeacherAccountsPage.vue');
const TeacherCheckinsPage = () => import('@/pages/teacher/TeacherCheckinsPage.vue');
const TeacherFeedbackPage = () => import('@/pages/teacher/TeacherFeedbackPage.vue');
const TeacherAnnouncementsPage = () => import('@/pages/teacher/TeacherAnnouncementsPage.vue');
const TeacherAIChatHistoryPage = () => import('@/pages/teacher/TeacherAIChatHistoryPage.vue');
const TeacherResearchAnnotationPage = () => import('@/pages/teacher/TeacherResearchAnnotationPage.vue');
const TeacherResponseReviewPage = () => import('@/pages/teacher/TeacherResponseReviewPage.vue');
const TeacherReflectionPage = () => import('@/pages/teacher/TeacherReflectionPage.vue');
const TeacherClassManagementPage = () => import('@/pages/teacher/TeacherClassManagementPage.vue');

const routes = [
  { path: '/app', redirect: '/app/home' },
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
        path: 'home',
        name: 'student-home',
        component: HomePage,
        meta: { section: 'home' },
      },
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
        path: 'workspace/knowledge',
        name: 'student-knowledge',
        component: KnowledgePage,
        meta: { section: 'knowledge' },
      },
      {
        path: 'workspace/feedback',
        name: 'student-feedback',
        component: FeedbackPage,
        meta: { section: 'feedback' },
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
  { path: '/app/teacher/manual-review', redirect: { path: '/app/teacher/reflection', query: { tab: 'review' } } },
  { path: '/app/teacher/review', redirect: { path: '/app/teacher/reflection', query: { tab: 'review' } } },
  { path: '/app/teacher/checkins', redirect: { path: '/app/teacher/reflection', query: { tab: 'checkins' } } },
  { path: '/app/teacher/stats', redirect: '/app/teacher/overview' },
  { path: '/app/teacher/quota', redirect: { path: '/app/teacher/class-management', query: { tab: 'accounts' } } },
  { path: '/app/teacher/accounts', redirect: { path: '/app/teacher/class-management', query: { tab: 'accounts' } } },
  { path: '/app/teacher/announcements', redirect: { path: '/app/teacher/class-management', query: { tab: 'announcements' } } },
  { path: '/app/teacher/feedback', redirect: { path: '/app/teacher/class-management', query: { tab: 'feedback' } } },
  { path: '/app/teacher/advanced', redirect: { path: '/app/teacher/class-management', query: { tab: 'advanced' } } },
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
        path: 'reflection',
        name: 'teacher-reflection',
        component: TeacherReflectionPage,
        meta: { section: 'reflection' },
      },
      {
        path: 'students',
        name: 'teacher-students',
        component: TeacherStudentsPage,
        meta: { section: 'students' },
      },
      {
        path: 'students/:studentId',
        name: 'teacher-student-dossier',
        component: TeacherStudentDossierPage,
        props: true,
        meta: { section: 'students' },
      },
      {
        path: 'aichat-history',
        name: 'teacher-aichat-history',
        component: TeacherAIChatHistoryPage,
        meta: { section: 'aichat-history' },
      },
      {
        path: 'research-annotation',
        name: 'teacher-research-annotation',
        component: TeacherResearchAnnotationPage,
        meta: { section: 'research-annotation' },
      },
      {
        path: 'response-review',
        name: 'teacher-response-review',
        component: TeacherResponseReviewPage,
        meta: { section: 'response-review' },
      },
      {
        path: 'class-management',
        name: 'teacher-class-management',
        component: TeacherClassManagementPage,
        meta: { section: 'class-management' },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/app/home' },
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
