import torch
import torch.nn.functional as F
import json
import requests
from safetensors.torch import load_file
from zhipuai import ZhipuAI
from transformers import GPTJConfig, GPTJModel

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
client = ZhipuAI(api_key="7296812e6d7e4ae1a8498156eddc8efb.XahVOK1vyVTT1xSy") 

def generate_graph_based_path(target_knowledge, student_mastery_dict, kg_rules_text):
    mastery_str = ""
    for point, mastery in student_mastery_dict.items():
        mastery_str += f" - 【{point}】掌握度为 {mastery * 100:.0f}%\n"
        
    dynamic_prompt = f"""
    你是一个基于知识图谱的智能导学系统。学生目标：【{target_knowledge}】。

    【约束条件1：学生当前知识状态】（来自 AAKT 模型预测）：
    {mastery_str}
    
    【约束条件2：教学逻辑图谱规则】（来自 Neo4j 图谱）：
    {kg_rules_text}
    
    请严格遵守图谱的先后逻辑，为学生生成最优复习与学习路径。
    必须纯 JSON 格式输出，包含 path (数组) 和 explanation (整体教育学解释)。
    """
    
    response = client.chat.completions.create(
        model="glm-4",  
        messages=[
            {"role": "system", "content": "你只能输出严格的JSON格式。"},
            {"role": "user", "content": dynamic_prompt}
        ],
    )
    result_str = response.choices[0].message.content
    if result_str.startswith("```json"):
        result_str = result_str[7:-3].strip()
    return json.loads(result_str)


# ==========================================
# 3. 全局初始化模型 (Django 启动时执行)
# ==========================================
print("Django 正在启动 AI 引擎...")
aakt_model = AAKT(
    num_questions = 4550, 
    num_tags = 4550, 
    with_tags = True, 
    with_times = True,
    max_seq_len = 500,
    n_layer = 4,
    n_embd = 128,
    n_head = 8,
    rotary_dim = 16
)

# 加载AAKT-main目录中的训练模型
weights_path = "../AAKT-main/output-Educoder-Final/model.safetensors"

try:
    aakt_model.load_state_dict(load_file(weights_path))
    aakt_model.eval()
    print("✅ 权重加载成功！AAKT 大脑已启动，随时可以接收前端请求。")
except Exception as e:
    print(f"❌ 加载失败，报错: {e}")


# ==========================================
# 4. 从 Neo4j 获取知识图谱规则
# ==========================================
def get_kg_rules_from_neo4j(target_knowledge):
    """
    从Neo4j数据库获取与目标知识点相关的先修关系规则
    """
    try:
        # 通过API调用获取先修关系
        url = f"http://localhost:8000/graphs/neo4j/prerequisites?target={target_knowledge}"
        response = requests.get(url)
        data = response.json()
        
        if data.get("code") == 200:
            return data.get("data", f"规则 A：未找到【{target_knowledge}】的先修知识点。")
        else:
            return f"规则 A：未找到【{target_knowledge}】的先修知识点。"
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        # 出错时返回默认规则
        return f"规则 A：未找到【{target_knowledge}】的先修知识点。"

# ==========================================
# 5. 供 Django 接口调用的主函数
# ==========================================
def get_smart_path_for_student(student_id, target_knowledge):
    """
    接收前端传来的学生ID和学习目标，返回大模型生成的 JSON 路径
    """
    # 模拟：获取该学生的做题记录 (未来对接数据库)
    dummy_input_ids = torch.randint(0, 1000, (1, 20), dtype=torch.long)
    dummy_input_times = torch.rand((1, 20), dtype=torch.float)
    
    with torch.no_grad():
        raw_preds = aakt_model(input_ids=dummy_input_ids, input_times=dummy_input_times)
    
    probabilities = F.softmax(raw_preds, dim=-1)
    
    # 模拟：映射出的薄弱知识点 (未来对接真实映射)
    student_status = {
        "一元一次方程": 0.35,  
        "合并同类项": 0.42,
        "等式的性质": 0.88
    }
    
    # 从Neo4j获取知识图谱规则
    kg_rules = get_kg_rules_from_neo4j(target_knowledge)
    
    # 最终调用大模型生成路径
    final_json = generate_graph_based_path(target_knowledge, student_status, kg_rules)
    return final_json