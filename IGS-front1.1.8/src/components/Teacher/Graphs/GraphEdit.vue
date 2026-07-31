<template>
     <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>
    <a href="/teacher/graphs/graph" class="back-to-list">
        <span class="icon">←</span>
        <span>返回知识图谱列表</span>
    </a>

    <!-- 功能提示对话框 -->
    <div v-if="showFeatureTip" class="feature-tip-overlay">
        <div class="feature-tip-dialog">
            <h3>{{ currentFeatureTip.title }}</h3>
            <p v-html="currentFeatureTip.description"></p>
            <button class="btn btn-save" @click="showFeatureTip = false">
                知道了
            </button>
        </div>
    </div>

    <div class="graph-editor-container">
        <div class="page-header">
            <div class="header-content">
                <h2>
                    编辑知识图谱
                    <span class="graph-status" :class="graphData.status">
                        {{ getStatusText(graphData.status) }}
                    </span>
                </h2>
                <p>
                    {{ graphData.name }} -
                    {{ getDomainName(graphData.domainId) }} ·
                    {{ getTypeText(graphData.type) }}
                </p>
            </div>

            <div class="header-actions">
                <button
                    class="btn btn-preview"
                    @click="handleAction('preview')"
                >
                    预览
                </button>
                <button class="btn btn-save" @click="handleAction('save')">
                    保存
                </button>
                <button
                    class="btn btn-publish"
                    @click="handleAction('publish')"
                    v-if="graphData.status !== 'published'"
                >
                    发布
                </button>
            </div>
        </div>

        <div class="editor-layout">
            <!-- 左侧工具栏 -->
            <div class="card editor-toolbar">
                <h3>工具栏</h3>

                <div class="tool-group">
                    <h4>操作工具</h4>
                    <div class="tool-buttons">
                        <button
                            class="tool-btn"
                            :class="{ active: activeTool === 'select' }"
                            @click="handleToolClick('select')"
                            title="选择"
                        >
                            <i>🛠</i>
                            <span>选择</span>
                        </button>

                        <button
                            class="tool-btn"
                            :class="{ active: activeTool === 'pan' }"
                            @click="handleToolClick('pan')"
                            title="移动画布"
                        >
                            <i>✋</i>
                            <span>移动</span>
                        </button>

                        <button
                            class="tool-btn"
                            :class="{ active: activeTool === 'delete' }"
                            @click="handleToolClick('delete')"
                            title="删除元素"
                        >
                            <i>❌</i>
                            <span>删除</span>
                        </button>
                    </div>
                </div>

                <div class="tool-group">
                    <h4>添加元素</h4>
                    <div class="tool-buttons">
                        <button
                            class="tool-btn"
                            @click="handleAction('addNode')"
                            title="添加节点"
                        >
                            <i>🔴</i>
                            <span>节点</span>
                        </button>
                        <button
                            class="tool-btn"
                            @click="handleAction('addRelationship')"
                            title="添加关系"
                        >
                            <i>🔗</i>
                            <span>关系</span>
                        </button>
                        <button
                            class="tool-btn"
                            @click="handleAction('addSubgraph')"
                            title="添加子图"
                        >
                            <i>✨</i>
                            <span>子图</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- 中间绘图区域 -->
            <div class="graph-canvas-container">
                <div class="canvas-actions">
                    <button
                        class="btn btn-save"
                        @click="handleAction('zoomIn')"
                    >
                        + 放大
                    </button>
                    <button
                        class="btn btn-save"
                        @click="handleAction('zoomOut')"
                    >
                        - 缩小
                    </button>
                    <button
                        class="btn btn-publish"
                        @click="handleAction('resetView')"
                    >
                        重置视图
                    </button>
                    <span class="canvas-info"
                        >节点: {{ graphData.nodes.length }} | 关系:
                        {{ graphData.relationships.length }}</span
                    >
                </div>

                <div class="canvas-wrapper">
                    <div
                        class="graph-canvas"
                        ref="graphCanvas"
                        @click="handleCanvasClick"
                        @mousedown.stop="handleCanvasMouseDown"
                        @mouseleave="handleCanvasMouseLeave"
                    >
                        <!-- 连接线渲染 (使用SVG) -->
                        <svg class="graph-edges" ref="edgesContainer">
                            <defs>
                                <marker
                                    id="arrowhead"
                                    markerWidth="10"
                                    markerHeight="7"
                                    refX="9"
                                    refY="3.5"
                                    orient="auto"
                                >
                                    <polygon
                                        points="0 0, 10 3.5, 0 7"
                                        fill="#94a3b8"
                                    />
                                </marker>
                            </defs>

                            <g
                                v-for="edge in graphData.relationships"
                                :key="edge.id"
                            >
                                <line
                                    :x1="getLineStartPoint(edge).x"
                                    :y1="getLineStartPoint(edge).y"
                                    :x2="getLineEndPoint(edge).x"
                                    :y2="getLineEndPoint(edge).y"
                                    stroke="#94a3b8"
                                    :stroke-width="edgeThickness"
                                    :stroke-dasharray="
                                        edge.data.dashed ? '5,5' : 'none'
                                    "
                                    :marker-end="
                                        edge.data.hasArrow &&
                                        (edge.data.arrowDirection === 'end' ||
                                            edge.data.arrowDirection === 'both')
                                            ? 'url(#arrowhead)'
                                            : null
                                    "
                                    :marker-start="
                                        edge.data.hasArrow &&
                                        (edge.data.arrowDirection === 'start' ||
                                            edge.data.arrowDirection === 'both')
                                            ? 'url(#arrowhead)'
                                            : null
                                    "
                                    :class="{
                                        active:
                                            activeElement?.id === edge.id &&
                                            activeElement?.type ===
                                                'relationship',
                                    }"
                                    @click.stop="handleRelationshipClick(edge)"
                                />
                                <text
                                    :x="getLabelPosition(edge).x"
                                    :y="getLabelPosition(edge).y"
                                    fill="#64748b"
                                    font-size="12"
                                    text-anchor="middle"
                                    :class="{
                                        active:
                                            activeElement?.id === edge.id &&
                                            activeElement?.type ===
                                                'relationship',
                                    }"
                                    @click.stop="handleRelationshipClick(edge)"
                                >
                                    {{ edge.data.label }}
                                </text>
                            </g>
                        </svg>

                        <!-- 框选区域 -->
                        <div
                            v-if="boxSelect.isSelecting"
                            class="selection-box"
                            :style="{
                                left: `${Math.min(
                                    boxSelect.startX,
                                    boxSelect.endX
                                )}px`,
                                top: `${Math.min(
                                    boxSelect.startY,
                                    boxSelect.endY
                                )}px`,
                                width: `${Math.abs(
                                    boxSelect.endX - boxSelect.startX
                                )}px`,
                                height: `${Math.abs(
                                    boxSelect.endY - boxSelect.startY
                                )}px`,
                            }"
                        ></div>

                        <!-- 节点渲染 -->
                        <div
                            v-for="node in graphData.nodes"
                            :key="node.id"
                            :id="node.id"
                            class="graph-node"
                            :class="{
                                active:
                                    activeElement?.id === node.id &&
                                    activeElement?.type === 'node',
                                selected: boxSelect.selectedNodes.some(
                                    (n) => n.id === node.id
                                ),
                            }"
                            :style="{
                                left: `${node.position.x}px`,
                                top: `${node.position.y}px`,
                                backgroundColor: node.data.color,
                                width: `${getNodeSize(node)}px`,
                                height: `${getNodeSize(node)}px`,
                            }"
                            @click.stop="handleNodeClick(node)"
                            @mousedown.stop="startDragNode(node)"
                        >
                            <div class="node-content">
                                <div class="node-label">
                                    {{ node.data.label }}
                                </div>
                                <div
                                    class="node-category"
                                    v-if="node.data.category"
                                >
                                    {{ getCategoryText(node.data.category) }}
                                </div>
                            </div>
                        </div>

                        <!-- 空状态提示 -->
                        <div
                            class="canvas-placeholder"
                            v-if="graphData.nodes.length === 0"
                        >
                            <div class="placeholder-content">
                                <i>🖌️</i>
                                <p>在此区域绘制知识图谱</p>
                                <p class="hint">使用左侧工具栏添加节点和关系</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 右侧属性面板 -->
            <div class="card properties-panel">
                <h3>
                    {{
                        activeElement
                            ? activeElement.type === "node"
                                ? "节点属性"
                                : activeElement.type === "multiple"
                                ? `选中 ${activeElement.nodes.length} 个节点`
                                : "关系属性"
                            : "属性面板"
                    }}
                </h3>

                <div v-if="activeElement">
                    <!-- 节点属性面板 -->
                    <div
                        class="property-group"
                        v-if="activeElement.type === 'node'"
                    >
                        <label>节点名称 *</label>
                        <input
                            type="text"
                            v-model="activeElement.data.label"
                            class="input-field"
                            @input="updateElement"
                        />

                        <label>节点类型</label>
                        <select
                            v-model="activeElement.data.category"
                            class="input-field"
                            @change="updateElement"
                        >
                            <option value="concept">概念</option>
                            <option value="entity">实体</option>
                            <option value="instance">实例</option>
                            <option value="attribute">属性</option>
                        </select>

                        <label>节点大小</label>
                        <input
                            type="range"
                            min="60"
                            max="200"
                            v-model="activeElement.data.size"
                            @input="updateElement"
                        />
                        <span class="size-value"
                            >{{ activeElement.data.size }}px</span
                        >

                        <label>颜色</label>
                        <div class="color-selector">
                            <input
                                type="color"
                                v-model="activeElement.data.color"
                                @input="updateElement"
                            />
                        </div>

                        <label>描述</label>
                        <textarea
                            v-model="activeElement.data.description"
                            class="input-field textarea-field"
                            rows="3"
                            @input="updateElement"
                        ></textarea>
                    </div>

                    <!-- 多节点选中面板 -->
                    <div v-if="activeElement.type === 'multiple'">
                        <p>已选中 {{ activeElement.nodes.length }} 个节点</p>
                        <div class="property-actions">
                            <button
                                class="btn btn-danger"
                                @click="deleteActiveElement"
                            >
                                批量删除选中节点
                            </button>
                        </div>
                    </div>

                    <!-- 关系属性面板 -->
                    <div
                        class="property-group"
                        v-if="activeElement.type === 'relationship'"
                    >
                        <label>关系名称 *</label>
                        <input
                            type="text"
                            v-model="activeElement.data.label"
                            class="input-field"
                            @input="updateElement"
                        />

                        <label>关系类型</label>
                        <select
                            v-model="activeElement.data.type"
                            class="input-field"
                            @change="updateElement"
                        >
                            <option value="association">关联</option>
                            <option value="hierarchy">层级</option>
                            <option value="composition">组成</option>
                            <option value="attribute">属性</option>
                        </select>

                        <label>是否虚线</label>
                        <input
                            type="checkbox"
                            v-model="activeElement.data.dashed"
                            @change="updateElement"
                        />

                        <label>是否带箭头</label>
                        <input
                            type="checkbox"
                            v-model="activeElement.data.hasArrow"
                            @change="updateElement"
                        />

                        <label v-if="activeElement.data.hasArrow"
                            >箭头方向</label
                        >
                        <select
                            v-if="activeElement.data.hasArrow"
                            v-model="activeElement.data.arrowDirection"
                            class="input-field"
                            @change="updateElement"
                        >
                            <option value="end">目标节点 (默认)</option>
                            <option value="start">源节点</option>
                            <option value="both">双向</option>
                        </select>

                        <label>源节点</label>
                        <input
                            type="text"
                            :value="
                                getSourceNodeLabel(activeElement.data.source)
                            "
                            class="input-field"
                            disabled
                        />

                        <label>目标节点</label>
                        <input
                            type="text"
                            :value="
                                getTargetNodeLabel(activeElement.data.target)
                            "
                            class="input-field"
                            disabled
                        />

                        <label>关系描述</label>
                        <textarea
                            v-model="activeElement.data.description"
                            class="input-field textarea-field"
                            rows="3"
                            @input="updateElement"
                        ></textarea>
                    </div>

                    <div
                        class="property-actions"
                        v-if="activeElement.type !== 'multiple'"
                    >
                        <button
                            class="btn btn-danger"
                            @click="deleteActiveElement"
                        >
                            删除此{{
                                activeElement.type === "node" ? "节点" : "关系"
                            }}
                        </button>
                    </div>
                </div>

                <div v-else class="panel-placeholder">
                    <p>选择一个节点或关系来编辑其属性</p>
                </div>
            </div>
        </div>

        <!-- 历史记录和导入导出 -->
        <div class="card extra-tools">
            <div class="tools-section">
                <h3>历史记录</h3>
                <div class="history-actions">
                    <button
                        class="btn btn-sm"
                        :disabled="!canUndo"
                        @click="handleAction('undo')"
                    >
                        ← 撤销
                    </button>
                    <button
                        class="btn btn-sm"
                        :disabled="!canRedo"
                        @click="handleAction('redo')"
                    >
                        重做 →
                    </button>
                </div>
            </div>

            <div class="tools-section">
                <h3>导入导出</h3>
                <div class="import-export-actions">
                    <button class="btn btn-sm" @click="handleAction('import')">
                        导入
                    </button>
                    <button class="btn btn-sm" @click="handleAction('export')">
                        导出
                    </button>
                    <button
                        class="btn btn-sm"
                        @click="handleAction('exportImage')"
                    >
                        导出为图片
                    </button>
                </div>
            </div>

            <div class="tools-section">
                <h3>批量操作</h3>
                <div class="batch-actions">
                    <button class="btn btn-sm" @click="handleAction('clear')">
                        清空图谱
                    </button>
                    <button
                        class="btn btn-sm"
                        @click="handleAction('autoArrange')"
                    >
                        自动排列
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, reactive, nextTick } from "vue";
import { useRouter, useRoute } from "vue-router";
import request from "../../../utils/request";

const router = useRouter();
const route = useRoute();

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

// 图谱数据
const graphData = reactive({
    id: route.params.id || "new",
    name: "未命名知识图谱",
    domainId: 1,
    type: "concept",
    status: "draft",
    description: "",
    nodes: [],
    relationships: [],
});

// 知识领域数据
const domains = ref([]);

const fetchDomains = async () => {
    const resp = await request.get("/graphs/domains/");
    const list = resp?.data;
    domains.value = Array.isArray(list) ? list : [];
};

const fetchGraphDetail = async () => {
    const resp = await request.get(`/graphs/${graphData.id}/`);
    const data = resp?.data || {};
    graphData.name = data.name || graphData.name;
    graphData.domainId = data.domainId || graphData.domainId;
    graphData.type = data.type || graphData.type;
    graphData.status = data.status || graphData.status;
    graphData.description = data.description || "";

    graphData.nodes = Array.isArray(data.nodes) ? data.nodes : [];
    graphData.relationships = Array.isArray(data.relationships)
        ? data.relationships
        : [];
};

// 编辑器状态
const activeTool = ref("select");
const activeElement = ref(null);
const isAddingRelationship = ref(false);
const relationshipSource = ref(null);
const defaultNodeSize = ref(80);
const edgeThickness = ref(2);
const canUndo = ref(false);
const canRedo = ref(false);
const graphCanvas = ref(null);
const edgesContainer = ref(null);
const dragState = ref({
    isDragging: false,
    currentNode: null,
    offset: { x: 0, y: 0 },
    isMultiSelect: false,
    initialPositions: null,
});
const viewState = ref({
    scale: 1,
    offset: { x: 0, y: 0 },
});

// 框选功能相关状态
const boxSelect = ref({
    isSelecting: false,
    startX: 0,
    startY: 0,
    endX: 0,
    endY: 0,
    selectedNodes: [],
});

// 画布拖动状态
const panState = ref({
    isPanning: false,
    startX: 0,
    startY: 0,
    initialOffset: { x: 0, y: 0 },
});

// 功能提示相关状态
const showFeatureTip = ref(false);
const currentFeatureTip = ref({ title: "", description: "" });
const usedFeatures = ref(new Set()); // 记录已使用过的功能

// 功能提示信息配置
const featureTips = {
    select: {
        title: "选择工具",
        description:
            "用于选择节点、关系或进行框选操作。<span class='highlight'>按住Shift键可进行多选。</span>",
    },
    pan: {
        title: "移动画布",
        description: "用于拖动整个画布，方便查看图谱的不同部分。",
    },
    delete: {
        title: "删除工具",
        description: "选择此工具后，点击节点或关系可将其删除。",
    },
    addNode: {
        title: "添加节点",
        description: "在画布中心添加一个新节点，可在右侧属性面板修改其属性。",
    },
    addRelationship: {
        title: "添加关系",
        description: "先点击源节点，再点击目标节点，即可创建两者之间的关系。",
    },
    addSubgraph: {
        title: "添加子图",
        description: "一次性添加包含三个节点和两个关系的子图结构。",
    },
    adjustNodeSize: {
        title: "调整节点大小",
        description: "滑动滑块可调整所有节点的默认大小。",
    },
    adjustEdgeThickness: {
        title: "调整边的粗细",
        description: "滑动滑块可调整所有关系连接线的粗细。",
    },
    zoomIn: {
        title: "放大视图",
        description: "放大画布视图，便于查看细节。",
    },
    zoomOut: {
        title: "缩小视图",
        description: "缩小画布视图，便于查看整体。",
    },
    resetView: {
        title: "重置视图",
        description: "将视图恢复到默认的缩放和位置。",
    },
    undo: {
        title: "撤销操作",
        description: "撤销上一步操作。",
    },
    redo: {
        title: "重做操作",
        description: "重做上一步被撤销的操作。",
    },
    import: {
        title: "导入图谱",
        description: "从本地导入JSON格式的图谱数据。",
    },
    export: {
        title: "导出图谱",
        description: "将当前图谱导出为JSON格式文件。",
    },
    exportImage: {
        title: "导出为图片",
        description: "将当前图谱导出为图片格式。",
    },
    clear: {
        title: "清空图谱",
        description: "删除当前图谱中的所有节点和关系。此操作不可恢复。",
    },
    autoArrange: {
        title: "自动排列",
        description: "自动调整所有节点的位置，使图谱布局更合理。",
    },
    save: {
        title: "保存图谱",
        description: "保存当前图谱的所有修改。",
    },
    publish: {
        title: "发布图谱",
        description: "将图谱发布，发布后所有人可见。",
    },
    preview: {
        title: "预览图谱",
        description: "查看图谱的最终展示效果。",
    },
};

// 初始化图谱
onMounted(async () => {
    if (!isLoggedIn.value) {
        try {
            router.push("/login");
        } catch (err) {
            console.error("路由跳转失败", err);
        }
        return;
    }

    if (graphData.id === "new") {
        router.push("/teacher/graphs/create");
        return;
    }

    try {
        await fetchDomains();
        await fetchGraphDetail();
    } catch (e) {
        await handleAuthFailure(e);
        return;
    }

    nextTick(() => {
        adjustEdgesContainerSize();
    });
});

// 初始化示例数据
const initSampleData = () => {
    if (graphData.id === "new" && graphData.nodes.length === 0) {
        graphData.nodes = [
            {
                id: "n1",
                data: {
                    label: "根节点",
                    category: "concept",
                    color: "#3b82f6",
                    description: "这是一个根节点示例",
                    size: defaultNodeSize.value,
                },
                position: { x: 300, y: 150 },
            },
            {
                id: "n2",
                data: {
                    label: "子节点",
                    category: "concept",
                    color: "#10b981",
                    description: "这是一个子节点示例",
                    size: defaultNodeSize.value,
                },
                position: { x: 500, y: 150 },
            },
            {
                id: "n3",
                data: {
                    label: "节点3",
                    category: "entity",
                    color: "#f59e0b",
                    description: "",
                    size: defaultNodeSize.value,
                },
                position: { x: 400, y: 300 },
            },
        ];

        graphData.relationships.push(
            {
                id: "e1",
                data: {
                    source: "n1",
                    target: "n2",
                    label: "包含",
                    type: "hierarchy",
                    dashed: false,
                    description: "",
                    hasArrow: true,
                    arrowDirection: "end",
                },
            },
            {
                id: "e2",
                data: {
                    source: "n1",
                    target: "n3",
                    label: "关联",
                    type: "association",
                    dashed: false,
                    description: "",
                    hasArrow: true,
                    arrowDirection: "end",
                },
            }
        );
    }
};

// 处理工具点击 - 带首次提示
const handleToolClick = (tool) => {
    // 检查是否是首次使用该功能
    if (!usedFeatures.value.has(tool)) {
        usedFeatures.value.add(tool);
        currentFeatureTip.value = featureTips[tool];
        showFeatureTip.value = true;
    }

    setActiveTool(tool);
};

// 处理功能操作 - 带首次提示
const handleAction = (action) => {
    // 检查是否是首次使用该功能
    if (!usedFeatures.value.has(action)) {
        usedFeatures.value.add(action);
        currentFeatureTip.value = featureTips[action];
        showFeatureTip.value = true;
    }

    // 执行对应的操作
    switch (action) {
        case "addNode":
            addNode();
            break;
        case "addRelationship":
            startAddRelationship();
            break;
        case "addSubgraph":
            addSubgraph();
            break;
        case "adjustNodeSize":
            adjustDefaultNodeSize();
            break;
        case "adjustEdgeThickness":
            adjustEdgeThickness();
            break;
        case "zoomIn":
            zoomIn();
            break;
        case "zoomOut":
            zoomOut();
            break;
        case "resetView":
            resetView();
            break;
        case "undo":
            undo();
            break;
        case "redo":
            redo();
            break;
        case "import":
            importGraph();
            break;
        case "export":
            exportGraph();
            break;
        case "exportImage":
            exportAsImage();
            break;
        case "clear":
            clearGraph();
            break;
        case "autoArrange":
            autoArrange();
            break;
        case "save":
            saveGraph();
            break;
        case "publish":
            publishGraph();
            break;
        case "preview":
            previewGraph();
            break;
    }
};

// 获取节点大小
const getNodeSize = (node) => {
    return node.data.size || defaultNodeSize.value;
};

// 获取节点类型文本
const getCategoryText = (category) => {
    switch (category) {
        case "concept":
            return "概念";
        case "entity":
            return "实体";
        case "instance":
            return "实例";
        case "attribute":
            return "属性";
        default:
            return "";
    }
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

// 设置活动工具
const setActiveTool = (tool) => {
    activeTool.value = tool;
    isAddingRelationship.value = false;
    relationshipSource.value = null;
    panState.value.isPanning = false;

    if (tool !== "select") {
        boxSelect.value.selectedNodes = [];
        activeElement.value = null;
    }

    // 更新鼠标样式
    if (graphCanvas.value) {
        graphCanvas.value.style.cursor = tool === "pan" ? "grab" : "default";
    }
};

// 添加节点
const addNode = () => {
    if (!graphCanvas.value) return;

    const canvasElement = graphCanvas.value;
    const canvasRect = canvasElement.getBoundingClientRect(); // 画布在视口中的位置和大小
    const wrapper = canvasElement.parentElement; // 滚动容器（假设是直接父元素）

    // 获取容器的滚动偏移（用户当前滚动到的位置）
    const scrollLeft = wrapper.scrollLeft || 0;
    const scrollTop = wrapper.scrollTop || 0;

    // 获取当前视图变换状态（缩放和位移）
    const scale = viewState.value.scale;
    const offsetX = viewState.value.offset.x;
    const offsetY = viewState.value.offset.y;

    // 计算当前视野的中心（基于用户可见区域，而非画布物理中心）
    // 1. 先计算可见区域在视口中的中心
    const visibleCenterX = canvasRect.width / 2;
    const visibleCenterY = canvasRect.height / 2;

    // 2. 转换为画布内部的坐标（考虑滚动和视图变换）
    const canvasCenterX = (visibleCenterX - offsetX) / scale + scrollLeft;
    const canvasCenterY = (visibleCenterY - offsetY) / scale + scrollTop;

    // 计算节点最终位置（减去节点一半大小，使中心对齐）
    const nodeSize = defaultNodeSize.value;
    const nodeX = canvasCenterX - nodeSize / 2;
    const nodeY = canvasCenterY - nodeSize / 2;

    // 生成节点ID和数据
    const nodeId = `n${Date.now().toString().slice(-5)}`;
    const newNode = {
        id: nodeId,
        data: {
            label: "新节点",
            category: "concept",
            color: getRandomColor(),
            description: "",
            size: nodeSize,
        },
        position: { x: nodeX, y: nodeY },
    };

    graphData.nodes.push(newNode);

    // 更新选中状态
    activeElement.value = {
        id: nodeId,
        type: "node",
        data: newNode.data,
        position: newNode.position,
    };
    boxSelect.value.selectedNodes = [];

    // 确保节点在视野中并更新布局
    nextTick(() => {
        adjustEdgesContainerSize();
        ensureNodeVisible(newNode, wrapper);
    });

    recordHistory();
};

// 确保节点在当前可见区域内
const ensureNodeVisible = (node, wrapper) => {
    const nodeSize = getNodeSize(node);
    const nodeLeft = node.position.x;
    const nodeTop = node.position.y;
    const nodeRight = nodeLeft + nodeSize;
    const nodeBottom = nodeTop + nodeSize;

    // 容器可见区域
    const wrapperRect = wrapper.getBoundingClientRect();
    const visibleLeft = wrapper.scrollLeft;
    const visibleTop = wrapper.scrollTop;
    const visibleRight = visibleLeft + wrapperRect.width;
    const visibleBottom = visibleTop + wrapperRect.height;

    // 如果节点超出可见区域，滚动到节点位置
    if (nodeLeft < visibleLeft) {
        wrapper.scrollLeft = nodeLeft - 20; // 留出20px边距
    } else if (nodeRight > visibleRight) {
        wrapper.scrollLeft = nodeRight - wrapperRect.width + 20;
    }

    if (nodeTop < visibleTop) {
        wrapper.scrollTop = nodeTop - 20;
    } else if (nodeBottom > visibleBottom) {
        wrapper.scrollTop = nodeBottom - wrapperRect.height + 20;
    }
};

// 滚动到节点位置
const scrollToNode = (node) => {
    if (!graphCanvas.value) return;

    const canvasRect = graphCanvas.value.getBoundingClientRect();
    const nodeSize = getNodeSize(node);
    const nodeCenterX = node.position.x + nodeSize / 2;
    const nodeCenterY = node.position.y + nodeSize / 2;

    if (
        nodeCenterX < 0 ||
        nodeCenterX > canvasRect.width ||
        nodeCenterY < 0 ||
        nodeCenterY > canvasRect.height
    ) {
        viewState.value.offset = {
            x: canvasRect.width / 2 - nodeCenterX,
            y: canvasRect.height / 2 - nodeCenterY,
        };
        applyViewTransform();
    }
};

// 获取随机颜色
const getRandomColor = () => {
    const colors = [
        "#3b82f6",
        "#10b981",
        "#f59e0b",
        "#ef4444",
        "#8b5cf6",
        "#ec4899",
        "#6366f1",
        "#14b8a6",
    ];
    return colors[Math.floor(Math.random() * colors.length)];
};

// 开始添加关系
const startAddRelationship = () => {
    if (graphData.nodes.length < 2) {
        alert("至少需要两个节点才能创建关系");
        return;
    }

    activeTool.value = "relationship";
    isAddingRelationship.value = true;
    relationshipSource.value = null;
    activeElement.value = null;
    boxSelect.value.selectedNodes = [];
};

// 添加子图
const addSubgraph = () => {
    const baseId = Date.now().toString().slice(-5);
    const centerX = 300;
    const centerY = 300;

    const subgraphNodes = [
        {
            id: `n${baseId}a`,
            data: {
                label: "子图节点1",
                category: "concept",
                color: "#f59e0b",
                size: defaultNodeSize.value,
            },
            position: { x: centerX - 150, y: centerY },
        },
        {
            id: `n${baseId}b`,
            data: {
                label: "子图节点2",
                category: "concept",
                color: "#f59e0b",
                size: defaultNodeSize.value,
            },
            position: { x: centerX, y: centerY },
        },
        {
            id: `n${baseId}c`,
            data: {
                label: "子图节点3",
                category: "concept",
                color: "#f59e0b",
                size: defaultNodeSize.value,
            },
            position: { x: centerX + 150, y: centerY },
        },
    ];

    graphData.nodes.push(...subgraphNodes);

    graphData.relationships.push(
        {
            id: `e${baseId}1`,
            data: {
                source: `n${baseId}a`,
                target: `n${baseId}b`,
                label: "关联",
                type: "association",
                dashed: false,
                hasArrow: true,
                arrowDirection: "end",
            },
        },
        {
            id: `e${baseId}2`,
            data: {
                source: `n${baseId}b`,
                target: `n${baseId}c`,
                label: "关联",
                type: "association",
                dashed: false,
                hasArrow: true,
                arrowDirection: "end",
            },
        }
    );

    nextTick(() => adjustEdgesContainerSize());
    recordHistory();
};

// 导入图谱功能实现
const importGraph = () => {
    // 创建隐藏的文件选择input
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".json"; // 只接受JSON文件

    // 监听文件选择事件
    fileInput.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // 验证文件类型
        if (file.type !== "application/json" && !file.name.endsWith(".json")) {
            alert("请选择JSON格式的文件");
            return;
        }

        try {
            // 读取文件内容
            const content = await readFileContent(file);
            const graphData = JSON.parse(content);

            // 验证图谱数据格式
            if (validateGraphData(graphData)) {
                // 确认覆盖当前图谱
                if (confirm("导入将覆盖当前图谱，是否继续？")) {
                    loadImportedGraph(graphData);
                    alert("图谱导入成功！");
                    recordHistory();
                }
            }
        } catch (error) {
            console.error("导入图谱失败:", error);
            alert(`导入失败: ${error.message}`);
        }
    });

    // 触发文件选择对话框
    fileInput.click();
};

// 读取文件内容
const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = () => reject(new Error("无法读取文件内容"));
        reader.readAsText(file);
    });
};

// 验证导入的图谱数据格式
const validateGraphData = (data) => {
    // 基本结构验证
    if (!data || typeof data !== "object") {
        throw new Error("无效的图谱数据格式");
    }

    // 必要字段验证
    if (typeof data.name !== "string") {
        throw new Error("图谱名称格式不正确");
    }

    // 节点数据验证
    if (!Array.isArray(data.nodes)) {
        throw new Error("节点数据必须是数组");
    }

    // 验证每个节点的格式
    data.nodes.forEach((node, index) => {
        if (!node || typeof node !== "object") {
            throw new Error(`第${index + 1}个节点格式无效`);
        }
        if (typeof node.id !== "string" || !node.id) {
            throw new Error(`第${index + 1}个节点缺少有效的ID`);
        }
        if (
            !node.data ||
            typeof node.data !== "object" ||
            typeof node.data.label !== "string"
        ) {
            throw new Error(`第${index + 1}个节点缺少有效的标签`);
        }
        if (
            !node.position ||
            typeof node.position.x !== "number" ||
            typeof node.position.y !== "number"
        ) {
            throw new Error(`第${index + 1}个节点位置信息无效`);
        }
    });

    // 关系数据验证
    if (!Array.isArray(data.relationships)) {
        throw new Error("关系数据必须是数组");
    }

    // 验证每个关系的格式
    data.relationships.forEach((rel, index) => {
        if (!rel || typeof rel !== "object") {
            throw new Error(`第${index + 1}个关系格式无效`);
        }
        if (typeof rel.id !== "string" || !rel.id) {
            throw new Error(`第${index + 1}个关系缺少有效的ID`);
        }
        if (!rel.data || typeof rel.data !== "object") {
            throw new Error(`第${index + 1}个关系数据无效`);
        }

        // 验证关系的源节点和目标节点是否存在
        const sourceExists = data.nodes.some(
            (node) => node.id === rel.data.source
        );
        const targetExists = data.nodes.some(
            (node) => node.id === rel.data.target
        );

        if (!sourceExists) {
            throw new Error(`第${index + 1}个关系的源节点不存在`);
        }
        if (!targetExists) {
            throw new Error(`第${index + 1}个关系的目标节点不存在`);
        }
        if (rel.data.source === rel.data.target) {
            throw new Error(`第${index + 1}个关系的源节点和目标节点不能相同`);
        }
    });

    return true;
};

// 加载导入的图谱数据
const loadImportedGraph = (importedData) => {
    // 清空当前图谱
    graphData.nodes = [];
    graphData.relationships = [];

    // 复制基本信息
    graphData.name = importedData.name || graphData.name;
    graphData.domainId = importedData.domainId || graphData.domainId;
    graphData.type = importedData.type || graphData.type;
    graphData.description = importedData.description || graphData.description;

    // 导入节点数据（深拷贝避免引用问题）
    importedData.nodes.forEach((node) => {
        graphData.nodes.push({
            id: node.id,
            data: { ...node.data },
            position: { ...node.position },
        });
    });

    // 导入关系数据
    importedData.relationships.forEach((rel) => {
        graphData.relationships.push({
            id: rel.id,
            data: { ...rel.data },
        });
    });

    // 重置选择状态
    activeElement.value = null;
    boxSelect.value.selectedNodes = [];

    // 调整视图以显示所有节点
    nextTick(() => {
        adjustEdgesContainerSize();
        if (graphData.nodes.length > 0) {
            fitViewToAllNodes(); // 适配视图显示所有节点
        }
    });
};

// 处理节点点击
// 处理节点点击（考虑画布缩放的Shift键多选）
const handleNodeClick = (node) => {
    if (isAddingRelationship.value) {
        // 保持原有关联添加逻辑
        if (!relationshipSource.value) {
            relationshipSource.value = node.id;
            activeElement.value = {
                id: node.id,
                type: "node",
                data: node.data,
            };
        } else if (relationshipSource.value !== node.id) {
            const edgeId = `e${Date.now().toString().slice(-5)}`;
            graphData.relationships.push({
                id: edgeId,
                data: {
                    source: relationshipSource.value,
                    target: node.id,
                    label: "关系",
                    type: "association",
                    dashed: false,
                    description: "",
                    hasArrow: true,
                    arrowDirection: "end",
                },
            });

            isAddingRelationship.value = false;
            activeElement.value = {
                id: edgeId,
                type: "relationship",
                data: graphData.relationships.find((e) => e.id === edgeId).data,
            };

            boxSelect.value.selectedNodes = [];
            nextTick(() => adjustEdgesContainerSize());
            recordHistory();
        } else {
            alert("不能创建节点到自身的关系");
        }
        return;
    }

    if (activeTool.value === "delete") {
        deleteNode(node.id);
        return;
    }

    // 支持Shift键多选（考虑画布缩放）
    if (event.shiftKey) {
        // 1. 计算当前节点在视口坐标系中的位置和大小（考虑缩放）
        const scale = viewState.value.scale;
        const nodeSize = getNodeSize(node) * scale;
        const nodeViewX = (node.position.x + viewState.value.offset.x) * scale;
        const nodeViewY = (node.position.y + viewState.value.offset.y) * scale;

        // 2. 获取鼠标在视口坐标系中的位置
        const canvasRect = graphCanvas.value.getBoundingClientRect();
        const mouseViewX = event.clientX - canvasRect.left;
        const mouseViewY = event.clientY - canvasRect.top;

        // 3. 验证点击是否在节点可视范围内（处理缩放导致的坐标偏差）
        const isClickInNode =
            mouseViewX >= nodeViewX &&
            mouseViewX <= nodeViewX + nodeSize &&
            mouseViewY >= nodeViewY &&
            mouseViewY <= nodeViewY + nodeSize;

        if (isClickInNode) {
            const index = boxSelect.value.selectedNodes.findIndex(
                (n) => n.id === node.id
            );
            if (index > -1) {
                boxSelect.value.selectedNodes.splice(index, 1);
            } else {
                boxSelect.value.selectedNodes.push(node);
            }
            activeElement.value = boxSelect.value.selectedNodes.length
                ? { type: "multiple", nodes: boxSelect.value.selectedNodes }
                : null;
        }
    } else {
        boxSelect.value.selectedNodes = [node];
        activeElement.value = {
            id: node.id,
            type: "node",
            data: node.data,
            position: node.position,
        };
    }
};

// 处理关系点击
const handleRelationshipClick = (edge) => {
    boxSelect.value.selectedNodes = [];

    if (activeTool.value === "delete") {
        deleteRelationship(edge.id);
        return;
    }

    activeElement.value = {
        id: edge.id,
        type: "relationship",
        data: edge.data,
    };
};

// 处理画布点击
const handleCanvasClick = () => {
    if (activeTool.value === "select" && !event.shiftKey) {
        activeElement.value = null;
        boxSelect.value.selectedNodes = [];
    }
};

// 处理画布鼠标按下 - 支持空白处框选和画布拖动
const handleCanvasMouseDown = (event) => {
    // 移动工具激活时，启动画布拖动
    if (activeTool.value === "pan") {
        const canvasRect = graphCanvas.value.getBoundingClientRect();
        panState.value = {
            isPanning: true,
            startX: event.clientX,
            startY: event.clientY,
            initialOffset: { ...viewState.value.offset },
        };

        // 更改鼠标样式
        if (graphCanvas.value) {
            graphCanvas.value.style.cursor = "grabbing";
        }

        document.addEventListener("mousemove", panCanvas);
        document.addEventListener("mouseup", stopPanning);
        return;
    }

    // 只有在选择工具且按下Shift键且点击空白处时才启动框选
    if (
        activeTool.value === "select" &&
        event.shiftKey &&
        event.target === graphCanvas.value
    ) {
        // 获取画布的客户端矩形（视口坐标）
        const canvasRect = graphCanvas.value.getBoundingClientRect();

        // 将鼠标点击位置从视口坐标转换为画布原始坐标（考虑缩放）
        // 公式：画布坐标 = (视口坐标 - 画布偏移) / 缩放比例
        const startX =
            (event.clientX - canvasRect.left) /
            viewState.value.scale -
            viewState.value.offset.x;
        const startY =
            (event.clientY - canvasRect.top) /
            viewState.value.scale -
            viewState.value.offset.y;

        boxSelect.value = {
            isSelecting: true,
            // 存储原始画布坐标（不受缩放影响）
            startX: startX,
            startY: startY,
            endX: startX,
            endY: startY,
            selectedNodes: [...boxSelect.value.selectedNodes],
        };

        // 更新框选函数（已适配缩放）
        const updateSelectionBoxScaled = (e) => {
            if (!boxSelect.value.isSelecting) return;

            // 实时转换鼠标位置到画布原始坐标
            const currentX =
                (e.clientX - canvasRect.left) /
                viewState.value.scale -
                viewState.value.offset.x;
            const currentY =
                (e.clientY - canvasRect.top) /
                viewState.value.scale -
                viewState.value.offset.y;

            boxSelect.value.endX = currentX;
            boxSelect.value.endY = currentY;

            calculateSelectedNodes();
        };

        // 结束框选函数
        const endSelectionScaled = () => {
            if (boxSelect.value.isSelecting) {
                boxSelect.value.isSelecting = false;

                if (boxSelect.value.selectedNodes.length > 0) {
                    activeElement.value = {
                        type: "multiple",
                        nodes: boxSelect.value.selectedNodes,
                    };
                }

                document.removeEventListener(
                    "mousemove",
                    updateSelectionBoxScaled
                );
                document.removeEventListener("mouseup", endSelectionScaled);
            }
        };

        document.addEventListener("mousemove", updateSelectionBoxScaled);
        document.addEventListener("mouseup", endSelectionScaled);
    }
};

// 处理画布鼠标离开事件
const handleCanvasMouseLeave = () => {
    if (panState.value.isPanning) {
        stopPanning();
    }
    if (boxSelect.value.isSelecting) {
        endSelection();
    }
    if (dragState.value.isDragging) {
        stopDragNode();
    }
};

// 拖动画布
const panCanvas = (event) => {
    if (!panState.value.isPanning) return;

    const deltaX = event.clientX - panState.value.startX;
    const deltaY = event.clientY - panState.value.startY;

    viewState.value.offset = {
        x: panState.value.initialOffset.x + deltaX,
        y: panState.value.initialOffset.y + deltaY,
    };

    applyViewTransform();
};

// 停止拖动画布
const stopPanning = () => {
    if (panState.value.isPanning) {
        panState.value.isPanning = false;

        // 恢复鼠标样式
        if (graphCanvas.value) {
            graphCanvas.value.style.cursor = "grab";
        }

        document.removeEventListener("mousemove", panCanvas);
        document.removeEventListener("mouseup", stopPanning);
        recordHistory();
    }
};

// 获取节点位置
const getNodePosition = (nodeId) => {
    const node = graphData.nodes.find((n) => n.id === nodeId);
    if (!node) return { x: 0, y: 0 };
    const nodeSize = getNodeSize(node);
    return {
        x: node.position.x + nodeSize / 2,
        y: node.position.y + nodeSize / 2,
    };
};

// 计算线段起点
const getLineStartPoint = (edge) => {
    const sourcePos = getNodePosition(edge.data.source);
    const targetPos = getNodePosition(edge.data.target);
    const sourceNode = graphData.nodes.find((n) => n.id === edge.data.source);
    const radius = getNodeSize(sourceNode) / 2;

    const dx = targetPos.x - sourcePos.x;
    const dy = targetPos.y - sourcePos.y;
    const distance = Math.sqrt(dx * dx + dy * dy) || 1; // 防止除以零

    return {
        x: sourcePos.x + (dx / distance) * radius,
        y: sourcePos.y + (dy / distance) * radius,
    };
};

// 计算线段终点
const getLineEndPoint = (edge) => {
    const sourcePos = getNodePosition(edge.data.source);
    const targetPos = getNodePosition(edge.data.target);
    const targetNode = graphData.nodes.find((n) => n.id === edge.data.target);
    const radius = getNodeSize(targetNode) / 2;

    const dx = sourcePos.x - targetPos.x;
    const dy = sourcePos.y - targetPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy) || 1; // 防止除以零

    return {
        x: targetPos.x + (dx / distance) * radius,
        y: targetPos.y + (dy / distance) * radius,
    };
};

// 计算关系标签位置
const getLabelPosition = (edge) => {
    const startPos = getLineStartPoint(edge);
    const endPos = getLineEndPoint(edge);

    return {
        x: (startPos.x + endPos.x) / 2,
        y: (startPos.y + endPos.y) / 2 - 5,
    };
};

// 获取源节点标签
const getSourceNodeLabel = (nodeId) => {
    const node = graphData.nodes.find((n) => n.id === nodeId);
    return node ? node.data.label : "-";
};

// 获取目标节点标签
const getTargetNodeLabel = (nodeId) => {
    const node = graphData.nodes.find((n) => n.id === nodeId);
    return node ? node.data.label : "-";
};

// 开始拖动节点
const startDragNode = (node) => {
    if (activeTool.value !== "select") return;

    // 如果按下Shift键，启动框选而不是拖动
    if (event.shiftKey) {
        const canvasRect = graphCanvas.value.getBoundingClientRect();
        boxSelect.value = {
            isSelecting: true,
            startX: event.clientX - canvasRect.left,
            startY: event.clientY - canvasRect.top,
            endX: event.clientX - canvasRect.left,
            endY: event.clientY - canvasRect.top,
            selectedNodes: [...boxSelect.value.selectedNodes],
        };

        document.addEventListener("mousemove", updateSelectionBox);
        document.addEventListener("mouseup", endSelection);
        return;
    }

    // 判断是否是多节点拖动
    const isMulti =
        boxSelect.value.selectedNodes.length > 0 &&
        boxSelect.value.selectedNodes.some((n) => n.id === node.id);

    const canvasRect = graphCanvas.value.getBoundingClientRect();
    const mouseX = event.clientX - canvasRect.left;
    const mouseY = event.clientY - canvasRect.top;

    dragState.value = {
        isDragging: true,
        currentNode: node,
        offset: {
            x: mouseX - node.position.x,
            y: mouseY - node.position.y,
        },
        isMultiSelect: isMulti,
        initialPositions: isMulti
            ? boxSelect.value.selectedNodes.reduce((acc, n) => {
                  acc[n.id] = { ...n.position };
                  return acc;
              }, {})
            : null,
    };

    document.addEventListener("mousemove", dragNode);
    document.addEventListener("mouseup", stopDragNode);
};

// 更新选择框
const updateSelectionBox = (event) => {
    if (!boxSelect.value.isSelecting) return;

    const canvasRect = graphCanvas.value.getBoundingClientRect();
    boxSelect.value.endX = event.clientX - canvasRect.left;
    boxSelect.value.endY = event.clientY - canvasRect.top;

    calculateSelectedNodes();
};

// 计算选中的节点
const calculateSelectedNodes = () => {
    const { startX, startY, endX, endY } = boxSelect.value;
    const minX = Math.min(startX, endX);
    const maxX = Math.max(startX, endX);
    const minY = Math.min(startY, endY);
    const maxY = Math.max(startY, endY);

    // 计算新选中的节点（使用原始坐标判断）
    const newlySelected = graphData.nodes.filter((node) => {
        const nodeSize = getNodeSize(node);
        // 节点中心坐标（原始画布坐标）
        const centerX = node.position.x + nodeSize / 2;
        const centerY = node.position.y + nodeSize / 2;

        // 判断节点中心是否在框选范围内
        return (
            centerX >= minX &&
            centerX <= maxX &&
            centerY >= minY &&
            centerY <= maxY
        );
    });

    // 合并已有选择和新选择（去重）
    const allSelectedIds = new Set(
        boxSelect.value.selectedNodes.map((n) => n.id)
    );
    boxSelect.value.selectedNodes = [
        ...boxSelect.value.selectedNodes,
        ...newlySelected.filter((node) => !allSelectedIds.has(node.id)),
    ];
};

// 结束框选
const endSelection = () => {
    if (boxSelect.value.isSelecting) {
        boxSelect.value.isSelecting = false;

        if (boxSelect.value.selectedNodes.length > 0) {
            activeElement.value = {
                type: "multiple",
                nodes: boxSelect.value.selectedNodes,
            };
        }

        document.removeEventListener("mousemove", updateSelectionBox);
        document.removeEventListener("mouseup", endSelection);
    }
};

// 拖动节点（支持单个和多个）
const dragNode = (event) => {
    if (!dragState.value.isDragging) return;

    const canvasRect = graphCanvas.value.getBoundingClientRect();
    const currentX = event.clientX - canvasRect.left;
    const currentY = event.clientY - canvasRect.top;

    // 多节点拖动
    if (
        dragState.value.isMultiSelect &&
        boxSelect.value.selectedNodes.length > 0
    ) {
        const deltaX =
            currentX -
            (dragState.value.currentNode.position.x + dragState.value.offset.x);
        const deltaY =
            currentY -
            (dragState.value.currentNode.position.y + dragState.value.offset.y);

        boxSelect.value.selectedNodes.forEach((node) => {
            const initial = dragState.value.initialPositions[node.id];
            node.position.x = initial.x + deltaX;
            node.position.y = initial.y + deltaY;
        });
    }
    // 单个节点拖动
    else {
        const node = dragState.value.currentNode;
        node.position.x = currentX - dragState.value.offset.x;
        node.position.y = currentY - dragState.value.offset.y;

        // 边界检查
        node.position.x = Math.max(
            0,
            Math.min(node.position.x, canvasRect.width - getNodeSize(node))
        );
        node.position.y = Math.max(
            0,
            Math.min(node.position.y, canvasRect.height - getNodeSize(node))
        );
    }
};

// 停止拖动节点
const stopDragNode = () => {
    if (dragState.value.isDragging) {
        dragState.value.isDragging = false;
        dragState.value.initialPositions = null;
        recordHistory();
    }
    document.removeEventListener("mousemove", dragNode);
    document.removeEventListener("mouseup", stopDragNode);
};

// 更新元素属性
const updateElement = () => {
    if (!activeElement.value) return;

    if (activeElement.value.type === "node") {
        const node = graphData.nodes.find(
            (n) => n.id === activeElement.value.id
        );
        if (node) {
            node.data = { ...activeElement.value.data };
        }
    } else if (activeElement.value.type === "relationship") {
        const edge = graphData.relationships.find(
            (e) => e.id === activeElement.value.id
        );
        if (edge) {
            edge.data = { ...activeElement.value.data };
        }
    }

    nextTick(() => adjustEdgesContainerSize());
};

// 删除节点
const deleteNode = (nodeId) => {
    if (confirm("确定要删除此节点及其关联关系吗？")) {
        graphData.nodes = graphData.nodes.filter((n) => n.id !== nodeId);
        graphData.relationships = graphData.relationships.filter(
            (r) => r.data.source !== nodeId && r.data.target !== nodeId
        );

        boxSelect.value.selectedNodes = boxSelect.value.selectedNodes.filter(
            (n) => n.id !== nodeId
        );
        if (activeElement.value?.id === nodeId) {
            activeElement.value = boxSelect.value.selectedNodes.length
                ? { type: "multiple", nodes: boxSelect.value.selectedNodes }
                : null;
        }

        nextTick(() => adjustEdgesContainerSize());
        recordHistory();
    }
};

// 删除关系
const deleteRelationship = (edgeId) => {
    if (confirm("确定要删除此关系吗？")) {
        graphData.relationships = graphData.relationships.filter(
            (r) => r.id !== edgeId
        );
        activeElement.value = null;
        nextTick(() => adjustEdgesContainerSize());
        recordHistory();
    }
};

// 删除活动元素（支持批量删除）
const deleteActiveElement = () => {
    if (!activeElement.value) return;

    if (activeElement.value.type === "node") {
        deleteNode(activeElement.value.id);
    } else if (activeElement.value.type === "multiple") {
        if (
            confirm(
                `确定要删除选中的${activeElement.value.nodes.length}个节点及其关联关系吗？`
            )
        ) {
            const nodeIds = activeElement.value.nodes.map((n) => n.id);

            graphData.nodes = graphData.nodes.filter(
                (n) => !nodeIds.includes(n.id)
            );
            graphData.relationships = graphData.relationships.filter(
                (r) =>
                    !nodeIds.includes(r.data.source) &&
                    !nodeIds.includes(r.data.target)
            );

            boxSelect.value.selectedNodes = [];
            activeElement.value = null;

            nextTick(() => adjustEdgesContainerSize());
            recordHistory();
        }
    } else {
        deleteRelationship(activeElement.value.id);
    }
};

// 缩放控制
const zoomIn = () => {
    viewState.value.scale = Math.min(2, viewState.value.scale + 0.1);
    applyViewTransform();
};

const zoomOut = () => {
    viewState.value.scale = Math.max(0.5, viewState.value.scale - 0.1);
    applyViewTransform();
};

const resetView = () => {
    viewState.value = {
        scale: 1,
        offset: { x: 0, y: 0 },
    };
    applyViewTransform();
};

// 应用视图变换
const applyViewTransform = () => {
    if (graphCanvas.value) {
        graphCanvas.value.style.transform = `scale(${
            viewState.value.scale
        }) translate(${viewState.value.offset.x / viewState.value.scale}px, ${
            viewState.value.offset.y / viewState.value.scale
        }px)`;
    }
};

// 调整默认节点大小
const adjustDefaultNodeSize = () => {
    graphData.nodes.forEach((node) => {
        if (node.data.size === undefined) {
            node.data.size = defaultNodeSize.value;
        }
    });
    nextTick(() => adjustEdgesContainerSize());
};

// 调整边的粗细
const adjustEdgeThickness = () => {};

// 调整连接线容器大小
const adjustEdgesContainerSize = () => {
    if (graphCanvas.value && edgesContainer.value) {
        const rect = graphCanvas.value.getBoundingClientRect();
        edgesContainer.value.setAttribute("width", rect.width);
        edgesContainer.value.setAttribute("height", rect.height);
    }
};

// 历史记录操作
const recordHistory = () => {
    canUndo.value = true;
    canRedo.value = false;
};

const undo = () => {
    alert("撤销操作");
    canUndo.value = false;
    canRedo.value = true;
};

const redo = () => {
    alert("重做操作");
    canRedo.value = false;
    canUndo.value = true;
};

// 图谱操作
const saveGraph = async () => {
    try {
        await request.patch(
            `/graphs/${graphData.id}/`,
            {
                name: graphData.name,
                domainId: graphData.domainId,
                type: graphData.type,
                status: graphData.status,
                description: graphData.description || "",
                nodes: graphData.nodes,
                relationships: graphData.relationships,
            },
            {
                headers: {
                    "Content-Type": "application/json",
                },
            }
        );
        alert("图谱已保存");
    } catch (e) {
        await handleAuthFailure(e);
    }
};

const publishGraph = async () => {
    if (confirm("确定要发布此图谱吗？发布后所有人可见。")) {
        try {
            const resp = await request.post(`/graphs/${graphData.id}/publish/`);
            graphData.status = resp?.data?.status || "published";
            await saveGraph();
        } catch (e) {
            await handleAuthFailure(e);
        }
    }
};

const previewGraph = () => {
    alert("预览图谱功能");
};

const exportGraph = async () => {
    try {
        const resp = await request.get(`/graphs/${graphData.id}/export/`);
        const exportData = resp?.data || graphData;
        const dataStr =
            "data:text/json;charset=utf-8," +
            encodeURIComponent(JSON.stringify(exportData));

        const downloadAnchorNode = document.createElement("a");
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute(
            "download",
            `${graphData.name || "graph"}.json`
        );
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    } catch (e) {
        await handleAuthFailure(e);
    }
};

const exportAsImage = () => {
    alert("导出为图片功能");
};

const clearGraph = () => {
    if (confirm("确定要清空图谱吗？此操作不可恢复。")) {
        graphData.nodes = [];
        graphData.relationships = [];
        activeElement.value = null;
        boxSelect.value.selectedNodes = [];
        recordHistory();
    }
};

const autoArrange = () => {
    alert("自动排列功能");
};
</script>

<style scoped>
/* 额外工具区域样式 */
.extra-tools {
    margin-top: 20px;
    padding: 15px;
    background-color: #ffffff;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tools-section {
    display: inline-block;
    vertical-align: top;
    margin-right: 30px;
    padding-right: 30px;
    border-right: 1px solid #f1f5f9;
}

.tools-section:last-child {
    margin-right: 0;
    padding-right: 0;
    border-right: none;
}

.tools-section h3 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: #334155;
    font-weight: 600;
}

/* 按钮容器样式 */
.history-actions,
.import-export-actions,
.batch-actions {
    display: flex;
    gap: 8px;
}

/* 小按钮基础样式 */
.btn.btn-sm {
    padding: 4px 10px;
    font-size: 12px;
    border-radius: 4px;
    height: 28px;
    line-height: 18px;
    color: #ffffff;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
    background-size: 200% auto;
}

/* 历史记录按钮 - 蓝色渐变 */
.history-actions .btn.btn-sm {
    background-image: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.history-actions .btn.btn-sm:hover {
    background-position: right center;
    box-shadow: 0 2px 5px rgba(59, 130, 246, 0.3);
}

/* 导入导出按钮 - 绿色渐变 */
.import-export-actions .btn.btn-sm {
    background-image: linear-gradient(135deg, #10b981, #34d399);
}

.import-export-actions .btn.btn-sm:hover {
    background-position: right center;
    box-shadow: 0 2px 5px rgba(16, 185, 129, 0.3);
}

/* 批量操作按钮 - 紫色渐变 */
.batch-actions .btn.btn-sm {
    background-image: linear-gradient(135deg, #8b5cf6, #a78bfa);
}

.batch-actions .btn.btn-sm:hover {
    background-position: right center;
    box-shadow: 0 2px 5px rgba(139, 92, 246, 0.3);
}

/* 清空按钮特殊处理 - 红色渐变 */
/* 修正选择器写法，使用按钮内容作为区分 */
.batch-actions .btn.btn-sm:contains("清空图谱") {
    background-image: linear-gradient(135deg, #ef4444, #f87171);
}

.batch-actions .btn.btn-sm:contains("清空图谱"):hover {
    box-shadow: 0 2px 5px rgba(239, 68, 68, 0.3);
}

/* 禁用状态样式 */
.btn.btn-sm:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-image: linear-gradient(135deg, #e2e8f0, #cbd5e1);
    color: #94a3b8;
    box-shadow: none;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .tools-section {
        display: block;
        margin-right: 0;
        padding-right: 0;
        border-right: none;
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid #f1f5f9;
    }

    .tools-section:last-child {
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
    }
}

/* 添加功能提示对话框的样式 */
.feature-tip-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.feature-tip-dialog {
    background-color: white;
    padding: 20px 30px;
    border-radius: 8px;
    width: 400px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.feature-tip-dialog h3 {
    margin-top: 0;
    color: #1e293b;
    font-size: 18px;
}

.feature-tip-dialog p {
    color: #64748b;
    margin-bottom: 20px;
    line-height: 1.5;
}
/* 添加必要的样式 */
.selection-box {
    position: absolute;
    background-color: rgba(59, 130, 246, 0.2);
    border: 1px solid #3b82f6;
    pointer-events: none;
    z-index: 50;
}

.graph-node {
    position: absolute;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
    z-index: 10;
}

.graph-node.selected {
    box-shadow: 0 0 0 2px #3b82f6, 0 3px 10px rgba(59, 130, 246, 0.3);
}

.graph-node.active {
    box-shadow: 0 0 0 2px #10b981, 0 3px 10px rgba(16, 185, 129, 0.3);
}

.graph-canvas {
    position: relative;
    width: 100%;
    height: 600px;
    overflow: hidden;
}

.graph-edges {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 5;
}
/* 框选样式 */
.selection-box {
    position: absolute;
    background-color: rgba(59, 130, 246, 0.2);
    border: 1px solid #3b82f6;
    pointer-events: none;
    z-index: 50;
}

/* 选中节点样式 */
.graph-node.selected {
    box-shadow: 0 0 0 2px #3b82f6, 0 3px 10px rgba(59, 130, 246, 0.2);
}
/* 整体容器样式 */
.graph-editor-container {
    width: 100%;
    padding: 0 20px;
    margin: 0 auto;
    max-width: 1600px;
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
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-content h2 {
    margin: 0;
    font-size: 24px;
    color: #1e3a8a;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 10px;
}

.header-content p {
    margin: 8px 0 0 0;
    color: #666;
    font-size: 14px;
}

.header-actions {
    display: flex;
    gap: 10px;
}

/* 编辑器布局 */
.editor-layout {
    display: grid;
    grid-template-columns: 240px 1fr 300px;
    gap: 20px;
    margin-bottom: 25px;
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

.card h3 {
    margin-bottom: 18px;
    color: #1e3a8a;
    font-size: 18px;
    font-weight: 600;
    padding-bottom: 8px;
    border-bottom: 1px dashed rgba(59, 130, 246, 0.2);
    position: relative;
    display: inline-block;
}

.card h3::before {
    content: "▷";
    display: inline-block;
    margin-right: 8px;
    font-size: 14px;
    color: #3b82f6;
    vertical-align: middle;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.12);
    border-color: rgba(191, 219, 254, 0.8);
}

.card:hover::before {
    transform: scaleY(1);
    opacity: 1;
}

/* 工具栏样式 */
.editor-toolbar {
    height: fit-content;
}

.tool-group {
    margin-bottom: 25px;
}

.tool-group h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: #555;
    font-weight: 600;
}

.tool-buttons {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}

.tool-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12px 8px;
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 12px;
    color: #555;
}

.tool-btn i {
    font-size: 18px;
    margin-bottom: 5px;
}

.tool-btn:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
    color: #1e3a8a;
}

.tool-btn.active {
    background-color: #eff6ff;
    border-color: #3b82f6;
    color: #2563eb;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.tool-options {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.slider-control {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.slider-control label {
    font-size: 13px;
    color: #666;
}

.slider-control input {
    width: 100%;
}

/* 画布容器样式 */
.graph-canvas-container {
    display: flex;
    flex-direction: column;
    height: 700px; /* 增加画布高度 */
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
    user-select: none;
    -webkit-user-select: none; /* 兼容 Safari */
    -moz-user-select: none; /* 兼容 Firefox */
    -ms-user-select: none; /* 兼容 IE/Edge */
}

.canvas-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 15px;
    background-color: #f8fafc;
    border-bottom: 1px solid #e0e0e0;
    z-index: 100; /* 确保操作按钮在最上层 */
    position: relative;
}

.canvas-wrapper {
    flex: 1;
    overflow: auto; /* 允许滚动 */
    position: relative;
}

.graph-canvas {
    width: 2000px; /* 拓宽画布宽度 */
    height: 1500px; /* 拓宽画布高度 */
    position: relative;
    background-color: white;
    background-image: linear-gradient(
            rgba(226, 232, 240, 0.3) 1px,
            transparent 1px
        ),
        linear-gradient(90deg, rgba(226, 232, 240, 0.3) 1px, transparent 1px);
    background-size: 30px 30px;
    cursor: default;
    transition: transform 0.3s ease;
    transform-origin: 0 0;
}

.canvas-info {
    margin-left: auto;
    font-size: 13px;
    color: #666;
}

/* 节点样式 - 圆形容器设计 */
.graph-node {
    position: absolute;
    border-radius: 50%; /* 圆形容器 */
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: move;
    transition: all 0.2s ease;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
    z-index: 10; /* 确保节点在连接线之上 */
    user-select: none;
    border: 2px solid rgba(255, 255, 255, 0.8);
}

.graph-node.active {
    box-shadow: 0 0 0 3px #3b82f6, 0 5px 15px rgba(59, 130, 246, 0.3);
    transform: scale(1.05);
}

.graph-node:hover {
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.25);
    transform: scale(1.05);
}

.node-content {
    text-align: center;
    padding: 8px;
    color: white;
    width: 100%;
    box-sizing: border-box;
}

.node-label {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.node-category {
    font-size: 11px;
    opacity: 0.9;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 1px 6px;
    display: inline-block;
}

/* 连接线容器 */
.graph-edges {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 5; /* 确保连接线在节点之下 */
}

.graph-edges line {
    cursor: pointer;
    transition: all 0.2s ease;
    pointer-events: auto;
}

.graph-edges text {
    cursor: pointer;
    pointer-events: auto;
}

.graph-edges line:hover {
    stroke: #3b82f6;
    stroke-width: 2.5px;
}

.graph-edges line.active {
    stroke: #3b82f6;
    stroke-width: 3px;
}

.graph-edges text.active {
    fill: #2563eb;
    font-weight: 500;
}

.canvas-placeholder {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
}

.placeholder-content {
    text-align: center;
    padding: 20px;
}

.placeholder-content i {
    font-size: 48px;
    margin-bottom: 15px;
    opacity: 0.5;
}

.placeholder-content p {
    margin: 0 0 8px 0;
    font-size: 16px;
}

.placeholder-content .hint {
    font-size: 13px;
    opacity: 0.8;
}

/* 属性面板样式 */
.properties-panel {
    height: fit-content;
}

.property-group {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-bottom: 20px;
}

.property-group label {
    display: block;
    font-size: 14px;
    color: #555;
    margin-bottom: 5px;
    font-weight: 500;
}

.size-value {
    font-size: 13px;
    color: #666;
    margin-top: -10px;
    margin-left: 5px;
}

.color-selector {
    display: flex;
    align-items: center;
    gap: 10px;
}

.color-selector input {
    width: 50px;
    height: 36px;
    padding: 2px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    cursor: pointer;
}

.property-actions {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px dashed #e0e0e0;
}

.panel-placeholder {
    padding: 20px 0;
    color: #94a3b8;
    text-align: center;
    font-size: 14px;
}

/* 额外工具区域 */
.extra-tools {
    display: flex;
    gap: 20px;
    padding: 15px 22px;
}

.tools-section {
    flex: 1;
}

.tools-section h3 {
    margin-bottom: 12px;
    font-size: 16px;
    padding-bottom: 5px;
}

.history-actions,
.import-export-actions,
.batch-actions {
    display: flex;
    gap: 10px;
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
    gap: 5px;
}

.btn-sm {
    padding: 6px 12px;
    font-size: 13px;
}

.btn-preview {
    background-color: #f1f5f9;
    color: #334155;
}

.btn-preview:hover {
    background-color: #e2e8f0;
    color: #1e293b;
}

.btn-save {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-save:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-publish {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: white;
}

.btn-publish:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

.btn-danger {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
}

.btn-danger:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

/* 状态标签 */
.graph-status {
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    text-transform: capitalize;
}

.graph-status.draft {
    background-color: #f1c40f15;
    color: #d35400;
}

.graph-status.published {
    background-color: #2ecc7115;
    color: #27ae60;
}

.graph-status.archived {
    background-color: #95a5a615;
    color: #7f8c8d;
}

/* 输入框样式统一 */
.input-field {
    width: 100%;
    padding: 10px 12px;
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

.textarea-field {
    resize: vertical;
}

/* 响应式设计 */
@media (max-width: 1400px) {
    .editor-layout {
        grid-template-columns: 200px 1fr 260px;
    }
}

@media (max-width: 1024px) {
    .editor-layout {
        grid-template-columns: 1fr;
        grid-template-rows: auto 1fr auto;
    }

    .editor-toolbar {
        order: 0;
    }

    .graph-canvas-container {
        order: 1;
        height: 600px;
    }

    .properties-panel {
        order: 2;
    }

    .tool-buttons {
        grid-template-columns: repeat(4, 1fr);
    }

    .extra-tools {
        flex-direction: column;
        gap: 15px;
    }
}

@media (max-width: 768px) {
    .page-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .header-actions {
        width: 100%;
        justify-content: space-between;
    }

    .tool-buttons {
        grid-template-columns: repeat(2, 1fr);
    }

    .canvas-actions {
        flex-wrap: wrap;
    }

    .canvas-info {
        margin-left: 0;
        width: 100%;
        margin-top: 10px;
        text-align: center;
    }
}
</style>
