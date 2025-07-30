import "babel-polyfill";
import Vue from 'vue';
import App from './App.vue';
import VueRouter from 'vue-router';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";
import setupFetchInterceptor from "@/utils/setupFetchInterceptor";
setupFetchInterceptor();


// Component imports
import index from './components/index.vue';
import admin_dashboard from './components/admin_components/admin_dashboard.vue';
import admin_quiz from './components/admin_components/admin_quiz.vue';
import admin_login from './components/admin_components/admin_login.vue';
import subject_page from './components/admin_components/admin_subject.vue';
import user_login from './components/user_components/user_login.vue';
import user_dashboard from './components/user_components/user_dashboard.vue';
import register from './components/user_components/register.vue';
import sidebar from './components/admin_components/sidebar.vue';
import admin_user from './components/admin_components/admin_user.vue';
import admin_summary from './components/admin_components/admin_summary.vue';
import admin_quiz_mgmt from './components/admin_components/admin_quiz_mgmt.vue';
import admin_chapter_mgmt from './components/admin_components/admin_chapter_mgmt.vue';
import admin_question from './components/admin_components/admin_question.vue';
import user_summary from './components/user_components/user_summary.vue';
import user_scores from './components/user_components/user_scores.vue';
import user_sidebar from './components/user_components/user_sidebar.vue';
import user_subject from './components/user_components/user_subject.vue';
import user_quiz from './components/user_components/user_quiz.vue';
import user_allquiz from './components/user_components/user_allquiz.vue';
import User_subject_quiz from "./components/user_components/user_subject_quiz.vue";
import User_subject_chapter from "./components/user_components/user_subject_chapter.vue";
import user_profile from "./components/user_components/user_profile.vue";
import missedscore from '@/components/user_components/missedscore.vue';


Vue.use(VueRouter);

// Route definitions
const routes = [
  { path: '/', component: index },
  { path: '/admin_login', component: admin_login },
  { path: '/user_login', component: user_login },
  { path: '/register', component: register },
  { path: '/sidebar', component: sidebar },
  { path: '/user_sidebar', component: user_sidebar },

  // Admin protected routes
  { path: '/admin_dashboard', component: admin_dashboard, meta: { requiresAuth: true, role: 'admin' }},
  { path: '/admin/subject/:subject_id/chapter/:chapter_id', component: admin_quiz, meta: { requiresAuth: true, role: 'admin' }},
  { path: '/admin/subject/:subject_id', component: subject_page, meta: { requiresAuth: true, role: 'admin' }},
  { path: '/admin/user', component: admin_user, meta: { requiresAuth: true, role: 'admin' }},
  { path: '/admin/summary', component: admin_summary, meta: { requiresAuth: true, role: 'admin' }},
  { path: '/admin/quiz_mgmt', component: admin_quiz_mgmt, meta: { requiresAuth: true, role: 'admin' }},
  { path: '/admin/chapter_mgmt', component: admin_chapter_mgmt, meta: { requiresAuth: true, role: 'admin' }},
  { path: '/admin/subject/:subject_id/chapter/:chapter_id/quiz/:quiz_id', component: admin_question, meta: { requiresAuth: true, role: 'admin' }},

  // User protected routes
  { path: '/user_dashboard', component: user_dashboard, meta: { requiresAuth: true, role: 'user' }},
  { path: '/user/subject', component: user_subject, meta: { requiresAuth: true, role: 'user' }},
  { path: '/user/scores/:quizId', component: user_scores, name: 'user_scores', meta: { requiresAuth: true, role: 'user' }},
  { path: '/user/summary', component: user_summary, meta: { requiresAuth: true, role: 'user' }},
  { path: '/user/quiz/:quizId', component: user_quiz, name: 'user_quiz', meta: { requiresAuth: true, role: 'user' }},
  { path: '/user/subject/:subject_id/chapter/:chapter_id/quizzes', component: User_subject_quiz, name: 'user_subject_quiz', meta: { requiresAuth: true, role: 'user' }},
  { path: '/user/subject/:subjectId/chapters', component: User_subject_chapter, name: 'user_subject_chapter', meta: { requiresAuth: true, role: 'user' }},
  { path: '/user/quizzes', component: user_allquiz, name: 'user_allquiz', meta: { requiresAuth: true, role: 'user' }},
  { path: '/user/profile', component: user_profile, name: 'user_profile', meta: { requiresAuth: true, role: 'user' }},
  {path: '/user/missed/:quiz_id',name: 'missedscore',component: missedscore,meta: { requiresAuth: true, role: 'user' }},
];

const router = new VueRouter({
  mode: "history",
  routes
});

// Mount app
new Vue({
  el: '#app',
  router,
  render: h => h(App)
});
