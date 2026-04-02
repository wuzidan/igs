from django.http import HttpResponse
from django.views import View
from django.contrib.auth import get_user_model
from django.db.models import F, Q, Value
from django.db.models.fields import TextField
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status, viewsets
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Exercise, Question, Challenge, PracticeRecord


class ExerciseListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    title = serializers.CharField(source="name", read_only=True)
    createTime = serializers.DateTimeField(source="created_at", read_only=True)
    useCount = serializers.IntegerField(source="visits", read_only=True)
    publishTime = serializers.DateTimeField(source="publish_time", allow_null=True, required=False)
    exerciseId = serializers.CharField(source="exercise_id", read_only=True)
    forkFrom = serializers.CharField(source="fork_from", allow_null=True, required=False)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "exerciseId",
            "title",
            "forkFrom",
            "status",
            "createTime",
            "publishTime",
            "useCount",
        ]


class ExerciseDetailSerializer(ExerciseListSerializer):
    pass


class ExerciseCreateSerializer(serializers.ModelSerializer):
    exerciseId = serializers.CharField(source="exercise_id")
    title = serializers.CharField(source="name")
    forkFrom = serializers.CharField(source="fork_from", required=False, allow_null=True, allow_blank=True)
    publishTime = serializers.DateTimeField(source="publish_time", required=False, allow_null=True)
    createTime = serializers.DateTimeField(source="created_at", required=False)
    useCount = serializers.IntegerField(source="visits", required=False)

    class Meta:
        model = Exercise
        fields = [
            "exerciseId",
            "title",
            "status",
            "forkFrom",
            "publishTime",
            "createTime",
            "useCount",
        ]

    def create(self, validated_data):
        if "created_at" not in validated_data or validated_data["created_at"] is None:
            validated_data["created_at"] = timezone.now()
        if "visits" not in validated_data or validated_data["visits"] is None:
            validated_data["visits"] = 0
        return super().create(validated_data)


@api_view(['GET'])
@permission_classes([AllowAny])  # 明确允许任何人访问
def debug_view(request):
    return Response({
        "message": "Debug view is working",
        "path": request.path,
        "method": request.method
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def question_list(request):
    # 从Challenge模型获取数据
    queryset = Challenge.objects.all()
    queryset = queryset.order_by('-id')

    # 分页参数
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 12)  # 修改为12

    # 分页处理
    paginator = Paginator(queryset, page_size)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    data = []
    for q in paginated_queryset:
        # 构建返回数据结构
        data.append({
            "id": q.id,
            "type": "shortAnswer",  # 默认为简答题类型
            "difficulty": q.difficulty,
            "content": q.task_pass,  # 使用task_pass作为题目内容
            "title": q.name,  # 添加title字段，使用name作为标题
            "correct": False,  # 默认为未正确
            "completed": False,  # 默认为未完成
            "accuracy": 0,  # 默认为0
            "score": q.score,  # 添加score字段
            "userAnswer": None,
            "answer": q.answer,  # 添加answer字段
            "correctAnswer": q.answer,  # 使用answer作为正确答案
            "options": [],  # 挑战题没有选项
            "analysis": "",  # 默认为空解析
        })

    # 返回分页数据和元数据
    return Response({
        "data": data,
        "total": paginator.count,
        "page": paginated_queryset.number,
        "page_size": page_size,
        "total_pages": paginator.num_pages
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def question_stats(request):
    """获取题目统计数据"""
    # 总题目数
    total_count = Challenge.objects.count()
    
    # 题目类型统计（目前所有挑战题都是简答题）
    type_stats = {
        "singleChoice": 0,
        "multipleChoice": 0,
        "judgment": 0,
        "shortAnswer": total_count
    }
    
    # 题目难度分布 - 将数字难度映射为字符串难度
    # 1=easy, 2=medium, 3=hard
    try:
        # 直接查询所有挑战题，然后在内存中统计难度分布
        challenges = Challenge.objects.all()
        difficulty_stats = {
            "easy": 0,
            "medium": 0,
            "hard": 0
        }
        
        for challenge in challenges:
            try:
                # 尝试将难度值转换为整数
                difficulty = int(challenge.difficulty)
                if difficulty == 1:
                    difficulty_stats["easy"] += 1
                elif difficulty == 2:
                    difficulty_stats["medium"] += 1
                elif difficulty == 3:
                    difficulty_stats["hard"] += 1
            except:
                # 如果转换失败，跳过该记录
                pass
    except:
        # 如果查询失败，使用默认值
        difficulty_stats = {
            "easy": 0,
            "medium": 0,
            "hard": 0
        }
    
    # 已完成题目数和正确率统计
    completed_count = 0
    avg_accuracy = 0
    recent_accuracy = 0
    
    # 尝试从请求中获取用户ID
    user_id = request.query_params.get('user_id')
    if user_id:
        try:
            # 查询该用户的练习记录
            practice_records = PracticeRecord.objects.filter(student_id=user_id)
            # 获取所有相关的题目
            questions = Question.objects.filter(record__in=practice_records)
            # 计算已完成题目数量
            completed_count = questions.count()
            
            # 计算正确率
            if completed_count > 0:
                correct_count = questions.filter(correct=True).count()
                avg_accuracy = round((correct_count / completed_count) * 100, 2)
                
                # 计算最近正确率（最近5次练习的正确率）
                recent_records = practice_records.order_by('-date')[:5]
                recent_questions = Question.objects.filter(record__in=recent_records)
                recent_correct_count = recent_questions.filter(correct=True).count()
                if recent_questions.count() > 0:
                    recent_accuracy = round((recent_correct_count / recent_questions.count()) * 100, 2)
        except Exception as e:
            print(f"查询学生答题记录时出错: {e}")
            # 出错时使用默认值
            completed_count = 0
            avg_accuracy = 0
            recent_accuracy = 0
    
    # 返回统计数据
    return Response({
        "total_count": total_count,
        "completed_count": completed_count,
        "avg_accuracy": avg_accuracy,
        "recent_accuracy": recent_accuracy,
        "type_stats": type_stats,
        "difficulty_stats": difficulty_stats
    })

# 类视图（classInfo 定义，继承自 View 或其子类）
class question(View):
    def get(self, request):
        return HttpResponse("学生信息页面（类视图）")


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    习题视图集：列表、详情、创建、我的习题、学科列表
    """
    queryset = Exercise.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ["title", "analysis"]
    ordering_fields = ["create_time", "use_count"]
    ordering = ["-create_time"]
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})

    def get_serializer_class(self):
        if self.action == 'create':
            return ExerciseCreateSerializer
        elif self.action == 'retrieve':
            return ExerciseDetailSerializer
        return ExerciseListSerializer

    @action(detail=False, methods=['get'], url_path='subjects')
    def get_subjects(self, request):
        """获取学科列表"""
        return Response([
            {"id": 1, "name": "默认学科"}
        ])


    def create(self, request, *args, **kwargs):
        """
        处理创建新习题的请求。
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"message": "习题创建成功！"},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Exercise.objects.all().annotate(
            title=F("name"),
            create_time=F("created_at"),
            use_count=F("visits"),
            analysis=Value("", output_field=TextField()),
        )

        # 处理查询参数
        subject_id = self.request.query_params.get('subjectId')
        difficulty = self.request.query_params.get('difficulty')
        type_ = self.request.query_params.get('type')
        keyword = self.request.query_params.get('keyword')

        if subject_id and subject_id.isdigit():
            queryset = queryset
        if difficulty:
            queryset = queryset
        if type_:
            queryset = queryset
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(exercise_id__icontains=keyword) |
                Q(status__icontains=keyword) |
                Q(fork_from__icontains=keyword)
            )

        return queryset

    # @action(detail=False, methods=['post'], url_path='add-to-my', permission_classes=[IsAuthenticated])
    #开发阶段暂时允许所有人访控
    @action(detail=True, methods=['post'], url_path='add-to-my', permission_classes=[AllowAny])
    def add_to_my(self, request):
        """批量或自定义添加到我的习题"""
        exercise_id = request.data.get("exercise_id") or request.data.get("exerciseId")
        if not exercise_id:
            return Response({"error": "缺少 exercise_id 参数"}, status=status.HTTP_400_BAD_REQUEST)

        exercise = None
        if str(exercise_id).isdigit():
            exercise = Exercise.objects.filter(id=int(exercise_id)).first()
        if not exercise:
            exercise = Exercise.objects.filter(exercise_id=str(exercise_id)).first()
        if not exercise:
            return Response({"error": "习题不存在"}, status=status.HTTP_404_NOT_FOUND)

        session_key = "my_exercise_ids"
        saved_ids = request.session.get(session_key, [])
        saved_ids = [str(x) for x in saved_ids]

        if str(exercise.pk) in saved_ids:
            return Response({"message": "该习题已在您的习题列表中"}, status=status.HTTP_200_OK)

        saved_ids.append(str(exercise.pk))
        request.session[session_key] = saved_ids
        return Response({"message": "习题已成功添加到您的习题列表！"}, status=status.HTTP_201_CREATED)
