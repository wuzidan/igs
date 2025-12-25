# notification/api/serializers.py
from rest_framework import serializers
from .models import Notification
from student.serializers import StudentDetailSerializer  # 学生基础序列化器（需提前创建）
from question.serializers import ExerciseListSerializer  # 习题列表序列化器

# 嵌套序列化器：通知详情（对应前端details字段）
class NotificationDetailsSerializer(serializers.Serializer):
    studentName = serializers.CharField(source='student.user.first_name', read_only=True)
    studentId = serializers.CharField(source='student.student_id', read_only=True)
    exerciseName = serializers.CharField(source='exercise.title', read_only=True)
    exerciseId = serializers.CharField(source='exercise.id', read_only=True)  # 前端用字符串ID
    submissionTime = serializers.DateTimeField(source='submission_time', format='%Y-%m-%dT%H:%M:%S', read_only=True)
    totalQuestions = serializers.IntegerField(source='practice_record.total_questions', read_only=True)  # 从练习记录获取
    attemptedQuestions = serializers.IntegerField(source='practice_record.attempted_questions', read_only=True)

# 通知主序列化器（前端列表/详情通用）
class NotificationSerializer(serializers.ModelSerializer):
    # 基础字段映射（对齐前端）
    type = serializers.ChoiceField(choices=Notification.NotificationType.choices, read_only=True)
    time = serializers.DateTimeField(source='created_at', format='%Y-%m-%dT%H:%M:%S', read_only=True)
    read = serializers.BooleanField(source='is_read', read_only=True)
    # 嵌套详情字段（前端details）
    details = NotificationDetailsSerializer(source='*', read_only=True)  # source='*'表示用当前模型数据

    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'content', 'time', 'read', 'details']
        read_only_fields = ['id', 'recipient', 'created_at']  # 接收者和创建时间不可修改

# 标记已读序列化器（仅更新is_read字段）
class NotificationMarkReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']  # 仅允许更新“是否已读”
        extra_kwargs = {
            'is_read': {'write_only': True, 'default': True}  # 默认为标记已读
        }