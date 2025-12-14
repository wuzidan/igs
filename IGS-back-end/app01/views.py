from django.shortcuts import render, HttpResponse
# from app01.models import aigroup
from django.core import serializers
import json
from django.http import JsonResponse

from app01.models import UserInfo


# # Create your views here.
# def index(request):
#     data_list = aigroup.objects.all()
#     data_list1 = aigroup.objects.filter(kind='数与代数')
#     data_list2 = aigroup.objects.filter(kind='图形与几何')
#     data_list3 = aigroup.objects.filter(kind='统计与概率')
#     data_list4 = aigroup.objects.filter(kind='量与计算')
#     data_list5 = aigroup.objects.filter(kind='逻辑与思维训练')
#     data_list6 = aigroup.objects.filter(kind='综合与实践')
#     return render(request, "index.html",
#                   {"data_list": data_list, "data_list1": data_list1, "data_list2": data_list2, "data_list3": data_list3,
#                    "data_list4": data_list4, "data_list5": data_list5, "data_list6": data_list6})
#
#
# def update_aigroup_percent(request):
#     if request.method == 'POST':
#         # 更新kind为"语法"的记录的percent为0.28
#         updated_count = aigroup.objects.filter(kind='语法').update(percent=0.28)
#         aigroup.objects.filter(kind='数据结构').update(percent=0.08)
#         if updated_count > 0:
#             return JsonResponse({'status': 'success', 'message': '更新成功'})
#         else:
#             return JsonResponse({'status': 'error', 'message': '未找到符合条件的记录'}, status=404)
#     return JsonResponse({'status': 'error', 'message': '仅支持POST请求'}, status=405)

#
# def user_list(request):
#     # 去app目录下的templates目录中找user_list.html(根据app的注册顺序，逐一去他们的templates目录中找）
#     return render(request, "user_list.html")
#
#
# def user_add(request):
#     return HttpResponse("添加用户")
#
#
# def tpl(request):
#     name = "wzd"
#     list = ["cyt", "wzd"]
#     return render(request, 'tpl.html', {"n1": name, "list": list})
#
#
# def test(request):
#     print(request.GET)
#     return HttpResponse("终于成功啦！")
#

# def login(request):
#     if request.method == "GET":
#         return render(request, "login.html")
#     else:
#         data_list = aigroup.objects.all()
#         data_list1 = aigroup.objects.filter(kind='数与代数')
#         data_list2 = aigroup.objects.filter(kind='图形与几何')
#         data_list3 = aigroup.objects.filter(kind='统计与概率')
#         data_list4 = aigroup.objects.filter(kind='量与计算')
#         data_list5 = aigroup.objects.filter(kind='逻辑与思维训练')
#         data_list6 = aigroup.objects.filter(kind='综合与实践')
#         return render(request, "index.html",
#                       {"data_list": data_list, "data_list1": data_list1, "data_list2": data_list2,
#                        "data_list3": data_list3, "data_list4": data_list4, "data_list5": data_list5,
#                        "data_list6": data_list6})
#
#
# def challenge_detail(request, item_id):
#     item = aigroup.objects.get(id=item_id)
#     # 将 item 模型实例转换为字典（提取需要的字段）
#     item_dict = {
#         'id': item.id,
#         'name': item.name,
#         'kind': item.kind,
#         'content': item.content,
#         'analysis': item.analysis,
#         # 其他需要的字段（如 answer）
#         'answer': item.answer  # 假设模型有 answer 字段
#     }
#     # 序列化为 JSON 字符串
#     item_json = json.dumps(item_dict)
#     # 同时确保 data_json 正确序列化（之前的逻辑）
#     data_list = list(aigroup.objects.all().values('id', 'name', 'content', 'analysis', 'answer'))
#     data_json = json.dumps(data_list)
#     return render(request, 'challenge_detail.html', {
#         'item_json': item_json,  # 传递 JSON 字符串
#         'data_json': data_json
#     })

# 视图函数名修改为与模型类不同的名称，例如 user_info_list
def user_info_list(request):
    # 此时 UserInfo 会正确指向模型类
    data_list = UserInfo.objects.all()
    return render(request, "info_list.html", {"data_list": data_list})
