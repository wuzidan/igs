<template>
    <div class="route-planning-page">
        <!-- 加载状态界面 -->
        <div class="loading-container" v-if="isLoading">
            <div class="loading-content">
                <div class="loader"></div>
                <h2>正在生成学习路径...</h2>
                <p>请稍候，我们正在为您定制最佳学习方案</p>
            </div>
        </div>

        <!-- 加载失败界面 -->
        <!-- <div class="error-container" v-if="!isLoading && errorMsg">
            <div class="error-content">
                <div class="error-icon">⚠️</div>
                <h2>加载失败</h2>
                <p class="error-message">{{ errorMsg }}</p>
                <button class="retry-btn" @click="retryLoad">重试</button>
            </div>
        </div> -->

        <!-- 使用标准顶栏组件 -->
        <StudentHeader title="学习路径规划" />

        <!-- 目标知识点选择 -->
        <div class="card target-selection-card">
            <h3>选择学习目标</h3>
            <div class="target-selection">
                <div class="select-container">
                    <!-- 下拉选择框 -->
                    <div class="custom-select">
                        <!-- 选择框触发按钮 -->
                        <div class="select-trigger" @click="toggleDropdown" :class="{ 'disabled': isLoading }">
                            <span v-if="selectedTarget">{{ selectedTarget }}</span>
                            <span v-else class="placeholder">请选择目标知识点</span>
                            <span class="select-arrow" :class="{ 'open': showDropdown, 'disabled': isLoading }">▼</span>
                        </div>
                        
                        <!-- 下拉菜单 -->
                        <div class="select-dropdown" v-show="showDropdown && !isLoading">
                            <!-- 搜索框 -->
                            <div class="dropdown-search">
                                <div class="search-input-container">
                                    <input 
                                        type="text" 
                                        v-model="searchKeyword" 
                                        placeholder="搜索知识点..."
                                        class="search-input"
                                    />
                                    <button 
                                        v-if="searchKeyword" 
                                        class="clear-search-btn"
                                        @click.stop="searchKeyword = ''"
                                    >
                                        ×
                                    </button>
                                </div>
                            </div>
                            
                            <!-- 选项列表 -->
                            <div class="dropdown-options">
                                <div 
                                    v-for="knowledge in filteredKnowledgeList" 
                                    :key="knowledge" 
                                    class="dropdown-item"
                                    @click="selectKnowledge(knowledge)"
                                >
                                    {{ knowledge }}
                                </div>
                                <div v-if="filteredKnowledgeList.length === 0" class="dropdown-empty">
                                    没有找到匹配的知识点
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <button @click="generatePath" class="generate-btn" :disabled="!selectedTarget || isLoading">
                    {{ isLoading ? '生成中...' : '推荐路径' }}
                </button>
            </div>
        </div>

        <div class="dashboard">
            <!-- 学习路径图 -->
            <div class="card path-card">
                <h3>推荐学习路径</h3>
                <div class="path-visualization-container">
                    <div class="path-visualization">
                        <!-- 计算总节点数 -->
                        <template v-if="knowledgePoints.length > 0">
                            <!-- 计算总节点数（包括当前位置和目标节点） -->
                            <div
                                class="path-node current-node"
                                :style="{ left: '10%', top: '50%' }"
                            >
                                <div class="node-content">当前位置</div>
                            </div>

                            <!-- 主连接线 -->
                            <div class="path-connector main-connector"></div>

                            <!-- 路径节点 -->
                            <div
                                v-for="(point, index) in knowledgePoints.slice(0, -1)"
                                :key="index"
                                class="path-node next-node"
                                :style="{
                                    left: (20 + index * (60 / Math.max(1, knowledgePoints.length - 1))) + '%', 
                                    top: '50%'
                                }"
                            >
                                <div class="node-content">{{ point.name }}</div>
                                <div class="node-details">
                                    难度: {{ point.difficulty }}
                                </div>
                            </div>

                            <!-- 目标节点 -->
                            <div
                                v-if="selectedTarget"
                                class="path-node target-node"
                                :style="{ left: '85%', top: '50%' }"
                            >
                                <div class="node-content">{{ selectedTarget }}</div>
                            </div>
                            <div
                                v-else
                                class="path-node target-node"
                                :style="{ left: '85%', top: '50%' }"
                            >
                                <div class="node-content">学习目标</div>
                            </div>
                        </template>
                        <template v-else>
                            <!-- 没有路径数据时的默认布局 -->
                            <div
                                class="path-node current-node"
                                :style="{ left: '15%', top: '50%' }"
                            >
                                <div class="node-content">当前位置</div>
                            </div>

                            <!-- 主连接线 -->
                            <div class="path-connector main-connector"></div>

                            <!-- 目标节点 -->
                            <div
                                class="path-node target-node"
                                :style="{ left: '85%', top: '50%' }"
                            >
                                <div class="node-content">学习目标</div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>

            <!-- 推荐依据 -->
            <div class="card reason-card">
                <h3>推荐依据</h3>
                <div class="reason-content">
                    <p v-if="pathReason">
                        {{ pathReason }}
                    </p>
                    <p v-else class="loading-reason">
                        选择目标知识点后点击"推荐路径"按钮生成推荐依据...
                    </p>
                </div>
            </div>
        </div>

        <a href="/student/index" class="back-to-home">
            <span class="icon">🏠</span>
            <span>首页</span>
        </a>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
// 导入API
import api from "../../../api/index";
// 导入标准顶栏组件
import StudentHeader from "../StudentHeader.vue";

// 用户信息 - 现在由StudentHeader组件管理
const userName = ref("李四");
const studentId = ref("20230002");

// 知识点数据
const knowledgePoints = ref([]);

// 推荐依据
const pathReason = ref('');

// 学习目标
const targetKnowledge = ref('处理器调度');

// 状态变量
const isLoading = ref(false);
const errorMsg = ref("");

// 知识点列表
const knowledgeList = ref([]);

// 搜索关键词
const searchKeyword = ref('');

// 选中的目标知识点
const selectedTarget = ref('');

// 下拉框显示状态
const showDropdown = ref(false);

// 过滤后的知识点列表
const filteredKnowledgeList = computed(() => {
    if (!searchKeyword.value) {
        return knowledgeList.value;
    }
    return knowledgeList.value.filter(knowledge => 
        knowledge.toLowerCase().includes(searchKeyword.value.toLowerCase())
    );
});

// 选择知识点
const selectKnowledge = (knowledge) => {
    selectedTarget.value = knowledge;
    searchKeyword.value = knowledge;
    showDropdown.value = false;
};

// 清除选择
const clearSelection = () => {
    selectedTarget.value = '';
    searchKeyword.value = '';
};

// 切换下拉框显示/隐藏
const toggleDropdown = () => {
    showDropdown.value = !showDropdown.value;
};

// 获取知识图谱节点
const fetchKnowledgeNodes = () => {
    // 立即使用默认数据，确保下拉框有内容
    knowledgeList.value = [
        "文件管理",
        "进程调度",
        "内存管理",
        "处理器调度",
        "缺页中断",
        "存储分配",
        "系统配置",
        "缓存",
        "辅助存储器",
        "内存管理单元",
        "中断机制",
        "虚拟地址空间",
        "储存空间"
    ];
    
    // API调用代码
    return api
        .getKnowledgeNodes()
        .then((res) => {
            console.log("获取的知识图谱节点：", res.data);
            const data = res.data;
            console.log("data.code：", data.code);
            console.log("data.data：", data.data);
            if (data.code === 200 && data.data) {
                // 从完整的知识图谱数据中提取节点名称
                console.log("data.data.nodes：", data.data.nodes);
                if (data.data.nodes) {
                    knowledgeList.value = data.data.nodes.map(node => node.name);
                    console.log("knowledgeList赋值后：", knowledgeList.value);
                } else {
                    console.log("没有nodes字段，保持默认数据");
                }
            } else {
                console.log("code不是200或data不存在，保持默认数据");
            }
        })
        .catch((err) => {
            console.error("获取知识图谱节点失败：", err);
            console.log("API调用失败，保持默认数据");
        });
};

// 获取学习路径数据
const fetchRouteData = (target) => {
    isLoading.value = true;
    // 实际API调用代码
    return api
        .getLearningRoute({ student_id: studentId.value, target_knowledge: target })
        .then((res) => {
            console.log("获取的学习路径数据：", res.data);
            const data = res.data;
            
            // 更新知识点数据
            if (data.path) {
                // 转换数据格式，处理可能的JSON字符串
                knowledgePoints.value = data.path.map((item, index) => {
                    let name = item;
                    // 尝试解析JSON字符串
                    if (typeof item === 'string') {
                        try {
                            // 清理字符串，移除可能的引号和空格
                            const cleanedItem = item.trim().replace(/^["']|["']$/g, '');
                            const parsed = JSON.parse(cleanedItem);
                            if (parsed.topic) {
                                name = parsed.topic;
                            } else if (typeof parsed === 'string') {
                                name = parsed;
                            } else {
                                // 尝试将对象转换为字符串
                                name = JSON.stringify(parsed);
                            }
                        } catch (e) {
                            // 解析失败，使用原始字符串
                            // 尝试提取topic字段
                            const topicMatch = item.match(/"topic":"([^"]+)"/);
                            if (topicMatch && topicMatch[1]) {
                                name = topicMatch[1];
                            } else {
                                // 直接使用原始字符串
                                name = item;
                            }
                        }
                    } else if (typeof item === 'object' && item !== null) {
                        // 如果已经是对象，直接提取topic字段
                        if (item.topic) {
                            name = item.topic;
                        } else if (item.name) {
                            name = item.name;
                        } else {
                            // 尝试将对象转换为字符串
                            name = JSON.stringify(item);
                        }
                    }
                    return {
                        id: index + 1,
                        name: name,
                        difficulty: "medium", // 默认难度
                        mastery: 50, // 默认掌握度
                        icon: "📐" // 默认图标
                    };
                });
            }
            
            // 更新推荐依据
            if (data.explanation) {
                pathReason.value = data.explanation;
            }
        })
        .catch((err) => {
            console.error("获取学习路径失败：", err);
            // 临时注释掉错误信息设置
            // errorMsg.value = "获取学习路径数据失败，请稍后重试";
            
            // 失败时使用模拟数据
            return new Promise((resolve) => {
                setTimeout(() => {
                    // 模拟从LLM获取的学习路径数据
                    knowledgePoints.value = [
                        { id: 1, name: "Vue基础语法", difficulty: "easy", mastery: 85, icon: "📐" },
                        { id: 2, name: "组件通信", difficulty: "medium", mastery: 65, icon: "🔄" },
                        { id: 3, name: "Vuex状态管理", difficulty: "medium", mastery: 45, icon: "📦" },
                    ];

                    // 模拟从LLM获取的推荐依据
                    pathReason.value = "基于您的学习状态和知识图谱分析，我们为您推荐以下学习路径：首先巩固Vue基础语法，这是后续学习的基础；然后学习组件通信，这是Vue开发中的核心概念；最后学习Vuex状态管理，这将帮助您更好地管理应用状态。这个路径符合知识的逻辑递进关系，能够帮助您更高效地掌握Vue技术栈。";

                    resolve();
                }, 1000);
            });
        })
        .finally(() => {
            isLoading.value = false;
        });
};

// 生成路径
const generatePath = () => {
    if (!selectedTarget.value) return;
    showDropdown.value = false; // 生成路径时关闭下拉框
    fetchRouteData(selectedTarget.value);
};

// 获取用户信息
const fetchUserInfo = () => {
    return api
        .getStudentinfo()
        .then((res) => {
            console.log("获取的用户信息：", res.data);
            const data = res.data;
            userName.value = data.userName || "未知用户";
            studentId.value = data.studentId || "";
        })
        .catch((err) => {
            console.error("获取用户信息失败：", err);
            // 不显示错误，使用默认值
        });
};

onMounted(() => {
    // 加载用户信息和知识图谱节点
    Promise.all([fetchUserInfo(), fetchKnowledgeNodes()])
        .then(() => {
            console.log("知识图谱节点加载完成，共" + knowledgeList.value.length + "个节点");
            console.log("knowledgeList值：", knowledgeList.value);
        });
    
    // 点击外部关闭下拉框
    document.addEventListener('click', (e) => {
        const customSelect = document.querySelector('.custom-select');
        if (customSelect && !customSelect.contains(e.target)) {
            showDropdown.value = false;
        }
    });
});

// 方法：重试加载
// 临时注释掉重试函数
/* const retryLoad = () => {
    isLoading.value = true;
    errorMsg.value = "";

    fetchRouteData()
        .then(() => {
            isLoading.value = false;
        })
        .catch(() => {
            isLoading.value = false;
            errorMsg.value = "重试加载失败，请检查网络连接后再试";
        });
}; */

// 退出功能 - 现在由StudentHeader组件管理
// const logout = () => {
//     alert("您已退出系统");
// };
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Arial", sans-serif;
}

.route-planning-page {
    width: 100%;
    min-height: 100vh;
    padding: 20px;
    background-color: #f4f7f9;
}

/* 加载状态样式 */
.loading-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.loading-content {
    text-align: center;
    padding: 30px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.loader {
    width: 50px;
    height: 50px;
    border: 5px solid #f3f3f3;
    border-top: 5px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

/* 错误状态样式 */
.error-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
}

.error-content {
    text-align: center;
    max-width: 500px;
    padding: 30px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.error-icon {
    font-size: 48px;
    margin-bottom: 20px;
    color: #f97316;
}

.error-message {
    margin: 15px 0 25px;
    color: #64748b;
    line-height: 1.6;
}

.retry-btn {
    padding: 10px 20px;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.retry-btn:hover {
    background-color: #2563eb;
}

/* 头部样式 - 现在使用标准StudentHeader组件，此处样式已移除 */

/* 卡片样式 */
.dashboard {
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 100%;
}

/* 路径卡片样式 */
.path-card {
    min-height: 300px;
}

/* 推荐依据卡片样式 */
.reason-card {
    min-height: 200px;
}

.reason-content {
    font-size: 16px;
    line-height: 1.6;
    color: #333;
}

.loading-reason {
    color: #999;
    font-style: italic;
}

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

.card .progress-item,
.card .stat-item {
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0.9;
}

.card:hover .progress-item,
.card:hover .stat-item {
    transform: translateX(3px);
    opacity: 1;
}

.card:hover .progress-item:nth-child(2),
.card:hover .stat-item:nth-child(2) {
    transition-delay: 0.1s;
}

.card:hover .progress-item:nth-child(3),
.card:hover .stat-item:nth-child(3) {
    transition-delay: 0.2s;
}

/* 统计卡片样式 */
.stats-card {
    background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
    overflow: hidden;
    position: relative;
}

.stats-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #3498db 0%, #22c55e 100%);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-top: 10px;
}

.stat-card {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    border-color: transparent;
}

.stat-mastered {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.stat-weak {
    background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
}

.stat-progress {
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
}

.stat-recommended {
    background: linear-gradient(135deg, #fcfafe 0%, #f3e8ff 100%);
}

.stat-icon {
    font-size: 24px;
    margin-bottom: 8px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-info {
    margin-bottom: 8px;
}

.stat-card .stat-label {
    font-size: 13px;
    color: #64748b;
    font-weight: 500;
}

.stat-card .stat-value {
    font-size: 22px;
    font-weight: 700;
    color: #1e293b;
    line-height: 1.2;
}

.stat-trend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
}

.trend-arrow {
    font-weight: bold;
}

.trend-arrow.up {
    color: #10b981;
}

.trend-arrow.down {
    color: #ef4444;
}

.trend-text {
    color: #64748b;
}

.trend-date {
    color: #8b5cf6;
    font-weight: 500;
}

/* 目标知识点选择样式 */
.target-selection-card {
    margin-bottom: 20px;
    overflow: visible;
    z-index: 1000;
}

.target-selection {
    display: flex;
    gap: 15px;
    align-items: center;
    flex-wrap: wrap;
}

.select-container {
    flex: 1;
    min-width: 300px;
    position: relative;
}

.custom-select {
    position: relative;
    width: 100%;
}

.select-trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 15px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: white;
    cursor: pointer;
    transition: all 0.3s ease;
}

.select-trigger:hover {
    border-color: #3b82f6;
}

.select-trigger:focus-within {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-trigger .placeholder {
    color: #94a3b8;
}

.select-arrow {
    font-size: 12px;
    color: #64748b;
    transition: transform 0.3s ease;
}

.select-arrow.open {
    transform: rotate(180deg);
}

.select-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 300px;
    overflow-y: auto;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 0 0 6px 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 9999;
    margin-top: 2px;
}

.dropdown-search {
    padding: 10px;
    border-bottom: 1px solid #e2e8f0;
}

.search-input-container {
    position: relative;
    width: 100%;
}

.dropdown-search .search-input {
    width: 100%;
    padding: 8px 32px 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 14px;
    transition: all 0.3s ease;
}

.dropdown-search .search-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.clear-search-btn {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 18px;
    color: #94a3b8;
    cursor: pointer;
    padding: 0 4px;
    border-radius: 2px;
    transition: all 0.2s ease;
}

.clear-search-btn:hover {
    background-color: #f1f5f9;
    color: #64748b;
}

.select-container.disabled {
    pointer-events: none;
    opacity: 0.6;
}

.select-trigger.disabled {
    cursor: not-allowed;
    background-color: #f8fafc;
}

.select-arrow.disabled {
    color: #cbd5e1;
}

.dropdown-options {
    max-height: 250px;
    overflow-y: auto;
}

.dropdown-item {
    padding: 10px 15px;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.dropdown-item:hover {
    background-color: #f1f5f9;
}

.dropdown-empty {
    padding: 15px;
    text-align: center;
    color: #94a3b8;
    font-size: 14px;
}

.generate-btn {
    padding: 10px 20px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    white-space: nowrap;
}

.generate-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.generate-btn:disabled {
    background: #e2e8f0;
    color: #94a3b8;
    cursor: not-allowed;
}

/* 路径可视化容器 */
.path-visualization-container {
    width: 100%;
    min-height: 250px;
    margin-top: 20px;
}

/* 路径可视化样式 */
.path-visualization {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 200px;
    padding: 40px 0;
}

.path-node {
    position: absolute;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 15px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    transform: translate(-50%, -50%);
    transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    z-index: 2;
    background-color: white;
}

.path-node:hover {
    transform: translate(-50%, -50%) scale(1.1);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
}

.path-node .node-content {
    font-size: 12px;
    font-weight: 600;
    line-height: 1.2;
}

.path-node .node-details {
    font-size: 10px;
    margin-top: 3px;
    color: #64748b;
}

.current-node {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: 3px solid #93c5fd;
    width: 110px;
    height: 110px;
}

.next-node {
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    color: #1e293b;
    border: 2px solid #dbeafe;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    width: 90px;
    height: 90px;
}

.next-node:hover {
    border-color: #3b82f6;
}

.target-node {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: 3px solid #a7f3d0;
    width: 110px;
    height: 110px;
}

.path-connector {
    position: absolute;
    top: 50%;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd, #bfdbfe);
    transform: translateY(-50%);
    z-index: 1;
}

.main-connector {
    height: 4px;
    background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd, #10b981);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

/* 知识点列表样式 */
.knowledge-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.knowledge-item {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
}

.knowledge-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
}

.knowledge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.knowledge-name {
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 8px;
}

.knowledge-icon {
    font-size: 18px;
}

.knowledge-difficulty {
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.difficulty-easy {
    background-color: #dcfce7;
    color: #166534;
}

.difficulty-medium {
    background-color: #fef3c7;
    color: #92400e;
}

.difficulty-hard {
    background-color: #fee2e2;
    color: #b91c1c;
}

.mastery-progress {
    margin-bottom: 12px;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 14px;
}

.progress-container {
    width: 100%;
    height: 10px;
    background-color: #f0f0f0;
    border-radius: 5px;
    overflow: hidden;
}

.progress {
    height: 100%;
    transition: width 0.3s ease;
    border-radius: 5px;
}

.progress-low {
    background: linear-gradient(90deg, #c0392b 0%, #e74c3c 100%);
}

.progress-medium {
    background: linear-gradient(90deg, #d35400 0%, #f39c12 50%, #f1c40f 100%);
}

.progress-high {
    background: linear-gradient(90deg, #1e7e34 0%, #2ecc71 50%, #81c784 100%);
}

.knowledge-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.review-btn,
.practice-btn {
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
}

.review-btn {
    background-color: #dbeafe;
    color: #1e40af;
}

.review-btn:hover {
    background-color: #bfdbfe;
}

.practice-btn {
    background-color: #dcfce7;
    color: #065f46;
}

.practice-btn:hover {
    background-color: #bbf7d0;
}

/* 资源推荐样式 */
.resources-filter {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.filter-control {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 10px;
    background-color: #f8fafc;
    border-radius: 6px;
}

.filter-label {
    font-size: 14px;
    color: #334155;
}

.resource-select {
    padding: 6px 25px 6px 10px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    background-color: #fff;
    font-size: 14px;
    color: #1e293b;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 8px center;
    cursor: pointer;
    transition: border-color 0.2s;
}

.resource-select:focus {
    outline: none;
    border-color: #3498db;
}

.resources-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
}

.resource-card {
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}

.resource-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.resource-type-badge {
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 500;
    color: white;
}

.resource-type-badge.video {
    background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.resource-type-badge.article {
    background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}

.resource-type-badge.exercise {
    background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.resource-type-badge.document {
    background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
}

.resource-content {
    padding: 15px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.resource-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #1e293b;
    line-height: 1.4;
}

.resource-description {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 12px;
    line-height: 1.5;
    flex: 1;
}

.resource-meta {
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    font-size: 12px;
    color: #64748b;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
}

.meta-item.difficulty.easy {
    color: #10b981;
}

.meta-item.difficulty.medium {
    color: #f59e0b;
}

.meta-item.difficulty.hard {
    color: #ef4444;
}

.resource-knowledge {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
    font-size: 12px;
}

.knowledge-tag {
    background-color: #eff6ff;
    color: #1e40af;
    padding: 2px 8px;
    border-radius: 12px;
}

.resource-action-btn {
    width: 100%;
    padding: 8px 0;
    background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.resource-action-btn:hover {
    background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
    transform: translateY(-1px);
    box-shadow: 0 3px 6px rgba(59, 130, 246, 0.15);
}

/* 周计划样式 */
.weekly-plan {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 15px;
}

.day-column {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
    overflow: hidden;
}

.day-header {
    background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    padding: 10px;
    text-align: center;
    font-weight: 600;
    font-size: 14px;
}

.day-content {
    padding: 10px;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.plan-item {
    display: flex;
    align-items: center;
    padding: 8px;
    background-color: #f8fafc;
    border-radius: 4px;
    font-size: 13px;
    gap: 10px;
}

.plan-icon {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    background-color: #dbeafe;
    color: #1e40af;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.plan-details {
    flex: 1;
}

.plan-title {
    font-weight: 500;
    margin-bottom: 2px;
}

.plan-duration {
    font-size: 11px;
    color: #64748b;
}

.plan-status {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    flex-shrink: 0;
}

.plan-status.completed {
    background-color: #dcfce7;
    color: #166534;
}

.plan-status.in-progress {
    background-color: #dbeafe;
    color: #1e40af;
}

.plan-status.pending {
    background-color: #f1f5f9;
    color: #64748b;
}

.add-plan-btn {
    margin-top: auto;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #eff6ff;
    color: #2563eb;
    border: 1px dashed #93c5fd;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.add-plan-btn:hover {
    background-color: #dbeafe;
    transform: scale(1.1);
}

/* 无数据样式 */
.no-data {
    text-align: center;
    color: #888;
    padding: 40px 20px;
    font-style: italic;
    background-color: white;
    border-radius: 8px;
    border: 1px solid #eee;
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
    .weekly-plan {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr;
    }

    .weekly-plan {
        grid-template-columns: repeat(2, 1fr);
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .resources-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .weekly-plan {
        grid-template-columns: 1fr;
    }

    .header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .user-info {
        width: 100%;
        justify-content: space-between;
    }
}
</style>