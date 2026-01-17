from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GraphDomainViewSet, KnowledgeGraphViewSet

app_name = "graphs"

router = DefaultRouter()
router.register("domains", GraphDomainViewSet, basename="graph-domain")
router.register("", KnowledgeGraphViewSet, basename="knowledge-graph")

urlpatterns = [
    path("", include(router.urls)),
]
