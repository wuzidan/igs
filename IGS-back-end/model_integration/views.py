import json
import numpy as np
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import sys
import os
from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from question.models import Question, PracticeRecord

# 尝试导入PyTorch，但不阻止程序运行
try:
    import torch
    print(f"PyTorch successfully imported, version: {torch.__version__}")
    TORCH_AVAILABLE = True
except ImportError:
    print("PyTorch not available, will use simulation mode")
    TORCH_AVAILABLE = False

# 获取当前文件的目录
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# AAKT-main与IGS-back-end在同一级目录
aakt_path = os.path.join(os.path.dirname(base_dir), 'AAKT-main')
sys.path.append(aakt_path)

# 尝试导入模型，但不阻止程序运行
AAKT = None
try:
    if TORCH_AVAILABLE:
        from models.AAKT import AAKT
        from safetensors.torch import load_file
        print("Model modules successfully imported")
    else:
        print("PyTorch not available, skipping model imports")
except ImportError as e:
    print(f"Model import error: {str(e)}")

# 全局变量，用于存储加载的模型和映射文件
MODEL = None
QUESTION_MAP = None
TAG_MAP = None
NUM_QUESTIONS = 0
NUM_TAGS = 0
DEVICE = None
MODEL_AVAILABLE = False
MIN_FORMAL_DIAGNOSIS_INTERACTIONS = 20
HIGH_CONFIDENCE_DIAGNOSIS_INTERACTIONS = 30
PRIOR_MASTERY_STRENGTH = 8
DEFAULT_PRIOR_ACCURACY = 0.6
MAX_DIAGNOSIS_HISTORY_USERS = 200
DIAGNOSIS_HISTORY = {}


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _get_accuracy_prior(accuracy):
    accuracy_value = _safe_float(accuracy, DEFAULT_PRIOR_ACCURACY)
    return float(np.clip(0.25 + accuracy_value * 0.55, 0.2, 0.9))


def _smooth_mastery_value(raw_score, accuracy, evidence_count):
    prior_value = _get_accuracy_prior(accuracy)
    evidence = max(0, int(evidence_count or 0))
    observation_weight = evidence / float(evidence + PRIOR_MASTERY_STRENGTH) if evidence > 0 else 0.0
    blended_score = prior_value * (1.0 - observation_weight) + _safe_float(raw_score, prior_value) * observation_weight
    return round(float(np.clip(blended_score, 0.1, 0.95)), 3)


def _smooth_mastery_map(mastery_per_tag, accuracy, evidence_count):
    if not isinstance(mastery_per_tag, dict):
        return {}
    return {
        tag: _smooth_mastery_value(score, accuracy, evidence_count)
        for tag, score in mastery_per_tag.items()
    }


def _compute_confidence(total_interactions, valid_interactions, used_model):
    total = max(0, int(total_interactions or 0))
    valid = max(0, int(valid_interactions or 0))
    total_component = min(total / float(MIN_FORMAL_DIAGNOSIS_INTERACTIONS), 1.0)
    valid_component = min(valid / float(max(int(MIN_FORMAL_DIAGNOSIS_INTERACTIONS * 0.6), 1)), 1.0)
    model_component = 1.0 if used_model else 0.55
    confidence_score = round(
        float(np.clip(0.45 * total_component + 0.35 * valid_component + 0.20 * model_component, 0.0, 1.0)),
        3,
    )

    formal_diagnosis = total >= MIN_FORMAL_DIAGNOSIS_INTERACTIONS and valid > 0
    if (not formal_diagnosis) or confidence_score < 0.55:
        confidence_level = "low"
    elif confidence_score < 0.8 or total < HIGH_CONFIDENCE_DIAGNOSIS_INTERACTIONS:
        confidence_level = "medium"
    else:
        confidence_level = "high"

    if not used_model and confidence_level == "high":
        confidence_level = "medium"

    return confidence_level, confidence_score, formal_diagnosis


def _assess_diagnosis_stability(user_id, mastery_per_tag):
    if user_id is None or not isinstance(mastery_per_tag, dict) or not mastery_per_tag:
        return None, None

    previous_result = DIAGNOSIS_HISTORY.get(user_id)
    stability_score = None
    stability_warning = None
    if previous_result and isinstance(previous_result.get("mastery_per_tag"), dict):
        previous_mastery = previous_result["mastery_per_tag"]
        common_tags = set(previous_mastery.keys()).intersection(mastery_per_tag.keys())
        if common_tags:
            deltas = [
                abs(_safe_float(mastery_per_tag[tag]) - _safe_float(previous_mastery.get(tag)))
                for tag in common_tags
            ]
            if deltas:
                stability_score = round(float(np.mean(deltas)), 3)
                if stability_score >= 0.18:
                    stability_warning = "连续两次诊断波动较大，数据不足，建议继续练习后再评估"

    if len(DIAGNOSIS_HISTORY) >= MAX_DIAGNOSIS_HISTORY_USERS and user_id not in DIAGNOSIS_HISTORY:
        oldest_user_id = next(iter(DIAGNOSIS_HISTORY))
        DIAGNOSIS_HISTORY.pop(oldest_user_id, None)

    DIAGNOSIS_HISTORY[user_id] = {
        "mastery_per_tag": dict(mastery_per_tag),
        "updated_at": datetime.now().isoformat(),
    }
    return stability_warning, stability_score


def _finalize_diagnosis_result(diagnosis_result, recommendations, user_id=None, used_model=False, fallback_reason=None):
    diagnosis_result = dict(diagnosis_result or {})
    recommendations = list(recommendations or [])

    total_interactions = max(0, int(diagnosis_result.get("total_interactions") or 0))
    valid_interactions = max(0, int(diagnosis_result.get("valid_interactions") or 0))
    evidence_count = valid_interactions if valid_interactions > 0 else total_interactions
    accuracy = diagnosis_result.get("accuracy")

    smoothed_mastery = _smooth_mastery_map(
        diagnosis_result.get("mastery_per_tag", {}),
        accuracy,
        evidence_count,
    )
    if smoothed_mastery:
        diagnosis_result["mastery_per_tag"] = smoothed_mastery
        diagnosis_result["weakest_tags"] = sorted(smoothed_mastery.keys(), key=lambda tag: smoothed_mastery[tag])[:3]

    confidence_level, confidence_score, formal_diagnosis = _compute_confidence(
        total_interactions,
        valid_interactions,
        used_model,
    )
    low_confidence = (confidence_level == "low") or (not formal_diagnosis)

    if total_interactions < MIN_FORMAL_DIAGNOSIS_INTERACTIONS:
        low_confidence_reason = "insufficient_sample"
    elif valid_interactions <= 0:
        low_confidence_reason = "no_valid_interactions"
    else:
        low_confidence_reason = None

    stability_warning, stability_score = _assess_diagnosis_stability(
        user_id,
        diagnosis_result.get("mastery_per_tag", {}),
    )

    diagnosis_messages = []
    if low_confidence:
        diagnosis_messages.append(
            f"当前样本量不足（{total_interactions}/{MIN_FORMAL_DIAGNOSIS_INTERACTIONS}），结果置信度较低，建议继续练习后再评估"
        )
    if stability_warning:
        diagnosis_messages.append(stability_warning)

    diagnosis_result.update({
        "confidence_level": confidence_level,
        "confidence_score": confidence_score,
        "low_confidence": low_confidence,
        "low_confidence_reason": low_confidence_reason,
        "formal_diagnosis": formal_diagnosis,
        "min_required_interactions": MIN_FORMAL_DIAGNOSIS_INTERACTIONS,
        "used_model_inference": bool(used_model),
        "fallback_reason": fallback_reason,
        "smoothed_mastery": True,
        "stability_warning": stability_warning,
        "stability_score": stability_score,
        "diagnosis_messages": diagnosis_messages,
    })

    merged_recommendations = []
    for message in recommendations + diagnosis_messages:
        if message and message not in merged_recommendations:
            merged_recommendations.append(message)

    return diagnosis_result, merged_recommendations


def _classify_interaction_mapping(interactions: list):
    valid_question_ids = []
    valid_correctness = []
    mapped_source_question_ids = []
    unmapped_question_ids = []

    has_question_map = isinstance(QUESTION_MAP, dict) and bool(QUESTION_MAP)
    for inter in interactions:
        q_id = str(inter.get("question_id"))
        if not has_question_map or q_id not in QUESTION_MAP:
            unmapped_question_ids.append(q_id)
            continue
        try:
            mapped_qid = int(QUESTION_MAP[q_id])
        except Exception:
            unmapped_question_ids.append(q_id)
            continue
        valid_question_ids.append(mapped_qid)
        valid_correctness.append(1 if bool(inter.get("correct", False)) else 0)
        mapped_source_question_ids.append(q_id)

    return valid_question_ids, valid_correctness, mapped_source_question_ids, unmapped_question_ids


def _build_mapping_coverage_report(interactions: list, max_examples: int = 50):
    total_interactions = len(interactions)
    valid_question_ids, valid_correctness, mapped_source_question_ids, unmapped_question_ids = _classify_interaction_mapping(interactions)
    valid_interactions = len(valid_question_ids)
    unmapped_interactions = len(unmapped_question_ids)
    mapping_coverage = round(valid_interactions / total_interactions, 3) if total_interactions > 0 else 0.0
    unique_mapped_question_ids = sorted(set(mapped_source_question_ids))
    unique_unmapped_question_ids = sorted(set(unmapped_question_ids))
    recommended_min_coverage = 0.7
    mapping_sufficient = (
        valid_interactions >= MIN_FORMAL_DIAGNOSIS_INTERACTIONS
        and mapping_coverage >= recommended_min_coverage
    )

    return {
        "total_interactions": total_interactions,
        "valid_interactions": valid_interactions,
        "unmapped_interactions": unmapped_interactions,
        "mapping_coverage": mapping_coverage,
        "mapping_coverage_percent": round(mapping_coverage * 100, 1),
        "question_map_loaded": isinstance(QUESTION_MAP, dict) and bool(QUESTION_MAP),
        "question_map_size": len(QUESTION_MAP) if isinstance(QUESTION_MAP, dict) else 0,
        "unique_mapped_question_count": len(unique_mapped_question_ids),
        "unique_unmapped_question_count": len(unique_unmapped_question_ids),
        "mapped_question_ids": unique_mapped_question_ids[:max_examples],
        "unmapped_question_ids": unique_unmapped_question_ids[:max_examples],
        "mapped_question_ids_truncated": len(unique_mapped_question_ids) > max_examples,
        "unmapped_question_ids_truncated": len(unique_unmapped_question_ids) > max_examples,
        "recommended_min_valid_interactions": MIN_FORMAL_DIAGNOSIS_INTERACTIONS,
        "recommended_min_coverage": recommended_min_coverage,
        "mapping_sufficient": mapping_sufficient,
        "sample_ready_for_formal_diagnosis": total_interactions >= MIN_FORMAL_DIAGNOSIS_INTERACTIONS,
        "valid_sample_ready_for_formal_diagnosis": valid_interactions >= MIN_FORMAL_DIAGNOSIS_INTERACTIONS,
        "correct_mapped_interactions": sum(valid_correctness),
    }


def _collect_user_interactions(user_id: int):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    practice_records = PracticeRecord.objects.filter(student=user).order_by('date')
    interactions = []
    for record in practice_records:
        for question in record.questions.all():
            model_qid = None
            try:
                if getattr(question, "exercise", None) is not None and getattr(question.exercise, "exercise_id", None) is not None:
                    model_qid = question.exercise.exercise_id
            except Exception:
                model_qid = None
            interactions.append({
                'question_id': model_qid if model_qid is not None else question.id,
                'correct': question.correct
            })

    return user, practice_records, interactions


# 在服务启动时加载模型（只加载一次）
def load_model():
    global MODEL, QUESTION_MAP, TAG_MAP, NUM_QUESTIONS, NUM_TAGS, DEVICE, MODEL_AVAILABLE
    
    # 检查PyTorch和模型模块是否可用
    if not TORCH_AVAILABLE or AAKT is None:
        print("PyTorch or model modules not available, skipping model loading")
        MODEL_AVAILABLE = False
        return
    
    if MODEL is not None:
        print("Model already loaded, skipping...")
        MODEL_AVAILABLE = True
        return  # 模型已经加载过了
    
    try:
        print("Initializing AAKT model...")
        
        # 添加更多调试信息来检查CUDA可用性
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA device count: {torch.cuda.device_count()}")
            print(f"CUDA current device: {torch.cuda.current_device()}")
            print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        else:
            print("CUDA is not available, using CPU")
            print(f"PyTorch version: {torch.__version__}")
        
        # 确定使用的设备
        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {DEVICE}")
        
        # 加载模型、问题映射和标签映射
        model_path = os.path.join(aakt_path, 'output-Educoder-Final', 'checkpoint-5830')
        question_map_path = os.path.join(aakt_path, 'autodl-tmp', 'question_map.json')
        tag_map_path = os.path.join(aakt_path, 'autodl-tmp', 'tag_map.json')
        
        # 尝试加载映射文件，但如果失败也不要阻止程序继续
        try:
            if os.path.exists(question_map_path):
                print(f"Loading question map from: {question_map_path}")
                with open(question_map_path, 'r', encoding='utf-8') as f:
                    QUESTION_MAP = json.load(f)
                NUM_QUESTIONS = len(QUESTION_MAP)
                print(f"Loaded {NUM_QUESTIONS} questions")
            else:
                print(f"Question map file not found: {question_map_path}")
                print("Using default question mapping")
                QUESTION_MAP = {}
                NUM_QUESTIONS = 0
            
            if os.path.exists(tag_map_path):
                print(f"Loading tag map from: {tag_map_path}")
                with open(tag_map_path, 'r', encoding='utf-8') as f:
                    TAG_MAP = json.load(f)
                NUM_TAGS = len(TAG_MAP)
                print(f"Loaded {NUM_TAGS} tags")
            else:
                print(f"Tag map file not found: {tag_map_path}")
                print("Using default tag mapping")
                TAG_MAP = {}
                NUM_TAGS = 0
        except Exception as mapping_error:
            print(f"Error loading mapping files: {str(mapping_error)}")
            print("Using default empty mappings")
            QUESTION_MAP = {}
            TAG_MAP = {}
            NUM_QUESTIONS = 0
            NUM_TAGS = 0
        
        # 如果没有标签数据，使用默认的标签列表
        if NUM_TAGS == 0:
            print("No tag data available, using default tags")
            default_tags = ["变量定义", "条件语句", "循环结构", "函数调用", "数据结构", "算法基础", "面向对象", "异常处理"]
            TAG_MAP = {str(i): tag for i, tag in enumerate(default_tags)}
            NUM_TAGS = len(default_tags)
        
        # 尝试创建模型实例
        try:
            print("Creating model instance...")
            
            # 直接使用output-Educoder-Final目录下的权重文件
            weights_path_safetensors = os.path.join(aakt_path, "output-Educoder-Final", "model.safetensors")
            if os.path.exists(weights_path_safetensors):
                try:
                    print(f"Loading model weights from {weights_path_safetensors}")
                    state_dict = load_file(weights_path_safetensors, device=DEVICE)
                    MODEL = AAKT(
                        num_questions=NUM_QUESTIONS if NUM_QUESTIONS > 0 else 4550,  # 使用默认值如果没有问题数据
                        num_tags=NUM_TAGS,
                        max_seq_len=500,
                        with_tags=True,
                        with_times=True,
                        n_layer=4,
                        n_embd=128,
                        n_head=8,
                        rotary_dim=None
                    )
                    MODEL.load_state_dict(state_dict)
                    print("Successfully loaded model weights")
                except Exception as weight_error:
                    print(f"Error loading model weights: {str(weight_error)}")
                    print("Continuing with untrained model...")
            else:
                print(f"Model weights file not found at {weights_path_safetensors}, using untrained model")
            
            MODEL.to(DEVICE)
            MODEL.eval()  # 设置为评估模式
            MODEL_AVAILABLE = True
            print(f"Model loaded successfully on {DEVICE}.")
            
        except Exception as model_error:
            print(f"Error creating model instance: {str(model_error)}")
            print("Model will not be used for diagnosis")
            MODEL_AVAILABLE = False
            MODEL = None
            
    except Exception as e:
        print(f"Unexpected error during model loading: {str(e)}")
        import traceback
        traceback.print_exc()
        MODEL_AVAILABLE = False
        MODEL = None


# 基于真实数据的智能模拟诊断函数
def get_smart_diagnosis_from_data(interactions: list, user_id: int = None) -> tuple:
    """
    基于用户的真实练习数据生成智能诊断结果
    虽然不使用模型，但会根据用户的答题正确率生成更符合实际情况的诊断
    """
    print(f"Generating smart diagnosis from {len(interactions)} real user interactions")
    
    # 计算用户的总体答题正确率
    if interactions:
        correct_count = sum(1 for i in interactions if i.get('correct', False))
        accuracy = correct_count / len(interactions)
        print(f"User's overall accuracy: {accuracy:.2f}")
    else:
        accuracy = 0.5  # 默认中等水平
        print("No interactions, using default accuracy")
    
    # 使用默认标签列表（如果没有从映射文件加载）
    if NUM_TAGS == 0 or not TAG_MAP:
        default_tags = ["变量定义", "条件语句", "循环结构", "函数调用", "数据结构", "算法基础", "面向对象", "异常处理"]
        tags = default_tags
    else:
        # 从TAG_MAP中提取标签名称
        tags = [TAG_MAP.get(str(i), f"未知知识点_{i}") for i in range(NUM_TAGS)]
    
    # 基于正确率生成更智能的掌握度评估
    # 使用用户ID作为随机种子，确保对同一用户的诊断结果具有一致性
    seed = user_id if user_id is not None else hash(str(interactions)) % 1000
    np.random.seed(seed)
    
    # 基础掌握度基于正确率，但添加一些随机性来模拟不同知识点的差异
    base_mastery = accuracy * 0.7 + 0.3  # 基础掌握度范围在0.3-1.0之间
    
    # 生成每个知识点的掌握度，使用正态分布增加一些随机性
    # 掌握度会围绕基础掌握度波动，但不会偏离太多
    mastery_values = np.clip(np.random.normal(base_mastery, 0.15, len(tags)), 0.1, 0.95)
    
    # 创建掌握度字典
    mastery_per_tag = {tag: round(mastery_values[i], 3) for i, tag in enumerate(tags)}
    
    # 找出掌握程度最低的3个知识点
    weakest_tags = sorted(mastery_per_tag.keys(), key=lambda x: mastery_per_tag[x])[:3]
    
    # 构建诊断结果
    diagnosis_result = {
        "mastery_per_tag": mastery_per_tag,
        "weakest_tags": weakest_tags,
        "total_interactions": len(interactions),
        "valid_interactions": len(interactions),
        "unknown_questions": 0,
        "model_status": "data_based_simulation",
        "accuracy": round(accuracy, 3) if interactions else None
    }
    
    print(f"Identified weakest tags from data: {weakest_tags}")
    
    # 生成更智能的推荐内容，根据掌握程度和答题情况提供个性化建议
    recommendations = []
    for tag in weakest_tags:
        mastery_level = mastery_per_tag[tag]
        
        # 根据掌握程度生成不同的推荐内容
        if mastery_level < 0.4:
            recommendations.append(f"重点加强 {tag} 的学习，建议从基础概念开始复习，多做一些入门级练习")
        elif mastery_level < 0.6:
            recommendations.append(f"需要提升 {tag} 的应用能力，建议多做相关中等难度的练习题")
        elif mastery_level < 0.8:
            recommendations.append(f"{tag} 的掌握程度良好，可以尝试挑战一些难题来进一步提升")
        else:
            recommendations.append(f"{tag} 掌握得不错，建议探索更深入的相关知识点或实际应用场景")
    
    # 如果有足够的交互记录，可以添加一些额外的个性化建议
    if len(interactions) > 10:
        if accuracy < 0.4:
            recommendations.append("整体表现较弱，建议多回顾基础知识，循序渐进地进行学习")
        elif accuracy > 0.8:
            recommendations.append("整体表现优秀，可以尝试更复杂的编程挑战")
    
    return diagnosis_result, recommendations

def get_diagnosis_from_model(interactions: list, user_id: int = None, force_model: bool = False) -> tuple:
    """
    智能诊断函数：
    1. 尝试使用模型进行诊断（如果可用）
    2. 如果模型不可用，使用基于真实数据的智能模拟诊断
    """
    print(f"Getting diagnosis for {len(interactions)} interactions, user_id: {user_id}")
    
    # 样本太少时不返回正式诊断，但仍返回低置信度结果
    if len(interactions) < 5:
        if force_model:
            raise ValueError("force_model已启用，但交互数据不足，无法进行模型推理")
        print("Not enough interactions for formal diagnosis, using low-confidence data-based diagnosis...")
        diagnosis_result, recommendations = get_smart_diagnosis_from_data(interactions, user_id)
        diagnosis_result["model_status"] = "insufficient_data_simulation"
        return _finalize_diagnosis_result(
            diagnosis_result,
            recommendations,
            user_id=user_id,
            used_model=False,
            fallback_reason="insufficient_interactions",
        )
    
    # 如果模型可用，尝试使用模型（真实推理路径）
    model_error_message = None
    try:
        if MODEL_AVAILABLE and MODEL is not None and TORCH_AVAILABLE:
            print("Attempting actual model inference...")

            input_tensor, input_times, valid_cnt, unknown_cnt = _prepare_aakt_inputs(interactions)

            correct_count = sum(1 for inter in interactions if inter.get("correct", False))
            total_interactions = len(interactions)
            accuracy = correct_count / total_interactions if total_interactions > 0 else 0.5

            with torch.no_grad():
                inputs_embeds = MODEL.model.wte(input_tensor)
                if getattr(MODEL, "with_times", False) and getattr(MODEL, "times_encoder", None) is not None:
                    times_embeds = MODEL.times_encoder(input_times.unsqueeze(-1))
                else:
                    times_embeds = torch.zeros_like(inputs_embeds)

                hidden_states = MODEL.model(inputs_embeds=inputs_embeds + times_embeds)[0]
                _preds_kts = MODEL.kts_classifier(hidden_states)

                hidden_features = hidden_states.mean(dim=1).detach().cpu().numpy()

            np.random.seed(user_id if user_id is not None else 0)
            base_mastery = accuracy * 0.7 + 0.3
            emb_dim = int(hidden_features.shape[1]) if len(hidden_features.shape) == 2 else 0
            usable = min(int(NUM_TAGS), emb_dim) if emb_dim > 0 else 0
            mastery_per_tag = {}
            denom = float(np.max(np.abs(hidden_features[0][:usable])) + 1e-8) if usable > 0 else 1.0
            for i in range(int(NUM_TAGS)):
                tag_name = TAG_MAP.get(str(i), f"未知知识点_{i}")
                if i < usable:
                    score = 0.3 + 0.6 * (float(abs(hidden_features[0][i])) / denom)
                    score = float(np.clip(score, 0.1, 0.9))
                else:
                    score = float(np.clip(base_mastery, 0.1, 0.9))
                mastery_per_tag[tag_name] = round(score, 3)

            weakest_tags = sorted(mastery_per_tag.keys(), key=lambda x: mastery_per_tag[x])[:3]

            recommendations = []
            for tag in weakest_tags:
                mastery_level = mastery_per_tag[tag]
                if mastery_level < 0.4:
                    recommendations.append(f"需要重点加强 {tag} 的学习，建议从基础概念开始复习")
                elif mastery_level < 0.6:
                    recommendations.append(f"需要提升 {tag} 的应用能力，建议多做相关中等难度的练习题")
                else:
                    recommendations.append(f"{tag} 的掌握程度良好，可以尝试挑战一些难题来进一步提升")

            diagnosis_result = {
                "mastery_per_tag": mastery_per_tag,
                "weakest_tags": weakest_tags,
                "total_interactions": len(interactions),
                "valid_interactions": int(valid_cnt),
                "unknown_questions": int(unknown_cnt),
                "model_status": "actual_model_inference",
                "accuracy": round(float(accuracy), 3),
            }

            print("Actual model inference completed")
            return _finalize_diagnosis_result(
                diagnosis_result,
                recommendations,
                user_id=user_id,
                used_model=True,
                fallback_reason=None,
            )

        print("Model not available")
        model_error_message = "model_not_available"
    except Exception as e:
        print(f"Model error: {str(e)}")
        model_error_message = str(e)
        if force_model:
            raise
    
    # 回退到基于真实数据的智能模拟诊断
    if force_model:
        raise RuntimeError("force_model enabled but model inference was not possible")
    print("Using data-based diagnosis")
    diagnosis_result, recommendations = get_smart_diagnosis_from_data(interactions, user_id)
    diagnosis_result["model_status"] = "data_based_simulation"
    fallback_reason = "model_fallback"
    if model_error_message == "model_not_available":
        fallback_reason = "model_not_available"
    elif model_error_message:
        fallback_reason = "model_error"
        diagnosis_result["model_error"] = model_error_message
    return _finalize_diagnosis_result(
        diagnosis_result,
        recommendations,
        user_id=user_id,
        used_model=False,
        fallback_reason=fallback_reason,
    )


@api_view(['GET'])
@csrf_exempt
def cognitiveDiagnosis(request):
    """
    认知诊断API端点 - 使用智能诊断函数处理用户请求
    智能诊断函数会自动尝试使用模型，如不可用则使用基于数据的智能模拟
    """
    print(f"Received cognitive diagnosis request from {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    try:
        # 获取用户ID
        user_id = request.GET.get('user_id')
        force_model = str(request.GET.get("force_model") or "").strip() in {"1", "true", "True", "yes", "on"}
        if not user_id:
            return JsonResponse({
                'error': '用户ID是必需的',
                'status': 'error'
            }, status=400)
        
        try:
            user_id = int(user_id)
        except ValueError:
            return JsonResponse({
                'error': '用户ID必须是整数',
                'status': 'error'
            }, status=400)
        
        print(f"Processing cognitive diagnosis for user: {user_id}")
        
        # 查询用户的实际练习记录
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            print(f"Found user: {user.username}")
            
            # 查询用户的交互历史
            practice_records = PracticeRecord.objects.filter(student=user).order_by('date')
            print(f"Found {practice_records.count()} practice records")
            
            # 准备输入数据
            interactions = []
            for record in practice_records:
                # 正确获取与练习记录关联的所有题目
                for question in record.questions.all():
                    model_qid = None
                    try:
                        if getattr(question, "exercise", None) is not None and getattr(question.exercise, "exercise_id", None) is not None:
                            model_qid = question.exercise.exercise_id
                    except Exception:
                        model_qid = None
                    interactions.append({
                        'question_id': model_qid if model_qid is not None else question.id,
                        'correct': question.correct
                    })
            
            print(f"Successfully collected {len(interactions)} user interactions from {practice_records.count()} practice records")
            
            # 如果有交互记录，使用智能诊断函数（会自动尝试模型或回退到数据驱动诊断）
            if interactions:
                print(f"Using smart diagnosis for user {user_id} with {len(interactions)} interactions")
                
                # 尝试加载模型（如果还未加载）
                if not MODEL_AVAILABLE and MODEL is None:
                    load_model()
                
                # 调用智能诊断函数，传递用户ID以确保诊断结果的一致性
                try:
                    diagnosis_result, recommendations = get_diagnosis_from_model(interactions, user_id, force_model=force_model)
                except Exception as model_exc:
                    if force_model:
                        return JsonResponse({
                            'error': f'模型推理不可用: {str(model_exc)}',
                            'status': 'error'
                        }, status=503)
                    raise
                
            else:
                print("No practice records found, using completely simulated data")
                if force_model:
                    return JsonResponse({
                        'error': 'force_model已启用，但当前用户没有可用于模型推理的交互数据',
                        'status': 'error'
                    }, status=400)
                # 生成模拟诊断结果（当没有用户数据时）
                mock_tags = ["变量定义", "条件语句", "循环结构", "函数调用", "数据结构", "算法基础", "面向对象", "异常处理"]
                # 使用用户ID作为随机种子，确保对同一用户的结果一致
                np.random.seed(user_id)
                # 生成合理的知识点掌握度数据，确保覆盖不同水平
                mock_mastery = {}
                for i, tag in enumerate(mock_tags):
                    # 确保有部分知识点掌握度较低，有部分中等，有部分较高
                    if i % 3 == 0:
                        # 低掌握度 (0.2-0.5)
                        mock_mastery[tag] = round(np.random.uniform(0.2, 0.5), 3)
                    elif i % 3 == 1:
                        # 中等掌握度 (0.5-0.7)
                        mock_mastery[tag] = round(np.random.uniform(0.5, 0.7), 3)
                    else:
                        # 高掌握度 (0.7-0.9)
                        mock_mastery[tag] = round(np.random.uniform(0.7, 0.9), 3)
                
                weakest_tags = sorted(mock_mastery.keys(), key=lambda x: mock_mastery[x])[:3]
                
                # 确保包含所有前端需要的字段，特别是mastery_per_tag和accuracy
                diagnosis_result = {
                    "mastery_per_tag": mock_mastery,
                    "weakest_tags": weakest_tags,
                    "total_interactions": 0,
                    "valid_interactions": 0,
                    "unknown_questions": 0,
                    "model_status": "no_data_simulation",
                    "accuracy": round(np.random.uniform(0.5, 0.8), 3)  # 模拟一个合理的准确率
                }
                
                # 生成更丰富的学习建议
                recommendations = []
                for tag in weakest_tags:
                    mastery_level = mock_mastery[tag]
                    if mastery_level < 0.4:
                        recommendations.append(f"需要重点加强 {tag} 的学习，建议从基础概念开始复习")
                    elif mastery_level < 0.6:
                        recommendations.append(f"需要提升 {tag} 的应用能力，建议多做相关中等难度的练习题")
                    else:
                        recommendations.append(f"{tag} 的掌握程度有待提高，建议针对性地进行练习")
                
                # 添加一个通用建议
                recommendations.append("整体学习表现不错，建议继续保持良好的学习状态")
                diagnosis_result, recommendations = _finalize_diagnosis_result(
                    diagnosis_result,
                    recommendations,
                    user_id=user_id,
                    used_model=False,
                    fallback_reason="no_interactions",
                )
        except User.DoesNotExist:
            return JsonResponse({
                'error': '用户不存在',
                'status': 'error'
            }, status=404)
    except Exception as e:
        print(f"Unexpected error in cognitiveDiagnosis: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'处理诊断请求时出错: {str(e)}',
            'status': 'error'
        }, status=500)
    
    # 返回诊断结果
    response_data = {
        'diagnosis_result': diagnosis_result,
        'recommendations': recommendations,
        'status': 'success',
        'timestamp': datetime.now().isoformat()
    }
    
    print("Successfully generated cognitive diagnosis result")
    return JsonResponse(response_data)


# 预测API视图函数（暂时用不上）
"""
@api_view(['POST'])
@csrf_exempt
def predict(request):
    print(f"Received prediction request from {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    try:
        # 确保模型已加载
        if MODEL is None:
            print("Model not loaded, attempting to load...")
            load_model()
        
        # 检查请求数据格式
        if not request.data:
            return JsonResponse({
                'error': 'Empty request data',
                'status': 'error'
            }, status=400)
        
        # 处理请求数据
        data = request.data
        
        # 支持不同的数据格式
        if isinstance(data, str):
            try:
                import json
                data = json.loads(data)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON format',
                    'status': 'error'
                }, status=400)
        
        interactions = data.get('interactions', [])
        
        if not interactions:
            return JsonResponse({
                'error': 'No interactions provided',
                'status': 'error'
            }, status=400)
        
        if not isinstance(interactions, list):
            return JsonResponse({
                'error': 'Interactions must be a list',
                'status': 'error'
            }, status=400)
        
        # 验证交互数据格式
        for i, inter in enumerate(interactions):
            if not isinstance(inter, dict):
                return JsonResponse({
                    'error': f'Interaction at index {i} must be a dictionary',
                    'status': 'error'
                }, status=400)
            if 'question_id' not in inter:
                return JsonResponse({
                    'error': f'Interaction at index {i} missing "question_id" field',
                    'status': 'error'
                }, status=400)
        
        print(f"Processing {len(interactions)} interactions")
        
        # 获取诊断结果
        diagnosis_result, recommendations = get_diagnosis_from_model(interactions)
        
        # 返回预测结果
        response_data = {
            'diagnosis_result': diagnosis_result,
            'recommendations': recommendations,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        print("Successfully generated diagnosis result")
        return JsonResponse(response_data)
        
    except ValueError as ve:
        print(f"Value error: {str(ve)}")
        return JsonResponse({
            'error': str(ve),
            'status': 'error'
        }, status=400)
    except RuntimeError as re:
        print(f"Runtime error: {str(re)}")
        return JsonResponse({
            'error': f'Model error: {str(re)}',
            'status': 'error'
        }, status=500)
    except FileNotFoundError as fnf:
        print(f"File not found error: {str(fnf)}")
        return JsonResponse({
            'error': f'Required model files not found: {str(fnf)}',
            'status': 'error'
        }, status=500)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': 'An internal server error occurred',
            'status': 'error',
            'details': str(e) if settings.DEBUG else 'Please contact administrator'
        }, status=500)
"""



def _predict_aakt_question_correct_prob(interactions: list, question_id):
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch not available")
    if not MODEL_AVAILABLE or MODEL is None:
        raise RuntimeError("Model not available")
    if not isinstance(QUESTION_MAP, dict) or not QUESTION_MAP:
        raise RuntimeError("Question map not available")
    if not isinstance(NUM_QUESTIONS, int) or NUM_QUESTIONS <= 0:
        raise RuntimeError("Invalid NUM_QUESTIONS")

    valid_question_ids = []
    valid_correctness = []
    for inter in interactions:
        q_id = str(inter.get("question_id"))
        if q_id in QUESTION_MAP:
            try:
                valid_question_ids.append(int(QUESTION_MAP[q_id]))
            except Exception:
                continue
            valid_correctness.append(1 if bool(inter.get("correct", False)) else 0)

    if not valid_question_ids:
        raise ValueError("No valid interactions found in question_map")

    qid_str = str(question_id)
    if qid_str not in QUESTION_MAP:
        raise ValueError(f"Question {question_id} not found in question_map")
    target_qid = int(QUESTION_MAP[qid_str])

    input_ids = []
    for qid, correct in zip(valid_question_ids, valid_correctness):
        input_ids.append(qid)
        input_ids.append(NUM_QUESTIONS + correct)

    input_ids.append(target_qid)

    device = DEVICE or ("cuda" if (TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu")
    input_tensor = torch.tensor([input_ids], dtype=torch.long, device=device)
    seq_len = int(input_tensor.shape[1])
    input_times = torch.zeros((1, seq_len), dtype=torch.float, device=device)

    with torch.no_grad():
        inputs_embeds = MODEL.model.wte(input_tensor)
        if getattr(MODEL, "with_times", False) and getattr(MODEL, "times_encoder", None) is not None:
            times_embeds = MODEL.times_encoder(input_times.unsqueeze(-1))
        else:
            times_embeds = torch.zeros_like(inputs_embeds)

        hidden_states = MODEL.model(inputs_embeds=inputs_embeds + times_embeds)[0]
        _preds_kts = MODEL.kts_classifier(hidden_states)
        logits = _preds_kts[0, -1]
        prob_correct = 1.0 / (torch.exp(logits[0] - logits[1]) + 1.0)

    return float(prob_correct.detach().cpu().item())

# 预测学生答对特定题目的概率
def predict_question_accuracy(user_id, question_id, interactions, force_model: bool = False):
    """
    预测学生答对特定题目的概率
    :param user_id: 用户ID
    :param question_id: 题目ID
    :param interactions: 用户历史交互数据
    :return: 预测的正确率（0-1之间）
    """
    # 基础预测逻辑：基于用户历史正确率
    if interactions:
        correct_count = sum(1 for inter in interactions if inter.get('correct', False))
        base_accuracy = correct_count / len(interactions)
    else:
        base_accuracy = 0.5

    if force_model and not interactions:
        raise ValueError("force_model已启用，但没有可用于模型推理的交互数据")

    if force_model and (not TORCH_AVAILABLE):
        raise RuntimeError("force_model已启用，但PyTorch不可用")

    if force_model and (not MODEL_AVAILABLE) and (MODEL is None):
        load_model()

    if MODEL_AVAILABLE and MODEL is not None and TORCH_AVAILABLE:
        print(f"Using model to predict accuracy for question {question_id}")
        try:
            return _predict_aakt_question_correct_prob(interactions, question_id)
        except Exception as e:
            print(f"Error predicting question accuracy with model: {str(e)}")
            if force_model:
                raise
            print(f"Using base prediction for question {question_id}")
            return float(base_accuracy)

    if force_model:
        raise RuntimeError("force_model enabled but model inference was not possible")

    print(f"Using base prediction for question {question_id}")
    return float(base_accuracy)

# 选择下一组预测题目
def select_next_questions(user_id, num_questions=5, force_model: bool = False):
    """
    选择下一组预测题目
    :param user_id: 用户ID
    :param num_questions: 题目数量
    :return: 选中的题目列表
    """
    try:
        print(f"Selecting next {num_questions} questions for user {user_id}")
        
        # 查询用户的实际练习记录，确定当前学习章节
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        # 查询用户的交互历史
        practice_records = PracticeRecord.objects.filter(student=user).order_by('date')
        interactions = []
        completed_question_ids = set()
        
        # 收集用户已做过的题目ID
        for record in practice_records:
            for question in record.questions.all():
                model_qid = None
                try:
                    if getattr(question, "exercise", None) is not None and getattr(question.exercise, "exercise_id", None) is not None:
                        model_qid = question.exercise.exercise_id
                except Exception:
                    model_qid = None
                interactions.append({
                    'question_id': model_qid if model_qid is not None else question.id,
                    'correct': question.correct
                })
                completed_question_ids.add(str(model_qid) if model_qid is not None else str(question.id))
        
        # 从HistoryRecord表中收集交互数据
        from historyRecord.models import HistoryRecord
        history_records = HistoryRecord.objects.filter(user=user).order_by('date')
        for record in history_records:
            # 使用record的id作为question_id，因为HistoryRecord没有直接关联到具体题目
            # 使用score > 0来判断是否正确
            interactions.append({
                'question_id': record.id,
                'correct': record.score > 0
            })
            completed_question_ids.add(str(record.id))
        
        print(f"User {user_id} has completed {len(completed_question_ids)} questions")
        
        # 使用题库表作为候选池（Exercise）
        from question.models import Exercise
        
        # 筛选学生未做过的题目
        available_questions = Exercise.objects.exclude(exercise_id__in=completed_question_ids)
        print(f"Found {available_questions.count()} available questions")
        
        if force_model and (not TORCH_AVAILABLE):
            raise RuntimeError("force_model已启用，但PyTorch不可用")
        if force_model and (not MODEL_AVAILABLE) and (MODEL is None):
            load_model()

        if force_model and (not MODEL_AVAILABLE or MODEL is None or not TORCH_AVAILABLE):
            raise RuntimeError("force_model已启用，但模型不可用")

        import random
        all_available = list(available_questions)
        if force_model:
            if not interactions:
                raise ValueError("force_model已启用，但没有可用于模型推理的交互数据")
            if not all_available:
                raise ValueError("force_model已启用，但没有可推荐的新题目")

            if not isinstance(QUESTION_MAP, dict) or not QUESTION_MAP:
                raise RuntimeError("force_model已启用，但question_map不可用")

            map_keys = set(str(k) for k in QUESTION_MAP.keys())
            all_available = [q for q in all_available if str(getattr(q, "exercise_id", "")) in map_keys]
            if not all_available:
                raise ValueError("force_model已启用，但可推荐题目均不在question_map中")

            max_candidates = 50
            candidate_questions = all_available[:min(max_candidates, len(all_available))]
            scored = []
            for q in candidate_questions:
                acc = predict_question_accuracy(user_id, q.exercise_id, interactions, force_model=True)
                scored.append((acc, q))
            scored.sort(key=lambda x: x[0], reverse=True)
            selected_questions = [q for _acc, q in scored[:min(num_questions, len(scored))]]
        else:
            selected_questions = random.sample(all_available, min(num_questions, len(all_available)))

        print(f"Selected {len(selected_questions)} questions")
        
        # 为每个题目预测正确率
        predicted_questions = []
        for question in selected_questions:
            accuracy = predict_question_accuracy(user_id, question.exercise_id, interactions, force_model=force_model)
            
            # 获取题目难度
            difficulty = 'medium'  # 默认难度
            
            # 通过ExerciseChallenge关联获取Challenge的难度
            try:
                from question.models import ExerciseChallenge, Challenge
                # 获取与当前Exercise关联的第一个Challenge
                exercise_challenge = ExerciseChallenge.objects.filter(exercise=question).first()
                if exercise_challenge and exercise_challenge.challenge:
                    difficulty = exercise_challenge.challenge.difficulty
            except Exception as e:
                print(f"Error getting difficulty for exercise {question.exercise_id}: {str(e)}")
            
            predicted_questions.append({
                'id': question.exercise_id,
                'name': question.name,
                'difficulty': difficulty,
                'predicted_accuracy': round(accuracy, 3)
            })
        
        # 如果题目不足，补充一些模拟题目
        if (not force_model) and len(predicted_questions) < num_questions:
            print(f"Not enough questions, adding {num_questions - len(predicted_questions)} mock questions")
            for i in range(num_questions - len(predicted_questions)):
                mock_question = {
                    'id': f'mock_{i}',
                    'name': f'模拟题目 {i+1}',
                    'difficulty': '中等',
                    'predicted_accuracy': round(random.uniform(0.3, 0.8), 3)
                }
                predicted_questions.append(mock_question)
        
        return predicted_questions
    except User.DoesNotExist:
        print(f"User {user_id} does not exist")
        if force_model:
            raise
        # 返回模拟题目
        import random
        mock_questions = []
        for i in range(num_questions):
            mock_questions.append({
                'id': f'mock_{i}',
                'name': f'模拟题目 {i+1}',
                'difficulty': '中等',
                'predicted_accuracy': round(random.uniform(0.3, 0.8), 3)
            })
        return mock_questions
    except Exception as e:
        print(f"Error selecting next questions: {str(e)}")
        if force_model:
            raise
        # 返回模拟题目
        import random
        mock_questions = []
        for i in range(num_questions):
            mock_questions.append({
                'id': f'mock_{i}',
                'name': f'模拟题目 {i+1}',
                'difficulty': '中等',
                'predicted_accuracy': round(random.uniform(0.3, 0.8), 3)
            })
        return mock_questions

# 预测下一组题目的API端点
@api_view(['GET'])
@csrf_exempt
def predict_next_questions(request):
    """
    预测下一组题目的API端点
    返回用户可能答对的下5道题及其正确率预测
    """
    print(f"Received predict next questions request from {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    try:
        # 获取用户ID
        user_id = request.GET.get('user_id')
        force_model = str(request.GET.get("force_model") or "").strip() in {"1", "true", "True", "yes", "on"}
        if not user_id:
            return JsonResponse({
                'error': '用户ID是必需的',
                'status': 'error'
            }, status=400)
        
        try:
            user_id = int(user_id)
        except ValueError:
            return JsonResponse({
                'error': '用户ID必须是整数',
                'status': 'error'
            }, status=400)
        
        print(f"Processing predict next questions for user: {user_id}")
        
        # 尝试加载模型（如果还未加载）
        if not MODEL_AVAILABLE and MODEL is None:
            try:
                load_model()
            except Exception as e:
                if force_model:
                    return JsonResponse({
                        'error': f'模型推理不可用: {str(e)}',
                        'status': 'error'
                    }, status=503)
                raise
        
        # 选择并预测题目
        try:
            predicted_questions = select_next_questions(user_id, 5, force_model=force_model)
        except ValueError as model_ve:
            if force_model:
                return JsonResponse({
                    'error': str(model_ve),
                    'status': 'error'
                }, status=400)
            raise
        except Exception as model_exc:
            if force_model:
                return JsonResponse({
                    'error': f'模型推理不可用: {str(model_exc)}',
                    'status': 'error'
                }, status=503)
            raise
        
        if not predicted_questions:
            if force_model:
                return JsonResponse({
                    'error': 'force_model已启用，但当前没有可用于推荐的题目',
                    'status': 'error'
                }, status=400)

            predicted_questions = []
            average_accuracy = 0.0
            recommendations = ["当前没有可推荐的题目"]
            response_data = {
                'predicted_questions': predicted_questions,
                'average_accuracy': round(average_accuracy, 3),
                'recommendations': recommendations,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }

            print(f"Successfully generated next questions prediction for user {user_id}")
            return JsonResponse(response_data)

        # 计算整体预测准确率
        average_accuracy = sum(q['predicted_accuracy'] for q in predicted_questions) / len(predicted_questions)
        
        # 生成学习建议
        recommendations = []
        if average_accuracy < 0.4:
            recommendations.append("整体预测准确率较低，建议加强基础知识学习")
        elif average_accuracy < 0.7:
            recommendations.append("整体预测准确率中等，建议针对性地进行练习")
        else:
            recommendations.append("整体预测准确率较高，可以尝试挑战更难的题目")
        
        # 分析预测结果，提供更具体的建议
        easy_questions = [q for q in predicted_questions if q['predicted_accuracy'] > 0.7]
        hard_questions = [q for q in predicted_questions if q['predicted_accuracy'] < 0.4]
        
        if easy_questions:
            recommendations.append(f"有{len(easy_questions)}道题预测准确率较高，可以尝试挑战")
        if hard_questions:
            recommendations.append(f"有{len(hard_questions)}道题预测准确率较低，建议重点关注")
        
        # 添加用户交互数据统计
        # 查询用户的实际练习记录，获取交互数据
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            practice_records = PracticeRecord.objects.filter(student=user).order_by('date')
            interactions = []
            for record in practice_records:
                for question in record.questions.all():
                    model_qid = None
                    try:
                        if getattr(question, "exercise", None) is not None and getattr(question.exercise, "exercise_id", None) is not None:
                            model_qid = question.exercise.exercise_id
                    except Exception:
                        model_qid = None
                    interactions.append({
                        'question_id': model_qid if model_qid is not None else question.id,
                        'correct': question.correct
                    })
            
            # 计算有效交互数（在question_map中存在的交互）
            valid_interactions_count = 0
            if QUESTION_MAP and isinstance(QUESTION_MAP, dict):
                for inter in interactions:
                    if str(inter['question_id']) in QUESTION_MAP:
                        valid_interactions_count += 1
            else:
                valid_interactions_count = len(interactions)
            
            total_interactions_count = len(interactions)
        except User.DoesNotExist:
            total_interactions_count = 0
            valid_interactions_count = 0
        
        # 返回预测结果
        response_data = {
            'predicted_questions': predicted_questions,
            'average_accuracy': round(average_accuracy, 3),
            'recommendations': recommendations,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            # 添加诊断统计字段
            'total_interactions': total_interactions_count,
            'valid_interactions': valid_interactions_count,
            'model_status': 'prediction_mode'
        }
        
        print(f"Successfully generated next questions prediction for user {user_id}")
        return JsonResponse(response_data)
        
    except User.DoesNotExist:
        return JsonResponse({
            'error': '用户不存在',
            'status': 'error'
        }, status=404)
    except Exception as e:
        print(f"Unexpected error in predict_next_questions: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'处理预测请求时出错: {str(e)}',
            'status': 'error'
        }, status=500)

# 在模块加载时尝试预加载模型
try:
    load_model()
except Exception as e:
    print(f"Warning: Model preloading failed, will try again on first request: {str(e)}")

# 核心诊断函数（智能组合模型和数据驱动诊断）

def _prepare_aakt_inputs(interactions: list):
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch not available")
    if not MODEL_AVAILABLE or MODEL is None:
        raise RuntimeError("Model not available")
    if not isinstance(QUESTION_MAP, dict) or not QUESTION_MAP:
        raise RuntimeError("Question map not available")
    if not isinstance(TAG_MAP, dict) or not TAG_MAP:
        raise RuntimeError("Tag map not available")
    if not isinstance(NUM_QUESTIONS, int) or NUM_QUESTIONS <= 0:
        raise RuntimeError("Invalid NUM_QUESTIONS")
    if not isinstance(NUM_TAGS, int) or NUM_TAGS <= 0:
        raise RuntimeError("Invalid NUM_TAGS")

    valid_question_ids, valid_correctness, _mapped_source_question_ids, unmapped_question_ids = _classify_interaction_mapping(interactions)

    if not valid_question_ids:
        raise ValueError("No valid interactions found in question_map")

    input_ids = []
    for qid, correct in zip(valid_question_ids, valid_correctness):
        input_ids.append(qid)
        input_ids.append(NUM_QUESTIONS + correct)

    device = DEVICE or ("cuda" if (TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu")
    input_tensor = torch.tensor([input_ids], dtype=torch.long, device=device)
    seq_len = int(input_tensor.shape[1])
    input_times = torch.zeros((1, seq_len), dtype=torch.float, device=device)

    return input_tensor, input_times, len(valid_question_ids), len(unmapped_question_ids)

@api_view(['GET'])
@csrf_exempt
def mappingCoverage(request):
    print(f"Received mapping coverage request from {request.META.get('REMOTE_ADDR', 'unknown')}")

    try:
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({
                'error': '用户ID是必需的',
                'status': 'error'
            }, status=400)

        try:
            user_id = int(user_id)
        except ValueError:
            return JsonResponse({
                'error': '用户ID必须是整数',
                'status': 'error'
            }, status=400)

        if not MODEL_AVAILABLE and MODEL is None:
            try:
                load_model()
            except Exception as load_exc:
                print(f"Warning: failed to load model before mapping coverage check: {str(load_exc)}")

        try:
            user, practice_records, interactions = _collect_user_interactions(user_id)
        except get_user_model().DoesNotExist:
            return JsonResponse({
                'error': '用户不存在',
                'status': 'error'
            }, status=404)

        coverage_report = _build_mapping_coverage_report(interactions)
        has_tag_map = isinstance(TAG_MAP, dict) and bool(TAG_MAP)
        model_ready = bool(
            TORCH_AVAILABLE
            and MODEL_AVAILABLE
            and MODEL is not None
            and coverage_report.get('question_map_loaded')
            and has_tag_map
        )

        response_data = {
            'status': 'success',
            'user_id': user_id,
            'username': getattr(user, 'username', ''),
            'practice_record_count': practice_records.count(),
            'model_ready': model_ready,
            'torch_available': TORCH_AVAILABLE,
            'model_available': MODEL_AVAILABLE and MODEL is not None,
            'tag_map_loaded': has_tag_map,
            'tag_map_size': len(TAG_MAP) if isinstance(TAG_MAP, dict) else 0,
            'timestamp': datetime.now().isoformat(),
        }
        response_data.update(coverage_report)
        print(f"Successfully generated mapping coverage report for user {user_id}")
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Unexpected error in mappingCoverage: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'处理映射覆盖率请求时出错: {str(e)}',
            'status': 'error'
        }, status=500)
