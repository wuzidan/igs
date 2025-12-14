<template>
    <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>

    <div class="class-info-container">
        <div class="page-header">
            <h2>学习者信息</h2>
            <p>查看和管理班级基本信息和学生列表</p>
        </div>

        <!-- 班级详情卡片 - 使用统一的card样式 -->
        <div class="card class-detail-card">
            <h3>班级详情</h3>
            <div class="card-body">
                <div class="info-row">
                    <div class="info-label">班级名称:</div>
                    <div class="info-value">{{ className }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">班级代码:</div>
                    <div class="info-value">{{ classCode }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">创建时间:</div>
                    <div class="info-value">{{ createTime }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">学生数量:</div>
                    <div class="info-value">{{ studentCount }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">课程名称:</div>
                    <div class="info-value">{{ courseName }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">班主任:</div>
                    <div class="info-value">{{ headTeacher }}</div>
                </div>
            </div>
            <div class="card-footer">
                <button class="btn btn-edit" @click="editClassInfo">
                    编辑班级信息
                </button>
                <button class="btn btn-add-student" @click="addStudent">
                    添加学生
                </button>
            </div>
        </div>

        <!-- 学生列表卡片 - 使用统一的card样式 -->
        <div class="card student-list-container">
            <div class="container-header">
                <h3>学生列表</h3>
                <div class="search-box">
                    <input
                        type="text"
                        placeholder="搜索学生..."
                        v-model="searchKeyword"
                        @input="debounceSearch"
                        class="input-field"
                    />
                    <button class="btn btn-search" @click="searchStudents">
                        搜索
                    </button>
                </div>
            </div>

            <div class="table-responsive">
                <table class="student-table">
                    <thead>
                        <tr>
                            <th>学生姓名</th>
                            <th>学号</th>
                            <th>性别</th>
                            <th>联系电话</th>
                            <th>邮箱</th>
                            <th>加入时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="student in students" :key="student.id">
                            <td>{{ student.name }}</td>
                            <td>{{ student.studentId }}</td>
                            <td>{{ student.gender }}</td>
                            <td>{{ student.phone }}</td>
                            <td>{{ student.email }}</td>
                            <td>{{ student.joinTime }}</td>
                            <td>
                                <button
                                    class="btn btn-view"
                                    @click="viewStudent(student.id)"
                                >
                                    查看
                                </button>
                                <button
                                    class="btn btn-remove"
                                    @click="removeStudent(student.id)"
                                >
                                    移除
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 班级信息
const className = ref("编程基础班");
const classCode = ref("PROG-2023-001");
const createTime = ref("2023-09-01");
const studentCount = ref(45);
const courseName = ref("计算机编程基础");
const headTeacher = ref("李老师");

// 学生数据
const students = ref([
    {
        id: 1,
        name: "张明",
        studentId: "PROG2023001",
        gender: "男",
        phone: "13800138000",
        email: "zhangming@example.com",
        joinTime: "2023-09-01",
    },
    {
        id: 2,
        name: "李华",
        studentId: "PROG2023002",
        gender: "女",
        phone: "13900139000",
        email: "lihua@example.com",
        joinTime: "2023-09-01",
    },
    {
        id: 3,
        name: "王强",
        studentId: "PROG2023003",
        gender: "男",
        phone: "13700137000",
        email: "wangqiang@example.com",
        joinTime: "2023-09-01",
    },
    {
        id: 4,
        name: "刘芳",
        studentId: "PROG2023004",
        gender: "女",
        phone: "13600136000",
        email: "liufang@example.com",
        joinTime: "2023-09-01",
    },
    {
        id: 5,
        name: "陈宇",
        studentId: "PROG2023005",
        gender: "男",
        phone: "13500135000",
        email: "chenyu@example.com",
        joinTime: "2023-09-01",
    },
]);

// 搜索和分页
const searchKeyword = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const totalPages = ref(Math.ceil(students.value.length / pageSize.value));

// 防抖搜索
const debounceSearch = () => {
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
        searchStudents();
    }, 500);
};

// 搜索学生
const searchStudents = () => {
    // 这里添加搜索逻辑
    console.log("搜索学生:", searchKeyword.value);
    // 实际应用中，这里会根据关键词过滤学生数据
};

// 改变页码
const changePage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
        // 实际应用中，这里会加载对应页的学生数据
    }
};

// 编辑班级信息
const editClassInfo = () => {
    // 这里添加编辑班级信息的逻辑
    console.log("编辑班级信息");
    // 实际应用中，这里会打开编辑对话框
};

// 添加学生
const addStudent = () => {
    // 这里添加添加学生的逻辑
    console.log("添加学生");
    // 实际应用中，这里会打开添加学生对话框
};

// 查看学生
const viewStudent = (studentId) => {
    router.push(`/teacher/class/student/${studentId}`);
};

// 移除学生
const removeStudent = (studentId) => {
    // 这里添加移除学生的逻辑
    if (confirm("确定要移除这名学生吗？")) {
        students.value = students.value.filter(
            (student) => student.id !== studentId
        );
        studentCount.value = students.value.length;
        totalPages.value = Math.ceil(students.value.length / pageSize.value);
        if (currentPage.value > totalPages.value && totalPages.value > 0) {
            currentPage.value = totalPages.value;
        }
    }
};

// 组件挂载时执行
onMounted(() => {
    // 初始化数据
    // 实际应用中，这里会从API获取班级信息和学生数据
});
</script>

<style scoped>
/* 整体容器样式 */
.class-info-container {
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

/* 班级详情卡片特有样式 */
.class-detail-card {
    margin-bottom: 30px;
}

.card-body {
    margin-bottom: 20px;
}

.info-row {
    display: flex;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .info-row {
    transform: translateX(3px);
    opacity: 1;
}

.card:hover .info-row:nth-child(2) {
    transition-delay: 0.05s;
}
.card:hover .info-row:nth-child(3) {
    transition-delay: 0.1s;
}
.card:hover .info-row:nth-child(4) {
    transition-delay: 0.15s;
}
.card:hover .info-row:nth-child(5) {
    transition-delay: 0.2s;
}
.card:hover .info-row:nth-child(6) {
    transition-delay: 0.25s;
}

.info-row:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.info-label {
    width: 120px;
    font-weight: 600;
    color: #555;
}

.info-value {
    flex: 1;
    color: #333;
    font-size: 14px;
}

.card-footer {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    padding-top: 20px;
    border-top: 1px dashed rgba(59, 130, 246, 0.2);
}

/* 学生列表容器特有样式 */
.student-list-container {
    margin-bottom: 25px;
}

.container-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    transition: transform 0.3s ease;
}

.card:hover .container-header {
    transform: translateX(3px);
}

.search-box {
    display: flex;
    gap: 10px;
    align-items: center;
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

.btn-edit,
.btn-view {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-edit:hover,
.btn-view:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
    background: linear-gradient(135deg, #64b5f6, #2196f3);
}

.btn-add-student {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: white;
}

.btn-add-student:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(46, 204, 113, 0.4);
    background: linear-gradient(135deg, #58d68d, #27ae60);
}

.btn-remove {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
    margin-left: 8px;
}

.btn-remove:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(231, 76, 60, 0.4);
    background: linear-gradient(135deg, #ec7063, #c0392b);
}

.btn-search {
    background: linear-gradient(135deg, #9b59b6, #8e44ad);
    color: white;
}

.btn-search:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(155, 89, 182, 0.4);
    background: linear-gradient(135deg, #b39ddb, #8e44ad);
}

/* 表格样式 */
.table-responsive {
    overflow-x: auto;
    margin-top: 20px;
}

.student-table {
    width: 100%;
    border-collapse: collapse;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .student-table {
    transform: translateX(3px);
    opacity: 1;
}

.student-table th {
    background-color: #f8f9fa;
    padding: 15px;
    text-align: left;
    font-weight: 600;
    color: #333;
    border-bottom: 2px solid #e9ecef;
    font-size: 14px;
}

.student-table td {
    padding: 15px;
    border-bottom: 1px solid #e9ecef;
    color: #666;
    font-size: 14px;
}

.student-table tr:last-child td {
    border-bottom: none;
}

.student-table tr:hover {
    background-color: #f8f9fa;
    transition: background-color 0.3s ease;
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
    .card-footer {
        justify-content: center;
        flex-wrap: wrap;
    }

    .search-box {
        flex-wrap: wrap;
        justify-content: center;
    }
}

@media (max-width: 768px) {
    .card {
        padding: 20px;
    }

    .info-row {
        flex-direction: column;
    }

    .info-label {
        width: 100%;
        margin-bottom: 5px;
    }

    .container-header {
        flex-direction: column;
        align-items: stretch;
        gap: 15px;
    }

    .btn {
        width: 100%;
        margin-bottom: 10px;
    }

    .btn-remove {
        margin-left: 0;
        margin-top: 5px;
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
