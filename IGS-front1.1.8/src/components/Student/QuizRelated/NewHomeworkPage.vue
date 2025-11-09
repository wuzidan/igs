<template>
    <div class="homework-doing-container">
        <!-- 题目头部信息 -->
        <div class="question-header">
            <div class="question-progress">
                <span
                    >第{{ currentQuestionIndex + 1 }}/{{
                        totalQuestions
                    }}题</span
                >
                <div class="progress-container">
                    <div
                        class="progress progress-high"
                        :style="{
                            width:
                                ((currentQuestionIndex + 1) / totalQuestions) *
                                    100 +
                                '%',
                        }"
                    ></div>
                </div>
            </div>
            <button class="exit-btn" @click="exitHomework">退出</button>
        </div>

        <!-- 题目内容区域 -->
        <div class="question-doing-content">
            <div class="question-number">{{ currentQuestionIndex + 1 }}.</div>
            <div class="question-text">{{ currentQuestion.content }}</div>

            <!-- 单选/多选题选项 -->
            <div
                class="question-options"
                v-if="
                    ['singleChoice', 'multipleChoice'].includes(
                        currentQuestion.type
                    )
                "
            >
                <div
                    class="option-item"
                    v-for="(option, index) in currentQuestion.options"
                    :key="index"
                    @click="handleOptionSelect(index)"
                    :class="{
                        'option-selected': isOptionSelected(index),
                        'option-correct': showAnswers && isCorrectAnswer(index),
                        'option-incorrect':
                            showAnswers &&
                            isOptionSelected(index) &&
                            !isCorrectAnswer(index),
                    }"
                >
                    <span class="option-letter"
                        >{{ String.fromCharCode(65 + index) }}.</span
                    >
                    <span class="option-text">{{ option }}</span>
                </div>
            </div>

            <!-- 判断题选项 -->
            <div
                class="judgment-options"
                v-if="currentQuestion.type === 'judgment'"
            >
                <div
                    class="judgment-option"
                    @click="handleJudgmentSelect(0)"
                    :class="{
                        'judgment-selected':
                            userAnswers[currentQuestionIndex] === 0,
                        'option-correct':
                            showAnswers && currentQuestion.correctAnswer === 0,
                        'option-incorrect':
                            showAnswers &&
                            userAnswers[currentQuestionIndex] === 0 &&
                            currentQuestion.correctAnswer !== 0,
                    }"
                >
                    正确
                </div>
                <div
                    class="judgment-option"
                    @click="handleJudgmentSelect(1)"
                    :class="{
                        'judgment-selected':
                            userAnswers[currentQuestionIndex] === 1,
                        'option-correct':
                            showAnswers && currentQuestion.correctAnswer === 1,
                        'option-incorrect':
                            showAnswers &&
                            userAnswers[currentQuestionIndex] === 1 &&
                            currentQuestion.correctAnswer !== 1,
                    }"
                >
                    错误
                </div>
            </div>

            <!-- 简答题区域 -->
            <div
                class="answer-area"
                v-if="currentQuestion.type === 'shortAnswer'"
            >
                <textarea
                    v-model="userAnswers[currentQuestionIndex]"
                    placeholder="请输入答案..."
                    :disabled="showAnswers"
                ></textarea>
            </div>
        </div>

        <!-- 题目操作按钮 -->
        <div class="question-actions">
            <button
                class="nav-btn prev-btn"
                @click="goToPreviousQuestion"
                :disabled="currentQuestionIndex === 0"
            >
                上一题
            </button>
            <button
                class="nav-btn next-btn"
                @click="goToNextQuestion"
                :disabled="currentQuestionIndex === totalQuestions - 1"
            >
                下一题
            </button>
            <button
                class="submit-btn"
                @click="submitHomework"
                v-if="currentQuestionIndex === totalQuestions - 1"
            >
                提交作业
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, reactive } from "vue";

// 模拟数据 - 在实际使用时应该从父组件或API获取
const mockHomework = reactive({
    id: 1,
    title: "练习作业 #4",
    questions: [
        {
            id: 1,
            type: "singleChoice",
            content: "SQL中用于插入数据的语句是?",
            options: ["UPDATE", "INSERT", "SELECT", "DELETE"],
            correctAnswer: 1, // B选项
        },
        {
            id: 2,
            type: "judgment",
            content: "Vue是一个渐进式JavaScript框架。",
            correctAnswer: 0, // 正确
        },
        {
            id: 3,
            type: "multipleChoice",
            content: "以下哪些是JavaScript的基本数据类型?",
            options: ["String", "Number", "Boolean", "Array"],
            correctAnswer: [0, 1, 2], // A、B、C选项
        },
    ],
});

// 当前作业数据
const currentHomework = ref(mockHomework);
// 当前题目索引
const currentQuestionIndex = ref(0);
// 用户答案数组
const userAnswers = ref([]);
// 是否显示答案解析
const showAnswers = ref(false);

// 计算属性
const totalQuestions = computed(() => currentHomework.value.questions.length);
const currentQuestion = computed(
    () => currentHomework.value.questions[currentQuestionIndex.value]
);

// 初始化用户答案数组
const initializeUserAnswers = () => {
    userAnswers.value = new Array(totalQuestions.value).fill(null);
};

// 检查选项是否被选中
const isOptionSelected = (index) => {
    const answer = userAnswers.value[currentQuestionIndex.value];
    if (!answer) return false;

    if (currentQuestion.value.type === "singleChoice") {
        return answer === index;
    } else if (currentQuestion.value.type === "multipleChoice") {
        return Array.isArray(answer) && answer.includes(index);
    }
    return false;
};

// 检查选项是否是正确答案
const isCorrectAnswer = (index) => {
    const correctAnswer = currentQuestion.value.correctAnswer;
    if (!correctAnswer) return false;

    if (currentQuestion.value.type === "singleChoice") {
        return correctAnswer === index;
    } else if (currentQuestion.value.type === "multipleChoice") {
        return Array.isArray(correctAnswer) && correctAnswer.includes(index);
    }
    return false;
};

// 处理选项选择（单选/多选）
const handleOptionSelect = (index) => {
    if (showAnswers.value) return;

    // 创建新数组以确保响应式更新
    const newAnswers = [...userAnswers.value];

    if (currentQuestion.value.type === "singleChoice") {
        // 单选题直接设置答案
        newAnswers[currentQuestionIndex.value] = index;

        // 保存答案后跳转到下一题（如果有）
        userAnswers.value = newAnswers;
        if (currentQuestionIndex.value < totalQuestions.value - 1) {
            setTimeout(() => {
                goToNextQuestion();
            }, 300); // 短暂延迟，让用户能看到选中效果
        }
    } else if (currentQuestion.value.type === "multipleChoice") {
        // 多选题处理
        if (!Array.isArray(newAnswers[currentQuestionIndex.value])) {
            newAnswers[currentQuestionIndex.value] = [];
        }

        const currentAnswers = [...newAnswers[currentQuestionIndex.value]];
        const optionIndex = currentAnswers.indexOf(index);

        if (optionIndex === -1) {
            currentAnswers.push(index);
        } else {
            currentAnswers.splice(optionIndex, 1);
        }

        newAnswers[currentQuestionIndex.value] = currentAnswers;
        userAnswers.value = newAnswers;
        // 多选题不自动跳转
    }
};

// 处理判断题选择
const handleJudgmentSelect = (value) => {
    if (showAnswers.value) return;

    // 创建新数组以确保响应式更新
    const newAnswers = [...userAnswers.value];
    newAnswers[currentQuestionIndex.value] = value;

    // 保存答案后跳转到下一题（如果有）
    userAnswers.value = newAnswers;
    if (currentQuestionIndex.value < totalQuestions.value - 1) {
        setTimeout(() => {
            goToNextQuestion();
        }, 300); // 短暂延迟，让用户能看到选中效果
    }
};

// 跳转到上一题
const goToPreviousQuestion = () => {
    if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--;
    }
};

// 跳转到下一题
const goToNextQuestion = () => {
    if (currentQuestionIndex.value < totalQuestions.value - 1) {
        currentQuestionIndex.value++;
    }
};

// 退出作业
const exitHomework = () => {
    if (confirm("确定要退出当前作业吗？未完成的部分将不会保存。")) {
        // 这里可以添加退出逻辑，比如返回上一页
        console.log("用户退出作业");
    }
};

// 提交作业
const submitHomework = () => {
    if (confirm("确定要提交作业吗？提交后将无法修改。")) {
        console.log("用户提交作业，答案为：", userAnswers.value);
        // 这里可以添加提交作业的逻辑
    }
};

// 组件初始化
initializeUserAnswers();
</script>

<style scoped>
.homework-doing-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.question-progress {
    flex: 1;
}

.progress-container {
    height: 8px;
    background-color: #e0e0e0;
    border-radius: 4px;
    margin-top: 8px;
    overflow: hidden;
}

.progress {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.progress-high {
    background-color: #4caf50;
}

.exit-btn {
    background-color: #f44336;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.exit-btn:hover {
    background-color: #d32f2f;
}

.question-doing-content {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.question-number {
    font-weight: bold;
    margin-bottom: 10px;
}

.question-text {
    font-size: 18px;
    margin-bottom: 20px;
}

.question-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.option-item {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.option-item:hover {
    background-color: #f0f0f0;
    border-color: #bbb;
}

.option-item.option-selected {
    background-color: #e3f2fd;
    border-color: #2196f3;
    color: #1565c0;
}

.option-item.option-correct {
    background-color: #e8f5e9;
    border-color: #4caf50;
    color: #2e7d32;
}

.option-item.option-incorrect {
    background-color: #ffebee;
    border-color: #f44336;
    color: #c62828;
}

.option-letter {
    font-weight: bold;
    margin-right: 12px;
}

.judgment-options {
    display: flex;
    gap: 20px;
}

.judgment-option {
    flex: 1;
    padding: 16px;
    text-align: center;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    font-size: 18px;
    transition: all 0.2s ease;
}

.judgment-option:hover {
    background-color: #f0f0f0;
    border-color: #bbb;
}

.judgment-option.judgment-selected {
    background-color: #e3f2fd;
    border-color: #2196f3;
    color: #1565c0;
}

.judgment-option.option-correct {
    background-color: #e8f5e9;
    border-color: #4caf50;
    color: #2e7d32;
}

.judgment-option.option-incorrect {
    background-color: #ffebee;
    border-color: #f44336;
    color: #c62828;
}

.answer-area {
    margin-top: 10px;
}

.answer-area textarea {
    width: 100%;
    min-height: 150px;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    resize: vertical;
}

.answer-area textarea:focus {
    outline: none;
    border-color: #2196f3;
}

.question-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

.nav-btn {
    padding: 10px 20px;
    border: 2px solid #2196f3;
    background-color: white;
    color: #2196f3;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.2s ease;
}

.nav-btn:hover:not(:disabled) {
    background-color: #2196f3;
    color: white;
}

.nav-btn:disabled {
    border-color: #ccc;
    color: #ccc;
    cursor: not-allowed;
}

.submit-btn {
    padding: 10px 20px;
    border: none;
    background-color: #4caf50;
    color: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.2s ease;
}

.submit-btn:hover {
    background-color: #45a049;
}
</style>
