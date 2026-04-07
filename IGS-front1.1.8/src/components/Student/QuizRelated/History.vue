<template>
    <div class="history-page">
        <!-- 加载状态界面 -->
        <div class="loading-container" v-if="isLoading">
            <div class="loading-content">
                <div class="loader"></div>
                <h2>正在加载题库内容...</h2>
                <p>请稍候，您的作答历史正在路上</p>
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

        <!-- 使用StudentHeader组件 -->
        <StudentHeader title="作答历史" />

        <div class="dashboard">
            <!-- 作答总体统计 -->
            <div class="card stats-card">
                <h3>作答总体统计</h3>
                <div class="stats-grid">
                    <div class="stat-card" :class="getStatCardClass('total')">
                        <div class="stat-icon">📊</div>
                        <div class="stat-info">
                            <div class="stat-label">总作答次数</div>
                            <div class="stat-value">{{ totalAttempts }}</div>
                        </div>
                        <div class="stat-trend">
                            <span class="trend-arrow up">↑</span>
                            <span class="trend-text">较上周 +2</span>
                        </div>
                    </div>

                    <div class="stat-card" :class="getStatCardClass('avg')">
                        <div class="stat-icon">⭐</div>
                        <div class="stat-info">
                            <div class="stat-label">平均得分</div>
                            <div class="stat-value">{{ avgScore }}分</div>
                        </div>
                        <div class="stat-trend">
                            <span class="trend-arrow up">↑</span>
                            <span class="trend-text">提升 5分</span>
                        </div>
                    </div>

                    <div class="stat-card" :class="getStatCardClass('time')">
                        <div class="stat-icon">⏱️</div>
                        <div class="stat-info">
                            <div class="stat-label">总耗时</div>
                            <div class="stat-value">{{ totalDuration }}</div>
                        </div>
                        <div class="stat-trend">
                            <span class="trend-arrow down">↓</span>
                            <span class="trend-text">减少 12分钟</span>
                        </div>
                    </div>

                    <div class="stat-card" :class="getStatCardClass('highest')">
                        <div class="stat-icon">🏆</div>
                        <div class="stat-info">
                            <div class="stat-label">最高得分</div>
                            <div class="stat-value">{{ highestScore }}分</div>
                        </div>
                        <div class="stat-trend">
                            <span class="trend-date">{{
                                lastHighestDate
                            }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 得分趋势趋势卡片 -->
            <div class="card">
                <h3>得分趋势</h3>
                <div class="chart-container small-chart">
                    <canvas id="scoreTrendChart"></canvas>
                </div>
            </div>

            <!-- 题目类型正确率统计 -->
            <div class="card">
                <h3>题型正确率统计</h3>
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-value"
                            >{{ typeAccuracy.singleChoice }}%</span
                        >
                        <span class="stat-label">单选题</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value"
                            >{{ typeAccuracy.multipleChoice }}%</span
                        >
                        <span class="stat-label">多选题</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value"
                            >{{ typeAccuracy.judgment }}%</span
                        >
                        <span class="stat-label">判断题</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value"
                            >{{ typeAccuracy.shortAnswer }}%</span
                        >
                        <span class="stat-label">简答题</span>
                    </div>
                </div>
            </div>

            <!-- 难度正确率统计 -->
            <div class="card">
                <h3>难度正确率统计</h3>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>简单题正确率</span>
                        <span>{{ difficultyAccuracy.easy }}%</span>
                    </div>

                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{ width: difficultyAccuracy.easy + '%' }"
                            :class="
                                getProgressColorClass(difficultyAccuracy.easy)
                            "
                        ></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>中等题正确率</span>
                        <span>{{ difficultyAccuracy.medium }}%</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{ width: difficultyAccuracy.medium + '%' }"
                            :class="
                                getProgressColorClass(difficultyAccuracy.medium)
                            "
                        ></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>困难题正确率</span>
                        <span>{{ difficultyAccuracy.hard }}%</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{ width: difficultyAccuracy.hard + '%' }"
                            :class="
                                getProgressColorClass(difficultyAccuracy.hard)
                            "
                        ></div>
                    </div>
                </div>
            </div>

            <!-- 作答历史列表 -->
            <div class="content-section">
                <div class="section-header">
                    <h3>作答记录</h3>
                    <div class="filter-controls">
                        <div class="filter-control">
                            <label for="date-filter" class="filter-label"
                                >日期：</label
                            >
                            <select
                                id="date-filter"
                                v-model="selectedDateRange"
                                @change="filterHistory"
                                class="date-select"
                            >
                                <option value="all">全部</option>
                                <option value="today">今天</option>
                                <option value="week">本周</option>
                                <option value="month">本月</option>
                                <option value="quarter">近三个月</option>
                            </select>
                        </div>
                        <div class="filter-control">
                            <label for="score-filter" class="filter-label"
                                >得分：</label
                            >
                            <select
                                id="score-filter"
                                v-model="selectedScoreRange"
                                @change="filterHistory"
                                class="score-select"
                            >
                                <option value="all">全部</option>
                                <option value="0-60">0-60分</option>
                                <option value="60-80">60-80分</option>
                                <option value="80-100">80-100分</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="history-list">
                    <div
                        class="history-item"
                        v-for="record in filteredRecords"
                        :key="record.id"
                    >
                        <!-- 点击头部展开/折叠详情 -->
                        <div
                            class="history-header"
                            @click="toggleHistoryDetail(record.id)"
                        >
                            <div class="history-type">
                                <span class="type-label">答题模式：</span>
                                <span class="type-value">{{
                                    record.type
                                }}</span>
                            </div>
                            <div class="history-date">
                                <span class="date-label">作答日期：</span>
                                <span class="date-value">{{
                                    record.date
                                }}</span>
                            </div>
                            <div class="history-stats">
                                <div class="stat-item score">
                                    <span class="stat-label">得分：</span>
                                    <span
                                        class="stat-value"
                                        :class="getScoreClass(record.score)"
                                        >{{ record.score }}分</span
                                    >
                                </div>
                                <div class="stat-item time">
                                    <span class="stat-label">用时：</span>
                                    <span class="stat-value">{{
                                        record.duration
                                    }}</span>
                                </div>
                                <div class="stat-item count">
                                    <span class="stat-label">题目数：</span>
                                    <span class="stat-value">{{
                                        getRecordStats(record).questionCount
                                    }}</span>
                                </div>
                                <div class="toggle-icon">
                                    <span v-if="record.expanded">−</span>
                                    <span v-else>+</span>
                                </div>
                            </div>
                        </div>

                        <!-- 详情内容 -->
                        <div class="history-detail" v-if="record.expanded">
                            <div class="accuracy-summary">
                                <div class="accuracy-item">
                                    <span class="accuracy-label">题目数：</span>
                                    <span class="accuracy-value"
                                        >{{
                                            getRecordStats(record)
                                                .questionCount
                                        }}题</span
                                    >
                                </div>
                                <div class="accuracy-item">
                                    <span class="accuracy-label">正确：</span>
                                    <span class="accuracy-value correct"
                                        >{{
                                            getRecordStats(record).correctCount
                                        }}题</span
                                    >
                                </div>
                                <div class="accuracy-item">
                                    <span class="accuracy-label">错误：</span>
                                    <span class="accuracy-value incorrect"
                                        >{{
                                            getRecordStats(record)
                                                .questionCount -
                                            getRecordStats(record).correctCount
                                        }}题</span
                                    >
                                </div>
                                <div class="accuracy-item">
                                    <span class="accuracy-label">正确率：</span>
                                    <span class="accuracy-value"
                                        >{{
                                            getRecordStats(record).accuracy
                                        }}%</span
                                    >
                                </div>
                            </div>

                            <div class="questions-summary">
                                <h4>题目完成情况</h4>
                                <div class="questions-grid">
                                    <div
                                        class="question-status-item"
                                        v-for="(
                                            question, index
                                        ) in record.questions"
                                        :key="question.id"
                                        :class="
                                            question.correct
                                                ? 'correct'
                                                : 'incorrect'
                                        "
                                        @click.stop="
                                            showQuestionDetail(question)
                                        "
                                    >
                                        <span class="question-number">{{
                                            index + 1
                                        }}</span>
                                        <span class="question-icon">{{
                                            question.correct ? "对" : "错"
                                        }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-if="filteredRecords.length === 0" class="no-data">
                        没有符合条件的作答记录
                    </div>
                </div>
            </div>
        </div>

        <!-- 题目详情弹窗 -->
        <div class="modal" v-if="isModalVisible">
            <div class="modal-content">
                <span class="close" @click="closeModal">&times;</span>
                <div class="question-detail-header" v-if="selectedQuestion">
                    <h3>题目详情</h3>
                    <div class="question-meta">
                        <span
                            class="meta-item"
                            :class="selectedQuestion.type"
                            >{{
                                getQuestionTypeText(selectedQuestion.type)
                            }}</span
                        >
                        <span
                            class="meta-item"
                            :class="
                                getDifficultyClass(selectedQuestion.difficulty)
                            "
                        >
                            {{ getDifficultyText(selectedQuestion.difficulty) }}
                        </span>
                        <span
                            class="meta-item"
                            :class="
                                selectedQuestion.correct
                                    ? 'status-correct'
                                    : 'status-incorrect'
                            "
                        >
                            {{
                                selectedQuestion.correct
                                    ? "回答正确"
                                    : "回答错误"
                            }}
                        </span>
                    </div>
                </div>
                <div class="question-detail-content" v-if="selectedQuestion">
                    <p class="question-detail-text">
                        {{ selectedQuestion.content }}
                    </p>

                    <!-- 选项展示（选择题） -->
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
                                :class="{
                                    'correct-option':
                                        selectedQuestion.correctAnswer.includes(
                                            index
                                        ),
                                    'user-option':
                                        selectedQuestion.userAnswer.includes(
                                            index
                                        ),
                                }"
                            >
                                <span class="option-letter"
                                    >{{
                                        String.fromCharCode(65 + index)
                                    }}.</span
                                >
                                <span class="option-text">{{ option }}</span>
                            </li>
                        </ul>
                    </div>

                    <!-- 判断题选项 -->
                    <div
                        v-if="selectedQuestion.type === 'judgment'"
                        class="judgment-options"
                    >
                        <div
                            class="judgment-option"
                            :class="{
                                correct: selectedQuestion.correctAnswer === 0,
                                'user-selected':
                                    selectedQuestion.userAnswer === 0,
                            }"
                        >
                            正确
                        </div>
                        <div
                            class="judgment-option"
                            :class="{
                                correct: selectedQuestion.correctAnswer === 1,
                                'user-selected':
                                    selectedQuestion.userAnswer === 1,
                            }"
                        >
                            错误
                        </div>
                    </div>

                    <!-- 简答题答案 -->
                    <div
                        v-if="selectedQuestion.type === 'shortAnswer'"
                        class="answer-section"
                    >
                        <h4>参考答案：</h4>
                        <p class="reference-answer">
                            {{ selectedQuestion.referenceAnswer }}
                        </p>

                        <h4 style="margin-top: 15px">你的答案：</h4>
                        <p class="user-answer">
                            {{ selectedQuestion.userAnswer || "未作答" }}
                        </p>
                    </div>

                    <!-- 解析 -->
                    <div
                        v-if="selectedQuestion.analysis"
                        class="question-analysis"
                    >
                        <h4>解析：</h4>
                        <p>{{ selectedQuestion.analysis }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <a href="/student/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from "vue";
import Chart from "chart.js/auto";
import api from "../../../api/index";
import StudentHeader from "../StudentHeader.vue";

// 由于使用StudentHeader组件，此处不再需要重复定义用户信息
// 用户信息由StudentHeader组件管理

// 统计数据 - 初始化为空，将由接口数据填充
const totalAttempts = ref(0);
const avgScore = ref(0);
const totalDuration = ref("");
const highestScore = ref(0);
const lastHighestDate = ref("");

// 题型正确率
const typeAccuracy = ref({
    singleChoice: 0,
    multipleChoice: 0,
    judgment: 0,
    shortAnswer: 0,
});

// 难度正确率
const difficultyAccuracy = ref({
    easy: 0,
    medium: 0,
    hard: 0,
});

// 作答记录数据
const historyRecords = ref([]);

// 定义响应式变量存储数据
const historyData = ref(null);
const studentInfoData = ref(null); // 存储个人信息完整数据
const isLoading = ref(true); // 加载状态
const errorMsg = ref(""); // 错误信息，初始为空

// 由于使用StudentHeader组件，此处不再需要重复获取个人信息
// 个人信息由StudentHeader组件获取和管理
const fetchStudentInfo = () => {
    return Promise.resolve(); // 返回空Promise以保持原有调用结构
};

// 获取练习历史数据
const fetchHistoryData = () => {
    return api
        .getHistory()
        .then((res) => {
            console.log("获取的练习历史数据：", res.data);
            const data = res.data;

            historyData.value = data;

            // 赋值统计数据
            totalAttempts.value = data.totalAttempts || 0;
            avgScore.value = data.avgScore || 0;
            totalDuration.value = data.totalDuration || "";
            highestScore.value = data.highestScore || 0;
            lastHighestDate.value = data.lastHighestDate || "";

            // 题型正确率
            typeAccuracy.value = { ...data.typeAccuracy };

            // 难度正确率
            difficultyAccuracy.value = { ...data.difficultyAccuracy };

            // 作答记录
            historyRecords.value = Array.isArray(data.historyRecords)
                ? [...data.historyRecords]
                : [];
        })
        .catch((err) => {
            console.error("获取练习历史失败：", err);
            errorMsg.value = "获取练习数据失败，请稍后重试";
        });
};

onMounted(() => {
    // 并行请求个人信息和练习历史数据
    Promise.all([fetchStudentInfo(), fetchHistoryData()])
        .then(() => {
            isLoading.value = false;
            errorMsg.value = ""; // 确保成功加载时清空错误信息
            // 数据加载完成后渲染图表
            nextTick(() => {
                renderScoreTrendChart();
            });
        })
        .catch(() => {
            isLoading.value = false;
            // 只有在实际出错时才设置错误信息
        });
});

// 获取记录统计信息
const getRecordStats = (record) => {
    const questionCount = record.questions?.length || 0;
    const correctCount = record.questions?.filter((q) => q.correct).length || 0;
    const accuracy =
        questionCount > 0
            ? Math.round((correctCount / questionCount) * 1000) / 10
            : 0;

    return {
        questionCount,
        correctCount,
        accuracy,
    };
};

// 筛选相关
const selectedDateRange = ref("all");
const selectedScoreRange = ref("all");

// 筛选后的记录
const filteredRecords = computed(() => {
    return historyRecords.value.filter((record) => {
        // 日期筛选（简化处理）
        if (selectedDateRange.value !== "all") {
            return true;
        }

        // 分数筛选
        if (selectedScoreRange.value !== "all") {
            const [min, max] = selectedScoreRange.value.split("-").map(Number);
            if (record.score < min || record.score >= max) {
                return false;
            }
        }

        return true;
    });
});

// 题目详情弹窗相关
const selectedQuestion = ref(null);
const isModalVisible = ref(false);

// 图表实例
let scoreTrendChartInstance = null;

// 切换历史详情展开/折叠
const toggleHistoryDetail = (recordId) => {
    const record = historyRecords.value.find((r) => r.id === recordId);
    if (record) {
        record.expanded = !record.expanded;
    }
};

// 显示题目详情
const showQuestionDetail = (question) => {
    selectedQuestion.value = { ...question };
    nextTick(() => {
        isModalVisible.value = true;
    });
};

// 关闭模态框
const closeModal = () => {
    isModalVisible.value = false;
    selectedQuestion.value = null;
};

// 筛选历史记录
const filterHistory = () => {
    // 由computed属性处理
};

// 根据分数获取样式类
const getScoreClass = (score) => {
    if (score >= 80) return "high-score";
    if (score >= 60) return "medium-score";
    return "low-score";
};

// 根据进度获取颜色类
const getProgressColorClass = (progress) => {
    if (progress < 50) return "progress-low";
    if (progress < 75) return "progress-medium";
    return "progress-high";
};

// 根据统计类型获取卡片样式
const getStatCardClass = (type) => {
    const classes = {
        total: "stat-total",
        avg: "stat-avg",
        time: "stat-time",
        highest: "stat-highest",
    };
    return classes[type];
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

// 渲染得分趋势图表
const renderScoreTrendChart = () => {
    const setupChartContainer = () => {
        const ctx = document.getElementById("scoreTrendChart");
        if (ctx) {
            const parent = ctx.parentElement;
            if (parent) {
                parent.style.width = "100%";
                parent.style.height = "300px";
                parent.style.display = "flex";
                parent.style.justifyContent = "center";
                parent.style.alignItems = "center";
            }
            ctx.style.width = "80%";
            ctx.style.height = "80%";
        }
    };

    setupChartContainer();
    const ctx = document.getElementById("scoreTrendChart");
    if (!ctx) return;

    if (scoreTrendChartInstance) {
        scoreTrendChartInstance.destroy();
    }

    // 准备图表数据（取最近5次记录）
    const recentRecords = [...historyRecords.value]
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, 5);

    const labels = recentRecords.map((r) => r.date.split(" ")[0]);
    const scores = recentRecords.map((r) => r.score);

    scoreTrendChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "得分",
                    data: scores,
                    borderColor: "#3498db",
                    backgroundColor: "rgba(52, 152, 219, 0.1)",
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: "#3498db",
                    pointBorderColor: "#fff",
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                },
            ],
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                    },
                },
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    backgroundColor: "rgba(25, 25, 25, 0.95)",
                    titleColor: "#ffffff",
                    bodyColor: "rgba(255, 255, 255, 0.9)",
                    borderColor: "rgba(255, 255, 255, 0.1)",
                    borderWidth: 1,
                    padding: 14,
                    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
                    cornerRadius: 8,
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function (context) {
                            return `得分: ${context.raw}分`;
                        },
                    },
                },
            },
            animation: {
                duration: 1000,
                easing: "easeOutQuart",
            },
        },
    });
};

const retryLoad = () => {
    // 重置状态
    isLoading.value = true;
    errorMsg.value = "";

    // 重新加载数据
    Promise.all([fetchStudentInfo(), fetchHistoryData()])
        .then(() => {
            isLoading.value = false;
            errorMsg.value = "";
        })
        .catch(() => {
            isLoading.value = false;
            errorMsg.value = "重试加载失败，请检查网络连接后再试";
        });
};
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}

.history-page {
    width: 100%;
    min-height: 100vh;
    padding: 20px;
    background-color: #f4f7f9;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 18px 24px; /* 调整内边距，上下稍窄左右稍宽 */
    border-bottom: 2px solid transparent;
    border-image: linear-gradient(90deg, #3498db, #9b59b6) 1; /* 渐变色下边框 */
    background: linear-gradient(
        135deg,
        #ffffff 0%,
        #f8fafc 100%
    ); /* 微妙的渐变背景 */
    border-radius: 12px; /* 增大圆角，更柔和 */
    box-shadow: 0 4px 20px rgba(52, 152, 219, 0.08); /* 浅蓝色调阴影，与主题呼应 */
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* 统一动画曲线 */
}

/* 顶部高光装饰 */
.header::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #3498db, #9b59b6, #3498db);
    background-size: 200% 100%;
    animation: headerGlow 6s ease-in-out infinite; /* 渐变光流动画 */
}

/* 标题文字样式优化 */
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

/* 标题左侧小装饰 */
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

/* 用户信息区域动画 */
.user-info {
    display: flex;
    align-items: center;
    transition: transform 0.3s ease;
}

/* 退出按钮美化 */
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

/* 按钮悬停效果 */
.logout-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
    background: linear-gradient(90deg, #2980b9, #3498db);
}

/* 按钮点击波纹效果 */
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

/* 整体悬停动画 */
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

/* 顶部渐变光流动画 */
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

.logout-btn {
    margin-left: 15px;
    padding: 8px 15px;
    background-color: #e74c3c;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}

.logout-btn:hover {
    background-color: #c0392b;
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

/* 左侧蓝色渐变装饰条 */
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

/* 顶部横向渐变光条 */
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

/* 标题前蓝色装饰图标 */
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

/* 悬停动画效果 */
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

/* 卡片内元素延迟动画 */
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

/* 子元素依次动画 */
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

.stat-item .stat-value {
    display: block;
    font-size: 24px;
    font-weight: bold;
    color: #3498db;
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

.stat-item .stat-value::after {
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
    grid-column: 1 / -1; /* 横跨所有列 */
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

/* 进度条颜色 */
.progress-low {
    background: linear-gradient(90deg, #c0392b 0%, #e74c3c 100%);
}

.progress-medium {
    background: linear-gradient(90deg, #d35400 0%, #f39c12 50%, #f1c40f 100%);
}

.progress-high {
    background: linear-gradient(90deg, #1e7e34 0%, #2ecc71 50%, #81c784 100%);
}

/* 图表容器 */
/* 图表容器的父元素样式 */
.chart-container {
    /* 确保父容器有明确的尺寸 */
    width: 100%;
    height: 400px; /* 根据需要调整高度 */

    /* 使用flex布局实现居中 */
    display: flex;
    justify-content: center; /* 水平居中 */
    align-items: center; /* 垂直居中 */
}

/* 图表本身的样式 */
#scoreTrendChart {
    width: 80%; /* 可以根据需要调整图表宽度 */
    height: 80%; /* 可以根据需要调整图表高度 */
    max-width: 800px; /* 可选：设置最大宽度 */
}

.small-chart {
    height: 180px;
}

/* 筛选控件样式 */
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
    transition: border-color 0.2s;
}

.filter-control select:focus {
    outline: none;
    border-color: #3498db;
}

/* 历史记录列表样式 */
.history-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.history-item {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    border: 1px solid #eee;
    overflow: hidden;
    transition: box-shadow 0.2s;
}

.history-item:hover {
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    cursor: pointer;
    background-color: #fafafa;
    border-bottom: 1px solid #f0f0f0;
    transition: background-color 0.2s;
}

.history-header:hover {
    background-color: #f5f7fa;
}

.history-type,
.history-date {
    display: flex;
    align-items: center;
    gap: 8px;
}

.type-label,
.date-label {
    color: #7f8c8d;
    font-size: 14px;
}

.type-value,
.date-value {
    font-size: 15px;
    color: #2c3e50;
    font-weight: 500;
}

.history-stats {
    display: flex;
    align-items: center;
    gap: 15px;
}

.history-stats .stat-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.history-stats .stat-label {
    color: #7f8c8d;
    font-size: 14px;
}

.history-stats .stat-value {
    font-size: 15px;
    font-weight: 500;
}

.score .stat-value {
    color: #3498db;
}

.time .stat-value {
    color: #9b59b6;
}

.count .stat-value {
    color: #2ecc71;
}

.high-score {
    color: #2ecc71;
}

.medium-score {
    color: #f39c12;
}

.low-score {
    color: #e74c3c;
}

.toggle-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background-color: #eaeaea;
    color: #7f8c8d;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.2s ease;
}

.toggle-icon:hover {
    background-color: #dcdcdc;
    color: #2c3e50;
}

/* 历史详情样式 */
.history-detail {
    padding: 15px 20px;
    border-top: 1px solid #f0f0f0;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.accuracy-summary {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px dashed #eee;
}

.accuracy-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.accuracy-label {
    color: #7f8c8d;
    font-size: 14px;
}

.accuracy-value {
    font-size: 15px;
    font-weight: 500;
}

.accuracy-value.correct {
    color: #2ecc71;
}

.accuracy-value.incorrect {
    color: #e74c3c;
}

.questions-summary {
    margin-top: 15px;
}

.questions-summary h4 {
    margin-bottom: 10px;
    color: #37474f;
    font-size: 15px;
}

.questions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(30px, 1fr));
    gap: 8px;
}

.question-status-item {
    width: 30px;
    height: 30px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
}

.question-status-item:hover {
    transform: scale(1.1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.question-status-item.correct {
    background-color: #e8f5e9;
    border: 1px solid #a5d6a7;
    color: #2e7d32;
}

.question-status-item.incorrect {
    background-color: #ffebee;
    border: 1px solid #ef9a9a;
    color: #c62828;
}

.question-number {
    position: absolute;
    font-size: 8px;
    top: 2px;
    left: 2px;
}

.question-icon {
    font-size: 14px;
}

/* 题目详情模态框 */
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
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s, visibility 0.3s;
}

.modal.active,
.modal {
    opacity: 1;
    visibility: visible;
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
    transform: translateY(20px);
    transition: transform 0.3s;
}

.modal.active .modal-content,
.modal .modal-content {
    transform: translateY(0);
}

.close {
    position: absolute;
    top: 15px;
    right: 15px;
    font-size: 24px;
    cursor: pointer;
    color: #7f8c8d;
    transition: color 0.2s;
    z-index: 1001;
}

.close:hover {
    color: #e74c3c;
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

/* 单选题 - 蓝紫色调 */
.meta-item.singleChoice {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    color: #6a1b9a;
}

/* 多选题 - 靛蓝色调 */
.meta-item.multipleChoice {
    background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
    color: #00838f;
}

/* 判断题 - 蓝紫色调 */
.meta-item.judgment {
    background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    color: #2c6ecb;
}

/* 简答题 - 深紫色调 */
.meta-item.shortAnswer {
    background: linear-gradient(135deg, #ede7f6 0%, #d1c4e9 100%);
    color: #4527a0;
}
.status-correct {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.status-incorrect {
    background-color: #ffebee;
    color: #c62828;
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
.question-analysis h4 {
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

.option-item.correct-option {
    background-color: #e8f5e9;
    border-left: 3px solid #2e7d32;
}

.option-item.user-option {
    border-left: 3px solid #3498db;
}

.option-item:hover {
    background-color: #f5f5f5;
}

.option-letter {
    font-weight: bold;
    margin-right: 10px;
    min-width: 20px;
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
}

.judgment-option.correct {
    background-color: #e8f5e9;
    border-color: #a5d6a7;
    color: #2e7d32;
    font-weight: bold;
}

.judgment-option.user-selected {
    border-color: #3498db;
    background-color: #ebf5fb;
}

.reference-answer {
    padding: 10px 15px;
    background-color: #f5f5f5;
    border-radius: 4px;
    line-height: 1.6;
}

.user-answer {
    padding: 10px 15px;
    background-color: #ebf5fb;
    border: 1px solid #bbdefb;
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

.no-data {
    text-align: center;
    color: #888;
    padding: 40px 20px;
    font-style: italic;
    background-color: white;
    border-radius: 8px;
    border: 1px solid #eee;
}

/* 头像样式 */
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

/* 难度标签样式 */
.difficulty-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 13px;
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

/* 美化的统计卡片样式 */
.stats-card {
    background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
    overflow: hidden;
    position: relative;
}

.stats-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #3498db 0%, #22c55e 100%);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-top: 10px;
}

.stat-card {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    border-color: transparent;
}

.stat-total {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.stat-avg {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.stat-time {
    background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
}

.stat-highest {
    background: linear-gradient(135deg, #fcfafe 0%, #f3e8ff 100%);
}

.stat-icon {
    font-size: 24px;
    margin-bottom: 8px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-info {
    margin-bottom: 8px;
}

.stat-card .stat-label {
    font-size: 13px;
    color: #64748b;
    font-weight: 500;
}

.stat-card .stat-value {
    font-size: 22px;
    font-weight: 700;
    color: #1e293b;
    line-height: 1.2;
}

.stat-trend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
}

.trend-arrow {
    font-weight: bold;
}

.trend-arrow.up {
    color: #10b981;
}

.trend-arrow.down {
    color: #ef4444;
}

.trend-text {
    color: #64748b;
}

.trend-date {
    color: #8b5cf6;
    font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr;
    }

    .history-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .history-stats {
        width: 100%;
        justify-content: space-between;
    }

    .accuracy-summary {
        flex-direction: column;
        gap: 8px;
    }

    .stats-grid {
        grid-template-columns: 1fr;
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
    transition: all 0.3s ease;
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
