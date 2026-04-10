# 图谱管理模块故障排除指南

## 问题：创建图谱时出现 IntegrityError

### 症状
在教师端创建知识图谱时，浏览器弹出错误信息显示 HTML 格式的 Django 错误页面。

### 根本原因
1. **数据库缺少默认领域数据**：`GraphDomain` 表中没有预设的知识领域
2. **外键约束失败**：创建图谱时引用的 `domainId` 在数据库中不存在
3. **错误处理不当**：后端返回 HTML 错误页面而非 JSON 格式

### 解决方案

#### 方法一：运行数据迁移（推荐）

1. 激活虚拟环境（如果有）
2. 运行迁移命令：

```bash
cd IGS-back-end
python manage.py migrate graphs
```

这将自动执行 `0002_add_default_domains.py` 迁移，创建默认的知识领域。

#### 方法二：使用管理命令初始化

如果迁移已经运行过但数据丢失，使用以下命令重新初始化：

```bash
cd IGS-back-end
python manage.py init_graph_domains
```

#### 方法三：手动添加领域数据

通过 Django Admin 或数据库工具手动添加以下领域：

- C/C++ 编程
- Python 编程
- Web 前端开发
- 数据结构与算法
- 机器学习
- 数据库技术
- 云计算与容器
- 移动应用开发
- 测试技术
- 其他编程技术

### 验证修复

1. 访问 `/teacher/graphs/create` 页面
2. 检查"知识领域"下拉框是否有选项
3. 填写表单并尝试创建图谱
4. 如果仍有问题，检查后端日志输出

### 代码改进

本次修复包含以下改进：

1. **后端错误处理**（`graphs/views.py`）：
   - 捕获 `IntegrityError` 并返回友好的 JSON 错误信息
   - 添加详细的日志记录便于调试
   - 区分不同类型的完整性错误

2. **前端错误显示**（`CreateGraph.vue`）：
   - 正确解析后端返回的 JSON 错误
   - 显示具体的错误信息而非通用错误

3. **管理命令**（`init_graph_domains.py`）：
   - 提供便捷的领域数据初始化工具
   - 支持幂等操作，可重复运行

### 预防措施

1. 确保在部署时运行所有数据迁移
2. 在测试环境中验证领域数据是否存在
3. 定期备份数据库
4. 监控后端日志以发现潜在问题

### 相关文件

- `graphs/models.py` - 数据模型定义
- `graphs/views.py` - API 视图和错误处理
- `graphs/serializers.py` - 数据序列化
- `graphs/migrations/0002_add_default_domains.py` - 默认数据迁移
- `graphs/management/commands/init_graph_domains.py` - 初始化命令
