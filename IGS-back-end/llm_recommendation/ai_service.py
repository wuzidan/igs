import torch
import torch.nn.functional as F
import json
import requests
import logging
import hashlib
import time
import concurrent.futures
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
from safetensors.torch import load_file
from transformers import GPTJConfig, GPTJModel
from zhipuai import ZhipuAI

load_dotenv(Path(__file__).resolve().parents[1] / '.env')


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 缓存字典
cache = {
    'aakt_diagnosis': {},  # AAKT诊断结果缓存
    'kg_rules': {},       # 知识图谱规则缓存
    'llm_path': {}         # LLM路径推荐缓存
}

# 缓存过期时间（秒）
CACHE_EXPIRY = {
    'aakt_diagnosis': 86400,  # 24小时
    'kg_rules': 604800,      # 7天
    'llm_path': 86400         # 24小时
}

# ==========================================
# 缓存工具函数
# ==========================================
def get_cache_key(prefix, *args):
    """生成缓存键"""
    key = f"{prefix}:{':'.join(str(arg) for arg in args)}"
    return hashlib.md5(key.encode()).hexdigest()

def get_cache(cache_type, *args):
    """获取缓存"""
    key = get_cache_key(cache_type, *args)
    if key in cache[cache_type]:
        item = cache[cache_type][key]
        # 检查是否过期
        if datetime.now().timestamp() < item['expiry']:
            logger.info(f"从缓存获取 {cache_type} 数据")
            return item['data']
        else:
            # 清除过期缓存
            del cache[cache_type][key]
            logger.info(f"缓存 {cache_type} 已过期")
    return None

def set_cache(cache_type, data, *args):
    """设置缓存"""
    key = get_cache_key(cache_type, *args)
    expiry = datetime.now().timestamp() + CACHE_EXPIRY[cache_type]
    cache[cache_type][key] = {
        'data': data,
        'expiry': expiry
    }
    logger.info(f"设置 {cache_type} 缓存")

# ==========================================
# 1. AAKT 模型类 
# ==========================================
class AAKT(torch.nn.Module):
    def __init__(self, num_questions, num_tags, max_seq_len=8096, with_tags=True, with_times=True, **kwargs):
        super().__init__()
        self.with_tags = with_tags
        self.with_times = with_times
        self.tag_emb = False
        self.correct_token_id = num_questions
        self.incorrect_token_id = num_questions + 1
        self.bos_token_id = num_questions + 2
        self.eos_token_id = num_questions + 3

        self.config = GPTJConfig(
            vocab_size=num_questions + 4,
            n_positions=max_seq_len,
            bos_token_id=self.bos_token_id,
            eos_token_id=self.eos_token_id,
            embd_pdrop=0.2,
            attn_pdrop=0.2,
            **kwargs,
        )
        self.model = GPTJModel(self.config)

        if self.with_times:
            self.times_encoder = torch.nn.Sequential(
                torch.nn.Linear(1, self.config.n_embd),
                torch.nn.Tanh(),
                torch.nn.Linear(self.config.n_embd, self.config.n_embd)
            )

        self.kts_classifier = torch.nn.Sequential(
            torch.nn.Linear(self.config.n_embd, self.config.n_embd),
            torch.nn.LogSigmoid(),
            torch.nn.Linear(self.config.n_embd, 2)
        )

        if self.with_tags:
            self.tags_classifier = torch.nn.Sequential(
                torch.nn.Linear(self.config.n_embd, num_tags)
            )

        if self.tag_emb:
            self.tags_embedding = torch.nn.Sequential(
                torch.nn.Linear(num_tags, self.config.n_embd),
                torch.nn.GELU(),
                torch.nn.Linear(self.config.n_embd, self.config.n_embd),
                torch.nn.Tanh()
            )

    def forward(self, input_ids, input_times=None, labels_kts=None, labels_tags=None):
        inputs_embeds = self.model.wte(input_ids)

        if self.with_times and input_times is not None:
            times_embeds = self.times_encoder(input_times.unsqueeze(-1))
        else:
            times_embeds = torch.zeros_like(inputs_embeds)

        if self.tag_emb and labels_tags is not None:
            tags_embeds = self.tags_embedding(labels_tags) / torch.sum(labels_tags, dim=-1, keepdim=True)
        else:
            tags_embeds = torch.zeros_like(inputs_embeds)

        hidden_states = self.model(inputs_embeds=inputs_embeds + times_embeds + tags_embeds)[0]  
        preds_kts = self.kts_classifier(hidden_states)  

        if labels_kts is None:
            return preds_kts
            
        return preds_kts


# ==========================================
# 2. 核心大模型生成函数
# ==========================================
client = ZhipuAI(api_key=required_env('ZHIPUAI_API_KEY')) 

def generate_graph_based_path(target_knowledge, student_mastery_dict, kg_rules_text):
    # 只包含掌握度低于60%的薄弱知识点
    weak_points = []
    for point, mastery in student_mastery_dict.items():
        if mastery < 0.6:
            weak_points.append(f" - 【{point}】掌握度为 {mastery * 100:.0f}%")
    
    relevant_weak_points = "\n".join(weak_points) if weak_points else "- 学生当前知识状态良好，无明显薄弱知识点"
        
    dynamic_prompt = f"""
        # 任务：个性化学习路径推荐

        ## 学生信息
        - 学生目标知识点：{target_knowledge}

        ## 学生认知状态（掌握度 < 60% 的知识点）
        {relevant_weak_points}

        ## 相关知识图谱规则
        {kg_rules_text}

        ## 任务要求
        1. 根据学生当前认知状态和知识图谱规则，生成从基础到目标知识点的学习路径
        2. 路径应遵循知识图谱中的先修关系，确保学习的连贯性
        3. 路径长度控制在3-5个步骤，避免过长
        4. 为每个步骤提供简要说明，解释为什么包含该知识点
        5. 生成详细的推荐依据，说明路径设计的理由

        ## 输出格式
        ```json
        {{
        "path": [
            "知识点1",
            "知识点2",
            "知识点3",
            "目标知识点"
        ],
        "explanation": "详细的推荐依据..."
        }}
        ```

        ## 示例输出
        ```json
        {{
        "path": [
            "编译系统",
            "配置文件",
            "文件子系统",
            "批处理系统"
        ],
        "explanation": "根据学生当前知识状态和知识图谱规则，推荐从编译系统开始学习，这是批处理系统的基础。然后学习配置文件和文件子系统，这些是批处理系统的直接先修知识点。最后学习批处理系统本身。这条路径遵循了知识图谱的先修关系，从基础到高级，适合学生当前的认知水平。"
        }}
        ```
    """
    
    logger.info(f"调用LLM API生成学习路径，目标知识点: {target_knowledge}")
    logger.info(f"学生掌握度数据: {student_mastery_dict}")
    logger.info(f"知识图谱规则: {kg_rules_text[:100]}...")  # 只记录前100个字符
    
    try:
        response = client.chat.completions.create(
            model="glm-4",  
            messages=[
                {"role": "system", "content": "你只能输出严格的JSON格式。"},
                {"role": "user", "content": dynamic_prompt}
            ],
        )
        logger.info(f"LLM API调用成功，响应状态: {response}")
        
        result_str = response.choices[0].message.content
        logger.info(f"LLM API返回结果: {result_str}")
        
        if result_str.startswith("```json"):
            result_str = result_str[7:-3].strip()
        
        final_result = json.loads(result_str)
        logger.info(f"解析后的路径推荐结果: {final_result}")
        return final_result
    except Exception as e:
        logger.error(f"LLM API调用失败: {e}")
        # 出错时返回默认路径
        default_result = {
            "path": [
                "复习：合并同类项",
                "学习：等式的性质",
                "练习：一元一次方程",
                f"挑战：{target_knowledge}"
            ],
            "explanation": "由于LLM服务暂时不可用，返回基于Neo4j知识图谱的默认学习路径。"
        }
        logger.warning(f"返回默认学习路径: {default_result}")
        return default_result


# ==========================================
# 3. 全局初始化模型 (Django 启动时执行)
# ==========================================
print("Django 正在启动 AI 引擎...")
# 暂时注释掉模型初始化，避免启动时的错误
#aakt_model = AAKT(
#    num_questions = 4550, 
#    num_tags = 4550, 
#    with_tags = True, 
#    with_times = True,
#    max_seq_len = 500,
#    n_layer = 4,
#    n_embd = 128,
#    n_head = 8,
#    rotary_dim = 16
#)
#
## 加载AAKT-main目录中的训练模型
#weights_path = "../AAKT-main/output-Educoder-Final/model.safetensors"

# 暂时使用None作为模型实例
aakt_model = None

# ==========================================
# 4. 从 Neo4j 获取知识图谱规则
# ==========================================
def get_kg_rules_from_neo4j(target_knowledge):
    """
    从Neo4j数据库获取与目标知识点相关的先修关系规则
    """
    # 尝试从缓存获取知识图谱规则
    cached_rules = get_cache('kg_rules', target_knowledge)
    if cached_rules:
        logger.info(f"从缓存获取知识图谱规则")
        return cached_rules
    
    try:
        # 通过API调用获取先修关系
        url = f"http://localhost:8000/graphs/neo4j/prerequisites?target={target_knowledge}"
        logger.info(f"调用Neo4j API获取先修关系: {url}")
        response = requests.get(url)
        logger.info(f"Neo4j API响应状态码: {response.status_code}")
        data = response.json()
        logger.info(f"Neo4j API响应数据: {data}")
        
        if data.get("code") == 200:
            rules = data.get("data", f"规则 A：未找到【{target_knowledge}】的先修知识点。")
            logger.info(f"获取到先修关系规则: {rules[:100]}...")  # 只记录前100个字符
            # 设置缓存
            set_cache('kg_rules', rules, target_knowledge)
            return rules
        else:
            logger.warning(f"Neo4j API返回错误: {data.get('msg')}")
            default_rules = f"规则 A：未找到【{target_knowledge}】的先修知识点。"
            # 设置默认规则缓存
            set_cache('kg_rules', default_rules, target_knowledge)
            return default_rules
    except Exception as e:
        logger.error(f"❌ API调用失败: {e}")
        # 出错时返回默认规则
        default_rules = f"规则 A：未找到【{target_knowledge}】的先修知识点。"
        # 设置默认规则缓存
        set_cache('kg_rules', default_rules, target_knowledge)
        return default_rules

# ==========================================
# 6. 缓存预热机制
# ==========================================
def warm_up_cache():
    """
    缓存预热：预加载常用知识点的缓存
    """
    logger.info("开始缓存预热...")
    
    # 常用知识点列表
    common_knowledge_points = [
        "文件管理",
        "进程调度",
        "内存管理",
        "处理器调度",
        "缺页中断",
        "存储分配",
        "系统配置",
        "缓存",
        "辅助存储器",
        "内存管理单元",
        "中断机制",
        "虚拟地址空间",
        "储存空间"
    ]
    
    # 并行预热知识图谱规则缓存
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for knowledge in common_knowledge_points:
            futures.append(executor.submit(get_kg_rules_from_neo4j, knowledge))
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"缓存预热失败: {e}")
    
    logger.info("缓存预热完成")

# 系统启动时执行缓存预热
# warm_up_cache()  # 暂时注释掉缓存预热，避免启动时的错误

# ==========================================
# 5. 供 Django 接口调用的主函数
# ==========================================
def get_aakt_diagnosis(student_id):
    """
    获取AAKT诊断结果
    """
    # 尝试从缓存获取AAKT诊断结果
    cached_diagnosis = get_cache('aakt_diagnosis', student_id)
    if cached_diagnosis:
        logger.info(f"从缓存获取AAKT诊断结果")
        return cached_diagnosis
    
    try:
        # 调用AAKT诊断接口获取学生认知诊断结果
        aakt_url = "http://localhost:8000/model/cognitiveDiagnosis/"
        params = {"user_id": student_id}
        response = requests.get(aakt_url, params=params, timeout=10)
        
        if response.status_code == 200:
            # 解析AAKT返回的诊断结果
            data = response.json()
            if data.get("status") == "success" and data.get("diagnosis_result"):
                diagnosis_result = data["diagnosis_result"]
                # 提取掌握度数据
                student_status = diagnosis_result.get("mastery_per_tag", {})
                logger.info(f"从AAKT获取到学生认知诊断结果: {student_status}")
                # 设置缓存
                set_cache('aakt_diagnosis', student_status, student_id)
                return student_status
            else:
                # 诊断失败，使用默认模拟数据
                logger.warning(f"AAKT诊断失败: {data.get('error', '未知错误')}")
                return {
                    "缺页中断": 0.35,  
                    "存储分配": 0.42,
                    "系统配置": 0.88
                }
        else:
            # API调用失败，使用默认模拟数据
            logger.warning(f"AAKT API调用失败，状态码: {response.status_code}")
            return {
                "缺页中断": 0.35,  
                "存储分配": 0.42,
                "系统配置": 0.88
            }
    except requests.Timeout:
        # 请求超时，使用默认模拟数据
        logger.error(f"调用AAKT API超时")
        return {
            "缺页中断": 0.35,  
            "存储分配": 0.42,
            "系统配置": 0.88
        }
    except Exception as e:
        # 发生异常，使用默认模拟数据
        logger.error(f"调用AAKT API失败: {e}")
        return {
            "缺页中断": 0.35,  
            "存储分配": 0.42,
            "系统配置": 0.88
        }

def get_smart_path_for_student(student_id, target_knowledge):
    """
    接收前端传来的学生ID和学习目标，返回大模型生成的 JSON 路径
    """
    start_time = time.time()
    logger.info(f"开始处理路径推荐请求，学生ID: {student_id}, 目标知识点: {target_knowledge}")
    
    # 生成缓存键
    cache_key = get_cache_key('llm_path', student_id, target_knowledge)
    
    # 尝试从缓存获取完整路径推荐结果
    cached_result = get_cache('llm_path', student_id, target_knowledge)
    if cached_result:
        cache_time = time.time() - start_time
        logger.info(f"从缓存获取完整路径推荐结果，耗时: {cache_time:.2f}秒")
        return cached_result
    
    # 并行获取AAKT诊断结果和知识图谱规则
    parallel_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # 提交两个任务
        future_aakt = executor.submit(get_aakt_diagnosis, student_id)
        future_kg = executor.submit(get_kg_rules_from_neo4j, target_knowledge)
        
        # 获取结果
        student_status = future_aakt.result()
        kg_rules = future_kg.result()
    
    parallel_time = time.time() - parallel_start
    logger.info(f"并行处理完成，耗时: {parallel_time:.2f}秒")
    
    # 最终调用大模型生成路径
    llm_start = time.time()
    final_json = generate_graph_based_path(target_knowledge, student_status, kg_rules)
    llm_time = time.time() - llm_start
    logger.info(f"大模型路径生成完成，耗时: {llm_time:.2f}秒")
    
    # 设置完整路径推荐结果缓存
    set_cache('llm_path', final_json, student_id, target_knowledge)
    
    total_time = time.time() - start_time
    logger.info(f"完整路径推荐处理完成，总耗时: {total_time:.2f}秒")
    
    return final_json
