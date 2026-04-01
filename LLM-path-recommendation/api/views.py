import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# 引入我们写在 ai_service.py 里的 AI 大脑
from .ai_service import get_smart_path_for_student  

@csrf_exempt  
def recommend_path_api(request):
    if request.method == "POST":
        try:
            # 解析前端发来的数据
            body = json.loads(request.body)
            student_id = body.get("student_id", "stu_001")
            target_knowledge = body.get("target", "一元二次方程") 
            
            # 调用 AI 引擎计算路径
            result_data = get_smart_path_for_student(student_id, target_knowledge)
            
            # 把 JSON 发给前端
            return JsonResponse({
                "code": 200,
                "msg": "可解释性路径生成成功",
                "data": result_data  
            }, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            return JsonResponse({
                "code": 500,
                "msg": f"服务器内部错误: {str(e)}"
            }, json_dumps_params={'ensure_ascii': False})
            
    return JsonResponse({"code": 405, "msg": "只支持 POST 请求"}, json_dumps_params={'ensure_ascii': False})