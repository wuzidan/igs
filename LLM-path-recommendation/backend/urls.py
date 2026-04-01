from django.contrib import admin
from django.urls import path
from api.views import recommend_path_api  # 暴力直连：直接把咱们写好的函数拉过来！

urlpatterns = [
    path('admin/', admin.site.urls),
    # 暴力直连：直接在这里写死完整路径！
    path('api/recommend-path', recommend_path_api), 
]