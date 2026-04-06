<template>
    <div class="login-page">
        <!-- 背景装饰元素 -->
        <div class="bg-decoration top-left"></div>
        <div class="bg-decoration bottom-right"></div>

        <div class="login-container">
            <div class="login-card">
                <!-- 登录卡片头部 -->
                <div class="login-header">
                    <div class="logo-container">
                        <div class="logo-icon">📚</div>
                        <h1>智能导学系统</h1>
                    </div>
                    <p class="login-desc">请登录您的账号以继续使用系统</p>
                </div>


                <!-- 登录表单 -->
                <form class="login-form" @submit.prevent="handleLogin">
                    <div class="form-group">
                        <label for="username" class="form-label">用户名</label>
                        <div class="input-wrapper">
                            <span class="input-icon">👤</span>
                            <input
                                type="text"
                                id="username"
                                v-model="username"
                                placeholder="请输入用户名"
                                required
                                class="form-input"
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="password" class="form-label">密码</label>
                        <div class="input-wrapper">
                            <span class="input-icon">🔒</span>
                            <input

                                :type="showPassword ? 'text' : 'password'"

                                id="password"
                                v-model="password"
                                placeholder="请输入密码"
                                required
                                class="form-input"
                            />
                            <button
                                type="button"
                                class="toggle-password"
                                @click="showPassword = !showPassword"
                            >
                                {{ showPassword ? "👁️" : "👁️‍🗨️" }}
                            </button>
                        </div>
                    </div>



             <!-- 错误提示 -->
             <div v-if="errorMessage" class="error-message" style="color: red;">
                    ⚠️ {{ errorMessage }}
                </div>

                    <div class="form-options">
                        <label class="remember-me">
                            <input type="checkbox" v-model="rememberMe" />
                            <span>记住我</span>
                        </label>
                        <a href="change-password" class="forgot-password"
                            >忘记密码?</a
                        >
                    </div>


                    <button type="submit" class="login-btn" :disabled="isLoading">
                        {{ isLoading ? "登录中..." : "登录" }}
                    </button>

                </form>

                <!-- 其他登录选项 -->
                <div class="other-options">
                    <div class="divider">
                        <span>或使用以下方式登录</span>
                    </div>
                    <div class="social-login">
                        <a class="social-btn" href="wechat-login">📱</a>
                        <button class="social-btn" title="QQ登录">🐧</button>
                        <button class="social-btn" title="校园网登录">
                            🏫
                        </button>
                    </div>
                </div>

                <!-- 注册提示 -->
                <div class="register-prompt">
                    还没有账号? <a href="Register">立即注册</a>
                </div>
            </div>
        </div>

        <!-- 页脚信息 -->
        <footer class="login-footer">
            <p>© 2025 智慧题库系统 版权所有</p>
            <div class="footer-links">
                <a href="#">使用条款</a>
                <a href="#">隐私政策</a>
                <a href="#">帮助中心</a>
            </div>
        </footer>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import request from "../../utils/request";

// 表单数据
const username = ref("");
const password = ref("");
const rememberMe = ref(false);
const showPassword = ref(false);
const errorMessage = ref("");
const isLoading = ref(false);


const router = useRouter();

// 登录处理
const handleLogin = async () => {
        // 验证输入
        if (!username.value.trim()) {
        errorMessage.value = "请输入用户名";
        return;
    }
    
    if (!password.value.trim()) {
        errorMessage.value = "请输入密码";
        return;
    }

    isLoading.value = true;
    errorMessage.value = "";

    try {
        window.localStorage && window.localStorage.removeItem("token");
        console.log("登录请求前 - localStorage token:", window.localStorage ? window.localStorage.getItem("token") : null);

        const resp = await request.post("/api/user/login/", {
            username: username.value,
            password: password.value,
        });

        console.log("登录响应:", resp.data);
        const token = resp?.data?.token;
        if (token) {
            window.localStorage && window.localStorage.setItem("token", token);
            console.log("登录成功后 - localStorage token:", window.localStorage ? window.localStorage.getItem("token") : null);
        }

        const userType = resp?.data?.userType;
        console.log("登录成功 - userType:", userType);
        if (userType === "admin") {
            console.log("管理员登录成功");
            router.push("/teacher/index");
        } else if (userType === "teacher") {
            console.log("教师登录成功");
            router.push("/teacher/index");
        } else {
            console.log("学生登录成功");
            router.push("/student/index");
        }
    } catch (e) {
        window.localStorage && window.localStorage.removeItem("token");
        console.error("登录失败", e);
        // 根据错误类型显示不同的错误信息
        if (e.response) {
            // 服务器返回错误
            const status = e.response.status;
            const data = e.response.data;
            console.error("登录失败 - 服务器错误:", status, data);
            
            if (status === 401) {
                errorMessage.value = "用户名或密码错误，请重新输入";
            } else if (status === 400) {
                errorMessage.value = data.detail || "请求参数错误";
            } else if (status === 404) {
                errorMessage.value = "用户不存在";
            } else if (status === 429) {
                errorMessage.value = "登录尝试次数过多，请稍后再试";
            } else if (status >= 500) {
                errorMessage.value = "服务器错误，请稍后再试";
            } else {
                errorMessage.value = data.detail || "登录失败，请稍后再试";
            }
        } else if (e.request) {
            // 请求已发送但没有响应
            console.error("登录失败 - 网络错误:", e.request);
            errorMessage.value = "网络连接失败，请检查网络设置";
        } else {
            // 其他错误
            console.error("登录失败 - 其他错误:", e.message);
            errorMessage.value = "登录失败，请稍后再试";
        }
        
        // 清空密码字段
        password.value = "";
    }
    finally {
        isLoading.value = false;
    }

};
</script>

<style scoped>
/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}

.login-page {
    min-height: 100vh;
    background-color: #f4f7f9;
    position: relative;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
    position: absolute;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    filter: blur(100px);
    z-index: 0;
}

.top-left {
    top: -250px;
    left: -250px;
    background: linear-gradient(
        135deg,
        rgba(52, 152, 219, 0.2),
        rgba(155, 89, 182, 0.1)
    );
}

.bottom-right {
    bottom: -250px;
    right: -250px;
    background: linear-gradient(
        135deg,
        rgba(46, 204, 113, 0.2),
        rgba(52, 152, 219, 0.1)
    );
}

/* 登录容器 */
.login-container {
    width: 100%;
    max-width: 420px;
    position: relative;
    z-index: 1;
}

/* 登录卡片 */
.login-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(240, 249, 255, 0.8);
    transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
    position: relative;
    overflow: hidden;
}

.login-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 4px;
    background: linear-gradient(180deg, #60a5fa 0%, #2563eb 100%);
}

.login-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(59, 130, 246, 0.15);
}

/* 登录头部 */
.login-header {
    text-align: center;
    margin-bottom: 30px;
}

.logo-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 15px;
}

.logo-icon {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3498db 0%, #9b59b6 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    margin-bottom: 15px;
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    transition: transform 0.3s ease;
}

.login-card:hover .logo-icon {
    transform: scale(1.05) rotate(5deg);
}

.login-header h1 {
    font-size: 24px;
    font-weight: 600;
    background: linear-gradient(90deg, #2c3e50, #34495e);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 8px;
}

.login-desc {
    color: #7f8c8d;
    font-size: 14px;
}

/* 表单样式 */
.login-form {
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 20px;
}

.form-label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: #334155;
    font-weight: 500;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.input-icon {
    position: absolute;
    left: 12px;
    color: #94a3b8;
    font-size: 16px;
}

.form-input {
    width: 100%;
    padding: 12px 12px 12px 40px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    background-color: #fff;
    font-size: 15px;
    color: #1e293b;
    transition: all 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: #60a5fa;
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2);
}

.form-input::placeholder {
    color: #94a3b8;
}

.toggle-password {
    position: absolute;
    right: 12px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: #94a3b8;
    transition: color 0.3s ease;
}

.toggle-password:hover {
    color: #3b82f6;
}

/* 表单选项 */
.form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    font-size: 14px;
}

.remember-me {
    display: flex;
    align-items: center;
    cursor: pointer;
    color: #334155;
}

.remember-me input {
    margin-right: 6px;
    accent-color: #3b82f6;
}

.forgot-password {
    color: #3b82f6;
    text-decoration: none;
    transition: all 0.3s ease;
    position: relative;
    padding-bottom: 2px;
}

.forgot-password::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0;
    height: 1px;
    background-color: #3b82f6;
    transition: width 0.3s ease;
}

.forgot-password:hover {
    color: #2563eb;
}

.forgot-password:hover::after {
    width: 100%;
}

/* 登录按钮 */
.login-btn {
    width: 100%;
    padding: 13px;
    background: linear-gradient(90deg, #3498db 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.login-btn::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.2),
        transparent
    );
    transition: all 0.6s ease;
}

.login-btn:hover {
    background: linear-gradient(90deg, #2563eb 0%, #3498db 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.login-btn:hover::before {
    left: 100%;
}

/* 其他登录选项 */
.other-options {
    margin: 25px 0;
}

.divider {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.divider::before,
.divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background-color: #e2e8f0;
}

.divider span {
    padding: 0 15px;
    font-size: 13px;
    color: #94a3b8;
}

.social-login {
    display: flex;
    justify-content: center;
    gap: 15px;
}

.social-btn {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    border: none;
    background-color: #f1f5f9;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.social-btn:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.social-btn:nth-child(1):hover {
    background-color: #4cd964;
    color: white;
}

.social-btn:nth-child(2):hover {
    background-color: #0099ff;
    color: white;
}

.social-btn:nth-child(3):hover {
    background-color: orange;
    color: white;
}

/* 注册提示 */
.register-prompt {
    text-align: center;
    font-size: 14px;
    color: #64748b;
}

.register-prompt a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.register-prompt a:hover {
    color: #2563eb;
}

/* 页脚 */
.login-footer {
    position: relative;
    z-index: 1;
    margin-top: 40px;
    text-align: center;
}

.login-footer p {
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 10px;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 20px;
}

.footer-links a {
    color: #94a3b8;
    text-decoration: none;
    font-size: 12px;
    transition: color 0.3s ease;
}

.footer-links a:hover {
    color: #3b82f6;
}

/* 响应式调整 */
@media (max-width: 480px) {
    .login-card {
        padding: 25px 20px;
    }

    .logo-icon {
        width: 60px;
        height: 60px;
        font-size: 24px;
    }

    .login-header h1 {
        font-size: 22px;
    }

    .form-input {
        padding: 11px 11px 11px 38px;
        font-size: 14px;
    }

    .login-btn {
        padding: 12px;
        font-size: 15px;
    }
}
</style>
