from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


# 1. 课程进度模型（记录用户课程完成情况）
class CourseProgress(models.Model):
    """用户的课程学习进度模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_progresses",
        verbose_name="关联用户"
    )
    course_name = models.CharField(
        "课程名称",
        max_length=100,
        help_text="如：Python编程基础"
    )
    is_completed = models.BooleanField(
        "是否完成",
        default=False,
        help_text="标记课程是否已完成"
    )
    score = models.IntegerField(
        "课程成绩",
        default=0,
        # 使用正确导入的验证器
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="课程得分（0-100）"
    )
    last_studied = models.DateTimeField(
        "最后学习时间",
        auto_now=True,
        help_text="最后一次学习该课程的时间"
    )

    class Meta:
        verbose_name = "课程进度"
        verbose_name_plural = "课程进度"
        unique_together = ("user", "course_name")  # 同一用户的课程不重复

    def __str__(self):
        status = "已完成" if self.is_completed else "未完成"
        return f"{self.user.name}的课程：{self.course_name}（{status}）"


# 2. 编程技能模型（记录用户各技能掌握程度）
class ProgrammingSkill(models.Model):
    """用户的编程技能模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="programming_skills",
        verbose_name="关联用户"
    )
    name = models.CharField(
        "技能名称",
        max_length=50,
        help_text="如：JavaScript、Python"
    )
    icon = models.CharField(
        "技能图标（emoji）",
        max_length=10,
        help_text="技能对应的emoji图标，如⚡、🐍"
    )
    level = models.IntegerField(
        "技能水平",
        # 同样使用正确导入的验证器
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="技能掌握程度（0-100）"
    )

    # ..
    class Meta:
        verbose_name = "编程技能"
        verbose_name_plural = "编程技能"
        unique_together = ("user", "name")  # 同一用户的技能不重复

    def __str__(self):
        return f"{self.user.name}的技能：{self.name}（{self.level}分）"


from django.db import models

# Create your models here.
