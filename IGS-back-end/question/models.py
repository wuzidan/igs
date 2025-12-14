import student
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings  # 导入settings
import json

# 练习记录类型枚举
class PracticeType(models.TextChoices):
    PRACTICE = '练习', '练习'
    MOCK_EXAM = '模拟考试', '模拟考试'
    OFFICIAL_EXAM = '正式考试', '正式考试'


# 练习记录模型
class PracticeRecord(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 引用配置的用户模型
        on_delete=models.CASCADE,
        related_name='practice_records',
        verbose_name="用户",
        help_text="关联的用户"
    )
    type = models.CharField(
        "类型",
        max_length=10,
        choices=PracticeType.choices,
        default=PracticeType.PRACTICE,
        help_text="练习类型"
    )
    date = models.DateTimeField(
        "日期时间",
        default=timezone.now,
        help_text="练习发生的时间"
    )
    score = models.IntegerField(
        "得分",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="本次练习得分"
    )
    duration_minutes = models.PositiveIntegerField(
        "时长(分钟)",
        help_text="练习持续时间（分钟）"
    )

    class Meta:
        verbose_name = "练习记录"
        verbose_name_plural = "练习记录"
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.name} - {self.get_type_display()} - {self.score}分"


# 题目类型枚举
class QuestionType(models.TextChoices):
    SINGLE_CHOICE = 'singleChoice', '单选题'
    MULTIPLE_CHOICE = 'multipleChoice', '多选题'
    JUDGMENT = 'judgment', '判断题'
    SHORT_ANSWER = 'shortAnswer', '简答题'


# 题目难度枚举
class DifficultyLevel(models.TextChoices):
    EASY = 'easy', '简单'
    MEDIUM = 'medium', '中等'
    HARD = 'hard', '困难'


# 练习题模型
class Exercise(models.Model):
    exercise_id = models.CharField(
        "练习题ID",
        max_length=100,
        unique=True,
        help_text="练习题的唯一标识符"
    )
    name = models.CharField(
        "练习题名称",
        max_length=200,
        help_text="练习题的名称"
    )
    visits = models.IntegerField(
        "访问次数",
        default=0,
        help_text="练习题的访问次数"
    )
    status = models.CharField(
        "状态",
        max_length=50,
        blank=True,
        null=True,
        help_text="练习题的状态"
    )
    fork_from = models.CharField(
        "来源练习题",
        max_length=100,
        blank=True,
        null=True,
        help_text="从哪个练习题复刻而来"
    )
    created_at = models.DateTimeField(
        "创建时间",
        help_text="练习题的创建时间"
    )
    publish_time = models.DateTimeField(
        "发布时间",
        blank=True,
        null=True,
        help_text="练习题的发布时间"
    )

    class Meta:
        verbose_name = "练习题"
        verbose_name_plural = "练习题"
        ordering = ['exercise_id']

    def __str__(self):
        return self.name


# 题目模型
class Question(models.Model):
    record = models.ForeignKey(
        PracticeRecord,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="练习记录",
        help_text="关联的练习记录"
    )
    # 新增：关联练习题（如果Question与Exercise有关联）
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='questions',
        verbose_name="关联练习题",
        help_text="关联的练习题"
    )
    type = models.CharField(
        "类型",
        max_length=20,
        choices=QuestionType.choices,
        help_text="题目类型"
    )
    difficulty = models.CharField(
        "难度",
        max_length=10,
        choices=DifficultyLevel.choices,
        help_text="题目难度级别"
    )
    content = models.TextField(
        "题目内容",
        help_text="题目的文本内容"
    )
    correct = models.BooleanField(
        "是否正确",
        help_text="用户是否答对"
    )

    # JSON字段用于存储答案和选项
    user_answer = models.JSONField(
        "用户答案",
        blank=True,
        null=True,
        help_text="用户的答案（JSON格式）"
    )
    correct_answer = models.JSONField(
        "正确答案",
        help_text="题目的正确答案（JSON格式）"
    )
    options = models.JSONField(
        "选项",
        blank=True,
        null=True,
        help_text="题目的选项（JSON格式）"
    )
    analysis = models.TextField(
        "解析",
        blank=True,
        help_text="题目的解析说明"
    )

    class Meta:
        verbose_name = "题目"
        verbose_name_plural = "题目"
        ordering = ['id']

    def __str__(self):
        return f"{self.get_type_display()} - {self.content[:30]}..."

    def get_options_list(self):
        """将JSON选项转换为列表"""
        if not self.options:
            return []
        if isinstance(self.options, str):
            try:
                return json.loads(self.options)
            except (json.JSONDecodeError, TypeError):
                return []
        return self.options

    def get_user_answer_list(self):
        """将JSON用户答案转换为可序列化的Python对象"""
        if self.user_answer is None:
            return []
        if isinstance(self.user_answer, str):
            try:
                return json.loads(self.user_answer)
            except (json.JSONDecodeError, TypeError):
                return self.user_answer
        return self.user_answer

    def get_correct_answer_list(self):
        """将JSON正确答案转换为可序列化的Python对象"""
        if self.correct_answer is None:
            return []
        if isinstance(self.correct_answer, str):
            try:
                return json.loads(self.correct_answer)
            except (json.JSONDecodeError, TypeError):
                return self.correct_answer
        return self.correct_answer


# 挑战题模型
class Challenge(models.Model):
    """挑战题模型"""
    challenge_id = models.CharField(
        "挑战题ID",
        max_length=100,
        unique=True,
        help_text="挑战题的唯一标识符"
    )
    name = models.CharField(
        "题目名称",
        max_length=200,
        help_text="题目的名称"
    )
    task_pass = models.TextField(
        "任务说明",
        default="",
        help_text="题目的任务说明和内容"
    )
    answer = models.TextField(
        "答案",
        help_text="题目的答案"
    )
    score = models.IntegerField(
        "分数",
        default=0,
        help_text="题目分数"
    )
    difficulty = models.CharField(
        "难度级别",
        max_length=10,
        choices=DifficultyLevel.choices,
        help_text="题目的难度级别"
    )
    praises_count = models.IntegerField(
        "点赞数",
        default=0,
        help_text="题目点赞数"
    )

    class Meta:
        verbose_name = "挑战题"
        verbose_name_plural = "挑战题"
        ordering = ['challenge_id']

    def __str__(self):
        return self.name


# 练习题与挑战题的关系模型
class ExerciseChallenge(models.Model):
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='exercise_challenges',
        verbose_name="练习题",
        help_text="关联的练习题"
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='exercise_challenges',
        verbose_name="挑战题",
        help_text="关联的挑战题"
    )

    class Meta:
        verbose_name = "练习题与挑战题关联"
        verbose_name_plural = "练习题与挑战题关联"
        db_table = 'exercise_challenge'  #与CSV文件名对应
        unique_together = ('exercise', 'challenge')  #确保每个练习题与挑战题的组合唯一

    def __str__(self):
        return f"{self.exercise.name} - {self.challenge.name}"