from rest_framework import serializers
from .models import Teacher, Subject


# 教学科目序列化器（嵌套在教师信息中）
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']  # 前端只需科目ID和名称


# 教师个人信息序列化器（对齐前端所有字段）
class SubjectsField(serializers.Field):
    def to_representation(self, value):
        try:
            return [s.name for s in value.all()]
        except Exception:
            return []

    def to_internal_value(self, data):
        if data is None:
            return []
        if not isinstance(data, list):
            raise serializers.ValidationError("subjects必须是数组")

        subjects = []
        for item in data:
            if item is None:
                continue
            if isinstance(item, int) or (isinstance(item, str) and item.isdigit()):
                try:
                    subjects.append(Subject.objects.get(pk=int(item)))
                except Subject.DoesNotExist:
                    raise serializers.ValidationError(f"科目不存在: {item}")
            else:
                name = str(item).strip()
                if not name:
                    continue
                subject, _ = Subject.objects.get_or_create(name=name)
                subjects.append(subject)
        return subjects


class TeacherProfileSerializer(serializers.ModelSerializer):

    # 从User模型关联的字段（前端对应：teacherName、email、phone、avatarUrl）
    teacherName = serializers.CharField(source='user.first_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone = serializers.CharField(source='user.phone', required=False)
    avatarUrl = serializers.SerializerMethodField(read_only=True)  # 头像URL

    # 教师专属字段（前端对应：teacherId、title、department等）
    teacherId = serializers.CharField(source='teacher_id', read_only=True)  # 工号不可修改
    birthDate = serializers.DateField(source='birth_date', required=False)
    hometown = serializers.CharField(required=False)
    politicalStatus = serializers.CharField(source='political_status', required=False)
    bio = serializers.CharField(required=False)
    officeAddress = serializers.CharField(source='office_address', required=False)

    # 多对多教学科目（前端对应subjects列表，接收ID列表，返回名称列表）
    subjects = SubjectsField(required=False)
    subjectsName = SubjectSerializer(source='subjects', many=True, read_only=True)  # 前端展示用名称列表

    class Meta:
        model = Teacher
        fields = [
            # User关联字段
            'teacherName', 'email', 'phone', 'avatarUrl',
            # Teacher专属字段
            'teacherId', 'title', 'department', 'officeAddress',
            'birthDate', 'hometown', 'politicalStatus', 'bio',
            # 教学科目
            'subjects', 'subjectsName'
        ]

    # 自定义获取头像URL（对应前端avatarUrl）
    def get_avatarUrl(self, obj):
        user = obj.user
        if hasattr(user, "user_avatar_url"):
            return user.user_avatar_url or ""
        return getattr(user, "avatar_url", "") or ""

    # 重写update方法：同时更新Teacher和关联的User模型字段
    def update(self, instance, validated_data):
        # 1. 提取User模型的字段（如teacherName、email、phone）
        user_data = validated_data.pop('user', {})
        subjects = validated_data.pop('subjects', None)
        if user_data:
            # 更新User模型
            user_instance = instance.user
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
            user_instance.save()

        # 2. 更新Teacher模型剩余字段（如birth_date、subjects）
        instance = super().update(instance, validated_data)
        if subjects is not None:
            instance.subjects.set(subjects)
        return instance