import { createRouter, createWebHistory } from 'vue-router';
import visualization from '../components/Student/KnowledgeStatus/KnowledgeVisualization.vue';
// 教师端组件

const routes = [
  // 添加默认路由重定向到/index
  {
    path: '/',
    redirect: '/student/index'
  },
  // 学生端路由
  {
    path: '/student/index',
    name: 'index',
    component: () => import('../components/Student/index.vue'),
  },
  {
    path: '/visualization',
    name: 'visualization',
    component: () => import('../components/Student/KnowledgeStatus/KnowledgeVisualization.vue'),
  },
  {
    path: '/route',
    name: 'route',
    component: () => import('../components/Student/UserInfo/Route.vue'),
  },
  {
    path: '/homework',
    name: 'homework',
    component: () => import('../components/Student/QuizRelated/Homework.vue'),
  },
  {
    path: '/user-info',
    name: 'userInfo',
    component: () => import('../components/Student/UserInfo/UserInfo.vue'),
  },
  {
    path: '/knowledge-structure',
    name: 'knowledge-structure',
    component: () => import('../components/Student/KnowledgeStatus/knowledgeStructure.vue'),
  },
  {
    path: '/quiz-challenge',
    name: 'quiz-challenge',
    component: () => import('../components/Student/QuizRelated/QuizChallenge.vue'),
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../components/Student/QuizRelated/History.vue'),
  },
  // 教师端路由
  {
    path: '/teacher',
    name: 'teacher',
    component: () => import('../components/Teacher/TeacherHeader.vue'),
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
        path: 'exercise/homework',
        name: 'exercise-homework',
        component: () => import('../components/Teacher/Exercise/Homework.vue'),
      },
      {
        path: 'info/personal',
        name: 'teacher-personal-info',
        component: () => import('../components/Teacher/Info/PersonalInfo.vue'),
      },
      {
        path: 'graphs/graph',
        name: 'graph',
        component: () => import('../components/Teacher/Graphs/Graph.vue'),
      },
      {
        path: 'graphs/create',
        name: 'create-graph',
        component: () => import('../components/Teacher/Graphs/CreateGraph.vue'),
      },
      {
        path: 'graphs/edit/new',
        name: 'edit-newgraph',
        component: () => import('../components/Teacher/Graphs/GraphEdit.vue'),
      },
      {
        path: 'index',
        name: 'teacher-index',
        component: () => import('../components/Teacher/index.vue'),
      },
    ],
  },
  // 公共路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('../components/LogRelated/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../components/LogRelated/Register.vue'),
  },
  {
    path: '/change-password',
    name: 'change-password',
    component: () => import('../components/LogRelated/ChangePassword.vue'),
  },
  {
    path: '/wechat-login',
    name: 'wechat-login',
    component: () => import('../components/LogRelated/LoginMethod/WechatLogin.vue'),
  },
  // 可以在这里添加其他路由
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;