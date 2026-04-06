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

# 导入Neo4j连接器
from neo4j_connector import neo4j_connector


def _is_teacher_user(user) -> bool:
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if bool(getattr(user, "is_staff", False)):
        return True
    # 检查用户角色是否为教师（role == 2）
    if getattr(user, "role", None) == 2:
        return True
    if bool(getattr(user, "is_teacher_user", False)):
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
        # 获取教师工号
        teacher_profile = getattr(user, "teacher_profile", None)
        if teacher_profile:
            created_by = teacher_profile.teacher_id
        else:
            created_by = user.username
        serializer.save(created_by=created_by)


class KnowledgeGraphViewSet(viewsets.ModelViewSet):
    pagination_class = GraphPagination
    permission_classes = [GraphWritePermission]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        # 暂时不使用 select_related，避免关联查询导致的错误
        qs = KnowledgeGraph.objects.all()

        if user is None or not getattr(user, "is_authenticated", False):
            return qs.filter(status=KnowledgeGraph.GraphStatus.PUBLISHED)

        if bool(getattr(user, "is_staff", False)):
            return qs

        if _is_teacher_user(user):
            try:
                # 导入Teacher模型
                from teacher.models import Teacher
                # 尝试通过user_id获取Teacher实例
                teacher_profile = Teacher.objects.filter(user=user).first()
                if teacher_profile:
                    return qs.filter(Q(status=KnowledgeGraph.GraphStatus.PUBLISHED) | Q(owner=teacher_profile))
            except Exception:
                pass
            return qs.filter(status=KnowledgeGraph.GraphStatus.PUBLISHED)

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

        # 获取教师工号
        teacher_profile = getattr(user, "teacher_profile", None)
        if not teacher_profile:
            raise PermissionDenied("教师档案不存在")
        teacher_id = teacher_profile.teacher_id

        graph = serializer.save(owner=teacher_profile)
        if not isinstance(graph.content, dict) or not graph.content:
            graph.content = {"nodes": [], "relationships": []}
            graph.save(update_fields=["content"])

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return Response({"error": "未授权"}, status=status.HTTP_401_UNAUTHORIZED)

        graph = self.get_object()
        # 获取教师工号进行权限检查
        teacher_profile = getattr(user, "teacher_profile", None)
        if not teacher_profile:
            return Response({"error": "教师档案不存在"}, status=status.HTTP_403_FORBIDDEN)
        teacher_id = teacher_profile.teacher_id

        if not (bool(getattr(user, "is_staff", False)) or graph.owner_id == teacher_id):
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

    @action(detail=False, methods=["get"], url_path="neo4j/graph")
    def get_neo4j_graph(self, request):
        """
        从Neo4j获取完整的知识图谱数据，用于前端展示
        """
        try:
            graph_data = neo4j_connector.get_knowledge_graph()
            return Response({
                "code": 200,
                "msg": "获取知识图谱成功",
                "data": graph_data
            })
        except Exception as e:
            return Response({
                "code": 500,
                "msg": f"获取知识图谱失败: {str(e)}",
                "data": {"nodes": [], "relationships": []}
            })

    @action(detail=False, methods=["get"], url_path="neo4j/prerequisites")
    def get_prerequisites(self, request):
        """
        从Neo4j获取目标知识点的先修关系规则
        """
        target_knowledge = request.query_params.get("target", "")
        if not target_knowledge:
            return Response({
                "code": 400,
                "msg": "缺少目标知识点参数",
                "data": ""
            })
        
        try:
            rules = neo4j_connector.get_prerequisite_relations(target_knowledge)
            return Response({
                "code": 200,
                "msg": "获取先修关系成功",
                "data": rules
            })
        except Exception as e:
            return Response({
                "code": 500,
                "msg": f"获取先修关系失败: {str(e)}",
                "data": f"规则 A：未找到【{target_knowledge}】的先修知识点。"
            })
