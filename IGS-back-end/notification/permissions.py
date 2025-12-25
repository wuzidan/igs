# notification/api/permissions.py
from rest_framework import permissions

class IsNotificationRecipient(permissions.BasePermission):
    """
    仅通知的接收教师（recipient）可访问/修改该通知
    """
    message = "您无权访问或修改其他教师的通知"

    def has_permission(self, request, view):
        # 先确保用户已登录且是教师角色
        return request.user and request.user.is_authenticated and request.user.is_teacher_user

    def has_object_permission(self, request, view, obj):
        # 仅通知的接收者（recipient）可操作
        return obj.recipient == request.user