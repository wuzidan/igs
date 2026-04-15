from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend_path, name='recommend_path'),
]