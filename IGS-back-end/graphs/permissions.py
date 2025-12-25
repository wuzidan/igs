from rest_framework.permissions import BasePermission, SAFE_METHODS


def _is_teacher_user(user) -> bool:
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if bool(getattr(user, "is_staff", False)):
        return True
    if bool(getattr(user, "is_teacher_user", False)):
        return True
    if getattr(user, "role", None) == "TEACHER":
        return True
    username = str(getattr(user, "username", "") or "")
    if username.lower().startswith("teacher"):
        return True
    student_id = str(getattr(user, "student_id", "") or "")
    if student_id.startswith("T"):
        return True
    return False


class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return _is_teacher_user(getattr(request, "user", None))


class DomainWritePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _is_teacher_user(getattr(request, "user", None))


class GraphWritePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _is_teacher_user(getattr(request, "user", None))

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return False
        if bool(getattr(user, "is_staff", False)):
            return True
        return getattr(obj, "owner_id", None) == getattr(user, "id", None)
