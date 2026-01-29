<template>
    <div class="wechat-qr-login-page">
        <!-- 页面头部 -->
        <header class="login-header">
            <div class="logo-container">
                <div class="logo-icon">📚</div>
                <h1>智能导学系统</h1>
            </div>
            <p class="login-desc">微信扫码登录</p>
        </header>

        <div class="login-container">
            <div class="login-card">
                <!-- 微信扫码区域 -->
                <div class="qr-section">
                    <div class="qr-header">
                        <h3>扫码登录</h3>
                        <span class="refresh-icon" @click="refreshQRCode"
                            >🔄</span
                        >
                    </div>

                    <div class="qr-content">
                        <div class="qr-code" v-if="qrcodeUrl">
                            <img :src="qrcodeUrl" alt="微信登录二维码" />
                            <div class="qr-mask" v-if="showScanAnimation"></div>
                        </div>
                        <div class="qr-code qr-loading" v-else>
                            <div class="loading-spinner"></div>
                            <p>生成二维码中...</p>
                        </div>

                        <div class="qr-tips">
                            <p>请使用微信扫描二维码</p>
                            <p class="qr-expire">
                                二维码将在
                                <span class="countdown">{{ countdown }}</span>
                                秒后过期
                            </p>
                        </div>
                    </div>

                    <div class="qr-footer">
                        <div class="login-status" :class="loginStatusClass">
                            <span class="status-icon">{{ statusIcon }}</span>
                            <span class="status-text">{{ statusText }}</span>
                        </div>
                    </div>
                </div>

                <!-- 其他登录选项 -->
                <div class="other-options">
                    <div class="divider">
                        <span>或使用以下方式登录</span>
                    </div>
                    <div class="login-methods">
                        <button class="method-btn" @click="goToPasswordLogin">
                            <span class="method-icon">🔑</span>
                            密码登录
                        </button>
                        <button class="method-btn" @click="goToRegister">
                            <span class="method-icon">📝</span>
                            立即注册
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 登录成功提示 -->
        <div class="success-toast" v-if="showSuccessToast">
            <div class="toast-content">
                <span class="toast-icon">✓</span>
                <p class="toast-text">登录成功，正在进入系统...</p>
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
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 二维码相关
const qrcodeUrl = ref("");
const countdown = ref(60);
const loginStatus = ref("default"); // default, scanning, confirmed, expired
const showScanAnimation = ref(false);
const showSuccessToast = ref(false);
const pollingTimer = ref(null);
const countdownTimer = ref(null);

// 微信开放平台配置
const appId = "wx8bd64578d53c7f2a"; // 替换为实际的微信开放平台appid
const redirectUri = encodeURIComponent(
    "https://igs.whu.edu.cn/wechat/callback",
); // 替换为实际的回调地址
const scope = "snsapi_login";

// 状态相关计算
const loginStatusClass = computed(() => ({
    "login-status": true,
    "status-default": loginStatus.value === "default",
    "status-scanning": loginStatus.value === "scanning",
    "status-confirmed": loginStatus.value === "confirmed",
    "status-expired": loginStatus.value === "expired",
}));

const statusIcon = computed(() => {
    switch (loginStatus.value) {
        case "default":
            return "📱";
        case "scanning":
            return "👀";
        case "confirmed":
            return "✓";
        case "expired":
            return "⏰";
        default:
            return "📱";
    }
});

const statusText = computed(() => {
    switch (loginStatus.value) {
        case "default":
            return "等待扫码...";
        case "scanning":
            return "正在扫描...";
        case "confirmed":
            return "扫码成功，即将登录";
        case "expired":
            return "二维码已过期，请刷新";
        default:
            return "等待扫码...";
    }
});

// 生成微信登录二维码
const generateQRCode = () => {
    // 生成随机state参数
    const state =
        "wechat_login_" +
        Date.now() +
        "_" +
        Math.random().toString(36).substr(2, 9);
    localStorage.setItem("wechat_login_state", state);

    // 构建微信授权URL
    const wechatAuthUrl = `https://open.weixin.qq.com/connect/qrconnect?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=${state}#wechat_redirect`;

    // 实际应用中，这里应该调用后端API生成二维码
    // 这里为了演示，使用一个模拟的二维码URL
    qrcodeUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(wechatAuthUrl)}`;

    // 开始倒计时
    startCountdown();

    // 开始轮询登录状态
    startPolling();
};

// 开始倒计时
const startCountdown = () => {
    if (countdownTimer.value) {
        clearInterval(countdownTimer.value);
    }

    countdown.value = 60;
    loginStatus.value = "default";

    countdownTimer.value = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) {
            clearInterval(countdownTimer.value);
            loginStatus.value = "expired";
            qrcodeUrl.value = "";
        }
    }, 1000);
};

// 开始轮询登录状态
const startPolling = () => {
    // 清除之前的轮询
    if (pollingTimer.value) {
        clearInterval(pollingTimer.value);
    }

    // 每2秒轮询一次登录状态
    pollingTimer.value = setInterval(() => {
        checkLoginStatus();
    }, 2000);
};

// 检查登录状态
const checkLoginStatus = () => {
    // 实际应用中，这里应该调用后端API检查登录状态
    // 这里为了演示，模拟登录过程
    if (Math.random() > 0.95) {
        // 5%的概率模拟登录成功
        handleLoginSuccess();
    }
};

// 处理登录成功
const handleLoginSuccess = () => {
    // 清除定时器
    if (pollingTimer.value) {
        clearInterval(pollingTimer.value);
    }
    if (countdownTimer.value) {
        clearInterval(countdownTimer.value);
    }

    loginStatus.value = "confirmed";
    showSuccessToast.value = true;

    // 模拟登录成功后跳转
    setTimeout(() => {
        // 实际应用中，这里应该根据后端返回的用户信息判断角色
        const isTeacher = Math.random() > 0.5;
        if (isTeacher) {
            router.push("/teacher/index");
        } else {
            router.push("/student/index");
        }
    }, 1500);
};

// 刷新二维码
const refreshQRCode = () => {
    showScanAnimation.value = true;
    setTimeout(() => {
        showScanAnimation.value = false;
        generateQRCode();
    }, 800);
};

// 跳转到密码登录
const goToPasswordLogin = () => {
    router.push("/login");
};

// 跳转到注册页面
const goToRegister = () => {
    router.push("/register");
};

// 组件挂载时生成二维码
onMounted(() => {
    generateQRCode();
});

// 组件卸载时清理定时器
onUnmounted(() => {
    if (pollingTimer.value) {
        clearInterval(pollingTimer.value);
    }
    if (countdownTimer.value) {
        clearInterval(countdownTimer.value);
    }
});
</script>

<style scoped>
/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}

.wechat-qr-login-page {
    min-height: 100vh;
    background-color: #f4f7f9;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* 头部样式 */
.login-header {
    text-align: center;
    margin-bottom: 30px;
    padding: 18px 24px;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(52, 152, 219, 0.08);
    position: relative;
    overflow: hidden;
    width: 100%;
    max-width: 500px;
}

.login-header::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #3498db, #2ecc71, #3498db);
    background-size: 200% 100%;
    animation: headerGlow 6s ease-in-out infinite;
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

/* 登录容器 */
.login-container {
    width: 100%;
    max-width: 420px;
    margin-bottom: 30px;
}

/* 登录卡片 */
.login-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(240, 249, 255, 0.8);
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

/* 二维码区域 */
.qr-section {
    margin-bottom: 25px;
}

.qr-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px dashed rgba(59, 130, 246, 0.2);
}

.qr-header h3 {
    color: #1e3a8a;
    font-size: 18px;
    font-weight: 600;
}

.refresh-icon {
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.3s ease;
    padding: 5px;
    border-radius: 50%;
}

.refresh-icon:hover {
    color: #3498db;
    background-color: rgba(52, 152, 219, 0.1);
    transform: rotate(90deg);
}

.qr-content {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.qr-code {
    width: 200px;
    height: 200px;
    background-color: white;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
}

.qr-code img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.qr-loading {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: #f8fafc;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 10px;
}

.qr-mask {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(52, 152, 219, 0.2) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    animation: scanAnimation 0.8s ease-in-out;
}

.qr-tips {
    text-align: center;
}

.qr-tips p {
    color: #334155;
    margin-bottom: 5px;
    font-size: 14px;
}

.qr-expire {
    color: #94a3b8;
    font-size: 13px;
}

.countdown {
    color: #e53935;
    font-weight: bold;
}

.qr-footer {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px dashed rgba(59, 130, 246, 0.2);
}

.login-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
}

.status-default {
    background-color: rgba(52, 152, 219, 0.1);
    color: #3498db;
}

.status-scanning {
    background-color: rgba(243, 156, 18, 0.1);
    color: #e67e22;
}

.status-confirmed {
    background-color: rgba(46, 204, 113, 0.1);
    color: #2ecc71;
}

.status-expired {
    background-color: rgba(231, 76, 60, 0.1);
    color: #e74c3c;
}

.status-icon {
    font-size: 16px;
}

/* 其他登录选项 */
.other-options {
    margin-top: 25px;
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

.login-methods {
    display: flex;
    gap: 10px;
}

.method-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px;
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border: 1px solid #dbeafe;
    border-radius: 8px;
    color: #3498db;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(59, 130, 246, 0.05);
}

.method-btn:hover {
    background: linear-gradient(145deg, #f0f7ff 0%, #dbeafe 100%);
    color: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.1);
}

.method-icon {
    font-size: 16px;
}

/* 登录成功提示 */
.success-toast {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 1000;
    background-color: rgba(0, 0, 0, 0.7);
    border-radius: 8px;
    padding: 20px 30px;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: toastFadeIn 0.3s ease-out;
}

.toast-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.toast-icon {
    color: #2ecc71;
    font-size: 24px;
}

.toast-text {
    color: white;
    font-size: 16px;
}

/* 页脚 */
.login-footer {
    text-align: center;
    margin-top: auto;
    padding-top: 20px;
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

/* 动画效果 */
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

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

@keyframes scanAnimation {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(100%);
    }
}

@keyframes toastFadeIn {
    from {
        opacity: 0;
        transform: translate(-50%, -50%) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }
}

/* 响应式调整 */
@media (max-width: 480px) {
    .login-card {
        padding: 25px 20px;
    }

    .qr-code {
        width: 180px;
        height: 180px;
    }

    .method-btn {
        padding: 10px;
        font-size: 13px;
    }
}
</style>
