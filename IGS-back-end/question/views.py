# question/views.py
from django.views import View
from django.http import JsonResponse
from .models import Exercise

# 类视图（class 定义，继承自 View 或其子类）
class question(View):
    def get(self, request):
        # 从Exercise模型中获取数据
        exercises = Exercise.objects.all()
        
        # 转换为前端期望的格式
        question_data = {
            "data": [
                {
                    "id": exercise.exercise_id,
                    "title": exercise.name,
                    "subjectId": 1,  # 默认设置为编程基础
                    "difficulty": "medium",  # 默认设置为中等难度
                    "type": 0,  # 默认设置为单选题
                    "creator": "admin",  # 默认设置为管理员
                    "createTime": exercise.created_at,
                    "useCount": exercise.visits,  # 前端使用useCount，后端是visits
                    # 其他字段供未来扩展使用
                    "quiz": exercise.name,
                    "status": exercise.status,
                    "publishTime": exercise.publish_time,
                    "result": "",
                    "analysis": ""
                }
                for exercise in exercises
            ]
        }
        return JsonResponse(question_data, safe=False)