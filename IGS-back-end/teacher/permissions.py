# teacher/api/permissions.py
from rest_framework import permissions

class IsTeacherOwner(permissions.BasePermission):
    """仅教师本人或管理员可访问/修改"""
    message = "您无权访问或修改其他教师的信息"

    def has_object_permission(self, request, view, obj):
        # 管理员可访问所有
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_admin", False):
            return True
        # 教师仅可访问自己的信息（obj是Teacher实例，obj.user是关联的User）
        return obj.user == request.user