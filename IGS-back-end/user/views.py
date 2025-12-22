from django.shortcuts import render
# user/api/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
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
class CustomLoginView(ObtainAuthToken):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        # 调用DRF默认登录逻辑
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        # 生成/获取Token（用于后续接口认证）
        token, created = Token.objects.get_or_create(user=user)
        # 返回Token+用户基础信息
        return Response({
            "token": token.key,
            "user": UserBaseSerializer(user).data
        }, status=status.HTTP_200_OK)

# 4. 管理员创建用户接口（仅管理员可访问）
class AdminCreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdmin]  # 仅管理员可创建用户
# Create your views here.
