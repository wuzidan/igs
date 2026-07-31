# class_info/api/permissions.py
from rest_framework import permissions
# 跨模块导入教师模型
from teacher.models import Teacher as TeacherModel

def _is_teacher_user(user) -> bool:
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if bool(getattr(user, "is_staff", False)):
        return True
    username = str(getattr(user, "username", "") or "")
    if username.lower().startswith("teacher"):
        return True
    student_id = str(getattr(user, "student_id", "") or "")
    if student_id.startswith("T"):
        return True
    return TeacherModel.objects.filter(user=user).exists()

class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return _is_teacher_user(getattr(request, "user", None))

class IsHeadTeacherOrAdmin(permissions.BasePermission):
    """仅管理员或教师可操作"""
    def has_permission(self, request, view):
        # 检查用户是否为教师或管理员
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return False
        if bool(getattr(user, "is_staff", False)):
            return True
        # 检查用户是否为教师角色
        return user.role == 2
    
    def has_object_permission(self, request, view, obj):
        # obj 是 ClassInfo 对象，判断权限：
        # 1. 管理员（is_staff=True）可操作所有班级
        if request.user.is_staff:
            return True
        # 2. 教师用户：允许操作所有班级
        return request.user.role == 2