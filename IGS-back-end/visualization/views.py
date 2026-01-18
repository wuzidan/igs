from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from question.models import Question
from historyRecord.models import HistoryRecord
from datetime import datetime, timedelta
from django.utils import timezone
import random


class KnowledgeVisualizationView(APIView):
    """学习可视化数据接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. 获取用户的历史答题记录
        history_records = user.history_records.all()
        
        # 2. 计算整体统计数据
        total_attempts = history_records.count()
        
        # 从historyrecord表中获取数据
        total_questions = history_records.count()
        
        # 计算正确题数（score > 0表示正确）
        correct_questions = history_records.filter(score__gt=0).count()
        
        # 计算正确率
        accuracy = (correct_questions / total_questions * 100) if total_questions > 0 else 0
        
        # 计算平均得分
        avg_score = history_records.aggregate(avg=Avg('score'))['avg'] or 0
        avg_score = round(avg_score)
        
        # 计算总时长
        # duration转换为分钟数
        total_minutes = 0
        for record in history_records:
            # 尝试从duration字段提取分钟数
            duration_str = record.duration
            try:
                # 从字符串中提取数字
                minutes = int(''.join(filter(str.isdigit, duration_str)))
                total_minutes += minutes
            except ValueError:
                continue
        
        # 3. 模拟课程进度数据
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
        
        # 4. 生成学习时长数据（按全年12个月统计）
        study_time_data = []
        
        # 1. 从history_records中获取真实的学习时长数据，按月份统计
        # 先创建一个字典来存储每个月份的总学习时长（分钟）
        monthly_minutes = {}
        
        # 遍历所有历史记录，统计每个月份的学习时长
        for record in history_records:
            # 获取记录的月份数字（1-12）
            record_month_num = record.date.month
            # 使用月份数字作为键
            
            # 解析duration字段，提取分钟数
            try:
                # 从字符串中提取数字部分
                duration_str = record.duration
                minutes = int(''.join(filter(str.isdigit, duration_str)))
                
                # 累加到对应月份的总时长中
                if record_month_num in monthly_minutes:
                    monthly_minutes[record_month_num] += minutes
                else:
                    monthly_minutes[record_month_num] = minutes
            except ValueError:
                # 如果解析失败，跳过这条记录
                continue
        
        # 2. 生成全年12个月的数据，从1月到12月
        for month_num in range(1, 13):
            # 获取该月份的总分钟数，如果没有记录则为0
            minutes = monthly_minutes.get(month_num, 0)
            # 转换为小时，保留一位小数
            hours = round(minutes / 60, 1)
            # 生成月份标签（如：1月, 2月, ..., 12月）
            month_name = f"{month_num}月"
            
            study_time_data.append({
                "month": month_name,
                "hours": hours
            })
        
        # 5. 格式化响应数据，确保与前端期望的结构一致
        # 转换学习时长为前端需要的格式
        learning_months = [item["month"] for item in study_time_data]
        learning_hours = [item["hours"] for item in study_time_data]
        
        # 生成技能数据
        skills = []
        if total_questions > 0:
            # 基于正确率生成技能数据
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
            "userName": getattr(user, 'name', '') or getattr(user, 'first_name', ''),
            "studentId": getattr(user, 'student_id', ''),
            "userAvatar": getattr(user, 'user_avatar_emoji', '👨‍🎓'),
            # 答题统计
            "accuracy": round(accuracy),
            "totalQuestions": total_questions,
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
