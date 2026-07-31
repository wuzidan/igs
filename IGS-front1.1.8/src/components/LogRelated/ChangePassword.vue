<template>
    <div class="reset-password-page">
        <!-- 页面头部 -->

        <!-- 重置密码卡片 -->
        <div class="reset-password-card">
            <div class="card-header">
                <h2>重置密码 🔑</h2>
                <p class="card-subtitle">设置新密码，重新开启学习之旅 🚀</p>
            </div>

            <form @submit.prevent="handleResetPassword" class="reset-form">
                <!-- 手机号码输入 -->
                <div class="form-group">
                    <label for="phone-number" class="form-label"
                        >手机号码</label
                    >
                    <div class="input-container">
                        <span class="input-icon">📱</span>
                        <input
                            type="tel"
                            id="phone-number"
                            v-model="phoneNumber"
                            class="form-input main-input"
                            placeholder="请输入您的手机号码"
                            pattern="1[3-9]\d{9}"
                            required
                            :class="{ 'input-error': phoneError }"
                        />
                    </div>
                    <p class="error-message" v-if="phoneError">
                        {{ phoneError }}
                    </p>
                </div>

                <!-- 验证码输入 -->
                <div class="form-group">
                    <label for="verification-code" class="form-label"
                        >验证码</label
                    >
                    <div class="verification-container input-container">
                        <span class="input-icon">📩</span>
                        <input
                            type="text"
                            id="verification-code"
                            v-model="verificationCode"
                            class="form-input code-input"
                            placeholder="输入收到的验证码"
                            required
                            :class="{ 'input-error': codeError }"
                        />
                        <button
                            type="button"
                            class="send-code-btn"
                            :disabled="!canSendCode"
                            @click="sendVerificationCode"
                        >
                            {{
                                isSendingCode
                                    ? `${countdown}秒后重发`
                                    : "发送验证码"
                            }}
                        </button>
                    </div>
                    <p class="error-message" v-if="codeError">
                        {{ codeError }}
                    </p>
                </div>

                <!-- 新密码输入 -->
                <div class="form-group">
                    <label for="new-password" class="form-label">新密码</label>
                    <div class="password-container input-container">
                        <span class="input-icon">🔒</span>
                        <input
                            :type="showNewPassword ? 'text' : 'password'"
                            id="new-password"
                            v-model="newPassword"
                            class="form-input main-input"
                            placeholder="设置新密码"
                            required
                            :class="{ 'input-error': passwordError }"
                        />
                        <button
                            type="button"
                            class="toggle-password"
                            @click="showNewPassword = !showNewPassword"
                        >
                            {{ showNewPassword ? "🙈" : "👁️" }}
                        </button>
                    </div>
                    <p class="password-hint">
                        密码长度至少8位，包含字母和数字 🔐
                    </p>
                    <p class="error-message" v-if="passwordError">
                        {{ passwordError }}
                    </p>
                </div>

                <!-- 确认密码输入 -->
                <div class="form-group">
                    <label for="confirm-password" class="form-label"
                        >确认密码</label
                    >
                    <div class="password-container input-container">
                        <span class="input-icon">🔄</span>
                        <input
                            :type="showConfirmPassword ? 'text' : 'password'"
                            id="confirm-password"
                            v-model="confirmPassword"
                            class="form-input main-input"
                            placeholder="再次输入新密码"
                            required
                        />
                        <button
                            type="button"
                            class="toggle-password"
                            @click="showConfirmPassword = !showConfirmPassword"
                        >
                            {{ showConfirmPassword ? "🙈" : "👁️" }}
                        </button>
                    </div>
                    <p
                        class="password-match-hint"
                        :class="{
                            match: passwordsMatch,
                            'not-match': !passwordsMatch && showMatchHint,
                        }"
                        v-if="showMatchHint"
                    >
                        {{ passwordsMatch ? "✓ 密码匹配" : "✗ 密码不匹配" }}
                    </p>
                </div>

                <!-- 提交按钮 -->
                <button type="submit" class="reset-btn float-animation">
                    <span class="btn-text">确认重置密码</span>
                    <span class="btn-icon">→</span>
                </button>
            </form>

            <div class="form-links">
                <router-link to="/login" class="form-link"
                    >返回登录 🔙</router-link
                >
                <span class="link-divider">|</span>
                <router-link to="/register" class="form-link"
                    >注册账号 🆕</router-link
                >
            </div>
        </div>

        <!-- 重置成功弹窗 -->
        <div class="modal" v-if="showSuccessModal">
            <div class="modal-content">
                <div class="success-icon">✓</div>
                <h3>密码重置成功！🎉</h3>
                <p>您的密码已更新，即将跳转到登录页面</p>
                <button class="modal-btn" @click="showSuccessModal = false">
                    确定
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 表单数据
const phoneNumber = ref("");
const verificationCode = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

// 错误信息
const phoneError = ref("");
const codeError = ref("");
const passwordError = ref("");

// 弹窗状态
const showSuccessModal = ref(false);

// 验证码状态
const isSendingCode = ref(false);
const countdown = ref(60);

// 密码验证相关计算属性
const passwordsMatch = computed(() => {
    return newPassword.value === confirmPassword.value;
});

// 只有两个密码框都有值时才显示匹配提示
const showMatchHint = computed(() => {
    return newPassword.value && confirmPassword.value;
});

const passwordIsValid = computed(() => {
    // 密码验证：至少8位，包含字母和数字
    const hasLetter = /[a-zA-Z]/.test(newPassword.value);
    const hasNumber = /\d/.test(newPassword.value);
    const isValid = newPassword.value.length >= 8 && hasLetter && hasNumber;

    // 设置密码错误信息
    if (newPassword.value && !isValid) {
        if (newPassword.value.length < 8) {
            passwordError.value = "密码长度不能少于8位";
        } else if (!hasLetter || !hasNumber) {
            passwordError.value = "密码必须包含字母和数字";
        } else {
            passwordError.value = "";
        }
    } else {
        passwordError.value = "";
    }

    return isValid;
});

// 验证手机号格式
const isPhoneValid = computed(() => {
    const isValid = /^1[3-9]\d{9}$/.test(phoneNumber.value);

    // 设置手机号错误信息
    if (phoneNumber.value && !isValid) {
        phoneError.value = "请输入有效的手机号";
    } else {
        phoneError.value = "";
    }

    return isValid;
});

// 验证验证码
const isCodeValid = computed(() => {
    const isValid =
        verificationCode.value.length === 6 &&
        /^\d{6}$/.test(verificationCode.value);

    // 设置验证码错误信息
    if (verificationCode.value && !isValid) {
        codeError.value = "请输入6位数字验证码";
    } else {
        codeError.value = "";
    }

    return isValid;
});

// 能否发送验证码（手机号有效且不在发送中）
const canSendCode = computed(() => {
    return isPhoneValid.value && !isSendingCode.value;
});

// 能否提交表单
const canSubmit = computed(() => {
    return (
        isPhoneValid.value &&
        isCodeValid.value &&
        newPassword.value &&
        confirmPassword.value &&
        passwordsMatch.value &&
        passwordIsValid.value
    );
});

// 发送验证码
const sendVerificationCode = () => {
    if (!canSendCode.value) return;

    // 模拟发送验证码
    isSendingCode.value = true;

    // 倒计时逻辑
    const timer = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) {
            clearInterval(timer);
            isSendingCode.value = false;
            countdown.value = 60;
        }
    }, 1000);

    // 实际应用中这里应该调用后端API发送验证码
    console.log(`向手机号 ${phoneNumber.value} 发送验证码`);
};

// 处理密码重置
const handleResetPassword = () => {
    if (canSubmit.value) {
        // 模拟密码重置请求
        console.log(`手机号 ${phoneNumber.value} 密码重置成功`);

        // 显示成功消息并跳转到登录页
        showSuccessModal.value = true;

        // 3秒后跳转到登录页
        setTimeout(() => {
            router.push("/login");
        }, 3000);
    }
};
</script>

<style scoped>
/* 基础样式优化 */
.input-container {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%; /* 确保容器宽度100% */
}

.input-icon {
    position: absolute;
    left: 15px;
    font-size: 16px;
    color: #94a3b8;
    transition: color 0.3s ease;
    z-index: 1; /* 确保图标在输入框上方 */
}

/* 主输入框样式 - 保持一致长度 */
.main-input {
    width: 100% !important;
    padding-left: 45px !important;
    padding-right: 15px !important;
}

/* 验证码输入框样式 - 保持合理宽度 */
.code-input {
    width: 55% !important;
    padding-left: 45px !important;
}

.form-input {
    padding: 12px 15px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    background-color: #fff;
    font-size: 15px;
    color: #1e293b;
    transition: all 0.3s ease;
    min-height: px; /* 统一输入框高度 */
}

.form-input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 验证码容器优化 */
.verification-container {
    display: flex;
    gap: 10px;
    width: 100%;
}

/* 错误提示样式 */
.error-message {
    font-size: 12px;
    color: #e74c3c;
    min-height: 16px;
    animation: fadeIn 0.3s ease;
}

.input-error {
    border-color: #e74c3c !important;
}

.input-error:focus {
    box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1) !important;
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

/* 按钮浮动动画 */
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

/* 重置按钮样式优化 */
.reset-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%; /* 按钮宽度100% */
}

.btn-text,
.btn-icon {
    transition: transform 0.3s ease;
}

.reset-btn:hover .btn-text {
    transform: translateX(-3px);
}

.reset-btn:hover .btn-icon {
    transform: translateX(3px);
}

/* 成功弹窗样式 */
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

/* 页面基础样式 */
.reset-password-page {
    min-height: 100vh;
    background-color: #f4f7f9;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.header {
    width: 100%;
    max-width: 500px;
    margin-bottom: 30px;
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
    font-size: 26px;
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

.reset-password-card {
    width: 100%;
    max-width: 500px;
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(240, 249, 255, 0.8);
    position: relative;
    overflow: hidden;
}

.reset-password-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 4px;
    background: linear-gradient(180deg, #60a5fa 0%, #2563eb 100%);
}

.card-header {
    text-align: center;
    margin-bottom: 30px;
}

.card-header h2 {
    color: #1e3a8a;
    margin-bottom: 8px;
    font-size: 22px;
    font-weight: 600;
}

.card-subtitle {
    color: #7f8c8d;
    font-size: 15px;
    margin: 0;
}

.reset-form {
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
    color: #334155;
    font-weight: 500;
}

.send-code-btn {
    padding: 0 20px;
    background: linear-gradient(90deg, #3498db, #2980b9);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
    white-space: nowrap;
    flex: 1; /* 验证码按钮自适应剩余空间 */
    min-height: 45px; /* 与输入框保持一致高度 */
}

/* 可点击状态添加浮动效果 */
.send-code-btn:not(:disabled) {
    animation: float 3s ease-in-out infinite;
}

.send-code-btn:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.send-code-btn:hover:not(:disabled) {
    background: linear-gradient(90deg, #2980b9, #3498db);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.password-container {
    position: relative;
}

.password-container .main-input {
    padding-right: 45px !important; /* 为密码可见性切换按钮预留空间 */
}

.toggle-password {
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s;
    z-index: 1;
}

.toggle-password:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

.password-hint {
    font-size: 12px;
    color: #7f8c8d;
    margin: 0;
    padding-top: 3px;
}

.password-match-hint {
    font-size: 12px;
    margin: 0;
    padding-top: 3px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.password-match-hint.match {
    color: #2ecc71;
}

.password-match-hint.not-match {
    color: #e74c3c;
}

.reset-btn {
    padding: 12px 20px;
    background: linear-gradient(90deg, #3498db, #2980b9);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.3s ease;
    margin-top: 10px;
}

/* 可点击状态添加浮动效果 */
.reset-btn:not(:disabled) {
    animation: float 3s ease-in-out infinite;
}

.reset-btn:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.reset-btn:hover:not(:disabled) {
    background: linear-gradient(90deg, #2980b9, #3498db);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

/* 浮动动画效果 */
@keyframes float {
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

.form-links {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    margin-top: 25px;
    font-size: 14px;
}

.form-link {
    color: #3498db;
    text-decoration: none;
    transition: all 0.2s ease;
    font-weight: 500;
}

.form-link:hover {
    color: #2980b9;
    text-decoration: underline;
}

.link-divider {
    color: #bdc3c7;
}

/* 响应式调整 */
@media (max-width: 576px) {
    .reset-password-card {
        padding: 20px;
    }

    .verification-container {
        flex-direction: column;
    }

    .code-input,
    .send-code-btn {
        width: 100% !important;
    }

    .send-code-btn {
        padding: 12px 20px;
    }
}
</style>
