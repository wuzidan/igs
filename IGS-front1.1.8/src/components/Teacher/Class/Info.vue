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

        <!-- 课程管理卡片 -->
        <div class="card course-management-card">
            <h3>课程管理</h3>
            <div class="card-body">
                <div class="course-actions">
                    <el-button type="primary" @click="showAddCourseDialog">添加课程</el-button>
                    <el-input
                        placeholder="搜索课程..."
                        v-model="courseSearchKeyword"
                        @input="debounceCourseSearch"
                        class="course-search-input"
                        clearable
                    />
                </div>
                <div class="course-list" v-if="courses.length > 0">
                    <div v-for="course in courses" :key="course.id" class="course-card">
                        <div class="course-card-body">
                            <h4>{{ course.name }}</h4>
                            <p class="course-description">{{ course.description || '无描述' }}</p>
                            <div class="course-meta">
                                <span class="course-id">ID: {{ course.id }}</span>
                            </div>
                        </div>
                        <div class="course-card-actions">
                            <el-button size="small" @click="editCourse(course)">编辑</el-button>
                            <el-button size="small" type="danger" @click="deleteCourse(course.id)">删除</el-button>
                        </div>
                    </div>
                </div>
                <div class="empty-state" v-else>
                    <p>暂无可管理的课程</p>
                    <el-button type="primary" @click="showAddCourseDialog">添加课程</el-button>
                </div>
            </div>
        </div>

        <div class="card class-detail-card" v-if="classes.length > 0">
            <h3>选择班级</h3>
            <div class="card-body">
                <div class="info-row">
                    <div class="info-label">当前班级:</div>
                    <div class="info-value">
                        <el-select v-model="selectedClassId" @change="onClassChange" placeholder="选择班级" class="class-select" :loading="classLoading">
                            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="String(c.id)"></el-option>
                        </el-select>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <el-button type="primary" @click="showCreateClassDialog" :loading="loading">新增班级</el-button>
                <el-button type="danger" :disabled="!selectedClassId" @click="showDeleteConfirm" :loading="loading">删除班级</el-button>
            </div>
        </div>

        <div class="card class-detail-card" v-else>
            <h3>选择班级</h3>
            <div class="card-body">
                <div class="info-row">
                    <div class="info-value">暂无可管理的班级</div>
                </div>
            </div>
            <div class="card-footer">
                <el-button type="primary" @click="showCreateClassDialog">新增班级</el-button>
            </div>
        </div>

        <!-- 班级详情卡片 - 使用统一的card样式 -->
        <div class="card class-detail-card">
            <h3>班级详情</h3>
            <div class="card-body" v-loading="classLoading">
                <div class="info-row">
                    <div class="info-label">班级名称:</div>
                    <div class="info-value">{{ className }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">班级代码:</div>
                    <div class="info-value">
                        {{ classCode }}
                        <el-button size="small" type="primary" @click="copyClassCode" style="margin-left: 10px;">
                            复制代码
                        </el-button>
                    </div>
                </div>
                <div class="info-row">
                    <div class="info-label">提示:</div>
                    <div class="info-value" style="color: #666; font-size: 14px;">
                        请将此班级代码告知学生，学生可通过代码加入班级。
                    </div>
                </div>
                <div class="info-row">
                    <div class="info-label">创建时间:</div>
                    <div class="info-value">{{ createTime }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">学生数量:</div>
                    <div class="info-value student-count">{{ studentCount }}</div>
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
                <el-button type="warning" @click="showEditClassDialog" :loading="loading">编辑班级信息</el-button>
                <el-button type="danger" :disabled="!selectedClassId" @click="showDeleteConfirm" :loading="loading">删除班级</el-button>
            </div>
        </div>

        <!-- 学生列表卡片 - 使用统一的card样式 -->
        <div class="card student-list-container">
            <div class="container-header">
                <h3>学生列表</h3>
                <div class="search-box">
                    <el-input
                        placeholder="搜索学生..."
                        v-model="searchKeyword"
                        @input="debounceSearch"
                        class="search-input"
                        clearable
                        :loading="studentLoading"
                    />
                    <el-button type="primary" @click="searchStudents" :loading="studentLoading">搜索</el-button>
                </div>
            </div>

            <div class="table-responsive">
                <el-table :data="students" style="width: 100%" class="student-table" v-loading="studentLoading">
                    <el-table-column prop="name" label="学生姓名" width="120" />
                    <el-table-column prop="studentId" label="学号" width="150" />
                    <el-table-column prop="gender" label="性别" width="80" />
                    <el-table-column prop="phone" label="联系电话" width="150" />
                    <el-table-column prop="email" label="邮箱" min-width="200" />
                    <el-table-column prop="joinTime" label="加入时间" width="150" />
                    <el-table-column label="操作" width="120" fixed="right">
                        <template #default="scope">
                            <el-button size="small" @click="viewStudent(scope.row.id)" :loading="loading">查看</el-button>
                            <el-button size="small" type="danger" @click="removeStudent(scope.row.id)" :loading="loading">移除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <div class="pagination-container" v-if="totalPages > 1">
                <el-pagination
                    v-model:current-page="currentPage"
                    v-model:page-size="pageSize"
                    :page-sizes="[10, 20, 50, 100]"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="totalCount"
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                    :loading="studentLoading"
                />
            </div>
        </div>
    </div>

    <!-- 创建班级对话框 -->
    <el-dialog
        v-model="createClassDialogVisible"
        title="新增班级"
        width="500px"
    >
        <el-form :model="createClassForm" :rules="createClassRules" ref="createClassFormRef">
            <el-form-item label="班级名称" prop="name">
                <el-input v-model="createClassForm.name" placeholder="请输入班级名称" />
            </el-form-item>
            <el-form-item label="课程名称" prop="course_id">
                <el-select v-model="createClassForm.course_id" placeholder="请选择课程" :loading="courseLoading">
                    <el-option v-for="course in courses" :key="course.id" :label="course.name" :value="String(course.id)"></el-option>
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="createClassDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleCreateClass">确定</el-button>
            </span>
        </template>
    </el-dialog>

    <!-- 编辑班级对话框 -->
    <el-dialog
        v-model="editClassDialogVisible"
        title="编辑班级信息"
        width="500px"
    >
        <el-form :model="editClassForm" :rules="editClassRules" ref="editClassFormRef">
            <el-form-item label="班级名称" prop="name">
                <el-input v-model="editClassForm.name" placeholder="请输入班级名称" />
            </el-form-item>
            <el-form-item label="课程名称" prop="course_id">
                <el-select v-model="editClassForm.course_id" placeholder="请选择课程" :loading="courseLoading">
                    <el-option v-for="course in courses" :key="course.id" :label="course.name" :value="String(course.id)"></el-option>
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="editClassDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleEditClass">确定</el-button>
            </span>
        </template>
    </el-dialog>

    <!-- 添加课程对话框 -->
    <el-dialog
        v-model="addCourseDialogVisible"
        title="添加课程"
        width="500px"
    >
        <el-form :model="addCourseForm" :rules="addCourseRules" ref="addCourseFormRef">
            <el-form-item label="课程名称" prop="name">
                <el-input v-model="addCourseForm.name" placeholder="请输入课程名称" />
            </el-form-item>
            <el-form-item label="课程描述">
                <el-input
                    v-model="addCourseForm.description"
                    placeholder="请输入课程描述"
                    type="textarea"
                    rows="3"
                />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="addCourseDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleAddCourse">确定</el-button>
            </span>
        </template>
    </el-dialog>

    <!-- 编辑课程对话框 -->
    <el-dialog
        v-model="editCourseDialogVisible"
        title="编辑课程"
        width="500px"
    >
        <el-form :model="editCourseForm" :rules="editCourseRules" ref="editCourseFormRef">
            <el-form-item label="课程名称" prop="name">
                <el-input v-model="editCourseForm.name" placeholder="请输入课程名称" />
            </el-form-item>
            <el-form-item label="课程描述">
                <el-input
                    v-model="editCourseForm.description"
                    placeholder="请输入课程描述"
                    type="textarea"
                    rows="3"
                />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="editCourseDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleEditCourse">确定</el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import request from "../../../utils/request";
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();
const route = useRoute();

const isLoggedIn = ref(
    !!(window.localStorage && window.localStorage.getItem("token"))
);

const handleAuthFailure = async (e) => {
    console.error("请求失败", e);
    // 只有真正的 401 未授权错误才跳转登录页
    // 500/网络错误/超时不应清除登录状态
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



// 加载状态
const loading = ref(false);
const classLoading = ref(false);
const studentLoading = ref(false);
const courseLoading = ref(false);

// 课程数据
const courses = ref([]);
const courseSearchKeyword = ref('');

// 课程对话框状态
const addCourseDialogVisible = ref(false);
const editCourseDialogVisible = ref(false);

// 课程表单数据
const addCourseForm = ref({
    name: '',
    description: ''
});

const editCourseForm = ref({
    id: '',
    name: '',
    description: ''
});

// 课程表单验证规则
const addCourseRules = ref({
    name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }]
});

const editCourseRules = ref({
    name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }]
});

// 课程表单引用
const addCourseFormRef = ref(null);
const editCourseFormRef = ref(null);

// 班级列表与当前班级
const classes = ref([]);
const selectedClassId = ref("");

// 班级信息
const className = ref("");
const classCode = ref("");
const createTime = ref("");
const studentCount = ref(0);
const courseName = ref("");
const headTeacher = ref("");

// 学生数据
const students = ref([]);

// 搜索和分页
const searchKeyword = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const totalPages = ref(0);
const totalCount = ref(0);

// 对话框状态
const createClassDialogVisible = ref(false);
const editClassDialogVisible = ref(false);

// 表单数据
const createClassForm = ref({
    name: '',
    course_id: ''
});

const editClassForm = ref({
    name: '',
    code: '',
    course_id: ''
});



// 表单验证规则
const createClassRules = ref({
    name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
    course_id: [{ required: true, message: '请选择课程', trigger: 'change' }]
});

const editClassRules = ref({
    name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
    course_id: [{ required: true, message: '请选择课程', trigger: 'change' }]
});

// 表单引用
const createClassFormRef = ref(null);
const editClassFormRef = ref(null);

const fetchClassList = async () => {
    if (!isLoggedIn.value) return;
    
    classLoading.value = true;
    try {
        const resp = await request.get("/classInfo/class-chart/class-list/");
        classes.value = Array.isArray(resp?.data) ? resp.data : [];

        if (!selectedClassId.value) {
            const fromQuery = route.query && route.query.classId;
            if (fromQuery) {
                selectedClassId.value = String(fromQuery);
            } else if (classes.value.length > 0) {
                selectedClassId.value = String(classes.value[0].id);
            }
        }
    } catch (e) {
        console.error("获取班级列表失败", e);
        ElMessage.error('获取班级列表失败，请稍后重试');
        await handleAuthFailure(e);
    } finally {
        classLoading.value = false;
    }
};

const fetchClassDetail = async () => {
    if (!isLoggedIn.value) return;
    if (!selectedClassId.value) return;
    
    classLoading.value = true;
    try {
        const resp = await request.get(`/classInfo/classes/${selectedClassId.value}/`);
        const data = resp?.data || {};
        className.value = data.name || "";
        classCode.value = data.code || "";
        createTime.value = data.create_time || data.createTime || "";
        courseName.value = data.course_name || data.courseName || "";
        studentCount.value = typeof data.student_count === "number" ? data.student_count : data.studentCount || 0;
        headTeacher.value =
            (data.head_teacher_info && data.head_teacher_info.teacherName) ||
            data.headTeacher ||
            "未设置";
    } catch (e) {
        console.error("获取班级详情失败", e);
        ElMessage.error('获取班级详情失败，请稍后重试');
        await handleAuthFailure(e);
    } finally {
        classLoading.value = false;
    }
};

const normalizeStudent = (s) => {
    const joinTime = s.joinTime || s.join_time || s.created_at || "";
    return {
        id: s.id,
        name: s.name || "",
        studentId: s.studentId || s.student_id || "",
        gender: s.gender || "-",
        phone: s.phone || "",
        email: s.email || "",
        joinTime: joinTime,
    };
};

const fetchStudents = async () => {
    if (!isLoggedIn.value) return;
    if (!selectedClassId.value) {
        students.value = [];
        totalPages.value = 0;
        totalCount.value = 0;
        return;
    }
    
    studentLoading.value = true;
    try {
        const resp = await request.get(`/classInfo/classes/${selectedClassId.value}/students/`, {
            params: {
                page: currentPage.value,
                page_size: pageSize.value,
                search: searchKeyword.value || "",
            },
        });
        const data = resp?.data || {};
        const payload = data.results || data;
        const list = payload.students || payload.results || [];
        students.value = Array.isArray(list) ? list.map(normalizeStudent) : [];

        const p = payload.pagination || {};
        totalPages.value = typeof p.total_pages === "number" ? p.total_pages : 0;
        totalCount.value = typeof data.count === "number" ? data.count : 0;
        if (!totalPages.value && totalCount.value > 0) {
            totalPages.value = Math.ceil(totalCount.value / pageSize.value);
        }
    } catch (e) {
        console.error("获取学生列表失败", e);
        ElMessage.error('获取学生列表失败，请稍后重试');
        await handleAuthFailure(e);
    } finally {
        studentLoading.value = false;
    }
};

// 防抖搜索
const debounceSearch = () => {
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
        searchStudents();
    }, 500);
};

// 搜索学生
const searchStudents = async () => {
    console.log("搜索学生:", searchKeyword.value);
    currentPage.value = 1;
    try {
        await fetchStudents();
    } catch (e) {
        await handleAuthFailure(e);
    }
};

// 改变页码
const changePage = async (page) => {
    if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
        try {
            await fetchStudents();
        } catch (e) {
            await handleAuthFailure(e);
        }
    }
};

// 处理分页大小变化
const handleSizeChange = async (size) => {
    pageSize.value = size;
    currentPage.value = 1;
    try {
        await fetchStudents();
    } catch (e) {
        await handleAuthFailure(e);
    }
};

// 处理当前页码变化
const handleCurrentChange = async (current) => {
    currentPage.value = current;
    try {
        await fetchStudents();
    } catch (e) {
        await handleAuthFailure(e);
    }
};

// 显示创建班级对话框
const showCreateClassDialog = () => {
    createClassForm.value = {
        name: '',
        code: '',
        course_id: ''
    };
    createClassDialogVisible.value = true;
};

// 复制班级代码
const copyClassCode = async () => {
    try {
        await navigator.clipboard.writeText(classCode.value);
        ElMessage.success('班级代码已复制到剪贴板');
    } catch (e) {
        console.error('复制失败', e);
        ElMessage.error('复制失败，请手动复制');
    }
};

// 处理创建班级
const handleCreateClass = async () => {
    if (!isLoggedIn.value) return;
    if (!createClassFormRef.value) return;
    
    createClassFormRef.value.validate(async (valid) => {
        if (!valid) return;
        
        try {
            console.log('开始创建班级...');
            console.log('courses数组:', courses.value);
            
            // 获取教师信息
            console.log('获取教师信息...');
            let teacherId = '';
            try {
                const teacherResp = await request.get("/teacher/profile/");
                console.log('教师信息API响应:', teacherResp);
                const teacherData = teacherResp?.data || {};
                console.log('教师信息数据:', teacherData);
                teacherId = teacherData.teacherId || '';
                console.log('教师ID:', teacherId);
                
                if (!teacherId) {
                    ElMessage.error('获取教师信息失败，请稍后重试');
                    return;
                }
            } catch (e) {
                console.error('获取教师信息失败:', e);
                ElMessage.error('获取教师信息失败，请稍后重试');
                return;
            }
            
            // 获取课程ID和名称
            const courseId = createClassForm.value.course_id;
            console.log('课程ID:', courseId);
            console.log('课程ID类型:', typeof courseId);
            
            // 修复类型不匹配问题，使用String()进行类型转换后比较
            const selectedCourse = courses.value.find(course => String(course.id) === courseId);
            console.log('找到的课程:', selectedCourse);
            
            const courseName = selectedCourse ? selectedCourse.name : '';
            console.log('课程名称:', courseName);
            
            if (!courseName) {
                ElMessage.error('获取课程信息失败，请稍后重试');
                return;
            }
            
            // 直接生成唯一的班级编码，使用时间戳确保唯一性
            console.log('生成班级编码...');
            const timestamp = Date.now().toString().slice(-4);
            // 生成符合固定格式的班级编码：COURSE-课程id-教师id-时间戳
            const code = `COURSE-${courseId}-${teacherId}-${timestamp}`;
            console.log('生成的班级编码:', code);
            
            // 发送创建班级请求
            console.log('发送创建班级请求...');
            try {
                const resp = await request.post("/classInfo/classes/", {
                    name: createClassForm.value.name,
                    code: code,
                    course_name: courseName
                });
                console.log('创建班级响应:', resp);
                
                const newId = resp?.data?.id;
                console.log('新班级ID:', newId);
                
                createClassDialogVisible.value = false;
                
                await fetchClassList();
                if (newId) {
                    selectedClassId.value = String(newId);
                } else if (!selectedClassId.value && classes.value.length > 0) {
                    selectedClassId.value = String(classes.value[0].id);
                }
                await fetchClassDetail();
                await fetchStudents();
                
                ElMessage.success('班级创建成功');
                console.log('班级创建成功');
            } catch (e) {
                console.error('创建班级失败:', e);
                ElMessage.error('班级创建失败，请稍后重试');
                return;
            }
        } catch (e) {
            console.error("创建班级失败", e);
            ElMessage.error('班级创建失败，请稍后重试');
            // 移除跳转到登录页面的逻辑
            // await handleAuthFailure(e);
        }
    });
};

// 显示编辑班级对话框
const showEditClassDialog = () => {
    if (!selectedClassId.value) {
        ElMessage.warning('请先选择一个班级');
        return;
    }
    
    // 查找当前课程对应的ID
    const currentCourse = courses.value.find(course => course.name === courseName.value);
    const courseId = currentCourse ? String(currentCourse.id) : '';
    
    editClassForm.value = {
        name: className.value,
        code: classCode.value,
        course_id: courseId
    };
    editClassDialogVisible.value = true;
};

// 显示添加学生对话框
const showAddStudentDialog = () => {
    if (!selectedClassId.value) {
        ElMessage.warning('请先选择一个班级');
        return;
    }
    addStudentForm.value = { student_id: '', name: '', phone: '', email: '' };
    addStudentDialogVisible.value = true;
};

// 处理编辑班级
const handleEditClass = async () => {
    if (!isLoggedIn.value) return;
    if (!selectedClassId.value) return;
    if (!editClassFormRef.value) return;
    
    editClassFormRef.value.validate(async (valid) => {
        if (!valid) return;
        
        try {
            await request.patch(`/classInfo/classes/${selectedClassId.value}/`, {
                name: editClassForm.value.name,
                code: editClassForm.value.code,
                course_id: editClassForm.value.course_id,
            });
            editClassDialogVisible.value = false;
            await fetchClassDetail();
            ElMessage.success('班级信息更新成功');
        } catch (e) {
            ElMessage.error('班级信息更新失败');
            await handleAuthFailure(e);
        }
    });
};



// 显示删除确认对话框
const showDeleteConfirm = () => {
    if (!selectedClassId.value) {
        ElMessage.warning('请先选择一个班级');
        return;
    }
    
    ElMessageBox.confirm(
        '确定要删除当前班级吗？删除后该班级学生将被移出班级。',
        '删除班级',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(async () => {
        await handleDeleteClass();
    }).catch(() => {
        // 取消删除
    });
};

// 处理删除班级
const handleDeleteClass = async () => {
    if (!isLoggedIn.value) return;
    if (!selectedClassId.value) return;
    
    try {
        await request.delete(`/classInfo/classes/${selectedClassId.value}/`);
        selectedClassId.value = "";
        className.value = "";
        classCode.value = "";
        createTime.value = "";
        studentCount.value = 0;
        courseName.value = "";
        headTeacher.value = "";
        students.value = [];
        totalPages.value = 0;
        totalCount.value = 0;

        await fetchClassList();
        if (classes.value.length > 0) {
            selectedClassId.value = String(classes.value[0].id);
            await fetchClassDetail();
            await fetchStudents();
        }
        
        ElMessage.success('班级删除成功');
    } catch (e) {
        ElMessage.error('班级删除失败');
        await handleAuthFailure(e);
    }
};



// 查看学生
const viewStudent = (studentId) => {
    router.push({
        name: 'class-student-detail',
        params: { studentId: String(studentId) },
        query: selectedClassId.value ? { classId: String(selectedClassId.value) } : {},
    });
};

// 移除学生
const removeStudent = async (studentId) => {
    if (!isLoggedIn.value) return;
    if (!selectedClassId.value) return;
    
    ElMessageBox.confirm(
        '确定要移除这名学生吗？',
        '移除学生',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(async () => {
        try {
            await request.delete(
                `/classInfo/classes/${selectedClassId.value}/students/${studentId}/`
            );
            await fetchClassDetail();
            await fetchStudents();
            ElMessage.success('学生移除成功');
        } catch (e) {
            ElMessage.error('学生移除失败');
            await handleAuthFailure(e);
        }
    }).catch(() => {
        // 取消移除
    });
};

const onClassChange = async () => {
    currentPage.value = 1;
    try {
        await fetchClassDetail();
        await fetchStudents();
    } catch (e) {
        await handleAuthFailure(e);
    }
};

// 获取课程列表
const fetchCourses = async () => {
    if (!isLoggedIn.value) return;
    
    courseLoading.value = true;
    try {
        const resp = await request.get("/knowledge/courses/");
        courses.value = Array.isArray(resp?.data) ? resp.data : [];
    } catch (e) {
        console.error("获取课程列表失败", e);
        ElMessage.error('获取课程列表失败，请稍后重试');
        await handleAuthFailure(e);
    } finally {
        courseLoading.value = false;
    }
};

// 防抖课程搜索
const debounceCourseSearch = () => {
    clearTimeout(window.courseSearchTimeout);
    window.courseSearchTimeout = setTimeout(() => {
        searchCourses();
    }, 500);
};

// 搜索课程
const searchCourses = async () => {
    if (!isLoggedIn.value) return;
    
    courseLoading.value = true;
    try {
        const resp = await request.get("/knowledge/courses/", {
            params: {
                search: courseSearchKeyword.value || ""
            }
        });
        courses.value = Array.isArray(resp?.data) ? resp.data : [];
    } catch (e) {
        console.error("搜索课程失败", e);
        ElMessage.error('搜索课程失败，请稍后重试');
        await handleAuthFailure(e);
    } finally {
        courseLoading.value = false;
    }
};

// 显示添加课程对话框
const showAddCourseDialog = () => {
    addCourseForm.value = {
        name: '',
        description: ''
    };
    addCourseDialogVisible.value = true;
};

// 处理添加课程
const handleAddCourse = async () => {
    if (!isLoggedIn.value) return;
    if (!addCourseFormRef.value) return;
    
    addCourseFormRef.value.validate(async (valid) => {
        if (!valid) return;
        
        loading.value = true;
        try {
            const resp = await request.post("/knowledge/courses/", {
                name: addCourseForm.value.name,
                description: addCourseForm.value.description || ''
            });
            addCourseDialogVisible.value = false;
            await fetchCourses();
            ElMessage.success('课程添加成功');
        } catch (e) {
            console.error("添加课程失败", e);
            ElMessage.error('添加课程失败，请稍后重试');
            // 暂时移除跳转到登录页面的逻辑
            // await handleAuthFailure(e);
        } finally {
            loading.value = false;
        }
    });
};

// 编辑课程
const editCourse = (course) => {
    editCourseForm.value = {
        id: course.id,
        name: course.name,
        description: course.description || ''
    };
    editCourseDialogVisible.value = true;
};

// 处理编辑课程
const handleEditCourse = async () => {
    if (!isLoggedIn.value) return;
    if (!editCourseFormRef.value) return;
    
    editCourseFormRef.value.validate(async (valid) => {
        if (!valid) return;
        
        loading.value = true;
        try {
            await request.patch(`/knowledge/courses/${editCourseForm.value.id}/`, {
                name: editCourseForm.value.name,
                description: editCourseForm.value.description
            });
            editCourseDialogVisible.value = false;
            await fetchCourses();
            ElMessage.success('课程编辑成功');
        } catch (e) {
            console.error("编辑课程失败", e);
            ElMessage.error('编辑课程失败，请稍后重试');
            await handleAuthFailure(e);
        } finally {
            loading.value = false;
        }
    });
};

// 删除课程
const deleteCourse = async (courseId) => {
    if (!isLoggedIn.value) return;
    
    ElMessageBox.confirm(
        '确定要删除这门课程吗？删除后相关班级可能会受到影响。',
        '删除课程',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(async () => {
        loading.value = true;
        try {
            await request.delete(`/knowledge/courses/${courseId}/`);
            await fetchCourses();
            ElMessage.success('课程删除成功');
        } catch (e) {
            console.error("删除课程失败", e);
            ElMessage.error('删除课程失败，请稍后重试');
            // 移除跳转到登录页面的逻辑
            // await handleAuthFailure(e);
        } finally {
            loading.value = false;
        }
    }).catch(() => {
        // 取消删除
    });
};

// 组件挂载时执行
onMounted(async () => {
    try {
        await fetchCourses();
        await fetchClassList();
        await fetchClassDetail();
        await fetchStudents();
    } catch (e) {
        await handleAuthFailure(e);
    }
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

/* 班级选择器样式 */
.class-select {
    min-width: 300px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    transition: all 0.3s ease;
}

.class-select:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.class-select:focus-within {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

/* 搜索输入框样式 */
.search-input {
    min-width: 250px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    transition: all 0.3s ease;
}

.search-input:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.search-input:focus-within {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
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
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #f0f0f0;
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
    background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
    padding: 15px;
    text-align: left;
    font-weight: 600;
    color: #1e3a8a;
    border-bottom: 2px solid #3b82f6;
    font-size: 14px;
    position: relative;
    transition: all 0.3s ease;
}

.student-table th:hover {
    background: linear-gradient(135deg, #e0f2fe 0%, #bfdbfe 100%);
    color: #2563eb;
}

.student-table td {
    padding: 15px;
    border-bottom: 1px solid #e2e8f0;
    color: #4b5563;
    font-size: 14px;
    transition: all 0.3s ease;
}

.student-table tr:last-child td {
    border-bottom: none;
}

.student-table tr {
    transition: all 0.3s ease;
}

.student-table tr:hover {
    background-color: #f0f9ff;
    transform: translateX(2px);
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

/* Element Plus 表格样式覆盖 */
:deep(.el-table) {
    border-radius: 8px;
    overflow: hidden;
}

:deep(.el-table__header-wrapper) {
    border-radius: 8px 8px 0 0;
}

:deep(.el-table__body-wrapper) {
    border-radius: 0 0 8px 8px;
}

:deep(.el-table__row) {
    transition: all 0.3s ease;
}

:deep(.el-table__row:hover) {
    background-color: #f0f9ff !important;
    transform: translateX(2px);
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

:deep(.el-table th) {
    background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%) !important;
    color: #1e3a8a !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #3b82f6 !important;
}

:deep(.el-table td) {
    color: #4b5563 !important;
    border-bottom: 1px solid #e2e8f0 !important;
}

/* 分页样式 */
.pagination-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    margin-top: 20px;
    padding: 20px;
    border-top: 1px solid #e2e8f0;
    border-radius: 0 0 8px 8px;
    background-color: #f8fafc;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .pagination-container {
    transform: translateX(3px);
    opacity: 1;
    background-color: #f0f9ff;
}

.pagination-btn {
    padding: 10px 16px;
    border: 1px solid #e2e8f0;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    color: #4b5563;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.pagination-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border-color: #3b82f6;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    color: #94a3b8;
}

.pagination-info {
    color: #64748b;
    font-size: 14px;
    font-weight: 500;
}

/* Element Plus 分页样式覆盖 */
:deep(.el-pagination) {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
}

:deep(.el-pagination__item) {
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
}

:deep(.el-pagination__item:hover) {
    border-color: #3b82f6;
    color: #3b82f6;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

:deep(.el-pagination__item.active) {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    border-color: #3b82f6;
    color: white;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

:deep(.el-pagination__button) {
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
}

:deep(.el-pagination__button:hover) {
    border-color: #3b82f6;
    color: #3b82f6;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

:deep(.el-pagination__button:disabled) {
    opacity: 0.5;
    cursor: not-allowed;
}

:deep(.el-pagination__jump) {
    color: #64748b;
    font-size: 14px;
}

:deep(.el-pagination__editor) {
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
}

:deep(.el-pagination__editor:hover) {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* 课程管理样式 */
.course-management-card {
    margin-bottom: 30px;
}

.course-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 10px;
}

.course-search-input {
    min-width: 250px;
    max-width: 400px;
}

.course-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.course-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 20px;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.course-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(59, 130, 246, 0.15);
    border-color: #3b82f6;
}

.course-card-body {
    flex: 1;
    margin-bottom: 15px;
}

.course-card-body h4 {
    margin: 0 0 10px 0;
    color: #1e3a8a;
    font-size: 16px;
    font-weight: 600;
}

.course-description {
    margin: 0 0 15px 0;
    color: #64748b;
    font-size: 14px;
    line-height: 1.4;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.course-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #94a3b8;
}

.course-card-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    padding-top: 15px;
    border-top: 1px solid #f1f5f9;
}

.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #64748b;
}

.empty-state p {
    margin-bottom: 20px;
    font-size: 16px;
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

    .course-actions {
        flex-direction: column;
        align-items: stretch;
    }

    .course-search-input {
        max-width: 100%;
    }

    .course-list {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
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

    .course-list {
        grid-template-columns: 1fr;
    }

    .course-card {
        padding: 15px;
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