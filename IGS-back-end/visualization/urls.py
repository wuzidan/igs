# 在应用的urls.py中添加
from django.urls import path
from .views import KnowledgeVisualizationView
app_name='visualization'
urlpatterns = [
    # 学习可视化数据接口
    path('display/', KnowledgeVisualizationView.as_view(), name='visualization'),
]