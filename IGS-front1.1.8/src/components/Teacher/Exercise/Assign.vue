<template>
    <div class="assignment-container">
      <!-- 返回首页 -->
       <a href="/teacher/index" class="back-to-home">
        <span class="icon">🏠</span>
        <span>首页</span>
    </a>
      <!-- 发布作业主区域 -->
      <div class="assignment-card">
        <h2 class="assignment-title">
          <span class="title-icon">📝</span>
          发布新作业
        </h2>
        
        <!-- 作业基本信息表单 -->
        <div class="form-section">
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">📋</span>
              <span>作业基本信息</span>
            </div>
            <div class="section-subtitle">填写作业的基本信息和要求</div>
          </div>
  
          <div class="form-grid">
            <div class="form-group">
              <label for="assignmentName" class="form-label">
                <span class="required">*</span>
                作业名称
              </label>
              <input
                type="text"
                id="assignmentName"
                v-model="assignment.name"
                placeholder="请输入作业名称"
                class="form-input"
              />
              <div class="form-hint">请填写一个清晰的作业名称</div>
            </div>
  
            <div class="form-group">
              <label for="deadline" class="form-label">
                <span class="required">*</span>
                截止时间
              </label>
              <input
                type="datetime-local"
                id="deadline"
                v-model="assignment.deadline"
                class="form-input"
              />
              <div class="form-hint">设置作业提交的最后期限</div>
            </div>
  
            <div class="form-group">
              <label for="class" class="form-label">
                <span class="required">*</span>
                选择班级
              </label>
              <select id="class" v-model="assignment.selectedClass" class="form-select">
                <option value="" disabled>请选择班级</option>
                <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
                  {{ classItem.name }} ({{ classItem.studentCount }}人)
                </option>
              </select>
              <div class="form-hint">选择要发布作业的班级</div>
            </div>
  
            <div class="form-group full-width">
              <label for="description" class="form-label">
                <span class="icon">📝</span>
                作业描述
              </label>
              <textarea
                id="description"
                v-model="assignment.description"
                placeholder="请输入作业的具体要求和说明..."
                class="form-textarea"
                rows="4"
              ></textarea>
              <div class="form-hint">{{ assignment.description.length }}/500 字符</div>
            </div>
          </div>
        </div>
  
        <!-- 题目选择区域 -->
        <div class="form-section">
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">📚</span>
              <span>从题库选择题目</span>
            </div>
            <div class="section-subtitle">从题库中挑选题目添加到作业中</div>
          </div>
  
          <!-- 题库筛选 -->
          <div class="question-filter">
            <div class="filter-group">
              <input
                type="text"
                v-model="searchKeyword"
                placeholder="搜索题目名称或关键词..."
                class="search-input"
              />
              <button class="search-button">
                <span class="search-icon">🔍</span>
                搜索
              </button>
            </div>
            
            <div class="filter-group">
              <label class="filter-label">难度：</label>
              <div class="filter-tags">
                <button
                  v-for="difficulty in difficultyLevels"
                  :key="difficulty.value"
                  :class="['tag-button', { 'tag-active': selectedDifficulty === difficulty.value }]"
                  @click="toggleDifficulty(difficulty.value)"
                >
                  {{ difficulty.label }}
                </button>
              </div>
            </div>
  
            <div class="filter-group">
              <label class="filter-label">类型：</label>
              <div class="filter-tags">
                <button
                  v-for="type in questionTypes"
                  :key="type.value"
                  :class="['tag-button', { 'tag-active': selectedType === type.value }]"
                  @click="toggleType(type.value)"
                >
                  {{ type.label }}
                </button>
              </div>
            </div>
          </div>
  
          <!-- 题库列表 -->
          <div class="question-bank">
            <div class="question-list-header">
              <div class="question-count">
                共 {{ filteredQuestions.length }} 道题目
                <span v-if="selectedQuestions.length > 0" class="selected-count">
                  （已选 {{ selectedQuestions.length }} 道）
                </span>
              </div>
              <button
                class="select-all-btn"
                @click="toggleSelectAll"
                :class="{ 'select-all-active': isAllSelected }"
              >
                {{ isAllSelected ? '取消全选' : '全选' }}
              </button>
            </div>
  
            <div class="question-list">
              <div
                v-for="question in paginatedQuestions"
                :key="question.id"
                :class="['question-card', { 'question-selected': isSelected(question.id) }]"
                @click="toggleQuestion(question.id)"
              >
                <div class="question-card-header">
                  <div class="question-checkbox">
                    <input
                      type="checkbox"
                      :checked="isSelected(question.id)"
                      @change="toggleQuestion(question.id)"
                      class="checkbox-input"
                    />
                  </div>
                  <div class="question-title">
                    {{ question.title }}
                    <span class="question-tag question-tag-difficulty" :class="`difficulty-${question.difficulty}`">
                      {{ getDifficultyText(question.difficulty) }}
                    </span>
                    <span class="question-tag question-tag-type">
                      {{ getTypeText(question.type) }}
                    </span>
                  </div>
                  <div class="question-meta">
                    <span class="meta-item">
                      <span class="meta-icon">⏱️</span>
                      预计用时: {{ question.estimatedTime }}分钟
                    </span>
                    <span class="meta-item">
                      <span class="meta-icon">👥</span>
                      使用次数: {{ question.usedCount }}次
                    </span>
                  </div>
                </div>
                
                <div class="question-content">
                  {{ question.content.substring(0, 100) }}...
                </div>
                
                <div class="question-footer">
                  <div class="question-skills">
                    <span class="skills-label">知识点：</span>
                    <span v-for="skill in question.skills.slice(0, 3)" :key="skill" class="skill-tag">
                      {{ skill }}
                    </span>
                    <span v-if="question.skills.length > 3" class="more-skills">
                      +{{ question.skills.length - 3 }}个
                    </span>
                  </div>
                  <div class="question-actions">
                    <button class="preview-btn" @click.stop="previewQuestion(question.id)">
                      <span class="preview-icon">👁️</span>
                      预览
                    </button>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- 分页 -->
            <div v-if="filteredQuestions.length > pageSize" class="pagination">
              <button
                :disabled="currentPage === 1"
                @click="currentPage--"
                class="page-button"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
              </span>
              <button
                :disabled="currentPage === totalPages"
                @click="currentPage++"
                class="page-button"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
  
        <!-- 已选题目预览 -->
        <div v-if="selectedQuestions.length > 0" class="selected-section">
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">✅</span>
              <span>已选题目 ({{ selectedQuestions.length }} 道)</span>
            </div>
            <button class="clear-selection" @click="clearSelection">
              <span class="clear-icon">🗑️</span>
              清空选择
            </button>
          </div>
          
          <div class="selected-list">
            <div
              v-for="question in selectedQuestions"
              :key="question.id"
              class="selected-item"
            >
              <div class="selected-item-content">
                <div class="selected-item-title">
                  <span class="item-index">{{ selectedQuestions.indexOf(question) + 1 }}.</span>
                  {{ question.title }}
                </div>
                <div class="selected-item-meta">
                  <span class="meta-badge difficulty-badge" :class="`difficulty-${question.difficulty}`">
                    {{ getDifficultyText(question.difficulty) }}
                  </span>
                  <span class="meta-badge">
                    ⏱️ {{ question.estimatedTime }}分钟
                  </span>
                </div>
              </div>
              <button class="remove-btn" @click="removeQuestion(question.id)">
                <span class="remove-icon">×</span>
              </button>
            </div>
          </div>
        </div>
  
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button class="action-btn action-btn-secondary" @click="saveDraft">
            <span class="btn-icon">💾</span>
            保存草稿
          </button>
          <button class="action-btn action-btn-primary" @click="publishAssignment" :disabled="!canPublish">
            <span class="btn-icon">🚀</span>
            发布作业
          </button>
          <button class="action-btn action-btn-cancel" @click="cancel">
            <span class="btn-icon">↩️</span>
            取消
          </button>
        </div>
      </div>
  
      <!-- 预览模态框 -->
      <div v-if="showPreview" class="modal-overlay" @click="closePreview">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>题目预览</h3>
            <button class="modal-close" @click="closePreview">×</button>
          </div>
          <div class="modal-body">
            <div v-if="previewQuestionData" class="preview-content">
              <h4>{{ previewQuestionData.title }}</h4>
              <div class="preview-meta">
                <span class="preview-tag" :class="`difficulty-${previewQuestionData.difficulty}`">
                  {{ getDifficultyText(previewQuestionData.difficulty) }}
                </span>
                <span class="preview-tag">
                  {{ getTypeText(previewQuestionData.type) }}
                </span>
                <span class="preview-tag">
                  ⏱️ {{ previewQuestionData.estimatedTime }}分钟
                </span>
              </div>
              <div class="preview-description">
                <h5>题目描述</h5>
                <p>{{ previewQuestionData.content }}</p>
              </div>
              <div class="preview-skills">
                <h5>涉及知识点</h5>
                <div class="skills-list">
                  <span v-for="skill in previewQuestionData.skills" :key="skill" class="skill-badge">
                    {{ skill }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'AssignAssignment',
    data() {
      return {
        assignment: {
          name: '',
          deadline: '',
          description: '',
          selectedClass: '',
        },
        classes: [
          { id: '1', name: '计算机科学2023级1班', studentCount: 45 },
          { id: '2', name: '软件工程2023级2班', studentCount: 50 },
          { id: '3', name: '人工智能2023级3班', studentCount: 40 },
          { id: '4', name: '数据科学2023级4班', studentCount: 38 },
        ],
        searchKeyword: '',
        selectedDifficulty: null,
        selectedType: null,
        selectedQuestions: [],
        showPreview: false,
        previewQuestionData: null,
        currentPage: 1,
        pageSize: 8,
        
        difficultyLevels: [
          { value: 'easy', label: '简单' },
          { value: 'medium', label: '中等' },
          { value: 'hard', label: '困难' },
        ],
        
        questionTypes: [
          { value: 'single', label: '单选题' },
          { value: 'multiple', label: '多选题' },
          { value: 'programming', label: '编程题' },
          { value: 'short', label: '简答题' },
        ],
        
        // 模拟题库数据
        questions: [
          {
            id: 1,
            title: '变量和数据类型基础',
            content: '定义一个整数变量并赋值，然后将其转换为浮点数类型。',
            difficulty: 'easy',
            type: 'programming',
            estimatedTime: 10,
            usedCount: 156,
            skills: ['变量声明', '数据类型', '类型转换'],
          },
          {
            id: 2,
            title: '条件语句应用',
            content: '编写一个程序，判断用户输入的数字是否为素数。',
            difficulty: 'medium',
            type: 'programming',
            estimatedTime: 20,
            usedCount: 98,
            skills: ['条件语句', '循环', '数学运算'],
          },
          {
            id: 3,
            title: '数组操作练习',
            content: '实现一个函数，将数组中的元素反转。',
            difficulty: 'medium',
            type: 'programming',
            estimatedTime: 15,
            usedCount: 120,
            skills: ['数组', '函数', '算法'],
          },
          {
            id: 4,
            title: '面向对象基础',
            content: '设计一个Student类，包含姓名、学号、成绩等属性。',
            difficulty: 'easy',
            type: 'programming',
            estimatedTime: 25,
            usedCount: 85,
            skills: ['类定义', '属性', '方法'],
          },
          {
            id: 5,
            title: '递归算法实现',
            content: '使用递归计算斐波那契数列的第n项。',
            difficulty: 'hard',
            type: 'programming',
            estimatedTime: 30,
            usedCount: 65,
            skills: ['递归', '算法', '数学'],
          },
          {
            id: 6,
            title: '字符串处理',
            content: '统计字符串中每个字符出现的次数。',
            difficulty: 'medium',
            type: 'programming',
            estimatedTime: 20,
            usedCount: 110,
            skills: ['字符串', '字典', '循环'],
          },
          {
            id: 7,
            title: '文件操作基础',
            content: '读取文本文件，统计文件中单词的数量。',
            difficulty: 'medium',
            type: 'programming',
            estimatedTime: 25,
            usedCount: 72,
            skills: ['文件操作', '字符串处理'],
          },
          {
            id: 8,
            title: '异常处理',
            content: '编写一个程序，处理除零异常和其他常见异常。',
            difficulty: 'easy',
            type: 'programming',
            estimatedTime: 15,
            usedCount: 90,
            skills: ['异常处理', '条件判断'],
          },
        ],
      };
    },
    computed: {
      filteredQuestions() {
        let filtered = this.questions;
        
        // 关键词搜索
        if (this.searchKeyword) {
          const keyword = this.searchKeyword.toLowerCase();
          filtered = filtered.filter(q => 
            q.title.toLowerCase().includes(keyword) || 
            q.content.toLowerCase().includes(keyword) ||
            q.skills.some(skill => skill.toLowerCase().includes(keyword))
          );
        }
        
        // 难度筛选
        if (this.selectedDifficulty) {
          filtered = filtered.filter(q => q.difficulty === this.selectedDifficulty);
        }
        
        // 类型筛选
        if (this.selectedType) {
          filtered = filtered.filter(q => q.type === this.selectedType);
        }
        
        return filtered;
      },
      
      paginatedQuestions() {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        return this.filteredQuestions.slice(start, end);
      },
      
      totalPages() {
        return Math.ceil(this.filteredQuestions.length / this.pageSize);
      },
      
      isAllSelected() {
        return this.filteredQuestions.length > 0 && 
               this.filteredQuestions.every(q => this.isSelected(q.id));
      },
      
      canPublish() {
        return (
          this.assignment.name.trim() &&
          this.assignment.deadline &&
          this.assignment.selectedClass &&
          this.selectedQuestions.length > 0
        );
      },
    },
    methods: {
      getDifficultyText(level) {
        const map = {
          easy: '简单',
          medium: '中等',
          hard: '困难',
        };
        return map[level] || level;
      },
      
      getTypeText(type) {
        const map = {
          single: '单选题',
          multiple: '多选题',
          programming: '编程题',
          short: '简答题',
        };
        return map[type] || type;
      },
      
      toggleDifficulty(difficulty) {
        this.selectedDifficulty = this.selectedDifficulty === difficulty ? null : difficulty;
        this.currentPage = 1;
      },
      
      toggleType(type) {
        this.selectedType = this.selectedType === type ? null : type;
        this.currentPage = 1;
      },
      
      toggleQuestion(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (!question) return;
        
        const index = this.selectedQuestions.findIndex(q => q.id === questionId);
        if (index > -1) {
          this.selectedQuestions.splice(index, 1);
        } else {
          this.selectedQuestions.push(question);
        }
      },
      
      toggleSelectAll() {
        if (this.isAllSelected) {
          // 取消全选：只取消当前页的选中
          const currentPageIds = this.paginatedQuestions.map(q => q.id);
          this.selectedQuestions = this.selectedQuestions.filter(
            q => !currentPageIds.includes(q.id)
          );
        } else {
          // 全选：添加当前页所有未选中的题目
          this.paginatedQuestions.forEach(question => {
            if (!this.isSelected(question.id)) {
              this.selectedQuestions.push(question);
            }
          });
        }
      },
      
      isSelected(questionId) {
        return this.selectedQuestions.some(q => q.id === questionId);
      },
      
      removeQuestion(questionId) {
        const index = this.selectedQuestions.findIndex(q => q.id === questionId);
        if (index > -1) {
          this.selectedQuestions.splice(index, 1);
        }
      },
      
      clearSelection() {
        this.selectedQuestions = [];
      },
      
      previewQuestion(questionId) {
        this.previewQuestionData = this.questions.find(q => q.id === questionId);
        this.showPreview = true;
      },
      
      closePreview() {
        this.showPreview = false;
        this.previewQuestionData = null;
      },
      
      saveDraft() {
        const draft = {
          ...this.assignment,
          selectedQuestions: this.selectedQuestions.map(q => q.id),
          savedAt: new Date().toISOString(),
        };
        
        // 这里应该调用API保存草稿
        localStorage.setItem('assignmentDraft', JSON.stringify(draft));
        
        this.$message({
          type: 'success',
          message: '草稿保存成功！',
        });
      },
      
      async publishAssignment() {
        if (!this.canPublish) {
          this.$message({
            type: 'warning',
            message: '请填写完整信息并至少选择一道题目',
          });
          return;
        }
        
        try {
          const assignmentData = {
            name: this.assignment.name,
            deadline: this.assignment.deadline,
            description: this.assignment.description,
            classId: this.assignment.selectedClass,
            questions: this.selectedQuestions.map(q => q.id),
          };
          
          // 这里应该调用API发布作业
          console.log('发布作业数据:', assignmentData);
          
          this.$message({
            type: 'success',
            message: '作业发布成功！',
          });
          
          // 发布成功后跳转到作业列表页
          setTimeout(() => {
            this.$router.push('/teacher/exercise/existing');
          }, 1500);
          
        } catch (error) {
          this.$message({
            type: 'error',
            message: '发布失败，请重试',
          });
        }
      },
      
      cancel() {
        this.$confirm('确定要取消吗？已填写的内容将不会被保存。', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }).then(() => {
          this.$router.push('/teacher/exercise/existing');
        });
      },
    },
    watch: {
      searchKeyword() {
        this.currentPage = 1;
      },
    },
  };
  </script>
  
  <style scoped>
  .assignment-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
  }
  
  .back-to-home {
    margin-bottom: 32px;
  }
  
  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #666;
    text-decoration: none;
    font-size: 14px;
    padding: 8px 16px;
    border-radius: 6px;
    transition: all 0.3s ease;
  }
  
  .back-link:hover {
    color: #1890ff;
    background-color: #f0f7ff;
  }
  
  .assignment-card {
    background: white;
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #e8e8e8;
  }
  
  .assignment-title {
    font-size: 28px;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .title-icon {
    font-size: 32px;
  }
  
  .form-section {
    margin-bottom: 40px;
    padding-bottom: 32px;
    border-bottom: 2px solid #f5f5f5;
  }
  
  .section-header {
    margin-bottom: 24px;
  }
  
  .section-title {
    font-size: 20px;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .section-icon {
    font-size: 20px;
  }
  
  .section-subtitle {
    color: #666;
    font-size: 14px;
  }
  
  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
  }
  
  .form-group.full-width {
    grid-column: 1 / -1;
  }
  
  .form-label {
    display: flex;
    align-items: center;
    gap: 4px;
    font-weight: 500;
    color: #333;
    margin-bottom: 8px;
    font-size: 14px;
  }
  
  .required {
    color: #ff4d4f;
  }
  
  .form-input,
  .form-select,
  .form-textarea {
    padding: 12px 16px;
    border: 2px solid #e8e8e8;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.3s ease;
    background: white;
  }
  
  .form-input:focus,
  .form-select:focus,
  .form-textarea:focus {
    outline: none;
    border-color: #1890ff;
    box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
  }
  
  .form-select {
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23666' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10l-5 5z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 16px center;
    background-size: 12px;
    padding-right: 40px;
  }
  
  .form-textarea {
    resize: vertical;
    min-height: 100px;
  }
  
  .form-hint {
    font-size: 12px;
    color: #999;
    margin-top: 4px;
  }
  
  /* 题目筛选 */
  .question-filter {
    background: #fafafa;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
  }
  
  .filter-group {
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .filter-group:last-child {
    margin-bottom: 0;
  }
  
  .filter-label {
    font-size: 14px;
    font-weight: 500;
    color: #333;
    min-width: 50px;
  }
  
  .search-input {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #e8e8e8;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.3s ease;
  }
  
  .search-input:focus {
    outline: none;
    border-color: #1890ff;
  }
  
  .search-button {
    padding: 12px 24px;
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
  }
  
  .search-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  }
  
  .filter-tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .tag-button {
    padding: 6px 16px;
    border: 2px solid #e8e8e8;
    border-radius: 20px;
    background: white;
    color: #666;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .tag-button:hover {
    border-color: #1890ff;
    color: #1890ff;
  }
  
  .tag-active {
    background: #1890ff;
    border-color: #1890ff;
    color: white;
  }
  
  /* 题库列表 */
  .question-bank {
    background: white;
    border-radius: 12px;
    border: 2px solid #f0f0f0;
    overflow: hidden;
  }
  
  .question-list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background: #fafafa;
    border-bottom: 2px solid #f0f0f0;
  }
  
  .question-count {
    font-size: 14px;
    color: #666;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .selected-count {
    color: #1890ff;
    font-weight: 500;
  }
  
  .select-all-btn {
    padding: 6px 16px;
    background: white;
    border: 2px solid #e8e8e8;
    border-radius: 6px;
    color: #666;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .select-all-btn:hover {
    border-color: #1890ff;
    color: #1890ff;
  }
  
  .select-all-active {
    background: #1890ff;
    border-color: #1890ff;
    color: white;
  }
  
  .question-list {
    padding: 16px;
    max-height: 600px;
    overflow-y: auto;
  }
  
  .question-card {
    padding: 20px;
    border: 2px solid #f0f0f0;
    border-radius: 12px;
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: white;
  }
  
  .question-card:hover {
    border-color: #1890ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
  }
  
  .question-selected {
    border-color: #1890ff;
    background: linear-gradient(135deg, rgba(24, 144, 255, 0.05) 0%, rgba(24, 144, 255, 0.02) 100%);
  }
  
  .question-card-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 12px;
  }
  
  .question-checkbox {
    margin-top: 4px;
  }
  
  .checkbox-input {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #1890ff;
  }
  
  .question-title {
    flex: 1;
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .question-tag {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
  }
  
  .question-tag-difficulty {
    color: white;
  }
  
  .difficulty-easy {
    background-color: #52c41a;
  }
  
  .difficulty-medium {
    background-color: #faad14;
  }
  
  .difficulty-hard {
    background-color: #ff4d4f;
  }
  
  .question-tag-type {
    background-color: #f0f0f0;
    color: #666;
  }
  
  .question-meta {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: #999;
  }
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .question-content {
    color: #666;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 16px;
    padding-left: 34px;
  }
  
  .question-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-left: 34px;
  }
  
  .question-skills {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .skills-label {
    font-size: 13px;
    color: #999;
  }
  
  .skill-tag {
    padding: 2px 8px;
    background: #f0f7ff;
    border-radius: 12px;
    font-size: 12px;
    color: #1890ff;
  }
  
  .more-skills {
    font-size: 12px;
    color: #999;
  }
  
  .question-actions {
    display: flex;
    gap: 8px;
  }
  
  .preview-btn {
    padding: 4px 12px;
    background: white;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    color: #666;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    transition: all 0.3s ease;
  }
  
  .preview-btn:hover {
    border-color: #1890ff;
    color: #1890ff;
  }
  
  /* 分页 */
  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    padding: 20px;
    border-top: 2px solid #f0f0f0;
  }
  
  .page-button {
    padding: 8px 16px;
    background: white;
    border: 2px solid #e8e8e8;
    border-radius: 6px;
    color: #666;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .page-button:hover:not(:disabled) {
    border-color: #1890ff;
    color: #1890ff;
  }
  
  .page-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .page-info {
    font-size: 14px;
    color: #666;
  }
  
  /* 已选题目 */
  .selected-section {
    background: linear-gradient(135deg, rgba(24, 144, 255, 0.05) 0%, rgba(24, 144, 255, 0.02) 100%);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
    border: 2px solid #e6f7ff;
  }
  
  .selected-section .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .clear-selection {
    padding: 6px 16px;
    background: white;
    border: 2px solid #ffa39e;
    border-radius: 6px;
    color: #ff4d4f;
    font-size: 13px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.3s ease;
  }
  
  .clear-selection:hover {
    background: #fff2f0;
    transform: translateY(-1px);
  }
  
  .selected-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 300px;
    overflow-y: auto;
  }
  
  .selected-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: white;
    border-radius: 8px;
    border: 2px solid #f0f0f0;
    transition: all 0.3s ease;
  }
  
  .selected-item:hover {
    border-color: #1890ff;
    transform: translateX(4px);
  }
  
  .selected-item-content {
    flex: 1;
  }
  
  .selected-item-title {
    font-weight: 500;
    color: #333;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .item-index {
    color: #1890ff;
    font-weight: 600;
    font-size: 14px;
  }
  
  .selected-item-meta {
    display: flex;
    gap: 8px;
  }
  
  .meta-badge {
    padding: 2px 8px;
    background: #f5f5f5;
    border-radius: 12px;
    font-size: 11px;
    color: #666;
  }
  
  .difficulty-badge.difficulty-easy {
    background: #f6ffed;
    color: #52c41a;
  }
  
  .difficulty-badge.difficulty-medium {
    background: #fff7e6;
    color: #faad14;
  }
  
  .difficulty-badge.difficulty-hard {
    background: #fff2f0;
    color: #ff4d4f;
  }
  
  .remove-btn {
    width: 28px;
    height: 28px;
    background: #fff2f0;
    border: none;
    border-radius: 50%;
    color: #ff4d4f;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }
  
  .remove-btn:hover {
    background: #ffccc7;
    transform: scale(1.1);
  }
  
  /* 操作按钮 */
  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 16px;
    padding-top: 32px;
    border-top: 2px solid #f5f5f5;
  }
  
  .action-btn {
    padding: 14px 32px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
  }
  
  .action-btn-primary {
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  }
  
  .action-btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(24, 144, 255, 0.4);
  }
  
  .action-btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
  }
  
  .action-btn-secondary {
    background: white;
    border: 2px solid #e8e8e8;
    color: #666;
  }
  
  .action-btn-secondary:hover {
    border-color: #1890ff;
    color: #1890ff;
    transform: translateY(-2px);
  }
  
  .action-btn-cancel {
    background: white;
    border: 2px solid #ffccc7;
    color: #ff4d4f;
  }
  
  .action-btn-cancel:hover {
    background: #fff2f0;
    transform: translateY(-2px);
  }
  
  .btn-icon {
    font-size: 18px;
  }
  
  /* 模态框 */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    border-radius: 16px;
    width: 90%;
    max-width: 700px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  }
  
  .modal-header {
    padding: 24px;
    border-bottom: 2px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .modal-header h3 {
    margin: 0;
    color: #1a1a1a;
    font-size: 20px;
    font-weight: 600;
  }
  
  .modal-close {
    background: none;
    border: none;
    font-size: 24px;
    color: #999;
    cursor: pointer;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.3s ease;
  }
  
  .modal-close:hover {
    background: #f5f5f5;
    color: #ff4d4f;
  }
  
  .modal-body {
    padding: 24px;
    overflow-y: auto;
  }
  
  .preview-content h4 {
    margin-top: 0;
    color: #1a1a1a;
    font-size: 18px;
    margin-bottom: 16px;
  }
  
  .preview-meta {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
  }
  
  .preview-tag {
    padding: 4px 12px;
    background: #f5f5f5;
    border-radius: 16px;
    font-size: 12px;
    color: #666;
  }
  
  .preview-tag.difficulty-easy {
    background: #f6ffed;
    color: #52c41a;
  }
  
  .preview-tag.difficulty-medium {
    background: #fff7e6;
    color: #faad14;
  }
  
  .preview-tag.difficulty-hard {
    background: #fff2f0;
    color: #ff4d4f;
  }
  
  .preview-description h5,
  .preview-skills h5 {
    color: #333;
    font-size: 16px;
    margin-bottom: 12px;
  }
  
  .preview-description p {
    color: #666;
    line-height: 1.8;
    margin: 0;
    white-space: pre-wrap;
  }
  
  .skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .skill-badge {
    padding: 4px 12px;
    background: #f0f7ff;
    border-radius: 16px;
    font-size: 13px;
    color: #1890ff;
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .assignment-container {
      padding: 16px;
    }
    
    .form-grid {
      grid-template-columns: 1fr;
    }
    
    .question-filter {
      padding: 16px;
    }
    
    .filter-group {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .action-buttons {
      flex-direction: column;
    }
    
    .assignment-card {
      padding: 20px;
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
  </style>