# student/admin.py
from django.contrib import admin
from .models import User  # 导入你的用户模型


# 注册 User 模型到 Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 显示的字段（根据你的模型字段调整）
    list_display = ('id', 'username', 'name', 'student_id', 'user_avatar_emoji')
    # 可搜索的字段
    search_fields = ('username', 'name', 'student_id')


from django.contrib import admin

# Register your models here.
