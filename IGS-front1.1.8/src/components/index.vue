<template>
    <div class="intelligent-platform">
        <!-- 顶部导航栏 -->
        <header class="header">
            <h1>智能导学系统</h1>

            <div class="user-info">
                <div class="avatar-container">
                    <div
                        class="avatar"
                        :class="isTeacher ? 'avatar-teacher' : 'avatar-student'"
                    >
                        <span class="icon">{{ isTeacher ? "👨‍🏫" : "👨‍🎓" }}</span>
                    </div>
                    <div class="user-basic">
                        <h2>{{ isTeacher ? teacherName : userName }}</h2>
                        <p class="user-id">
                            {{ isTeacher ? teacherId : studentId }}
                        </p>
                    </div>
                </div>
                <button class="logout-btn" @click="logout">退出</button>
            </div>
        </header>

        <!-- 主内容区域 -->
        <main class="content-wrapper">
            <!-- 加载提示 -->
            <div v-if="loading" class="loading-container">
                <div class="loading-spinner"></div>
                <p>正在加载...</p>
            </div>

            <!-- 角色选择界面（仅管理员可见） -->
            <div v-else-if="userRole === 'admin'" class="role-selection">
                <h2 class="selection-title">请选择身份</h2>
                <div class="role-options">
                    <button class="role-option" @click="switchToTeacher">
                        <span class="role-icon">👨‍🏫</span>
                        <span class="role-name">教师</span>
                    </button>
                    <button class="role-option" @click="switchToStudent">
                        <span class="role-icon">👨‍🎓</span>
                        <span class="role-name">学生</span>
                    </button>
                </div>

                <!-- 账号搜索功能 -->
                <div class="account-search">
                    <input
                        type="text"
                        v-model="accountSearch"
                        placeholder="搜索账号ID或姓名"
                        class="search-input"
                    />
                    <button
                        class="search-btn"
                        @click="searchAccount"
                        :disabled="searchLoading"
                    >
                        {{ searchLoading ? "搜索中..." : "搜索" }}
                    </button>

                    <!-- 搜索结果 -->
                    <div v-if="searchResult" class="search-result">
                        <p>
                            找到账号: {{ searchResult.name }} ({{
                                searchResult.role
                            }})
                        </p>
                    </div>
                </div>
            </div>

            <!-- 普通用户重定向提示 -->
            <div v-else class="redirect-message">
                <p>
                    正在为您重定向到{{ isTeacher ? "教师" : "学生" }}端首页...
                </p>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

// 路由实例
const router = useRouter();

// 身份与权限相关状态
const isTeacher = ref(true);
const userRole = ref("teacher"); // 可能的值: student, teacher, admin
const loading = ref(true);
const accountSearch = ref("");
const searchResult = ref(null);
const searchLoading = ref(false);

// 用户信息
const teacherName = ref("李教授");
const teacherId = ref("T2023001");
const userName = ref("张三");
const studentId = ref("S2023001");

// 模拟账号数据库
const mockAccounts = [
    { id: "T2023001", name: "李教授", role: "teacher" },
    { id: "T2023002", name: "王老师", role: "teacher" },
    { id: "S2023001", name: "张三", role: "student" },
    { id: "S2023002", name: "李四", role: "student" },
    { id: "S2023003", name: "王五", role: "student" },
    { id: "A2023001", name: "管理员", role: "admin" },
];

// 账号搜索功能
const searchAccount = async () => {
    if (!accountSearch.value.trim()) {
        alert("请输入账号ID或姓名");
        return;
    }

    searchLoading.value = true;
    searchResult.value = null;

    // 模拟搜索延迟
    await new Promise((resolve) => setTimeout(resolve, 500));

    // 根据账号ID或姓名搜索
    const result = mockAccounts.find(
        (account) =>
            account.id
                .toLowerCase()
                .includes(accountSearch.value.toLowerCase()) ||
            account.name
                .toLowerCase()
                .includes(accountSearch.value.toLowerCase())
    );

    if (result) {
        searchResult.value = result;
    } else {
        alert("未找到匹配的账号");
    }

    searchLoading.value = false;
};

// 切换到教师身份
const switchToTeacher = () => {
    if (userRole.value === "admin") {
        isTeacher.value = true;
        userRole.value = "teacher";
        router.push("/teacher/index");
    } else {
        alert("只有管理员可以切换身份");
    }
};

// 切换到学生身份
const switchToStudent = () => {
    if (userRole.value === "admin") {
        isTeacher.value = false;
        userRole.value = "student";
        router.push("/student/index");
    } else {
        alert("只有管理员可以切换身份");
    }
};

// 退出登录
const logout = () => {
    // 实际项目中这里应该清除登录状态和token
    router.push("/login");
};

// 页面加载时执行
onMounted(() => {
    // 模拟身份验证和数据加载
    setTimeout(() => {
        loading.value = false;

        // 根据用户角色自动重定向
        if (userRole.value !== "admin") {
            // 延迟重定向，让用户看到提示信息
            setTimeout(() => {
                if (isTeacher.value) {
                    router.push("/teacher/index");
                } else {
                    router.push("/student/index");
                }
            }, 1000);
        }
    }, 800);
});
</script>

<style scoped>
/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Microsoft YaHei", Arial, sans-serif;
}

.intelligent-platform {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    flex-direction: column;
}

/* 顶部导航栏样式 */
.header {
    background: rgba(255, 255, 255, 0.95);
    padding: 20px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 0 0 15px 15px;
    margin-bottom: 40px;
}

.header h1 {
    font-size: 28px;
    color: #2d3748;
    font-weight: 600;
    background: linear-gradient(90deg, #667eea, #764ba2);
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 20px;
}

.avatar-container {
    display: flex;
    align-items: center;
    gap: 12px;
}

.avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    transition: all 0.3s ease;
}

.avatar-teacher {
    background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
}

.avatar-student {
    background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.user-basic h2 {
    font-size: 18px;
    color: #2d3748;
    font-weight: 500;
}

.user-id {
    font-size: 14px;
    color: #718096;
}

.logout-btn {
    padding: 10px 20px;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.logout-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
}

/* 主内容区域样式 */
.content-wrapper {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
}

/* 加载提示样式 */
.loading-container {
    text-align: center;
    color: white;
}

.loading-spinner {
    width: 60px;
    height: 60px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* 角色选择界面样式 */
.role-selection {
    background: rgba(255, 255, 255, 0.95);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    text-align: center;
    backdrop-filter: blur(10px);
    min-width: 500px;
}

.selection-title {
    font-size: 24px;
    color: #2d3748;
    margin-bottom: 30px;
    font-weight: 600;
}

.role-options {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-bottom: 40px;
}

.role-option {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 15px;
    padding: 30px 40px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    min-width: 150px;
}

.role-option:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
    border-color: #667eea;
}

.role-icon {
    font-size: 48px;
}

.role-name {
    font-size: 18px;
    color: #2d3748;
    font-weight: 500;
}

/* 账号搜索样式 */
.account-search {
    display: flex;
    flex-direction: column;
    gap: 15px;
    align-items: center;
}

.search-input {
    padding: 12px 20px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 16px;
    width: 100%;
    max-width: 400px;
    transition: all 0.3s ease;
}

.search-input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-btn {
    padding: 12px 30px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.search-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.search-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.search-result {
    background: #f0f4ff;
    padding: 15px 20px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    font-size: 14px;
    color: #4a5568;
    margin-top: 10px;
    max-width: 400px;
    width: 100%;
}

/* 重定向提示样式 */
.redirect-message {
    background: rgba(255, 255, 255, 0.95);
    padding: 40px 60px;
    border-radius: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.redirect-message p {
    font-size: 20px;
    color: #2d3748;
    font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .header {
        padding: 15px 20px;
        flex-direction: column;
        gap: 15px;
    }

    .header h1 {
        font-size: 24px;
    }

    .role-selection {
        min-width: auto;
        padding: 30px 20px;
    }

    .role-options {
        flex-direction: column;
    }

    .role-option {
        min-width: auto;
        width: 100%;
    }

    .redirect-message {
        padding: 30px 20px;
    }

    .redirect-message p {
        font-size: 18px;
    }
}
</style>
