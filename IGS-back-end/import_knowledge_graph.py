#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入知识图谱数据到 Django 数据库
数据来源: D:\IGS\[CS knowledge graph]record_cs.json
"""

import os
import sys
import json
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ITS_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from user.models import User
from graphs.models import GraphDomain, KnowledgeGraph


def import_knowledge_graph():
    """导入知识图谱数据"""
    
    # 读取 JSON 文件
    json_path = r'D:\IGS\[CS knowledge graph]record_cs.json'
    print(f"正在读取文件: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8-sig') as f:
        raw_data = json.load(f)
    
    print(f"读取到 {len(raw_data)} 条记录")
    
    # 提取所有节点和关系
    nodes_dict = {}  # 使用字典去重
    relationships = []
    
    for item in raw_data:
        # 处理起始节点
        start_node = item.get('start_node')
        if start_node and start_node.get('properties'):
            node_id = start_node.get('identity')
            node_name = start_node['properties'].get('name')
            if node_name and node_id not in nodes_dict:
                nodes_dict[node_id] = {
                    'id': node_id,
                    'name': node_name,
                    'labels': start_node.get('labels', ['Concept'])
                }
        
        # 处理结束节点
        end_node = item.get('end_node')
        if end_node and end_node.get('properties'):
            node_id = end_node.get('identity')
            node_name = end_node['properties'].get('name')
            if node_name and node_id not in nodes_dict:
                nodes_dict[node_id] = {
                    'id': node_id,
                    'name': node_name,
                    'labels': end_node.get('labels', ['Concept'])
                }
        
        # 处理关系
        relation = item.get('relation')
        if relation and start_node and end_node:
            relationships.append({
                'source': start_node.get('identity'),
                'target': end_node.get('identity'),
                'type': relation.get('type', 'PREREQUISITE'),
                'properties': relation.get('properties', {})
            })
    
    nodes = list(nodes_dict.values())
    print(f"提取到 {len(nodes)} 个唯一节点")
    print(f"提取到 {len(relationships)} 条关系")
    
    # 获取第一个用户
    try:
        user = User.objects.filter(id=1).first()
        if not user:
            user = User.objects.first()
        if not user:
            print("错误: 系统中没有用户，请先创建用户")
            return
        print(f"使用用户: {user.username} (ID: {user.id})")
    except Exception as e:
        print(f"获取用户失败: {e}")
        return
    
    # 获取或创建知识领域
    domain_name = "计算机科学"
    domain, created = GraphDomain.objects.get_or_create(
        name=domain_name,
        defaults={
            'created_by': user
        }
    )
    if created:
        print(f"创建知识领域: {domain_name}")
    else:
        print(f"使用已有知识领域: {domain_name}")
    
    # 准备图谱内容
    graph_content = {
        'nodes': nodes,
        'relationships': relationships
    }
    
    # 创建知识图谱
    graph_name = "CS 知识图谱"
    graph, created = KnowledgeGraph.objects.update_or_create(
        name=graph_name,
        defaults={
            'owner': user,
            'domain': domain,
            'type': KnowledgeGraph.GraphType.CONCEPT,
            'status': KnowledgeGraph.GraphStatus.PUBLISHED,
            'description': "从 Neo4j 导出的计算机科学知识图谱，包含 287 个概念节点和 725 条先修关系",
            'content': graph_content
        }
    )
    
    if created:
        print(f"成功创建知识图谱: {graph_name}")
    else:
        print(f"成功更新知识图谱: {graph_name}")
    
    print(f"图谱 ID: {graph.id}")
    print(f"节点数量: {len(nodes)}")
    print(f"关系数量: {len(relationships)}")
    print("\n导入完成!")


if __name__ == '__main__':
    import_knowledge_graph()
