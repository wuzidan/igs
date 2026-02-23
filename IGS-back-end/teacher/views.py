# teacher/api/views.py
import os
import logging
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Avg
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classInfo.models import ClassInfo
from question.models import Exercise, PracticeRecord, Question
from student.models import User
from .models import Teacher, Subject
from .serializers import TeacherProfileSerializer, SubjectSerializer

logger = logging.getLogger(__name__)

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

        # 使用外键关联查询学生数量
        student_count = (
            User.objects.filter(class_info__in=class_qs).count() if class_qs else 0
        )

        question_count = Exercise.objects.count()

        class_progress_data = []
        for cls in class_qs:
            last_progress = cls.weekly_progress.order_by("-week").first()
            progress_value = int(getattr(last_progress, "progress", 0) or 0)
            
            # 使用外键关联获取班级学生列表
            students = User.objects.filter(class_info=cls)
            student_list = [
                {
                    "id": student.id,
                    "studentId": student.student_id,
                    "name": student.core_user.first_name or student.core_user.username,
                    "class_name": student.class_name
                }
                for student in students
            ]
            
            class_progress_data.append(
                {
                    "id": cls.id,
                    "className": cls.name,
                    "code": cls.code,
                    "courseName": cls.course_name,
                    "studentCount": len(student_list),
                    "students": student_list,
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


class StudentKnowledgeMasteryView(APIView):
    """
    教师端查看学生知识点掌握程度
    通过调用 model_integration 中的 AAKT 模型诊断逻辑，
    获取指定学生的知识点掌握度数据。

    GET /teacher/student-knowledge-mastery/?student_id=<int>
    """
    permission_classes = [IsAuthenticated]

    # 知识点对应的颜色映射，用于前端进度条展示
    SKILL_COLORS = [
        "#3498db", "#e74c3c", "#2ecc71", "#9b59b6",
        "#f39c12", "#1abc9c", "#e67e22", "#34495e",
        "#16a085", "#c0392b", "#2980b9", "#8e44ad",
        "#27ae60", "#d35400", "#2c3e50", "#f1c40f",
    ]

    def _collect_student_interactions(self, student_user):
        """收集学生的答题交互数据，用于 AAKT 模型输入
        注意：PracticeRecord.student FK 指向 user.User (AUTH_USER_MODEL)，
        而 student_user 是 student.models.User，需要通过 core_user 关联查询。
        """
        interactions = []

        # PracticeRecord.student 是 user.User 的 FK
        # 尝试通过 core_user 获取对应的 user.User 实例
        auth_user = getattr(student_user, 'core_user', None)
        if auth_user is None:
            # 回退：直接用 student_user.id 按 student_id 查询
            practice_records = PracticeRecord.objects.filter(
                student_id=student_user.id
            ).order_by('date')
        else:
            practice_records = PracticeRecord.objects.filter(
                student=auth_user
            ).order_by('date')

        for record in practice_records:
            for question in record.questions.all():
                model_qid = None
                try:
                    if (getattr(question, "exercise", None) is not None
                            and getattr(question.exercise, "exercise_id", None) is not None):
                        model_qid = question.exercise.exercise_id
                except Exception:
                    model_qid = None
                interactions.append({
                    'question_id': model_qid if model_qid is not None else question.id,
                    'correct': question.correct,
                })

        return interactions

    def _mastery_to_skills(self, mastery_per_tag: dict, max_display: int = 20) -> list:
        """将 mastery_per_tag 字典转换为前端 skills 数组格式
        当知识点过多时，取最弱和最强的各 max_display/2 个展示。
        """
        all_skills = []
        for tag_name, mastery_value in mastery_per_tag.items():
            all_skills.append({
                "name": tag_name,
                "level": round(mastery_value * 100, 1),
            })
        # 按掌握度升序排列
        all_skills.sort(key=lambda s: s["level"])

        # 如果知识点过多，取最弱和最强的各一半
        if len(all_skills) > max_display:
            half = max_display // 2
            all_skills = all_skills[:half] + all_skills[-half:]

        # 分配颜色
        color_list = self.SKILL_COLORS
        for idx, skill in enumerate(all_skills):
            skill["color"] = color_list[idx % len(color_list)]

        return all_skills

    def get(self, request):
        # 验证教师身份
        teacher = _ensure_teacher_profile(request.user)
        if teacher is None:
            return Response(
                {"error": "当前用户未关联教师档案"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 获取学生 ID 参数
        student_id = request.query_params.get("student_id")
        if not student_id:
            return Response(
                {"error": "缺少必需参数 student_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "student_id 必须是整数"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 查找学生（student.models.User 存储业务数据）
        try:
            student_user = User.objects.get(id=student_id)
        except User.DoesNotExist:
            return Response(
                {"error": "学生不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 权限校验：学生必须属于该教师管理的班级
        teacher_classes = ClassInfo.objects.filter(head_teacher=teacher)
        student_class_id = getattr(
            getattr(student_user, 'class_info', None), 'id', None
        )
        if student_class_id is None or not teacher_classes.filter(id=student_class_id).exists():
            # 宽松模式：DEBUG 下跳过校验
            if not getattr(settings, "DEBUG", False):
                return Response(
                    {"error": "该学生不属于您管理的班级"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # 收集学生交互数据
        interactions = self._collect_student_interactions(student_user)
        logger.info(
            "Student %s has %d interactions for AAKT diagnosis",
            student_id, len(interactions),
        )

        # 调用 model_integration 中已有的 AAKT 诊断逻辑
        try:
            from model_integration.views import (
                get_diagnosis_from_model,
                load_model,
                MODEL_AVAILABLE,
                MODEL,
            )

            # 确保模型已加载
            if not MODEL_AVAILABLE and MODEL is None:
                load_model()

            diagnosis_result, recommendations = get_diagnosis_from_model(
                interactions, user_id=student_id
            )
        except Exception as e:
            logger.error("AAKT diagnosis failed for student %s: %s", student_id, str(e))
            return Response(
                {"error": f"知识点诊断失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 转换为前端 skills 格式
        mastery_per_tag = diagnosis_result.get("mastery_per_tag", {})
        skills = self._mastery_to_skills(mastery_per_tag)

        return Response({
            "status": "success",
            "student_id": student_id,
            "student_name": getattr(student_user, 'name', None) or student_user.first_name or student_user.username,
            "skills": skills,
            "weakest_tags": diagnosis_result.get("weakest_tags", []),
            "recommendations": recommendations,
            "diagnosis_info": {
                "total_interactions": diagnosis_result.get("total_interactions", 0),
                "valid_interactions": diagnosis_result.get("valid_interactions", 0),
                "model_status": diagnosis_result.get("model_status", "unknown"),
                "accuracy": diagnosis_result.get("accuracy"),
            },
            "timestamp": datetime.now().isoformat(),
        })