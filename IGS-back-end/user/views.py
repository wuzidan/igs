from django.shortcuts import render
# user/api/views.py
from rest_framework import generics, status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db import DatabaseError
from .models import User
from .serializers import UserBaseSerializer, UserUpdateSerializer, UserLoginSerializer, UserCreateSerializer
from .permissions import IsAdmin, IsStudent, IsTeacher

# 1. 当前用户信息接口（所有登录用户可访问）
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserBaseSerializer
    permission_classes = [permissions.IsAuthenticated]  # 需登录

    def get_object(self):
        # 返回当前登录用户（request.user由DRF自动注入）
        return self.request.user

# 2. 修改当前用户基础资料接口
class UpdateCurrentUserView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# 3. 自定义登录接口（返回Token+用户信息）
class CustomLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            try:
                token, created = Token.objects.get_or_create(user=user)
            except DatabaseError as exc:
                return Response({
                    "detail": "登录失败：Token 创建异常",
                    "error": str(exc)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            role = getattr(user, "role", None)
            if role == 1:
                user_type = "student"
            elif role == 2:
                user_type = "teacher"
            elif role == 3:
                user_type = "admin"
            else:
                user_type = "student"
            try:
                user_data = UserBaseSerializer(user).data
            except Exception as exc:
                return Response({
                    "detail": "登录失败：用户信息序列化异常",
                    "error": str(exc),
                    "user_id": getattr(user, "id", None),
                    "role": role,
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({
                "token": token.key,
                "userType": user_type,
                "user": user_data
            }, status=status.HTTP_200_OK)
        except ValidationError:
            raise
        except Exception as exc:
            return Response({
                "detail": "登录失败：未处理异常",
                "error": str(exc),
                "exception_type": exc.__class__.__name__,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 4. 管理员创建用户接口（仅管理员可访问）
class AdminCreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdmin]  # 仅管理员可创建用户
# Create your views here.
