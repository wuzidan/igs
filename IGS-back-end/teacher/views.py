# teacher/api/views.py
import os
import logging
import re
from datetime import datetime
from collections import Counter
from collections import defaultdict
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Avg

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classInfo.models import ClassInfo
from question.models import Exercise, PracticeRecord, Question
from knowledge.models import KnowledgeChallengeTopic
from student.models import User
from user.models import User as CoreUser
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

    def _resolve_core_user(self, student_user):
        auth_user = getattr(student_user, 'core_user', None)
        if auth_user is not None:
            return auth_user

        username = str(getattr(student_user, 'username', '') or '').strip()
        email = str(getattr(student_user, 'email', '') or '').strip()

        if username:
            auth_user = CoreUser.objects.filter(username=username).first()
            if auth_user is not None:
                return auth_user

        if email:
            auth_user = CoreUser.objects.filter(email=email).first()
            if auth_user is not None:
                return auth_user

        return None

    def _count_usable_aakt_interactions(self, candidate_id):
        if candidate_id is None:
            return 0

        practice_records = list(
            PracticeRecord.objects.filter(student_id=candidate_id)
            .select_related('challenge')
            .prefetch_related('questions__exercise__exercise_challenges__challenge')
            .order_by('date')
        )

        usable_count = 0
        for record in practice_records:
            record_challenge = getattr(record, 'challenge', None)
            record_challenge_id = getattr(record_challenge, 'challenge_id', None)
            if record_challenge_id is not None:
                usable_count += 1
                continue

            for question in record.questions.all():
                model_qid = None
                question_record_challenge = getattr(question.record, 'challenge', None)
                if getattr(question_record_challenge, 'challenge_id', None) is not None:
                    model_qid = question_record_challenge.challenge_id
                elif getattr(question, 'exercise', None) is not None:
                    challenge_link = question.exercise.exercise_challenges.select_related('challenge').first()
                    if challenge_link is not None and getattr(challenge_link.challenge, 'challenge_id', None) is not None:
                        model_qid = challenge_link.challenge.challenge_id
                if model_qid is not None:
                    usable_count += 1

        return usable_count

    def _log_aakt_record_diagnostics(self, student_user, diagnosis_user_id, practice_records):
        diagnostics = Counter()
        samples = []

        for record in practice_records:
            record_challenge = getattr(record, 'challenge', None)
            record_challenge_code = getattr(record_challenge, 'challenge_id', None)
            if record_challenge_code is not None:
                diagnostics['record_has_challenge'] += 1
            else:
                diagnostics['record_missing_challenge'] += 1

            questions = list(record.questions.all())
            if questions:
                diagnostics['record_has_questions'] += 1
            else:
                diagnostics['record_without_questions'] += 1

            usable_from_questions = 0
            question_with_exercise = 0
            question_with_challenge_link = 0
            question_missing_exercise = 0
            for question in questions:
                exercise = getattr(question, 'exercise', None)
                if exercise is None:
                    question_missing_exercise += 1
                    continue
                question_with_exercise += 1
                challenge_link = exercise.exercise_challenges.select_related('challenge').first()
                if challenge_link is not None and getattr(challenge_link.challenge, 'challenge_id', None) is not None:
                    question_with_challenge_link += 1
                    usable_from_questions += 1

            diagnostics['questions_total'] += len(questions)
            diagnostics['questions_with_exercise'] += question_with_exercise
            diagnostics['questions_missing_exercise'] += question_missing_exercise
            diagnostics['questions_with_challenge_link'] += question_with_challenge_link
            if usable_from_questions > 0:
                diagnostics['record_usable_via_questions'] += 1
            else:
                diagnostics['record_not_usable_via_questions'] += 1

            if len(samples) < 5:
                samples.append({
                    'record_id': getattr(record, 'id', None),
                    'practice_student_id': getattr(record, 'student_id', None),
                    'record_challenge_fk': getattr(record, 'challenge_id', None),
                    'record_challenge_code': record_challenge_code,
                    'question_count': len(questions),
                    'question_with_exercise': question_with_exercise,
                    'question_with_challenge_link': question_with_challenge_link,
                    'usable_from_questions': usable_from_questions,
                })

        logger.info(
            "AAKT interaction diagnostics for student_id=%s, diagnosis_user_id=%s: %s",
            getattr(student_user, 'student_id', None),
            diagnosis_user_id,
            dict(diagnostics),
        )
        logger.info(
            "AAKT interaction diagnostic samples for student_id=%s: %s",
            getattr(student_user, 'student_id', None),
            samples,
        )

    def _resolve_diagnosis_user_id(self, student_user):
        """选择用于诊断的 PracticeRecord.student 外键主键值。"""
        candidate_ids = []

        student_user_id = getattr(student_user, 'id', None)
        if student_user_id is not None:
            candidate_ids.append(student_user_id)

        primary_user = self._resolve_core_user(student_user)
        primary_user_id = getattr(primary_user, 'id', None)
        if primary_user_id is not None:
            candidate_ids.append(primary_user_id)

        username = str(getattr(student_user, 'username', '') or '').strip()
        email = str(getattr(student_user, 'email', '') or '').strip()

        if username:
            matched_by_username = CoreUser.objects.filter(username=username).first()
            matched_id = getattr(matched_by_username, 'id', None)
            if matched_id is not None:
                candidate_ids.append(matched_id)

        if email:
            matched_by_email = CoreUser.objects.filter(email=email).first()
            matched_id = getattr(matched_by_email, 'id', None)
            if matched_id is not None:
                candidate_ids.append(matched_id)

        best_candidate_id = None
        best_usable_interactions = -1
        best_record_count = -1
        seen_ids = set()
        candidate_counts = []
        for candidate_id in candidate_ids:
            if candidate_id is None or candidate_id in seen_ids:
                continue
            seen_ids.add(candidate_id)
            record_count = PracticeRecord.objects.filter(student_id=candidate_id).count()
            usable_interactions = self._count_usable_aakt_interactions(candidate_id)
            candidate_counts.append({
                "candidate_id": candidate_id,
                "record_count": record_count,
                "usable_interactions": usable_interactions,
            })
            if usable_interactions > best_usable_interactions:
                best_usable_interactions = usable_interactions
                best_record_count = record_count
                best_candidate_id = candidate_id
                continue
            if usable_interactions == best_usable_interactions and record_count > best_record_count:
                best_record_count = record_count
                best_candidate_id = candidate_id

        logger.info(
            "AAKT diagnosis candidate resolution for student_id=%s, student_user_pk=%s, core_user_pk=%s, candidates=%s, selected=%s",
            getattr(student_user, 'student_id', None),
            student_user_id,
            primary_user_id,
            candidate_counts,
            best_candidate_id,
        )

        if best_candidate_id is not None:
            return best_candidate_id

        return student_user_id or primary_user_id

    def _collect_student_interactions(self, student_user, diagnosis_user_id=None):
        """收集学生的答题交互数据，用于 AAKT 模型输入
        注意：PracticeRecord.student FK 指向 user.User (AUTH_USER_MODEL)，
        而 student_user 是 student.models.User，需要通过 core_user 关联查询。
        """
        interactions = []

        practice_records = self._get_student_practice_records(
            student_user,
            diagnosis_user_id=diagnosis_user_id,
        )
        self._log_aakt_record_diagnostics(student_user, diagnosis_user_id, practice_records)

        for record in practice_records:
            record_challenge = getattr(record, "challenge", None)
            record_challenge_id = getattr(record_challenge, "challenge_id", None)
            if record_challenge_id is not None:
                interactions.append({
                    'question_id': record_challenge_id,
                    'correct': bool(getattr(record, 'score', 0) > 0),
                })
                continue

            record_questions = list(record.questions.all())
            if not record_questions:
                interactions.append({
                    'question_id': f"synthetic_record_{getattr(record, 'id', 'unknown')}",
                    'correct': bool(getattr(record, 'score', 0) > 0),
                    'synthetic': True,
                    'source': 'practice_record_fallback',
                })
                continue

            for question in record_questions:
                model_qid = None
                try:
                    question_record_challenge = getattr(question.record, "challenge", None)
                    if question_record_challenge is not None and getattr(question_record_challenge, "challenge_id", None) is not None:
                        model_qid = question_record_challenge.challenge_id
                    elif (getattr(question, "exercise", None) is not None
                            and getattr(question.exercise, "exercise_id", None) is not None):
                        challenge_link = question.exercise.exercise_challenges.select_related('challenge').first()
                        if challenge_link is not None and getattr(challenge_link.challenge, "challenge_id", None) is not None:
                            model_qid = challenge_link.challenge.challenge_id
                except Exception:
                    model_qid = None
                interactions.append({
                    'question_id': model_qid if model_qid is not None else question.id,
                    'correct': question.correct,
                })

        return interactions

    def _get_student_practice_records(self, student_user, diagnosis_user_id=None):
        target_user_id = diagnosis_user_id or self._resolve_diagnosis_user_id(student_user)
        records = PracticeRecord.objects.filter(student_id=target_user_id).order_by('date')
        if records.exists():
            logger.info(
                "AAKT practice records matched primary target for student_id=%s: target_user_id=%s, count=%s",
                getattr(student_user, 'student_id', None),
                target_user_id,
                records.count(),
            )
            return records
        student_user_id = getattr(student_user, 'id', None)
        if student_user_id is not None and student_user_id != target_user_id:
            records = PracticeRecord.objects.filter(student_id=student_user_id).order_by('date')
            if records.exists():
                logger.info(
                    "AAKT practice records matched student_user.id fallback for student_id=%s: student_user_id=%s, count=%s",
                    getattr(student_user, 'student_id', None),
                    student_user_id,
                    records.count(),
                )
                return records
        core_user = self._resolve_core_user(student_user)
        core_user_id = getattr(core_user, 'id', None)
        if core_user_id is not None and core_user_id != target_user_id:
            records = PracticeRecord.objects.filter(student_id=core_user_id).order_by('date')
            if records.exists():
                logger.info(
                    "AAKT practice records matched core_user.id fallback for student_id=%s: core_user_id=%s, count=%s",
                    getattr(student_user, 'student_id', None),
                    core_user_id,
                    records.count(),
                )
                return records
        logger.info(
            "AAKT practice records not found for student_id=%s using target_user_id=%s, student_user_id=%s, core_user_id=%s",
            getattr(student_user, 'student_id', None),
            target_user_id,
            student_user_id,
            core_user_id,
        )
        return PracticeRecord.objects.filter(student_id=student_user.id).order_by('date')

    def _build_mastery_from_question_relations(self, student_user, diagnosis_user_id=None):
        """
        从数据库关系直接计算学生知识点掌握度：
        student -> practice_record -> question -> exercise -> challenge -> topic。
        """
        practice_records = self._get_student_practice_records(
            student_user,
            diagnosis_user_id=diagnosis_user_id,
        )

        questions = list(
            Question.objects.filter(
                record__in=practice_records,
                exercise__isnull=False,
            ).only('id', 'exercise_id', 'correct')
        )
        if not questions:
            return []

        exercise_ids = {q.exercise_id for q in questions if q.exercise_id is not None}
        if not exercise_ids:
            return []

        topic_rows = KnowledgeChallengeTopic.objects.filter(
            challenge__exercise_challenges__exercise_id__in=exercise_ids,
        ).values(
            'challenge__exercise_challenges__exercise_id',
            'topic_id',
            'topic__clean_name',
            'topic__name',
            'topic__category',
        )

        exercise_topics = defaultdict(list)
        for row in topic_rows:
            exercise_id = row.get('challenge__exercise_challenges__exercise_id')
            if exercise_id is None:
                continue
            exercise_topics[exercise_id].append(
                {
                    'topic_id': row.get('topic_id'),
                    'name': row.get('topic__clean_name') or row.get('topic__name') or '未知知识点',
                    'category': row.get('topic__category') or 'general',
                }
            )

        topic_stats = {}
        for question in questions:
            topics = exercise_topics.get(question.exercise_id, [])
            if not topics:
                continue

            # 同一题目映射到同一知识点时只计一次，避免重复统计
            per_question_topic_ids = set()
            for topic in topics:
                topic_id = topic['topic_id']
                if topic_id in per_question_topic_ids:
                    continue
                per_question_topic_ids.add(topic_id)

                if topic_id not in topic_stats:
                    topic_stats[topic_id] = {
                        'topicId': topic_id,
                        'name': topic['name'],
                        'category': topic['category'],
                        'totalQuestions': 0,
                        'correctQuestions': 0,
                    }

                topic_stats[topic_id]['totalQuestions'] += 1
                if bool(question.correct):
                    topic_stats[topic_id]['correctQuestions'] += 1

        skills = []
        for stat in topic_stats.values():
            total_questions = stat['totalQuestions']
            mastery = round((stat['correctQuestions'] / total_questions) * 100, 1) if total_questions else 0.0
            skills.append(
                {
                    **stat,
                    'level': mastery,
                    'mastery': mastery,
                }
            )

        skills.sort(key=lambda item: item['level'])
        for idx, skill in enumerate(skills):
            skill['color'] = self.SKILL_COLORS[idx % len(self.SKILL_COLORS)]
        return skills

    def _get_student_topic_display_names(self, student_user, diagnosis_user_id=None):
        relation_skills = self._build_mastery_from_question_relations(
            student_user,
            diagnosis_user_id=diagnosis_user_id,
        )
        return [item['name'] for item in relation_skills if item.get('name')]

    def _remap_mastery_display_names(self, mastery_per_tag: dict, student_user, diagnosis_user_id=None) -> dict:
        if not isinstance(mastery_per_tag, dict) or not mastery_per_tag:
            return {}

        real_topic_names = self._get_student_topic_display_names(
            student_user,
            diagnosis_user_id=diagnosis_user_id,
        )
        if not real_topic_names:
            return mastery_per_tag

        remapped = {}
        fallback_index = 0
        for raw_tag_name, mastery_value in mastery_per_tag.items():
            raw_name = str(raw_tag_name or '').strip()
            if re.fullmatch(r'知识点_\d+', raw_name) and fallback_index < len(real_topic_names):
                display_name = real_topic_names[fallback_index]
                fallback_index += 1
            else:
                display_name = raw_name

            dedupe_name = display_name
            duplicate_index = 2
            while dedupe_name in remapped:
                dedupe_name = f"{display_name}_{duplicate_index}"
                duplicate_index += 1
            remapped[dedupe_name] = mastery_value

        return remapped

    def _mastery_to_skills(self, mastery_per_tag: dict, max_display: int = 20) -> list:
        """将 mastery_per_tag 字典转换为前端 skills 数组格式，仅展示最弱的非占位知识点。"""
        all_skills = []
        for tag_name, mastery_value in mastery_per_tag.items():
            normalized_name = str(tag_name or '').strip()
            if not normalized_name or re.fullmatch(r'知识点_\d+', normalized_name):
                continue
            all_skills.append({
                "name": normalized_name,
                "level": round(mastery_value * 100, 1),
            })

        all_skills.sort(key=lambda item: item["level"])

        if max_display > 0 and len(all_skills) > max_display:
            all_skills = all_skills[:max_display]

        # 分配颜色
        color_list = self.SKILL_COLORS
        for idx, skill in enumerate(all_skills):
            skill["color"] = color_list[idx % len(color_list)]

        return all_skills

    def get(self, request):
        teacher = _ensure_teacher_profile(request.user)
        if teacher is None:
            return Response(
                {"error": "当前用户未关联教师档案"},
                status=status.HTTP_404_NOT_FOUND,
            )

        student_id = request.query_params.get("student_id")
        if not student_id:
            return Response(
                {"error": "缺少必需参数 student_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 尝试通过student_id字段查询学生
            student_user = User.objects.get(student_id=student_id)
        except User.DoesNotExist:
            # 如果通过student_id查询失败，尝试通过id字段查询
            try:
                student_id_int = int(student_id)
                student_user = User.objects.get(id=student_id_int)
            except (ValueError, TypeError, User.DoesNotExist):
                return Response(
                    {"error": "学生不存在"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        teacher_classes = ClassInfo.objects.filter(head_teacher=teacher)
        student_class_id = getattr(getattr(student_user, 'class_info', None), 'id', None)
        if student_class_id is None or not teacher_classes.filter(id=student_class_id).exists():
            if not getattr(settings, "DEBUG", False):
                return Response(
                    {"error": "该学生不属于您管理的班级"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        diagnosis_user_id = self._resolve_diagnosis_user_id(student_user)
        logger.info(
            "AAKT diagnosis request context: requested_student_id=%s, student_user_pk=%s, diagnosis_user_id=%s",
            student_id,
            getattr(student_user, 'id', None),
            diagnosis_user_id,
        )
        relation_skills = self._build_mastery_from_question_relations(
            student_user,
            diagnosis_user_id=diagnosis_user_id,
        )

        if relation_skills:
            strongest = sorted(relation_skills, key=lambda item: item['level'], reverse=True)[:3]
            weakest = sorted(relation_skills, key=lambda item: item['level'])[:3]
            total_relation_interactions = sum(item['totalQuestions'] for item in relation_skills)
            relation_formal_diagnosis = total_relation_interactions >= 20
            relation_confidence_level = 'medium' if relation_formal_diagnosis else 'low'
            relation_stability_warning = None if relation_formal_diagnosis else '当前样本量不足，建议继续练习后再评估'
            recommendations = [
                f"优先巩固《{item['name']}》知识点，当前掌握度 {item['level']}%" for item in weakest
            ]
            if relation_stability_warning and relation_stability_warning not in recommendations:
                recommendations.append(relation_stability_warning)

            return Response(
                {
                    'status': 'success',
                    'student_id': student_id,
                    'student_name': getattr(student_user, 'name', None) or student_user.first_name or student_user.username,
                    'skills': relation_skills,
                    'weakest_tags': [item['name'] for item in weakest],
                    'strongest_tags': [item['name'] for item in strongest],
                    'recommendations': recommendations,
                    'diagnosis_info': {
                        'data_source': 'question_relation',
                        'diagnosis_user_id': diagnosis_user_id,
                        'total_topics': len(relation_skills),
                        'total_interactions': total_relation_interactions,
                        'model_status': 'rule_based',
                        'confidence_level': relation_confidence_level,
                        'low_confidence': not relation_formal_diagnosis,
                        'formal_diagnosis': relation_formal_diagnosis,
                        'min_required_interactions': 20,
                        'stability_warning': relation_stability_warning,
                    },
                    'timestamp': datetime.now().isoformat(),
                }
            )

        interactions = self._collect_student_interactions(
            student_user,
            diagnosis_user_id=diagnosis_user_id,
        )
        logger.info(
            "Student %s has %d interactions for AAKT diagnosis",
            student_id, len(interactions),
        )

        try:
            from model_integration.views import (
                get_diagnosis_from_model,
                load_model,
                MODEL_AVAILABLE,
                MODEL,
            )

            if not MODEL_AVAILABLE and MODEL is None:
                load_model()

            diagnosis_result, recommendations = get_diagnosis_from_model(
                interactions, user_id=diagnosis_user_id
            )
        except Exception as e:
            logger.error("AAKT diagnosis failed for student %s: %s", student_id, str(e))
            return Response(
                {"error": f"知识点诊断失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        mastery_per_tag = self._remap_mastery_display_names(
            diagnosis_result.get("mastery_per_tag", {}),
            student_user,
            diagnosis_user_id=diagnosis_user_id,
        )
        diagnosis_result["mastery_per_tag"] = mastery_per_tag
        filtered_weakest_tags = [
            tag for tag in sorted(
                mastery_per_tag.keys(),
                key=lambda tag: mastery_per_tag[tag],
            )
            if not re.fullmatch(r'知识点_\d+', str(tag or '').strip())
        ]
        diagnosis_result["weakest_tags"] = filtered_weakest_tags[:3]
        skills = self._mastery_to_skills(mastery_per_tag, max_display=6)

        return Response({
            "status": "success",
            "student_id": student_id,
            "student_name": getattr(student_user, 'name', None) or student_user.first_name or student_user.username,
            "skills": skills,
            "weakest_tags": diagnosis_result.get("weakest_tags", []),
            "recommendations": recommendations,
            "diagnosis_info": {
                "data_source": "aakt_model",
                "total_interactions": diagnosis_result.get("total_interactions", 0),
                "valid_interactions": diagnosis_result.get("valid_interactions", 0),
                "model_status": diagnosis_result.get("model_status", "unknown"),
                "accuracy": diagnosis_result.get("accuracy"),
                "confidence_level": diagnosis_result.get("confidence_level"),
                "confidence_score": diagnosis_result.get("confidence_score"),
                "low_confidence": diagnosis_result.get("low_confidence", False),
                "low_confidence_reason": diagnosis_result.get("low_confidence_reason"),
                "formal_diagnosis": diagnosis_result.get("formal_diagnosis", False),
                "min_required_interactions": diagnosis_result.get("min_required_interactions"),
                "used_model_inference": diagnosis_result.get("used_model_inference", False),
                "fallback_reason": diagnosis_result.get("fallback_reason"),
                "smoothed_mastery": diagnosis_result.get("smoothed_mastery", False),
                "stability_warning": diagnosis_result.get("stability_warning"),
                "stability_score": diagnosis_result.get("stability_score"),
                "diagnosis_messages": diagnosis_result.get("diagnosis_messages", []),
                "diagnosis_user_id": diagnosis_user_id,
            },
            "timestamp": datetime.now().isoformat(),
        })