# class_info/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
# 跨模块导入学生、教师模型
from student.models import User as StudentModel
from teacher.models import Teacher as TeacherModel

# 1. 班级周进度模型（对应前端 progressData）
class ClassWeeklyProgress(models.Model):
    class_info = models.ForeignKey(
        'ClassInfo',
        on_delete=models.CASCADE,
        related_name='weekly_progress',  # 反向查询：class_info.weekly_progress.all()
        verbose_name=_("关联班级")
    )
    week = models.IntegerField(_("周次"))  # 如1（对应前端"第1周"到"第12周"）
    progress = models.IntegerField(_("班级进度"))  # 如65（对应前端datasets.data数组）

    class Meta:
        verbose_name = _("班级周进度")
        verbose_name_plural = _("班级周进度")
        unique_together = ('class_info', 'week')  # 同一班级的周次不重复
        ordering = ['week']  # 按周次正序（匹配前端"第1周→第12周"）

    def __str__(self):
        return f"{self.class_info.name} - 第{self.week}周进度({self.progress}%)"


# 2. 知识点掌握度模型（对应前端 knowledgeData）
class KnowledgeMastery(models.Model):
    # 掌握度类型：整体掌握度/优秀学生掌握度
    MASTERY_TYPE = [
        ('OVERALL', _('整体掌握度')),
        ('EXCELLENT', _('优秀学生掌握度'))
    ]
    knowledge_name = models.CharField(_("知识点名称"), max_length=100)  # 如"JavaScript基础"
    mastery_type = models.CharField(_("掌握度类型"), max_length=20, choices=MASTERY_TYPE)
    mastery_value = models.IntegerField(_("掌握度值"), help_text="0-100的整数")  # 如85

    class Meta:
        verbose_name = _("知识点掌握度")
        verbose_name_plural = _("知识点掌握度")
        unique_together = ('knowledge_name', 'mastery_type')  # 同一知识点的类型不重复

    def __str__(self):
        return f"{self.get_mastery_type_display()} - {self.knowledge_name}({self.mastery_value}%)"


class ClassInfo(models.Model):
    """班级模型（核心，关联学生和教师）"""
    name = models.CharField(_("班级名称"), max_length=100)  # 如“编程基础班”
    code = models.CharField(_("班级编码"), max_length=50, unique=True)  # 如“PROG-2023-001”
    course_name = models.CharField(_("课程名称"), max_length=100)  # 如“计算机编程基础”
    create_time = models.DateField(_("创建时间"), auto_now_add=True)

    # 1. 关联教师（班主任）：多对一（一个教师可带多个班级）
    head_teacher = models.ForeignKey(
        TeacherModel,
        on_delete=models.SET_NULL,  # 教师删除后，班级保留，班主任设为NULL
        related_name="managed_classes",  # 教师反向查“管理的班级”：teacher.managed_classes.all()
        null=True, blank=True,
        verbose_name=_("班主任")
    )

    class Meta:
        verbose_name = _("班级信息")
        verbose_name_plural = _("班级信息")
        ordering = ["-create_time"]

    def __str__(self):
        return f"{self.name}（{self.code}）"

    @property
    def student_count(self):
        """动态计算班级学生数（通过学生模型的反向关联）"""
        return StudentModel.objects.filter(class_name=self.name).count()