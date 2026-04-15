from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ai_service import get_smart_path_for_student

@api_view(['POST'])
def recommend_path(request):
    """
    路径推荐API
    接收学生ID和目标知识点，返回个性化学习路径
    """
    try:
        # 获取请求数据
        data = request.data
        student_id = data.get('student_id')
        target_knowledge = data.get('target_knowledge')
        
        # 验证参数
        if not student_id or not target_knowledge:
            return Response(
                {"error": "缺少必要参数: student_id 和 target_knowledge"},
                status=400
            )
        
        # 调用路径推荐函数
        result = get_smart_path_for_student(student_id, target_knowledge)
        
        # 返回结果
        return Response(result)
        
    except Exception as e:
        return Response(
            {"error": f"内部服务器错误: {str(e)}"},
            status=500
        )
