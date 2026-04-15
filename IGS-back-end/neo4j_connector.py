"""
Neo4j 连接管理模块
提供单例模式的Neo4j连接，供多个组件使用
"""
from neo4j import GraphDatabase
from django.conf import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jConnector:
    """Neo4j连接管理类，使用单例模式"""
    _instance = None
    
    def __new__(cls, uri=None, user=None, password=None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(Neo4jConnector, cls).__new__(cls)
            cls._instance._initialize(uri, user, password)
        return cls._instance
    
    def _initialize(self, uri, user, password):
        """初始化Neo4j连接"""
        try:
            # 从settings.py读取配置，如果没有则使用默认值
            self.uri = uri or getattr(settings, 'NEO4J_URI', "bolt://localhost:7687")
            self.user = user or getattr(settings, 'NEO4J_USER', "neo4j")
            self.password = password or getattr(settings, 'NEO4J_PASSWORD', "neo4j")
            
            # 创建驱动实例
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            
            # 测试连接
            self.test_connection()
            logger.info("✅ Neo4j连接初始化成功")
            
        except Exception as e:
            logger.error(f"❌ Neo4j连接初始化失败: {e}")
            self.driver = None
    
    def test_connection(self):
        """测试Neo4j连接"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS num")
                for record in result:
                    logger.info(f"✅ 连接测试成功，返回: {record['num']}")
            return True
        except Exception as e:
            logger.error(f"❌ 连接测试失败: {e}")
            return False
    
    def query(self, cypher_query, parameters=None):
        """
        执行Cypher查询
        :param cypher_query: Cypher查询语句
        :param parameters: 查询参数
        :return: 查询结果列表
        """
        try:
            if not self.driver:
                logger.error("❌ 驱动未初始化")
                return []
            
            with self.driver.session() as session:
                result = session.run(cypher_query, parameters)
                return [record for record in result]
        except Exception as e:
            logger.error(f"❌ 查询执行失败: {e}")
            return []
    
    def get_prerequisite_relations(self, target_node):
        """
        获取目标节点的先修关系
        :param target_node: 目标节点名称
        :return: 先修关系规则文本
        """
        # Cypher查询：获取目标节点的直接和间接先修关系
        query = """
        MATCH (s)-[:PREREQUISITE]->(t) 
        WHERE t.name = $target
        RETURN s.name as source, t.name as target
        UNION
        MATCH (s)-[:PREREQUISITE]->(m)-[:PREREQUISITE]->(t) 
        WHERE t.name = $target
        RETURN s.name as source, m.name as target
        """
        
        try:
            results = self.query(query, parameters={"target": target_node})
            
            # 构建规则文本
            rules = []
            rule_id = 1
            
            for record in results:
                source = record["source"]
                target = record["target"]
                rules.append(f"规则 {chr(64 + rule_id)}：【{source}】是【{target}】的先修知识点。")
                rule_id += 1
            
            # 如果没有找到规则，返回默认规则
            if not rules:
                return f"规则 A：未找到【{target_node}】的先修知识点。"
            
            return "\n".join(rules)
        except Exception as e:
            logger.error(f"❌ 获取先修关系失败: {e}")
            return f"规则 A：未找到【{target_node}】的先修知识点。"
    
    def get_knowledge_graph(self):
        """
        获取完整的知识图谱数据，用于前端展示
        :return: 知识图谱节点和关系
        """
        # Cypher查询：获取所有节点和关系
        query_nodes = """
        MATCH (n) 
        RETURN id(n) as id, n.name as name, labels(n) as labels, 'node' as type
        """
        
        query_relationships = """
        MATCH (s)-[r]->(t) 
        RETURN id(s) as source, id(t) as target, type(r) as relationship_type, 'relationship' as type
        """
        
        try:
            # 执行节点查询
            node_results = self.query(query_nodes)
            # 执行关系查询
            relationship_results = self.query(query_relationships)
            
            # 处理节点结果
            nodes = []
            for record in node_results:
                nodes.append({
                    "id": record["id"],
                    "name": record["name"],
                    "labels": record["labels"]
                })
            
            # 处理关系结果
            relationships = []
            for record in relationship_results:
                relationships.append({
                    "source": record["source"],
                    "target": record["target"],
                    "type": record["relationship_type"]
                })
            
            return {
                "nodes": nodes,
                "relationships": relationships
            }
        except Exception as e:
            logger.error(f"❌ 获取知识图谱失败: {e}")
            return {"nodes": [], "relationships": []}
    
    def close(self):
        """关闭Neo4j连接"""
        try:
            if self.driver:
                self.driver.close()
                logger.info("✅ Neo4j连接已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭连接失败: {e}")

# 全局实例（延迟初始化）
_neo4j_connector_instance = None

def get_neo4j_connector():
    """获取Neo4j连接器实例（延迟初始化）"""
    global _neo4j_connector_instance
    if _neo4j_connector_instance is None:
        _neo4j_connector_instance = Neo4jConnector()
    return _neo4j_connector_instance

# 为了向后兼容，保留 neo4j_connector 变量，但使用属性访问
def __getattr__(name):
    if name == 'neo4j_connector':
        return get_neo4j_connector()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

if __name__ == "__main__":
    # 测试连接
    connector = Neo4jConnector()
    
    # 测试查询
    result = connector.query("MATCH (n) RETURN n LIMIT 5")
    print("查询结果:", result)
    
    # 测试获取先修关系
    rules = connector.get_prerequisite_relations("一元二次方程")
    print("先修关系规则:", rules)
    
    # 测试获取知识图谱
    graph = connector.get_knowledge_graph()
    print("知识图谱节点数:", len(graph["nodes"]))
    print("知识图谱关系数:", len(graph["relationships"]))
    
    # 关闭连接
    connector.close()