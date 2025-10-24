# serializers.py
import json
from rest_framework import serializers
from .models import Question

class QuestionSerializer(serializers.ModelSerializer):
    """题目序列化器"""
    # 自定义字段处理JSON反序列化
    userAnswer = serializers.SerializerMethodField()
    correctAnswer = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    
    def get_userAnswer(self, obj):
        """处理用户答案的JSON字段"""
        # 原代码：直接使用source映射
        # "userAnswer": {"source": "user_answer"},
        # 新代码：处理JSON反序列化
        if obj.user_answer:
            if isinstance(obj.user_answer, str):
                try:
                    return json.loads(obj.user_answer)
                except (json.JSONDecodeError, TypeError):
                    return obj.user_answer
            return obj.user_answer
        return None
    
    def get_correctAnswer(self, obj):
        """处理正确答案的JSON字段"""
        # 原代码：直接使用source映射
        # "correctAnswer": {"source": "correct_answer"},
        # 新代码：处理JSON反序列化
        if obj.correct_answer:
            if isinstance(obj.correct_answer, str):
                try:
                    return json.loads(obj.correct_answer)
                except (json.JSONDecodeError, TypeError):
                    return obj.correct_answer
            return obj.correct_answer
        return None
    
    def get_options(self, obj):
        """处理选项的JSON字段"""
        # 新代码：处理JSON反序列化
        if obj.options:
            if isinstance(obj.options, str):
                try:
                    return json.loads(obj.options)
                except (json.JSONDecodeError, TypeError):
                    return obj.options
            return obj.options
        return []
    
    class Meta:
        model = Question
        fields = [
            "id", "type", "difficulty", "content",
            "correct", "userAnswer", "correctAnswer",
            "options", "analysis"
        ]


