import { createRouter, createWebHistory } from 'vue-router';
import index from '../components/Student/index.vue';
import userInfo from '../components/Student/UserInfo/UserInfo.vue';
import visualization from '../components/Student/KnowledgeStatus/KnowledgeVisualization.vue';
import knowledgeStructure from '../components/Student/KnowledgeStatus/knowledgeStructure.vue';
import quizChallenge from '../components/Student/QuizRelated/QuizChallenge.vue';
import history from '../components/Student/QuizRelated/History.vue';
import login from '../components/LogRelated/Login.vue';
import register from '../components/LogRelated/Register.vue';
import changePassword from '../components/LogRelated/ChangePassword.vue';
import wechatLogin from '../components/LogRelated/LoginMethod/WechatLogin.vue';
// 教师端组件
import teacherHeader from '../components/Teacher/TeacherHeader.vue';
import personalInfo from '../components/Teacher/Info/PersonalInfo.vue';

const routes = [
  // 添加默认路由重定向到/index
  {
    path: '/',
    redirect: '/index'
  },
  // 学生端路由
  {
    path: '/index',
    name: 'index',
    component: index,
  },
  {
    path: '/visualization',
    name: 'visualization',
    component: visualization,
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
    component: userInfo,
  },
  {
    path: '/knowledge-structure',
    name: 'knowledge-structure',
    component: knowledgeStructure,
  },
  {
    path: '/quiz-challenge',
    name: 'quiz-challenge',
    component: quizChallenge,
  },
  {
    path: '/history',
    name: 'history',
    component: history,
  },
  // 教师端路由
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
  // 可以在这里添加其他路由
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
