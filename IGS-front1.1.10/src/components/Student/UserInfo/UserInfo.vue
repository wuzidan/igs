<template>
    <div class="user-info-container">
        <!-- 使用统一的学生头部组件 -->
        <StudentHeader title="个人信息" />
        <!-- 头像上传区域 -->
        <div class="avatar-section">
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
                        v-if="userAvatarUrl"
                        :src="userAvatarUrl"
                        class="custom-avatar"
                        alt="用户头像"
                    />
                    <!-- 默认头像图标 -->
                    <span v-else class="icon">{{ userAvatar }}</span>

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
                        v-if="userAvatarUrl"
                    >
                        恢复默认
                    </button>
                </div>
            </div>
        </div>
        <!-- 编辑按钮 -->
        <div class="edit-button-section">
            <button class="edit-btn" @click="toggleEditMode">
                <span v-if="!isEditing">编辑信息</span>
                <span v-if="isEditing">保存</span>
                <i class="edit-icon" :class="{ 'rotate-icon': isEditing }">✎</i>
            </button>
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
                    <label>个人网站:</label>
                    <template v-if="isEditing">
                        <input
                            type="url"
                            v-model="website"
                            placeholder="输入个人网站"
                        />
                    </template>
                    <span v-else>{{ website || "未设置" }}</span>
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
                    <h3>兴趣爱好</h3>
                    <div class="card-icon">🎯</div>
                </div>
                <div class="hobbies-container">
                    <template v-if="isEditing">
                        <div class="hobby-input">
                            <input
                                type="text"
                                v-model="newHobby"
                                placeholder="添加兴趣爱好"
                            />
                            <button @click="addHobby">添加</button>
                        </div>
                    </template>
                    <div class="hobby-tags">
                        <span
                            v-for="(hobby, index) in hobbies"
                            :key="index"
                            class="hobby-tag"
                        >
                            {{ hobby }}
                            <span
                                v-if="isEditing"
                                class="remove-hobby"
                                @click.stop="removeHobby(index)"
                                >×</span
                            >
                        </span>
                    </div>
                </div>
            </div>

            <div
                class="info-card full-width-card"
                :class="{ editing: isEditing }"
            >
                <div class="card-header">
                    <h3>技能特长</h3>
                    <div class="card-icon">🛠️</div>
                </div>
                <div class="skills-container">
                    <div
                        v-for="(skill, index) in skills"
                        :key="index"
                        class="skill-item"
                    >
                        <!-- 技能名称 -->
                        <div class="skill-name">
                            <template v-if="isEditing">
                                <input
                                    type="text"
                                    v-model="skill.name"
                                    placeholder="技能名称"
                                />
                            </template>
                            <span v-else>{{ skill.name }}</span>
                        </div>

                        <!-- 技能水平和进度条 -->
                        <div class="skill-level-container">
                            <template v-if="isEditing">
                                <select v-model="skill.level">
                                    <option value="初级">初级</option>
                                    <option value="中级">中级</option>
                                    <option value="高级">高级</option>
                                    <option value="精通">精通</option>
                                </select>
                            </template>
                            <template v-else>
                                <!-- 进度条容器 -->
                                <div class="skill-progress-container">
                                    <div
                                        class="skill-progress-bar"
                                        :style="getSkillStyle(skill.level)"
                                        :data-level="skill.level"
                                    ></div>
                                </div>
                                <!-- 技能水平文本说明 -->
                                <div class="skill-level-text">
                                    <span :class="getSkillClass(skill.level)">{{
                                        skill.level
                                    }}</span>
                                    <span class="skill-description">{{
                                        getSkillDescription(skill.level)
                                    }}</span>
                                </div>
                            </template>
                        </div>

                        <!-- 操作按钮 -->
                        <div v-if="isEditing" class="skill-actions">
                            <button @click="removeSkill(index)">删除</button>
                        </div>
                    </div>
                    <div v-if="isEditing" class="add-skill">
                        <button @click="addSkill">添加技能</button>
                    </div>
                </div>
            </div>

            <div
                class="info-card full-width-card"
                :class="{ editing: isEditing }"
            >
                <div class="card-header">
                    <h3>教育经历</h3>
                    <div class="card-icon">🎓</div>
                </div>
                <div class="education-container">
                    <div
                        v-for="(edu, index) in education"
                        :key="index"
                        class="education-item"
                    >
                        <div class="edu-school">
                            <template v-if="isEditing">
                                <input
                                    type="text"
                                    v-model="edu.school"
                                    placeholder="学校名称"
                                />
                            </template>
                            <span v-else>{{ edu.school }}</span>
                        </div>
                        <div class="edu-dates">
                            <template v-if="isEditing">
                                <div class="date-inputs">
                                    <input
                                        type="date"
                                        v-model="edu.period_s"
                                        placeholder="入学"
                                    />
                                    <span class="date-separator">-</span>
                                    <input
                                        type="date"
                                        v-model="edu.period_e"
                                        placeholder="毕业"
                                    />
                                </div>
                            </template>
                            <span v-else>
                                {{ edu.period_s }} - {{ edu.period_e }}
                            </span>
                        </div>
                        <div class="edu-major">
                            <template v-if="isEditing">
                                <input
                                    type="text"
                                    v-model="edu.major"
                                    placeholder="专业"
                                />
                            </template>
                            <span v-else>{{ edu.major }}</span>
                        </div>
                        <div class="edu-degree">
                            <template v-if="isEditing">
                                <select v-model="edu.degree">
                                    <option value="本科">本科</option>
                                    <option value="硕士">硕士</option>
                                    <option value="博士">博士</option>
                                    <option value="高中">高中</option>
                                    <option value="初中">初中</option>
                                    <option value="小学">小学</option>
                                </select>
                            </template>
                            <span v-else>{{ edu.degree }}</span>
                        </div>
                        <div v-if="isEditing" class="edu-actions">
                            <button @click="removeEducation(index)">
                                删除
                            </button>
                        </div>
                    </div>
                    <div v-if="isEditing" class="add-education">
                        <button @click="addEducation">添加教育经历</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <a href="/student/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span class="bth-text">首页</span>
    </a>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../../../api/index";
import StudentHeader from "../StudentHeader.vue";

// 头像相关数据
const userAvatarUrl = ref(""); // 自定义头像URL
const userAvatar = ref("👨‍💻"); // 默认头像emoji

// 基本信息数据
const isEditing = ref(false);
const birthDate = ref("");
const hometown = ref("");
const politicalStatus = ref("");
const email = ref("");
const phone = ref("");
const website = ref("");
const bio = ref("");
const hobbies = ref([]);
const newHobby = ref("");
const skills = ref([]);
const education = ref([]);

// 用户信息由StudentHeader组件管理，此处不再需要单独定义
const userName = ref("");
const studentId = ref("");
const className = ref("");
const major = ref("");

// 响应式变量
const isLoading = ref(true); // 加载状态
const errorMsg = ref(""); // 错误信息
const saveLoading = ref(false); // 保存请求状态
const studentInfo = ref({}); // 学生信息完整数据
const knowledgeList = ref([]); // 知识点列表

// 头像处理方法
const triggerUpload = () => {
    // 直接触发文件选择器点击
    const fileInput = document.getElementById("avatar-upload");
    if (fileInput) {
        fileInput.click();
    }
};

const handleAvatarUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
        // 验证文件类型
        if (!file.type.startsWith("image/")) {
            alert("请选择图片文件（JPG、PNG等格式）");
            return;
        }

        // 验证文件大小（限制5MB以内）
        if (file.size > 5 * 1024 * 1024) {
            alert("图片大小不能超过5MB");
            return;
        }

        // 预览图片
        const reader = new FileReader();
        reader.onload = (event) => {
            userAvatarUrl.value = event.target.result;
        };
        reader.readAsDataURL(file);

        // 清空输入，允许重复选择同一文件
        e.target.value = "";
    }
};

const resetAvatar = () => {
    if (confirm("确定要恢复默认头像吗？")) {
        userAvatarUrl.value = "";
    }
};

// 信息编辑方法
const toggleEditMode = () => {
    if (isEditing.value) {
        // 退出编辑模式时保存数据
        saveStudentInfo();
    } else {
        // 进入编辑模式
        isEditing.value = true;
    }
};

// 保存个人信息到服务器（使用PUT接口）
const saveStudentInfo = () => {
    // 构建要保存的数据对象
    const saveData = {
        userAvatarUrl: userAvatarUrl.value,
        userAvatar: userAvatar.value,
        userName: userName.value,
        studentId: studentId.value,
        className: className.value,
        major: major.value,
        birthDate: birthDate.value,
        hometown: hometown.value,
        politicalStatus: politicalStatus.value,
        email: email.value,
        phone: phone.value,
        website: website.value,
        bio: bio.value,
        hobbies: hobbies.value,
        skills: skills.value,
        education: education.value,
    };

    // 验证必填字段
    if (!userName.value.trim()) {
        alert("请输入姓名");
        return;
    }

    // 显示保存加载状态
    saveLoading.value = true;

    // 调用PUT接口保存数据
    api.putStudentinfo(saveData)
        .then((res) => {
            console.log("个人信息修改成功", res.data);
            saveLoading.value = false;
            isEditing.value = false;

            // 显示成功提示
            alert("个人信息修改成功！");

            // 更新本地完整数据
            studentInfo.value = res.data;
        })
        .catch((err) => {
            console.error("修改失败", err);
            saveLoading.value = false;
            alert(
                "修改失败：" +
                    (err.response?.data?.message || "网络错误，请稍后重试")
            );
        });
};

// 取消编辑
const cancelEdit = () => {
    if (confirm("确定要取消修改吗？未保存的内容将丢失")) {
        // 恢复原始数据
        restoreOriginalData();
        isEditing.value = false;
    }
};

// 恢复原始数据（取消编辑时使用）
const restoreOriginalData = () => {
    const original = studentInfo.value;
    if (original) {
        userAvatarUrl.value = original.userAvatarUrl || "";
        userAvatar.value = original.userAvatar || "👨‍💻";
        userName.value = original.userName || "";
        studentId.value = original.studentId || "";
        className.value = original.className || "";
        major.value = original.major || "";
        birthDate.value = original.birthDate || "";
        hometown.value = original.hometown || "";
        politicalStatus.value = original.politicalStatus || "";
        email.value = original.email || "";
        phone.value = original.phone || "";
        website.value = original.website || "";
        bio.value = original.bio || "";
        hobbies.value = Array.isArray(original.hobbies)
            ? [...original.hobbies]
            : [];
        skills.value = Array.isArray(original.skills)
            ? [...original.skills]
            : [];
        education.value = Array.isArray(original.education)
            ? [...original.education]
            : [];
    }
};

// 兴趣爱好管理
const addHobby = () => {
    if (
        newHobby.value.trim() &&
        !hobbies.value.includes(newHobby.value.trim())
    ) {
        hobbies.value.push(newHobby.value.trim());
        newHobby.value = "";
    }
};

const removeHobby = (index) => {
    hobbies.value.splice(index, 1);
};

// 技能管理
const addSkill = () => {
    skills.value.push({ name: "", level: "初级" });
};

const removeSkill = (index) => {
    skills.value.splice(index, 1);
};

// 技能水平样式和描述 - 红、橙、绿、金配色
const getSkillStyle = (level) => {
    const styles = {
        初级: {
            width: "25%",
            background: "linear-gradient(90deg, #ff6b6b, #ff4757)", // 红色渐变
            boxShadow: "0 0 6px rgba(255, 71, 87, 0.4)",
        },
        中级: {
            width: "50%",
            background: "linear-gradient(90deg, #ff9f43, #ff7b29)", // 橙色渐变（替换黄色）
            boxShadow: "0 0 6px rgba(255, 123, 41, 0.4)",
        },
        高级: {
            width: "75%",
            background: "linear-gradient(90deg, #4ecdc4, #26a69a)", // 绿色渐变
            boxShadow: "0 0 6px rgba(38, 166, 154, 0.4)",
        },
        精通: {
            width: "100%",
            background: "linear-gradient(90deg, #ffd700, #ffb74d, #ffd700)", // 金色渐变
            boxShadow: "0 0 15px rgba(255, 215, 0, 0.7)",
            position: "relative",
            overflow: "hidden",
        },
    };
    return styles[level] || styles["初级"];
};

// 对应的熟练度文本样式
const getSkillClass = (level) => {
    const classes = {
        初级: "level-beginner",
        中级: "level-intermediate",
        高级: "level-advanced",
        精通: "level-expert",
    };
    return classes[level] || "level-beginner";
};

const getSkillDescription = (level) => {
    const descriptions = {
        初级: "具备基础概念和简单应用能力",
        中级: "能够独立完成常规任务和问题解决",
        高级: "深入理解原理，能够优化和创新应用",
        精通: "行业专家水平，能引领技术方向和解决复杂问题",
    };
    return descriptions[level] || "";
};

// 教育经历管理
const addEducation = () => {
    education.value.push({
        school: "",
        period_s: "",
        period_e: "",
        major: "",
        degree: "本科",
    });
};

const removeEducation = (index) => {
    education.value.splice(index, 1);
};

// 生命周期钩子 - 加载个人信息（用户基本信息由StudentHeader组件管理）
onMounted(() => {
    // 调用接口获取数据
    api.getStudentinfo()
        .then((res) => {
            console.log("获取的个人信息数据：", res.data);
            isLoading.value = false;

            // 保存完整原始数据（用于取消编辑时恢复）
            studentInfo.value = res.data;

            // 为字段赋值（不包括由StudentHeader管理的字段）
            userAvatarUrl.value = res.data.userAvatarUrl || "";
            userAvatar.value = res.data.userAvatar || "👨‍💻";
            birthDate.value = res.data.birthDate || "";
            hometown.value = res.data.hometown || "";
            politicalStatus.value = res.data.politicalStatus || "";
            email.value = res.data.email || "";
            phone.value = res.data.phone || "";
            website.value = res.data.website || "";
            bio.value = res.data.bio || "";
            hobbies.value = Array.isArray(res.data.hobbies)
                ? [...res.data.hobbies]
                : [];
            skills.value = Array.isArray(res.data.skills)
                ? [...res.data.skills]
                : [];
            education.value = Array.isArray(res.data.education)
                ? [...res.data.education]
                : [];
        })
        .catch((err) => {
            isLoading.value = false;
            errorMsg.value = "网络请求错误，无法加载个人信息";
            console.error("请求失败:", err);

            // 加载失败时使用默认数据
            setDefaultData();
        });
});

// 设置默认数据（当接口请求失败时）
const setDefaultData = () => {
    const defaultData = {
        userAvatarUrl: "",
        userAvatar: "👨‍💻",
        userName: "姚竣博",
        studentId: "20232132055",
        className: "计算机科学与技术 2023级",
        major: "计算机科学与技术",
        birthDate: "2005-01-15",
        hometown: "广东省广州市",
        politicalStatus: "团员",
        email: "zhangsan@example.com",
        phone: "13800138000",
        website: "",
        bio: "我是一名计算机科学与技术专业的学生...",
        hobbies: ["编程", "篮球", "音乐", "阅读"],
        skills: [{ name: "JavaScript", level: "中级" }],
        education: [
            {
                school: "华南师范大学",
                period_s: "2021-09-01",
                period_e: "2025-06-30",
                major: "计算机科学与技术",
                degree: "本科",
            },
        ],
    };

    studentInfo.value = defaultData;
    // 填充表单数据（不包括由StudentHeader管理的字段）
    const fieldsToSet = [
        "userAvatarUrl",
        "userAvatar",
        "birthDate",
        "hometown",
        "politicalStatus",
        "email",
        "phone",
        "website",
        "bio",
        "hobbies",
        "skills",
        "education",
    ];

    fieldsToSet.forEach((key) => {
        if (key in defaultData && this[key] !== undefined) {
            this[key] = defaultData[key];
        }
    });
};

// 计算属性
const sortedKnowledgeList = computed(() => {
    return [...knowledgeList.value].sort((a, b) => a.id - b.id);
});

// 头像样式计算
const avatarClass = computed(() => {
    return "avatar-gradient";
});
</script>
<style scoped>
/* 头像上传区域样式 */
.avatar-section {
    background: linear-gradient(135deg, #4a6fa5 0%, #36cbcb 100%);
    color: white;
    padding: 35px;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    margin-bottom: 30px;
    display: flex;
    justify-content: center;
}

/* 头像相关样式 */
.avatar-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
}

.avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    transition: all 0.4s ease;
    border: 3px solid rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
    cursor: pointer;
    margin: 0;
}

.custom-avatar {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}

.avatar-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
    border-radius: 50%;
}

.avatar:hover .avatar-overlay {
    opacity: 1;
}

.overlay-text {
    font-size: 14px;
    font-weight: 500;
    transform: translateY(5px);
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
    gap: 10px;
    width: 100%;
    max-width: 220px;
    padding: 0 5px;
    box-sizing: border-box;
}

.action-btn {
    padding: 7px 0;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
    font-weight: 500;
    flex: 1;
    text-align: center;
}

.upload-btn {
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
    color: white;
}

.upload-btn:hover {
    box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
    transform: translateY(-2px);
}

.reset-btn {
    background-color: #f0f7ff;
    color: #4a6fa5;
    border: 1px solid #d1e0f5;
}

.reset-btn:hover {
    background-color: #e6f0ff;
    transform: translateY(-2px);
}

/* 全局样式 */
.user-info-container {
    padding: 30px;
    background-color: #f7f9fc;
    min-height: 100vh;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    color: #333;
    line-height: 1.6;
}

.user-info-header {
    position: relative;
    background: linear-gradient(135deg, #4a6fa5 0%, #36cbcb 100%);
    color: white;
    padding: 35px;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    margin-bottom: 30px;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.user-info-header:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.header-decoration {
    position: absolute;
    top: 0;
    right: 0;
    width: 300px;
    height: 300px;
    background: radial-gradient(
        circle,
        rgba(255, 255, 255, 0.1) 0%,
        rgba(255, 255, 255, 0) 70%
    );
    border-radius: 50%;
    transform: translate(30%, -30%);
    z-index: 0;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}

.avatar-container {
    display: flex;
    align-items: center;
}

.avatar-gradient {
    background: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.9),
        rgba(255, 255, 255, 0.7)
    );
    color: #4a6fa5;
}

.avatar:hover {
    transform: scale(1.08) rotate(5deg);
}

.user-basic {
    margin: 0 0 0 20px;
}

.user-basic h2 {
    font-size: 32px;
    margin: 0 0 8px 0;
    color: white;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-name,
.user-id,
.user-class,
.user-major {
    font-size: 15px;
    opacity: 0.92;
    margin: 4px 0;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    color: white;
}

.edit-btn {
    background-color: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(5px);
    color: white;
    border: none;
    padding: 11px 22px;
    border-radius: 30px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 500;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.edit-btn:hover {
    background-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-3px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.edit-icon {
    transition: transform 0.3s ease;
}

.rotate-icon {
    transform: rotate(180deg);
}

.user-info-content {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    width: 100%;
}

.full-width-card {
    grid-column: 1 / -1;
}

.info-card {
    background-color: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.03);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.info-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
    transform: scaleX(0);
    transform-origin: left center;
    transition: transform 0.3s ease;
}

.info-card:hover::before {
    transform: scaleX(1);
}

.info-card:hover {
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    transform: translateY(-5px);
}

.info-card.editing {
    border: 1px dashed #36cbcb;
    background-color: #fcfdff;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
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

input,
textarea,
select {
    width: 80%;
    padding: 11px 10px;
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
}

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

.remove-hobby {
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
}

.remove-hobby:hover {
    background-color: #e74c3c;
    color: white;
}

/* 技能特长样式 */
.skills-container {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.skill-item {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 12px 15px;
    background-color: #f9fbfd;
    border-radius: 10px;
    transition: all 0.3s ease;
    border-left: 3px solid transparent;
}

.skill-item:hover {
    background-color: #f0f7ff;
    transform: translateX(5px);
    border-left-color: #4a6fa5;
}

.skill-name {
    flex: 0 0 200px;
    font-weight: 600;
    padding-right: 15px;
    border-right: 1px dashed #e1e5eb;
}

.skill-level-container {
    flex: 1;
    padding: 0 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.skill-progress-container {
    height: 10px;
    width: 100%;
    background-color: #f0f2f5;
    border-radius: 5px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* 技能进度条基础样式 */
.skill-progress-bar {
    height: 100%;
    border-radius: 5px;
    transition: width 1s ease-in-out;
    position: relative;
}

/* 金色进度条闪闪发光动画效果 */
.skill-progress-bar[data-level="精通"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.9) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    transform: skewX(-25deg);
    animation: goldShine 1.5s infinite;
}

/* 金色进度条额外光点效果 */
.skill-progress-bar[data-level="精通"]::after {
    content: "";
    position: absolute;
    width: 100%;
    height: 100%;
    background: radial-gradient(
        circle at var(--random-x) var(--random-y),
        rgba(255, 255, 255, 0.6) 0%,
        rgba(255, 255, 255, 0) 8%
    );
    animation: sparkle 1.5s infinite;
}

/* 闪光动画 */
@keyframes goldShine {
    0% {
        left: -100%;
    }
    100% {
        left: 200%;
    }
}

/* 随机光点动画 */
@keyframes sparkle {
    0% {
        --random-x: 20%;
        --random-y: 40%;
        opacity: 0.6;
    }
    25% {
        --random-x: 70%;
        --random-y: 20%;
        opacity: 0.8;
    }
    50% {
        --random-x: 40%;
        --random-y: 80%;
        opacity: 0.6;
    }
    75% {
        --random-x: 90%;
        --random-y: 60%;
        opacity: 0.7;
    }
    100% {
        --random-x: 30%;
        --random-y: 30%;
        opacity: 0.5;
    }
}

.skill-level-text {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
}

.skill-description {
    color: #6c7a89;
    font-size: 13px;
    font-style: italic;
}

/* 熟练度文本样式 */
.level-beginner {
    color: #ff4757; /* 红色 */
    font-weight: 600;
    text-shadow: 0 0 3px rgba(255, 71, 87, 0.2);
}

.level-intermediate {
    color: #ff7b29; /* 橙色（替换黄色） */
    font-weight: 600;
    text-shadow: 0 0 3px rgba(255, 123, 41, 0.2);
}

.level-advanced {
    color: #26a69a; /* 绿色 */
    font-weight: 600;
    text-shadow: 0 0 3px rgba(38, 166, 154, 0.2);
}

.level-expert {
    color: #ffd700; /* 金色 */
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.7);
    font-weight: 600;
}

/* 为金色进度条容器添加额外样式 */
.skill-item:nth-child(4) .skill-progress-container {
    border: 1px solid rgba(255, 215, 0, 0.3);
}

.skill-actions {
    flex: 0 0 80px;
    text-align: right;
}

.skill-actions button {
    padding: 6px 12px;
    background-color: #fdecea;
    color: #e74c3c;
    border: 1px solid #fcd9cf;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.skill-actions button:hover {
    background-color: #e74c3c;
    color: white;
}

.add-skill {
    margin-top: 15px;
    text-align: center;
}

.add-skill button {
    padding: 9px 18px;
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.add-skill button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
}

.education-container {
    margin-top: 15px;
}

.education-item {
    display: grid;
    grid-template-columns: 2fr 2fr 2fr 1.5fr auto;
    gap: 20px;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px 0;
    border-bottom: 1px dashed #f0f2f5;
}

.education-item:last-child {
    border-bottom: none;
}

.edu-dates {
    display: flex;
    align-items: center;
}

.date-inputs {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 0;
    margin: 0;
    border-bottom: none;
}

.date-inputs input {
    width: 100%;
    min-width: 120px;
}

.edu-major,
.edu-school {
    width: 100%;
}

.edu-degree {
    width: 100%;
}

.edu-actions {
    white-space: nowrap;
}

.date-separator {
    color: #6c7a89;
    font-weight: 500;
    padding: 0 2px;
}

.edu-actions button {
    padding: 6px 12px;
    background-color: #fdecea;
    color: #e74c3c;
    border: 1px solid #fcd9cf;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.edu-actions button:hover {
    background-color: #e74c3c;
    color: white;
}

.add-education {
    margin-top: 15px;
    text-align: center;
}

.add-education button {
    padding: 9px 18px;
    background: linear-gradient(90deg, #4a6fa5, #36cbcb);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.add-education button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
}

/* 响应式调整 */
@media (max-width: 992px) {
    .user-info-content {
        grid-template-columns: 1fr;
    }

    .skill-name {
        flex: 0 0 150px;
    }
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        text-align: center;
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
    }

    .edit-btn {
        margin-top: 15px;
        width: 100%;
        justify-content: center;
    }

    .skill-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .skill-name {
        flex: none;
        width: 100%;
        border-right: none;
        border-bottom: 1px dashed #e1e5eb;
        padding-bottom: 8px;
        margin-bottom: 8px;
    }

    .skill-level-container {
        flex: none;
        width: 100%;
        padding: 0;
    }

    .skill-actions {
        flex: none;
        width: 100%;
        text-align: left;
        margin-top: 10px;
    }

    .user-info-container {
        padding: 20px 15px;
    }

    .info-card {
        padding: 20px 15px;
    }

    .education-item {
        grid-template-columns: 1fr 1fr;
        gap: 15px;
    }
}

@media (max-width: 480px) {
    .education-item {
        grid-template-columns: 1fr;
    }
    .date-inputs input {
        width: 45%;
    }
}

/* 编辑按钮区域样式 */
.edit-button-section {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
}

.edit-button-section .edit-btn {
    background-color: rgba(74, 111, 165, 0.9);
    color: white;
    border: none;
    padding: 11px 22px;
    border-radius: 30px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 500;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.edit-button-section .edit-btn:hover {
    background-color: rgba(74, 111, 165, 1);
    transform: translateY(-3px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 返回首页按钮样式 */
.back-to-home {
    position: fixed;
    right: 30px;
    bottom: 30px;
    display: flex;
    align-items: center;
    justify-content: center; /* 居中图标 */
    gap: 0; /* 初始无间距 */
    padding: 12px; /* 小球状态的内边距 */
    width: 50px; /* 小球宽度 */
    height: 50px; /* 小球高度 */
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 50%, #3b82f6 100%);
    color: white;
    border-radius: 50%; /* 初始圆形 */
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
    transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); /* 平滑过渡 */
    z-index: 9999;
    border: none;
    cursor: pointer;
    font-weight: 500;
    overflow: hidden; /* 隐藏溢出内容 */
}

.back-to-home .icon {
    font-size: 18px;
    transition: transform 0.5s ease; /* 图标旋转动画 */
}

.back-to-home span:not(.icon) {
    opacity: 0; /* 文字初始隐藏 */
    width: 0; /* 文字初始宽度为0 */
    transition: all 0.5s ease; /* 文字显示动画 */
    white-space: nowrap; /* 防止文字换行 */
}

/* 悬停状态 - 展开成椭圆 */
.back-to-home:hover {
    width: 180px; /* 展开后的宽度 */
    height: 50px; /* 保持高度不变 */
    border-radius: 50px; /* 椭圆效果 */
    padding: 12px 20px; /* 展开后的内边距 */
    gap: 8px; /* 图标与文字间距 */
    transform: translateY(-5px); /* 轻微上浮 */
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4);
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #4f46e5 100%);
}

/* 悬停时显示文字并添加滚动效果 */
.back-to-home:hover span:not(.icon) {
    opacity: 1; /* 显示文字 */
    width: auto; /* 恢复文字宽度 */
    animation: slideIn 0.5s ease forwards; /* 文字滑入动画 */
}

/* 悬停时图标旋转 */
.back-to-home:hover .icon {
    transform: rotate(360deg); /* 图标旋转一周 */
}

.back-to-home:active {
    transform: translateY(-2px);
}

/* 文字滑入动画 */
@keyframes slideIn {
    from {
        transform: translateX(-20px); /* 从左侧进入 */
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
.bth-text {
    color: white;
}
</style>
