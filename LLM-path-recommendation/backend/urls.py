from django.contrib import admin
from django.urls import path
from api.views import recommend_path_api  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/recommend_path/', recommend_path_api), 
]