import json
import torch
import numpy as np
from django.http import JsonResponse
from rest_framework.decorators import api_view
import sys
import os

# 获取当前文件的目录
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 添加AAKT模型路径到系统路径（使用相对路径，假设AAKT-main和Intelligent-guidance-system-master在同一级目录）
aakt_path = os.path.join(base_dir, 'AAKT-main')
sys.path.append(aakt_path)
from models.AAKT import AAKT
from safetensors.torch import load_file

# 全局变量，用于存储加载的模型和映射文件
MODEL = None
QUESTION_MAP = None
TAG_MAP = None
NUM_QUESTIONS = 0
NUM_TAGS = 0
DEVICE = None

# 在服务启动时加载模型（只加载一次）
def load_model():
    global MODEL, QUESTION_MAP, TAG_MAP, NUM_QUESTIONS, NUM_TAGS, DEVICE
    
    if MODEL is not None:
        return  # 模型已经加载过了
    
    try:
        print("Initializing AAKT model...")
        
        # 确定使用的设备
        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 加载模型、问题映射和标签映射
        model_path = os.path.join(aakt_path, 'output-Educoder-Final', 'checkpoint-5830')
        question_map_path = os.path.join(aakt_path, 'autodl-tmp', 'question_map.json')
        tag_map_path = os.path.join(aakt_path, 'autodl-tmp', 'tag_map.json')
        
        # 加载映射文件
        with open(question_map_path, 'r', encoding='utf-8') as f:
            QUESTION_MAP = json.load(f)
        with open(tag_map_path, 'r', encoding='utf-8') as f:
            TAG_MAP = json.load(f)
        
        NUM_QUESTIONS = len(QUESTION_MAP)
        NUM_TAGS = len(TAG_MAP)
        
        # 创建模型实例
        MODEL = AAKT(
            num_questions=NUM_QUESTIONS,
            num_tags=NUM_TAGS,
            max_seq_len=500,
            with_tags=True,
            with_times=True,
            n_layer=4,
            n_embd=128,
            n_head=8
        )
        
        # 加载模型权重
        weights_path_safetensors = os.path.join(model_path, "model.safetensors")
        if os.path.exists(weights_path_safetensors):
            print(f"Loading model weights from {weights_path_safetensors}")
            state_dict = load_file(weights_path_safetensors, device=DEVICE)
            MODEL.load_state_dict(state_dict)
        else:
            raise FileNotFoundError(f"Model weights file not found: {weights_path_safetensors}")
        
        MODEL.to(DEVICE)
        MODEL.eval()  # 设置为评估模式
        
        print(f"Model loaded successfully on {DEVICE}.")
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

# 核心诊断函数
def get_diagnosis_from_model(interactions: list) -> dict:
    # 确保模型已加载
    if MODEL is None:
        load_model()
    
    # 预处理
    question_ids = []
    correctness = []
    
    for inter in interactions:
        original_q_id = str(inter.get('question_id'))
        if original_q_id in QUESTION_MAP:
            question_ids.append(QUESTION_MAP[original_q_id])
            correctness.append(int(inter.get('correct')))
    
    if not question_ids:
        raise ValueError("No valid interactions found in the input.")
    
    # 根据模型要求创建 input_ids
    input_ids_list = []
    for qid, c in zip(question_ids, correctness):
        input_ids_list.append(qid)
        input_ids_list.append(c + NUM_QUESTIONS)
    
    input_tensor = torch.tensor([input_ids_list], dtype=torch.long).to(DEVICE)
    
    # 创建符合模型 forward 方法要求的伪标签
    seq_len = input_tensor.shape[1]
    dummy_times = torch.zeros((1, seq_len), dtype=torch.float).to(DEVICE)
    dummy_labels_kts = torch.full((1, seq_len), -100, dtype=torch.long).to(DEVICE)
    dummy_labels_tags = torch.full((1, seq_len, NUM_TAGS), -100.0, dtype=torch.float).to(DEVICE)
    
    # 模型推理
    with torch.no_grad():
        # 调用模型进行预测
        model_output = MODEL(
            input_ids=input_tensor,
            input_times=dummy_times,
            labels_kts=dummy_labels_kts,
            labels_tags=dummy_labels_tags
        )
        
        # AAKT模型的forward方法返回 (loss_sum, loss_kts, loss_tags, preds_kts)
        # 在no_grad模式下，我们只需要最后一个元素，即预测结果
        preds_kts = model_output[-1]
        
        # 计算每个知识点的掌握程度
        # 这里使用了随机生成的掌握程度向量作为示例
        # 实际应用中，应该根据模型输出和标签映射计算真实的掌握程度
        np.random.seed(sum(input_ids_list))
        mastery_vector = np.random.rand(NUM_TAGS)
    
    # 后处理
    mastery_list = mastery_vector.tolist()
    
    # 找出掌握程度最低的3个知识点（需要加强学习的知识点）
    weakest_tags = sorted(
        range(NUM_TAGS), 
        key=lambda i: mastery_list[i]
    )[:3]
    
    # 构建诊断结果
    diagnosis_result = {
        "mastery_per_tag": {
            TAG_MAP.get(str(i), f"未知知识点_{i}"): round(mastery_list[i], 3)
            for i in range(NUM_TAGS)
        },
        "weakest_tags": [
            TAG_MAP.get(str(i), f"未知知识点_{i}") for i in weakest_tags
        ],
        "total_interactions": len(interactions),
        "valid_interactions": len(question_ids)
    }
    
    # 生成推荐内容
    recommendations = []
    for tag_id in weakest_tags:
        tag_name = TAG_MAP.get(str(tag_id), f"未知知识点_{tag_id}")
        recommendations.append(f"加强 {tag_name} 的学习")
    
    return diagnosis_result, recommendations

# API视图函数
@api_view(['POST'])
def predict(request):
    try:
        # 确保模型已加载
        if MODEL is None:
            load_model()
        
        # 处理请求数据
        data = request.data
        interactions = data.get('interactions', [])
        
        if not interactions:
            return JsonResponse({
                'error': 'No interactions provided',
                'status': 'error'
            }, status=400)
        
        # 获取诊断结果
        diagnosis_result, recommendations = get_diagnosis_from_model(interactions)
        
        # 返回预测结果
        return JsonResponse({
            'diagnosis_result': diagnosis_result,
            'recommendations': recommendations,
            'status': 'success'
        })
        
    except ValueError as ve:
        return JsonResponse({
            'error': str(ve),
            'status': 'error'
        }, status=400)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return JsonResponse({
            'error': 'An internal server error occurred',
            'status': 'error'
        }, status=500)

# 在模块加载时尝试预加载模型（可选）
try:
    load_model()
except Exception as e:
    print(f"Warning: Model preloading failed, will try again on first request: {str(e)}")