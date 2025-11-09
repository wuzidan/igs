<template>
    <div class="app-container">
        <AppSidebar v-if="showSidebar" />
        <main :class="['main-content', { 'has-sidebar': showSidebar }]">
            <router-view />
        </main>
    </div>
</template>

<script setup lang="js">
import AppSidebar from './components/AppSidebar.vue';
import { useRoute } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();
const showSidebar = computed(() => {
  const normalizedPath = route.path.replace(/\/$/, '');
  const routeName = route.name?.toLowerCase() || '';
  console.log('当前路由信息:', { name: route.name, normalizedPath, routeName });
  // 排除教师端路由和登录注册等页面，以及首页，不显示侧边栏
  const excludedRouteNames = [ 'login', 'register', 'change-password', 'wechat-login', 'qq-login', 'other-login', 'student-index','teacher-index'];
  const excludedPaths = [ '/login', '/register', '/change-password', '/wechat-login', '/qq-login', '/other-login', '/index', '/student/index','/teacher/index'];

  return !(excludedRouteNames.includes(routeName)
  || excludedPaths.includes(normalizedPath)
  || normalizedPath.startsWith('/teacher'));
});
</script>

<style scoped>
.app-container {
    display: flex;
    min-height: 100vh;
}

.main-content {
    flex: 1;
    background-color: #f7f8fa;
    margin-left: 0;
    min-height: 100vh;
}

.main-content.has-sidebar {
    margin-left: 250px;
}
</style>
