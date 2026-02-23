<template>
    <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>

    <div class="knowledge-graph-container">
        <div class="page-header">
            <h2>图谱管理</h2>
            <p>查看和管理系统中的所有知识图谱资源</p>
        </div>

        <!-- 筛选条件卡片 -->
        <div class="card filters-container">
            <h3>筛选条件</h3>
            <div class="filter-content">
                <div class="filter-group">
                    <div class="filter-item">
                        <label for="domain-select">知识领域:</label>
                        <select
                            id="domain-select"
                            v-model="selectedDomain"
                            class="input-field"
                            @change="onFiltersChange"
                        >
                            <option value="">全部领域</option>
                            <option
                                v-for="domain in domains"
                                :key="domain.id"
                                :value="domain.id"
                            >
                                {{ domain.name }}
                            </option>
                        </select>
                    </div>

                    <div class="filter-item">
                        <label for="graph-type">图谱类型:</label>
                        <select
                            id="graph-type"
                            v-model="selectedType"
                            class="input-field"
                            @change="onFiltersChange"
                        >
                            <option value="">全部类型</option>
                            <option value="concept">概念图谱</option>
                            <option value="relationship">关系图谱</option>
                            <option value="hierarchical">层级图谱</option>
                            <option value="integrated">综合图谱</option>
                        </select>
                    </div>

                    <div class="filter-item">
                        <label for="status-select">状态:</label>
                        <select
                            id="status-select"
                            v-model="selectedStatus"
                            class="input-field"
                            @change="onFiltersChange"
                        >
                            <option value="">全部状态</option>
                            <option value="draft">草稿</option>
                            <option value="published">已发布</option>
                            <option value="archived">已归档</option>
                        </select>
                    </div>
                </div>

                <div class="search-container">
                    <input
                        type="text"
                        placeholder="搜索图谱..."
                        v-model="searchKeyword"
                        @input="debounceSearch"
                        class="input-field"
                    />
                    <button class="btn btn-search" @click="searchGraphs">
                        搜索
                    </button>
                </div>
            </div>
        </div>

        <!-- 图谱列表卡片 -->
        <div class="card graph-list-container">
            <div class="card-header">
                <h3>知识图谱列表</h3>
                <button class="btn btn-create" @click="createNewGraph">
                    创建新图谱
                </button>
            </div>

            <div class="graph-grid">
                <div
                    class="graph-card"
                    v-for="graph in graphs"
                    :key="graph.id"
                    @click="viewGraph(graph.id)"
                >
                    <div class="graph-preview">
                        <div
                            class="graph-visualization"
                            :style="graph.previewStyle"
                        ></div>
                    </div>
                    <div class="graph-info">
                        <h4 class="graph-title">{{ graph.name }}</h4>
                        <div class="graph-meta">
                            <span class="meta-item">
                                <i class="icon-domain">📌</i>
                                {{ getDomainName(graph.domainId) }}
                            </span>
                            <span class="meta-item">
                                <i class="icon-type">🔖</i>
                                {{ getTypeText(graph.type) }}
                            </span>
                            <span class="meta-item">
                                <i class="icon-nodes">📊</i>
                                {{ graph.nodesCount }}个节点
                            </span>
                        </div>
                        <div class="graph-stats">
                            <span class="stat-item">
                                <i class="icon-rels">🔗</i>
                                {{ graph.relationshipsCount }}个关系
                            </span>
                            <span class="stat-item">
                                <i class="icon-date">📅</i>
                                {{ formatDate(graph.updateTime) }}
                            </span>
                            <span
                                class="stat-item status-badge"
                                :class="graph.status"
                            >
                                {{ getStatusText(graph.status) }}
                            </span>
                        </div>
                    </div>
                    <div class="graph-actions">
                        <button
                            class="btn btn-edit"
                            @click.stop="editGraph(graph.id)"
                        >
                            编辑
                        </button>
                        <button
                            class="btn btn-share"
                            @click.stop="shareGraph(graph.id)"
                        >
                            分享
                        </button>
                    </div>
                </div>
            </div>

            <div class="pagination-container" v-if="totalPages > 1">
                <button
                    class="pagination-btn"
                    :disabled="currentPage === 1"
                    @click="changePage(currentPage - 1)"
                >
                    上一页
                </button>
                <span class="pagination-info">
                    {{ currentPage }} / {{ totalPages }}
                </span>
                <button
                    class="pagination-btn"
                    :disabled="currentPage === totalPages"
                    @click="changePage(currentPage + 1)"
                >
                    下一页
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import request from "../../../utils/request";

const router = useRouter();

const isLoggedIn = ref(
    !!(window.localStorage && window.localStorage.getItem("token"))
);

const handleAuthFailure = async (e) => {
    console.error("请求失败", e);
    isLoggedIn.value = false;
    try {
        window.localStorage && window.localStorage.removeItem("token");
    } catch (err) {
        console.error("清理登录状态失败", err);
    }
    try {
        router.push("/login");
    } catch (err) {
        console.error("路由跳转失败", err);
    }
};

// 知识领域数据
const domains = ref([]);

// 筛选条件
const selectedDomain = ref("");
const selectedType = ref("");
const selectedStatus = ref("");
const searchKeyword = ref("");

// 分页数据
const currentPage = ref(1);
const pageSize = ref(6);
const totalPages = ref(1);
const total = ref(0);

// 图谱数据
const graphs = ref([]);

const normalizeGraph = (g) => {
    if (!g || typeof g !== "object") return {};
    const type = g.type || "concept";
    const domainId = g.domainId;
    const palette = {
        concept: "linear-gradient(135deg, #3498db10, #2980b915)",
        relationship: "linear-gradient(135deg, #9b59b610, #8e44ad15)",
        hierarchical: "linear-gradient(135deg, #1abc9c10, #16a08515)",
        integrated: "linear-gradient(135deg, #f1c40f10, #f39c1215)",
    };
    const background = palette[type] || palette.concept;
    return {
        ...g,
        domainId,
        previewStyle: {
            background,
        },
    };
};

const fetchDomains = async () => {
    const resp = await request.get("/graphs/domains/");
    const data = resp?.data || {};
    const list = data.results || data;
    domains.value = Array.isArray(list) ? list : [];
};

const fetchGraphs = async () => {
    const resp = await request.get("/graphs/", {
        params: {
            page: currentPage.value,
            pageSize: pageSize.value,
            domainId: selectedDomain.value || "",
            type: selectedType.value || "",
            status: selectedStatus.value || "",
            keyword: searchKeyword.value || "",
        },
    });

    const results = resp?.data?.results;
    total.value = resp?.data?.total || 0;
    graphs.value = (Array.isArray(results) ? results : []).map(normalizeGraph);
    totalPages.value = Math.max(1, Math.ceil((total.value || 0) / pageSize.value));
};

// 格式化日期
const formatDate = (dateString) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
    });
};

// 获取领域名称
const getDomainName = (domainId) => {
    const domain = domains.value.find((d) => d.id === domainId);
    return domain ? domain.name : "-";
};

// 获取图谱类型文本
const getTypeText = (type) => {
    switch (type) {
        case "concept":
            return "概念图谱";
        case "relationship":
            return "关系图谱";
        case "hierarchical":
            return "层级图谱";
        case "integrated":
            return "综合图谱";
        default:
            return "-";
    }
};

// 获取状态文本
const getStatusText = (status) => {
    switch (status) {
        case "draft":
            return "草稿";
        case "published":
            return "已发布";
        case "archived":
            return "已归档";
        default:
            return "-";
    }
};

// 防抖搜索
const debounceSearch = () => {
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
        searchGraphs();
    }, 500);
};

// 搜索图谱
const searchGraphs = async () => {
    currentPage.value = 1;
    try {
        await fetchGraphs();
    } catch (e) {
        await handleAuthFailure(e);
    }
};

const onFiltersChange = async () => {
    await searchGraphs();
};

// 改变页码
const changePage = async (page) => {
    if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
        try {
            await fetchGraphs();
        } catch (e) {
            await handleAuthFailure(e);
        }
    }
};

// 查看图谱
const viewGraph = (graphId) => {
    router.push(`/teacher/graphs/edit/${graphId}`);
};

// 编辑图谱
const editGraph = (graphId) => {
    router.push(`/teacher/graphs/edit/${graphId}`);
};

// 创建新图谱
const createNewGraph = () => {
    router.push(`/teacher/graphs/create`);
};

// 分享图谱
const shareGraph = (graphId) => {
    console.log("分享图谱:", graphId);
    alert("图谱分享功能已触发，图谱ID: " + graphId);
};

// 组件挂载时执行
onMounted(async () => {
    try {
        await fetchDomains();
        await fetchGraphs();
    } catch (e) {
        await handleAuthFailure(e);
    }
});
</script>

<style scoped>
/* 整体容器样式 */
.knowledge-graph-container {
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

/* 卡片头部样式 */
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

/* 筛选条件容器 */
.filters-container {
    margin-bottom: 30px;
}

.filter-content {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: center;
    transition: transform 0.3s ease;
}

.card:hover .filter-content {
    transform: translateX(3px);
}

.filter-group {
    display: flex;
    gap: 20px;
    flex: 1;
    flex-wrap: wrap;
}

.filter-item {
    display: flex;
    flex-direction: column;
    min-width: 150px;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .filter-item {
    transform: translateX(3px);
    opacity: 1;
}

.card:hover .filter-item:nth-child(2) {
    transition-delay: 0.05s;
}
.card:hover .filter-item:nth-child(3) {
    transition-delay: 0.1s;
}

.filter-item label {
    font-size: 14px;
    color: #555;
    margin-bottom: 8px;
    font-weight: 500;
}

/* 搜索容器 */
.search-container {
    display: flex;
    align-items: center;
    gap: 10px;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .search-container {
    transform: translateX(3px);
    opacity: 1;
}

/* 输入框样式统一 */
.input-field {
    padding: 12px 15px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.3s ease;
    min-width: 200px;
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

.btn-search,
.btn-view {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-search:hover,
.btn-view:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
    background: linear-gradient(135deg, #64b5f6, #2196f3);
}

.btn-add,
.btn-create {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: white;
}

.btn-add:hover,
.btn-create:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(46, 204, 113, 0.4);
    background: linear-gradient(135deg, #58d68d, #27ae60);
}

.btn-edit {
    background: linear-gradient(135deg, #f39c12, #d35400);
    color: white;
    margin-right: 8px;
}

.btn-edit:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(243, 156, 18, 0.4);
    background: linear-gradient(135deg, #f8c471, #e67e22);
}

.btn-share {
    background: linear-gradient(135deg, #9b59b6, #8e44ad);
    color: white;
}

.btn-share:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(155, 89, 182, 0.4);
    background: linear-gradient(135deg, #c39bd3, #9b59b6);
}

/* 图谱列表容器特有样式 */
.graph-list-container {
    margin-bottom: 25px;
}

/* 图谱网格布局 */
.graph-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 25px;
    margin-top: 20px;
}

/* 图谱卡片样式 */
.graph-card {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #f0f0f0;
    transition: all 0.3s ease;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}

.graph-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 20px rgba(59, 130, 246, 0.12);
    border-color: rgba(191, 219, 254, 0.5);
}

/* 图谱预览区 */
.graph-preview {
    height: 160px;
    padding: 15px;
    background-color: #fafafa;
    position: relative;
    overflow: hidden;
}

.graph-visualization {
    width: 100%;
    height: 100%;
    border-radius: 6px;
    position: relative;
    overflow: hidden;
}

/* 图谱信息区 */
.graph-info {
    padding: 15px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.graph-title {
    margin: 0 0 12px 0;
    font-size: 16px;
    color: #1e3a8a;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.graph-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 12px;
    margin-bottom: 12px;
    font-size: 12px;
    color: #666;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.graph-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
    font-size: 12px;
    color: #666;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

/* 状态标签 */
.status-badge {
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 500;
    text-transform: capitalize;
}

.status-badge.draft {
    background-color: #f1c40f15;
    color: #d35400;
}

.status-badge.published {
    background-color: #2ecc7115;
    color: #27ae60;
}

.status-badge.archived {
    background-color: #95a5a615;
    color: #7f8c8d;
}

/* 图谱操作区 */
.graph-actions {
    padding: 12px 15px;
    border-top: 1px solid #f0f0f0;
    display: flex;
    justify-content: flex-end;
}

/* 分页样式 */
.pagination-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e9ecef;
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .pagination-container {
    transform: translateX(3px);
    opacity: 1;
}

.pagination-btn {
    padding: 10px 16px;
    border: 1px solid #e0e0e0;
    background-color: white;
    color: #333;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
}

.pagination-btn:hover:not(:disabled) {
    background-color: #3498db;
    color: white;
    border-color: #3498db;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination-info {
    color: #666;
    font-size: 14px;
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

/* 响应式设计 */
@media (max-width: 1200px) {
    .filter-content {
        justify-content: center;
    }

    .filter-item {
        flex: 1;
        min-width: auto;
        max-width: 300px;
    }
}

@media (max-width: 768px) {
    .card {
        padding: 20px;
    }

    .filter-content {
        flex-direction: column;
        align-items: stretch;
    }

    .filter-item {
        min-width: auto;
        max-width: none;
    }

    .graph-grid {
        grid-template-columns: 1fr;
    }

    .btn {
        width: 100%;
        margin-bottom: 10px;
    }

    .graph-actions {
        flex-direction: column;
    }

    .btn-edit {
        margin-right: 0;
        margin-bottom: 8px;
    }
}
</style>
