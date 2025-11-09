<template>
    <div class="question-bank-page">
        <!-- 加载状态界面 -->
        <div class="loading-container" v-if="isLoading">
            <div class="loading-content">
                <div class="loader"></div>
                <h2>正在加载题库内容...</h2>
                <p>请稍候，我们正在为您准备最新的题目数据</p>
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
        <!-- 使用统一的学生头部组件 -->
        <StudentHeader title="题库中心" />

        <!-- 题库内容区域（仅登录状态显示） -->
        <div class="dashboard" v-if="isLoggedIn">
            <!-- 题库总体情况卡片 -->
            <div class="card">
                <h3>题库总体情况</h3>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>已完成题目</span>
                        <span>{{ completedCount }}/{{ totalCount }}</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{
                                width:
                                    (completedCount / totalCount) * 100 + '%',
                            }"
                            :class="
                                getProgressColorClass(
                                    (completedCount / totalCount) * 100
                                )
                            "
                        ></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>平均正确率</span>
                        <span>{{ avgAccuracy }}%</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{ width: avgAccuracy + '%' }"
                            :class="getProgressColorClass(avgAccuracy)"
                        ></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>最近正确率</span>
                        <span>{{ recentAccuracy }}%</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{ width: recentAccuracy + '%' }"
                            :class="getProgressColorClass(recentAccuracy)"
                        ></div>
                    </div>
                </div>
            </div>

            <!-- 题目类型统计卡片 -->
            <div class="card">
                <h3>题目类型统计</h3>
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-value">{{
                            typeStats.singleChoice
                        }}</span>
                        <span class="stat-label">单选题</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{
                            typeStats.multipleChoice
                        }}</span>
                        <span class="stat-label">多选题</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{ typeStats.judgment }}</span>
                        <span class="stat-label">判断题</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{
                            typeStats.shortAnswer
                        }}</span>
                        <span class="stat-label">简答题</span>
                    </div>
                </div>
            </div>

            <!-- 难度分布统计 -->
            <div class="content-section">
                <h3>题目难度分布</h3>
                <div class="chart-table-wrapper">
                    <div class="chart-container">
                        <canvas id="difficultyChart"></canvas>
                    </div>
                    <div class="chart-table">
                        <div class="table-container">
                            <table class="styled-table">
                                <thead>
                                    <tr>
                                        <th>难度</th>
                                        <th>题目数量</th>
                                        <th>平均正确率</th>
                                        <th>已完成</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr class="difficulty-row easy-row">
                                        <td>
                                            <span
                                                class="difficulty-badge difficulty-easy"
                                                >简单</span
                                            >
                                        </td>
                                        <td>{{ difficultyStats.easy }}</td>
                                        <td>
                                            <div class="accuracy-indicator">
                                                <span class="accuracy-value"
                                                    >{{
                                                        difficultyAccuracy.easy
                                                    }}%</span
                                                >
                                                <div class="accuracy-bar">
                                                    <div
                                                        class="accuracy-fill"
                                                        :style="{
                                                            width:
                                                                difficultyAccuracy.easy +
                                                                '%',
                                                        }"
                                                    ></div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            {{ completedDifficulty.easy }}题
                                        </td>
                                    </tr>
                                    <tr class="difficulty-row medium-row">
                                        <td>
                                            <span
                                                class="difficulty-badge difficulty-medium"
                                                >中等</span
                                            >
                                        </td>
                                        <td>{{ difficultyStats.medium }}</td>
                                        <td>
                                            <div class="accuracy-indicator">
                                                <span class="accuracy-value"
                                                    >{{
                                                        difficultyAccuracy.medium
                                                    }}%</span
                                                >
                                                <div class="accuracy-bar">
                                                    <div
                                                        class="accuracy-fill"
                                                        :style="{
                                                            width:
                                                                difficultyAccuracy.medium +
                                                                '%',
                                                        }"
                                                    ></div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            {{ completedDifficulty.medium }}题
                                        </td>
                                    </tr>
                                    <tr class="difficulty-row hard-row">
                                        <td>
                                            <span
                                                class="difficulty-badge difficulty-hard"
                                                >困难</span
                                            >
                                        </td>
                                        <td>{{ difficultyStats.hard }}</td>
                                        <td>
                                            <div class="accuracy-indicator">
                                                <span class="accuracy-value"
                                                    >{{
                                                        difficultyAccuracy.hard
                                                    }}%</span
                                                >
                                                <div class="accuracy-bar">
                                                    <div
                                                        class="accuracy-fill"
                                                        :style="{
                                                            width:
                                                                difficultyAccuracy.hard +
                                                                '%',
                                                        }"
                                                    ></div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            {{ completedDifficulty.hard }}题
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 题目列表区域 -->
            <div class="content-section">
                <div class="section-header">
                    <h3>题目列表</h3>
                    <div class="filter-controls">
                        <div class="filter-control">
                            <label for="type-filter" class="filter-label"
                                >题目类型：</label
                            >
                            <select
                                id="type-filter"
                                v-model="selectedType"
                                @change="filterQuestions"
                                class="type-select"
                            >
                                <option value="all">全部</option>
                                <option value="singleChoice">单选题</option>
                                <option value="multipleChoice">多选题</option>
                                <option value="judgment">判断题</option>
                                <option value="shortAnswer">简答题</option>
                            </select>
                        </div>
                        <div class="filter-control">
                            <label for="difficulty-filter" class="filter-label"
                                >难度：</label
                            >
                            <select
                                id="difficulty-filter"
                                v-model="selectedDifficulty"
                                @change="filterQuestions"
                                class="difficulty-select"
                            >
                                <option value="all">全部</option>
                                <option value="easy">简单</option>
                                <option value="medium">中等</option>
                                <option value="hard">困难</option>
                            </select>
                        </div>
                        <div class="filter-control">
                            <label for="status-filter" class="filter-label"
                                >状态：</label
                            >
                            <select
                                id="status-filter"
                                v-model="selectedStatus"
                                @change="filterQuestions"
                                class="status-select"
                            >
                                <option value="all">全部</option>
                                <option value="completed">已完成</option>
                                <option value="uncompleted">未完成</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="questions-container">
                    <div
                        class="question-card"
                        v-for="question in filteredQuestions"
                        :key="question.id"
                        @click="showQuestionDetail(question)"
                    >
                        <div class="question-header">
                            <div class="question-type" :class="question.type">
                                {{ getQuestionTypeText(question.type) }}
                            </div>

                            <div
                                class="question-difficulty"
                                :class="getDifficultyClass(question.difficulty)"
                            >
                                {{ getDifficultyText(question.difficulty) }}
                            </div>
                        </div>
                        <div class="question-content">
                            <p class="question-text">{{ question.content }}</p>
                            <div
                                v-if="question.completed"
                                class="question-status"
                            >
                                <span
                                    :class="
                                        question.correct
                                            ? 'status-correct'
                                            : 'status-incorrect'
                                    "
                                >
                                    {{
                                        question.correct
                                            ? "回答正确✅"
                                            : "回答错误❌"
                                    }}
                                </span>
                                <span class="accuracy-badge"
                                    >正确率: {{ question.accuracy }}%</span
                                >
                            </div>
                            <div
                                v-else
                                class="question-status status-uncompleted"
                            >
                                未完成🔒
                            </div>
                        </div>
                    </div>
                    <div v-if="filteredQuestions.length === 0" class="no-data">
                        没有符合条件的题目
                    </div>
                </div>
            </div>
        </div>

        <!-- 未登录状态提示 -->
        <div class="unauthorized-message" v-else>
            <div class="message-container">
                <div class="message-icon">🔒</div>
                <h2>请先登录以访问题库内容</h2>
                <p>登录后即可查看和练习各类题目，追踪学习进度</p>
            </div>
        </div>

        <!-- 题目详情弹窗 -->
        <div class="modal" v-if="selectedQuestion && isLoggedIn">
            <div class="modal-content">
                <span class="close" @click="selectedQuestion = null"
                    >&times;</span
                >
                <div class="question-detail-header">
                    <h3>题目详情</h3>
                    <div class="question-meta">
                        <span class="meta-item">{{
                            getQuestionTypeText(selectedQuestion.type)
                        }}</span>
                        <span
                            class="meta-item"
                            :class="
                                getDifficultyClass(selectedQuestion.difficulty)
                            "
                        >
                            {{ getDifficultyText(selectedQuestion.difficulty) }}
                        </span>
                        <span class="meta-item"
                            >正确率: {{ selectedQuestion.accuracy }}%</span
                        >
                    </div>
                </div>
                <div class="question-detail-content">
                    <p class="question-detail-text">
                        {{ selectedQuestion.content }}
                    </p>

                    <div
                        v-if="
                            ['singleChoice', 'multipleChoice'].includes(
                                selectedQuestion.type
                            )
                        "
                        class="question-options"
                    >
                        <h4>选项：</h4>
                        <ul>
                            <li
                                v-for="(
                                    option, index
                                ) in selectedQuestion.options"
                                :key="index"
                                class="option-item"
                            >
                                <span class="option-letter"
                                    >{{
                                        String.fromCharCode(65 + index)
                                    }}.</span
                                >
                                <span class="option-text">{{ option }}</span>
                                <span
                                    v-if="
                                        isCorrectAnswer(selectedQuestion, index)
                                    "
                                    class="correct-marker"
                                    >正确答案</span
                                >
                            </li>
                        </ul>
                    </div>

                    <div
                        v-if="selectedQuestion.type === 'judgment'"
                        class="judgment-options"
                    >
                        <div
                            class="judgment-option"
                            :class="
                                selectedQuestion.correctAnswer === 0
                                    ? 'correct'
                                    : ''
                            "
                        >
                            正确
                        </div>
                        <div
                            class="judgment-option"
                            :class="
                                selectedQuestion.correctAnswer === 1
                                    ? 'correct'
                                    : ''
                            "
                        >
                            错误
                        </div>
                    </div>

                    <div
                        v-if="selectedQuestion.type === 'shortAnswer'"
                        class="answer-section"
                    >
                        <h4>参考答案：</h4>
                        <p class="reference-answer">
                            {{ selectedQuestion.correctAnswer }}
                        </p>
                    </div>

                    <div
                        v-if="selectedQuestion.analysis"
                        class="question-analysis"
                    >
                        <h4>解析：</h4>
                        <p>{{ selectedQuestion.analysis }}</p>
                    </div>
                </div>

                <div
                    v-if="selectedQuestion.completed"
                    class="your-answer-section"
                >
                    <h4>你的答案：</h4>
                    <p
                        class="your-answer"
                        :class="
                            selectedQuestion.correct ? 'correct' : 'incorrect'
                        "
                    >
                        {{ getYourAnswerText(selectedQuestion) }}
                    </p>
                </div>

                <div class="question-actions">
                    <button class="action-btn review-btn">加入错题本</button>
                    <button class="action-btn practice-btn">重新练习</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 返回首页按钮 -->
    <a href="/student/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span class="text">首页</span>
    </a>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import Chart from "chart.js/auto";
import { useRouter } from "vue-router";
import api from "../../../api/index";
import StudentHeader from "../StudentHeader.vue";

// 路由实例
const router = useRouter();

// 登录状态管理 - 与StudentHeader组件保持一致
const isLoggedIn = ref(true);

// 用户信息由StudentHeader组件管理

// 题目列表数据
const questionList = ref([]);

// 筛选相关变量
const selectedType = ref("all");
const selectedDifficulty = ref("all");
const selectedStatus = ref("all");

// 定义响应式变量存储数据
const isLoading = ref(true); // 加载状态
const errorMsg = ref(""); // 错误信息

// 数据库题目类型映射
const TYPE_MAP = {
    0: "singleChoice",
    1: "multipleChoice",
    2: "judgment",
    3: "shortAnswer",
};

/**
 * 转换数据库题目到前端格式
 */
const convertDbQuestion = (dbQuestion) => {
    const { id, quiz, result, analysis, type } = dbQuestion;

    // 处理题目内容和选项
    const lines = quiz
        .split(/[\n\r]+/)
        .map((line) => line.trim())
        .filter((line) => line);

    const [content, ...optionLines] = lines;

    // 处理选项
    let options = [];
    if ([0, 1].includes(type)) {
        // 单选题/多选题
        options = optionLines.map((line) =>
            line.replace(/^[A-Za-z][.、) )]\s*/, "")
        );
    } else if (type === 2) {
        // 判断题
        options = ["正确", "错误"];
    }

    // 处理正确答案
    let correctAnswer = null;
    if (type === 0) {
        // 单选题
        correctAnswer = result.charCodeAt(0) - "A".charCodeAt(0);
    } else if (type === 1) {
        // 多选题
        const answers = result.replace(/,/g, "").split("");
        correctAnswer = answers.map(
            (char) => char.charCodeAt(0) - "A".charCodeAt(0)
        );
    } else if (type === 2) {
        // 判断题
        correctAnswer = ["对", "正确", "A"].includes(result) ? 0 : 1;
    } else if (type === 3) {
        // 简答题
        correctAnswer = result || "暂无答案";
    }

    // 模拟难度
    let difficulty = "medium";
    if (id % 3 === 0) difficulty = "easy";
    else if (id % 3 === 2) difficulty = "hard";

    return {
        id,
        content,
        type: TYPE_MAP[type] || "singleChoice",
        difficulty,
        options,
        correctAnswer,
        analysis: analysis || "暂无解析",
        accuracy: Math.floor(Math.random() * 30) + 50,
        completed: Math.random() > 0.5,
        correct: Math.random() > 0.3,
        userAnswer:
            Math.random() > 0.5
                ? correctAnswer
                : Math.floor(Math.random() * (options.length || 2)),
    };
};

// 获取用户信息的函数已在StudentHeader组件中实现，此处不再需要

// 加载题目数据
const fetchQuestionData = () => {
    return api
        .getQuestion()
        .then((res) => {
            console.log("获取的题目数据：", res.data);
            if (res.data && res.data.data) {
                // 处理单题或多题数据
                const rawQuestions = Array.isArray(res.data.data)
                    ? res.data.data
                    : [res.data.data];

                // 转换所有题目为前端格式
                questionList.value = rawQuestions.map(convertDbQuestion);

                // 渲染图表
                renderDifficultyChart();
            } else {
                errorMsg.value = "数据格式错误";
            }
        })
        .catch((err) => {
            console.error("获取题目数据失败:", err);
            errorMsg.value = "网络请求错误，请稍后重试";
        });
};

// 页面加载时初始化
onMounted(() => {
    // 加载题目数据（用户信息已由StudentHeader组件加载）
    fetchQuestionData()
        .then(() => {
            isLoading.value = false;
        })
        .catch(() => {
            isLoading.value = false;
        });
});

// 计算统计数据
const totalCount = computed(() => questionList.value.length);
const completedCount = computed(
    () => questionList.value.filter((q) => q.completed).length
);
const avgAccuracy = computed(() => {
    if (questionList.value.length === 0) return 0;
    const sum = questionList.value.reduce((acc, q) => acc + q.accuracy, 0);
    return Math.round(sum / questionList.value.length);
});
const recentAccuracy = computed(() => {
    const recentCompleted = questionList.value
        .filter((q) => q.completed)
        .slice(-10);
    if (recentCompleted.length === 0) return 0;
    const correctCount = recentCompleted.filter((q) => q.correct).length;
    return Math.round((correctCount / recentCompleted.length) * 100);
});

// 筛选题目
const filteredQuestions = computed(() => {
    return questionList.value.filter((question) => {
        if (
            selectedType.value !== "all" &&
            question.type !== selectedType.value
        )
            return false;
        if (
            selectedDifficulty.value !== "all" &&
            question.difficulty !== selectedDifficulty.value
        )
            return false;
        if (selectedStatus.value === "completed" && !question.completed)
            return false;
        if (selectedStatus.value === "uncompleted" && question.completed)
            return false;
        return true;
    });
});

// 统计题目类型数量
const typeStats = computed(() => ({
    singleChoice: questionList.value.filter((q) => q.type === "singleChoice")
        .length,
    multipleChoice: questionList.value.filter(
        (q) => q.type === "multipleChoice"
    ).length,
    judgment: questionList.value.filter((q) => q.type === "judgment").length,
    shortAnswer: questionList.value.filter((q) => q.type === "shortAnswer")
        .length,
}));

// 统计难度分布
const difficultyStats = computed(() => ({
    easy: questionList.value.filter((q) => q.difficulty === "easy").length,
    medium: questionList.value.filter((q) => q.difficulty === "medium").length,
    hard: questionList.value.filter((q) => q.difficulty === "hard").length,
}));

// 各难度正确率
const difficultyAccuracy = computed(() => ({
    easy: calculateAvgAccuracy("easy"),
    medium: calculateAvgAccuracy("medium"),
    hard: calculateAvgAccuracy("hard"),
}));

// 计算各难度平均正确率
const calculateAvgAccuracy = (difficulty) => {
    const questions = questionList.value.filter(
        (q) => q.difficulty === difficulty
    );
    if (questions.length === 0) return 0;
    const totalAccuracy = questions.reduce((sum, q) => sum + q.accuracy, 0);
    return Math.round(totalAccuracy / questions.length);
};

// 已完成各难度题目数量
const completedDifficulty = computed(() => ({
    easy: questionList.value.filter(
        (q) => q.difficulty === "easy" && q.completed
    ).length,
    medium: questionList.value.filter(
        (q) => q.difficulty === "medium" && q.completed
    ).length,
    hard: questionList.value.filter(
        (q) => q.difficulty === "hard" && q.completed
    ).length,
}));

// 选中的题目
const selectedQuestion = ref(null);

// 图表实例
let difficultyChartInstance = null;

// 判断是否为正确答案
const isCorrectAnswer = (question, index) => {
    if (question.type === "singleChoice")
        return question.correctAnswer === index;
    if (question.type === "multipleChoice")
        return question.correctAnswer.includes(index);
    return false;
};

// 根据进度获取颜色类
const getProgressColorClass = (progress) => {
    if (progress < 50) return "progress-low";
    if (progress < 75) return "progress-medium";
    return "progress-high";
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

// 获取难度文本
const getDifficultyText = (difficulty) => {
    const difficulties = {
        easy: "简单",
        medium: "中等",
        hard: "困难",
    };
    return difficulties[difficulty] || "未知难度";
};

// 获取难度样式类
const getDifficultyClass = (difficulty) => {
    const classes = {
        easy: "difficulty-easy",
        medium: "difficulty-medium",
        hard: "difficulty-hard",
    };
    return classes[difficulty] || "";
};

// 获取用户答案文本
const getYourAnswerText = (question) => {
    if (!question.userAnswer) return "未作答";

    if (question.type === "singleChoice") {
        return question.options[question.userAnswer]
            ? `${String.fromCharCode(65 + question.userAnswer)}.${
                  question.options[question.userAnswer]
              }`
            : "无效答案";
    } else if (question.type === "multipleChoice") {
        if (!Array.isArray(question.userAnswer)) return "无效答案";
        return question.userAnswer
            .map(
                (index) =>
                    question.options[index] &&
                    `${String.fromCharCode(65 + index)}.${
                        question.options[index]
                    }`
            )
            .filter(Boolean)
            .join("，");
    } else if (question.type === "judgment") {
        return question.userAnswer === 0 ? "正确" : "错误";
    } else if (question.type === "shortAnswer") {
        return question.userAnswer || "未填写";
    }
    return "无答案";
};

// 显示题目详情
const showQuestionDetail = (question) => {
    selectedQuestion.value = { ...question };
};

// 渲染难度分布图表
const renderDifficultyChart = () => {
    const ctx = document.getElementById("difficultyChart");
    if (!ctx) return;

    if (difficultyChartInstance) {
        difficultyChartInstance.destroy();
    }

    const colors = {
        easy: {
            background: "rgba(46, 204, 113, 0.7)",
            border: "rgba(46, 204, 113, 1)",
            hover: "rgba(46, 204, 113, 0.9)",
        },
        medium: {
            background: "rgba(234, 179, 8, 0.7)",
            border: "rgba(234, 179, 8, 1)",
            hover: "rgba(234, 179, 8, 0.9)",
        },
        hard: {
            background: "rgba(239, 68, 68, 0.7)",
            border: "rgba(239, 68, 68, 1)",
            hover: "rgba(239, 68, 68, 0.9)",
        },
    };

    difficultyChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["简单", "中等", "困难"],
            datasets: [
                {
                    data: [
                        difficultyStats.value.easy,
                        difficultyStats.value.medium,
                        difficultyStats.value.hard,
                    ],
                    backgroundColor: [
                        colors.easy.background,
                        colors.medium.background,
                        colors.hard.background,
                    ],
                    borderColor: [
                        colors.easy.border,
                        colors.medium.border,
                        colors.hard.border,
                    ],
                    borderWidth: 2,
                    borderRadius: 8,
                    hoverOffset: 20,
                    hoverBackgroundColor: [
                        colors.easy.hover,
                        colors.medium.hover,
                        colors.hard.hover,
                    ],
                },
            ],
        },
        options: {
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500,
                easing: "easeOutQuart",
            },
            layout: {
                padding: { top: 20, right: 20, bottom: 40, left: 20 },
            },
            cutout: "50%",
            plugins: {
                title: {
                    display: true,
                    text: "题目难度分布",
                    font: {
                        size: 18,
                        weight: "bold",
                        family: "'Arial', sans-serif",
                    },
                    color: "#2c3e50",
                    padding: { bottom: 20 },
                },
                legend: {
                    position: "bottom",
                    labels: {
                        font: { size: 14, family: "'Arial', sans-serif" },
                        color: "#34495e",
                        padding: 25,
                        usePointStyle: true,
                        pointStyle: "circle",
                        font: { weight: "500" },
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(255, 255, 255, 0.95)",
                    titleColor: "#2c3e50",
                    bodyColor: "#3498db",
                    borderColor: "#e1e4e8",
                    borderWidth: 1,
                    padding: 12,
                    boxPadding: 6,
                    usePointStyle: true,
                    callbacks: {
                        label: function (context) {
                            const label = context.label || "";
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce(
                                (a, b) => a + b,
                                0
                            );
                            const percentage = Math.round(
                                (value / total) * 100
                            );
                            return `${label}: ${value} 题 (${percentage}%)`;
                        },
                    },
                    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
                    animationDuration: 300,
                },
            },
            interaction: { mode: "nearest", intersect: false, axis: "x" },
            responsive: true,
            maintainAspectRatio: false,
        },
    });
};

// 筛选题目
const filterQuestions = () => {
    // 由computed属性自动处理
};

// 跳转功能
const goToHome = () => {
    router.push("/student/index");
};

const goToLogin = () => {
    router.push({ name: "Login", params: { type: "login" } });
};

const goToRegister = () => {
    router.push({ name: "Register", params: { type: "register" } });
};

const retryLoad = () => {
    // 重置状态
    isLoading.value = true;
    errorMsg.value = "";

    // 重新加载数据
    Promise.all([fetchUserInfo(), fetchQuestionData()])
        .then(() => {
            isLoading.value = false;
        })
        .catch(() => {
            isLoading.value = false;
            errorMsg.value = "重试加载失败，请检查网络连接后再试";
        });
};
</script>

<style scoped>
.loading-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    transition: opacity 0.3s ease;
}

.loading-content {
    text-align: center;
    padding: 30px;
    border-radius: 12px;
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    max-width: 500px;
    width: 90%;
}

.loader {
    width: 60px;
    height: 60px;
    margin: 0 auto 20px;
    border: 5px solid #f0f4f8;
    border-top: 5px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1.2s linear infinite;
    position: relative;
}

.loader::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80%;
    height: 80%;
    border: 3px dashed #93c5fd;
    border-radius: 50%;
    animation: spin-reverse 1.8s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

@keyframes spin-reverse {
    0% {
        transform: translate(-50%, -50%) rotate(0deg);
    }
    100% {
        transform: translate(-50%, -50%) rotate(-360deg);
    }
}

.loading-content h2 {
    color: #1e3a8a;
    margin-bottom: 10px;
    font-size: 22px;
}

.loading-content p {
    color: #64748b;
    font-size: 15px;
    line-height: 1.6;
}

/* 加载失败界面样式 */
.error-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #fef2f2;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    padding: 20px;
}

.error-content {
    text-align: center;
    padding: 40px 30px;
    border-radius: 12px;
    background: white;
    box-shadow: 0 10px 30px rgba(239, 68, 68, 0.1);
    max-width: 500px;
    width: 100%;
}

.error-icon {
    font-size: 60px;
    margin-bottom: 25px;
    color: #dc2626;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
    100% {
        transform: scale(1);
    }
}

.error-content h2 {
    color: #b91c1c;
    margin-bottom: 15px;
    font-size: 24px;
}

.error-message {
    color: #7f1d1d;
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 30px;
    padding: 15px;
    background-color: #fef2f2;
    border-radius: 8px;
    border-left: 4px solid #ef4444;
}

.retry-btn,
.home-btn {
    padding: 10px 24px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    margin: 0 8px;
    transition: all 0.3s ease;
}

.retry-btn {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    color: white;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.retry-btn:hover {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.home-btn {
    background: linear-gradient(90deg, #64748b, #334155);
    color: white;
    box-shadow: 0 2px 8px rgba(52, 64, 84, 0.3);
}

.home-btn:hover {
    background: linear-gradient(90deg, #334155, #64748b);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 64, 84, 0.4);
}

.auth-header {
    justify-content: space-between;
}

.auth-buttons {
    display: flex;
    gap: 10px;
}

.auth-btn {
    padding: 9px 18px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.login-btn {
    background: linear-gradient(90deg, #3498db, #2980b9);
    color: white;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.login-btn:hover {
    background: linear-gradient(90deg, #2980b9, #3498db);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

.register-btn {
    background: linear-gradient(90deg, #2ecc71, #27ae60);
    color: white;
    box-shadow: 0 2px 8px rgba(46, 204, 113, 0.3);
}

.register-btn:hover {
    background: linear-gradient(90deg, #27ae60, #2ecc71);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(46, 204, 113, 0.4);
}

.unauthorized-message {
    min-height: calc(100vh - 120px);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.message-container {
    text-align: center;
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    padding: 40px 30px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(240, 249, 255, 0.8);
    max-width: 500px;
    width: 100%;
}

.message-icon {
    font-size: 50px;
    margin-bottom: 20px;
    color: #3498db;
}

.message-container h2 {
    color: #2c3e50;
    margin-bottom: 15px;
    font-size: 22px;
}

.message-container p {
    color: #7f8c8d;
    font-size: 15px;
    line-height: 1.6;
}

/* 原有样式... */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}
.header-left {
    display: flex;
    align-items: center;
    gap: 15px;
}
/* 加载界面样式 */
.loading-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    transition: opacity 0.3s ease;
}

.loading-content {
    text-align: center;
    padding: 30px;
    border-radius: 12px;
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    max-width: 500px;
    width: 90%;
}

.loader {
    width: 60px;
    height: 60px;
    margin: 0 auto 20px;
    border: 5px solid #f0f4f8;
    border-top: 5px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1.2s linear infinite;
    position: relative;
}

.loader::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80%;
    height: 80%;
    border: 3px dashed #93c5fd;
    border-radius: 50%;
    animation: spin-reverse 1.8s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

@keyframes spin-reverse {
    0% {
        transform: translate(-50%, -50%) rotate(0deg);
    }
    100% {
        transform: translate(-50%, -50%) rotate(-360deg);
    }
}

.loading-content h2 {
    color: #1e3a8a;
    margin-bottom: 10px;
    font-size: 22px;
}

.loading-content p {
    color: #64748b;
    font-size: 15px;
    line-height: 1.6;
}

/* 加载失败界面样式 */
.error-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #fef2f2;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    padding: 20px;
}

.error-content {
    text-align: center;
    padding: 40px 30px;
    border-radius: 12px;
    background: white;
    box-shadow: 0 10px 30px rgba(239, 68, 68, 0.1);
    max-width: 500px;
    width: 100%;
}

.error-icon {
    font-size: 60px;
    margin-bottom: 25px;
    color: #dc2626;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
    100% {
        transform: scale(1);
    }
}

.error-content h2 {
    color: #b91c1c;
    margin-bottom: 15px;
    font-size: 24px;
}

.error-message {
    color: #7f1d1d;
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 30px;
    padding: 15px;
    background-color: #fef2f2;
    border-radius: 8px;
    border-left: 4px solid #ef4444;
}

.retry-btn,
.home-btn {
    padding: 10px 24px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    margin: 0 8px;
    transition: all 0.3s ease;
}

.retry-btn {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    color: white;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.retry-btn:hover {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.home-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: linear-gradient(90deg, #9b59b6, #3498db);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
    transition: all 0.3s ease;
}

.home-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

.home-icon {
    font-size: 16px;
}

.question-bank-page {
    width: 100%;
    height: 100%;
    padding: 20px;
    background-color: #f4f7f9;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 18px 24px;
    border-bottom: 2px solid transparent;
    border-image: linear-gradient(90deg, #3498db, #9b59b6) 1;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(52, 152, 219, 0.08);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 18px 24px;
    border-bottom: 2px solid transparent;
    border-image: linear-gradient(90deg, #3498db, #9b59b6) 1;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(52, 152, 219, 0.08);
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
    background: linear-gradient(90deg, #3498db, #9b59b6, #3498db);
    background-size: 200% 100%;
    animation: headerGlow 6s ease-in-out infinite;
}

.header h1 {
    margin: 0;
    font-size: 30px;
    font-weight: 600;
    background: linear-gradient(90deg, #2c3e50, #34495e);
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
    background: linear-gradient(180deg, #3498db, #9b59b6);
}

.user-info {
    display: flex;
    align-items: center;
    transition: transform 0.3s ease;
}

.logout-btn {
    margin-left: 15px;
    padding: 9px 18px;
    background: linear-gradient(90deg, #3498db, #2980b9);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px !important;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.logout-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
    background: linear-gradient(90deg, #2980b9, #3498db);
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
    box-shadow: 0 6px 25px rgba(52, 152, 219, 0.12);
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

.user-info {
    font-size: 15px;
    display: flex;
    align-items: center;
}

.dashboard {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    width: 100%;
}

.card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 10px;
    padding: 22px;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(240, 249, 255, 0.8);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 4px;
    background: linear-gradient(180deg, #60a5fa 0%, #2563eb 100%);
    transform: scaleY(0.8);
    opacity: 0.7;
    transition: all 0.4s ease;
}

.card::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(59, 130, 246, 0.25),
        transparent
    );
    transform: translateX(-100%);
    transition: transform 0.7s ease-in-out;
}

.card h3 {
    margin-bottom: 18px;
    color: #1e3a8a;
    font-size: 18px;
    font-weight: 600;
    padding-bottom: 8px;
    border-bottom: 1px dashed rgba(59, 130, 246, 0.2);
    position: relative;
    display: inline-block;
    transition: color 0.3s ease;
}

.card h3::before {
    content: "▷";
    display: inline-block;
    margin-right: 8px;
    font-size: 14px;
    color: #3b82f6;
    vertical-align: middle;
    transform: scale(0.9) translateX(-2px);
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 10px 25px rgba(59, 130, 246, 0.15);
    border-color: rgba(191, 219, 254, 0.8);
}

.card:hover::before {
    transform: scaleY(1);
    opacity: 1;
}

.card:hover::after {
    transform: translateX(100%);
}

.card:hover h3 {
    color: #2563eb;
}

.card:hover h3::before {
    transform: scale(1.2) translateX(0) rotate(90deg);
    color: #2563eb;
}

.card .progress-item,
.card .stat-item {
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .progress-item,
.card:hover .stat-item {
    transform: translateX(3px);
    opacity: 1;
}

.card:hover .progress-item:nth-child(2),
.card:hover .stat-item:nth-child(2) {
    transition-delay: 0.1s;
}

.card:hover .progress-item:nth-child(3),
.card:hover .stat-item:nth-child(3) {
    transition-delay: 0.2s;
}

.stats {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 10px;
}

.stat-item {
    text-align: center;
    min-width: 80px;
}

.stat-value {
    display: block;
    font-size: 28px;
    font-weight: 700;
    color: #2c3e50;
    position: relative;
    padding: 8px 0;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    transition: transform 0.3s ease;
}

.stat-item:hover .stat-value {
    transform: scale(1.05);
}

.stat-value::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
    transition: width 0.3s ease;
}

.stat-item:hover .stat-value::after {
    width: 60%;
}

.stat-label {
    color: #7f8c8d;
    font-size: 14px;
}

.content-section {
    grid-column: 1 / -1;
}

.chart-table-wrapper {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.chart-container {
    flex: 1;
    min-width: 300px;
    position: relative;
    height: 300px;
}

.chart-table {
    flex: 1;
    min-width: 300px;
    overflow-x: auto;
}

.table-container {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f0f0f0;
}

.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    background-color: #fff;
}

.styled-table thead {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.styled-table th {
    padding: 14px 12px;
    text-align: left;
    font-weight: 600;
    color: #334155;
    border-bottom: 1px solid #e2e8f0;
    position: relative;
}

.styled-table th::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(
        90deg,
        rgba(46, 204, 113, 0) 0%,
        rgba(46, 204, 113, 1) 50%,
        rgba(46, 204, 113, 0) 100%
    );
    opacity: 0;
    transition: opacity 0.3s ease;
}

.styled-table th:hover::after {
    opacity: 1;
}

.styled-table td {
    padding: 14px 12px;
    border-bottom: 1px solid #f1f5f9;
    vertical-align: middle;
}

.styled-table .difficulty-row:last-child td {
    border-bottom: none;
}

.styled-table .difficulty-row:hover {
    background-color: #f8fafc;
    transform: translateX(4px);
    transition: all 0.2s ease;
}

.difficulty-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
}

.accuracy-indicator {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.accuracy-value {
    font-weight: 500;
    color: #1e293b;
}

.accuracy-bar {
    height: 6px;
    width: 100%;
    background-color: #f1f5f9;
    border-radius: 3px;
    overflow: hidden;
}

.accuracy-fill {
    height: 100%;
    transition: width 1s ease;
    border-radius: 5px;
}

.easy-row .accuracy-fill {
    background: linear-gradient(90deg, #4ade80 0%, #10b981 100%);
}

.medium-row .accuracy-fill {
    background: linear-gradient(90deg, #facc15 0%, #f59e0b 100%);
}

.hard-row .accuracy-fill {
    background: linear-gradient(90deg, #f87171 0%, #ef4444 100%);
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

th,
td {
    padding: 10px 8px;
    text-align: left;
    border-bottom: 1px solid #f0f0f0;
}

th {
    background-color: #f9f9f9;
    font-weight: bold;
}

tr:hover {
    background-color: #f5f5f5;
}

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
    width: 100%;
    height: 10px;
    background-color: #f0f0f0;
    border-radius: 5px;
    overflow: hidden;
}

.progress {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 5px;
}

.progress-low {
    background: linear-gradient(90deg, #c0392b 0%, #e74c3c 100%);
}

.progress-medium {
    background: linear-gradient(90deg, #d35400 0%, #f39c12 50%, #f1c40f 100%);
}

.progress-high {
    background: linear-gradient(90deg, #1e7e34 0%, #2ecc71 50%, #81c784 100%);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    flex-wrap: wrap;
    gap: 10px;
}

.filter-controls {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.filter-control {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 10px;
    background-color: #f8fafc;
    border-radius: 6px;
}

.filter-label {
    font-size: 14px;
    color: #334155;
}

.filter-control select {
    padding: 6px 25px 6px 10px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    background-color: #fff;
    font-size: 14px;
    color: #1e293b;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 8px center;
    cursor: pointer;
}

.questions-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.question-card {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    border: 1px solid #eee;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
}

.question-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.question-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    font-size: 13px;
}

.question-type {
    padding: 3px 8px;
    border-radius: 4px;
}

.question-type.singleChoice {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    color: #6a1b9a;
}

.question-type.multipleChoice {
    background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
    color: #00838f;
}

.question-type.judgment {
    background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    color: #2c6ecb;
}

.question-type.shortAnswer {
    background: linear-gradient(135deg, #ede7f6 0%, #d1c4e9 100%);
    color: #4527a0;
}

.question-difficulty {
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 500;
}

.difficulty-easy {
    background: linear-gradient(135deg, #e8f5e9 0%, #dcedc8 100%);
    color: #2e7d32;
}

.difficulty-medium {
    background: linear-gradient(135deg, #fff8e1 0%, #ffe082 100%);
    color: #f57c00;
}

.difficulty-hard {
    background: linear-gradient(135deg, #ffebee 0%, #ef9a9a 100%);
    color: #b71c1c;
}

.question-content {
    flex: 1;
}

.question-text {
    margin: 0 0 10px 0;
    color: #263238;
    font-size: 14px;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.question-status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    margin-top: auto;
    padding-top: 10px;
    border-top: 1px dashed #eee;
}

.status-correct {
    color: #43a047;
    font-weight: 500;
}

.status-incorrect {
    color: #e53935;
    font-weight: 500;
}

.status-uncompleted {
    color: #78909c;
    padding-top: 10px;
    border-top: 1px dashed #eee;
    font-size: 13px;
}

.accuracy-badge {
    color: #607d8b;
    background-color: #f5f5f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
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
    padding: 25px;
    border-radius: 8px;
    width: 90%;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
}

.close {
    position: absolute;
    top: 15px;
    right: 15px;
    font-size: 24px;
    cursor: pointer;
    color: #7f8c8d;
}

.question-detail-header {
    margin-bottom: 20px;
}

.question-meta {
    display: flex;
    gap: 10px;
    margin-top: 10px;
    flex-wrap: wrap;
}

.meta-item {
    font-size: 14px;
    padding: 4px 10px;
    border-radius: 4px;
}

.question-detail-content {
    margin-bottom: 20px;
}

.question-detail-text {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
}

.question-options {
    margin-bottom: 20px;
}

.question-options h4,
.answer-section h4,
.question-analysis h4,
.your-answer-section h4 {
    margin-bottom: 10px;
    color: #37474f;
    font-size: 15px;
}

.option-item {
    list-style: none;
    margin-bottom: 10px;
    padding: 8px 10px;
    border-radius: 4px;
    transition: background-color 0.2s;
    display: flex;
    align-items: flex-start;
}

.option-item:hover {
    background-color: #f5f5f5;
}

.option-letter {
    font-weight: bold;
    margin-right: 10px;
    min-width: 20px;
}

.correct-marker {
    margin-left: auto;
    background-color: #e8f5e9;
    color: #2e7d32;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

.judgment-options {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}

.judgment-option {
    flex: 1;
    padding: 15px;
    text-align: center;
    border-radius: 6px;
    border: 1px solid #ddd;
    cursor: default;
}

.judgment-option.correct {
    background-color: #e8f5e9;
    border-color: #a5d6a7;
    color: #2e7d32;
    font-weight: bold;
}

.reference-answer {
    padding: 10px 15px;
    background-color: #f5f5f5;
    border-radius: 4px;
    line-height: 1.6;
}

.question-analysis {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #eee;
}

.question-analysis p {
    line-height: 1.6;
    color: #546e7a;
}

.your-answer-section {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #eee;
}

.your-answer {
    padding: 10px 15px;
    border-radius: 4px;
    line-height: 1.6;
}

.your-answer.correct {
    background-color: #e8f5e9;
    border: 1px solid #a5d6a7;
    color: #2e7d32;
}

.your-answer.incorrect {
    background-color: #ffebee;
    border: 1px solid #ef9a9a;
    color: #c62828;
}

.question-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #eee;
}

.action-btn {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.2s;
}

.review-btn {
    background-color: #f39c12;
    color: white;
}

.review-btn:hover {
    background-color: #e67e22;
}

.practice-btn {
    background-color: #3498db;
    color: white;
}

.practice-btn:hover {
    background-color: #2980b9;
}

.no-data {
    text-align: center;
    color: #888;
    padding: 40px 20px;
    font-style: italic;
    grid-column: 1 / -1;
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

.avatar-default {
    background-color: #3498db;
    color: white;
}

.user-basic h2 {
    font-size: 16px;
    margin: 0;
    color: #2c3e50;
}

.user-id {
    font-size: 12px;
    color: #7f8c8d;
    margin: 0;
}

@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr;
    }

    .chart-table-wrapper {
        flex-direction: column;
    }

    .questions-container {
        grid-template-columns: 1fr;
    }
}

/* 响应式调整 */
@media (max-width: 768px) {
    .back-to-home {
        padding: 10px 16px;
        right: 20px;
        bottom: 20px;
    }

    .back-to-home .text {
        display: none;
    }

    .back-to-home .icon {
        font-size: 20px;
    }
}

/* 返回首页按钮样式 */
.back-to-home {
    position: fixed;
    right: 30px;
    bottom: 30px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 50%, #3b82f6 100%);
    color: white;
    border-radius: 50px;
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
    transition: all 1s ease;
    z-index: 9999;
    border: none;
    cursor: pointer;
    font-weight: 500;
}

.back-to-home .icon {
    font-size: 18px;
}

.back-to-home:hover {
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4);
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #4f46e5 100%);
}

.back-to-home:active {
    transform: translateY(-2px);
}
</style>
