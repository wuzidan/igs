# notification/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import User  # 基础用户模型（教师是User的子角色）
from student.models import User  # 学生模型（关联details中的学生信息）
from question.models import Exercise  # 习题模型（关联details中的习题信息）
from question.models import PracticeRecord  # 练习记录（关联答题数量等）

class Notification(models.Model):
    """教师通知模型：存储教师接收的所有通知，关联业务数据"""
    # 1. 通知类型（前端type字段，预留扩展）
    class NotificationType(models.TextChoices):
        EXERCISE = 'exercise', _('习题相关')  # 前端当前使用的类型
        ANNOUNCEMENT = 'announcement', _('系统公告')
        OTHER = 'other', _('其他通知')

    # 2. 核心字段（对齐前端基础数据）
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications',  # 教师查自己的通知：user.received_notifications.all()
        verbose_name=_('接收教师'),
        help_text='通知的接收者（必须是教师角色）'
    )
    type = models.CharField(
        _('通知类型'),
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.EXERCISE,
        help_text='对应前端type字段'
    )
    title = models.CharField(_('通知标题'), max_length=200, help_text='对应前端title字段')
    content = models.TextField(_('通知内容'), help_text='对应前端content字段')
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True,
        help_text='对应前端time字段（通知生成时间）'
    )
    is_read = models.BooleanField(
        _('是否已读'),
        default=False,
        help_text='对应前端read字段（默认未读）'
    )

    # 3. 关联业务模型（前端details字段通过关联获取，避免冗余）
    student = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_notifications',
        verbose_name=_('关联学生'),
        help_text='details中的学生信息（如张明）'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_notifications',
        verbose_name=_('关联习题'),
        help_text='details中的习题信息（如JavaScript高级特性）'
    )
    practice_record = models.ForeignKey(
        PracticeRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_notifications',
        verbose_name=_('关联练习记录'),
        help_text='details中的答题数量（totalQuestions/attemptedQuestions）'
    )
    submission_time = models.DateTimeField(
        _('学生提交时间'),
        null=True,
        blank=True,
        help_text='对应前端details.submissionTime字段'
    )

    class Meta:
        verbose_name = _('教师通知')
        verbose_name_plural = _('教师通知')
        ordering = ['-created_at']  # 默认按时间倒序（最新通知在前）
        indexes = [
            models.Index(fields=['recipient', 'is_read']),  # 优化“教师查未读通知”的查询
            models.Index(fields=['recipient', 'type']),     # 优化“按类型筛选通知”
        ]

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}（接收者：{self.recipient.full_name}）"