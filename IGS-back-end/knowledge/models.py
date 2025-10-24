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
        related_name="knowledge_points",
        help_text="关联的用户"
    )

    class Meta:
        verbose_name = "知识点"
        verbose_name_plural = "知识点"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}（{self.get_category_display()}）"