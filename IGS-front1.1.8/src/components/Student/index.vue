<template>
    <div class="intelligent-platform">
        <!-- 顶部导航栏 -->
        <header class="header">
            <h1>智能导学系统</h1>

            <div class="user-info">
                <div class="avatar-container">
                    <div class="avatar avatar-student">
                        {{ userAvatar }}
                    </div>
                    <div class="user-basic">
                        <h2>{{ userName }}</h2>
                        <div class="user-id">{{ studentId }}</div>
                    </div>
                </div>
                <button class="logout-btn" @click="logout">退出</button>
            </div>
        </header>

        <main class="content-wrapper">
            <!-- 学生界面内容 -->
            <section v-if="!isTeacher">
                <!-- 欢迎面板 -->
                <div class="welcome-panel">
                    <div class="welcome-gradient"></div>
                    <div class="welcome-content">
                        <div>
                            <h2 class="welcome-title">
                                <span class="welcome-emoji">👋</span>
                                欢迎回来，{{ userName }}
                            </h2>
                            <p class="welcome-message">
                                今天也是学习的好日子！继续保持学习的热情，你离目标更进一步了。
                            </p>
                        </div>
                        <div class="study-streak">
                            <div class="streak-info">
                                <span class="streak-label">学习天数</span>
                                <span class="streak-value">{{
                                    learningDays
                                }}</span>
                            </div>
                            <div class="streak-info">
                                <span class="streak-icon">🔥</span>
                                <span class="streak-value">{{
                                    continuousDays
                                }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 学习状态卡片 -->
                <section class="status-overview">
                    <h3 class="section-title">
                        <span class="title-icon">📊</span>
                        学习状态
                        <span class="title-underline"></span>
                    </h3>
                    <div class="status-cards">
                        <!-- 已完成任务 -->
                        <div id="completed-tasks" class="status-card">
                            <div class="card-gradient"></div>
                            <div class="card-header">
                                <span class="card-title">已完成任务</span>
                                <span class="card-icon">✅</span>
                            </div>
                            <div class="card-stat">
                                <span class="stat-value">{{
                                    completedTasks
                                }}</span>
                                <span class="stat-total"
                                    >/{{ totalTasks }}</span
                                >
                            </div>
                            <div class="progress-container">
                                <div class="progress-background"></div>
                                <div
                                    class="progress-bar"
                                    :style="{ width: completionRate + '%' }"
                                ></div>
                            </div>
                            <div class="card-trend">
                                <span class="trend-indicator"
                                    >+{{ weeklyGrowth }}%</span
                                >
                                <span class="trend-text">本周增长</span>
                            </div>
                        </div>

                        <!-- 平均正确率 -->
                        <div id="accuracy-rate" class="status-card">
                            <div class="card-gradient"></div>
                            <div class="card-header">
                                <span class="card-title">平均正确率</span>
                                <span class="card-icon">🎯</span>
                            </div>
                            <div class="card-stat">
                                <span class="stat-value">{{
                                    accuracyRate
                                }}</span>
                                <span class="stat-unit">%</span>
                            </div>
                            <div class="progress-container">
                                <div class="progress-background"></div>
                                <div
                                    class="progress-bar"
                                    :style="{ width: accuracyRate + '%' }"
                                ></div>
                            </div>
                            <div class="card-trend">
                                <span class="trend-indicator"
                                    >+{{ accuracyGrowth }}%</span
                                >
                                <span class="trend-text">较上周</span>
                            </div>
                        </div>

                        <!-- 掌握知识点 -->
                        <div id="mastered-topics" class="status-card">
                            <div class="card-gradient"></div>
                            <div class="card-header">
                                <span class="card-title">掌握知识点</span>
                                <span class="card-icon">📚</span>
                            </div>
                            <div class="card-stat">
                                <span class="stat-value">{{
                                    masteredTopics
                                }}</span>
                                <span class="stat-total"
                                    >/{{ totalTopics }}</span
                                >
                            </div>
                            <div class="progress-container">
                                <div class="progress-background"></div>
                                <div
                                    class="progress-bar"
                                    :style="{ width: masteryRate + '%' }"
                                ></div>
                            </div>
                            <div class="card-trend">
                                <span class="trend-indicator"
                                    >+{{ newTopics }}</span
                                >
                                <span class="trend-text">本周新增</span>
                            </div>
                        </div>

                        <!-- 学习时长 -->
                        <div id="study-duration" class="status-card">
                            <div class="card-gradient"></div>
                            <div class="card-header">
                                <span class="card-title">本周学习时长</span>
                                <span class="card-icon">⏱️</span>
                            </div>
                            <div class="card-stat">
                                <span class="stat-value">{{
                                    weeklyStudyHours
                                }}</span>
                                <span class="stat-unit">小时</span>
                            </div>
                            <div class="progress-container">
                                <div class="progress-background"></div>
                                <div
                                    class="progress-bar"
                                    :style="{
                                        width: studyHoursRateStudent + '%',
                                    }"
                                ></div>
                            </div>
                            <div class="card-trend">
                                <span class="trend-indicator"
                                    >+{{ hoursIncrease }}</span
                                >
                                <span class="trend-text">较上周</span>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- 核心功能区 -->
                <section class="core-features">
                    <h3 class="section-title">
                        <span class="title-icon">🚀</span>
                        核心功能
                        <span class="title-underline"></span>
                    </h3>
                    <div class="features-grid">
                        <!-- 题库资源 -->
                        <div
                            class="feature-card floating-card"
                            @click="navigateTo('/student/quiz-challenge')"
                        >
                            <div class="feature-hover-effect"></div>
                            <div class="feature-icon-container">
                                <span class="feature-icon">📝</span>
                            </div>
                            <h4 class="feature-title">题库资源</h4>
                            <p class="feature-description">
                                访问超过{{
                                    questionBankCount
                                }}道题目，涵盖多种题型和难度级别，随时进行练习。
                            </p>
                            <div class="feature-stats">
                                <span class="feature-count"
                                    >最近完成：{{ recentAnswers }}道</span
                                >
                                <span class="feature-badge">🔥推荐</span>
                            </div>
                        </div>

                        <!-- 作答历史 -->
                        <div
                            class="feature-card floating-card"
                            @click="navigateTo('/student/history')"
                        >
                            <div class="feature-hover-effect"></div>
                            <div class="feature-icon-container">
                                <span class="feature-icon">📈</span>
                            </div>
                            <h4 class="feature-title">作答历史</h4>
                            <p class="feature-description">
                                查看你的学习轨迹，分析错题原因，针对性提升学习效率和成绩。
                            </p>
                            <div class="feature-stats">
                                <span class="feature-count"
                                    >错误率：{{ errorRate }}%</span
                                >
                                <span class="feature-badge">📊数据</span>
                            </div>
                        </div>

                        <!-- 状态可视化 -->
                        <div
                            class="feature-card floating-card"
                            @click="navigateTo('/student/visualization')"
                        >
                            <div class="feature-hover-effect"></div>
                            <div class="feature-icon-container">
                                <span class="feature-icon">🎨</span>
                            </div>
                            <h4 class="feature-title">状态可视化</h4>
                            <p class="feature-description">
                                通过图表直观了解自己的学习进度和知识掌握情况，智能规划学习路径。
                            </p>
                            <div class="feature-stats">
                                <span class="feature-count"
                                    >支持多维度分析</span
                                >
                                <span class="feature-badge">📱动态</span>
                            </div>
                        </div>

                        <!-- 知识结构 -->
                        <div
                            class="feature-card floating-card"
                            @click="navigateTo('/student/knowledge-structure')"
                        >
                            <div class="feature-hover-effect"></div>
                            <div class="feature-icon-container">
                                <span class="feature-icon">🧩</span>
                            </div>
                            <h4 class="feature-title">知识结构</h4>
                            <p class="feature-description">
                                浏览{{
                                    knowledgeDomains
                                }}个知识领域的完整结构，构建系统化知识体系。
                            </p>
                            <div class="feature-stats">
                                <span class="feature-count">持续更新中</span>
                                <span class="feature-badge">🌐全面</span>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- 知识图谱和推荐区域 -->
                <section class="knowledge-section">
                    <div class="knowledge-graph-container">
                        <h3 class="section-title">
                            <span class="title-icon">🔗</span>
                            知识图谱
                            <span class="title-underline"></span>
                        </h3>
                        <div class="graph-visualization">
                            <div class="graph-gradient-bg"></div>
                            <div class="knowledge-nodes">
                                <!-- 主节点 -->
                                <div
                                    class="knowledge-node primary-node"
                                    style="top: 40%; left: 20%"
                                >
                                    <div class="node-glow"></div>
                                    编程语言基础
                                </div>
                                <div
                                    class="knowledge-node primary-node"
                                    style="top: 40%; left: 60%"
                                >
                                    <div class="node-glow"></div>
                                    数据结构与算法
                                </div>

                                <!-- 从节点 -->
                                <div
                                    class="knowledge-node secondary-node"
                                    style="top: 20%; left: 30%"
                                >
                                    JavaScript
                                </div>
                                <div
                                    class="knowledge-node secondary-node"
                                    style="top: 20%; left: 70%"
                                >
                                    数组
                                </div>
                                <div
                                    class="knowledge-node secondary-node"
                                    style="top: 60%; left: 30%"
                                >
                                    HTML/CSS
                                </div>
                                <div
                                    class="knowledge-node secondary-node"
                                    style="top: 60%; left: 70%"
                                >
                                    排序算法
                                </div>

                                <!-- 连接线背景 -->
                                <div class="knowledge-connections"></div>
                            </div>
                            <button
                                class="explore-graph-btn"
                                @click="exploreKnowledgeGraph"
                            >
                                探索完整图谱
                            </button>
                        </div>
                    </div>

                    <div class="recommendations-container">
                        <h3 class="section-title">
                            <span class="title-icon">💡</span>
                            为你推荐
                            <span class="title-underline"></span>
                        </h3>
                        <div class="recommendation-cards">
                            <div
                                class="recommendation-card"
                                v-for="(item, index) in recommendations"
                                :key="index"
                            >
                                <div class="recommendation-icon">
                                    {{ item.icon }}
                                </div>
                                <div class="recommendation-content">
                                    <h4 class="recommendation-title">
                                        {{ item.title }}
                                    </h4>
                                    <p class="recommendation-desc">
                                        {{ item.description }}
                                    </p>
                                    <div class="recommendation-meta">
                                        <span
                                            class="recommendation-difficulty"
                                            >{{ item.difficulty }}</span
                                        >
                                        <span class="recommendation-time">{{
                                            item.estimatedTime
                                        }}</span>
                                    </div>
                                </div>
                                <button
                                    class="start-learning-btn"
                                    @click="startLearning(item.id)"
                                >
                                    开始学习
                                </button>
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

// 路由实例
const router = useRouter();

// 身份与权限相关状态
const isTeacher = ref(false);
const userRole = ref("student"); // 可能的值: student, teacher, admin

// 学生信息和数据
const userName = ref("张明");
const studentId = ref("20230001");
const userAvatar = ref("👨");
const learningDays = ref(127);
const continuousDays = ref(15);

// 学生学习数据
const completedTasks = ref(387);
const totalTasks = ref(1250);
const completionRate = ref(Math.round((387 / 1250) * 100));
const weeklyGrowth = ref(12);

const accuracyRate = ref(78);
const accuracyGrowth = ref(5);

const masteredTopics = ref(24);
const totalTopics = ref(60);
const masteryRate = ref(Math.round((24 / 60) * 100));
const newTopics = ref(3);

const weeklyStudyHours = ref(18.5);
const studyHoursRateStudent = ref(Math.round((18.5 / 30) * 100));
const hoursIncrease = ref(3.2);

// 学生资源数据
const questionBankCount = ref(15000);
const recentAnswers = ref(42);
const errorRate = ref(23);
const knowledgeDomains = ref(8);

// 学生推荐内容
const recommendations = reactive([
    {
        id: 1,
        icon: "💻",
        title: "编程入门基础",
        description:
            "学习编程基础知识，包括变量、数据类型、循环和条件语句等核心概念",
        difficulty: "初级",
        estimatedTime: "45分钟",
    },
    {
        id: 2,
        icon: "🌐",
        title: "前端开发实战",
        description:
            "学习HTML、CSS和JavaScript基础，完成一个简单响应式网页的开发",
        difficulty: "中等",
        estimatedTime: "60分钟",
    },
    {
        id: 3,
        icon: "📊",
        title: "算法与数据结构进阶",
        description: "深入学习常用算法与数据结构，提升编程思维和问题解决能力",
        difficulty: "高级",
        estimatedTime: "90分钟",
    },
]);

// 权限判断计算属性
const canAccessStudentFunctions = computed(() => {
    return userRole.value === "student" || userRole.value === "admin";
});

// 确保DOM加载完成后执行初始化
onMounted(() => {
    console.log("学生首页组件已挂载，界面初始化完成");
    userRole.value = "student";
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
    console.log("学生退出登录");
    try {
        router.push("/login");
    } catch (error) {
        console.error("退出登录失败:", error);
    }
};

// 学生特有方法
const exploreKnowledgeGraph = () => {
    if (canAccessStudentFunctions.value) {
        console.log("探索完整知识图谱");
        navigateTo("/student/knowledge-graph");
    } else {
        console.log("权限不足：无法访问学生功能");
    }
};

const startLearning = (id) => {
    if (canAccessStudentFunctions.value) {
        console.log(`开始学习: ${id}`);
        navigateTo(`/student/learning/${id}`);
    } else {
        console.log("权限不足：无法访问学生功能");
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

.avatar-student {
    background-color: #3b82f6;
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

.study-streak {
    display: flex;
    gap: 2rem;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    border: 1px solid rgba(59, 130, 246, 0.1);
}

.streak-info {
    display: flex;
    flex-direction: column;
}

.streak-label {
    color: #64748b;
    font-size: 0.9rem;
}

.streak-value {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1e3a8a;
}

.streak-icon {
    font-size: 1.8rem;
    color: #f59e0b;
}

/* 状态卡片通用样式 */
.status-overview {
    margin-bottom: 2.5rem;
}

.status-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.2rem;
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

.progress-glow {
    position: absolute;
    top: -5px;
    left: 0;
    width: 100%;
    height: 18px;
    background: inherit;
    filter: blur(8px);
    opacity: 0.5;
    z-index: 0;
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

.trend-down {
    color: #ef4444;
}

.trend-text {
    color: #64748b;
}

/* 学生状态卡片特殊样式 */
#completed-tasks .card-gradient,
#completed-tasks .progress-bar {
    background: linear-gradient(135deg, #10b981, #059669);
}

#accuracy-rate .card-gradient,
#accuracy-rate .progress-bar {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
}

#mastered-topics .card-gradient,
#mastered-topics .progress-bar {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

#study-duration .card-gradient,
#study-duration .progress-bar {
    background: linear-gradient(135deg, #f59e0b, #d97706);
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

/* 知识与任务区域通用样式 */
.knowledge-section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
}

.knowledge-graph-container,
.recommendations-container {
    display: flex;
    flex-direction: column;
}

.graph-visualization {
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

.graph-gradient-bg {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 300px;
    height: 300px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    filter: blur(120px);
    opacity: 0.1;
    transform: translate(-50%, -50%);
}

/* 学生知识图谱样式 */
.knowledge-nodes {
    position: relative;
    width: 100%;
    height: calc(100% - 50px);
}

.knowledge-node {
    position: absolute;
    padding: 0.8rem 1.2rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    z-index: 2;
}

.primary-node {
    background: rgba(67, 97, 238, 0.15);
    border: 1px solid rgba(67, 97, 238, 0.3);
    min-width: 120px;
    font-size: 1.1rem;
}

.node-glow {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 12px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    filter: blur(15px);
    opacity: 0.3;
    z-index: -1;
}

.secondary-node {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(59, 130, 246, 0.1);
    min-width: 100px;
    font-size: 1rem;
}

.knowledge-node:hover {
    transform: scale(1.05);
}

.knowledge-connections {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    pointer-events: none;
    background-image: radial-gradient(
            circle,
            rgba(59, 130, 246, 0.3) 1px,
            transparent 1px
        ),
        linear-gradient(to right, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(59, 130, 246, 0.1) 1px, transparent 1px);
    background-size: 30px 30px;
}

/* 按钮通用样式 */
.explore-graph-btn {
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

.explore-graph-btn:hover {
    background: rgba(59, 130, 246, 0.2);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

/* 推荐卡片样式 */
.recommendation-cards {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    height: 100%;
}

.recommendation-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 16px;
    padding: 1.2rem;
    border: 1px solid rgba(240, 249, 255, 0.8);
    display: flex;
    gap: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
}

.recommendation-card:hover {
    background: #f8fafc;
    transform: translateX(5px);
    box-shadow: 0 5px 15px rgba(59, 130, 246, 0.1);
}

.recommendation-icon {
    font-size: 1.8rem;
    min-width: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #3b82f6;
}

.recommendation-content {
    flex: 1;
}

.recommendation-title {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #1e3a8a;
}

.recommendation-desc {
    color: #64748b;
    font-size: 0.9rem;
    line-height: 1.4;
    margin-bottom: 0.8rem;
}

.recommendation-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.8rem;
}

.recommendation-difficulty {
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.recommendation-time {
    color: #64748b;
}

.start-learning-btn {
    align-self: flex-end;
    padding: 0.6rem 1.2rem;
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
}

.start-learning-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
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
    .knowledge-section {
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

    .status-cards {
        grid-template-columns: 1fr;
    }
}
</style>
