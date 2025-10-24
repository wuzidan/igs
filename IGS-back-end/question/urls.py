# urls.py（应用内）
from django.urls import path
from .views import question

app_name='question'
urlpatterns = [
    # 作答记录数据
    path('question/', question.as_view(), name='question'),
]