<template>
    <div class="login-page">
        <!-- 页面头部 -->
        <header class="header">
            <h1>智能导学系统</h1>
        </header>

        <!-- 登录主容器 -->
        <div class="login-container">
            <!-- 左侧：登录说明 -->
            <div class="login-info">
                <div class="login-title">
                    <h2 class="wechat">微信扫码登录</h2>
                    <p>使用微信扫描右侧二维码登录系统</p>
                </div>

                <div class="login-features">
                    <div class="feature-item">
                        <div class="feature-icon">🔒</div>
                        <div class="feature-text">
                            <h3>安全可靠</h3>
                            <p>微信安全验证，保护账号信息</p>
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">⚡</div>
                        <div class="feature-text">
                            <h3>快捷便捷</h3>
                            <p>无需记住密码，一键扫码登录</p>
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📱</div>
                        <div class="feature-text">
                            <h3>多端同步</h3>
                            <p>学习进度实时同步，随时随地练习</p>
                        </div>
                    </div>
                </div>

                <div class="login-other-options">
                    <button class="option-btn" @click="showPhoneLogin">
                        <span class="option-icon">📞</span>
                        手机号登录
                    </button>
                    <button class="option-btn" @click="showHelp">
                        <span class="option-icon">❓</span>
                        登录遇到问题
                    </button>
                </div>
            </div>

            <!-- 右侧：二维码区域 -->
            <div class="qr-code-container">
                <div class="qr-card">
                    <div class="qr-header">
                        <h3>扫码登录</h3>
                        <span class="refresh-icon" @click="refreshQrCode"
                            >🔄</span
                        >
                    </div>

                    <div class="qr-content">
                        <div class="qr-code">
                            <!-- 二维码区域 -->
                            <div class="qr-placeholder"></div>
                            <div class="qr-mask" v-if="showScanAnimation"></div>
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

                <div class="security-info">
                    <span class="lock-icon">🔒</span>
                    <p>安全连接，保护您的信息安全</p>
                </div>
            </div>
        </div>

        <!-- 页脚 -->
        <footer class="footer">
            <div class="footer-links">
                <a href="#" class="footer-link">关于我们</a>
                <a href="#" class="footer-link">用户协议</a>
                <a href="#" class="footer-link">隐私政策</a>
                <a href="#" class="footer-link">帮助中心</a>
            </div>
            <p class="copyright">© 2025 题库中心 版权所有</p>
        </footer>

        <!-- 登录成功提示 -->
        <div class="success-toast" v-if="showSuccessToast">
            <div class="toast-content">
                <span class="toast-icon">✓</span>
                <p class="toast-text">登录成功，正在进入系统...</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 二维码倒计时
const countdown = ref(60);
// 登录状态
const loginStatus = ref("default"); // default, scanning, confirmed, expired
// 显示扫描动画
const showScanAnimation = ref(false);
// 显示登录成功提示
const showSuccessToast = ref(false);

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

// 倒计时计时器
let countdownTimer = null;

// 开始倒计时
const startCountdown = () => {
    if (countdownTimer) {
        clearInterval(countdownTimer);
    }

    countdown.value = 60;
    loginStatus.value = "default";

    countdownTimer = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) {
            clearInterval(countdownTimer);
            loginStatus.value = "expired";
        }
    }, 1000);
};

// 刷新二维码
const refreshQrCode = () => {
    showScanAnimation.value = true;
    setTimeout(() => {
        showScanAnimation.value = false;
        startCountdown();
    }, 800);
};

// 显示手机号登录
const showPhoneLogin = () => {
    console.log("切换到手机号登录");
    router.push("/login");
    // 实际应用中可以路由跳转到手机号登录页面
};

// 显示帮助
const showHelp = () => {
    console.log("显示登录帮助");
};

// 模拟扫码过程
const simulateLoginProcess = () => {
    // 仅用于演示
    setTimeout(() => {
        loginStatus.value = "scanning";
        setTimeout(() => {
            loginStatus.value = "confirmed";
            setTimeout(() => {
                showSuccessToast.value = true;
                // 登录成功后跳转
                // 实际项目中这里会有真实的角色判断逻辑
                // 这里简单模拟: 随机决定是教师还是学生
                setTimeout(() => {
                    const isTeacher = Math.random() > 0.5;
                    if (isTeacher) {
                        router.push("/teacher/index");
                    } else {
                        router.push("/student/index");
                    }
                }, 1500);
            }, 1000);
        }, 2000);
    }, 5000);
};

onMounted(() => {
    startCountdown();
    // 仅用于演示，实际环境中删除
    simulateLoginProcess();
});

onUnmounted(() => {
    if (countdownTimer) {
        clearInterval(countdownTimer);
    }
});
</script>

<style scoped>
/* 基础样式 */
* {
    color: linear-gradient(135deg, #7ed321 0%, #5cb85c 50%, #3d9970 100%);
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}

.login-page {
    min-height: 100vh;
    background-color: #f4f7f9;
    padding: 20px;
    display: flex;
    flex-direction: column;
    color: linear-gradient(135deg, #7ed321 0%, #5cb85c 50%, #3d9970 100%);
}

/* 头部样式 */
.header {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 30px;
    padding: 18px 24px;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(52, 152, 219, 0.08);
    position: relative;
    overflow: hidden;
    color: linear-gradient(135deg, #7ed321 0%, #5cb85c 50%, #3d9970 100%);
}

.header::before {
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

.header h1 {
    margin: 0;
    font-size: 30px;
    font-weight: 600;
    background: linear-gradient(90deg, #2c3e50, #34495e);
    -webkit-background-clip: text;
    background-clip: text;
    color: linear-gradient(135deg, #7ed321 0%, #5cb85c 50%, #3d9970 100%);
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
    background: linear-gradient(180deg, #3498db, #2ecc71);
}

/* 登录容器 */
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex: 1;
    gap: 50px;
    padding: 20px 0;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

/* 左侧登录说明 */
.login-info {
    flex: 1;
    max-width: 500px;
}

.login-title {
    color: linear-gradient(135deg, #7ed321 0%, #5cb85c 50%, #3d9970 100%);
    margin-bottom: 40px;
    text-align: center;
}

.login-title h2 {
    font-size: 28px;
    color: #2c3e50;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #3498db, #2980b9);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.login-title p {
    color: #7f8c8d;
    font-size: 16px;
}

.login-features {
    display: flex;
    flex-direction: column;
    gap: 30px;
    margin-bottom: 40px;
}

.feature-item {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    padding: 15px;
    border-radius: 10px;
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(240, 249, 255, 0.8);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.12);
}

.feature-icon {
    font-size: 24px;
    color: #3498db;
    margin-top: 3px;
    min-width: 30px;
}

.feature-text h3 {
    color: #2c3e50;
    margin-bottom: 5px;
    font-size: 18px;
}

.feature-text p {
    color: #7f8c8d;
    font-size: 14px;
    line-height: 1.5;
}

.login-other-options {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

.option-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border: 1px solid #dbeafe;
    border-radius: 8px;
    color: #3498db;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(59, 130, 246, 0.05);
}

.option-btn:hover {
    background: linear-gradient(145deg, #f0f7ff 0%, #dbeafe 100%);
    color: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.1);
}

.option-icon {
    font-size: 16px;
}

/* 右侧二维码区域 */
.qr-code-container {
    flex: 1;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.qr-card {
    width: 100%;
    max-width: 300px;
    background: linear-gradient(145deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(240, 249, 255, 0.8);
    position: relative;
    overflow: hidden;
}

.qr-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 4px;
    background: linear-gradient(180deg, #3498db 0%, #2ecc71 100%);
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

.qr-placeholder {
    width: 100%;
    height: 100%;
    position: relative;
}

.wechat-logo {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-size: 24px;
    z-index: 1;
}

.qr-grid {
    width: 100%;
    height: 100%;
    background-image: linear-gradient(to right, #3498db 2px, transparent 2px),
        linear-gradient(to bottom, #3498db 2px, transparent 2px);
    background-size: 20px 20px;
    opacity: 0.2;
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

.security-info {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 20px;
    color: #94a3b8;
    font-size: 13px;
}

.lock-icon {
    color: #2ecc71;
}

/* 页脚样式 */
.footer {
    margin-top: auto;
    padding: 20px 0;
    text-align: center;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}

.footer-link {
    color: #94a3b8;
    text-decoration: none;
    font-size: 13px;
    transition: color 0.3s ease;
}

.footer-link:hover {
    color: #3498db;
    text-decoration: underline;
}

.copyright {
    color: #cbd5e1;
    font-size: 12px;
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

/* 响应式设计 */
@media (max-width: 768px) {
    .login-container {
        flex-direction: column;
        gap: 30px;
    }

    .login-info {
        order: 2;
    }

    .qr-code-container {
        order: 1;
    }

    .login-title {
        margin-bottom: 25px;
    }

    .login-features {
        gap: 20px;
        margin-bottom: 30px;
    }
}
</style>
