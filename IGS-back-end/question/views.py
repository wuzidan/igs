# question/views.py
from django.views import View
from django.http import JsonResponse

# 类视图（class 定义，继承自 View 或其子类）
class question(View):
    def get(self, request):
        # 返回符合前端期望格式的题库数据
        # 前端期望格式: res.data.data 包含题目列表
        # 每个题目需要有: id, quiz, result, analysis, type等字段
        question_data = {
            "data": [
                # 单选题示例 (type=0)
                {
                    "id": 1,
                    "quiz": "下列哪种数据结构是线性的？\nA. 树\nB. 图\nC. 数组\nD. 二叉树",
                    "result": "C",
                    "analysis": "数组是一种线性数据结构，而树、图和二叉树都属于非线性数据结构。",
                    "type": 0
                },
                # 多选题示例 (type=1)
                {
                    "id": 2,
                    "quiz": "下列哪些排序算法是稳定的？\nA. 冒泡排序\nB. 快速排序\nC. 插入排序\nD. 堆排序",
                    "result": "AC",
                    "analysis": "冒泡排序和插入排序是稳定的排序算法，而快速排序和堆排序是不稳定的。",
                    "type": 1
                },
                # 判断题示例 (type=2)
                {
                    "id": 3,
                    "quiz": "快速排序的平均时间复杂度是O(n log n)。",
                    "result": "对",
                    "analysis": "快速排序的平均时间复杂度确实是O(n log n)，但最坏情况下是O(n²)。",
                    "type": 2
                },
                # 简答题示例 (type=3)
                {
                    "id": 4,
                    "quiz": "简述二叉搜索树的基本性质。",
                    "result": "二叉搜索树具有以下性质：1. 若任意节点的左子树不空，则左子树上所有节点的值均小于它的根节点的值；2. 若任意节点的右子树不空，则右子树上所有节点的值均大于它的根节点的值；3. 任意节点的左、右子树也分别为二叉搜索树。",
                    "analysis": "二叉搜索树是一种特殊的二叉树，它支持快速的查找、插入和删除操作，平均时间复杂度为O(log n)。",
                    "type": 3
                },
                # 更多单选题示例
                {
                    "id": 5,
                    "quiz": "Python中，以下哪个不是可变数据类型？\nA. 列表(list)\nB. 字典(dict)\nC. 元组(tuple)\nD. 集合(set)",
                    "result": "C",
                    "analysis": "在Python中，元组(tuple)是不可变的数据类型，而列表、字典和集合都是可变的。",
                    "type": 0
                }
            ]
        }
        return JsonResponse(question_data, safe=False)