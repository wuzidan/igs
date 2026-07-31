<template>
    <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>

    <div class="class-tracking-container">
        <div class="page-header">
            <h2>追踪状态</h2>
            <p>查看和跟踪班级学生学习情况</p>
        </div>
        <!-- 筛选区域 -->
        <div class="card">
            <h3>筛选条件</h3>
            <div class="filters-container">
                <div class="filter-item">
                    <label for="class-select">选择班级:</label>
                    <select
                        id="class-select"
                        v-model="selectedClass"
                        class="input-field"
                    >
                        <option value="">全部班级</option>
                        <option
                            v-for="classItem in classes"
                            :key="classItem.id"
                            :value="classItem.id"
                        >
                            {{ classItem.name }}
                        </option>
                    </select>
                </div>

                <div class="filter-item">
                    <label for="date-range">日期范围:</label>
                    <input
                        type="date"
                        id="start-date"
                        v-model="startDate"
                        class="input-field"
                    />
                    <span>至</span>
                    <input
                        type="date"
                        id="end-date"
                        v-model="endDate"
                        class="input-field"
                    />
                </div>

                <div class="filter-item">
                    <button class="btn btn-primary" @click="applyFilters">
                        应用筛选
                    </button>
                    <button class="btn btn-secondary" @click="resetFilters">
                        重置
                    </button>
                </div>
            </div>
        </div>

        <!-- 数据可视化区域 - 垂直排列 -->
        <div class="data-visualization">
            <!-- 班级整体进度图表 -->
            <div class="card chart-card">
                <h3>班级整体进度</h3>
                <div class="chart-container">
                    <canvas id="progress-chart"></canvas>
                </div>
            </div>

            <!-- 知识点知识点掌握情况图表 -->
            <div class="card chart-card">
                <h3>知识点掌握情况</h3>
                <div class="chart-wrapper">
                    <div class="chart-container-x-scroll">
                        <div
                            class="knowledge-chart-inner"
                            style="min-width: 900px; width: 100%; height: 380px"
                        >
                            <canvas id="knowledge-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 学生列表区域 -->
        <div class="card">
            <h3>学生详细数据</h3>
            <div class="table-wrapper">
                <table class="table">
                    <thead>
                        <tr>
                            <th>学生姓名</th>
                            <th>学号</th>
                            <th>擅长语言</th>
                            <th>完成进度</th>
                            <th>平均分数</th>
                            <th>完成项目</th>
                            <th>最近学习时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="student in students" :key="student.id">
                            <td>{{ student.name }}</td>
                            <td>{{ student.studentId }}</td>
                            <td>{{ student.favoriteLanguage }}</td>
                            <td>
                                <div class="progress-container">
                                    <div
                                        class="progress-bar"
                                        :style="{
                                            width: student.progress + '%',
                                        }"
                                    ></div>
                                </div>
                                <span class="progress-text"
                                    >{{ student.progress }}%</span
                                >
                            </td>
                            <td>{{ student.averageScore }}</td>
                            <td>{{ student.completedProjects }}个</td>
                            <td>{{ formatDate(student.lastStudyTime) }}</td>
                            <td>
                                <button
                                    class="btn btn-primary"
                                    @click="viewStudentDetail(student.id)"
                                >
                                    查看详情
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- 学生详情模态窗口 -->
    <div
        v-if="showStudentDetail"
        class="modal-overlay"
        @click="closeStudentDetail"
    >
        <div class="modal-container" @click.stop>
            <div class="modal-header">
                <h3>学生详情</h3>
                <button class="close-btn" @click="closeStudentDetail">×</button>
            </div>

            <div class="modal-body">
                <div class="student-header">
                    <div class="student-avatar">
                        <span>{{ currentStudent.name.charAt(0) }}</span>
                    </div>
                    <div class="student-basic-info">
                        <h4>{{ currentStudent.name }}</h4>
                        <p>学号: {{ currentStudent.studentId }}</p>
                        <p>班级: {{ getClassName(currentStudent.classId) }}</p>
                    </div>
                    <div class="student-stats">
                        <div class="stat-item">
                            <span class="stat-value"
                                >{{ currentStudent.progress }}%</span
                            >
                            <span class="stat-label">完成进度</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{
                                currentStudent.averageScore
                            }}</span>
                            <span class="stat-label">平均分数</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{
                                currentStudent.completedProjects
                            }}</span>
                            <span class="stat-label">完成项目</span>
                        </div>
                    </div>
                </div>

                <div class="student-details-grid">
                    <div class="detail-section">
                        <h4>基本信息</h4>
                        <ul class="info-list">
                            <li>
                                <span class="label">入学日期:</span>
                                {{ formatDate(currentStudent.enrollmentDate) }}
                            </li>
                            <li>
                                <span class="label">擅长语言:</span>
                                {{ currentStudent.favoriteLanguage }}
                            </li>
                            <li>
                                <span class="label">最近学习:</span>
                                {{ formatDate(currentStudent.lastStudyTime) }}
                            </li>
                            <li>
                                <span class="label">学习时长:</span>
                                {{ currentStudent.totalStudyHours }}小时
                            </li>
                            <li>
                                <span class="label">出勤率:</span>
                                {{ currentStudent.attendanceRate }}%
                            </li>
                        </ul>
                    </div>

                    <div class="detail-section">
                        <h4>技能掌握</h4>
                        <div class="skills-container">
                            <div
                                v-for="skill in currentStudent.skills"
                                :key="skill.name"
                                class="skill-item"
                            >
                                <div class="skill-header">
                                    <span class="skill-name">{{
                                        skill.name
                                    }}</span>
                                    <span class="skill-level"
                                        >{{ skill.level }}%</span
                                    >
                                </div>
                                <div class="progress-container">
                                    <div
                                        class="progress-bar"
                                        :style="{
                                            width: skill.level + '%',
                                            backgroundColor: skill.color,
                                        }"
                                    ></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="recent-projects">
                    <h4>最近完成的项目</h4>
                    <div class="projects-list">
                        <div
                            v-for="project in currentStudent.recentProjects"
                            :key="project.id"
                            class="project-card"
                        >
                            <div class="project-header">
                                <h5>{{ project.name }}</h5>
                                <span class="project-score"
                                    >{{ project.score }}分</span
                                >
                            </div>
                            <p class="project-description">
                                {{ project.description }}
                            </p>
                            <div class="project-meta">
                                <span
                                    >完成日期:
                                    {{
                                        formatDate(project.completionDate)
                                    }}</span
                                >
                                <span>耗时: {{ project.hoursSpent }}小时</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div
                    v-if="currentStudent.recommendations && currentStudent.recommendations.length"
                    class="recommendations-section"
                >
                    <h4>AAKT模型学习建议</h4>
                    <div
                        v-if="currentStudent.diagnosisInfo"
                        class="diagnosis-quality-panel"
                    >
                        <div class="diagnosis-badges">
                            <span class="diagnosis-badge" :class="getConfidenceBadgeClass(currentStudent.diagnosisInfo.confidence_level)">
                                置信等级：{{ getConfidenceLabel(currentStudent.diagnosisInfo.confidence_level) }}
                            </span>
                            <span class="diagnosis-badge" :class="currentStudent.diagnosisInfo.formal_diagnosis ? 'success' : 'warning'">
                                {{ currentStudent.diagnosisInfo.formal_diagnosis ? '正式诊断' : '参考诊断' }}
                            </span>
                            <span class="diagnosis-badge" :class="currentStudent.diagnosisInfo.used_model_inference ? 'info' : 'neutral'">
                                {{ currentStudent.diagnosisInfo.used_model_inference ? '模型推理' : '非模型直推' }}
                            </span>
                        </div>

                        <div v-if="currentStudent.diagnosisInfo.low_confidence" class="diagnosis-alert warning">
                            当前结果为低置信度诊断，建议继续积累练习数据后再评估。
                        </div>
                        <div v-if="currentStudent.diagnosisInfo.stability_warning" class="diagnosis-alert danger">
                            {{ currentStudent.diagnosisInfo.stability_warning }}
                        </div>
                    </div>
                    <ul class="recommendations-list">
                        <li
                            v-for="(rec, idx) in currentStudent.recommendations"
                            :key="idx"
                            class="recommendation-item"
                        >
                            {{ rec }}
                        </li>
                    </ul>
                    <div
                        v-if="currentStudent.diagnosisInfo"
                        class="diagnosis-meta"
                    >
                        <span>交互记录: {{ currentStudent.diagnosisInfo.total_interactions || 0 }}条</span>
                        <span>有效记录: {{ currentStudent.diagnosisInfo.valid_interactions || 0 }}条</span>
                        <span>诊断模式: {{ currentStudent.diagnosisInfo.model_status || '-' }}</span>
                        <span>最少样本: {{ currentStudent.diagnosisInfo.min_required_interactions || '-' }}条</span>
                    </div>
                </div>

                <div class="learning-trend">
                    <h4>学习趋势</h4>
                    <div class="chart-container-small">
                        <canvas id="student-trend-chart"></canvas>
                    </div>
                </div>
            </div>

            <div class="modal-footer">
                <button class="btn btn-secondary" @click="closeStudentDetail">
                    关闭
                </button>
                <button class="btn btn-primary">导出报告</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watchEffect } from "vue";
import { useRouter } from "vue-router";
import { Chart, registerables } from "chart.js";
import request from "../../../utils/request";

// 注册 Chart.js 所有组件
Chart.register(...registerables);

const router = useRouter();

// 图表实例
const progressChart = ref(null);
const knowledgeChart = ref(null);
const studentTrendChart = ref(null);

// 班级数据
const classes = ref([]);

// 筛选条件
const selectedClass = ref("");
const startDate = ref("");
const endDate = ref("");

// 学生数据 - 扩展了更多详细信息
const students = ref([]);

// 模态窗口状态
const showStudentDetail = ref(false);
const currentStudent = ref(null);

// 格式化日期
const formatDate = (dateString) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    });
};

// 获取班级名称
const getClassName = (classId) => {
    const cls = classes.value.find((c) => c.id === classId);
    return cls ? cls.name : "未知班级";
};

const getConfidenceLabel = (level) => {
    if (level === "high") return "高";
    if (level === "medium") return "中";
    if (level === "low") return "低";
    return "未知";
};

const getConfidenceBadgeClass = (level) => {
    if (level === "high") return "success";
    if (level === "medium") return "warning";
    if (level === "low") return "danger";
    return "neutral";
};

// 班级整体进度数据
const progressData = ref({ labels: [], datasets: [] });

// 知识点掌握情况数据
const knowledgeData = ref({ labels: [], datasets: [] });

const isLoggedIn = ref(
    !!(window.localStorage && window.localStorage.getItem("token"))
);

const handleAuthFailure = async (e) => {
    console.error("请求失败", e);
    // 只有真正的 401 未授权错误才跳转登录页
    // 超时、网络错误等不应清除登录状态
    const status = e?.originalError?.response?.status || e?.response?.status;
    if (status === 401) {
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
    } else {
        console.warn("非认证错误，保持登录状态:", e?.message || e);
    }
};

const fetchClasses = async () => {
    if (!isLoggedIn.value) return;
    const resp = await request.get("/classInfo/class-chart/class-list/");
    classes.value = Array.isArray(resp?.data) ? resp.data : [];
};

const fetchCharts = async () => {
    if (!isLoggedIn.value) return;
    // 两个图表请求独立处理，knowledge-chart 较慢，失败时不影响进度图表
    const [progressResult, knowledgeResult] = await Promise.allSettled([
        request.get("/classInfo/class-chart/progress-chart/"),
        request.get("/classInfo/class-chart/knowledge-chart/"),
    ]);
    if (progressResult.status === 'fulfilled') {
        progressData.value = progressResult.value?.data || { labels: [], datasets: [] };
    }
    if (knowledgeResult.status === 'fulfilled') {
        knowledgeData.value = knowledgeResult.value?.data || { labels: [], datasets: [] };
    } else {
        console.warn("知识点图表加载失败（可能超时），将在后台继续加载:", knowledgeResult.reason?.message);
    }
};

const fetchStudents = async () => {
    if (!isLoggedIn.value) return;
    if (!selectedClass.value) {
        students.value = [];
        return;
    }
    const resp = await request.get(
        `/classInfo/classes/${selectedClass.value}/students/`
    );
    const data = resp?.data;
    const list = data?.results?.students || data?.students || data?.results || [];
    students.value = Array.isArray(list)
        ? list.map((s) => ({
              id: s.id,
              name: s.name || "",
              studentId: s.studentId || s.student_id || "",
              favoriteLanguage: s.favoriteLanguage || "-",
              progress: typeof s.progress === "number" ? s.progress : 0,
              averageScore: s.averageScore || "-",
              completedProjects: s.completedProjects || 0,
              lastStudyTime: s.lastStudyTime || s.joinTime || "",
              weeklyProgress: Array.isArray(s.weeklyProgress)
                  ? s.weeklyProgress
                  : [0, 0, 0, 0, 0],
          }))
        : [];
};

// 创建班级整体进度图表
const createProgressChart = () => {
    // 先销毁已有实例
    if (progressChart.value) {
        progressChart.value.destroy();
    }

    // 使用watchEffect确保证元素存在
    const unwatch = watchEffect(() => {
        const ctx = document.getElementById("progress-chart");
        if (ctx) {
            // 确保DOM尺寸正确
            nextTick(() => {
                const container = ctx.parentElement;
                container.style.display = "block";
                container.style.width = "100%";
                container.style.minHeight = "350px";

                // 强制刷新尺寸
                ctx.width = container.offsetWidth;
                ctx.height = 350;

                const allData = [];
                progressData.value.datasets.forEach((dataset) => {
                    allData.push(...dataset.data);
                });
                const minValue = Math.min(...allData);
                const yAxisMin = Math.floor(minValue * 0.9);

                // 创建图表
                progressChart.value = new Chart(ctx, {
                    type: "line",
                    data: progressData.value,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: "top",
                                labels: {
                                    usePointStyle: true,
                                    boxWidth: 6,
                                    font: { size: 12 },
                                },
                            },
                            tooltip: {
                                mode: "index",
                                intersect: false,
                                callbacks: {
                                    label: (context) =>
                                        `${context.dataset.label}: ${context.parsed.y}%`,
                                },
                            },
                            title: {
                                display: true,
                                text: "班级编程学习进度趋势",
                                font: { size: 16, weight: "bold" },
                            },
                        },
                        scales: {
                            y: {
                                min: yAxisMin,
                                max: 100,
                                ticks: {
                                    callback: (value) => `${value}%`,
                                    stepSize: 5,
                                },
                                grid: {
                                    display: true,
                                    drawBorder: false,
                                    color: "rgba(0, 0, 0, 0.05)",
                                },
                                title: {
                                    display: true,
                                    text: "完成率",
                                    font: { size: 12 },
                                },
                            },
                            x: {
                                grid: {
                                    display: false,
                                },
                                ticks: {
                                    font: { size: 11 },
                                },
                            },
                        },
                        interaction: {
                            intersect: false,
                            mode: "index",
                        },
                        animation: {
                            duration: 1500,
                            easing: "easeOutQuart",
                        },
                        elements: {
                            line: {
                                borderWidth: 3,
                            },
                        },
                    },
                });
                unwatch(); // 完成后停止监听
            });
        }
    });
};

// 创建知识点掌握情况图表
const createKnowledgeChart = () => {
    // 先销毁已有实例
    if (knowledgeChart.value) {
        knowledgeChart.value.destroy();
    }

    // 使用watchEffect确保元素存在
    const unwatch = watchEffect(() => {
        const ctx = document.getElementById("knowledge-chart");
        if (ctx) {
            // 确保DOM尺寸正确
            nextTick(() => {
                const container = ctx.parentElement;
                container.style.minHeight = "350px";
                ctx.width = container.offsetWidth;
                ctx.height = 350;

                // 创建图表
                knowledgeChart.value = new Chart(ctx, {
                    type: "bar",
                    data: knowledgeData.value,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                ticks: {
                                    callback: (value) => `${value}%`,
                                },
                            },
                            x: {
                                grid: {
                                    display: false,
                                },
                            },
                        },
                        plugins: {
                            title: {
                                display: true,
                                text: "编程知识点掌握情况",
                            },
                        },
                    },
                });
                unwatch(); // 完成后停止监听
            });
        }
    });
};

// 创建学生学习趋势图表
const createStudentTrendChart = () => {
    // 先销毁已有实例
    if (studentTrendChart.value) {
        studentTrendChart.value.destroy();
    }

    // 使用watchEffect确保元素存在
    const unwatch = watchEffect(() => {
        const ctx = document.getElementById("student-trend-chart");
        if (ctx && currentStudent.value) {
            // 确保DOM尺寸正确
            nextTick(() => {
                const container = ctx.parentElement;
                container.style.minHeight = "250px";
                ctx.width = container.offsetWidth;
                ctx.height = 250;

                // 创建图表
                studentTrendChart.value = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: ["5周前", "4周前", "3周前", "2周前", "上周"],
                        datasets: [
                            {
                                label: "学习进度",
                                data: currentStudent.value.weeklyProgress,
                                borderColor: "#3498db",
                                backgroundColor: "rgba(52, 152, 219, 0.1)",
                                tension: 0.4,
                                fill: true,
                                pointRadius: 4,
                                pointBackgroundColor: "#3498db",
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
                                    callback: (value) => `${value}%`,
                                },
                            },
                            x: {
                                grid: {
                                    display: false,
                                },
                            },
                        },
                        plugins: {
                            legend: {
                                display: false,
                            },
                        },
                    },
                });
                unwatch(); // 完成后停止监听
            });
        }
    });
};

// 应用筛选
const applyFilters = async () => {
    console.log("应用筛选:", { selectedClass, startDate, endDate });
    try {
        await fetchStudents();
        await fetchCharts();
        createProgressChart();
        createKnowledgeChart();
    } catch (e) {
        await handleAuthFailure(e);
    }
};

// 重置筛选
const resetFilters = () => {
    selectedClass.value = "";
    startDate.value = "";
    endDate.value = "";
};

// 获取学生知识点掌握度（调用AAKT模型诊断）
const fetchStudentKnowledgeMastery = async (studentId) => {
    try {
        const resp = await request.get(
            `/teacher/student-knowledge-mastery/?student_id=${studentId}`
        );
        const data = resp?.data;
        if (data && data.status === "success") {
            return {
                skills: Array.isArray(data.skills) ? data.skills : [],
                recommendations: Array.isArray(data.recommendations)
                    ? data.recommendations
                    : [],
                weakestTags: Array.isArray(data.weakest_tags)
                    ? data.weakest_tags
                    : [],
                diagnosisInfo: data.diagnosis_info || {},
            };
        }
    } catch (e) {
        console.error("获取学生知识点掌握度失败:", e);
    }
    return { skills: [], recommendations: [], weakestTags: [], diagnosisInfo: {} };
};

// 查看学生详情
const viewStudentDetail = async (studentId) => {
    const student = students.value.find((s) => s.id === studentId);
    if (student) {
        currentStudent.value = { ...student, skills: [], recommendations: [] };
        showStudentDetail.value = true;

        // 异步获取AAKT模型诊断的知识点掌握度
        const mastery = await fetchStudentKnowledgeMastery(studentId);
        currentStudent.value = {
            ...currentStudent.value,
            skills: mastery.skills,
            recommendations: mastery.recommendations,
            weakestTags: mastery.weakestTags,
            diagnosisInfo: mastery.diagnosisInfo,
        };

        // 确保DOM更新后创建图表
        nextTick(() => {
            createStudentTrendChart();
        });
    }
};

// 关闭学生详情
const closeStudentDetail = () => {
    showStudentDetail.value = false;
    // 销毁学生趋势图表实例
    if (studentTrendChart.value) {
        studentTrendChart.value.destroy();
        studentTrendChart.value = null;
    }
};

// 处理窗口大小变化
const handleResize = () => {
    if (progressChart.value) progressChart.value.resize();
    if (knowledgeChart.value) knowledgeChart.value.resize();
    if (studentTrendChart.value) studentTrendChart.value.resize();
};

// 组件挂载时初始化
onMounted(async () => {
    const timer = setTimeout(async () => {
        try {
            await fetchClasses();
            await fetchCharts();
            await nextTick();
            createProgressChart();
            createKnowledgeChart();
            window.addEventListener("resize", handleResize);
        } catch (e) {
            await handleAuthFailure(e);
        }
    }, 100);

    return () => clearTimeout(timer);
});

// 组件卸载时清理
onUnmounted(() => {
    if (progressChart.value) progressChart.value.destroy();
    if (knowledgeChart.value) knowledgeChart.value.destroy();
    if (studentTrendChart.value) studentTrendChart.value.destroy();
    window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
/* 页面头部 */
.page-header {
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e0e0e0;
}

.page-header h2 {
    margin: 0;
    font-size: 24px;
    color: #1e3a8a;
    font-weight: 600;
}

.page-header p {
    margin: 8px 0 0 0;
    color: #666;
    font-size: 14px;
}
/* 整体容器样式 */
.class-tracking-container {
    width: 100%;
    padding: 0;
    margin: 0;
}

/* 卡片样式 - 应用新设计 */
.card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 10px;
    padding: 22px;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(240, 249, 255, 0.8);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
    margin-bottom: 25px;
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

/* 图表卡片额外样式 */
.chart-card {
    width: 100%;
}

/* 筛选器容器 */
.filters-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: flex-end;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .filters-container {
    transform: translateX(3px);
    opacity: 1;
}

.filter-item {
    display: flex;
    align-items: center;
    gap: 10px;
}

.filter-item label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
}

.filter-item span {
    color: #666;
}

.input-field {
    padding: 12px 15px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.3s ease;
}

.input-field:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

/* 按钮样式 */
.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.btn-primary {
    background: linear-gradient(135deg, #64b5f6, #2196f3);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    transition: all 0.3s ease;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(33, 150, 243, 0.4);
    background: linear-gradient(135deg, #81c7f5, #1976d2);
}

.btn-secondary {
    background: linear-gradient(135deg, #b8c5c6, #7f8c8d);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(127, 140, 141, 0.4);
    background: linear-gradient(135deg, #d0dbdc, #6c7a7b);
}

/* 数据可视化区域 */
.data-visualization {
    display: flex;
    flex-direction: column;
    gap: 25px;
    margin: 25px 0;
}

/* 图表容器 */
.chart-container {
    min-height: 320px;
    height: 380px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    transition: background-color 0.3s ease;
    position: relative;
    width: 100%;
}

/* 知识点图表专用包装器 */
.chart-wrapper {
    width: 100%;
    height: 380px;
    position: relative;
}

/* 横向滚动图表容器 */
.chart-container-x-scroll {
    width: 100%;
    height: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: thin;
    scrollbar-color: #888 #f1f1f1;
    display: flex;
    align-items: center;
}

/* 知识点图表内部容器 */
.knowledge-chart-inner {
    padding: 20px 0;
    position: relative;
}

/* 滚动条样式 */
.chart-container-x-scroll::-webkit-scrollbar {
    height: 8px;
}

.chart-container-x-scroll::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.chart-container-x-scroll::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

.chart-container-x-scroll::-webkit-scrollbar-thumb:hover {
    background: #555;
}

.chart-container:hover {
    background-color: #e9ecef;
}

/* 进度条和进度文本 */
.progress-container {
    height: 8px;
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #3498db, #2ecc71);
    transition: width 0.3s ease;
    border-radius: 4px;
}

.progress-text {
    font-size: 14px;
    color: #333;
    margin-top: 8px;
    display: block;
    font-weight: 500;
}

/* 表格样式 */
.table-wrapper {
    overflow-x: auto;
}

.table {
    width: 100%;
    border-collapse: collapse;
}

.table th,
.table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #f0f0f0;
}

.table th {
    background-color: #f8f9fa;
    color: #333;
    font-weight: 600;
    font-size: 14px;
}

.table tr:hover {
    background-color: #f8f9fa;
}

.table td {
    color: #666;
    font-size: 14px;
}

/* 表格和进度条的动画效果 */
.table,
.progress-item,
.stat-item {
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .table,
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

/* 响应式设计 */
@media (max-width: 1200px) {
    .data-visualization {
        gap: 20px;
    }

    .filters-container {
        gap: 15px;
        justify-content: center;
    }

    .chart-container {
        min-height: 280px;
    }
}

@media (max-width: 768px) {
    .card {
        padding: 20px;
    }

    .filters-container {
        flex-direction: column;
        align-items: stretch;
    }

    .filter-item {
        flex-direction: column;
        align-items: stretch;
    }

    .filter-item label {
        margin-bottom: 8px;
    }

    .filter-item span {
        display: none;
    }

    .filter-item input[type="date"] {
        margin-bottom: 8px;
    }

    .btn {
        width: 100%;
        padding: 12px 15px;
        margin-bottom: 8px;
    }

    .chart-container {
        min-height: 250px;
        padding: 15px;
    }

    .table th,
    .table td {
        padding: 10px;
        font-size: 13px;
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

/* 模态窗口样式 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(3px);
    animation: fadeIn 0.3s ease;
}

.modal-container {
    background-color: white;
    border-radius: 10px;
    width: 90%;
    max-width: 1000px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    animation: slideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.modal-header {
    padding: 20px 25px;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    font-size: 20px;
    color: #1e3a8a;
    font-weight: 600;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
    transition: color 0.2s ease;
    padding: 0 10px;
}

.close-btn:hover {
    color: #e74c3c;
}

.modal-body {
    padding: 25px;
}

.modal-footer {
    padding: 15px 25px;
    border-top: 1px solid #f0f0f0;
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    background-color: #f9fafb;
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}

/* 学生详情样式 */
.student-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #f0f0f0;
}

.student-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #64b5f6, #2196f3);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2);
}

.student-basic-info h4 {
    margin: 0 0 10px 0;
    font-size: 22px;
    color: #1e3a8a;
}

.student-basic-info p {
    margin: 5px 0;
    color: #666;
}

.student-stats {
    display: flex;
    gap: 20px;
    margin-left: auto;
}

.stat-item {
    text-align: center;
    padding: 15px;
    background-color: #f8fafc;
    border-radius: 8px;
    min-width: 80px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-value {
    display: block;
    font-size: 20px;
    font-weight: bold;
    color: #2563eb;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 13px;
    color: #666;
}

.student-details-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-bottom: 30px;
}

.detail-section h4 {
    margin: 0 0 15px 0;
    font-size: 16px;
    color: #1e3a8a;
    padding-bottom: 8px;
    border-bottom: 1px solid #f0f0f0;
}

.info-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.info-list li {
    padding: 10px 0;
    border-bottom: 1px solid #f8fafc;
    display: flex;
}

.info-list li:last-child {
    border-bottom: none;
}

.label {
    font-weight: 500;
    color: #4b5563;
    min-width: 100px;
}

.skills-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.skill-item {
    background-color: #f8fafc;
    padding: 12px;
    border-radius: 6px;
}

.skill-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 14px;
}

.skill-name {
    font-weight: 500;
}

.skill-level {
    color: #2563eb;
    font-weight: 500;
}

/* 最近完成的项目区域样式 */
.recent-projects {
    margin-bottom: 40px;
    padding: 20px;
    background-color: #f8fafc;
    border-radius: 10px;
    position: relative;
}

.recent-projects h4 {
    margin: 0 0 20px 0;
    font-size: 18px;
    color: #1e3a8a;
    font-weight: 600;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

/* 项目列表容器 */
.projects-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 25px;
}

/* 项目卡片样式 */
.project-card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #f0f0f0;
    transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    position: relative;
    overflow: hidden;
    margin-bottom: 15px; /* 增加底部间距防止动画遮挡 */
}

/* 项目卡片悬停效果 */
.project-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 20px rgba(59, 130, 246, 0.12);
    border-color: rgba(59, 130, 246, 0.2);
}

/* 项目卡片顶部装饰 */
.project-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.project-card:hover::before {
    transform: scaleX(1);
}

/* 项目头部 */
.project-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.project-header h5 {
    margin: 0;
    font-size: 16px;
    color: #1e3a8a;
    transition: color 0.3s ease;
}

.project-card:hover .project-header h5 {
    color: #2563eb;
}

/* 项目分数 */
.project-score {
    background-color: rgba(37, 99, 235, 0.1);
    color: #2563eb;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.project-card:hover .project-score {
    background-color: rgba(37, 99, 235, 0.2);
    transform: scale(1.05);
}

/* 项目描述 */
.project-description {
    margin: 0 0 18px 0;
    color: #64748b;
    font-size: 14px;
    line-height: 1.6;
    position: relative;
    z-index: 1; /* 确保文字在最上层 */
}

/* 项目元数据 */
.project-meta {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: #94a3b8;
    padding-top: 12px;
    border-top: 1px dashed #f0f0f0;
    position: relative;
    z-index: 1; /* 确保文字在最上层 */
}

/* 响应式调整 */
@media (max-width: 768px) {
    .projects-list {
        grid-template-columns: 1fr;
        gap: 20px;
    }

    .project-card {
        padding: 15px;
        margin-bottom: 10px;
    }

    .project-meta {
        flex-direction: column;
        gap: 5px;
    }
}

.learning-trend {
    margin-bottom: 15px;
}

.chart-container-small {
    min-height: 200px;
    height: 250px;
    background-color: #f8fafc;
    border-radius: 8px;
    padding: 15px;
}

/* 模态窗口动画 */
@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes slideIn {
    from {
        transform: translateY(30px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* 响应式模态窗口 */
@media (max-width: 768px) {
    .student-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .student-stats {
        margin-left: 0;
        width: 100%;
        justify-content: space-between;
    }

    .student-details-grid {
        grid-template-columns: 1fr;
    }

    .projects-list {
        grid-template-columns: 1fr;
    }

    .modal-container {
        width: 95%;
        max-height: 85vh;
    }

    .modal-body {
        padding: 15px;
    }

    .modal-header {
        padding: 15px;
    }

    .modal-footer {
        padding: 15px;
        flex-direction: column;
    }

    .modal-footer .btn {
        width: 100%;
        margin-bottom: 10px;
    }

    .modal-footer .btn:last-child {
        margin-bottom: 0;
    }
}

/* AAKT模型学习建议区域 */
.recommendations-section {
    margin-top: 20px;
    padding: 18px;
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: 10px;
    border-left: 4px solid #3b82f6;
}

.recommendations-section h4 {
    margin: 0 0 12px 0;
    color: #1e3a8a;
    font-size: 16px;
    font-weight: 600;
}

.recommendations-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.recommendation-item {
    padding: 8px 12px;
    margin-bottom: 8px;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 6px;
    font-size: 13px;
    color: #334155;
    line-height: 1.5;
    position: relative;
    padding-left: 24px;
}

.recommendation-item::before {
    content: "\2714";
    position: absolute;
    left: 8px;
    color: #3b82f6;
    font-size: 12px;
}

.recommendation-item:last-child {
    margin-bottom: 0;
}

.diagnosis-meta {
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px dashed rgba(59, 130, 246, 0.3);
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 12px;
    color: #64748b;
}

.diagnosis-quality-panel {
    margin-bottom: 14px;
}

.diagnosis-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 10px;
}

.diagnosis-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

.diagnosis-badge.success {
    background: #dcfce7;
    color: #166534;
}

.diagnosis-badge.warning {
    background: #fef3c7;
    color: #92400e;
}

.diagnosis-badge.danger {
    background: #fee2e2;
    color: #991b1b;
}

.diagnosis-badge.info {
    background: #dbeafe;
    color: #1d4ed8;
}

.diagnosis-badge.neutral {
    background: #e5e7eb;
    color: #374151;
}

.diagnosis-alert {
    padding: 10px 12px;
    border-radius: 8px;
    margin-bottom: 10px;
    font-size: 13px;
    line-height: 1.5;
}

.diagnosis-alert.warning {
    background: #fff7ed;
    color: #9a3412;
}

.diagnosis-alert.danger {
    background: #fef2f2;
    color: #b91c1c;
}
</style>
