from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Sum
import random

from student.models import User
from .models import KnowledgePoint


class KnowledgeStructureView(APIView):
    # """知识点结构数据接口"""
    # permission_classes = [IsAuthenticated]  # 仅登录用户可访问
    permission_classes = []
    def get(self, request):
        # 直接返回模拟数据，确保前端显示有意义的内容
        return self.get_mock_data()

        # 以下是原始逻辑，暂时注释掉
        # 获取测试用户
        # test_user = User.objects.filter(id=1).first()
        # if not test_user:
        #     # 即使没有用户，也返回模拟数据
        #     return self.get_mock_data()

        # # 获取用户的知识点数据
        # knowledge_points = KnowledgePoint.objects.filter(user=test_user)

        # # 如果数据库中没有数据，返回模拟数据
        # if not knowledge_points.exists():
        #     return self.get_mock_data()

        # 计算统计数据
        total_count = knowledge_points.count()  # 总知识点数量
        mastered_count = knowledge_points.filter(mastery__gte=60).count()  # 掌握的知识点（假设≥60为掌握）
        coverage_rate = (mastered_count / total_count) * 100 if total_count > 0 else 0  # 覆盖率
        avg_mastery = knowledge_points.aggregate(avg=Avg("mastery"))["avg"] or 0  # 平均掌握程度

        # 格式化知识点列表
        knowledge_list = [
            {
                "id": point.id,
                "name": point.name,
                "category": point.category,
                "categoryText": point.get_category_display(),  # 显示分类文本（如"核心知识点"）
                "mastery": point.mastery,
                "description": point.description,
                "practiceCount": point.practice_count,
                "lastPracticed": point.last_practiced.strftime("%Y-%m-%d") if point.last_practiced else None,
            }
            for point in knowledge_points
        ]

        # 返回前端所需的完整数据结构
        return Response({
            "coverageRate": round(coverage_rate),  # 四舍五入为整数
            "masteredCount": mastered_count,
            "totalCount": total_count,
            "avgMastery": round(avg_mastery),
            "knowledgeList": knowledge_list
        })
    
    def get_mock_data(self):
        # 生成模拟的知识点数据
        mock_knowledge_points = [
            {
                "id": 1,
                "name": "变量与数据类型",
                "category": "core",
                "categoryText": "核心知识点",
                "mastery": 65,
                "description": "学习Python中的基本数据类型、变量定义和类型转换",
                "practiceCount": 15,
                "lastPracticed": "2024-01-15"
            },
            {
                "id": 2,
                "name": "控制结构",
                "category": "core",
                "categoryText": "核心知识点",
                "mastery": 50,
                "description": "掌握条件语句和循环结构的使用",
                "practiceCount": 12,
                "lastPracticed": "2024-01-18"
            },
            {
                "id": 3,
                "name": "函数模块",
                "category": "core",
                "categoryText": "核心知识点",
                "mastery": 75,
                "description": "学习函数定义、参数传递和返回值",
                "practiceCount": 10,
                "lastPracticed": "2024-01-20"
            },
            {
                "id": 4,
                "name": "数据结构基础",
                "category": "important",
                "categoryText": "重要知识点",
                "mastery": 45,
                "description": "掌握列表、元组、字典和集合的基本操作",
                "practiceCount": 8,
                "lastPracticed": "2024-01-22"
            },
            {
                "id": 5,
                "name": "算法分析",
                "category": "important",
                "categoryText": "重要知识点",
                "mastery": 30,
                "description": "学习时间复杂度和空间复杂度的分析方法",
                "practiceCount": 5,
                "lastPracticed": "2024-01-25"
            },
            {
                "id": 6,
                "name": "文件操作",
                "category": "general",
                "categoryText": "一般知识点",
                "mastery": 60,
                "description": "学习文件的读写操作和异常处理",
                "practiceCount": 6,
                "lastPracticed": "2024-01-28"
            }
        ]
        
        # 计算统计数据
        total_count = len(mock_knowledge_points)
        mastered_count = sum(1 for point in mock_knowledge_points if point['mastery'] >= 60)
        coverage_rate = (mastered_count / total_count) * 100 if total_count > 0 else 0
        avg_mastery = sum(point['mastery'] for point in mock_knowledge_points) / total_count if total_count > 0 else 0
        
        # 返回模拟数据
        return Response({
            "coverageRate": round(coverage_rate),  # 四舍五入为整数
            "masteredCount": mastered_count,
            "totalCount": total_count,
            "avgMastery": round(avg_mastery),
            "knowledgeList": mock_knowledge_points
        })