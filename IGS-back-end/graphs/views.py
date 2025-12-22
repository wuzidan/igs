from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import GraphDomain, KnowledgeGraph
from .permissions import DomainWritePermission, GraphWritePermission
from .serializers import (
    GraphDomainSerializer,
    KnowledgeGraphDetailSerializer,
    KnowledgeGraphListSerializer,
    KnowledgeGraphWriteSerializer,
)


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


class GraphPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "pageSize"

    def get_paginated_response(self, data):
        try:
            page_number = int(self.page.number)
        except Exception:
            page_number = 1

        page_size = self.get_page_size(self.request) or len(data)

        return Response(
            {
                "page": page_number,
                "pageSize": page_size,
                "total": self.page.paginator.count,
                "results": data,
            }
        )


class GraphDomainViewSet(viewsets.ModelViewSet):
    queryset = GraphDomain.objects.all()
    serializer_class = GraphDomainSerializer
    permission_classes = [DomainWritePermission]

    def perform_create(self, serializer):
        user = getattr(self.request, "user", None)
        if not _is_teacher_user(user):
            raise PermissionDenied("只有教师/管理员可新增领域")
        serializer.save(created_by=user)


class KnowledgeGraphViewSet(viewsets.ModelViewSet):
    pagination_class = GraphPagination
    permission_classes = [GraphWritePermission]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        qs = KnowledgeGraph.objects.select_related("domain", "owner").all()

        if user is None or not getattr(user, "is_authenticated", False):
            return qs.filter(status=KnowledgeGraph.GraphStatus.PUBLISHED)

        if bool(getattr(user, "is_staff", False)):
            return qs

        if _is_teacher_user(user):
            return qs.filter(Q(status=KnowledgeGraph.GraphStatus.PUBLISHED) | Q(owner=user))

        return qs.filter(status=KnowledgeGraph.GraphStatus.PUBLISHED)

    def get_serializer_class(self):
        if self.action in ["list"]:
            return KnowledgeGraphListSerializer
        if self.action in ["create", "update", "partial_update", "import_graph"]:
            return KnowledgeGraphWriteSerializer
        return KnowledgeGraphDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        domain_id = request.query_params.get("domainId")
        type_ = request.query_params.get("type")
        status_ = request.query_params.get("status")
        keyword = request.query_params.get("keyword")

        if domain_id and str(domain_id).isdigit():
            queryset = queryset.filter(domain_id=int(domain_id))
        if type_:
            queryset = queryset.filter(type=type_)
        if status_:
            queryset = queryset.filter(status=status_)
        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data})

    def perform_create(self, serializer):
        user = getattr(self.request, "user", None)
        if not _is_teacher_user(user):
            raise PermissionDenied("只有教师/管理员可创建图谱")

        graph = serializer.save(owner=user)
        if not isinstance(graph.content, dict) or not graph.content:
            graph.content = {"nodes": [], "relationships": []}
            graph.save(update_fields=["content"])

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return Response({"error": "未授权"}, status=status.HTTP_401_UNAUTHORIZED)

        graph = self.get_object()
        if not (bool(getattr(user, "is_staff", False)) or graph.owner_id == user.id):
            return Response({"error": "无权限"}, status=status.HTTP_403_FORBIDDEN)

        graph.status = KnowledgeGraph.GraphStatus.PUBLISHED
        graph.published_at = timezone.now()
        graph.save(update_fields=["status", "published_at", "updated_at"])
        return Response({"status": graph.status, "publishedAt": graph.published_at})

    @action(detail=True, methods=["get"], url_path="export")
    def export(self, request, pk=None):
        instance = self.get_object()
        serializer = KnowledgeGraphDetailSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="import")
    def import_graph(self, request):
        user = getattr(request, "user", None)
        if not _is_teacher_user(user):
            raise PermissionDenied("只有教师/管理员可导入图谱")

        serializer = KnowledgeGraphWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        graph = serializer.save(owner=user)
        if not isinstance(graph.content, dict) or not graph.content:
            graph.content = {"nodes": [], "relationships": []}
            graph.save(update_fields=["content"])
        return Response({"id": graph.id}, status=status.HTTP_201_CREATED)
