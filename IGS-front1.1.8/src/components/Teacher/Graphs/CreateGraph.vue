<template>
    <a href="/teacher/graph" class="back-to-list">
        <span class="icon">←</span>
        <span>返回知识图谱列表</span>
    </a>

    <div class="create-graph-container">
        <div class="page-header">
            <h2>创建知识图谱</h2>
            <p>创建新的知识图谱资源，完善图谱基本信息</p>
        </div>

        <div class="card create-form-container">
            <h3>基本信息设置</h3>

            <form @submit.prevent="submitGraph">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="graph-name"
                            >图谱名称 <span class="required">*</span></label
                        >
                        <input
                            type="text"
                            id="graph-name"
                            v-model="graphForm.name"
                            class="input-field"
                            placeholder="请输入知识图谱名称"
                            required
                        />
                        <p class="form-hint">
                            请输入清晰描述图谱内容的名称，便于识别
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="graph-domain"
                            >知识领域 <span class="required">*</span></label
                        >
                        <select
                            id="graph-domain"
                            v-model="graphForm.domainId"
                            class="input-field"
                            required
                        >
                            <option value="">请选择知识领域</option>
                            <option
                                v-for="domain in domains"
                                :key="domain.id"
                                :value="domain.id"
                            >
                                {{ domain.name }}
                            </option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="graph-type"
                            >图谱类型 <span class="required">*</span></label
                        >
                        <select
                            id="graph-type"
                            v-model="graphForm.type"
                            class="input-field"
                            required
                        >
                            <option value="">请选择图谱类型</option>
                            <option value="concept">概念图谱</option>
                            <option value="relationship">关系图谱</option>
                            <option value="hierarchical">层级图谱</option>
                            <option value="integrated">综合图谱</option>
                        </select>
                        <p class="form-hint">
                            概念图谱：侧重概念定义与解释<br />
                            关系图谱：侧重实体间关系展示<br />
                            层级图谱：侧重层级结构展示<br />
                            综合图谱：包含多种类型特征
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="graph-status">初始状态</label>
                        <select
                            id="graph-status"
                            v-model="graphForm.status"
                            class="input-field"
                        >
                            <option value="draft">草稿</option>
                            <option value="published">已发布</option>
                        </select>
                    </div>

                    <div class="form-group full-width">
                        <label for="graph-description">图谱描述</label>
                        <textarea
                            id="graph-description"
                            v-model="graphForm.description"
                            class="input-field textarea-field"
                            placeholder="请描述该知识图谱的内容、用途或特点..."
                            rows="4"
                        ></textarea>
                    </div>

                    <div class="form-group full-width">
                        <label for="graph-tags">标签</label>
                        <input
                            type="text"
                            id="graph-tags"
                            v-model="graphForm.tags"
                            class="input-field"
                            placeholder="请输入标签，多个标签用逗号分隔"
                        />
                        <p class="form-hint">添加标签有助于快速检索和分类</p>
                    </div>
                </div>

                <div class="form-actions">
                    <button
                        type="button"
                        class="btn btn-cancel"
                        @click="cancelCreate"
                    >
                        取消
                    </button>
                    <button
                        type="button"
                        class="btn btn-save"
                        @click="saveAsDraft"
                    >
                        保存为草稿
                    </button>
                    <button type="submit" class="btn btn-create">
                        创建并进入编辑
                    </button>
                </div>
            </form>
        </div>

        <div class="card template-section">
            <h3>使用模板创建</h3>
            <p class="section-desc">选择以下模板快速创建知识图谱</p>

            <div class="template-grid">
                <div
                    class="template-card"
                    v-for="template in templates"
                    :key="template.id"
                    @click="useTemplate(template.id)"
                >
                    <div
                        class="template-preview"
                        :style="template.previewStyle"
                    ></div>
                    <div class="template-info">
                        <h4>{{ template.name }}</h4>
                        <p>{{ template.description }}</p>
                        <span class="template-type">{{
                            template.typeText
                        }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 知识领域数据
const domains = ref([
    { id: 1, name: "计算机科学" },
    { id: 2, name: "数学" },
    { id: 3, name: "物理学" },
    { id: 4, name: "生物学" },
    { id: 5, name: "工程技术" },
]);

// 图谱模板数据
const templates = ref([
    {
        id: 1,
        name: "基础概念图谱模板",
        description: "适用于构建基础概念及定义的知识图谱",
        type: "concept",
        typeText: "概念图谱",
        previewStyle: {
            background: "linear-gradient(135deg, #3498db10, #2980b915)",
        },
    },
    {
        id: 2,
        name: "实体关系模板",
        description: "适用于展示实体间复杂关系的知识图谱",
        type: "relationship",
        typeText: "关系图谱",
        previewStyle: {
            background: "linear-gradient(135deg, #9b59b610, #8e44ad15)",
        },
    },
    {
        id: 3,
        name: "学科体系模板",
        description: "适用于构建学科知识体系的层级图谱",
        type: "hierarchical",
        typeText: "层级图谱",
        previewStyle: {
            background: "linear-gradient(135deg, #1abc9c10, #16a08515)",
        },
    },
]);

// 表单数据
const graphForm = ref({
    name: "",
    domainId: "",
    type: "",
    status: "draft",
    description: "",
    tags: "",
});

// 提交表单
const submitGraph = () => {
    // 验证表单
    if (
        !graphForm.value.name ||
        !graphForm.value.domainId ||
        !graphForm.value.type
    ) {
        alert("请填写必填字段");
        return;
    }

    // 这里添加创建图谱的逻辑
    console.log("创建知识图谱:", graphForm.value);

    // 实际应用中，这里会调用API创建图谱
    // 创建成功后跳转到编辑页面
    alert("图谱创建成功，即将进入编辑页面");
    router.push(`/teacher/graphs/edit/new`);
};

// 保存为草稿
const saveAsDraft = () => {
    // 验证必要字段
    if (
        !graphForm.value.name ||
        !graphForm.value.domainId ||
        !graphForm.value.type
    ) {
        alert("请填写必填字段");
        return;
    }

    // 设置状态为草稿
    graphForm.value.status = "draft";

    // 这里添加保存为草稿的逻辑
    console.log("保存为草稿:", graphForm.value);

    // 实际应用中，这里会调用API保存
    alert("已保存为草稿");
    router.push(`/teacher/graph`);
};

// 取消创建
const cancelCreate = () => {
    if (confirm("确定要取消创建吗？已填写的内容将不会保存")) {
        router.push(`/teacher/graph`);
    }
};

// 使用模板创建
const useTemplate = (templateId) => {
    const template = templates.value.find((t) => t.id === templateId);
    if (template) {
        // 填充模板数据到表单
        graphForm.value.type = template.type;
        graphForm.value.name = template.name;
        graphForm.value.description = template.description;

        alert(`已选择"${template.name}"模板，表单已自动填充相关信息`);
    }
};
</script>

<style scoped>
/* 整体容器样式 */
.create-graph-container {
    width: 100%;
    padding: 0;
    margin: 0;
}

/* 返回列表按钮 */
.back-to-list {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background-color: #f1f5f9;
    color: #334155;
    border-radius: 6px;
    text-decoration: none;
    margin-bottom: 20px;
    font-size: 14px;
    transition: all 0.3s ease;
}

.back-to-list:hover {
    background-color: #e2e8f0;
    color: #1e293b;
    transform: translateX(-3px);
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

/* 卡片样式 - 保持统一设计 */
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

/* 表单样式 */
.form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.form-group {
    margin-bottom: 0;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.95;
}

.card:hover .form-group {
    transform: translateX(3px);
    opacity: 1;
}

.form-group.full-width {
    grid-column: 1 / -1;
}

.form-group label {
    display: block;
    font-size: 14px;
    color: #555;
    margin-bottom: 8px;
    font-weight: 500;
}

.required {
    color: #e74c3c;
}

.form-hint {
    margin: 6px 0 0 0;
    font-size: 12px;
    color: #888;
    line-height: 1.5;
}

.textarea-field {
    resize: vertical;
}

/* 输入框样式统一 */
.input-field {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.3s ease;
}

.input-field:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
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

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.btn-cancel {
    background-color: #f1f5f9;
    color: #334155;
}

.btn-cancel:hover {
    background-color: #e2e8f0;
    color: #1e293b;
    transform: translateY(-2px);
}

.btn-save {
    background: linear-gradient(135deg, #f39c12, #d35400);
    color: white;
}

.btn-save:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(243, 156, 18, 0.4);
    background: linear-gradient(135deg, #f8c471, #e67e22);
}

.btn-create {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: white;
}

.btn-create:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(46, 204, 113, 0.4);
    background: linear-gradient(135deg, #58d68d, #27ae60);
}

/* 模板区域样式 */
.template-section {
    margin-top: 30px;
}

.section-desc {
    margin: -10px 0 20px 24px;
    color: #666;
    font-size: 14px;
}

.template-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 10px;
}

.template-card {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #f0f0f0;
    transition: all 0.3s ease;
    cursor: pointer;
}

.template-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 10px 20px rgba(59, 130, 246, 0.1);
    border-color: rgba(191, 219, 254, 0.5);
}

.template-preview {
    height: 120px;
    background-color: #fafafa;
}

.template-info {
    padding: 15px;
}

.template-info h4 {
    margin: 0 0 8px 0;
    font-size: 16px;
    color: #1e3a8a;
}

.template-info p {
    margin: 0 0 10px 0;
    font-size: 13px;
    color: #666;
    line-height: 1.5;
}

.template-type {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 12px;
    background-color: #eff6ff;
    color: #2563eb;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .form-grid {
        grid-template-columns: 1fr;
    }

    .form-actions {
        flex-direction: column;
    }

    .btn {
        width: 100%;
    }

    .template-grid {
        grid-template-columns: 1fr;
    }
}
</style>
