# class_info/api/serializers.py
from rest_framework import serializers

from student.models import User as StudentModel
from teacher.serializers import TeacherProfileSerializer

from .models import ClassInfo, ClassWeeklyProgress, KnowledgeMastery


class StudentListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name", read_only=True)
    studentId = serializers.CharField(source="student_id", read_only=True)
    joinTime = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = StudentModel
        fields = ["id", "name", "studentId", "phone", "email", "joinTime"]


class StudentDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name", read_only=True)
    studentId = serializers.CharField(source="student_id", read_only=True)
    joinTime = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = StudentModel
        fields = ["id", "name", "studentId", "email", "joinTime"]


# 1. 班级详情序列化器（含学生列表、班主任信息，给前端班级管理页用）
class ClassDetailSerializer(serializers.ModelSerializer):
    # 嵌套班主任信息（复用教师模块的基础序列化器）
    head_teacher_info = TeacherProfileSerializer(source="head_teacher", read_only=True)
    # 嵌套班级学生列表 - 使用 SerializerMethodField
    student_list = serializers.SerializerMethodField()
    # 动态学生数（直接调用模型的student_count属性）
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClassInfo
        fields = [
            "id", "name", "code", "course_name", "create_time",
            "head_teacher", "head_teacher_info",  # 班主任ID+详情
            "student_list", "student_count"  # 学生列表+数量
        ]
        read_only_fields = ["id", "create_time", "student_count"]  # 不可修改字段

    def get_student_list(self, obj):
        """获取班级学生列表"""
        try:
            students = StudentModel.objects.filter(class_info=obj)
            return StudentListSerializer(students, many=True).data
        except Exception as e:
            return []


# 2. 班级编辑序列化器（仅允许修改前端可编辑的字段）
class ClassUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInfo
        fields = ["name", "code", "course_name", "head_teacher"]  # 仅编辑班级基本信息+班主任


class ClassCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInfo
        fields = ["name", "code", "course_name", "head_teacher"]


# 3. 班级添加学生序列化器（前端添加学生到班级时用）
class ClassAddStudentSerializer(serializers.Serializer):
    # 接收学生基础信息（复用学生模块的字段逻辑，或直接引用学生序列化器）
    student_id = serializers.CharField(required=True, max_length=20)
    name = serializers.CharField(required=True, max_length=100)
    phone = serializers.CharField(required=False, max_length=20, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    # 验证：学号是否已存在（跨模块操作学生模型）
    def validate_student_id(self, value):
        from student.models import User as StudentModel  # 局部导入避免循环引用
        if StudentModel.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("该学号的学生已存在")
        return value


# 班级列表序列化器（用于前端classes下拉筛选）
class ClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInfo
        fields = ['id', 'name']  # 匹配前端classes的id和name字段


# 班级进度图表序列化器（匹配前端progressData格式）
class ClassProgressChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())  # 前端的labels数组（如["第1周",...]）
    datasets = serializers.ListField(
        child=serializers.DictField(
            child=serializers.Field(),
            allow_empty=False
        )
    )  # 前端的datasets数组（含label、data、borderColor等）

    # 从数据库查询并组装图表数据
    @classmethod
    def get_chart_data(cls):
        # 1. 生成labels（第1周到第12周）
        labels = [f"第{week}周" for week in range(1, 13)]

        # 2. 按班级分组查询周进度
        classes = ClassInfo.objects.all()
        datasets = []
        for cls_info in classes:
            # 获取该班级所有周的进度（按周次排序）
            progress_data = cls_info.weekly_progress.all().values_list('progress', flat=True)
            # 补充不足12周的数据（若有缺失，用0填充）
            progress_list = list(progress_data) + [0] * (12 - len(progress_data))
            # 组装datasets格式（匹配前端颜色，可扩展多颜色）
            color_map = {
                "编程基础班": "#3498db",
                "前端开发班": "#e74c3c",
                "后端开发班": "#2ecc71",
                "算法与数据结构班": "#9b59b6"
            }
            border_color = color_map.get(cls_info.name, "#95a5a6")
            datasets.append({
                "label": cls_info.name,
                "data": progress_list,
                "borderColor": border_color,
                "backgroundColor": f"rgba({border_color.lstrip('#')}, 0.1)",
                "tension": 0.3,
                "fill": True,
                "pointRadius": 4,
                "pointHoverRadius": 6
            })

        return {"labels": labels, "datasets": datasets}


# 知识点掌握度图表序列化器（匹配前端knowledgeData格式）
class KnowledgeChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(
        child=serializers.DictField(
            child=serializers.Field(),
            allow_empty=False
        )
    )

    # 从数据库查询并组装图表数据
    @classmethod
    def get_chart_data(cls):
        # 1. 获取所有知识点名称（按数据库存储顺序）
        knowledge_names = KnowledgeMastery.objects.values_list('knowledge_name', flat=True).distinct()
        labels = list(knowledge_names)

        # 2. 分别查询"整体掌握度"和"优秀学生掌握度"
        overall_data = KnowledgeMastery.objects.filter(
            mastery_type='OVERALL'
        ).order_by('knowledge_name').values_list('mastery_value', flat=True)
        excellent_data = KnowledgeMastery.objects.filter(
            mastery_type='EXCELLENT'
        ).order_by('knowledge_name').values_list('mastery_value', flat=True)

        # 3. 组装datasets
        datasets = [
            {
                "label": "整体掌握度",
                "data": list(overall_data),
                "backgroundColor": "rgba(52, 152, 219, 0.2)",
                "borderColor": "rgba(52, 152, 219, 1)",
                "pointBackgroundColor": "rgba(52, 152, 219, 1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(52, 152, 219, 1)",
                "borderWidth": 2
            },
            {
                "label": "优秀学生掌握度",
                "data": list(excellent_data),
                "backgroundColor": "rgba(46, 204, 113, 0.2)",
                "borderColor": "rgba(46, 204, 113, 1)",
                "pointBackgroundColor": "rgba(46, 204, 113, 1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(46, 204, 113, 1)",
                "borderWidth": 2
            }
        ]

        return {"labels": labels, "datasets": datasets}