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
    """仅管理员或班级班主任可操作"""
    def has_object_permission(self, request, view, obj):
        # obj 是 ClassInfo 对象，判断权限：
        # 1. 管理员（is_staff=True）可操作所有班级
        if request.user.is_staff:
            return True
        # 2. 普通用户：判断是否为该班级的班主任（需关联教师模型的user字段）
        try:
            # 教师模型需关联User：teacher.user = request.user
            teacher = TeacherModel.objects.get(user=request.user)
            return obj.head_teacher == teacher  # 班主任是否匹配
        except TeacherModel.DoesNotExist:
            return False  # 非教师用户无权限