# 应用内 urls.py
from django.urls import path
from .views import KnowledgeStructureView, CourseManagementView

app_name = "knowledge"
urlpatterns = [
    path("structure/", KnowledgeStructureView.as_view(), name="knowledge_structure"),
    path("courses/", CourseManagementView.as_view(), name="course_management"),
    path("courses/<int:pk>/", CourseManagementView.as_view(), name="course_detail"),
]

