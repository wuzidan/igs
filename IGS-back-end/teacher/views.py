# teacher/api/views.py
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Avg
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classInfo.models import ClassInfo
from question.models import Exercise, PracticeRecord, Question
from student.models import User as StudentModel
from .models import Teacher, Subject
from .serializers import TeacherProfileSerializer, SubjectSerializer


def _is_teacher_user(user) -> bool:
    if user is None:
        return False
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


def _default_teacher_id_for_user(user) -> str:
    return f"T{getattr(user, 'id', 0) or 0:06d}"


def _ensure_teacher_profile(user):
    teacher = getattr(user, "teacher_profile", None)
    if teacher is not None:
        return teacher

    if not getattr(user, "is_authenticated", False):
        return None

    can_autocreate = bool(getattr(settings, "DEBUG", False)) or _is_teacher_user(user)
    if not can_autocreate:
        return None

    teacher, _ = Teacher.objects.get_or_create(
        user=user,
        defaults={
            "teacher_id": _default_teacher_id_for_user(user),
            "title": "未设置",
            "department": "未设置",
        },
    )
    return teacher


class TeacherProfileView(APIView):
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, request):
        if getattr(request, "user", None) is None or not request.user.is_authenticated:
            return None
        return _ensure_teacher_profile(request.user)

    def get(self, request):
        instance = self.get_object(request)
        if instance is None:
            return Response({"error": "当前用户未关联教师档案"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def put(self, request):
        instance = self.get_object(request)
        if instance is None:
            return Response({"error": "当前用户未关联教师档案"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "信息保存成功！", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        instance = self.get_object(request)
        if instance is None:
            return Response({"error": "当前用户未关联教师档案"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "信息保存成功！", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherAvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response({"error": "请选择要上传的头像文件"}, status=status.HTTP_400_BAD_REQUEST)

        teacher = _ensure_teacher_profile(request.user) if getattr(request, "user", None) is not None and request.user.is_authenticated else None
        if teacher is None:
            return Response({"error": "当前用户未关联教师档案"}, status=status.HTTP_404_NOT_FOUND)

        upload = request.FILES['avatar']
        upload_path = os.path.join("teachers", upload.name)
        saved_path = default_storage.save(upload_path, upload)
        avatar_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path.replace("\\", "/"))

        user_instance = teacher.user
        if hasattr(user_instance, "user_avatar_url"):
            user_instance.user_avatar_url = avatar_url
            user_instance.save(update_fields=["user_avatar_url"])
        elif hasattr(user_instance, "avatar_url"):
            user_instance.avatar_url = avatar_url
            user_instance.save(update_fields=["avatar_url"])

        return Response({
            "message": "头像上传成功！",
            "avatarUrl": avatar_url
        }, status=status.HTTP_200_OK)


class SubjectListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)


class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request, "user", None) is None or not request.user.is_authenticated:
            return Response({"error": "未授权"}, status=status.HTTP_401_UNAUTHORIZED)

        teacher = _ensure_teacher_profile(request.user)
        if teacher is None:
            return Response({"error": "当前用户未关联教师档案"}, status=status.HTTP_404_NOT_FOUND)

        class_qs = ClassInfo.objects.filter(head_teacher=teacher)
        class_count = class_qs.count()

        class_names = list(class_qs.values_list("name", flat=True))
        student_count = (
            StudentModel.objects.filter(class_name__in=class_names).count() if class_names else 0
        )

        question_count = Exercise.objects.count()

        class_progress_data = []
        for cls in class_qs:
            last_progress = cls.weekly_progress.order_by("-week").first()
            progress_value = int(getattr(last_progress, "progress", 0) or 0)
            class_progress_data.append(
                {
                    "id": cls.id,
                    "className": cls.name,
                    "progress": max(0, min(100, progress_value)),
                }
            )

        total_questions = Question.objects.count()
        correct_questions = Question.objects.filter(correct=True).count()
        average_accuracy = (
            int(round((correct_questions / total_questions) * 100)) if total_questions else 0
        )

        avg_duration = PracticeRecord.objects.aggregate(v=Avg("duration_minutes")).get("v")
        avg_hours = float(avg_duration or 0) / 60.0
        average_study_hours = round(avg_hours, 1)
        study_hours_rate_teacher = int(round((average_study_hours / 25.0) * 100))
        study_hours_rate_teacher = max(0, min(100, study_hours_rate_teacher))

        profile = TeacherProfileSerializer(teacher).data

        return Response(
            {
                "teacher": profile,
                "summary": {
                    "classCount": class_count,
                    "studentCount": student_count,
                    "questionCount": question_count,
                },
                "tasks": {
                    "pendingTasks": 0,
                    "pendingTaskList": [],
                },
                "stats": {
                    "averageAccuracy": average_accuracy,
                    "accuracyTrend": 0,
                    "averageStudyHours": average_study_hours,
                    "studyHoursRateTeacher": study_hours_rate_teacher,
                    "hoursTrend": 0,
                    "completedAssignments": 0,
                    "totalAssignments": 0,
                    "assignmentCompletionRate": 0,
                    "assignmentsTrend": 0,
                },
                "classProgressData": class_progress_data,
            }
        )