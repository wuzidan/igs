<template>
    <!-- 左侧导航栏 -->
    <nav class="sidebar">
        <!-- 高光装饰元素 -->
        <div class="sidebar-glow"></div>

        <div class="logo-container">
            <div class="logo-icon">📚</div>
            <div class="logo-text">智能导学系统-学生端</div>
        </div>

        <ul class="menu">
            <!-- 答题模块 -->
            <li
                class="menu-item"
                :class="{ active: activeMenu === 'answer' }"
                data-menu="answer"
            >
                <div class="menu-title" @click="toggleMenu('answer')">
                    <span class="icon">📝</span>
                    <span>答题模块</span>
                    <span
                        class="arrow"
                        :class="{ rotate: activeMenu === 'answer' }"
                        >▼</span
                    >
                </div>
                <ul class="submenu" v-if="activeMenu === 'answer'">
                    <li>
                        <router-link
                            to="/student/quiz-challenge"
                            :class="{
                                'active-submenu': activeSubmenu === '题库中心',
                            }"
                            @click="setActiveSubmenu('题库中心')"
                        >
                            <span class="submenu-dot"></span>题库中心
                        </router-link>
                    </li>
                    <li>
                        <router-link
                            to="/student/history"
                            :class="{
                                'active-submenu': activeSubmenu === '作答历史',
                            }"
                            @click="setActiveSubmenu('作答历史')"
                        >
                            <span class="submenu-dot"></span>作答历史
                        </router-link>
                    </li>
                </ul>
            </li>

            <li
                class="menu-item"
                :class="{ active: activeMenu === 'knowledge' }"
                data-menu="knowledge"
            >
                <div class="menu-title" @click="toggleMenu('knowledge')">
                    <span class="icon">📊</span>
                    <span>知识状态</span>
                    <span
                        class="arrow"
                        :class="{ rotate: activeMenu === 'knowledge' }"
                        >▼</span
                    >
                </div>
                <ul class="submenu" v-if="activeMenu === 'knowledge'">
                    <li>
                        <router-link
                            to="/student/visualization"
                            :class="{
                                'active-submenu':
                                    activeSubmenu === '状态可视化',
                            }"
                            @click="setActiveSubmenu('状态可视化')"
                        >
                            <span class="submenu-dot"></span>状态可视化
                        </router-link>
                    </li>
                    <li>
                        <router-link
                            to="/student/knowledge-structure"
                            :class="{
                                'active-submenu': activeSubmenu === '知识结构',
                            }"
                            @click="setActiveSubmenu('知识结构')"
                        >
                            <span class="submenu-dot"></span>知识结构
                        </router-link>
                    </li>
                </ul>
            </li>

            <li
                class="menu-item"
                :class="{ active: activeMenu === 'info' }"
                data-menu="info"
            >
                <div class="menu-title" @click="toggleMenu('info')">
                    <span class="icon">👤</span>
                    <span>信息模块</span>
                    <span
                        class="arrow"
                        :class="{ rotate: activeMenu === 'info' }"
                        >▼</span
                    >
                </div>
                <ul class="submenu" v-if="activeMenu === 'info'">
                    <li>
                        <router-link
                            to="/student/user-info"
                            :class="{
                                'active-submenu': activeSubmenu === '个人信息',
                            }"
                            @click="setActiveSubmenu('个人信息')"
                        >
                            <span class="submenu-dot"></span>个人信息
                        </router-link>
                    </li>
                </ul>
            </li>
        </ul>

        <div class="sidebar-footer"></div>
    </nav>
</template>

<script>
import { ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";

export default {
    name: "AppSidebar",
    components: { RouterLink },
    setup() {
        const route = useRoute();
        const activeMenu = ref("knowledge");
        const activeSubmenu = ref("状态可视化");

        // 根据当前路由自动激活对应菜单
        watch(
            () => route.path,
            (newPath) => {
                switch (newPath) {
                    case "/quiz-challenge":
                    case "/student/quiz-challenge":
                        activeMenu.value = "answer";
                        activeSubmenu.value = "题库中心";
                        break;
                    case "/history":
                    case "/student/history":
                        activeMenu.value = "answer";
                        activeSubmenu.value = "作答历史";
                        break;
                    case "/":
                    case "/student/index":
                        activeMenu.value = "knowledge";
                        activeSubmenu.value = "状态可视化";
                        break;
                    case "/knowledge-structure":
                    case "/student/knowledge-structure":
                        activeMenu.value = "knowledge";
                        activeSubmenu.value = "知识结构";
                        break;
                    case "/user-info":
                    case "/student/user-info":
                        activeMenu.value = "info";
                        activeSubmenu.value = "个人信息";
                        break;
                    case "/visualization":
                    case "/student/visualization":
                        activeMenu.value = "knowledge";
                        activeSubmenu.value = "状态可视化";
                        break;
                }
            },
            { immediate: true }
        );

        const toggleMenu = (menuName) => {
            activeMenu.value = activeMenu.value === menuName ? "" : menuName;
        };

        const setActiveSubmenu = (submenuName) => {
            activeSubmenu.value = submenuName;
        };

        return {
            activeMenu,
            activeSubmenu,
            toggleMenu,
            setActiveSubmenu,
        };
    },
};
</script>

<style scoped>
/* 侧边栏基础样式 */
.sidebar {
    width: 260px;
    background: linear-gradient(180deg, #162436 0%, #2c3e50 100%);
    color: #ecf0f1;
    height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 100;
    box-shadow: 2px 0 20px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    transform: translateX(0);
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* 高光效果增强 */
.sidebar-glow {
    position: absolute;
    top: 0;
    right: 0;
    width: 40px;
    height: 100%;
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.03) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    pointer-events: none;
    z-index: 1;
    transition: opacity 0.3s ease;
}

.sidebar:hover .sidebar-glow {
    opacity: 0.8;
}

/* Logo区域动画 */
.logo-container {
    display: flex;
    align-items: center;
    padding: 22px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 20px;
    position: relative;
    z-index: 2;
}

.logo-icon {
    font-size: 26px;
    margin-right: 14px;
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #3498db, #9b59b6);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.logo-container:hover .logo-icon {
    transform: scale(1.05) rotate(5deg);
    box-shadow: 0 6px 20px rgba(52, 152, 219, 0.5);
}

.logo-text {
    font-size: 18px;
    font-weight: 600;
    background: linear-gradient(90deg, #3498db, #ecf0f1);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    transition: letter-spacing 0.3s ease;
    white-space: nowrap;
}

.logo-container:hover .logo-text {
    letter-spacing: 0.5px;
}

/* 菜单基础样式 */
.menu {
    list-style: none;
    padding: 0 12px;
    position: relative;
    z-index: 2;
}

.menu-item {
    margin-bottom: 6px;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
}

/* 主菜单标题动画 */
.menu-title {
    padding: 15px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    font-weight: 500;
    font-size: 16px;
}

.menu-title:hover {
    background-color: rgba(255, 255, 255, 0.08);
    padding-left: 24px;
    transform: translateX(3px);
}

.menu-item.active .menu-title {
    background-color: rgba(52, 152, 219, 0.15);
    color: #3498db;
}

/* 选中状态装饰条动画 */
.menu-item.active .menu-title::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 4px;
    background: linear-gradient(180deg, #3498db, #9b59b6);
    transform: scaleY(0);
    animation: fillHeight 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes fillHeight {
    0% {
        transform: scaleY(0);
    }
    100% {
        transform: scaleY(1);
    }
}

.icon {
    margin-right: 14px;
    font-size: 20px;
    width: 26px;
    text-align: center;
    transition: transform 0.3s ease;
}

.menu-title:hover .icon {
    transform: scale(1.15);
}

/* 箭头动画 */
.arrow {
    font-size: 15px;
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    opacity: 0.7;
    transform-origin: center;
}

.arrow.rotate {
    transform: rotate(-90deg) scale(1.1);
    opacity: 1;
}

/* 子菜单弹出动画 */
.submenu {
    list-style: none;
    overflow: hidden;
    max-height: 0;
    transition: max-height 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    padding-left: 0;
}

.menu-item.active .submenu {
    max-height: 300px;
    padding-left: 0;
}

.submenu li {
    margin: 2px 0;
    opacity: 0;
    transform: translateX(-10px);
    animation: fadeIn 0.3s ease forwards;
}

/* 子菜单项依次出现 */
.menu-item.active .submenu li:nth-child(1) {
    animation-delay: 0.1s;
}
.menu-item.active .submenu li:nth-child(2) {
    animation-delay: 0.2s;
}
.menu-item.active .submenu li:nth-child(3) {
    animation-delay: 0.3s;
}

@keyframes fadeIn {
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* 子菜单链接样式 */
.submenu li a {
    display: flex;
    align-items: center;
    padding: 13px 22px 13px 58px;
    color: #bdc3c7;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border-radius: 6px;
    font-size: 15px;
    position: relative;
    overflow: hidden;
}

/* 子菜单悬停效果 */
.submenu li a:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: #3498db;
    padding-left: 60px;
}

.submenu li a:hover::after {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 3px;
    background: linear-gradient(180deg, #3498db, #9b59b6);
}

/* 子菜单圆点动画 */
.submenu-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: #bdc3c7;
    margin-right: 12px;
    transition: all 0.5s ease;
}

.submenu li a:hover .submenu-dot {
    background-color: #3498db;
    transform: scale(1.3) translateY(1px);
    box-shadow: 0 0 8px rgba(52, 152, 219, 0.6);
}

/* 子菜单选中样式 */
.submenu li a.active-submenu {
    background-color: rgba(52, 152, 219, 0.1);
    color: #3498db;
    font-weight: 500;
}

.submenu li a.active-submenu .submenu-dot {
    background-color: #3498db;
    box-shadow: 0 0 8px rgba(52, 152, 219, 0.6);
}

/* 底部装饰动画 */
.sidebar-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 80px;
    background: linear-gradient(0deg, rgba(155, 89, 182, 0.15), transparent);
    pointer-events: none;
    opacity: 0.7;
    transition: opacity 7s ease, height 0.7s ease;
}

.sidebar:hover .sidebar-footer {
    opacity: 1;
    height: 100px;
}
</style>
