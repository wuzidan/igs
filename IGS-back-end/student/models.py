from django.db import models
from django.conf import settings
from question.models import Question


from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

# 学生业务模型（与User模型一对一关联）
class User(AbstractUser):
    """
    学生业务模型：存储学生特有的业务数据
    登录相关信息存储在 user.User 模型中
    """
    
    # 与用户模型的一对一关联
    core_user = models.OneToOneField(
        'user.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_user'
    )
    
    # 学号字段
    student_id = models.CharField(
        "学号",
        max_length=20,
        unique=True,
        help_text="学生的唯一标识符"
    )
    
    # 班级相关字段
    class_name = models.CharField(
        "班级",
        max_length=50,
        blank=True,
        help_text="如：计算机科学与技术 2023级"
    )
    class_info = models.ForeignKey(
        'classInfo.ClassInfo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="关联班级"
    )
    
    # 学生特有字段
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

    # 覆盖 AbstractUser 的字段
    groups = models.ManyToManyField(
        Group,
        related_name='student_user_set',
        related_query_name='student_user',
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='student_user_set',
        related_query_name='student_user',
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    class Meta:
        verbose_name = "学生"
        verbose_name_plural = "学生"
        ordering = ['student_id']
        db_table = 'student_user'

    @property
    def name(self):
        """返回用户姓名"""
        return self.first_name or self.username

    def __str__(self):
        return f"{self.name} ({self.student_id})"


# 爱好模型（与User为一对多关系）
class Hobby(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="hobbies",
        verbose_name="关联学生"
    )
    name = models.CharField(
        "爱好名称",
        max_length=50,
        help_text="如：编程、篮球"
    )

    class Meta:
        verbose_name = "爱好"
        verbose_name_plural = "爱好"
        unique_together = ('user', 'name')  # 同一学生的爱好不重复
        db_table = 'student_hobby'

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
        'User',
        on_delete=models.CASCADE,
        related_name="skills",
        verbose_name="关联学生"
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
        unique_together = ('user', 'name')  # 同一学生的技能不重复
        db_table = 'student_skill'

    def __str__(self):
        return f"{self.user.name}的技能：{self.name}（{self.level}）"


# 教育经历模型（与User为一对多关系）
class Education(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="education",
        verbose_name="关联学生"
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
        db_table = 'student_education'

    def __str__(self):
        return f"{self.user.name}的教育经历：{self.school} {self.degree}"

