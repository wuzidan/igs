# user/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


# 1. 角色模型（存储用户角色信息）
class Role(models.Model):
    """
    角色模型：存储系统中的用户角色
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("角色名称"), max_length=50, unique=True)
    description = models.CharField(_("角色描述"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("角色")
        verbose_name_plural = _("角色")
        ordering = ["id"]

    def __str__(self):
        return self.name


# 2. 自定义User模型（系统唯一身份模型，所有用户共用）
class User(AbstractUser):
    """
    基础用户模型：存储所有用户的通用身份信息
    业务专属信息（如学号、工号）存放在对应业务模块（student/teacher）
    """

    # 基础身份字段（覆盖/扩展AbstractUser）
    username = models.CharField(_("用户名"), max_length=50, unique=True)  # 登录用（如手机号/邮箱）
    email = models.EmailField(_("电子邮箱"), unique=True, blank=False)  # 用于验证/通知
    first_name = models.CharField(_("真实姓名"), max_length=50, blank=False)  # 所有用户都有姓名
    password = models.CharField(_("密码"), max_length=128)  # 明文存储密码

    groups = models.ManyToManyField(
        Group,
        related_name="core_user_set",
        related_query_name="core_user",
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="core_user_set",
        related_query_name="core_user",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    # 通用基础信息
    role = models.IntegerField(
        verbose_name=_('用户角色'),
        help_text="区分用户类型：1=学生/2=教师/3=管理员"
    )
    phone = models.CharField(_("手机号"), max_length=20, blank=True, null=True)  # 通用联系方式
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)  # 账号创建时间
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)  # 信息更新时间

    # 认证配置（覆盖AbstractUser默认值）
    USERNAME_FIELD = "username"  # 登录字段：用户名（可改为email）
    REQUIRED_FIELDS = ["email", "first_name"]  # 创建用户时必填的字段

    avatar = models.ImageField(
        "头像",
        upload_to="teachers/",  # 子目录，自动在 MEDIA_ROOT 下创建
        blank=True,
        null=True,
        help_text="上传教师头像图片"
    )
    # 快捷获取头像URL（前端调用）
    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url  # 返回 URL：/static/avatars/teachers/文件名.jpg
        return ""  # 无头像时返回空字符串

    def __str__(self):
        role_names = {1: "学生", 2: "教师", 3: "管理员"}
        return f"{self.first_name}（{role_names.get(self.role, '未知')}）"

    @property
    def full_name(self):
        """兼容旧逻辑：返回真实姓名"""
        return self.first_name

    @property
    def is_admin(self):
        """快捷判断：是否为管理员"""
        return self.role == 3

    @property
    def is_student_user(self):
        """快捷判断：是否为学生角色"""
        return self.role == 1

    @property
    def is_teacher_user(self):
        """快捷判断：是否为教师角色"""
        return self.role == 2

    class Meta:
        verbose_name = _("用户")
        verbose_name_plural = _("用户")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["role"]),  # 按角色查询索引（优化权限判断）
            models.Index(fields=["phone"]),  # 手机号查询索引
        ]