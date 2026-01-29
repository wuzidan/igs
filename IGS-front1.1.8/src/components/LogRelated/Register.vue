<template>
    <div class="register-page">
        <div class="register-container">
            <div class="register-card">
                <div class="card-header">
                    <h2>用户注册</h2>
                    <p>创建账号，开始您的知识管理之旅</p>
                </div>

                <form class="register-form" @submit.prevent="handleRegister">
                    <div class="form-group">
                        <label for="username" class="form-label">用户名</label>
                        <div class="input-container">
                            <span class="input-icon">👤</span>
                            <input
                                type="text"
                                id="username"
                                v-model="username"
                                class="form-input"
                                placeholder="请输入您的用户名（2-10个字符）"
                                required
                                :class="{ 'input-error': usernameError }"
                            />
                        </div>
                        <p class="error-message" v-if="usernameError">
                            {{ usernameError }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="phone" class="form-label">手机号</label>
                        <div class="input-container">
                            <span class="input-icon">📱</span>
                            <input
                                type="tel"
                                id="phone"
                                v-model="phone"
                                class="form-input"
                                placeholder="请输入您的手机号"
                                required
                                :class="{ 'input-error': phoneError }"
                            />
                        </div>
                        <p class="error-message" v-if="phoneError">
                            {{ phoneError }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="userid" class="form-label">用户ID</label>
                        <div class="input-container">
                            <span class="input-icon">🆔</span>
                            <input
                                type="text"
                                id="userid"
                                v-model="userId"
                                class="form-input"
                                placeholder="请输入用户ID（字母或数字，5-15位）"
                                required
                                :class="{ 'input-error': userIdError }"
                            />
                        </div>
                        <p class="error-message" v-if="userIdError">
                            {{ userIdError }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="password" class="form-label">密码</label>
                        <div class="input-container">
                            <span class="input-icon">🔒</span>
                            <input
                                :type="showPassword ? 'text' : 'password'"
                                id="password"
                                v-model="password"
                                class="form-input"
                                placeholder="请设置密码（至少6位，包含字母和数字）"
                                required
                                :class="{ 'input-error': passwordError }"
                            />
                            <button
                                type="button"
                                class="toggle-password"
                                @click="showPassword = !showPassword"
                            >
                                {{ showPassword ? "🙈" : "👁️" }}
                            </button>
                        </div>
                        <p class="error-message" v-if="passwordError">
                            {{ passwordError }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="confirmPassword" class="form-label"
                            >确认密码</label
                        >
                        <div class="input-container">
                            <span class="input-icon">🔄</span>
                            <input
                                :type="showPassword ? 'text' : 'password'"
                                id="confirmPassword"
                                v-model="confirmPassword"
                                class="form-input"
                                placeholder="请再次输入密码"
                                required
                                :class="{ 'input-error': confirmPasswordError }"
                            />
                        </div>
                        <p class="error-message" v-if="confirmPasswordError">
                            {{ confirmPasswordError }}
                        </p>
                    </div>

                    <div class="form-group terms-group">
                        <input
                            type="checkbox"
                            id="terms"
                            v-model="agreeTerms"
                            :class="{ 'input-error': termsError }"
                        />
                        <label for="terms" class="terms-label">
                            我已阅读并同意<a href="#" class="terms-link"
                                >用户协议</a
                            >和<a href="#" class="terms-link">隐私政策</a>
                        </label>
                        <p class="error-message" v-if="termsError">
                            {{ termsError }}
                        </p>
                    </div>

                    <button type="submit" class="register-btn float-animation">
                        <span class="btn-text">注册账号</span>
                        <span class="btn-icon">→</span>
                    </button>
                </form>

                <div class="login-link">
                    已有账号？<a href="/Login" class="link">立即登录</a>
                </div>
            </div>
        </div>

        <!-- 注册成功弹窗 -->
        <div class="modal" v-if="showSuccessModal">
            <div class="modal-content">
                <div class="success-icon">✓</div>
                <h3>注册成功！</h3>
                <p>您的账号已创建完成，即将跳转到登录页面</p>
                <button class="modal-btn" @click="handleConfirm">确定</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const agreeTerms = ref(false);
const showPassword = ref(false);
const showSuccessModal = ref(false);

const router = useRouter();

const handleConfirm = () => {
    showSuccessModal.value = false;
    router.push("/login");
};

// 错误信息
const usernameError = ref("");
const phoneError = ref("");
const userIdError = ref("");
const passwordError = ref("");
const confirmPasswordError = ref("");
const termsError = ref("");

// 验证表单
const validateForm = () => {
    let isValid = true;

    // 验证用户名（优化规则）
    if (!username.value.trim()) {
        usernameError.value = "用户名不能为空";
        isValid = false;
    } else if (username.value.length < 2 || username.value.length > 10) {
        usernameError.value = "用户名长度必须在2-10个字符之间";
        isValid = false;
    } else if (/[^\u4e00-\u9fa5a-zA-Z0-9_]/.test(username.value)) {
        usernameError.value = "用户名只能包含中文、字母、数字和下划线";
        isValid = false;
    } else {
        usernameError.value = "";
    }

    // 验证手机号（新增）
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phone.value.trim()) {
        phoneError.value = "手机号不能为空";
        isValid = false;
    } else if (!phoneRegex.test(phone.value)) {
        phoneError.value = "请输入有效的手机号";
        isValid = false;
    } else {
        phoneError.value = "";
    }

    // 验证用户ID
    const userIdRegex = /^[a-zA-Z0-9]+$/;
    if (!userId.value.trim()) {
        userIdError.value = "用户ID不能为空";
        isValid = false;
    } else if (!userIdRegex.test(userId.value)) {
        userIdError.value = "用户ID只能包含字母和数字";
        isValid = false;
    } else if (userId.value.length < 5 || userId.value.length > 15) {
        userIdError.value = "用户ID长度必须在5-15个字符之间";
        isValid = false;
    } else {
        userIdError.value = "";
    }

    // 验证密码（增强规则）
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{6,}$/;
    if (!password.value) {
        passwordError.value = "密码不能为空";
        isValid = false;
    } else if (password.value.length < 6) {
        passwordError.value = "密码长度不能少于6位";
        isValid = false;
    } else if (!passwordRegex.test(password.value)) {
        passwordError.value = "密码必须包含字母和数字";
        isValid = false;
    } else {
        passwordError.value = "";
    }

    // 验证确认密码
    if (!confirmPassword.value) {
        confirmPasswordError.value = "请确认密码";
        isValid = false;
    } else if (confirmPassword.value !== password.value) {
        confirmPasswordError.value = "两次输入的密码不一致";
        isValid = false;
    } else {
        confirmPasswordError.value = "";
    }

    // 验证同意条款
    if (!agreeTerms.value) {
        termsError.value = "请阅读并同意用户协议和隐私政策";
        isValid = false;
    } else {
        termsError.value = "";
    }

    return isValid;
};

// 处理注册
const handleRegister = () => {
    if (validateForm()) {
        setTimeout(() => {
            showSuccessModal.value = true;
            // 重置表单
            username.value = "";
            phone.value = "";
            userId.value = "";
            password.value = "";
            confirmPassword.value = "";
            agreeTerms.value = false;
        }, 1000);
    }
};
</script>

<style scoped>
/* 样式保持不变，与之前版本一致 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}

.register-page {
    width: 100%;
    min-height: 100vh;
    padding: 20px;
    background-color: #f4f7f9;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.header {
    width: 100%;
    max-width: 1200px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 30px 0;
    padding: 18px 24px;
    border-bottom: 2px solid transparent;
    border-image: linear-gradient(90deg, #3498db, #9b59b6) 1;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(52, 152, 219, 0.08);
    position: relative;
    overflow: hidden;
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
    font-size: 28px;
    font-weight: 600;
    background: linear-gradient(90deg, #2c3e50, #34495e);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    position: relative;
    padding-left: 12px;
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

.register-container {
    width: 100%;
    max-width: 500px;
    margin: 20px auto;
    flex-grow: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}

.register-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 12px;
    padding: 30px;
    width: 100%;
    box-shadow: 0 5px 25px rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(240, 249, 255, 0.8);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
    animation: cardFloat 6s ease-in-out infinite;
}

@keyframes cardFloat {
    0% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-8px);
    }
    100% {
        transform: translateY(0px);
    }
}

.register-card::before {
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

.register-card:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.15);
    border-color: rgba(191, 219, 254, 0.8);
    animation-play-state: paused;
}

.register-card:hover::before {
    transform: scaleY(1);
    opacity: 1;
}

.card-header {
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px dashed rgba(59, 130, 246, 0.2);
}

.card-header h2 {
    color: #1e3a8a;
    font-size: 24px;
    margin-bottom: 8px;
    font-weight: 600;
    position: relative;
    display: inline-block;
}

.card-header h2::after {
    content: "";
    position: absolute;
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 3px;
    background: linear-gradient(90deg, #3498db, #9b59b6);
    border-radius: 2px;
}

.card-header p {
    color: #7f8c8d;
    font-size: 14px;
}

.register-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.form-label {
    font-size: 14px;
    font-weight: 500;
    color: #334155;
    display: block;
    transition: color 0.3s ease;
}

.input-container {
    position: relative;
    display: flex;
    align-items: center;
}

.form-input {
    width: 100%;
    padding: 12px 15px 12px 45px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 15px;
    color: #1e293b;
    background-color: #ffffff;
    transition: all 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    transform: translateY(-2px);
}

.form-input::placeholder {
    color: #94a3b8;
    font-size: 14px;
}

.input-icon {
    position: absolute;
    left: 15px;
    font-size: 16px;
    color: #94a3b8;
    transition: color 0.3s ease;
}

.form-input:focus + .input-icon {
    color: #3b82f6;
}

.form-input:focus ~ .toggle-password {
    color: #3b82f6;
}

.toggle-password {
    position: absolute;
    right: 15px;
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
    color: #94a3b8;
    transition: color 0.3s ease;
    padding: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.error-message {
    font-size: 12px;
    color: #e74c3c;
    min-height: 16px;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-5px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.input-error {
    border-color: #e74c3c !important;
}

.input-error:focus {
    box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1) !important;
}

.terms-group {
    flex-direction: row;
    align-items: flex-start;
    margin-top: 5px;
}

.terms-group input {
    margin-top: 2px;
    margin-right: 8px;
    width: 16px;
    height: 16px;
    accent-color: #3b82f6;
}

.terms-label {
    font-size: 13px;
    color: #64748b;
    line-height: 1.5;
}

.terms-link {
    color: #3b82f6;
    text-decoration: none;
    transition: all 0.2s ease;
    position: relative;
}

.terms-link::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background-color: #3b82f6;
    transform: scaleX(0);
    transition: transform 0.2s ease;
}

.terms-link:hover::after {
    transform: scaleX(1);
}

.register-btn {
    width: 100%;
    padding: 13px 20px;
    background: linear-gradient(90deg, #3498db, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    position: relative;
    overflow: hidden;
    margin-top: 10px;
}

.register-btn::before {
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

.register-btn:hover {
    background: linear-gradient(90deg, #2563eb, #3498db);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    animation-play-state: paused;
}

.register-btn:hover::before {
    left: 100%;
}

.float-animation {
    animation: buttonFloat 3s ease-in-out infinite;
}

@keyframes buttonFloat {
    0% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-5px);
    }
    100% {
        transform: translateY(0px);
    }
}

.btn-text,
.btn-icon {
    position: relative;
    z-index: 1;
    transition: transform 0.3s ease;
}

.register-btn:hover .btn-text {
    transform: translateX(-3px);
}

.register-btn:hover .btn-icon {
    transform: translateX(3px);
}

.login-link {
    text-align: center;
    margin-top: 25px;
    font-size: 14px;
    color: #64748b;
}

.link {
    color: #3b82f6;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s ease;
    position: relative;
}

.link::after {
    content: "";
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 0;
    height: 1px;
    background-color: #3b82f6;
    transition: width 0.2s ease;
}

.link:hover::after {
    width: 100%;
}

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
    animation: fadeIn 0.3s ease;
}

.modal-content {
    background-color: white;
    padding: 30px;
    border-radius: 12px;
    width: 90%;
    max-width: 400px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    animation: scaleIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes scaleIn {
    from {
        transform: scale(0.9);
        opacity: 0;
    }
    to {
        transform: scale(1);
        opacity: 1;
    }
}

.success-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    border-radius: 50%;
    color: white;
    font-size: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(1);
        box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.4);
    }
    70% {
        transform: scale(1.05);
        box-shadow: 0 0 0 10px rgba(46, 204, 113, 0);
    }
    100% {
        transform: scale(1);
        box-shadow: 0 0 0 0 rgba(46, 204, 113, 0);
    }
}

.modal-content h3 {
    color: #2c3e50;
    font-size: 22px;
    margin-bottom: 10px;
}

.modal-content p {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 25px;
}

.modal-btn {
    padding: 10px 25px;
    background: linear-gradient(90deg, #3498db, #2563eb);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.modal-btn:hover {
    background: linear-gradient(90deg, #2563eb, #3498db);
    transform: translateY(-2px);
    box-shadow: 0 3px 10px rgba(59, 130, 246, 0.2);
}

@media (max-width: 480px) {
    .register-card {
        padding: 20px 15px;
    }

    .header h1 {
        font-size: 24px;
    }

    .form-input {
        padding: 10px 12px 10px 40px;
        font-size: 14px;
    }

    .register-btn {
        padding: 11px 20px;
        font-size: 15px;
    }
}
</style>
