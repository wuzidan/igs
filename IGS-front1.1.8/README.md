# 智能导学系统 - 前端项目

## 项目简介
智能导学系统是一个面向计算机编程技能学习的智能辅导平台，旨在帮助学生更好地掌握编程知识和技能。本项目为系统的前端部分，采用现代Web技术栈开发，提供友好的用户界面和丰富的学习功能。

## 技术栈
- **框架**: Vue 3 (Composition API)
- **路由**: Vue Router
- **构建工具**: Vite
- **语言**: TypeScript, JavaScript
- **样式**: CSS (Scoped Style)
- **状态管理**: 暂未指定 

## 项目结构
```
IGS-front1.1.8/
├── .gitignore                 # Git忽略文件
├── README.md                  # 项目说明文档
├── dist/                      # 构建输出目录
├── index.html                 # 项目入口HTML文件
├── package-lock.json          # npm依赖锁文件
├── package.json               # npm依赖配置文件
├── src/                       # 源代码目录
│   ├── App.vue                # 根组件
│   ├── api/                   # API接口相关
│   │   ├── index.js           # API请求封装
│   │   └── path.js            # API路径定义
│   ├── components/            # 自定义组件
│   │   ├── AppSidebar.vue     # 侧边栏组件
│   │   ├── KnowledgeStatus/   # 知识状态相关组件
│   │   ├── LogRelated/        # 日志相关组件
│   │   ├── QuizRelated/       # 答题相关组件
│   │   ├── Teacher/           # 教师相关组件
│   │   ├── Student/           # 学生相关组件
│   │   ├── UserInfo/          # 用户信息相关组件
│   │   ├── app_aigroup.json   # 应用分组配置
│   │   ├── icons/             # 图标组件
│   │   ├── index.vue          # 索引组件
│   │   └── lyq.vue            # 自定义组件
│   ├── main.ts                # 项目入口文件
│   ├── router/                # 路由配置
│   │   └── index.ts           # 路由定义
│   ├── shims-vue.d.ts         # Vue类型声明
│   └── utils/                 # 工具函数
│       └── request.js         # 请求工具函数
├── tsconfig.app.json          # TypeScript应用配置
├── tsconfig.json              # TypeScript全局配置
├── tsconfig.node.json         # TypeScript节点配置
└── vite.config.ts             # Vite构建配置
```

## 功能模块

### 1. 学生端功能
- **答题模块** (`QuizRelated`)
  - 题库浏览和搜索
  - 在线答题练习
  - 作答历史记录查看
  - 答题详情和解析

- **知识状态模块** (`KnowledgeStatus`)
  - 学习状态可视化展示
  - 知识结构分析
  - 学习进度追踪
  - 知识点掌握程度评估

- **知识图谱**
  - 知识体系结构展示
  - 知识点关联关系可视化
  - 个性化学习路径推荐

- **个人中心**
  - 个人信息管理
  - 学习数据统计
  - 学习成就展示

### 2. 教师端功能
- **习题管理**
  - 创建和编辑习题
  - 题库管理
  - 习题分类和标签管理
  - 查看学生作答情况

- **学习分析**
  - 学生学习数据统计
  - 多维度学习报告生成
  - 学生学习薄弱环节定位
  - 班级整体学习情况分析

- **智能推荐**
  - 基于学生学习数据的个性化推荐
  - 学习路径优化建议

## 协作指南
1. **代码规范**
   - 组件逻辑使用JavaScript/TypeScript编写
   - 遵循Vue 3 Composition API风格
   - 组件样式使用scoped属性隔离
   - 提交代码前确保代码格式化
   - API调用统一封装在`api/`目录下
   - 工具函数统一放在`utils/`目录下

2. **开发流程**
   - 新功能开发前创建分支
   - 代码提交前进行本地测试
   - 提交PR前确保代码无冲突
   - 代码审核通过后合并到主分支

## 注意事项
1. 请不要将敏感信息（如API密钥）提交到代码仓库
2. 保持代码简洁、可维护，添加必要注释
3. 新功能开发前请先讨论方案
4. 遇到问题及时沟通，避免长时间卡壳
5. 定期更新本地代码，避免冲突
6. 组件命名采用驼峰命名法，文件命名采用kebab-case
7. API接口调用统一使用`src/utils/request.js`封装的请求工具
8. 所有API路径配置统一放在`src/api/path.js`中

## 项目设置

```sh
# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

## 使用说明
1. 确保已安装Node.js 16+和npm 8+
2. 克隆项目到本地
3. 安装项目依赖：`npm install`
4. 运行开发服务器：`npm run dev`
5. 在浏览器中访问 http://localhost:3000 (默认端口)

## 与后端和模型集成说明

### 1. 后端API配置
- API基础地址配置在`src/api/path.js`中的`baseURL`变量
- 开发环境下默认为`http://localhost:8000`
- 如需修改，请确保与后端服务地址保持一致

### 2. 请求工具使用
- 所有API请求请使用`src/utils/request.js`中封装的请求工具
- 该工具已实现请求拦截器和响应拦截器，处理了常见的错误情况
- 支持请求参数格式化和响应数据统一处理

### 3. 模型集成接口
- 模型预测API地址：`/model/predict/`
- 请求方式：POST
- 请求参数：`{ interactions: [...] }`（学生答题交互数据）
- 返回数据：包含诊断结果和学习推荐

## 版本信息
- 当前版本：1.1.8
- 主要更新：
  - 优化了学生端和教师端的用户界面
  - 增强了知识状态可视化功能
  - 完善了智能推荐系统
  - 改进了API请求处理机制
  - 更新了依赖包版本

## 浏览器兼容性
- Chrome 90+ (推荐)
- Firefox 88+ 
- Safari 14+ 
- Edge 90+

## 开发工具推荐
- Visual Studio Code
- Vue Language Features (Volar)
- TypeScript Vue Plugin (Volar)
- ESLint
- Prettier

```
