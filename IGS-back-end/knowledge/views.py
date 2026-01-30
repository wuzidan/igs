from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Sum
import random

from student.models import User
from .models import KnowledgePoint, Course, Chapter, CourseChapter, KnowledgeTopics
from question.models import Exercise, Challenge


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
        if user_knowledge_map:
            coverage_rate = (mastered_count / total_count) * 100 if total_count > 0 else 0
            avg_mastery = sum(user_knowledge_map.values()) / len(user_knowledge_map) if user_knowledge_map else 0
        else:
            # 如果没有用户数据，使用随机生成的掌握程度计算统计数据
            # 模拟中等水平的掌握情况
            avg_mastery = 55  # 平均掌握度 55%
            mastered_count = int(total_count * 0.4)  # 40% 的知识点被掌握
            coverage_rate = 40  # 覆盖率 40%
        
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
                chapter_mastery_sum = 0
                chapter_mastery_count = 0
                
                for topic in chapter_topics:
                    # 获取用户对该知识点的掌握程度
                    mastery = user_knowledge_map.get(topic.name, 0)
                    # 如果没有掌握数据，生成随机掌握程度（模拟数据）
                    if mastery == 0 and not user_knowledge_map:
                        # 生成 0-100 的随机掌握程度，加权倾向于中等水平
                        import random
                        mastery = random.choices(
                            [20, 30, 40, 50, 60, 70, 80, 90],
                            weights=[1, 2, 3, 4, 3, 2, 1, 1],
                            k=1
                        )[0]
                    
                    # 累计章节的掌握度
                    chapter_mastery_sum += mastery
                    chapter_mastery_count += 1
                    
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
                
                # 计算章节的平均掌握度
                chapter_avg_mastery = chapter_mastery_sum / chapter_mastery_count if chapter_mastery_count > 0 else 0
                
                # 构建章节数据
                chapter_data = {
                    "id": cc.chapter.id,
                    "courseId": course.id,
                    "name": cc.chapter.name,
                    "avgMastery": round(chapter_avg_mastery),
                    "topics": topics_for_chapter  # 章节包含的知识点
                }
                chapters_for_course.append(chapter_data)
                chapter_list.append(chapter_data)  # 添加到全局章节列表
            
            # 计算课程的平均掌握度
            course_mastery_sum = sum(chapter['avgMastery'] for chapter in chapters_for_course)
            course_mastery_count = len(chapters_for_course)
            course_avg_mastery = course_mastery_sum / course_mastery_count if course_mastery_count > 0 else 0
            
            # 构建课程数据
            course_data = {
                "id": course.id,
                "name": course.name,
                "avgMastery": round(course_avg_mastery),
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