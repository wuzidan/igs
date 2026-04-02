from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework import status
from django.db.models import Avg, Count, Sum
import random

from student.models import User
from .models import KnowledgePoint, Course, Chapter, CourseChapter, KnowledgeTopics
from question.models import Exercise, Challenge

class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器"""
    class Meta:
        model = Course
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class CourseManagementView(APIView):
    """课程管理API接口"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取课程列表，支持搜索，只返回当前登录老师的课程"""
        search_keyword = request.query_params.get('search', '')
        
        # 获取当前登录用户
        user = request.user
        
        # 构建查询
        queryset = Course.objects.all()
        
        # 过滤出当前登录老师的课程
        try:
            # 从用户关联到老师
            from teacher.models import Teacher
            teacher = Teacher.objects.filter(user=user).first()
            if teacher:
                # 只返回与该老师关联的课程
                queryset = queryset.filter(course_teachers__teacher=teacher)
        except Exception as e:
            print(f"获取老师课程失败: {e}")
        
        # 如果有搜索关键词，添加搜索条件
        if search_keyword:
            queryset = queryset.filter(name__icontains=search_keyword)
        
        # 序列化课程数据
        serializer = CourseSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """添加新课程，自动关联到当前登录老师"""
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            # 保存课程
            course = serializer.save()
            
            # 关联到当前登录老师
            try:
                from teacher.models import Teacher
                user = request.user
                
                # 确保教师实例存在
                teacher = Teacher.objects.filter(user=user).first()
                if not teacher:
                    # 尝试创建教师实例
                    try:
                        teacher = Teacher.objects.create(
                            user=user,
                            teacher_id=f"T{user.id:06d}",
                            title="未设置",
                            department="未设置"
                        )
                        print(f"自动创建教师实例: {teacher}")
                    except Exception as create_error:
                        print(f"创建教师实例失败: {create_error}")
                        # 即使教师实例创建失败，课程仍然创建成功
                
                if teacher:
                    # 创建课程与老师的关联
                    from .models import CourseTeacher
                    CourseTeacher.objects.create(
                        course=course,
                        teacher=teacher
                    )
                    print(f"课程关联教师成功: 课程ID={course.id}, 教师ID={teacher.teacher_id}")
                else:
                    print(f"教师实例不存在，课程未关联: 课程ID={course.id}")
            except Exception as e:
                print(f"关联老师失败: {e}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        """编辑课程，只能编辑自己的课程"""
        try:
            course = Course.objects.get(pk=pk)
            
            # 检查是否是当前老师的课程
            from teacher.models import Teacher
            user = request.user
            teacher = Teacher.objects.filter(user=user).first()
            if teacher:
                # 检查课程是否与该老师关联
                if not course.course_teachers.filter(teacher=teacher).exists():
                    return Response({'error': '无权编辑此课程'}, status=status.HTTP_403_FORBIDDEN)
        except Course.DoesNotExist:
            return Response({'error': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': '操作失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """删除课程，只能删除自己的课程"""
        try:
            course = Course.objects.get(pk=pk)
            
            # 检查是否是当前老师的课程
            from teacher.models import Teacher
            user = request.user
            
            # 确保教师实例存在
            teacher = Teacher.objects.filter(user=user).first()
            if not teacher:
                # 尝试创建教师实例
                try:
                    teacher = Teacher.objects.create(
                        user=user,
                        teacher_id=f"T{user.id:06d}",
                        title="未设置",
                        department="未设置"
                    )
                    print(f"自动创建教师实例: {teacher}")
                except Exception as create_error:
                    print(f"创建教师实例失败: {create_error}")
                    return Response({'error': '教师实例不存在，无法删除课程'}, status=status.HTTP_403_FORBIDDEN)
            
            # 检查课程是否与该老师关联
            if not course.course_teachers.filter(teacher=teacher).exists():
                print(f"课程与教师无关联: 课程ID={course.id}, 教师ID={teacher.teacher_id}")
                return Response({'error': '无权删除此课程'}, status=status.HTTP_403_FORBIDDEN)
            
        except Course.DoesNotExist:
            print(f"课程不存在: {pk}")
            return Response({'error': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"删除课程失败: {e}")
            return Response({'error': f'操作失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 删除课程
        course.delete()
        print(f"课程删除成功: 课程ID={pk}")
        return Response({'message': '课程删除成功'}, status=status.HTTP_200_OK)

class KnowledgeStructureView(APIView):
    # """知识点结构数据接口"""
    # permission_classes = [IsAuthenticated]  # 仅登录用户可访问
    permission_classes = []
    def get(self, request):
        target_user = None
        if getattr(request, "user", None) and request.user.is_authenticated:
            target_user = request.user
        else:
            user_id = request.query_params.get("user_id") or request.query_params.get("userId")
            if user_id:
                target_user = User.objects.filter(id=user_id).first()

        # 初始化用户知识点掌握情况
        user_knowledge_map = {}
        mastered_count = 0
        
        if target_user:
            # 获取用户的知识点掌握情况
            user_knowledge_points = KnowledgePoint.objects.filter(user=target_user)
            for point in user_knowledge_points:
                user_knowledge_map[point.name] = point.mastery
                if point.mastery >= 60:
                    mastered_count += 1

        # 获取所有公共知识点总数
        total_count = KnowledgeTopics.objects.count()
        
        # 如果没有知识点，返回默认数据
        if total_count == 0:
            return Response({
                "coverageRate": 0,
                "masteredCount": 0,
                "totalCount": 0,
                "avgMastery": 0,
                "courseList": [],
                "chapterList": [],
                "knowledgeList": [],
            })
        
        # 计算总体统计数据
        coverage_rate = (mastered_count / total_count) * 100 if total_count > 0 else 0
        avg_mastery = sum(user_knowledge_map.values()) / len(user_knowledge_map) if user_knowledge_map else 0
        
        # 添加分页支持
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 20))
        offset = (page - 1) * page_size
        
        # 优化课程查询，只获取分页数据
        courses = Course.objects.all()[offset:offset+page_size]
        
        # 初始化返回数据结构
        course_list = []
        chapter_list = []
        knowledge_list = []
        
        # 构建课程列表
        for course in courses:
            # 获取课程关联的前5个章节
            course_chapters = CourseChapter.objects.filter(
                course=course
            ).order_by('position')[:5]
            
            # 构建章节数据
            chapters_for_course = []
            for cc in course_chapters:
                # 获取章节关联的知识点（简化：直接获取所有知识点，实际应根据章节关联的练习题获取）
                # 返回所有知识点，不再限制数量，前端通过固定高度和滚动条控制显示
                chapter_topics = KnowledgeTopics.objects.all()[:10]  # 限制每个章节最多返回10个知识点
                
                # 构建章节的知识点数据
                topics_for_chapter = []
                for topic in chapter_topics:
                    # 获取用户对该知识点的掌握程度
                    mastery = user_knowledge_map.get(topic.name, 0)
                    
                    topic_data = {
                        "id": topic.topic_id,
                        "courseId": course.id,
                        "chapterId": cc.chapter.id,
                        "name": topic.clean_name or topic.name,
                        "category": topic.category or "general",
                        "categoryText": dict(KnowledgeTopics._meta.get_field('category').choices).get(topic.category, "一般知识点"),
                        "mastery": mastery,
                        "description": topic.description or "",
                        "practiceCount": 0,
                        "lastPracticed": None
                    }
                    topics_for_chapter.append(topic_data)
                    knowledge_list.append(topic_data)  # 添加到全局知识点列表
                
                # 构建章节数据
                chapter_data = {
                    "id": cc.chapter.id,
                    "courseId": course.id,
                    "name": cc.chapter.name,
                    "avgMastery": 0,
                    "topics": topics_for_chapter  # 章节包含的知识点
                }
                chapters_for_course.append(chapter_data)
                chapter_list.append(chapter_data)  # 添加到全局章节列表
            
            # 构建课程数据
            course_data = {
                "id": course.id,
                "name": course.name,
                "avgMastery": 0,
                "chapters": chapters_for_course  # 课程包含的章节
            }
            course_list.append(course_data)
        
        # 获取总课程数
        total_courses = Course.objects.count()
        
        # 返回完整的数据结构，确保chapterList和knowledgeList包含数据
        return Response({
            "coverageRate": round(coverage_rate),
            "masteredCount": mastered_count,
            "totalCount": total_count,
            "avgMastery": round(avg_mastery),
            "courseList": course_list,
            "chapterList": chapter_list,  # 全局章节列表
            "knowledgeList": knowledge_list,  # 全局知识点列表
            "totalCourses": total_courses,
            "currentPage": page,
            "pageSize": page_size
        })
    
    def get_mock_data(self):
        # 生成模拟的知识点数据
        mock_knowledge_points = [
            {
                "id": 1,
                "name": "变量与数据类型",
                "category": "core",
                "categoryText": "核心知识点",
                "mastery": 65,
                "description": "学习Python中的基本数据类型、变量定义和类型转换",
                "practiceCount": 15,
                "lastPracticed": "2024-01-15"
            },
            {
                "id": 2,
                "name": "控制结构",
                "category": "core",
                "categoryText": "核心知识点",
                "mastery": 50,
                "description": "掌握条件语句和循环结构的使用",
                "practiceCount": 12,
                "lastPracticed": "2024-01-18"
            },
            {
                "id": 3,
                "name": "函数模块",
                "category": "core",
                "categoryText": "核心知识点",
                "mastery": 75,
                "description": "学习函数定义、参数传递和返回值",
                "practiceCount": 10,
                "lastPracticed": "2024-01-20"
            },
            {
                "id": 4,
                "name": "数据结构基础",
                "category": "important",
                "categoryText": "重要知识点",
                "mastery": 45,
                "description": "掌握列表、元组、字典和集合的基本操作",
                "practiceCount": 8,
                "lastPracticed": "2024-01-22"
            },
            {
                "id": 5,
                "name": "算法分析",
                "category": "important",
                "categoryText": "重要知识点",
                "mastery": 30,
                "description": "学习时间复杂度和空间复杂度的分析方法",
                "practiceCount": 5,
                "lastPracticed": "2024-01-25"
            },
            {
                "id": 6,
                "name": "文件操作",
                "category": "general",
                "categoryText": "一般知识点",
                "mastery": 60,
                "description": "学习文件的读写操作和异常处理",
                "practiceCount": 6,
                "lastPracticed": "2024-01-28"
            }
        ]
        
        # 计算统计数据
        total_count = len(mock_knowledge_points)
        mastered_count = sum(1 for point in mock_knowledge_points if point['mastery'] >= 60)
        coverage_rate = (mastered_count / total_count) * 100 if total_count > 0 else 0
        avg_mastery = sum(point['mastery'] for point in mock_knowledge_points) / total_count if total_count > 0 else 0
        
        # 返回模拟数据
        return Response({
            "coverageRate": round(coverage_rate),  # 四舍五入为整数
            "masteredCount": mastered_count,
            "totalCount": total_count,
            "avgMastery": round(avg_mastery),
            "knowledgeList": mock_knowledge_points
        })