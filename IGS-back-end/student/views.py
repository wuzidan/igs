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

        # 使用role ID判断用户类型
        def _get_user_role(user_obj) -> int:
            """获取用户角色ID"""
            # 检查用户是否有core_user属性（关联到user.User模型）
            if hasattr(user_obj, "core_user") and user_obj.core_user:
                return user_obj.core_user.role
            # 检查用户是否有role属性（直接存储角色ID）
            if hasattr(user_obj, "role"):
                return user_obj.role
            # 默认返回学生角色
            return 1

        user_role = _get_user_role(user)
        teacher_like = (user_role == 2)
        student_like = (user_role == 1)
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
        elif user_role == 1:
            user_type = "student"
        elif user_role == 2:
            user_type = "teacher"
        elif user_role == 3:
            user_type = "admin"
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
        print(f"StudentInfoView.get: 请求用户: {request.user}")
        print(f"StudentInfoView.get: 用户角色: {getattr(request.user, 'role', '未知')}")
        print(f"StudentInfoView.get: 用户ID: {request.user.id}")
        print(f"StudentInfoView.get: 用户名: {request.user.username}")
        
        # 从认证用户关联到学生业务模型
        try:
            student_user = request.user.student_user
            print(f"StudentInfoView.get: 通过 student_user 关联获取学生信息: {student_user}")
        except AttributeError:
            print(f"StudentInfoView.get: 没有 student_user 关联")
            # 尝试通过学生ID或用户名查找学生信息
            from django.db.models import Q
            student_user = User.objects.filter(
                Q(core_user=request.user) | Q(username=request.user.username) | Q(email=request.user.email)
            ).first()
            print(f"StudentInfoView.get: 通过过滤查找学生信息: {student_user}")
            if not student_user:
                print(f"StudentInfoView.get: 未找到学生信息")
                return Response(
                    {"error": "当前用户不是学生账号"},
                    status=status.HTTP_403_FORBIDDEN
                )

        # 格式化教育经历数据
        education_list = []
        try:
            education_list = [
                {
                    "school": edu.school,
                    "period_s": edu.period_s.strftime("%Y-%m-%d"),
                    "period_e": edu.period_e.strftime("%Y-%m-%d"),
                    "major": edu.major,
                    "degree": edu.degree,
                }
                for edu in student_user.education.all()
            ]
            print(f"StudentInfoView.get: 教育经历数据: {education_list}")
        except Exception as e:
            print(f"StudentInfoView.get: 教育经历数据获取失败: {e}")
            education_list = []

        # 格式化技能数据
        skill_list = []
        try:
            skill_list = [
                {
                    "name": skill.name,
                    "level": skill.level  # 假设存储值为"初级"/"中级"/"高级"
                }
                for skill in student_user.skills.all()
            ]
            print(f"StudentInfoView.get: 技能数据: {skill_list}")
        except Exception as e:
            print(f"StudentInfoView.get: 技能数据获取失败: {e}")
            skill_list = []

        # 格式化兴趣爱好（假设以逗号分隔存储）
        hobbies = []
        try:
            hobbies = [hobby.name for hobby in student_user.hobbies.all()]
            print(f"StudentInfoView.get: 兴趣爱好数据: {hobbies}")
        except Exception as e:
            print(f"StudentInfoView.get: 兴趣爱好数据获取失败: {e}")
            hobbies = []

        return Response({
            # 头像相关
            "userAvatarUrl": getattr(student_user, 'user_avatar_url', '') or "",  # 自定义头像URL
            "userAvatar": getattr(student_user, 'user_avatar_emoji', '') or "👨‍💻",  # 默认头像emoji

            # 基本信息
            "userName": student_user.name,
            "studentId": student_user.student_id,
            "className": student_user.class_name,
            "major": student_user.major,
            "birthDate": student_user.birth_date.strftime("%Y-%m-%d") if student_user.birth_date else "",
            "hometown": student_user.hometown or "",
            "politicalStatus": student_user.political_status or "",
            "email": student_user.core_user.email or "" if student_user.core_user else "",
            "phone": student_user.core_user.phone or "" if student_user.core_user else "",
            "website": student_user.website or "",
            "bio": student_user.bio or "",
            "hobbies": hobbies,
            "skills": skill_list,
            "education": education_list
        })

    def put(self, request):
        """更新个人信息（部分字段示例）"""
        # 从认证用户关联到学生业务模型
        try:
            student_user = request.user.student_user
        except AttributeError:
            return Response(
                {"error": "当前用户不是学生账号"},
                status=status.HTTP_403_FORBIDDEN
            )

        # 处理可更新字段（根据实际需求扩展）
        update_data = request.data
        if "userName" in update_data:
            student_user.first_name = update_data["userName"]
        if "email" in update_data and student_user.core_user:
            student_user.core_user.email = update_data["email"]
        if "phone" in update_data and student_user.core_user:
            student_user.core_user.phone = update_data["phone"]
        if "bio" in update_data:
            student_user.bio = update_data["bio"]
        if "hobbies" in update_data:
            hobbies_payload = update_data["hobbies"]
            if hobbies_payload is None:
                hobbies_payload = []
            if isinstance(hobbies_payload, str):
                hobbies_payload = [h.strip() for h in hobbies_payload.split(",") if h.strip()]

            Hobby.objects.filter(user=student_user).delete()
            for hobby_name in hobbies_payload:
                if hobby_name:
                    Hobby.objects.create(user=student_user, name=hobby_name)

        # 保存学生业务模型
        student_user.save()
        # 保存关联的用户模型（如果有修改）
        if student_user.core_user:
            student_user.core_user.save()
        return Response({"message": "信息更新成功"})
