<template>
    <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>

    <div class="existing-exercise-container">
        <div class="page-header">
            <h2>已设计习题</h2>
            <p>查看和管理已创建的习题</p>
        </div>

        <!-- 筛选条件卡片 - 使用统一的card样式 -->
        <div class="card filters-container">
            <h3>筛选条件</h3>
            <div class="filter-content">
                <div class="filter-group">
                    <div class="filter-item">
                        <label for="subject-select">学科:</label>
                        <select
                            id="subject-select"
                            v-model="selectedSubject"
                            class="input-field"
                            @change="onFiltersChange"
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
                            @change="onFiltersChange"
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
                            @change="onFiltersChange"
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

        <!-- 习题列表卡片 - 使用统一的card样式 -->
        <div class="card exercise-list-container">
            <h3>习题列表</h3>
            <div class="table-responsive">
                <table class="exercise-table">
                    <thead>
                        <tr>
                            <th>习题ID</th>
                            <th>题目</th>
                            <th>学科</th>
                            <th>难度</th>
                            <th>题型</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="exercise in displayExercises" :key="exercise.id">
                            <td>{{ exercise.exerciseId || exercise.id }}</td>
                            <td class="exercise-title">
                                {{ truncateText(exercise.title, 30) }}
                            </td>
                            <td>{{ getSubjectName(exercise.subjectId) }}</td>
                            <td>
                                {{ getDifficultyText(exercise.difficulty) }}
                            </td>
                            <td>{{ getTypeText(exercise.type) }}</td>
                            <td>{{ formatDate(exercise.createTime) }}</td>
                            <td>
                                <button
                                    class="btn btn-view"
                                    @click="viewExercise(exercise.id)"
                                >
                                    查看
                                </button>
                                <button
                                    class="btn btn-edit"
                                    @click="editExercise(exercise.id)"
                                >
                                    编辑
                                </button>
                                <button
                                    class="btn btn-delete"
                                    @click="deleteExercise(exercise.id)"
                                >
                                    删除
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="pagination-container" v-if="totalPages > 1">
                <button
                    class="pagination-btn"
                    :disabled="currentPage === 1"
                    @click="changePage(currentPage - 1)"
                >
                    上一页
                </button>
                <span class="pagination-info">
                    {{ currentPage }} / {{ totalPages }}
                </span>
                <button
                    class="pagination-btn"
                    :disabled="currentPage === totalPages"
                    @click="changePage(currentPage + 1)"
                >
                    下一页
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import request from "../../../utils/request";

const router = useRouter();

const isLoggedIn = ref(
    !!(window.localStorage && window.localStorage.getItem("token"))
);

const handleAuthFailure = async (e) => {
    console.error("请求失败", e);
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
};

// 学科数据
const subjects = ref([]);

// 筛选条件
const selectedSubject = ref("");
const selectedDifficulty = ref("");
const selectedType = ref("");
const searchKeyword = ref("");

// 分页数据
const currentPage = ref(1);
const pageSize = ref(10);
const totalPages = ref(1);

// 习题数据
const exercises = ref([]);

const displayExercises = computed(() => {
    const list = Array.isArray(exercises.value) ? exercises.value : [];
    const start = (currentPage.value - 1) * pageSize.value;
    return list.slice(start, start + pageSize.value);
});

const normalizeExercise = (item) => {
    if (!item || typeof item !== "object") return {};
    return {
        ...item,
        id: item.id,
        exerciseId: item.exerciseId || item.exercise_id || item.exerciseId,
        title: item.title || item.name || "",
        createTime: item.createTime || item.created_at || item.createdAt || "",
        subjectId: item.subjectId,
        difficulty: item.difficulty,
        type: item.type,
    };
};

const applyOptionalClientFilters = (list) => {
    let out = Array.isArray(list) ? list : [];

    if (selectedSubject.value) {
        out = out.filter((x) => {
            if (x.subjectId === undefined || x.subjectId === null || x.subjectId === "") {
                return true;
            }
            return String(x.subjectId) === String(selectedSubject.value);
        });
    }
    if (selectedDifficulty.value) {
        out = out.filter((x) => {
            if (!x.difficulty) return true;
            return String(x.difficulty) === String(selectedDifficulty.value);
        });
    }
    if (selectedType.value) {
        out = out.filter((x) => {
            if (!x.type) return true;
            return String(x.type) === String(selectedType.value);
        });
    }
    return out;
};

const fetchSubjects = async () => {
    const resp = await request.get("/question/subjects/");
    const list = resp?.data;
    subjects.value = Array.isArray(list) ? list : [];
};

const fetchExercises = async () => {
    const resp = await request.get("/question/", {
        params: {
            keyword: searchKeyword.value || "",
            subjectId: selectedSubject.value || "",
            difficulty: selectedDifficulty.value || "",
            type: selectedType.value || "",
        },
    });

    const list = resp?.data?.data;
    const normalized = (Array.isArray(list) ? list : []).map(normalizeExercise);
    exercises.value = applyOptionalClientFilters(normalized);
    totalPages.value = Math.max(1, Math.ceil(exercises.value.length / pageSize.value));
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
        case "single-choice":
            return "单选题";
        case "multiple-choice":
            return "多选题";
        case "true-false":
            return "判断题";
        case "blank":
            return "填空题";
        case "essay":
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

// 搜索习题
const searchExercises = async () => {
    currentPage.value = 1;
    try {
        await fetchExercises();
    } catch (e) {
        await handleAuthFailure(e);
    }
};

const onFiltersChange = async () => {
    await searchExercises();
};

// 改变页码
const changePage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
    }
};

// 查看习题
const viewExercise = (exerciseId) => {
    router.push(`/teacher/exercise/view/${exerciseId}`);
};

// 编辑习题
const editExercise = (exerciseId) => {
    router.push(`/teacher/exercise/edit/${exerciseId}`);
};

// 删除习题
const deleteExercise = async (exerciseId) => {
    if (!confirm("确定要删除这道习题吗？")) return;
    try {
        await request.delete(`/question/${exerciseId}/`);
        exercises.value = exercises.value.filter((exercise) => exercise.id !== exerciseId);
        totalPages.value = Math.max(1, Math.ceil(exercises.value.length / pageSize.value));
        if (currentPage.value > totalPages.value) {
            currentPage.value = totalPages.value;
        }
    } catch (e) {
        await handleAuthFailure(e);
    }
};

// 组件挂载时执行
onMounted(async () => {
    if (!isLoggedIn.value) {
        try {
            router.push("/login");
        } catch (err) {
            console.error("路由跳转失败", err);
        }
        return;
    }

    try {
        await fetchSubjects();
        await fetchExercises();
    } catch (e) {
        await handleAuthFailure(e);
    }
});
</script>

<style scoped>
/* 整体容器样式 */
.existing-exercise-container {
    width: 100%;
    padding: 0;
    margin: 0;
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

.btn-edit {
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

.btn-edit {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: white;
}

.btn-edit:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(46, 204, 113, 0.4);
    background: linear-gradient(135deg, #58d68d, #27ae60);
}

.btn-delete {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
}

.btn-delete:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(231, 76, 60, 0.4);
    background: linear-gradient(135deg, #ec7063, #c0392b);
}

/* 习题列表容器特有样式 */
.exercise-list-container {
    margin-bottom: 25px;
}

/* 表格样式 */
.table-responsive {
    overflow-x: auto;
    margin-top: 20px;
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
    max-width: 300px;
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
        margin-right: 0 !important;
    }

    .exercise-table td {
        padding: 10px;
        font-size: 13px;
    }

    .exercise-list-container {
        padding: 20px;
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
