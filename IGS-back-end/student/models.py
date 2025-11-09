
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
from django.db import models

from question.models import Question

# 用户主模型（扩展AbstractUser）
class User(AbstractUser):
    # 原有字段
    student_id = models.CharField(
        "学号",
        max_length=20,
        unique=True,
        help_text="学生的唯一标识符"
    )
    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
        help_text="用户账户创建时间"
    )

    # 新增基本信息字段
    user_avatar_url = models.URLField(
        "自定义头像URL",
        max_length=255,
        blank=True,
        null=True,
        help_text="用户上传的头像图片URL"
    )
    user_avatar_emoji = models.CharField(
        "默认头像emoji",
        max_length=10,
        default="👨‍💻",
        help_text="默认显示的emoji头像"
    )
    class_name = models.CharField(
        "班级",
        max_length=50,
        blank=True,
        help_text="如：计算机科学与技术 2023级"
    )
    major = models.CharField(
        "专业",
        max_length=50,
        blank=True,
        help_text="如：计算机科学与技术"
    )
    birth_date = models.DateField(
        "出生日期",
        blank=True,
        null=True,
        help_text="格式：YYYY-MM-DD"
    )
    hometown = models.CharField(
        "籍贯",
        max_length=100,
        blank=True,
        help_text="如：广东省广州市"
    )
    political_status = models.CharField(
        "政治面貌",
        max_length=20,
        blank=True,
        help_text="如：团员、党员"
    )
    phone = models.CharField(
        "手机号",
        max_length=20,
        blank=True,
        help_text="用户联系电话"
    )
    website = models.URLField(
        "个人网站",
        max_length=255,
        blank=True,
        null=True,
        help_text="个人博客或主页URL"
    )
    bio = models.TextField(
        "个人简介",
        blank=True,
        help_text="用户的自我描述"
    )

    # 覆盖默认配置
    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['email', 'first_name']  # first_name用作真实姓名

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        ordering = ['-created_at']

    @property
    def name(self):
        """返回用户姓名"""
        return self.first_name or self.username

    def __str__(self):
        return f"{self.name} ({self.student_id})"


# 爱好模型（与User为一对多关系）
class Hobby(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hobbies",
        verbose_name="关联用户"
    )
    name = models.CharField(
        "爱好名称",
        max_length=50,
        help_text="如：编程、篮球"
    )

    class Meta:
        verbose_name = "爱好"
        verbose_name_plural = "爱好"
        unique_together = ('user', 'name')  # 同一用户的爱好不重复

    def __str__(self):
        return f"{self.user.name}的爱好：{self.name}"


# 技能模型（与User为一对多关系）
class Skill(models.Model):
    LEVEL_CHOICES = [
        ("初级", "初级"),
        ("中级", "中级"),
        ("高级", "高级"),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="skills",
        verbose_name="关联用户"
    )
    name = models.CharField(
        "技能名称",
        max_length=50,
        help_text="如：JavaScript、Python"
    )
    level = models.CharField(
        "技能水平",
        max_length=10,
        choices=LEVEL_CHOICES,
        help_text="技能掌握程度"
    )

    class Meta:
        verbose_name = "技能"
        verbose_name_plural = "技能"
        unique_together = ('user', 'name')  # 同一用户的技能不重复

    def __str__(self):
        return f"{self.user.name}的技能：{self.name}（{self.level}）"


# 教育经历模型（与User为一对多关系）
class Education(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="education",
        verbose_name="关联用户"
    )
    school = models.CharField(
        "学校名称",
        max_length=100,
        help_text="如：华南师范大学"
    )
    period_s = models.DateField(
        "开始时间",
        help_text="入学日期，格式：YYYY-MM-DD"
    )
    period_e = models.DateField(
        "结束时间",
        help_text="毕业日期，格式：YYYY-MM-DD"
    )
    major = models.CharField(
        "专业",
        max_length=50,
        help_text="如：计算机科学与技术"
    )
    degree = models.CharField(
        "学位",
        max_length=20,
        help_text="如：本科、硕士"
    )

    class Meta:
        verbose_name = "教育经历"
        verbose_name_plural = "教育经历"
        ordering = ['-period_s']  # 按入学时间倒序排列

    def __str__(self):
        return f"{self.user.name}的教育经历：{self.school} {self.degree}"

