# urls.py（应用内）
from django.urls import path
from .views import StudentInfoView
app_name='student'
urlpatterns = [
    # 作答记录数据
    path('studentInfo/', StudentInfoView.as_view(), name='student'),
]