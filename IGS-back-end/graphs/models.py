from django.db import models


class GraphDomain(models.Model):
    name = models.CharField("领域名称", max_length=100, unique=True)
    created_by = models.CharField("创建者", max_length=20, blank=True, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "知识图谱领域"
        verbose_name_plural = "知识图谱领域"
        ordering = ["name"]

    def __str__(self):
        return self.name


class KnowledgeGraph(models.Model):
    class GraphType(models.TextChoices):
        CONCEPT = "concept", "概念图谱"
        RELATIONSHIP = "relationship", "关系图谱"
        HIERARCHICAL = "hierarchical", "层级图谱"
        INTEGRATED = "integrated", "综合图谱"

    class GraphStatus(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"
        ARCHIVED = "archived", "已归档"

    owner = models.ForeignKey(
        'teacher.Teacher',
        on_delete=models.RESTRICT,
        to_field='teacher_id',
        db_column='owner_id',
        related_name='owned_graphs',
        verbose_name="创建者",
    )
    
    class Meta:
        verbose_name = "知识图谱"
        verbose_name_plural = "知识图谱"
        ordering = ["-updated_at", "-id"]

    name = models.CharField("图谱名称", max_length=200)
    domain = models.ForeignKey(
        GraphDomain,
        on_delete=models.PROTECT,
        related_name="graphs",
        verbose_name="知识领域",
    )
    type = models.CharField(
        "图谱类型",
        max_length=20,
        choices=GraphType.choices,
        default=GraphType.CONCEPT,
    )
    status = models.CharField(
        "状态",
        max_length=20,
        choices=GraphStatus.choices,
        default=GraphStatus.DRAFT,
    )
    description = models.TextField("描述", blank=True, default="")
    tags = models.JSONField("标签", default=list, blank=True)

    # content schema: {"nodes": [...], "relationships": [...]}
    content = models.JSONField("图谱内容", default=dict, blank=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    published_at = models.DateTimeField("发布时间", null=True, blank=True)

    class Meta:
        verbose_name = "知识图谱"
        verbose_name_plural = "知识图谱"
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.name
