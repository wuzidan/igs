from django.db import models
from django.contrib.auth.models import User  # 假设关联用户
from django.conf import settings  # 导入 settings 模块
from question.models import QuestionType, Question, DifficultyLevel


class HistoryRecord(models.Model):
    """作答记录主表（对应historyRecords中的每个对象）"""
    TYPE_CHOICES = [
        ("练习", "练习"),
        ("考试", "考试"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 关键：改为引用配置的用户模型
        on_delete=models.CASCADE,
        related_name="history_records"
    )#关联用户
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)  # 类型：练习/考试
    date = models.DateTimeField()  # 作答时间
    score = models.IntegerField()  # 得分
    duration = models.CharField(max_length=20)  # 时长（如"25分钟"）
    expanded = models.BooleanField(default=False)  # 是否展开详情

    # 统计用户历史答题数据
    class UserStatistics(models.Model):
        user = models.ForeignKey(
            settings.AUTH_USER_MODEL,  # 关键：改为引用配置的用户模型
            on_delete=models.CASCADE,
            primary_key=True,
            related_name='statistics',
            verbose_name="用户",
            help_text="关联的用户"
        )
        total_attempts = models.PositiveIntegerField(
            "总练习次数",
            default=0,
            help_text="用户的总练习次数"
        )
        avg_score = models.DecimalField(
            "平均得分",
            max_digits=5,
            decimal_places=2,
            default=0.00,
            help_text="用户的平均得分"
        )
        total_duration_minutes = models.PositiveIntegerField(
            "总时长(分钟)",
            default=0,
            help_text="用户的总练习时长（分钟）"
        )
        highest_score = models.PositiveIntegerField(
            "最高得分",
            default=0,
            help_text="用户的最高得分"
        )
        last_highest_date = models.DateField(
            "最高分日期",
            blank=True,
            null=True,
            help_text="用户最近一次获得最高分的日期"
        )

        # JSON字段用于存储正确率
        type_accuracy = models.JSONField(
            "题型正确率",
            blank=True,
            null=True,
            help_text="各题型的正确率（JSON格式）"
        )
        difficulty_accuracy = models.JSONField(
            "难度正确率",
            blank=True,
            null=True,
            help_text="各难度题目的正确率（JSON格式）"
        )

        last_updated = models.DateTimeField(
            "最后更新时间",
            auto_now=True,
            help_text="统计数据的最后更新时间"
        )

        class Meta:
            verbose_name = "用户统计"
            verbose_name_plural = "用户统计"

        def __str__(self):
            return f"{self.user.name}的统计数据"

        def update_statistics(self):
            """更新用户统计数据"""
            from django.db.models import Count, Avg, Max, Sum

            # 获取用户的所有练习记录
            # 原代码：records = self.user.practice_records.all()
            # 新代码：使用正确的related_name
            records = self.user.history_records.all()

            # 计算基础统计
            self.total_attempts = records.count()
            self.avg_score = records.aggregate(avg_score=Avg('score'))['avg_score'] or 0
            self.total_duration_minutes = records.aggregate(total_duration=Sum('duration_minutes'))[
                                              'total_duration'] or 0

            # 获取最高分和日期
            max_score = records.aggregate(max_score=Max('score'))['max_score']
            if max_score:
                self.highest_score = max_score
                latest_max = records.filter(score=max_score).order_by('-date').first()
                if latest_max:
                    self.last_highest_date = latest_max.date.date()

            # 计算题型正确率
            type_accuracy = {}
            for q_type in QuestionType.values:
                correct_count = Question.objects.filter(
                    record__user=self.user,
                    type=q_type,
                    correct=True
                ).count()
                total_count = Question.objects.filter(
                    record__user=self.user,
                    type=q_type
                ).count()

                accuracy = round((correct_count / total_count * 100) if total_count > 0 else 0)
                type_accuracy[q_type] = accuracy

            self.type_accuracy = type_accuracy

            # 计算难度正确率
            difficulty_accuracy = {}
            for diff in DifficultyLevel.values:
                correct_count = Question.objects.filter(
                    record__user=self.user,
                    difficulty=diff,
                    correct=True
                ).count()
                total_count = Question.objects.filter(
                    record__user=self.user,
                    difficulty=diff
                ).count()

                accuracy = round((correct_count / total_count * 100) if total_count > 0 else 0)
                difficulty_accuracy[diff] = accuracy

            self.difficulty_accuracy = difficulty_accuracy

            self.save()

        def get_type_accuracy_dict(self):
            """获取题型正确率字典"""
            if self.type_accuracy:
                return self.type_accuracy
            return {
                'singleChoice': 0,
                'multipleChoice': 0,
                'judgment': 0,
                'shortAnswer': 0
            }

        def get_difficulty_accuracy_dict(self):
            """获取难度正确率字典"""
            if self.difficulty_accuracy:
                return self.difficulty_accuracy
            return {
                'easy': 0,
                'medium': 0,
                'hard': 0
            }

    def __str__(self):
        return f"{self.user.username}的{self.type}记录（{self.date}）"

