# student/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Hobby, User  # 导入学生模型


class StudentInfoView(APIView):
    """个人信息接口：获取和更新用户信息"""

    # 开发阶段暂时    permission_classes = []

    def get(self, request):
        """获取个人信息数据"""
        # 开发阶段：使用测试用户（实际环境替换为request.user）
        test_user_id = 1
        try:
            user = User.objects.get(id=test_user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 格式化教育经历数据
        education_list = [
            {
                "school": edu.school,
                "period_s": edu.period_s.strftime("%Y-%m-%d"),
                "period_e": edu.period_e.strftime("%Y-%m-%d"),
                "major": edu.major,
                "degree": edu.degree,
            }
            for edu in user.education.all()
        ]

        # 格式化技能数据
        skill_list = [
            {
                "name": skill.name,
                "level": skill.level  # 假设存储值为"初级"/"中级"/"高级"
            }
            for skill in user.skills.all()
        ]

        # 格式化兴趣爱好（假设以逗号分隔存储）
        hobbies = [hobby.name for hobby in user.hobbies.all()]

        return Response({
            # 头像相关
            "userAvatarUrl": user.user_avatar_url or "",  # 自定义头像URL
            "userAvatar": user.user_avatar_emoji or "👨‍💻",  # 默认头像emoji

            # 基本信息
            "userName": user.name,
            "studentId": user.student_id,
            "className": user.class_name,
            "major": user.major,
            "birthDate": user.birth_date.strftime("%Y-%m-%d") if user.birth_date else "",
            "hometown": user.hometown or "",
            "politicalStatus": user.political_status or "",
            "email": user.email or "",
            "phone": user.phone or "",
            "website": user.website or "",
            "bio": user.bio or "",
            "hobbies": hobbies,
            "skills": skill_list,
            "education": education_list
        })

    def put(self, request):
        """更新个人信息（部分字段示例）"""
        test_user_id = 1
        try:
            user = User.objects.get(id=test_user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 处理可更新字段（根据实际需求扩展）
        update_data = request.data
        if "userName" in update_data:
            user.first_name = update_data["userName"]
        if "email" in update_data:
            user.email = update_data["email"]
        if "phone" in update_data:
            user.phone = update_data["phone"]
        if "bio" in update_data:
            user.bio = update_data["bio"]
        if "hobbies" in update_data:
            hobbies_payload = update_data["hobbies"]
            if hobbies_payload is None:
                hobbies_payload = []
            if isinstance(hobbies_payload, str):
                hobbies_payload = [h.strip() for h in hobbies_payload.split(",") if h.strip()]

            Hobby.objects.filter(user=user).delete()
            for hobby_name in hobbies_payload:
                if hobby_name:
                    Hobby.objects.create(user=user, name=hobby_name)

        user.save()
        return Response({"message": "信息更新成功"})
