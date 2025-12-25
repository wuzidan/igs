<template>
    <div class="intelligent-platform">
        <!-- 顶部导航栏 -->
        <header class="header">
            <h1>智能导学系统</h1>

            <div class="user-info">
                <div class="avatar-container">
                    <div class="avatar avatar-teacher">
                        {{ userAvatar }}
                    </div>
                    <div class="user-basic">
                        <h2>{{ userName }}</h2>
                        <div class="user-id">{{ teacherId }}</div>
                    </div>
                </div>
                <button class="logout-btn" @click="logout">退出</button>
            </div>
        </header>

        <main class="content-wrapper">
            <!-- 教师界面内容 -->
            <section v-if="isTeacher">
                <!-- 欢迎面板 -->
                <div class="welcome-panel">
                    <div class="welcome-gradient"></div>
                    <div class="welcome-content">
                        <div>
                            <h2 class="welcome-title">
                                <span class="welcome-emoji">👋</span>
                                欢迎回来，{{ userName }}老师
                            </h2>
                            <p class="welcome-message">
                                今天有{{
                                    pendingTasks
                                }}个待办任务需要处理，加油！
                            </p>
                        </div>
                        <div class="teacher-summary">
                            <div class="summary-info">
                                <span class="summary-label">已教班级</span>
                                <span class="summary-value">{{
                                    classCount
                                }}</span>
                            </div>
                            <div class="summary-info">
                                <span class="summary-label">学生总数</span>
                                <span class="summary-value">{{
                                    studentCount
                                }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 教师待办任务 -->
                <section class="teacher-tasks">
                    <h3 class="section-title">
                        <span class="title-icon">📝</span>
                        待办任务
                        <span class="title-underline"></span>
                    </h3>
                    <div class="tasks-container">
                        <div
                            v-for="task in pendingTaskList"
                            :key="task.id"
                            class="task-card"
                        >
                            <div class="task-header">
                                <span class="task-title">{{ task.title }}</span>
                                <span
                                    class="task-priority"
                                    :class="task.priority"
                                    >{{ task.priority }}</span
                                >
                            </div>
                            <div class="task-content">
                                <p class="task-description">
                                    {{ task.description }}
                                </p>
                                <div class="task-meta">
                                    <span class="task-deadline">{{
                                        task.deadline
                                    }}</span>
                                    <span class="task-progress">{{
                                        task.progress
                                    }}</span>
                                </div>
                            </div>
                            <div class="task-actions">
                                <button
                                    class="action-btn complete-btn"
                                    @click="markTaskAsComplete(task.id)"
                                >
                                    完成
                                </button>
                                <button
                                    class="action-btn view-btn"
                                    @click="viewTaskDetails(task.id)"
                                >
                                    详情
                                </button>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- 教师核心功能区 -->
                <section class="core-features">
                    <h3 class="section-title">
                        <span class="title-icon">🚀</span>
                        核心功能
                        <span class="title-underline"></span>
                    </h3>
                    <div class="features-grid">
                        <!-- 班级管理 -->
                        <div
                            class="feature-card floating-card"
                            @click="navigateTo('/teacher/class/tracking')"
                        >
                            <div class="feature-hover-effect"></div>
                            <div class="feature-icon-container">
                                <span class="feature-icon">🏫</span>
                            </div>
                            <h4 class="feature-title">班级管理</h4>
                            <p class="feature-description">
                                管理{{
                                    classCount
                                }}个班级，查看学生表现，发布公告和通知，组织课堂活动。
                            </p>
                            <div class="feature-stats">
                                <span class="feature-count"
                                    >共{{ studentCount }}名学生</span
                                >
                                <span class="feature-badge">📋管理</span>
                            </div>
                        </div>

                        <!-- 习题管理 -->
                        <div
                            class="feature-card floating-card"
                            @click="navigateTo('/teacher/exercise/bank')"
                        >
                            <div class="feature-hover-effect"></div>
                            <div class="feature-icon-container">
                                <span class="feature-icon">📝</span>
                            </div>
                            <h4 class="feature-title">习题管理</h4>
                            <p class="feature-description">
                                创建、编辑和管理题库资源，设计个性化的习题集和测验，跟踪学生作答情况。
                            </p>
                            <div class="feature-stats">
                                <span class="feature-count"
                                    >已上传{{ questionCount }}道题</span
                                >
                                <span class="feature-badge">📚题库</span>
                            </div>
                        </div>

                        <!-- 学习分析 -->
                        <div
                            class="feature-card floating-card"
                            @click="navigateTo('/teacher/class/tracking')"
                        >
                            <div class="feature-hover-effect"></div>
                            <div class="feature-icon-container">
                                <span class="feature-icon">📊</span>
                            </div>
                            <h4 class="feature-title">学习分析</h4>
                            <p class="feature-description">
                                深入分析学生学习数据，生成多维度学习报告，精准定位学习薄弱环节。
                            </p>
                            <div class="feature-stats">
                                <span class="feature-count"
                                    >支持10+种分析维度</span
                                >
                                <span class="feature-badge">🔍分析</span>
                            </div>
                        </div>

                        <!-- 智能推荐 -->
                        <div
                            class="feature-card floating-card"
                            @click="navigateTo('/teacher/exercise/new')"
                        >
                            <div class="feature-hover-effect"></div>
                            <div class="feature-icon-container">
                                <span class="feature-icon">💡</span>
                            </div>
                            <h4 class="feature-title">智能推荐</h4>
                            <p class="feature-description">
                                基于AI算法的个性化学习路径推荐，为每个学生提供定制化的学习内容。
                            </p>
                            <div class="feature-stats">
                                <span class="feature-count">实时AI分析</span>
                                <span class="feature-badge">🤖智能</span>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- 班级进度和数据 -->
                <section class="teacher-data-section">
                    <div class="class-progress-container">
                        <h3 class="section-title">
                            <span class="title-icon">📈</span>
                            班级学习进度
                            <span class="title-underline"></span>
                        </h3>
                        <div class="progress-chart">
                            <!-- 这里是进度图表区域 -->
                            <div class="chart-container">
                                <div class="chart-grid">
                                    <!-- X轴 -->
                                    <div class="chart-x-axis">
                                        <div class="x-axis-label">班级</div>
                                        <div class="x-axis-ticks">
                                            <div
                                                class="x-tick"
                                                v-for="cls in classProgressData"
                                                :key="cls.id"
                                            >
                                                {{ cls.className }}
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Y轴 -->
                                    <div class="chart-y-axis">
                                        <div class="y-axis-label">完成率</div>
                                        <div class="y-axis-ticks">
                                            <div class="y-tick">100%</div>
                                            <div class="y-tick">80%</div>
                                            <div class="y-tick">60%</div>
                                            <div class="y-tick">40%</div>
                                            <div class="y-tick">20%</div>
                                            <div class="y-tick">0%</div>
                                        </div>
                                    </div>

                                    <!-- 柱状图 -->
                                    <div class="chart-bars">
                                        <div
                                            class="chart-bar"
                                            v-for="cls in classProgressData"
                                            :key="cls.id"
                                            :style="{
                                                height: cls.progress + '%',
                                            }"
                                        >
                                            <div class="bar-value">
                                                {{ cls.progress }}%
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <button
                                class="view-details-btn"
                                @click="viewProgressDetails"
                            >
                                查看详情
                            </button>
                        </div>
                    </div>

                    <div class="teacher-stats-container">
                        <h3 class="section-title">
                            <span class="title-icon">📊</span>
                            教学统计
                            <span class="title-underline"></span>
                        </h3>
                        <div class="teacher-stats-cards">
                            <!-- 教师状态卡片 - 平均正确率 -->
                            <div id="teacher-accuracy-rate" class="status-card">
                                <div class="card-gradient"></div>
                                <div class="card-header">
                                    <span class="card-title"
                                        >班级平均正确率</span
                                    >
                                    <span class="card-icon">🎯</span>
                                </div>
                                <div class="card-stat">
                                    <span class="stat-value">{{
                                        averageAccuracy
                                    }}</span>
                                    <span class="stat-unit">%</span>
                                </div>
                                <div class="progress-container">
                                    <div class="progress-background"></div>
                                    <div
                                        class="progress-bar"
                                        :style="{
                                            width: averageAccuracy + '%',
                                        }"
                                    ></div>
                                </div>
                                <div class="card-trend">
                                    <span class="trend-indicator"
                                        >+{{ accuracyTrend }}%</span
                                    >
                                    <span class="trend-text">较上月</span>
                                </div>
                            </div>

                            <!-- 教师状态卡片 - 学习时长 -->
                            <div
                                id="teacher-study-duration"
                                class="status-card"
                            >
                                <div class="card-gradient"></div>
                                <div class="card-header">
                                    <span class="card-title">平均学习时长</span>
                                    <span class="card-icon">⏱️</span>
                                </div>
                                <div class="card-stat">
                                    <span class="stat-value">{{
                                        averageStudyHours
                                    }}</span>
                                    <span class="stat-unit">小时/周</span>
                                </div>
                                <div class="progress-container">
                                    <div class="progress-background"></div>
                                    <div
                                        class="progress-bar"
                                        :style="{
                                            width: studyHoursRateTeacher + '%',
                                        }"
                                    ></div>
                                </div>
                                <div class="card-trend">
                                    <span class="trend-indicator"
                                        >+{{ hoursTrend }}</span
                                    >
                                    <span class="trend-text">较上月</span>
                                </div>
                            </div>

                            <!-- 教师状态卡片 - 完成任务 -->
                            <div
                                id="teacher-completed-tasks"
                                class="status-card"
                            >
                                <div class="card-gradient"></div>
                                <div class="card-header">
                                    <span class="card-title">已完成作业</span>
                                    <span class="card-icon">✅</span>
                                </div>
                                <div class="card-stat">
                                    <span class="stat-value">{{
                                        completedAssignments
                                    }}</span>
                                    <span class="stat-total"
                                        >/{{ totalAssignments }}</span
                                    >
                                </div>
                                <div class="progress-container">
                                    <div class="progress-background"></div>
                                    <div
                                        class="progress-bar"
                                        :style="{
                                            width:
                                                assignmentCompletionRate + '%',
                                        }"
                                    ></div>
                                </div>
                                <div class="card-trend">
                                    <span class="trend-indicator"
                                        >+{{ assignmentsTrend }}%</span
                                    >
                                    <span class="trend-text">较上月</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </section>
        </main>

        <!-- 页脚 -->
        <footer class="main-footer">
            <div class="footer-content">
                <div class="footer-logo">智能导学系统 © 2025</div>
                <div class="footer-links">
                    <a href="/lyq" class="footer-link">关于我们</a>
                    <a href="/lyq" class="footer-link">使用指南</a>
                    <a href="/lyq" class="footer-link">隐私政策</a>
                    <a href="/lyq" class="footer-link">联系我们</a>
                </div>
                <div class="footer-copyright">
                    智能导学系统 - 为教学提供高效辅助工具
                </div>
            </div>
        </footer>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import request from "../../utils/request";

// 路由实例
const router = useRouter();

// 身份与权限相关状态
const isTeacher = ref(true);
const userRole = ref("teacher"); // 可能的值: student, teacher, admin

const isLoggedIn = ref(
    !!(window.localStorage && window.localStorage.getItem("token"))
);

const handleAuthFailure = async (e) => {
    console.error("请求失败", e);
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
};

// 教师信息
const userName = ref("");
const teacherId = ref("");
const userAvatar = ref("👨🏫");
const classCount = ref(0);
const studentCount = ref(0);

// 教师待办任务数据
const pendingTasks = ref(0);
const pendingTaskList = ref([]);

// 教师教学数据
const questionCount = ref(0);
const averageAccuracy = ref(0);
const accuracyTrend = ref(0);
const averageStudyHours = ref(0);
const studyHoursRateTeacher = ref(0);
const hoursTrend = ref(0);
const completedAssignments = ref(0);
const totalAssignments = ref(0);
const assignmentCompletionRate = ref(0);
const assignmentsTrend = ref(0);

// 班级进度数据
const classProgressData = ref([]);

// 权限判断计算属性
const canAccessTeacherFunctions = computed(() => {
    return userRole.value === "teacher" || userRole.value === "admin";
});

// 确保DOM加载完成后执行初始化
onMounted(async () => {
    console.log("教师首页组件已挂载，界面初始化完成");
    userRole.value = "teacher";

    if (!isLoggedIn.value) {
        try {
            router.push("/login");
        } catch (err) {
            console.error("路由跳转失败", err);
        }
        return;
    }

    try {
        const resp = await request.get("/teacher/dashboard/");
        const data = resp?.data || {};

        const teacher = data.teacher || {};
        userName.value = teacher.teacherName || userName.value;
        teacherId.value = teacher.teacherId || teacherId.value;
        if (userName.value) {
            userAvatar.value = userName.value.slice(0, 1);
        }

        const summary = data.summary || {};
        classCount.value = summary.classCount || 0;
        studentCount.value = summary.studentCount || 0;
        questionCount.value = summary.questionCount || 0;

        const tasks = data.tasks || {};
        pendingTasks.value = tasks.pendingTasks || 0;
        pendingTaskList.value = Array.isArray(tasks.pendingTaskList)
            ? tasks.pendingTaskList
            : [];
        if (!pendingTasks.value) {
            pendingTasks.value = pendingTaskList.value.length;
        }

        const stats = data.stats || {};
        averageAccuracy.value = stats.averageAccuracy || 0;
        accuracyTrend.value = stats.accuracyTrend || 0;
        averageStudyHours.value = stats.averageStudyHours || 0;
        studyHoursRateTeacher.value = stats.studyHoursRateTeacher || 0;
        hoursTrend.value = stats.hoursTrend || 0;
        completedAssignments.value = stats.completedAssignments || 0;
        totalAssignments.value = stats.totalAssignments || 0;
        assignmentCompletionRate.value = stats.assignmentCompletionRate || 0;
        assignmentsTrend.value = stats.assignmentsTrend || 0;

        classProgressData.value = Array.isArray(data.classProgressData)
            ? data.classProgressData
            : [];
    } catch (e) {
        await handleAuthFailure(e);
    }
});

// 通用方法
const navigateTo = (path) => {
    console.log(`导航至: ${path}`);
    // 实际项目中使用路由跳转
    try {
        router.push(path);
    } catch (error) {
        console.error("路由跳转失败:", error);
    }
};

const logout = () => {
    console.log("教师退出登录");
    try {
        window.localStorage && window.localStorage.removeItem("token");
        router.push("/login");
    } catch (error) {
        console.error("退出登录失败:", error);
    }
};

// 教师特有方法
const markTaskAsComplete = (taskId) => {
    if (canAccessTeacherFunctions.value) {
        console.log(`标记任务完成: ${taskId}`);
        const task = pendingTaskList.value.find((task) => task.id === taskId);
        if (task) {
            task.progress = "100%";
            pendingTasks.value--;
        }
    } else {
        console.log("权限不足：无法访问教师功能");
    }
};

const viewTaskDetails = (taskId) => {
    if (canAccessTeacherFunctions.value) {
        console.log(`查看任务详情: ${taskId}`);
        navigateTo(`/teacher/task-details/${taskId}`);
    } else {
        console.log("权限不足：无法访问教师功能");
    }
};

const viewProgressDetails = () => {
    if (canAccessTeacherFunctions.value) {
        console.log("查看班级进度详情");
        navigateTo("/teacher/progress-details");
    } else {
        console.log("权限不足：无法访问教师功能");
    }
};
</script>

<style scoped>
/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.intelligent-platform {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    background-image: radial-gradient(
            circle at 25% 25%,
            rgba(59, 130, 246, 0.1) 0%,
            transparent 50%
        ),
        radial-gradient(
            circle at 75% 75%,
            rgba(99, 102, 241, 0.1) 0%,
            transparent 50%
        );
    color: #1e293b;
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
}

/* 顶部导航栏样式 */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 18px 24px;
    border-bottom: 2px solid transparent;
    border-image: linear-gradient(90deg, #3b82f6, #6366f1) 1;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.08);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.header::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #3b82f6, #6366f1, #3b82f6);
    background-size: 200% 100%;
    animation: headerGlow 6s ease-in-out infinite;
}

.header h1 {
    margin: 0;
    font-size: 30px;
    font-weight: 600;
    background: linear-gradient(90deg, #1e293b, #334155);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    position: relative;
    padding-left: 12px;
    transition: transform 0.3s ease;
}

.header h1::before {
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 60%;
    border-radius: 2px;
    background: linear-gradient(180deg, #3b82f6, #6366f1);
}

.user-info {
    display: flex;
    align-items: center;
    transition: transform 0.3s ease;
}

.logout-btn {
    margin-left: 15px;
    padding: 9px 18px;
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.logout-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    background: linear-gradient(90deg, #2563eb, #3b82f6);
}

.logout-btn::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 120px;
    height: 120px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%) scale(0);
    transition: transform 0.6s ease;
}

.logout-btn:active::after {
    transform: translate(-50%, -50%) scale(1);
}

.header:hover {
    box-shadow: 0 6px 25px rgba(59, 130, 246, 0.12);
    transform: translateY(-2px);
}

.header:hover h1 {
    transform: translateX(5px);
}

.header:hover .user-info {
    transform: translateX(-5px);
}

@keyframes headerGlow {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}

.avatar-container {
    display: flex;
    align-items: center;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-right: 10px;
}

.avatar-teacher {
    background-color: #6366f1;
    color: white;
}

.user-basic {
    display: flex;
    flex-direction: column;
}

.user-basic h2 {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
}

.user-id {
    font-size: 13px;
    color: #64748b;
}

/* 主内容区域样式 */
.content-wrapper {
    padding: 1.5rem 2rem;
    max-width: 1600px;
    margin: 0 auto;
}

.section-title {
    font-size: 1.3rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    padding-bottom: 0.5rem;
    color: #1e3a8a;
}

.title-icon {
    font-size: 1.5rem;
}

.title-underline {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.5), transparent);
    margin-left: 1rem;
}

/* 欢迎面板 */
.welcome-panel {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(240, 249, 255, 0.8);
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
}

.welcome-gradient {
    position: absolute;
    top: 0;
    right: 0;
    width: 300px;
    height: 300px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    filter: blur(100px);
    opacity: 0.15;
    transform: translate(30%, -30%);
}

.welcome-content {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.welcome-title {
    font-size: 1.8rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #1e3a8a;
}

.welcome-emoji {
    font-size: 1.5rem;
}

.welcome-message {
    color: #64748b;
    margin-top: 0.5rem;
    font-size: 1rem;
}

.teacher-summary {
    display: flex;
    gap: 2rem;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    border: 1px solid rgba(59, 130, 246, 0.1);
}

.summary-info {
    display: flex;
    flex-direction: column;
}

.summary-label {
    color: #64748b;
    font-size: 0.9rem;
}

.summary-value {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1e3a8a;
}

/* 教师待办任务 */
.teacher-tasks {
    margin-bottom: 2.5rem;
}

.tasks-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 1.5rem;
}

.task-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(240, 249, 255, 0.8);
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
    transition: all 0.3s ease;
}

.task-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(59, 130, 246, 0.12);
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.task-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e3a8a;
}

.task-priority {
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
}

.task-priority.high {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

.task-priority.medium {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
}

.task-priority.low {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
}

.task-description {
    color: #64748b;
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 0.8rem;
}

.task-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #94a3b8;
}

.task-actions {
    display: flex;
    gap: 0.8rem;
    margin-top: 1rem;
}

.action-btn {
    padding: 0.5rem 1rem;
    border-radius: 8px;
    border: none;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.complete-btn {
    background: linear-gradient(90deg, #10b981, #059669);
    color: white;
}

.complete-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.view-btn {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    color: white;
}

.view-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* 核心功能区通用样式 */
.core-features {
    margin-bottom: 2.5rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.feature-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(240, 249, 255, 0.8);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    cursor: pointer;
    height: 100%;
    display: flex;
    flex-direction: column;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 20px rgba(59, 130, 246, 0.15);
    border-color: rgba(191, 219, 254, 0.8);
}

.feature-icon-container {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.2rem;
    background: rgba(59, 130, 246, 0.1);
}

.feature-icon {
    font-size: 1.8rem;
    color: #3b82f6;
}

.feature-title {
    font-size: 1.2rem;
    margin-bottom: 0.8rem;
    font-weight: 600;
    color: #1e3a8a;
}

.feature-description {
    color: #64748b;
    font-size: 0.95rem;
    line-height: 1.5;
    margin-bottom: 1.2rem;
    flex: 1;
}

.feature-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
}

.feature-count {
    font-size: 0.9rem;
    color: #64748b;
}

.feature-badge {
    font-size: 0.8rem;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.1);
}

.feature-hover-effect {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(59, 130, 246, 0.05);
    transform: scaleX(0);
    transition: transform 0.5s ease;
    transform-origin: left;
}

.feature-card:hover .feature-hover-effect {
    transform: scaleX(1);
}

/* 浮动动画效果 */
.floating-card {
    animation: float 6s ease-in-out infinite;
}

.floating-card:nth-child(2) {
    animation-delay: 1s;
}

.floating-card:nth-child(3) {
    animation-delay: 2s;
}

.floating-card:nth-child(4) {
    animation-delay: 3s;
}

@keyframes float {
    0% {
        transform: translateY(-10px);
    }
    50% {
        transform: translateY(10px);
    }
    100% {
        transform: translateY(-10px);
    }
}

/* 教师数据区域 */
.teacher-data-section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
}

.class-progress-container,
.teacher-stats-container {
    display: flex;
    flex-direction: column;
}

.progress-chart {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(240, 249, 255, 0.8);
    height: 100%;
    min-height: 400px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
}

/* 教师进度图表样式 */
.chart-container {
    width: 100%;
    height: calc(100% - 50px);
    position: relative;
}

.chart-grid {
    display: grid;
    grid-template-columns: 1fr auto;
    grid-template-rows: auto 1fr;
    height: 100%;
}

.chart-x-axis {
    grid-column: 2;
    grid-row: 2;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    height: 100%;
}

.x-axis-label {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 0.5rem;
}

.x-axis-ticks {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.5rem;
}

.x-tick {
    font-size: 0.85rem;
    color: #64748b;
    writing-mode: vertical-rl;
    text-orientation: mixed;
    transform: rotate(180deg);
}

.chart-y-axis {
    grid-column: 1;
    grid-row: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    padding-right: 1rem;
}

.y-axis-label {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 1rem;
    writing-mode: vertical-rl;
}

.y-axis-ticks {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.y-tick {
    font-size: 0.85rem;
    color: #64748b;
}

.chart-bars {
    grid-column: 2;
    grid-row: 1;
    display: flex;
    align-items: flex-end;
    gap: 1.5rem;
    height: 100%;
    padding-bottom: 3rem;
    padding-top: 1rem;
}

.chart-bar {
    flex: 1;
    min-width: 30px;
    background: linear-gradient(180deg, #3b82f6, #6366f1);
    border-radius: 8px 8px 0 0;
    position: relative;
    transition: height 1s ease-in-out;
}

.chart-bar:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
}

.bar-value {
    position: absolute;
    top: -25px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.9rem;
    font-weight: 600;
    color: #1e3a8a;
}

/* 按钮通用样式 */
.view-details-btn {
    position: absolute;
    bottom: 1.5rem;
    right: 1.5rem;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #3b82f6;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
}

.view-details-btn:hover {
    background: rgba(59, 130, 246, 0.2);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

/* 教师统计卡片 */
.teacher-stats-cards {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    height: 100%;
}

.status-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 10px;
    padding: 22px;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(240, 249, 255, 0.8);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.status-card:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 10px 25px rgba(59, 130, 246, 0.15);
    border-color: rgba(191, 219, 254, 0.8);
}

.card-gradient {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.card-title {
    font-size: 1rem;
    color: #64748b;
    font-weight: 500;
}

.card-icon {
    font-size: 1.2rem;
}

.card-stat {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1e3a8a;
}

.stat-total,
.stat-target,
.stat-unit {
    color: #64748b;
    font-size: 0.9rem;
}

.progress-container {
    height: 8px;
    border-radius: 4px;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
}

.progress-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(226, 232, 240, 0.5);
}

.progress-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 1s ease-in-out;
}

.card-trend {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.9rem;
}

.trend-indicator {
    color: #10b981;
    font-weight: bold;
}

/* 教师状态卡片特殊样式 */
#teacher-accuracy-rate .card-gradient,
#teacher-accuracy-rate .progress-bar {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
}

#teacher-study-duration .card-gradient,
#teacher-study-duration .progress-bar {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

#teacher-completed-tasks .card-gradient,
#teacher-completed-tasks .progress-bar {
    background: linear-gradient(135deg, #10b981, #059669);
}

/* 页脚样式 */
.main-footer {
    margin-top: 3rem;
    padding: 2rem;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-top: 1px solid rgba(59, 130, 246, 0.1);
}

.footer-content {
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
}

.footer-logo {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e3a8a;
    margin-bottom: 1rem;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-bottom: 1rem;
}

.footer-link {
    color: #64748b;
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer-link:hover {
    color: #3b82f6;
}

.footer-copyright {
    color: #94a3b8;
    font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .teacher-data-section {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .welcome-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .features-grid {
        grid-template-columns: 1fr;
    }

    .header h1 {
        font-size: 24px;
    }

    .tasks-container {
        grid-template-columns: 1fr;
    }

    .chart-bars {
        padding-bottom: 6rem;
    }
}
</style>
