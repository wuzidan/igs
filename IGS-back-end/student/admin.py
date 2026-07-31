# student/admin.py
from django.contrib import admin
from .models import User  # 导入学生模型


# 注册 User 模型到 Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 显示的字段（根据你的模型字段调整）
    list_display = ('username', 'first_name', 'student_id', 'class_name', 'major')
    # 可搜索的字段
    search_fields = ('student_id', 'class_name', 'major', 'username', 'first_name')


from django.contrib import admin

# Register your models here.
