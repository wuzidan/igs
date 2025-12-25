# teacher/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# 新增：教学科目模型（如“Web前端开发”“算法与数据结构”）
class Subject(models.Model):
    """教学科目模型：存储所有可选的教学/研究方向"""
    name = models.CharField(
        _("科目名称"),
        max_length=100,
        unique=True,  # 科目名称唯一，避免重复
        help_text="如：Web前端开发、算法与数据结构"
    )
    description = models.TextField(_("科目描述"), blank=True, null=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        verbose_name = _("教学科目")
        verbose_name_plural = _("教学科目")
        ordering = ["name"]

    def __str__(self):
        return self.name


# 完善：教师模型（补充缺失字段 + 多对多关联科目）
class Teacher(models.Model):
    """教师业务档案：补充前端所需的所有字段"""
    # 核心关联：一个教师对应一个User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",  # User反向查教师档案：user.teacher_profile
        verbose_name=_("关联用户")
    )
    # 原有字段保留
    teacher_id = models.CharField(_("工号"), max_length=20, unique=True, help_text="教师唯一标识")
    title = models.CharField(_("职称"), max_length=50, help_text="如：教授、讲师")
    department = models.CharField(_("所属院系"), max_length=100, help_text="如：计算机学院")
    office_address = models.CharField(_("办公室地址"), max_length=200, blank=True, null=True)

    # 新增：前端所需的缺失字段
    birth_date = models.DateField(_("出生日期"), blank=True, null=True)  # 对应前端birthDate
    hometown = models.CharField(_("籍贯"), max_length=100, blank=True, null=True)  # 对应前端hometown
    political_status = models.CharField(
        _("政治面貌"),
        max_length=50,
        blank=True,
        null=True,
        choices=[("群众", "群众"), ("党员", "党员"), ("团员", "团员"), ("其他", "其他")]  # 前端politicalStatus
    )
    bio = models.TextField(_("个人简介"), blank=True, null=True)  # 对应前端bio

    # 新增：多对多关联教学科目（前端subjects列表）
    subjects = models.ManyToManyField(
        Subject,
        related_name="teachers",  # 科目反向查教师：subject.teachers.all()
        blank=True,
        verbose_name=_("教学科目")
    )

    class Meta:
        verbose_name = _("教师档案")
        verbose_name_plural = _("教师档案")
        ordering = ["teacher_id"]

    def __str__(self):
        display_name = getattr(self.user, "full_name", None) or getattr(self.user, "name", None) or getattr(self.user, "first_name", "")
        return f"{display_name}（工号：{self.teacher_id}）"