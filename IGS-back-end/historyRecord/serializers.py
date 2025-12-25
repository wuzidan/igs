# serializers.py
from rest_framework import serializers

from question.serializers import QuestionSerializer
from .models import HistoryRecord

class HistoryRecordSerializer(serializers.ModelSerializer):
    """作答记录序列化器（嵌套题目）"""
    questions = QuestionSerializer(many=True, read_only=True)  # 嵌套序列化题目列表

    class Meta:
        model = HistoryRecord
        fields = ["id", "type", "date", "score", "duration", "expanded", "questions"]
        extra_kwargs = {
            "date": {"format": "%Y-%m-%d %H:%M"}  # 格式化时间为前端需要的格式
        }