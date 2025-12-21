<template>
    <div class="teacher-index-container">
        <!-- 布局容器 -->
        <div class="layout">
            <!-- 侧边栏 -->
            <TeacherSidebar />

            <!-- 主内容区域 -->
            <div class="main-content">
                <header class="page-header">
                    <div class="header-gradient"></div>
                    <div class="header-highlight"></div>
                    <div class="header-wave"></div>
                    <div class="header-content">
                        <div class="header-title">
                            <h1>{{ pageTitle }}</h1>
                            <p>{{ pageDescription }}</p>
                        </div>

                        <!-- 用户菜单和通知区域 - 调整容器样式使内容左移 -->
                        <div class="user-notification-area">
                            <!-- 通知图标 - 调整位置 -->
                            <div
                                class="notification-icon"
                                @click.stop="toggleNotificationPanel"
                            >
                                🔔
                                <span
                                    class="notification-badge"
                                    v-if="unreadCount > 0"
                                    >{{ unreadCount }}</span
                                >
                            </div>

                            <!-- 用户菜单触发区域 - 调整布局以显示更多信息 -->
                            <div
                                class="user-menu-trigger"
                                @click.stop="toggleUserMenu"
                            >
                                <div class="user-info">
                                    <!-- 显示教师姓名和账号 -->
                                    <div class="user-details">
                                        <div class="user-name">
                                            {{ userName }}
                                        </div>
                                        <div class="user-account">
                                            {{ userAccount }}
                                        </div>
                                    </div>
                                    <div class="user-avatar">
                                        <img
                                            v-if="userAvatarUrl"
                                            :src="userAvatarUrl"
                                            alt="用户头像"
                                        />
                                        <span v-else>{{ userAvatar }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                <!-- 页面内容 -->
                <main class="content">
                    <RouterView />
                </main>
            </div>
        </div>

        <!-- 通知面板 -->
        <div
            v-if="showNotificationPanel"
            class="notification-panel-container"
            @click.stop
        >
            <div class="notification-panel">
                <div class="notification-panel-header">
                    <h3>通知消息</h3>
                    <button
                        class="mark-all-read"
                        @click="markAllAsRead"
                        v-if="unreadCount > 0"
                    >
                        全部标为已读
                    </button>
                </div>

                <div class="notification-list">
                    <div
                        v-for="notification in notifications"
                        :key="notification.id"
                        class="notification-item"
                        :class="{
                            unread: !notification.read,
                        }"
                        @click="viewNotificationDetail(notification.id)"
                    >
                        <div class="notification-icon-type">
                            {{
                                notification.type === "exercise"
                                    ? "📝"
                                    : notification.type === "system"
                                    ? "🔧"
                                    : notification.type === "student"
                                    ? "👨‍🎓"
                                    : "📢"
                            }}
                        </div>
                        <div class="notification-content">
                            <div class="notification-title">
                                {{ notification.title }}
                            </div>
                            <div class="notification-time">
                                {{ formatTime(notification.time) }}
                            </div>
                        </div>
                    </div>

                    <div
                        class="no-notifications"
                        v-if="notifications.length === 0"
                    >
                        暂无通知消息
                    </div>
                </div>
            </div>
        </div>

        <!-- 用户下拉菜单 -->
        <div v-if="showUserMenu" class="global-user-dropdown" @click.stop>
            <div class="user-dropdown">
                <ul>
                    <li @click="navigateTo('personal-info')">
                        <span class="user-dropdown-icon">👤</span>
                        个人信息
                    </li>
                    <li @click="navigateTo('settings')">
                        <span class="user-dropdown-icon">⚙️</span>
                        设置
                    </li>
                    <li class="logout-item" @click="logout">
                        <span class="user-dropdown-icon">🚪</span>
                        退出登录
                    </li>
                </ul>
            </div>
        </div>

        <!-- 通知详情模态框 -->
        <div
            v-if="showNotificationDetail"
            class="modal-backdrop"
            @click="closeNotificationDetail"
        >
            <div class="notification-detail-modal" @click.stop>
                <div class="modal-header">
                    <h3>通知详情</h3>
                    <button class="close-btn" @click="closeNotificationDetail">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="modal-body">
                    <div v-if="currentNotification" class="detail-wrapper">
                        <div class="notification-detail-header">
                            <div class="detail-icon">
                                {{
                                    currentNotification.type === "exercise"
                                        ? "📝"
                                        : currentNotification.type === "system"
                                        ? "🔧"
                                        : currentNotification.type === "student"
                                        ? "👨‍🎓"
                                        : "📢"
                                }}
                            </div>
                            <div class="detail-header-text">
                                <h4>{{ currentNotification.title }}</h4>
                                <div class="detail-time">
                                    {{ formatDate(currentNotification.time) }}
                                </div>
                            </div>
                        </div>

                        <div class="notification-detail-content">
                            <p>{{ currentNotification.content }}</p>

                            <!-- 习题通知详情 -->
                            <div
                                v-if="currentNotification.type === 'exercise'"
                                class="notification-details-card exercise-details"
                            >
                                <div class="detail-item">
                                    <span class="detail-label">学生:</span>
                                    <span class="detail-value">{{
                                        currentNotification.details.studentName
                                    }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">习题名称:</span>
                                    <span class="detail-value">{{
                                        currentNotification.details.exerciseName
                                    }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">提交时间:</span>
                                    <span class="detail-value">{{
                                        formatDate(
                                            currentNotification.details
                                                .submissionTime
                                        )
                                    }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">题目数量:</span>
                                    <span class="detail-value"
                                        >{{
                                            currentNotification.details
                                                .totalQuestions
                                        }}题</span
                                    >
                                </div>

                                <div class="detail-actions">
                                    <button
                                        class="btn btn-primary"
                                        @click="gotoExerciseCorrection"
                                    >
                                        前往批改
                                    </button>
                                </div>
                            </div>

                            <!-- 学生提问详情 -->
                            <div
                                v-if="currentNotification.type === 'student'"
                                class="notification-details-card student-question-details"
                            >
                                <div class="detail-item">
                                    <span class="detail-label">学生:</span>
                                    <span class="detail-value">{{
                                        currentNotification.details.studentName
                                    }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">章节:</span>
                                    <span class="detail-value">{{
                                        currentNotification.details.chapter
                                    }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">问题:</span>
                                    <span class="detail-value">{{
                                        currentNotification.details.question
                                    }}</span>
                                </div>

                                <div class="detail-actions">
                                    <button
                                        class="btn btn-primary"
                                        @click="gotoAnswerQuestion"
                                    >
                                        前往解答
                                    </button>
                                </div>
                            </div>

                            <!-- 系统通知详情 -->
                            <div
                                v-if="currentNotification.type === 'system'"
                                class="notification-details-card system-notification-details"
                            >
                                <div class="detail-item">
                                    <span class="detail-label">版本:</span>
                                    <span class="detail-value">{{
                                        currentNotification.details.version
                                    }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">维护时间:</span>
                                    <span class="detail-value">{{
                                        formatDate(
                                            currentNotification.details
                                                .startTime
                                        ) +
                                        " 至 " +
                                        formatDate(
                                            currentNotification.details.endTime
                                        )
                                    }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">更新内容:</span>
                                    <span class="detail-value">
                                        <ul>
                                            <li
                                                v-for="(
                                                    feature, index
                                                ) in currentNotification.details
                                                    .features"
                                                :key="index"
                                            >
                                                {{ feature }}
                                            </li>
                                        </ul>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import TeacherSidebar from "./TeacherSidebar.vue";
import request from "../../utils/request";

const router = useRouter();

// 页面标题和描述
const pageTitle = ref("智能导学平台");
const pageDescription = ref(
    "欢迎使用智能编程技能学习系统教师端 - 助力学生高效掌握编程技能"
);

// 用户信息 - 新增账号信息
const userAvatar = ref("👨🏫");
const userAvatarUrl = ref("");
const userName = ref("");
const userAccount = ref(""); // 新增教师账号信息

const isLoggedIn = ref(
    !!(window.localStorage && window.localStorage.getItem("token"))
);

const fetchTeacherInfo = async () => {
    if (!isLoggedIn.value) {
        return;
    }
    try {
        const resp = await request.get("/teacher/profile/");
        const data = resp?.data || {};

        if (typeof data.teacherName === "string" && data.teacherName) {
            userName.value = data.teacherName;
        }
        if (typeof data.teacherId === "string" && data.teacherId) {
            userAccount.value = data.teacherId;
        }
        if (typeof data.avatarUrl === "string" && data.avatarUrl) {
            userAvatarUrl.value = data.avatarUrl;
        }
    } catch (e) {
        console.error("获取教师信息失败", e);
        isLoggedIn.value = false;
        try {
            window.localStorage && window.localStorage.removeItem("token");
        } catch (err) {
            console.error("清理登录状态失败", err);
        }
        try {
            router.push("/login");
        } catch (err) {
            console.error("路由跳转失败", err);
        }
    }
};

onMounted(async () => {
    await fetchTeacherInfo();
});

// 用户菜单状态
const showUserMenu = ref(false);

// 通知相关状态
const showNotificationPanel = ref(false);
const showNotificationDetail = ref(false);
const currentNotification = ref(null);
const notifications = ref([
    {
        id: 1,
        type: "exercise", // 习题相关
        title: "学生习题已完成",
        content: "张明已完成JavaScript高级特性习题，等待您的批改",
        time: new Date(Date.now() - 30 * 60000).toISOString(), // 30分钟前
        read: false,
        details: {
            studentName: "张明",
            exerciseName: "JavaScript高级特性",
            submissionTime: new Date(Date.now() - 35 * 60000).toISOString(),
            exerciseId: "ex-1024",
            totalQuestions: 15,
            attemptedQuestions: 15,
            studentId: "DEV2023001",
        },
    },
    {
        id: 2,
        type: "student", // 学生相关
        title: "学生提问",
        content: "李华对Python数据结构章节提出了疑问",
        time: new Date(Date.now() - 4 * 3600000).toISOString(), // 4小时前
        read: false,
        details: {
            studentName: "李华",
            question: "关于二叉树遍历的具体实现方法",
            chapter: "Python数据结构",
            studentId: "DEV2023002",
        },
    },
    {
        id: 3,
        type: "system", // 系统通知
        title: "系统更新通知",
        content: "平台将于今晚23:00进行系统维护，预计持续2小时",
        time: new Date(Date.now() - 20 * 3600000).toISOString(), // 20小时前
        read: true,
        details: {
            version: "v2.3.0",
            startTime: new Date(Date.now() + 8 * 3600000).toISOString(), // 8小时后
            endTime: new Date(Date.now() + 10 * 3600000).toISOString(), // 10小时后
            features: ["新增习题分析功能", "优化学生成绩统计"],
        },
    },
    {
        id: 4,
        type: "exercise", // 习题相关
        title: "学生习题已完成",
        content: "刘洋已完成Go并发编程习题，等待您的批改",
        time: new Date(Date.now() - 25 * 3600000).toISOString(), // 25小时前
        read: true,
        details: {
            studentName: "刘洋",
            exerciseName: "Go并发编程",
            submissionTime: new Date(Date.now() - 25.5 * 3600000).toISOString(),
            exerciseId: "ex-1025",
            totalQuestions: 10,
            attemptedQuestions: 10,
            studentId: "DEV2023006",
        },
    },
]);

// 计算未读通知数量
const unreadCount = computed(() => {
    return notifications.value.filter((notification) => !notification.read)
        .length;
});

// 切换用户菜单显示/隐藏
const toggleUserMenu = () => {
    showUserMenu.value = !showUserMenu.value;
    showNotificationPanel.value = false; // 关闭通知面板
};

// 切换通知面板显示/隐藏
const toggleNotificationPanel = () => {
    showNotificationPanel.value = !showNotificationPanel.value;
    showUserMenu.value = false; // 关闭用户菜单

    // 打开时标记所有为已读
    if (showNotificationPanel.value) {
        markVisibleAsRead();
    }
};

// 标记所有可见通知为已读
const markVisibleAsRead = () => {
    notifications.value.forEach((notification) => {
        if (!notification.read) {
            notification.read = true;
        }
    });
};

// 标记所有通知为已读
const markAllAsRead = () => {
    notifications.value.forEach((notification) => {
        notification.read = true;
    });
};

// 查看通知详情
const viewNotificationDetail = (notificationId) => {
    const notification = notifications.value.find(
        (item) => item.id === notificationId
    );
    if (notification) {
        currentNotification.value = { ...notification };
        showNotificationDetail.value = true;
        showNotificationPanel.value = false;

        // 标记为已读
        if (!notification.read) {
            notification.read = true;
        }
    }
};

// 关闭通知详情
const closeNotificationDetail = () => {
    showNotificationDetail.value = false;
    currentNotification.value = null;
};

// 前往习题批改
const gotoExerciseCorrection = () => {
    if (
        currentNotification.value &&
        currentNotification.value.details.exerciseId
    ) {
        const exerciseId = currentNotification.value.details.exerciseId;
        const studentId = currentNotification.value.details.studentId;

        router.push(
            `/teacher/exercises/correct/${exerciseId}?student=${studentId}`
        );
        closeNotificationDetail();
    }
};

// 前往解答学生问题
const gotoAnswerQuestion = () => {
    if (
        currentNotification.value &&
        currentNotification.value.details.studentId
    ) {
        const studentId = currentNotification.value.details.studentId;
        const question = currentNotification.value.details.question;

        router.push(
            `/teacher/students/${studentId}/questions?query=${encodeURIComponent(
                question
            )}`
        );
        closeNotificationDetail();
    }
};

// 导航到指定页面
const navigateTo = (page) => {
    switch (page) {
        case "personal-info":
            router.push("/teacher/info/personal");
            break;
        case "settings":
            router.push("/teacher/settings");
            break;
        default:
            break;
    }
    showUserMenu.value = false;
};

// 退出登录
const logout = () => {
    try {
        window.localStorage && window.localStorage.removeItem("token");
    } catch (e) {
        console.error("清理登录状态失败", e);
    }
    router.push("/login");
    showUserMenu.value = false;
};

// 格式化时间（相对时间）
const formatTime = (timeString) => {
    try {
        const now = new Date();
        const time = new Date(timeString);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return "刚刚";
        if (diffMins < 60) return `${diffMins}分钟前`;
        if (diffHours < 24) return `${diffHours}小时前`;
        if (diffDays < 7) return `${diffDays}天前`;

        // 超过一周显示日期
        return time.toLocaleDateString("zh-CN", {
            month: "short",
            day: "numeric",
        });
    } catch (error) {
        console.error("时间格式化错误:", error);
        return "未知时间";
    }
};

// 格式化完整日期
const formatDate = (dateString) => {
    try {
        const date = new Date(dateString);
        return date.toLocaleString("zh-CN", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        });
    } catch (error) {
        console.error("日期格式化错误:", error);
        return "未知日期";
    }
};
</script>

<style scoped>
/* 基础布局样式 */
.teacher-index-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background-color: #f7f8fa;
    overflow: hidden;
    position: relative;
}

.layout {
    display: flex;
    height: 100%;
    position: relative;
    z-index: 1;
}

.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    width: calc(100% - 260px);
    margin-left: 260px;
}

/* 页面头部样式 */
.page-header {
    position: relative;
    height: 120px;
    display: flex;
    align-items: center;
    padding: 0 20px; /* 减少右侧内边距，使内容左移 */
    overflow: hidden;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.header-gradient {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6b8dd6 100%);
    z-index: 0;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    position: relative;
    z-index: 2;
}

.header-title h1 {
    margin: 0;
    font-size: 28px;
    color: white;
    font-weight: 700;
}

.header-title p {
    margin: 5px 0 0 0;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
}

/* 用户和通知区域容器 - 调整样式使内容左移 */
.user-notification-area {
    display: flex;
    align-items: center;
    gap: 15px; /* 减小间距 */
    margin-left: auto; /* 确保区域靠右但不贴边 */
    margin-right: 15px; /* 右侧留出空间，避免贴边 */
}

/* 通知图标 - 调整位置 */
.notification-icon {
    font-size: 24px;
    color: white;
    cursor: pointer;
    position: relative;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: 1.5px solid rgba(255, 255, 255, 0.4);
    z-index: 10;
    transition: all 0.3s ease;
}

.notification-icon:hover {
    transform: scale(1.08);
    background-color: rgba(255, 255, 255, 0.15);
}

.notification-badge {
    position: absolute;
    top: -2px;
    right: -2px;
    width: 18px;
    height: 18px;
    background-color: #ff4757;
    color: white;
    font-size: 11px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border: 1.5px solid white;
    animation: pulse 2s infinite;
}

/* 通知面板容器 */
.notification-panel-container {
    position: fixed;
    top: 95px;
    right: 20px; /* 调整右距离，避免超出屏幕 */
    z-index: 9999999;
    isolation: isolate;
}

/* 通知面板样式 */
.notification-panel {
    width: 380px;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    transform: translateY(10px);
    opacity: 0;
    animation: fadeInUp 0.3s ease forwards;
    overflow: hidden;
    max-height: 500px;
}

/* 通知面板头部 */
.notification-panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #f0f2f5;
}

.notification-panel-header h3 {
    margin: 0;
    font-size: 16px;
    color: #1e3a8a;
    font-weight: 600;
}

.mark-all-read {
    background: none;
    border: none;
    color: #3498db;
    font-size: 13px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.2s ease;
}

.mark-all-read:hover {
    background-color: rgba(52, 152, 219, 0.1);
    color: #2980b9;
}

/* 通知列表 */
.notification-list {
    max-height: calc(500px - 60px);
    overflow-y: auto;
}

.notification-item {
    padding: 14px 20px;
    border-bottom: 1px solid #f0f2f5;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
}

.notification-item:hover {
    background-color: #f8f9fa;
    transform: translateX(4px);
}

.notification-item.unread {
    background-color: rgba(52, 152, 219, 0.05);
}

.notification-item.unread::before {
    content: "";
    position: absolute;
    left: 12px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #3498db;
}

.notification-icon-type {
    font-size: 20px;
    margin-top: 2px;
    min-width: 24px;
    text-align: center;
}

.notification-content {
    flex: 1;
    position: relative;
}

.notification-title {
    font-size: 14px;
    color: #333;
    margin-bottom: 4px;
    line-height: 1.4;
}

.notification-time {
    font-size: 12px;
    color: #94a3b8;
}

/* 用户菜单样式 - 调整以显示更多信息 */
.user-menu-trigger {
    cursor: pointer;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

/* 新增：用户详情区域，显示姓名和账号 */
.user-details {
    text-align: right; /* 文字右对齐，与头像保持一致 */
}

.user-name {
    font-size: 15px;
    color: white;
    font-weight: 500;
    white-space: nowrap;
}

/* 新增：用户账号样式 */
.user-account {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
    white-space: nowrap;
}

.user-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    border: 2px solid rgba(255, 255, 255, 0.6);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.user-avatar span {
    font-size: 22px;
    color: white;
}

/* 全局下拉菜单 - 调整位置 */
.global-user-dropdown {
    position: absolute;
    top: 85px;
    right: 20px; /* 调整右距离，避免超出屏幕 */
    z-index: 9999998;
}

.user-dropdown {
    width: 200px;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    transform: translateY(10px);
    opacity: 0;
    animation: fadeInUp 0.3s ease forwards;
    overflow: hidden;
}

/* 通知详情模态框 */
.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 99999999;
    padding: 20px;
    animation: fadeIn 0.3s ease;
    backdrop-filter: blur(4px);
}

.notification-detail-modal {
    width: 100%;
    max-width: 550px;
    background-color: white;
    border-radius: 16px;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    animation: scaleIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    overflow: hidden;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #f0f2f5;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.modal-header h3 {
    margin: 0;
    font-size: 18px;
    color: white;
    font-weight: 600;
}

.close-btn {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: rgba(255, 255, 255, 0.8);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.close-btn:hover {
    background-color: rgba(255, 255, 255, 0.15);
    color: white;
}

.modal-body {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
}

.detail-wrapper {
    animation: fadeIn 0.4s ease;
}

.notification-detail-header {
    display: flex;
    gap: 15px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f0f2f5;
}

.detail-icon {
    font-size: 32px;
    margin-top: 3px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background-color: rgba(102, 126, 234, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
}

.detail-header-text h4 {
    margin: 0 0 8px 0;
    font-size: 18px;
    color: #1e3a8a;
    font-weight: 600;
}

.detail-time {
    font-size: 13px;
    color: #94a3b8;
}

.notification-detail-content {
    color: #64748b;
    line-height: 1.7;
    font-size: 15px;
    margin-bottom: 20px;
}

.notification-detail-content p {
    margin: 0 0 24px 0;
    padding: 12px 16px;
    background-color: #f8fafc;
    border-radius: 8px;
    border-left: 3px solid #667eea;
}

/* 详情卡片样式 */
.notification-details-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    margin-top: 15px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #f0f2f5;
}

/* 详情项样式 */
.detail-item {
    display: flex;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px dashed #f0f2f5;
}

.detail-item:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}

.detail-label {
    flex: 0 0 100px;
    font-weight: 500;
    color: #333;
}

.detail-value {
    flex: 1;
}

.detail-value ul {
    margin: 0;
    padding-left: 20px;
}

.detail-value ul li {
    margin-bottom: 8px;
    position: relative;
    padding-left: 8px;
}

.detail-value ul li:before {
    content: "•";
    color: #667eea;
    font-weight: bold;
    position: absolute;
    left: -12px;
}

.detail-actions {
    margin-top: 24px;
    display: flex;
    justify-content: flex-end;
}

/* 按钮样式 */
.btn {
    padding: 10px 24px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-primary:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 内容区域 */
.content {
    flex: 1;
    padding: 30px 40px;
    overflow-y: auto;
    background-color: #f7f8fa;
    position: relative;
    z-index: 10;
}

/* 动画效果 */
@keyframes fadeInUp {
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes scaleIn {
    from {
        transform: scale(0.95);
        opacity: 0;
    }
    to {
        transform: scale(1);
        opacity: 1;
    }
}

@keyframes pulse {
    0% {
        transform: scale(1);
        box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.7);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 6px rgba(255, 71, 87, 0);
    }
    100% {
        transform: scale(1);
        box-shadow: 0 0 0 0 rgba(255, 71, 87, 0);
    }
}

/* 响应式调整 */
@media (max-width: 768px) {
    .main-content {
        width: 100%;
        margin-left: 0;
    }

    .notification-panel-container {
        right: 10px;
        top: 85px;
    }

    .notification-panel {
        width: calc(100vw - 20px);
    }

    .notification-detail-modal {
        width: calc(100% - 20px);
    }

    .detail-label {
        flex: 0 0 80px;
    }

    /* 响应式下调整用户信息显示 */
    .user-account {
        display: none; /* 小屏幕隐藏账号 */
    }
}
</style>
