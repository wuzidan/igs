# urls.py（应用内）
from django.urls import path
from .views import SubmitPracticeRecordView, historyRecord

app_name='historyRecord'
urlpatterns = [
    # 作答记录数据
    path('getHistoryRecord/', historyRecord.as_view(), name='historyRecord'),
    path('submitPracticeRecord/', SubmitPracticeRecordView.as_view(), name='submitPracticeRecord'),
]