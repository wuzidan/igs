# views.py
import json
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg
from django.utils import timezone
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from question.models import DifficultyLevel, Exercise, PracticeRecord, PracticeType, Question, QuestionType
from .models import HistoryRecord


class HistoryRecordView(APIView):
    """
    提供前端所需的所有统计数据和作答记录
    """
    def get(self, request):
        # 获取当前登录用户的所有作答记录
        User = get_user_model()
        
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return Response({"error": "用户未登录"}, status=401)
        
        # 获取用户的练习记录和历史记录
        practice_records = request.user.practice_records.all()
        history_records_model = request.user.history_records.all()
        
        print(f"使用真实用户: {request.user.username} (ID: {request.user.id})")
        print(f"找到 {practice_records.count()} 条练习记录")
        print(f"找到 {history_records_model.count()} 条历史记录")

        # 1. 计算基本统计数据
        total_attempts = history_records_model.count()

        # 平均分计算
        avg_score = history_records_model.aggregate(avg=Avg('score'))['avg'] or 0
        avg_score = round(avg_score)

        # 总时长计算
        # 解析history_records_model中的duration字段，如"11分钟" → 11
        total_minutes = 0
        for record in history_records_model:
            try:
                # 提取分钟数，处理"X分钟"格式
                total_minutes += int(record.duration.split('分钟')[0])
            except (ValueError, IndexError):
                continue

        # 转换总分钟为"X小时Y分钟"格式
        total_duration = self.format_duration(total_minutes)

        # 最高分及日期
        highest_score_record = history_records_model.order_by('-score').first()
        highest_score = highest_score_record.score if highest_score_record else 0
        last_highest_date = ""
        if highest_score_record:
            # 格式化为"xx月xx日"
            last_highest_date = f"{highest_score_record.date.month}月{highest_score_record.date.day}日"

        # 2. 计算题型正确率 - 由于HistoryRecord与Question无直接关联，暂时使用默认值
        type_accuracy = {
            'singleChoice': 0,
            'multipleChoice': 0,
            'judgment': 0,
            'shortAnswer': 0
        }

        # 3. 计算难度正确率 - 由于HistoryRecord与Question无直接关联，暂时使用默认值
        difficulty_accuracy = {
            'easy': 0,
            'medium': 0,
            'hard': 0
        }

        # 4. 获取作答记录列表（使用history_records_model）
        history_records = []
        for record in history_records_model:
            # HistoryRecord没有直接关联Question模型，questions_data为空列表
            questions_data = []
            
            history_records.append({
                "id": record.id,
                "type": record.type,  # HistoryRecord的type是直接存储的字符串，如"练习"或"考试"
                "date": record.date.strftime("%Y-%m-%d %H:%M"),
                "score": record.score,
                "duration": record.duration,  # HistoryRecord的duration直接存储为字符串，如"11分钟"
                "expanded": record.expanded,
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


historyRecord = HistoryRecordView


class SubmitPracticeRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def _resolve_exercise(self, question_data):
        content_value = str(question_data.get("content") or "").strip()
        exercise_pk_candidates = [
            question_data.get("exercise_pk"),
            question_data.get("exercisePk"),
        ]
        exercise_id_candidates = [
            question_data.get("exercise_id"),
            question_data.get("exerciseId"),
        ]
        source_question_candidates = [
            question_data.get("question_id"),
            question_data.get("questionId"),
            question_data.get("id"),
        ]

        for candidate in exercise_pk_candidates:
            if candidate in (None, ""):
                continue
            try:
                exercise = Exercise.objects.filter(pk=int(candidate)).first()
                if exercise is not None:
                    return exercise
            except (TypeError, ValueError):
                pass

        for candidate in exercise_id_candidates:
            if candidate in (None, ""):
                continue
            exercise = Exercise.objects.filter(exercise_id=str(candidate)).first()
            if exercise is not None:
                return exercise

            try:
                exercise = Exercise.objects.filter(pk=int(candidate)).first()
                if exercise is not None:
                    return exercise
            except (TypeError, ValueError):
                pass

        for candidate in source_question_candidates:
            if candidate in (None, ""):
                continue

            try:
                source_question = Question.objects.select_related("exercise").filter(pk=int(candidate)).first()
                if source_question is not None and source_question.exercise is not None:
                    return source_question.exercise
                if source_question is not None and not content_value:
                    content_value = str(source_question.content or "").strip()
            except (TypeError, ValueError):
                pass

        if content_value:
            matched_question = (
                Question.objects.select_related("exercise")
                .filter(content=content_value, exercise__isnull=False)
                .order_by("-id")
                .first()
            )
            if matched_question is not None and matched_question.exercise is not None:
                return matched_question.exercise

            matched_exercise = Exercise.objects.filter(name=content_value).first()
            if matched_exercise is not None:
                return matched_exercise

        return None

    def post(self, request):
        payload = request.data
        questions = payload.get("questions", [])
        if isinstance(questions, str):
            try:
                questions = json.loads(questions)
            except json.JSONDecodeError:
                return Response({"error": "questions 字段必须是合法 JSON"}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(questions, list) or not questions:
            return Response({"error": "questions 不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        practice_type = payload.get("practice_type") or payload.get("type") or PracticeType.PRACTICE
        if practice_type not in PracticeType.values:
            practice_type = PracticeType.PRACTICE

        duration_value = payload.get("duration_minutes") or payload.get("durationMinutes") or 1
        try:
            duration_minutes = max(1, int(duration_value))
        except (TypeError, ValueError):
            duration_minutes = 1

        submitted_at = timezone.now()
        correct_count = sum(1 for item in questions if isinstance(item, dict) and bool(item.get("correct")))
        explicit_score = payload.get("score")
        try:
            score = int(round(float(explicit_score))) if explicit_score is not None else round(correct_count * 100 / len(questions))
        except (TypeError, ValueError, ZeroDivisionError):
            score = round(correct_count * 100 / len(questions)) if questions else 0
        score = max(0, min(100, score))

        created_questions = 0
        mapped_questions = 0

        with transaction.atomic():
            practice_record = PracticeRecord.objects.create(
                student=request.user,
                type=practice_type,
                date=submitted_at,
                score=score,
                duration_minutes=duration_minutes,
            )

            for index, question_data in enumerate(questions):
                if not isinstance(question_data, dict):
                    continue

                question_type = question_data.get("type") or QuestionType.SINGLE_CHOICE
                if question_type not in QuestionType.values:
                    question_type = QuestionType.SINGLE_CHOICE

                difficulty = question_data.get("difficulty") or DifficultyLevel.MEDIUM
                if difficulty not in DifficultyLevel.values:
                    difficulty = DifficultyLevel.MEDIUM

                exercise = self._resolve_exercise(question_data)
                if exercise is not None:
                    mapped_questions += 1

                Question.objects.create(
                    record=practice_record,
                    exercise=exercise,
                    type=question_type,
                    difficulty=difficulty,
                    content=str(question_data.get("content") or f"题目 {index + 1}"),
                    correct=bool(question_data.get("correct")),
                    user_answer=question_data.get("user_answer", question_data.get("userAnswer")),
                    correct_answer=question_data.get("correct_answer", question_data.get("correctAnswer", [])),
                    options=question_data.get("options"),
                    analysis=question_data.get("analysis") or "",
                )
                created_questions += 1

            if created_questions == 0:
                return Response({"error": "没有可保存的题目数据"}, status=status.HTTP_400_BAD_REQUEST)

            HistoryRecord.objects.create(
                user=request.user,
                type="练习" if practice_type == PracticeType.PRACTICE else "考试",
                date=submitted_at,
                score=score,
                duration=f"{duration_minutes}分钟",
                expanded=False,
            )

        return Response(
            {
                "status": "success",
                "practice_record_id": practice_record.id,
                "saved_questions": created_questions,
                "mapped_questions": mapped_questions,
                "unmapped_questions": max(created_questions - mapped_questions, 0),
                "correct_questions": correct_count,
                "score": score,
                "duration_minutes": duration_minutes,
                "submitted_at": submitted_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )
