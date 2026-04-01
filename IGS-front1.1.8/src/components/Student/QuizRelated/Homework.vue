<template>
    <div class="homework-page">
        <!-- 加载状态界面 -->
        <div class="loading-container" v-if="isLoading">
            <div class="loading-content">
                <div class="loader"></div>
                <h2>正在加载作业内容...</h2>
                <p>请稍候，我们正在为您准备最新的作业数据</p>
            </div>
        </div>

        <!-- 加载失败界面 -->
        <div class="error-container" v-if="!isLoading && errorMsg">
            <div class="error-content">
                <div class="error-icon">⚠️</div>
                <h2>加载失败</h2>
                <p class="error-message">{{ errorMsg }}</p>
                <button class="retry-btn" @click="retryLoad">重试</button>
            </div>
        </div>

        <!-- 登录状态头部 -->
        <header class="header" v-if="isLoggedIn">
            <div class="header-left">
                <h1>我的作业</h1>
            </div>
            <div class="user-info">
                <div class="avatar-container">
                    <div class="avatar avatar-default">
                        <span class="icon">👨‍🎓</span>
                    </div>
                    <div class="user-basic">
                        <h2>{{ userName }}</h2>
                        <p class="user-id">{{ studentId }}</p>
                    </div>
                </div>
                <button class="logout-btn" @click="logout">退出</button>
            </div>
        </header>

        <!-- 未登录状态头部 -->
        <header class="header auth-header" v-else>
            <h1>我的作业</h1>
            <div class="auth-buttons">
                <button class="auth-btn login-btn" @click="goToLogin">
                    登录
                </button>
                <button class="auth-btn register-btn" @click="goToRegister">
                    注册
                </button>
            </div>
        </header>

        <!-- 作业内容区域（登录后显示） -->
        <div class="dashboard" v-if="isLoggedIn">
            <!-- 作业完成情况卡片 -->
            <div class="card">
                <h3>作业完成情况</h3>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>已完成作业</span>
                        <span
                            >{{ completedHomeworks }}/{{ totalHomeworks }}</span
                        >
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{
                                width:
                                    (completedHomeworks / totalHomeworks) *
                                        100 +
                                    '%',
                            }"
                            :class="
                                getProgressColorClass(
                                    (completedHomeworks / totalHomeworks) * 100
                                )
                            "
                        ></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>平均得分</span>
                        <span>{{ avgScore }}分</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{ width: avgScore + '%' }"
                            :class="getProgressColorClass(avgScore)"
                        ></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>待完成作业</span>
                        <span>{{ pendingHomeworks }}</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress progress-medium"
                            :style="{
                                width:
                                    (pendingHomeworks / totalHomeworks) * 100 +
                                    '%',
                            }"
                        ></div>
                    </div>
                </div>
            </div>

            <!-- 作业类型统计卡片 -->
            <div class="card">
                <h3>作业类型统计</h3>
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-value">{{ typeStats.daily }}</span>
                        <span class="stat-label">日常作业</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{ typeStats.weekly }}</span>
                        <span class="stat-label">周测验</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{ typeStats.monthly }}</span>
                        <span class="stat-label">月考试</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{ typeStats.practice }}</span>
                        <span class="stat-label">练习作业</span>
                    </div>
                </div>
            </div>

            <!-- 作业列表区域 -->
            <div class="content-section">
                <div class="section-header">
                    <h3>作业列表</h3>
                    <div class="filter-controls">
                        <div class="filter-control">
                            <label for="status-filter" class="filter-label"
                                >状态：</label
                            >
                            <select
                                id="status-filter"
                                v-model="selectedStatus"
                                @change="filterHomeworks"
                                class="status-select"
                            >
                                <option value="all">全部</option>
                                <option value="pending">待完成</option>
                                <option value="completed">已完成</option>
                                <option value="overdue">已逾期</option>
                            </select>
                        </div>
                        <div class="filter-control">
                            <label for="type-filter" class="filter-label"
                                >作业类型：</label
                            >
                            <select
                                id="type-filter"
                                v-model="selectedType"
                                @change="filterHomeworks"
                                class="type-select"
                            >
                                <option value="all">全部</option>
                                <option value="daily">日常作业</option>
                                <option value="weekly">周测验</option>
                                <option value="monthly">月考试</option>
                                <option value="practice">练习作业</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="homeworks-container">
                    <div
                        class="homework-card"
                        v-for="homework in filteredHomeworks"
                        :key="homework.id"
                        @click="handleHomeworkClick(homework)"
                    >
                        <div class="homework-header">
                            <div class="homework-type" :class="homework.type">
                                {{ getHomeworkTypeText(homework.type) }}
                            </div>
                            <div
                                class="homework-status"
                                :class="getHomeworkStatusClass(homework.status)"
                            >
                                {{ getHomeworkStatusText(homework.status) }}
                            </div>
                        </div>
                        <div class="homework-content">
                            <h4 class="homework-title">{{ homework.title }}</h4>
                            <p class="homework-description">
                                {{ homework.description }}
                            </p>
                            <div class="homework-meta">
                                <span class="meta-item">
                                    <i>📅</i> 截止：{{
                                        formatDate(homework.deadline)
                                    }}
                                </span>
                                <span class="meta-item">
                                    <i>❓</i> {{ homework.questionCount }}题
                                </span>
                                <span
                                    class="meta-item"
                                    v-if="homework.status === 'completed'"
                                >
                                    <i>⭐</i> 得分：{{ homework.score }}分
                                </span>
                            </div>
                        </div>
                    </div>
                    <div v-if="filteredHomeworks.length === 0" class="no-data">
                        没有符合条件的作业
                    </div>
                </div>
            </div>
        </div>

        <!-- 未登录提示 -->
        <div class="unauthorized-message" v-else>
            <div class="message-container">
                <div class="message-icon">🔒</div>
                <h2>请先登录以访问作业内容</h2>
                <p>登录后即可查看和完成各类作业，追踪学习进度</p>
            </div>
        </div>

        <!-- 作业详情弹窗 -->
        <div
            class="modal"
            v-if="currentHomework && showHomeworkDetail"
            @click="closeHomeworkDetail"
        >
            <div class="modal-content" @click.stop>
                <span class="close" @click="closeHomeworkDetail">&times;</span>
                <div class="homework-detail-header">
                    <h3>作业详情</h3>
                    <div class="homework-detail-title">
                        {{ currentHomework.title }}
                    </div>
                    <div class="homework-meta-detail">
                        <span class="meta-item" :class="currentHomework.type">
                            {{ getHomeworkTypeText(currentHomework.type) }}
                        </span>
                        <span
                            class="meta-item status-item"
                            :class="
                                getHomeworkStatusClass(currentHomework.status)
                            "
                        >
                            {{ getHomeworkStatusText(currentHomework.status) }}
                        </span>
                        <span class="meta-item">
                            <i>📅</i> 发布：{{
                                formatDate(currentHomework.publishDate)
                            }}
                        </span>
                        <span class="meta-item">
                            <i>⏰</i> 截止：{{
                                formatDate(currentHomework.deadline)
                            }}
                        </span>
                        <span class="meta-item">
                            <i>❓</i> {{ currentHomework.questionCount }}题
                        </span>
                        <span
                            class="meta-item"
                            v-if="currentHomework.status === 'completed'"
                        >
                            <i>⭐</i> 得分：{{ currentHomework.score }}分
                        </span>
                    </div>
                </div>

                <div class="homework-detail-content">
                    <h4>作业说明：</h4>
                    <p class="homework-description-detail">
                        {{ currentHomework.description }}
                    </p>

                    <div v-if="currentHomework.status === 'completed'">
                        <h4>完成情况：</h4>
                        <div class="completion-stats">
                            <div class="stat-item">
                                <span class="stat-label">总得分</span>
                                <span class="stat-value"
                                    >{{ currentHomework.score }}分</span
                                >
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">正确率</span>
                                <span class="stat-value"
                                    >{{ currentHomework.accuracy }}%</span
                                >
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">完成时间</span>
                                <span class="stat-value">{{
                                    formatDate(currentHomework.completeTime)
                                }}</span>
                            </div>
                        </div>

                        <button class="review-btn" @click="reviewHomework">
                            查看作业详情
                        </button>
                    </div>

                    <div v-else>
                        <h4>作业内容：</h4>
                        <div class="question-preview">
                            <p>
                                包含{{
                                    currentHomework.questionCount
                                }}道题目，类型包括：
                            </p>
                            <ul class="question-types-list">
                                <li
                                    v-for="(
                                        count, type
                                    ) in currentHomework.questionTypes"
                                    :key="type"
                                >
                                    {{ getQuestionTypeText(type) }}:
                                    {{ count }}题
                                </li>
                            </ul>
                        </div>

                        <button class="start-btn" @click="startHomework">
                            开始做作业
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 做作业弹窗 -->
        <div class="modal" v-if="isDoingHomework" @click="exitDoingHomework">
            <div class="modal-content homework-modal" @click.stop>
                <div class="homework-doing-header">
                    <div class="homework-title">
                        {{ currentHomework.title }}
                    </div>
                    <div class="progress-info">
                        <span
                            >第{{ currentQuestionIndex + 1 }}/{{
                                currentHomework.questionCount
                            }}题</span
                        >
                        <div class="progress-container">
                            <div
                                class="progress progress-high"
                                :style="{
                                    width:
                                        ((currentQuestionIndex + 1) /
                                            currentHomework.questionCount) *
                                            100 +
                                        '%',
                                }"
                            ></div>
                        </div>
                    </div>
                    <button class="exit-btn" @click="exitDoingHomework">
                        退出
                    </button>
                </div>

                <div class="question-doing-content">
                    <div class="question-number">
                        {{ currentQuestionIndex + 1 }}.
                    </div>
                    <div class="question-text">
                        {{ currentQuestion.content }}
                    </div>

                    <!-- 单选/多选题选项 -->
                    <div
                        class="question-options"
                        v-if="
                            ['singleChoice', 'multipleChoice'].includes(
                                currentQuestion.type
                            )
                        "
                    >
                        <div
                            class="option-item"
                            v-for="(option, index) in currentQuestion.options"
                            :key="index"
                            @click="selectOption(index)"
                            :class="{
                                'option-selected': isOptionSelected(index),
                                'option-correct':
                                    showAnswers &&
                                    currentQuestion.correctAnswer === index,
                                'option-incorrect':
                                    showAnswers &&
                                    isOptionSelected(index) &&
                                    currentQuestion.correctAnswer !== index,
                            }"
                        >
                            <span class="option-letter"
                                >{{ String.fromCharCode(65 + index) }}.</span
                            >
                            <span class="option-text">{{ option }}</span>
                        </div>
                    </div>

                    <!-- 判断题选项 -->
                    <div
                        class="judgment-options"
                        v-if="currentQuestion.type === 'judgment'"
                    >
                        <div
                            class="judgment-option"
                            @click="selectJudgmentOption(0)"
                            :class="{
                                'judgment-selected':
                                    userAnswers[currentQuestionIndex] === 0,
                                'option-correct':
                                    showAnswers &&
                                    currentQuestion.correctAnswer === 0,
                                'option-incorrect':
                                    showAnswers &&
                                    userAnswers[currentQuestionIndex] === 0 &&
                                    currentQuestion.correctAnswer !== 0,
                            }"
                        >
                            正确
                        </div>
                        <div
                            class="judgment-option"
                            @click="selectJudgmentOption(1)"
                            :class="{
                                'judgment-selected':
                                    userAnswers[currentQuestionIndex] === 1,
                                'option-correct':
                                    showAnswers &&
                                    currentQuestion.correctAnswer === 1,
                                'option-incorrect':
                                    showAnswers &&
                                    userAnswers[currentQuestionIndex] === 1 &&
                                    currentQuestion.correctAnswer !== 1,
                            }"
                        >
                            错误
                        </div>
                    </div>

                    <!-- 简答题区域 -->
                    <div
                        class="answer-area"
                        v-if="currentQuestion.type === 'shortAnswer'"
                    >
                        <textarea
                            v-model="userAnswers[currentQuestionIndex]"
                            placeholder="请输入答案..."
                            :disabled="showAnswers"
                            :class="{
                                'answer-correct':
                                    showAnswers &&
                                    userAnswers[currentQuestionIndex],
                                'answer-incorrect':
                                    showAnswers &&
                                    !userAnswers[currentQuestionIndex],
                            }"
                        ></textarea>
                        <div v-if="showAnswers" class="correct-answer">
                            <strong>参考答案：</strong>
                            {{ currentQuestion.correctAnswer }}
                        </div>
                    </div>
                </div>

                <div class="question-navigation">
                    <button
                        class="nav-btn prev-btn"
                        @click="prevQuestion"
                        :disabled="currentQuestionIndex === 0"
                    >
                        上一题
                    </button>

                    <button
                        class="nav-btn next-btn"
                        @click="nextQuestion"
                        :disabled="
                            currentQuestionIndex ===
                            currentHomework.questionCount - 1
                        "
                    >
                        下一题
                    </button>

                    <button
                        class="submit-btn"
                        @click="submitHomework"
                        v-if="
                            currentQuestionIndex ===
                                currentHomework.questionCount - 1 &&
                            !showAnswers
                        "
                    >
                        提交作业
                    </button>
                </div>
            </div>
        </div>

        <!-- 返回首页按钮 -->
        <a href="/index" class="back-to-home">
            <span class="icon">🏠</span>
            <span class="text">首页</span>
        </a>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from "vue";
import { useRouter } from "vue-router";
import api from "../../../api/index";

// 路由实例
const router = useRouter();

// 登录状态管理
const isLoggedIn = ref(true);

// 用户信息
const userName = ref("姚竣博");
const studentId = ref("20232132055");

// 作业列表数据
const homeworkList = ref([]);

// 筛选相关变量
const selectedStatus = ref("all");
const selectedType = ref("all");

// 状态管理
const isLoading = ref(true);
const errorMsg = ref("");
const showHomeworkDetail = ref(false);
const currentHomework = ref(null);
const isDoingHomework = ref(false);
const currentQuestionIndex = ref(0);
const currentQuestion = ref(null);
const userAnswers = ref([]);
const showAnswers = ref(false);
const isSubmitting = ref(false);
const homeworkStartedAt = ref(null);

const parseDate = (date) => {
    if (!date) return null;
    const parsedDate = new Date(date);
    return isNaN(parsedDate.getTime()) ? date : parsedDate;
};

const buildQuestionTypes = (questions) => {
    return (questions || []).reduce((acc, question) => {
        const questionType = question.type || "singleChoice";
        acc[questionType] = (acc[questionType] || 0) + 1;
        return acc;
    }, {});
};

const normalizeQuestion = (question, index) => {
    const normalizedType = question.type || "singleChoice";
    const normalizedCorrectAnswer =
        question.correctAnswer ??
        question.correct_answer ??
        (normalizedType === "multipleChoice" ? [] : null);

    return {
        ...question,
        id: question.id ?? question.questionId ?? index + 1,
        questionId: question.questionId ?? question.id ?? index + 1,
        type: normalizedType,
        difficulty: question.difficulty || "medium",
        content: question.content || `题目 ${index + 1}`,
        options: Array.isArray(question.options) ? question.options : [],
        correctAnswer: normalizedCorrectAnswer,
        userAnswer: question.userAnswer ?? question.user_answer ?? null,
        analysis: question.analysis || "",
        completed: Boolean(question.completed),
        exercisePk: question.exercisePk ?? question.exercise_pk ?? null,
        exerciseId: question.exerciseId ?? question.exercise_id ?? null,
        exerciseTitle: question.exerciseTitle ?? question.exercise_title ?? null,
    };
};

const normalizeHomework = (homework, index) => {
    const questions = Array.isArray(homework.questions)
        ? homework.questions.map((question, questionIndex) =>
              normalizeQuestion(question, questionIndex)
          )
        : [];

    return {
        ...homework,
        id: homework.id ?? `homework-${index + 1}`,
        title: homework.title || homework.name || `练习作业 #${index + 1}`,
        description: homework.description || "请完成以下练习题目。",
        type: homework.type || "practice",
        questions,
        questionCount: homework.questionCount || questions.length,
        questionTypes: homework.questionTypes || buildQuestionTypes(questions),
        status:
            homework.status ||
            (questions.length > 0 && questions.every((question) => question.completed)
                ? "completed"
                : "pending"),
        score: Number(homework.score || 0),
        accuracy: Number(homework.accuracy || 0),
        publishDate: parseDate(homework.publishDate || homework.publish_time || new Date()),
        deadline: parseDate(homework.deadline || homework.publishDate || homework.publish_time || new Date()),
        completeTime: parseDate(homework.completeTime || homework.complete_time),
    };
};

const normalizeHomeworkData = (rawData) => {
    if (!Array.isArray(rawData) || rawData.length === 0) {
        return [];
    }

    const firstItem = rawData[0] || {};
    if (Array.isArray(firstItem.questions)) {
        return rawData.map((homework, index) => normalizeHomework(homework, index));
    }

    const normalizedQuestions = rawData.map((question, index) => normalizeQuestion(question, index));
    return [
        normalizeHomework(
            {
                id: "practice-homework",
                title: "练习作业",
                description: "基于当前题目数据生成的练习作业。",
                type: "practice",
                status: normalizedQuestions.every((question) => question.completed) ? "completed" : "pending",
                questions: normalizedQuestions,
                questionCount: normalizedQuestions.length,
                questionTypes: buildQuestionTypes(normalizedQuestions),
            },
            0
        ),
    ];
};

// 从接口获取作业数据
const fetchHomeworks = async () => {
    try {
        isLoading.value = true;
        errorMsg.value = "";

        const response = await api.getHomework();
        console.log("作业接口返回数据：", response);

        const data = Array.isArray(response.data)
            ? response.data
            : response.data.data || [];

        console.log("实际作业数据：", data);

        const formattedData = normalizeHomeworkData(data);

        homeworkList.value = formattedData;
        console.log("格式化后的作业数据：", homeworkList.value);
    } catch (err) {
        console.error("获取作业数据失败详情：", err);
        if (err.response) {
            errorMsg.value = `加载失败（${err.response.status}）：${err.response.statusText}`;
        } else if (err.request) {
            errorMsg.value = "网络错误，无法连接到服务器";
        } else {
            errorMsg.value = `加载失败：${err.message}`;
        }
    } finally {
        isLoading.value = false;
    }
};

// 页面加载时初始化
onMounted(() => {
    fetchHomeworks();
});

// 计算统计数据
const totalHomeworks = computed(() => homeworkList.value.length);
const completedHomeworks = computed(
    () => homeworkList.value.filter((h) => h.status === "completed").length
);
const pendingHomeworks = computed(
    () => homeworkList.value.filter((h) => h.status === "pending").length
);
const avgScore = computed(() => {
    const completed = homeworkList.value.filter(
        (h) => h.status === "completed"
    );
    if (completed.length === 0) return 0;
    const sum = completed.reduce((acc, h) => acc + h.score, 0);
    return Math.round(sum / completed.length);
});

// 统计作业类型数量
const typeStats = computed(() => ({
    daily: homeworkList.value.filter((h) => h.type === "daily").length,
    weekly: homeworkList.value.filter((h) => h.type === "weekly").length,
    monthly: homeworkList.value.filter((h) => h.type === "monthly").length,
    practice: homeworkList.value.filter((h) => h.type === "practice").length,
}));

// 筛选作业
const filteredHomeworks = computed(() => {
    return homeworkList.value.filter((homework) => {
        if (
            selectedStatus.value !== "all" &&
            homework.status !== selectedStatus.value
        )
            return false;
        if (
            selectedType.value !== "all" &&
            homework.type !== selectedType.value
        )
            return false;
        return true;
    });
});

// 格式化日期
const formatDate = (date) => {
    if (!date) return "";
    const d = new Date(date);
    return `${d.getFullYear()}-${(d.getMonth() + 1)
        .toString()
        .padStart(2, "0")}-${d.getDate().toString().padStart(2, "0")} ${d
        .getHours()
        .toString()
        .padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
};

// 获取作业类型文本
const getHomeworkTypeText = (type) => {
    const types = {
        daily: "日常作业",
        weekly: "周测验",
        monthly: "月考试",
        practice: "练习作业",
    };
    return types[type] || "未知类型";
};

// 获取题目类型文本
const getQuestionTypeText = (type) => {
    const types = {
        singleChoice: "单选题",
        multipleChoice: "多选题",
        judgment: "判断题",
        shortAnswer: "简答题",
    };
    return types[type] || "未知类型";
};

// 获取作业状态文本
const getHomeworkStatusText = (status) => {
    const statuses = {
        pending: "待完成",
        completed: "已完成",
        overdue: "已逾期",
    };
    return statuses[status] || "未知状态";
};

// 获取作业状态样式类
const getHomeworkStatusClass = (status) => {
    const classes = {
        pending: "status-pending",
        completed: "status-completed",
        overdue: "status-overdue",
    };
    return classes[status] || "";
};

// 根据进度获取颜色类
const getProgressColorClass = (progress) => {
    if (progress < 50) return "progress-low";
    if (progress < 75) return "progress-medium";
    return "progress-high";
};

// 处理作业点击
const handleHomeworkClick = (homework) => {
    currentHomework.value = { ...homework };
    showHomeworkDetail.value = true;
};

// 关闭作业详情
const closeHomeworkDetail = () => {
    showHomeworkDetail.value = false;
    currentHomework.value = null;
};

// 开始做作业
const startHomework = () => {
    showHomeworkDetail.value = false;
    isDoingHomework.value = true;
    currentQuestionIndex.value = 0;
    currentQuestion.value = currentHomework.value.questions[0];
    userAnswers.value = currentHomework.value.questions.map(
        (question) => question.userAnswer ?? null
    );
    showAnswers.value = false;
    homeworkStartedAt.value = Date.now();
};

// 退出做题
const exitDoingHomework = () => {
    if (confirm("确定要退出作业吗？当前进度不会保存。")) {
        isDoingHomework.value = false;
        currentQuestionIndex.value = 0;
        currentQuestion.value = null;
        userAnswers.value = [];
        homeworkStartedAt.value = null;
    }
};

// 上一题
const prevQuestion = async () => {
    if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--;
        // 强制DOM更新，确保选中状态正确显示
        await nextTick();
        currentQuestion.value =
            currentHomework.value.questions[currentQuestionIndex.value];
    }
};

// 下一题
const nextQuestion = async () => {
    if (currentQuestionIndex.value < currentHomework.value.questionCount - 1) {
        currentQuestionIndex.value++;
        // 强制DOM更新，确保选中状态正确显示
        await nextTick();
        currentQuestion.value =
            currentHomework.value.questions[currentQuestionIndex.value];
    }
};

// 选择选项（单选/多选）
const selectOption = (index) => {
    console.log("选择选项：", index);
    console.log(showAnswers);
    if (showAnswers.value) return;
    console.log(currentQuestion.value.type);
    //单选题
    if (currentQuestion.value.type === "singleChoice") {
        console.log("单选题选择：", index);
        // 直接更新当前题目的答案
        const newAnswers = [...userAnswers.value];
        newAnswers[currentQuestionIndex.value] = index;
        userAnswers.value = newAnswers;

        // 立即触发视图更新
        isOptionSelected(index); // 强制重新计算选中状态

        // 立即跳转到下一题，不使用异步方式
        if (
            currentQuestionIndex.value <
            currentHomework.value.questionCount - 1
        ) {
            currentQuestionIndex.value++;
            currentQuestion.value =
                currentHomework.value.questions[currentQuestionIndex.value];
        }
    } else {
        // 多选题处理
        console.log("多选题选择：", index);
        const newAnswers = [...userAnswers.value];
        if (!newAnswers[currentQuestionIndex.value]) {
            newAnswers[currentQuestionIndex.value] = [];
        }

        const currentQuestionAnswers = [
            ...newAnswers[currentQuestionIndex.value],
        ];
        const idx = currentQuestionAnswers.indexOf(index);

        if (idx === -1) {
            currentQuestionAnswers.push(index);
        } else {
            currentQuestionAnswers.splice(idx, 1);
        }

        newAnswers[currentQuestionIndex.value] = currentQuestionAnswers;
        userAnswers.value = newAnswers;

        // 立即触发视图更新
        isOptionSelected(index); // 强制重新计算选中状态
    }
};

// 选择判断选项
const selectJudgmentOption = (value) => {
    console.log("选择判断题选项：", value);
    console.log(showAnswers.value);
    if (showAnswers.value) return;

    console.log("判断题选择：", value);
    // 直接创建新数组确保响应式更新
    const newAnswers = [...userAnswers.value];
    newAnswers[currentQuestionIndex.value] = value;
    userAnswers.value = newAnswers;

    // 立即触发视图更新
    getJudgmentClass(value); // 强制重新计算选中状态

    // 立即跳转到下一题，不使用异步方式
    if (currentQuestionIndex.value < currentHomework.value.questionCount - 1) {
        currentQuestionIndex.value++;
        currentQuestion.value =
            currentHomework.value.questions[currentQuestionIndex.value];
    }
};

// 计算判断题样式类 - 保留函数但使用新的直接绑定方式
const getJudgmentClass = (value) => {
    return {
        "judgment-selected":
            userAnswers.value[currentQuestionIndex.value] === value,
        "option-correct":
            showAnswers.value && currentQuestion.value.correctAnswer === value,
        "option-incorrect":
            showAnswers.value &&
            userAnswers.value[currentQuestionIndex.value] === value &&
            currentQuestion.value.correctAnswer !== value,
    };
};

// 检查选项是否被选中
const isOptionSelected = (index) => {
    if (!userAnswers.value || !userAnswers.value[currentQuestionIndex.value])
        return false;

    if (currentQuestion.value.type === "singleChoice") {
        return userAnswers.value[currentQuestionIndex.value] === index;
    } else if (currentQuestion.value.type === "multipleChoice") {
        // 确保是数组才调用includes方法
        return (
            Array.isArray(userAnswers.value[currentQuestionIndex.value]) &&
            userAnswers.value[currentQuestionIndex.value].includes(index)
        );
    }
    return false;
};

// 提交作业
const submitHomework = async () => {
    if (isSubmitting.value) return;
    if (confirm("确定要提交作业吗？提交后无法修改。")) {
        let correctCount = 0;
        const questionResults = [];

        currentHomework.value.questions.forEach((q, index) => {
            let isCorrect = false;

            if (q.type === "singleChoice") {
                isCorrect = userAnswers.value[index] === q.correctAnswer;
            } else if (q.type === "multipleChoice") {
                if (
                    userAnswers.value[index] &&
                    Array.isArray(q.correctAnswer)
                ) {
                    // 检查长度是否相同
                    if (
                        userAnswers.value[index].length ===
                        q.correctAnswer.length
                    ) {
                        // 检查所有用户选项是否都在正确答案中，且所有正确答案都被用户选中
                        const sortedUserAnswers = [
                            ...userAnswers.value[index],
                        ].sort();
                        const sortedCorrectAnswers = [
                            ...q.correctAnswer,
                        ].sort();
                        isCorrect = sortedUserAnswers.every(
                            (val, i) => val === sortedCorrectAnswers[i]
                        );
                    }
                }
            } else if (q.type === "judgment") {
                isCorrect = userAnswers.value[index] === q.correctAnswer;
            } else if (q.type === "shortAnswer") {
                // 简答题简单判断是否有回答
                isCorrect = !!userAnswers.value[index];
            }

            if (isCorrect) correctCount++;

            // 保存每道题的结果
            questionResults.push({
                question: q,
                userAnswer: userAnswers.value[index],
                isCorrect,
            });
        });

        // 计算分数和正确率
        const score = Math.round(
            (correctCount / currentHomework.value.questionCount) * 100
        );
        const accuracy = Math.round(
            (correctCount / currentHomework.value.questionCount) * 100
        );

        const durationMinutes = homeworkStartedAt.value
            ? Math.max(1, Math.ceil((Date.now() - homeworkStartedAt.value) / 60000))
            : Math.max(1, currentHomework.value.questionCount);

        const payload = {
            practice_type: "练习",
            durationMinutes,
            score,
            questions: questionResults.map((item) => ({
                id: item.question.id,
                questionId: item.question.questionId,
                exercisePk: item.question.exercisePk,
                exerciseId: item.question.exerciseId,
                type: item.question.type,
                difficulty: item.question.difficulty,
                content: item.question.content,
                userAnswer: item.userAnswer,
                correctAnswer: item.question.correctAnswer,
                options: item.question.options,
                analysis: item.question.analysis,
                correct: item.isCorrect,
            })),
        };

        try {
            isSubmitting.value = true;
            const response = await api.submitPracticeRecord(payload);
            const result = response?.data || {};

            currentHomework.value.status = "completed";
            currentHomework.value.score = score;
            currentHomework.value.accuracy = accuracy;
            currentHomework.value.completeTime = new Date();
            currentHomework.value.results = questionResults;
            currentHomework.value.practiceRecordId = result.practice_record_id;
            currentHomework.value.questions = currentHomework.value.questions.map(
                (question, index) => ({
                    ...question,
                    userAnswer: userAnswers.value[index],
                    completed: true,
                    correct: questionResults[index]?.isCorrect || false,
                    accuracy: questionResults[index]?.isCorrect ? 100 : 0,
                })
            );

            const idx = homeworkList.value.findIndex(
                (h) => h.id === currentHomework.value.id
            );
            if (idx !== -1) {
                homeworkList.value[idx] = { ...currentHomework.value };
            }

            showAnswers.value = true;
            homeworkStartedAt.value = null;

            alert(
                `作业提交成功！\n得分：${score}分\n正确率：${accuracy}%\n已保存题目：${result.saved_questions || currentHomework.value.questionCount}道\n可映射题目：${result.mapped_questions || 0}道`
            );
        } catch (err) {
            console.error("提交作业失败：", err);
            alert(`作业提交失败：${err.message || "请稍后重试"}`);
        } finally {
            isSubmitting.value = false;
        }
    }
};

// 查看作业详情
const reviewHomework = () => {
    showHomeworkDetail.value = false;
    isDoingHomework.value = true;
    currentQuestionIndex.value = 0;
    currentQuestion.value = currentHomework.value.questions[0];
    showAnswers.value = true;
};

// 筛选作业
const filterHomeworks = () => {};

// 退出功能
const logout = () => {
    isLoggedIn.value = false;
    userName.value = "";
    studentId.value = "";
};

// 跳转功能
const goToLogin = () => {
    router.push({ name: "Login", params: { type: "login" } });
};

const goToRegister = () => {
    router.push({ name: "Register", params: { type: "register" } });
};

// 重试加载数据
const retryLoad = () => {
    fetchHomeworks();
};
</script>

<style scoped>
/* 基础样式 */
.loading-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.loading-content {
    text-align: center;
}

.loader {
    width: 50px;
    height: 50px;
    border: 5px solid #f3f3f3;
    border-top: 5px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

.error-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.error-content {
    text-align: center;
    max-width: 400px;
    padding: 20px;
}

.error-icon {
    font-size: 48px;
    margin-bottom: 20px;
}

.error-message {
    margin: 15px 0 25px;
    color: #dc2626;
}

.retry-btn {
    padding: 8px 16px;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background-color: #2563eb;
    color: white;
}

.auth-header {
    justify-content: space-between;
}

.auth-buttons {
    display: flex;
    gap: 10px;
}

.auth-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
}

.login-btn {
    background-color: white;
    color: #2563eb;
}

.register-btn {
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
}

.unauthorized-message {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 500px;
}

.message-container {
    text-align: center;
    max-width: 500px;
    padding: 30px;
}

.message-icon {
    font-size: 64px;
    margin-bottom: 20px;
}

.dashboard {
    padding: 20px;
    max-width: 100%;
    margin: 0 auto;
}

.card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.stats {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
}

.stat-item {
    text-align: center;
    flex: 1;
    padding: 10px;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #2563eb;
}

.stat-label {
    color: #64748b;
    font-size: 14px;
}

.content-section {
    grid-column: 1 / -1;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.filter-controls {
    display: flex;
    gap: 15px;
}

.filter-control {
    display: flex;
    align-items: center;
    gap: 8px;
}

.filter-label {
    color: #64748b;
    font-size: 14px;
}

.status-select,
.type-select {
    padding: 6px 10px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
}

.no-data {
    text-align: center;
    padding: 40px 0;
    color: #64748b;
    background-color: #f8fafc;
    border-radius: 8px;
}

.avatar-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 18px;
}

.avatar-default {
    background-color: rgba(255, 255, 255, 0.2);
}

.user-basic {
    line-height: 1.3;
}

.user-id {
    font-size: 12px;
    opacity: 0.8;
}

.logout-btn {
    margin-left: 15px;
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background-color: white;
    border-radius: 8px;
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    overflow-y: auto;
    padding: 20px;
    position: relative;
}

.close {
    position: absolute;
    top: 15px;
    right: 20px;
    font-size: 24px;
    cursor: pointer;
    color: #64748b;
}

.back-to-home {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #2563eb;
    color: white;
    padding: 10px 15px;
    border-radius: 30px;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 5px;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3);
}

/* 作业特有样式 */
.homeworks-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 15px;
    margin-top: 15px;
    padding: 0 10px;
}

.homework-card {
    background-color: white;
    border-radius: 8px;
    padding: 18px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    border: 1px solid #eee;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    display: flex;
    flex-direction: column;
}

.homework-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.12);
    border-color: rgba(191, 219, 254, 0.5);
}

.homework-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 13px;
}

.homework-type {
    padding: 4px 10px;
    border-radius: 4px;
    font-weight: 500;
}

.homework-type.daily {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    color: #0d47a1;
}

.homework-type.weekly {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    color: #1b5e20;
}

.homework-type.monthly {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    color: #e65100;
}

.homework-type.practice {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    color: #4a148c;
}

.homework-status {
    padding: 4px 10px;
    border-radius: 4px;
    font-weight: 500;
}

.status-pending {
    background: linear-gradient(135deg, #fff8e1 0%, #ffe082 100%);
    color: #f57c00;
}

.status-completed {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    color: #2e7d32;
}

.status-overdue {
    background: linear-gradient(135deg, #ffebee 0%, #ef9a9a 100%);
    color: #c62828;
}

.homework-title {
    margin: 0 0 10px 0;
    color: #1a365d;
    font-size: 16px;
    font-weight: 600;
}

.homework-description {
    margin: 0 0 15px 0;
    color: #4a5568;
    font-size: 14px;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.homework-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    font-size: 13px;
    color: #6b7280;
    margin-top: auto;
    padding-top: 10px;
    border-top: 1px dashed #eee;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

/* 作业详情样式 */
.homework-detail-header {
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
}

.homework-detail-title {
    font-size: 20px;
    font-weight: 600;
    color: #1a365d;
    margin: 10px 0 15px;
}

.homework-meta-detail {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    font-size: 14px;
}

.homework-meta-detail .meta-item {
    padding: 5px 12px;
    border-radius: 4px;
    background-color: #f8fafc;
}

.homework-meta-detail .status-item {
    font-weight: 500;
}

.homework-detail-content {
    margin-bottom: 20px;
}

.homework-description-detail {
    line-height: 1.7;
    color: #4a5568;
    padding: 10px 0 20px;
    border-bottom: 1px solid #eee;
    margin-bottom: 20px;
}

.completion-stats {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.completion-stats .stat-item {
    flex: 1;
    min-width: 120px;
    background-color: #f8fafc;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
}

.completion-stats .stat-label {
    display: block;
    font-size: 14px;
    color: #64748b;
    margin-bottom: 5px;
}

.completion-stats .stat-value {
    display: block;
    font-size: 24px;
    font-weight: 700;
    color: #2563eb;
}

.question-preview {
    background-color: #f8fafc;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 25px;
}

.question-types-list {
    margin-top: 10px;
    margin-left: 20px;
}

.question-types-list li {
    margin-bottom: 5px;
}

.start-btn,
.review-btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.start-btn {
    background: linear-gradient(90deg, #3498db, #2980b9);
    color: white;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.start-btn:hover {
    background: linear-gradient(90deg, #2980b9, #3498db);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

.review-btn {
    background: linear-gradient(90deg, #9b59b6, #7e57c2);
    color: white;
    box-shadow: 0 2px 8px rgba(155, 89, 182, 0.3);
}

.review-btn:hover {
    background: linear-gradient(90deg, #7e57c2, #9b59b6);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(155, 89, 182, 0.4);
}

/* 做题界面样式 */
.homework-modal {
    width: 95%;
    max-width: 900px;
    max-height: 90vh;
}

.homework-doing-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
    position: relative;
}

.homework-doing-header .homework-title {
    font-size: 18px;
    margin-bottom: 15px;
}

.progress-info {
    margin-bottom: 10px;
}

.progress-info span {
    display: block;
    margin-bottom: 5px;
    font-size: 14px;
    color: #64748b;
}

.exit-btn {
    position: absolute;
    top: 0;
    right: 0;
    background: none;
    border: none;
    color: #e53935;
    cursor: pointer;
    font-size: 14px;
    padding: 5px 10px;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.exit-btn:hover {
    background-color: #ffebee;
}

.question-doing-content {
    margin-bottom: 25px;
}

.question-number {
    display: inline-block;
    font-weight: bold;
    margin-right: 8px;
    color: #3b82f6;
}

.question-text {
    display: inline;
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 20px;
}

.question-options {
    margin-top: 15px;
    margin-left: 25px;
}

.option-item {
    padding: 10px 15px;
    margin-bottom: 10px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    position: relative;
    overflow: hidden;
    z-index: 1;
}

/* 鼠标悬浮动画 */
.option-item:hover {
    background-color: #f1f5f9;
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05),
        0 2px 4px -1px rgba(0, 0, 0, 0.03);
    border-color: #cbd5e1;
}

/* 单选/多选题选中样式 - 带从左到右覆盖动画 */
.option-item.option-selected {
    border-color: #93c5fd !important;
    color: #1e40af !important;
    font-weight: 500;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(147, 197, 253, 0.3) !important;
}

/* 从左到右覆盖的蓝色渐变层 */
.option-item.option-selected::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    z-index: -1;
    transform: scaleX(0);
    transform-origin: left center;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: coverFromLeft 0.5s forwards;
}

/* 取消选中时的从右向左消失动画 */
.option-item:not(.option-selected)::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    z-index: -1;
    transform: scaleX(1);
    transform-origin: right center; /* 从右侧开始消失 */
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: coverFromRight 0.5s forwards;
}

/* 定义覆盖和消失动画 */
@keyframes coverFromLeft {
    0% {
        transform: scaleX(0);
    }
    100% {
        transform: scaleX(1);
    }
}

@keyframes coverFromRight {
    0% {
        transform: scaleX(1);
    } /* 起始：完全显示 */
    100% {
        transform: scaleX(0);
    } /* 结束：完全消失 */
}

/* 显示答案时的正确选项样式 */
.option-item.option-correct {
    background-color: #dcfce7 !important;
    border-color: #86efac !important;
    color: #15803d !important;
    font-weight: 600;
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(134, 239, 172, 0.3) !important;
    transition: all 0.3s ease;
}

/* 显示答案时的错误选项样式 */
.option-item.option-incorrect {
    background-color: #fee2e2 !important;
    border-color: #fca5a5 !important;
    color: #b91c1c !important;
    font-weight: 500;
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(252, 165, 165, 0.3) !important;
    transition: all 0.3s ease;
}

/* 判断题选中样式 - 同样应用从左到右覆盖 */
.judgment-option.judgment-selected {
    border-color: #93c5fd !important;
    color: #1e40af !important;
    font-weight: 600;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(147, 197, 253, 0.3) !important;
    position: relative;
    overflow: hidden;
    z-index: 1;
}

.judgment-option.judgment-selected::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #dbeafe;
    z-index: -1;
    transform: scaleX(0);
    transform-origin: left center;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: coverFromLeft 0.5s forwards;
}

/* 判断题取消选中动画 */
.judgment-option:not(.judgment-selected)::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #dbeafe;
    z-index: -1;
    transform: scaleX(1);
    transform-origin: right center;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: coverFromRight 0.5s forwards;
}

/* 判断题正确/错误选项样式保持不变 */
.judgment-option.option-correct {
    background-color: #dcfce7 !important;
    border-color: #86efac !important;
    color: #15803d !important;
    font-weight: 600;
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(134, 239, 172, 0.3) !important;
    transition: all 0.3s ease;
}

.judgment-option.option-incorrect {
    background-color: #fee2e2 !important;
    border-color: #fca5a5 !important;
    color: #b91c1c !important;
    font-weight: 500;
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(252, 165, 165, 0.3) !important;
    transition: all 0.3s ease;
}
.option-letter {
    font-weight: bold;
    margin-right: 10px;
    min-width: 20px;
}

.judgment-options {
    display: flex;
    gap: 20px;
    margin-top: 15px;
    margin-left: 25px;
}

.judgment-option {
    flex: 1;
    padding: 15px;
    text-align: center;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    cursor: pointer;
    transition: all 0.2s ease;
}

.judgment-option:hover {
    background-color: #f1f5f9;
}

.answer-area {
    margin-top: 15px;
    margin-left: 25px;
}

.answer-area textarea {
    width: 100%;
    min-height: 120px;
    padding: 12px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    resize: vertical;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.6;
}

.answer-area textarea:focus {
    outline: none;
    border-color: #93c5fd;
    box-shadow: 0 0 0 2px rgba(147, 197, 253, 0.3);
}

/* 简答题答案样式 */
.answer-area textarea.answer-correct {
    background-color: #dcfce7;
    border-color: #86efac;
}

.answer-area textarea.answer-incorrect {
    background-color: #fee2e2;
    border-color: #fca5a5;
}

.correct-answer {
    margin-top: 15px;
    padding: 10px 15px;
    background-color: #f0f9ff;
    border-left: 4px solid #3b82f6;
    border-radius: 4px;
    font-size: 14px;
    line-height: 1.6;
}

.question-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 15px;
    border-top: 1px solid #eee;
}

.nav-btn {
    padding: 8px 16px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    background-color: white;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s ease;
}

.nav-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.nav-btn:not(:disabled):hover {
    background-color: #f1f5f9;
}

.next-btn {
    color: #2563eb;
    border-color: #93c5fd;
}

.next-btn:not(:disabled):hover {
    background-color: #eff6ff;
}

.submit-btn {
    padding: 8px 20px;
    background: linear-gradient(90deg, #10b981, #059669);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.submit-btn:hover {
    background: linear-gradient(90deg, #059669, #10b981);
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

/* 进度条样式 */
.progress-item {
    margin-bottom: 15px;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 14px;
}

.progress-container {
    height: 8px;
    background-color: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
}

.progress {
    height: 100%;
    transition: width 0.3s ease;
}

.progress-low {
    background-color: #f97316;
}

.progress-medium {
    background-color: #facc15;
}

.progress-high {
    background-color: #10b981;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .homeworks-container {
        grid-template-columns: 1fr;
    }

    .filter-controls {
        flex-direction: column;
        width: 100%;
    }

    .filter-control {
        width: 100%;
    }

    .filter-control select {
        width: 100%;
    }

    .judgment-options {
        flex-direction: column;
    }

    .stats {
        flex-wrap: wrap;
    }

    .stat-item {
        flex-basis: 45%;
        margin-bottom: 10px;
    }
}
</style>
