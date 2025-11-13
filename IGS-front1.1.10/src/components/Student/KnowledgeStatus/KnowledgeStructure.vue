<template>
    <div class="knowledge-page">
        <!-- 加载动画 -->
        <div v-if="isLoading && !errorMsg" class="loading-container">
            <div class="loading-spinner"></div>
            <p class="loading-text">正在加载知识结构数据...</p>
            <div class="loading-progress">
                <div
                    class="progress-bar"
                    :style="{ width: loadingProgress + '%' }"
                ></div>
            </div>
        </div>

        <!-- 加载失败界面 -->
        <div v-if="errorMsg" class="error-container">
            <div class="error-icon">⚠️</div>
            <h2 class="error-title">加载失败</h2>
            <p class="error-message">{{ errorMsg }}</p>
            <button class="retry-btn" @click="retryLoad">重试</button>
            <button class="home-btn" @click="goToHome">返回首页</button>
        </div>

        <!-- 主内容区 - 仅在加载完成且无错误时显示 -->
        <div v-else class="main-content">
            <!-- 使用StudentHeader组件 -->
            <StudentHeader title="知识结构可视化" />

            <div class="dashboard">
                <!-- 总体掌握情况卡片 -->
                <div class="card">
                    <h3>总体掌握情况</h3>
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>知识点覆盖率</span>
                            <span>{{ coverageRate }}%</span>
                        </div>
                        <div class="progress-container">
                            <div
                                class="progress"
                                :style="{ width: coverageRate + '%' }"
                                :class="getProgressColorClass(coverageRate)"
                            ></div>
                        </div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>已掌握知识点</span>
                            <span>{{ masteredCount }}/{{ totalCount }}</span>
                        </div>
                        <div class="progress-container">
                            <div
                                class="progress"
                                :style="{
                                    width:
                                        (masteredCount / totalCount) * 100 +
                                        '%',
                                }"
                                :class="
                                    getProgressColorClass(
                                        (masteredCount / totalCount) * 100
                                    )
                                "
                            ></div>
                        </div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>平均掌握程度</span>
                            <span>{{ avgMastery }}%</span>
                        </div>
                        <div class="progress-container">
                            <div
                                class="progress"
                                :style="{ width: avgMastery + '%' }"
                                :class="getProgressColorClass(avgMastery)"
                            ></div>
                        </div>
                    </div>
                </div>

                <!-- 知识点分类统计卡片 -->
                <div class="card">
                    <h3>知识点分类统计</h3>
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-value">{{
                                categoryStats.core
                            }}</span>
                            <span class="stat-label">核心知识点</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{
                                categoryStats.important
                            }}</span>
                            <span class="stat-label">重要知识点</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{
                                categoryStats.general
                            }}</span>
                            <span class="stat-label">一般知识点</span>
                        </div>
                    </div>
                </div>

                <!-- 知识点掌握度区域（增加筛选功能） -->
                <div class="content-section">
                    <div class="section-header">
                        <h3>知识点掌握度</h3>
                        <!-- 筛选控件 -->
                        <div class="filter-control">
                            <label for="mastery-filter" class="filter-label"
                                >按掌握情况筛选：</label
                            >
                            <select
                                id="mastery-filter"
                                v-model="selectedLevel"
                                @change="updateMasteryChart"
                                class="mastery-select"
                            >
                                <option value="all">全部</option>
                                <option value="unmastered">
                                    未掌握（<30%）
                                </option>
                                <option value="basic">了解（30%-50%）</option>
                                <option value="mastered">
                                    掌握（50%-70%）
                                </option>
                                <option value="proficient">
                                    熟练（70%-90%）
                                </option>
                                <option value="expert">精通（≥90%）</option>
                            </select>
                        </div>
                    </div>
                    <div class="chart-table-wrapper">
                        <div class="chart-container">
                            <canvas id="masteryChart"></canvas>
                        </div>
                        <div class="chart-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>编号</th>
                                        <th>知识点</th>
                                        <th>掌握度</th>
                                        <th>等级</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr
                                        v-for="knowledge in filteredKnowledgeList"
                                        :key="knowledge.id"
                                    >
                                        <td>{{ knowledge.id }}</td>
                                        <td>{{ knowledge.name }}</td>
                                        <td>{{ knowledge.mastery }}%</td>
                                        <td>
                                            <span
                                                :class="
                                                    getMasteryColorClass(
                                                        knowledge.mastery,
                                                        'level'
                                                    )
                                                "
                                            >
                                                {{
                                                    getMasteryLevelText(
                                                        knowledge.mastery
                                                    )
                                                }}
                                            </span>
                                        </td>
                                    </tr>
                                    <tr
                                        v-if="
                                            filteredKnowledgeList.length === 0
                                        "
                                    >
                                        <td colspan="4" class="no-data">
                                            没有符合条件的知识点
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- 知识点分类掌握度区域 -->
                <div class="content-section">
                    <h3>知识点分类掌握度</h3>
                    <div class="chart-table-wrapper">
                        <div class="chart-container">
                            <canvas id="categoryMasteryChart"></canvas>
                        </div>
                        <div class="chart-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>分类</th>
                                        <th>知识点数量</th>
                                        <th>平均掌握度</th>
                                        <th>最高掌握度</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>核心知识点</td>
                                        <td>{{ categoryStats.core }}</td>
                                        <td>
                                            {{
                                                categoryAvgMastery.core.toFixed(
                                                    1
                                                )
                                            }}%
                                        </td>
                                        <td>{{ categoryMaxMastery.core }}%</td>
                                    </tr>
                                    <tr>
                                        <td>重要知识点</td>
                                        <td>{{ categoryStats.important }}</td>
                                        <td>
                                            {{
                                                categoryAvgMastery.important.toFixed(
                                                    1
                                                )
                                            }}%
                                        </td>
                                        <td>
                                            {{ categoryMaxMastery.important }}%
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>一般知识点</td>
                                        <td>{{ categoryStats.general }}</td>
                                        <td>
                                            {{
                                                categoryAvgMastery.general.toFixed(
                                                    1
                                                )
                                            }}%
                                        </td>
                                        <td>
                                            {{ categoryMaxMastery.general }}%
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- 知识点详情区域 -->
                <div class="content-section">
                    <h3>知识点详情</h3>
                    <div class="knowledge-container">
                        <div
                            class="knowledge-card"
                            v-for="knowledge in knowledgeList"
                            :key="knowledge.id"
                            @click="showKnowledgeDetail(knowledge)"
                        >
                            <div class="knowledge-icon">
                                {{ getCategoryIcon(knowledge.category) }}
                            </div>
                            <div class="knowledge-info">
                                <h4>{{ knowledge.name }}</h4>
                                <div class="knowledge-progress-container">
                                    <div
                                        class="knowledge-progress"
                                        :style="{
                                            width: knowledge.mastery + '%',
                                        }"
                                        :class="
                                            getMasteryColorClass(
                                                knowledge.mastery
                                            )
                                        "
                                    ></div>
                                </div>
                                <div class="knowledge-meta">
                                    <span class="knowledge-level">{{
                                        getMasteryLevelText(knowledge.mastery)
                                    }}</span>
                                    <span class="knowledge-category">{{
                                        knowledge.categoryText
                                    }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 单个知识点详情弹窗 -->
            <div class="modal" v-if="selectedKnowledge">
                <div class="modal-content">
                    <span class="close" @click="selectedKnowledge = null"
                        >&times;</span
                    >
                    <h3>{{ selectedKnowledge.name }}</h3>
                    <p class="knowledge-description">
                        {{ selectedKnowledge.description }}
                    </p>

                    <div class="knowledge-detail-chart">
                        <canvas id="knowledgeDetailChart"></canvas>
                    </div>

                    <div class="knowledge-stats">
                        <div class="stat-item">
                            <span class="stat-value"
                                >{{ selectedKnowledge.mastery }}%</span
                            >
                            <span class="stat-label">掌握程度</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{
                                selectedKnowledge.practiceCount
                            }}</span>
                            <span class="stat-label">练习次数</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{
                                selectedKnowledge.lastPracticed
                            }}</span>
                            <span class="stat-label">最后练习</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <a href="/student/index" class="back-to-home">
            <span class="icon">🏠</span>
            <span>首页</span>
        </a>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from "vue";
import Chart from "chart.js/auto";
import { useRouter } from "vue-router";
import api from "../../../api/index";
import StudentHeader from "../StudentHeader.vue";

// 路由实例
const router = useRouter();

// 用户信息由StudentHeader组件管理，此处不再需要单独定义

// 总体数据
const coverageRate = ref(0);
const masteredCount = ref(0);
const totalCount = ref(0);
const avgMastery = ref(0);

// 知识点列表
const knowledgeList = ref([]);

// 筛选相关变量
const selectedLevel = ref("all");

// 响应式变量
const structureRecords = ref(null);
const isLoading = ref(true);
const errorMsg = ref("");
const userInfoLoading = ref(true); // 用户信息加载状态
const loadingProgress = ref(0); // 加载进度

// 获取用户信息的函数已在StudentHeader组件中实现，此处不再需要

// 获取知识点结构数据
const fetchStructureData = () => {
    return api
        .getStructure()
        .then((res) => {
            console.log("获取的知识点结构数据为：", res.data);
            const data = res.data;

            // 更新总体数据
            coverageRate.value = data.coverageRate || 0;
            masteredCount.value = data.masteredCount || 0;
            totalCount.value = data.totalCount || 0;
            avgMastery.value = data.avgMastery || 0;

            // 更新知识点列表
            knowledgeList.value = Array.isArray(data.knowledgeList)
                ? data.knowledgeList
                : [];

            structureRecords.value = data;
            updateLoadingProgress(100); // 加载完成
        })
        .catch((err) => {
            console.error("获取知识点数据失败:", err);
            // 设置错误信息
            errorMsg.value = "网络请求错误，请稍后重试";
            isLoading.value = false;
        });
};

// 更新加载进度
const updateLoadingProgress = (value) => {
    // 使用动画效果更新进度
    const duration = 500; // 动画持续时间（毫秒）
    const start = loadingProgress.value;
    const increment = value - start;
    const step = increment / (duration / 16); // 每16ms更新一次

    const timer = setInterval(() => {
        loadingProgress.value += step;
        if (
            (step > 0 && loadingProgress.value >= value) ||
            (step < 0 && loadingProgress.value <= value)
        ) {
            loadingProgress.value = value;
            clearInterval(timer);
        }
    }, 16);
};

// 初始加载数据
const loadData = () => {
    // 重置状态
    isLoading.value = true;
    errorMsg.value = "";
    loadingProgress.value = 0;

    // 加载知识点数据
    fetchStructureData()
        .then(() => {
            isLoading.value = false;
            // 渲染图表
            nextTick(() => {
                updateMasteryChart();
                renderCategoryMasteryChart();
            });
        })
        .catch(() => {
            isLoading.value = false;
            if (!errorMsg.value) {
                errorMsg.value = "数据加载失败，请重试";
            }
        });
};

// 重试加载
const retryLoad = () => {
    loadData();
};

// 生命周期钩子
onMounted(() => {
    loadData();
});

// 按ID排序的知识点列表
const sortedKnowledgeList = computed(() => {
    return [...knowledgeList.value].sort((a, b) => a.id - b.id);
});

// 按筛选条件过滤知识点
const filteredKnowledgeList = computed(() => {
    if (selectedLevel.value === "all") {
        return sortedKnowledgeList.value;
    }
    return sortedKnowledgeList.value.filter((knowledge) => {
        const mastery = knowledge.mastery;
        switch (selectedLevel.value) {
            case "unmastered":
                return mastery < 30;
            case "basic":
                return mastery >= 30 && mastery < 50;
            case "mastered":
                return mastery >= 50 && mastery < 70;
            case "proficient":
                return mastery >= 70 && mastery < 90;
            case "expert":
                return mastery >= 90;
            default:
                return true;
        }
    });
});

// 分类统计
const categoryStats = computed(() => ({
    core: knowledgeList.value.filter((k) => k.category === "core").length,
    important: knowledgeList.value.filter((k) => k.category === "important")
        .length,
    general: knowledgeList.value.filter((k) => k.category === "general").length,
}));

// 计算分类平均掌握度
const categoryAvgMastery = computed(() => {
    const getAvg = (category) => {
        const items = knowledgeList.value.filter(
            (k) => k.category === category
        );
        return items.length
            ? items.reduce((sum, k) => sum + k.mastery, 0) / items.length
            : 0;
    };
    return {
        core: getAvg("core"),
        important: getAvg("important"),
        general: getAvg("general"),
    };
});

// 计算分类最高掌握度
const categoryMaxMastery = computed(() => {
    const getMax = (category) => {
        const items = knowledgeList.value.filter(
            (k) => k.category === category
        );
        return items.length ? Math.max(...items.map((k) => k.mastery)) : 0;
    };
    return {
        core: getMax("core"),
        important: getMax("important"),
        general: getMax("general"),
    };
});

// 选中的知识点
const selectedKnowledge = ref(null);

// 图表实例
let masteryChartInstance = null;
let categoryMasteryChartInstance = null;
let knowledgeDetailChartInstance = null;

// 根据掌握程度获取进度条颜色类
const getProgressColorClass = (progress) => {
    if (progress < 50) return "progress-low";
    if (progress < 75) return "progress-medium";
    return "progress-high";
};

// 根据掌握程度获取样式类
const getMasteryColorClass = (mastery, type = "progress") => {
    if (type === "level") {
        if (mastery < 30) return "level-unmastered";
        if (mastery < 50) return "level-basic";
        if (mastery < 70) return "level-mastered";
        if (mastery < 90) return "level-proficient";
        return "level-expert";
    }
    return getProgressColorClass(mastery);
};

// 根据掌握程度获取文本描述
const getMasteryLevelText = (level) => {
    if (level < 30) return "未掌握";
    if (level < 50) return "了解";
    if (level < 70) return "掌握";
    if (level < 90) return "熟练";
    return "精通";
};

// 根据知识点分类获取图标
const getCategoryIcon = (category) => {
    const icons = { core: "⭐", important: "🔑", general: "📘" };
    return icons[category] || "📚";
};

// 显示知识点详情弹窗
const showKnowledgeDetail = (knowledge) => {
    selectedKnowledge.value = knowledge;
    nextTick(() => {
        renderKnowledgeDetailChart(knowledge);
    });
};

// 渲染知识点详情图表
const renderKnowledgeDetailChart = (knowledge) => {
    const ctx = document.getElementById("knowledgeDetailChart");
    if (!ctx) return;
    if (knowledgeDetailChartInstance) {
        knowledgeDetailChartInstance.destroy();
    }
    const historyData = [30, 45, 60, 55, 70, knowledge.mastery];
    const historyLabels = ["1月", "2月", "3月", "4月", "5月", "当前"];
    knowledgeDetailChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: historyLabels,
            datasets: [
                {
                    label: "掌握程度 (%)",
                    data: historyData,
                    borderColor: "#3498db",
                    backgroundColor: "rgba(52, 152, 219, 0.1)",
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                },
            ],
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } },
        },
    });
};

// 在updateMasteryChart函数中替换backgroundColors部分
const updateMasteryChart = () => {
    const masteryCtx = document.getElementById("masteryChart");
    if (!masteryCtx) return;

    if (masteryChartInstance) {
        masteryChartInstance.destroy();
    }

    const labels = filteredKnowledgeList.value.map((k) => `K${k.id}`);
    const data = filteredKnowledgeList.value.map((k) => k.mastery);

    // 创建渐变颜色数组
    const backgroundColors = filteredKnowledgeList.value.map((k) => {
        // 创建渐变上下文
        const gradient = masteryCtx
            .getContext("2d")
            .createLinearGradient(0, 0, 0, 400);

        // 渐变色设置
        if (k.mastery < 50) {
            gradient.addColorStop(0, "rgba(249, 115, 22, 0.55)"); // 橙红色
            gradient.addColorStop(1, "rgba(189, 54, 54, 1)"); // 深暗红色
        } else if (k.mastery < 75) {
            gradient.addColorStop(0, "rgba(250, 204, 21, 0.55)"); // 亮黄色
            gradient.addColorStop(1, "rgba(234, 179, 8, 1)"); // 深黄色
        } else {
            gradient.addColorStop(0, "rgba(16, 185, 129, 0.55)"); // 亮绿色
            gradient.addColorStop(1, "rgba(22, 163, 74, 1)"); // 深绿色
        }

        return gradient;
    });

    masteryChartInstance = new Chart(masteryCtx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "掌握程度 (%)",
                    data: data,
                    backgroundColor: backgroundColors,
                    borderWidth: 1,
                    borderColor: filteredKnowledgeList.value.map((k) => {
                        if (k.mastery < 50) return "rgba(189, 54, 54, 0.8)";
                        if (k.mastery < 75) return "rgba(234, 179, 8, 0.8)";
                        return "rgba(22, 163, 74, 0.8)";
                    }),
                    // 添加圆角配置
                    borderRadius: {
                        topLeft: 8, // 左上角圆角
                        topRight: 8, // 右上角圆角
                        bottomLeft: 2, // 左下角小圆角
                        bottomRight: 2, // 右下角小圆角
                    },
                    shadowColor: "rgba(0, 0, 0, 0.2)",
                    shadowBlur: 4,
                    shadowOffsetX: 0,
                    shadowOffsetY: 2,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "掌握度 (%)" },
                },
                x: { title: { display: true, text: "知识点编号" } },
            },
        },
    });
};

// 渲染分类掌握度图表
// 渲染分类掌握度图表（更新后）
const renderCategoryMasteryChart = () => {
    const categoryCtx = document.getElementById("categoryMasteryChart");
    if (!categoryCtx) return;

    if (categoryMasteryChartInstance) {
        categoryMasteryChartInstance.destroy();
    }

    // 准备数据
    const labels = ["核心知识点", "重要知识点", "一般知识点"];
    const data = [
        categoryStats.value.core,
        categoryStats.value.important,
        categoryStats.value.general,
    ];

    // 创建渐变色数组（与知识点图表风格一致）
    const backgroundColors = data.map((_, index) => {
        const gradient = categoryCtx
            .getContext("2d")
            .createLinearGradient(0, 0, 0, 400);

        // 为不同分类定义对应的渐变色
        if (index === 0) {
            // 核心知识点
            gradient.addColorStop(0, "rgba(59, 130, 246, 0.55)"); // 亮蓝色
            gradient.addColorStop(1, "rgba(30, 64, 175, 1)"); // 深蓝色
        } else if (index === 1) {
            // 重要知识点
            gradient.addColorStop(0, "rgba(139, 92, 246, 0.55)"); // 亮紫色
            gradient.addColorStop(1, "rgba(99, 102, 241, 1)"); // 深紫色
        } else {
            // 一般知识点
            gradient.addColorStop(0, "rgba(16, 185, 129, 0.55)"); // 亮绿色
            gradient.addColorStop(1, "rgba(22, 163, 74, 1)"); // 深绿色
        }

        return gradient;
    });

    // 边框颜色（与渐变深色部分匹配）
    const borderColors = [
        "rgba(30, 64, 175, 0.8)",
        "rgba(99, 102, 241, 0.8)",
        "rgba(22, 163, 74, 0.8)",
    ];

    categoryMasteryChartInstance = new Chart(categoryCtx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "知识点数量",
                    data: data,
                    backgroundColor: backgroundColors,
                    borderWidth: 1,
                    borderColor: borderColors,
                    // 统一的圆角样式（与知识点图表相同）
                    borderRadius: {
                        topLeft: 8,
                        topRight: 8,
                        bottomLeft: 2,
                        bottomRight: 2,
                    },
                    // 统一的阴影效果
                    shadowColor: "rgba(0, 0, 0, 0.1)",
                    shadowBlur: 4,
                    shadowOffsetX: 0,
                    shadowOffsetY: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "知识点数量" },
                },
                x: { title: { display: true, text: "知识点分类" } },
            },
        },
    });
};

// 退出功能已在StudentHeader组件中实现，此处不再需要

// 跳转到首页
const goToHome = () => {
    router.push("/student/index");
};
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}

.knowledge-page {
    width: 100%;
    min-height: 100vh;
    padding: 20px;
    background-color: #f4f7f9;
}

/* 加载动画样式 */
.loading-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.95);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    transition: opacity 0.5s ease;
}

.loading-spinner {
    width: 80px;
    height: 80px;
    border: 6px solid rgba(52, 152, 219, 0.1);
    border-radius: 50%;
    border-top-color: #3498db;
    animation: spin 1.5s ease-in-out infinite;
    margin-bottom: 25px;
    box-shadow: 0 0 20px rgba(52, 152, 219, 0.15);
}

.loading-text {
    font-size: 18px;
    color: #2c3e50;
    margin-bottom: 20px;
    font-weight: 500;
    text-align: center;
    max-width: 80%;
}

.loading-progress {
    width: 300px;
    height: 8px;
    background-color: #f1f5f9;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #3498db, #9b59b6);
    border-radius: 4px;
    transition: width 0.3s ease;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* 错误界面样式 */
.error-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #fefefe;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    padding: 20px;
    text-align: center;
}

.error-icon {
    font-size: 80px;
    margin-bottom: 30px;
    animation: pulse 2s infinite;
}

.error-title {
    font-size: 28px;
    color: #e74c3c;
    margin-bottom: 15px;
    font-weight: 600;
}

.error-message {
    font-size: 18px;
    color: #34495e;
    max-width: 600px;
    margin-bottom: 30px;
    line-height: 1.6;
}

.retry-btn,
.home-btn {
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
    margin: 0 10px;
}

.retry-btn {
    background: linear-gradient(90deg, #3498db, #2980b9);
    color: white;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.home-btn {
    background: linear-gradient(90deg, #95a5a6, #7f8c8d);
    color: white;
    box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

.retry-btn:hover {
    background: linear-gradient(90deg, #2980b9, #3498db);
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
}

.home-btn:hover {
    background: linear-gradient(90deg, #7f8c8d, #95a5a6);
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(149, 165, 166, 0.4);
}

.retry-btn:active,
.home-btn:active {
    transform: translateY(-1px);
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
    color: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
}

.stat-label {
    color: #7f8c8d;
    font-size: 14px;
}

.content-section {
    grid-column: 1 / -1; /* 让内容区域横跨所有列 */
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
    align-items: center; /* 垂直居中 */
    justify-content: center; /* 水平居中 */
    height: 200%; /* 占满父组件高度 */
    min-height: 350px; /* 保留最小高度，防止内容过小时变形 */
}

.chart-table {
    flex: 1;
    min-width: 300px;
    overflow-x: auto;
}

/* 表格样式优化 */
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 14px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* 表头样式 */
th {
    padding: 12px 15px;
    text-align: left;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    color: #334155;
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    border-bottom: 2px solid #e2e8f0;
    position: relative;
}

/* 表头底部装饰线 */
th:after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

/* 表头组悬停效果 */
table:hover th:after {
    transform: scaleX(1);
}

/* 表格内容单元格样式 */
td {
    padding: 12px 15px;
    text-align: left;
    color: #475569;
    border-bottom: 1px solid #f1f5f9;
    transition: all 0.2s ease;
}

/* 隔行变色 - 增强可读性 */
tbody tr:nth-child(even) {
    background-color: #f8fafc;
}

tbody tr:nth-child(odd) {
    background-color: #ffffff;
}

/* 行悬浮效果 */
tbody tr:hover {
    background-color: #eff6ff;
    transform: translateX(4px);
}

/* 悬浮时单元格文字变色 */
tbody tr:hover td {
    color: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    font-weight: 500;
}

/* 第一列加粗突出编号 */
td:first-child {
    font-weight: 600;
    color: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
}

/* 无数据提示样式优化 */
.no-data {
    text-align: center;
    color: #94a3b8;
    padding: 30px;
    font-style: italic;
    background-color: #f8fafc;
    border-bottom: none;
}

/* 表格最后一行去除下边框 */
tbody tr:last-child td {
    border-bottom: none;
}

/* 掌握度数值列特殊样式 */
td:nth-child(3) {
    font-weight: 600;
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

/* 进度条容器 - 确保容器本身有圆角，避免进度条边角溢出 */
.progress-container {
    width: 100%;
    height: 10px;
    background-color: #f0f0f0;
    border-radius: 8px; /* 增大圆角值，让边角更圆润 */
    overflow: hidden;
}

/* 进度条 - 设置圆角，与容器匹配 */
.progress {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 8px; /* 与容器圆角保持一致 */
}

/* 知识点卡片中的进度条容器也需要同步设置 */
.knowledge-progress-container {
    width: 100%;
    height: 8px;
    background-color: #f0f0f0;
    border-radius: 4px; /* 小一点的圆角，适配更细的进度条 */
    overflow: hidden;
    margin-bottom: 5px;
}

/* 知识点卡片中的进度条 */
.knowledge-progress {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 4px; /* 与容器匹配 */
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

/* 未掌握 - 纯红色 */
.level-unmastered {
    background: linear-gradient(90deg, #c0392b 0%, #e74c3c 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 15px;
    font-weight: 600;
}

.level-basic {
    background: red;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 15px;
    font-weight: 600;
}

.level-mastered {
    background: #f39c12;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 15px;
    font-weight: 600;
}

.level-proficient {
    background: green;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-size: 15px;
    font-weight: 600;
}

/* 精通 - 深绿色渐变 */
.level-expert {
    background: linear-gradient(90deg, #1e7e34 0%, #27ae60 50%, #2ecc71 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-size: 15px;
    font-weight: 600;
}

.knowledge-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.knowledge-card {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid #eee;
}

.knowledge-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.knowledge-icon {
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

.knowledge-info {
    flex: 1;
}

.knowledge-info h4 {
    margin-bottom: 8px;
    color: #2c3e50;
    font-size: 16px;
}

.knowledge-progress-container {
    width: 100%;
    height: 8px;
    background-color: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 5px;
}

.knowledge-progress {
    height: 100%;
    transition: width 0.3s ease;
}

.knowledge-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
}

.knowledge-level {
    font-weight: bold;
}

.knowledge-category {
    color: #7f8c8d;
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
    max-width: 700px;
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

.knowledge-description {
    margin: 15px 0;
    color: #34495e;
    line-height: 1.6;
}

.knowledge-detail-chart {
    height: 250px;
    margin: 20px 0;
}

.knowledge-stats {
    display: flex;
    justify-content: space-around;
    margin-top: 20px;
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

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.filter-control {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 15px;
    background-color: #f8fafc;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-control label {
    font-weight: 500;
    color: #334155;
    font-size: 0.95em;
    white-space: nowrap;
}

.filter-control select {
    padding: 8px 30px 8px 14px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    background-color: #fff;
    font-size: 0.9em;
    color: #1e293b;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.filter-control select:hover {
    border-color: #94a3b8;
}

.filter-control select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* 选项样式优化 */
.filter-control select option {
    padding: 8px;
    background-color: #fff;
    color: #1e293b;
}

.filter-control select option:hover {
    background-color: #f1f5f9;
}

@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr;
    }

    .chart-table-wrapper {
        flex-direction: column;
    }

    .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .loading-progress {
        width: 80%;
    }

    .error-message {
        font-size: 16px;
    }

    .retry-btn,
    .home-btn {
        width: 80%;
        margin: 10px 0;
    }
}

/* 返回首页按钮样式 */
.back-to-home {
    position: fixed;
    right: 30px;
    bottom: 30px;
    display: flex;
    align-items: center;
    justify-content: center; /* 居中图标 */
    gap: 0; /* 初始无间距 */
    padding: 12px; /* 小球状态的内边距 */
    width: 50px; /* 小球宽度 */
    height: 50px; /* 小球高度 */
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 50%, #3b82f6 100%);
    color: white;
    border-radius: 50%; /* 初始圆形 */
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
    transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); /* 平滑过渡 */
    z-index: 9999;
    border: none;
    cursor: pointer;
    font-weight: 500;
    overflow: hidden; /* 隐藏溢出内容 */
}

.back-to-home .icon {
    font-size: 18px;
    transition: transform 0.5s ease; /* 图标旋转动画 */
}

.back-to-home span:not(.icon) {
    opacity: 0; /* 文字初始隐藏 */
    width: 0; /* 文字初始宽度为0 */
    transition: all 0.5s ease; /* 文字显示动画 */
    white-space: nowrap; /* 防止文字换行 */
}

/* 悬停状态 - 展开成椭圆 */
.back-to-home:hover {
    width: 180px; /* 展开后的宽度 */
    height: 50px; /* 保持高度不变 */
    border-radius: 50px; /* 椭圆效果 */
    padding: 12px 20px; /* 展开后的内边距 */
    gap: 8px; /* 图标与文字间距 */
    transform: translateY(-5px); /* 轻微上浮 */
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4);
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #4f46e5 100%);
}

/* 悬停时显示文字并添加滚动效果 */
.back-to-home:hover span:not(.icon) {
    opacity: 1; /* 显示文字 */
    width: auto; /* 恢复文字宽度 */
    animation: slideIn 0.5s ease forwards; /* 文字滑入动画 */
}

/* 悬停时图标旋转 */
.back-to-home:hover .icon {
    transform: rotate(360deg); /* 图标旋转一周 */
}

.back-to-home:active {
    transform: translateY(-2px);
}

/* 文字滑入动画 */
@keyframes slideIn {
    from {
        transform: translateX(-20px); /* 从左侧进入 */
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
</style>
