# user/api/permissions.py
from rest_framework import permissions
from .models import User

class IsAdmin(permissions.BasePermission):
    """仅管理员可访问"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class IsStudent(permissions.BasePermission):
    """仅学生角色可访问"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_student_user

class IsTeacher(permissions.BasePermission):
    """仅教师角色可访问"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_teacher_user