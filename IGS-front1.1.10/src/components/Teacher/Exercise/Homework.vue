<template>
    <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>

    <div class="homework-container">
        <div class="page-header">
            <h2>发布作业</h2>
            <p>创建并发布新的作业任务</p>
        </div>

        <!-- 作业基本信息卡片 -->
        <div class="card homework-info-card">
            <h3>作业基本信息</h3>
            <div class="form-content">
                <div class="form-group">
                    <div class="form-item">
                        <label for="homework-title">作业标题:</label>
                        <input
                            type="text"
                            id="homework-title"
                            v-model="homework.title"
                            placeholder="请输入作业标题"
                            class="input-field"
                            required
                        />
                    </div>

                    <div class="form-item">
                        <label for="homework-type">作业类型:</label>
                        <select
                            id="homework-type"
                            v-model="homework.type"
                            class="input-field"
                            required
                        >
                            <option value="">请选择作业类型</option>
                            <option value="quiz">小测</option>
                            <option value="homework">作业</option>
                            <option value="exercise">练习</option>
                            <option value="assignment">任务</option>
                            <option value="exam">考试</option>
                        </select>
                    </div>

                    <div class="form-item">
                        <label for="homework-subject">所属学科:</label>
                        <select
                            id="homework-subject"
                            v-model="homework.subjectId"
                            class="input-field"
                            @change="loadSubjectExercises"
                            required
                        >
                            <option value="">请选择学科</option>
                            <option
                                v-for="subject in subjects"
                                :key="subject.id"
                                :value="subject.id"
                            >
                                {{ subject.name }}
                            </option>
                        </select>
                    </div>

                    <!-- 班级选择改为按钮触发弹窗模式 -->
                    <div class="form-item">
                        <label>选择班级:</label>
                        <div class="class-selection-wrapper">
                            <button
                                type="button"
                                class="input-field student-selector-btn"
                                @click="showClassSelection"
                            >
                                {{ getSelectedClassesText() }}
                            </button>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <div class="form-item">
                        <label>选择学生:</label>
                        <div class="student-selection-wrapper">
                            <button
                                type="button"
                                class="input-field student-selector-btn"
                                @click="showStudentSelection"
                            >
                                {{ getSelectedStudentsText() }}
                            </button>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <div class="form-item">
                        <label for="homework-difficulty">作业难度:</label>
                        <select
                            id="homework-difficulty"
                            v-model="homework.difficulty"
                            class="input-field"
                            required
                        >
                            <option value="">请选择难度</option>
                            <option value="easy">简单</option>
                            <option value="medium">中等</option>
                            <option value="hard">困难</option>
                            <option value="mixed">混合</option>
                        </select>
                    </div>

                    <div class="form-item">
                        <label for="homework-start-time">开始时间:</label>
                        <input
                            type="datetime-local"
                            id="homework-start-time"
                            v-model="homework.startTime"
                            class="input-field"
                            required
                        />
                    </div>

                    <div class="form-item">
                        <label for="homework-end-time">截止时间:</label>
                        <input
                            type="datetime-local"
                            id="homework-end-time"
                            v-model="homework.endTime"
                            class="input-field"
                            required
                        />
                    </div>
                </div>

                <div class="form-item full-width">
                    <label for="homework-description">作业描述:</label>
                    <textarea
                        id="homework-description"
                        v-model="homework.description"
                        placeholder="请输入作业描述（可选）"
                        class="textarea-field"
                        rows="4"
                    ></textarea>
                </div>
            </div>
        </div>

        <!-- 习题选择卡片 -->
        <div class="card exercise-selection-card">
            <h3>选择题库习题</h3>
            <div class="exercise-selection-content">
                <!-- 习题筛选 -->
                <div class="filter-bar">
                    <div class="filter-item">
                        <label for="exercise-difficulty-filter">难度:</label>
                        <select
                            id="exercise-difficulty-filter"
                            v-model="exerciseFilters.difficulty"
                            class="input-field"
                        >
                            <option value="">全部难度</option>
                            <option value="easy">简单</option>
                            <option value="medium">中等</option>
                            <option value="hard">困难</option>
                        </select>
                    </div>

                    <div class="filter-item">
                        <label for="exercise-type-filter">题型:</label>
                        <select
                            id="exercise-type-filter"
                            v-model="exerciseFilters.type"
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

                    <div class="search-container">
                        <input
                            type="text"
                            placeholder="搜索习题..."
                            v-model="exerciseFilters.searchKeyword"
                            @input="debounceExerciseSearch"
                            class="input-field"
                        />
                        <button class="btn btn-search" @click="filterExercises">
                            搜索
                        </button>
                    </div>
                </div>

                <!-- 习题列表 -->
                <div class="exercise-selection-grid">
                    <div class="exercise-grid-header">
                        <input
                            type="checkbox"
                            id="select-all-exercises"
                            v-model="selectAllExercises"
                            @change="toggleSelectAll"
                        />
                        <label for="select-all-exercises">全选</label>
                        <span class="selected-count"
                            >已选择: {{ selectedExercises.length }} 题</span
                        >
                    </div>

                    <div class="table-responsive">
                        <table class="exercise-table">
                            <thead>
                                <tr>
                                    <th style="width: 50px">选择</th>
                                    <th>习题ID</th>
                                    <th>题目</th>
                                    <th>题型</th>
                                    <th>难度</th>
                                    <th style="width: 100px">分值</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr
                                    v-for="exercise in filteredExercises"
                                    :key="exercise.id"
                                >
                                    <td>
                                        <input
                                            type="checkbox"
                                            :id="`exercise-${exercise.id}`"
                                            :value="exercise.id"
                                            v-model="selectedExercises"
                                        />
                                    </td>
                                    <td>{{ exercise.id }}</td>
                                    <td class="exercise-title">
                                        {{ truncateText(exercise.title, 50) }}
                                    </td>
                                    <td>{{ getTypeText(exercise.type) }}</td>
                                    <td>
                                        {{
                                            getDifficultyText(
                                                exercise.difficulty
                                            )
                                        }}
                                    </td>
                                    <td>
                                        <input
                                            type="number"
                                            v-model="
                                                exerciseScores[exercise.id]
                                            "
                                            min="0"
                                            step="0.5"
                                            class="score-input"
                                            :disabled="
                                                !selectedExercises.includes(
                                                    exercise.id
                                                )
                                            "
                                        />
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- 分页 -->
                    <div
                        class="pagination-container"
                        v-if="exerciseTotalPages > 1"
                    >
                        <button
                            class="pagination-btn"
                            :disabled="exerciseCurrentPage === 1"
                            @click="changeExercisePage(exerciseCurrentPage - 1)"
                        >
                            上一页
                        </button>
                        <span class="pagination-info">
                            {{ exerciseCurrentPage }} / {{ exerciseTotalPages }}
                        </span>
                        <button
                            class="pagination-btn"
                            :disabled="
                                exerciseCurrentPage === exerciseTotalPages
                            "
                            @click="changeExercisePage(exerciseCurrentPage + 1)"
                        >
                            下一页
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 已选题列表卡片 -->
        <div
            class="card selected-exercises-card"
            v-if="selectedExercises.length > 0"
        >
            <h3>已选习题 ({{ selectedExercises.length }})</h3>
            <div class="selected-exercises-content">
                <div class="table-responsive">
                    <table class="selected-exercise-table">
                        <thead>
                            <tr>
                                <th>习题ID</th>
                                <th>题目</th>
                                <th>题型</th>
                                <th>难度</th>
                                <th>分值</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                                v-for="exercise in getSelectedExerciseDetails"
                                :key="exercise.id"
                            >
                                <td>{{ exercise.id }}</td>
                                <td class="exercise-title">
                                    {{ truncateText(exercise.title, 40) }}
                                </td>
                                <td>{{ getTypeText(exercise.type) }}</td>
                                <td>
                                    {{ getDifficultyText(exercise.difficulty) }}
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        v-model="exerciseScores[exercise.id]"
                                        min="0"
                                        step="0.5"
                                        class="score-input"
                                    />
                                </td>
                                <td>
                                    <button
                                        class="btn btn-remove"
                                        @click="
                                            removeSelectedExercise(exercise.id)
                                        "
                                    >
                                        移除
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="total-score">
                    总分:
                    <span class="score-value">{{ calculateTotalScore }}</span>
                </div>
            </div>
        </div>

        <!-- 学生选择弹窗 -->
        <div v-if="showStudentSelector" class="student-selector-overlay">
            <div class="student-selector-modal">
                <div class="modal-header">
                    <h3>选择学生</h3>
                    <div class="modal-header-actions">
                        <button
                            class="close-btn"
                            @click="closeStudentSelection"
                        >
                            ×
                        </button>
                    </div>
                </div>
                <div class="modal-body">
                    <div class="student-list">
                        <!-- 学生全选按钮 - 添加了 select-all-btn 类并动态绑定状态类 -->
                        <button
                            class="btn select-all-btn"
                            :class="{
                                'select-all': !isAllStudentsSelected,
                                'deselect-all': isAllStudentsSelected,
                            }"
                            @click="toggleSelectAllStudents"
                        >
                            {{ isAllStudentsSelected ? "取消全选" : "全选" }}
                        </button>
                        <div
                            v-for="student in students"
                            :key="student.id"
                            class="student-item"
                        >
                            <label class="student-checkbox">
                                <input
                                    type="checkbox"
                                    :value="student"
                                    v-model="selectedStudents"
                                    :id="`student-${student.id}`"
                                />
                                <span class="checkbox-custom"></span>
                                <span class="student-info">
                                    {{ student.name }} ({{ student.studentId }})
                                </span>
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button
                        class="btn btn-secondary"
                        @click="closeStudentSelection"
                    >
                        取消
                    </button>
                    <button
                        class="btn btn-primary"
                        @click="closeStudentSelection"
                    >
                        确定
                    </button>
                </div>
            </div>
        </div>

        <!-- 班级选择弹窗 -->
        <div v-if="showClassSelector" class="student-selector-overlay">
            <div class="student-selector-modal">
                <div class="modal-header">
                    <h3>选择班级</h3>
                    <div class="modal-header-actions">
                        <button class="close-btn" @click="closeClassSelection">
                            ×
                        </button>
                    </div>
                </div>
                <div class="modal-body">
                    <div class="student-list">
                        <!-- 班级全选按钮 - 添加了 select-all-btn 类并动态绑定状态类 -->
                        <button
                            class="btn select-all-btn"
                            :class="{
                                'select-all': !isAllClassesSelected,
                                'deselect-all': isAllClassesSelected,
                            }"
                            @click="toggleSelectAllClasses"
                        >
                            {{ isAllClassesSelected ? "取消全选" : "全选" }}
                        </button>
                        <div
                            v-for="cls in classes"
                            :key="cls.id"
                            class="class-item"
                        >
                            <label class="class-checkbox">
                                <input
                                    type="checkbox"
                                    :value="cls.id"
                                    v-model="homework.selectedClassIds"
                                    @change="handleClassChange"
                                />

                                <span class="class-info">
                                    {{ cls.name }}
                                </span>
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button
                        class="btn btn-secondary"
                        @click="closeClassSelection"
                    >
                        取消
                    </button>
                    <button
                        class="btn btn-primary"
                        @click="closeClassSelection"
                    >
                        确定
                    </button>
                </div>
            </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
            <button class="btn btn-preview" @click="previewHomework">
                预览作业
            </button>
            <button class="btn btn-save-draft" @click="saveAsDraft">
                保存草稿
            </button>
            <button class="btn btn-publish" @click="publishHomework">
                发布作业
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
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

// 作业基本信息
const homework = ref({
    title: "",
    type: "",
    subjectId: "",
    difficulty: "",
    selectedClassIds: [], // 存储多个班级ID的数组
    selectedClassNames: [], // 存储多个班级名称的数组
    startTime: formatDateTime(new Date()),
    endTime: formatDateTime(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)), // 默认7天后
    description: "",
});

// 班级数据
const classes = ref([
    { id: "1", name: "高三(1)班" },
    { id: "2", name: "高三(2)班" },
    { id: "3", name: "高三(3)班" },
    { id: "4", name: "高二(1)班" },
    { id: "5", name: "高二(2)班" },
]);

// 学生选择相关
const students = ref([]); // 学生列表（根据选中的班级动态加载）
const selectedStudents = ref([]); // 选中的学生列表
const showStudentSelector = ref(false); // 是否显示学生选择器

// 班级选择相关
const showClassSelector = ref(false); // 是否显示班级选择器

// 初始化学生数据（模拟数据，实际应该根据班级ID动态获取）
const mockStudents = {
    1: [
        { id: "101", name: "张三", studentId: "2021001", gender: "男" },
        { id: "102", name: "李四", studentId: "2021002", gender: "女" },
        { id: "103", name: "王五", studentId: "2021003", gender: "男" },
        { id: "104", name: "赵六", studentId: "2021004", gender: "女" },
        { id: "105", name: "钱七", studentId: "2021005", gender: "男" },
    ],
    2: [
        { id: "201", name: "孙八", studentId: "2021051", gender: "女" },
        { id: "202", name: "周九", studentId: "2021052", gender: "男" },
        { id: "203", name: "吴十", studentId: "2021053", gender: "女" },
    ],
    3: [
        { id: "301", name: "郑十一", studentId: "2021101", gender: "男" },
        { id: "302", name: "王十二", studentId: "2021102", gender: "女" },
    ],
    4: [
        { id: "401", name: "陈十三", studentId: "2022001", gender: "男" },
        { id: "402", name: "林十四", studentId: "2022002", gender: "女" },
    ],
    5: [
        { id: "501", name: "黄十五", studentId: "2022051", gender: "男" },
        { id: "502", name: "张十六", studentId: "2022052", gender: "女" },
    ],
};

// 习题列表数据（模拟数据）
const availableExercises = ref([
    {
        id: 1001,
        title: "JavaScript中，以下哪个不是基本数据类型？",
        subjectId: 1,
        difficulty: "easy",
        type: "single-choice",
    },
    {
        id: 1002,
        title: "以下哪些排序算法的平均时间复杂度为O(n log n)？",
        subjectId: 3,
        difficulty: "medium",
        type: "multiple-choice",
    },
    {
        id: 1003,
        title: "在React中，useState钩子是否可以直接修改状态？",
        subjectId: 4,
        difficulty: "easy",
        type: "true-false",
    },
    {
        id: 1004,
        title: "链表和数组相比，插入操作的时间复杂度有什么优势？",
        subjectId: 2,
        difficulty: "medium",
        type: "essay",
    },
    {
        id: 1005,
        title: "什么是闭包？闭包在JavaScript中有什么应用场景？",
        subjectId: 1,
        difficulty: "hard",
        type: "essay",
    },
    {
        id: 1006,
        title: "快速排序的平均时间复杂度和最坏时间复杂度分别是多少？",
        subjectId: 3,
        difficulty: "medium",
        type: "blank",
    },
    {
        id: 1007,
        title: "Vue组件之间的通信方式有哪些？",
        subjectId: 4,
        difficulty: "medium",
        type: "multiple-choice",
    },
    {
        id: 1008,
        title: "以下哪个不是RESTful API的特点？",
        subjectId: 5,
        difficulty: "easy",
        type: "single-choice",
    },
    {
        id: 1009,
        title: "二叉树的中序遍历算法可以使用栈来实现吗？",
        subjectId: 2,
        difficulty: "medium",
        type: "true-false",
    },
    {
        id: 1010,
        title: "解释什么是虚拟DOM以及它在现代前端框架中的作用。",
        subjectId: 4,
        difficulty: "hard",
        type: "essay",
    },
]);

// 习题筛选条件
const exerciseFilters = ref({
    difficulty: "",
    type: "",
    searchKeyword: "",
});

// 习题分页数据
const exerciseCurrentPage = ref(1);
const exercisePageSize = ref(5);
const exerciseTotalPages = ref(1);

// 已选习题
const selectedExercises = ref([]);
const exerciseScores = ref({});
const selectAllExercises = ref(false);

// 格式化日期时间为input datetime-local格式
function formatDateTime(date) {
    return new Date(date).toISOString().slice(0, 16);
}

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

// 根据筛选条件过滤习题
const filteredExercises = computed(() => {
    let filtered = availableExercises.value;

    // 根据学科筛选
    if (homework.value.subjectId) {
        filtered = filtered.filter(
            (ex) => ex.subjectId === Number(homework.value.subjectId)
        );
    }

    // 根据难度筛选
    if (exerciseFilters.value.difficulty) {
        filtered = filtered.filter(
            (ex) => ex.difficulty === exerciseFilters.value.difficulty
        );
    }

    // 根据题型筛选
    if (exerciseFilters.value.type) {
        filtered = filtered.filter(
            (ex) => ex.type === exerciseFilters.value.type
        );
    }

    // 根据关键词搜索
    if (exerciseFilters.value.searchKeyword) {
        const keyword = exerciseFilters.value.searchKeyword.toLowerCase();
        filtered = filtered.filter((ex) =>
            ex.title.toLowerCase().includes(keyword)
        );
    }

    return filtered;
});

// 分页后的习题列表
const paginatedExercises = computed(() => {
    const start = (exerciseCurrentPage.value - 1) * exercisePageSize.value;
    const end = start + exercisePageSize.value;
    return filteredExercises.value.slice(start, end);
});

// 已选习题详情
const getSelectedExerciseDetails = computed(() => {
    return availableExercises.value.filter((ex) =>
        selectedExercises.value.includes(ex.id)
    );
});

// 计算总分
const calculateTotalScore = computed(() => {
    return getSelectedExerciseDetails.value.reduce((total, exercise) => {
        const score = Number(exerciseScores.value[exercise.id]) || 0;
        return total + score;
    }, 0);
});

// 防抖搜索习题
const debounceExerciseSearch = () => {
    clearTimeout(window.exerciseSearchTimeout);
    window.exerciseSearchTimeout = setTimeout(() => {
        filterExercises();
    }, 500);
};

// 处理班级选择变化
const handleClassChange = () => {
    // 更新已选班级名称
    homework.value.selectedClassNames = classes.value
        .filter((cls) => homework.value.selectedClassIds.includes(cls.id))
        .map((cls) => cls.name);

    // 合并所有选中班级的学生并去重
    let allStudents = [];
    let studentIds = new Set();

    homework.value.selectedClassIds.forEach((classId) => {
        const classStudents = mockStudents[classId] || [];
        classStudents.forEach((student) => {
            if (!studentIds.has(student.id)) {
                studentIds.add(student.id);
                allStudents.push(student);
            }
        });
    });

    // 更新学生列表
    students.value = allStudents;

    // 清空之前选择的学生
    selectedStudents.value = [];
};

// 显示学生选择器
const showStudentSelection = () => {
    if (homework.value.selectedClassIds.length === 0) {
        alert("请先选择班级");
        return;
    }
    showStudentSelector.value = true;
};

// 检查是否所有学生都已选中
const isAllStudentsSelected = computed(() => {
    return (
        students.value.length > 0 &&
        selectedStudents.value.length === students.value.length
    );
});

// 全选/取消全选学生
const toggleSelectAllStudents = () => {
    if (isAllStudentsSelected.value) {
        // 取消全选
        selectedStudents.value = [];
    } else {
        // 全选
        selectedStudents.value = [...students.value];
    }
};

// 关闭学生选择器
const closeStudentSelection = () => {
    showStudentSelector.value = false;
};

// 获取已选学生显示文本
const getSelectedStudentsText = () => {
    if (selectedStudents.value.length === 0) {
        return "点击选择学生";
    }
    if (selectedStudents.value.length <= 3) {
        return selectedStudents.value.map((s) => s.name).join(", ");
    }
    return `${selectedStudents.value[0].name} 等 ${selectedStudents.value.length} 人`;
};

// 班级选择相关方法
const showClassSelection = () => {
    showClassSelector.value = true;
};

const closeClassSelection = () => {
    showClassSelector.value = false;
};

const isAllClassesSelected = computed(() => {
    return (
        classes.value.length > 0 &&
        homework.value.selectedClassIds.length === classes.value.length
    );
});

const toggleSelectAllClasses = () => {
    if (isAllClassesSelected.value) {
        homework.value.selectedClassIds = [];
    } else {
        homework.value.selectedClassIds = classes.value.map((cls) => cls.id);
    }
    handleClassChange();
};

const getSelectedClassesText = () => {
    if (homework.value.selectedClassIds.length === 0) {
        return "点击选择班级";
    }
    if (homework.value.selectedClassIds.length <= 3) {
        return homework.value.selectedClassNames.join(", ");
    }
    return `${homework.value.selectedClassNames[0]} 等 ${homework.value.selectedClassIds.length} 个班级`;
};

// 学生难度配置相关
const studentDifficultyConfig = ref({}); // 存储学生特定的难度配置
const showDifficultyConfig = ref(false); // 是否显示难度配置弹窗

// 为选中的学生设置默认难度配置
const setupDefaultDifficultyConfig = () => {
    selectedStudents.value.forEach((student) => {
        if (!studentDifficultyConfig.value[student.id]) {
            studentDifficultyConfig.value[student.id] = {
                ...homework.value, // 默认使用作业的全局难度
                studentId: student.id,
                studentName: student.name,
            };
        }
    });
};

// 显示学生难度配置弹窗
const showStudentDifficultyConfig = () => {
    if (selectedStudents.value.length === 0) {
        alert("请先选择学生");
        return;
    }
    setupDefaultDifficultyConfig();
    showDifficultyConfig.value = true;
};

// 关闭学生难度配置弹窗
const closeDifficultyConfig = () => {
    showDifficultyConfig.value = false;
};

// 更新学生难度配置
const updateStudentDifficulty = (studentId, field, value) => {
    if (!studentDifficultyConfig.value[studentId]) {
        studentDifficultyConfig.value[studentId] = {};
    }
    studentDifficultyConfig.value[studentId][field] = value;
};

// 重置学生配置为默认值
const resetStudentConfig = (studentId) => {
    studentDifficultyConfig.value[studentId] = {
        ...homework.value,
        studentId: studentId,
        studentName: selectedStudents.value.find((s) => s.id === studentId)
            ?.name,
    };
};

// 根据学生ID获取配置的难度
const getStudentDifficulty = (studentId) => {
    return studentDifficultyConfig.value[studentId] || homework.value;
};

// 获取学生特定的习题列表
const getStudentSpecificExercises = (studentId) => {
    const config = getStudentDifficulty(studentId);
    // 根据学生配置的难度筛选习题
    return availableExercises.value.filter(
        (ex) =>
            (!config.difficultyId || ex.difficultyId === config.difficultyId) &&
            (!config.typeId || ex.typeId === config.typeId) &&
            (!config.subjectId || ex.subjectId === config.subjectId)
    );
};

// 获取学生个性化的作业数据
const getPersonalizedHomeworkData = () => {
    const baseData = {
        ...homework.value,
        totalScore: calculateTotalScore.value,
    };

    // 为每个学生创建个性化的作业数据
    const personalizedData = selectedStudents.value.map((student) => {
        const studentConfig = getStudentDifficulty(student.id);
        // 根据学生的难度配置筛选习题
        const studentExercises = getStudentSpecificExercises(student.id);

        // 获取适合该学生难度的已选题（这里简化处理，实际可能需要更复杂的逻辑）
        let selectedExercises = getSelectedExerciseDetails.value.filter(
            (ex) =>
                !studentConfig.difficultyId ||
                ex.difficultyId === studentConfig.difficultyId
        );

        // 如果筛选后没有习题，使用部分原难度习题
        if (
            selectedExercises.length === 0 &&
            getSelectedExerciseDetails.value.length > 0
        ) {
            selectedExercises = getSelectedExerciseDetails.value.slice(0, 2); // 取前2道题
        }

        return {
            ...baseData,
            studentId: student.id,
            studentName: student.name,
            difficultyId: studentConfig.difficultyId,
            difficultyName: getDifficultyText(studentConfig.difficultyId),
            exercises: selectedExercises.map((ex) => ({
                exerciseId: ex.id,
                score: Number(exerciseScores.value[ex.id]) || 0,
            })),
        };
    });

    return personalizedData;
};

// 筛选习题
const filterExercises = () => {
    exerciseCurrentPage.value = 1;
    updateExerciseTotalPages();
};

// 更新习题总页数
const updateExerciseTotalPages = () => {
    exerciseTotalPages.value = Math.ceil(
        filteredExercises.value.length / exercisePageSize.value
    );
};

// 加载指定学科的习题
const loadSubjectExercises = () => {
    exerciseCurrentPage.value = 1;
    updateExerciseTotalPages();
    // 实际应用中，这里会根据选择的学科从API获取习题数据
};

// 改变习题页码
const changeExercisePage = (page) => {
    if (page >= 1 && page <= exerciseTotalPages.value) {
        exerciseCurrentPage.value = page;
    }
};

// 切换全选/取消全选
const toggleSelectAll = () => {
    if (selectAllExercises.value) {
        // 全选当前页的习题
        paginatedExercises.value.forEach((exercise) => {
            if (!selectedExercises.value.includes(exercise.id)) {
                selectedExercises.value.push(exercise.id);
                // 为新选中的习题设置默认分值
                if (!exerciseScores.value[exercise.id]) {
                    exerciseScores.value[exercise.id] = 10;
                }
            }
        });
    } else {
        // 取消选择当前页的习题
        const currentPageExerciseIds = paginatedExercises.value.map(
            (ex) => ex.id
        );
        selectedExercises.value = selectedExercises.value.filter(
            (id) => !currentPageExerciseIds.includes(id)
        );
    }
};

// 移除已选题
const removeSelectedExercise = (exerciseId) => {
    selectedExercises.value = selectedExercises.value.filter(
        (id) => id !== exerciseId
    );
    // 保持全选状态的一致性
    checkSelectAllStatus();
};

// 检查是否所有当前页的习题都已选中
const checkSelectAllStatus = () => {
    const currentPageExerciseIds = paginatedExercises.value.map((ex) => ex.id);
    const allSelected = currentPageExerciseIds.every((id) =>
        selectedExercises.value.includes(id)
    );
    selectAllExercises.value = allSelected && currentPageExerciseIds.length > 0;
};

// 预览作业
const previewHomework = () => {
    if (!validateHomework()) return;
    alert("预览作业功能待实现");
};

// 保存草稿
const saveAsDraft = () => {
    if (!validateHomework()) return;
    alert("保存草稿功能待实现");
};

// 发布作业
const publishHomework = () => {
    if (!validateHomework(true)) return;

    // 构建作业数据（包含学生个性化难度配置）
    const personalizedData = getPersonalizedHomeworkData();

    const homeworkData = {
        ...homework.value,
        selectedStudents: selectedStudents.value,
        studentDifficultyConfigs: Object.values(studentDifficultyConfig.value),
        exercises: getSelectedExerciseDetails.value.map((ex) => ({
            exerciseId: ex.id,
            score: Number(exerciseScores.value[ex.id]) || 0,
        })),
        totalScore: calculateTotalScore.value,
        personalizedData, // 包含每个学生的个性化作业配置
    };

    console.log("发布作业数据:", homeworkData);
    alert("作业发布成功！");
    router.push("/teacher/index");
};

// 验证作业信息
const validateHomework = (isPublish = false) => {
    // 验证基本信息
    if (
        !homework.value.title ||
        !homework.value.type ||
        !homework.value.subjectId ||
        homework.value.selectedClassIds.length === 0 ||
        selectedStudents.value.length === 0
    ) {
        alert("请填写作业标题、类型、所属学科、选择班级和学生");
        return false;
    }

    // 验证时间
    const startTime = new Date(homework.value.startTime);
    const endTime = new Date(homework.value.endTime);
    const now = new Date();

    if (startTime > endTime) {
        alert("开始时间不能晚于截止时间");
        return false;
    }

    if (endTime <= now) {
        alert("截止时间不能早于当前时间");
        return false;
    }

    // 发布时验证是否选择题
    if (isPublish && selectedExercises.value.length === 0) {
        alert("请至少选择一道习题");
        return false;
    }

    // 验证已选题的分值
    if (isPublish) {
        for (const exerciseId of selectedExercises.value) {
            const score = Number(exerciseScores.value[exerciseId]);
            if (isNaN(score) || score <= 0) {
                alert("请为所有已选习题设置有效的分值");
                return false;
            }
        }
    }

    return true;
};

// 组件挂载时执行
onMounted(() => {
    updateExerciseTotalPages();
    // 初始化时为习题设置默认分值
    availableExercises.value.forEach((exercise) => {
        exerciseScores.value[exercise.id] = 10;
    });
});
</script>
<style scoped>
/* 整体容器样式 */
.homework-container {
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

/* 表单内容 */
.form-content {
    transition: transform 0.3s ease;
}

.card:hover .form-content {
    transform: translateX(3px);
}

.form-group {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.form-item {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 200px;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .form-item {
    transform: translateX(3px);
    opacity: 1;
}

.form-item.full-width {
    min-width: 100%;
}

.form-item label {
    font-size: 14px;
    color: #555;
    margin-bottom: 8px;
    font-weight: 500;
}

/* 输入框样式统一 */
.input-field,
.textarea-field {
    padding: 12px 15px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.3s ease;
}

.textarea-field {
    resize: vertical;
    min-height: 100px;
}

.input-field:focus,
.textarea-field:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

/* 习题选择区域 */
.exercise-selection-content {
    transition: transform 0.3s ease;
}

.card:hover .exercise-selection-content {
    transform: translateX(3px);
}

.filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 20px;
    align-items: center;
}

.search-container {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    min-width: 250px;
}

/* 习题网格头部 */
.exercise-grid-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e0e0e0;
}

.exercise-grid-header label {
    font-size: 14px;
    color: #555;
    cursor: pointer;
}

.selected-count {
    margin-left: auto;
    font-size: 14px;
    color: #3b82f6;
    font-weight: 500;
}

/* 表格样式 */
.table-responsive {
    overflow-x: auto;
    margin-bottom: 20px;
}

.exercise-table,
.selected-exercise-table {
    width: 100%;
    border-collapse: collapse;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .exercise-table,
.card:hover .selected-exercise-table {
    transform: translateX(3px);
    opacity: 1;
}

.exercise-table th,
.selected-exercise-table th {
    background-color: #f8f9fa;
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    color: #333;
    border-bottom: 2px solid #e9ecef;
    font-size: 14px;
}

.exercise-table td,
.selected-exercise-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #e9ecef;
    color: #666;
    font-size: 14px;
}

.exercise-table tr:last-child td,
.selected-exercise-table tr:last-child td {
    border-bottom: none;
}

.exercise-table tr:hover,
.selected-exercise-table tr:hover {
    background-color: #f8f9fa;
    transition: background-color 0.3s ease;
}

.exercise-title {
    max-width: 400px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 分值输入框 */
.score-input {
    width: 70px;
    padding: 6px 8px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    text-align: center;
    font-size: 14px;
}

.score-input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.score-input:disabled {
    background-color: #f8f9fa;
    cursor: not-allowed;
    opacity: 0.6;
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

/* 总分显示 */
.total-score {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e9ecef;
    font-size: 16px;
    font-weight: 600;
    color: #1e3a8a;
}

.score-value {
    margin-left: 10px;
    color: #3b82f6;
    font-size: 20px;
}

/* 操作按钮 */
.action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e0e0e0;
}

/* 按钮样式统一 */
.btn {
    padding: 12px 24px;
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

.btn-preview {
    background: linear-gradient(135deg, #94a3b8, #64748b);
    color: white;
}

.btn-preview:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(148, 163, 184, 0.4);
    background: linear-gradient(135deg, #cbd5e1, #64748b);
}

.btn-save-draft {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
}

.btn-save-draft:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4);
    background: linear-gradient(135deg, #fbbf24, #d97706);
}

.btn-publish {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: white;
}

.btn-publish:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(46, 204, 113, 0.4);
    background: linear-gradient(135deg, #58d68d, #27ae60);
}

.btn-remove {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
    padding: 6px 12px;
    font-size: 12px;
}

.btn-remove:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
    background: linear-gradient(135deg, #ec7063, #c0392b);
}

.btn-search {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    min-width: 80px;
}

.btn-search:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
    background: linear-gradient(135deg, #64b5f6, #2196f3);
}

/* 学生选择相关样式 */
.student-selection-wrapper {
    position: relative;
}

.student-selector-btn {
    width: 100%;
    text-align: left;
    cursor: pointer;
    background-color: white;
}

.student-selector-btn:hover {
    border-color: #3498db;
}

/* 学生选择弹窗样式 */
.student-selector-overlay {
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

.student-selector-modal {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
    margin: 0;
    color: #1e3a8a;
    font-size: 18px;
    font-weight: 600;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.close-btn:hover {
    color: #333;
}

.modal-body {
    padding: 20px;
    flex: 1;
    overflow-y: auto;
}

/* 学生选择头部样式 */
.student-selection-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e5e7eb;
}

.student-selection-header .btn-secondary {
    background-color: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
}

.student-selection-header .btn-secondary:hover {
    background-color: #e5e7eb;
}

.student-selection-header .selected-count {
    font-size: 14px;
    color: #666;
}

/* 班级选择相关样式 */
.class-checkbox-group {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 10px;
    max-height: 120px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    background-color: #f9fafb;
}

.class-checkbox {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 6px;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.class-checkbox:hover {
    background-color: rgba(59, 130, 246, 0.08);
    border-color: rgba(59, 130, 246, 0.2);
}

.class-checkbox input[type="checkbox"] {
    margin-right: 8px;
    width: 16px;
    height: 16px;
    cursor: pointer;
}

.class-checkbox input[type="checkbox"]:checked {
    accent-color: #3b82f6;
}

.selected-classes-info {
    margin-top: 12px;
    font-size: 14px;
    color: #666;
    font-style: italic;
    background-color: #f0f9ff;
    padding: 8px 12px;
    border-radius: 4px;
    border-left: 3px solid #3b82f6;
}

.student-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.student-item {
    padding: 8px 0;
}

.student-checkbox {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 4px;
    transition: background-color 0.3s ease;
}

.student-checkbox:hover {
    background-color: #f8f9fa;
}

.student-checkbox input[type="checkbox"] {
    display: none;
}

.checkbox-custom {
    position: relative;
    display: inline-block;
    width: 18px;
    height: 18px;
    border: 2px solid #e0e0e0;
    border-radius: 4px;
    margin-right: 10px;
    transition: all 0.3s ease;
}

.student-checkbox input[type="checkbox"]:checked + .checkbox-custom {
    background-color: #3498db;
    border-color: #3498db;
}

.student-checkbox input[type="checkbox"]:checked + .checkbox-custom::after {
    content: "✓";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
}

.student-info {
    color: #333;
    font-size: 14px;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: 15px 20px;
    border-top: 1px solid #e0e0e0;
}

.btn-primary {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-secondary {
    background: linear-gradient(135deg, #95a5a6, #7f8c8d);
    color: white;
}

.btn-secondary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(149, 165, 166, 0.4);
    background: linear-gradient(135deg, #a4b4b5, #95a5a6);
}

.btn-secondary:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}
/* 全选/取消全选按钮基础样式 */
.select-all-btn {
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    color: white;
    font-weight: 500;
    cursor: pointer;
    height: 40px;
    transition: all 0.3s ease;
    margin-bottom: 15px;
}

/* 全选状态 - 绿色渐变 */
.select-all-btn.select-all {
    background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 50%, #86efac 100%);
    color: #006426;
    box-shadow: 0 2px 5px rgba(74, 222, 128, 0.2);
}

.select-all-btn.select-all:hover {
    background: linear-gradient(135deg, #bbf7d0 0%, #86efac 50%, #4ade80 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(74, 222, 128, 0.3);
}

/* 取消全选状态 - 红色渐变 */
.select-all-btn.deselect-all {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 50%, #fca5a5 100%);
    color: #880000;
    box-shadow: 0 2px 5px rgba(239, 68, 68, 0.2);
}

.select-all-btn.deselect-all:hover {
    background: linear-gradient(135deg, #fecaca 0%, #fca5a5 50%, #ef4444 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
}
/* 学生难度配置弹窗样式 */
.difficulty-config-overlay {
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

.difficulty-config-modal {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 700px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.student-difficulty-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.student-difficulty-item {
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
}

.student-info-header {
    font-weight: 600;
    margin-bottom: 10px;
    color: #1e3a8a;
    font-size: 15px;
}

.difficulty-config-form {
    display: flex;
    gap: 20px;
    align-items: center;
}

.config-item {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.config-item label {
    font-size: 14px;
    color: #666;
}

.input-field.small {
    width: 150px;
    padding: 6px 10px;
    font-size: 14px;
}

/* 难度配置指示器 */
.difficulty-config-indicator {
    margin-right: 5px;
    font-size: 16px;
}

.config-count {
    font-size: 12px;
    margin-left: 4px;
    background-color: rgba(255, 255, 255, 0.3);
    padding: 2px 6px;
    border-radius: 10px;
}

/* 自定义配置标记 */
.custom-config-badge {
    background-color: #27ae60;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    margin-left: 10px;
    font-weight: normal;
}

/* 配置操作按钮 */
.config-actions {
    margin-left: auto;
}

.btn-reset {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    border: none;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-reset:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
    background: linear-gradient(135deg, #c0392b, #a93226);
}

/* 动画效果 */
.student-difficulty-item {
    transition: all 0.3s ease;
}

.student-difficulty-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-color: #3498db;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .difficulty-config-form {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .input-field.small {
        width: 100%;
    }

    .config-actions {
        margin-left: 0;
        margin-top: 5px;
    }

    .student-info-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }

    .custom-config-badge {
        margin-left: 0;
    }

    .student-selector-modal,
    .difficulty-config-modal {
        width: 95%;
        max-height: 90vh;
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
/* 响应式设计 */
@media (max-width: 1200px) {
    .form-group {
        flex-direction: column;
    }

    .form-item {
        min-width: 100%;
    }

    .filter-bar {
        flex-direction: column;
        align-items: stretch;
    }

    .search-container {
        min-width: 100%;
    }
}

@media (max-width: 768px) {
    .card {
        padding: 20px;
    }

    .action-buttons {
        flex-direction: column;
    }

    .btn {
        width: 100%;
    }

    .exercise-table th,
    .selected-exercise-table th,
    .exercise-table td,
    .selected-exercise-table td {
        padding: 8px;
        font-size: 12px;
    }

    .exercise-title {
        max-width: 200px;
    }

    .score-input {
        width: 50px;
    }
}
</style>
