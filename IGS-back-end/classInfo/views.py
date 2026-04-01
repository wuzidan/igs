<<<<<<< HEAD
=======
# classInfo/views.py 调整建议
>>>>>>> 82a490f (完善“教师端查看学生知识点掌握情况”的功能)
from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, status, generics

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import threading
import time
import logging

_knowledge_chart_cache = {}
_knowledge_chart_lock = threading.Lock()
_knowledge_chart_computing = False
_logger = logging.getLogger(__name__)

from .models import ClassInfo
from .serializers import (
    ClassDetailSerializer,
    ClassUpdateSerializer,
    ClassCreateSerializer,
    ClassAddStudentSerializer,
    StudentDetailSerializer,
)
from .permissions import IsHeadTeacherOrAdmin, IsTeacherOrAdmin

from .pagination import ClassStudentPagination
from student.models import User as StudentModel
from teacher.models import Teacher


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassInfo.objects.all()
    permission_classes = [IsHeadTeacherOrAdmin]
    lookup_field = 'id'  # 明确指定查找字段
    lookup_url_kwarg = 'class_id'

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ClassDetailSerializer
        return ClassUpdateSerializer

    def perform_destroy(self, instance):
        try:
            StudentModel.objects.filter(class_name=instance.name).update(class_name="")
        except Exception:
            pass
        instance.delete()


class ClassCreateView(generics.CreateAPIView):
    queryset = ClassInfo.objects.all()
    serializer_class = ClassCreateSerializer
    permission_classes = [IsTeacherOrAdmin]

    def perform_create(self, serializer):
        user = getattr(self.request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            serializer.save()
            return

        if bool(getattr(user, "is_staff", False)):
            serializer.save()
            return

        teacher = Teacher.objects.filter(user=user).first()
        if teacher is None:
            serializer.save()
            return

        if serializer.validated_data.get("head_teacher") is None:
            serializer.save(head_teacher=teacher)
        else:
            serializer.save()


class StudentManagementViewSet(viewsets.ViewSet):
    """
    学生管理ViewSet - 重新设计以匹配接口文档
    """
    permission_classes = [IsHeadTeacherOrAdmin]
    pagination_class = ClassStudentPagination

    def _get_class(self, class_id):
        try:
            return ClassInfo.objects.get(id=class_id)
        except ClassInfo.DoesNotExist:
            return Response(
                {
                    "error_code": "CLASS_NOT_FOUND",
                    "message": "指定的班级不存在",
                    "timestamp": timezone.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def _get_student(self, student_id):
        try:
            return StudentModel.objects.get(id=student_id)
        except StudentModel.DoesNotExist:
            return Response(
                {
                    "error_code": "STUDENT_NOT_FOUND",
                    "message": "指定的学生不存在",
                    "timestamp": timezone.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def list(self, request, class_id=None):
        """
        获取学生列表 - 匹配 GET /api/classes/{class_id}/students/
        """
        try:
            class_obj = self._get_class(class_id)
            if isinstance(class_obj, Response):
                return class_obj

            # 搜索逻辑
            search_keyword = request.query_params.get("search", "")
            # 使用外键关联查询学生
            students_queryset = StudentModel.objects.filter(class_info=class_obj)
            if search_keyword:
                students_queryset = students_queryset.filter(
                    Q(first_name__icontains=search_keyword) |
                    Q(student_id__icontains=search_keyword)
                )

            # 分页
            paginator = self.pagination_class()
            paginated_students = paginator.paginate_queryset(students_queryset, request)

            serializer = StudentDetailSerializer(paginated_students, many=True)

            # 安全访问分页属性
            try:
                current_page = paginator.page.number
                page_size = paginator.page.paginator.per_page
                total_pages = paginator.page.paginator.num_pages
                total_count = paginator.page.paginator.count
            except AttributeError:
                # 处理分页器属性访问错误
                current_page = 1
                page_size = paginator.page_size
                total_pages = 0
                total_count = 0

            return paginator.get_paginated_response({
                "students": serializer.data,
                "pagination": {
                    "current_page": current_page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_count": total_count
                },
                "search_info": {
                    "keyword": search_keyword,
                    "result_count": total_count
                }
            })
        except Exception as e:
            # 捕获并处理所有异常
            return Response(
                {
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "获取学生列表时发生错误",
                    "details": str(e),
                    "timestamp": timezone.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

<<<<<<< HEAD
=======
    def create(self, request, class_id=None):
        """
        添加学生 - 匹配 POST /api/classes/{class_id}/students/
        """
        class_obj = self._get_class(class_id)
        if isinstance(class_obj, Response):
            return class_obj

        serializer = ClassAddStudentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error_code": "INVALID_PARAMETERS",
                    "message": "请求参数验证失败",
                    "details": serializer.errors,
                    "timestamp": timezone.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查学号是否已存在
        if StudentModel.objects.filter(student_id=serializer.validated_data["student_id"]).exists():
            return Response(
                {
                    "error_code": "STUDENT_ID_EXISTS",
                    "message": f"学号 {serializer.validated_data['student_id']} 已存在",
                    "timestamp": timezone.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        student = StudentModel.objects.create(
            student_id=serializer.validated_data["student_id"],
            username=serializer.validated_data["student_id"],
            first_name=serializer.validated_data["name"],
            phone=serializer.validated_data.get("phone", ""),
            email=serializer.validated_data.get("email", ""),
            class_name=class_obj.name,
            class_info=class_obj,  # 设置外键关联
            password="123",
        )

        try:
            student.set_password("123")
            student.save(update_fields=["password"])
        except Exception:
            pass

        return Response(StudentDetailSerializer(student).data, status=status.HTTP_201_CREATED)

>>>>>>> 82a490f (完善“教师端查看学生知识点掌握情况”的功能)
    def retrieve(self, request, class_id=None, pk=None):
        """
        获取学生详情 - 新增接口，匹配 GET /api/classes/{class_id}/students/{student_id}/
        """
        class_obj = self._get_class(class_id)
        if isinstance(class_obj, Response):
            return class_obj

        student = self._get_student(pk)
        if isinstance(student, Response):
            return student

        # 验证学生是否属于当前班级
        if getattr(student, "class_name", "") != class_obj.name:
            return Response(
                {
                    "error_code": "STUDENT_NOT_IN_CLASS",
                    "message": "该学生不属于当前班级",
                    "timestamp": timezone.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(StudentDetailSerializer(student).data)

    def destroy(self, request, class_id=None, pk=None):
        """
        移除学生 - 匹配 DELETE /api/classes/{class_id}/students/{student_id}/
        """
        class_obj = self._get_class(class_id)
        if isinstance(class_obj, Response):
            return class_obj

        student = self._get_student(pk)
        if isinstance(student, Response):
            return student

        if getattr(student, "class_name", "") != class_obj.name:
            return Response(
                {
                    "error_code": "STUDENT_NOT_IN_CLASS",
                    "message": "该学生不属于当前班级",
                    "timestamp": timezone.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        student.class_name = ""
        student.class_info = None  # 清除外键关联
        student.save(update_fields=["class_name", "class_info"])

        # 返回204 No Content，符合RESTful规范
        return Response(status=status.HTTP_204_NO_CONTENT)


# class_info/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ClassInfo
from .serializers import (
    ClassListSerializer, ClassProgressChartSerializer,
    KnowledgeChartSerializer
)

class ClassAndChartViewSet(viewsets.ReadOnlyModelViewSet):
    """班级与图表视图集：提供班级列表、进度图表、知识点图表接口"""
    permission_classes = [IsAuthenticated]
    queryset = ClassInfo.objects.all()
    serializer_class = ClassListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return qs
        if bool(getattr(user, "is_staff", False)):
            return qs
        teacher = Teacher.objects.filter(user=user).first()
        if teacher is None:
            return qs.none()
        return qs.filter(head_teacher=teacher)

    # 1. 获取班级列表（对应前端classes下拉筛选）
    @action(detail=False, methods=['get'], url_path='class-list')
    def class_list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 2. 获取班级进度图表数据（对应前端createProgressChart）
    @action(detail=False, methods=['get'], url_path='progress-chart')
    def progress_chart(self, request):
        chart_data = ClassProgressChartSerializer.get_chart_data()
        return Response(chart_data)

    # 3. 获取知识点掌握度图表数据（对应前端createKnowledgeChart）
    #    使用内存缓存：首次请求立即返回静态数据，后台异步计算 AAKT 结果并缓存
    @action(detail=False, methods=['get'], url_path='knowledge-chart')
    def knowledge_chart(self, request):
        global _knowledge_chart_computing

        cache_key = 'aakt_knowledge_chart'
        cached = _knowledge_chart_cache.get(cache_key)

        if cached is not None:
            # 缓存命中，直接返回（附加缓存时间戳供调试）
            return Response(cached)

        # 缓存未命中：立即返回静态数据，同时触发后台计算
        with _knowledge_chart_lock:
            if not _knowledge_chart_computing:
                _knowledge_chart_computing = True
                t = threading.Thread(
                    target=self._compute_and_cache_knowledge_chart,
                    daemon=True,
                )
                t.start()

        fallback = KnowledgeChartSerializer.get_chart_data()
        return Response(fallback)

    def _compute_and_cache_knowledge_chart(self):
        """后台线程：运行 AAKT 聚合诊断并将结果写入内存缓存"""
        global _knowledge_chart_computing
        try:
            result = self._get_aakt_knowledge_chart()
            if result is not None:
                _knowledge_chart_cache['aakt_knowledge_chart'] = result
                _logger.info("AAKT knowledge chart cached with %d labels", len(result.get('labels', [])))
        except Exception as e:
            _logger.error("Background AAKT knowledge chart computation failed: %s", e)
        finally:
            with _knowledge_chart_lock:
                _knowledge_chart_computing = False

    def _get_aakt_knowledge_chart(self):
        """
        使用 AAKT 模型聚合该教师管理班级中有练习记录的学生的知识点掌握度，
        生成与前端 knowledgeData 格式兼容的图表数据。
        """
        import logging
        logger = logging.getLogger(__name__)
        try:
            from question.models import PracticeRecord
            from model_integration.views import (
                get_diagnosis_from_model, load_model,
                MODEL_AVAILABLE, MODEL,
            )

            if not MODEL_AVAILABLE and MODEL is None:
                try:
                    load_model()
                except Exception:
                    pass

            # 获取有练习记录的学生ID列表
            # 注意：PracticeRecord.student FK 指向 user.User (AUTH_USER_MODEL)，
            # 而 class_info 在 student.models.User 上，无法直接跨表 join。
            # 先获取该教师班级内的学生 core_user ID，再筛选有记录的。
            class_qs = self.get_queryset()
            class_student_core_ids = list(
                StudentModel.objects
                .filter(class_info__in=class_qs, core_user__isnull=False)
                .values_list('core_user_id', flat=True)
            )
            if class_student_core_ids:
                students_with_records = (
                    PracticeRecord.objects
                    .filter(student_id__in=class_student_core_ids)
                    .values_list('student_id', flat=True)
                    .distinct()
                )
            else:
                students_with_records = PracticeRecord.objects.none()

            # 如果教师班级内没有练习记录，扩大到全局有记录的学生
            if not students_with_records.exists():
                students_with_records = (
                    PracticeRecord.objects
                    .values_list('student_id', flat=True)
                    .distinct()
                )
            if not students_with_records.exists():
                return None

            # 收集所有学生的交互数据并聚合诊断
            all_mastery = {}  # tag_name -> [mastery_values]
            excellent_mastery = {}  # tag_name -> [mastery_values] (accuracy > 0.7)
            student_ids = list(students_with_records[:50])  # 限制最多50个学生

            for sid in student_ids:
                interactions = []
                records = PracticeRecord.objects.filter(student_id=sid).order_by('date')
                for record in records:
                    for q in record.questions.all():
                        model_qid = None
                        try:
                            if (getattr(q, "exercise", None) is not None
                                    and getattr(q.exercise, "exercise_id", None) is not None):
                                model_qid = q.exercise.exercise_id
                        except Exception:
                            model_qid = None
                        interactions.append({
                            'question_id': model_qid if model_qid is not None else q.id,
                            'correct': q.correct,
                        })

                if not interactions:
                    continue

                try:
                    diag, _ = get_diagnosis_from_model(interactions, user_id=sid)
                except Exception:
                    continue

                mastery_per_tag = diag.get("mastery_per_tag", {})
                accuracy = diag.get("accuracy") or 0

                for tag, val in mastery_per_tag.items():
                    all_mastery.setdefault(tag, []).append(val)
                    if accuracy >= 0.7:
                        excellent_mastery.setdefault(tag, []).append(val)

            if not all_mastery:
                return None

            # 构建图表数据，限制最多展示 20 个知识点
            MAX_CHART_TAGS = 20
            # 按平均掌握度排序，取最弱的 MAX_CHART_TAGS 个
            sorted_tags = sorted(
                all_mastery.keys(),
                key=lambda t: sum(all_mastery[t]) / len(all_mastery[t])
            )
            if len(sorted_tags) > MAX_CHART_TAGS:
                sorted_tags = sorted_tags[:MAX_CHART_TAGS]

            labels = sorted_tags
            overall_data = [
                round(sum(all_mastery[tag]) / len(all_mastery[tag]) * 100, 1)
                for tag in sorted_tags
            ]
            excellent_data = [
                round(sum(excellent_mastery.get(tag, all_mastery[tag])) / len(excellent_mastery.get(tag, all_mastery[tag])) * 100, 1)
                for tag in sorted_tags
            ]

            datasets = [
                {
                    "label": "整体掌握度",
                    "data": overall_data,
                    "backgroundColor": "rgba(52, 152, 219, 0.6)",
                    "borderColor": "rgba(52, 152, 219, 1)",
                    "borderWidth": 1,
                },
                {
                    "label": "优秀学生掌握度",
                    "data": excellent_data,
                    "backgroundColor": "rgba(46, 204, 113, 0.6)",
                    "borderColor": "rgba(46, 204, 113, 1)",
                    "borderWidth": 1,
                },
            ]

            return {"labels": labels, "datasets": datasets}

        except Exception as e:
            logger.error("AAKT knowledge chart aggregation failed: %s", str(e))
            return None