# user/api/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

# 1. 基础序列化器（列表/详情，不暴露敏感字段）
class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "email", "role",
            "avatar_url", "phone", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "username", "created_at", "updated_at"]  # 不可修改字段

# 2. 创建用户序列化器（管理员创建用户时用，需处理密码）
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "username", "password", "email", "first_name", "role",
            "avatar_url", "phone"
        ]

    def create(self, validated_data):
        # 明文存储密码
        return super().create(validated_data)

# 3. 更新用户序列化器（修改基础资料，不允许改密码）
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "email", "avatar_url", "phone"]  # 仅允许修改这些字段

# 4. 登录序列化器（对接DRF登录接口）
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # 尝试通过用户名或邮箱查找用户
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                raise serializers.ValidationError('用户名或密码错误')

        # 验证密码（明文比较）
        # 直接从数据库中获取密码字段，避免使用 AbstractUser 的 password 属性
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM user_user WHERE id = %s", [user.id])
            db_password = cursor.fetchone()[0]

        if db_password != password:
            raise serializers.ValidationError('用户名或密码错误')

        # 验证用户是否激活
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')

        attrs['user'] = user
        return attrs