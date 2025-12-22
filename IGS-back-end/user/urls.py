# user/api/urls.py
from django.urls import path
from student.views import StudentLoginView
from .views import (
    CurrentUserView, UpdateCurrentUserView,
    AdminCreateUserView
)

urlpatterns = [
    # 登录：POST /api/user/login/
    path("login/", StudentLoginView.as_view(), name="user-login"),
    # 当前用户信息：GET /api/user/me/
    path("me/", CurrentUserView.as_view(), name="current-user"),
    # 修改当前用户资料：PUT/PATCH /api/user/me/
    path("me/", UpdateCurrentUserView.as_view(), name="update-current-user"),
    # 管理员创建用户：POST /api/user/admin/create/
    path("admin/create/", AdminCreateUserView.as_view(), name="admin-create-user"),
]