from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from question.models import Question
from datetime import datetime, timedelta
import random


class KnowledgeVisualizationView(APIView):
    """学习可视化数据接口（使用实际的答题历史数据）"""
    permission_classes = []  # 测试阶段允许匿名访问

    def get(self, request):
        # 开发阶段：优先使用testuser用户
        User = get_user_model()
        try:
            # 优先尝试使用testuser用户
            user = User.objects.get(username='testuser')
            print(f"使用测试用户: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            try:
                # 如果testuser不存在，尝试使用ID=1的用户
                user = User.objects.get(id=1)
                print(f"使用ID=1的用户: {user.username}")
            except User.DoesNotExist:
                return Response({
                    "error": "测试用户不存在，请先创建用户"},
                    status=400
                )

        # 1. 获取用户的练习记录
        practice_records = user.practice_records.all()
        
        # 2. 计算整体统计数据
        total_attempts = practice_records.count()
        
        # 正确统计答题数据：通过关联关系获取所有题目
        # 获取所有练习记录关联的题目
        all_questions = []
        for record in practice_records:
            # 收集每个练习记录的所有题目
            all_questions.extend(record.questions.all())
        
        total_questions = len(all_questions)
        correct_questions = sum(1 for q in all_questions if q.correct)
        
        # 计算正确率
        accuracy = (correct_questions / total_questions * 100) if total_questions > 0 else 0
        
        # 计算平均得分
        avg_score = practice_records.aggregate(avg=Avg('score'))['avg'] or 0
        avg_score = round(avg_score)
        
        # 计算总时长（分钟）
        total_minutes = sum(record.duration_minutes for record in practice_records)
        
        # 3. 模拟课程进度数据（基于实际答题情况）
        # 根据练习次数和正确率生成合理的进度
        if total_attempts > 0:
            overall_progress = min(100, accuracy * 1.2)  # 进度略高于正确率
            completed_courses = int(total_attempts * 0.8)  # 每5次练习完成4门课程
            total_courses = max(completed_courses + 3, 10)  # 总课程数至少10门
        else:
            # 如果没有练习记录，提供一些基础数据
            overall_progress = 15
            completed_courses = 2
            total_courses = 10
            avg_score = 70
        
        # 4. 生成知识掌握度数据（六边形图）
        knowledge_areas = ['HTML', 'CSS', 'JavaScript', '数据库', '算法', '网络']
        knowledge_mastery = []
        
        # 根据练习记录生成知识掌握度数据
        if total_questions > 0:
            # 基于正确率生成不同知识点的掌握度，添加一些随机性
            base_mastery = accuracy * 0.7  # 基础掌握度
            for area in knowledge_areas:
                # 每个知识领域有不同的掌握度，添加随机波动
                mastery_level = min(100, max(10, base_mastery + random.randint(-20, 20)))
                knowledge_mastery.append({
                    "name": area,
                    "value": round(mastery_level)
                })
        else:
            # 如果没有练习记录，提供模拟数据
            knowledge_mastery = [
                {"name": "HTML", "value": 60},
                {"name": "CSS", "value": 40},
                {"name": "JavaScript", "value": 20},
                {"name": "数据库", "value": 10},
                {"name": "算法", "value": 30},
                {"name": "网络", "value": 50}
            ]
        
        # 5. 生成学习时长数据（按月统计）
        months = ['1月', '2月', '3月', '4月', '5月']
        study_time_data = []
        
        # 根据总时长生成月度学习时间分布
        if total_minutes > 0:
            # 将总时长分配到各个月份，最近月份学习时间较长
            weights = [0.8, 1.2, 1.5, 1.1, 1.0]  # 各月份权重
            total_weight = sum(weights)
            total_hours = total_minutes / 60  # 转换为小时
            
            for i, month in enumerate(months):
                hours = (total_hours * weights[i] / total_weight) + random.randint(5, 15)  # 添加一些基础时间
                study_time_data.append({
                    "month": month,
                    "hours": round(hours)
                })
        else:
            # 模拟学习时长数据
            study_time_data = [
                {"month": "1月", "hours": 15},
                {"month": "2月", "hours": 40},
                {"month": "3月", "hours": 55},
                {"month": "4月", "hours": 45},
                {"month": "5月", "hours": 35}
            ]
        
        # 6. 格式化响应数据，确保与前端期望的结构一致
        # 转换知识掌握度为数字数组
        mastery_values = [area["value"] for area in knowledge_mastery]
        
        # 转换学习时长为前端需要的格式
        learning_months = [item["month"] for item in study_time_data]
        learning_hours = [item["hours"] for item in study_time_data]
        
        # 生成技能数据
        skills = []
        if total_questions > 0:
            # 基于知识掌握度生成技能数据
            skill_base = accuracy * 0.8
            skills = [
                {"name": "JavaScript", "icon": "⚡", "level": round(min(100, skill_base + random.randint(10, 30)))},
                {"name": "Python", "icon": "🐍", "level": round(min(100, skill_base + random.randint(-10, 20)))},
                {"name": "Java", "icon": "☕", "level": round(min(100, skill_base + random.randint(-20, 10)))},
                {"name": "HTML/CSS", "icon": "🌐", "level": round(min(100, skill_base + random.randint(0, 30)))},
                {"name": "Git", "icon": "🔀", "level": round(min(100, skill_base + random.randint(-15, 15)))},
                {"name": "SQL", "icon": "🗃️", "level": round(min(100, skill_base + random.randint(-5, 25)))}
            ]
        else:
            # 模拟技能数据
            skills = [
                {"name": "JavaScript", "icon": "⚡", "level": 75},
                {"name": "Python", "icon": "🐍", "level": 65},
                {"name": "Java", "icon": "☕", "level": 50},
                {"name": "HTML/CSS", "icon": "🌐", "level": 85},
                {"name": "Git", "icon": "🔀", "level": 60},
                {"name": "SQL", "icon": "🗃️", "level": 55}
            ]
        
        return Response({
            # 学习进度数据
            "overallProgress": round(overall_progress),
            "completedCourses": completed_courses,
            "totalCourses": total_courses,
            "avgScore": avg_score,
            "userName": getattr(user, 'name', '测试用户'),  # 从User模型获取
            "studentId": getattr(user, 'student_id', '20230001'),
            "userAvatar": getattr(user, 'user_avatar_emoji', '👨‍🎓'),
            # 答题统计
            "accuracy": round(accuracy),
            "totalQuestions": total_questions,
            # 知识掌握度（前端期望的数字数组）
            "knowledgeMastery": mastery_values,
            # 学习时长数据（前端期望的格式）
            "learningMonths": learning_months,
            "learningHours": learning_hours,
            # 技能数据
            "skills": skills,
            # 保留原有格式以兼容其他可能的前端使用
            "studyTime": study_time_data
        })



from django.shortcuts import render

# Create your views here.
