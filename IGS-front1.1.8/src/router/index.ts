import { createRouter, createWebHistory } from 'vue-router';
import index from '../components/index.vue';
import userInfo from '../components/Student/UserInfo/UserInfo.vue';
import visualization from '../components/Student/KnowledgeStatus/KnowledgeVisualization.vue';
import knowledgeStructure from '../components/Student/KnowledgeStatus/knowledgeStructure.vue';
import quizChallenge from '../components/Student/QuizRelated/QuizChallenge.vue';
import history from '../components/Student/QuizRelated/History.vue';
import login from '../components/LogRelated/Login.vue';
import register from '../components/LogRelated/Register.vue';
import changePassword from '../components/LogRelated/ChangePassword.vue';
import wechatLogin from '../components/LogRelated/LoginMethod/WechatLogin.vue';
import lyq from '../components/lyq.vue';
// 教师端组件
import teacherHeader from '../components/Teacher/TeacherHeader.vue';
import personalInfo from '../components/Teacher/Info/PersonalInfo.vue';


const routes = [
  // 学生端路由
  {
    path: '/student',
    name: 'student',
    children: [
      {
        path: 'index',
        name: 'student-index',
        component: () => import('../components/student/index.vue'),
      },
      {
        path: 'visualization',
        name: 'student-visualization',
        component: visualization,
      },
      {
        path: 'user-info',
        name: 'student-userInfo',
        component: userInfo,
      },
      {
        path: 'knowledge-structure',
        name: 'student-knowledge-structure',
        component: knowledgeStructure,
      },
      {
        path: 'quiz-challenge',
        name: 'student-quiz-challenge',
        component: quizChallenge,
      },
      {
        path: 'history',
        name: 'student-history',
        component: history,
      },
    ],
  },
  // 保留原来的学生端路由作为重定向，确保兼容性
  {
    path: '/index',
    redirect: '/student/index'
  },
  {
    path: '/visualization',
    redirect: '/student/visualization'
  },
  {
    path: '/user-info',
    redirect: '/student/user-info'
  },
  {
    path: '/knowledge-structure',
    redirect: '/student/knowledge-structure'
  },
  {
    path: '/quiz-challenge',
    redirect: '/student/quiz-challenge'
  },
  {
    path: '/history',
    redirect: '/student/history'
  },
  // 教师端路由
  {
    path: '/teacher/index',
    name: 'teacher-index',
    component: () => import('../components/teacher/index.vue'),
  },
  {
    path: '/teacher',
    name: 'teacher',
    component: teacherHeader,
    children: [
      {
        path: 'class/tracking',
        name: 'class-tracking',
        component: () => import('../components/Teacher/Class/Tracking.vue'),
      },
      {
        path: 'class/info',
        name: 'class-info',
        component: () => import('../components/Teacher/Class/Info.vue'),
      },
      {
        path: 'exercise/existing',
        name: 'exercise-existing',
        component: () => import('../components/Teacher/Exercise/Existing.vue'),
      },
      {
        path: 'exercise/new',
        name: 'exercise-new',
        component: () => import('../components/Teacher/Exercise/New.vue'),
      },
      {
        path: 'exercise/bank',
        name: 'exercise-bank',
        component: () => import('../components/Teacher/Exercise/Bank.vue'),
      },
      {
        path: 'info/personal',
        name: 'teacher-personal-info',
        component: personalInfo,
      },
    ],
  },
  // 公共路由
  {
    path: '/login',
    name: 'Login',
    component: login,
  },
  {
    path: '/register',
    name: 'Register',
    component: register,
  },
  {
    path: '/change-password',
    name: 'change-password',
    component: changePassword,
  },
  {
    path: '/wechat-login',
    name: 'wechat-login',
    component: wechatLogin,
  },
  {
    path: '/lyq',
    name: 'lyq',
    component: lyq,
  },
  // 可以在这里添加其他路由
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;