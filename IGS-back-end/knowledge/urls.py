# 应用内 urls.py
from django.urls import path
from .views import KnowledgeStructureView

app_name = "knowledge"
urlpatterns = [
    path("structure/", KnowledgeStructureView.as_view(), name="knowledge_structure"),
]

