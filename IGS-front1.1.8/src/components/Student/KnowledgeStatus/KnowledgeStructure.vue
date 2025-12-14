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

                <!-- 课程统计卡片 -->
                <div class="card">
                    <h3>课程统计</h3>
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-value">{{
                                courseList.length
                            }}</span>
                            <span class="stat-label">已学课程</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{
                                getTotalChapters()
                            }}</span>
                            <span class="stat-label">总章节数</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{ totalCount }}</span>
                            <span class="stat-label">总知识点</span>
                        </div>
                    </div>
                </div>

                <!-- 知识点掌握度区域（增加筛选功能） -->
                <div class="content-section">
                    <div class="section-header">
                        <h3>知识点掌握度</h3>
                        <!-- 筛选控件 -->
                        <div class="filter-controls">
                            <div class="filter-control">
                                <label for="course-filter" class="filter-label"
                                    >按课程筛选：</label
                                >
                                <select
                                    id="course-filter"
                                    v-model="selectedCourseId"
                                    @change="updateFilters"
                                    class="mastery-select"
                                >
                                    <option value="all">全部课程</option>
                                    <option
                                        v-for="course in courseList"
                                        :key="course.id"
                                        :value="course.id"
                                    >
                                        {{ course.name }}
                                    </option>
                                </select>
                            </div>
                            <div class="filter-control">
                                <label for="chapter-filter" class="filter-label"
                                    >按章节筛选：</label
                                >
                                <select
                                    id="chapter-filter"
                                    v-model="selectedChapterId"
                                    @change="updateFilters"
                                    class="mastery-select"
                                >
                                    <option value="all">全部章节</option>
                                    <option
                                        v-for="chapter in filteredChapters"
                                        :key="chapter.id"
                                        :value="chapter.id"
                                    >
                                        {{ chapter.name }}
                                    </option>
                                </select>
                            </div>
                            <div class="filter-control">
                                <label for="mastery-filter" class="filter-label"
                                    >按掌握情况筛选：</label
                                >
                                <select
                                    id="mastery-filter"
                                    v-model="selectedLevel"
                                    @change="updateFilters"
                                    class="mastery-select"
                                >
                                    <option value="all">全部</option>
                                    <option value="unmastered">
                                        未掌握（<30%）
                                    </option>
                                    <option value="basic">
                                        了解（30%-50%）
                                    </option>
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
                    </div>
                    <div class="chart-table-wrapper">
                        <div class="chart-container">
                            <canvas id="masteryChart"></canvas>
                        </div>
                        <div class="chart-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>课程</th>
                                        <th>章节</th>
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
                                        <td>
                                            {{
                                                getCourseName(
                                                    knowledge.courseId
                                                )
                                            }}
                                        </td>
                                        <td>
                                            {{
                                                getChapterName(
                                                    knowledge.chapterId
                                                )
                                            }}
                                        </td>
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
                                        <td colspan="5" class="no-data">
                                            没有符合条件的知识点
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- 课程章节知识点层级展示（两列布局） -->
                <div class="content-section">
                    <h3>课程-章节-知识点结构</h3>
                    <!-- 核心修改：两列网格布局 -->
                    <div class="course-structure-grid">
                        <!-- 课程列表 -->
                        <div
                            v-for="course in courseList"
                            :key="course.id"
                            class="course-card"
                        >
                            <div
                                class="course-header"
                                @click="toggleCourse(course.id)"
                            >
                                <span class="expand-icon">{{
                                    courseExpanded[course.id] ? "▼" : "▶"
                                }}</span>
                                <div class="course-info">
                                    <h4>{{ course.name }}</h4>
                                    <div class="course-meta">
                                        <span
                                            >{{
                                                getChaptersByCourse(course.id)
                                                    .length
                                            }}
                                            章节</span
                                        >
                                        <span
                                            >{{
                                                getKnowledgeByCourse(course.id)
                                                    .length
                                            }}
                                            知识点</span
                                        >
                                        <span
                                            class="mastery-badge"
                                            :class="
                                                getProgressColorClass(
                                                    course.avgMastery
                                                )
                                            "
                                        >
                                            {{ course.avgMastery.toFixed(1) }}%
                                            掌握度
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <!-- 章节列表 -->
                            <div
                                v-if="courseExpanded[course.id]"
                                class="chapters-container"
                            >
                                <div
                                    v-for="chapter in getChaptersByCourse(
                                        course.id
                                    )"
                                    :key="chapter.id"
                                    class="chapter-card"
                                >
                                    <div
                                        class="chapter-header"
                                        @click="toggleChapter(chapter.id)"
                                    >
                                        <span class="expand-icon">{{
                                            chapterExpanded[chapter.id]
                                                ? "▼"
                                                : "▶"
                                        }}</span>
                                        <div class="chapter-info">
                                            <h5>{{ chapter.name }}</h5>
                                            <div class="chapter-meta">
                                                <span
                                                    >{{
                                                        getKnowledgeByChapter(
                                                            chapter.id
                                                        ).length
                                                    }}
                                                    知识点</span
                                                >
                                                <span
                                                    class="mastery-badge"
                                                    :class="
                                                        getProgressColorClass(
                                                            chapter.avgMastery
                                                        )
                                                    "
                                                >
                                                    {{
                                                        chapter.avgMastery.toFixed(
                                                            1
                                                        )
                                                    }}% 掌握度
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 知识点列表 -->
                                    <div
                                        v-if="chapterExpanded[chapter.id]"
                                        class="knowledge-list"
                                    >
                                        <div
                                            class="knowledge-item"
                                            v-for="knowledge in getKnowledgeByChapter(
                                                chapter.id
                                            )"
                                            :key="knowledge.id"
                                            @click="
                                                showKnowledgeDetail(knowledge)
                                            "
                                        >
                                            <div class="knowledge-icon">
                                                {{
                                                    getCategoryIcon(
                                                        knowledge.category
                                                    )
                                                }}
                                            </div>
                                            <div class="knowledge-content">
                                                <div class="knowledge-name">
                                                    {{ knowledge.name }}
                                                </div>
                                                <div
                                                    class="knowledge-progress-container"
                                                >
                                                    <div
                                                        class="knowledge-progress"
                                                        :style="{
                                                            width:
                                                                knowledge.mastery +
                                                                '%',
                                                        }"
                                                        :class="
                                                            getMasteryColorClass(
                                                                knowledge.mastery
                                                            )
                                                        "
                                                    ></div>
                                                </div>
                                                <div class="knowledge-footer">
                                                    <span
                                                        class="mastery-level"
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
                                                        ({{
                                                            knowledge.mastery
                                                        }}%)
                                                    </span>
                                                    <span
                                                        class="knowledge-category"
                                                        >{{
                                                            knowledge.categoryText
                                                        }}</span
                                                    >
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
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
            </div>

            <!-- 单个知识点详情弹窗 -->
            <div class="modal" v-if="selectedKnowledge">
                <div class="modal-content">
                    <span class="close" @click="selectedKnowledge = null"
                        >&times;</span
                    >
                    <h3>{{ selectedKnowledge.name }}</h3>
                    <div class="knowledge-path">
                        {{ getCourseName(selectedKnowledge.courseId) }} >
                        {{ getChapterName(selectedKnowledge.chapterId) }}
                    </div>
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
import StudentHeader from "../StudentHeader.vue";

// 路由实例
const router = useRouter();

// ===================== Mock数据定义 =====================
// 基础统计数据
const MOCK_BASE_DATA = {
    coverageRate: 85,
    masteredCount: 28,
    totalCount: 35,
    avgMastery: 78.5,
};

// 课程列表
const MOCK_COURSE_LIST = [
    {
        id: 1,
        name: "Vue3 核心原理与实战",
        avgMastery: 82.3,
    },
    {
        id: 2,
        name: "TypeScript 进阶开发",
        avgMastery: 75.8,
    },
    {
        id: 3,
        name: "前端工程化实践",
        avgMastery: 70.5,
    },
];

// 章节列表
const MOCK_CHAPTER_LIST = [
    // Vue3课程章节
    { id: 101, courseId: 1, name: "Vue3 基础语法", avgMastery: 90.5 },
    { id: 102, courseId: 1, name: "组合式API", avgMastery: 85.2 },
    { id: 103, courseId: 1, name: "组件通信与生命周期", avgMastery: 78.9 },

    // TS课程章节
    { id: 201, courseId: 2, name: "TS 类型系统", avgMastery: 80.1 },
    { id: 202, courseId: 2, name: "高级类型与泛型", avgMastery: 72.5 },
    { id: 203, courseId: 2, name: "TS与Vue3结合", avgMastery: 75.3 },

    // 工程化课程章节
    { id: 301, courseId: 3, name: "Vite 构建工具", avgMastery: 78.6 },
    { id: 302, courseId: 3, name: "ESLint与Prettier", avgMastery: 65.4 },
    { id: 303, courseId: 3, name: "CI/CD 自动化部署", avgMastery: 67.8 },
];

// 知识点列表
const MOCK_KNOWLEDGE_LIST = [
    // Vue3 - 基础语法
    {
        id: 1001,
        courseId: 1,
        chapterId: 101,
        name: "模板语法与指令",
        mastery: 95,
        category: "core",
        categoryText: "核心知识点",
        description:
            "掌握Vue3模板语法，包括插值表达式、指令系统、动态绑定等核心概念，能够熟练运用到实际开发中。",
        practiceCount: 28,
        lastPracticed: "2025-06-10",
    },
    {
        id: 1002,
        courseId: 1,
        chapterId: 101,
        name: "响应式数据声明",
        mastery: 92,
        category: "core",
        categoryText: "核心知识点",
        description:
            "理解ref和reactive的区别，掌握响应式数据的声明和使用方式，解决响应式丢失问题。",
        practiceCount: 25,
        lastPracticed: "2025-06-08",
    },
    {
        id: 1003,
        courseId: 1,
        chapterId: 101,
        name: "计算属性与侦听器",
        mastery: 88,
        category: "important",
        categoryText: "重要知识点",
        description:
            "掌握computed和watch的使用场景，理解缓存机制，优化组件性能。",
        practiceCount: 20,
        lastPracticed: "2025-06-05",
    },

    // Vue3 - 组合式API
    {
        id: 1004,
        courseId: 1,
        chapterId: 102,
        name: "setup语法糖",
        mastery: 89,
        category: "core",
        categoryText: "核心知识点",
        description:
            "熟练使用setup语法糖，理解其执行时机和上下文，掌握<script setup>的各种特性。",
        practiceCount: 22,
        lastPracticed: "2025-06-09",
    },
    {
        id: 1005,
        courseId: 1,
        chapterId: 102,
        name: "生命周期钩子",
        mastery: 82,
        category: "important",
        categoryText: "重要知识点",
        description:
            "掌握Vue3组合式API中的生命周期钩子函数，理解与选项式API的对应关系。",
        practiceCount: 18,
        lastPracticed: "2025-06-07",
    },
    {
        id: 1006,
        courseId: 1,
        chapterId: 102,
        name: "依赖注入provide/inject",
        mastery: 75,
        category: "general",
        categoryText: "一般知识点",
        description: "理解依赖注入的原理和使用场景，解决深层组件通信问题。",
        practiceCount: 12,
        lastPracticed: "2025-06-03",
    },

    // TS - 类型系统
    {
        id: 2001,
        courseId: 2,
        chapterId: 201,
        name: "基础类型与接口",
        mastery: 85,
        category: "core",
        categoryText: "核心知识点",
        description:
            "掌握TypeScript基础类型定义，熟练使用interface定义复杂类型结构。",
        practiceCount: 24,
        lastPracticed: "2025-06-08",
    },
    {
        id: 2002,
        courseId: 2,
        chapterId: 201,
        name: "类型断言与类型守卫",
        mastery: 78,
        category: "important",
        categoryText: "重要知识点",
        description:
            "理解类型断言的使用场景，掌握typeof、instanceof等类型守卫技巧。",
        practiceCount: 16,
        lastPracticed: "2025-06-04",
    },

    // TS - 高级类型
    {
        id: 2003,
        courseId: 2,
        chapterId: 202,
        name: "泛型编程",
        mastery: 70,
        category: "core",
        categoryText: "核心知识点",
        description: "掌握泛型的定义和使用，理解泛型约束、默认类型等高级特性。",
        practiceCount: 15,
        lastPracticed: "2025-06-02",
    },
    {
        id: 2004,
        courseId: 2,
        chapterId: 202,
        name: "条件类型与映射类型",
        mastery: 65,
        category: "important",
        categoryText: "重要知识点",
        description: "学习高级类型操作，掌握条件类型、映射类型的使用技巧。",
        practiceCount: 10,
        lastPracticed: "2025-06-01",
    },

    // 工程化 - Vite
    {
        id: 3001,
        courseId: 3,
        chapterId: 301,
        name: "Vite 配置详解",
        mastery: 82,
        category: "core",
        categoryText: "核心知识点",
        description:
            "掌握Vite的核心配置项，理解开发服务器、构建优化等关键配置。",
        practiceCount: 18,
        lastPracticed: "2025-06-07",
    },
    {
        id: 3002,
        courseId: 3,
        chapterId: 301,
        name: "插件开发与使用",
        mastery: 75,
        category: "important",
        categoryText: "重要知识点",
        description: "了解Vite插件机制，能够开发简单插件或集成第三方插件。",
        practiceCount: 11,
        lastPracticed: "2025-06-03",
    },

    // 工程化 - 代码规范
    {
        id: 3003,
        courseId: 3,
        chapterId: 302,
        name: "ESLint 配置",
        mastery: 70,
        category: "general",
        categoryText: "一般知识点",
        description: "掌握ESLint的基本配置，理解规则定制和共享配置的使用。",
        practiceCount: 9,
        lastPracticed: "2025-05-30",
    },
    {
        id: 3004,
        courseId: 3,
        chapterId: 302,
        name: "Prettier 集成",
        mastery: 60,
        category: "general",
        categoryText: "一般知识点",
        description: "学习Prettier与ESLint的集成方案，解决代码格式化冲突问题。",
        practiceCount: 7,
        lastPracticed: "2025-05-28",
    },

    // 工程化 - CI/CD
    {
        id: 3005,
        courseId: 3,
        chapterId: 303,
        name: "GitHub Actions",
        mastery: 65,
        category: "important",
        categoryText: "重要知识点",
        description: "了解GitHub Actions基本语法，能够编写简单的CI/CD工作流。",
        practiceCount: 8,
        lastPracticed: "2025-05-25",
    },
    {
        id: 3006,
        courseId: 3,
        chapterId: 303,
        name: "自动化部署流程",
        mastery: 70,
        category: "general",
        categoryText: "一般知识点",
        description: "掌握前端项目自动化部署的基本流程，理解环境变量配置。",
        practiceCount: 6,
        lastPracticed: "2025-05-20",
    },
];
// ===================== Mock数据定义结束 =====================

// 总体数据
const coverageRate = ref(0);
const masteredCount = ref(0);
const totalCount = ref(0);
const avgMastery = ref(0);

// 层级数据
const courseList = ref([]);
const chapterList = ref([]);
const knowledgeList = ref([]);

// 筛选相关变量
const selectedLevel = ref("all");
const selectedCourseId = ref("all");
const selectedChapterId = ref("all");

// 展开/折叠状态
const courseExpanded = ref({});
const chapterExpanded = ref({});

// 响应式变量
const structureRecords = ref(null);
const isLoading = ref(true);
const errorMsg = ref("");
const loadingProgress = ref(0); // 加载进度

// 选中的知识点
const selectedKnowledge = ref(null);

// 图表实例
let masteryChartInstance = null;
let categoryMasteryChartInstance = null;
let knowledgeDetailChartInstance = null;

// 模拟API请求（带失败降级逻辑）
const mockApiGetStructure = () => {
    // 模拟50%概率请求失败，用于测试降级逻辑
    const isSuccess = true; // 改为false可测试失败场景

    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (isSuccess) {
                resolve({
                    data: {
                        ...MOCK_BASE_DATA,
                        courseList: MOCK_COURSE_LIST,
                        chapterList: MOCK_CHAPTER_LIST,
                        knowledgeList: MOCK_KNOWLEDGE_LIST,
                    },
                });
            } else {
                reject(new Error("模拟API请求失败"));
            }
        }, 1500); // 模拟网络延迟
    });
};

// 获取知识点结构数据（带降级逻辑）
const fetchStructureData = () => {
    // 先尝试调用真实API，失败则使用Mock数据
    return mockApiGetStructure() // 替换为真实api.getStructure()
        .then((res) => {
            console.log("获取的知识点结构数据为：", res.data);
            const data = res.data;

            // 验证数据有效性
            if (
                !data ||
                !Array.isArray(data.courseList) ||
                !Array.isArray(data.chapterList) ||
                !Array.isArray(data.knowledgeList)
            ) {
                throw new Error("数据格式异常");
            }

            // 更新总体数据
            coverageRate.value = data.coverageRate || 0;
            masteredCount.value = data.masteredCount || 0;
            totalCount.value = data.totalCount || 0;
            avgMastery.value = data.avgMastery || 0;

            // 更新层级数据
            courseList.value = data.courseList;
            chapterList.value = data.chapterList;
            knowledgeList.value = data.knowledgeList;

            structureRecords.value = data;
            updateLoadingProgress(100); // 加载完成
        })
        .catch((err) => {
            console.error("获取知识点数据失败，使用兜底Mock数据:", err);

            // 降级使用Mock数据
            coverageRate.value = MOCK_BASE_DATA.coverageRate;
            masteredCount.value = MOCK_BASE_DATA.masteredCount;
            totalCount.value = MOCK_BASE_DATA.totalCount;
            avgMastery.value = MOCK_BASE_DATA.avgMastery;

            courseList.value = MOCK_COURSE_LIST;
            chapterList.value = MOCK_CHAPTER_LIST;
            knowledgeList.value = MOCK_KNOWLEDGE_LIST;

            structureRecords.value = {
                ...MOCK_BASE_DATA,
                courseList: MOCK_COURSE_LIST,
                chapterList: MOCK_CHAPTER_LIST,
                knowledgeList: MOCK_KNOWLEDGE_LIST,
            };

            updateLoadingProgress(100);
            // 不设置errorMsg，让页面正常显示Mock数据
            // errorMsg.value = "网络请求错误，已加载本地示例数据";
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
            // 初始化展开状态
            courseList.value.forEach((course) => {
                courseExpanded.value[course.id] = true; // 默认展开所有课程
            });
            chapterList.value.forEach((chapter) => {
                chapterExpanded.value[chapter.id] = false; // 默认折叠所有章节
            });

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

// 切换课程展开/折叠状态
const toggleCourse = (courseId) => {
    courseExpanded.value[courseId] = !courseExpanded.value[courseId];
};

// 切换章节展开/折叠状态
const toggleChapter = (chapterId) => {
    chapterExpanded.value[chapterId] = !chapterExpanded.value[chapterId];
};

// 根据课程ID获取章节列表
const getChaptersByCourse = (courseId) => {
    return chapterList.value.filter((chapter) => chapter.courseId === courseId);
};

// 根据章节ID获取知识点列表
const getKnowledgeByChapter = (chapterId) => {
    return knowledgeList.value.filter(
        (knowledge) => knowledge.chapterId === chapterId
    );
};

// 根据课程ID获取知识点列表
const getKnowledgeByCourse = (courseId) => {
    const chapterIds = getChaptersByCourse(courseId).map(
        (chapter) => chapter.id
    );
    return knowledgeList.value.filter((knowledge) =>
        chapterIds.includes(knowledge.chapterId)
    );
};

// 获取课程名称
const getCourseName = (courseId) => {
    const course = courseList.value.find((item) => item.id === courseId);
    return course ? course.name : "未知课程";
};

// 获取章节名称
const getChapterName = (chapterId) => {
    const chapter = chapterList.value.find((item) => item.id === chapterId);
    return chapter ? chapter.name : "未知章节";
};

// 获取总章节数
const getTotalChapters = () => {
    return chapterList.value.length;
};

// 筛选章节（根据选中的课程）
const filteredChapters = computed(() => {
    if (selectedCourseId.value === "all") {
        return chapterList.value;
    }
    return getChaptersByCourse(selectedCourseId.value);
});

// 按筛选条件过滤知识点
const filteredKnowledgeList = computed(() => {
    let filtered = [...knowledgeList.value];

    // 按课程筛选
    if (selectedCourseId.value !== "all") {
        const chapterIds = getChaptersByCourse(selectedCourseId.value).map(
            (chapter) => chapter.id
        );
        filtered = filtered.filter((knowledge) =>
            chapterIds.includes(knowledge.chapterId)
        );
    }

    // 按章节筛选
    if (selectedChapterId.value !== "all") {
        filtered = filtered.filter(
            (knowledge) => knowledge.chapterId === selectedChapterId.value
        );
    }

    // 按掌握程度筛选
    if (selectedLevel.value !== "all") {
        filtered = filtered.filter((knowledge) => {
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
    }

    // 按ID排序
    return filtered.sort((a, b) => a.id - b.id);
});

// 更新筛选条件并重新渲染图表
const updateFilters = () => {
    nextTick(() => {
        updateMasteryChart();
    });
};

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

// 更新掌握度图表
const updateMasteryChart = () => {
    const masteryCtx = document.getElementById("masteryChart");
    if (!masteryCtx) return;

    if (masteryChartInstance) {
        masteryChartInstance.destroy();
    }

    const labels = filteredKnowledgeList.value.map(
        (k) =>
            `${getCourseName(k.courseId)}-${getChapterName(
                k.chapterId
            )}-${k.name.substring(0, 8)}`
    );
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
                x: {
                    title: { display: true, text: "知识点" },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                    },
                },
            },
        },
    });
};

// 渲染分类掌握度图表
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

/* 根容器 - 确保页面高度足够，避免内容溢出 */
.knowledge-page {
    width: 100%;
    min-height: 100vh;
    padding: 20px;
    background-color: #f4f7f9;
    overflow-x: hidden; /* 隐藏横向滚动 */
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

/* 主内容区 - 修复布局溢出 */
.main-content {
    width: 100%;
    max-width: 100%;
    margin: 0 auto;
    padding-bottom: 40px; /* 底部留白 */
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

/* 仪表盘布局 - 修复网格布局溢出 */
.dashboard {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    width: 100%;
    max-width: 100%;
    margin: 0 auto;
}

/* 卡片样式 - 确保高度自适应，不溢出 */
.card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 10px;
    padding: 22px;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(240, 249, 255, 0.8);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
    min-height: 200px; /* 最小高度，避免内容过少时塌陷 */
    height: 100%; /* 高度自适应父容器 */
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

/* 统计项样式 */
.stats {
    display: flex;
    justify-content: space-around;
    height: calc(100% - 60px); /* 减去标题高度，自适应 */
    align-items: center;
}

.stat-item {
    text-align: center;
}

.stat-value {
    display: block;
    font-size: 24px;
    font-weight: bold;
    background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.stat-label {
    color: #7f8c8d;
    font-size: 14px;
}

/* 内容区域 - 跨列显示，修复宽度 */
.content-section {
    grid-column: 1 / -1;
    background: #ffffff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
    margin-bottom: 20px;
    width: 100%;
    max-width: 100%;
    overflow: hidden; /* 隐藏内部溢出 */
}

.content-section h3 {
    color: #1e3a8a;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

/* 筛选控件样式 - 修复布局 */
.filter-controls {
    display: flex;
    gap: 15px;
    flex-wrap: wrap; /* 自适应换行 */
    margin-bottom: 20px;
    align-items: center;
    padding: 10px;
    background: #f8fafc;
    border-radius: 8px;
}

.filter-control {
    display: flex;
    align-items: center;
    gap: 8px;
}

.filter-label {
    font-size: 14px;
    color: #34495e;
    font-weight: 500;
}

.mastery-select {
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 14px;
    color: #34495e;
    background: #ffffff;
    cursor: pointer;
    transition: border-color 0.3s ease;
    min-width: 150px;
}

.mastery-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* 图表+表格容器 - 修复高度和溢出 */
.chart-table-wrapper {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    width: 100%;
    min-height: 400px; /* 最小高度，确保图表显示完整 */
}

/* 图表容器 - 修复高度不足问题 */
.chart-container {
    flex: 1;
    min-width: 300px;
    position: relative;
    display: flex; /* 修复居中 */
    align-items: center;
    justify-content: center;
    height: 400px; /* 固定高度，确保图表显示完整 */
    min-height: 350px;
    background: #f8fafc;
    border-radius: 8px;
    padding: 10px;
}

/* 表格容器 - 修复横向滚动 */
.chart-table {
    flex: 1;
    min-width: 300px;
    overflow-x: auto;
    max-height: 400px; /* 固定高度，避免表格过高 */
    overflow-y: auto; /* 纵向滚动 */
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* 表格样式 */
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 14px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

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
    position: sticky; /* 表头固定 */
    top: 0;
    z-index: 10;
}

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

table:hover th:after {
    transform: scaleX(1);
}

td {
    padding: 12px 15px;
    text-align: left;
    color: #475569;
    border-bottom: 1px solid #f1f5f9;
    transition: all 0.2s ease;
}

tbody tr:nth-child(even) {
    background-color: #f8fafc;
}

tbody tr:nth-child(odd) {
    background-color: #ffffff;
}

tbody tr:hover {
    background-color: #eff6ff;
    transform: translateX(4px);
}

tbody tr:hover td {
    color: #2563eb;
    font-weight: 500;
}

td:first-child {
    font-weight: 600;
    color: #1e3a8a;
}

.no-data {
    text-align: center;
    color: #94a3b8;
    padding: 30px;
    font-style: italic;
    background-color: #f8fafc;
    border-bottom: none;
}

tbody tr:last-child td {
    border-bottom: none;
}

td:nth-child(3) {
    font-weight: 600;
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
    border-radius: 8px;
    overflow: hidden;
}

.progress {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 8px;
}

/* 知识点进度条 */
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
    border-radius: 4px;
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

/* 掌握度等级样式 */
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
    background: linear-gradient(90deg, #d35400 0%, #f39c12 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 15px;
    font-weight: 600;
}

.level-mastered {
    background: linear-gradient(90deg, #f39c12 0%, #f1c40f 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 15px;
    font-weight: 600;
}

.level-proficient {
    background: linear-gradient(90deg, #2ecc71 0%, #81c784 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 15px;
    font-weight: 600;
}

.level-expert {
    background: linear-gradient(90deg, #1e7e34 0%, #27ae60 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 15px;
    font-weight: 600;
}

/* 课程结构容器 - 修复层级显示 */
.course-structure-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.course-card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
    overflow: hidden;
    transition: all 0.3s ease;
}

.course-card:hover {
    box-shadow: 0 5px 15px rgba(59, 130, 246, 0.1);
}

.course-header {
    padding: 15px 20px;
    background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
}

.expand-icon {
    font-size: 14px;
    color: #3b82f6;
    transition: transform 0.3s ease;
}

.course-info h4 {
    font-size: 16px;
    color: #1e3a8a;
    margin-bottom: 5px;
}

.course-meta {
    display: flex;
    gap: 15px;
    font-size: 12px;
    color: #64748b;
}

.mastery-badge {
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 12px;
    color: white;
}

.chapters-container {
    padding: 10px 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.chapter-card {
    margin-left: 20px;
    background: #f8fafc;
    border-radius: 6px;
    overflow: hidden;
}

.chapter-header {
    padding: 12px 15px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
}

.chapter-info h5 {
    font-size: 14px;
    color: #334155;
    margin-bottom: 3px;
}

.chapter-meta {
    display: flex;
    gap: 10px;
    font-size: 11px;
    color: #64748b;
}

/* 知识点列表 - 修复溢出 */
.knowledge-list {
    padding: 10px 0;
    margin-left: 20px;
    display: flex;
    flex-direction: column;
    gap: 5px;
    max-height: 300px; /* 最大高度，超出滚动 */
    overflow-y: auto;
}

.knowledge-item {
    padding: 10px 15px;
    background: #ffffff;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    border-left: 3px solid transparent;
}

.knowledge-item:hover {
    background: #eff6ff;
    border-left-color: #3b82f6;
    transform: translateX(3px);
}

.knowledge-icon {
    font-size: 16px;
    width: 24px;
    text-align: center;
}

.knowledge-content {
    flex: 1;
}

.knowledge-name {
    font-size: 14px;
    color: #1e3a8a;
    font-weight: 500;
    margin-bottom: 3px;
}

.knowledge-footer {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
}

.knowledge-category {
    color: #64748b;
}

/* 弹窗样式 - 修复显示不全 */
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
    padding: 20px; /* 留白，避免边缘溢出 */
}

.modal-content {
    background-color: #ffffff;
    border-radius: 10px;
    width: 100%;
    max-width: 800px; /* 最大宽度 */
    max-height: 90vh; /* 最大高度，避免超出视口 */
    overflow-y: auto; /* 内容溢出滚动 */
    padding: 30px;
    position: relative;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.close {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 24px;
    cursor: pointer;
    color: #64748b;
    transition: color 0.3s ease;
}

.close:hover {
    color: #e74c3c;
}

.knowledge-path {
    font-size: 12px;
    color: #64748b;
    margin: 10px 0 20px;
    font-style: italic;
}

.knowledge-description {
    line-height: 1.6;
    color: #34495e;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e2e8f0;
}

.knowledge-detail-chart {
    height: 300px; /* 固定高度 */
    margin-bottom: 20px;
}

.knowledge-stats {
    display: flex;
    justify-content: space-around;
    padding-top: 20px;
    border-top: 1px solid #e2e8f0;
}

/* 返回首页按钮 */
.back-to-home {
    position: fixed;
    bottom: 30px;
    right: 30px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: linear-gradient(90deg, #3498db, #2980b9);
    color: white;
    border-radius: 30px;
    text-decoration: none;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    transition: all 0.3s ease;
    z-index: 999;
}

.back-to-home:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
    background: linear-gradient(90deg, #2980b9, #3498db);
}

.back-to-home .icon {
    font-size: 18px;
}

/* 响应式适配 - 修复小屏幕显示 */
@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr; /* 小屏幕单列 */
    }

    .chart-table-wrapper {
        flex-direction: column; /* 图表和表格上下排列 */
    }

    .chart-container {
        height: 300px; /* 减小图表高度 */
    }

    .filter-controls {
        flex-direction: column; /* 筛选控件垂直排列 */
        align-items: flex-start;
    }

    .course-meta,
    .chapter-meta {
        flex-direction: column; /* 元信息垂直排列 */
        gap: 5px;
    }

    .modal-content {
        padding: 20px;
        max-width: 95%; /* 占满屏幕宽度 */
    }
}

/* 修复Chart.js canvas高度问题 */
canvas {
    width: 100% !important;
    height: 100% !important;
}
</style>
