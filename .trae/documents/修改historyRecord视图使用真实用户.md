### 修改historyRecord视图使用真实用户

**问题分析**：
当前historyRecord视图中使用了测试用户覆盖代码，优先使用testuser或ID为1的用户，这不符合生产环境需求。需要改为使用真实登录的用户，通过request.user获取当前用户。

**修改方案**：
1. **移除测试用户覆盖代码**：删除views.py中第19-31行的测试用户自动切换逻辑
2. **保留用户记录获取逻辑**：继续使用request.user获取用户的练习记录和历史记录
3. **确保关联关系正确**：系统已通过外键正确关联HistoryRecord和User模型

**代码修改**：
```python
# 修改前（第16-38行）
def get(self, request):
    # 获取当前用户的所有作答记录
    # 调试专用：优先使用testuser用户
    User = get_user_model()
    try:
        # 优先尝试使用testuser用户
        test_user = User.objects.get(username='testuser')
        request.user = test_user  # 覆盖匿名用户
        print(f"使用测试用户: {test_user.username} (ID: {test_user.id})")
    except User.DoesNotExist:
        try:
            # 如果testuser不存在，尝试使用ID=1的用户
            test_user = User.objects.get(id=1)
            request.user = test_user
            print(f"使用ID=1的用户: {test_user.username}")
        except User.DoesNotExist:
            return Response({"error": "测试用户不存在"}, status=400)

    # 获取用户的练习记录和历史记录
    practice_records = request.user.practice_records.all()
    history_records_model = request.user.history_records.all()
    
    print(f"找到 {practice_records.count()} 条练习记录")
    print(f"找到 {history_records_model.count()} 条历史记录")

# 修改后
def get(self, request):
    # 获取当前登录用户的所有作答记录
    User = get_user_model()
    
    # 直接使用request.user获取当前登录用户
    if not request.user.is_authenticated:
        return Response({"error": "用户未登录"}, status=401)
    
    # 获取用户的练习记录和历史记录
    practice_records = request.user.practice_records.all()
    history_records_model = request.user.history_records.all()
    
    print(f"使用真实用户: {request.user.username} (ID: {request.user.id})")
    print(f"找到 {practice_records.count()} 条练习记录")
    print(f"找到 {history_records_model.count()} 条历史记录")
```

**关联关系说明**：
- HistoryRecord模型通过`user`外键字段关联到User模型
- User模型在student/models.py中定义，包含`student_id`字段作为学生唯一标识符
- 数据库中historyrecord_historyrecord表的`user_id`字段关联到student_user表的`id`字段
- 系统已正确配置AUTH_USER_MODEL，使用student.User作为自定义用户模型

**修改文件**：
- `c:\Users\吴紫丹\Desktop\IGS\IGS-back-end\historyRecord\views.py`

**预期效果**：
- 移除测试用户覆盖，使用真实登录用户
- API返回当前登录用户的作答记录和统计数据
- 保留调试信息输出，方便开发人员追踪
- 提高API的安全性，确保只有登录用户才能访问自己的数据