from django.db import models
from django.conf import settings


class KnowledgePoint(models.Model):
    """知识点模型"""
    # 分类选项（对应category和categoryText）
    CATEGORY_CHOICES = [
        ("core", "核心知识点"),
        ("basic", "基础知识点"),
        ("advanced", "高级知识点"),
        ("extended", "扩展知识点"),
    ]

    name = models.CharField(
        "知识点名称",
        max_length=100,
        help_text="如：变量与数据类型"
    )
    category = models.CharField(
        "分类标识",
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="如：core/basic"
    )
    mastery = models.IntegerField(
        "掌握程度",
        help_text="掌握百分比（0-100）"
    )
    description = models.TextField(
        "知识点描述",
        help_text="对知识点的说明"
    )
    practice_count = models.IntegerField(
        "练习次数",
        default=0,
        help_text="该知识点的练习次数"
    )
    last_practiced = models.DateField(
        "最后练习时间",
        null=True,
        blank=True,
        help_text="最后一次练习的日期"
    )
    # 关联用户（如果知识点掌握程度是用户个性化数据）
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_knowledge_points",
        help_text="关联的用户"
    )

    class Meta:
        verbose_name = "知识点"
        verbose_name_plural = "知识点"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}（{self.get_category_display()}）"


class KnowledgeTopics(models.Model):
    """公共知识点表"""
    topic_id = models.IntegerField(
        "Topics表ID",
        unique=True,
        help_text="数据集中topics表的topic_id"
    )
    name = models.CharField(
        "知识点名称",
        max_length=100,
        help_text="知识点的中文名称"
    )
    clean_name = models.CharField(
        "清洗后名称",
        max_length=100,
        blank=True,
        null=True,
        help_text="解决编码问题后的中文名称"
    )
    category = models.CharField(
        "知识点分类",
        max_length=20,
        choices=[
            ("core", "核心知识点"),
            ("basic", "基础知识点"),
            ("advanced", "高级知识点"),
            ("extended", "扩展知识点"),
        ],
        blank=True,
        null=True,
        help_text="知识点分类"
    )
    description = models.TextField(
        "知识点描述",
        blank=True,
        null=True,
        help_text="对知识点的详细说明"
    )

    class Meta:
        verbose_name = "公共知识点"
        verbose_name_plural = "公共知识点"
        ordering = ["topic_id"]
        db_table = "knowledge_topics"  # 显式指定表名为knowledge_topics

    def __str__(self):
        return self.clean_name or self.name


class Course(models.Model):
    """课程模型"""
    name = models.CharField(
        "课程名称",
        max_length=200,
        help_text="如：Python编程入门"
    )
    description = models.TextField(
        "课程描述",
        help_text="对课程的详细说明"
    )
    learning_notes = models.TextField(
        "学习笔记",
        null=True,
        blank=True,
        help_text="课程学习提示"
    )
    created_at = models.DateTimeField(
        "创建时间",
        help_text="课程创建时间"
    )
    publish_time = models.DateTimeField(
        "发布时间",
        help_text="课程发布时间"
    )
    visits = models.IntegerField(
        "访问量",
        default=0,
        help_text="课程访问次数"
    )

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Chapter(models.Model):
    """章节模型"""
    name = models.CharField(
        "章节名称",
        max_length=200,
        help_text="如：Python基础语法"
    )
    description = models.TextField(
        "章节描述",
        null=True,
        blank=True,
        help_text="对章节的详细说明"
    )
    created_at = models.DateTimeField(
        "创建时间",
        help_text="章节创建时间"
    )

    class Meta:
        verbose_name = "章节"
        verbose_name_plural = "章节"
        ordering = ["id"]

    def __str__(self):
        return self.name


class CourseChapter(models.Model):
    """课程-章节关系模型"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_chapters",
        help_text="关联的课程"
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="chapter_courses",
        help_text="关联的章节"
    )
    position = models.FloatField(
        "章节顺序",
        help_text="章节在课程中的顺序"
    )

    class Meta:
        verbose_name = "课程-章节关系"
        verbose_name_plural = "课程-章节关系"
        unique_together = [("course", "chapter")]  # 确保一门课程中一个章节只出现一次
        ordering = ["course", "position"]
        db_table = "course_chapter"  

    def __str__(self):
        return f"{self.course.name} - {self.chapter.name} (位置: {self.position})"


class KnowledgeChallengeTopic(models.Model):
    """知识点与题目关联表"""
    topic = models.ForeignKey(
        KnowledgeTopics,
        on_delete=models.CASCADE,
        related_name="challenge_relations",
        help_text="关联的知识点"
    )
    challenge = models.ForeignKey(
        'question.Challenge',  # 使用字符串引用避免循环导入
        on_delete=models.CASCADE,
        related_name="topic_relations",
        verbose_name="挑战题",
        help_text="关联的挑战题",
        null=True,  # 允许为空
        blank=True  # 允许空白
    )
    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
        help_text="记录创建时间"
    )

    class Meta:
        verbose_name = "知识点与题目关联"
        verbose_name_plural = "知识点与题目关联"
        ordering = ["topic", "challenge"]
        db_table = "challenge_topic"  
        unique_together = ("topic", "challenge")  # 确保知识点与题目关联唯一

    def __str__(self):
        return f"{self.topic} - {self.challenge.name}"


# 导入Exercise模型，用于课程与练习题的关联
from question.models import Exercise

class CourseExercise(models.Model):
    """课程与练习题关联表"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_exercises",
        help_text="关联的课程"
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="exercise_courses",
        help_text="关联的练习题"
    )
    position = models.IntegerField(
        "练习题顺序",
        help_text="练习题在课程中的位置顺序"
    )
    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
        help_text="记录创建时间"
    )

    class Meta:
        verbose_name = "课程与练习题关联"
        verbose_name_plural = "课程与练习题关联"
        ordering = ["course", "position"]
        unique_together = ("course", "exercise")  # 确保一门课程中一个练习题只出现一次
        db_table = "course_exercise"  # 显式指定表名