# student/views.py
from django.db.models import Q
from django.db.utils import ProgrammingError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from teacher.models import Teacher
from .models import Hobby, User  # 导入学生模型


class StudentLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "用户名或密码不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        account = str(username).strip()
        user = (
            User.objects.filter(
                Q(student_id=account) | Q(username=account) | Q(email=account)
            )
            .distinct()
            .first()
        )
        if user is None or not user.check_password(password):
            return Response({"error": "账号或密码错误"}, status=status.HTTP_400_BAD_REQUEST)

        if hasattr(user, "is_active") and not user.is_active:
            return Response({"error": "账号已被禁用"}, status=status.HTTP_403_FORBIDDEN)

        def _is_teacher_like(account_value: str, user_obj) -> bool:
            acc = (account_value or "").strip()
            if acc.lower().startswith("teacher") or acc.startswith("T"):
                return True
            u_username = str(getattr(user_obj, "username", "") or "")
            if u_username.lower().startswith("teacher"):
                return True
            u_student_id = str(getattr(user_obj, "student_id", "") or "")
            if u_student_id.startswith("T"):
                return True
            return False

        teacher_like = _is_teacher_like(account, user)
        if teacher_like:
            Teacher.objects.get_or_create(
                user=user,
                defaults={
                    "teacher_id": f"T{getattr(user, 'id', 0) or 0:06d}",
                    "title": "未设置",
                    "department": "未设置",
                },
            )

        try:
            token, _ = Token.objects.get_or_create(user=user)
        except ProgrammingError as e:
            # 典型原因：未执行 authtoken 的迁移，导致 authtoken_token 表不存在
            return Response(
                {
                    "error": "Token 表不存在，请先执行数据库迁移：python manage.py migrate authtoken",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if bool(getattr(user, "is_superuser", False)) or bool(getattr(user, "is_staff", False)):
            user_type = "admin"
        elif teacher_like or Teacher.objects.filter(user=user).exists():
            user_type = "teacher"
        else:
            user_type = "student"
        return Response(
            {
                "token": token.key,
                "userType": user_type,
                "user": {
                    "id": user.id,
                    "name": getattr(user, "name", None) or getattr(user, "first_name", ""),
                    "studentId": getattr(user, "student_id", ""),
                    "username": getattr(user, "username", ""),
                    "email": getattr(user, "email", ""),
                },
            },
            status=status.HTTP_200_OK,
        )


class StudentInfoView(APIView):
    """个人信息接口：获取和更新用户信息"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取个人信息数据"""
        user = request.user

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
        user = request.user

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
