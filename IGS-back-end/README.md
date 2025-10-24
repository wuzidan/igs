# IGS-back-end - 智能导学系统后端

## 项目概述
IGS-back-end是智能导学系统( Intelligent Tutoring System )的后端服务，基于Django框架开发，提供全面的学习管理、数据分析和智能推荐功能。该系统旨在帮助教师和学生进行个性化学习和教学管理。

## 技术栈

- **框架**: Django 5.1.7
- **API框架**: Django REST Framework
- **数据库**: MySQL 5.7+
- **开发语言**: Python 3.8+
- **跨域支持**: django-cors-headers
- **身份认证**: Django内置认证系统+自定义用户模型

## 项目结构

```
IGS-back-end/
├── .idea/                # IDE配置文件
├── .venv/                # Python虚拟环境
├── ITS_project/          # 项目主配置目录
│   ├── settings.py       # 项目全局设置
│   ├── urls.py           # 主URL配置
│   └── wsgi.py           # WSGI接口配置
├── app01/                # 基础应用
├── db.sqlite3            # SQLite测试数据库（开发环境）
├── djangoProject/        # Django项目相关文件
├── fixtures/             # 测试数据JSON文件
├── graphdemo/            # 图表演示相关
├── historyRecord/        # 学习历史记录管理
├── knowledge/            # 知识点管理
├── manage.py             # Django管理脚本
├── model_integration/    # AI/ML模型集成
├── question/             # 题目与练习管理
├── student/              # 用户（学生）管理
├── test_knowledge_structure.py # 知识结构API测试脚本
├── test_visualization_api.py   # 可视化数据API测试脚本
├── test_visualization_stats.py # 可视化统计数据测试脚本
└── visualization/        # 数据可视化模块
```

## 核心应用模块

### 1. student（用户管理模块）
**主要功能**: 用户信息管理、身份认证、个人资料维护

**关键模型**: 
- `User`: 扩展Django的AbstractUser，包含学号、班级、专业等学生特有信息

**API端点**: 
- `/student/studentInfo/`: 获取和更新用户个人信息

### 2. question（题目管理模块）
**主要功能**: 题目类型管理、难度级别划分、练习记录存储

**关键模型**: 
- `Question`: 题目内容、类型、难度等信息
- `PracticeRecord`: 用户练习记录、得分、时长
- `QuestionType`: 题目类型枚举（单选、多选、判断、简答）
- `DifficultyLevel`: 难度级别枚举（简单、中等、困难）

**API端点**: 
- `/question/question/`: 题目相关数据接口

### 3. historyRecord（历史记录模块）
**主要功能**: 用户学习历史记录、统计分析、学习进度跟踪

**关键模型**: 
- `HistoryRecord`: 作答记录主表
- `UserStatistics`: 用户统计数据（总练习次数、平均得分、正确率等）

**API端点**: 
- `/historyRecord/getHistoryRecord/`: 获取用户学习历史记录

### 4. knowledge（知识点管理模块）
**主要功能**: 知识点分类、掌握程度评估、学习推荐基础

**关键模型**: 
- `KnowledgePoint`: 知识点名称、分类、掌握程度、练习次数等

**分类选项**: 
- 核心知识点(core)
- 基础知识点(basic)
- 高级知识点(advanced)
- 扩展知识点(extended)

### 5. visualization（数据可视化模块）
**主要功能**: 学习数据可视化、课程进度跟踪、技能图谱展示

**关键模型**: 
- `CourseProgress`: 用户课程学习进度
- `ProgrammingSkill`: 用户编程技能掌握程度

### 6. model_integration（模型集成模块）
**主要功能**: 集成AI/ML模型进行学习预测、个性化推荐

**API端点**: 
- `/model/predict/`: 调用预测模型接口

## 数据库配置
项目使用MySQL数据库，配置信息位于`ITS_project/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'igs',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

## 跨域配置
系统已配置CORS支持，允许以下源的请求：
- http://localhost:8000
- http://127.0.0.1:5174
- http://127.0.0.1:8000
- http://127.0.0.1:5173 (Vue3开发环境默认端口)
- http://localhost:5173

## 开发环境设置

### 1. 克隆项目并进入目录
```bash
git clone <项目地址>
cd IGS-back-end
```

### 2. 创建并激活虚拟环境
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt  # 若文件不存在，可手动安装主要依赖
pip install django djangorestframework mysqlclient django-cors-headers
```

### 4. 配置数据库
确保MySQL已安装并运行，创建名为`igs`的数据库，并更新`settings.py`中的数据库配置

### 5. 执行数据库迁移
```bash
python manage.py migrate
```

### 6. 创建超级用户
```bash
python create_admin_simple.py  # 使用提供的脚本或Django自带命令
# 或使用标准命令
python manage.py createsuperuser
```

### 7. 启动开发服务器
```bash
python manage.py runserver
```

服务器将在 http://127.0.0.1:8000 启动

## API使用指南

### 学生信息管理
- **获取个人信息**: GET `/student/studentInfo/`
- **更新个人信息**: PUT `/student/studentInfo/`

### 历史记录管理
- **获取历史记录**: GET `/historyRecord/getHistoryRecord/`

### 题目管理
- **获取题目数据**: GET `/question/question/`

### 知识点管理
- **获取知识结构**: GET `/knowledge/structure/`

### 数据可视化
- **获取可视化数据**: GET `/visualization/display/`

### 模型预测
- **调用预测模型**: GET/POST `/model/predict/`

## 测试脚本说明

### 1. test_knowledge_structure.py
**用途**: 测试知识结构API接口的响应数据
**功能**: 
- 验证知识点覆盖率数据
- 检查已掌握知识点数量和总体掌握程度
- 打印所有知识点的名称、分类和掌握度信息
**使用方法**: `python test_knowledge_structure.py`

### 2. test_visualization_api.py
**用途**: 测试可视化数据API接口的完整响应
**功能**:
- 验证学习进度数据（整体进度、已完成课程、平均得分）
- 检查答题统计（正确率、总题数）
- 显示知识掌握度详情和学习时长统计
**使用方法**: `python test_visualization_api.py`

### 3. test_visualization_stats.py
**用途**: 测试可视化数据API的统计功能
**功能**:
- 验证答题统计数据的准确性
- 打印完整的API响应数据（格式化输出）
**使用方法**: `python test_visualization_stats.py`

**注意事项**: 运行测试脚本前，请确保开发服务器已启动（`python manage.py runserver`）

## 协作开发规范

1. **代码风格**: 遵循PEP 8 Python编码规范
2. **分支管理**: 
   - `main`: 主分支（生产环境）
   - `develop`: 开发分支
   - 功能开发创建特性分支，完成后合并到develop
3. **提交信息**: 清晰描述改动内容，格式：`[模块名] 简短描述`
4. **数据库迁移**: 模型变更后必须创建迁移文件并提交
5. **API设计**: 遵循RESTful设计原则

## 注意事项

1. 开发环境下`DEBUG = True`，生产环境必须设置为`False`
2. 生产环境需要修改`SECRET_KEY`为安全的随机字符串
3. 确保数据库配置信息安全，避免泄露敏感信息
4. 前后端协作时，确保前端请求的端口在`CORS_ALLOWED_ORIGINS`中配置

## 项目文档
- Django官方文档: https://docs.djangoproject.com/
- Django REST Framework文档: https://www.django-rest-framework.org/



## 团队协作联调指南

### 后端开发环境配置

1. **克隆项目仓库**
```bash
git clone <项目仓库地址>
cd IGS-back-end
```

2. **创建并激活虚拟环境**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **安装项目依赖**
```bash
pip install -r requirements.txt  # 如果文件不存在，执行下面的命令
pip install django djangorestframework mysqlclient django-cors-headers
```

4. **数据库配置**
   - 确保MySQL服务已安装并运行
   - 创建数据库：`CREATE DATABASE igs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
   - 更新 `ITS_project/settings.py` 中的数据库配置（用户名、密码）

5. **初始化数据库**
```bash
# 执行数据库迁移
python manage.py migrate

# 导入测试数据（可选）
python manage.py loaddata fixtures/users.json fixtures/questions.json fixtures/knowledge_points.json fixtures/practice_records.json
```

6. **启动后端服务**
```bash
python manage.py runserver
```
后端服务将在 http://127.0.0.1:8000 启动

### 前端开发环境配置

1. **进入前端项目目录**
```bash
cd ../IGS-front1.1.8
```

2. **安装依赖**
```bash
npm install
```

3. **启动开发服务器**
```bash
npm run dev
```
前端服务通常会在 http://localhost:5173 或 http://localhost:5174 启动

### 联调测试步骤

1. **验证后端API可用性**
   - 使用测试脚本验证API响应
   ```bash
   # 测试知识结构API
   python test_knowledge_structure.py
   
   # 测试可视化数据API
   python test_visualization_api.py
   ```

2. **前端访问测试**
   - 打开浏览器访问前端开发服务器地址
   - 检查页面是否能正常加载
   - 验证API调用是否成功（通过浏览器开发者工具的Network面板）

3. **常见联调问题排查**
   - **跨域问题**：确保后端CORS配置正确，已允许前端开发服务器地址
   - **API路径错误**：检查前端 `api/path.js` 中的路径配置
   - **数据库连接失败**：确认MySQL服务运行正常，配置信息正确
   - **数据缺失**：使用 `loaddata` 命令导入测试数据

### 协作规范

1. **代码提交前**
   - 确保所有测试脚本运行正常
   - 检查JSON格式是否正确（特别是fixtures目录下的文件）

2. **环境变量管理**
   - 敏感配置信息（如数据库密码）不要硬编码在代码中
   - 可以考虑使用环境变量或配置文件管理敏感信息

3. **测试数据更新**
   - 当数据库模型变更时，及时更新fixtures中的测试数据
   - 使用 `python manage.py dumpdata` 命令导出最新数据

---
最后更新: 2025-9-22