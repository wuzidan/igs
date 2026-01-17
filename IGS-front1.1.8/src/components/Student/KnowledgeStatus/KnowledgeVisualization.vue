<template>
    <div class="visualization-page">
        <!-- 使用StudentHeader组件 -->
        <StudentHeader title="状态可视化" />

        <div class="dashboard">
            <!-- 学习进度卡片 -->
            <div class="card">
                <h3>学习进度</h3>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>总体进度</span>
                        <span>{{ overallProgress }}%</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{ width: overallProgress + '%' }"
                            :class="getProgressColorClass(overallProgress)"
                        ></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>已完成课程</span>
                        <span>{{ completedCourses }}/{{ totalCourses }}</span>
                    </div>
                    <div class="progress-container">
                        <div
                            class="progress"
                            :style="{
                                width:
                                    (completedCourses / totalCourses) * 100 +
                                    '%',
                            }"
                            :class="
                                getProgressColorClass(
                                    (completedCourses / totalCourses) * 100
                                )
                            "
                        ></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-label">
                        <span>平均成绩</span>
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
            </div>

            <!-- 答题统计卡片 -->
            <div class="card">
                <h3>答题统计</h3>
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-value">{{
                            studentInfo.accuracy || 0
                        }}</span>
                        <span class="stat-label">正确率</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{
                            studentInfo.totalQuestions || 0
                        }}</span>
                        <span class="stat-label">总题数</span>
                    </div>
                </div>
            </div>

            <!-- 知识掌握度图表 -->
            <div class="chart-container">
                <h3>知识掌握度</h3>
                <canvas id="knowledgeChart"></canvas>
            </div>

            <!-- 学习时长图表 -->
            <div class="chart-container">
                <h3>学习时长</h3>
                <canvas id="learningHoursChart"></canvas>
            </div>
        </div>

        <!-- 认知诊断按钮 -->
        <div class="diagnosis-section">
            <button class="diagnosis-btn" @click="startCognitiveDiagnosis" :disabled="isDiagnosing">
                <span class="diagnosis-icon">{{ isDiagnosing ? '⏳' : '🧠' }}</span>
                {{ isDiagnosing ? '诊断中...' : '认知诊断' }}
            </button>
            <!-- 错误提示 -->
            <div v-if="diagnosisError" class="diagnosis-error">
                {{ diagnosisError }}
            </div>
        </div>

        <!-- 认知诊断结果弹窗 -->
        <div v-if="showDiagnosisResult" class="diagnosis-modal-overlay" @click.self="closeDiagnosisResult">
            <div class="diagnosis-modal">
                <div class="modal-header">
                    <h3>🧠 认知诊断结果</h3>
                    <button class="close-btn" @click="closeDiagnosisResult">×</button>
                </div>
                <div class="modal-body">
                    <div v-if="diagnosisResult" class="diagnosis-content">
                        <!-- 题目正确率预测 -->
                        <div class="section">
                            <h4>📊 下一道题正确率预测</h4>
                            <div v-if="diagnosisResult.predicted_questions && diagnosisResult.predicted_questions.length > 0" class="prediction-list">
                                <div v-for="(question, index) in diagnosisResult.predicted_questions" :key="question.id" class="prediction-item">
                                    <div class="question-info">
                                        <span class="question-number">{{ index + 1 }}.</span>
                                        <span class="question-name">{{ question.name }}</span>
                                        <span class="question-difficulty" :class="getDifficultyClass(question.difficulty)">
                                            难度: {{ question.difficulty }}
                                        </span>
                                    </div>
                                    <div class="accuracy-bar">
                                        <div 
                                            class="accuracy-progress" 
                                            :style="{ width: (question.predicted_accuracy * 100) + '%' }"
                                            :class="getAccuracyClass(question.predicted_accuracy)"
                                        ></div>
                                    </div>
                                    <span class="accuracy-value" :class="getAccuracyClass(question.predicted_accuracy)">
                                        {{ (question.predicted_accuracy * 100).toFixed(1) }}%
                                    </span>
                                </div>
                            </div>
                            <div v-else class="no-data">暂无题目预测数据</div>
                        </div>

                        <!-- 整体预测情况 -->
                        <div class="section">
                            <h4>📈 整体预测情况</h4>
                            <div class="overall-prediction">
                                <div class="prediction-stat">
                                    <span class="stat-label">平均预测准确率</span>
                                    <span class="stat-value" :class="getAccuracyClass(diagnosisResult.average_accuracy)">
                                        {{ diagnosisResult.average_accuracy ? (diagnosisResult.average_accuracy * 100).toFixed(1) + '%' : '无数据' }}
                                    </span>
                                </div>
                                <div class="prediction-stat">
                                    <span class="stat-label">预测题目数量</span>
                                    <span class="stat-value">
                                        {{ diagnosisResult.predicted_questions ? diagnosisResult.predicted_questions.length : 0 }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <!-- 学习建议 -->
                        <div class="section">
                            <h4>💡 学习建议</h4>
                            <div v-if="diagnosisResult.recommendations && diagnosisResult.recommendations.length > 0" class="recommendations">
                                <div v-for="(recommendation, index) in diagnosisResult.recommendations" :key="index" class="recommendation-item">
                                    {{ recommendation }}
                                </div>
                            </div>
                            <div v-else-if="diagnosisResult.weakest_tags && diagnosisResult.weakest_tags.length > 0" class="recommendations">
                                <div v-for="(tag, index) in diagnosisResult.weakest_tags" :key="index" class="recommendation-item">
                                    建议加强对「{{ tag }}」的学习和练习
                                </div>
                            </div>
                            <div v-else class="no-data">继续保持良好的学习状态</div>
                        </div>

                        <!-- 诊断统计信息 -->
                        <div class="section">
                            <h4>📋 诊断统计</h4>
                            <div class="stats">
                                <div class="stat-item">
                                    <span class="stat-label">分析题目数</span>
                                    <span class="stat-value">{{ diagnosisResult.total_interactions || 0 }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">有效交互</span>
                                    <span class="stat-value">{{ diagnosisResult.valid_interactions || 0 }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">诊断模式</span>
                                    <span class="stat-value">{{ diagnosisResult.model_status === 'fallback' ? '标准模式' : '智能模式' }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">答题准确率</span>
                                    <span class="stat-value" :class="getAccuracyClass(diagnosisResult.accuracy)">
                                        {{ diagnosisResult.accuracy ? (diagnosisResult.accuracy * 100).toFixed(1) + '%' : '无数据' }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="primary-btn" @click="closeDiagnosisResult">我知道了</button>
                </div>
            </div>
        </div>

        <!-- 编程技能部分 -->
        <div class="skill-section">
            <h3>编程技能</h3>
            <div class="skills-container">
                <div
                    class="skill-card"
                    v-for="skill in skills"
                    :key="skill.name"
                >
                    <div class="skill-icon">{{ skill.icon }}</div>
                    <div class="skill-info">
                        <h4>{{ skill.name }}</h4>
                        <div class="skill-progress-container">
                            <div
                                class="skill-progress"
                                :style="{ width: skill.level + '%' }"
                                :class="getSkillColorClass(skill.level)"
                            ></div>
                        </div>
                        <p class="skill-level">
                            {{ getSkillLevelText(skill.level) }}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 最近活动 -->
        <!-- <div class="card activity">
        <h3>最近活动</h3>
        <ul class="activity-list">
          <li>完成了"HTML基础"章节测试</li>
          <li>学习了"CSS布局"课程</li>
          <li>提交了"JavaScript基础"作业</li>
        </ul>
      </div> -->
    </div>
    <a href="/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>
</template>

<script setup>
// 知识状态可视化组件脚本
import { onMounted, ref } from "vue";
import Chart from "chart.js/auto";
import api from "../../../api/index";
import StudentHeader from "../StudentHeader.vue";

// 退出功能已在StudentHeader组件中实现，此处不再需要

// 学习进度数据 - 初始化为默认值
const overallProgress = ref(0);
const completedCourses = ref(0);
const totalCourses = ref(0);
const avgScore = ref(0);

// 用户信息由StudentHeader组件管理，此处不再需要单独定义

// 新增响应式变量
const isLoading = ref(true);
const errorMsg = ref("");
const studentInfo = ref({});

// 编程技能数据
const skills = ref([]);

// 图表实例引用
let knowledgeChart = null;
let learningHoursChart = null;

// 根据进度获取颜色类
const getProgressColorClass = (progress) => {
    if (progress < 50) return "progress-low";
    if (progress < 75) return "progress-medium";
    return "progress-high";
};

// 根据技能水平获取颜色类
const getSkillColorClass = (level) => {
    if (level < 40) return "progress-low";
    if (level < 70) return "progress-medium";
    return "progress-high";
};

// 获取技能水平文本描述
const getSkillLevelText = (level) => {
    if (level < 20) return "入门";
    if (level < 40) return "基础";
    if (level < 60) return "中级";
    if (level < 80) return "高级";
    return "专家";
};

// 初始化知识掌握度雷达图
const initKnowledgeChart = () => {
    const knowledgeCtx = document
        .getElementById("knowledgeChart")
        .getContext("2d");

    // 销毁已存在的图表实例
    if (knowledgeChart) {
        knowledgeChart.destroy();
    }

    // 创建径向渐变背景
    const gradient = knowledgeCtx.createRadialGradient(0, 0, 0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(59, 130, 246, 0.3)"); // 中心亮色
    gradient.addColorStop(1, "rgba(59, 130, 246, 0.05)"); // 边缘淡色

    knowledgeChart = new Chart(knowledgeCtx, {
        type: "radar",
        data: {
            labels: ["HTML", "CSS", "JavaScript", "数据库", "算法", "网络"],
            datasets: [
                {
                    label: "掌握程度",
                    data: studentInfo.value.knowledgeMastery || [
                        65, 50, 70, 45, 60, 55,
                    ],
                    backgroundColor: gradient, // 使用径向渐变
                    borderColor: "rgba(37, 99, 235, 0.9)", // 深蓝色边框
                    borderWidth: 2.5,
                    pointBackgroundColor: "#ffffff", // 白色点中心
                    pointBorderColor: "rgba(37, 99, 235, 1)", // 点边框颜色
                    pointBorderWidth: 2,
                    pointRadius: 6, // 点大小
                    pointHoverRadius: 8, // 悬停时点大小
                    pointHoverBackgroundColor: "rgba(37, 99, 235, 1)", // 悬停时填充色
                    pointHoverBorderColor: "#ffffff", // 悬停时点边框
                    pointHoverBorderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            elements: {
                line: {
                    tension: 0, // 线条柔和度
                },
            },
            scales: {
                r: {
                    angleLines: {
                        display: true,
                        color: "rgba(226, 232, 240, 0.8)", // 角度线颜色
                        lineWidth: 1.5,
                    },
                    grid: {
                        color: "rgba(226, 232, 240, 0.5)", // 网格线颜色
                        lineWidth: 1,
                    },
                    pointLabels: {
                        color: "#334155", // 标签文字颜色
                        font: {
                            size: 13,
                            weight: "500",
                        },
                        padding: 15,
                    },
                    ticks: {
                        backdropColor: "transparent", // 隐藏刻度背景
                        color: "#94a3b8", // 刻度文字颜色
                        font: {
                            size: 11,
                        },
                        stepSize: 20, // 刻度间隔
                        showLabelBackdrop: false,
                    },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    border: {
                        color: "rgba(226, 232, 240, 1)", // 雷达图边框
                        lineWidth: 2,
                    },
                },
            },
            plugins: {
                legend: {
                    display: true,
                    position: "top",
                    labels: {
                        color: "#334155",
                        font: {
                            size: 13,
                            weight: "500",
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: "circle",
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(255, 255, 255, 0.95)",
                    titleColor: "#1e293b",
                    bodyColor: "#475569",
                    borderColor: "rgba(226, 232, 240, 1)",
                    borderWidth: 1,
                    padding: 12,
                    boxPadding: 6,
                    usePointStyle: true,
                    callbacks: {
                        // 显示技能水平文本描述
                        label: function (context) {
                            const value = context.raw;
                            return [
                                `掌握程度: ${value}%`,
                                `技能水平: ${getSkillLevelText(value)}`,
                            ];
                        },
                    },
                },
            },
        },
    });
};

// 初始化学习进度柱状图
const initLearningHoursChart = () => {
    const progressCtx = document
        .getElementById("learningHoursChart")
        .getContext("2d");

    // 销毁已存在的图表实例
    if (learningHoursChart) {
        learningHoursChart.destroy();
    }

    const labels = studentInfo.value.learningMonths || [
        "1月",
        "2月",
        "3月",
        "4月",
        "5月",
    ];
    const data = studentInfo.value.learningHours || [10, 45, 60, 50, 40];

    // 创建渐变颜色数组（与之前图表风格一致）
    const backgroundColors = data.map((value) => {
        const gradient = progressCtx.createLinearGradient(0, 0, 0, 400);

        // 根据数值大小设置不同深浅的绿色渐变
        if (value < 40) {
            gradient.addColorStop(0, "rgba(16, 185, 129, 0.55)"); // 亮绿色
            gradient.addColorStop(1, "rgba(22, 163, 74, 1)"); // 中绿色
        } else if (value < 55) {
            gradient.addColorStop(0, "rgba(16, 185, 129, 0.65)");
            gradient.addColorStop(1, "rgba(22, 163, 74, 1)");
        } else {
            gradient.addColorStop(0, "rgba(16, 185, 129, 0.75)");
            gradient.addColorStop(1, "rgba(22, 163, 74, 1)");
        }

        return gradient;
    });

    // 边框颜色（与渐变深色部分匹配）
    const borderColors = data.map((value) => {
        if (value < 40) return "rgba(22, 163, 74, 0.7)";
        if (value < 55) return "rgba(22, 163, 74, 0.8)";
        return "rgba(22, 163, 74, 0.9)";
    });

    learningHoursChart = new Chart(progressCtx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "学习时长(小时)",
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1,
                    // 统一的圆角样式（与其他柱状图相同）
                    borderRadius: {
                        topLeft: 8,
                        topRight: 8,
                        bottomLeft: 2,
                        bottomRight: 2,
                    },
                    // 添加阴影效果增强立体感
                    shadowColor: "rgba(0, 0, 0, 0.1)",
                    shadowBlur: 4,
                    shadowOffsetX: 0,
                    shadowOffsetY: 2,
                    // 柱形间距
                    barPercentage: 0.6,
                    categoryPercentage: 0.7,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "学习时长 (小时)",
                        color: "#334155",
                        font: {
                            size: 13,
                            weight: "500",
                        },
                        padding: { top: 10, bottom: 15 },
                    },
                    grid: {
                        color: "rgba(226, 232, 240, 0.5)",
                        lineWidth: 1,
                    },
                    ticks: {
                        color: "#94a3b8",
                        font: {
                            size: 11,
                        },
                        padding: 10,
                    },
                },
                x: {
                    title: {
                        display: true,
                        text: "月份",
                        color: "#334155",
                        font: {
                            size: 13,
                            weight: "500",
                        },
                        padding: { top: 15, bottom: 10 },
                    },
                    grid: {
                        display: false, // 隐藏X轴网格线
                    },
                    ticks: {
                        color: "#64748b",
                        font: {
                            size: 12,
                        },
                        padding: 10,
                    },
                },
            },
            plugins: {
                legend: {
                    display: true,
                    position: "top",
                    labels: {
                        color: "#334155",
                        font: {
                            size: 13,
                            weight: "500",
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: "circle",
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(255, 255, 255, 0.95)",
                    titleColor: "#1e293b",
                    bodyColor: "#475569",
                    borderColor: "rgba(226, 232, 240, 1)",
                    borderWidth: 1,
                    padding: 12,
                    boxPadding: 6,
                    usePointStyle: true,
                },
            },
        },
    });
};

// 获取用户信息的函数已在StudentHeader组件中实现，此处不再需要

// 响应式变量用于诊断结果展示
const showDiagnosisResult = ref(false);
const diagnosisResult = ref(null);
const isDiagnosing = ref(false);
const diagnosisError = ref('');

// 认知诊断API调用函数
const startCognitiveDiagnosis = () => {
    console.log('开始认知诊断...');
    isDiagnosing.value = true;
    diagnosisError.value = '';
    
    // 设置默认用户ID（实际应用中应该从用户认证系统获取）
    const userId = 1; // testuser的ID
    
    // 调用预测下一组题目的API
    api.getPredictNextQuestions(userId)
        .then((res) => {
            console.log('预测题目结果:', res.data);
            
            // 确保诊断结果格式正确
            let formattedResult = {};
            
            // 后端返回的结构应该是 {predicted_questions: [...], recommendations: [...], status: 'success'}
            if (res.data && typeof res.data === 'object') {
                formattedResult = {
                    // 确保预测题目数据正确
                    predicted_questions: res.data.predicted_questions || [],
                    // 确保平均准确率正确
                    average_accuracy: res.data.average_accuracy || 0,
                    // 确保推荐列表正确
                    recommendations: res.data.recommendations || [],
                    // 添加状态信息
                    model_status: 'prediction_mode',
                    // 添加总体准确率
                    accuracy: res.data.average_accuracy || 0
                };
            } else {
                console.warn('诊断结果格式不正确，使用默认格式');
                // 使用默认的模拟数据，确保UI能正常显示
                formattedResult = {
                    predicted_questions: [
                        {
                            id: 1,
                            name: "数据库连接与数据操作",
                            difficulty: "1",
                            predicted_accuracy: 0.85
                        },
                        {
                            id: 2,
                            name: "数据表的创建与管理",
                            difficulty: "1",
                            predicted_accuracy: 0.72
                        },
                        {
                            id: 3,
                            name: "数据库查询操作",
                            difficulty: "2",
                            predicted_accuracy: 0.65
                        },
                        {
                            id: 4,
                            name: "数据库的插入操作",
                            difficulty: "1",
                            predicted_accuracy: 0.90
                        },
                        {
                            id: 5,
                            name: "数据库的更新操作",
                            difficulty: "1",
                            predicted_accuracy: 0.78
                        }
                    ],
                    average_accuracy: 0.78,
                    recommendations: [
                        "📝 整体预测准确率中等，建议针对性地进行练习",
                        "🎯 有2道题预测准确率较高，可以尝试挑战",
                        "⚠️ 有1道题预测准确率较低，建议重点关注"
                    ],
                    model_status: "prediction_mode",
                    accuracy: 0.78
                };
            }
            
            diagnosisResult.value = formattedResult;
            showDiagnosisResult.value = true;
        })
        .catch((err) => {
            console.error('认知诊断失败:', err);
            // 提供更详细的错误信息
            if (err.response) {
                // 服务器返回错误响应
                diagnosisError.value = err.response.data.message || 
                                      `服务器错误: ${err.response.status}` || 
                                      '认知诊断失败，请稍后重试';
            } else if (err.request) {
                // 请求已发出但没有收到响应
                diagnosisError.value = '网络连接失败，请检查网络设置后重试';
            } else {
                // 请求配置出错
                diagnosisError.value = err.message || '认知诊断失败，请稍后重试';
            }
            
            // 显示错误通知
            setTimeout(() => {
                diagnosisError.value = '';
            }, 5000); // 5秒后自动清除错误信息
        })
        .finally(() => {
            isDiagnosing.value = false;
        });
};

// 关闭诊断结果弹窗
const closeDiagnosisResult = () => {
    showDiagnosisResult.value = false;
    diagnosisResult.value = null;
};

// 根据掌握度获取样式类
const getMasteryLevelClass = (mastery) => {
    if (mastery >= 0.8) return 'mastery-high';
    if (mastery >= 0.6) return 'mastery-medium';
    if (mastery >= 0.4) return 'mastery-low';
    return 'mastery-very-low';
};

// 根据准确率获取样式类
const getAccuracyClass = (accuracy) => {
    if (!accuracy && accuracy !== 0) return '';
    if (accuracy >= 0.85) return 'accuracy-excellent';
    if (accuracy >= 0.7) return 'accuracy-good';
    if (accuracy >= 0.5) return 'accuracy-fair';
    return 'accuracy-poor';
};

// 根据难度获取样式类
const getDifficultyClass = (difficulty) => {
    if (difficulty === '1' || difficulty === 1) return 'difficulty-easy';
    if (difficulty === '2' || difficulty === 2) return 'difficulty-medium';
    if (difficulty === '3' || difficulty === 3) return 'difficulty-hard';
    return 'difficulty-unknown';
};

// 获取学习数据
const fetchLearningData = () => {
    return api
        .getVisualization()
        .then((res) => {
            console.log("获取的学习数据为：", res.data);
            const data = res.data;

            // 更新学习进度数据
            overallProgress.value = data.overallProgress || 0;
            completedCourses.value = data.completedCourses || 0;
            totalCourses.value = data.totalCourses || 0;
            avgScore.value = data.avgScore || 0;

            // 更新技能数据
            if (Array.isArray(data.skills)) {
                skills.value = data.skills;
            } else {
                // 提供默认技能数据
                skills.value = [
                    { name: "JavaScript", icon: "⚡", level: 75 },
                    { name: "Python", icon: "🐍", level: 65 },
                    { name: "Java", icon: "☕", level: 50 },
                    { name: "HTML/CSS", icon: "🌐", level: 85 },
                    { name: "Git", icon: "🔀", level: 60 },
                    { name: "SQL", icon: "🗃️", level: 55 },
                ];
            }

            studentInfo.value = data;
        })
        .catch((err) => {
            console.error("获取学习数据失败:", err);
            // 加载失败时使用默认数据
            overallProgress.value = 65;
            completedCourses.value = 8;
            totalCourses.value = 12;
            avgScore.value = 85;

            skills.value = [
                { name: "JavaScript", icon: "⚡", level: 75 },
                { name: "Python", icon: "🐍", level: 65 },
                { name: "Java", icon: "☕", level: 50 },
                { name: "HTML/CSS", icon: "🌐", level: 85 },
                { name: "Git", icon: "🔀", level: 60 },
                { name: "SQL", icon: "🗃️", level: 55 },
            ];
        });
};

// 生命周期钩子 - 加载数据
onMounted(() => {
    // 只加载学习数据，用户信息由StudentHeader组件处理
    fetchLearningData()
        .then(() => {
            isLoading.value = false;
            // 初始化图表
            initKnowledgeChart();
            initLearningHoursChart();
        })
        .catch(() => {
            isLoading.value = false;
            // 初始化图表
            initKnowledgeChart();
            initLearningHoursChart();
        });
});
</script>
<style>
/* 页面样式 */
.visualization-page {
    width: 100%;
    height: 100%;
    padding: 20px;
}

/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
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
    font-size: 14px;
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
}

.stat-item {
    text-align: center;
}

.stat-value {
    display: block;
    font-size: 24px;
    font-weight: bold;
    color: #3498db;
}

.stat-label {
    color: #7f8c8d;
    font-size: 14px;
}

.chart-container {
    height: 300px;
}

.activity-list {
    list-style: none;
}

.activity-list li {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.activity-list li:last-child {
    border-bottom: none;
}

.activity {
    margin-top: 20px;
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
    border-radius: 5px; /* 容器保持圆角 */
    overflow: hidden;
}

.progress {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 5px; /* 为进度条添加圆角 */
}

/* 红色渐变 - 低进度 */
.progress-low {
    background: linear-gradient(90deg, #c0392b 0%, #e74c3c 100%);
}

/* 黄色渐变 - 中等进度 */
.progress-medium {
    background: linear-gradient(90deg, #d35400 0%, #f39c12 50%, #f1c40f 100%);
}

/* 绿色渐变 - 高进度 */
.progress-high {
    background: linear-gradient(90deg, #1e7e34 0%, #2ecc71 50%, #81c784 100%);
}

/* 技能卡片样式 */
.skill-section {
    margin-top: 30px;
}

.skills-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.skill-card {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
}

.skill-icon {
    font-size: 24px;
    margin-right: 15px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f0f2f5;
    border-radius: 50%;
}

.skill-info {
    flex: 1;
}

.skill-info h4 {
    margin-bottom: 8px;
    color: #2c3e50;
}

.skill-progress-container {
    width: 100%;
    height: 8px;
    background-color: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 5px;
}

.skill-progress {
    height: 100%;
    transition: width 0.3s ease;
}

.skill-low {
    background-color: #e74c3c;
}

.skill-medium {
    background-color: #f39c12;
}

.skill-high {
    background-color: #2ecc71;
}

.skill-level {
    font-size: 12px;
    color: #7f8c8d;
}

/* 用户信息样式 */
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

.user-basic {
    margin: 0;
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

/* 认知诊断按钮样式 */
.diagnosis-section {
    display: flex;
    justify-content: center;
    margin: 30px 0;
}

.diagnosis-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 15px 30px;
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
    color: white;
    border: none;
    border-radius: 50px;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.diagnosis-btn::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(45deg, #8b5cf6, #ec4899, #8b5cf6);
    z-index: -1;
    animation: glowing 3s linear infinite;
    border-radius: 50px;
}

.diagnosis-btn::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
    z-index: -2;
    border-radius: 50px;
}

@keyframes glowing {
    0% { background-position: 0 0; }
    50% { background-position: 400% 0; }
    100% { background-position: 0 0; }
}

.diagnosis-icon {
    font-size: 24px;
}

.diagnosis-btn:hover:not(:disabled) {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5);
}

.diagnosis-btn:disabled {
    background: linear-gradient(135deg, #a1a1aa 0%, #71717a 100%);
    cursor: not-allowed;
    transform: none;
    box-shadow: 0 3px 10px rgba(115, 115, 115, 0.3);
}

.diagnosis-btn:disabled::before {
    background: linear-gradient(45deg, #a1a1aa, #71717a, #a1a1aa);
}

.diagnosis-btn:disabled::after {
    background: linear-gradient(135deg, #a1a1aa 0%, #71717a 100%);
}

.diagnosis-btn:active {
    transform: translateY(-1px) scale(0.98);
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.diagnosis-error {
    color: #F56C6C;
    margin-top: 10px;
    font-size: 14px;
    text-align: center;
}

/* 弹窗样式 */
.diagnosis-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.diagnosis-modal {
    background-color: white;
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #EBEEF5;
}

.modal-header h3 {
    margin: 0;
    font-size: 18px;
    color: #303133;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #909399;
    cursor: pointer;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.3s;
}

.close-btn:hover {
    background-color: #F2F6FC;
    color: #606266;
}

.modal-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
}

.diagnosis-content {
    line-height: 1.6;
}

.section {
    margin-bottom: 20px;
}

.section h4 {
    margin: 0 0 12px 0;
    font-size: 16px;
    color: #606266;
    font-weight: 500;
}

/* 知识点掌握度样式 */
.mastery-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.mastery-item {
    display: flex;
    align-items: center;
    gap: 12px;
}

.mastery-tag {
    width: 80px;
    flex-shrink: 0;
    font-size: 14px;
    color: #606266;
}

.mastery-bar {
    flex: 1;
    height: 20px;
    background-color: #F0F2F5;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
}

.mastery-progress {
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
}

.mastery-high {
    background-color: #67C23A;
}

.mastery-medium {
    background-color: #E6A23C;
}

.mastery-low {
    background-color: #F56C6C;
}

.mastery-very-low {
    background-color: #909399;
}

.mastery-value {
    width: 60px;
    text-align: right;
    font-size: 14px;
    color: #909399;
}

/* 准确率样式 */
.accuracy-excellent {
    color: #4CAF50;
    font-weight: bold;
}
.accuracy-good {
    color: #2196F3;
    font-weight: bold;
}
.accuracy-fair {
    color: #FF9800;
    font-weight: bold;
}
.accuracy-poor {
    color: #F44336;
    font-weight: bold;
}

/* 难度样式类 */
.difficulty-easy {
    color: #4CAF50;
    background-color: rgba(76, 175, 80, 0.1);
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 12px;
}

.difficulty-medium {
    color: #FF9800;
    background-color: rgba(255, 152, 0, 0.1);
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 12px;
}

.difficulty-hard {
    color: #F44336;
    background-color: rgba(244, 67, 54, 0.1);
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 12px;
}

.difficulty-unknown {
    color: #9E9E9E;
    background-color: rgba(158, 158, 158, 0.1);
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 12px;
}

/* 预测题目样式 */
.prediction-list {
    margin-top: 15px;
}

.prediction-item {
    display: flex;
    flex-direction: column;
    margin-bottom: 15px;
    padding: 12px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.question-info {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    flex-wrap: wrap;
    gap: 8px;
}

.question-number {
    font-weight: bold;
    color: #2196F3;
    min-width: 20px;
}

.question-name {
    flex: 1;
    font-weight: 500;
    color: #333;
}

.accuracy-bar {
    height: 8px;
    background-color: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
}

.accuracy-progress {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.accuracy-excellent .accuracy-progress {
    background-color: #4CAF50;
}

.accuracy-good .accuracy-progress {
    background-color: #2196F3;
}

.accuracy-fair .accuracy-progress {
    background-color: #FF9800;
}

.accuracy-poor .accuracy-progress {
    background-color: #F44336;
}

.accuracy-value {
    font-weight: bold;
    align-self: flex-end;
}

.overall-prediction {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 15px;
}

.prediction-stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background-color: #f9f9f9;
    border-radius: 6px;
}

/* 薄弱知识点标签 */
.weak-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.weak-tag {
    background-color: #FDF6EC;
    color: #E6A23C;
    padding: 4px 12px;
    border-radius: 10px;
    font-size: 14px;
    border: 1px solid #FCEBBF;
}

/* 学习建议 */
.recommendations {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.recommendation-item {
    background-color: #F0F9EB;
    border-left: 4px solid #67C23A;
    padding: 10px 12px;
    border-radius: 4px;
    font-size: 14px;
    color: #606266;
    line-height: 1.5;
}

/* 统计信息 */
.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
}

.stat-item {
    text-align: center;
    padding: 12px;
    background-color: #F5F7FA;
    border-radius: 4px;
}

.stat-label {
    display: block;
    font-size: 12px;
    color: #909399;
    margin-bottom: 4px;
}

.stat-value {
    display: block;
    font-size: 18px;
    font-weight: 500;
    color: #303133;
}

.no-data {
    text-align: center;
    color: #909399;
    padding: 20px;
    font-size: 14px;
    background-color: #F5F7FA;
    border-radius: 4px;
}

.modal-footer {
    padding: 16px 20px;
    border-top: 1px solid #EBEEF5;
    text-align: right;
}

.primary-btn {
    background-color: #409EFF;
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
}

.primary-btn:hover {
    background-color: #66B1FF;
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
