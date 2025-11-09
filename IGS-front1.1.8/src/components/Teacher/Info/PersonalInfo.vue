<template>
    <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span class="btnIndex">首页</span>
    </a>
    <div class="user-info-container">
        <div class="user-info-header">
            <div class="header-decoration"></div>
            <div class="header-content">
                <div class="avatar-container">
                    <!-- 头像容器（包含预览和上传层） -->
                    <div class="avatar-wrapper">
                        <!-- 头像区域（可点击触发上传） -->
                        <div
                            class="avatar"
                            :class="avatarClass"
                            @click="triggerUpload"
                            role="button"
                            tabindex="0"
                            aria-label="更换头像"
                        >
                            <!-- 自定义头像图片 -->
                            <img
                                v-if="teacherAvatarUrl"
                                :src="teacherAvatarUrl"
                                class="custom-avatar"
                                alt="教师头像"
                            />
                            <!-- 默认头像图标 -->
                            <span v-else class="icon">{{ teacherAvatar }}</span>

                            <!-- 悬停时显示的操作层 -->
                            <div class="avatar-overlay">
                                <span class="overlay-text">更换头像</span>
                            </div>
                        </div>

                        <!-- 隐藏的文件选择器 -->
                        <input
                            type="file"
                            id="avatar-upload"
                            class="avatar-upload"
                            accept="image/*"
                            @change="handleAvatarUpload"
                        />

                        <!-- 头像操作按钮组 -->
                        <div class="avatar-actions">
                            <button
                                class="action-btn upload-btn"
                                @click="triggerUpload"
                            >
                                上传头像
                            </button>
                            <button
                                class="action-btn reset-btn"
                                @click="resetAvatar"
                                v-if="teacherAvatarUrl"
                            >
                                恢复默认
                            </button>
                        </div>
                    </div>

                    <div class="user-basic">
                        <h2 class="user-name">{{ teacherName }}</h2>
                        <p class="user-id">{{ teacherId }}</p>
                        <p class="user-title">{{ title }}</p>
                        <p class="user-department">{{ department }}</p>
                    </div>
                </div>
                <button class="edit-btn" @click="toggleEditMode">
                    <span v-if="!isEditing">编辑信息</span>
                    <span v-if="isEditing">保存</span>
                    <i class="edit-icon" :class="{ 'rotate-icon': isEditing }"
                        >✎</i
                    >
                </button>
            </div>
        </div>

        <!-- 信息内容区域 -->
        <div class="user-info-content">
            <div class="info-card" :class="{ editing: isEditing }">
                <div class="card-header">
                    <h3>基本信息</h3>
                    <div class="card-icon">👤</div>
                </div>
                <div class="info-item">
                    <label>出生日期:</label>
                    <template v-if="isEditing">
                        <input type="date" v-model="birthDate" />
                    </template>
                    <span v-else>{{ birthDate }}</span>
                </div>
                <div class="info-item">
                    <label>籍贯:</label>
                    <template v-if="isEditing">
                        <input
                            type="text"
                            v-model="hometown"
                            placeholder="输入籍贯"
                        />
                    </template>
                    <span v-else>{{ hometown }}</span>
                </div>
                <div class="info-item">
                    <label>政治面貌:</label>
                    <template v-if="isEditing">
                        <select v-model="politicalStatus">
                            <option value="群众">群众</option>
                            <option value="团员">团员</option>
                            <option value="党员">党员</option>
                            <option value="预备党员">预备党员</option>
                        </select>
                    </template>
                    <span v-else>{{ politicalStatus }}</span>
                </div>
            </div>

            <div class="info-card" :class="{ editing: isEditing }">
                <div class="card-header">
                    <h3>联系方式</h3>
                    <div class="card-icon">✉️</div>
                </div>
                <div class="info-item">
                    <label>电子邮箱:</label>
                    <template v-if="isEditing">
                        <input
                            type="email"
                            v-model="email"
                            placeholder="输入电子邮箱"
                        />
                    </template>
                    <span v-else>{{ email }}</span>
                </div>
                <div class="info-item">
                    <label>联系电话:</label>
                    <template v-if="isEditing">
                        <input
                            type="tel"
                            v-model="phone"
                            placeholder="输入联系电话"
                        />
                    </template>
                    <span v-else>{{ phone }}</span>
                </div>
                <div class="info-item">
                    <label>办公地址:</label>
                    <template v-if="isEditing">
                        <input
                            type="text"
                            v-model="officeAddress"
                            placeholder="输入办公地址"
                        />
                    </template>
                    <span v-else>{{ officeAddress || "未设置" }}</span>
                </div>
            </div>

            <div
                class="info-card full-width-card"
                :class="{ editing: isEditing }"
            >
                <div class="card-header">
                    <h3>个人简介</h3>
                    <div class="card-icon">📝</div>
                </div>
                <div class="info-item full-width">
                    <template v-if="isEditing">
                        <textarea
                            v-model="bio"
                            placeholder="输入个人简介"
                            rows="5"
                        ></textarea>
                    </template>
                    <span v-else>{{ bio }}</span>
                </div>
            </div>

            <div
                class="info-card full-width-card"
                :class="{ editing: isEditing }"
            >
                <div class="card-header">
                    <h3>研究方向/教学科目</h3>
                    <div class="card-icon">🎯</div>
                </div>
                <div class="hobbies-container">
                    <template v-if="isEditing">
                        <div class="hobby-input">
                            <input
                                type="text"
                                v-model="newSubject"
                                placeholder="添加研究方向或教学科目"
                            />
                            <button @click="addSubject">添加</button>
                        </div>
                    </template>
                    <div class="hobby-tags">
                        <span
                            v-for="(subject, index) in subjects"
                            :key="index"
                            class="hobby-tag"
                        >
                            {{ subject }}
                            <button
                                v-if="isEditing"
                                class="remove-tag"
                                @click.stop="removeSubject(index)"
                            >
                                ×
                            </button>
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import request from "../../../utils/request";

const router = useRouter();

// 编辑模式状态
const isEditing = ref(false);

// 教师信息数据
const teacherName = ref("李老师");
const teacherId = ref("DEV_TEACHER_2023001");
const title = ref("教授");
const department = ref("计算机学院");
const birthDate = ref("1982-08-20");
const hometown = ref("上海市");
const politicalStatus = ref("群众");
const email = ref("li.program@smartedu.com");
const phone = ref("13900139000");
const officeAddress = ref("创新楼A503");
const bio = ref(
    "计算机学院高级讲师，拥有15年编程教学经验，专注于Web开发、算法设计与数据结构教学。曾在知名科技企业担任技术主管，参与过多个大型软件项目开发。现致力于将行业实践经验融入教学，培养实用型编程人才。"
);
const subjects = ref([
    "Web前端开发",
    "JavaScript/TypeScript",
    "算法与数据结构",
    "后端开发",
    "编程思维训练",
    "软件工程实践",
]);
const newSubject = ref("");

// 头像相关
const teacherAvatar = ref("👨");
const teacherAvatarUrl = ref("");
const avatarClass = computed(() =>
    teacherAvatarUrl.value ? "has-avatar" : ""
);

// 切换编辑模式
const toggleEditMode = () => {
    if (isEditing.value) {
        // 保存修改
        saveTeacherInfo();
    }
    isEditing.value = !isEditing.value;
};

// 保存教师信息
const saveTeacherInfo = () => {
    // 这里应该发送请求到后端保存数据
    // 为了演示，这里只打印信息
    console.log("保存教师信息:", {
        teacherName: teacherName.value,
        teacherId: teacherId.value,
        title: title.value,
        department: department.value,
        birthDate: birthDate.value,
        hometown: hometown.value,
        politicalStatus: politicalStatus.value,
        email: email.value,
        phone: phone.value,
        officeAddress: officeAddress.value,
        bio: bio.value,
        subjects: subjects.value,
    });

    // 模拟保存成功
    alert("信息保存成功！");
};

// 头像上传相关
const triggerUpload = () => {
    document.getElementById("avatar-upload").click();
};

const handleAvatarUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        // 这里应该上传文件到服务器
        // 为了演示，这里只使用本地URL
        const reader = new FileReader();
        reader.onload = (e) => {
            teacherAvatarUrl.value = e.target.result;
        };
        reader.readAsDataURL(file);
    }
};

const resetAvatar = () => {
    teacherAvatarUrl.value = "";
};

// 研究方向/教学科目相关
const addSubject = () => {
    if (newSubject.value && !subjects.value.includes(newSubject.value)) {
        subjects.value.push(newSubject.value);
        newSubject.value = "";
    }
};

const removeSubject = (index) => {
    subjects.value.splice(index, 1);
};
</script>

<style scoped>
/* 整体容器样式 */
.user-info-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
        Ubuntu, Cantarell, sans-serif;
}

/* 响应式宽度调整 */
@media (min-width: 1400px) {
    .user-info-container {
        max-width: 1400px;
        padding: 20px 40px;
    }
}

@media (min-width: 1600px) {
    .user-info-container {
        max-width: 1600px;
    }
}

/* 头部样式 */
.user-info-header {
    background-color: #fff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    margin-bottom: 30px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.user-info-header:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.header-decoration {
    height: 5px;
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
}

.header-content {
    padding: 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
}

/* 头像样式 */
.avatar-container {
    display: flex;
    align-items: center;
}

.avatar-wrapper {
    text-align: center;
}

.avatar {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background-color: #f0f7ff;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 15px;
    position: relative;
    cursor: pointer;
    overflow: hidden;
    border: 3px solid #e6f0ff;
    transition: all 0.3s ease;
}

.avatar:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(74, 111, 165, 0.15);
    border-color: #4a6fa5;
}

.avatar.has-avatar .icon {
    display: none;
}

.custom-avatar {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}

.icon {
    font-size: 60px;
    color: #4a6fa5;
}

.avatar-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        180deg,
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, 0.7) 100%
    );
    display: flex;
    justify-content: center;
    align-items: flex-end;
    opacity: 0;
    transition: opacity 0.3s ease;
    padding-bottom: 20px;
}

.avatar:hover .avatar-overlay {
    opacity: 1;
}

.overlay-text {
    color: white;
    font-size: 16px;
    font-weight: 500;
    transform: translateY(10px);
    transition: transform 0.3s ease;
}

.avatar:hover .overlay-text {
    transform: translateY(0);
}

.avatar-upload {
    display: none;
}

.avatar-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
}

.action-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.upload-btn {
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
    color: white;
    box-shadow: 0 2px 8px rgba(74, 111, 165, 0.2);
}

.upload-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
}

.reset-btn {
    background-color: #f0f0f0;
    color: #6c7a89;
    border: 1px solid #e1e5eb;
}

.reset-btn:hover {
    background-color: #e6f0ff;
    border-color: #4a6fa5;
    color: #4a6fa5;
}

/* 用户基本信息 */
.user-basic {
    margin-left: 40px;
}

.user-name {
    margin: 0 0 8px 0;
    font-size: 28px;
    color: #2c3e50;
    font-weight: 700;
}

.user-id,
.user-title,
.user-department {
    margin: 6px 0;
    color: #6c7a89;
    font-size: 16px;
}

/* 编辑按钮 */
.edit-btn {
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(74, 111, 165, 0.2);
}

.edit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(74, 111, 165, 0.3);
}

.edit-icon {
    transition: transform 0.3s ease;
    font-size: 16px;
}

.rotate-icon {
    transform: rotate(180deg);
}

/* 内容区域样式 */
.user-info-content {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
}

/* 卡片样式 */
.info-card {
    flex: 1 1 45%;
    min-width: 300px;
    background-color: #fff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    padding: 24px;
    transition: all 0.3s ease;
    border: 1px solid #f0f2f5;
}

.info-card:hover {
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    transform: translateY(-5px);
    border-color: #e6f0ff;
}

.info-card.editing {
    border: 1px dashed #36cbcb;
    background-color: #fcfdff;
}

.full-width-card {
    flex: 1 1 100%;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.info-card h3 {
    font-size: 19px;
    color: #2c3e50;
    margin-top: 0;
    margin-bottom: 0;
    padding-bottom: 15px;
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
}

.info-card h3::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 50px;
    height: 3px;
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
    border-radius: 3px;
}

.card-icon {
    font-size: 22px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #f0f7ff;
    color: #4a6fa5;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 信息项样式 */
.info-item {
    display: flex;
    flex-direction: column;
    margin-bottom: 22px;
    padding-bottom: 18px;
    border-bottom: 1px solid #f0f2f5;
    transition: all 0.2s ease;
}

.info-item:hover {
    background-color: #fafbff;
    padding-left: 5px;
}

.info-item.full-width {
    grid-column: 1 / -1;
}

.info-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

label {
    font-weight: 600;
    color: #6c7a89;
    margin-bottom: 8px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
}

label::before {
    content: "•";
    font-size: 8px;
    color: #4a6fa5;
}

span {
    color: #2c3e50;
    font-size: 16px;
    line-height: 1.6;
}

/* 表单元素样式 */
input,
textarea,
select {
    width: 80%;
    padding: 11px 16px;
    border: 1px solid #e1e5eb;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.3s ease;
    margin-bottom: 10px;
    background-color: #fcfdff;
}

input:focus,
textarea:focus,
select:focus {
    border-color: #4a6fa5;
    outline: none;
    box-shadow: 0 0 0 3px rgba(74, 111, 165, 0.15);
    transform: translateY(-2px);
}

textarea {
    min-height: 120px;
    resize: vertical;
    line-height: 1.6;
    width: 100%;
    box-sizing: border-box;
}

/* 研究方向/教学科目样式 */
.hobbies-container {
    margin-top: 15px;
}

.hobby-input {
    display: flex;
    margin-bottom: 20px;
    gap: 12px;
}

.hobby-input input {
    flex: 1;
    margin-bottom: 0;
}

.hobby-input button {
    padding: 0 20px;
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.hobby-input button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
}

.hobby-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 10px 0;
}

.hobby-tag {
    background-color: #f0f7ff;
    color: #4a6fa5;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.hobby-tag:hover {
    background-color: #e6f0ff;
    transform: translateY(-2px);
    box-shadow: 0 3px 8px rgba(74, 111, 165, 0.15);
    border-color: #d1e0f5;
}

.remove-tag {
    margin-left: 8px;
    cursor: pointer;
    font-weight: bold;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background-color: rgba(74, 111, 165, 0.1);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    transition: all 0.2s ease;
    border: none;
    color: #6c7a89;
}

.remove-tag:hover {
    background-color: #e74c3c;
    color: white;
}

/* 编辑状态样式 */
.info-card.editing .info-item span {
    display: none;
}

.info-card:not(.editing) .info-item input,
.info-card:not(.editing) .info-item select,
.info-card:not(.editing) .info-item textarea,
.info-card:not(.editing) .hobby-input {
    display: none;
}

/* 响应式样式 */
@media (max-width: 992px) {
    .user-info-content {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        text-align: center;
        padding: 20px;
    }

    .avatar-container {
        margin-bottom: 25px;
        flex-direction: column;
    }

    .user-basic {
        margin: 20px 0 0 0;
    }

    .avatar {
        margin-right: 0;
        margin-bottom: 15px;
        width: 120px;
        height: 120px;
    }

    .edit-btn {
        color: white;
        margin-top: 15px;
        width: 100%;
        justify-content: center;
    }

    .user-info-container {
        padding: 20px 15px;
    }

    .info-card {
        padding: 20px 15px;
    }

    input,
    textarea,
    select {
        width: 100%;
        box-sizing: border-box;
    }

    .hobby-input {
        flex-direction: column;
    }

    .hobby-input button {
        margin-top: 10px;
        width: 100%;
        padding: 10px;
    }
}

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
.btnIndex {
    color: white;
}
</style>
