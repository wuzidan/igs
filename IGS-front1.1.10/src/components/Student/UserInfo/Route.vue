<template>
    <div class="route-planning-page">
        <!-- 加载状态界面 -->
        <div class="loading-container" v-if="isLoading">
            <div class="loading-content">
                <div class="loader"></div>
                <h2>正在生成学习路径...</h2>
                <p>请稍候，我们正在为您定制最佳学习方案</p>
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

        <header class="header">
            <h1>学习路径规划</h1>
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

        <div class="dashboard">
            <!-- 学习状态统计 -->
            <div class="card stats-card">
                <h3>学习状态概览</h3>
                <div class="stats-grid">
                    <div
                        class="stat-card"
                        :class="getStatCardClass('mastered')"
                    >
                        <div class="stat-icon">✅</div>
                        <div class="stat-info">
                            <div class="stat-label">已掌握知识点</div>
                            <div class="stat-value">
                                {{ stats.masteredCount }}
                            </div>
                        </div>
                        <div class="stat-trend">
                            <span class="trend-arrow up">↑</span>
                            <span class="trend-text"
                                >较上周 +{{ stats.masteredIncrease }}</span
                            >
                        </div>
                    </div>

                    <div class="stat-card" :class="getStatCardClass('weak')">
                        <div class="stat-icon">⚠️</div>
                        <div class="stat-info">
                            <div class="stat-label">薄弱知识点</div>
                            <div class="stat-value">{{ stats.weakCount }}</div>
                        </div>
                        <div class="stat-trend">
                            <span
                                class="trend-arrow"
                                :class="stats.weakIncrease >= 0 ? 'up' : 'down'"
                            >
                                {{ stats.weakIncrease >= 0 ? "↑" : "↓" }}
                            </span>
                            <span class="trend-text">
                                {{ stats.weakIncrease >= 0 ? "增加" : "减少" }}
                                {{ Math.abs(stats.weakIncrease) }}
                            </span>
                        </div>
                    </div>

                    <div
                        class="stat-card"
                        :class="getStatCardClass('progress')"
                    >
                        <div class="stat-icon">📈</div>
                        <div class="stat-info">
                            <div class="stat-label">总体进度</div>
                            <div class="stat-value">
                                {{ stats.overallProgress }}%
                            </div>
                        </div>
                        <div class="stat-trend">
                            <span class="trend-arrow up">↑</span>
                            <span class="trend-text"
                                >目标: {{ stats.targetProgress }}%</span
                            >
                        </div>
                    </div>

                    <div
                        class="stat-card"
                        :class="getStatCardClass('recommended')"
                    >
                        <div class="stat-icon">📚</div>
                        <div class="stat-info">
                            <div class="stat-label">推荐资源</div>
                            <div class="stat-value">{{ resources.length }}</div>
                        </div>
                        <div class="stat-trend">
                            <span class="trend-date">今日更新</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 学习路径图 -->
            <div class="card">
                <h3>推荐学习路径</h3>
                <div class="small-chart">
                    <div class="path-visualization">
                        <div
                            class="path-node current-node"
                            :style="{ left: '10%', top: '50%' }"
                        >
                            <div class="node-content">当前位置</div>
                        </div>

                        <div class="path-connector"></div>

                        <div
                            class="path-node next-node"
                            :style="{ left: '30%', top: '30%' }"
                        >
                            <div class="node-content">
                                {{ knowledgePoints[0].name }}
                            </div>
                            <div class="node-details">
                                难度: {{ knowledgePoints[0].difficulty }}
                            </div>
                        </div>

                        <div class="path-connector"></div>

                        <div
                            class="path-node next-node"
                            :style="{ left: '50%', top: '60%' }"
                        >
                            <div class="node-content">
                                {{ knowledgePoints[1].name }}
                            </div>
                            <div class="node-details">
                                难度: {{ knowledgePoints[1].difficulty }}
                            </div>
                        </div>

                        <div class="path-connector"></div>

                        <div
                            class="path-node next-node"
                            :style="{ left: '70%', top: '40%' }"
                        >
                            <div class="node-content">
                                {{ knowledgePoints[2].name }}
                            </div>
                            <div class="node-details">
                                难度: {{ knowledgePoints[2].difficulty }}
                            </div>
                        </div>

                        <div class="path-connector"></div>

                        <div
                            class="path-node target-node"
                            :style="{ left: '90%', top: '50%' }"
                        >
                            <div class="node-content">学习目标</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 知识点掌握情况 -->
            <div class="card">
                <h3>知识点掌握情况</h3>
                <div class="knowledge-list">
                    <div
                        class="knowledge-item"
                        v-for="(point, index) in knowledgePoints"
                        :key="index"
                        :class="{ 'weak-knowledge': point.mastery < 60 }"
                    >
                        <div class="knowledge-header">
                            <div class="knowledge-name">
                                <span class="knowledge-icon">{{
                                    point.icon
                                }}</span>
                                {{ point.name }}
                            </div>
                            <div
                                class="knowledge-difficulty"
                                :class="getDifficultyClass(point.difficulty)"
                            >
                                {{ point.difficulty }}
                            </div>
                        </div>
                        <div class="mastery-progress">
                            <div class="progress-label">
                                <span>掌握度</span>
                                <span>{{ point.mastery }}%</span>
                            </div>
                            <div class="progress-container">
                                <div
                                    class="progress"
                                    :style="{ width: point.mastery + '%' }"
                                    :class="
                                        getProgressColorClass(point.mastery)
                                    "
                                ></div>
                            </div>
                        </div>
                        <div class="knowledge-actions">
                            <button
                                class="review-btn"
                                @click="reviewKnowledge(point.id)"
                            >
                                复习
                            </button>
                            <button
                                class="practice-btn"
                                @click="practiceKnowledge(point.id)"
                            >
                                练习
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 学习资源推荐 -->
            <div class="card">
                <h3>推荐学习资源</h3>
                <div class="resources-filter">
                    <div class="filter-control">
                        <label for="resource-type" class="filter-label"
                            >资源类型：</label
                        >
                        <select
                            id="resource-type"
                            v-model="selectedResourceType"
                            @change="filterResources"
                            class="resource-select"
                        >
                            <option value="all">全部</option>
                            <option value="video">视频教程</option>
                            <option value="article">文章</option>
                            <option value="exercise">练习题</option>
                            <option value="document">文档</option>
                        </select>
                    </div>
                    <div class="filter-control">
                        <label for="resource-sort" class="filter-label"
                            >排序：</label
                        >
                        <select
                            id="resource-sort"
                            v-model="resourceSort"
                            @change="filterResources"
                            class="resource-select"
                        >
                            <option value="relevance">相关度优先</option>
                            <option value="difficulty">难度递增</option>
                            <option value="duration">时长从短到长</option>
                        </select>
                    </div>
                </div>
                <div class="resources-grid">
                    <div
                        class="resource-card"
                        v-for="(resource, index) in filteredResources"
                        :key="index"
                        @click="openResource(resource.id)"
                    >
                        <div class="resource-type-badge" :class="resource.type">
                            {{ getResourceTypeText(resource.type) }}
                        </div>
                        <div class="resource-content">
                            <h4 class="resource-title">{{ resource.title }}</h4>
                            <p class="resource-description">
                                {{ resource.description }}
                            </p>
                            <div class="resource-meta">
                                <span class="meta-item duration">
                                    <i>⏱️</i> {{ resource.duration }}
                                </span>
                                <span
                                    class="meta-item difficulty"
                                    :class="resource.difficulty"
                                >
                                    {{ resource.difficulty }}
                                </span>
                                <span class="meta-item rating">
                                    <i>⭐</i> {{ resource.rating }}
                                </span>
                            </div>
                            <div class="resource-knowledge">
                                <span>关联知识点：</span>
                                <span
                                    class="knowledge-tag"
                                    v-for="(tag, i) in resource.knowledgeTags"
                                    :key="i"
                                >
                                    {{ tag }}
                                </span>
                            </div>
                        </div>
                        <button class="resource-action-btn">查看资源</button>
                    </div>
                </div>
                <div v-if="filteredResources.length === 0" class="no-data">
                    没有符合条件的学习资源
                </div>
            </div>

            <!-- 学习计划 -->
            <div class="card" style="grid-column: 1 / -1">
                <h3>本周学习计划</h3>
                <div class="weekly-plan">
                    <div
                        class="day-column"
                        v-for="(day, index) in weeklyPlan"
                        :key="index"
                    >
                        <div class="day-header">{{ day.day }}</div>
                        <div class="day-content">
                            <div
                                class="plan-item"
                                v-for="(item, i) in day.items"
                                :key="i"
                            >
                                <div class="plan-icon">{{ item.icon }}</div>
                                <div class="plan-details">
                                    <div class="plan-title">
                                        {{ item.title }}
                                    </div>
                                    <div class="plan-duration">
                                        {{ item.duration }}
                                    </div>
                                </div>
                                <div class="plan-status" :class="item.status">
                                    {{
                                        item.status === "completed"
                                            ? "✓"
                                            : item.status === "in-progress"
                                            ? "◔"
                                            : "○"
                                    }}
                                </div>
                            </div>
                            <button
                                class="add-plan-btn"
                                @click="addPlan(day.day)"
                            >
                                +
                            </button>
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
import { ref, onMounted, computed } from "vue";
// 假设api已导入，如果没有实际的API服务，可以注释掉下面这行
// import api from "../../../api/index";

// 用户信息
const userName = ref("李四");
const studentId = ref("20230002");

// 学习统计数据
const stats = ref({
    masteredCount: 0,
    masteredIncrease: 0,
    weakCount: 0,
    weakIncrease: 0,
    overallProgress: 0,
    targetProgress: 0,
});

// 知识点数据
const knowledgePoints = ref([
    // 示例数据
    { id: 1, name: "Vue基础语法", difficulty: "easy", mastery: 85, icon: "📐" },
    { id: 2, name: "组件通信", difficulty: "medium", mastery: 65, icon: "🔄" },
    {
        id: 3,
        name: "Vuex状态管理",
        difficulty: "medium",
        mastery: 45,
        icon: "📦",
    },
    {
        id: 4,
        name: "Vue Router路由",
        difficulty: "medium",
        mastery: 70,
        icon: "🧭",
    },
    {
        id: 5,
        name: "Composition API",
        difficulty: "hard",
        mastery: 30,
        icon: "🧩",
    },
]);

// 学习资源
const resources = ref([
    // 示例数据
    {
        id: 1,
        type: "video",
        title: "Vue基础入门到精通",
        description:
            "本视频系列涵盖Vue的核心概念和基础语法，适合初学者快速入门。",
        duration: "2小时30分",
        difficulty: "easy",
        rating: 4.8,
        relevance: 95,
        knowledgeTags: ["Vue基础语法"],
    },
    {
        id: 2,
        type: "article",
        title: "深入理解Vue组件通信方式",
        description: "详细介绍Vue中各种组件通信方法的优缺点及使用场景。",
        duration: "15分钟",
        difficulty: "medium",
        rating: 4.6,
        relevance: 90,
        knowledgeTags: ["组件通信"],
    },
    {
        id: 3,
        type: "exercise",
        title: "Vuex状态管理实战练习",
        description: "通过实际案例练习Vuex的核心功能和最佳实践。",
        duration: "45分钟",
        difficulty: "medium",
        rating: 4.5,
        relevance: 88,
        knowledgeTags: ["Vuex状态管理"],
    },
    {
        id: 4,
        type: "document",
        title: "Vue Router官方文档详解",
        description: "官方文档的中文解读，包含路由守卫、动态路由等高级用法。",
        duration: "30分钟",
        difficulty: "medium",
        rating: 4.7,
        relevance: 85,
        knowledgeTags: ["Vue Router路由"],
    },
    {
        id: 5,
        type: "video",
        title: "Composition API完全指南",
        description: "从选项式API迁移到组合式API的完整教程，包含实战案例。",
        duration: "3小时",
        difficulty: "hard",
        rating: 4.9,
        relevance: 80,
        knowledgeTags: ["Composition API"],
    },
]);

// 筛选相关
const selectedResourceType = ref("all");
const resourceSort = ref("relevance");

// 本周学习计划
const weeklyPlan = ref([
    // 示例数据
    {
        day: "周一",
        items: [
            {
                icon: "📚",
                title: "学习Vue基础语法",
                duration: "45分钟",
                status: "completed",
            },
        ],
    },
    {
        day: "周二",
        items: [
            {
                icon: "✏️",
                title: "Vue基础练习",
                duration: "30分钟",
                status: "completed",
            },
        ],
    },
    {
        day: "周三",
        items: [
            {
                icon: "📚",
                title: "学习组件通信",
                duration: "60分钟",
                status: "in-progress",
            },
        ],
    },
    {
        day: "周四",
        items: [
            {
                icon: "✏️",
                title: "组件通信练习",
                duration: "45分钟",
                status: "pending",
            },
        ],
    },
    {
        day: "周五",
        items: [
            {
                icon: "📚",
                title: "学习Vuex基础",
                duration: "60分钟",
                status: "pending",
            },
        ],
    },
    {
        day: "周六",
        items: [
            {
                icon: "📚",
                title: "Vuex进阶用法",
                duration: "90分钟",
                status: "pending",
            },
            {
                icon: "✏️",
                title: "Vuex实战练习",
                duration: "60分钟",
                status: "pending",
            },
        ],
    },
    {
        day: "周日",
        items: [
            {
                icon: "📝",
                title: "本周知识点总结",
                duration: "60分钟",
                status: "pending",
            },
        ],
    },
]);

// 状态变量
const isLoading = ref(true);
const errorMsg = ref("");

// 获取学习路径数据
const fetchRouteData = () => {
    // 模拟API调用
    return new Promise((resolve) => {
        setTimeout(() => {
            // 更新统计数据
            stats.value = {
                masteredCount: 12,
                masteredIncrease: 3,
                weakCount: 5,
                weakIncrease: -1,
                overallProgress: 45,
                targetProgress: 100,
            };

            resolve();
        }, 1000);
    });

    // 实际API调用代码（如果有）
    /*
    return api
        .getLearningRoute()
        .then((res) => {
            console.log("获取的学习路径数据：", res.data);
            const data = res.data;
            
            // 更新统计数据
            stats.value = { ...data.stats };
            
            // 更新知识点数据
            knowledgePoints.value = [...data.knowledgePoints];
            
            // 更新学习资源
            resources.value = [...data.resources];
            
            // 更新学习计划
            weeklyPlan.value = [...data.weeklyPlan];
        })
        .catch((err) => {
            console.error("获取学习路径失败：", err);
            errorMsg.value = "获取学习路径数据失败，请稍后重试";
            throw err;
        });
    */
};

// 获取用户信息
const fetchUserInfo = () => {
    // 模拟API调用
    return new Promise((resolve) => {
        setTimeout(() => {
            // 保持现有示例数据不变
            resolve();
        }, 500);
    });

    // 实际API调用代码（如果有）
    /*
    return api
        .getStudentinfo()
        .then((res) => {
            console.log("获取的用户信息：", res.data);
            const data = res.data;
            userName.value = data.userName || "未知用户";
            studentId.value = data.studentId || "";
        })
        .catch((err) => {
            console.error("获取用户信息失败：", err);
            // 不显示错误，使用默认值
        });
    */
};

onMounted(() => {
    // 加载数据
    Promise.all([fetchUserInfo(), fetchRouteData()])
        .then(() => {
            isLoading.value = false;
        })
        .catch(() => {
            isLoading.value = false;
            if (!errorMsg.value) {
                errorMsg.value = "加载数据失败，请稍后重试";
            }
        });
});

// 筛选后的资源
const filteredResources = computed(() => {
    let result = [...resources.value];

    // 按类型筛选
    if (selectedResourceType.value !== "all") {
        result = result.filter((r) => r.type === selectedResourceType.value);
    }

    // 排序
    switch (resourceSort.value) {
        case "difficulty":
            result.sort((a, b) => {
                const difficultyOrder = { easy: 1, medium: 2, hard: 3 };
                return (
                    difficultyOrder[a.difficulty] -
                    difficultyOrder[b.difficulty]
                );
            });
            break;
        case "duration":
            result.sort((a, b) => {
                const getMinutes = (str) => {
                    if (str.includes("小时")) {
                        const hours = parseInt(str);
                        return hours * 60;
                    }
                    return parseInt(str);
                };
                return getMinutes(a.duration) - getMinutes(b.duration);
            });
            break;
        // 默认按相关度
        default:
            result.sort((a, b) => b.relevance - a.relevance);
    }

    return result;
});

// 方法：筛选资源
const filterResources = () => {
    // 由computed属性处理
};

// 方法：获取资源类型文本
const getResourceTypeText = (type) => {
    const types = {
        video: "视频教程",
        article: "文章",
        exercise: "练习题",
        document: "文档",
    };
    return types[type] || "未知类型";
};

// 方法：获取进度条颜色类
const getProgressColorClass = (progress) => {
    if (progress < 50) return "progress-low";
    if (progress < 75) return "progress-medium";
    return "progress-high";
};

// 方法：获取难度样式类
const getDifficultyClass = (difficulty) => {
    const classes = {
        easy: "difficulty-easy",
        medium: "difficulty-medium",
        hard: "difficulty-hard",
    };
    return classes[difficulty] || "";
};

// 方法：获取统计卡片样式
const getStatCardClass = (type) => {
    const classes = {
        mastered: "stat-mastered",
        weak: "stat-weak",
        progress: "stat-progress",
        recommended: "stat-recommended",
    };
    return classes[type];
};

// 方法：复习知识点
const reviewKnowledge = (id) => {
    alert(`开始复习知识点 #${id}`);
    // 实际应用中会导航到相应的复习页面
};

// 方法：练习知识点
const practiceKnowledge = (id) => {
    alert(`开始练习知识点 #${id}`);
    // 实际应用中会导航到相应的练习页面
};

// 方法：打开资源
const openResource = (id) => {
    alert(`打开资源 #${id}`);
    // 实际应用中会打开相应的资源
};

// 方法：添加计划
const addPlan = (day) => {
    alert(`在${day}添加新计划`);
    // 实际应用中会打开添加计划的表单
};

// 方法：重试加载
const retryLoad = () => {
    isLoading.value = true;
    errorMsg.value = "";

    fetchRouteData()
        .then(() => {
            isLoading.value = false;
        })
        .catch(() => {
            isLoading.value = false;
            errorMsg.value = "重试加载失败，请检查网络连接后再试";
        });
};

// 退出功能
const logout = () => {
    alert("您已退出系统");
};
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}

.route-planning-page {
    width: 100%;
    min-height: 100vh;
    padding: 20px;
    background-color: #f4f7f9;
}

/* 加载状态样式 */
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
    padding: 30px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
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

/* 错误状态样式 */
.error-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
}

.error-content {
    text-align: center;
    max-width: 500px;
    padding: 30px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.error-icon {
    font-size: 48px;
    margin-bottom: 20px;
    color: #f97316;
}

.error-message {
    margin: 15px 0 25px;
    color: #64748b;
    line-height: 1.6;
}

.retry-btn {
    padding: 10px 20px;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.retry-btn:hover {
    background-color: #2563eb;
}

/* 头部样式 */
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
    margin-right: 10px;
}

.avatar-default {
    background-color: #dbeafe;
    color: #1e40af;
    font-size: 20px;
}

.user-basic h2 {
    font-size: 16px;
    margin: 0;
    color: #1e293b;
}

.user-id {
    font-size: 13px;
    color: #64748b;
    margin: 0;
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

/* 卡片样式 */
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

/* 统计卡片样式 */
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

.stat-mastered {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.stat-weak {
    background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
}

.stat-progress {
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
}

.stat-recommended {
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

/* 路径可视化样式 */
.path-visualization {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 200px;
    padding: 20px 0;
}

.path-node {
    position: absolute;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translate(-50%, -50%);
    transition: all 0.3s ease;
    z-index: 2;
}

.path-node:hover {
    transform: translate(-50%, -50%) scale(1.1);
}

.path-node .node-content {
    font-size: 14px;
    font-weight: 600;
}

.path-node .node-details {
    font-size: 12px;
    margin-top: 5px;
    color: #64748b;
}

.current-node {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: 3px solid #93c5fd;
    width: 90px;
    height: 90px;
}

.next-node {
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    color: #1e293b;
    border: 2px solid #dbeafe;
}

.target-node {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: 3px solid #a7f3d0;
}

.path-connector {
    position: absolute;
    top: 50%;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd, #bfdbfe);
    transform: translateY(-50%);
    z-index: 1;
}

/* 知识点列表样式 */
.knowledge-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.knowledge-item {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
}

.knowledge-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
}

.knowledge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.knowledge-name {
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 8px;
}

.knowledge-icon {
    font-size: 18px;
}

.knowledge-difficulty {
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.difficulty-easy {
    background-color: #dcfce7;
    color: #166534;
}

.difficulty-medium {
    background-color: #fef3c7;
    color: #92400e;
}

.difficulty-hard {
    background-color: #fee2e2;
    color: #b91c1c;
}

.mastery-progress {
    margin-bottom: 12px;
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

.knowledge-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.review-btn,
.practice-btn {
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
}

.review-btn {
    background-color: #dbeafe;
    color: #1e40af;
}

.review-btn:hover {
    background-color: #bfdbfe;
}

.practice-btn {
    background-color: #dcfce7;
    color: #065f46;
}

.practice-btn:hover {
    background-color: #bbf7d0;
}

/* 资源推荐样式 */
.resources-filter {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
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

.resource-select {
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

.resource-select:focus {
    outline: none;
    border-color: #3498db;
}

.resources-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
}

.resource-card {
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}

.resource-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.resource-type-badge {
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 500;
    color: white;
}

.resource-type-badge.video {
    background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.resource-type-badge.article {
    background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}

.resource-type-badge.exercise {
    background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.resource-type-badge.document {
    background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
}

.resource-content {
    padding: 15px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.resource-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #1e293b;
    line-height: 1.4;
}

.resource-description {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 12px;
    line-height: 1.5;
    flex: 1;
}

.resource-meta {
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    font-size: 12px;
    color: #64748b;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
}

.meta-item.difficulty.easy {
    color: #10b981;
}

.meta-item.difficulty.medium {
    color: #f59e0b;
}

.meta-item.difficulty.hard {
    color: #ef4444;
}

.resource-knowledge {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
    font-size: 12px;
}

.knowledge-tag {
    background-color: #eff6ff;
    color: #1e40af;
    padding: 2px 8px;
    border-radius: 12px;
}

.resource-action-btn {
    width: 100%;
    padding: 8px 0;
    background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.resource-action-btn:hover {
    background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
    transform: translateY(-1px);
    box-shadow: 0 3px 6px rgba(59, 130, 246, 0.15);
}

/* 周计划样式 */
.weekly-plan {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 15px;
}

.day-column {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    overflow: hidden;
}

.day-header {
    background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    padding: 10px;
    text-align: center;
    font-weight: 600;
    font-size: 14px;
}

.day-content {
    padding: 10px;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.plan-item {
    display: flex;
    align-items: center;
    padding: 8px;
    background-color: #f8fafc;
    border-radius: 4px;
    font-size: 13px;
    gap: 10px;
}

.plan-icon {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    background-color: #dbeafe;
    color: #1e40af;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.plan-details {
    flex: 1;
}

.plan-title {
    font-weight: 500;
    margin-bottom: 2px;
}

.plan-duration {
    font-size: 11px;
    color: #64748b;
}

.plan-status {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    flex-shrink: 0;
}

.plan-status.completed {
    background-color: #dcfce7;
    color: #166534;
}

.plan-status.in-progress {
    background-color: #dbeafe;
    color: #1e40af;
}

.plan-status.pending {
    background-color: #f1f5f9;
    color: #64748b;
}

.add-plan-btn {
    margin-top: auto;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #eff6ff;
    color: #2563eb;
    border: 1px dashed #93c5fd;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.add-plan-btn:hover {
    background-color: #dbeafe;
    transform: scale(1.1);
}

/* 无数据样式 */
.no-data {
    text-align: center;
    color: #888;
    padding: 40px 20px;
    font-style: italic;
    background-color: white;
    border-radius: 8px;
    border: 1px solid #eee;
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

/* 响应式设计 */
@media (max-width: 1200px) {
    .weekly-plan {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr;
    }

    .weekly-plan {
        grid-template-columns: repeat(2, 1fr);
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .resources-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .weekly-plan {
        grid-template-columns: 1fr;
    }

    .header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .user-info {
        width: 100%;
        justify-content: space-between;
    }
}
</style>
