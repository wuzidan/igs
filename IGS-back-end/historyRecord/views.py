# views.py
from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from question.models import Question
from .models import HistoryRecord


class historyRecord(APIView):
    """
    提供前端所需的所有统计数据和作答记录
    """
    def get(self, request):
        # 获取当前用户的所有作答记录
        # 调试专用：优先使用testuser用户
        User = get_user_model()
        try:
            # 优先尝试使用testuser用户
            test_user = User.objects.get(username='testuser')
            request.user = test_user  # 覆盖匿名用户
            print(f"使用测试用户: {test_user.username} (ID: {test_user.id})")
        except User.DoesNotExist:
            try:
                # 如果testuser不存在，尝试使用ID=1的用户
                test_user = User.objects.get(id=1)
                request.user = test_user
                print(f"使用ID=1的用户: {test_user.username}")
            except User.DoesNotExist:
                return Response({"error": "测试用户不存在"}, status=400)

        # 获取用户的练习记录和历史记录
        practice_records = request.user.practice_records.all()
        history_records_model = request.user.history_records.all()
        
        print(f"找到 {practice_records.count()} 条练习记录")
        print(f"找到 {history_records_model.count()} 条历史记录")

        # 1. 计算基本统计数据
        total_attempts = practice_records.count()

        # 平均分计算
        avg_score = practice_records.aggregate(avg=Avg('score'))['avg'] or 0
        avg_score = round(avg_score)

        # 总时长计算（直接使用practice_records中的duration_minutes字段）
        total_minutes = sum(record.duration_minutes for record in practice_records)

        # 转换总分钟为"X小时Y分钟"格式
        total_duration = self.format_duration(total_minutes)

        # 最高分及日期
        highest_score_record = practice_records.order_by('-score').first()
        highest_score = highest_score_record.score if highest_score_record else 0
        last_highest_date = ""
        if highest_score_record:
            # 格式化为"10月10日"
            last_highest_date = f"{highest_score_record.date.month}月{highest_score_record.date.day}日"

        # 2. 计算题型正确率
        all_questions = Question.objects.filter(record__in=practice_records)
        print(f"找到 {all_questions.count()} 道题目记录")
        type_accuracy = self.calculate_type_accuracy(all_questions)

        # 3. 计算难度正确率
        difficulty_accuracy = self.calculate_difficulty_accuracy(all_questions)

        # 4. 获取作答记录列表（使用practice_records，因为题目直接关联到它）
        history_records = []
        for record in practice_records:
            questions_data = []
            for q in record.questions.all():
                questions_data.append({
                    "id": q.id,
                    "type": q.type,
                    "difficulty": q.difficulty,
                    "content": q.content,
                    "correct": q.correct,
                    "userAnswer": q.get_user_answer_list(),
                    "correctAnswer": q.get_correct_answer_list(),
                    "options": q.get_options_list(),
                    "analysis": q.analysis
                })
            
            history_records.append({
                "id": record.id,
                "type": record.get_type_display(),
                "date": record.date.strftime("%Y-%m-%d %H:%M"),
                "score": record.score,
                "duration": f"{record.duration_minutes}分钟",
                "expanded": False,
                "questions": questions_data
            })

        # 确保按日期降序排序
        history_records.sort(key=lambda x: x['date'], reverse=True)
        
        # 构建返回数据
        response_data = {
            'totalAttempts': total_attempts,
            'avgScore': avg_score,
            'totalDuration': total_duration,
            'highestScore': highest_score,
            'lastHighestDate': last_highest_date,
            'typeAccuracy': type_accuracy,
            'difficultyAccuracy': difficulty_accuracy,
            'historyRecords': history_records
        }
        
        print("返回数据:", response_data)
        return Response(response_data)

    def format_duration(self, total_minutes):
        """将总分钟数格式化为"X小时Y分钟"格式"""
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"

    def calculate_type_accuracy(self, questions):
        """计算各题型的正确率"""
        # 所有可能的题型
        question_types = ['singleChoice', 'multipleChoice', 'judgment', 'shortAnswer']
        accuracy = {}

        for q_type in question_types:
            # 筛选该类型的所有题目
            type_questions = questions.filter(type=q_type)
            total = type_questions.count()

            if total == 0:
                accuracy[q_type] = 0
                continue

            # 计算正确的题目数量
            correct = type_questions.filter(correct=True).count()

            # 计算正确率并四舍五入
            accuracy[q_type] = round((correct / total) * 100)

        return accuracy

    def calculate_difficulty_accuracy(self, questions):
        """计算各难度的正确率"""
        # 所有可能的难度级别
        difficulties = ['easy', 'medium', 'hard']
        accuracy = {}

        for difficulty in difficulties:
            # 筛选该难度的所有题目
            diff_questions = questions.filter(difficulty=difficulty)
            total = diff_questions.count()

            if total == 0:
                accuracy[difficulty] = 0
                continue

            # 计算正确的题目数量
            correct = diff_questions.filter(correct=True).count()

            # 计算正确率并四舍五入
            accuracy[difficulty] = round((correct / total) * 100)

        return accuracy


