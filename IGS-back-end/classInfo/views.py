# classInfo/views.py 调整建议
from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, status, generics

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

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
        class_obj = self._get_class(class_id)
        if isinstance(class_obj, Response):
            return class_obj

        # 搜索逻辑
        search_keyword = request.query_params.get("search", "")
        students_queryset = StudentModel.objects.filter(class_name=class_obj.name)
        if search_keyword:
            students_queryset = students_queryset.filter(
                Q(first_name__icontains=search_keyword) |
                Q(student_id__icontains=search_keyword)
            )

        # 分页
        paginator = self.pagination_class()
        paginated_students = paginator.paginate_queryset(students_queryset, request)

        serializer = StudentDetailSerializer(paginated_students, many=True)

        return paginator.get_paginated_response({
            "students": serializer.data,
            "pagination": {
                "current_page": paginator.page.number,  # 改为下划线命名
                "page_size": paginator.page.paginator.per_page,
                "total_pages": paginator.page.paginator.num_pages,
                "total_count": paginator.page.paginator.count
            },
            "search_info": {
                "keyword": search_keyword,
                "result_count": paginator.page.paginator.count
            }
        })

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
            password="123",
        )

        try:
            student.set_password("123")
            student.save(update_fields=["password"])
        except Exception:
            pass

        return Response(StudentDetailSerializer(student).data, status=status.HTTP_201_CREATED)

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
        student.save(update_fields=["class_name"])

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
    @action(detail=False, methods=['get'], url_path='knowledge-chart')
    def knowledge_chart(self, request):
        chart_data = KnowledgeChartSerializer.get_chart_data()
        return Response(chart_data)