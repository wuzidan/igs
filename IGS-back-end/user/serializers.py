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
        # 密码加密存储（必须！不能明文）
        validated_data["password"] = make_password(validated_data.get("password"))
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