from django.urls import path
from .views import recommend_path_api

urlpatterns = [
    path('recommend_path/', recommend_path_api, name='recommend_path'),
]