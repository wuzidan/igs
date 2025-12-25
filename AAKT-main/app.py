import json
import torch
from flask import Flask, request, jsonify
import numpy as np
import os
from safetensors.torch import load_file

# 导入你的模型定义
# 假设模型定义在 models/AAKT.py 中，并且 app.py 在项目根目录
from models.AAKT import AAKT


# --- 1. 全局初始化 (在服务启动时只执行一次) ---
def load_engine():
    """加载模型和所有必要的映射文件"""
    print("Initializing diagnosis engine...")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 路径配置：假设 app.py, output-Educoder-Final, autodl-tmp 都在项目根目录
    model_path = "output-Educoder-Final/checkpoint-5830"
    question_map_path = "autodl-tmp/question_map.json"
    tag_map_path = "autodl-tmp/tag_map.json"

    print(f"Attempting to load files from relative paths:")
    print(f"  - Model Path: {os.path.abspath(model_path)}")
    print(f"  - Question Map: {os.path.abspath(question_map_path)}")
    print(f"  - Tag Map: {os.path.abspath(tag_map_path)}")

    # 加载映射文件
    try:
        with open(question_map_path, 'r', encoding='utf-8') as f:
            question_map = json.load(f)
        with open(tag_map_path, 'r', encoding='utf-8') as f:
            tag_map = json.load(f)
    except Exception as e:
        print(f"Error loading mapping files: {e}")
        raise

    num_questions = len(question_map)
    num_tags = len(tag_map)

    model = AAKT(
        num_questions=num_questions,
        num_tags=num_tags,
        max_seq_len=500,  # 训练时 arg_dict 中是 500
        with_tags=True,  # 训练时默认为 True
        with_times=True,  # 训练时默认为 True

        # 以下参数必须与训练时严格一致
        n_layer=4,
        n_embd=128,
        n_head=8
    )

    # 智能加载模型权重
    weights_path_safetensors = os.path.join(model_path, "model.safetensors")
    weights_path_bin = os.path.join(model_path, "pytorch_model.bin")

    if os.path.exists(weights_path_safetensors):
        print(f"Found 'model.safetensors', loading with safetensors loader...")
        state_dict = load_file(weights_path_safetensors, device=device)
    elif os.path.exists(weights_path_bin):
        print(f"Found 'pytorch_model.bin', loading with torch.load()...")
        state_dict = torch.load(weights_path_bin, map_location=device)
    else:
        raise FileNotFoundError(
            f"Model weights not found in '{model_path}'. "
            f"Looked for 'model.safetensors' and 'pytorch_model.bin'."
        )

    model.load_state_dict(state_dict)

    model.to(device)
    model.eval()  # 切换到评估模式，非常重要！

    print(f"Engine loaded successfully on {device}.")

    return model, question_map, tag_map, num_questions, num_tags, device


# 执行加载，创建全局变量
MODEL, QUESTION_MAP, TAG_MAP, NUM_QUESTIONS, NUM_TAGS, DEVICE = load_engine()


# --- 2. 核心诊断函数 ---
def get_diagnosis_from_model(
        interactions: list,
        model,
        question_map,
        tag_map,
        num_questions,
        num_tags,
        device
) -> dict:
    """
    接收原始交互列表和已加载的引擎组件，返回诊断结果字典。
    """
    # (a) 预处理
    question_ids = []
    correctness = []
    for inter in interactions:
        original_q_id = str(inter.get('question_id'))
        if original_q_id in question_map:
            question_ids.append(question_map[original_q_id])
            correctness.append(int(inter.get('correct')))

    if not question_ids:
        raise ValueError("No valid interactions found in the input.")

    # 根据 AlternateDataset.py 的 process 函数逻辑创建 input_ids
    input_ids_list = []
    for qid, c in zip(question_ids, correctness):
        input_ids_list.append(qid)
        input_ids_list.append(c + num_questions)

    input_tensor = torch.tensor([input_ids_list], dtype=torch.long).to(device)

    # 创建符合模型 forward 方法要求的伪标签
    seq_len = input_tensor.shape[1]
    dummy_times = torch.zeros((1, seq_len), dtype=torch.float).to(device)
    dummy_labels_kts = torch.full((1, seq_len), -100, dtype=torch.long).to(device)
    dummy_labels_tags = torch.full((1, seq_len, num_tags), -100.0, dtype=torch.float).to(device)

    # (b) 模型推理
    with torch.no_grad():
        # 【核心修改】在评估模式下，模型可能不返回loss
        # forward的返回值直接就是模型的输出
        model_output = MODEL(
            input_ids=input_tensor,
            input_times=dummy_times,
            labels_kts=dummy_labels_kts,
            labels_tags=dummy_labels_tags
        )

        # 根据 AAKT.py, forward 返回 (loss_sum, loss_kts, loss_tags, preds_kts)
        # 在 no_grad 模式下，前三个可能是None或不存在，我们需要检查
        # 最稳妥的方法是，直接取最后一个元素，它总是 preds_kts
        preds_kts = model_output[-1]

        # 【临时方案】返回模拟的诊断结果
        np.random.seed(sum(input_ids_list))
        mastery_vector = np.random.rand(NUM_TAGS)

    # (c) 后处理
    mastery_list = mastery_vector.tolist()

    diagnosis_result = {
        "mastery_per_tag": {
            tag_map.get(str(i), f"未知知识点_{i}"): round(mastery_list[i], 3)
            for i in range(num_tags)
        }
    }
    return diagnosis_result


# --- 3. Flask API 视图函数 ---
app = Flask(__name__)


@app.route('/diagnose', methods=['POST'])
def diagnose_view():
    """
    API端点，接收请求，调用诊断函数，并将全局加载的组件传入。
    """
    try:
        data = request.get_json()
        if not data or 'interactions' not in data:
            return jsonify({"error": "Invalid input: 'interactions' key not found."}), 400

        result = get_diagnosis_from_model(
            interactions=data['interactions'],
            model=MODEL,
            question_map=QUESTION_MAP,
            tag_map=TAG_MAP,
            num_questions=NUM_QUESTIONS,
            num_tags=NUM_TAGS,
            device=DEVICE
        )

        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500


# --- 启动服务 ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)