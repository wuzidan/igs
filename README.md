# 智能导学系统（Intelligent Guidance System）

## 项目概述
智能导学系统是一个面向计算机编程技能学习的智能辅导平台，旨在帮助学生更好地掌握编程知识和技能。系统通过知识追踪模型（AAKT）分析学生的学习数据，提供个性化的学习推荐和诊断报告。

## 项目架构
本项目采用前后端分离的架构设计，由三个主要部分组成：

1. **AAKT-main**: 知识追踪模型实现，用于分析学生学习数据，预测学习状态
2. **IGS-back-end**: Django后端服务，提供API接口和业务逻辑处理
3. **IGS-front1.1.8**: Vue 3前端应用，提供用户界面和交互功能

## 项目结构
```
IGS/
├── AAKT-main/           # 知识追踪模型
├── IGS-back-end/        # Django后端项目
└── IGS-front1.1.8/      # Vue 3前端项目
```

## 各模块详细介绍

### 1. AAKT-main（知识追踪模型）

AAKT (Alternate Autoregressive Knowledge Tracing) 是一个用于学生知识状态建模的深度学习模型，基于论文《AAKT: Enhancing Knowledge Tracing with Alternate Autoregressive Modeling》实现。

**主要功能：**
- 基于学生的历史答题数据，动态追踪和预测学生对各个知识点的掌握程度
- 支持多标签学习，可同时评估学生对多个知识点的理解情况
- 提供预测和诊断功能，为学生提供个性化学习建议

**核心文件：**
- `models/AAKT.py`: 模型架构实现
- `aakt_entry.py`: 模型训练和评估入口
- `app.py`: 模型应用接口封装
- `run.py`: 模型运行脚本

**详细说明请参考**：[AAKT-main/README.md](AAKT-main/README.md)

### 2. IGS-back-end（Django后端）

Django后端服务提供API接口和业务逻辑处理，连接前端和模型，实现完整的业务流程。

**技术栈：**
- **框架**: Django 5.1.7
- **API框架**: Django REST Framework
- **数据库**: MySQL
- **跨域处理**: django-cors-headers

**项目结构：**
```
IGS-back-end/
├── ITS_project/              # 项目配置目录
│   ├── settings.py           # 项目全局配置
│   └── urls.py               # 主路由配置
├── student/                  # 学生管理模块
├── question/                 # 题目管理模块
├── historyRecord/            # 答题记录模块
├── knowledge/                # 知识点管理模块
├── visualization/            # 数据可视化模块
├── model_integration/        # 模型集成模块
└── manage.py                 # Django管理脚本
```

**主要功能模块：**
- **student**: 学生信息管理、认证授权
- **question**: 题目管理、题库维护
- **historyRecord**: 学生答题记录、学习行为分析
- **knowledge**: 知识点体系管理、知识图谱构建
- **visualization**: 学习数据可视化、报表生成
- **model_integration**: AAKT模型集成、预测API提供

**开发指南：**
1. 确保安装了Python 3.10+和pip
2. 安装依赖：`pip install -r requirements.txt`
3. 运行开发服务器：`python manage.py runserver`
4. 默认访问地址：http://localhost:8000

### 3. IGS-front1.1.8（Vue 3前端）

Vue 3前端应用提供用户界面和交互功能，为学生和教师提供不同的功能体验。

**技术栈：**
- **框架**: Vue 3 (Composition API)
- **路由**: Vue Router
- **构建工具**: Vite
- **语言**: TypeScript, JavaScript
- **样式**: CSS (Scoped Style)

**项目结构：**
```
IGS-front1.1.8/
├── src/                       # 源代码目录
│   ├── api/                   # API接口相关
│   ├── components/            # 自定义组件
│   ├── router/                # 路由配置
│   └── utils/                 # 工具函数
├── package.json               # npm依赖配置文件
└── vite.config.ts             # Vite构建配置
```

**主要功能模块：**
- **学生端**: 答题练习、学习进度追踪、知识状态查看、个性化推荐
- **教师端**: 习题管理、学习分析、班级管理
- **公共功能**: 用户认证、数据可视化、学习记录查看

**开发指南：**
1. 确保安装了Node.js 16+和npm
2. 安装依赖：`npm install`
3. 运行开发服务器：`npm run dev`
4. 构建生产版本：`npm run build`
5. 默认访问地址：http://localhost:3000

**详细说明请参考**：[IGS-front1.1.8/README.md](IGS-front1.1.8/README.md)

## 系统整合流程

### 前端与后端连接
1. 前端通过axios请求后端API接口
2. 所有API路径定义在`src/api/path.js`中
3. 请求封装和拦截器在`src/utils/request.js`中实现
4. 后端配置了CORS支持跨域请求

### 后端与模型集成
1. 后端通过`model_integration`应用集成AAKT模型
2. 模型路径使用相对路径配置，确保可移植性
3. 提供`/model/predict/`API接口供前端调用
4. 实现了模型的懒加载和缓存机制，提高性能

### 数据流流程
1. 学生在前端进行答题操作
2. 前端将答题数据发送到后端API
3. 后端保存答题记录并调用AAKT模型进行预测
4. 模型返回预测结果（知识点掌握程度等）
5. 后端处理预测结果并返回给前端
6. 前端展示诊断报告和学习推荐

## 协作指南

### 分支管理
- `main`: 主分支，保持稳定版本
- `develop`: 开发分支，日常开发工作在此分支进行
- 功能分支: 新功能开发创建单独的功能分支，完成后合并到develop

### 代码规范
- **前端**: 遵循Vue 3 Composition API风格，组件命名采用驼峰命名法，文件命名采用kebab-case
- **后端**: 遵循Django项目结构规范，视图函数使用REST Framework风格
- **模型**: 遵循Python代码规范，保持模型接口的一致性

### 提交规范
- 提交信息清晰明了，说明修改内容和原因
- 提交前确保代码通过本地测试
- 避免提交敏感信息（如API密钥、数据库密码等）

### 环境配置
- 前端开发环境：Node.js 16+, npm 8+
- 后端开发环境：Python 3.10+, pip 22+
- 数据库：MySQL 8.0+
- 可选：GPU环境（用于加速模型训练和推理）

## 部署指南

### 开发环境部署
1. 克隆项目代码到本地
2. 分别配置前端、后端和模型环境
3. 启动后端服务：`python manage.py runserver`
4. 启动前端服务：`npm run dev`
5. 确保模型文件和映射文件路径正确

### 生产环境部署（简化版）
1. 后端：使用Gunicorn/uWSGI + Nginx部署Django应用
2. 前端：构建静态文件，使用Nginx提供服务
3. 数据库：配置独立的MySQL服务器
4. 模型：确保模型文件正确部署，路径配置正确

## 注意事项
1. 请不要将敏感信息（如数据库密码、API密钥等）提交到代码仓库
2. 定期更新依赖包，确保系统安全和稳定性
3. 遇到问题及时沟通，避免长时间卡壳
4. 新功能开发前请先讨论方案，确保技术路线一致
5. 保持代码简洁、可维护，添加必要的注释

## 附录

### API文档
后端API文档可通过访问`http://localhost:8000/swagger/`查看（需安装并配置drf-yasg）

### 常见问题解决
1. **跨域问题**: 确保后端正确配置了CORS_ORIGIN_WHITELIST
2. **数据库连接问题**: 检查settings.py中的数据库配置是否正确
3. **模型加载失败**: 检查模型文件路径和权限设置
4. **前端请求错误**: 检查API路径和请求参数是否正确


---
**版本**: 1.0.0