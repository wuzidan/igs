# classInfo/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ClassAndChartViewSet

# 方法1：使用ViewSet + 路由器（推荐）
router = DefaultRouter()
router.register('class-chart', ClassAndChartViewSet, basename='class-chart')
router.register(
    r'classes/(?P<class_id>[^/.]+)/students',
    views.StudentManagementViewSet,
    basename='class-students'
)

urlpatterns = [
    path('', include(router.urls)),
    path('classes/', views.ClassCreateView.as_view(), name='class-create'),
    # 班级详情和编辑
    path('classes/<str:class_id>/', views.ClassDetailView.as_view(), name='class-detail'),
]



