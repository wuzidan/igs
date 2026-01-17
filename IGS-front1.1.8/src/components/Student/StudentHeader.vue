<template>
    <header class="header" :class="{ 'auth-header': !isLoggedIn }">
        <div class="header-left">
            <h1>{{ title }}</h1>
        </div>

        <div class="user-info" v-if="isLoggedIn">
            <!-- 用户信息内容 -->
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

        <div class="auth-buttons" v-else>
            <button class="auth-btn login-btn" @click="goToLogin">登录</button>
            <button class="auth-btn register-btn" @click="goToRegister">
                注册
            </button>
        </div>
    </header>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../../api/index";

// 从父组件接收标题属性
const props = defineProps({
    title: {
        type: String,
        required: true,
    },
});

// 路由实例
const router = useRouter();

// 登录状态管理
const isLoggedIn = ref(Boolean(window.localStorage && window.localStorage.getItem("token")));

// 用户信息
const userName = ref("未知用户");
const studentId = ref("未知学号");
const userAvatar = ref("👨‍💻");
const userAvatarUrl = ref(""); // 头像URL
const className = ref(""); // 班级
const major = ref(""); // 专业
const email = ref(""); // 邮箱

// 获取用户信息
const fetchUserInfo = () => {
    if (!isLoggedIn.value) {
        return Promise.resolve();
    }
    return api
        .getStudentinfo()
        .then((res) => {
            const userData = res.data;
            // 填充用户信息
            userName.value = userData.userName || "未知用户";
            studentId.value = userData.studentId || "未知学号";
            userAvatar.value = userData.userAvatar || "👨‍💻";
            userAvatarUrl.value = userData.userAvatarUrl || "";
            className.value = userData.className || "";
            major.value = userData.major || "";
            email.value = userData.email || "";
        })
        .catch((err) => {
            console.error("获取用户信息失败:", err);
            isLoggedIn.value = false;
            window.localStorage && window.localStorage.removeItem("token");
            router.push("/login");
        });
};

// 退出登录
const logout = () => {
    isLoggedIn.value = false;
    window.localStorage && window.localStorage.removeItem("token");
    // 清空用户信息
    userName.value = "";
    studentId.value = "";
    userAvatarUrl.value = "";
    className.value = "";
    major.value = "";
    email.value = "";

    // 跳转到登录页面
    router.push("/login");
};

// 跳转功能
const goToHome = () => {
    router.push("/student/index");
};

const goToLogin = () => {
    router.push({ name: "Login", params: { type: "login" } });
};

const goToRegister = () => {
    router.push({ name: "Register", params: { type: "register" } });
};

// 页面加载时初始化
onMounted(() => {
    fetchUserInfo();
});
</script>

<style scoped>
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

.header-left {
    display: flex;
    align-items: center;
    gap: 15px;
}

.user-info {
    display: flex;
    align-items: center;
    transition: transform 0.3s ease;
}

.avatar-container {
    display: flex;
    align-items: center;
    margin-right: 15px;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
    transition: transform 0.3s ease;
}

.avatar:hover {
    transform: scale(1.1);
}

.avatar-default {
    background: linear-gradient(135deg, #3498db, #9b59b6);
    color: white;
}

.avatar-custom {
    background-color: #f0f0f0;
    overflow: hidden;
}

.user-avatar {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.user-basic {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin: 0;
}

.user-basic h2 {
    font-size: 16px;
    margin: 0;
    font-weight: 500;
    color: #2c3e50;
}

.user-id {
    font-size: 12px;
    color: #7f8c8d;
    margin: 2px 0 0 0;
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

.auth-header {
    justify-content: space-between;
}

.auth-buttons {
    display: flex;
    gap: 10px;
}

.auth-btn {
    padding: 9px 18px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.login-btn {
    background: linear-gradient(90deg, #3498db, #2980b9);
    color: white;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.login-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
    background: linear-gradient(90deg, #2980b9, #3498db);
}

.register-btn {
    background: linear-gradient(90deg, #2ecc71, #27ae60);
    color: white;
    box-shadow: 0 2px 8px rgba(46, 204, 113, 0.3);
}

.register-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(46, 204, 113, 0.4);
    background: linear-gradient(90deg, #27ae60, #2ecc71);
}

/* 响应式调整 */
@media (max-width: 768px) {
    .header {
        flex-direction: column;
        gap: 10px;
        padding: 15px;
    }

    .user-info {
        flex-direction: column;
        gap: 10px;
    }

    .avatar-container {
        margin-right: 0;
    }

    .auth-buttons {
        width: 100%;
        justify-content: center;
    }
}
</style>
