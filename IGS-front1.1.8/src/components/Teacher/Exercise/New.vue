<template>
    <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>

    <div class="exercise-bank-container">
        <div class="page-header">
            <h2>题库管理</h2>
            <p>查看和管理系统中的所有习题资源</p>
        </div>

        <!-- 筛选条件卡片 - 使用统一的card样式 -->
        <div class="card filters-container">
            <!-- 筛选条件内容保持不变 -->
            <h3>筛选条件</h3>
            <div class="filter-content">
                <div class="filter-group">
                    <div class="filter-item">
                        <label for="subject-select">学科:</label>
                        <select
                            id="subject-select"
                            v-model="selectedSubject"
                            class="input-field"
                        >
                            <option value="">全部学科</option>
                            <option
                                v-for="subject in subjects"
                                :key="subject.id"
                                :value="subject.id"
                            >
                                {{ subject.name }}
                            </option>
                        </select>
                    </div>

                    <div class="filter-item">
                        <label for="difficulty-select">难度:</label>
                        <select
                            id="difficulty-select"
                            v-model="selectedDifficulty"
                            class="input-field"
                        >
                            <option value="">全部难度</option>
                            <option value="easy">简单</option>
                            <option value="medium">中等</option>
                            <option value="hard">困难</option>
                        </select>
                    </div>

                    <div class="filter-item">
                        <label for="exercise-type">题型:</label>
                        <select
                            id="exercise-type"
                            v-model="selectedType"
                            class="input-field"
                        >
                            <option value="">全部题型</option>
                            <option value="single-choice">单选题</option>
                            <option value="multiple-choice">多选题</option>
                            <option value="true-false">判断题</option>
                            <option value="blank">填空题</option>
                            <option value="essay">简答题</option>
                        </select>
                    </div>
                </div>

                <div class="search-container">
                    <input
                        type="text"
                        placeholder="搜索习题..."
                        v-model="searchKeyword"
                        @input="debounceSearch"
                        class="input-field"
                    />
                    <button class="btn btn-search" @click="searchExercises">
                        搜索
                    </button>
                </div>
            </div>
        </div>

        <!-- 习题列表和我的题库使用网格布局 -->
        <div class="exercise-lists-container">
            <!-- 公共题库列表卡片 - 不可滚动 -->
            <div class="card exercise-list-container">
                <h3>公共题库</h3>
                <div class="table-responsive">
                    <table class="exercise-table">
                        <thead>
                            <tr>
                                <th>习题ID</th>
                                <th>题目</th>
                                <th>学科</th>
                                <th>难度</th>
                                <th>题型</th>
                                <th>创建者</th>
                                <th>创建时间</th>
                                <th>使用次数</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="loading">
                                <td colspan="9" class="loading-message">
                                    正在加载数据...
                                </td>
                            </tr>
                            <tr
                                v-else-if="
                                    paginatedPublicExercises.length === 0
                                "
                            >
                                <td colspan="9" class="empty-message">
                                    没有找到相关习题
                                </td>
                            </tr>
                            <tr
                                v-else
                                v-for="exercise in paginatedPublicExercises"
                                :key="exercise.id"
                            >
                                <td>{{ exercise.id }}</td>
                                <td class="exercise-title">
                                    {{ truncateText(exercise.title, 30) }}
                                </td>
                                <td>
                                    {{ getSubjectName(exercise.subjectId) }}
                                </td>
                                <td>
                                    {{ getDifficultyText(exercise.difficulty) }}
                                </td>
                                <td>{{ getTypeText(exercise.type) }}</td>
                                <td>{{ exercise.creator }}</td>
                                <td>{{ formatDate(exercise.createTime) }}</td>
                                <td>{{ exercise.useCount }}</td>
                                <td>
                                    <button
                                        class="btn btn-view"
                                        @click="viewExercise(exercise.id)"
                                    >
                                        查看
                                    </button>
                                    <button
                                        class="btn btn-add"
                                        @click="
                                            addExerciseToMyList(exercise.id)
                                        "
                                        :disabled="isInMyList(exercise.id)"
                                    >
                                        {{
                                            isInMyList(exercise.id)
                                                ? "已添加"
                                                : "添加到我的习题"
                                        }}
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="pagination-container" v-if="publicTotalPages > 1">
                    <button
                        class="pagination-btn"
                        :disabled="publicCurrentPage === 1"
                        @click="changePublicPage(publicCurrentPage - 1)"
                    >
                        上一页
                    </button>
                    <span class="pagination-info">
                        {{ publicCurrentPage }} / {{ publicTotalPages }}
                    </span>
                    <button
                        class="pagination-btn"
                        :disabled="publicCurrentPage === publicTotalPages"
                        @click="changePublicPage(publicCurrentPage + 1)"
                    >
                        下一页
                    </button>
                </div>
            </div>

            <!-- 我的题库列表卡片 - 改为和公共题库一致的不可滚动样式 -->
            <div class="card exercise-list-container">
                <h3>我的题库</h3>
                <div class="table-responsive">
                    <table class="exercise-table">
                        <thead>
                            <tr>
                                <th>习题ID</th>
                                <th>题目</th>
                                <th>学科</th>
                                <th>难度</th>
                                <th>题型</th>
                                <th>添加时间</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="myExercises.length === 0">
                                <td colspan="7" class="empty-message">
                                    我的题库中暂无习题，可从公共题库添加
                                </td>
                            </tr>
                            <tr v-else-if="paginatedMyExercises.length === 0">
                                <td colspan="7" class="empty-message">
                                    当前页没有习题
                                </td>
                            </tr>
                            <tr
                                v-else
                                v-for="exercise in paginatedMyExercises"
                                :key="exercise.id"
                            >
                                <td>{{ exercise.id }}</td>
                                <td class="exercise-title">
                                    {{ truncateText(exercise.title, 30) }}
                                </td>
                                <td>
                                    {{ getSubjectName(exercise.subjectId) }}
                                </td>
                                <td>
                                    {{ getDifficultyText(exercise.difficulty) }}
                                </td>
                                <td>{{ getTypeText(exercise.type) }}</td>
                                <td>{{ formatDate(exercise.addTime) }}</td>
                                <td>
                                    <button
                                        class="btn btn-view"
                                        @click="viewExercise(exercise.id)"
                                    >
                                        查看
                                    </button>
                                    <button
                                        class="btn btn-remove"
                                        @click="removeFromMyList(exercise.id)"
                                    >
                                        移除
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- 我的题库分页控件 -->
                <div class="pagination-container" v-if="myTotalPages > 1">
                    <button
                        class="pagination-btn"
                        :disabled="myCurrentPage === 1"
                        @click="changeMyPage(myCurrentPage - 1)"
                    >
                        上一页
                    </button>
                    <span class="pagination-info">
                        {{ myCurrentPage }} / {{ myTotalPages }}
                    </span>
                    <button
                        class="pagination-btn"
                        :disabled="myCurrentPage === myTotalPages"
                        @click="changeMyPage(myCurrentPage + 1)"
                    >
                        下一页
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 学科数据
const subjects = ref([
    { id: 1, name: "编程基础" },
    { id: 2, name: "数据结构" },
    { id: 3, name: "算法设计" },
    { id: 4, name: "前端开发" },
    { id: 5, name: "后端开发" },
]);

// 筛选条件
const selectedSubject = ref("");
const selectedDifficulty = ref("");
const selectedType = ref("");
const searchKeyword = ref("");

// 分页配置 - 每页10条
const pageSize = ref(10);

// 公共题库分页数据
const publicCurrentPage = ref(1);
const publicTotalPages = ref(1);

// 我的题库分页数据
const myCurrentPage = ref(1);
const myTotalPages = ref(1);

// 习题数据
const allExercises = ref([]); // 存储所有公共题库习题
const myExercises = ref([]); // 存储我的题库习题

// 加载中状态
const loading = ref(false);

// 计算属性：根据筛选条件过滤公共题库习题
const filteredExercises = computed(() => {
    return allExercises.value.filter((exercise) => {
        // 过滤已添加到我的题库的习题
        if (myExercises.value.some((item) => item.id === exercise.id)) {
            return false;
        }

        // 学科筛选
        if (
            selectedSubject.value &&
            exercise.subjectId !== selectedSubject.value
        ) {
            return false;
        }

        // 难度筛选
        if (
            selectedDifficulty.value &&
            exercise.difficulty !== selectedDifficulty.value
        ) {
            return false;
        }

        // 题型筛选
        if (selectedType.value) {
            // 转换题型字符串为数字以便比较
            const typeMap = {
                "single-choice": 0,
                "multiple-choice": 1,
                "true-false": 2,
                essay: 3,
            };
            if (exercise.type !== typeMap[selectedType.value]) {
                return false;
            }
        }

        // 关键词搜索
        if (
            searchKeyword.value &&
            !exercise.title.includes(searchKeyword.value)
        ) {
            return false;
        }

        return true;
    });
});

// 计算属性：公共题库分页数据
const paginatedPublicExercises = computed(() => {
    const startIndex = (publicCurrentPage.value - 1) * pageSize.value;
    const endIndex = startIndex + pageSize.value;
    return filteredExercises.value.slice(startIndex, endIndex);
});

// 计算属性：我的题库分页数据
const paginatedMyExercises = computed(() => {
    const startIndex = (myCurrentPage.value - 1) * pageSize.value;
    const endIndex = startIndex + pageSize.value;
    return myExercises.value.slice(startIndex, endIndex);
});

// 检查习题是否已在我的题库中
const isInMyList = (exerciseId) => {
    return myExercises.value.some((item) => item.id === exerciseId);
};

// 格式化日期
const formatDate = (dateString) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
    });
};

// 获取学科名称
const getSubjectName = (subjectId) => {
    const subject = subjects.value.find((s) => s.id === subjectId);
    return subject ? subject.name : "-";
};

// 获取难度文本
const getDifficultyText = (difficulty) => {
    switch (difficulty) {
        case "easy":
            return "简单";
        case "medium":
            return "中等";
        case "hard":
            return "困难";
        default:
            return "-";
    }
};

// 获取题型文本
const getTypeText = (type) => {
    switch (type) {
        case 0:
            return "单选题";
        case 1:
            return "多选题";
        case 2:
            return "判断题";
        case 3:
            return "简答题";
        default:
            return "-";
    }
};

// 截断文本
const truncateText = (text, length) => {
    if (!text || text.length <= length) return text;
    return text.substring(0, length) + "...";
};

// 防抖搜索
const debounceSearch = () => {
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
        searchExercises();
    }, 500);
};

// 获取习题数据
const fetchExercises = async () => {
    loading.value = true;
    try {
        const response = await fetch(
            "http://localhost:8000/question/question/"
        );
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        const data = await response.json();
        allExercises.value = data.data;

        // 初始化公共题库分页
        publicTotalPages.value = Math.ceil(
            filteredExercises.value.length / pageSize.value
        );

        // 从本地存储加载我的题库（实际应用中应该从API加载）
        const savedMyExercises = localStorage.getItem("myExercises");
        if (savedMyExercises) {
            myExercises.value = JSON.parse(savedMyExercises);
            // 初始化我的题库分页
            myTotalPages.value = Math.ceil(
                myExercises.value.length / pageSize.value
            );
        }
    } catch (error) {
        console.error("Error fetching exercises:", error);
    } finally {
        loading.value = false;
    }
};

// 搜索习题
const searchExercises = () => {
    // 重置公共题库到第一页
    publicCurrentPage.value = 1;
    publicTotalPages.value = Math.ceil(
        filteredExercises.value.length / pageSize.value
    );
};

// 改变公共题库页码
const changePublicPage = (page) => {
    if (page >= 1 && page <= publicTotalPages.value) {
        publicCurrentPage.value = page;
        // 移除滚动逻辑，因为公共题库不可滚动
    }
};

// 改变我的题库页码
const changeMyPage = (page) => {
    if (page >= 1 && page <= myTotalPages.value) {
        myCurrentPage.value = page;
        // 移除滚动逻辑，保持和公共题库一致
    }
};

// 查看习题
const viewExercise = (exerciseId) => {
    router.push(`/teacher/exercise/view/${exerciseId}`);
};

// 添加到我的习题
const addExerciseToMyList = (exerciseId) => {
    // 查找要添加的习题
    const exerciseToAdd = allExercises.value.find(
        (item) => item.id === exerciseId
    );
    if (exerciseToAdd && !isInMyList(exerciseId)) {
        // 添加添加时间
        const exerciseWithAddTime = {
            ...exerciseToAdd,
            addTime: new Date().toISOString(),
        };

        // 添加到我的题库
        myExercises.value = [...myExercises.value, exerciseWithAddTime];

        // 更新我的题库分页
        myTotalPages.value = Math.ceil(
            myExercises.value.length / pageSize.value
        );

        // 保存到本地存储（实际应用中应该调用API保存到服务器）
        localStorage.setItem("myExercises", JSON.stringify(myExercises.value));

        // 如果添加后公共题库数据变化，更新分页
        publicTotalPages.value = Math.ceil(
            filteredExercises.value.length / pageSize.value
        );
    }
};

// 从我的题库移除
const removeFromMyList = (exerciseId) => {
    if (confirm("确定要从我的题库中移除这道习题吗？")) {
        const prevLength = myExercises.value.length;
        myExercises.value = myExercises.value.filter(
            (item) => item.id !== exerciseId
        );

        // 更新我的题库分页
        myTotalPages.value = Math.ceil(
            myExercises.value.length / pageSize.value
        );

        // 如果删除后当前页超出范围，跳转到最后一页
        if (
            myCurrentPage.value > myTotalPages.value &&
            myTotalPages.value > 0
        ) {
            myCurrentPage.value = myTotalPages.value;
        }

        // 更新本地存储
        localStorage.setItem("myExercises", JSON.stringify(myExercises.value));

        // 如果移除后公共题库数据变化，更新分页
        publicTotalPages.value = Math.ceil(
            filteredExercises.value.length / pageSize.value
        );
    }
};

// 组件挂载时执行
onMounted(() => {
    fetchExercises();
});
</script>

<style scoped>
/* 整体容器样式 */
.exercise-bank-container {
    width: 100%;
    padding: 0;
    margin: 0;
}

/* 新增：两个列表并排显示 */
.exercise-lists-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 25px;
}

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

/* 卡片样式 - 应用统一设计 */
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

/* 筛选条件容器 */
.filters-container {
    margin-bottom: 30px;
}

.filter-content {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: center;
    transition: transform 0.3s ease;
}

.card:hover .filter-content {
    transform: translateX(3px);
}

.filter-group {
    display: flex;
    gap: 20px;
    flex: 1;
    flex-wrap: wrap;
}

.filter-item {
    display: flex;
    flex-direction: column;
    min-width: 150px;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .filter-item {
    transform: translateX(3px);
    opacity: 1;
}

.card:hover .filter-item:nth-child(2) {
    transition-delay: 0.05s;
}
.card:hover .filter-item:nth-child(3) {
    transition-delay: 0.1s;
}

.filter-item label {
    font-size: 14px;
    color: #555;
    margin-bottom: 8px;
    font-weight: 500;
}

/* 搜索容器 */
.search-container {
    display: flex;
    align-items: center;
    gap: 10px;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .search-container {
    transform: translateX(3px);
    opacity: 1;
}

/* 输入框样式统一 */
.input-field {
    padding: 12px 15px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.3s ease;
    min-width: 200px;
}

.input-field:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

/* 按钮样式统一 */
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

/* 按钮间隙调整 */
.btn-view {
    margin-right: 10px;
}

.btn-search,
.btn-view {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-search:hover,
.btn-view:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
    background: linear-gradient(135deg, #64b5f6, #2196f3);
}

.btn-add {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: white;
}

.btn-add:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(46, 204, 113, 0.4);
    background: linear-gradient(135deg, #58d68d, #27ae60);
}

.btn-add:disabled {
    background: #cccccc;
    cursor: not-allowed;
    opacity: 0.7;
}

/* 新增：移除按钮样式 */
.btn-remove {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
}

.btn-remove:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(231, 76, 60, 0.4);
    background: linear-gradient(135deg, #ec7063, #c0392b);
}

/* 公共题库和我的题库容器 - 统一为不可滚动样式 */
.exercise-list-container {
    margin-bottom: 25px;
    /* 移除最大高度和滚动 */
    max-height: none;
    overflow: visible;
}

/* 表格样式 */
.table-responsive {
    overflow-x: auto;
    margin-top: 20px;
}

/* 公共题库和我的题库表格容器 - 统一为不可滚动 */
.exercise-list-container .table-responsive {
    max-height: none;
    overflow: visible;
}

.exercise-table {
    width: 100%;
    border-collapse: collapse;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .exercise-table {
    transform: translateX(3px);
    opacity: 1;
}

.exercise-table th {
    background-color: #f8f9fa;
    padding: 15px;
    text-align: left;
    font-weight: 600;
    color: #333;
    border-bottom: 2px solid #e9ecef;
    font-size: 14px;
    /* 统一移除粘性表头 */
    position: static;
    z-index: auto;
}

.exercise-table td {
    padding: 15px;
    border-bottom: 1px solid #e9ecef;
    color: #666;
    font-size: 14px;
}

.exercise-table tr:last-child td {
    border-bottom: none;
}

.exercise-table tr:hover {
    background-color: #f8f9fa;
    transition: background-color 0.3s ease;
}

.exercise-title {
    max-width: 200px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 分页样式 */
.pagination-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #e9ecef;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .pagination-container {
    transform: translateX(3px);
    opacity: 1;
}

.pagination-btn {
    padding: 10px 16px;
    border: 1px solid #e0e0e0;
    background-color: white;
    color: #333;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
}

.pagination-btn:hover:not(:disabled) {
    background-color: #3498db;
    color: white;
    border-color: #3498db;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination-info {
    color: #666;
    font-size: 14px;
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

/* 响应式设计 */
@media (max-width: 1200px) {
    .filter-content {
        justify-content: center;
    }

    .filter-item {
        flex: 1;
        min-width: auto;
        max-width: 300px;
    }

    .exercise-lists-container {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .card {
        padding: 20px;
    }

    .filter-content {
        flex-direction: column;
        align-items: stretch;
    }

    .filter-item {
        min-width: auto;
        max-width: none;
    }

    .btn {
        width: 100%;
        margin-bottom: 10px;
    }

    .btn-view {
        margin-right: 0;
    }
}
</style>