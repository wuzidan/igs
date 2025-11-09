<template>
    <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>

    <div class="new-exercise-container">
        <div class="page-header">
            <h2>设计新题</h2>
            <p>创建新的习题内容</p>
        </div>

        <!-- 使用统一的card样式包裹表单 -->
        <div class="card exercise-form-container">
            <h3>习题信息</h3>
            <form class="exercise-form" @submit.prevent="submitExercise">
                <div class="form-group">
                    <label for="subject-select">学科:</label>
                    <select
                        id="subject-select"
                        v-model="formData.subjectId"
                        required
                        class="input-field"
                    >
                        <option value="">请选择学科</option>
                        <option
                            v-for="subject in subjects"
                            :key="subject.id"
                            :value="subject.id"
                        >
                            {{ subject.name }}
                        </option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="difficulty-select">难度:</label>
                    <select
                        id="difficulty-select"
                        v-model="formData.difficulty"
                        required
                        class="input-field"
                    >
                        <option value="">请选择难度</option>
                        <option value="easy">简单</option>
                        <option value="medium">中等</option>
                        <option value="hard">困难</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="exercise-type">题型:</label>
                    <select
                        id="exercise-type"
                        v-model="formData.type"
                        @change="onTypeChange"
                        required
                        class="input-field"
                    >
                        <option value="">请选择题型</option>
                        <option value="single-choice">单选题</option>
                        <option value="multiple-choice">多选题</option>
                        <option value="true-false">判断题</option>
                        <option value="blank">填空题</option>
                        <option value="essay">简答题</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="exercise-title">题目:</label>
                    <textarea
                        id="exercise-title"
                        v-model="formData.title"
                        placeholder="输入题目内容"
                        required
                        class="input-field"
                    ></textarea>
                </div>

                <!-- 选项区域 - 根据题型动态显示 -->
                <div
                    v-if="
                        formData.type === 'single-choice' ||
                        formData.type === 'multiple-choice'
                    "
                    class="options-container"
                >
                    <h3>选项</h3>
                    <div
                        v-for="(option, index) in formData.options"
                        :key="index"
                        class="option-item"
                    >
                        <input
                            type="text"
                            v-model="option.content"
                            placeholder="选项内容"
                            :id="'option-' + index"
                            required
                            class="input-field"
                        />
                        <input
                            type="radio"
                            v-model="formData.correctAnswer"
                            :value="index"
                            :id="'correct-' + index"
                            v-if="formData.type === 'single-choice'"
                        />
                        <input
                            type="checkbox"
                            v-model="formData.correctAnswers"
                            :value="index"
                            :id="'correct-' + index"
                            v-if="formData.type === 'multiple-choice'"
                        />
                        <label :for="'correct-' + index">正确选项</label>
                        <button
                            type="button"
                            class="btn btn-remove-option"
                            @click="removeOption(index)"
                            :disabled="formData.options.length <= 2"
                        >
                            删除
                        </button>
                    </div>
                    <button
                        type="button"
                        class="btn btn-add-option"
                        @click="addOption"
                    >
                        添加选项
                    </button>
                </div>

                <!-- 判断题区域 -->
                <div
                    v-if="formData.type === 'true-false'"
                    class="true-false-container"
                >
                    <h3>答案</h3>
                    <div class="radio-group">
                        <input
                            type="radio"
                            id="true-option"
                            v-model="formData.correctAnswer"
                            value="true"
                        />
                        <label for="true-option">正确</label>
                        <input
                            type="radio"
                            id="false-option"
                            v-model="formData.correctAnswer"
                            value="false"
                        />
                        <label for="false-option">错误</label>
                    </div>
                </div>

                <!-- 填空题区域 -->
                <div v-if="formData.type === 'blank'" class="blank-container">
                    <h3>答案</h3>
                    <input
                        type="text"
                        v-model="formData.correctAnswer"
                        placeholder="输入正确答案"
                        required
                        class="input-field"
                    />
                </div>

                <!-- 简答题区域 -->
                <div v-if="formData.type === 'essay'" class="essay-container">
                    <h3>参考答案</h3>
                    <textarea
                        v-model="formData.correctAnswer"
                        placeholder="输入参考答案"
                        required
                        class="input-field"
                    ></textarea>
                </div>

                <div class="form-group">
                    <label for="exercise-explanation">解析:</label>
                    <textarea
                        id="exercise-explanation"
                        v-model="formData.explanation"
                        placeholder="输入题目解析（可选）"
                        class="input-field"
                    ></textarea>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn btn-submit">
                        保存习题
                    </button>
                    <button
                        type="button"
                        class="btn btn-preview"
                        @click="previewExercise"
                    >
                        预览
                    </button>
                    <button
                        type="button"
                        class="btn btn-reset"
                        @click="resetForm"
                    >
                        重置
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 学科数据
const subjects = ref([
    { id: 1, name: "编程基础" },
    { id: 2, name: "数据结构" },
    { id: 3, name: "算法设计" },
    { id: 4, name: "前端开发" },
    { id: 5, name: "后端开发" },
]);

// 表单数据
const formData = ref({
    subjectId: "",
    difficulty: "",
    type: "",
    title: "",
    options: [{ content: "" }, { content: "" }],
    correctAnswer: "",
    correctAnswers: [],
    explanation: "",
});

// 题型改变时重置相关字段
const onTypeChange = () => {
    formData.value.options = [{ content: "" }, { content: "" }];
    formData.value.correctAnswer = "";
    formData.value.correctAnswers = [];
};

// 添加选项
const addOption = () => {
    formData.value.options.push({ content: "" });
};

// 删除选项
const removeOption = (index) => {
    formData.value.options.splice(index, 1);
    // 如果删除的是正确选项，重置正确选项
    if (
        formData.value.type === "single-choice" &&
        formData.value.correctAnswer === index.toString()
    ) {
        formData.value.correctAnswer = "";
    }
    if (formData.value.type === "multiple-choice") {
        formData.value.correctAnswers = formData.value.correctAnswers.filter(
            (val) => val !== index
        );
    }
};

// 提交表单
const submitExercise = () => {
    // 这里添加表单验证和提交逻辑
    console.log("提交习题:", formData.value);
    // 实际应用中，这里会调用API提交习题
    // 提交成功后跳转到已设计习题页面
    router.push("/teacher/exercise/existing");
};

// 预览习题
const previewExercise = () => {
    // 这里添加预览逻辑
    console.log("预览习题:", formData.value);
    // 实际应用中，这里会打开预览对话框
};

// 重置表单
const resetForm = () => {
    formData.value = {
        subjectId: "",
        difficulty: "",
        type: "",
        title: "",
        options: [{ content: "" }, { content: "" }],
        correctAnswer: "",
        correctAnswers: [],
        explanation: "",
    };
};

// 组件挂载时执行
onMounted(() => {
    // 初始化数据
});
</script>

<style scoped>
/* 整体容器样式 */
.new-exercise-container {
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

/* 表单容器 */
.exercise-form-container {
    transition: box-shadow 0.3s ease;
}

/* 表单样式 */
.exercise-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
    transition: transform 0.3s ease;
}

.card:hover .exercise-form {
    transform: translateX(3px);
}

.form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 15px;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .form-group {
    transform: translateX(3px);
    opacity: 1;
}

.form-group label {
    font-size: 14px;
    color: #555;
    margin-bottom: 8px;
    font-weight: 500;
}

/* 输入框样式统一 */
.input-field {
    padding: 12px 15px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.3s ease;
    font-family: inherit;
}

.input-field:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.form-group textarea {
    min-height: 100px;
    resize: vertical;
}

/* 选项容器 */
.options-container {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .options-container {
    transform: translateX(3px);
    opacity: 1;
}

.options-container h3 {
    margin-top: 0;
    font-size: 16px;
    color: #333;
    font-weight: 600;
    margin-bottom: 15px;
}

.option-item {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 8px;
    transition: background-color 0.3s ease;
}

.option-item:hover {
    background-color: #e9ecef;
}

.option-item input[type="text"] {
    flex: 1;
}

.option-item input[type="radio"],
.option-item input[type="checkbox"] {
    width: 16px;
    height: 16px;
    cursor: pointer;
}

.option-item label {
    margin: 0;
    font-size: 14px;
    color: #666;
    cursor: pointer;
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

.btn-remove-option {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
    padding: 8px 16px;
    font-size: 12px;
}

.btn-remove-option:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(231, 76, 60, 0.3);
}

.btn-remove-option:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.btn-add-option {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    margin-top: 10px;
}

.btn-add-option:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

/* 判断题容器 */
.true-false-container {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .true-false-container {
    transform: translateX(3px);
    opacity: 1;
}

.true-false-container h3 {
    margin-top: 0;
    font-size: 16px;
    color: #333;
    font-weight: 600;
    margin-bottom: 15px;
}

.radio-group {
    display: flex;
    gap: 30px;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 8px;
}

.radio-group input[type="radio"] {
    width: 18px;
    height: 18px;
    margin-right: 8px;
    cursor: pointer;
}

.radio-group label {
    font-size: 14px;
    color: #333;
    cursor: pointer;
    display: flex;
    align-items: center;
}

/* 填空题和简答题容器 */
.blank-container,
.essay-container {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .blank-container,
.card:hover .essay-container {
    transform: translateX(3px);
    opacity: 1;
}

.blank-container h3,
.essay-container h3 {
    margin-top: 0;
    font-size: 16px;
    color: #333;
    font-weight: 600;
    margin-bottom: 15px;
}

.essay-container textarea {
    min-height: 150px;
}

/* 表单操作按钮 */
.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px solid #f0f0f0;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .form-actions {
    transform: translateX(3px);
    opacity: 1;
}

.btn-submit {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: white;
}

.btn-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(46, 204, 113, 0.4);
    background: linear-gradient(135deg, #58d68d, #27ae60);
}

.btn-preview {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-preview:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
    background: linear-gradient(135deg, #64b5f6, #2196f3);
}

.btn-reset {
    background: linear-gradient(135deg, #95a5a6, #7f8c8d);
    color: white;
}

.btn-reset:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(149, 165, 166, 0.4);
    background: linear-gradient(135deg, #bdc3c7, #95a5a6);
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .form-actions {
        justify-content: center;
        flex-wrap: wrap;
    }
}

@media (max-width: 768px) {
    .card {
        padding: 20px;
    }

    .option-item {
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
    }

    .radio-group {
        flex-direction: column;
        gap: 15px;
    }

    .input-field {
        padding: 10px 12px;
    }

    .btn {
        padding: 8px 16px;
        font-size: 13px;
    }

    .form-actions {
        flex-direction: column;
    }

    .form-actions button {
        width: 100%;
        margin-bottom: 10px;
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
